#
# UI for XTAL.AXISA, AXIXB

import tkinter as tk

from . import layoutmode
from . import balloonhelp

from .tktool import optionframe
from .tktool import validateentry

param_default = None
param_example = {
    'axisa': [1.0, 0.0, 0.0],
    'axisb': [0.0, 1.0, 0.0]
}


# axis A and B is optional
class Axis(optionframe.OptionFrame,
           layoutmode.LayoutModeImplement,
           balloonhelp.BalloonHelpImplement):
    def __init__(self, parent=None):
        optionframe.OptionFrame.__init__(self, parent, title='AXIS')
        self.disabled = False

    def layoutlabel(self):
        self.checkbutton.config(anchor=tk.E)
        self.config(labelanchor=tk.W)

    def body(self):
        self.axisalabel = tk.Label(self, text='A')
        self.axisa = validateentry.Vec3d(self)
        self.axisaballoonhelp = '''\
The direction of an axis in the target surface. The layer is
oriented with AXISA along the positive x-axis of the internal
coordinate system. (AXISA)'''

        self.axisa.config(width=10)
        self.axisblabel = tk.Label(self, text='B')
        self.axisb = validateentry.Vec3d(self)
        self.axisb.config(width=10)
        self.axisbballoonhelp = '''\
The direction of another axis in the target surface. It need
not be orthogonal to AXISA but must be a distinct vector. (AXISB)'''

        self.layout()

    def layout(self, mode=0):
        self.axisalabel.grid(row=0, column=0, sticky=tk.NE)
        self.axisa.grid(row=0, column=1, sticky=tk.NW)
        self.axisblabel.grid(row=1, column=0, sticky=tk.SE)
        self.axisb.grid(row=1, column=1, sticky=tk.SW)
        self.grid_columnconfigure(1, weight=1)

    def bind_with_balloonhelp(self, b):
        for v in self.axisa.array:
            b.bind(v, balloonHelp=self.axisaballoonhelp)
        for v in self.axisb.array:
            b.bind(v, balloonHelp=self.axisbballoonhelp)

    def set_checkbutton(self, val):
        self.checkvar.set(val)
        if val:
            self.axisa.enable()
            self.axisb.enable()
        else:
            self.axisa.disable()
            self.axisb.disable()

    def get(self):
        if not self.disabled and self.checkvar.get():
            return {'axisa': self.axisa.get(),
                    'axisb': self.axisb.get()}
        return None

    def set(self, d):
        # disabled is default
        self.set_checkbutton(False)
        if d is None:
            return
        if 'axisa' in d:
            self.set_checkbutton(True)
            self.axisa.set(d['axisa'])
        if 'axisb' in d:
            self.set_checkbutton(True)
            self.axisb.set(d['axisb'])

    def clear(self):
        self.set(param_default)

    def validate(self):
        err = []
        if (not self.is_disabled()) and self.checkvar.get():
            # validate
            for n, w in [('axisa', self.axisa), ('axisb', self.axisb)]:
                e = w.validate()
                if e:
                    err.append((n, e))
        return err if err else None

    def enable(self):
        self.disabled = False
        self.checkbutton.config(state=tk.NORMAL)
        self.set_checkbutton(self.checkvar.get())

    def disable(self):
        self.disabled = True
        self.checkbutton.config(state=tk.DISABLED)
        self.axisa.disable()
        self.axisb.disable()

    def is_disabled(self):
        return self.disabled
