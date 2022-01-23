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

from omfit_classes.omfit_ascii import OMFITascii

__all__ = ['OMFITgingred']


class OMFITgingred(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with GINGRED input files

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.read()
        lines = lines.replace('{', '[')
        lines = lines.replace('}', ']')
        for line in lines.split('\n'):
            line = line.strip().split(';')[0].strip()
            if not len(line):
                continue
            key, value = line.split('=')
            try:
                self[key.strip()] = eval(value.strip())
            except NameError:
                pass

    @dynaSave
    def save(self):
        lines = []
        for key, value in list(self.items()):
            lines.append('%s = %s' % (key, value))
        lines = '\n'.join(lines)
        lines = lines.replace('[', '{')
        lines = lines.replace(']', '}')
        with open(self.filename, 'w') as f:
            f.write(lines)
