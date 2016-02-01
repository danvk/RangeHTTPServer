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


SimpleHTTPServer.test(HandlerClass=RangeRequestHandler)
