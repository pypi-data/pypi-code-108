import tkinter as tk

from . import scon
from . import guidata
from . import layoutmode
from . import balloonhelp

from .tktool import validateentry
from .tktool import codedoptionmenu


class ProjElem(tk.Frame,
               layoutmode.LayoutModeImplement,
               balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        # prim
        self.primoptions = [
            (0, '0:Full cascade'),
            (1, '1:PKA and initial disp.'),
            (2, '2:PKA only')]
        self.prim = codedoptionmenu.CodedOptionMenu(self,
                                                    self.primoptions)
        self.prim.config(width=10, anchor='w')
        self.primballoonhelp = '''Development of cascades to be calculated (PRIM)'''
        self.primlabel = tk.Label(self, text='PRIM:')

        # maxrun
        self.maxrunlabel = tk.Label(self, text='MAXRUN:')
        self.maxrun = validateentry.Int(self)
        self.maxrunballoonhelp = '''\
The number of primary recoils to be generated statistically.
If MAXRUN = 0, all initial conditions must be supplied.
Some statistical procedures require MAXRUN > 1 for output
to be produced. (MAXRUN)'''
        self.maxrun.config(width=10)

        # laip
        self.laiplabel = tk.Label(self, text='LAIP:')
        self.laip = validateentry.Int(self)
        self.laipballoonhelp = '''\
The type number of the first primary recoil in a cascade group. (LAIP)'''
        self.laip.config(width=10)

        # ekip
        self.ekiplabel = tk.Label(self, text='EKIP:')
        self.ekip = validateentry.Double(self)
        self.ekipballoonhelp = '''\
The initial kinetic energy of the primary recoil in eV (EKIP)'''
        self.ekip.config(width=10)

        # trmp
        self.trmpoptions = [
            (True, 'T:external cood. of LYME layer'),
            (False, 'F:internal coord. of LYME layer')]
        self.trmp = codedoptionmenu.CodedOptionMenu(self,
                                                    self.trmpoptions)
        self.trmpballoonhelp = '''\
Coordination system for RAIP, REFIP and BEAM (TRMP)'''
        self.trmp.config(anchor='w', width=20)
        self.trmplabel = tk.Label(self, text='TRMP:')

        # raip
        self.raip = validateentry.Vec3d(self)
        self.raip.config(width=10)
        self.raipballoonhelp = '''\
The initial location of the first primary recoil in
a cascade group. The initial positions of subsequent
primaries in a group are found statistically. (RAIP)'''
        self.raiplabel = tk.Label(self, text='RAIP:')

        # refip
        self.refip = validateentry.Vec3d(self)
        self.refip.config(width=10)
        self.refipballoonhelp = '''\
The location of a lattice site at (or near) which the first
primary recoil in a cascade group starts. (REFIP)'''
        self.refiplabel = tk.Label(self, text='REFIP:')

        # lrip
        self.lriplabel = tk.Label(self, text='LRIP:')
        self.lrip = validateentry.Int(self)
        self.lripballoonhelp = '''\
The type number of this lattice site (LRIP)'''
        self.lrip.config(width=10)

        # leap
        self.leapoptions = [
            (0, '0:Isotropic in all space'),
            (1, '1:Isotropic in z >=0 hemisphere'),
            (2, '2:Isotorpic in first octant'),
            (3, '3:1/48 space bordered by <001>, <111>, <101>'),
            (4, '4:Specify beam direction by BEAM or THA and PHI record.\n'
             + 'Aleatory is applied on beam divergence and initial position'),
            (5,
             '5:Similar to 4, but aleatory is applied only initial position'),
            (6, '6:Similar to 6, but no aleatory is applied.'),
            # (10, '10:user specified' ),
            (20,
             '20:Selected uniformly in the initial impact parallelogram given by LYME layer'),
            (21, '21:area bounded by 20 and AXISA'),
            (22, '22:area bounded by 20, AXISA, and AXISB'),
            (23,
             '23:Selected uniformly in an ellipse inscribed in the initial impact parallelogram'),
            (25,
             '25:Specify initial position. Aleatory is taken into account.'),
            (26,
             '26:Specify initial position. Aleatory is not taken into account.'),
            # (30, '30:'),
        ]
        self.leap = codedoptionmenu.CodedOptionMenu(self,
                                                    self.leapoptions)
        self.leap.config(anchor='w', width=10)
        self.leapballoonhelp = '''\
Controls the initialization of the primary recoil (LEAP):
- For internal primaries, LEAP < 20. The initial position is
  supplied by input data.
- For external irradiations, LEAP >= 20. The initial primary
  direction is given by input data.
- When LEAP < 26, this direction is subject to aleatory
  selection from a range determined by the value of DVRG.'''
        self.leaplabel = tk.Label(self, text='LEAP:')

        # miller
        self.milleroptions = [
            (True, 'T: Use Miller indices'),
            (False, 'F: Use THA and PHI')]
        self.miller = codedoptionmenu.CodedOptionMenu(self,
                                                      self.milleroptions,
                                                      command=self._miller_action)
        self.miller.config(anchor='w', width=20)
        self.millerballoonhelp = '''\
Controls whether the initial primary direction (MILLER)'''
        self.millerlabel = tk.Label(self, text='MILLER:')

        # beam
        self.beam = validateentry.Vec3d(self)
        self.beam.config(width=10)
        self.beamballoonhelp = '''\
The (average) initial direction of the primary recoils.
The elements of the vector must be proportional to the
Miller indices of the desired direction. (BEAM)'''
        self.beamlabel = tk.Label(self, text='BEAM:')

        # tha
        self.thalabel = tk.Label(self, text='THA:')
        self.tha = validateentry.Double(self)
        self.thaballoonhelp = '''\
The initial polar angle of the primary direction (degrees),
measured from the internal z-axis (THA).'''
        self.tha.config(width=10)

        # phi
        self.philabel = tk.Label(self, text='PHI:')
        self.phi = validateentry.Double(self)
        self.phiballoonhelp = '''\
The initial azimuthal angle of the primary direction (degrees),
measured from the internal x-axis in the internal x-y plane. (PHI)'''
        self.phi.config(width=10)

        # dvrg
        self.dvrglabel = tk.Label(self, text='DVRG:')
        self.dvrg = validateentry.Double(self)
        self.dvrgballoonhelp = '''\
The primary particle beam divergence (degrees). The beam is
distributed isotropically within this interval (DVRG)'''
        self.dvrg.config(width=10)

        # ranx
        self.ranxs = []
        self.ranxrowlabels = []
        self.ranxrowframes = []
        self.ranxsballoonhelp = 'The seed of the random number generator. (RANX)'
        ranxcolumns = 4
        # calculate how to align cells 4*q + r
        q, r = divmod(scon.nrnx, ranxcolumns)
        for i in range(scon.nrnx):
            r, c = divmod(i, ranxcolumns)
            if c == 0:
                # prepare label
                if r == 0:
                    ranxlabel = tk.Label(self,
                                         text='RANX({0:d}-):'.format(i + 1))
                else:
                    ranxlabel = tk.Label(self,
                                         text='({0:d}-):'.format(i + 1))
                self.ranxrowlabels.append(ranxlabel)

                # prepare frame
                self.ranxrowframes.append(tk.Frame(self))

            # Int entry box
            ranx = validateentry.Int(self.ranxrowframes[r])
            ranx.config(width=8)
            self.ranxs.append(ranx)

        # new
        self.newlabel = tk.Label(self, text='NEW:')
        self.new = validateentry.Int(self)
        self.newballoonhelp = '''\
The file number of the initial point defect atom which is
to be used as the primary recoil. (NEW)'''
        self.new.config(width=10)

        self.clear()
        self.layout()

    def layout(self, mode=0):
        prow = 0

        self.primlabel.grid(row=prow, column=0, sticky=tk.E)
        self.prim.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.maxrunlabel.grid(row=prow, column=0, sticky=tk.E)
        self.maxrun.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.laiplabel.grid(row=prow, column=0, sticky=tk.E)
        self.laip.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.ekiplabel.grid(row=prow, column=0, sticky=tk.E)
        self.ekip.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.trmplabel.grid(row=prow, column=0, sticky=tk.E)
        self.trmp.grid(row=prow, column=1, sticky=tk.W + tk.E)
        prow += 1
        self.raiplabel.grid(row=prow, column=0, sticky=tk.E)
        self.raip.grid(row=prow, column=1, sticky=tk.W + tk.E)
        prow += 1
        self.refiplabel.grid(row=prow, column=0, sticky=tk.E)
        self.refip.grid(row=prow, column=1, sticky=tk.W + tk.E)
        prow += 1
        if mode == 0:
            self.lriplabel.grid(row=prow, column=0, sticky=tk.E)
            self.lrip.grid(row=prow, column=1, sticky=tk.W)
            prow += 1
        else:
            self.lriplabel.grid_forget()
            self.lrip.grid_forget()
        self.leaplabel.grid(row=prow, column=0, sticky=tk.E)
        self.leap.grid(row=prow, column=1, sticky=tk.W + tk.E)
        prow += 1
        self.millerlabel.grid(row=prow, column=0, sticky=tk.E)
        self.miller.grid(row=prow, column=1, sticky=tk.W + tk.E)
        prow += 1
        self.beamlabel.grid(row=prow, column=0, sticky=tk.E)
        self.beam.grid(row=prow, column=1, sticky=tk.W + tk.E)
        prow += 1
        self.thalabel.grid(row=prow, column=0, sticky=tk.E)
        self.tha.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.philabel.grid(row=prow, column=0, sticky=tk.E)
        self.phi.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        if mode == 0:
            self.dvrglabel.grid(row=prow, column=0, sticky=tk.E)
            self.dvrg.grid(row=prow, column=1, sticky=tk.W)
            prow += 1
        else:
            self.dvrglabel.grid_forget()
            self.dvrg.grid_forget()

        for lab, fra in zip(self.ranxrowlabels, self.ranxrowframes):
            if mode == 0:
                lab.grid(row=prow, column=0, sticky=tk.E)
                fra.grid(row=prow, column=1, sticky=tk.W)
                prow += 1
            else:
                lab.grid_forget()
                fra.grid_forget()

        if mode == 0:
            self.newlabel.grid(row=prow, column=0, sticky=tk.E)
            self.new.grid(row=prow, column=1, sticky=tk.W)
            prow += 1
        else:
            self.newlabel.grid_forget()
            self.new.grid_forget()

        # subwidgets
        self._layout_ranxrowframes(mode)

    def _layout_ranxrowframes(self, mode=0):
        for r in self.ranxs:
            # each r is bounded to proper self.ranxrowframes
            if mode == 0:
                r.pack(side=tk.LEFT)
            else:
                r.pack_forget()

    def bind_with_balloonhelp(self, b):
        b.bind(self.prim, balloonHelp=self.primballoonhelp)
        b.bind(self.maxrun, balloonHelp=self.maxrunballoonhelp)
        b.bind(self.laip, balloonHelp=self.laipballoonhelp)
        b.bind(self.ekip, balloonHelp=self.ekipballoonhelp)
        b.bind(self.trmp, balloonHelp=self.trmpballoonhelp)
        b.bind(self.raip, balloonHelp=self.raipballoonhelp)
        b.bind(self.refip, balloonHelp=self.refipballoonhelp)
        b.bind(self.lrip, balloonHelp=self.lripballoonhelp)
        b.bind(self.leap, balloonHelp=self.leapballoonhelp)
        b.bind(self.miller, balloonHelp=self.millerballoonhelp)
        b.bind(self.beam, balloonHelp=self.beamballoonhelp)
        b.bind(self.tha, balloonHelp=self.thaballoonhelp)
        b.bind(self.phi, balloonHelp=self.phiballoonhelp)
        b.bind(self.dvrg, balloonHelp=self.dvrgballoonhelp)
        for r in self.ranxs:
            b.bind(r, balloonHelp=self.ranxsballoonhelp)
        b.bind(self.new, balloonHelp=self.newballoonhelp)

    def _select_beam_method(self):
        """command when miller is changed"""
        if self.miller.get():
            self.beam.config(state=tk.NORMAL)
            self.tha.config(state=tk.DISABLED)
            self.phi.config(state=tk.DISABLED)
        else:
            self.beam.config(state=tk.DISABLED)
            self.tha.config(state=tk.NORMAL)
            self.phi.config(state=tk.NORMAL)

    def _miller_action(self, value):
        self._select_beam_method()

    def set(self, d):
        ranx = d.get('ranx', guidata.proj_elem_default['ranx'])
        for w, v in zip(self.ranxs, ranx):
            w.set(v)
        self.maxrun.set(
            d.get('maxrun',
                  guidata.proj_elem_default['maxrun']))
        self.prim.set(
            d.get('prim',
                  guidata.proj_elem_default['prim']))
        self.new.set(
            d.get('new',
                  guidata.proj_elem_default['new']))
        self.ekip.set(
            d.get('ekip',
                  guidata.proj_elem_default['ekip']))
        self.leap.set(
            d.get('leap',
                  guidata.proj_elem_default['leap']))
        self.trmp.set(
            d.get('trmp',
                  guidata.proj_elem_default['trmp']))
        self.raip.set(
            d.get('raip',
                  guidata.proj_elem_default['raip']))
        self.laip.set(
            d.get('laip',
                  guidata.proj_elem_default['laip']))
        self.refip.set(
            d.get('refip',
                  guidata.proj_elem_default['refip']))
        self.lrip.set(
            d.get('lrip',
                  guidata.proj_elem_default['lrip']))
        self.miller.set(
            d.get('miller',
                  guidata.proj_elem_default['miller']))
        self.beam.set(
            d.get('beam',
                  guidata.proj_elem_default['beam']))
        self.tha.set(
            d.get('tha',
                  guidata.proj_elem_default['tha']))
        self.phi.set(
            d.get('phi',
                  guidata.proj_elem_default['phi']))
        self.dvrg.set(
            d.get('dvrg',
                  guidata.proj_elem_default['dvrg']))

        self._select_beam_method()

    def get(self):
        d = {}
        d['ranx'] = [w.get() for w in self.ranxs]
        d['maxrun'] = self.maxrun.get()
        d['prim'] = self.prim.get()
        d['new'] = self.new.get()
        d['ekip'] = self.ekip.get()
        d['leap'] = self.leap.get()
        d['trmp'] = self.trmp.get()
        d['raip'] = self.raip.get()
        d['laip'] = self.laip.get()
        d['refip'] = self.refip.get()
        d['lrip'] = self.lrip.get()
        d['miller'] = self.miller.get()
        d['beam'] = self.beam.get_nostatechk()
        d['tha'] = self.tha.get_nostatechk()
        d['phi'] = self.phi.get_nostatechk()
        d['dvrg'] = self.dvrg.get()
        return d

    def clear(self):
        self.set(guidata.proj_elem_default)

    def validate(self):
        err = []

        for i, w in enumerate(self.ranxs):
            e = w.validate()
            if e:
                err.append(('RANX{0:d}'.format(i + 1), e))
        e = self.maxrun.validate()
        if e:
            err.append(('MAXRUN', e))
        e = self.new.validate()
        if e:
            err.append(('NEW', e))
        e = self.ekip.validate()
        if e:
            err.append(('EKIP', e))

        e = self.raip.validate()
        if e:
            err.append(('RAIP', e))

        e = self.laip.validate()
        if e:
            err.append(('LAIP', e))

        e = self.refip.validate()
        if e:
            err.append(('REFIP', e))

        e = self.lrip.validate()
        if e:
            err.append(('LRIP', e))

        if self.miller.get():
            e = self.beam.validate()
            if e:
                err.append(('BEAM', e))
        else:
            e = self.tha.validate()
            if e:
                err.append(('THA', e))

            e = self.phi.validate()
            if e:
                err.append(('PHI', e))

        e = self.dvrg.validate()
        if e:
            err.append(('DVRG', e))

        return err if err else None

    def enable(self):
        for w in self.ranxs:
            w.config(state=tk.NORMAL)
        self.maxrun.config(state=tk.NORMAL)
        self.prim.config(state=tk.NORMAL)
        self.new.config(state=tk.NORMAL)
        self.ekip.config(state=tk.NORMAL)
        self.leap.config(state=tk.NORMAL)
        self.trmp.config(state=tk.NORMAL)
        self.raip.config(state=tk.NORMAL)
        self.laip.config(state=tk.NORMAL)
        self.refip.config(state=tk.NORMAL)
        self.lrip.config(state=tk.NORMAL)
        self.miller.config(state=tk.NORMAL)
        # self.{beam,tha,phi}.config(state=tk.NORMAL) are controled by _select_beam_method()
        self._select_beam_method()
        self.dvrg.config(state=tk.NORMAL)

    def disable(self):
        for w in self.ranxs:
            w.config(state=tk.DISABLED)
        self.maxrun.config(state=tk.DISABLED)
        self.prim.config(state=tk.DISABLED)
        self.new.config(state=tk.DISABLED)
        self.ekip.config(state=tk.DISABLED)
        self.leap.config(state=tk.DISABLED)
        self.trmp.config(state=tk.DISABLED)
        self.raip.config(state=tk.DISABLED)
        self.laip.config(state=tk.DISABLED)
        self.refip.config(state=tk.DISABLED)
        self.lrip.config(state=tk.DISABLED)
        self.miller.config(state=tk.DISABLED)
        self.beam.config(state=tk.DISABLED)
        self.tha.config(state=tk.DISABLED)
        self.phi.config(state=tk.DISABLED)
        self.dvrg.config(state=tk.DISABLED)
