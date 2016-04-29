# -*- coding: utf-8 -*-
import BaseHTTPServer
import os
import commands

from server_exception import *
import template


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    """
    @property
    def full_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), self.path)

    def do_GET(self):
        try:
            for cls in HandlerCase.__subclasses__():
                cls_inst = cls()
                if cls_inst.bingo(self):
                    cls_inst.act(self)
                    break

            raise NoHandlerException("Won't handled!")
        except ServerException as excep_msg:
            print excep_msg
            self.send_content(template.render("error_page.html", msg="500 Error!"), 500, excep_msg)

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


class CGIFileCase(HandlerCase):
    def bingo(self, handler):
        return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')

    def act(self, handler):
        cmd = 'python ' + handler.full_path
        status, output = commands.getstatusoutput(cmd)
        if status != 0:
            raise CGIRunException
        handler.send_content(output)



class ReadFileCase(HandlerCase):
    def bingo(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        with open(handler.full_path, 'rb') as f:
            handler.send_content(f.read())


class IndexDirCase(HandlerCase):
    def bingo(self, handler):
        return os.path.isdir(handler.full_path) and 'index.html' in os.listdir(handler.full_path)

    def act(self, handler):
        with open(os.path.join(handler.full_path, 'index.html'), 'rb') as f:
            handler.send_content(f.read())


class ListDirCase(HandlerCase):
    def bingo(self, handler):
        return os.path.isdir(handler.full_path)

    def act(self, handler):
        file_list = os.listdir(handler.full_path)
        file_list_html = '\n'.join(['<li><a href="{}">{}</a></li>'.format('/'.join([handler.full_path.rstrip('/'), _]), _)
                                    for _ in file_list])
        handler.send_content(template.render("list_dir.html", lists=file_list_html))


if __name__ == '__main__':
    server_address = ('localhost', 8000)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    server.serve_forever()