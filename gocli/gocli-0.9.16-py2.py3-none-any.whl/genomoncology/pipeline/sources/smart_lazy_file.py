import tarfile

from click._compat import open_stream, get_streerror
from click.exceptions import FileError

from .const import TGZ_PATH_DELIMITER


class SmartLazyFile(object):
    """
    Built using LazyFile from Click project. Reference:
    https://github.com/pallets/click/blob/master/click/utils.py#L70
    """

    def __init__(
        self, filename, mode="r", encoding=None, errors="strict", atomic=False
    ):
        self.name = filename
        self.mode = mode
        self.encoding = encoding
        self.errors = errors
        self.atomic = atomic
        self.member_path = None

        if filename == "-":
            self._f, self.should_close = open_stream(
                filename, mode, encoding, errors
            )

        elif filename.startswith(f"tgz{TGZ_PATH_DELIMITER}"):
            assert "w" not in mode, "TGZ not supporting write mode."

            (_, file_path, member_path) = filename.split(TGZ_PATH_DELIMITER)
            tgz = tarfile.open(file_path)
            self.name = file_path
            self.member_path = member_path

            # note: decode(): tarball files come out as bytes not strings
            self._f = map(lambda x: x.decode(), tgz.extractfile(member_path))
            self.should_close = False

        else:
            if "r" in mode:
                # Open and close the file in case we're opening it for
                # reading so that we can catch at least some errors in
                # some cases early.
                open(filename, mode).close()
            self._f = None
            self.should_close = True

    def __getattr__(self, name):
        return getattr(self.open(), name)

    def __repr__(self):
        if self._f is not None:
            return repr(self._f)
        return "<unopened file %r %s>" % (self.name, self.mode)

    def open(self):
        """Opens the file if it's not yet open.  This call might fail with
        a :exc:`FileError`.  Not handling this error will produce an error
        that Click shows.
        """
        if self._f is not None:
            return self._f
        try:
            rv, self.should_close = open_stream(
                self.name,
                self.mode,
                self.encoding,
                self.errors,
                atomic=self.atomic,
            )
        except (IOError, OSError) as e:
            raise FileError(self.name, hint=get_streerror(e))
        self._f = rv
        return rv

    def close(self):
        """Closes the underlying file, no matter what."""
        if self._f is not None:
            self._f.close()

    def close_intelligently(self):
        """This function only closes the file if it was opened by the lazy
        file wrapper.  For instance this will never close stdin.
        """
        if self.should_close:
            self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close_intelligently()

    def __iter__(self):
        self.open()
        return iter(self._f)
