import struct
import zipfile
import time

from StringIO import StringIO

class ZipStreamer(object):
    def __init__(self):
        self.out_stream = StringIO()

        # write to the stringIO with no compression
        self.zipfile = zipfile.ZipFile(self.out_stream, 'w', zipfile.ZIP_STORED)

        self.current_file = None

        self._last_streamed = 0

    def put_file(self, name, date_time=None):
        if date_time is None:
            date_time = time.localtime(time.time())[:6]

        zinfo = zipfile.ZipInfo(name, date_time)
        zinfo.compress_type = zipfile.ZIP_STORED
        zinfo.flag_bits = 0x08
        zinfo.external_attr = 0600 << 16
        zinfo.header_offset = self.out_stream.pos

        # write right values later
        zinfo.CRC = 0
        zinfo.file_size = 0
        zinfo.compress_size = 0

        self.zipfile._writecheck(zinfo)

        # write header to stream
        self.out_stream.write(zinfo.FileHeader())

        self.current_file = zinfo

    def flush(self):
        zinfo = self.current_file
        self.out_stream.write(struct.pack("<LLL", zinfo.CRC, zinfo.compress_size, zinfo.file_size))
        self.zipfile.filelist.append(zinfo)
        self.zipfile.NameToInfo[zinfo.filename] = zinfo
        self.current_file = None

    def write(self, bytes):
        self.out_stream.write(bytes)
        self.out_stream.flush()
        zinfo = self.current_file
        # update these...
        zinfo.CRC = zipfile.crc32(bytes, zinfo.CRC) & 0xffffffff
        zinfo.file_size += len(bytes)
        zinfo.compress_size += len(bytes)

    def read(self):
        i = self.out_stream.pos

        self.out_stream.seek(self._last_streamed)
        bytes = self.out_stream.read()

        self.out_stream.seek(i)
        self._last_streamed = i

        return bytes

    def close(self):
        self.zipfile.close()
