import sys

sys.path.append('/home/wspeirs/src/cldblkdev/')

import gcs

KB_4 = 4 * 1024


def open(readonly):
    print "Got open call"
    return gcs.get_gcs()


def close():
    print "Got close call"


def get_size(h):
    return 1000000000000  # 1 TB


def can_write(h):
    return True


def can_flush(h):
    return False


def is_rotational(h):
    return False


def can_trim(h):
    return True


def pread(h, count, offset):
    ret = []

    print "Asked to read %d bytes starting at %d" % (count, offset)

    if offset % KB_4 != 0:
        raise

    for i in range(offset, offset+count, step=KB_4):
        print "Getting file %d" % i
        ret += gcs.get(h, str(i))

    print "Returning %d bytes" % len(ret)

    if len(ret) != count:
        raise

    return ret


def pwrite(h, buf, offset):
    count = len(buf)
    print "Asked to write %d bytes starting at %d" % (count, offset)

    if offset % KB_4 != 0:
        raise

    for i in range(offset, offset+count, step=KB_4):
        print "Putting file %d (%d -> %d)" % (i, i, i+KB_4)
        gcs.put(h, str(i), buf[i:i+KB_4])


def trim(h, count, offset):
    print "Asked to trim %d bytes starting at %d" % (count, offset)

    if offset % KB_4 != 0:
        raise

    for i in range(offset, offset+count, step=KB_4):
        print "Deleting file %d" % (i)
        gcs.delete(h, str(i))
