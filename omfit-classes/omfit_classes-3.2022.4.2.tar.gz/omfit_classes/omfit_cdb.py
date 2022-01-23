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

if 'CDB_PATH' in os.environ:
    _pycdb_pythonpath = os.path.abspath(os.environ['CDB_PATH'])
    if _pycdb_pythonpath not in [os.path.abspath(_path) for _path in sys.path]:
        sys.path.insert(1, _pycdb_pythonpath)
        print('* Path to CDB has been added: ' + _pycdb_pythonpath)
    else:
        print('* Path to CDB was found' + _pycdb_pythonpath)
    if 'PYTHONPATH' in os.environ and os.environ['PYTHONPATH']:
        if _pycdb_pythonpath not in os.environ['PYTHONPATH']:
            os.environ['PYTHONPATH'] = _pycdb_pythonpath + ':' + os.environ['PYTHONPATH']
    else:
        os.environ['PYTHONPATH'] = _pycdb_pythonpath
try:
    import pyCDB
    from pyCDB.client import CDBClient
except Exception as _excp:
    pyCDB = None
    CDBClient = None

__all__ = ['OMFITcdb', 'OMFITcdbValue', 'pyCDB']


class OMFITcdbValue(object):
    def __init__(self, **kw):
        self.alias = kw.pop('alias', None)
        if 'shot' in kw:
            kw['record_number'] = kw.pop('shot')
        self.user_kw = kw
        self._kw = kw
        self._data = None

    def __getattr__(self, attr):
        attr_list = [
            'axes',
            'daq_attachment',
            'daq_parameters',
            'data',
            'description',
            'file_ref',
            'get_axes_info',
            'get_log_level',
            'get_ndim',
            'gs_parameters',
            'gs_ref',
            'info',
            'log_level',
            'name',
            'ndim',
            'plot',
            'ref',
            'set_log_level',
            'set_ndim',
            'time_axis',
            'units',
            'url',
        ]
        if attr in attr_list + ['axis%d' % k for k in range(1, 7)]:
            self.fetch()
        return getattr(self._data, attr)

    def fetch(self):
        if self._data is None:
            if 'CDBclient' not in OMFITaux:
                OMFITaux['CDBclient'] = CDBClient()
            client = OMFITaux['CDBclient']
            if 'CDB_cache' not in OMFIT['scratch']:
                OMFIT['scratch']['CDB_cache'] = {}
            if tuple(self.user_kw.values()) not in OMFIT['scratch']['CDB_cache']:
                OMFIT['scratch']['CDB_cache'][tuple(self.user_kw.values())] = client.get_signal(**self.user_kw)
            self._data = OMFIT['scratch']['CDB_cache'][tuple(self.user_kw.values())]
            self._kw = self._data.__dict__

    @property
    def _description(self):
        if 'description' in self._kw and self._kw['description']:
            return self._kw['description']
        elif 'generic_signal_name' in self._kw and self._kw['generic_signal_name']:
            return re.sub('_', ' ', self._kw['generic_signal_name'])
        elif 'generic_signal_id' in self._kw and self._kw['generic_signal_id']:
            return 'signal id: %d' % self._kw['generic_signal_id']

    def plot(self):
        self.fetch()
        tmp = self._data.plot(fig=pyplot.gcf())
        pyplot.gcf().suptitle(self._description)
        return tmp

    def __str__(self):
        description = self._description
        tmp = [description, '=' * 21]
        tmp.append('%s: %s' % ('alias'.ljust(20), self.alias))
        for k in self._kw:
            if k in ['ref', 'data', 'axes']:
                continue
            if isinstance(self._kw[k], pyCDB.client.CDBSignal):
                tmp.append('%s: %s' % (k.ljust(20), 'CDB signal --> ' + str(self._kw[k].name)))
            elif isinstance(self._kw[k], pyCDB.pyCDBBase.OrderedDict):
                continue
            else:
                tmp.append('%s: %s' % (k.ljust(20), self._kw[k]))
        return '\n'.join(tmp)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(self._kw)[1:-1])

    @property
    def help(self):
        units = ''
        if 'units' in self._kw and self._kw['units']:
            units = '[%s] ' % self._kw['units']
        return units + self._description

    def __tree_repr__(self):
        if self._data is not None:
            values = [self.data, ['MDSactive']]
        else:
            values = [self.help, []]
        return values


class OMFITcdb(SortedDict):
    def __init__(self, shot):
        SortedDict.__init__(self, sorted=True)
        self.shot = shot
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        if 'CDBclient' not in OMFITaux:
            OMFITaux['CDBclient'] = CDBClient()
        client = OMFITaux['CDBclient']
        tmp = client.get_generic_signal_references(record_number=self.shot)
        groups = {k.data_source_id: k for k in client.get_data_source_references()}
        for k in tmp:
            group_name = groups[k.data_source_id].name
            self.setdefault(group_name, {})
            self[group_name][k.generic_signal_name] = OMFITcdbValue(record_number=self.shot, **k)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, 'shot=%d' % self.shot)

    def __tree_repr__(self):
        return '#%d @ COMPASS' % self.shot, []


class OMFITcdb(SortedDict):
    def __init__(self, shot):
        SortedDict.__init__(self, sorted=True)
        self.shot = shot
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        if 'CDBclient' not in OMFITaux:
            OMFITaux['CDBclient'] = CDBClient()
        client = OMFITaux['CDBclient']
        tmp = client.get_generic_signal_references(record_number=self.shot)
        groups = {k.data_source_id: k for k in client.get_data_source_references()}
        for k in tmp:
            group_name = groups[k.data_source_id].name
            self.setdefault(group_name, {})
            self[group_name][k.generic_signal_name] = OMFITcdbValue(record_number=self.shot, **k)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, 'shot=%d' % self.shot)

    def __tree_repr__(self):
        return '#%d @ COMPASS' % self.shot, []
