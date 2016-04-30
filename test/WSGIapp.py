# coding=utf-8
"""

"""
import json
def app(environ, start_response):
    import time
    # time.sleep(1)
    status = '200'
    response_header = [
        ('Content-Type', 'text/plain')
    ]
    start_response(status, response_header)
    return [environ]