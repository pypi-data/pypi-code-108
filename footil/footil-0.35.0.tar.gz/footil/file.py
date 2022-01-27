import tempfile


def WrittenNamedTemporaryFile(
    data,
    mode='w+b',
    buffering=-1,
    encoding=None,
    newline=None,
    suffix=None,
    prefix=None,
    dir=None,
    delete=True,
    seek=None,
        close=False):
    """Create NamedTeporaryFile and write data on it.

    It works the same as NamedTemporaryFile except that it also writes
    data on temp file, with possibility of changing stream position at
    the start and/or closing temp file (when for example it is not
    deleted and will be used later).

    Write mode must be used here.
    """
    f = tempfile.NamedTemporaryFile(
        mode=mode,
        buffering=buffering,
        encoding=encoding,
        newline=newline,
        dir=dir,
        prefix=prefix,
        suffix=suffix,
        delete=delete)
    f.write(data)
    if seek is not None:
        f.seek(seek)
    if close:
        f.close()
    return f
