#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

try:
    # Python 3
    from http.server import BaseHTTPRequestHandler
    from http.server import HTTPServer
    from socketserver import ThreadingMixIn
except ImportError:
    # Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
    from SocketServer import ThreadingMixIn

# 最大スレッド数
MAX_THREADS = 10

class GreetingHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

        # Content-Body の送信まで 5 秒のディレイが入る
        time.sleep(5)

        self.wfile.write(b'Hello, World!\r\n')


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """マルチスレッド化した HTTPServer"""
    pass
        
def main():
    server_address = ('localhost', 8000)
    # マルチスレッド化した HTTP サーバを使う
    httpd = ThreadedHTTPServer(server_address, GreetingHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    main()