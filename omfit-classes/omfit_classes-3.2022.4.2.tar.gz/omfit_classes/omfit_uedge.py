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
from omfit_classes.omfit_hdf5 import OMFIThdf5
from omfit_classes.omfit_json import OMFITjson

__all__ = [
    'OMFITuedge',
    'uedge_variable',
    'uedge_common_mapper',
    'uedge_common_map_generator',
    'OMFITuedgeBasisInput',
    'OMFITuedgeInput',
    'OMFITuedge',
]


class uedge_variable(str):
    """
    class used to distinguish between strings and uedge variables in the PyUEDGE input deck
    """

    pass


def uedge_common_map_generator(uedge_dir):
    """
    Parse the bbb.v com.v flx.v grd.v files and generate mapper for common blocks

    This is useful because the BASIS version of UEDGE used not
    to require specifying the common blocks for variables.
    Transition to PyUEDGE requires people to add the common block
    information to the old input files.

    To translate old UEDGE files to the new PyUEDGE format use:
    >> OMFITuedgeBasisInput('old_uedge_input.txt').convert()

    :param uedge_dir: folder where UEDGE is installed

    :return: OMFITjson object containing with mapping info
    """
    mapper = OMFITjson('uedge_common_map.json')
    for common in ['aph', 'api', 'bbb', 'com', 'flx', 'grd', 'svr', 'wdf']:
        with open(uedge_dir + '/%s/%s.v' % (common, common), 'r') as f:
            lines = f.read().split('\n')
        block = ''
        var = None
        for line in lines:
            # identify block
            if re.match(r'\*\*\*\*\* \w+:', line):
                block = line.split()[1][:-1]
            # append to previous var comment
            if var is not None and line.strip().startswith('#'):
                mapper[var]['comment'] += '\n' + line
            # parse the line
            tmp = line.strip().split()
            # nothing to do
            if len(tmp) < 2 or tmp[0].startswith('#') or tmp[0].startswith('$'):
                continue
            # if it is a variable then add it to the mapper
            if (
                tmp[1].strip('_') in ['real', 'integer']
                or tmp[1].strip('_').startswith('character')
                or (len(tmp) > 2 and tmp[2].strip('_') in ['real', 'integer'])
                or (len(tmp) > 2 and tmp[2].strip('_').startswith('character'))
            ):
                var = tmp[0].split('(')[0]
                if var not in mapper:
                    mapper[var] = {}
                    mapper[var]['location'] = []
                mapper[var]['var'] = tmp[0]
                mapper[var]['location'].append((common, block))
                mapper[var]['comment'] = line
        mapper.sort()
    return mapper


_uedge_common = []


def uedge_common_mapper(var=None):
    """
    Parses the uedge_common_map.json and caches it for later use

    :param var: either variable name or None

    :return: mapper if var is None else mapping info for var
    """
    import json

    if not len(_uedge_common):
        with open(os.path.split(__file__)[0] + os.sep + 'uedge_common_map.json') as f:
            _uedge_common.append(json.load(f))
    if var is None:
        return _uedge_common[0]
    else:
        var = var.split('(')[0]
        return _uedge_common[0][var]


class OMFITuedgeBasisInput(OMFITascii, SortedDict):
    """
    Class used to parse input files from BASIS version of UEDGE

    To translate old UEDGE files to the new PyUEDGE format use:
    >> OMFITuedgeBasisInput('old_uedge_input.txt').convert()
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        for li in self.read().splitlines():
            if '=' not in li:
                continue
            k, v = li.split('=', 1)
            k = k.strip()
            v = v.split('#')[0].strip()
            try:
                v = ast.literal_eval(v)
            except ValueError:
                v = uedge_variable(v)
            self[k] = v

    def convert(self):
        """
        Convert input files from BASIS version of UEDGE to Python version

        :return: OMFITuedgeInput object
        """
        tmp = OMFITuedgeInput(os.path.basename(self.filename))
        for item in self:
            var = item.split('(')[0]
            if var in uedge_common_mapper():
                mapper = uedge_common_mapper(var)
                common = mapper['location'][0][0]
                mapped_item = item
                if '(' in item:
                    index = np.array(list(map(int, item.split('(')[-1][:-1].split(',')))) - 1
                    mapped_item = var + '[%s]' % ','.join(map(str, index))
                if common not in tmp:
                    tmp[common] = SortedDict()
                tmp[common][mapped_item] = self[item]
        return tmp


class OMFITuedgeInput(OMFITascii, SortedDict):
    """
    Class used to parse input files of Python version of UEDGE
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        for li in self.read().splitlines():
            if '=' not in li:
                continue
            k, v = li.split('=', 1)
            k = k.strip()
            v = v.split('#')[0].strip()

            try:
                if v.startswith('array(') and v.endswith(')'):
                    # Deal with np arrays
                    v = v[6:-1]  # strip the 'array('  and ')'
                    v = np.array(ast.literal_eval(v))  # This can parse high dimension arrays that fromstring() can't
                else:
                    v = ast.literal_eval(v)
            except ValueError:
                v = uedge_variable(v)
            if '.' in k:
                c, k = k.split('.')
                self.setdefault(c, {})
                self[c][k] = v
            else:
                self[k] = v

    @dynaSave
    def save(self):
        tmp = []
        for c in self:
            if isinstance(self[c], dict):
                for k, v in self[c].items():
                    if isinstance(v, uedge_variable):
                        tmp.append(f'{c}.{k}={v}'.replace('\n', '').replace(' ', ''))
                    else:
                        tmp.append(f'{c}.{k}={repr(v)}'.replace('\n', '').replace(' ', ''))
            else:
                v = self[c]
                if isinstance(v, uedge_variable):
                    tmp.append(f'{c}={v}'.replace('\n', '').replace(' ', ''))
                else:
                    tmp.append(f'{c}={repr(v)}'.replace('\n', '').replace(' ', ''))
        with open(self.filename, 'w') as f:
            f.write('\n'.join(tmp))


class OMFITuedge(OMFIThdf5):
    def plot_mesh(self, ax=None, **kw):
        r"""
        Plot mesh

        :param ax: plot axes

        :param \**kw: extra arguments passed to plot
        """
        if ax is None:
            ax = pyplot.gca()

        ix = self['com']['nx']['data']
        iy = self['com']['ny']['data']

        drm = self['com']['rm']['data']
        dzm = self['com']['zm']['data']

        for jy in np.arange(0, iy + 2):
            for jx in np.arange(0, ix + 2):
                ax.plot(drm[jx, jy, [1, 2, 4, 3, 1]], dzm[jx, jy, [1, 2, 4, 3, 1]], **kw)
                if 'color' not in kw:
                    kw['color'] = ax.lines[-1].get_color()

        ax.set_xlabel('$R$ [m]')
        ax.set_ylabel('$Z$ [m]')

        ax.set_aspect('equal', 'datalim')

    def plot_box(self, variable='te', ax=None, levels=None, edgecolor='none', **kw):
        r"""
        Plot UEDGE results for a box mesh

        :param variable: variable to plot

        :param ax: axes

        :param levels: number of levels in contour plot

        :param edgecolor: edgecolor of contour plot

        :param \**kw: extra arguments passed to contour plot
        """
        if ax is None:
            ax = pyplot.gca()

        nice = self.nice_vars(variable)

        comrm = self['com']['rm']['data']
        comzm = self['com']['zm']['data']
        bbbte = self['bbb'][variable]['data']

        yy = bbbte / nice['norm']

        CS = ax.contourf(comzm[:, :, 0], comrm[:, :, 0], yy, levels=levels, **kw)
        ax.contour(comzm[:, :, 0], comrm[:, :, 0], yy, levels=levels, edgecolor=edgecolor)

        ax.set_title('%s [%s]' % (nice['label'], nice['units']))

        ax.set_xlabel('$Z$ [m]')
        ax.set_ylabel('$R$ [m]')

        cbar = pyplot.gcf().colorbar(CS)
        cbar.ax.set_ylabel(nice['units'])

    def plot(self, variable='te', ax=None, edgecolor='none', **kw):
        r"""
        Plot UEDGE results for a poloidal mesh

        :param variable: variable to plot

        :param ax: axes

        :param levels: number of levels in contour plot

        :param edgecolor: edgecolor of contour plot

        :param \**kw: extra arguments passed to PatchCollection
        """

        if ax is None:
            ax = pyplot.gca()

        nice = self.nice_vars(variable)

        from matplotlib.patches import Polygon
        from matplotlib.collections import PatchCollection

        comnx = self['com']['nx']['data']
        comny = self['com']['ny']['data']
        comrm = self['com']['rm']['data']
        comzm = self['com']['zm']['data']

        bbbte = self['bbb'][variable]['data']

        patches = []

        for iy in np.arange(0, comny + 2):
            for ix in np.arange(0, comnx + 2):
                rcol = comrm[ix, iy, [1, 2, 4, 3]]
                zcol = comzm[ix, iy, [1, 2, 4, 3]]
                rcol.shape = (4, 1)
                zcol.shape = (4, 1)
                polygon = Polygon(np.column_stack((rcol, zcol)), True)
                patches.append(polygon)

        vals = np.zeros((comnx + 2) * (comny + 2))

        for iy in np.arange(0, comny + 2):
            for ix in np.arange(0, comnx + 2):
                k = ix + (comnx + 2) * iy
                vals[k] = bbbte[ix, iy] * nice['norm']

        p = PatchCollection(patches, edgecolors=edgecolor, **kw)
        p.set_array(np.array(vals))
        ax.add_collection(p)
        ax.autoscale_view()

        ax.set_title('%s [%s]' % (nice['label'], nice['units']))

        pyplot.xlabel('$R$ [m]')
        pyplot.ylabel('$Z$ [m]')

        ax.set_aspect('equal')

        cbar = pyplot.gcf().colorbar(p)
        cbar.ax.set_ylabel(nice['units'])

    def nice_vars(self, variable):
        """
        return info for a given UEDGE output variable

        :param variable: variable name

        :return: dictionary with units, label, norm
        """
        tmp = {}
        if variable.startswith('t'):
            tmp['label'] = r'T$\mathregular{_%s}$' % variable[1:]
            tmp['units'] = 'eV'
            tmp['norm'] = 1.0 / self['bbb']['ev']['data']
        elif variable.startswith('n'):
            tmp['label'] = r'n$\mathregular{_%s}$' % variable[1:]
            tmp['units'] = '[m^{-3}/1e20]'
            tmp['norm'] = 1.0 / 1.0e20
        elif variable.startswith('u'):
            tmp['label'] = r'V$\mathregular{_%s}$' % variable[1:]
            tmp['units'] = '[(m/s)/1e3]'
            tmp['norm'] = 1.0 / 1e3
        else:
            tmp['label'] = variable
            tmp['units'] = ''
            tmp['norm'] = 1.0
        return tmp
