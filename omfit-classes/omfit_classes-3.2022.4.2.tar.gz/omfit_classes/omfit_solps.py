"""
Provides classes and utility functions for managing SOLPS runs or post-processing SOLPS results.
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

from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.utils_base import is_string
from omfit_classes.omfit_namelist import OMFITnamelist
from omfit_classes.omfit_base import OMFITtree
from omfit_classes.namelist import interpreter, sparray

import unittest
import numpy as np
import string
import traceback

debug_topic = 'omfit_solps'

__all__ = []


def _available_to_user_solps(f):
    OMFITaux.setdefault('OMFITsolps_functions', [])
    OMFITaux['OMFITsolps_functions'].append(f)
    __all__.append(f.__name__)
    return f


@_available_to_user_solps
def find_closest_key(keys, search_string=None, block_id=None, case_sensitive=False):
    """
    Decides which string in a list of strings (like a list of dictionary keys) best matches a search string. This is
    provided so that subtle changes in the spelling, arrangement, or sanitization of headers in input.dat don't break
    the interface.

    :param keys: List of keys which are potential matches to test_key

    :param search_string: String to search for; it should be similar to an expected key name in keys.

    :param block_id: A string with the block number, like '1' or '3a'. If this is provided, the standard approximate
        block name will be used and search_string is not needed.

    :param case_sensitive: T/F: If False, strings will have output of .upper() compared instead of direct comparison.

    :return: A string containing the key name which is the closest match to search_string
    """

    if search_string is None and block_id is None:
        printe('Provide search_string or block_id')
        return None

    # Top level block names
    block_approx_names = {
        '1': '1. Data for operating mode',
        '2': '2. Data for standard mesh',
        '3a': '3a. Data for non default standard surfaces',
        '3b': '3b. Data for additional surfaces',
        '4': '4. Data for species and atomic physics module',
        '5': '5. Data for plasma background',
        '6': '6a. General data for reflection model',  # Alias for 6a because I don't see a 6b here.
        '6a': '6a. General data for reflection model',
        '7': '7. Data for primary sources, nstrai strata',
        '8': '8. Additional data for specific zones',
        '9': '9. Data for statistic and nonalog model',
        '10': '10. Data for additional tallies',
        '11': '11. Data for numerical and graphical output',
        '12': '12. Data for diagnostic module',
        '13': '13. Data for nonlinear and time dep. option',
        '14': '14. Data for interfacing routine infusr',
        '15': '15. Data for interfacing routine addusr',
        # The rest are not top level blocks, they are sub-blocks under the top level blocks.
        '4a': '4a. Neutral atom species',
        '4b': '4b. Neutral molecule species',
        '4c': '4c. Test ion species',
        '4d': '4d. Photon species',  # Not always present
    }

    if search_string is None:
        search_string = block_approx_names.get(str(block_id), None)
        if search_string is None:
            printe(
                'Invalid block_id provided to find_closest_key: {}. Valid options are: {}'.format(block_id, list(block_approx_names.keys()))
            )
            return None

    ss_ = search_string.split()
    match_quality = np.zeros(len(keys))

    for k_, key_ in enumerate(keys):
        for s_ in ss_:
            if case_sensitive:
                if s_ in key_:
                    match_quality[k_] += 1
                if ss_[0] in key_:
                    match_quality[k_] += 3  # Additional weight for the first word, which is assumed to be a number.
            else:
                if s_.upper() in key_.upper():
                    match_quality[k_] += 1
                if ss_[0].upper() in key_.upper():
                    match_quality[k_] += 3  # Additional weight for the first word, which is assumed to be a number.

    return keys[match_quality.argmax()]


def find_solps_module_and_run(solps_file=None):
    """
    Looks up references to the SOLPS module and the OMFITsolpsCase that holds this file within the OMFIT tree

    Won't work if not running within the tree

    :param solps_file: OMFITsolps or OMFITsolpsNamelist instance

    :return: OMFITmodule, string, list of strings
        Reference to SOLPS module, key to the current OMFITsolpsCase within RUNS, and list of OMFIT tree locations
        leading to current file. All can be replaced by None if lookup fails.
    """
    assert solps_file is not None, 'Must provide an SOLPS file'
    try:
        locs = treeLocation(solps_file)
        solps_loc = [loc for loc in locs if getattr(eval(loc), 'ID', None) == 'SOLPS'][-1]
        root = eval(solps_loc)
    except (KeyError, IndexError):
        print('Could not access OMFIT SOLPS module root')
        root = None
        run_key = None
        locs = None
    else:
        try:
            case_loc = [loc for loc in locs if type(eval(loc)).__name__ == "OMFITsolpsCase"][-1]
            run_key = case_loc.split("'")[-2]
        except (KeyError, IndexError):
            run_key = None
            print('Could not look up key to an OMFITsolpsCase.')

    return root, run_key, locs


@_available_to_user_solps
class OMFITsolps(SortedDict, OMFITascii):
    """
    Class for parsing some OMFIT input files
    """

    def __init__(self, filename='', dynaload=True, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = dynaload

        # input.dat has fixed formatting. Each line is done with one of the following formats, with few exceptions:
        #   (6E12.4)      only real variables
        #   (12I6)        only integer variables
        #   (12(5L1,1X))  only logical variables
        #   (A72)         only text
        #   (K(I6,6x),(6-K)E12.4)     mixture of K (K<6) integers first then up to 6-K real variables
        # The above are copied directly from the Eirene manual and are format codes for fortran.
        self.inputdat_int_len = 6
        self.inputdat_flt_len = 12
        self.inputdat_flt_dec = 5  # The manual says 4, but my file has 5 decimal places.
        self.special_bool_int_mix_len = 27  # Length for integer field following length 1 bool field in block 11.

    @dynaLoad
    def load(self):
        printd('OMFITsolps load()...', topic=debug_topic)
        from numpy import char, real

        self.clear()

        t0 = time.time()
        timing = [t0]

        def ticktock(mark=None):
            new = time.time()
            dt = new - timing[-1]
            timing.append(new)
            if mark is None:
                mark = str(len(timing))
            printd(
                '        {:22s}: {:30s} {:8.2f} ms, {:8.2f} ms, {}'.format(
                    'omfit_solps.load', mark, dt * 1000, (timing[-1] - t0) * 1000, os.path.split(self.filename)[1]
                ),
                topic='OMFITsolps_profiling',
            )

        ticktock('start loading')

        def item_dim_form(line_):
            item_ = re.split(r'[\s\n]', line_)[0][1:]
            extra = ('('.join(line_.split('(')[1:]).strip())[:-1]
            tmp__ = extra.split(';')
            dim_ = tmp__[0].strip() if ';' in extra else None
            form_ = tmp__[1].strip() if len(tmp__) > 1 else None
            return item_, dim_, form_

        # b2ai is fully parsed -----------------------------------------------------------------------------------------
        if os.path.split(self.filename)[1] == 'b2ai.dat':
            with open(self.filename, 'r') as f:
                lines = f.readlines()
            item = None
            while len(lines):
                line = lines.pop(0)
                if line.startswith('*specs'):
                    prop = [x.strip() for x in list(filter(None, re.findall(r"(?:\'.*?\'|\S)+", line)))[1:]]
                    self['specs'] = SortedDict()
                    for _ in range(self['dimens']['data']):
                        line = re.findall(r"(?:\'.*?\'|\S)+", lines.pop(0))
                        self['specs'][eval(eval(line[0]))] = SortedDict()
                        for k, p in enumerate(prop):
                            self['specs'][eval(eval(line[0]))][p] = eval(line[1 + k])
                elif line.startswith('*'):
                    item, dim, form = item_dim_form(line)
                    self[item] = {}
                    self[item]['dimension'] = dim
                    self[item]['format'] = form
                else:
                    try:
                        self[item]['data'] = ast.literal_eval(line.strip())
                    except (ValueError, SyntaxError):
                        self[item]['data'] = []
                        for thing in re.split('[ |\t]+', line.strip()):
                            self[item]['data'].extend(tolist(interpreter(thing)))
            ticktock('done with b2ai')

        # b2mn and b2ag are partly parsed ------------------------------------------------------------------------------
        elif os.path.split(self.filename)[1] in ['b2mn.dat', 'b2ag.dat']:
            printd(' parsing b2ag or b2mn...', topic=debug_topic)
            with open(self.filename, 'r') as f:
                lines = f.readlines()
            for k, line in enumerate(lines):
                printd('line #{} = {}'.format(k, line), topic=debug_topic)
                if line[0] != "'":
                    self['__comment_%d__' % k] = line.strip('\n')
                    continue
                key = line.split()[0].strip("'")
                printd('   key = {}'.format(key), topic=debug_topic)
                try:
                    value = [eval(x.strip("'")) for x in line.split()[1:]]
                    printd('   value from try: {}'.format(value), topic=debug_topic)
                except (NameError, SyntaxError):
                    value = line.split("'")[3]
                    printd('     value from except : {}'.format(value), topic=debug_topic)
                if len(value) == 1:
                    self[key] = value[0]
                else:
                    self[key] = value
            ticktock('done with b2mn or b2ag')
 
        # b2fgmtry and/or b2fplasmf is parsed -------------------------------------------------------------------------------------------
        elif os.path.split(self.filename)[1] in ['b2fgmtry','b2fplasmf']:
            with open(self.filename, 'r') as f:
                tmp = f.read()
            tmp = re.sub('\n', ' ', tmp)
            tmp = tmp.split("*c")
            tmp = [[f for f in x.split(' ') if f] for x in tmp]

            m = {'int': int, 'real': float, 'char': str}

            for line in tmp[1:]:
                if len(line) > 4:
                    self[line[3]] = np.array(list(map(m[line[1]], line[4:])))
                else:
                    self[line[3]] = None
            ticktock('done with b2fgmtry/b2fplasmf')

        # b2fstate and b2fstati
        elif os.path.split(self.filename)[1] in ['b2fstate', 'b2fstati']:
            printd('Identified b2fstate or b2fstati type file (LOAD).', topic=debug_topic)
            with open(self.filename, 'r') as f:
                lines = f.readlines()

            ticktock('opened file')

            # Initialize
            self['__notes__'] = []
            self['__unhandled__'] = []
            data = np.array([])

            translations = {'real': 'float'}

            self['nx'], self['ny'], self['ns'] = 0, 0, 0

            def close_field():
                # Handle previous field
                if n > 0:
                    printd(
                        'Finishing previous field;    dat_type = "{}", n = {}, names = {}, len(names) = {}'.format(
                            dat_type, n, names, len(names)
                        ),
                        topic=debug_topic,
                    )
                    if len(names) == 1:
                        # 2D arrays: X Y
                        if n == (self['nx'] + 2) * (self['ny'] + 2):
                            # This is an X by Y spatial array with guard cells
                            self[names[0]] = data.reshape(-1, self['nx'] + 2)
                        elif n == self['nx'] * self['ny']:
                            # This is an X by Y spatial array with no guard cells
                            self[names[0]] = data.reshape(-1, self['nx'])

                        # 3D arrays - X Y S
                        elif n == (self['nx'] + 2) * (self['ny'] + 2) * self['ns']:
                            # This is an X by Y by species array with guard cells
                            self[names[0]] = data.reshape(self['ns'], -1, self['nx'] + 2)
                        elif n == (self['nx']) * (self['ny']) * self['ns']:
                            # This is an X by Y by species array with no guard cells
                            self[names[0]] = data.reshape(self['ns'], -1, self['nx'])

                        # 3D arrays - X Y v
                        # Page 183 of the 2015 Feb 27 SOLPS manual mentions "fhe - (-1:nx, -1:ny, 0:1) real*8 array
                        # I think there's a row major vs. column major difference going on or something, but anyway,
                        # python gets the array out correctly if nx corresponds to the last axis when 2D, which is
                        # the opposite of the documentation, so the v axis with length 2 should be the first axis in
                        # python.
                        elif n == (self['nx'] + 2) * (self['ny'] + 2) * 2:
                            # This is an X by Y by 2 (probably poloidal & radial components) array w/ guard cells.
                            self[names[0]] = data.reshape(2, -1, self['nx'] + 2)
                        elif n == self['nx'] * self['ny'] * 2:
                            # This is an X by Y by 2 (probably poloidal & radial components) array w/o guard cells.
                            self[names[0]] = data.reshape(2, -1, self['nx'])

                        # 4D arrays - X Y S v
                        # Manual calls fna X Y v S, so it should be S v Y X here.
                        elif n == (self['nx'] + 2) * (self['ny'] + 2) * self['ns'] * 2:
                            # This is an X by Y by species by 2 array w/ guard cells.
                            self[names[0]] = data.reshape(self['ns'], 2, -1, self['nx'] + 2)
                        elif n == (self['nx']) * (self['ny']) * self['ns'] * 2:
                            # This is an X by Y by species by 2 array w/o guard cells.
                            self[names[0]] = data.reshape(self['ns'], 2, -1, self['nx'])

                        else:
                            # Can't identify higher dimensions of this array or it is just 1D, so don't mess with it
                            self[names[0]] = data
                    elif len(names) == n:
                        for ii, name in enumerate(names):
                            self[name] = data[ii]
                    else:
                        printw(
                            'WARNING! Problem parsing b2fstate or b2fstati in omfit_solps class: Cannot handle '
                            'more than one name unless length of names matches length of data!'
                        )
                        self['__unhandled__'] += [{'names': names, 'data': data}]

            cflines = []
            for i, line in enumerate(lines):
                if line.startswith('*cf:'):
                    cflines += [i]

            cflines += [len(lines)]
            ticktock('done finding cflines')

            if cflines[0] > 0:
                printd('    Found header line(s), adding to notes: {}'.format(lines[: cflines[0]]), topic=debug_topic)
                self['__notes__'] += [line.split('\n')[0] for line in lines[: cflines[0]]]
                ticktock('header line')

            for i in range(len(cflines) - 1):
                printd('Setting up field: {}'.format(lines[cflines[i]].split('\n')[0]), topic=debug_topic)
                dat_type_string = lines[cflines[i]].split()[1].strip()
                dat_type_string = translations.get(dat_type_string, dat_type_string)
                dat_type = eval(dat_type_string)
                n = int(lines[cflines[i]].split()[2])
                names = lines[cflines[i]].split()[3].split(',')
                printd(
                    '   dat_type = "{}" / "{}", n = {}, names = {}, len(names) = {}'.format(
                        dat_type_string, dat_type, n, names, len(names)
                    ),
                    topic=debug_topic,
                )

                raw = lines[cflines[i] + 1 : cflines[i + 1]]
                if dat_type_string != 'char':
                    data = np.array(' '.join(raw).split()).astype(dat_type)
                else:
                    data = lines[cflines[i] + 1].split('\n')[0][1:]
                ticktock('cfline {}'.format(i))
                close_field()
            ticktock('end b2fstate/b2fstati')

        # This basic loader makes a bunch of nested dictionaries with integer keys (counting lines) and string
        # values holding the contents of each line. Assumes that lines which should be the starts of new
        # dictionaries start with *, **, or ***. Can be used as a starting point for more advanced parsing since
        # it organizes things nicely.
        else:
            with open(self.filename, 'r') as f:
                lines = f.readlines()
            parent = tmp = self
            last = -1

            def sanitize_line(a, save_trailing_whitespace=True):
                trail = ' ' * (len(a) - len(a.rstrip())) if save_trailing_whitespace else ''
                return ('_'.join(a.replace('*', '').replace(':', '').strip().lstrip().split())).replace('_-_', '-').replace('"', '') + trail

            # Pull out dictionary structure (*, **, ***)
            for line_in in lines:
                line = line_in.split('\n')[0]
                if re.match(r'\*\*\*\s*\w+', line):
                    new_line = sanitize_line(line)
                    printd('  3 star, line = {},   new_line = {}'.format(line, new_line), topic=debug_topic)
                    self[new_line] = tmp = SortedDict()
                    self[new_line]['__name__'] = line
                    parent = tmp
                    last = 3
                elif re.match(r'\*\*\s*\w+', line):
                    new_line = sanitize_line(line)
                    printd('  2 star, line = {},   new_line = {}'.format(line, new_line), topic=debug_topic)
                    if last == 2:
                        printd('    last was 2 also', topic=debug_topic)
                        parent[new_line] = tmp = SortedDict()
                        parent[new_line]['__name__'] = line
                    else:
                        printd('      last was NOT 2', topic=debug_topic)
                        parent = tmp
                        tmp[new_line] = tmp = SortedDict()
                        tmp['__name__'] = line
                    last = 2
                elif re.match(r'\*\s*\w+', line):
                    new_line = sanitize_line(line)
                    printd('  1 star, line = {},   new_line = {}'.format(line, new_line), topic=debug_topic)
                    parent[new_line] = tmp = SortedDict()
                    parent[new_line]['__name__'] = line
                    last = 1
                elif not len(tmp):
                    tmp[0] = line
                else:
                    tmp[len(tmp)] = line

        # Additional input.dat-specific reading of results of generic loader -------------------------------------------
        if os.path.split(self.filename)[1] in ['input.dat']:
            self.input_dat_renames()

    def input_dat_renames(self):
        ghost = SortedDict([])
        # noinspection PyBroadException
        try:
            # Split up strings into lists and stuff (all input.dat blocks)
            for block_name in list(self.keys()):
                printd('block name = {}'.format(block_name), topic=debug_topic)
                block = self[block_name]
                ghost[block_name] = SortedDict([]) if isinstance(self[block_name], dict) else 'not a block'

                def grok_it(line_):
                    printd('   Checking input: {}'.format(repr(line_)), topic=debug_topic)
                    if np.all([(a == 'T') or (a == 'F') or (a == ' ') for a in line_.upper()]):
                        # Booleans are stored as TTFFT TFFFT TFF etc., separated into blocks of 5 with spaces.
                        printd(
                            '      line_ contains only "T", "F", and " ", so it is a bunch of TF flags mashed ' 'together',
                            topic=debug_topic,
                        )
                        line_ = [char.upper() == 'T' for char in ''.join(line_.split())]
                        if len(line_) == 1:
                            line_ = line_[0]
                            printd('         looks like actually only one T/F flag', topic=debug_topic)
                    else:  # elif len(line_.strip().split()) > 1:
                        printd('      line_ has things other than T and F and has spaces, so maybe a list of numbers', topic=debug_topic)
                        # Integer / float mix
                        # ints first then floats is a standard format. There is a special format with floats first
                        # and then ints. I accidentally made this work for an arbitrary mix, so hurray.
                        count = 0
                        len_use = []
                        remaining = copy.copy(line_)
                        while remaining:
                            if 'E' in remaining[: self.inputdat_flt_len]:
                                cut_len = self.inputdat_flt_len
                            else:
                                cut_len = self.inputdat_int_len
                            remaining = remaining[cut_len:]
                            count += 1
                            len_use += [cut_len]
                        try:
                            printd('        count = {}'.format(count), topic=debug_topic)
                            printd('        len_use = {}   ({} elements)'.format(len_use, len(len_use)), topic=debug_topic)
                            printd([[np.sum(len_use[:ii]), np.sum(len_use[: ii + 1])] for ii in range(count)], topic=debug_topic)
                            printd(
                                [line_[int(np.sum(len_use[:ii])) : np.sum(len_use[: ii + 1])].strip() for ii in range(count)],
                                topic=debug_topic,
                            )
                            line_ = [
                                ast.literal_eval(line_[int(np.sum(len_use[:ii])) : np.sum(len_use[: ii + 1])].strip())
                                for ii in range(count)
                            ]
                        except (ValueError, SyntaxError):
                            # See if it's a special bool / int mix in block 11
                            special_block11 = True  # Assume true until proven otherwise
                            bool_part = line_[0]
                            if bool_part in ['T', 'F']:
                                bool_part = bool_part.upper() == 'T'
                            else:
                                special_block11 = False
                            try:
                                int_part = line_[1 : self.special_bool_int_mix_len + 1].strip()
                                if ' ' in int_part:
                                    special_block11 = False
                                else:
                                    int_part = ast.literal_eval(int_part)
                            except (ValueError, SyntaxError):
                                int_part = None
                                special_block11 = False

                            if special_block11:
                                printd('         looks like it was a special bool/int mix format for block 11', topic=debug_topic)
                                line_ = [bool_part, int_part]
                            else:
                                printd('         nevermind, maybe it is just a string', topic=debug_topic)

                    if len(tolist(line_)) == 1:
                        line_ = tolist(line_)[0]
                    printd('    grokked "{}"'.format(line_), topic=debug_topic)
                    return line_

                for sub_block_name in block:
                    printd('sub_block_name = {}'.format(sub_block_name), topic=debug_topic)
                    sub_block = block[sub_block_name]

                    if isinstance(sub_block, dict):
                        # Parse the sub block because it's a dictionary. It has information about particle statistics
                        # near one of the boundaries.
                        gsb = ghost[block_name][sub_block_name] = SortedDict([])
                        printd('  this sub block is a dict', topic=debug_topic)
                        for k in sub_block:
                            line = sub_block[k]
                            line0 = copy.copy(line)
                            line = grok_it(line)
                            printd('   line {} = {}'.format(k, line), topic=debug_topic)
                            printd('   line0 {} = {}'.format(k, line0), topic=debug_topic)
                            gsb[k] = line
                    else:
                        printd('  this sub block is not a dict', topic=debug_topic)
                        ghost[block_name][sub_block_name] = grok_it(sub_block)

                printd('    finished sub_block_name loop', topic=debug_topic)
            printd('  finished block_name loop', topic=debug_topic)

            def key_rename(a_, key_, newkey_):
                if len(tolist(newkey_)) == 1:
                    printd(' Simple key rename: {} --> {}'.format(key_, newkey_), topic=debug_topic)
                    ii = list(a_.keys()).index(key_)
                    a_.insert(ii, newkey_, a_.pop(key_))
                else:
                    printd(' Rename list to dict: {} (list) --> {} (dict) w/ keys {}'.format(key_, key_, newkey_), topic=debug_topic)
                    if isinstance(a_[key_], list):
                        newkey_ = tolist(newkey_)
                        # Make sure newkey_ is long enough and pad it with a range() of the remaining indices if needed.
                        n1 = len(tolist(a_[key_]))
                        n2 = len(newkey_)
                        if n1 > n2:
                            newkey_ += list(range(n2, n1))
                        newval = SortedDict([[newkey_[ii], a_[key_][ii]] for ii in range(n1)])
                        # Note: if newkey_ is longer than a_[key_], then not all of the values from newkey_ will be
                        # used. This is fine and it is consistent with input.dat leaving off the last number sometimes
                        # if it wants to let it go to the default value.
                        newval['__collapse_to_list_on_output__'] = True
                        a_[key_] = newval
                    else:
                        printd('  Ooops, this item is not a list. Aborting rename. Maybe it was not parsed properly?', topic=debug_topic)
                return a_

            def count_comment_lines(parent_):
                """Assuming the keys are named 1, 2, 3, ... (ints like 1 not strings like '1'), find the first one
                which isn't a string starting with *. I think that an arbitrary number of these are allowed at the start
                of each block."""
                comments = 1
                while comments in parent_ and isinstance(parent_[comments], str) and parent_[comments].startswith('*'):
                    comments += 1
                printd('     count_comment_lines() is returning {}'.format(comments - 1), topic=debug_topic)
                return comments - 1

            def rename_comment_lines(parent_, tag=''):
                """Renames comment lines in parent dictionary (if any) and returns number of comment lines. Can include
                an optional tag (like the block number) in the comment name."""
                ocl = count_comment_lines(parent_)
                for ii in range(ocl):
                    key_rename(parent_, ii + 1, 'comment{}_{}'.format(tag, string.ascii_lowercase[ii]))
                return ocl

            # The names used in renaming are from the Eirene manual version 2017 July 31.
            # The Eirene manual can be found in SOLPS documentation.

            # Renaming of specific blocks can be turned on/off for debugging (side effect: easy code folding :) )
            rename_blocks = [None, True, True, True, True, True, True, True, True, True, True, True]

            if rename_blocks[1]:
                # Handle block 1, which has operating mode. Names for renaming block 1 came from the manual,
                # page 69, with details given on pages 69--76.

                # Find block 1's exact tag name, even if slight changes to it were made (whitespace, punctuation, etc.)
                b1name = find_closest_key(list(self.keys()), block_id=1)
                printd('block1_name =', b1name, topic=debug_topic)
                block1 = ghost[b1name]

                ocl1 = rename_comment_lines(block1, '1')  # Opening Comment Lines in block 1 (may be zero)

                # Renaming instructions for block
                second_required = 2 + ocl1  # Index of the second required card can change if optional cards are present
                #                           between required cards 1 and 2.
                second_optional = 3 + ocl1  # The second optional card can also be displaced (second out of possible
                #                           optional cards, not out of optional cards which are actually present in a
                #                           given deck).

                # Find out if there is an optional card after the first required one. The second mandatory card is a
                # list of bools, whereas the second optional card is ints (or at least numbers; maybe floats are allowed
                # for some).
                optional_card_1_present = not isinstance(tolist(block1[second_required])[0], bool)
                if optional_card_1_present:
                    # This card is only for EIRENE_2002 and younger and is optional in these versions.
                    printd('  Detected optional card 1 in block 1 of Eirene input.dat.', topic=debug_topic)
                    first_optional_card = {
                        second_required: [
                            'NOPTIM',
                            'NOPTM1',
                            'NGEOM_USR',
                            'NCOUP_INPUT',
                            'NSMSTRA',
                            'NSTORAM',
                            'NGSTAL',
                            'NRTAL',
                            'NCREAC_ADD',
                        ]
                    }
                    second_required += 1  # Index of the second mandatory card displaced by insertion of optional card
                    second_optional += 1  # Other optional cards displaced as well
                else:
                    printd('  Optional card 1 not detected in block 1 of input.dat.', topic=debug_topic)
                    first_optional_card = None

                more_optional_cards_present = len(block1) - 1 - 2 - int(optional_card_1_present)
                printd(
                    '  Detected {} instances of optional card type 2 in block 1 of Eirene input.dat.'.format(more_optional_cards_present),
                    topic=debug_topic,
                )
                if more_optional_cards_present:
                    # These cards are only for EIRENE_2005 & younger and are optional. There can be any number of these.
                    opt_card2_contents = ['CFILE', 'DBHANDLE', 'DBFNAME']
                    more_optional_cards = {}
                    for i in range(more_optional_cards_present):
                        more_optional_cards[second_optional + i] = opt_card2_contents
                else:
                    more_optional_cards = None

                renames1 = {
                    1 + ocl1: ['NMACH', 'NMODE', 'NTCPU', 'NFILE', 'NITER0', 'NITER', 'NTIME0', 'NTIME'],
                    second_required: [
                        'NLSCL',
                        'NLTEST',
                        'NLANA',
                        'NLDRFT',
                        'NLCRR',
                        'NLERG',
                        'NLIDENT',
                        'NLONE',
                        'NLMOVIE',
                        'NLDFST',
                        'NLOLDRAN',
                        'NLCASCAD',
                        'NLOCTREE',
                        'NLWRMSH',
                    ],
                }

                # Put in optional cards if appropriate
                if first_optional_card is not None:
                    printd('   Inserting block 1 optional card 1 instructions into renaming dictionary...', topic=debug_topic)
                    renames1.update(first_optional_card)
                if more_optional_cards is not None:
                    printd(
                        '   Inserting block 1 optional card 2 instructions (x{}) into renaming dictionary...'.format(
                            more_optional_cards_present
                        ),
                        topic=debug_topic,
                    )
                    renames1.update(more_optional_cards)

                # Do the renaming
                for k, v in list(renames1.items()):
                    key_rename(block1, k, v)

                # Followup additional renaming
                renames1b = {1: 'Global_options_int', second_required: 'Global_options_bool'}
                for k, v in list(renames1b.items()):
                    key_rename(block1, k, v)

            if rename_blocks[3]:
                # Handles block 3A and 3B, which have data for surfaces. Names for renaming block 3a came from the
                # manual, pages 90--91, with details given on pages 91--92. Names for renaming block 3b came from
                # pages 94--95, with details on pages 95--103.

                # Block 3A ------------------------------------------ - - - - - - - - - - - - - - - - - - - - - - - - -

                # Find block 3a's exact tag name, even if slight changes to it were made (whitespace, punctuation, etc.)
                b3a_name = find_closest_key(list(self.keys()), block_id='3a')
                printd('block3a_name =', b3a_name, topic=debug_topic)
                block3a = ghost[b3a_name]

                ocl3a = rename_comment_lines(block3a, '3A')  # Opening Comment Lines in block 3a (may be zero)

                # Find sub-blocks. Block 3a only has one top level key and one fake top level key ('__name__'), so all
                # the other keys go to sub-blocks (unless there are comments).
                subs3a = list(block3a.keys())
                subs3a.remove('__name__')
                subs3a.remove(1 + ocl3a)
                if ocl3a:
                    for i in range(ocl3a):
                        subs3a.remove('comment3A_{}'.format(string.ascii_lowercase[i]))

                # Renaming instructions for the first few values in the top level block (not in the sub-blocks).
                renames3a = {1 + ocl3a: 'NSTSI'}

                # Do the high level renaming
                for k, v in list(renames3a.items()):
                    key_rename(block3a, k, v)

                # Define the contents of the sub-blocks in block 3a (these are not real sub-blocks from Eirene's
                # perspective as they are separated by one-star (*) comment lines and not two-star (**) sub-block
                # titles. However, OMFIT breaks these into separate dictionaries for convenience, so we'll treat the
                # like sub-blocks).

                # The first group should always be present
                surf_group_a = {
                    1: ['ISTS', 'IDIMP', 'INUMP(ISTSI,IDIMP)', 'IRPTA1', 'IRPTE1', 'IRPTA2', 'IRPTE2', 'IRPTA3', 'IRPTE3'],
                    2: ['ILIIN', 'ILSIDE', 'ILSWCH', 'ILEQUI', 'ILTOR', 'ILCOL', 'ILFIT', 'ILCELL', 'ILBOX', 'ILPLG'],
                }
                # The next group is optional and the default particle-surface model will be activated for this surface
                # element if it is omitted.
                surf_group_b = {
                    3: ['ILREF', 'ILSPT', 'ISRS', 'ISRC'],
                    4: ['ZNML', 'EWALL', 'EWBIN', 'TRANSP(1,N)', 'TRANSP(2,N)', 'FSHEAT'],
                    5: ['RECYCF', 'RECYCT', 'RECPRM', 'EXPPL', 'EXPEL', 'EXPIL'],
                }
                # The last group is an optional piece of group b. Group c should not be used without group b.
                surf_group_c = {6: ['RECYCS', 'RECYCC', 'SPTPRM']}

                # Rename keys in the sub-blocks
                for sub_name in subs3a:
                    b3r = copy.deepcopy(surf_group_a)
                    kk = list(block3a[sub_name].keys())
                    extra_lines = len(kk) - 1 - 2  # 2 required lines and one __name__ entry
                    if extra_lines:
                        # Optional lines have been provided
                        printd('     > Extra lines detected for optional settings', topic=debug_topic)

                        # See if one of the optional lines is SURFMOD. This will always be last if it is present.
                        for k in kk:
                            if 'SURFMOD' in block3a[sub_name][k]:
                                printd('     # SURFMOD line detected', topic=debug_topic)
                                # Rename surfmod and decrement the number of extra_lines left to handle
                                key_rename(block3a[sub_name], k, 'SURFMOD')
                                extra_lines -= 1

                        # Handle any remaining extra lines.
                        if extra_lines == 0:
                            printd('         ^ There are NO extra lines (after handling surfmod, if needed)! Done!', topic=debug_topic)
                        elif extra_lines == 3:
                            # There are more extra lines besides just SURFMOD and they are group b
                            printd('         $ 3 extra lines (after handling surfmod, if needed); must be surf_group_b', topic=debug_topic)
                            b3r.update(surf_group_b)
                        elif extra_lines == 4:
                            printd('         % 4 extra lines (after surfmod, if needed)! Must be surf_group_b & c', topic=debug_topic)
                            b3r.update(surf_group_b)
                            b3r.update(surf_group_c)
                        else:
                            printe(
                                "Parsing input.dat, block 3a: {} of extra lines left in subblock {} after handling "
                                "surfmod: doesn't correspond to a recognized case!".format(extra_lines, sub_name)
                            )
                    for k, v in list(b3r.items()):
                        key_rename(block3a[sub_name], k, v)

                # Block 3B ------------------------------------------ - - - - - - - - - - - - - - - - - - - - - - - - -

                # Find block 3b's exact tag name, even if slight changes to it were made (whitespace, punctuation, etc.)
                b3b_name = find_closest_key(list(self.keys()), block_id='3b')
                printd('block3b_name =', b3b_name, topic=debug_topic)
                block3b = ghost[b3b_name]

                ocl3b = rename_comment_lines(block3b, '3B')  # Opening Comment Lines in block 3b (may be zero)

                # Find sub-blocks. There can apparently be an arbitrary number of stings ("CH0-cards", each with its own
                # line?) stuffed in here, so just pick out the dictionaries.
                subs3b = list(block3b.keys())
                for key in copy.copy(subs3b):
                    if not isinstance(block3b[key], dict):
                        subs3b.remove(key)

                # Renaming instructions for the first few values in the top level block (not in the sub-blocks).
                renames3b = {1 + ocl3b: 'NLIMI'}

                # Do the high level renaming
                for k, v in list(renames3b.items()):
                    key_rename(block3b, k, v)

                # Handle the sub blocks in 3b (again, not real Eirene sub-blocks, but convenient to treat them like it)
                for sub_name in subs3b:
                    sub = block3b[sub_name]
                    # This thing can open with "CH1-cards" and "CH2-cards", which are strings, so find the first
                    # line with numbers on it.
                    subkeys = list(sub.keys())
                    subkeys.remove('__name__')
                    first_numbers = 0  # There isn't a 0, so getting this back would indicate a problem.
                    i = 0
                    while first_numbers == 0 and i <= len(subkeys):
                        if not isinstance(sub[subkeys[i]], str):
                            first_numbers = subkeys[i]
                        i += 1
                    printd('     parse 3b sub {}: first numbers found on line {}'.format(sub_name, first_numbers), topic=debug_topic)

                    # First group of renames
                    renames3b_sub = SortedDict(
                        [
                            [first_numbers + 0, 'general_surface_data_1'],
                            ['general_surface_data_1', ['RLBND', 'RLARE', 'RLWMN', 'RLWMX']],
                            [first_numbers + 1, 'general_surface_data_2'],
                            [
                                'general_surface_data_2',
                                ['ILIIN', 'ILSIDE', 'ILSWCH', 'ILEQUI', 'ILTOR', 'ILCOL', 'ILFIT', 'ILCELL', 'ILBOX', 'ILPLG'],
                            ],
                        ]
                    )
                    for k, v in list(renames3b_sub.items()):
                        key_rename(sub, k, v)

                    # Additional renames
                    rlbnd = sub['general_surface_data_1']['RLBND']
                    if rlbnd <= 1:
                        # This isn't tested because I don't have an example
                        renames3b_sub2 = {
                            first_numbers + 2: ['A0LM', 'A1LM', 'A2LM', 'A3LM', 'A4LM', 'A5LM'],
                            first_numbers + 3: ['A6LM', 'A7LM', 'A8LM', 'A9LM'],
                        }
                        if rlbnd < 0:
                            # RLBND is interpreted as -KL, so K is the first digit and L is the second, and they control
                            # how many copies of line s3c (L) and how many copies of block s3bl (K) are present.
                            # Block s3bl has 2 lines: s3bl1 and s3bl2.
                            rlbnd_k = int(-sub['general_surface_data_1']['RLBND'] // 10)
                            rlbnd_l = -(sub['general_surface_data_1']['RLBND'] + rlbnd_k * 10)

                            s3c = ['ALIMS', 'XLIMS', 'YLIMS', 'ZLIMS']
                            s3bl1 = ['ALIMS0', 'XLIMS1', 'YLIMS1', 'ZLIMS1', 'XLIMS2', 'YLIMS2']
                            s3bl2 = ['ZLIMS2', 'XLIMS3', 'YLIMS3', 'ZLIMS3']

                            for i in range(rlbnd_l):
                                renames3b_sub2[first_numbers + 4 + i] = s3c
                            for i in range(rlbnd_k):
                                renames3b_sub2.update(
                                    {first_numbers + 4 + rlbnd_l + i * 2: s3bl1, first_numbers + 5 + rlbnd_l + i * 2: s3bl2}
                                )
                        if rlbnd == 1:
                            renames3b_sub2.update({first_numbers + 5: ['XLIMS1', 'YLIMS1', 'ZLIMS1', 'XLIMS2', 'YLIMS2', 'ZLIMS2']})
                    else:  # RLBND >= 2
                        # All of the entries in my example are RLBND == 2
                        renames3b_sub2 = {first_numbers + 2: ['P1(1,..)', 'P1(2,..)', 'P1(3,..)', 'P2(1,..)', 'P2(2,..)', 'P2(3,..)']}
                        if rlbnd > 2:
                            # The manual specifies k > 2 here (see the comment in the rlbnd < 0 case), but
                            # interpretation of rlbnd into -KL was specified only for rlbnd < 0, so I've assumed that
                            # they meant rlbnd > 2 instead of k > 2, which hasn't been properly defined for this case.
                            renames3b_sub2[first_numbers + 2] = ['P3(1,..)', 'P3(2,..)', 'P3(3,..)', 'P4(1,..)', 'P4(2,..)', 'P4(3,..)']
                        if rlbnd > 4:
                            renames3b_sub2[first_numbers + 3] = ['P5(1,..)', 'P5(2,..)', 'P5(3,..)']

                    for k, v in list(renames3b_sub2.items()):
                        key_rename(sub, k, v)

                    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    # surf_group_b and surf_group_c can optionally appear between the above and SURFMOD.
                    # I didn't implement the renaming here yet because I am not equipped to test it properly.

                    # See if one of the optional lines is SURFMOD. In 3B, this doesn't have to be the last line
                    for k in list(sub.keys()):
                        printd(' test key k {}'.format(k), topic=debug_topic)
                        if 'SURFMOD' in sub[k]:
                            key_rename(sub, k, 'SURFMOD')

                    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                    # A TRANSFORM block can appear here at the end (optional).

            if rename_blocks[4]:
                # Handle block 4, which has data for atomic physics module. Names for block 4 came from the manual,
                # pages 107--109, with details given on the following pages.
                b4name = find_closest_key(list(self.keys()), block_id='4')
                printd('block4_name =', b4name, topic=debug_topic)
                block4 = ghost[b4name]

                rename_comment_lines(block4, '4')  # Opening Comment Lines in block 4 (may be none)
                # Block 4 does not have any top level data; its only children are sub-blocks and possibly comments.

                # Identify sub-blocks in block 4
                react_name = find_closest_key(list(block4.keys()), 'reactions')
                printd('      react_name = {}'.format(react_name), topic=debug_topic)
                reactions = block4[react_name]
                block4a = block4[find_closest_key(list(block4.keys()), block_id='4a')]
                block4b = block4[find_closest_key(list(block4.keys()), block_id='4b')]
                block4c = block4[find_closest_key(list(block4.keys()), block_id='4c')]
                block4d_name = find_closest_key(list(block4.keys()), block_id='4d')
                if '4d' in block4d_name:
                    block4d = block4[block4d_name]
                else:
                    printd('  No block 4d', topic=debug_topic)
                    block4d = None

                renames_reactions = {1: 'NREACI'}
                renames_4a = {1: 'NATMI'}
                renames_4b = {1: 'NMOLI'}
                renames_4c = {1: 'NIONI'}
                renames_4d = {1: 'NPHOTI'}

                sub_blocks = [reactions, block4a, block4b, block4c, block4d]
                sub_renames = [renames_reactions, renames_4a, renames_4b, renames_4c, renames_4d]
                for sub_block, sub_rename in zip(sub_blocks, sub_renames):
                    if sub_block is not None:
                        for k, v in list(sub_rename.items()):
                            key_rename(sub_block, k, v)

            if rename_blocks[5]:
                # Handle block 5, which has information about the plasma background. Names for block 5 came from the
                # manual, pages 134--135, with details given on the following pages.

                # Find block 5's exact tag name, even if slight changes to it were made (whitespace, punctuation, etc.)
                b5name = find_closest_key(list(self.keys()), block_id='5')
                printd('block5_name =', b5name, topic=debug_topic)
                block5 = ghost[b5name]

                ocl5 = rename_comment_lines(block5, '5')  # Opening Comment Lines in block 5
                block5_renames = {ocl5 + 1: 'NPLSI'}

                # Do the renaming
                for k, v in list(block5_renames.items()):
                    key_rename(block5, k, v)

                # The rest of the block contains mixtures of strings and numbers in a special format. Deal with that
                # when it becomes necessary.

            if rename_blocks[6]:
                # Handle block 6, which has data for surface interaction models. Names for block 6 came from the manual,
                # pages 142--143, with details given on pages 143--

                # Find block 6's exact tag name, even if slight changes to it were made (whitespace, punctuation, etc.)
                b6name = find_closest_key(list(self.keys()), block_id='6a')
                printd('block6a_name =', b6name, topic=debug_topic)
                block6a = ghost[b6name]

                ocl6a = rename_comment_lines(block6a, '6A')  # Opening Comment Lines in block 6a (may be none)

                # Detect path card
                path_card_present = 'PATH' in str(block6a[2 + ocl6a]).upper()

                # Count "target-projectile specification cards". They look like "D_on_C" for deuterium on carbon or
                # "C_on_C" for carbon on carbon. They will be parsed by OMFIT as strings.
                keys6 = list(block6a.keys())
                keys6.remove('__name__')  # Ignore the original block name
                keys6.remove(1 + ocl6a)  # Ignore NLTRIM
                first_numbers = 0  # There isn't a 0, so getting this back would indicate a problem.
                i = ocl6a
                while first_numbers == 0 and i <= len(keys6):
                    if not isinstance(block6a[keys6[i]], str):
                        first_numbers = keys6[i]
                    i += 1
                num_a_on_b_cards = first_numbers - 1 - 1 - int(path_card_present) - ocl6a  # One of the -1 hits is for NLTRIM

                def get_either_key(parent_dict, key1, key2):
                    """Handles alternative keys in case parsing of earlier blocks is turned off."""
                    result = parent_dict.get(key1, None)
                    if result is None:
                        result = parent_dict.get(key2, None)
                    return result

                # Decide if DPHT is included
                block4 = self[find_closest_key(list(self.keys()), block_id='4')]
                b4k = list(block4.keys())
                b4k.remove('__name__')
                include_dpht = False  # Default to False if we can't figure this out
                block4d_name = find_closest_key(list(block4.keys()), block_id='4d')
                if '4d' in block4d_name:
                    block4d = block4[block4d_name]
                    nphoti = get_either_key(block4d, 'NPHOTI', 1)
                    include_dpht = nphoti > 0
                else:
                    printd('  No block 4d', topic=debug_topic)
                    nphoti = None

                # Look for surface models and convert them into their own dictionaries, moving relevant keys from the
                # top level.
                surfmod_keys = [k for k in keys6 if 'SURFMOD' in str(block6a[k]).upper()]
                surfmods = [block6a[k] for k in surfmod_keys]
                printd('    found surface models in block6a: {}'.format(surfmod_keys), topic=debug_topic)
                b6a_surfmod_renames = {
                    1: ['ILREF', 'ILSPT', 'ISRS', 'ISRC'],
                    2: ['ZNML', 'EWALL', 'EWBIN', 'TRANSP(1,N)', 'TRANSP(2,N)', 'FSHEAT'],
                    3: ['RECYCF', 'RECYCT', 'RECPRM', 'EXPPL', 'EXPEL', 'EXPIL'],
                    4: ['RECYCS', 'RECYCC', 'SPTPRM', 'ESPUTS', 'ESPUTC'],  # Optional; default sputter model if omitted
                }
                for i, k in enumerate(surfmod_keys):
                    key_rename(block6a, k, block6a[k])
                    block6a[surfmods[i]] = {1: block6a.pop(k + 1), 2: block6a.pop(k + 2), 3: block6a.pop(k + 3)}
                    j = 4
                    while (k + j) in keys6 and (k + j) not in surfmod_keys:
                        # If this key is present (not off the end of the block) and it is not the start of a new surface
                        # model, then it must be the 4th (optional) key in the current surface model, or one of the
                        # extra optional VARNAME SPZNAME VALUE lines, of which there can be any number.
                        block6a[surfmods[i]][j] = block6a.pop(k + j)
                        j += 1
                    printd('    Done migrating surfmod info to new surfmod dictionaries', topic=debug_topic)
                    for kk, v in list(b6a_surfmod_renames.items()):
                        if kk in block6a[surfmods[i]]:
                            key_rename(block6a[surfmods[i]], kk, v)

                # Find line with ERMIN, ERCUT, etc.
                if surfmod_keys:
                    # This is the line before the first surface model
                    erminline = surfmod_keys[0] - 1
                else:
                    # This is the last line in the file
                    erminline = keys6[-1]
                printd('     I think ERMIN is on line {}'.format(erminline), topic=debug_topic)

                # Convenient shortcut to first line of DADT.
                n = int(path_card_present + num_a_on_b_cards + ocl6a)

                # Determine how much space is allowed for each of the DADT, DMLD, DIOD, DPLD, and DPHT arrays. They can
                # be zero padded with each one stretching onto multiple lines.
                # The lengths of the arrays are NATM, NMOL, etc. The lengths of the parts of the arrays which are
                # actually USED are NATMI, NMOLI, etc. The *I lengths are stored in the other blocks. I haven't found
                # the real lengths on disk (not ending in I) yet. Pull out the *I lengths to use as a sanity check on
                # the automatic length finder.
                natmi = get_either_key(block4[find_closest_key(list(block4.keys()), block_id='4a')], 'NATMI', 1)
                nmoli = get_either_key(block4[find_closest_key(list(block4.keys()), block_id='4b')], 'NMOLI', 1)
                nioni = get_either_key(block4[find_closest_key(list(block4.keys()), block_id='4c')], 'NIONI', 1)
                nplsi = get_either_key(self[find_closest_key(list(self.keys()), block_id='5')], 'NPLSI', 2)
                # NPLSI IS A COMMENT
                min_lines_per_array = np.array([int(natmi), int(nmoli), int(nioni), int(nplsi) / 2.0]) / 6.0
                if include_dpht:
                    min_lines_per_array = np.append(min_lines_per_array, nphoti)
                min_lines_per_array = min_lines_per_array.max()
                array_lines = erminline - n - 1
                arrays = 4 + include_dpht
                multi_line_arrays = array_lines > arrays
                printd(
                    '        there are {} lines of DADT, etc. arrays to hold {} arrays. '
                    'Some lines are multi-line = {}'.format(array_lines, arrays, multi_line_arrays),
                    topic=debug_topic,
                )
                datd_line = 2 + n
                # Figure out how many lines for each array. This way isn't guaranteed to be completely robust.
                arrays += 1  # DPLD (with zero padding) seems to be twice as long as each of DADT, DMLD, and DIOD
                lines_per_array = array_lines // arrays
                # Sanity check: make sure the number of lines per array is enough. This will fail if one array is much
                # longer than the others, other than nplsi which is assumed to be double the length of the others.
                if lines_per_array < min_lines_per_array:
                    lines_per_array = min_lines_per_array
                # Find the lines where the arrays start
                dmld_line = datd_line + lines_per_array * 1
                diod_line = datd_line + lines_per_array * 2
                dpld_line = datd_line + lines_per_array * 3
                # DPHT may not be present. But if it is, it will start on this line:
                dpht_line = datd_line + lines_per_array * (4 + multi_line_arrays)  # Assumed that dpld is twice as long

                # Renaming instructions for block 6a
                renames6a = {
                    1 + ocl6a: 'NLTRIM',
                    datd_line: 'DATD',
                    dmld_line: 'DMLD',
                    diod_line: 'DIOD',
                    dpld_line: 'DPLD',
                    erminline: ['ERMIN', 'ERCUT', 'RPROB0', 'RINTEG', 'EINTEG', 'AINTEG'],
                }
                lines = list(map(int, [datd_line, dmld_line, diod_line, dpld_line, dpht_line]))
                line_names = ['DATD', 'DMLD', 'DIOD', 'DPLD', 'DPHT']
                if include_dpht:
                    renames6a[dpht_line] = 'DPHT'
                    lines += [erminline]
                # Renaming instructions for continuation lines
                for j in range(len(lines) - 1):
                    for i in range(lines[j] + 1, lines[j + 1], 1):
                        renames6a[i] = '{}_continued_{}'.format(line_names[j], i - lines[j])

                # Do the renaming
                for k, v in list(renames6a.items()):
                    key_rename(block6a, k, v)

            if rename_blocks[7]:
                # Handle block 7, which has particle stats and stuff. Names for renaming block 7 came from the manual,
                # page 156, with details given on pages 157--170.

                # Find block 7's exact tag name, even if slight changes to it were made (whitespace, punctuation, etc.)
                b7name = find_closest_key(list(self.keys()), block_id='7')
                printd('block7_name =', b7name, topic=debug_topic)
                block7 = ghost[b7name]

                ocl7 = rename_comment_lines(block7, '7')  # Opening Comment Lines in block 7 (may be none)

                # Renaming instructions for the first few values in the top level block (not in the sub-blocks).
                renames7 = {1 + ocl7: 'NSTRAI', 2 + ocl7: 'INDSRC(ISTRA)', 3 + ocl7: 'ALLOC'}
                # Do the high level renaming
                for k, v in list(renames7.items()):
                    key_rename(block7, k, v)

                # Renaming instructions for the sub-blocks
                sub_renames7 = {
                    1: ['NLAVRP', 'NLAVRT', 'NLSYMP', 'NLSYMT'],
                    2: ['NPTS', 'NINITL', 'NEMODS', 'NAMODS', 'NMINPTS'],
                    3: ['FLUX', 'SCALV', 'IVLSF', 'ISCLS', 'ISCLT', 'ISCL1', 'ISCL2', 'ISCL3', 'ISCLB', 'ISCLA'],
                    4: ['NLATM', 'NLMOL', 'NLION', 'NLPLS', 'NLPHOT'],
                    5: 'NSPEZ',
                    6: ['NLPNT', 'NLLNE', 'NLSRF', 'NLVOL', 'NLCNS'],
                    7: 'NSRFSI',
                }
                nsrfsi_deck = [
                    ['INUM', 'INDIM', 'INSOR', 'INGRDA(1)', 'INGRDE(1)', 'INGRDA(2)', 'INGRDE(2)', 'INGRDA(3)', 'INGRDE(3)'],
                    ['SORWGT', 'SORLIM', 'SORIND', 'SOREXP', 'SORIFL'],
                    ['NSOR', 'NPSOR', 'NTSOR', 'NBSOR', 'NASOR', 'NISOR'],
                    ['SORAD1', 'SORAD2', 'SORAD3', 'SORAD4', 'SORAD5', 'SORAD6'],
                ]
                sub_renames7b = {  # nsrfsi_ind+1+nsrfsi*4 will be added to the keys
                    0: ['SORENI', 'SORENE', 'SORVDX', 'SORVDY', 'SORVDZ'],
                    1: ['SORCOS', 'SORMAX', 'SORCTX', 'SORCTY', 'SORCTZ'],
                }

                # Do the renaming within each sub-block.
                for sub in list(block7.keys()):
                    if isinstance(block7[sub], dict):
                        printd('  block7 sub {} is a dict'.format(sub), topic=debug_topic)
                        for k, v in list(sub_renames7.items()):
                            block7[sub] = key_rename(block7[sub], k, v)
                        nsrfsi = block7[sub]['NSRFSI']
                        nsrfsi_ind = 7
                        for k in range(nsrfsi):
                            printd('   nsrfsi loop, k = {}'.format(k), topic=debug_topic)
                            for i in range(4):
                                printd('     nsrfsi inner loop, i = {}; {}'.format(i, nsrfsi_deck[i]), topic=debug_topic)
                                block7[sub] = key_rename(block7[sub], nsrfsi_ind + 1 + k * 4 + i, nsrfsi_deck[i])
                        for k, v in list(sub_renames7b.items()):
                            block7[sub] = key_rename(block7[sub], k + nsrfsi_ind + 1 + nsrfsi * 4, v)

            rename_blocks[11] = False  # I don't know what's going on with this yet. Don't use.
            if rename_blocks[11]:
                printe('Parsing of block 11 is not ready yet. Do not use.')
                # The manual is not consistent with my sample input.dat and I don't know how Eirene will interpret this.

                # Find block 11's exact tag name, even if slight changes to it were made (whitespace, punctuation, etc.)
                output_name = '11. Data for numerical and graphical output'  # Approx. name; variation may be allowed.
                block11_name = find_closest_key(list(self.keys()), output_name)

                printd('self.keys() =', list(self.keys()), topic=debug_topic)
                printd('block11_name =', block11_name, topic=debug_topic)
                block11 = ghost[block11_name]

                # Set up trcsrcs subset
                block7 = ghost[find_closest_key(list(self.keys()), block_id='7')]
                try:
                    nstrai = block7['NSTRAI']
                except KeyError:
                    nstrai = block7[1]  # If block 7 wasn't parsed

                trcsrcs = ['TRCSRC({})'.format(i) for i in range(nstrai)]

                # Enforce formatting. Some of these are supposed to be lists but could've gone to ints if only one
                # element was supplied in input.dat (which is allowed as the missing one will get its default value).
                block11[3] = tolist(block11[3])

                # Get nvolpr and nsurpr because they define how many lines there are
                nvolpr = block11[3][0]
                # nsurpr = block11[4+nvolpr]

                # Renaming instructions for block 11
                renames11 = {
                    1: [
                        'TRCPLT',
                        'TRCHST',
                        'TRCNAL',
                        'TRCREA',
                        'TRCSIG',
                        'TRCGRD',
                        'TRCSUR',
                        'TRCREF',
                        'TRCFLE',
                        'TRCAMD',
                        'TRCINT',
                        'TRCLST',
                        'TRCSOU',
                        'TRCREC',
                        'TRCTIM',
                        'TRCBLA',
                        'TRCBLM',
                        'TRCBLI',
                        'TRCBLP',
                        'TRCBLE',
                    ],
                    2: ['TRCBLPH', 'TRCTAL', 'TRCOCT', 'TRCCEN', 'TRCRNF'] + trcsrcs,
                    3: ['NVOLPR', 'NSPCPR'],
                    4 + nvolpr: 'NSURPR',
                    # 5+nvolpr+nsurpr: 'NLTVOUT'
                }
                # Do the high level renaming
                for k, v in list(renames11.items()):
                    key_rename(block11, k, v)

        except Exception:
            printe('Failed to parse file {} as input.dat'.format(self.filename))
            printe(''.join(traceback.format_exception(*sys.exc_info())))
            printw(
                'Because of this failure, the file will be parsed as a generic OMFITsolps-dict-like instance '
                'without the input.dat-specific field identification.'
            )
            printw('Failure to identify fields in input.dat could result from SOLPS version incompatibility.')
        else:
            for block_name in list(self.keys()):
                self[block_name] = ghost[block_name]

        # End of renaming section

        printd('OMFITsolps load() complete!', topic=debug_topic)

    # ------------------------------------------------------------------------------------------------------------------

    @dynaSave
    def save(self):
        printd('OMFITsolps save()...', topic=debug_topic)
        strip_trailing_whitespace = False  # Stripping it can cause some files to not be read properly & SOLPS to fail.

        def print_format(x_):
            if isinstance(x_, str):
                return x_
            else:
                return '%3.3g' % x_

        def item_dim_form(item_):
            dim = self[item_]['dimension']
            form = self[item_]['format']
            data = self[item_]['data']
            if isinstance(data, (list, tuple, np.ndarray)):
                data = ' '.join(map(print_format, data))
            else:
                data = repr(data)
            dimform = ' (' + dim + '; ' + form + ')' if (dim is not None) and (form is not None) else ''
            return '*' + item_.ljust(14) + dimform + '\n   ' + data

        # b2ai
        if os.path.split(self.filename)[1] == 'b2ai.dat':
            lines = []
            for item in list(self.keys()):
                if item == 'specs':
                    for k in self[item]:
                        if k == 0:
                            lines.append('*specs' + ' '.join([x.rjust(8) for x in list(self[item][k].keys())]))
                        lines.append(repr(str(k)).rjust(6) + ' '.join([str(x).rjust(8) for x in list(self[item][k].values())]))
                else:
                    lines.append(item_dim_form(item))

            with open(self.filename, 'w') as f:
                if strip_trailing_whitespace:
                    f.write('\n'.join([line.rstrip() for line in lines]))
                else:
                    f.write('\n'.join(lines))

        # b2mn and b2ag
        elif os.path.split(self.filename)[1] in ['b2mn.dat', 'b2ag.dat']:
            lines = []
            for item in list(self.keys()):
                if '__' in item[:2]:
                    lines.append(self[item])
                else:
                    lines.append("'" + item + "'   '" + str(self[item]) + "'")
            with open(self.filename, 'w') as f:
                if strip_trailing_whitespace:
                    f.write('\n'.join([line.rstrip() for line in lines]))
                else:
                    f.write('\n'.join(lines))

        # input.dat
        elif os.path.split(self.filename)[1] in ['input.dat']:

            def bool_block(a):
                # Bools are stored in blocks of 5 like this: TTTFF FFTFT FTTFF FTF
                blk = 5
                nn = len(a)
                b = int(np.ceil(nn / float(blk)))
                a = ' '.join([(a + ' ' * (blk * b - nn))[ii * blk : (ii + 1) * blk] for ii in range(b)]).strip()
                return a

            def write_thing(thing_):
                # Decide whether this is a dictionary that was made from a list which should be written as a list.
                try:
                    collapse = thing_['__collapse_to_list_on_output__']
                except (TypeError, KeyError):
                    collapse = False
                if collapse:
                    printd('   Collapsing {} into a list...'.format(thing_), topic=debug_topic)
                    thing_ = [thing_[k_] for k_ in list(thing_.keys()) if not str(k_).startswith('__')]

                thing = tolist(thing_)

                fltform = '{{:{}.{}e}}'.format(self.inputdat_flt_len, self.inputdat_flt_dec)

                if np.all([isinstance(a, bool) or a is None for a in tolist(thing)]):
                    lines.append(bool_block(''.join([{False: 'F', True: 'T'}[a] for a in thing])))
                    printd('            TYPE IS bool', topic=debug_topic)
                elif len(thing) == 2 and isinstance(thing[0], bool) and isinstance(thing[1], int):
                    printd('            TYPE IS special block11 bool/int mix', topic=debug_topic)
                    line_out = '{}{:27d}'.format({False: 'F', True: 'T'}[thing[0]], thing[1])
                    lines.append(line_out)
                elif np.all([is_int(a) for a in thing]):
                    # This will catch bool if it's not trapped first
                    lines.append(''.join([str(x_).rjust(self.inputdat_int_len) for x_ in thing]))
                    printd('            TYPE IS int', topic=debug_topic)
                elif np.all([isinstance(a, float) for a in thing]):
                    lines.append(''.join([fltform.format(x_).replace('e', 'E') for x_ in thing]))
                    printd('            TYPE IS float', topic=debug_topic)
                elif np.all([isinstance(a, float) or isinstance(a, int) for a in thing]):
                    printd('            TYPE IS MIX OF int & float', topic=debug_topic)
                    line_out = ''
                    for a in thing:
                        if isinstance(a, int):
                            af = str(a).rjust(self.inputdat_int_len)
                            line_out += af
                        elif isinstance(a, float):
                            af = fltform.format(a).replace('e', 'E')
                            line_out += af
                        else:
                            # May we never get here
                            printe(
                                'ERROR in writing input.dat: line is supposed to be mix of ints and floats, '
                                'but value {} is neither int nor float.'.format(a)
                            )
                    lines.append(line_out)
                else:
                    lines.append(str(thing_))
                    printd('            TYPE IS other', topic=debug_topic)

                printd('        it came out as ', lines[-1], topic=debug_topic)
                return

            lines = []
            for item in list(self.keys()):
                new_item = self[item].get('__name__', item)
                printd('write {}'.format(new_item), topic=debug_topic)
                lines.append(new_item)
                for k in self[item]:
                    if not str(k).startswith('__'):
                        if isinstance(self[item][k], dict) and ('__collapse_to_list_on_output__' not in self[item][k]):
                            printd('    *>>> writing DICTIONARY self[item][k] = {}'.format(self[item][k]), topic=debug_topic)
                            lines.append(self[item][k].get('__name__', k))
                            for kk in self[item][k]:
                                if not str(kk).startswith('__'):
                                    write_thing(self[item][k][kk])
                        else:
                            printd('     >>> writing self[item][k] = {}'.format(self[item][k]), topic=debug_topic)
                            write_thing(self[item][k])
                    else:
                        printd(' __ not including item {} because it starts with __'.format(k), topic=debug_topic)

            lines.append('')
            with open(self.filename, 'w') as f:
                if strip_trailing_whitespace:
                    f.write('\n'.join([line.rstrip() for line in lines]))
                else:
                    f.write('\n'.join(lines))

        # b2fstate and b2fstati
        elif os.path.split(self.filename)[1] in ['b2fstate', 'b2fstati']:
            printd('Identified b2fstate or b2fstati type file (SAVE).', topic=debug_topic)

            # Start with the header
            lines = copy.deepcopy(self['__notes__'])

            # Define line formats
            field_start_form = '*cf:    {dat_type:8s}    {n:8d}    {name:32s}'
            forms = {'real': ' {: 20.13E}', 'int': ' {:10d}', 'char': ' {}'}  # Up to 6 per row  # don't know limit
            counts = {'real': 6, 'int': 120, 'char': 1}  # Guess, but unlikely to be consequential if wrong
            translations = {'str': 'char', 'string': 'char', 'float': 'real', 'long': 'int'}  # Is this a good idea?

            # Add in the first field, giving dimensions
            lines += [field_start_form.format(dat_type='int', n=3, name='nx,ny,ns')]
            lines += [(forms['int'] * 3).format(self['nx'], self['ny'], self['ns'])]

            # Write each item
            for item in list(self.keys()):
                if item.startswith('__'):
                    pass  # Don't save hidden comments
                elif item in ['nx', 'ny', 'ns']:
                    pass  # Already handled manually
                else:
                    # Multi-dimensional arrays are printed as just plain 1D
                    flat = np.atleast_1d(self[item]).flatten()
                    # Translate the data type back to one of the things that SOLPS understands
                    type_str = type(flat[0]).__name__
                    type_str = ''.join([i for i in type_str if not i.isdigit()]).strip().split('_')[0]
                    type_str = translations.get('{}'.format(type_str), type_str)
                    # Get the length of the data with special treatment for strings
                    n = len(flat)
                    if type_str == 'char' and n == 1:
                        n = len(flat[0])
                    # Put in the field header
                    lines += [field_start_form.format(dat_type=type_str, n=n, name=item)]
                    # Get field info and decide how many rows there are
                    count = counts[type_str]
                    form_ = forms[type_str]
                    rows = int(np.ceil(len(flat) / float(count)))
                    for _ in range(rows):
                        if len(flat) > count:
                            chunk = flat[0:count]
                            flat = flat[count:]
                        else:
                            chunk = flat
                            flat = ''
                        line = ''
                        for j in chunk:
                            entry = form_.format(j)
                            if 'E' in entry:
                                # Make sure the exponent has enough digits. If it only has 2, we have to add one.
                                mantissa, exponent = entry.split('E')
                                if len(exponent) < 4:  # 4 because the sign is included
                                    exponent = exponent[0] + '0' + exponent[1:]
                                entry = 'E'.join([mantissa, exponent])
                            line += entry
                        lines += [line]
            lines += ['']  # Newline at end of file

            with open(self.filename, 'w') as f:
                f.write('\n'.join(lines))  # Note: SOLPS will fail if you strip the trailing white space.

        # Otherwise treat like an ascii file
        else:
            # Put generic writer here which works better than just dumping ASCII. See structure of generic loader.
            super().save()  # First arg is not this class

        printd('OMFITsolps save() complete!', topic=debug_topic)

    def run(self, **kw):
        """
        Activates a GUI to edit the current file in the OMFIT SOLPS module

        :return: 1 if failed or output from relevant SOLPS GUI (probably None)
        """

        root, run_key, locs = find_solps_module_and_run(self)
        if root is None:
            return 1
        root['SETTINGS']['RUNS']['active_run'] = run_key
        root['SETTINGS']['GUI_STATE']['phase'] = 1
        root['__scratch__']['file_to_edit'] = locs[-1]
        if len(kw.keys()):
            printd('      Ignored keywords passed to OMFITsolps.run')
        return root['GUIS']['SOLPS_GUI'].run()

    def __popup_menu__(self):
        return [['Edit', self.run]]

    def __call__(self, **kw):
        return self.run(**kw)

    # End of class OMFITsolps


@_available_to_user_solps
class OMFITsolpsNamelist(OMFITnamelist):
    """
    Special namelist class for SOLPS files.

    - Launches a custom GUI in SOLPS module.
    - Fixes the dimensions of b2.boundary.parameters arrays by setting up collect_arrays() instructions
      (only if collect_arrays keyword is not already specified)
    """

    def __init__(self, filename, **kw):
        if 'b2.boundary.parameters' in filename and 'collect_arrays' not in list(kw.keys()):
            # Special treatment for boundary parameters to get instructions for the array collector

            pregame = OMFITnamelist(filename, **kw)
            nbc = pregame['boundary']['NBC']
            nvalsa = 2  # number of parameter values available to define a boundary condition; group A: ENE, ENI, POT
            nvalsb = 3  # number of parameter values available to define a boundary condition; group B: CON, MOM

            # Set up array collection instructions
            tags2d_a = ['ENEPAR', 'ENIPAR', 'POTPAR']  # tags that have 2 dimensions that aren't species dependent
            tags2d_b = ['BCMOM', 'BCCON']  # tags that have 2 dimensions and are species dependent
            tags3d = ['CONPAR', 'MOMPAR']  # tags that have 3 dimensions (species dependent)

            # Set up offsets for arrays (hopefully there is one and only one way to set these up for SOLPS)
            species_offset = 0
            boundary_offset = 1
            value_offset = 1

            # Number of species
            nspec = max(
                [np.shape(pregame['boundary'][tag])[0] for tag in ['BCCON', 'BCMOM', 'CONPAR', 'mompar'] if tag in pregame['boundary']]
                + [0]
            )
            nspec = nspec - species_offset if nspec > 0 else nspec
            # If nspec is 0, we failed to determine number of species, but we better not need to know. This can happen
            # if the file has none of the BCCON, BCMOM, etc. fields in it. Presumably, they'll be set somewhere else.

            # Offset tuples to supply to array collector
            off2d_a = (boundary_offset, value_offset)
            off2d_b = (species_offset, boundary_offset)
            off3d = (species_offset, boundary_offset, value_offset)

            # Array shape tuples to supply to array collector
            shape2d_a = (nbc, nvalsa)
            shape2d_b = (nspec, nbc)
            shape3d = (nspec, nbc, nvalsb)

            # Finalize instructions for collect_arrays
            collect_arrays = {'__default__': 0}
            for tag in tags2d_a:
                collect_arrays[tag] = {'offset': off2d_a, 'shape': shape2d_a}
            for tag in tags2d_b:
                collect_arrays[tag] = {'offset': off2d_b, 'shape': shape2d_b, 'dtype': 1}
            for tag in tags3d:
                collect_arrays[tag] = {'offset': off3d, 'shape': shape3d}

            kw['collect_arrays'] = collect_arrays

        if 'b2.neutrals.parameters' in filename and 'collect_arrays' not in list(kw.keys()):
            # Special treatment for neutrals parameters to get instructions for the array collector

            pregame = OMFITnamelist(filename, **kw)
            nstrai = pregame['NEUTRALS']['NSTRAI']
            strai_offset = 1
            species_offset = 0
            chem_val_offset = 0
            nvals_chem = 2
            spec_info_1 = [np.shape(pregame['NEUTRALS'][tag])[0] for tag in ['recyc', 'erecyc'] if tag in pregame['NEUTRALS']]
            if spec_info_1:
                # Simple way to find number of species
                nspecies = max(spec_info_1) - species_offset
            else:
                # This file isn't playing nice
                printd('  OMFITsolpsNamelist is using plan B to count species in b2.neutrals.parameters...')
                nspecies_recyc = 0
                nspecies_erecyc = 0
                attempt_up_to = 15
                for attempt in range(attempt_up_to):
                    k1 = 'recyc({},{})'.format(attempt, strai_offset)
                    if k1 in pregame['NEUTRALS']:
                        nspecies_recyc += len(np.atleast_1d(pregame['NEUTRALS'][k1]))
                for attempt in range(attempt_up_to):
                    k1 = 'erecyc({},{})'.format(attempt, strai_offset)
                    if k1 in pregame['NEUTRALS']:
                        nspecies_erecyc += len(np.atleast_1d(pregame['NEUTRALS'][k1]))
                nspecies = max([nspecies_recyc, nspecies_erecyc])
            printd(
                '  OMFITsolpsNamelist determined nspecies = {}, nstrai = {}, nvals_chem = {}, '
                'species_offset = {}, strai_offset = {}, chem_val_offset = {}'.format(
                    nspecies, nstrai, nvals_chem, species_offset, strai_offset, chem_val_offset
                )
            )

            kw['collect_arrays'] = {
                '__default__': 0,
                'erecyc': {'offset': (species_offset, strai_offset), 'shape': (nspecies, nstrai)},
                'recyc': {'offset': (species_offset, strai_offset), 'shape': (nspecies, nstrai)},
                'chem_sput': {'offset': (chem_val_offset, strai_offset), 'shape': (nvals_chem, nstrai)},
            }
            printd('  OMFITsolpsNamelist array collector instructions =\n{}'.format(kw['collect_arrays']))

        OMFITnamelist.__init__(self, filename, **kw)

    def run(self, **kw):
        if os.path.split(self.filename)[1].startswith('b2.') and (
            os.path.split(self.filename)[1].endswith('.parameters') or os.path.split(self.filename)[1].endswith('.inputs')
        ):

            root, run_key, locs = find_solps_module_and_run(self)
            if root is None:
                return 1

            root['SETTINGS']['RUNS']['active_run'] = run_key
            root['SETTINGS']['GUI_STATE']['phase'] = 1
            root['__scratch__']['file_to_edit'] = locs[-1]
            return root['GUIS']['SOLPS_GUI'].run()
        else:
            print('Filename of OMFITsolpsNamelist instance was not recognized as a SOLPS file: {}'.format(os.path.split(self.filename)[1]))
            return OMFITnamelist.run(self, **kw)

    def __popup_menu__(self):
        return [['Edit', self.run]]

    def __call__(self, **kw):
        return self.run(**kw)

    # End of class OMFITsolpsNamelist


OMFITsolpsCase_save_attrs = [
    'debug',
    'common_folder',
    'label',
    'key',
    'custom_required_files',
    'custom_required_files_coupled',
    'custom_required_files_continue',
    'custom_key_outputs',
    'custom_required_files_coupled_continue',
    'use_common_folder',
    'status',
    'version',
]


@_available_to_user_solps
class OMFITsolpsCase(OMFITtree):
    """
    Class for holding SOLPS runs

    Key methods:
    ------------
    - inputs: returns a list of file references for building an input deck. Includes current run and common_folder.

    - check_inputs: returns a list of missing files in the input deck
    """

    def __getattr__(self, attr_name):
        """
        Custom attribute access method
         - https://docs.python.org/3/reference/datamodel.html#customizing-attribute-access
         - https://stackoverflow.com/a/52729406/6605826

        :param attr_name: string
            Name of the attribute

        :return: Attribute value
        """
        if attr_name in OMFITsolpsCase_save_attrs:
            return self.OMFITproperties.get(attr_name, None)
        raise AttributeError(attr_name)

    def __setattr__(self, attr_name, value):
        if attr_name in OMFITsolpsCase_save_attrs:
            self.OMFITproperties[attr_name] = value
            if attr_name.startswith('custom_'):
                # Setting a custom attribute should update the attribute it overrides, as it does in init
                setattr(self, attr_name[len('custom_') :], value)
            return
        super().__setattr__(attr_name, value)  # Doesn't work with reload_python

    def __delattr__(self, attr_name):
        if attr_name in OMFITsolpsCase_save_attrs:
            self.OMFITproperties[attr_name] = None
            if attr_name.startswith('custom_'):
                # Deleting a custom attribute should revert its counterpart to default
                setattr(self, attr_name[len('custom_') :], getattr(self, 'default_' + attr_name[len('custom_') :], None))
            return
        super().__delattr__(attr_name)

    def __init__(
        self,
        filename='',
        label=None,
        common_folder=False,
        baserun=None,
        coupled=True,
        debug=True,
        key=None,
        custom_required_files=None,
        custom_required_files_coupled=None,
        custom_required_files_coupled_continue=None,
        custom_required_files_continue=None,
        custom_key_outputs=None,
        version=None,
        **kw,
    ):
        """
        :param filename: string

        :param label: string

        :param common_folder: bool
            Flag this run as a common folder. It is not a real run. Instead, it holds common files which are shared
            between the run folders.

        :param baserun: bool [deprecated]
            Old name for common_folder. Used to support loading old projects. Do not use in new development.

        :param coupled: bool
            Order a coupled B2.5 + Eirene run instead of a B2.5 standalone run.

        :param debug: bool
            Activate debug mode

        :param key: string [optional]
            Key used in the OMFIT tree

        :param custom_required_files: list of strings [optional]
            Override the standard required_files list in a manner which will persist across updates to the class.
            If this option is not used and the default required_files list in the class changes, class instances will
            update to the new list when they are loaded from saved projects. If the customization is used, even to
            assign the default list, the customized list will persist even if the default changes.

        :param custom_required_files_coupled: list of strings [optional]
            Similar to custom_required_files, but for additional files used in coupled B2.5 + Eirene runs

        :param custom_required_files_continue: list of strings [optional]
            Similar to custom_required_files, but for additional files used to continue the run after initialization

        :param custom_key_outputs: list of strings [optional]
            Similar to custom_required_files, but for key output files

        :param version: string [optional]
            Used to keep track of the SOLPS code version that should be used to run this case. Should be like 'SOLPS5.0'

        :param kw: dict
            Additional keywords passed to super class or used to accept restored attributes.
        """
        super().__init__(filename=filename, **kw)
        self.OMFITproperties = {}
        self.debug = debug
        self.common_folder = baserun or common_folder
        self.label = label
        self.coupled = coupled
        self.key = key
        self.version = version
        if self.label is None and not self.common_folder:
            print('Set the .label attribute (or use the label keyword during initialization) to give your run a label')
        self.use_common_folder = None  # Will be assigned when self.find_cases() is called by __tree_repr__ or any other

        # Declare file lists: these will update when the class is updated unless they are locked in with customization.
        self.default_required_files = [
            'AMJUEL',
            'H2VIBR',
            'HYDHEL',
            'METHANE',
            'SPUTER',
            'fort.21',
            'fort.22',
            'fort.30',
            'fort.31',
            'fort.44',
            'b2mn.dat',
            'b2ag.dat',
            'b2ai.dat',
            'b2ah.dat',
            'b2ar.dat',
            'b2.boundary.parameters',
            'b2.neutrals.parameters',
            'b2.transport.parameters',
            'b2.numerics.parameters',
            'b2fgmtry',
        ]
        self.default_required_files_coupled = ['input.dat']
        self.default_required_files_continue = ['b2ar.prt', 'b2ai.prt', 'b2ah.prt', 'b2fstati']
        self.default_required_files_coupled_continue = ['fort.15']
        self.default_key_outputs = ['b2fstate', 'b2fplasma', 'b2time.nc', 'b2tallies.nc']
        # Apply customizations to file lists: these will persist with OMFIT project save/load
        if custom_key_outputs is not None:
            self.key_outputs = self.custom_key_outputs = custom_key_outputs
        else:
            self.key_outputs = self.default_key_outputs
        if custom_required_files is not None:
            self.required_files = self.custom_required_files = custom_required_files
        else:
            self.required_files = self.default_required_files
        if custom_required_files_coupled is not None:
            self.required_files_coupled = self.custom_required_files_coupled = custom_required_files_coupled
        else:
            self.required_files_coupled = self.default_required_files_coupled
        if custom_required_files_continue is not None:
            self.required_files_continue = self.custom_required_files_continue = custom_required_files_continue
        else:
            self.required_files_continue = self.default_required_files_continue
        if custom_required_files_coupled_continue is not None:
            self.required_files_coupled_continue = custom_required_files_coupled_continue
            self.custom_required_files_coupled_continue = custom_required_files_coupled_continue
        else:
            self.required_files_coupled_continue = self.default_required_files_coupled_continue

        self.status = {'description': 'initialized / blank', 'code': 0, 'flags': {'failed': False}}

        if not self.common_folder:
            self.setdefault('OUT', OMFITtree())

        if self.version == 'SOLPS-ITER':
            # First fill in some assumptions, then try to update them using data from input deck
            self.na_min = 1e12
            # Update from input deck later (during check_setup); the case is probably empty at init so nothing to read

        self.find_cases()
        self.update_status()

        # Make sure all saved attributes are restored by allowing them to be passed in through **kw
        for attr in OMFITsolpsCase_save_attrs:
            kw_attr = kw.pop(attr, None)
            if kw_attr is not None:
                setattr(self, attr, kw_attr)

    def __tree_repr__(self):
        """Returns representation for this object in the OMFIT tree"""
        brl = 'COMMON' if self.common_folder else None
        ncl = '[STANDALONE B2.5]' if not self.coupled else None
        description = ' '.join(
            [i for i in [brl, self.label, self.version, None if self.common_folder else self.status['description'], ncl] if i is not None]
        )
        if self.common_folder:
            cases, common_folders = self.find_cases(quiet=True)
            if len(common_folders) > 1:
                description = 'ERROR: detected {} common_folders. THERE CAN BE ONLY ONE!'.format(len(common_folders))
        else:
            req = self.required_files + self.required_files_coupled if self.coupled else self.required_files
            missing = self.check_inputs(required_files=req, quiet=True)
            if len(missing):
                file_note = ', missing {}/{} inputs'.format(len(missing), len(req))
            else:
                missing_out = self.check_outputs(quiet=True)
                file_note = '' if len(missing_out) or self.common_folder else ', output files complete'
            description += file_note
        return description, []

    def __printds__(self, *arg, **kw):
        """Customized debug print with default topic and class toggle switch"""
        if self.debug:
            kw.setdefault('topic', 'OMFITsolpsCase')
            printd(*arg, **kw)

    def find_cases(self, quiet=False):
        """
        Searches parent item in OMFIT tree to find sibling instances of
        OMFITsolpsCase and identify them as main or common_folder. This won't
        necessarily work the first time or during init because this case
        (and maybe others) won't be in the tree yet.

        :param quiet: bool
            Suppress print statements, even debug
        """

        def printq(*arg):
            header = '  OMFITsolpsCase.find_cases: '
            if not quiet:
                self.__printds__(header, *arg)

        printq('treeLocation(self) = {}'.format(treeLocation(self)))
        try:
            parent = eval(treeLocation(self)[-2])
        except (IndexError, SyntaxError):
            return [], []
        printq('type(parent) = {}, parent.keys() = {}'.format(type(parent), list(parent.keys())))
        printq('isinstance(parent[k]), OMFITsolpsCase = {}'.format([isinstance(parent[k], OMFITsolpsCase) for k in list(parent.keys())]))
        printq('type(parent[k]) = {}'.format([type(parent[k]) for k in list(parent.keys())]))
        solps_cases = [k for k in list(parent.keys()) if isinstance(parent[k], OMFITsolpsCase)]
        common_folders = [k for k in solps_cases if parent[k].common_folder]
        printq('solps_cases = {}, common_folders = {}'.format(solps_cases, common_folders))

        if len(common_folders) == 1:
            self.use_common_folder = common_folders[0]
        else:
            self.use_common_folder = None
        return solps_cases, common_folders

    def inputs(self, quiet=False, no_warnings=True):
        """
        Gathers a set of input files from this run and the common_folder(s).
        Returns only common_folder inputs if this is a common_folder.

        :param quiet: bool
            Suppress printout, even debug

        :param no_warnings: bool
            Suppress warnings about missing files

        :return: list of file references
        """

        def printq(*arg):
            if not quiet:
                self.__printds__(*arg)

        input_files = {k: v for k, v in list(self.items()) if isinstance(v, OMFITascii)}

        if self.common_folder:
            return list(input_files.values())

        if self.use_common_folder is None:
            self.find_cases()

        the_common_folder = None
        if self.use_common_folder is None:
            printq('Could not locate a common_folder OMFITsolpsCase instance from which to draw files.')
        elif isinstance(self.use_common_folder, OMFITsolpsCase) and self.use_common_folder.common_folder:
            printq(
                'Was provided a direct reference to a common_folder instance. This is not the '
                'recommended way to use this system within the OMFIT GUI/framework. This functionality is '
                'provided for use without the OMFIT GUI.'
            )
            the_common_folder = self.use_common_folder
        else:
            try:
                parent = eval(treeLocation(self)[-2])
            except (IndexError, SyntaxError):
                printq('Could not find parent location in OMFIT tree: unable to access common_folder files.')
            else:
                printq('Extending input set using common_folder files...')
                if self.use_common_folder in parent:
                    the_common_folder = parent[self.use_common_folder]
                else:
                    printq('Failed to connect to the common_folder instance. It must have gotten lost or deleted.')
                    self.find_cases()
        if the_common_folder is not None:
            common_folder_files = {k: v for k, v in list(the_common_folder.items()) if isinstance(v, OMFITascii)}
            # Filter common_folder files to avoid overwriting top level input files with common_folder files.
            input_filenames = [os.path.split(f.filename)[1] for f in list(input_files.values())]
            common_folder_files = {
                k: v for k, v in list(common_folder_files.items()) if os.path.split(v.filename)[1] not in input_filenames
            }
            common_folder_files.update(input_files)
            input_files = common_folder_files

        missing_files = self.check_inputs(inputs=list(input_files.values()))
        if not len(missing_files):
            printq('Case labeled {} has access to all required SOLPS input files'.format(self.label))
        elif no_warnings:
            printq('Case {}: Missing files in input deck = {}'.format(self.label, missing_files))
        else:
            warnings.warn(
                'OMFITsolpsCase labeled {} does not have access to all required SOLPS input files. '
                'Missing files = {}'.format(self.label, missing_files)
            )

        if len(input_files):
            printq(
                'Found input files: \n{}'.format('\n'.join(['        {} : {}'.format(k, type(v)) for k, v in list(input_files.items())]))
            )
        else:
            printq('Did not find any input files')

        return list(input_files.values())

    def check_inputs(self, inputs=None, initial=True, required_files=None, quiet=False):
        """
        Checks whether the input deck is complete

        :param inputs: [Optional] list of references to input files
            If this is None, self.inputs() will be used to obtain the list.

        :param initial: bool
            Check list vs. initialization requirements instead of continuation requirements.
            If True, some intermediate files won't be added to the list. If False, it is assumed that the run is being
            continued and there will be more required files.

        :param required_files: [Optional] list of strings
            IF this is None, the default self.required_files or self.required_files+required_files_coupled will be used.

        :param quiet: bool
            Suppress print statements, even debug

        :return: list of strings
            List of missing files. If it is emtpy, then there are no missing files and everything is cool, dude.
        """
        inputs = self.inputs(quiet=quiet, no_warnings=True) if inputs is None else inputs
        if required_files is None:
            required_files = self.required_files + self.required_files_coupled if self.coupled else self.required_files
        if not initial:
            required_files += (
                self.required_files_continue + self.required_files_coupled_continue if self.coupled else self.required_files_continue
            )

        input_filenames = [os.path.split(inp.filename)[1] for inp in inputs]
        missing_files = [required for required in required_files if required not in input_filenames]
        if np.any(['*' in f or '?' in f for f in missing_files]):
            missing_files = [mf for mf in missing_files if not len([fnmatch.filter([ifn], mf) for ifn in input_filenames])]

        return missing_files

    def read_solps_iter_settings(self):
        """
        Attempts to read SOLPS-ITER specific settings or fills in required values with assumptions
        These are special settings that are used in setup checks or similar activities
        :return: None
        """
        settings_found = []  # For testing
        b2mn = self.get_file('b2mn.dat')
        if isinstance(b2mn, OMFITsolps):
            na_min = b2mn.get('b2mndr_na_min', None)
            if na_min is not None:
                if self.na_min != na_min:
                    self.__printds__('Read na_min from b2mn.dat: {}'.format(na_min))
                self.na_min = na_min
                settings_found += [na_min]
        return settings_found

    def check_setup(self, quiet=False):
        """
        Check for obvious setup problems
        :param quiet: bool
        :return: tuple of four lists of stings
            - Descriptions of setup problems
            - Commands to execute to resolve setup problems (first define r to be a reference to this OMFITsolpsCase)
            - Descriptions of minor setup issues
            - Commands to execute to resolve minor setup issues (with r defined as this OMFITsolpsCase)
        """
        self.read_solps_iter_settings()  # Update this at checking time

        setup_problems = []
        solutions = []
        minor_issues = []
        minor_solutions = []

        b2mn = self.get_file('b2mn.dat')
        if isinstance(b2mn, OMFITsolps) and (self.coupled is not None):
            b2mndr_eirene = b2mn.get('b2mndr_eirene', None)
            try:
                # Try to force the flag to int to allow a valid comparison because it might be '1' or something.
                b2mndr_eirene = int(b2mndr_eirene)
            except TypeError:
                pass
            if self.coupled != b2mndr_eirene:
                setup_problems += [
                    'b2mn.dat / b2mndr_eirene flag ({}) does not match case settings ({}).'.format(
                        repr(b2mn.get('b2mndr_eirene', None)), repr(self.coupled)
                    )
                ]
                solutions += ["r.get_file('b2mn.dat')['b2mndr_eirene'] = {}".format(int(self.coupled))]

        if self.version == 'SOLPS-ITER':
            tmp = self._check_setup_iter(quiet)
            setup_problems += tmp[0]
            solutions += tmp[1]
            minor_issues += tmp[2]
            minor_solutions += tmp[3]

        if not quiet:
            if len(setup_problems):
                printw('WARNING: The following problems were detected with setup for run {} labeled {}:'.format(self.key, self.label))
                printw('    \n'.join([''] + setup_problems))

                print('Recommended commands for resolving setup problems ' '(r is a reference to this OMFITsolpsCase instance):')
                print('    \n'.join([''] + solutions))
            else:
                print('No setup problems detected')

        return setup_problems, solutions, minor_issues, minor_solutions

    def _check_setup_iter(self, quiet=False):
        """
        Additional checks for SOLPS-ITER
        :param inputs, initial, required_files: lists; see check_inputs()
        :param quiet:  bool
        :return: list of strings
        """
        setup_problems_iter = []
        solutions_iter = []
        minor_issues_iter = []
        minor_solutions_iter = []
        b2ai = self.get_file('b2ai.dat')
        b2mn = self.get_file('b2mn.dat')
        if not isinstance(b2ai, OMFITsolps):
            if not quiet:
                printw(
                    'Unable to complete some SOLPS-ITER setup checks for {} because b2ai.dat was not '.format(self.key) + 'found'
                    if b2ai is None
                    else 'parsed as OMFITsolps.'
                )
                if b2ai is None:
                    printw('Could not find b2ai.dat; unable to complete SOLPS-ITER setup checks.')
        else:
            naini = b2ai.get('naini', {}).get('data', None)
            if naini is not None:
                naini = np.atleast_1d(naini)
            if not is_numeric(self.na_min) or not is_numeric(naini):
                # This is about a type error for "< not supported between array and str" in naini < self.na_min
                if not quiet:
                    printw(
                        "Warning: problem comparing initial ion density because this run's is_numeric(na_min) = {}, "
                        "is_numeric(b2ai.naini) = {}".format(is_numeric(self.na_min), is_numeric(naini))
                    )
            elif np.any(np.atleast_1d(naini < self.na_min)):
                newdata = np.atleast_1d(copy.copy(naini))
                newdata[np.atleast_1d(naini) < self.na_min] = self.na_min
                problem = 'Some element(s) in b2ai.dat/naini were below na_min={}, ' 'which will cause b2ai to fail.'.format(
                    '{:0.2e}'.format(self.na_min) if is_numeric(self.na_min) else repr(self.na_min)
                )
                solution = "r.get_file('b2ai.dat')['naini']['data'] = {newdata:}".format(na_min=self.na_min, newdata=repr(tolist(newdata)))
                setup_problems_iter += [problem]
                solutions_iter += [solution]

        if isinstance(b2mn, OMFITsolps):
            if b2mn['b2mndr_stim'] == -1:
                minor_issues_iter += ['b2mn.dat / b2mndr_stim should be set to 0 for consistent behavior with ' 'SOLPS5.X setting of -1']
                minor_solutions_iter += ["r.get_file('b2mn.dat')['b2mndr_stim'] = 0"]

        return setup_problems_iter, solutions_iter, minor_issues_iter, minor_solutions_iter

    def check_outputs(self, quiet=False):
        """
        Checks whether key output files are present

        :param quiet: bool
            Suppress print statements, even debug

        :return: list of missing key output files
        """
        if self.common_folder:
            if not quiet:
                self.__printds__('The common_folder does not actually run or produce real final output.')
            return []
        all_files = [os.path.split(v.filename)[1] for k, v in list(self.get('OUT', {}).items()) if isinstance(v, OMFITascii)]
        output_files = [fn for fn in all_files if fn in self.key_outputs]
        missing_files = [output for output in self.key_outputs if output not in output_files]
        if not quiet:
            self.__printds__('OMFITsolpsCase {} has these files: {}'.format(self.label, all_files))
            if len(output_files):
                self.__printds__('OMFITsolpsCase has these key output files: {}'.format(output_files))
            else:
                self.__printds__('OMFITsolpsCase does not have any key output files')

        return missing_files

    def run(self, **kw):
        """
        Activates the current case in the OMFIT SOLPS module

        :return: 1 if failed or output from relevant SOLPS GUI (probably None)
        """

        if len(kw.keys()):
            printd('      Ignored keywords passed to OMFITsolps.run')

        if self.key is None:
            print('key not defined. Skipping .run method.')
            return 1
        try:
            locs = treeLocation(self)
            solps_loc = [loc for loc in locs if getattr(eval(loc), 'ID', None) == 'SOLPS'][-1]
            root = eval(solps_loc)
        except KeyError:
            print('Could not access OMFIT SOLPS module root')
            return 1
        else:
            root['SETTINGS']['RUNS']['active_run'] = self.key
            return root['GUIS']['SOLPS_GUI'].run()

    def update_status(self):
        all_files = [os.path.split(v.filename)[1] for k, v in list(self.items()) if isinstance(v, OMFITascii)]
        all_out_files = (
            []
            if self.common_folder
            else [os.path.split(v.filename)[1] for k, v in list(self.get('OUT', {}).items()) if isinstance(v, OMFITascii)]
        )
        output_files = [fn for fn in all_out_files if fn in self.key_outputs]
        req = self.required_files + self.required_files_coupled if self.coupled else self.required_files
        local_inputs = [fn for fn in all_files if fn in req]
        inputs = self.inputs()
        self.status['flags']['some_files_loaded'] = bool(len(local_inputs))
        self.status['flags']['input_deck_complete'] = len(self.check_inputs(inputs=inputs)) == 0
        self.status['flags']['has_some_outputs'] = bool(len(output_files))
        self.status['flags']['has_all_key_outputs'] = len(self.check_outputs()) == 0 if not self.common_folder else False
        self.status['flags']['has_setup_problems'] = len(self.check_setup(quiet=True)[0]) > 0
        self.status['flags']['has_minor_setup_problems'] = len(self.check_setup(quiet=True)[2]) > 0
        self.status['flags']['active'] = 'job_run' in list(self.keys())
        code = (
            int(self.status['flags']['some_files_loaded'])
            + 2 * int(self.status['flags']['input_deck_complete'])
            + 4 * int(self.status['flags']['has_some_outputs'])
            + 8 * int(self.status['flags']['has_all_key_outputs'])
        )
        self.status['description'] = (
            'bad setup'
            if self.status['flags']['has_setup_problems']
            else 'failed'
            if self.status['flags']['failed']
            else {
                0: 'initialized / blank',
                1: 'loading files',
                3: 'inputs complete',
                4: 'leftover outputs from missing input',
                5: 'leftover outputs from incomplete input',
                7: 'partial output',
                12: 'leftover output from missing input',
                13: 'leftover output from incomplete input',
                15: 'complete',  # YES, this is what we want
            }.get(code, 'file_scan_error')
        )  # 2, 6, 8, 9, 10, 11, 14, & 16+ should be impossible.
        if self.status['flags']['active']:
            self.status['description'] = '(ACTIVE) ' + self.status['description']
        self.status['code'] = code

    def get_file(self, filename):
        """
        Finds a file with name matching filename within this case, its common_folder, or subfolders

        Assumes all files are parsed such that they will register as instances of OMFITascii

        :param filename: string

        :return: file reference or None
        """

        # Look for files in the top level
        top = [v for v in list(self.values()) if isinstance(v, OMFITascii) and os.path.split(v.filename)[1] == filename]
        if len(top) == 1:
            self.__printds__('Found file {} in top level.'.format(filename))
            return top[0]
        elif len(top) > 1:
            raise ValueError('Found more than one file named {} in the top level. This is bad!'.format(filename))

        # Look for files in the common_folder, if one is linked
        base = []
        if self.use_common_folder:
            if isinstance(self.use_common_folder, OMFITsolpsCase):
                common_folder = self.use_common_folder
            else:
                try:
                    parent = eval(treeLocation(self)[-2])
                except (IndexError, SyntaxError):
                    common_folder = {}
                else:
                    common_folder = parent[self.use_common_folder] if self.use_common_folder in parent else {}
            base = [v for v in list(common_folder.values()) if isinstance(v, OMFITascii) and os.path.split(v.filename)[1] == filename]
        else:
            self.__printds__('No common_folder is linked by self.use_common_folder; skipping file search in common.')
        if len(base) == 1:
            self.__printds__('Found file {} in common_folder.'.format(filename))
            return base[0]
        elif len(base) > 1:
            raise ValueError('Found more than one file named {} in the common_folder. This is bad!'.format(filename))

        # Now look in subfolders
        def looky(thing):
            x = [f for f in list(thing.values()) if isinstance(f, OMFITascii) and os.path.split(f.filename)[1] == filename]
            if len(x) == 1:
                return x[0]
            elif len(x) > 1:
                raise ValueError('Duplicate filename {} found in subfolder!'.format(filename))
            subs = [s for s in list(thing.values()) if isinstance(s, OMFITtree)]
            if len(subs):
                x = [looky(sub) for sub in subs]
                x = [xx for xx in x if xx is not None]
                if len(x) == 1:
                    return x[0]
                elif len(x) > 1:
                    warnings.warn('Duplicate filenames {} found in parallel subfolders. ' 'Picking one to return...'.format(filename))
                    return x[0]
                else:
                    return None
            else:
                return None

        sub_file = looky(self)
        if sub_file is not None:
            self.__printds__('Found {} in a sub-folder'.format(filename))
        else:
            self.__printds__('Could not find filename {}'.format(filename))
        return sub_file

    def __popup_menu__(self):
        return [['Activate case', self.run]]

    def __call__(self, **kw):
        return self.run(**kw)

    # End of class OMFITsolpsCase


############################################
if __name__ == '__main__':
    test_classes_main_header()

    import shutil
    import tempfile

    tmpd = tempfile.mkdtemp()
    shutil.copytree(OMFITsrc + '/../modules/SOLPS/TEMPLATES/AUG', tmpd + '/AUG')
    tmp_ = OMFITsolps(tmpd + '/AUG/b2ai.dat')
    print('==========')
    with open(tmp_.filename, 'r') as _f:
        print(_f.read())
    tmp_.load()
    tmp_.save()
    print('==========')
    with open(tmp_.filename, 'r') as _f:
        print(_f.read())
