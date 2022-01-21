import tkinter as tk

from . import tktool

from . import guidata

from . import gui_xtal_layer

from . import layoutmode
from . import balloonhelp


class Xtal(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        # QUIT | NEWS | UNIT | BASE

        # quit
        self.quitlabel = tk.Label(self, text='QUIT:')
        self.quitoptions = [
            (False, 'F: run normaly'),
            (True, 'T: terminates immediately after reporting on the target crystal')]
        self.quit = tktool.codedoptionmenu.CodedOptionMenu(self, self.quitoptions)
        self.quit.config(width=10, anchor='w')

        # news
        self.newslabel = tk.Label(self, text='NEWS:')
        self.newsoptions = [
            (1, '1: Input data, crystal densities, and brief notes ...'),
            (2, '2: Adds the interatomic separations and the neighbor lists ...'),
            (3, '3: Adds the transformation matrices relating the internal orthogonal coordinate system ...'),
            (4, '4: Adds a complete description of the crystallite ...')]
        self.news = tktool.codedoptionmenu.CodedOptionMenu(self, self.newsoptions)
        self.news.config(width=10, anchor='w')

        # unit
        self.unitlabel = tk.Label(self, text='UNIT:')
        self.unitoptions = [
            (-1, '-1: refer BASE value in &MODL.METRIC unit'),
            (0, '0: in &MODL.METRIC unit'),
            (1, '1: use lattice edge a'),
            (2, '2: use lattice edge b'),
            (3, '3: use lattice edge c')]
        self.unit = tktool.codedoptionmenu.CodedOptionMenu(self, self.unitoptions)
        self.unit.config(width=10, anchor='w')
        self.unitmsg = 'Selection of Computational Unit Length (UNIT)'

        # base
        self.baselabel = tk.Label(self, text='BASE:')
        self.base = tktool.validateentry.Double(self)
        self.base.config(width=10)
        self.basemsg = 'Base Length Value (BASE)'

        # xtal_layer
        self.layerfrm = tk.LabelFrame(self, text='LAYER')
        self.layer = gui_xtal_layer.XtalLayer(self.layerfrm)

        self.layout()

        self.clear()

    def layout(self, mode=0):
        prow = 0
        pcol = 0
        # QUIT | NEWS | UNIT | BASE
        if mode == 0:
            # quit
            self.quitlabel.grid(row=prow, column=pcol, sticky=tk.W)
            self.quit.grid(row=prow+1, column=pcol, sticky=tk.EW)
            pcol += 1
            # news
            self.newslabel.grid(row=prow, column=1, sticky=tk.W)
            self.news.grid(row=prow+1, column=1, sticky=tk.EW)
            pcol += 1
        else:
            self.quitlabel.grid_forget()
            self.quit.grid_forget()
            self.newslabel.grid_forget()
            self.news.grid_forget()

        self.unitlabel.grid(row=prow, column=pcol, sticky=tk.W)
        self.unit.grid(row=prow+1, column=pcol, sticky=tk.EW)
        pcol += 1
        self.baselabel.grid(row=prow, column=pcol, sticky=tk.W)
        self.base.grid(row=prow+1, column=pcol, sticky=tk.EW)
        pcol += 1

        prow += 2

        self._layout_xtal_layer(mode)

        self.layerfrm.grid(row=prow, column=0, columnspan=pcol)
        prow += 1

    def _layout_xtal_layer(self, mode=0):
        self.layer.pack()

    def bind_with_balloonhelp(self, b):
        b.bind(self.unit, balloonHelp=self.unitmsg)
        b.bind(self.base, balloonHelp=self.basemsg)
        self.layer.bind_with_balloonhelp(b)

    def set(self, v):
        self.quit.set(v.get('quit', guidata.xtal_default['quit']))
        self.news.set(v.get('news', guidata.xtal_default['news']))
        self.unit.set(v.get('unit', guidata.xtal_default['unit']))
        self.base.set(v.get('base', guidata.xtal_default['base']))
        self.layer.set(v.get('layer', guidata.xtal_default['layer']))

    def get(self):
        d = {}
        d['quit'] = self.quit.get()
        d['news'] = self.news.get()
        d['unit'] = self.unit.get()
        d['base'] = self.base.get()
        d['layer'] = self.layer.get()

        return d

    def clear(self):
        self.set(guidata.xtal_default)

    def validate(self):
        err = []
        for n, w in [('base', self.base)]:
            e = w.validate()
            if e:
                err.append((n, e))
        return err if err else None
