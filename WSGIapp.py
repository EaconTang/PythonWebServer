# coding=utf-8
"""

"""
def app(environ, start_response):
    status = '200'
    response_header = [
        ('Content-Type', 'text/plain')
    ]
    start_response(status, response_header)
    return ['Saluton from a simple WSGI application!\n']