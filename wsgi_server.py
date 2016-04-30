# -*- coding: utf-8 -*-
import StringIO
import socket
import sys
import datetime
import select
import Queue
import time
import gevent

from parser import RequestParser
from server_exception import *


class WSGIServer(object):
    def __init__(self, server_address, set_nonblock=None, request_queue_size=1, buffer_size=4096):
        assert isinstance(server_address, tuple)
        self.server_address = server_address
        self._nonblock_way = set_nonblock
        self.request_queue_size = request_queue_size

        self.sock = self.build_sock()
        self.buffer = buffer_size
        self.server_host, self.server_port = self.sock.getsockname()[:2]
        self.server_name = socket.getfqdn(self.server_host)

    def build_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self._nonblock_way:
            sock.setblocking(0)
        sock.bind(self.server_address)
        sock.listen(self.request_queue_size)
        return sock

    def set_buffer(self, buffer_size):
        self.buffer = buffer_size

    def set_application(self, app):
        """callable app served"""
        self.app = app

    def serve_forever(self):
        if self._nonblock_way.lower() == 'poll':
            self.poll_server()
        if self._nonblock_way.lower() == 'gevent':
            self.gevent_server()
        else:
            self.block_server()

    def poll_server(self):
        """
        use select.poll
        :return:
        """
        poller = select.poll()
        EVENT_READ_ONLY = (select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
        EVENT_WRITE_ONLY = (select.POLLOUT | select.POLLHUP | select.POLLERR)
        EVENT_READ_WRITE = (EVENT_READ_ONLY | select.POLLOUT)
        poller.register(self.sock.fileno(), EVENT_READ_ONLY)

        # fd_to_sock = {self.sock.fileno(): self.sock}
        fd_to_conn = {}         # fileno: client_connetion
        # fd_to_request = {}      # client_connection: request_queue
        fd_to_response = {}    # client_connection: response
        while True:
            events = poller.poll(1)
            if not events:
                continue
            print events
            for fd, event in events:
                if fd == self.sock.fileno():                            # socket get a new client connection
                    conn, addr = self.sock.accept()
                    print "#"*40, "\n[fd:{}]]got connection from: {}".format(conn.fileno(), addr)
                    conn.setblocking(0)
                    poller.register(conn.fileno(), EVENT_READ_ONLY)     # next time we'll check this connection
                    fd_to_conn[conn.fileno()] = conn
                    fd_to_response[conn.fileno()] = Queue.Queue()
                elif event & select.POLLIN:                             # con could receive data
                    request_data = fd_to_conn[fd].recv(self.buffer)
                    if request_data:
                        print "#"*40, "\n[fd:{}]received:\n{}".format(fd,request_data, request_data)
                        environ = self.build_environ(request_data)
                        status, headers, body = self.run_app(environ)
                        response = self.build_response(status, headers, body)
                        fd_to_response[fd].put(response)
                        poller.modify(fd, EVENT_READ_WRITE)             # now conn could be read or wrote
                elif event & select.POLLOUT:                            # conn could send data
                    res = fd_to_response[fd].get_nowait()
                    print '#'*40, '\n[fd:{}]sending:\n{}'.format(fd, res)
                    self.send_response(fd_to_conn[fd], res)
                    if fd_to_response[fd].empty():
                        self.close(fd_to_conn[fd])
                        poller.unregister(fd)
                        del fd_to_response[fd]
                elif event & select.POLLHUP:
                    print '#'*40, "\nclosing HUP client: ", fd_to_conn[fd].getpeername()
                    self.close(fd_to_conn[fd])
                    poller.unregister(fd)
                    del fd_to_response[fd]
                elif event & select.POLLNVAL:
                    raise POLLEXCEPTION("Descriptor closed before unregisterd!")
                elif event & select.POLLERR:
                    self.sock.close()
                    raise POLLEXCEPTION("Error on select.poll")

    def gevent_server(self):
        while True:
            gevent.joinall([gevent.spawn(self._gevent_server) for i in range(self.request_queue_size)])

    def _gevent_server(self):
        cli, addr = self.sock.accept()
        cli.setblocking(0)
        data = cli.recv(self.buffer)
        environ = self.build_response(data)
        status, headers, body = self.run_app(environ)
        res = self.build_response(status, headers, body)
        self.send_n_close(cli, res)

    def block_server(self):
        while True:
            client_connection, client_address = self.sock.accept()          # block-point
            print "Got connection from: ", client_address
            request_data = self.receive_from(client_connection)             # block-point
            print "Received: ", request_data
            environ = self.build_environ(request_data)
            status, headers, body = self.run_app(environ)
            response = self.build_response(status, headers, body)
            print "Sending: ", response
            self.send_n_close(client_connection, response)                 # block-point

    def receive_from(self, client):
        request_data = b""
        EOL_1 = b"\n\n"
        EOL_2 = b"\n\r\n"
        while True:
                data = client.recv(self.buffer)
                if not data:
                    break
                else:
                    request_data += data
                if len(data) != self.buffer:
                    break
        return request_data

    def build_environ(self, request):
        """
        build a environ dict for a request from a client
        :param request:
        :return:
        """
        req = RequestParser(request)
        env = {}
        env['REQUEST_METHOD'] = req.request_method
        env['PATH_INFO'] = req.request_path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)
        # WSGI/CGI vars
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO.StringIO(request)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False
        return env

    @property
    def server_response_headers(self):
        """
        default server headers
        :return:
        """
        return [
            ("Date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]

    def run_app(self, environ):
        """
        call web-app, set the status, headers and get result of body
        encapsulate function 'start_response'
        :param environ:
        :return:
        """
        assert callable(self.app)
        _status = ''
        _headers = []
        _body = ''

        def start_response(status, headers):
            _status = status
            _headers = self.server_response_headers + headers

        for data in self.app(environ, start_response):
            _body += str(data)
        return _status, _headers, _body

    @staticmethod
    def build_response(status, headers, body):
        response_lines = []
        response_lines.append("HTTP/1.1 {}".format(status))
        for header in headers:
            response_lines.append("{}: {}".format(header[0], header[-1]))
        response_lines.append('')  # space line
        response_lines.append(body)
        return '\n'.join(response_lines)

    @staticmethod
    def send_response(client, res):
        try:
            client.sendall(res)
        except Exception as e:
            raise

    @staticmethod
    def shutdown(client):
        client.shutdown()

    @staticmethod
    def close(client):
        try:
            client.close()
        except Exception as e:
            raise

    @staticmethod
    def send_n_close(client, res):
        WSGIServer.send_response(client, res)
        WSGIServer.close(client)


if __name__ == '__main__':
    from test import WSGIapp
    # print {
    #     'in': select.POLLIN,
    #     'out': select.POLLOUT,
    #     'hup': select.POLLHUP,
    #     'pri': select.POLLPRI,
    #     'err': select.POLLERR,
    #     'nval': select.POLLNVAL,
    #     'rdband': select.POLLRDBAND,
    #     'rdnorm': select.POLLRDNORM,
    #     'wrband': select.POLLWRBAND,
    #     'wrnorm': select.POLLWRNORM,
    # }
    # {'wrnorm': 4, 'hup': 16, 'err': 8, 'in': 1, 'wrband': 256, 'rdband': 128, 'nval': 32, 'pri': 2, 'rdnorm': 64, 'out': 4}


    svr = WSGIServer(('localhost', 8000), set_nonblock='gevent', request_queue_size=128)
    svr.set_application(WSGIapp.app)
    svr.serve_forever()
