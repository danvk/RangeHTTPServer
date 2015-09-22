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
        # TODO(danvk): pick a random, available port
        httpd = HTTPServer(('', 8712), RangeRequestHandler)
        httpd.serve_forever()

    global server_thread
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    time.sleep(1.0)


def teardown():
    httpd.shutdown()
    server_thread.join()


def headers_of_note(response):
    '''Returns a dict of just the interesting headers for RangeHTTPServer.'''
    return {k: response.headers.get(k) for k in [
        'Content-Type',
        'Accept-Ranges',
        'Content-Range',
        'Content-Length']}


def test_simple_request():
    r = requests.get('http://localhost:8712/tests/data.txt')
    eq_(200, r.status_code)
    eq_('0123456789abcdef\n', r.text)
    eq_('text/plain', r.headers['content-type'])


def test_range_request():
    r = requests.get('http://localhost:8712/tests/data.txt',
                     headers={'Range': 'bytes=0-9'})
    eq_(206, r.status_code)
    eq_('0123456789', r.text)
    eq_({
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 0-9/17',
        'Content-Length': '10'
        }, headers_of_note(r))


def test_open_range_request():
    r = requests.get('http://localhost:8712/tests/data.txt',
                     headers={'Range': 'bytes=10-'})
    eq_(206, r.status_code)
    eq_('abcdef\n', r.text)
    eq_({
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 10-16/17',
        'Content-Length': '7'
        }, headers_of_note(r))


def test_mid_file_range_request():
    r = requests.get('http://localhost:8712/tests/data.txt',
                     headers={'Range': 'bytes=6-10'})
    eq_(206, r.status_code)
    eq_('6789a', r.text)
    eq_({
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 6-10/17',
        'Content-Length': '5'
        }, headers_of_note(r))


def test_404():
    r = requests.get('http://localhost:8712/tests/nonexistent.txt',
                     headers={'Range': 'bytes=6-10'})
    eq_(404, r.status_code)


def test_bad_range():
    r = requests.get('http://localhost:8712/tests/data.txt',
                     headers={'Range': 'bytes=abc'})
    eq_(400, r.status_code)


def test_range_past_eof():
    r = requests.get('http://localhost:8712/tests/data.txt',
                     headers={'Range': 'bytes=10-100'})
    eq_(206, r.status_code)
    eq_('abcdef\n', r.text)
    eq_({
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 10-16/17',
        'Content-Length': '7'
        }, headers_of_note(r))


def test_range_at_eof():
    r = requests.get('http://localhost:8712/tests/data.txt',
                     headers={'Range': 'bytes=16-'})
    eq_(206, r.status_code)
    eq_('\n', r.text)
    eq_({
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 16-16/17',
        'Content-Length': '1'
        }, headers_of_note(r))


def test_range_starting_past_eof():
    r = requests.get('http://localhost:8712/tests/data.txt',
                     headers={'Range': 'bytes=17-'})
    eq_(416, r.status_code)  # "Requested Range Not Satisfiable"
