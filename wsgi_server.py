# -*- coding: utf-8 -*-
import StringIO
import socket
import sys
import datetime
import select
import Queue

from parser import RequestParser
from server_exception import *


class WSGIServer(object):
    def __init__(self, server_address, set_nonblock=False, request_queue_size=1, buffer_size=4096):
        assert isinstance(server_address, tuple)
        self.server_address = server_address
        self._use_nonblock = set_nonblock
        self.request_queue_size = request_queue_size

        self.sock = self.build_sock()
        self.buffer = buffer_size
        self.server_host, self.server_port = self.sock.getsockname()[:2]
        self.server_name = socket.getfqdn(self.server_host)

    def build_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self._use_nonblock:
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
        if self._use_nonblock:
            self.serve_nonblock()
        else:
            self.serve_block()

    def serve_nonblock(self):
        """
        use select.poll
        :return:
        """
        poller = select.poll()
        EVENT_READ_ONLY = (select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
        EVENT_WRITE_ONLY = (select.POLLOUT | select.POLLHUP | select.POLLERR)
        EVENT_READ_WRITE = (EVENT_READ_ONLY | select.POLLOUT)
        poller.register(self.sock.fileno(), EVENT_READ_ONLY)

        fd_to_sock = {self.sock.fileno(): self.sock}
        fd_to_conn = {}         # fileno: client_connetion
        fd_to_request = {}      # client_connection: request_queue
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
                elif event & select.POLLIN:                             # con could receive data
                    request_data = fd_to_conn[fd].recv(self.buffer)
                    if request_data:
                        print "#"*40, "\n[fd:{}]received:\n{}".format(fd,request_data, request_data)
                        environ = self.build_environ(request_data)
                        status, headers, body = self.run_app(environ)
                        response = self.build_response(status, headers, body)
                        fd_to_response[fd] = response
                        poller.modify(fd, EVENT_WRITE_ONLY)             # now conn could be read or wrote
                elif event & select.POLLOUT:                            # conn could send data
                    res = fd_to_response[fd]
                    print '#'*40, '\n[fd:{}]sending:\n{}'.format(fd, res)
                    self.send_response(fd_to_conn[fd], res)
                    # poller.unregister(fd)
                elif event & select.POLLHUP:
                    print '#'*40, "\nclosing HUP client: ", fd_to_conn[fd].getpeername()
                    poller.unregister(fd)
                    fd_to_conn[fd].shutdown(socket.SHUT_RDWR)
                    if fd_to_response.empty():
                        del fd_to_response
                elif event & select.POLLNVAL:
                    raise POLLEXCEPTION("Descriptor closed before unregisterd!")
                elif event & select.POLLERR:
                    self.sock.close()
                    raise POLLEXCEPTION("Error on select.poll")

    def serve_block(self):
        while True:
            client_connection, client_address = self.sock.accept()          # block-point
            request_data = self.receive_from(client_connection)             # block-point
            environ = self.build_environ(request_data)
            status, headers, body = self.run_app(environ)
            response = self.build_response(status, headers, body)
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
    def send_n_close(client, res):
        try:
            client.sendall(res)
        except Exception as e:
            raise SendResponseException(e)
        finally:
            client.close()

    @staticmethod
    def send_response(client, res):
        try:
            client.sendall(res)
        except Exception as e:
            raise SendResponseException(e)


if __name__ == '__main__':
    from test import WSGIapp

    svr = WSGIServer(('localhost', 8000), set_nonblock=True)
    svr.set_application(WSGIapp.app)
    svr.serve_forever()
