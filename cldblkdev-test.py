import cldblkdev

BS = 4 * 1024

h = cldblkdev.open(False)

data = bytearray('a' * BS)


cldblkdev.pread(h, 9216, 132096)

exit(1)


cldblkdev.pwrite(h, data, 0)
ret_data = cldblkdev.pread(h, BS, 0)

if data != ret_data:
    print "Didn't read what was written: %d != %d" % (len(data), len(ret_data))
