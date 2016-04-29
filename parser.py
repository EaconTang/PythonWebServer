# -*- coding: utf-8 -*-
class RequestParser(object):
    """

    """
    def __init__(self, request):
        self._request = request.lstrip().rstrip()
        self._all_request_lines = self._request.splitlines()
        self._index_space = self.get_index_space()

    def get_index_space(self):
        """
        if no request-body, index_space is None
        """
        try:
            index_space = self._all_request_lines.index('')
        except ValueError:
            index_space = None
        return index_space

    @property
    def resquest_line(self):
        return self._all_request_lines[0].rstrip('\n').rstrip('\r')

    @property
    def request_method(self):
        return self.resquest_line.split()[0]

    @property
    def request_path(self):
        return self.resquest_line.split()[1]

    @property
    def request_version(self):
        return self.resquest_line.split()[2]

    @property
    def request_headers(self):
        if self._index_space is not None:
            _headers = self._all_request_lines[1:self._index_space]
        else:
            _headers = self._all_request_lines[1:]
        _headers = [header.split(':', 1) for header in _headers]
        return [(header[0].strip(), header[-1].strip()) for header in _headers]

    def get_header(self, key):
        return dict(self.request_headers).get(key, None)

    @property
    def request_body(self):
        if self._index_space is not None:
            return '\n'.join(self._all_request_lines[self._index_space + 1:])
        else:
            return None


if __name__ == '__main__':
    text = """GET /hello.txt HTTP/1.1
User-Agent: curl/7.16.3 libcurl/7.16.3 OpenSSL/0.9.7l zlib/1.2.3
Host: www.example.com
Accept-Language: en, mi

body-1
body-2
"""
    req = RequestParser(text)
    print req.resquest_line
    print req.request_method, req.request_path, req.request_version
    print req.request_headers
    print req.get_header('User-Agent')
    print req.request_body