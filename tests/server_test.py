from http.server import HTTPServer
import socket
import threading
import time

import pytest
import requests

from RangeHTTPServer import RangeRequestHandler


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def http_server():
    port = get_free_port()
    def start_server():
        global httpd
        RangeRequestHandler.protocol_version = 'HTTP/1.0'
        httpd = HTTPServer(('', port), RangeRequestHandler)
        httpd.serve_forever()

    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    time.sleep(1.0)

    yield f'http://localhost:{port}'

    httpd.shutdown()
    server_thread.join()


def headers_of_note(response):
    '''Returns a dict of just the interesting headers for RangeHTTPServer.'''
    return {k: response.headers.get(k) for k in [
        'Content-Type',
        'Accept-Ranges',
        'Content-Range',
        'Content-Length']}


def test_simple_request(http_server):
    r = requests.get(f'{http_server}/tests/data.txt')
    assert 200 == r.status_code
    assert '0123456789abcdef\n' == r.text
    assert 'text/plain' == r.headers['content-type']


def test_range_request(http_server):
    r = requests.get(f'{http_server}/tests/data.txt',
                     headers={'Range': 'bytes=0-9'})
    assert 206 == r.status_code
    assert '0123456789' == r.text
    assert {
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 0-9/17',
        'Content-Length': '10'
        } == headers_of_note(r)


def test_open_range_request(http_server):
    r = requests.get(f'{http_server}/tests/data.txt',
                     headers={'Range': 'bytes=10-'})
    assert 206 == r.status_code
    assert 'abcdef\n' == r.text
    assert {
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 10-16/17',
        'Content-Length': '7'
        } == headers_of_note(r)


def test_mid_file_range_request(http_server):
    r = requests.get(f'{http_server}/tests/data.txt',
                     headers={'Range': 'bytes=6-10'})
    assert 206 == r.status_code
    assert '6789a' == r.text
    assert {
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 6-10/17',
        'Content-Length': '5'
        } == headers_of_note(r)


def test_404(http_server):
    r = requests.get(f'{http_server}/tests/nonexistent.txt',
                     headers={'Range': 'bytes=6-10'})
    assert 404 == r.status_code


def test_bad_range(http_server):
    r = requests.get(f'{http_server}/tests/data.txt',
                     headers={'Range': 'bytes=abc'})
    assert 400 == r.status_code


def test_range_past_eof(http_server):
    r = requests.get(f'{http_server}/tests/data.txt',
                     headers={'Range': 'bytes=10-100'})
    assert 206 == r.status_code
    assert 'abcdef\n' == r.text
    assert {
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 10-16/17',
        'Content-Length': '7'
        } == headers_of_note(r)


def test_range_at_eof(http_server):
    r = requests.get(f'{http_server}/tests/data.txt',
                     headers={'Range': 'bytes=16-'})
    assert 206 == r.status_code
    assert '\n' == r.text
    assert {
        'Content-Type': 'text/plain',
        'Accept-Ranges': 'bytes',
        'Content-Range': 'bytes 16-16/17',
        'Content-Length': '1'
        } == headers_of_note(r)


def test_range_starting_past_eof(http_server):
    r = requests.get(f'{http_server}/tests/data.txt',
                     headers={'Range': 'bytes=17-'})
    assert 416 == r.status_code  # "Requested Range Not Satisfiable"
