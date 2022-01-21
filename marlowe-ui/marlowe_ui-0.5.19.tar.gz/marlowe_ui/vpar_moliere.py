import tkinter as tk

import itertools
import copy

from . import scon
from . import tktool
from .tktool import validateentry

import logging
logger = logging.getLogger(__name__)

param_default = {
        # (i,j):value, i<=j, i,j=1,2,...,scon.kind
        'BPAR':dict([(c,0.0) for c in itertools.combinations_with_replacement(list(range(1,1+scon.kind)),2)])
        }

param_example = {
        'BPAR':{
            (2, 3):0.05,
            (1, 2):0.01
            }
        }

# param['BPAR'] contains tuple key, so
# this should be tranlated for json output
def param_to_json(native_param):
    """translate native parameter to json assecptable form"""
    d = copy.deepcopy(native_param)
    if 'BPAR' in d:
        d['BPAR'] = [dict(i=i, j=j, value=v) for (i, j), v in sorted(d['BPAR'].items())]
    return d

def param_from_json(json_param):
    """translate json acceptable data to native form"""
    d = copy.deepcopy(json_param)
    if 'BPAR' in d:
        d['BPAR'] = dict([((e['i'], e['j']), e['value']) for e in d['BPAR']])
    return d

class VparMoliere(tk.Frame):
    """ edit VPAR record, up to 5x5 triangle matrics """

    def __init__(self, master,
                entry_config={'justify':tk.RIGHT, 'width':10}):
        tk.Frame.__init__(self, master)

        self.state = tk.NORMAL # or tk.DISABLED

        self.validkinds = scon.kind

        lframe = tk.LabelFrame(self, text='BPAR')
        lframe.pack(expand=True, fill=tk.BOTH)
        
        columnheaders = ['type'] + [str(i+1) for i in range(scon.kind)]
        rowheaders = [str(i+1) for i in range(scon.kind)]

        for c, txt in enumerate(columnheaders):
            tk.Label(lframe, text=txt).grid(row=0, column=c, sticky=tk.NSEW)
        for r, txt in enumerate(rowheaders):
            tk.Label(lframe, text=txt).grid(row=r+1, column=0, sticky=tk.NSEW)

        # {(i, j):DoubleNoNegative} (i, j is 1-based index).
        self.entries = {}

        for r in range(scon.kind):
            for c in range(scon.kind):
                if c >= r:
                    e = tktool.validateentry.DoubleNoNegative(lframe)
                    e.config(**entry_config)
                    e.grid(row=r+1, column=c+1, sticky=tk.NSEW)
                    self.entries[(r+1, c+1)] = e

        self.clear()

    def set(self, d):
        bpar = d.get('BPAR', param_default['BPAR'])
        for ij, w in self.entries.items():
            w.set(bpar.get(ij, 0.0))
        self.set_validkinds(scon.kind)

    def clear(self):
        self.set(param_default)

    def set_validkinds(self, k):
        self.validkinds = k
        if not self.is_disabled():
            # reset entry stats
            self.enable()

    def enable(self):
        for (i, j), w in self.entries.items():
            if i <= self.validkinds and j <= self.validkinds:
                w.config(state=tk.NORMAL)
            else:
                w.config(state=tk.DISABLED)
        self.state=tk.NORMAL

    def disable(self):
        for e in self.entries.values():
            e.config(state=tk.DISABLED)
        self.state=tk.DISABLED

    def is_disabled(self):
        return self.state == tk.DISABLED

    def validate(self):
        err = []
        for ij, w in self.entries.items():
            e = w.validate()
            if e:
                err.append(str(ij)+':'+e)
        return err if err else None

    def get(self):
        values = {'BPAR':{}}
        for ij, w in self.entries.items():
            if not w.is_disabled():
                values['BPAR'][ij] = w.get()
        return values

    def get_nostatechk(self):
        return {'BPAR':dict([(ij, w.get_nostatechk()) for ij, w in self.entries.items()])}
