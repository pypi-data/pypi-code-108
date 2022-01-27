import errno
import os


def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:  # Python >=3.2
        os.makedirs(path, exist_ok=True)  # pylint: disable=unexpected-keyword-arg
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
