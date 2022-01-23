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

import numpy as np
from astropy.io import ascii as asciitable

__all__ = ['OMFITasciitable']


class OMFITasciitable(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with ascii tables files

    This class makes use of the asciitable Python module http://cxc.harvard.edu/contrib/asciitable/

    Files can have a header preceeding the talbe (e.g. comment) and will be stored in the ['header'] field

    NOTE: the ['data'] field is a np.recarray and the data in the tables columns can be retrieved with the names defined in the ['columns'] field

    :param filename: filename passed to OMFITascii class

    :param skipToLine: (integer) line to skip to before doing the parsing

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.addedDot = False
        self.skipToLine = kw.get('skipToLine', 0)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """
        self['header'] = ''
        self['columns'] = []
        self['data'] = np.array([])

        with open(self.filename, 'r') as f:
            lines = f.read()

        if not len(lines.strip()):
            return

        if 'd' in lines.lower():
            # convert FORTRAN exponentials (d,D) to (e,E)
            lines = re.sub(r'([0-9]+|[0-9]*(?:[0-9]\.|\.[0-9])[0-9]*)[dD]([\-\+]*[0-9]+)', r'\1e\2', lines)
            with open(self.filename, 'w') as f:
                f.write(lines)

        lines = lines.splitlines(True)
        self['header'] = ''.join(lines[: self.skipToLine])
        lines = lines[self.skipToLine :]

        if len(lines):
            for k in range(len(lines)):
                tmp = ''.join(lines[k:])
                try:
                    if asciitable.__name__ == 'asciitable':
                        self['data'] = asciitable.read(tmp)
                    else:
                        self['data'] = np.array(asciitable.read(tmp, guess=True)).view(np.recarray)
                    self.addedDot = False
                    break
                except Exception:
                    tmp = '. ' + tmp
                    try:
                        if asciitable.__name__ == 'asciitable':
                            self['data'] = asciitable.read(tmp)
                        else:
                            self['data'] = np.array(asciitable.read(tmp, guess=True)).view(np.recarray)
                        self.addedDot = True
                        break
                    except Exception as _excp:
                        pass
            if k == len(lines):
                raise _excp

            self['columns'] = list(self['data'].dtype.names)
            self['header'] = self['header'] + ''.join(lines[:k])[:-1]
        self.dynaLoad = False

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        with open(self.filename, 'w') as f:
            if len(self['header']):
                f.write(self['header'] + '\n')

            if np.all(['col' in item for item in self['columns']]):
                if asciitable.__name__ == 'asciitable':
                    asciitable.write(self['data'], f, asciitable.NoHeader)
                else:
                    asciitable.write(self['data'], f, 'fixed_width_no_header', delimiter=' ')
            else:
                if asciitable.__name__ == 'asciitable':
                    asciitable.write(self['data'], f, asciitable.Basic)
                else:
                    asciitable.write(self['data'], f, 'fixed_width', delimiter=' ')


############################################
if '__main__' == __name__:
    test_classes_main_header()

    filename = 'omfit_asciitable_test.dat'
    data = OMFITasciitable(filename, fromString='a b c\n1 2 3')
    data.load()
    data.save()
