import pytomlpp


def read(fn):
    with open(fn, "r") as fid:
        return pytomlpp.loads(fid.read())


def write(d, fn):
    with open(fn, "w") as fid:
        fid.write(pytomlpp.dumps(d))
