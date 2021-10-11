#!/usr/bin/python
'''
Use this in the same way as Python's SimpleHTTPServer:

  python -m RangeHTTPServer [port]

The only difference from SimpleHTTPServer is that RangeHTTPServer supports
'Range:' headers to load portions of files. This is helpful for doing local web
development with genomic data files, which tend to be to large to load into the
browser all at once.
'''

try:
    # Python3
    import http.server as SimpleHTTPServer

except ImportError:
    # Python 2
    import SimpleHTTPServer

from . import RangeRequestHandler

import argparse
import contextlib
import socket


class DualStackServer(SimpleHTTPServer.ThreadingHTTPServer):
    def server_bind(self):
        # suppress exception when protocol is IPv4
        with contextlib.suppress(Exception):
            self.socket.setsockopt(
                socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        return super().server_bind()


parser = argparse.ArgumentParser()
parser.add_argument('port', action='store',
                    default=8000, type=int,
                    nargs='?', help='Specify alternate port [default: 8000]')

args = parser.parse_args()
SimpleHTTPServer.test(HandlerClass=RangeRequestHandler,
                      ServerClass=DualStackServer,
                      port=args.port)
