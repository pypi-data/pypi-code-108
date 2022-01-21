import tkinter as tk

from . import scon
from . import guidata
from . import layoutmode
from . import balloonhelp

from .tktool import codedoptionmenu
from .tktool import validateentry


class Surf(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        # link to gui_xtal_layer_elem
        self._xtallayerelem = None

        # surface (0, 1, 2, 3, or >=6)
        self.surfacelabel = tk.Label(self, text='SURFCE:')
        self.surfaceoptions = [
            (0, '0: No external surfaces'),
            (1, '1: Front'),
            (2, '2: Front + Back side'),
            (3, '3: F+B+limited lateral extent'),
            # (6, '>=6: User supplied (not implemented)')
            (-1, '-1: Internal Primary Atoms mode')]
        self.surfacevardefault = self.surfaceoptions[0]
        self.surface = codedoptionmenu.CodedOptionMenu(self, self.surfaceoptions,
                                                       command=self._surface_action)
        self.surfaceballoonhelp = '''Cofiguration of target surface (&MODL::SURFACE)'''
        self.surface.config(width=20, anchor='w')

        # LYME (default 1)
        self.lymelabel = tk.Label(self, text='LYME:')
        self.lymeoptions = [(i, str(i)) for i in range(1, scon.nlay+1)]
        self.lymedefault = self.lymeoptions[0]
        self.lyme = codedoptionmenu.CodedOptionMenu(self, self.lymeoptions)
        self.lymeballoonhelp = '''\
The layer used as the basis to configure initial parallelogram impact area
(SIDES and RSRF) and for limiting the lateral extent of the target (EDGE).'''
        self.lyme.config(width=4, anchor='w')

        # CALC
        # temporally skipped

        self.impactareaframe = tk.LabelFrame(self, text='Impact\nArea:', labelanchor=tk.W)

        # available at surfce == 1, 2, 3
        # (if surfce==0 inner primary atom mode, but is not valid now)
        # SIDES
        self.sideslabel = tk.Label(self.impactareaframe, text='SIDES:')
        self.sides = validateentry.Vec3d(self.impactareaframe)
        self.sides.config(width='10')
        self.sidesballoonhelp = '''\
The lengths in units of BASE (or its square) of the sides of
the parallelogram, within which the initial impact points of
the primary atoms on the target surface are selected.
The two components are parallel to AXISA and AXISB, for
the layer numbered LYME. (SIDES)'''

        # RSRF
        self.rsrflabel = tk.Label(self.impactareaframe, text='RSRF:')
        self.rsrf = validateentry.Vec3d(self.impactareaframe)
        self.rsrf.config(width='10')
        self.rsrfballoonhelp = '''\
The location of one corner of the parallelogram, within which
the initial impact points of the primary atoms on the target
surface are selected. The two components are displacements from
the ORIGIN of the layer numbered LYME, in units of BASE,
parallel to AXISA and AXISB (RSRF)'''
        # valid if surfce == 3
        # CORNER
        # self.cornerlabel = tk.Label(self, text='CORNER:')
        # self.corner = validateentry.Vec2d(self)
        # self.corner.config(width='10')

        # EDGE
        self.edgelabel = tk.Label(self, text='Surface\nArea:')
        self.edge = validateentry.Vec2d(self)
        self.edge.config(width='10')
        self.edgeballoonhelp = '''\
The lengths in units of BASE (or its square) of the sides
of the parallelogram. The two components are parallel
to AXISA and AXISB for the layer numbered LYME. (EDGE)'''

        self.clear()

        self.layout()

    def layout(self, mode=0):
        prow = 0

        self.surfacelabel.grid(row=prow, column=0, sticky=tk.E)
        self.surface.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.lymelabel.grid(row=prow, column=0, sticky=tk.E)
        self.lyme.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.impactareaframe.grid(row=prow, column=0, columnspan=2, sticky=tk.E+tk.W)
        prow += 1
        # self.cornerlabel.grid(row=prow, column=0, sticky=tk.E)
        # self.corner.grid(row=prow, column=1, sticky=tk.W)
        # prow += 1
        self.edgelabel.grid(row=prow, column=0, sticky=tk.E)
        self.edge.grid(row=prow, column=1, sticky=tk.W)

        self._layout_impactareaframe(mode)

    def _layout_impactareaframe(self, mode=0):
        self.sideslabel.grid(row=0, column=0, sticky=tk.W)
        self.sides.grid(row=1, column=0, sticky=tk.W, padx=(10, 0))
        self.rsrflabel.grid(row=2, column=0, sticky=tk.W)
        self.rsrf.grid(row=3, column=0, sticky=tk.W, padx=(10, 0))

    def bind_with_balloonhelp(self, b):
        b.bind(self.surface, balloonHelp=self.surfaceballoonhelp)
        b.bind(self.lyme, balloonHelp=self.lymeballoonhelp)
        b.bind(self.sides, balloonHelp=self.sidesballoonhelp)
        b.bind(self.rsrf, balloonHelp=self.rsrfballoonhelp)
        b.bind(self.edge, balloonHelp=self.edgeballoonhelp)

    def set(self, d):
        if 'surfce' in d:
            idx = d['surfce']
            if -1 <= idx <= 3:
                self.surface.set(idx)
            else:
                self.surface.set(6)
        if 'lyme' in d:
            self.lyme.set(d['lyme'])
        if 'sides' in d:
            self.sides.set(d['sides'])
        if 'rsrf' in d:
            self.rsrf.set(d['rsrf'])
        # if 'corner' in d:
        #    self.corner.set(d['corner'])
        if 'edge' in d:
            self.edge.set(d['edge'])

        self.set_avail_by_surface()

    def get(self):
        d = {}
        d['surfce'] = self.surface.get()
        s = d['surfce']
        if s >= 1 or s == -1:
            d['lyme'] = self.lyme.get()
            d['sides'] = self.sides.get()
            d['rsrf'] = self.rsrf.get()
        if s == 3:
            # d['corner'] = self.corner.get()
            d['edge'] = self.edge.get()
        return d

    def clear(self):
        self.set(guidata.surf_default)

    def validate(self):
        err = []
        # r = self.surface.validate()
        # if r:
        #    err.append(('surfce', r))
        s = self.surface.get()
        if s >= 1 or s == -1:
            r = self.lyme.validate()
            if r:
                err.append(('lyme', r))
            r = self.sides.validate()
            if r:
                err.append(('sides', r))
            r = self.rsrf.validate()
            if r:
                err.append(('rsrf', r))
        if s == 3:
            # r = self.corner.validate()
            # if r:
            #    err.append(('corner', r))
            r = self.edge.validate()
            if r:
                err.append(('edge', r))

        return err if err else None

    def link_xtallayerelem(self, widget):
        self._xtallayerelem = widget

    def _surface_action(self, value):
        self.set_avail_by_surface()

    def _set_avail_by_surface_ext(self):
        # change status outside the widget
        if self._xtallayerelem:
            v = self.surface.get()

            if v in (-1, 1, 2, 3):
                self._xtallayerelem.enable_surfopt()
            else:
                self._xtallayerelem.disable_surfopt()

    def set_avail_by_surface(self):
        s = self.surface.get()
        if s == 0:
            self.lyme.disable()
            self.sides.disable()
            self.rsrf.disable()
            # self.corner.disable()
            self.edge.disable()
        elif s in (-1, 1, 2):
            self.lyme.enable()
            self.sides.enable()
            self.rsrf.enable()
            # self.corner.disable()
            self.edge.disable()
        elif s == 3:
            self.lyme.enable()
            self.sides.enable()
            self.rsrf.enable()
            # self.corner.enable()
            self.edge.enable()
        self._set_avail_by_surface_ext()

    def enable(self):
        self.surface.enable()
        self.set_avail_by_surface()

    def disable(self):
        self.surface.disable()
        self.lyme.disable()
        self.sides.disable()
        self.rsrf.disable()
        # self.corner.disable()
        self.edge.disable()
