# coding=utf-8
"""

"""
import json
import time
import random

def app(environ, start_response):
    time.sleep(random.randint(0, 10))
    status = '200'
    response_header = [
        ('Content-Type', 'text/plain')
    ]
    start_response(status, response_header)
    return [environ]