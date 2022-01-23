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

__all__ = ['OMFITcsv']

_defaults = {
    'delimiter': None,
    'comments': ['#', '!', '%'],
    'fmt': '%.18e',
    'missing_values': ['nan', 'NAN', "N/A", "???"],
    'filling_values': np.nan,
}


class OMFITcsv(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with Comma Separated Value files

    This class makes use of the np.genfromtxt and np.savetxt methods http://docs.scipy.org/doc/np/user/basics.io.genfromtxt.html

    :param filename: filename passed to OMFITascii class

    :param delimiter: delimiter character that is used to separate the values

    :param comments: charachter or list of characters that will be recognized as comments

    :param fmt: format used to save the data to file

    :param missing_values: The set of strings corresponding to missing data

    :param filling_values: The set of values to be used as default when the data are missing

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(
        self,
        filename,
        delimiter=_defaults['delimiter'],
        comments=_defaults['comments'],
        fmt=_defaults['fmt'],
        missing_values=_defaults['missing_values'],
        filling_values=_defaults['filling_values'],
        **kw,
    ):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        if delimiter == ' ':
            delimiter = None
        for k in _defaults:
            self.OMFITproperties.setdefault(k, eval(k))
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """
        with open(self.filename, 'r') as f:
            lines = f.read()

        # try to find out what is the comment used
        # and use pound as the default comment style
        if not isinstance(self.OMFITproperties['comments'], str):
            for comment in self.OMFITproperties['comments']:
                if comment in lines:
                    self.OMFITproperties['comments'] = comment
                    break
        if not isinstance(self.OMFITproperties['comments'], str):
            self.OMFITproperties['comments'] = self.OMFITproperties['comments'][0]

        self['data'] = np.array([])
        try:
            self['data'] = np.genfromtxt(
                self.filename,
                delimiter=self.OMFITproperties['delimiter'],
                comments=self.OMFITproperties['comments'],
                missing_values=self.OMFITproperties['missing_values'],
                filling_values=self.OMFITproperties['filling_values'],
                invalid_raise=True,
            )
        except Exception as _excp:
            try:
                tmpFile = []
                other = []
                nonochar = re.sub(r'[0-9\n\r\+-\. \teEdD' + re.escape(self.OMFITproperties['delimiter']) + ']', '', string.printable)
                with open(self.filename, 'r') as f:
                    for line in f.readlines():
                        if re.search('[' + nonochar + ']', line) is None:
                            tmpFile.append(line)
                        else:
                            other.append(line)

                tmp = OMFITascii('')
                with open(tmp.filename, 'w') as f:
                    f.writelines(tmpFile)

                try:
                    self['data'] = np.genfromtxt(
                        tmp.filename,
                        delimiter=self.OMFITproperties['delimiter'],
                        missing_values=self.OMFITproperties['missing_values'],
                        filling_values=self.OMFITproperties['filling_values'],
                        invalid_raise=True,
                    )

                except Exception:
                    self['data'] = np.genfromtxt(
                        tmp.filename,
                        delimiter=self.OMFITproperties['delimiter'],
                        skip_header=1,
                        missing_values=self.OMFITproperties['missing_values'],
                        filling_values=self.OMFITproperties['filling_values'],
                        invalid_raise=True,
                    )
                    with open(tmp.filename, 'r') as f:
                        header = f.readline()
                    with open(tmp.filename, 'w') as f:
                        f.writelines(header)
                    self['header'] = np.genfromtxt(
                        tmp.filename,
                        delimiter=self.OMFITproperties['delimiter'],
                        missing_values=self.OMFITproperties['missing_values'],
                        filling_values=self.OMFITproperties['filling_values'],
                        invalid_raise=True,
                    )

                self['other'] = other

            except Exception:
                self['data'] = np.genfromtxt(
                    self.filename,
                    delimiter=self.OMFITproperties['delimiter'],
                    comments=self.OMFITproperties['comments'],
                    missing_values=self.OMFITproperties['missing_values'],
                    filling_values=self.OMFITproperties['filling_values'],
                    invalid_raise=False,
                )

        self['data'] = np.atleast_2d(self['data'])
        # if there is no delimiter, then it's a vertical array and data should be transposed
        if (self.OMFITproperties['delimiter'] is None and ' ' not in lines) or (
            self.OMFITproperties['delimiter'] is not None and self.OMFITproperties['delimiter'] not in lines
        ):
            self['data'] = self['data'].T

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        if self.OMFITproperties['delimiter'] is None:
            np.savetxt(self.filename, self['data'], fmt=self.OMFITproperties['fmt'])
        else:
            np.savetxt(self.filename, self['data'], delimiter=self.OMFITproperties['delimiter'], fmt=self.OMFITproperties['fmt'])

    def __save_kw__(self):
        """
        :return: kw dictionary used to save the attributes to be passed when reloading from OMFITsave.txt
        """
        tmp = self.OMFITproperties.copy()
        for k in _defaults:
            if self.OMFITproperties[k] is _defaults[k] or self.OMFITproperties[k] == _defaults[k]:
                tmp.pop(k)
        return tmp
