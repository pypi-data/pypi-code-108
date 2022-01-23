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
from omfit_classes.utils_math import is_uncertain
from omfit_classes import namelist

from scipy import signal
import json

# Import both numpy and numpy as np to support evaluation of expressions
import numpy
import numpy as np

__all__ = ['OMFITjson', 'OMFITsettings', 'SettingsName']


def u2s(x, dctType):
    if isinstance(x, str):
        xs = x.encode('utf-8')
        if xs == x:
            return xs
    elif isinstance(x, list):
        return list([u2s(x, dctType) for x in x])
    elif isinstance(x, dict):
        return loader(list(x.items()), dctType)
    return x


# json loader/dumper are borrowed from OMAS
from omas.omas_utils import json_dumper

# customize json_dumper for OMFIT
def dumper(obj):
    if isinstance_str(obj, ['OMFITexpression', 'OMFITiterableExpression']):
        return evalExpr(obj)
    else:
        return json_dumper(obj)


from omas.omas_utils import json_loader

# customize json_loader for OMFIT
def loader(object_pairs, dctType):
    object_pairs = list([(u2s(o[0], dctType), u2s(o[1], dctType)) for o in object_pairs])
    return json_loader(object_pairs, dctType)


class OMFITjson(SortedDict, OMFITascii):
    """
    OMFIT class to read/write json files
    """

    baseDict = SortedDict

    def __init__(self, filename, use_leading_comma=None, add_top_level_brackets=False, **kw):
        r'''
        OMFIT class to parse json files

        :param filename: filename of the json file

        :param use_leading_comma: whether commas whould be leading

        :param add_top_level_brackets: whether to add opening `{` and closing `}` to string read from file

        :param \**kw: arguments passed to __init__ of OMFITascii
        '''
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.use_leading_comma = use_leading_comma
        self.add_top_level_brackets = add_top_level_brackets
        self.dynaLoad = True

    @property
    def use_leading_comma(self):
        return self.OMFITproperties['use_leading_comma']

    @use_leading_comma.setter
    def use_leading_comma(self, use_leading_comma):
        self.OMFITproperties['use_leading_comma'] = use_leading_comma

    @property
    def add_top_level_brackets(self):
        return self.OMFITproperties['add_top_level_brackets']

    @add_top_level_brackets.setter
    def add_top_level_brackets(self, add_top_level_brackets):
        self.OMFITproperties['add_top_level_brackets'] = add_top_level_brackets

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            tmp = f.read().strip()

        if not len(tmp):
            return

        if self.add_top_level_brackets:
            if not isinstance(self.add_top_level_brackets, str):
                raise ValueError("`add_top_level_brackets` should be either '{}' or '[]'")
            if "{" in self.add_top_level_brackets:
                tmp = "\n".join(["{", tmp.rstrip(','), "}"])
            elif "[" in self.add_top_level_brackets:
                tmp = "\n".join(["[", tmp.rstrip(','), "]"])
            else:
                raise ValueError("`add_top_level_brackets` should be either '{}' or '[]'")
            self.add_top_level_brackets = False

        self.update(json.loads(tmp, object_pairs_hook=lambda obj: loader(obj, self.baseDict)))

        # figure out if the style of this json is to have a leading comma
        if self.use_leading_comma is None:
            trailing_commas = tmp.count(',\n')
            leading_commas = re.subn('\n(\\s+),', '', tmp)[1]  # https://stackoverflow.com/a/1374893/6605826
            use_leading_comma = leading_commas > trailing_commas
            self.use_leading_comma = leading_commas > trailing_commas

    @dynaSave
    def save(self):
        with open(self.filename, 'w') as f:
            try:
                output = json.dumps(self, default=dumper, indent=1, separators=(',', ': '))
            except AttributeError as _excp:
                raise AttributeError(str(_excp) + ':\nMake sure that the dictionary entries ')
            if self.use_leading_comma:
                output = re.sub(r",\n(\s+)", r"\n\1,", output)
            f.write(output + '\n')

    def __save_kw__(self):
        """
        :return: kw dictionary used to save the attributes to be passed when reloading from OMFITsave.txt
        """
        tmp = self.OMFITproperties.copy()
        if 'use_leading_comma' in tmp and not tmp['use_leading_comma']:
            tmp.pop('use_leading_comma')
        if 'add_top_level_brackets' in tmp and not tmp['add_top_level_brackets']:
            tmp.pop('add_top_level_brackets')
        return tmp


class SettingsName(SortedDict):
    """
    Class used for dict-types under OMFITsettings
    """

    baseDict = None

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, self.baseDict):
            tmp = self.baseDict()
            tmp.update(value)
            value = tmp
        return super().__setitem__(key, value)

    def __repr__(self):
        # we use a simple dictionary representation of Settings
        # to allow nice editing of settings in the OMFIT GUIs
        return self.todict().__repr__()


SettingsName.baseDict = SettingsName


class OMFITsettings(OMFITjson):
    """
    OMFIT class to read/write modules settings
    """

    baseDict = SettingsName

    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self.caseInsensitive = True

    @dynaLoad
    def load(self):
        """
        load as json and if it fails, load as namelist
        """
        try:
            super().load()
        except Exception as _excp:
            tmp = namelist.NamelistFile(self.filename)
            self.update(tmp)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, self.baseDict):
            tmp = self.baseDict()
            tmp.update(value)
            value = tmp
        return super().__setitem__(key, value)


def sanitize_all_settings():
    for_all_modules(
        doThis='''
fname = os.path.split(moduleFile)[0] + os.sep + os.path.split(root['SETTINGS'].filename)[1]
root['SETTINGS']=OMFITsettings(fname)
root['SETTINGS'].load()
root['SETTINGS'].use_leading_comma = False
root['SETTINGS'].deploy(fname)
    ''',
        deploy=False,
        skip=False,
    )


############################################
if '__main__' == __name__:
    test_classes_main_header()

    settings = OMFITjson(OMFITsrc + '/../modules/EFIT/SettingsNamelist.txt', use_leading_comma=True)
    print('leading comma', settings.OMFITproperties.get('use_leading_comma', None))
