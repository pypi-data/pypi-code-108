import tkinter as tk

from .tktool import validateentry
from .tktool import codedoptionmenu

from . import scon
from . import guidata
from . import layoutmode
from . import balloonhelp


class SizeBody(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):

    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        # RB
        # enabile and disable control will be needed
        self.rbs = []
        self.rblabels = []
        self.rbballoonhelp = 'The maximum impact parameter in units of BASE'
        for i in range(scon.nrbx):
            if i == 0:
                rblabel = tk.Label(self, text='RB({0:d}):'.format(i + 1))
            else:
                rblabel = tk.Label(self, text='({0:d}):'.format(i + 1))
            rb = validateentry.Double(self)
            rb.config(width=10)
            self.rbs.append(rb)
            self.rblabels.append(rblabel)

        # XILIM
        self.xilims = []
        self.xilimlabels = []
        self.xilimsballoonhelp = [
            '''\
The minimum distance forward used to collect potential
collision partners (in nm unit).''',
            '''\
The minimum effective distance defining the time interval
after which the first collision may occur (in BASE unit).''',
            '''\
The maximum interval permitted between simultaneous collision
points after corrections for scattering (in nm unit).''',
            '''\
Controls the minimum search distance for the following
collision (in BASE unit).''']
        for i in range(4):
            if i == 0:
                xilimlabel = tk.Label(
                    self, text='XILIM({0:d})[nm]:'.format(i + 1))
            elif i == 2:
                xilimlabel = tk.Label(self, text='({0:d})[nm]:'.format(i + 1))
            else:
                xilimlabel = tk.Label(
                    self, text='({0:d})[base]:'.format(i + 1))
            xilim = validateentry.Double(self)
            xilim.config(width=10)
            self.xilims.append(xilim)
            self.xilimlabels.append(xilimlabel)

        # SLICE:
        self.slicelabel = tk.Label(self, text='SLICE:')
        self.slice_ = validateentry.Double(self)
        self.slice_.config(width=10)
        self.sliceballoonhelp = '''\
The width in femtoseconds of the time-slice used
in time-ordered cascade calculations.'''

        # STEP
        self.steplabel = tk.Label(self, text='STEP:')
        self.step = validateentry.Double(self)
        self.step.config(width=10)
        self.stepballoonhelp = '''\
The maximum time in femtoseconds that a collision may
be deferred before it is re-examined.'''

        # LIFO
        self.lifolabel = tk.Label(self, text='LIFO')
        self.lifooptions = [
            (True,
             'T: The last atom stored in the time-slice table is processed first'),
            (False, 'F: The first atom stored in the time-slice table is processed first')]
        self.lifo = codedoptionmenu.CodedOptionMenu(self,
                                                    self.lifooptions)
        self.lifo.config(width=20, anchor=tk.W)
        self.lifoballoonhelp = '''Controls the inventory policy used when collisions are time-ordered.'''

        self.clear()
        self.layout()

    def layout(self, mode=0):
        prow = 0
        for l, e in zip(self.rblabels, self.rbs):
            l.grid(row=prow, column=0, sticky=tk.E)
            e.grid(row=prow, column=1, sticky=tk.W)
            prow += 1

        for l, e in zip(self.xilimlabels, self.xilims):
            l.grid(row=prow, column=0, sticky=tk.E)
            e.grid(row=prow, column=1, sticky=tk.W)
            prow += 1

        self.slicelabel.grid(row=prow, column=0, sticky=tk.E)
        self.slice_.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.steplabel.grid(row=prow, column=0, sticky=tk.E)
        self.step.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.lifolabel.grid(row=prow, column=0, sticky=tk.E)
        self.lifo.grid(row=prow, column=1, sticky=tk.W)

    def bind_with_balloonhelp(self, b):
        for l, e in zip(self.rblabels, self.rbs):
            b.bind(l, balloonHelp=self.rbballoonhelp)
            b.bind(e, balloonHelp=self.rbballoonhelp)

        for l, e, h in zip(self.xilimlabels, self.xilims, self.xilimsballoonhelp):
            b.bind(l, balloonHelp=h)
            b.bind(e, balloonHelp=h)

        b.bind(self.slicelabel, balloonHelp=self.sliceballoonhelp)
        b.bind(self.slice_, balloonHelp=self.sliceballoonhelp)
        b.bind(self.steplabel, balloonHelp=self.stepballoonhelp)
        b.bind(self.step, balloonHelp=self.stepballoonhelp)
        b.bind(self.lifolabel, balloonHelp=self.lifoballoonhelp)
        b.bind(self.lifo, balloonHelp=self.lifoballoonhelp)

    def set(self, d):
        xval = d.get('rb', guidata.size_body_default['rb'])
        for w, x in zip(self.rbs, xval):
            w.set(x)

        xval = d.get('xilim', guidata.size_body_default['xilim'])
        for w, x in zip(self.xilims, xval):
            w.set(x)

        self.slice_.set(d.get('slice',
                              guidata.size_body_default['slice']))
        self.step.set(d.get('step',
                            guidata.size_body_default['step']))
        self.lifo.set(d.get('lifo',
                            guidata.size_body_default['lifo']))

    def get(self):
        d = {}
        d['rb'] = [w.get() for w in self.rbs]
        d['xilim'] = [w.get() for w in self.xilims]
        d['slice'] = self.slice_.get()
        d['step'] = self.step.get()
        d['lifo'] = self.lifo.get()
        return d

    def clear(self):
        self.set(guidata.size_body_default)

    def validate(self):
        err = []
        for n, w in [
                ('slice', self.slice_),
                ('step', self.step)]:
            e = w.validate()
            if e:
                err.append((n, e))
        return err if err else None

    def enable(self):
        for w in self.rbs:
            w.config(state=tk.NORMAL)
        for w in self.xilims:
            w.config(state=tk.NORMAL)
        self.slice_.config(state=tk.NORMAL)
        self.step.config(state=tk.NORMAL)
        self.lifo.config(state=tk.NORMAL)

    def disable(self):
        for w in self.rbs:
            w.config(state=tk.DISABLED)
        for w in self.xilims:
            w.config(state=tk.DISABLED)
        self.slice_.config(state=tk.DISABLED)
        self.step.config(state=tk.DISABLED)
        self.lifo.config(state=tk.DISABLED)
