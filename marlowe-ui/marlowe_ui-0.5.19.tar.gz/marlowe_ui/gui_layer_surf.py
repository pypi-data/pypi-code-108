import tkinter as tk

from . import guidata
from . import layoutmode
from . import balloonhelp
from . import tktool
from .tktool import gui_abstract


class LayerSurfOption(tk.Frame,
                      tktool.gui_abstract.GUIAbstract,
                      layoutmode.LayoutModeImplement,
                      balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)
        gui_abstract.GUIAbstract.__init__(
            self, defaultparam=guidata.layer_surfopt_default)

        # depth
        self.depthlabel = tk.Label(self, text='DEPTH')
        self.depth = tktool.validateentry.Double(self)
        self.depth.config(width=10)
        self.depthballoonhelp = '''\
The thickness in units of BASE, one value for each layer. (DEPTH)'''
        self.add_widget('depth', self.depth)

        # origin
        self.originlabel = tk.Label(self, text='ORIGIN')
        self.origin = tktool.validateentry.Vec3d(self)
        self.origin.config(width=10)
        self.originballoonhelp = '''\
Origin of lattice in BASE unit (ORIGIN)'''
        self.add_widget('origin', self.origin)

        # lo
        self.lolabel = tk.Label(self, text='LO')
        self.lo = tktool.validateentry.IntPositive(self)
        self.lo.config(width=10)
        self.loballoonhelp = '''\
The site index number which is assigned at the ORIGIN. (LO)'''
        self.add_widget('lo', self.lo)

        self.layout()

    def layout(self, mode=0):
        prow = 0
        self.depthlabel.grid(row=prow, column=0, sticky=tk.E)
        self.depth.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.lolabel.grid(row=prow, column=0, sticky=tk.E)
        self.lo.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.originlabel.grid(row=prow, column=0, sticky=tk.E)
        self.origin.grid(row=prow, column=1, sticky=tk.W)

    def bind_with_balloonhelp(self, b):
        b.bind(self.depth, balloonHelp=self.depthballoonhelp)
        b.bind(self.origin, balloonHelp=self.originballoonhelp)
        b.bind(self.lo, balloonHelp=self.loballoonhelp)
