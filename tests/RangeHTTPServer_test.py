# Import RangeHTTPServer from this project, not the global install.
import pytest

from io import StringIO
from range_http_server.request_handlers.range_request_handler import parse_byte_range, copy_byte_range

def test_parse_byte_range():
    assert (0, 499) == parse_byte_range('bytes=0-499')[0]
    assert (987, 1024) == parse_byte_range('bytes=987-1024')[0]
    assert (None, None) == parse_byte_range('')[0]
    assert (10, None) == parse_byte_range('bytes=10-')[0]

    with pytest.raises(ValueError):
        parse_byte_range('bytes=abc')
    with pytest.raises(ValueError):
        parse_byte_range('characters=0-10')
    with pytest.raises(ValueError):
        parse_byte_range('bytes=100-2')


def test_copy_byte_range():
    inbuffer = StringIO(u'0123456789abcdefghijklmnopqrstuvwxyz')
    outbuffer = StringIO()

    copy_byte_range(inbuffer, outbuffer, 4, 10)
    assert '456789a' == outbuffer.getvalue()

    outbuffer = StringIO()
    copy_byte_range(inbuffer, outbuffer, 0, 4)
    assert '01234' == outbuffer.getvalue()

    outbuffer = StringIO()
    copy_byte_range(inbuffer, outbuffer, 26)
    assert 'qrstuvwxyz' == outbuffer.getvalue()

    outbuffer = StringIO()
    copy_byte_range(inbuffer, outbuffer, 0, 9, 10)
    assert '0123456789' == outbuffer.getvalue()

    inbuffer.seek(0)
    outbuffer = StringIO()
    copy_byte_range(inbuffer, outbuffer)
    assert '0123456789abcdefghijklmnopqrstuvwxyz' == outbuffer.getvalue()

if __name__ == "__main__":
    test_parse_byte_range()