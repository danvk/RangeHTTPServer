# Import RangeHTTPServer from this project, not the global install.
import sys
sys.path = ['.'] + sys.path
import RangeHTTPServer
from RangeHTTPServer import RangeRequestHandler

from nose.tools import *
from StringIO import StringIO
from BaseHTTPServer import HTTPServer
import requests
import threading
import time


def test_parse_byte_range():
    eq_((0, 499), RangeHTTPServer.parse_byte_range('bytes=0-499'))
    eq_((987, 1024), RangeHTTPServer.parse_byte_range('bytes=987-1024'))
    eq_((None, None), RangeHTTPServer.parse_byte_range(''))
    eq_((10, None), RangeHTTPServer.parse_byte_range('bytes=10-'))


def test_copy_byte_range():
    inbuffer = StringIO('0123456789abcdefghijklmnopqrstuvwxyz')
    outbuffer = StringIO()

    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer, 4, 10)
    eq_('456789a', outbuffer.getvalue())

    outbuffer = StringIO()
    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer, 0, 4)
    eq_('01234', outbuffer.getvalue())

    outbuffer = StringIO()
    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer, 26)
    eq_('qrstuvwxyz', outbuffer.getvalue())

    outbuffer = StringIO()
    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer, 0, 9, 10)
    eq_('0123456789', outbuffer.getvalue())

    inbuffer.seek(0)
    outbuffer = StringIO()
    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer)
    eq_('0123456789abcdefghijklmnopqrstuvwxyz', outbuffer.getvalue())


def test_server():
    httpd = [None]  # no other way to set this from inside start_server() :(
    def start_server():
        RangeRequestHandler.protocol_version = 'HTTP/1.0'
        httpd[0] = HTTPServer(('', 8712), RangeRequestHandler)
        httpd[0].serve_forever()

    server_thread = threading.Thread(target=start_server)
    server_thread.setDaemon(True)
    server_thread.start()
    time.sleep(1.0)

    r = requests.get('http://localhost:8712/tests/data.txt')
    eq_('0123456789abcdef\n', r.text)

    httpd[0].shutdown()
    server_thread.join()
