"""
Contains classes and utility/support functions for parsing DIII-D patch panel files
"""

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

import struct
import numpy as np
from omfit_classes.omfit_ascii import OMFITascii

__all__ = ['OMFITpatch', 'OMFITpatchObject', 'OMFITpatchList']


def lrl(item):
    """Shortcut to avoid writing list(range(len(...))) so many times. Does special format for long lists."""
    if len(item) > 5:
        return '0:{}'.format(len(item) - 1)
    return '{}'.format(list(range(len(item))))


class OMFITpatchList(list):
    """
    Handles list-like data within patch panels.

    __setitem__ notifies parent object of new assignment so values index/name pairs can be kept self consistent.
    Without this intervention, a list's element can be changed without changing the list itself and so the parent
    OMFITpatchObject instance gets no notification, and lists of chopper indices and chopper names can get out of sync.
    """

    def __init__(self, *args, **kw):
        self.OMFITproperties = {}
        parent = kw.pop('parent', None)
        assert isinstance(parent, (OMFITpatchObject, OMFITpatch)), 'parent object should be OMFITpatch or OMFITpatchObject'
        list.__init__(self, *args)
        self.parent = parent

    @property
    def parent(self):
        return self.OMFITproperties.get('parent', None)

    @parent.setter
    def parent(self, value):
        self.OMFITproperties['parent'] = value

    def __setitem__(self, idx, value):
        pkey = [k for k in self.parent if self.parent[k] is self][0]
        new_list = [v for v in self]
        new_list[idx] = value
        self.parent.__setitem__(pkey, new_list)

    def __copy__(self):
        """
        Instead of a true copy, return a mundane list.
        Special properties exist in relation to parent only, and that relationship can't be guaranteed during copy.
        """
        return [v for v in self]

    def __deepcopy__(self, memo):
        """
        Instead of a true copy, return a mundane list.
        Special properties exist in relation to parent only, and that relationship can't be guaranteed during copy.
        """
        return [copy.deepcopy(v) for v in self]


class OMFITpatchObject(SortedDict, OMFITobject):
    """
    Handles objects within a patch panel (such as a single F coil) and keeps indices & names consistent with each other
    """

    rail_map = ['E supply', 'VFI', '?', '']  # Maps rail_name to rail_index
    power_supply_map = {  # Maps power_supply_name to power_supply_index. Values < 1 are special & affect chopper, too.
        -3: '',  # RV2 or RV1
        0: '',  # SHORT
        1: 'D',
        2: 'V',
        3: 'T1',
        4: 'T2',
        5: 'HV1',
        6: 'HV2',
        8: 'D2',
    }
    # If the first chopper is 0, then it's named 'SHORT'. Otherwise, it's '' for unused.
    # If dealing with key 'cl' instead of an F-coil, it's 'OPEN'.
    chopper_map = (
        ['?']
        + ['X{}'.format(i + 1) for i in range(20)]
        + ['HX{}'.format(i + 1) for i in range(16)]
        + ['RV1', 'RV2']
        + ['?39', '?40', '?41', 'FSUP']
    )
    direction_map = ['', 'PUSH', 'PULL']

    allowed_choppers = {
        '1A': list(range(0, 21)) + [37, 38],
        '1B': list(range(0, 21)) + [37, 38],  # All X, RV1, RV2
        '2A': list(range(0, 21)) + [37, 38],
        '2B': list(range(0, 21)) + [37, 38],  # All X, RV1, RV2
        '3A': list(range(0, 21)) + [37, 38],
        '3B': list(range(0, 21)) + [37, 38],  # All X, RV1, RV2
        '4A': list(range(0, 21)) + [37, 38],
        '4B': list(range(0, 21)) + [37, 38],  # All X, RV1, RV2
        '5A': list(range(0, 21)) + [37, 38],
        '5B': list(range(0, 21)) + [37, 38],  # All X, RV1, RV2
        '6A': [0] + list(range(5, 13)) + list(range(21, 29)) + list(range(31, 37)),
        '6B': [0] + list(range(5, 13)) + list(range(21, 31)) + list(range(33, 37)),
        '7A': [0] + list(range(5, 13)) + list(range(21, 29)) + list(range(31, 37)),
        '7B': [0] + list(range(5, 13)) + list(range(21, 31)) + list(range(33, 37)),
        '8A': [0] + list(range(5, 13)) + [19, 20] + list(range(21, 27)) + list(range(31, 35)) + [37, 38],
        '8B': [0] + list(range(5, 13)) + [19, 20] + list(range(21, 27)) + list(range(33, 37)) + [37, 38],
        '9A': [0] + list(range(5, 13)) + [19, 20] + list(range(21, 27)) + list(range(31, 35)) + [37, 38],
        '9B': [0] + list(range(5, 13)) + [19, 20] + list(range(21, 27)) + list(range(33, 37)) + [37, 38],
        'cl': [0, 42],  # Leave it open or use FSUP to connect D-supply
        'HV1': list(range(21, 37)),
        'HV2': list(range(21, 37)),  # All HX choppers
        'D': list(range(1, 30)) + [42],  # All X, HX1-9 and FSUP to C-coils
        'V': list(range(1, 30)),  # All X, HX1-9
        'T1': list(range(1, 21)),  # All X choppers
        'T2': list(range(1, 21)) + list(range(21, 28)),  # All X, HX1-7
        'D2': list(range(1, 30)),  # All X choppers, HX1-9
    }
    cmc = {'{}{}'.format(i, a): 3 for i in [1, 2, 3, 4, 5, 8] for a in 'AB'}
    cmc['9A'] = cmc['9B'] = 4
    cmc['6A'] = cmc['6B'] = cmc['7A'] = cmc['7B'] = 6
    cmc['cl'] = 1
    chopper_max_counts = cmc

    lonely_choppers = [37, 38, 42]  # These chopper-like items aren't allowed to be in parallel with anything

    def __init__(self, filename=None, **kw):
        self.OMFITproperties = {}
        self.locked = False
        OMFITobject.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.filename = filename  # This doesn't actually have a filename; it just can't be missing.
        return

    @property
    def locked(self):
        return self.OMFITproperties.get('locked', None)

    @locked.setter
    def locked(self, value):
        self.OMFITproperties['locked'] = value
        return

    def __copy__(self):  # https://stackoverflow.com/a/48339837/6605826
        """
        Special copy method that unlocks, does copy, then restores locked status.
        Without the unlock first, there can be an infinite loop as the special __setitem__ fights itself.
        """
        result = OMFITpatchObject()
        result.locked = False
        for k, v in self.items():
            result[k] = self[k]
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):  # https://stackoverflow.com/a/15774013/6605826
        """
        Special copy method that unlocks, does copy, then restores locked status.
        Without the unlock first, there can be an infinite loop as the special __setitem__ fights itself.
        """
        result = OMFITpatchObject()
        memo[id(self)] = result
        result.locked = False
        for k, v in self.items():
            result[copy.deepcopy(k)] = copy.deepcopy(self[k])
            if isinstance(self[k], OMFITpatchList):
                result[k] = OMFITpatchList(result[k], parent=result)

        for k, v in self.__dict__.items():
            if k in ['parent', '_OMFITparent']:
                setattr(result, k, None)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def __setitem__(self, key, value):
        """
        The point of this special setitem method is to keep names and indices in sync.
        For example, changing 'rail_name' will also change 'rail_index'.
        If you want to mess with the file without synchronized updates taking place,
        unlock by setting self.locked = False and then this method will pass through
        to the super class's setitem method.
        :param key:
            Key for looking up stuff in self
        :param value:
            Value to assign to self[key]
        :return: None
        """
        if not getattr(self, 'locked', False):
            # This instance is unlocked, so don't do synchronized updates.
            SortedDict.__setitem__(self, key, value)
            return

        # Handle power supply rails
        if key == 'rail_name':
            other_key = 'rail_index'
            if value not in self.rail_map:
                raise ValueError('Invalid power rail name: {}. Valid = {}'.format(value, repr(self.rail_map)))
            if value == '':
                other_value = 3  # This is for D supply on C coils, which is a special case.
                # There may be other weird setups
            else:
                other_value = self.rail_map.index(value)
        elif key == 'rail_index':
            value = int(value)
            other_key = 'rail_name'
            if (value >= len(self.rail_map)) or (value < 0):
                raise ValueError('Invalid power rail index: {}. Valid = {}'.format(value, lrl(self.rail_map)))
            other_value = self.rail_map[value]

        # Handle current directions
        elif key == 'direction_name':
            other_key = 'direction_index'
            if value not in self.direction_map:
                raise ValueError('Invalid current direction name: {}. Valid = {}'.format(repr(value), repr(self.direction_map)))
            other_value = self.direction_map.index(value)
        elif key == 'direction_index':
            value = int(value)
            other_key = 'direction_name'
            if (value >= len(self.direction_map)) or (value < 0):
                raise ValueError('Invalid current dir index: {}. Valid = {}'.format(value, lrl(self.direction_map)))
            other_value = self.direction_map[value]

        # Handle choppers
        elif key == 'chopper_name':
            other_key = 'chopper_index'
            for val in value:
                if val not in (self.chopper_map + ['', 'SHORT', 'OPEN', 'SHOR']):
                    raise ValueError('Invalid chopper name: {}. Valid = {}'.format(repr(val), repr(self.chopper_map)))
            other_value = [self.chopper_map.index(val) if val in self.chopper_map else 0 for val in value]
            new_count = np.sum([ov != 0 for ov in other_value])
            SortedDict.__setitem__(self, 'chopper_count', new_count)
            if ('power_supply_name' in self) and (self['power_supply_name'] == ''):
                new_power_supply_index = 0 if other_value[0] == 0 else -3
                SortedDict.__setitem__(self, 'power_supply_index', new_power_supply_index)
        elif key == 'chopper_index':
            value = [int(val) for val in value]
            other_key = 'chopper_name'
            for val in value:
                if (val >= len(self.chopper_map)) or (val < 0):
                    raise ValueError('Invalid chopper index: {}. Valid = {}'.format(val, lrl(self.chopper_map)))
            other_value = [self.chopper_map[val] for val in value]
            # Resolve stuff stored in the 0 index
            if other_value[0] == '?':
                if self['coil_index'] == 19:
                    other_value[0] = 'OPEN'
                else:
                    other_value[0] = 'SHORT'
            for i in range(1, len(other_value)):
                if other_value[i] == '?':
                    other_value[i] = ''
            new_count = np.sum([ov != '' for ov in other_value])
            SortedDict.__setitem__(self, 'chopper_count', new_count)
            if self['power_supply_name'] == '':
                new_power_supply_index = 0 if value[0] == 0 else -3
                SortedDict.__setitem__(self, 'power_supply_index', new_power_supply_index)
        elif key == 'chopper_count':
            raise ValueError('Do not change chopper count manually')

        # Handle power supplies
        elif key == 'power_supply_name':
            other_key = 'power_supply_index'
            if value not in list(self.power_supply_map.values()):
                raise ValueError(
                    'Invalid power supply name: {}. Valid = {}'.format(repr(value), repr(list(self.power_supply_map.values())))
                )
            other_value = [k for k, v in self.power_supply_map.items() if v == value]
            # Resolve possible duplicates that have '' as the value
            if (self['chopper_index'][0] > 36) and (0 in other_value):
                other_value = [ov for ov in other_value if ov < 0]
            elif (self['chopper_index'][0] == 0) and (min(other_value) < 0):
                other_value = [ov for ov in other_value if ov >= 0]
            if len(other_value) == 1:
                other_value = other_value[0]
            else:
                raise ValueError('Values in power supply map should be unique after handling values of ""')
        elif key == 'power_supply_index':
            other_key = 'power_supply_name'
            if value not in self.power_supply_map:
                raise ValueError('Invalid power supply index: {}. Valid = {}'.format(value, repr(list(self.power_supply_map.keys()))))
            other_value = self.power_supply_map[value]

        # Contingency
        else:
            other_key = other_value = None

        # The OMFITpatchList class notifies its parent when an element is updated, so replace lists with that.
        if isinstance(value, list):
            value = OMFITpatchList(value, parent=self)
        if isinstance(other_value, list):
            other_value = OMFITpatchList(other_value, parent=self)

        # Write the new values to self
        SortedDict.__setitem__(self, key, value)
        if other_key is not None and other_value is not None:
            SortedDict.__setitem__(self, other_key, other_value)

        # Update status
        if (getattr(self, '_OMFITparent', None) is not None) and self.locked:
            self._OMFITparent.check()

        return None

    def __tree_repr__(self):
        """Provides custom tree representation for this object"""
        try:
            patch_type = self._OMFITparent.patch_type
        except AttributeError:
            patch_type = '?'

        if patch_type in ['F', 'P']:
            chopper_note = self['chopper_name'][0] if self['chopper_count'] == 1 else '{} choppers'.format(self['chopper_count'])
            tree_repr = '{rail:10s} {ps:8s} {dir:8s} {chopper_note:}'.format(
                rail=self['rail_name'], ps=self['power_supply_name'], dir=self['direction_name'], chopper_note=chopper_note
            )
        elif patch_type == 'I':
            tree_repr = []
            if 'c_coil_parity' in self:
                tree_repr += ['C parity: {}'.format(self['c_coil_parity'])]
            if 'i_coil_file' in self:
                tree_repr += ['I-coils: {}'.format(self['i_coil_file'])]
            if np.all([a in self for a in ['slot', 'sign', 'spa', 'c_idx', 'coil']]):
                tree_repr += ['{slot:2s} {sign:3s} {spa:4s} {c_idx:1d} {coil:}'.format(**self)]
            if np.all(['AA{}'.format(i) in self for i in range(1, 13)]):
                aa = []
                for i in range(1, 13):
                    if self['AA{}'.format(i)]:
                        aa += ['AA{}:{}'.format(i, self['AA{}'.format(i)])]
                tree_repr += aa if aa else ['No AA used']

            tree_repr = ', '.join(tree_repr)
        else:
            tree_repr = None
        return tree_repr, []


# List attributes which need to be saved with projects.
OMFITpatch_save_attrs = [
    'debug_topic',
    'patch_type',
    'auto_clean',
    'status',
    'contents',
    'original_contents',
    'patch_name',
    'original_patch_name',
    'original_patch_type',
    'fpconvert',
    'shot',
    '_load_complete',
    'server',
    'tunnel',
    'remote_dir',
    'work_dir',
    # Deliberately not listed:
    # 'problems',
]


class OMFITpatch(SortedDict, OMFITascii):
    """
    Parses DIII-D PCS patch panel files.

    Several types of files are recognized:
    - Type-F: F-coil patch panel in ASCII archival format.
    - Type-P: F-coil patch panel in binary format. Can be converted to type-F by
      changing .patch_type attribute and executing .add_c_coil() method. May be obsolete.
    - Type-I: I&C coil patch panel in ASCII format.

    """

    # Define the marker for P-files with binary data. Also split them here.
    bin_mark = r'\x00'

    def __getattr__(self, attr_name):
        """
        Custom attribute access method.
        There are too many funky attributes and I don't want to do a @property
        declaration for each one, so we're doing this instead.
         - https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access
         - https://stackoverflow.com/a/52729406/6605826

        :param attr_name: string
            Name of the attribute

        :return: Attribute value
        """
        if attr_name in OMFITpatch_save_attrs:
            return self.OMFITproperties.get(attr_name, None)
        return SortedDict.__getattr__(self, attr_name)

    def __setattr__(self, attr_name, value):
        """
        Allows handling of a large number of attributes without @property declarations
        :param attr_name: string
        :param value:
        :return: None
        """
        if attr_name in OMFITpatch_save_attrs:
            self.OMFITproperties[attr_name] = value
            if attr_name.startswith('custom_'):
                # Setting a custom attribute should update the attribute it overrides, as it does in init
                setattr(self, attr_name[len('custom_') :], value)
            return
        SortedDict.__setattr__(self, attr_name, value)
        return

    def __delattr__(self, attr_name):
        """
        Allows handling of a large number of attributes without @property declarations
        :param attr_name: string
        :return: None
        """
        if attr_name in OMFITpatch_save_attrs:
            self.OMFITproperties[attr_name] = None
            if attr_name.startswith('custom_'):
                # Deleting a custom attribute should revert its counterpart to default
                setattr(self, attr_name[len('custom_') :], getattr(self, 'default_' + attr_name[len('custom_') :], None))
            return
        SortedDict.__delattr__(self, attr_name)
        return

    def __init__(
        self,
        filename=None,
        shot=None,
        patch_type=None,
        debug_topic='OMFITpatch',
        auto_clean=True,
        fpconvert=True,
        server=None,
        tunnel=None,
        work_dir=None,
        remote_dir=None,
        default_patch_type='F',
        **kw,
    ):
        """
        :param filename: string [optional if shot is provided]
            Filename of original source file, including path. This will be preserved as
            self.source_file, even if the class updates to a temporary file copy.
            If shot is provided, filename controls output only; no source file is read.
            In this case, filename need not include path.

        :param shot: int [optional if filename is provided]
            Shot number to use to look up patch data. Must provide patch_type when using shot.
            If a filename is provided as well, shot will be used for lookup and filename will control output only.

        :param patch_type: None or string
            None lets the class auto-assign, which should be fine.
            You can force it explicitly if you really want to.

        :param debug_topic: string
            Topic keyword to pass to printd. Allows all printd from the class to be consistent.

        :param auto_clean: bool
            Run cleanup method after parsing. This will remove some problems,
            but prevent exact recovery of problematic original contents.

        :param fpconvert: bool
            Automatically convert type P files into type F so they can be saved.

        :param server: string [optional if running in OMFIT framework]
            Complete access instruction for server that runs viwhed, like "eldond@iris.gat.com:22"

        :param tunnel: string [optional if running in OMFIT framework]
            Complete access instruction for tunnel used to reach server, like "eldond@cybele.gat.com:2039".
            Use empty string '' if no tunnel is needed.

        :param work_dir: string  [optional if running in OMFIT framework]
            Local working directory (temporary/scratch) for temporary files related to remote executable calls

        :param remote_dir: string  [optional if running in OMFIT framework]
            Remote working directory (temporary/scratch) for temporary files related to remote executable calls

        :param default_patch_type: string
            Patch panel type to assign if auto detection fails, such as if you're initializing a blank patch panel file.
            If you are reading a valid patch panel file, auto detection will probably work because it is very good.
            Please choose from 'F' or 'I'. 'P' is a valid patch_type, but it's read-only so it's a very bad choice for
            initializing a blank file to fill in yourself.

        :param kw: Other keywords passed to OMFITascii
        """
        self.OMFITproperties = {}
        self.source_file = copy.copy(filename) if shot is None else shot
        SortedDict.__init__(self)
        if filename is None:
            fn = funny_random_name_generator(patch_type == 'I')
        elif filename.endswith(os.sep):
            fn = filename + funny_random_name_generator(patch_type == 'I')
        else:
            fn = filename
        if os.sep in fn:
            from pathlib import Path

            Path(fn).touch()  # OMFITobjects don't like getting a filename with a path unless the file exists
        OMFITascii.__init__(self, fn, **kw)
        self._load_complete = kw.pop('_load_complete', False)
        self.shot = shot
        self.server = server
        self.tunnel = tunnel
        self.remote_dir = remote_dir
        self.work_dir = work_dir
        self.debug_topic = debug_topic
        self.status = 'init'
        self.auto_clean = auto_clean
        self.fpconvert = fpconvert
        self.patch_type = patch_type
        if ((shot is None) or self._load_complete) and (filename is not None):
            try:
                with open(self.filename, 'r') as f:
                    self.contents = f.read()
            except UnicodeDecodeError:
                with open(self.filename, 'rb') as f:
                    self.contents = str(f.read())
        elif shot is not None:
            self.contents = self._read_shot(default_patch_type)
        else:
            self.contents = ''
        self.original_contents = copy.copy(self.contents)
        self.patch_type = self._guess_patch_type(default=default_patch_type) if patch_type is None else patch_type
        self.original_patch_type = copy.copy(self.patch_type)
        self.patch_name = getattr(self, 'patch_name', None)  # Allows for possibility that it was set by OMFITproperties
        if self.patch_type == 'F':
            if (self.shot is None) or self._load_complete:
                # The type-F method is suitable from a type-F FILE or from contents from a shot after parsing
                self._read_type_f()
            else:
                # The type-P method is suitable for contents read directly from a shot
                self._read_type_p_inner(self.contents)
                if self.auto_clean:
                    self.printq('Running automatic cleanup of F-patch file to remove junk chopper data')
                    self._clean_type_f()
        elif self.patch_type == 'P':
            self._read_type_p()
        elif self.patch_type == 'I':
            if (self.shot is None) or self._load_complete:
                self._read_type_i()
            else:
                self._read_type_j()
        else:
            raise ValueError('Invalid or unhandled patch panel file.')
        self.check()
        self.original_patch_name = copy.copy(self.patch_name)
        self.problems = []

        if self.filename is None and self.patch_name is not None:
            # This must've been read in from a shot numbers instead of a file. Let's make a real filename.
            # Generate a temporary directory name
            subprocess_dir = '_'.join(map(str, OMFITaux['prun_process']))
            if len(subprocess_dir):
                subprocess_dir = '__p' + subprocess_dir
            directory = (
                OMFITcwd + os.sep + 'objects' + os.sep + 'file_' + utils_base.now("%Y-%m-%d__%H_%M" + subprocess_dir + os.sep + "%S__%f")
            )
            while os.path.exists(directory):
                directory += "_"
            # Assign the new filename
            self.filename = directory + os.sep + self.patch_name
            if self.patch_type in ['I', 'F']:
                if not os.path.exists(self.filename):
                    os.makedirs(os.path.split(self.filename)[0])
                self.save()
            self.printq('Auto-assigned filename {}'.format(self.filename))

        # Make sure all saved attributes are restored by allowing them to be passed in through **kw
        for attr in OMFITpatch_save_attrs:
            kw_attr = kw.pop(attr, None)
            if kw_attr is not None:
                setattr(self, attr, kw_attr)

        if ((filename is None) or filename.endswith(os.sep)) and self.patch_name is not None:
            # Replace "working title" filename with good patch name if we were able to find one
            self.filename = self.patch_name if filename is None else filename + self.patch_name
        self._load_complete = True  # Prevents instance from saved project from re-doing read from shot or whatever
        return

    def __tree_repr__(self):
        """Forms strings to display in OMFIT tree GUI to represent instances of this class"""
        file_rep = OMFITascii.__tree_repr__(self)[0]
        tree_rep = file_rep + ', STATUS: {}, PATCH TYPE: {}, NAME: {}'.format(self.status, self.patch_type, self.patch_name)
        return tree_rep, []

    def _read_shot(self, default_patch_type):
        """Reads patch data from a shot number"""

        if (self.patch_type is None) and (default_patch_type in ['F', 'I', 'P']):
            self.patch_type = default_patch_type
            self.original_patch_type = default_patch_type
            self.printq('Assigned patch_type to default ("{}") while reading from shot.'.format(default_patch_type))

        if self.patch_type in ['F', 'P']:
            patch_code = 'PATCH'
        elif self.patch_type == 'I':
            patch_code = 'SPATCH'
        else:
            raise ValueError(
                'Bad patch_type={}. Please specify patch_type="I" or patch_type="F". True automatic patch_type '
                'determination is not possible when reading from a shot number.'.format(repr(self.patch_type))
            )

        executable = 'module load defaults\nviwhed'
        interactive = ['sh {}'.format(self.shot), 'na {}'.format(patch_code), 'df', 'ex']
        stdout_catch = []
        stderr_catch = []
        self._set_default_server_info()
        import omfit_classes.OMFITx as OMFITx

        OMFITx.executable(
            None,
            [],
            [],
            server=self.server,
            tunnel=self.tunnel,
            remotedir=self.remote_dir,
            workdir=self.work_dir,
            std_out=stdout_catch,
            std_err=stderr_catch,
            executable=executable,
            interactive_input='\n'.join(interactive),
        )
        i = 0
        props = 'server = {server:}, tunnel = {tunnel:}, remote_dir = {remote_dir:}, work_dir = {work_dir:}'.format(**self.OMFITproperties)

        while (i < len(stdout_catch)) and (' ASCII -' not in stdout_catch[i]):
            i += 1
        if i == len(stdout_catch):
            printe('ERROR in OMFITpatch._read_shot: Reached end of stdout without finding expected ASCII marker!')
            print('-' * 79)
            print('\n'.join(stdout_catch))
            print('-' * 79)
            print(props)
            raise ValueError('Reached end of stdout without finding expected ASCII marker!')
        j = i + 1
        while (j < len(stdout_catch)) and (' INT16 - ' not in stdout_catch[j]):
            j += 1
        if i == len(stdout_catch):
            printe('ERROR in OMFITpatch._read_shot: Reached end of stdout without finding expected INT16 marker!')
            print('-' * 79)
            print('\n'.join(stdout_catch))
            print('-' * 79)
            print(props)
            raise ValueError('Reached end of stdout without finding expected INT16 marker!')

        return ''.join([line.split('"')[1] for line in stdout_catch[i + 1 : j]])

    def _set_default_server_info(self):
        """If any of server, tunnel, work_dir, or remote_dir are None, update them with default values"""
        import getpass

        server_name = 'iris'  # The server options are VERY limited. It's okay to leave this at just iris.
        if None in [self.server, self.tunnel, self.remote_dir, self.work_dir]:
            # Need to load defaults
            dir_suffix = os.sep + str(datetime.datetime.now()).replace(' ', '_').replace(':', '_')
            # noinspection PyBroadException
            try:
                default_server = evalExpr(OMFIT['MainSettings']['SERVER'][server_name]['server'])
                default_remote_dir = evalExpr(OMFIT['MainSettings']['SERVER'][server_name]['workDir']) + dir_suffix
                localhost = evalExpr(OMFIT['MainSettings']['SERVER']['localhost'])
                if isinstance(localhost, str):
                    localhost = evalExpr(OMFIT['MainSettings']['SERVER'][localhost])
                default_work_dir = evalExpr(localhost['workDir']) + dir_suffix
                default_tunnel = evalExpr(OMFIT['MainSettings']['SERVER'][server_name]['server'])
            except Exception:
                # This plan used to be relevant, but maybe not anymore?
                # It might trigger on KeyError for 'MainSettings' not being in OMFIT, if that can ever happen
                self.printq(
                    'Failed to reference OMFIT MainSettings. Guessing default settings for remote server access. '
                    'If these do not work, try specifying server, tunnel, remote_dir, and work_dir next time.'
                )
                username = getpass.getuser()
                default_server = '{}@iris.gat.com:22'.format(username)
                default_tunnel = '{}@cybele.gat.com:2039'.format(username)
                default_work_dir = tempfile.mkdtemp('_OMFIT_patch_read_shot') + os.sep
                default_remote_dir = os.sep.join(['cluster-scratch', username, 'OMFIT', dir_suffix])
            self.server = default_server if self.server is None else self.server
            self.tunnel = default_tunnel if self.tunnel is None else self.tunnel
            self.remote_dir = default_remote_dir if self.remote_dir is None else self.remote_dir
            self.work_dir = default_work_dir if self.work_dir is None else self.work_dir
        else:
            self.printq('server, work_dir, and remote_dir settings are already good; no need to load defaults')

    def check(self):
        """Checks for problems and returns a status string that is either 'OKAY' or a list of problems."""
        if self.patch_type in ['F', 'P']:
            status = self._check_type_f()
        else:
            status = '?'
        self.status = status
        return status

    def _check_type_f(self):
        """
        Specific checking method for type-F or P patch panel files.
        :return: string
            "OKAY" if no problems are found. Otherwise, a terse description of problems.
        """
        assert self.patch_type in ['F', 'P'], 'This method only applies to patch_type F or P, not {}'.format(self.patch_type)

        problems = []
        coils = [k for k in self if isinstance(self[k], OMFITpatchObject)]

        # Check for duplicate choppers
        all_chopper_name = []
        for k in coils:
            all_chopper_name += self[k]['chopper_name']
        ignores = ['', 'SHORT', 'OPEN']
        for ignore in ignores:
            while ignore in all_chopper_name:
                all_chopper_name.remove(ignore)
        duplicate_choppers = []
        noted = []
        for chop in all_chopper_name:
            chop_count = all_chopper_name.count(chop)
            if chop_count > 1:
                if chop not in noted:
                    c_on_coils = [k for k in coils if chop in self[k]['chopper_name']]
                    duplicate_choppers += ['{}({})'.format(chop, ','.join(c_on_coils))]
                    noted += [chop]
        if len(duplicate_choppers):
            problems += ['DUPL.CHOP: [' + ', '.join(duplicate_choppers) + ']']

        # Check for mis-matched current directions for the same power supply
        ps_map = OMFITpatchObject.power_supply_map
        pwr_dirs = {k: None for k in ps_map if k > 0}
        coils_used = {k: [] for k in ps_map if k > 0}
        for k in coils:
            ps = self[k]['power_supply_index']
            if ps in pwr_dirs:
                coils_used[ps] += [k]
                if pwr_dirs[ps] is None:
                    pwr_dirs[ps] = self[k]['direction_index']
                else:
                    if pwr_dirs[ps] != self[k]['direction_index']:
                        pwr_dirs[ps] = -1
        dir_problems = []
        for k in pwr_dirs:
            if pwr_dirs[k] == -1:
                dir_problems += ['{}({})'.format(ps_map[k], ','.join(coils_used[k]))]
        if len(dir_problems):
            problems += ['DIR.CONFL.: [' + ', '.join(dir_problems) + ']']

        # Check for missing C-coil
        if 'cl' not in self:
            problems += ['MISSING.C.CL']

        if len(self) > 0:
            # Can't have these problems if there are no coils defined

            # Check for too many choppers
            cmc = self[coils[0]].chopper_max_counts
            too_many_choppers = []
            for coil in coils:
                if coil not in cmc:
                    too_many_choppers += ['{}({}>?)'.format(coil, self[coil]['chopper_count'])]
                elif self[coil]['chopper_count'] > cmc[coil]:
                    too_many_choppers += ['{}({}>{})'.format(coil, self[coil]['chopper_count'], cmc[coil])]
            if too_many_choppers:
                problems += ['EXCESS.CHOP.: [' + ', '.join(too_many_choppers) + ']']

            # Check for illegal chopper vs. coil and power supply pairings
            ac = self[coils[0]].allowed_choppers
            illegal_choppers = []
            for coil in coils:
                illp = []
                illc = []
                psn = self[coil].get('power_supply_name', '')
                if coil not in ac:
                    self.printq('Coil {} is not recognized in dict of allowed choppers; cannot check properly'.format(coil))
                for ci in self[coil]['chopper_index']:
                    if (coil in ac) and (ci not in ac[coil]):
                        illc += [self[coil].chopper_map[ci]]
                    if (psn in ac) and (ci != 0) and (ci not in ac[psn]):
                        illp += ['{}:{}'.format(self[coil].chopper_map[ci], coil)]
                if illc:
                    illegal_choppers += ['{}({})'.format(coil, ','.join(illc))]
                if illp:
                    illegal_choppers += ['{}({})'.format(psn, ','.join(illp))]
            if illegal_choppers:
                problems += ['ILLEG.CHOP.: [' + ', '.join(illegal_choppers) + ']']

            bad_parallel_choppers = []
            for coil in coils:
                # Check for parallel chopper-like objects that aren't allowed to be in parallel
                for lc in self[coils[0]].lonely_choppers:
                    if (lc in self[coil]['chopper_index']) and (self[coil]['chopper_count'] > 1):
                        names = [cn for cn in self[coil]['chopper_name'] if cn]
                        bad_parallel_choppers += ['{}({})'.format(coil, ', '.join(names))]
            if bad_parallel_choppers:
                problems += ['BAD.PARALLEL.: [' + ', '.join(list(set(bad_parallel_choppers))) + ']']
        else:
            problems += ['NO.COILS.']

        # Summarize problems
        if problems:
            status = ', '.join(problems)
        else:
            status = 'OKAY'
        self.problems = problems
        return status

    def printq(self, *args):
        """Print wrapper for keeping topic consistent within the instance"""
        printd(*args, topic=self.debug_topic)

    def _guess_patch_type(self, default='?'):
        """
        Differentiates between various file types and returns a string or None.
        :return:
            'P': PCS format, like ptpatch.dat. Similar to 'F' type, but includes strange binary data
            'F': F-coil patch panel, ASCII
            'I': I&C-coil patch panel, ASCII
            None: Failed to determine type
        """
        if self.bin_mark in self.contents:
            return 'P'
        elif 'C-coil parity:' in self.contents:
            return 'I'
        elif 'I-coil file:' in self.contents:
            return 'I'
        elif (('PUSH' in self.contents) or ('PULL' in self.contents)) and ('1A' in self.contents):
            return 'F'
        else:
            return default

    def _read_type_f(self):
        """Parses F-coil patch panel files into dict-like structure"""
        assert self.patch_type == 'F', 'This method only works for type "F". Type is instead: %s' % self.patch_type
        field_widths = [3, 4, 3, 6, 3, 4, 2, 5, 2, 2, 5, 5, 5, 5, 5, 3, 3, 3, 3, 3]

        for i, line in enumerate(self.contents.split('\n')):
            if len(line) != np.sum(field_widths):
                self.printq('Line {} does not match expected length ({}); contents = {}'.format(i, np.sum(field_widths), line))
                continue
            fields = [''] * len(field_widths)
            start = 0
            for j in range(len(field_widths)):
                fields[j] = line[start : start + field_widths[j]]
                start += field_widths[j]
            out = self[fields[1].strip()] = OMFITpatchObject()
            out['coil_index'] = int(fields[0])
            out['chopper_count'] = int(fields[9])
            out['chopper_index'] = [int(fields[2])]
            out['power_supply_index'] = int(fields[4])
            out['direction_index'] = int(fields[6])
            out['rail_index'] = int(fields[8])
            out['chopper_name'] = [fields[3].strip()]
            out['power_supply_name'] = fields[5].strip()
            out['direction_name'] = fields[7].strip()
            if out['rail_index'] == 0:
                out['rail_name'] = 'E supply'
            elif out['rail_index'] == 1:
                out['rail_name'] = 'VFI'
            else:
                out['rail_name'] = ''
            out['chopper_name'] = [out['chopper_name'][0]] + [cn.strip() for cn in fields[10:15]]
            out['chopper_index'] = [out['chopper_index'][0]] + [int(ci) for ci in fields[15:20]]
            out['chopper_name'] = OMFITpatchList(out['chopper_name'], parent=out)
            out['chopper_index'] = OMFITpatchList(out['chopper_index'], parent=out)
            out.locked = True

        self.get_patch_name()

        if self.auto_clean:
            self.printq('Running automatic cleanup of F-patch file (archive format/type F) to remove junk chopper data')
            self._clean_type_f()

    def _read_type_p(self, include_c_coil=False):
        """Parses type-P patch panel files, which are F-patch files in binary format"""
        self._read_type_p_inner(self.contents.split(self.bin_mark)[45])

        if include_c_coil:
            self.add_c_coil()
            # This might be needed to make converted type-P to F files consistent with natural type-F files

        if self.auto_clean:
            self.printq('Running automatic cleanup of F-patch file (binary format/type P) to remove junk chopper data')
            self._clean_type_f()

        if self.fpconvert:
            printd('Automatically converting from type-P (binary) to type-F (ASCII) to enable saving.')
            self.patch_type = 'F'
            if 'cl' not in self:
                printw('WARNING: please use .add_c_coil(d_supply=True/False) to add C-coil to converted P-type patch!')

    def _read_type_p_inner(self, item_names):
        """Splits apart a string that's formatted like the relevant section of a type-P file"""
        fcoil_len = 36  # Number of characters for each F-coil
        title_len = 12  # Number of characters for title
        self.patch_name = item_names[:title_len].strip()
        rest = item_names[title_len:]
        coil_index = 1
        while len(rest) >= fcoil_len:
            out = self[rest[:4].strip()] = OMFITpatchObject()
            out['coil_index'] = coil_index
            # Load placeholders so the order will be consistent with F-type
            out['chopper_count'] = 0
            out['chopper_index'] = [0, 0, 0, 0, 0, 0]
            out['power_supply_index'] = 0
            out['direction_index'] = 0
            out['rail_index'] = 0
            # Done with placeholders
            out.locked = True
            out['chopper_name'] = [rest[16 + i * 4 : 20 + i * 4].strip() for i in range(5)] + ['']  # P-type only holds 5 choppers
            ps = rest[4:8].strip()
            out['power_supply_name'] = '' if ps == 'NONE' else ps
            out['direction_name'] = rest[12:16].strip()
            out['rail_name'] = 'VFI' if rest[8:11] == 'YES' else 'E supply'
            rest = rest[fcoil_len:]
            coil_index = coil_index + 1
        assert len(rest) == 0, 'Inner P contents after read FC should be empty, but instead: len{} remainder={}'.format(
            len(rest), repr(rest)
        )
        return

    def _read_type_i(self):
        """Parses I & C coil files"""
        assert self.patch_type == 'I', 'This method only works for type "I". Type is instead: %s' % self.patch_type
        if self.contents:
            lines = self.contents.split('\n')
            self._read_type_i_inner(lines)
        self.get_patch_name()

    def _read_type_i_inner(self, lines, xs=0):
        self['config'] = OMFITpatchObject()
        self['config']['c_coil_parity'] = lines[0][15:].strip()
        self['config']['i_coil_file'] = lines[11][13:].strip()
        for i in range(10):
            line = lines[1 + i]
            out = self['c{}'.format(i)] = OMFITpatchObject()
            out['slot'] = line[2:4]
            out['sign'] = line[5:8]
            out['spa'] = line[9:13].strip()
            out['c_idx'] = int(line[14 + xs : 15 + xs])
            out['coil'] = line[16:].strip()
        self['AA'] = OMFITpatchObject()
        for i in range(12):
            line = lines[12 + i]
            self['AA'][line[:5].strip()] = line[5:].strip()
        self['SS'] = OMFITpatchObject()
        if len(lines) > 25:
            # Has SS entries
            for i in range(12):
                line = lines[24 + i]
                self['SS'][line[:7].strip()] = line[7:].strip()
        else:
            # Old file with no SS entries, set them all disconnected
            for i in [1, 2]:
                for a in 'ABCDEF':
                    self['SS']['SS{}{}'.format(i, a)] = ''

    def _read_type_j(self):
        """Parses I & C patch information obtained from a shot number"""
        line_len1 = 36
        line_len2 = 10
        line_lens = [line_len1] * 10 + [32, 4] + [line_len2] * 12 + [line_len1] * 12
        rest = copy.copy(self.contents)
        lines = []
        for line_len in line_lens:
            lines += [rest[:line_len]]
            rest = rest[line_len:]
        self.patch_name = rest.strip()
        lines_out = ['C-coil parity: ' + lines[11]] + lines[0:10] + ['I-Coil file: ' + lines[10]] + lines[12:]
        lines_out = [line.replace(' pos', 'pos').replace(' neg', 'neg') for line in lines_out]
        self._read_type_i_inner(lines_out, xs=1)

    def get_patch_name(self):
        """Tries to determine patch panel name"""
        if (getattr(self, '_load_complete', None) is not None) and (getattr(self, 'patch_name', None) is not None):
            # Already have patch_name determined by previous load
            return
        elif (self.source_file is not None) and os.path.split(self.source_file)[-1].lower().endswith('patnow.dat'):
            name_file = self.source_file.replace('patnow.dat', 'patnow.nam')
            if os.path.exists(name_file):
                with open(name_file, 'r') as f:
                    patch_dat = f.read()
                    self.patch_name = patch_dat.split('\n')[0]
                return
        elif getattr(self, 'filename', None) is not None:
            self.patch_name = os.path.split(self.filename)[-1]
            return

        self.patch_name = funny_random_name_generator(self.patch_type == 'I')
        return

    def add_c_coil(self, d_supply=False):
        """
        Adds an entry for C-coils to type-F patch panels, which is useful if converted from type-P.
        Type-P files don't have a C-coil entry.
        :param d_supply: bool
            True: Add the default D supply on C-coil setup.
            False: Add default C-coil setup with no F-coil supplies on the C-coils (C-coil entry in F is blank)
        """
        if 'cl' in self:
            self.printq('This patch panel already has C-coils. Skipping.')
            return

        out = self['cl'] = OMFITpatchObject()
        out['coil_index'] = max([a.get('coil_index', 0) for a in self.values() if isinstance(a, OMFITpatchObject)]) + 1
        if d_supply:
            out['chopper_count'] = 1
            out['chopper_index'] = [42, 0, 0, 0, 0, 0]
            out['power_supply_index'] = 1
            out['direction_index'] = 1
            out['rail_index'] = 3
            out['chopper_name'] = ['FSUP', '', '', '', '', '']
            out['power_supply_name'] = 'D'
            out['direction_name'] = 'PUSH'
            out['rail_name'] = ''
        else:
            out['chopper_count'] = 1
            out['chopper_index'] = [0, 0, 0, 0, 0, 0]
            out['power_supply_index'] = 0
            out['direction_index'] = 0
            out['rail_index'] = 1
            out['chopper_name'] = ['OPEN', '', '', '', '', '']
            out['power_supply_name'] = ''
            out['direction_name'] = ''
            out['rail_name'] = 'VFI'
        out.locked = True

    def _clean_type_f(self):
        """Removes unused chopper indices and other problems"""
        assert self.patch_type in ['F', 'P'], 'This method should only be used for type F or P patch panels'
        coils = [k for k in self if isinstance(self[k], OMFITpatchObject)]
        for coil in coils:
            a = self[coil]
            # If the first chopper isn't a real chopper, any other indices specified are junk
            if (a['chopper_index'][0] < 1) or (a['chopper_name'][0] in ['RV1', 'RV2', 'OPEN', 'SHORT', '']):
                for i in range(1, 6):
                    a['chopper_index'][i] = 0

    def cleanup(self):
        """Cleans up junk data and blatant inconsistencies. May prevent output from matching buggy input."""
        if self.patch_type in ['F', 'P']:
            self._clean_type_f()
        else:
            print('No cleanup method for patch panel type {}'.format(self.patch_type))

    def _write_type_f(self):
        """Method for forming output string (file contents) for type-F patch panel files."""
        out_format = (
            '{coil_index:3d} {coil:>3s}{c0i:3d} {c0n:5s}{power_supply_index:3d} {power_supply_name:3s}'
            '{direction_index:2d} {direction_name:4s}{rail_index:2d}{chopper_count:2d} {c1n:24s}{c1i:15s}'
        )
        output = []
        for i, coil in enumerate([k for k in self if 'coil_index' in self[k]]):
            d = dict(**self[coil])
            d['c0i'] = d['chopper_index'][0]
            d['c0n'] = d['chopper_name'][0]
            d['c1n'] = ' '.join(['{:4s}'.format(cn) for cn in d['chopper_name'][1:]])
            d['c1i'] = ''.join(['{:3d}'.format(ci) for ci in d['chopper_index'][1:]])
            d['coil'] = coil
            output += [out_format.format(**d)]
        if not self.filename.startswith('patnow'):
            output += ['Configuration Description']
        output = '\n'.join(output)
        self.contents = output
        return output

    def _write_type_i(self):
        """Method for forming output string for type-I patch panel files"""
        output = []
        output += ['C-coil parity: ' + self.get('config', {}).get('c_coil_parity', '')]
        blank_c = dict(slot='', sign='', spa='', coil='', c_idx=0)
        for i in range(10):
            output += [
                str(1 + int(np.floor(i / 2)))
                + ' {slot:2s} {sign:3s} {spa:>4s} {c_idx:1d} {coil:58s}'.format(**self.get('c{}'.format(i), blank_c))
            ]
        output += ['I-Coil file: ' + self.get('config', {}).get('i_coil_file', '')]
        for a in range(1, 13):
            output += ['AA{:<2d} {:69s}'.format(a, self.get('AA', {}).get('AA{}'.format(a), ''))]
        for i in [1, 2]:
            for a in 'ABCDEF':
                ss = 'SS{}{}'.format(i, a)
                output += ['{:6s} {:67s}'.format(ss, self.get('SS', {}).get(ss, ''))]
        output = '\n'.join(output)
        self.contents = output
        return output

    @dynaSave
    def save(self, no_write=False):
        """Saves file to disk"""
        if self.patch_type == 'F':
            output = self._write_type_f()
        elif self.patch_type == 'P':
            raise TypeError(
                'Cannot save type P files; set self.patch_type="F" first to allow saving. Type P is F-coil patch in '
                'some old format, which is binary and hard to use. Type F is F-coil patch in archival format, which is '
                'ASCII and easy to deal with. If a type-P file is converted, it is recommended that a C-coil entry be '
                'added using self.add_c_coil(). Specify d_supply=True if the D power supply should power C-coils.'
            )
        elif self.patch_type == 'I':
            output = self._write_type_i()
        else:
            raise NotImplementedError('Patch type {} does not have a write method yet; sorry'.format(self.patch_type))
        if not no_write:
            with open(self.filename, 'w') as f:
                self.printq('Writing patch panel main file {}...'.format(self.filename))
                f.write(output)
            if os.path.split(self.filename)[1].endswith('patnow.dat') and (self.patch_type in 'FI'):
                name_file = self.filename.replace('patnow.dat', 'patnow.nam')
                name_output = '\n'.join([self.patch_name, 'Configuration Description'])
                self.printq('Writing patch panel name file {}...'.format(name_file))
                with open(name_file, 'w') as f:
                    f.write(name_output)
        return output
