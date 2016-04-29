# -*- coding: utf-8 -*-
import BaseHTTPServer
import os

from server_exception import ServerException, RequestPathException, NoHandlerException


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    if path is a dir, list the files;
    if path is a file, return the file content(permission satisfied)

    refactor version of http_server01
        all handler cases could be add by subclassing HandlerCase;
        the case priority sort by class-define
    """
    def do_GET(self):
        try:
            for cls in HandlerCase.__subclasses__():
                cls_inst = cls()
                if cls_inst.bingo(self):
                    cls_inst.act(self)
                    break

            raise NoHandlerException("Won't handled!")
        except ServerException as excep_msg:
            self.send_error(500, excep_msg)

    def send_content(self, content, status=200, msg=""):
        self.send_response(status, message=msg)
        self.send_header("content-type", "text/html")
        self.send_header("content-length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


class HandlerCase(object):
    def __init__(self):
        pass

    def bingo(self, handler):
        raise NotImplementedError

    def act(self, handler):
        raise NotImplementedError


class ReadFileCase(HandlerCase):
    def bingo(self, handler):
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), handler.path)
        return os.path.isfile(full_path)

    def act(self, handler):
        with open(handler.path, 'rb') as f:
            handler.send_content(f.read())


class ListDirCase(HandlerCase):
    def bingo(self, handler):
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), handler.path)
        return os.path.isdir(full_path)

    def act(self, handler):
        file_list = os.listdir(handler.path)
        handler.send_content(str(file_list))


if __name__ == '__main__':
    server_address = ('localhost', 8000)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    server.serve_forever()