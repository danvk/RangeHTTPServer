# Import RangeHTTPServer from this project, not the global install.
import sys
sys.path = ['.'] + sys.path
import RangeHTTPServer
from RangeHTTPServer import RangeRequestHandler

from nose.tools import *

from BaseHTTPServer import HTTPServer
import requests
import threading
import time


httpd = None
server_thread = None
def setup():
    def start_server():
        global httpd
        RangeRequestHandler.protocol_version = 'HTTP/1.0'
        httpd = HTTPServer(('', 8712), RangeRequestHandler)
        httpd.serve_forever()

    global server_thread
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    time.sleep(1.0)


def teardown():
    httpd.shutdown()
    server_thread.join()


def test_server():
    r = requests.get('http://localhost:8712/tests/data.txt')
    eq_('0123456789abcdef\n', r.text)
