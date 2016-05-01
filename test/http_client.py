# -*- coding: utf-8 -*-
import httplib
from multiprocessing import Pool
import os
import sys
import time
import select
import socket
import gevent

req = """Get / HTTP/1.1
Accept: */*

saluton
saluton
salutonsaluton
saluton
saluton
saluton
salutons
"""

ct = lambda : time.time()

def foo(n):
    # print _range
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8008))
    s.send(req)
    return s

def bar(n, s):
    data = s.recv(4096)
    s.close()
    print "[process:{}]done".format(n)

    #
    # conn_list = []
    # inputs = []
    # outputs = conn_list
    #
    # while True:
    #     readable, writable, exceptional = select.select(inputs, outputs, outputs, 60)
    #     if not (readable or writable or exceptional):
    #         break
    #     for s in writable:
    #         s.send(req_body)
    #         if s not in inputs:
    #             inputs.append(s)
    #         writable.remove(s)
    #     for s in readable:
    #         data = s.recv(4096)
    #         readable.remove(s)
    #         print '[fd:{}]got response!'.format(s.fileno())

    # conn.request(method="GET", url="/", body=req_body, headers={
    #             "Accept": "text/*",
    #         })
    #         res = conn.getresponse()
    #     if res.status == httplib.OK:
    #         print '[pid:{}]finish request {}!'.format(os.getpid(), i)
    # print '[pid:{}]Done!'.format(os.getpid())

def main(x):

    #
    # t1 = ct()
    #
    # gevent.joinall([gevent.spawn(foo, i) for i in range(x)])
    # print 'Done'
    #
    # res1 = ct() - t1
    #
    t2 = ct()
    socks = []
    for i in range(x):
        s= foo(i)
        socks.append(s)

    for i in range(x):
        bar(i, socks[i])

    print 'Done'

    res2 = ct() - t2

    # print res1
    print res2

if __name__ == '__main__':
    main(20)
