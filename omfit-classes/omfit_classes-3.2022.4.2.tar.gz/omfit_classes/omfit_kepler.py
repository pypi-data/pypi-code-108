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

__all__ = ['OMFITkeplerParams']


class OMFITkeplerParams(SortedDict, OMFITascii):
    r"""
    OMFIT class used to interface with kepler input files

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
            if '=' not in line:
                continue
            key, value = line.split('=')
            key = key.strip()
            value = value.strip()
            if value == 'false':
                value = False
            elif value == 'true':
                value = True
            elif value == 'none':
                value = None
            else:
                try:
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    if '\\,' in value:
                        value = list(map(lambda x: ast.literal_eval(x.strip()), value.split('\\,')))
                    else:
                        value = re.sub(r'\\', '', value)
            key = re.sub(r'\\', '', key)
            h = self
            for k in key.split('.')[:-1]:
                if k not in h:
                    h[k] = SortedDict()
                h = h[k]
            h[key.split('.')[-1]] = value

    @dynaSave
    def save(self):
        def escape(inv):
            if isinstance(inv, list):
                return '\\,'.join(map(str, inv))
            elif inv in [True, False, None]:
                return str(inv).lower()
            elif not isinstance(inv, str):
                return inv
            return re.sub('([ ,])', r'\\\1', inv)

        with open(self.filename, 'w') as f:
            for key in traverse(self, onlyLeaf=True):
                value = eval('self' + key)
                key = '.'.join(parseLocation(key))[1:]
                f.write('%s = %s\n' % (escape(key), escape(value)))


############################################
if '__main__' == __name__:
    test_classes_main_header()

    tmp = OMFITkeplerParams(OMFITsrc + '/../samples/kepler_input_sample.txt')
    tmp.load()
    tmp.saveas(os.getcwd() + 'kepler_input_sample.txt')
