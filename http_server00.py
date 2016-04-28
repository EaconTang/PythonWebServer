# -*- coding: utf-8 -*-
import BaseHTTPServer


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    response_page = """
    <html>
        <body>
            saluton
        </body>
    </html>
    """

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(self.response_page)))
        self.end_headers()
        self.wfile.write(self.response_page)


if __name__ == '__main__':
    server_address = ('localhost', 8000)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    server.serve_forever()