try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise


from omfit_classes.omfit_path import OMFITpath

__all__ = ['OMFITascii']

class OMFITascii(OMFITpath):
    r"""
    OMFIT class used to interface with ASCII files

    :param filename: filename passed to OMFITobject class

    :param fromString: string that is written to file

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, **kw):
        fromString = kw.pop('fromString', None)
        OMFITpath.__init__(self, filename, **kw)
        if fromString is not None:
            with open(self.filename, 'wb') as f:
                if isinstance(fromString, bytes):
                    f.write(fromString)
                else:
                    f.write(fromString.encode('utf-8'))

    def read(self):
        '''
        Read ASCII file and return content

        :return:  string with content of file
        '''
        with open(self.filename, 'r') as f:
            return f.read()

    def write(self, value):
        '''
        Write string value to ASCII file

        :param value: string to be written to file

        :return: string with content of file
        '''
        with open(self.filename, 'w') as f:
            f.write(value)
        return value

    def append(self, value):
        '''
        Append string value to ASCII file

        :param value: string to be written to file

        :return: string with content of file
        '''
        with open(self.filename, 'a') as f:
            f.write(value)
        return self.read()
