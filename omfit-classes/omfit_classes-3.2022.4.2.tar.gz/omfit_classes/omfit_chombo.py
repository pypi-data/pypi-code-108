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

__all__ = ['OMFITchombo']


class OMFITchombo(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with CHOMBO input files

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
            lines = f.read().split('\n')
        for line in lines:
            line = re.sub('#.*', '', line).strip()
            if not len(line):
                continue
            where, val = list(map(lambda x: str(x).strip(), line.split('=')))
            where = where.split('.')
            s = self
            for loc in where[:-1]:
                s.setdefault(loc, SortedDict())
                s = s[loc]
            if where[-1] in ['magnetic_geometry_mapping']:
                s['__' + where[-1] + '__'] = namelist.interpreter(val)
                s[where[-1]] = SortedDict()
            elif "'" in val or '"' in val:
                v = val[0]
                s[where[-1]] = eval('np.array([' + re.sub(v + ' ' + v, v + ',' + v, val) + '])')
                if len(s[where[-1]]) == 1:
                    s[where[-1]] = s[where[-1]][0]
            else:
                s[where[-1]] = list(map(namelist.interpreter, val.split()))
                if len(s[where[-1]]) == 1:
                    s[where[-1]] = s[where[-1]][0]
                else:
                    s[where[-1]] = np.array(s[where[-1]])

    @dynaSave
    def save(self):
        lines = []
        prev = list(self.keys())[0]
        for where in traverse(self, onlyLeaf=True):

            # split main blocks
            tmp = parseBuildLocation(where)[0]
            if tmp != prev:
                lines.append('')
                prev = tmp

            tmp = re.sub('\'', '"', namelist.encoder(eval('self' + where), dotBoolean=False, array_compress=False, max_array_chars=None))
            if isinstance(eval('self' + where), bool):
                tmp = tmp.lower()
            lines.append('.'.join([x.strip('__') for x in parseBuildLocation(where)]) + ' = ' + re.sub('\'', '"', tmp))

        with open(self.filename, 'w') as f:
            f.write('\n'.join(lines))
