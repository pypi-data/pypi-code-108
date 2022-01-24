import os
from pandas import DataFrame
from parse import parse
from itertools import chain
import glob

class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class Ampule:
    def __init__(self, py_path, dep_path, pdf_path):
        self.py_path = py_path.replace(' ', '\ ')
        self.dep_path = dep_path.replace(' ', '\ ')
        self.pdf_path = pdf_path.replace(' ', '\ ')
        self.dat_paths = set()

    def load(self, parser, path):
        self.dat_paths.update([path.replace(' ', '\ ')])
        return parser(path)

    def save(self, save_func, path, **kwargs):
        filename = f'{self.pdf_path}/{path}'
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        if kwargs.pop('repr_plot', True):
            kwargs.setdefault('metadata', {}).update({'CreationDate': None})

        save_func(filename, **kwargs)

    def flush_deps(self):
        with open(self.dep_path, 'w') as deps:
            print(self.pdf_path + ":", self.py_path, end = ' ', file = deps)
            dat_paths = sorted(list(self.dat_paths))
            for dat_path in dat_paths:
                print(dat_path, end = ' ', file = deps)
            print(file = deps)
            print(file = deps)
            for dat_path in dat_paths:
                print(dat_path + ":", file = deps)
                print(file = deps)

def search_mask(pref, suff = None, cls = int, key_ordering = lambda x: x):
    if not suff:
        mask = pref + '*'
        sl = slice(len(pref), None)
    else:
        mask = pref + '*' + suff
        sl = slice(len(pref), -len(suff))
    return sorted(((p, cls(p[sl])) for p in glob.glob(mask)), key = lambda x: key_ordering(x[1]))

def dat_parser(path):
    with open(path) as f:
        meta = AttrDict()
        while True:
            hline = f.readline()
            if not hline.startswith('#:'):
                break
            p = parse("{}={}", hline[2:])
            if p:
                name, val = p
                meta[name] = eval(val)
            else:
                names = hline[2:].split()
        raw_columns = zip(*(map(float, line.split()) for line in chain([hline], f)))
        return DataFrame({name: col for name, col in zip(names, raw_columns)}), meta
