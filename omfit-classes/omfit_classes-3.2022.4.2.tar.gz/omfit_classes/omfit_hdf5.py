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

from matplotlib import pyplot
import numpy as np

try:
    import h5py._hl.dataset

    def h5py_dataset_tree_repr(self):
        return self[()], []

    h5py._hl.dataset.Dataset.__tree_repr__ = h5py_dataset_tree_repr
    import h5py
except ImportError as _excp:
    h5py = None
    warnings.warn('No `hdf5` support: ' + repr(_excp))

__all__ = ['OMFIThdf5raw', 'OMFIThdf5', 'dict2hdf5']


def dict2hdf5(filename, dictin, groupname='', recursive=True, lists_as_dicts=False, compression=None):
    """
    Save hierarchy of dictionaries containing np-compatible objects to hdf5 file

    :param filename: hdf5 file to save to

    :param dictin: input dictionary

    :param groupname: group to save the data in

    :param recursive: traverse the dictionary

    :param lists_as_dicts: convert lists to dictionaries with integer strings

    :param compression: gzip compression level
    """
    if isinstance(filename, str):
        with h5py.File(filename, 'w') as g:
            dict2hdf5(g, dictin, recursive=recursive, lists_as_dicts=lists_as_dicts, compression=compression)
        return
    else:
        parent = filename

    if groupname:
        g = parent.create_group(groupname)
    else:
        g = parent

    for key, item in list(dictin.items()):

        if isinstance(item, dict):
            if recursive:
                dict2hdf5(g, item, key, recursive=recursive, lists_as_dicts=lists_as_dicts, compression=compression)

        elif lists_as_dicts and isinstance(item, (list, tuple)) and not isinstance(item, np.ndarray):
            item = {'%d' % k: v for k, v in enumerate(item)}
            dict2hdf5(g, item, key, recursive=recursive, lists_as_dicts=lists_as_dicts, compression=compression)

        else:
            if item is None:
                item = '_None'
            tmp = np.array(item)
            printd('tmp.dtype=', tmp.dtype, topic='hdf5')
            printd('tmp.dtype.name=', tmp.dtype.name, topic='hdf5')
            if str(tmp.dtype).lower().lstrip('<>|').startswith('u'):
                tmp = tmp.astype('S')
            elif tmp.dtype.name.lower().startswith('o'):
                printw('Could not save `%s` to h5 file' % key)
                continue
            if tmp.shape == ():
                g.create_dataset(key, tmp.shape, dtype=tmp.dtype)[...] = tmp
            else:
                g.create_dataset(key, tmp.shape, dtype=tmp.dtype, compression=compression)[...] = tmp

    return g


class OMFIThdf5raw(SortedDict, OMFITobject):
    """
    OMFIT class that exposes directly the h5py.File class
    """

    def __init__(self, filename, **kw):
        OMFITobject.__init__(self, filename, **kw)
        SortedDict.__init__(self, sorted=True)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        self.clear()
        self.update(h5py.File(self.filename, 'r'))


class OMFIThdf5dataset(SortedDict):
    """
    Replacement for h5py.Dataset that provides some useful methods like plot, etc.
    """

    def __init__(self, dataset, oh5=None):
        """

        :param dataset: h5py.Dataset instance
        :param oh5: parent OMFIThdf5 instance
            Required for handling lookup of dimensions
        """
        self.update(dataset.attrs)
        self['data'] = dataset[()]
        self.oh5 = oh5
        h5file = self.get_h5file()
        if 'DIMENSION_LIST' in self:
            self['dims'] = [b2s(h5py.h5r.get_name(self['DIMENSION_LIST'][0][i], h5file.id)) for i in range(len(self['DIMENSION_LIST'][0]))]
        return

    def get_h5file(self):
        """Gets a reference to the h5py.File instance associated with the parent OMFIThdf5"""
        if self.oh5 is None:
            return None
        else:
            h5file = getattr(self.oh5, '_data')
            if h5file is None:
                h5file = h5py.File(self.filename, 'r')
            return h5file

    def plot(self, ax=None, **plot_kw):
        """
        Plots data.

        If enough information is available, the correct coordinates will be used. Otherwise, plots vs. array index.

        :param ax: Axes instance

        :param plot_kw: parameters passed to plot() call

        :return: output from plot call; probably an array of line objects or something
        """

        ndim = len(np.shape(self['data']))

        if ndim == 1:
            return self._plot_1d(ax=ax, **plot_kw)
        else:
            printe('Method for plotting ndim = {} is not yet supported, sorry.'.format(ndim))
            return None

    def get_dim(self, idx):
        """
        Gets information about a coordinate dimension
        :param idx: int
            Which dimension?
        :return: tuple containing array, string, string
            x
            label
            units
        """
        xunits = ''
        xlabel = ''
        if self.oh5 is None or 'dims' not in self or len(self['dims']) == 0:
            x = None
        else:
            d0 = self['dims'][idx]
            if d0 in self.oh5:
                dim = self.oh5[d0]
            elif d0[1:] in self.oh5:
                dim = self.oh5[d0[1:]]
            else:
                dim = None

            if dim is None or dim.get('data', None) is None:
                x = None
            else:
                x = dim['data']
                xunits = b2s(dim.get('units', ''))
                xlabel = b2s(dim.get('title', ''))

        return x, xunits, xlabel

    def _plot_1d(self, ax=None, **plot_kw):
        """
        Plots 1D data

        :param ax: Axes instance

        :param plot_kw: keywords passed to plot

        :return: output from plot call; probably an array of line objects or something
        """

        if ax is None:
            ax = pyplot.gca()

        y = self['data']
        yunits = b2s(self.get('units', ''))
        ylabel = b2s(self.get('title', ''))

        x, xunits, xlabel = self.get_dim(0)
        if x is None:
            x = np.arange(len(y))
            xlabel = 'index'
            xunits = ''

        if yunits:
            ylabel += ' ({})'.format(yunits)
        if xunits:
            xlabel += ' ({})'.format(xunits)
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        return ax.plot(x, y, **plot_kw)


class OMFIThdf5(SortedDict, OMFITobject):
    """
    OMFIT class that translates HDF5 file to python dictionary
    At this point this class is read only. Changes made to the
    its content will not be reflected to the HDF5 file.
    """

    def __init__(self, filename, **kw):
        OMFITobject.__init__(self, filename, **kw)
        SortedDict.__init__(self, sorted=True)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        self.clear()
        try:
            self._data = h5py.File(self.filename, 'r')
            self._convertDataset()
        finally:
            if hasattr(self, '_data'):
                self._data.close()
                delattr(self, '_data')

    def update(self, dictin, groupname='', recursive=True, lists_as_dicts=True, compression=None):
        with h5py.File(self.filename, 'w') as g:
            dict2hdf5(g, dictin, recursive=recursive, compression=compression)
        return self

    def _convertDataset(self, path=''):
        data_location = eval('self._data' + path)
        self_location = eval('self' + path)
        for item in data_location:
            if isinstance(data_location[item], h5py.Dataset):
                self_location[item] = OMFIThdf5dataset(data_location[item], self)
            elif isinstance(data_location[item], h5py.Group):
                self_location[item] = SortedDict(sorted=True)
                self._convertDataset(path=path + "[%s]" % repr(item))
        return


############################################
if __name__ == '__main__':
    test_classes_main_header()

    tmp = OMFIThdf5raw(OMFITsrc + '/../samples/def_equilibrium.h5')
    tmp.load()
