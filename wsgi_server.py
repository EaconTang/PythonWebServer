# -*- coding: utf-8 -*-
import StringIO
import socket
import sys

from parser import RequestParser
from server_exception import *


class WSGIServer(object):
    def __init__(self, server_address, request_queue_size=1, buffer_size=1024):
        assert isinstance(server_address, tuple)
        self.server_address = server_address
        self.sock = self.build_sock()
        self.sock.bind(self.server_address)
        self.sock.listen(request_queue_size)

        self.buffer = buffer_size
        self.server_host, self.server_port = self.sock.getsockname()[:2]
        self.server_name = socket.getfqdn(self.server_host)

    def build_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def set_buffer(self, buffer_size):
        self.buffer = buffer_size

    def serve_forever(self):
        while True:
            self.client_connection, self.client_address = self.sock.accept()
            self.request_data = self.client_connection.recv(self.buffer)
            self.handle_request(self.request_data)
            self.send_response()

    def handle_request(self, request):
        self.environ = self.build_environ(request)
        self.run_app(self.app)

    def start_response(self, status, response_headers, exc_info=None):
        self.respose_status = status
        self.respose_headers = self.server_response_headers + response_headers

    def set_application(self, app):
        """callable app served"""
        self.app = app

    def build_environ(self, request):
        req = RequestParser(request)
        env = {}
        env['REQUEST_METHOD'] = req.request_method
        env['PATH_INFO'] = req.request_path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)
        # WSGI/CGI vars
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False
        return env

    def run_app(self, app):
        assert callable(app)
        response = ''
        for data in app(self.environ, self.start_response):
            response += str(data)
        self.response_body = response

    @property
    def server_response_headers(self):
        return []

    def build_response(self):
        response_lines = []
        response_lines.append("HTTP/1.1 {}".format(self.respose_status))
        for header in self.respose_headers:
            response_lines.append("{}: {}".format(header[0], header[-1]))
        response_lines.append('')  # space line
        response_lines.append(self.response_body)
        return '\n'.join(response_lines)

    def send_response(self):
        try:
            res = self.build_response()
            self.client_connection.sendall(res)
        except Exception as e:
            raise SendResponseException(e)
        finally:
            self.client_connection.close()


if __name__ == '__main__':
    from test import WSGIapp

    svr = WSGIServer(('localhost', 8000))
    svr.set_application(WSGIapp.app)
    svr.serve_forever()
