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

from omfit_classes.utils_base import *
from omfit_classes.sortedDict import *

import numpy as np
import warnings
import uncertainties

comment_ptrn = re.compile(r'^__comment.*__$')


def _debug():
    try:
        return int(os.environ.get('OMFIT_DEBUG', '0'))
    except ValueError:
        return 0


def _split_arrays_function(name, value, offset=1, sparse_indexing=False):
    names = []
    values = []

    if isinstance(value, sparray):
        tmp = value.fortran_repr()
        for off, sub_value in zip(list(tmp.keys()), list(tmp.values())):
            if len(off):
                N, V = _split_arrays_function(name, sub_value, eval(off), sparse_indexing=True)
                names.extend(N)
                values.extend(V)
            else:
                names.append(name + '()')
                values.append(sub_value)
        return names, values

    for k, v in np.ndenumerate(value):
        k = np.atleast_1d(offset) * 0 + np.atleast_1d(k)
        if sparse_indexing and len(k) > 1:
            k[1:] *= 0
        k = tuple(k + offset)
        names.append('%s%s' % (name, re.sub(' ', '', re.sub(r',\)', ')', str(k)))))
        values.append([v])

    return names, values


def interpreter(orig, escaped_strings=True):
    """
    Parse string value in a fortran namelist format

    NOTE: for strings that are arrays of elements one may use the following notation:
    >> lines = '1 1.2 2.3 4.5 8*5.6'
    >> values = []
    >> for item in re.split('[ |\t]+', line.strip()):
    >>     values.extend(tolist(namelist.interpreter(item)))

    :param orig: string value element in a fortran namelist format

    :param escaped_strings: do strings follow proper escaping

    :return: parsed namelist element
    """

    # originally everything is in form of string but already split
    def eval_(a):
        try:
            return int(a)
        except Exception:
            try:
                return float(a)
            except Exception:
                return ast.literal_eval(a)

    out = orig
    if not isinstance(out, str):
        out = repr(orig)

    try:
        # fist try a number or a string that has been correctly escaped
        # remove fortran namelist escaping
        if escaped_strings:
            orig_ = re.sub(r'\\([!&$])', r'\1', orig)
            # fortran does not escape newlines
            if escaped_strings == 'fortran':
                orig_ = re.sub(r'\\', r'\\\\', orig_)
        else:
            orig_ = orig
        out = eval_(orig_)
        if isinstance(out, tuple):
            return complex(out[0], out[1])
    except Exception:
        try:
            if '+/-' in orig:
                out = uncertainties.ufloat_fromstr(orig)
            elif orig == 'nan':
                out = np.nan
            elif orig == 'inf':
                out = np.inf
            elif re.match(r'\- ?inf', orig):
                out = -np.inf
            else:
                raise
        except Exception:
            try:

                # then try a number saved with float format 0.d0
                tmp = re.sub(r'([0-9]+|[0-9]*(?:[0-9]\.|\.[0-9])[0-9]*)[dD]([\-\+]*[0-9]+)', r'\1e\2', orig)
                # also remove +'s
                tmp = re.sub(r'\+', '', tmp)
                out = eval_(tmp)
            except (SyntaxError, TypeError, ValueError):
                try:
                    # then check if it's one of those fortran repetition array
                    if re.match(r'([0-9]+)\*(.+)', tmp):
                        nrep = int(re.sub(r'([0-9]+)\*(.+)', r'\1', tmp))
                        val = re.sub(r'([0-9]+)\*(.+)', r'\2', tmp)
                        out = [eval_(val)] * nrep
                    else:
                        raise
                except Exception:
                    try:
                        # then try a boolean
                        tmp = re.sub(r'(?i)^\.true\.', '1', orig)
                        tmp = re.sub(r'(?i)^\.false\.', '0', tmp)
                        tmp = re.sub(r'(?i)^true', '1', tmp)
                        tmp = re.sub(r'(?i)^false', '0', tmp)
                        tmp = re.sub(r'(?i)^\.t', '1', tmp)
                        tmp = re.sub(r'(?i)^\.f', '0', tmp)
                        tmp = re.sub(r'(?i)^t', '1', tmp)
                        tmp = re.sub(r'(?i)^f', '0', tmp)
                        tmp = bool(eval_(tmp))
                        out = tmp
                    except (SyntaxError, TypeError, ValueError):
                        pass
    return out


def array_encoder(orig, line='', level=0, separator_arrays=' ', compress_arrays=True, max_array_chars=79, escaped_strings=True):
    all = line
    tmps = list([encoder(orig, escaped_strings) for orig in np.atleast_1d(orig)])

    # compress repeted entries
    if compress_arrays and len(tmps) > 0:
        tmpsc = []
        c = -1
        kold = tmps[0]
        for k in tmps + [tmps[-1] + ' ']:
            if kold == k:
                c += 1
            else:
                if c == 0:
                    tmpsc.append(kold)
                else:
                    tmpsc.append(str(c + 1) + '*' + kold)
                kold = k
                c = 0
        tmps = tmpsc

    # wrap entries so that they do not take more than max_array_chars per lines
    for k, tmp in enumerate(tmps):
        if k != (len(tmps) - 1):
            tmp = tmp + separator_arrays
        if not max_array_chars or len(line) + len(tmp) < max_array_chars:
            all += tmp
            line += tmp
        else:
            line = ' ' * level + tmp
            all += '\n' + line
    return all


def encoder(orig, escaped_strings=True, dotBoolean=True, compress_arrays=True, max_array_chars=79):
    if isinstance(orig, (bool, np.bool_)):
        if dotBoolean:
            tmp = '.' + str(orig).lower() + '.'
        else:
            tmp = str(orig)
    elif escaped_strings and isinstance(orig, str):
        tmp = repr(orig)
        tmp = re.sub('([!&$])', r'\\\1', tmp)
        if escaped_strings == 'fortran':
            tmp = re.sub(r'\\\\', r'\\', tmp)
    elif isinstance(orig, uncertainties.core.AffineScalarFunc):
        tmp = repr(orig)
    elif isinstance(orig, complex):
        tmp = repr((float(np.real(orig)), float(np.imag(orig))))
    elif isinstance(orig, tuple):
        tmp = array_encoder(
            np.array(list(orig)).flatten(),
            compress_arrays=compress_arrays,
            max_array_chars=max_array_chars,
            escaped_strings=escaped_strings,
        )
    elif isinstance(orig, list):
        tmp = array_encoder(
            np.array(orig).flatten(), compress_arrays=compress_arrays, max_array_chars=max_array_chars, escaped_strings=escaped_strings
        )
    elif isinstance(orig, np.ndarray):
        tmp = array_encoder(
            orig.flatten(), compress_arrays=compress_arrays, max_array_chars=max_array_chars, escaped_strings=escaped_strings
        )
    elif orig is None:
        tmp = ''
    elif orig == None:
        tmp = ''
    else:
        tmp = str(orig)
    return tmp


class NamelistName(SortedDict):
    """Defines variables defined within a &XXX and / delimiter in a FOTRAN namelist"""

    def __init__(self, *args, **kw):
        SortedDict.__init__(self, *args, **kw)
        self.caseInsensitive = True
        self._collect = False
        self.collect_arrays = False
        self.index_offset = kw.get('index_offset', False)

    def _checkSetitem(self, key, value):
        """
        Namelists can only handle strings as their dictionary keys
        This function will raise an exception during __setitem__ if that's not the case.
        """
        if not isinstance(key, str):
            raise Exception('Namelist only allows strings as dictionary keys')
        else:
            return key, value

    def collectArrays(self, _dimensions=None, **input_dimensions):
        """
        This function collects the multiple namelist arrays into a single one::

             collectArrays(**{'__default__':0,        # default value for whole namelist (use when no default is found)
                              'BCMOM':{               # options for specific entry in the namelist
                                  'default':3,        # a default value must be defined to perform math ops (automatically set by a=... )
                                  'shape':(30,30),    # this overrides automatic shape detection (automatically set by a(30,30)=...)
                                  'offset':(-10,-10), # this overrides automatic offset detection (automatically set to be the minimum of the offsets of the entries in all dimensions a(-10,-10)=...)
                                  'dtype':0}          # this overrides automatic type detection (automatically set to float if at least one float is found)
                              })
        """
        collect = SortedDict(caseInsensitive=True)
        defaults = SortedDict(caseInsensitive=True)
        offsets = SortedDict(caseInsensitive=True)
        dtypes = SortedDict(caseInsensitive=True)
        outputs = SortedDict(caseInsensitive=True)
        shapes = SortedDict(caseInsensitive=True)
        dimensions = SortedDict(caseInsensitive=True)

        dimensions.update(input_dimensions)
        if isinstance(_dimensions, dict):
            dimensions.update(_dimensions)
        if not isinstance(self.collect_arrays, dict):
            self.collect_arrays = SortedDict(caseInsensitive=True)
        self.collect_arrays.update(dimensions)

        dimensions.update(self.collect_arrays)

        # find the arrays to collect
        for kid in list(self.keys()):
            if isinstance(self[kid], NamelistName):
                self[kid].collect_arrays = self.collect_arrays
                self[kid].collectArrays(dimensions, **input_dimensions)
                continue
            if re.match(r'.*\(.*\)', kid) or kid in self.collect_arrays:
                if re.match(r'.*\(.*\)', kid):
                    var = re.sub(r'(.*)\((.*)\)', r'\1', kid)
                else:
                    var = kid
                # add to list of items to append
                collect.setdefault(var, [])

        # expand ranges
        for kid in list(self.keys()):
            mat = re.match(r'(.*)\((.*)\)', kid)
            if not mat:
                continue
            if self[kid] is None:
                printw('Assigning 0 length array to finite range: %s' % kid)
                continue
            sk = mat.groups()
            if len(sk) < 2:
                continue
            var, ind = sk
            if ':' not in ind:
                continue
            rnk_ranges = []
            ranks = ind.split(',')
            for ri, rank in enumerate(ranks):
                if ':' not in rank:
                    continue
                rnk_ranges.append(ri)
            if len(rnk_ranges) > 1:
                raise NotImplementedError(f'{kid}: must only give one dimension with a range')
            rng_ri = rnk_ranges[0]
            new_key = '{var}({prefix}{rg_ind}{postfix})'
            prefix = ','.join(ranks[:rng_ri])
            if rng_ri > 0:
                prefix = prefix + ','
            postfix = ''
            if rng_ri != len(ranks) - 1:
                postfix = postfix + ','
            postfix = postfix + ','.join(ranks[rng_ri + 1 :])

            rngs = list(map(int, ranks[rng_ri].split(':')))
            rngs[1] = rngs[1] + 1
            if len(list(range(*rngs))) != len(self[kid]):
                raise ValueError('Length of range and values disagree for %s: %s; %s' % (kid, ranks[rng_ri], self[kid]))
            for ri, rang in enumerate(range(*rngs)):
                self[new_key.format(prefix=prefix, var=var, rg_ind=rang, postfix=postfix)] = self[kid][ri]
            del self[kid]

        # find the arrays to collect
        warn_msg = []
        for kid in list(self.keys()):
            if (
                re.sub(r'(.*)\((.*)\)', r'\1', kid) in collect
                or kid in self.collect_arrays
                and self.collect_arrays[kid].get('sparray', True)
            ):
                if re.match(r'.*\(.*\)', kid):
                    try:
                        var = re.sub(r'(.*)\((.*)\)', r'\1', kid)
                        indexStr = re.sub(r'(.*)\((.*)\)', r'\2', kid)
                        index = np.array(list(map(int, indexStr.split(','))))
                    except ValueError:
                        continue
                else:
                    var = kid
                    indexStr = None
                    index = (1,)

                # types
                if var in dimensions and 'dtype' in dimensions[var]:
                    tmp = dimensions[var]['dtype']
                    if callable(tmp):
                        tmp = tmp(0)
                    dtypes[var] = tmp
                elif np.atleast_1d(self[kid]).dtype.kind.lower() in ['s', 'u']:
                    dtypes[var] = ''  # string
                elif np.atleast_1d(self[kid]).dtype.kind.lower() in ['f']:
                    dtypes[var] = 0.0  # float
                elif np.atleast_1d(self[kid]).dtype.kind.lower() in ['b']:
                    dtypes[var] = False  # boolean
                elif var not in dtypes:
                    dtypes[var] = 0  # int

                # offsets
                if var not in offsets:
                    offsets[var] = index
                off = np.ones(np.shape(index))
                off[: len(offsets[var])] = offsets[var]
                offsets[var] = np.min([off, index], 0)
                offsets[var] = tuple(map(int, offsets[var].tolist()))

                # add to list of items to append
                collect[var].append(indexStr)

        # user defined shapes
        for var in list(collect.keys()):
            if var in dimensions and 'shape' in dimensions[var]:
                shapes[var] = tuple(dimensions[var]['shape'])
            else:
                shapes[var] = None

        # if there is something to collect
        if len(collect):
            # if there was a default as array update the offsets to be at maximum 1
            for var in list(collect.keys()):
                for k, indexStr in enumerate(collect[var]):
                    if indexStr is None:
                        if len(collect[var]) > 1 or offsets[var] != 0:
                            offsets[var] = np.min([offsets[var], np.ones(np.shape(offsets[var]))], 0)
                            offsets[var] = tuple(map(int, offsets[var].tolist()))
                        else:
                            del collect[var]
                            del offsets[var]
                            continue

            # user defined offsets
            for var in list(offsets.keys()):
                if var in dimensions and 'offset' in dimensions[var]:
                    offsets[var] = tuple(dimensions[var]['offset'])
                elif '__offset__' in dimensions:
                    offsets[var] = tuple([dimensions['__offset__']] * len(offsets[var]))
                else:
                    # equal offsets for all dimensions (reasonable?)
                    offsets[var] = tuple([min(offsets[var])] * len(offsets[var]))

            # defaults
            for var in list(offsets.keys()):
                if isinstance(dtypes[var], str):
                    defaults[var] = dimensions.get('__default__', '')
                else:
                    defaults[var] = dimensions.get('__default__', np.nan)
            for var in list(offsets.keys()):
                if var in dimensions and 'default' in dimensions[var]:
                    defaults[var] = dimensions[var]['default']

            # define sparse arrays
            for var in list(offsets.keys()):

                # handle arrays of strings
                if isinstance(dtypes[var], str):
                    # for the time being only handle var(1)=['a','b','c'] type string arrays
                    if len(offsets[var]) > 1:
                        continue

                    # figure out the shape
                    if shapes[var] is None:
                        shapes[var] = 0
                        for indexStr in collect[var]:
                            if indexStr is None:
                                defaults[var] = self[var]
                                continue
                            kid = '%s(%s)' % (var, indexStr)
                            shapes[var] = max([shapes[var], int(indexStr) + len(tolist(self[kid])) - 1])
                        shapes[var] = (shapes[var],)

                    # generate array
                    outputs[var] = [defaults[var]] * shapes[var][0]
                    for indexStr in collect[var]:
                        if indexStr is None:
                            continue
                        kid = '%s(%s)' % (var, indexStr)
                        for k, value in enumerate(tolist(self[kid])):
                            outputs[var][int(indexStr) - offsets[var][0] + k] = value

                # handle numerical arrays
                else:
                    outputs[var] = sparray(shapes[var], offset=offsets[var], default=defaults[var], dtype=dtypes[var], index_offset=True)
                    for indexStr in collect[var]:
                        if indexStr is None:
                            kid = var
                            indexStr = ','.join(list(map(str, offsets[var])))
                        else:
                            kid = '%s(%s)' % (var, indexStr)
                        outputs[var].fortran(indexStr, self[kid])
                    outputs[var].index_offset = self.index_offset
                    # keep it sparse if requested by user
                    if var in self.collect_arrays and self.collect_arrays[var].get('sparray', True):
                        pass

                    # dense if 1D or 2D and offsets start at 1
                    elif (outputs[var].ndim == 1 and np.atleast_1d(outputs[var].offset)[0] == 1) or (
                        outputs[var].ndim == 2 and np.atleast_1d(outputs[var].offset)[0] == 1 and np.atleast_1d(outputs[var].offset)[1] == 1
                    ):
                        tmp = outputs[var].dense()
                        if not np.any(outputs[var].isnan(tmp)):
                            outputs[var] = tmp

        # substitute collected values
        for var in outputs:
            i = -1
            for k, kid in enumerate(self.keys()):
                if kid.lower().startswith(var.lower() + '('):
                    del self[kid]
                    i = k

            self.insert(i, var, outputs[var])

        self._collect = True

    def collect(self, value):
        self._collect = value
        for kid in list(self.keys()):
            if isinstance(self[kid], NamelistName):
                self[kid].collect(value)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, NamelistName):
            tmp = NamelistName(index_offset=self.index_offset)
            tmp.update(value)
            value = tmp
        return super().__setitem__(key, value)

    def __getitem__(self, key):
        key = self._keyCaseInsensitive(key)

        # handle internal key indexing
        if key not in list(self.keys()) and re.match(r'.*\(.*\)', key):
            index = np.array(list(map(int, re.sub(r'(.*)\((.*)\)', r'\2', key).split(','))))
            key = re.sub(r'(.*)\((.*)\)', r'\1', key)
        else:
            index = None

        try:
            tmp = super().__getitem__(key)
        except KeyError:
            raise

        # return (indexed) object
        if index is None or not len(np.shape(tmp)):
            return tmp
        else:
            offset = -1
            while index[-1] == 1 and len(index) > len(np.atleast_1d(tmp).shape):
                index = index[:-1]
            index += offset
            return tmp[tuple(index)]

    def __setstate__(self, tmp):
        self.__dict__.update(tmp[0])
        if hasattr(self, '_collect'):
            _collectBCKP = self._collect
            self.collect(False)
        for key, value in zip(self.keyOrder, tmp[1]):
            self[key] = self._setLocation(key, value)
        if hasattr(self, '_collect'):
            self.collect(_collectBCKP)

    def __deepcopy__(self, memo={}):
        if hasattr(self, '_collect'):
            _collectBCKP = self._collect
        else:
            _collectBCKP = False
        self.collect(False)
        tmp = pickle.loads(pickle.dumps(self, pickle.HIGHEST_PROTOCOL))
        tmp.collect(_collectBCKP)
        self.collect(_collectBCKP)
        return tmp


class NamelistFile(NamelistName):
    """
    FORTRAN namelist file object, which can contain multiple namelists blocks

    :param filename: filename to be parsed

    :param input_string: input string to be parsed (preceeds filename)

    :param nospaceIsComment: whether a line which starts without a space should be retained as a comment. If None, a "smart" guess is attempted

    :param outsideOfNamelistIsComment: whether the content outside of the namelist blocks should be retained as comments. If None, a "smart" guess is attempted

    :param retain_comments: whether comments should be retained or discarded

    :param skip_to_symbol: string to jump to for the parsing. Content before this string is ignored

    :param collect_arrays: whether arrays defined throughout the namelist should be collected into single entries
     (e.g. a=5,a(1,4)=0)

    :param multiDepth: wether nested namelists are allowed

    :param bang_comment_symbol: string containing the characters that should be interpreted as comment delimiters.

    :param equals: how the equal sign should be written when saving the namelist

    :param compress_arrays: compress repeated elements in an array by using v*n namelist syntax

    :param max_array_chars: wrap long array lines

    :param explicit_arrays: (True,False,1) whether to place `name(1)` in front of arrays.
                            If `1` then (1) is only placed in front of arrays that have only one value.

    :param separator_arrays: characters to use between array elements

    :param split_arrays: write each array element explicitly on a separate line
                         Specifically this functionality was introduced to split TRANSP arrays

    :param idlInput: whether to interpret the namelist as IDL code
    """

    def __init__(
        self,
        filename=None,
        input_string='',
        nospaceIsComment=None,
        outsideOfNamelistIsComment=None,
        retain_comments=True,
        skip_to_symbol=None,
        collect_arrays=True,
        multiDepth=True,
        bang_comment_symbol='!;',
        equals=' = ',
        compress_arrays=True,
        max_array_chars=79,
        explicit_arrays=False,
        separator_arrays=' ',
        split_arrays=False,
        idlInput=False,
        end_token='/',
        index_offset=False,
        **kw,
    ):

        NamelistName.__init__(self, index_offset=index_offset)

        self.filename = filename
        self.retain_comments = retain_comments
        self.nospaceIsComment = nospaceIsComment
        self.outsideOfNamelistIsComment = outsideOfNamelistIsComment
        self.skip_to_symbol = skip_to_symbol
        self.collect_arrays = collect_arrays
        self.multiDepth = multiDepth
        self.idlInput = bool(idlInput)
        self.bang_comment_symbol = bang_comment_symbol
        self._equals = equals
        self.compress_arrays = compress_arrays
        self.max_array_chars = max_array_chars
        self.explicit_arrays = explicit_arrays
        self.separator_arrays = separator_arrays
        self.split_arrays = split_arrays
        self.end_token = end_token

        if idlInput:
            self.bang_comment_symbol = ';'
            self.nospaceIsComment = False
            self.outsideOfNamelistIsComment = False
            self.compress_arrays = False
            self.max_array_chars = None
            self.separator_arrays = ','

        self.dynaLoad = False
        if input_string != '':
            if self.filename is not None:
                with open(self.filename, 'w') as f:
                    f.write(input_string)
            else:
                self.parse(input_string.splitlines(True))
        if self.filename is not None:
            self.dynaLoad = True

    def parse(self, content):
        self.clear()
        if not len(content):
            return

        if _debug():
            start = time.time()

        # ignore cvs version line by adding a bang comment
        for k, line in enumerate(content):
            if '$Id' in line:
                content[k] = re.sub(r'.*\$Id([^$]*?)\$', self.bang_comment_symbol[0] + r' $Id\1$', line)

        # nospace should be interpreted as a comment if I do not find any line which starts by a letter and has a variable assignment
        if self.nospaceIsComment is None:
            self.nospaceIsComment = True
            for line in content:
                line = line.strip('\n')
                for k in self.bang_comment_symbol:  # skip commented lines
                    line = line.split(k)[0]
                line = line.rstrip()
                if not len(line):  # Skip lines without length
                    continue
                elif re.search(r'^\s', line):  # Skip lines with leading space
                    continue
                elif re.search(r'(?i)^[&$][_a-z0-9]', line):  # Begin/end of namelist on first char
                    self.nospaceIsComment = False
                elif re.search(r'^[&/$]', line):  # End of namelist on first char
                    self.nospaceIsComment = False
                elif re.search(r'(?i)^[_a-z0-9]\w*\s*=\s*[-\'\"\.]?\w*', line):  # Variable assignment on first char
                    self.nospaceIsComment = False
                    # Variable assignment on first char
                elif re.search(r'(?i)^[_a-z0-9](\([,0-9]\))*\w*\s*=\s*[-\'\"\.]?\w*', line):
                    self.nospaceIsComment = False

        # see if there are variable assignements outside of namelist
        if self.outsideOfNamelistIsComment is None:
            self.outsideOfNamelistIsComment = True
            inside = False
            for line in content:
                line = line.strip('\n')
                for k in self.bang_comment_symbol:  # skip commented lines
                    line = line.split(k)[0]
                line = line.rstrip()
                if not len(line):  # skip lines without length
                    continue
                elif re.search('(?i)^[_a-z0-9]', line) and self.nospaceIsComment:  # Skip if it's a line commment
                    continue
                elif re.search(r'(?i)^\s*[&$][_a-z0-9]', line):  # Begin of namelist --> inside=True
                    inside = True
                elif re.search(r"(?i)^\s*[&/$]", line):  # End of namelist --> inside=False
                    inside = False
                elif not inside:
                    tmp1 = re.findall(r'(?i)^[_a-z0-9](\([,0-9]\))*\w*\s*=\s*[-\'\"\.]?\w*', line)
                    if len(tmp1) == 1:  # Only one variable per line
                        tmp2 = re.findall(r'(?i)^[_a-z0-9](\([,0-9]\))*\w*\s*=\s*[-\'\"\.]?\w*', line)
                        if len(tmp2) and tmp2[0] == tmp1[0]:  # There is no text before the first variable
                            self.outsideOfNamelistIsComment = False

        if _debug():
            for k in ['nospaceIsComment', 'outsideOfNamelistIsComment']:
                print(k, getattr(self, k))
            print('read in ' + format(time.time() - start, '3.3f') + ' sec.')

        rules = {}
        rules['single'] = 0
        rules['double'] = 0
        rules['round_bracket'] = 0
        rules['bang_comment'] = 0
        rules['line_comment'] = 0
        if self.skip_to_symbol is None:
            tmpj = ''.join(content)
        else:
            for si, s in enumerate(content):
                if self.skip_to_symbol in s:
                    break
            if si == len(content):
                si = 0
            tmpj = ''.join(content[si:])
        item_offset = 0
        item_length = 0
        item_prepend = ''
        tmp = []

        if self.idlInput:
            # in IDL language `&` is like a new line
            # here it's safer to convert to a space
            tmpj = re.sub('&', ' ', tmpj)

        inside = 0
        tmpj = re.sub(r"(?i)[&/$]end(_\S*)?", "$", tmpj).rstrip() + '\n' * 3

        kk = 0
        for cm, c, cp in zip(*['\n' + tmpj, tmpj, tmpj[1:] + '\n']):
            kk += 1
            if _debug() > 1:
                print(cm, c, cp, tmp)

            if cm == '\\':
                # if it's an escaped character, then it's nothing special, by definition
                item_length += 1
                continue

            if c == '\n':
                # if it's a new line, then it's a new record and all rules should be reset
                for key in list(rules.keys()):
                    rules[key] = 0

            # handle comments outside of namelist
            if self.outsideOfNamelistIsComment:

                # bang comments should always be considered comments
                if c in self.bang_comment_symbol:
                    rules['bang_comment'] = 1

                # when namelist block starts or the file ends, assign all to be comment
                if not rules['bang_comment'] and re.match(r'(?i)[$&][_a-z0-9]', c + cp) or kk == len(tmpj):
                    if not inside:
                        item_ = tmpj[item_offset : item_offset + item_length]
                        item_ = re.sub('[\n \t]', '', item_)
                        if len(item_):  # do not store empty blocks
                            if not len(tmp):
                                item = u'\1' + tmpj[item_offset : item_offset + item_length].rstrip(' \t')[:-1]
                            else:
                                item = u'\1' + tmpj[item_offset : item_offset + item_length].strip(' \t')[1:-1]
                            item_offset += item_length
                            item_length = 0
                            item_prepend = ''
                            tmp.append(item)

                # check if a namelist block is starting
                if not rules['bang_comment'] and re.match(r'(?i)[$&][_a-z0-9]', c + cp):
                    inside += 1
                    if _debug() > 1:
                        print('namelist block starts')

            # if inside of a namelist block or if variables outside namelist blocks are not comments
            if inside or not self.outsideOfNamelistIsComment:

                # this is a new item
                if (c in ' \t,=' and not np.any([rules[key] for key in list(rules.keys())])) or c == '\n':
                    if item_length > 0:
                        item = item_prepend + tmpj[item_offset : item_offset + item_length]
                        item_offset += item_length
                        item_length = 0
                        item_prepend = ''
                        if len(item.strip('\n \t,=')):
                            tmp.append(item.strip('\n \t,='))
                        if c == '=':
                            tmp.append(c)

                # this is the continuation of the current item
                else:
                    if c == '(' and not np.any([rules[key] for key in list(rules.keys()) if key != 'round_bracket']):
                        rules['round_bracket'] += 1
                    elif c == ')' and not np.any([rules[key] for key in list(rules.keys()) if key != 'round_bracket']):
                        rules['round_bracket'] -= 1
                    elif c == "'" and not np.any([rules[key] for key in list(rules.keys()) if key != 'single']):
                        rules['single'] = (rules['single'] + 1) % 2
                    elif c == '"' and not np.any([rules[key] for key in list(rules.keys()) if key != 'double']):
                        rules['double'] = (rules['double'] + 1) % 2
                    elif (c in self.bang_comment_symbol) and not np.any(
                        [rules[key] for key in list(rules.keys()) if key != 'bang_comment']
                    ):
                        rules['bang_comment'] = 1
                    elif (
                        (self.nospaceIsComment and not self.outsideOfNamelistIsComment)
                        and (cm == '\n' and c not in ' \t')
                        and not np.any([rules[key] for key in list(rules.keys()) if key != 'line_comment'])
                    ):
                        rules['line_comment'] = 1
                        item_prepend = u'\1'

                # when namelist block ends
                if self.outsideOfNamelistIsComment:
                    if inside and not np.any([rules[key] for key in list(rules.keys())]) and ((cm == '/' and c == '\n')):
                        inside -= 1
                        # if namelist block ends and last item had / then
                        # reasonable to assume that / was the termination
                        if inside == 0 and len(tmp[-1]) > 1 and tmp[-1][-1] == '/':
                            tmp[-1] = tmp[-1][:-1]
                        if _debug() > 1:
                            print('namelist block ends')

            item_length = item_length + 1

        if _debug():
            print('b in ' + format(time.time() - start, '3.3f') + ' sec.')
        tmp = [re.sub(r"(?i)[&/$]end", "/", line) for line in tmp]
        if _debug() > 1:
            print(tmp)

        def uniqueSortedComment(itm, tree):
            out = '__comment' + omfit_hash(str(itm), 10) + '__'
            while out in tree:
                out = '__comment' + omfit_hash(str(out), 10) + '__'
            return out

        # build the namelist tree
        tree = self
        vlist = None
        for k, item in enumerate(tmp):
            if re.match(r'^[&$].+', item):
                if not self.multiDepth and '__parent__' in tree:
                    tmptree = tree['__parent__']
                    del tree['__parent__']
                    tree = tmptree
                    vlist = None
                # is it a namelist header
                nlist = re.sub(r'^[&$](.*)', r'\1', item)
                if nlist not in tree:
                    tree[nlist] = NamelistName(index_offset=self.index_offset)
                tree[nlist]['__parent__'] = tree
                tree = tree[nlist]
            elif item[0] == u'\1':
                # it's a line comment
                if self.retain_comments:
                    tree[uniqueSortedComment(item[1:], tree)] = item[1:] + '\n'
            elif item[0] in self.bang_comment_symbol:
                # it's a bang comment
                if self.retain_comments:
                    tree[uniqueSortedComment(item, tree)] = item + '\n'
            elif item in ['/', '$', '&']:
                # is it a namelist close
                try:
                    tmptree = tree['__parent__']
                    del tree['__parent__']
                    tree = tmptree
                    vlist = None
                except Exception:
                    if self.multiDepth:
                        warnings.warn('Some problem with namelist closure near: +\n\n' + ' '.join(tmp[k - 100 : k]))
            elif k != len(tmp) - 1 and tmp[k + 1] == '=':
                # If the next item is an equal sign, this means that it's a variable name
                tmp[k] = item = re.sub(' ', '', item)  # variable names in namelists cannot have spaces
                tree[item] = []
                vlist = tree[item]
            elif item == '=':
                pass
            else:
                if not (vlist is None):
                    if '*' in item and re.match(r'([0-9]+)\*(.+)', item):
                        nrep = int(re.sub(r'([0-9]+)\*(.+)', r'\1', item))
                        val = re.sub(r'([0-9]+)\*(.+)', r'\2', item)
                        vlist.extend([val] * nrep)
                    elif self.idlInput:
                        vlist.append(item.strip('[]'))
                    else:
                        vlist.append(item)
        if _debug():
            print('c in ' + format(time.time() - start, '3.3f') + ' sec.')

        if not self.multiDepth:
            fun_str = lambda orig: interpreter(orig, escaped_strings='fortran')
        else:
            fun_str = lambda orig: interpreter(orig, escaped_strings=True)

        # now interpret the list of stings
        def i_traverse(me):
            if '__parent__' in list(me.keys()):
                del me['__parent__']
            for kid in list(me.keys()):
                if isinstance(me[kid], dict):
                    i_traverse(me[kid])
                elif not re.match(comment_ptrn, kid):
                    fun = fun_str
                    if len(me[kid]) > 1:
                        item0 = copy.deepcopy(me[kid][0])
                        try:
                            int(item0)
                            fun = int
                        except Exception:
                            try:
                                float(item0)
                                fun = float
                            except Exception:
                                pass
                    try:
                        me[kid] = list(map(fun, me[kid]))
                    except Exception:
                        me[kid] = list(map(fun_str, me[kid]))
                    if isinstance(me[kid], str):
                        pass
                    elif len(me[kid]) > 1:
                        me[kid] = np.array(me[kid])
                    elif len(me[kid]) == 1:
                        me[kid] = me[kid][0]
                    else:
                        me[kid] = None

        i_traverse(self)
        if _debug():
            print('d in ' + format(time.time() - start, '3.3f') + ' sec.')

        # collect arrays
        if self.collect_arrays:
            try:
                self.collectArrays(self.collect_arrays)
            except Exception as _excp:
                printw('Could not collect arrays: ' + repr(_excp))

        if _debug():
            print('end of loading namelist')
            print('Parsing namelist in ' + format(time.time() - start, '3.3f') + ' sec.')

    def saveas(self, filename):
        """save namelist to a new file"""
        self.filename = os.path.abspath(filename)
        directory = os.path.split(os.path.abspath(filename))[0]
        if os.path.exists(directory) == 0:
            os.makedirs(directory)
        self.save()

    @dynaSave
    def save(self, fp=None):
        if self.filename == None and fp == None:
            return
        # this whole pointer trickery is to allow saving of namelists in EFIT g-file
        if fp is not None:
            f = fp
        else:
            f = open(self.filename, 'w+')

        def f_traverse(me, level):
            for kid in list(me.keys()):
                if _debug():
                    print('Writing ', kid)
                if isinstance_str(me[kid], ['OMFITexpression', 'OMFITiterableExpression']):
                    meKid = me[kid]._value_()
                else:
                    meKid = me[kid]

                if isinstance(meKid, dict):
                    level += 1
                    f.writelines(' ' * level + '&' + kid + '\n')
                    f_traverse(meKid, level)
                    f.writelines(' ' * level + self.end_token + '\n')
                    level -= 1
                elif re.match(comment_ptrn, kid):
                    f.writelines(meKid.rstrip() + '\n')
                else:
                    # if it is an array
                    if (
                        isinstance(meKid, np.ndarray)
                        or isinstance(meKid, sparray)
                        or isinstance(meKid, list)
                        or re.search(r'^\[(([ \n]*[0-9\-+.ji]+)*)\]$', str(meKid))
                    ):
                        # handle split_arrays functionality by looping over individual segments
                        if not self.split_arrays:
                            kid0, meKid0 = (
                                [kid],
                                [meKid],
                            )
                        elif callable(
                            self.split_arrays
                        ):  # this cannot be saved, but it is useful for development of the _split_arrays_function
                            kid0, meKid0 = self.split_arrays(kid, meKid)
                        else:
                            kid0, meKid0 = _split_arrays_function(kid, meKid)
                        for kid, meKid in zip(kid0, meKid0):
                            if isinstance(meKid, sparray):
                                tmp = meKid.fortran_repr()
                                for item, value in zip(list(tmp.keys()), list(tmp.values())):
                                    line = ' ' * level + kid + item + self._equals
                                    if self.idlInput:
                                        line += '['
                                    tmp = array_encoder(
                                        value,
                                        line,
                                        level,
                                        separator_arrays=self.separator_arrays,
                                        compress_arrays=self.compress_arrays,
                                        max_array_chars=self.max_array_chars,
                                        escaped_strings=['fortran', True][self.multiDepth],
                                    )
                                    if self.idlInput:
                                        tmp += ']'
                                    f.writelines(tmp.rstrip() + '\n')
                            elif isinstance(meKid, np.ndarray) and len(meKid.shape) > 1:
                                kidShape = list(meKid.shape)
                                kidShape[0] = 1
                                i = 0
                                fi = lambda i=i: '0:' + str(i)
                                ndim = np.reshape(eval("np.mgrid[" + ','.join([fi(i) for i in kidShape]) + "]"), (len(kidShape), -1))
                                tmpData = np.reshape(meKid, (meKid.shape[0], -1))
                                for kk, k in enumerate(range(len(ndim[0]))):
                                    line = ' ' * level + kid + '(' + ','.join([str(i + 1) for i in ndim[:, k]]) + ')' + self._equals
                                    if self.idlInput:
                                        line += '['
                                    tmp = array_encoder(
                                        tmpData[:, kk],
                                        line,
                                        level,
                                        separator_arrays=self.separator_arrays,
                                        compress_arrays=self.compress_arrays,
                                        max_array_chars=self.max_array_chars,
                                        escaped_strings=['fortran', True][self.multiDepth],
                                    )
                                    if self.idlInput:
                                        tmp += ']'
                                    f.writelines(tmp.rstrip() + '\n')
                            else:
                                if re.match(r'.*\(\)', kid):
                                    kid = kid[:-2]
                                elif self.explicit_arrays is 1 and len(meKid) == 1 and not re.match(r'.*\(.*\)', kid):
                                    kid = kid + '(1)'
                                elif self.explicit_arrays is True and not re.match(r'.*\(.*\)', kid):
                                    kid = kid + '(1)'
                                line = ' ' * level + kid + self._equals
                                if self.idlInput:
                                    line += '['
                                tmp = array_encoder(
                                    meKid,
                                    line,
                                    level,
                                    separator_arrays=self.separator_arrays,
                                    compress_arrays=self.compress_arrays,
                                    max_array_chars=self.max_array_chars,
                                    escaped_strings=['fortran', True][self.multiDepth],
                                )
                                if self.idlInput:
                                    tmp += ']'
                                f.writelines(tmp.rstrip() + '\n')
                    else:
                        f.writelines(
                            (' ' * level + kid + self._equals + encoder(meKid, escaped_strings=['fortran', True][self.multiDepth])).rstrip()
                            + '\n'
                        )

        f_traverse(self, 0)
        if fp is None:
            f.close()

    @dynaLoad
    def load(self, filename=''):
        """Load namelist from file."""
        self.clear()
        self.dynaLoad = False
        if filename != '':
            self.filename = filename
        with open(self.filename, 'r') as f:
            self.parse(f.readlines())
        return self


class fortran_environment(object):
    """
    Environment class used to allow FORTRAN index convention of sparrays in a namelist
    """

    def __init__(self, nml):
        self.nml = nml
        self.sp = traverse(self.nml, onlyLeaf=(sparray,))

    def __enter__(self):
        self.index_offset_bkp = {}
        for item in self.sp:
            self.index_offset_bkp[item] = getattr(eval("self.nml" + item), 'index_offset', 0)
            eval("self.nml" + item).index_offset = True

    def __exit__(self, type, value, traceback):
        for item in self.sp:
            eval("self.nml" + item).index_offset = self.index_offset_bkp[item]


class sparray(object):
    """
    Class for n-dimensional sparse array objects using Python's dictionary structure.
    based upon: http://www.janeriksolem.net/2010/02/sparray-sparse-n-dimensional-arrays-in.html
    """

    def __init__(self, shape=None, default=np.nan, dtype=None, wrap_dim=0, offset=0, index_offset=False):
        if dtype is None:
            self.dtype = None
        elif callable(dtype):
            self.dtype = dtype = np.array(dtype(0)).dtype
        else:
            self.dtype = dtype = np.array(dtype).dtype
        self.default = np.array(default)
        if self.dtype is not None:
            self.default = np.array(default).astype(dtype)
        elif dtype is None:
            self.dtype = dtype = self.default.dtype
        if shape is None:
            self.shape = ()
        else:
            self.shape = tuple(shape)
        self.ndim = len(self.shape)
        self.wrap_dim = wrap_dim
        self.__data = self.data = OrderedDict()
        self.offset = np.atleast_1d(offset)
        self.index_offset = index_offset

    def _index_offset(self, index, mult=-1):
        if not self.index_offset:
            return index
        index = np.atleast_1d(index)
        _index = []
        offset = np.zeros(index.shape) + self.offset
        for i, o in zip(index, offset):
            if isinstance(i, slice):
                start, stop, step = i.start, i.stop, i.step
                if start is not None:
                    start = int(start + o * mult)
                if stop is not None:
                    stop = int(stop + o * mult)
                _index.append(slice(start, stop, step))
            else:
                _index.append(int(i + o * mult))
        return tuple(_index)

    def _setitem_base(self, index, value):
        """set value to position given in index, where index is a tuple."""
        # adjust number of dimensions
        index = tuple(map(int, index))
        if len(index) > len(self.shape):
            tmp = list(np.array(index) + 1)
            tmp[: len(self.shape)] = self.shape
            self.shape = tuple(tmp)
        # adjust dimensions
        for k, dim in enumerate(np.array(index) + 1):
            if dim > self.shape[k]:
                tmp = list(self.shape)
                tmp[k] = dim
                self.shape = tuple(tmp)
        self.ndim = len(self.shape)
        if self.dtype is None:
            self.dtype = np.array(value).dtype
            self.default = np.array(self.default).astype(self.dtype)
        self.__data[index] = np.atleast_1d([value]).astype(self.dtype)

    def __setitem__(self, index, value):
        """set value to position given in index, where index is a tuple."""
        index = self._index_offset(index, -1)
        if isinstance(value, np.ndarray):
            _index = list(index)
            for k in range(len(value)):
                self._setitem_base(tuple(_index), value[k])
                _index[self.wrap_dim] += 1
        else:
            self._setitem_base(index, value)

    def __getitem__(self, index):
        """get value at position given in index, where index is a tuple."""
        index = self._index_offset(index, -1)
        try:
            return self.dense()[index]
        except IndexError:
            return index * 0 + self.default

    def __delitem__(self, index):
        """index is tuples of element to be deleted."""
        index = self._index_offset(index)
        if index in self.__data:
            del self.__data[index]

    def __binary_op__(self, other, op):
        if isinstance(other, sparray):
            if self.shape == other.shape:
                tmp = copy.deepcopy(self)
                for k in set.difference(set(tmp.__data.keys()), set(other.__data.keys())):
                    tmp.__data[k] = eval('tmp.__data[k].' + op + '(other.default)')
                tmp.default = eval('tmp.default.' + op + '(other.default)')
                for k in list(other.__data.keys()):
                    old_val = tmp.__data.setdefault(k, tmp.default)
                    tmp.__data[k] = eval('old_val.' + op + '(other.__data[k])')
                return tmp
            else:
                raise ValueError('Array sizes do not match. ' + str(self.shape) + ' versus ' + str(other.shape))
        else:
            return eval('self.dense().' + op + '(other)')

    def __unary_op__(self, op):
        tmp = copy.deepcopy(self)
        for k in tmp.__data.keys():
            tmp.__data[k] = eval('tmp.__data[k].' + op + '()')
        tmp.default = eval('tmp.default.' + op + '()')
        return tmp

    def __str__(self):
        return str(self.dense())

    def dense(self):
        """Convert to dense NumPy array"""
        out = (self.default * np.ones(self.shape)).astype(self.dtype)
        for ind in self.__data:
            out[ind] = self.__data[ind].astype(self.dtype)
        return out

    def sum(self):
        """Sum of elements"""
        s = self.default * np.array(self.shape).prod()
        for ind in self.__data:
            s += self.__data[ind] - self.default
        return s

    def fortran(self, index, value):
        # Drop leading zeros otherwise the index is evaluated as an octal.
        index = _delete_leading_zeros(index)
        index = eval('(' + re.sub('([0-9]+):', r'\1', index.split('(')[-1].strip(')')) + ')')
        self.__setitem__(index, value)
        return self

    def isnan(self, x):
        if np.iterable(x):
            x = np.array(x)
            i = np.where(x == -9223372036854775808)
            x = x.astype(float)
            x[i] = np.nan
            return np.isnan(np.array(x))
        elif np.isnan(x):
            return True
        elif x == np.array(np.nan).astype(np.array(x).dtype):
            return x == np.array(np.nan).astype(np.array(x).dtype)

    def fortran_repr(self):
        # print strips
        strips = OrderedDict()
        for item in list(self.__data.keys()):
            item = tuple(item)
            strips.setdefault(item[1:], item)
            strips[item[1:]] = tuple(map(int, np.min([strips[item[1:]], item], 0)))

        # prints
        outputs = OrderedDict()
        if not self.isnan(self.default):
            outputs[''] = self.default

        for item in list(strips.values()):
            tmp = list(item)
            tmp[0] = slice(None)
            tmp = tuple(tmp)

            # do not use self[tmp] to avoid self._index_offset
            dense_tmp = self.dense()[tmp]

            if self.isnan(self.default):
                ix_ = np.where(self.isnan(dense_tmp))[0]
            else:
                ix_ = np.where(dense_tmp == self.default)[0]

            # split where default value is found
            substrips_ = np.split(dense_tmp, ix_)
            substrips = []
            ix = []
            ix_ = [0] + list(ix_)
            for ki, ks in zip(ix_, substrips_):
                if len(ks) > 1:
                    ix.append(ki)
                    ix.append(ki + 1)
                    substrips.append(ks[:1])
                    substrips.append(ks[1:])
                elif len(ks):
                    ix.append(ki)
                    substrips.append(ks)

            # print substrips
            # note: values that are equal to the default value or that are NaN will not be printed
            item = item + self.offset
            for k, v in enumerate(substrips):
                if not len(v):
                    continue
                elif self.isnan(v[0]):
                    continue
                elif v[0] == self.default:
                    continue
                item[0] = ix[k] + self.offset[0]
                if len(item) == 1:
                    outputs['(%d)' % item.astype(int)] = v.astype(self.dtype)
                else:
                    outputs[str(re.sub(' ', '', repr(tuple(item.astype(int)))))] = v.astype(self.dtype)

        return outputs

    def __str__(self):
        tmp = self.fortran_repr()
        out = []
        for item, value in zip(list(tmp.keys()), list(tmp.values())):
            out.append('%s: %s' % (str(item)[1:-1], str(value)))
        return '\n'.join(out)

    def __repr__(self):
        return self.__str__()

    def __tree_repr__(self):
        return self.dense(), []

    def __iter__(self):
        for i in self.dense():
            yield i

    # binary operations
    def lt(self, other):
        return self.__binary_op__(other, 'lt')

    def le(self, other):
        return self.__binary_op__(other, 'le')

    def eq(self, other):
        return self.__binary_op__(other, 'eq')

    def ge(self, other):
        return self.__binary_op__(other, 'ge')

    def gt(self, other):
        return self.__binary_op__(other, 'gt')

    def __lt__(self, other):
        return self.__binary_op__(other, '__lt__')

    def __le__(self, other):
        return self.__binary_op__(other, '__le__')

    def __eq__(self, other):
        return self.__binary_op__(other, '__eq__')

    def __ne__(self, other):
        return self.__binary_op__(other, '__ne__')

    def __ge__(self, other):
        return self.__binary_op__(other, '__ge__')

    def __gt__(self, other):
        return self.__binary_op__(other, '__gt__')

    def is_(self, other):
        return self.__binary_op__(other, 'is_')

    def is_not(self, other):
        return self.__binary_op__(other, 'is_not')

    def add(self, other):
        return self.__binary_op__(other, 'add')

    def __add__(self, other):
        return self.__binary_op__(other, '__add__')

    def __radd__(self, other):
        return self.__binary_op__(other, '__radd__')

    def and_(self, other):
        return self.__binary_op__(other, 'and_')

    def __and__(self, other):
        return self.__binary_op__(other, '__and__')

    def __rand__(self, other):
        return self.__binary_op__(other, '__rand__')

    def floordiv(self, other):
        return self.__binary_op__(other, 'floordiv')

    def __floordiv__(self, other):
        return self.__binary_op__(other, '__floordiv__')

    def __rfloordiv__(self, other):
        return self.__binary_op__(other, '__rfloordiv__')

    def index(self, other):
        return self.__binary_op__(other, 'index')

    def __index__(self, other):
        return self.__binary_op__(other, '__index__')

    def lshift(self, other):
        return self.__binary_op__(other, 'lshift')

    def __lshift__(self, other):
        return self.__binary_op__(other, '__lshift__')

    def __rlshift__(self, other):
        return self.__binary_op__(other, '__rlshift__')

    def mod(self, other):
        return self.__binary_op__(other, 'mod')

    def __mod__(self, other):
        return self.__binary_op__(other, '__mod__')

    def __rmod__(self, other):
        return self.__binary_op__(other, '__rmod__')

    def mul(self, other):
        return self.__binary_op__(other, 'mul')

    def __mul__(self, other):
        return self.__binary_op__(other, '__mul__')

    def __rmul__(self, other):
        return self.__binary_op__(other, '__rmul__')

    def matmul(self, other):
        return self.__binary_op__(other, 'matmul')

    def __matmul__(self, other):
        return self.__binary_op__(other, '__matmul__')

    def or_(self, other):
        return self.__binary_op__(other, 'or_')

    def __or__(self, other):
        return self.__binary_op__(other, '__or__')

    def __ror__(self, other):
        return self.__binary_op__(other, '__ror__')

    def pow(self, other):
        return self.__binary_op__(other, 'pow')

    def __pow__(self, other):
        return self.__binary_op__(other, '__pow__')

    def __rpow__(self, other):
        return self.__binary_op__(other, '__rpow__')

    def rshift(self, other):
        return self.__binary_op__(other, 'rshift')

    def __rshift__(self, other):
        return self.__binary_op__(other, '__rshift__')

    def __rrshift__(self, other):
        return self.__binary_op__(other, '__rrshift__')

    def sub(self, other):
        return self.__binary_op__(other, 'sub')

    def __sub__(self, other):
        return self.__binary_op__(other, '__sub__')

    def __rsub__(self, other):
        return self.__binary_op__(other, '__rsub__')

    def truediv(self, other):
        return self.__binary_op__(other, 'truediv')

    def __truediv__(self, other):
        return self.__binary_op__(other, '__truediv__')

    def __rtruediv__(self, other):
        return self.__binary_op__(other, '__rtruediv__')

    def __divmod__(self, other):
        return self.__binary_op__(other, '__divmod__')

    def __rdivmod__(self, other):
        return self.__binary_op__(other, '__rdivmod__')

    def xor(self, other):
        return self.__binary_op__(other, 'xor')

    def __xor__(self, other):
        return self.__binary_op__(other, '__xor__')

    def __rxor__(self, other):
        return self.__binary_op__(other, '__rxor__')

    # unary operations
    def bool(self):
        return self.__unary_op__('bool')

    def __bool__(self):
        return self.__unary_op__('__bool__')

    def __nonzero__(self):
        return self.__unary_op__('__nonzero__')

    def real(self):
        return self.__unary_op__('real')

    def imag(self):
        return self.__unary_op__('imag')

    def not_(self):
        return self.__unary_op__('not_')

    def __not__(self):
        return self.__unary_op__('__not__')

    def truth(self):
        return self.__unary_op__('truth')

    def abs(self):
        return self.__unary_op__('abs')

    def __abs__(self):
        return self.__unary_op__('__abs__')

    def inv(self):
        return self.__unary_op__('inv')

    def invert(self):
        return self.__unary_op__('invert')

    def __inv__(self):
        return self.__unary_op__('__inv__')

    def __invert__(self):
        return self.__unary_op__('__invert__')

    def neg(self):
        return self.__unary_op__('neg')

    def __neg__(self):
        return self.__unary_op__('__neg__')

    def pos(self):
        return self.__unary_op__('pos')

    def __pos__(self):
        return self.__unary_op__('__pos__')

    def __float__(self):
        return self.__unary_op__('__float__')

    def __complex__(self):
        return self.__unary_op__('__complex__')

    def __oct__(self):
        return self.__unary_op__('__oct__')

    def __hex__(self):
        return self.__unary_op__('__hex__')

    def __trunc__(self):
        return self.__unary_op__('__trunc__')

    __hash__ = None

    def copy(self):
        return copy.deepcopy(self)


def _delete_leading_zeros(number_str):
    """
    Delete leading zeros from array indices

    :param number_str: A string containing comma separated dimension indices and colon separated ranges and strides, such as '008:010,0001:0002'

    :return: String with leading zeros stripped, such as '8:10,1:2'
    """
    return ','.join(
        [
            ':'.join([colon_split.lstrip('0') if colon_split.lstrip('0') else '0' for colon_split in comma_split.split(':')])
            for comma_split in number_str.split(',')
        ]
    )


# --------------------------------
# --------------------------------
# --------------------------------
############################################
if __name__ == '__main__':
    OMFITsrc = os.path.abspath(os.path.dirname(__file__) + os.sep + '..')
    test_classes_main_header()

    ranged_nl = NamelistFile(
        input_string='''
                             &test
                                 entry(1,1) = 1
                                 entry(2,1:2) = 1, 2
                                 entry(3,1) = 1
                                 entry(3,2) = 2
                                 entry(3,3) = 3
                                 entry(4,1) = 4
                                 entry(5,1:2) = 1, 2
                                 entry(6:7,1) = 6, 7
                             /
                             '''
    )
    assert ranged_nl['test']['entry'][1, 1] == 2  # Note that internal slicing is python-style based on 0
    ranged_nl['test']['entry'][1, 1] = 1
    assert ranged_nl['test']['entry'][1, 1] == 1
    assert ranged_nl['test']['entry'][4, 1] == 2

    ranged_nl.filename = '/tmp/ranged_nl.dat'
    ranged_nl.save()
    ranged_nl2 = NamelistFile('/tmp/ranged_nl.dat')
    ranged_nl2.load()
    failed_nl = NamelistFile(
        input_string='''
                             &test
                                entry(1:2,1:2) = 1
                             /
                             '''
    )
    failed_nl.load()
    foo = NamelistFile(OMFITsrc + '/../samples/k139817.00109')
    foo.load()
    print('---')
    foo['asd(1,1)'] = np.array([1, 2, 3])
    foo['asd(1,2)'] = np.array([4, 5, 6])
    foo.collectArrays()

    A2_Z = list(range(2))
    ILA_Z = list(range(3))
    antennas = list(range(6))
    foo['YGEOANT_A'] = YGEOANT_A = sparray(shape=(max(len(A2_Z), len(ILA_Z)), 6), default=0)
    for a, ant in enumerate(antennas):
        for i in range(len(A2_Z)):
            YGEOANT_A[(i + 1, a + 1)] = (i + 1) * 10 + a + 1

    foo.filename = '/tmp/%s/%s' % (os.environ.get('USER', 'nobody'), os.path.split(foo.filename)[1])
    foo.save()
    foo = NamelistFile(foo.filename)

    with open(foo.filename) as f:
        print(f.read())
    # print(foo)

    # asd=copy.deepcopy(foo)
    # foo.saveas('../samples/inone.03680_saved')
    # with open('../samples/inone.03680_saved','r') as f:
    #     for k in f.readlines():
    #        print(k.strip('\n'))

#     test='''
# because of this line it is assumed that everything outside the namelist blocks is a comment
# !b=1
# ac=4
# &my_namelist
#     hello='1 \$ 1'
#     array=1 2 3 3 4 5 6 6 6 7 8
#     array2=1 2 2*3 4 5 3*6 7 8
#     array3=asd asd asd
#     array4=3*asd
#     array5=
#     aaa(1,1)=4
#     aaa(1, 1)=5
# $END
#  ;this is another comment
# !this is a different comment format
#     '''
#     foo = NamelistFile(input_string=test,bang_comment_symbol='!;')
#     print(foo)
#     print(array_encoder(foo['my_namelist']['array']))
#     print(array_encoder(foo['my_namelist']['array3']))
#
#
