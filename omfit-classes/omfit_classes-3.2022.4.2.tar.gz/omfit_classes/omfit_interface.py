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

import numpy as np

__all__ = ['OMFITinterface', 'interface']


class OMFITinterfaceError(Exception):
    pass


class OMFITinterfaceAdaptor(SortedDict):

    type = ''

    def __init__(self, data=None):
        SortedDict.__init__(self)
        self['__quantities__'] = SortedDict(sorted=True)
        self['__dimensions__'] = SortedDict(sorted=True)
        baseDimensions = ['', 'i', 'b', 'r', 't']

        s = list(baseDimensions[1:])
        self.allowedDimensions = []
        for k in itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1)):
            self.allowedDimensions.append(''.join(k))
        self.allowedDimensions.insert(0, '')
        # i and b should not coexist

        self.data = data
        self.list()
        self.dims()

    def definitions(self, key, data):
        pass

    def dims(self):
        if self.data is None:
            return

        if hasattr(self, 'adaptor'):
            self['__dimensions__'].update(self.adaptor['__dimensions__'])

        for item in self['__dimensions__']:
            if not isinstance(self['__dimensions__'][item], str):
                continue
            if item == '':
                self['__dimensions__'][item] = (1,)
            else:
                self['__dimensions__'][item] = self[self['__dimensions__'][item]].shape

        for item in list(self['__dimensions__'].keys()):
            if item != '' and np.iterable(self['__dimensions__'][item]):
                tmp = [1] * len(item)
                for k, s in enumerate(self['__dimensions__'][item]):
                    tmp[k] = s
                self['__dimensions__'][item] = tmp

        for item in list(self['__dimensions__'].keys()):
            if np.iterable(self['__dimensions__'][item]):
                for k, s in enumerate(item):
                    self['__dimensions__'][s] = self['__dimensions__'][item][k]
                del self['__dimensions__'][item]
            self['__dimensions__'][''] = 1

    def register(self, key, quantity, description, units, dimension):

        quantities = np.atleast_1d(quantity)
        for quantity in quantities:

            if quantity not in list(self['__quantities__'].keys()):
                if dimension not in self.allowedDimensions:
                    raise OMFITinterfaceError('Dimension `' + dimension + '` is not allowed, use: ' + repr(self.allowedDimensions))

                self['__quantities__'][quantity] = SortedDict({'description': description, 'units': units, 'raw_dimension': dimension})
                self['__dimensions__'][dimension] = quantity

            if key is not None and key == quantity:
                return True

        return False

    def __getitem__(self, key):
        if key in list(self.keys()):
            return super().__getitem__(key)
        else:
            if hasattr(self, 'adaptor'):
                data = self.adaptor.data
            else:
                data = self.data
            try:
                value = self.definitions(key, self.data)
            except Exception as _excp:
                printe('Error in the definition of ' + key)
                raise
            value = np.atleast_1d(value)
            super().__setitem__(key, value)
            return value

    def list(self):
        if not len(self['__quantities__']):

            if hasattr(self, 'adaptor'):
                self.adaptor.list()
                self['__quantities__'].update(self.adaptor['__quantities__'])

            self.definitions(None, self.data)

        return list(self['__quantities__'].keys())

    def get_all(self):
        for item in self['__quantities__']:
            self[item]


class OMFITinterface(OMFITinterfaceAdaptor):
    """
    :param data: input data to be read by the adaptor

    :param adaptor: adaptor class to be used

    :param adaptorsFile: adaptor class to be used (defaults to 'OMFIT-source/omfit/adaptors.py')

    :param t: t at which to return data

    :param r: r at which to return data

    :param squeeze: string with dimensions ('r','t','rt') to squeeze if length is one

    :param checkAdaptors: check adaptors for inconsistencies (only if adaptor keyword is not passed)
    """

    def __init__(self, data=None, adaptor=None, adaptorsFile=None, t=None, r=None, squeeze='', interp='linear', checkAdaptors=True):

        if adaptor is None:
            namespace = self.getAdaptors(adaptorsFile)
            excp_s = ''
            for k in namespace:
                try:
                    if namespace[k].identify(data):
                        adaptor = namespace[k]
                        break
                except Exception as _excp:
                    excp_s += '\nadaptor ' + k + ': ' + repr(_excp)

            if adaptor is None:
                printe('OMFITinterface could not associate the data to an adaptor' + excp_s)
                adaptor = OMFITinterfaceAdaptor

            if checkAdaptors:
                self.checkInterfaceAdaptors(namespace, quiet_if_ok=True)

        elif not adaptor.identify(data):
            printe('data is not valid for adaptor ' + adaptor.type)
            adaptor = OMFITinterfaceAdaptor

        self.adaptor = adaptor(data)
        OMFITinterfaceAdaptor.__init__(self)
        self.t = t
        self.r = r
        self.squeeze = squeeze
        self.interp = interp

    @staticmethod
    def getAdaptors(adaptorsFile=None):
        namespace = {}
        if adaptorsFile is None:
            adaptorsFile = OMFITsrc + os.sep + 'omfit_classes' + os.sep + 'adaptors.py'
        elif hasattr(adaptorsFile, 'filename'):
            adaptorsFile = adaptorsFile.filename
        with open(adaptorsFile, 'r') as f:
            exec(f.read(), globals(), namespace)
        return namespace

    @property
    def type(self):
        if self.adaptor is None:
            return ''
        return self.adaptor.type

    def definitions(self, key, data):
        if key in self.adaptor.list():
            return self.adaptor[key]

        if self.register(key, 'me', 'Electron mass', 'C', ''):
            return 9.10938291e-31

        if self.register(key, 'mH', 'Hydrogen mass', 'kg', ''):
            return 1.6726e-27

        if self.register(key, 'mD', 'Deuteron mass', 'kg', ''):
            return 2 * 1.6726e-27

        if self.register(key, 'mT', 'Tritium mass', 'kg', ''):
            return 3 * 1.6726e-27

        if self.register(key, 'mHe', 'Helium mass', 'kg', ''):
            return 4 * 1.6726e-27

        if self.register(key, 'mC', 'Carbon mass', 'kg', ''):
            return 12 * 1.6726e-27

        if self.register(key, 'e', 'Electron charge (positive)', 'C', ''):
            return 1.60217646e-19

        if self.register(key, 'eV', 'eV', 'J', ''):
            return 1.60217646e-19

        if self.register(key, 'keV -> ', 'keV', 'J', ''):
            return 1.60217646e-16

        if self.register(key, 'c', 'Light speed', 'm/s', ''):
            return 299792458.0

    def get(self, item, dim, t=None, r=None, interp=None, squeeze=None):
        if t is None:
            t = self.t
        if r is None:
            r = self.r
        if squeeze is None:
            squeeze = self.squeeze
        if interp is None:
            interp = self.interp

        items = np.atleast_1d(item)
        dims = np.atleast_1d(dim)

        tmp = []
        for item in items:
            for dim in dims:
                tmp.append(self._get(item, dim, t, r, interp, squeeze))

        if len(items) == 1 and len(dims) == 1:
            return tmp[0]
        else:
            return np.squeeze(np.reshape(tmp, (len(items), len(dims))))

    def _get(self, item, dim, t, r, interp, squeeze=None):
        if item not in self['__quantities__']:
            raise OMFITinterfaceError('\'' + item + '\' is not available, did you mean ' + repr(bestChoice(self.list(), item)[0]) + ' ?')

        if dim in ['desc', 'description']:
            return self['__quantities__'][item]['description']

        elif dim in ['unit', 'units']:
            return self['__quantities__'][item]['units']

        elif dim in ['dim', 'raw_dimension']:
            return self['__quantities__'][item]['units']

        if dim not in self.allowedDimensions:
            raise OMFITinterfaceError(item + ': Dimension \'' + dim + '\' is not allowed, use: ' + repr(self.allowedDimensions))

        raw_dim = self['__quantities__'][item]['raw_dimension']

        # stop if dimension requested is smaller than raw data
        if len(raw_dim.strip(dim)):
            raise OMFITinterfaceError('You are asking for `' + item + '` in ' + dim + ', but it is defined in ' + raw_dim)

        tmp = self[item]

        # do not attempt anything if it's a string
        if isinstance(tmp[0], str):
            return tmp

        # tiling
        missing = re.sub('[ ' + raw_dim + ']', '', dim)
        # print('was:'+raw_dim,'asked:'+dim,'missing:'+missing)
        tmp_dim = raw_dim
        tl = []
        for k in missing[::-1]:
            tmp_dim = k + tmp_dim
        for k in missing:
            if k in self['__dimensions__']:
                tl.append(self['__dimensions__'][k])
            else:
                tl.append(1)
        tl.extend([1] * len(tmp.shape))
        tmp = np.tile(tmp, tl)

        # reordering
        tmp_dim = list(tmp_dim)
        for step in range(len(tmp_dim)):
            order = {}
            for k, s in enumerate(tmp_dim):
                if dim[k] != s:
                    order[s] = (k, dim.index(s))
            if not len(order):
                break
            # print(order)
            swap = order[list(order.keys())[0]]
            tmp = np.swapaxes(tmp, swap[0], swap[1])
            tt = tmp_dim[swap[0]]
            tmp_dim[swap[0]] = tmp_dim[swap[1]]
            tmp_dim[swap[1]] = tt

        # ==============
        # after this point the object has the dimensionality which was requested by the user
        # ==============
        for k in self['__dimensions__']:
            if k not in dim and eval(k) is not None:
                raise OMFITinterfaceError(
                    item + ': Cannot return data at specific `' + k + '`, with dimension `' + dim + '` wich is not `' + k + '` dependent'
                )

        # interpolation by user request
        # make sure to keep shape even when interpolating at one point
        mp = {'t': 'time', 'r': 'rho'}
        for k, d in enumerate(dim):
            if d in mp and eval(d) is not None:
                sh = list(tmp.shape)
                if tmp.shape[k] > 1:
                    sh[k] = len(np.atleast_1d(eval(d)))
                    tmp = interp1e(self[mp[d]], tmp, axis=k, kind=interp)(eval(d))
                    tmp = np.reshape(tmp, sh)

        # squeeze dimensions
        sh = []
        for k, d in enumerate(dim):
            if (squeeze is True or d in squeeze) and tmp.shape[k] == 1:
                continue
            sh.append(tmp.shape[k])
        if len(sh):
            tmp = np.reshape(tmp, sh)
        else:
            tmp = np.reshape(tmp, (1,))[0]

        return tmp

    @staticmethod
    def checkInterfaceAdaptors(namespace=None, checkList=['units', 'description'], quiet_if_ok=True):
        if namespace is None:
            namespace = OMFITinterface.getAdaptors()

        adaptorInstances = {}
        q_master = {}
        for k1 in list(namespace.keys()):
            k = namespace[k1].type
            adaptorInstances[k] = namespace[k1]()
            quantities = adaptorInstances[k]['__quantities__']
            for q in quantities:
                q_master.setdefault(q, []).append((k, quantities[q]))

        anyIssue = False
        for q in q_master:
            adaptors = []
            prop = {}
            for adpt in q_master[q]:
                adaptors.append(adpt[0])
                for p in checkList:
                    prop.setdefault(p, []).append(adpt[1][p])
            for p in checkList:
                if len(set(prop[p])) > 1:
                    anyIssue += 1
                    printe('\n\n' + q + ' ' + ':')
                    for k, a in enumerate(adaptors):
                        printe(' * ' + a + '\t\t\t-->\t' + prop[p][k])
        if anyIssue:
            printe('\n' + str(anyIssue) + ' adaptors inconsistencies were detected!')
        elif not quiet_if_ok:
            printi('All adaptors definitions are consistent: ' + str(list(adaptorInstances.keys())))


def interface(data, *args, **kw):
    if data is None or (np.iterable(data) and not len(data)):
        return None
    tmp = OMFITinterface(data, *args, **kw)
    if len(tmp.type):
        return tmp
