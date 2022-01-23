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

from omfit_classes.omfit_nc import OMFITnc

__all__ = ['OMFITgksout']


class OMFITgksout(OMFITnc):
    def __init__(self, filename, **kw):
        OMFITnc.__init__(self, filename, **kw)

    def plot(self, asd=None):
        from matplotlib import pyplot
        import numpy as np
        from omfit_classes.utils_plot import pcolor2

        pyplot.subplots_adjust(hspace=0.3)
        zdata = self['gamma_electron']['data']
        ydata = self['kys_k']['data']
        xdata = self['rho_k']['data']
        print(zdata.shape, ydata.shape, xdata.shape)
        if len(ydata.shape) == 2:

            def log10_label(x, pos=''):
                """
                Used for making $10^$ labels after having taken log10 of a quantity
                """
                return '$10^{%g}$' % x

            formatter = pyplot.FuncFormatter(log10_label)
            ax = pyplot.gcf().add_subplot(121)
            ax.yaxis.set_major_formatter(formatter)
            if len(xdata.shape) == 2:
                xdata = xdata[:, 0]
            r = xdata.flatten()
            xdata = np.array([r] * len(ydata[0, :])).T
            ydata = np.log10(ydata)
            obj = pcolor2(xdata, ydata, zdata)
            pyplot.title('$\\gamma_e$')
            pyplot.colorbar(obj, orientation='vertical')
            pyplot.ylabel('$k_{\\theta} \\, \\rho_s$')
            pyplot.xlabel('$\\rho_N$')

            ax = pyplot.gcf().add_subplot(122, sharex=ax, sharey=ax)
            ax.yaxis.set_major_formatter(formatter)
            zdata = self['gamma_ion']['data']
            obj = pcolor2(xdata, ydata, zdata)
            pyplot.title('$\\gamma_i$')
            pyplot.colorbar(obj, orientation='vertical')
            pyplot.ylabel('$k_{\\theta} \\, \\rho_s$')
            pyplot.xlabel('$\\rho_N$')

            # pyplot.gcf().add_subplot(223)
            # pyplot.plot(r,self['fprim1']['data'],label='ion')
            # pyplot.plot(r,self['fprim2']['data'],label='impurity')
            # pyplot.plot(r,self['fprim3']['data'],label='electron')
            # pyplot.legend().draggable(state=True)
            # pyplot.title('$\\nabla n$')
            # pyplot.xlabel('$\\rho_N$')

            # pyplot.gcf().add_subplot(224)
            # pyplot.plot(r,self['tprim1']['data']*self['tprim3']['data'],label='ion')
            # pyplot.plot(r,self['tprim2']['data']*self['tprim3']['data'],label='impurity')
            # pyplot.plot(r,self['tprim3']['data'],label='electron')
            # pyplot.title('$\\nabla T$')
            # pyplot.xlabel('$\\rho_N$')
            pyplot.suptitle(
                'Shot %s @ %s sec. - Growth Rates'
                % (''.join(np.atleast_1d(self['shot']['data'])).strip(), np.mean(self['xp_time']['data']))
            )

        elif len(ydata) > 1:

            ax = pyplot.gcf().add_subplot(111)
            zdata[np.where(zdata == 0)] = np.nan
            if len(np.where(zdata > 0)[0]):
                pyplot.loglog(ydata, zdata, label='$Log_{10} \\gamma_e$')
            else:
                pyplot.plot(ydata, zdata, label='$Log_{10} \\gamma_e$')
            pyplot.xlabel('$Log_{10} {\\gamma}$')
            pyplot.xlabel('$k_{\\theta} \\, \\rho_s$')
            zdata = self['gamma_ion']['data']
            if len(np.where(zdata > 0)[0]):
                pyplot.loglog(ydata, zdata, label='$Log_{10} \\gamma_i$')
            else:
                pyplot.plot(ydata, zdata, label='$Log_{10} \\gamma_i$')
            pyplot.legend().draggable(state=True)
            pyplot.title(
                'Shot %s @ %s sec. - Growth Rates at $\\rho=%2.2f$'
                % (''.join(np.atleast_1d(self['shot']['data'])).strip(), self['xp_time']['data'], self['rho_k']['data'])
            )

        pyplot.draw()
