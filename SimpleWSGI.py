# encoding=utf-8
"""
下面的代码片段展示了（WSGI）接口的服务器和框架端
def run_application(application):
    '''Server code.'''
    # This is where an application/framework stores
    # an HTTP status and HTTP response headers for the server
    # to transmit to the client
    headers_set = []
    # Environment dictionary with WSGI/CGI variables
    environ = {}

    def start_response(status, response_headers, exc_info=None):
        headers_set[:] = [status, response_headers]

    # Server invokes the ‘application' callable and gets back the
    # response body
    result = application(environ, start_response)
    # Server builds an HTTP response and transmits it to the client
    …

def app(environ, start_response):
    '''A barebones WSGI app.'''
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello world!']

run_application(app)


以下是它如何工作的：

1.框架提供一个可调用的’应用’（WSGI规格并没有要求如何实现）
2.服务器每次接收到HTTP客户端请求后，执行可调用的’应用’。服务器把一个包含了WSGI/CGI变量的字典和一个可调用的’start_response’做为参数给可调用的’application’。
3.框架/应用生成HTTP状态和HTTP响应头，然后把它们传给可调用的’start_response’，让服务器保存它们。框架/应用也返回一个响应体。
4.服务器把状态，响应头，响应体合并到HTTP响应里，然后传给（HTTP）客户端（这步不是（WSGI）规格里的一部分，但它是后面流程中的一步，为了解释清楚我加上了这步）
"""
import socket
import StringIO
import sys


class WSGIServer(object):
    """

    """
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )
        listen_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )
        listen_socket.bind(server_address)
        listen_socket.listen(self.request_queue_size)
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        listen_socket = self.listen_socket
        while 1:
            self.client_connection, self.client_address = listen_socket.accept()
            self.handle_one_request()

    def handle_one_request(self):
        self.request_data = request_data = self.client_connection.recv(1024)
        print ''.join(['< %s\n' % line for line in request_data.splitlines()])
        self.parse_request(request_data)
        env = self.get_environ

        result = self.application(env, self.start_response)
        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0].rstrip('\n')  # rstrip('\n')?
        (self.request_method,
         self.path,
         self.request_version) = request_line.split()

    def get_environ(self):
        env = {}
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False

        env['REQUEST_METHOD'] = self.request_method
        env['PATH_INFO'] = self.path
        env['SERVER_NAME'] = self.server_name
        env['SERVER_PORT'] = str(self.server_port)
        #
        # env = {
        #     'wsgi.version': (1,0),
        #     'wsgi.url_scheme': 'http',
        #     'wsgi.input': StringIO.StringIO(self.request_data),
        #     'wsgi.errors': sys.stderr,
        #     'wsgi.multithread': False,
        #     'wsgi.multiprocess': False,
        #     'wsgi.run_once': False,
        #
        #     'REQUEST_METHOD' = self.request_data,
        #     'PATH_INFO': self.path,
        #     'SERVER_NAME': self.server_name,
        #     'SERVER_PORT': str(self.server_port),
        # }

        return env

    def start_response(self, status, response_headers, exc_info=None):
        server_headers = [
            ('Date', 'Fri, 26 Feb 2016 12:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = 'HTTP/1.1 {0}\n'.format(status)
            for header in response_headers:
                response += '{0}: {1}\n'.format(*header)
            response += '\n'
            for data in result:
                response += data
            print ''.join(['> {0}\n'.format(line) for line in response.splitlines()])
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()


def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server


if __name__ == '__main__':
    SERVER_ADDRESS = (HOST, PORT) = '', 8888

    if len(sys.argv) < 2:
        sys.exit('Please provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print 'WSGIServer: Sering HTTP on port {0}...\n'.format(PORT)
    httpd.serve_forever()
