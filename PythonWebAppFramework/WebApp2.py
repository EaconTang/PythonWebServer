# -*- coding: utf-8 -*-
import re
import Utils


class MyApp(object):
    """

    """

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    @Utils.iter_wraper
    def __iter__(self):
        path = self.get_path()
        method = self.get_method()
        for pattern, name in self.url_pattern:
            m = re.match(pattern, path)
            if m:
                funcname = method + '_' + name
                if hasattr(self, funcname):
                    func = getattr(self, funcname)
                    path_args = m.groups()
                    return func(*path_args)
        return self.not_found()

    @property
    def url_pattern(self):
        _urls = (
            (r'^/$', 'index'),
            (r'^/saluton/?(.*)$', 'saluton'),
        )
        return _urls

    def make_response(self, status='200 OK'):
        status = status
        response_header = [
            ('Content-type', 'text/plain'),
        ]
        self.start_response(status, response_header)

    def get_path(self):
        return self.environ['PATH_INFO']

    def get_method(self):
        return self.environ['REQUEST_METHOD']

    def GET_index(self):
        self.make_response()
        yield 'Index Page!\n'

    def GET_saluton(self, *args):
        self.make_response()
        args = [arg for arg in args if arg]  # remove string ''
        if len(args) == 1:
            yield 'Saluton {0}!\n'.format(*args)
        elif len(args) > 1:
            args_list_str = ','.join(args)
            yield 'Saluton ' + args_list_str + '!\n'
        else:
            yield 'Saluton!\n'

    def not_found(self):
        self.make_response('404 Not Found')
        yield 'Page Not Found!\n'
