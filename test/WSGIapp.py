# coding=utf-8
"""

"""
import json
def app(environ, start_response):
    status = '200'
    response_header = [
        ('Content-Type', 'text/plain')
    ]
    start_response(status, response_header)
    return [environ]