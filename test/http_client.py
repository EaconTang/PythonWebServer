# -*- coding: utf-8 -*-
import httplib

req_body = """saluton
saluton
salutonsaluton
saluton
saluton
saluton
salutons
"""


def main():
    conn = httplib.HTTPConnection(host="localhost", port=8000)
    conn.request(method="GET", url="/", body=req_body, headers={
        "Accept": "text/*",
    })

    res = conn.getresponse()
    if res.status == httplib.OK:
        print res.read()
    else:
        print res.reason


if __name__ == '__main__':
    main()
