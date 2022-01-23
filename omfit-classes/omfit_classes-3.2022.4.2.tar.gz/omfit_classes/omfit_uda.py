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

try:
    import pyuda
except ImportError:
    pyuda = None

__all__ = ['OMFITudaValue', 'OMFITudaConnections']

OMFITudaConnections = {}


class OMFITudaValue:
    """
    A wrapper for pyuda calls that behaves like OMFITmdsValue
    """

    def __init__(self, server, shot=None, TDI=None, **kw):
        r"""
        :param server: The device or server from which to get a signal

        :param shot: Which shot

        :param TDI: The signal to fetch

        :param \**kw: Additional keywords that OMFITmdsValue might take, but
            are not necessary for UDA
        """
        if pyuda is None:
            raise RuntimeError('pyuda package is not installed')
        if shot is None:
            raise ValueError('shot must be given')
        if TDI is None:
            raise ValueError('TDI signal must be given')
        if server not in OMFITudaConnections:
            OMFITudaConnections[server] = pyuda.Client()
        self.client = OMFITudaConnections[server]
        self.shot = shot
        self.signal = TDI
        self.udasignal = self.client.get(self.signal, self.shot)

    def data(self):
        return self.udasignal.data[:]

    def dim_of(self, index=0):
        return self.udasignal.dims[index].data

    def units(self):
        return self.udasignal.units

    def units_dim_of(self, index=0):
        return self.udasignal.dims[index].units

    def xarray(self):
        """
        :return: DataArray with information from this node
        """

        data = self.data()
        dims = ['dim_%d' % k for k in range(data.ndim)]
        clist = []
        for k, c in enumerate(dims):
            clist.append(self.dim_of(k))

        if data.shape != tuple([len(k) if np.ndim(k) == 1 else k.shape[ik] for ik, k in enumerate(clist)]):
            dims = dims[::-1]
            clist = clist[::-1]

        coords = {}
        for k, c in enumerate(dims):
            if np.ndim(clist[k]) == 1:
                ck = c
                coords[ck] = ([c], clist[k], {'units': self.units_dim_of(k)})
            else:
                ck = c + '_val'
                coords[ck] = (dims, clist[k], {'units': self.units_dim_of(k)})

        xdata = DataArray(data, dims=dims, coords=coords, attrs={'units': self.units()})
        return xdata
