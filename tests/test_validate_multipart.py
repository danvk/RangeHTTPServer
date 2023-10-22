import pytest

from requests_toolbelt.multipart.decoder import MultipartDecoder
import requests

from http.server import HTTPServer

import threading
import time

from range_http_server.request_handlers.range_request_handler import RangeRequestHandler

httpd = None
server_thread = None
def setup():
    def start_server():
        global httpd
        RangeRequestHandler.protocol_version = 'HTTP/1.0'
        # TODO(danvk): pick a random, available port
        httpd = HTTPServer(('', 8713), RangeRequestHandler)
        httpd.serve_forever()

    global server_thread
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    time.sleep(1.0)


def teardown():
    httpd.shutdown()
    server_thread.join()

def test_validate_multipart():

    url = 'http://localhost:8713/tests/data.txt'
    headers = {'Range': 'bytes=6-10,12-14,14-17'}

    response = requests.get(url, headers=headers)
    if response.status_code == 206:
        decoder = MultipartDecoder.from_response(response)
        parts = decoder.parts

        combined_content = b''
        for part in parts:
            combined_content += part.content
        content_decoded = combined_content.decode()

        assert content_decoded == '6789acdeef\n'
        print(combined_content.decode())
    else:
        print(f"Unexpected response status: {response.status_code}")