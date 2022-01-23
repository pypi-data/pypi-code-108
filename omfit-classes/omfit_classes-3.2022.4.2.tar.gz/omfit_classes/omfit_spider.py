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

__all__ = ['OMFITspider_bonfit']


class OMFITspider_bonfit(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with SPIDER equilibirum bonfit (boundary fit) input file

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
        llines = lines.strip().split('\n')
        llines = [l.split('!')[0] for l in llines]

        ilines = iter(llines)

        def readline(ilines):
            while True:
                tmp = ilines.next().strip()
                if tmp:
                    return tmp

        self['w1'] = np.array(list(map(float, readline(ilines).split())))
        self['w2'] = np.array(list(map(float, readline(ilines).split())))
        n = int(readline(ilines).split()[0])
        self['R'] = []
        self['Z'] = []
        for k in range(n):
            r, z = list(map(float, readline(ilines).split()))
            self['R'].append(r)
            self['Z'].append(z)
        self['R'] = np.array(self['R'])
        self['Z'] = np.array(self['Z'])
        n = int(readline(ilines).split()[0])
        self['control_points'] = {}
        for k in range(n):
            r, z = list(map(float, readline(ilines).split()))
            self['control_points'][k] = np.array([r, z])
        self['xpoint'] = np.array(list(map(float, readline(ilines).split())))
        self['flux'] = float(readline(ilines).split()[0])
        self['xpoint2'] = np.array(list(map(float, readline(ilines).split())))

    @dynaSave
    def save(self):
        txt = []
        for item in self:
            if item == 'control_points':
                txt.append('%d' % len(self[item]))
                for k in self[item]:
                    txt.append(' '.join(list(map(str, self[item][k]))))
            elif item == 'R':
                txt.append('%d' % len(self['R']))
                for r, z in zip(self['R'], self['Z']):
                    txt.append('%s %s' % (r, z))
            elif item == 'Z':
                continue
            elif item == 'flux':
                txt.append(str(self[item]))
            else:
                txt.append(' '.join(list(map(str, self[item]))))
        with open(self.filename, 'w') as f:
            f.write('\n'.join(txt))

    def plot(self, ax=None):
        if ax is None:
            from matplotlib import pyplot

            ax = pyplot.gca()
        ax.plot(self['R'], self['Z'], 'r')
        for cp in self['control_points'].values():
            ax.plot(cp[0], cp[1], 'ro')
        ax.plot(self['xpoint'][0], self['xpoint'][1], '+r', ms=10)
        ax.plot(self['xpoint2'][0], self['xpoint2'][1], '+r', ms=10)
        ax.set_aspect('equal')
