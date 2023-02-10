# Import RangeHTTPServer from this project, not the global install.
import sys
sys.path = ['.'] + sys.path
import RangeHTTPServer

import pytest

from io import StringIO


def test_parse_byte_range():
    assert (0, 499) == RangeHTTPServer.parse_byte_range('bytes=0-499')
    assert (987, 1024) == RangeHTTPServer.parse_byte_range('bytes=987-1024')
    assert (None, None) == RangeHTTPServer.parse_byte_range('')
    assert (10, None) == RangeHTTPServer.parse_byte_range('bytes=10-')

    with pytest.raises(ValueError):
        RangeHTTPServer.parse_byte_range('bytes=abc')
    with pytest.raises(ValueError):
        RangeHTTPServer.parse_byte_range('characters=0-10')
    with pytest.raises(ValueError):
        RangeHTTPServer.parse_byte_range('bytes=100-2')


def test_copy_byte_range():
    inbuffer = StringIO(u'0123456789abcdefghijklmnopqrstuvwxyz')
    outbuffer = StringIO()

    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer, 4, 10)
    assert '456789a' == outbuffer.getvalue()

    outbuffer = StringIO()
    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer, 0, 4)
    assert '01234' == outbuffer.getvalue()

    outbuffer = StringIO()
    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer, 26)
    assert 'qrstuvwxyz' == outbuffer.getvalue()

    outbuffer = StringIO()
    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer, 0, 9, 10)
    assert '0123456789' == outbuffer.getvalue()

    inbuffer.seek(0)
    outbuffer = StringIO()
    RangeHTTPServer.copy_byte_range(inbuffer, outbuffer)
    assert '0123456789abcdefghijklmnopqrstuvwxyz' == outbuffer.getvalue()
