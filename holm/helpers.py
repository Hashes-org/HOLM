import hashlib


def file_get_contents(filename):
  with open(filename) as f:
    return f.read()


def file_sha1(fname):
  hash_sha1 = hashlib.sha1()
  with open(fname, "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
      hash_sha1.update(chunk)
  return hash_sha1.hexdigest()
