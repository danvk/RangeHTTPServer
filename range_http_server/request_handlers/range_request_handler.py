import re


try:
    # Python3
    from http.server import SimpleHTTPRequestHandler

except ImportError:
    # Python 2
    from SimpleHTTPServer import SimpleHTTPRequestHandler

import os

MULTIPART_BOUNDARY_STRING = "python-boundary-string-1234"
class RangeRequestHandler(SimpleHTTPRequestHandler):
    """Adds support for HTTP 'Range' requests to SimpleHTTPRequestHandler

    The approach is to:
    - Override send_head to look for 'Range' and respond appropriately.
    - Override copyfile to only transmit a range when requested.
    """
    def send_head(self):
        if 'Range' not in self.headers:
            self.ranges = None
            return SimpleHTTPRequestHandler.send_head(self)
        try:
            self.ranges = parse_byte_range(self.headers['Range'])
        except ValueError as e:
            self.send_error(400, 'Invalid byte range')
            return None
        
        # Mirroring SimpleHTTPServer.py here
        path = self.translate_path(self.path)
        f = None
        ctype = self.guess_type(path)
        self.ctype = ctype
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, 'File not found')
            return None

        response_length = 0
        
        sent_response = False
        
        for range in self.ranges:

            first, last = range

            fs = os.fstat(f.fileno())
            file_len = fs[6]
            if first >= file_len:
                self.send_error(416, 'Requested Range Not Satisfiable')
                return None
            if last is None or last >= file_len:
                last = file_len - 1
                        
            value = 'bytes %s-%s/%s' % (first, last, file_len)
            
            message_length = last - first + 1
            
            if sent_response is False:
                self.send_response(206)
                if len(self.ranges) == 1:
                    self.send_header('Content-type', ctype)
                else:
                    self.send_header('Content-type', 'multipart/byteranges; boundary='+MULTIPART_BOUNDARY_STRING)
                sent_response = True
           
            if len(self.ranges) > 1:
                message_length += len( self.get_section_boundary_string(ctype, first, last, file_len) )
            
            response_length += message_length

            self.send_header('Content-Range',
                         value)
            
        if len(self.ranges) > 1:
            response_length += len(("\r\n--"+MULTIPART_BOUNDARY_STRING+"--").encode())
        
        self.send_header('Content-Length', str(response_length))
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        return SimpleHTTPRequestHandler.end_headers(self)

    def copyfile(self, source, outputfile):
        if not self.ranges:
            return SimpleHTTPRequestHandler.copyfile(self, source, outputfile)

        # SimpleHTTPRequestHandler uses shutil.copyfileobj, which doesn't let
        # you stop the copying before the end of the file.
        #start, stop = self.range  # set in send_head()
        #get total length from source

        total_byte_length = os.fstat(source.fileno())[6]
        for range in self.ranges:
            start, stop = range
            
            if len(self.ranges) > 1:
                boundary_string = self.get_section_boundary_string(self.ctype, start, stop, total_byte_length)
                outputfile.write(boundary_string.encode())

            copy_byte_range(source, outputfile, start, stop)
        
        if len(self.ranges) > 1:
            #copy in final boundary string
            outputfile.write(("\r\n--"+MULTIPART_BOUNDARY_STRING+"--").encode())

    def get_section_boundary_string(self, content_type, start, end, total):
        boundary_string = MULTIPART_BOUNDARY_STRING
        formatted_boundary_string = "\r\n--"+boundary_string+"\r\n"
        content_header = f"Content-Type: {content_type}\r\n"
        range_header = "Content-Range: bytes "+str(start)+"-"+str(end)+"/"+str(total)+"\r\n\r\n"
        return formatted_boundary_string+content_header+range_header

def copy_byte_range(infile, outfile, start=None, stop=None, bufsize=16*1024):
    """Like shutil.copyfileobj, but only copy a range of the streams.

    Both start and stop are inclusive.
    """
    if start is not None: infile.seek(start)
    while 1:
        to_read = min(bufsize, stop + 1 - infile.tell() if stop else bufsize)
        buf = infile.read(to_read)
        if not buf:
            break
        outfile.write(buf)


BYTE_RANGE_RE = re.compile(r'bytes=(\d+)-(\d+)?$')
def parse_byte_range(byte_range):
    """Returns the two numbers in 'bytes=123-456' or throws ValueError.

    The last number or both numbers may be None.
    """
    if byte_range.strip() == '':
        return [(None, None)]

    #get index of 'bytes=' str
    start = byte_range.index('bytes=')
    range_data = byte_range[start+6:]
    print(range_data)
    range_list = range_data.split(",")

    ranges = []
    for range in range_list:
        if len(range.split("-")) < 2:
            raise ValueError('Invalid byte range %s' % byte_range)
        first, last = [x and int(x) for x in range.split("-")]
        if last == '':
            last = None
        if last and last < first:
            raise ValueError('Invalid byte range %s' % byte_range)
        
        ranges.append((first, last))

    return ranges