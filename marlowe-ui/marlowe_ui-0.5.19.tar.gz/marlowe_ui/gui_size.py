import tkinter as tk

from . import guidata
from . import gui_size_body
from . import layoutmode
from . import balloonhelp


class Size(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        # validate, invalidate check
        self.validvar = tk.IntVar(self)
        self.valid = tk.Checkbutton(
            self, text='Config &SIZE (&MODL.RDNML(3))',
            variable=self.validvar,
            command=self.valid_action)

        # body
        self.size_body = gui_size_body.SizeBody(self)

        self.clear()
        self.layout()

    def layout(self, mode=0):
        prow = 0
        self.valid.grid(row=prow, column=0, sticky=tk.W)
        prow += 1
        self.size_body.grid(row=prow, column=0)

        self.size_body.layout(mode)

    def bind_with_balloonhelp(self, b):
        self.size_body.bind_with_balloonhelp(b)

    def valid_action(self):
        if self.validvar.get():
            self.size_body.enable()
        else:
            self.size_body.disable()

    def set(self, d):
        if d is None:
            self.size_body.clear()
            self.size_body.disable()
            self.validvar.set(0)
        else:
            self.validvar.set(1)
            self.size_body.enable()
            self.size_body.set(d)

    def get(self):
        if self.validvar.get():
            return self.size_body.get()
        return None

    def clear(self):
        self.set(guidata.size_default)

    def validate(self):
        if self.validvar.get():
            return self.size_body.validate()
        return None

    def enable(self):
        self.valid.config(state=tk.NORMAL)
        if self.validvar.get():
            self.size_body.enable()
        else:
            self.size_body.disable()

    def disable(self):
        self.size_body.disable()
        self.valid.config(state=tk.DISABLED)
