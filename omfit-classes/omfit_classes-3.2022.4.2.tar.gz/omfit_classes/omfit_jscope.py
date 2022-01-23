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

__all__ = ['OMFITjscope', 'OMFITdwscope']


class OMFITjscope(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with jScope save files

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
            if not len(line.strip()):
                continue
            elif line.startswith('Scope.'):
                key, value = line.split(':', 1)
                value = value.strip()
                if value == 'false':
                    value = False
                elif value == 'true':
                    value = True
                else:
                    try:
                        value = ast.literal_eval(value.strip())
                    except (SyntaxError, ValueError):
                        pass
                    except Exception:
                        printe(line, value)
                        raise
                h = self
                for item in key.split('.')[1:-1]:
                    h = h.setdefault(item, {})
                h[key.split('.')[-1]] = value

    def server(self):
        '''
        Figure out server to connect to

        :return: server name or machine name
        '''
        if 'data_server_argument' in self:
            return self['data_server_argument']
        elif 'global_1_1' in self and any('nstx' in str(value).lower() for value in self['global_1_1'].values()):
            return 'NSTX'
        else:
            raise ValueError('Could not determine what MDS+ server to connect to')

    def treename(self, item, yname):
        '''
        Figure out threename to use

        :param item: thing to plot

        :param yname: `y` or `y_expr_1`

        :return:
        '''

        if 'experiment' in self[item].keys():

            treename = self[item]['experiment']
        else:
            signal = self[item][yname]
            if ':' in signal:
                treename = signal.split(':')[0].strip('\\')
            else:
                treename = self['global_1_1']['experiment']
        if 'pcs.' in treename.lower():  # for NSTX
            treename = 'eng_test'
        return treename

    def plot(self, shot=None):
        '''
        Plot signals

        :param shot: shot number

        :return: dictionary with all axes indexed by a tuple indicating the row and column
        '''
        from matplotlib.pyplot import subplot
        from omfit_classes.omfit_mds import OMFITmdsValue

        axs = {}
        rows = {}
        cols = []
        for item in self:
            if not item.startswith('plot_'):
                continue
            r, c = map(int, item.split('_')[1:])
            rows[c] = r
            cols.append(c)
        cols = max(cols)
        ax = None
        for item in self:
            if not item.startswith('plot_'):
                continue
            r, c = map(int, item.split('_')[1:])
            axs[r, c] = ax = subplot(rows[c], cols, cols * (r - 1) + c, sharex=ax)
            ax.set_title(self[item]['title'].split("//")[0], y=0.5)
            yname = 'y_expr_1' if 'y_expr_1' in self[item] else 'y'
            xname = 'x_expr_1' if 'x_expr_1' in self[item] else 'x'
            treename = self.treename(item, yname)
            server = self.server()
            if shot is not None:
                y = OMFITmdsValue(server, treename, shot, self[item][yname])
                if y.check():
                    if xname in self[item]:
                        treename = self.treename(self[item][xname])
                        x = OMFITmdsValue(server, treename, shot, self[item][xname]).data()
                    else:
                        x = y.dim_of(0)
                    ax.plot(x, y.data())
            if self[item].get('x_log', False):
                ax.set_xscale('log')
            if self[item].get('y_log', False):
                ax.set_yscale('log')
            ax.set_xlim(self['global_1_1'].get('xmin',None), self['global_1_1'].get('xmax',None))

        if shot is None:
            printw('Please specify shot number')
        return axs

    def signal_treename(self, item):
        yname = 'y_expr_1' if 'y_expr_1' in self[item] else 'y'
        treename = self.treename(item, yname)
        signal = self[item][yname].split(':')[-1].strip('\\')
        return signal, treename


class OMFITdwscope(OMFITjscope):
    pass
