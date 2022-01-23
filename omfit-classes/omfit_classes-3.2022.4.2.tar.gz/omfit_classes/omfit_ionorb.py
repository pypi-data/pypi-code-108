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

__all__ = ['OMFITionorbConfig', 'OMFITionorbBirth', 'OMFITionorbHits', 'OMFITionorbFull']


class OMFITionorbConfig(SortedDict, OMFITascii):
    """
    OMFIT class used to read/write IONORB configuration file

    :param filename: filename

    :param kw: additional parameters passed to the OMFITascii class
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
            line = line.strip()
            if line.startswith('#') or not len(line):
                continue
            else:
                tmp = line.split(' ')
                self[tmp[0]] = ' '.join(tmp[1:])
                try:
                    self[tmp[0]] = eval(self[tmp[0]])
                except Exception:
                    pass

    @dynaSave
    def save(self):
        txt = ''
        for item in self:
            if isinstance(self[item], (tuple, list, np.ndarray)):
                txt += item + ' ' + ', '.join(map(str, self[item])) + '\n'
            else:
                txt += item + ' ' + str(self[item]) + '\n'
        with open(self.filename, 'w') as f:
            f.write(txt)


class OMFITionorbBirth(SortedDict, OMFITascii):
    """
    OMFIT class used to read/write IONORB birth list or profiles

    :param filename: filename

    :param kw: additional parameters passed to the OMFITascii class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

    columns = ['R[m]', 'Phi[Rad]', 'z[m]', 'v_R[m/s]', 'v_phi[m/s]', 'v_z[m/s]']

    @dynaLoad
    def load(self):
        conversion = {'m': 'mass', 'q': 'charge', 'notshine': 'fracpinjdepo', 'nels': 'npart'}
        with open(self.filename, 'Ur') as f:
            lines = f.read().strip().split('\n')
        self['header'] = []
        for i, l in enumerate(lines):
            if l[0] == '#':
                self['header'].append(l)
                continue
            if l.startswith('<start-of-data>'):
                break
            k, v = l.split()
            k = conversion.get(k, k)
            self[k] = v
        data = np.fromstring('\n'.join(lines[i + 1 :]), sep=' ').reshape(-1, len(self.columns))

        for k, name in enumerate(self.columns):
            self[name.split('[')[0]] = data[:, k]

    @dynaSave
    def save2(self):
        txt = '# ionorb birth profile source\n'
        txt += '# version: v2\n'
        txt += 'm %5.5f\n' % self['mass']
        txt += 'q %5.5f\n' % self['charge']
        txt += 'notshine %d\n' % self['fracpinjdepo']
        txt += 'nels %5.3f\n' % self['npart']
        txt += ' ' + ' '.join([x.ljust(13) for x in self.columns]) + '\n'
        txt += '<start-of-data>\n'
        data = np.array([self[name.split('[')[0]] for name in self.columns]).T
        data_string = []
        for row in range(data.shape[0]):
            data_string.append(' ' + ' '.join(['% 8.6e' % x for x in data[row, :]]))
        txt += '\n'.join(data_string)
        with open(self.filename, 'w') as f:
            f.write(txt)


class OMFITionorbHits(SortedDict, OMFITascii):
    """
    OMFIT class used to read the IONORB hits file

    :param filename: filename

    :param kw: additional parameters passed to the OMFITascii class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

    columns = ['ID', 'Time[s]', 'Step', 'Wall_Idx', 'R[m]', 'Phi[Rad]', 'z[m]', 'v_R[m/s]', 'v_phi[m/s]', 'v_z[m/s]']

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.read().strip().split('\n')
        data = np.array([list(map(float, line.split())) for line in lines[1:]])
        for k, name in enumerate(self.columns):
            self[name.split('[')[0]] = data[:, k]

    def plot(self, **kw):
        kw.setdefault('ls', '')
        kw.setdefault('marker', 'x')
        pyplot.plot(self['R'], self['z'], **kw)


class OMFITionorbFull(SortedDict, OMFITascii):
    """
    OMFIT class used to read the Full Orbit file output by the ionorbiter code

    :param filename: filename

    :param kw: additional parameters passed to the OMFITascii class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

    columns = ['Time[s]', 'Step', 'R[m]', 'Phi[Rad]', 'z[m]']

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.read().strip().split('\n')
        data = np.array([list(map(float, line.split())) for line in lines[1:]])
        for k, name in enumerate(self.columns):
            self[name.split('[')[0]] = data[:, k]
