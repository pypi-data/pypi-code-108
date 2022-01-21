# coding: utf-8
""" root gui
"""

import tkinter as tk
import tkinter.ttk

from . import guidata

from . import gui_modl
from . import gui_atom
from . import gui_xtal
from . import gui_surf
from . import gui_size
from . import gui_outp
from . import gui_proj
from . import vpar

from . import layoutmode
from . import balloonhelp

from .tktool import truncatedentry


class Root(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # comment
        self.comment1label = tk.Label(self, text='comment1:')
        self.comment1 = truncatedentry.TruncatedEntry(self, limitwidth=80, width=81)

        self.comment2label = tk.Label(self, text='comment2:')
        self.comment2 = truncatedentry.TruncatedEntry(self, limitwidth=80, width=81)

        # frame including other records
        #
        # r0: &ATOM | &XTL | MISC.
        #     ------+      |
        # r1: &VPAR |      |

        self.frame2 = tk.Frame(self)

        # atom
        self.atomframe = tk.LabelFrame(self.frame2, text='&ATOM')
        self.atom = gui_atom.Atom(self.atomframe)

        # vpar
        self.vparframe = tk.LabelFrame(
            self.frame2,
            labelwidget=tk.Label(
                self.frame2, text='&VPAR\n(Inter-atomic Potential)', justify=tk.LEFT))
        self.vpar = vpar.Vpar(self.vparframe)
        self.vparballoonhelp = '''\
Supplies the data for the interatomic potential.'''

        # xtal
        self.xtalframe = tk.LabelFrame(self.frame2, text='&XTAL')
        self.xtal = gui_xtal.Xtal(self.xtalframe)

        # tab-switched frames
        self.tab = tkinter.ttk.Notebook(self.frame2)
        self.tabfirst = True

        # proj
        self.proj = gui_proj.Proj(self.tab)

        # surf
        self.surf = gui_surf.Surf(self.tab, root=self)

        # modl
        self.modl = gui_modl.Modl(self.tab)

        # outp
        self.outp = gui_outp.Outp(self.tab)

        # size
        self.size = gui_size.Size(self.tab)

        # make inter-gui messaging
        self.surf.link_xtallayerelem(self.xtal.layer.view)

        # set default value
        self.clear()

        # layout all widgets
        self.layout()

    def layout(self, mode=0):
        # count up current row
        prow = 0

        self.comment1label.grid(row=prow, column=0, sticky=tk.E)
        self.comment1.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        self.comment2label.grid(row=prow, column=0, sticky=tk.E)
        self.comment2.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        self._layout_frame2(mode)

        self.frame2.grid(row=prow, column=0, columnspan=2)

    def _layout_frame2(self, mode=0):
        # frame including other records
        #
        # r0: &ATOM | &XTL | MISC.
        #     ------+      |
        # r1: &VPAR |      |

        # within self.frame2
        self._layout_atomframe(mode)
        self.atomframe.grid(row=0, column=0, sticky=tk.N+tk.EW)

        self._layout_vparframe(mode)
        if mode == 0:
            self.vparframe.grid(row=1, column=0, sticky=tk.NSEW)
        else:
            self.vparframe.grid_forget()

        self.frame2.grid_rowconfigure(1, weight=1)

        self._layout_xtalframe(mode)
        self.xtalframe.grid(row=0, column=1, rowspan=2, sticky=tk.N+tk.W)

        self._layout_tab(mode)
        self.tab.grid(row=0, column=2, rowspan=2, sticky=tk.N+tk.W)

    def _layout_atomframe(self, mode=0):
        self.atom.layout(mode)
        self.atom.pack(fill=tk.BOTH, expand=False)

    def _layout_vparframe(self, mode=0):
        self.vpar.pack(fill=tk.BOTH, expand=True)

    def _layout_xtalframe(self, mode=0):
        self.xtal.layout(mode)
        self.xtal.pack(fill=tk.BOTH, expand=True)

    def _layout_tab(self, mode=0):
        self.proj.layout(mode)
        self.surf.layout(mode)
        self.modl.layout(mode)
        self.outp.layout(mode)
        self.size.layout(mode)
        if self.tabfirst:
            self.tab.add(self.proj, text='&PROJ')
            self.tab.add(self.surf, text='&SURF')
            self.tab.add(self.modl, text='&MODL')
            self.tab.add(self.outp, text='&OUTP')
            self.tab.add(self.size, text='&SIZE')
            self.tabfirst = False
        else:
            self.tab.add(self.proj)
            self.tab.add(self.surf)
            self.tab.add(self.modl)
            self.tab.add(self.outp)
            if mode == 0:
                self.tab.add(self.size)
            else:
                self.tab.hide(self.size)

    def bind_with_balloonhelp(self, b):
        # comments
        msgcom1 = 'Job Identification Record coomment 1'
        msgcom2 = 'Job Identification Record coomment 2'

        b.bind(self.comment1, balloonHelp=msgcom1)
        b.bind(self.comment2, balloonHelp=msgcom2)

        self.atom.bind_with_balloonhelp(b)
        self.xtal.bind_with_balloonhelp(b)
        self.proj.bind_with_balloonhelp(b)
        self.surf.bind_with_balloonhelp(b)
        self.modl.bind_with_balloonhelp(b)
        self.outp.bind_with_balloonhelp(b)
        self.size.bind_with_balloonhelp(b)

        b.bind(self.vpar, balloonHelp=self.vparballoonhelp)

    def set(self, v):
        """set data to gui
        """
        self.comment1.set(v.get('comment1', guidata.root_default['comment1']))
        self.comment2.set(v.get('comment2', guidata.root_default['comment2']))
        self.modl.set(v.get('modl', guidata.root_default['modl']))
        self.atom.set(v.get('atom', guidata.root_default['atom']))
        self.xtal.set(v.get('xtal', guidata.root_default['xtal']))
        self.surf.set(v.get('surf', guidata.root_default['surf']))
        self.size.set(v.get('size', guidata.root_default['size']))
        self.outp.set(v.get('outp', guidata.root_default['outp']))
        self.proj.set(v.get('proj', guidata.root_default['proj']))
        self.vpar.set(v.get('vpar', guidata.root_default['vpar']))

    def get(self):
        """return the context of gui in Data structure
        befor get(). validation is recommended
        retrun value is compatible to the argument for viewparam.ViewParam.map_load
        """
        d = {}
        # commen record
        d['comment1'] = self.comment1.get()
        d['comment2'] = self.comment2.get()

        # modl record
        d['modl'] = self.modl.get()

        # atom record
        d['atom'] = self.atom.get()

        # xtal
        d['xtal'] = self.xtal.get()

        # surf
        d['surf'] = self.surf.get()

        # size
        d['size'] = self.size.get()

        # outp
        d['outp'] = self.outp.get()

        # proj
        d['proj'] = self.proj.get()

        # vpar
        d['vpar'] = self.vpar.get()

        return d

    def clear(self):
        self.set(guidata.root_default)

    def validate(self):
        """validate control value
        return: tuple of (result, reason)
            result: True | False
            reason: structured data to descrive error reason (default is None)
        """
        # comment1 and 2 are automatially truncated in 80 chars

        errordata = {}

        # modl
        errordata['modl'] = self.modl.validate()

        # atom
        errordata['atom'] = self.atom.validate()

        # xtal
        errordata['xtal'] = self.xtal.validate()

        # surf
        errordata['surf'] = self.surf.validate()

        # size
        errordata['size'] = self.size.validate()

        # outp
        errordata['outp'] = self.outp.validate()

        # proj
        errordata['proj'] = self.proj.validate()

        # vpar
        # validate is not implemented yet

        # join error structure
        err = []

        for name, e in errordata.items():
            if e:
                err.append((name, e))

        return err if err else None
