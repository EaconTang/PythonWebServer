# -*- coding: utf-8 -*-

class MyApp(object):
    """
    implement callable application in Class, support URL distinguish
    """
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    def __iter__(self):
        status_200 = '200 OK'
        status_404 = '404 Not Found'
        response_headers = [
            ('Content-type', 'text/plain'),
        ]
        # self.start_response(status, response_headers)
        # yield 'Saluton!\n'

        request_url = self.environ['PATH_INFO']
        request_url = str(request_url).lower()
        if request_url == '/':
            self.start_response(status_200, response_headers)
            yield 'Home index!\n'
        elif request_url == '/saluton':
            self.start_response(status_200, response_headers)
            yield 'Saluton!\n'
        else:
            self.start_response(status_404, response_headers)
            yield 'Sorry! Page Not Found!\n'