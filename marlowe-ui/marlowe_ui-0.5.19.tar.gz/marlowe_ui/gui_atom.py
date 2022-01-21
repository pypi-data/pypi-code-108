import tkinter as tk

from . import tktool

from . import gui_atomtbl
from . import guidata
from . import layoutmode
from . import balloonhelp


class Atom(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        self.tblfrm = tk.LabelFrame(self, text='TYPES')
        self.atomtbl = gui_atomtbl.AtomTbl(self.tblfrm)

        self.loxlabel = tk.Label(self, text='LOX:')
        self.loxoptions = [
            (0, '0:EBND(1) is const.'),
            (1, '1:EBND(1) to EBND(2)'),
            (2, '2:LOX=1 + neighbor effect')]
        self.lox = tktool.codedoptionmenu.CodedOptionMenu(self, self.loxoptions)
        self.lox.config(width=20, anchor='w')

        # EBND (and DIST) is moved to gui_site_elem

        self.lbndoptions = [
            (0, '0: Only undisturbed'),
            (1, '1: (Proper) focuson members)'),
            (2, '2: Proper replacements'),
            (3, '3: Proper close pairs')]
        self.lbndlabel = tk.Label(self, text='LBND:')
        self.lbnd = tktool.codedoptionmenu.CodedOptionMenu(self, self.lbndoptions)
        self.lbnd.config(width=20, anchor='w')

        self.clear()

        self.layout()

    def layout(self, mode=0):
        prow = 0
        self._layout_tblfrm(mode)
        self.tblfrm.grid(row=prow, column=0, columnspan=2)
        prow += 1

        if mode == 0:
            self.loxlabel.grid(row=prow, column=0, sticky=tk.E)
            self.lox.grid(row=prow, column=1, sticky=tk.W)
            prow += 1
        else:
            self.loxlabel.grid_forget()
            self.lox.grid_forget()

        if mode == 0:
            self.lbndlabel.grid(row=prow, column=0, sticky=tk.E)
            self.lbnd.grid(row=prow, column=1, sticky=tk.W)
            prow += 1
        else:
            self.lbndlabel.grid_forget()
            self.lbnd.grid_forget()

    def bind_with_balloonhelp(self, b):
        self.atomtbl.bind_with_balloonhelp(b)

    def _layout_tblfrm(self, mode=0):
        self.atomtbl.layout(mode)
        self.atomtbl.pack()

    def set(self, v):
        self.atomtbl.set(v.get('atomtbl', guidata.atom_default['atomtbl']))
        self.lox.set(v.get('lox', guidata.atom_default['lox']))
        self.lbnd.set(v.get('lbnd', guidata.atom_default['lbnd']))

    def get(self):
        d = {}
        d['atomtbl'] = self.atomtbl.get()
        d['lox'] = self.lox.get()
        d['lbnd'] = self.lbnd.get()

        return d

    def clear(self):
        self.set(guidata.atom_default)

    def validate(self):
        err = []
        for n, w in [('atomtbl', self.atomtbl)]:
            e = w.validate()
            if e:
                err.append((n, e))
        return err if err else None
