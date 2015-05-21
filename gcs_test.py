import gcs


h = gcs.get_gcs()

print gcs.list(h)

print 'OBJ: ' + gcs.get(h, 'test')

gcs.put(h, 'test2', 'something')

gcs.delete(h, 'test2')