# Import RangeHTTPServer from this project, not the global install.
import sys
sys.path = ['.'] + sys.path
import RangeHTTPServer

from nose.tools import *
from StringIO import StringIO


def test_parse_byte_range():
    eq_((0, 499), RangeHTTPServer.parse_byte_range('bytes=0-499'))
    eq_((987, 1024), RangeHTTPServer.parse_byte_range('bytes=987-1024'))
    eq_((None, None), RangeHTTPServer.parse_byte_range(''))
    eq_((10, None), RangeHTTPServer.parse_byte_range('bytes=10-'))

    with assert_raises(ValueError):
        RangeHTTPServer.parse_byte_range('bytes=abc')
    with assert_raises(ValueError):
        RangeHTTPServer.parse_byte_range('characters=0-10')
    with assert_raises(ValueError):
        RangeHTTPServer.parse_byte_range('bytes=100-2')


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
