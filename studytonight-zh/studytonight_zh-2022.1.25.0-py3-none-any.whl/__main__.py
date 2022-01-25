from http.server import \
    SimpleHTTPRequestHandler, \
    HTTPServer
from socketserver import ThreadingMixIn
import sys
from os import path
import os

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def main():
    os.chdir(path.dirname(__file__))
    port = sys.argv[1] if len(sys.argv) > 1 else 3000
    addr = ('localhost', int(port))
    SimpleHTTPRequestHandler.protocol_version = "HTTP/1.1"
    svr = ThreadingHTTPServer(addr, SimpleHTTPRequestHandler)
    print(f"Serving HTTP on localhost port {port} ...")
    svr.serve_forever()
    
if __name__ == '__main__': main()