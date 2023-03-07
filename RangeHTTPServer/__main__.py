"""
Use this in the same way as Python's SimpleHTTPServer:

  python -m RangeHTTPServer [port]

The only difference from SimpleHTTPServer is that RangeHTTPServer supports
'Range:' headers to load portions of files. This is helpful for doing local web
development with genomic data files, which tend to be to large to load into the
browser all at once.
"""

try:
    # Python3
    import http.server as SimpleHTTPServer

except ImportError:
    # Python 2
    import SimpleHTTPServer

from . import RangeRequestHandler

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('port', action='store',
                    default=8000, type=int,
                    nargs='?', help='Specify alternate port [default: 8000]')

args = parser.parse_args()
SimpleHTTPServer.test(HandlerClass=RangeRequestHandler, port=args.port)
