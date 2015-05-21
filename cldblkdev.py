import sys

sys.path.append('/home/wspeirs/src/cldblkdev/')

import gcs

KB_4 = 4 * 1024

blks_on_server = set()
EMPTY_BLOCK = "\0" * KB_4


def open(readonly):
    global blks_on_server

    print "Got open call"
    h = gcs.get_gcs()

    blks_on_server = set(gcs.list(h))

    return h


def close():
    print "Got close call"


def get_size(h):
    return KB_4 * 256


def can_write(h):
    return True


def can_flush(h):
    return False


def is_rotational(h):
    return False


def can_trim(h):
    return True


def round_down(val):
    if val % KB_4 == 0:
        return val

    return val - (val % KB_4)


def pread(h, count, offset):
    ret = bytearray()

    print "Asked to read %d bytes starting at %d" % (count, offset)

    pad = offset % KB_4
    start = offset - pad
    end = (offset+count) + KB_4 - ((offset+count) % KB_4)

    for i in range(start, end+1, KB_4):
        print "Getting file %d" % i

        if i in blks_on_server:
            ret += gcs.get(h, str(i))[pad:]
        else:
            ret += EMPTY_BLOCK[pad:]

        pad = 0

    if len(ret) < count:
        print "Error, didn't read enough"

    return ret[:count]


def pwrite(h, buf, offset):
    count = len(buf)
    print "Asked to write %d bytes starting at %d" % (count, offset)
    print type(buf)

    if offset % KB_4 != 0:
        raise

    for i in range(0, count, KB_4):
        print "Putting file %d (%d -> %d)" % (i+offset, i, i+KB_4)
        gcs.put(h, str(i+offset), buf[i:i+KB_4])
        blks_on_server.add(i+offset)


def trim(h, count, offset):
    print "Asked to trim %d bytes starting at %d" % (count, offset)

    if offset % KB_4 != 0:
        raise

    for i in range(offset, offset+count, KB_4):
        print "Deleting file %d" % (i)
        gcs.delete(h, str(i))
        blks_on_server.remove(i)
