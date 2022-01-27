import os


def list_jars(path, ends='.jar'):
    return [os.path.join(path, fn) for fn in os.listdir(path) if fn.endswith(ends)]


def load_options(fn):
    with open(fn, 'rt') as f:
        return [line.strip() for line in f if line.startswith('-')]
