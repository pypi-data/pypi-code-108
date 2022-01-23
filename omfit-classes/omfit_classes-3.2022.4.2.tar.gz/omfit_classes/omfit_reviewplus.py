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

__all__ = ['OMFITreviewplus']


class OMFITreviewplus(SortedDict, OMFITascii):
    def __init__(self, filename='', **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):

        with open(self.filename, 'r') as f:
            lines = f.readlines()
        self['data'] = data = {}
        self['style'] = style = {}
        k = -1
        kst = -1
        mode = 'data'
        for line in lines[4:]:
            # ================
            if mode == 'data' and line.startswith('----'):
                k = -1
                mode = 'style'
                continue
            # ----------------
            if line.strip() == '53':
                mode = 'data'
                k += 1
                continue
            # ----------------
            if line.strip() == '66':
                kst += 1
                mode = 'style'
                continue
            # ================
            if mode == 'style':
                if kst not in style:
                    style[kst] = {}
                d = line.split('=')
                key = d[0]
                value = '='.join(d[1:]).strip()
                try:
                    style[kst][key] = eval(value)
                except Exception:
                    pass
                    # print key,value
            # ----------------
            if mode == 'data':
                if line.startswith('YEXP'):
                    k += 1
                if k not in data:
                    data[k] = {}
                data[k]['__style__'] = kst
                d = line.split('=')
                key = d[0]
                value = '='.join(d[1:]).strip()
                try:
                    data[k][key] = eval(value)
                except Exception:
                    pass
                    # print key,value
