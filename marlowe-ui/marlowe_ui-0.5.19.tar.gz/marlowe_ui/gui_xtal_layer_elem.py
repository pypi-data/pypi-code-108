import tkinter as tk

from . import guidata
from . import gui_site_elem
from . import gui_layer_surf
from . import axis
from . import layoutmode
from . import balloonhelp

from .tktool import validateentry
from .tktool import oneof
from .tktool import codedoptionmenu

Site = oneof.OneofFactory(gui_site_elem.SiteElem,
                          guidata.site_elem_default)


class XtalLayerElem(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        self.disabled = False

        # ALAT.a b c
        self.latticelabel = tk.Label(self, text='(a,b,c):')
        self.lattice = validateentry.Vec3d(self)
        self.lattice.config(width=10)
        self.latticeballoonhelp = 'Unit cell edge length (ALAT(1:3)).\n' + \
            'Described in the unit given by &MODEL.METRIC option'

        # ALAT.bc ca ab
        self.anglelabel = tk.Label(self, text='angl:')
        self.angle = validateentry.Vec3d(self)
        self.angle.config(width=10)
        self.angleballoonhelp = 'Angle of cell edges in degree unit (ALAT(4:6)).'

        # centre and poly fields
        self.centrepolylabel = tk.Label(self, text='CRYST.:')

        # centre
        self.crystalframe = tk.Frame(self)
        self.centreoptions = [
            (1, '1: (P) Primitive'),
            (2, '2: (I) Body-centered'),
            (3, '3: (A) End-centered on b-c plane'),
            (4, '4: (B) End-centered on c-a plane'),
            (5, '5: (C) End-centered on a-b plane'),
            (6, '6: (F) Face-centered')]
        self.centre = codedoptionmenu.CodedOptionMenu(self.crystalframe,
                                                      self.centreoptions)
        self.centre.config(width=10, anchor='w')
        self.centreballoonhelp = 'Centering symmetry of the unit cell (CENTRE)'

        # poly
        self.polyoptions = [
            (0, '0: monocrystalline'),
            (1, '1: polycrystalline'),
            (2, '2: amorphous')]
        self.poly = codedoptionmenu.CodedOptionMenu(self.crystalframe,
                                                    self.polyoptions)
        self.poly.config(width=10, anchor='w')
        self.polyballoonhelp = 'Crystrallinity of the layer'

        # dmax
        self.dmaxlabel = tk.Label(self, text='DMAX')
        self.dmax = validateentry.Double(self)
        self.dmax.config(width=10)
        self.dmaxballoonhelp = '''\
The maximum distance from the origin of neighboring
atoms that are to be included in the crystal description
of the current layer. DMAX must be in units of BASE. (DMAX)'''

        # axis
        self.axis = axis.Axis(self)

        # rz, atom.lock and atom.order
        self.siteframe = tk.LabelFrame(self, text='SITE')
        self.site = Site(self.siteframe)

        # surface option
        self.surfoptframe = tk.LabelFrame(self, text='&SURF opt.')
        self.surfoptframeballoonhelp = '''\
To enable this frame, set &SURF.SURFACE parameter'''
        self.surfopt = gui_layer_surf.LayerSurfOption(self.surfoptframe)

        self.clear()

        # surfopt_enabled just controls gui status but does not affect
        # on set() and get() method,

        self.disable_surfopt()

        self.layout()

    def layout(self, mode=0):
        prow = 0
        self.latticelabel.grid(row=prow, column=0, sticky=tk.E)
        self.lattice.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.anglelabel.grid(row=prow, column=0, sticky=tk.E)
        self.angle.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.centrepolylabel.grid(row=prow, column=0, sticky=tk.E)
        self.crystalframe.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.dmaxlabel.grid(row=prow, column=0, sticky=tk.E)
        self.dmax.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.axis.grid(row=prow, column=0, columnspan=2, sticky=tk.E)
        prow += 1
        self.siteframe.grid(row=prow, column=0, columnspan=2)
        prow += 1
        self.surfoptframe.grid(row=prow, column=0, columnspan=2)

        # layout subsidgt contents using WIDGET.layout() method
        self.axis.layout(mode)

        # layout subwidget contents using self._layout_WIDGET method
        self._layout_crystalframe(mode)
        self._layout_siteframe(mode)
        self._layout_surfoptframe(mode)

    def _layout_crystalframe(self, mode=0):
        self.centre.pack(side=tk.LEFT)
        self.poly.pack(side=tk.LEFT)

    def _layout_siteframe(self, mode=0):
        self.site.pack()

        # subwidget contents
        self.site.layout(mode)

    def _layout_surfoptframe(self, mode=0):
        self.surfopt.pack()

        # subwidget contents
        self.surfopt.layout(mode)

    def bind_with_balloonhelp(self, b):
        for w in self.lattice.array:
            b.bind(w, balloonHelp=self.latticeballoonhelp)
        for w in self.angle.array:
            b.bind(w, balloonHelp=self.angleballoonhelp)
        b.bind(self.centre, balloonHelp=self.centreballoonhelp)
        b.bind(self.poly, balloonHelp=self.polyballoonhelp)
        b.bind(self.dmax, balloonHelp=self.dmaxballoonhelp)
        b.bind(self.surfoptframe, balloonHelp=self.surfoptframeballoonhelp)

        self.axis.bind_with_balloonhelp(b)
        self.site.bind_with_balloonhelp(b)
        self.surfopt.bind_with_balloonhelp(b)

    def set(self, d):
        self.lattice.set(d.get('alat', guidata.xtal_layer_elem_default['alat'])[0:3])
        self.angle.set(d.get('alat', guidata.xtal_layer_elem_default['alat'])[3:6])

        self.centre.set(d.get('centre', guidata.xtal_layer_elem_default['centre']))
        self.dmax.set(d.get('dmax', guidata.xtal_layer_elem_default['dmax']))
        self.poly.set(d.get('poly', guidata.xtal_layer_elem_default['poly']))

        # axis is optional, if None is given for axis.set,
        # this frame is disabled.
        self.axis.set(d.get('axis', None))

        self.site.set(d.get('site', guidata.xtal_layer_elem_default['site']))

        if 'surfopt' in d and d['surfopt']:
            self.surfopt.set(d['surfopt'])
        else:
            self.surfopt.set(guidata.layer_surfopt_default)

    def get(self):
        d = {}
        if self.is_disabled():
            return d

        d['alat'] = list(self.lattice.get() + self.angle.get())
        d['centre'] = self.centre.get()
        d['dmax'] = self.dmax.get()
        d['poly'] = self.poly.get()

        daxis = self.axis.get()
        if daxis:
            d['axis'] = daxis

        d['site'] = self.site.get()
        d['surfopt'] = self.surfopt.get_nostatechk()
        return d

    def clear(self):
        self.set(guidata.xtal_layer_elem_default)

    def validate(self):
        err = []
        if self.is_disabled():
            return None
        for n, w in [
                ('lattice', self.lattice),
                ('angle', self.angle),
                ('dmax', self.dmax),
                ('axis', self.axis),
                ('site', self.site)]:
            e = w.validate()
            if e:
                err.append((n, e))
        if self.surfopt_enabled:
            e = self.surfopt.validate()
            if e:
                err.append(('surfopt', e))

        return err if err else None

    def enable(self):
        self.lattice.config(state=tk.NORMAL)
        self.angle.config(state=tk.NORMAL)
        self.centre.config(state=tk.NORMAL)
        self.poly.config(state=tk.NORMAL)
        self.dmax.config(state=tk.NORMAL)
        self.axis.enable()
        self.site.enable()
        if self.surfopt_enabled:
            self.surfopt.enable()
        else:
            # keep widget disabled
            self.surfopt.disable()
        self.disabled = False

    def disable(self):
        self.lattice.config(state=tk.DISABLED)
        self.angle.config(state=tk.DISABLED)
        self.centre.config(state=tk.DISABLED)
        self.poly.config(state=tk.DISABLED)
        self.dmax.config(state=tk.DISABLED)
        self.axis.disable()
        self.site.disable()
        self.surfopt.disable()
        self.disabled = True

    def enable_surfopt(self):
        self.surfopt_enabled = True
        # change gui status
        if not self.is_disabled():
            self.surfopt.enable()

    def disable_surfopt(self):
        self.surfopt_enabled = False
        if not self.is_disabled():
            self.surfopt.disable()

    def is_disabled(self):
        return self.disabled
