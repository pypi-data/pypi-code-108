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
from omfit_classes import namelist

import configobj

__all__ = ['OMFITiniSection', 'OMFITini']


class OMFITiniSection(SortedDict):
    def __init__(self):
        SortedDict.__init__(self, caseInsensitive=True)

    def __delitem__(self, key):
        super().__delitem__(key)
        if '__' + key + '__' in self:
            super().__delitem__('__' + key + '__')

    def _cast(self, data):
        for k in list(data.keys()):
            if isinstance(data[k], dict):
                self[k] = OMFITiniSection()._cast(data[k])
            else:
                self[k] = data[k]
            if k in data.comments and len(data.comments[k]):
                self['__' + k + '__'] = data.comments[k]

        if hasattr(data, 'initial_comment'):
            self.insert(0, '__header__', data.initial_comment)

        return self

    def _uncast(self, data=None, parent=None, depth=None, main=None):
        if data is None:
            main = tmp = configobj.ConfigObj(infile=[], indent_type='    ')
            data = self
            depth = 0
        else:
            tmp = configobj.Section(parent, depth, main)

        for k in self.keys(filter=hide_ptrn, matching=False):
            if isinstance(self[k], OMFITiniSection):
                tmp[k] = self[k]._uncast(self[k], tmp, depth + 1, main)
            else:
                tmp[k] = self[k]

        for k in self.keys(filter=hide_ptrn, matching=True):
            if k != '__header__':
                tmp.comments[k[2:-2]] = self[k]
            else:
                tmp.initial_comment = self[k]

        return tmp

    @staticmethod
    def _translate(self, key):
        """
        This method recursively substitute the ${...} values
        to evaluate the actual string of the expression
        (used for evaluating variables in IPS configuration files)

        :param key: key to be evaluated
        """
        if not isinstance(self[key], str) or '$' not in self[key]:
            return self[key]

        c1 = re.compile(r'\$([^{]\w+)([ /]*)')
        c2 = re.compile(r'\${(\w*)}')
        tmp = self[key]
        while '$' in tmp:
            tmp = re.sub(c1, r'${\1}\2', tmp)
            m = re.search(c2, tmp)
            tmp = tmp[: m.start()] + str(self._ask(m.expand(r'\1'))) + tmp[m.end() :]
        tmp = re.sub(r'\|start\|(.*)\|end\|', r'${\1}', tmp)
        return tmp

    def _ask(self, key):
        if key in self:
            return self[key]
        elif isinstance(self._OMFITparent, OMFITiniSection):
            return self._OMFITparent._ask(key)
        else:
            return '|start|' + key + '|end|'

    def translate(self, key=None):
        if key is not None:
            tmp = self._translate(self, key)
        else:
            tmp = copy.deepcopy(self)
            tmp.walk(self._translate)
        return tmp


class OMFITini(OMFITiniSection, OMFITascii):
    r"""
    OMFIT class used to interface with configuration files (INI files).
    This types of files are used by codes such as IMFIT and IPS

    This class is based on the configobj class https://configobj.readthedocs.io/en/latest/index.html

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self, caseInsensitive=True)
        self.list_values = True
        self.dynaLoad = True

    @staticmethod
    def _interpret(section, key):
        section[key] = namelist.interpreter(section[key], escaped_strings=False)

    @staticmethod
    def _encode(section, key):
        section[key] = namelist.encoder(section[key], escaped_strings=False, dotBoolean=False)

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """
        tmp = configobj.ConfigObj(self.filename, list_values=self.list_values)
        tmp.walk(self._interpret)
        self.clear()
        self._cast(tmp)

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        tmp = self._uncast()
        tmp.filename = self.filename
        tmp.walk(self._encode)
        tmp.write()


############################################
if '__main__' == __name__:
    test_classes_main_header()

    tmp = OMFITini(f'{OMFITsrc}/../modules/EPED/eped.config')
    tmp.load()
