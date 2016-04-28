# -*- coding: utf-8 -*-
import BaseHTTPServer
import os

from server_exception import ServerException, RequestPathException, NoHandlerException


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    if path is a dir, list the files;
    if path is a file, return the file content(permission satisfied)
    """
    def do_GET(self):
        try:
            dir_name = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(dir_name, self.path)
            print full_path
            if not os.path.exists(full_path):
                raise RequestPathException("Wrong path!")
            if os.path.isdir(full_path):
                self.handle_dir(full_path)
            elif os.path.isfile(full_path):
                self.handler_file(full_path)
            else:
                raise NoHandlerException("Won't handled!")
        except ServerException as excep_msg:
            self.send_error(500, excep_msg)

    def handle_dir(self, path):
        file_list = os.listdir(path)
        self.send_content(str(file_list))

    def handler_file(self, path):
        with open(path, 'rb') as f:
            self.send_content(f.read())

    def send_content(self, content, status=200, msg=""):
        self.send_response(status, message=msg)
        self.send_header("content-type", "text/html")
        self.send_header("content-length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == '__main__':
    server_address = ('localhost', 8000)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    server.serve_forever()