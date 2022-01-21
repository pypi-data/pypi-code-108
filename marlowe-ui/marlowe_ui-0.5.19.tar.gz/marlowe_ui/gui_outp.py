import tkinter as tk

from . import guidata
from . import layoutmode
from . import balloonhelp

from .tktool import validateentry
from .tktool import codedoptionmenu
from .tktool import gui_abstract


class OutpInform(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):

    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        self.checkvars = []
        self.checks = []
        self.mesgs = [
            '1 Primary recoil ranges and summaries of the initial and primary states of the primaries.',
            '2 Distributions of collision-event types.',
            '3 Statistical analyses of sets of cascades. Requires MAXRUN > 1.',
            '4 Distributions of the times of events and of particle energies.',
            '5 Analysis of replacement sequences and channeled trajectory segments.',
            '6 The distant interstitial - vacancy pair distribution.',
            '7 The analysis procedure SINGLE. See Input Record 13.',
            '8 The analysis procedure EXTRA. See Input Record 14.']
        self.widgets = []

        for t in self.mesgs:
            v = tk.IntVar(self)
            c = tk.Checkbutton(self,
                               text=t,
                               wraplength=250,
                               variable=v, anchor='w', justify='left')
            self.widgets.append(c)
            self.checkvars.append(v)
            self.checks.append(c)

        self.enabled = True

        self.layout()

    def layout(self, mode=0):
        prow = 0
        for i, c in enumerate(self.widgets):
            if i < 6 or mode == 0:
                c.grid(row=prow, column=0, sticky=tk.E + tk.W)
                prow += 1
            else:  # if i >= and mode != 0
                c.grid_forget()

    def bind_with_balloonhelp(self, b):
        b.bind(self, balloonHelp='Controls various output options')

    def set(self, d):
        for var, v in zip(self.checkvars, d):
            # True is set as 1, False is 0
            var.set(v)

    def get(self):
        return [var.get() == 1 for var in self.checkvars]

    def get_nostatechk(self):
        return self.get()

    def clear(self):
        self.set(guidata.outp_inform_default)

    def validate(self):
        return None

    def enable(self):
        for w in self.checks:
            w.config(state=tk.NORMAL)
        self.enabled = True

    def disable(self):
        for w in self.checks:
            w.config(state=tk.DISABLED)
        self.enabled = False

    def is_disabled(self):
        return not self.enabled


class Outp(
        tk.Frame,
        gui_abstract.GUIAbstract,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):

    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)
        gui_abstract.GUIAbstract.__init__(self,
                                          defaultparam=guidata.outp_default)

        # DRNG
        self.drnglabel = tk.Label(self, text='DRNG')
        self.drng = validateentry.Vec3d(self)
        self.add_widget('drng', self.drng)
        self.drng.config(width=10)
        self.drnglabelballoonhelp = 'Histogram Channel Widths'
        self.drngballoonhelps = [
            '''\
The initial channel width for primary recoil range distributions
in units of BASE. The program adjusts the actual channel width
as necessary to contain all the entries.''',
            '''\
The channel width for distributions of distant interstitial - vacancy
pair separations in units of BASE. No adjustment of this channel
width occurs.''',
            '''\
The initial channel width for time distributions in fs.
The program adjusts the actual channel width as necessary
to contain all the entries.''']

        # LCS
        self.lcslabel = tk.Label(self, text='LCS')
        self.lcs = validateentry.Vec2Int(self)
        self.add_widget('lcs', self.lcs)
        self.lcs.config(width=10)
        self.lcsballoonhelp = '''\
Controls the analysis of replacement collision sequences.
LCS(1) = 0: LCS directions are ignored, but their lengths are analyzed,
  an option advised for crystals of all but the highest symmetry. It is
  imposed for amorphous media.
LCS(1) < 0: LCS directions are kept as generated. Sequences with
  lengths < |LCS(1)| are omitted from the analysis.
LCS(1) > 0: LCS directions are combined into a reduced form. The rules
  for the reduction are discussed in Chapter 8. LCSs with lengths < LCS(1)
  are omitted.
LCS(2): If LCS(2) < LLCS, the maximum distinguishable LCS length is
  LCS(2). If LCS(2) >= LLCS, the maximum distinguishable LCS length
  is LLCS - 1.'''

        # TRACE
        self.tracelabel = tk.Label(self, text='TRACE')
        self.trace = validateentry.Vec3Int(self)
        self.add_widget('trace', self.trace)
        self.trace.config(width=10)
        self.traceballoonhelp = '''\
Controls the listing of trajectory details:
TRACE = 0, 0, 0: No trajectory listings are produced.
TRACE = -1, 0, 0: All collisions are reported in all cascades.
TRACE = N, 0, 0: All collisions in cascade N are reported.
TRACE = N, M, 0: All collisions in cascade N involving projectile M are reported.
TRACE = N, M, L: Collisions in cascade N from collision M through collision L are reported.'''

        # LOOK
        self.looklabel = tk.Label(self, text='LOOK')
        self.lookoptions = [
            (0, '0: No description of individual cascades'),
            (1, '1: A summary of cascade properties, with no details ..'),
            (2, '2: Adds escaping atoms, truncated trajetories, ...'),
            (3, '3: Adds vacant sites and interstitials.'),
            (4, '4: Adds complete description of displacement cascade')]
        self.look = codedoptionmenu.CodedOptionMenu(self,
                                                    self.lookoptions)
        self.add_widget('look', self.look)
        self.look.config(width=20, anchor='w')
        self.lookballoonhelp = 'Controls the output describing a single collision cascade'

        # GREX
        self.grexlabel = tk.Label(self, text='GREX')
        self.grexoptions = [
            (False, 'F: Individual cascade damage'),
            (True, 'T: Accumulate cascade damage')]
        self.grex = codedoptionmenu.CodedOptionMenu(self,
                                                    self.grexoptions)
        self.add_widget('grex', self.grex)
        self.grex.config(width=20, anchor='w')
        self.grexballoonhelp = 'Configure if damage is accumulated from one cascade to another'

        # INFORM
        self.informfrm = tk.LabelFrame(self, text='INFORM')
        self.inform = OutpInform(self.informfrm)
        self.add_widget('inform', self.inform)

        # initialize widget contents
        self.clear()

        # layout widget
        self.layout()

    def layout(self, mode=0):
        prow = 0

        self.looklabel.grid(row=prow, column=0, sticky=tk.E)
        self.look.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        self.drnglabel.grid(row=prow, column=0, sticky=tk.E)
        self.drng.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        if mode == 0:
            self.lcslabel.grid(row=prow, column=0, sticky=tk.E)
            self.lcs.grid(row=prow, column=1, sticky=tk.W)
            prow += 1
        else:
            self.lcslabel.grid_forget()
            self.lcs.grid_forget()

        if mode == 0:
            self.tracelabel.grid(row=prow, column=0, sticky=tk.E)
            self.trace.grid(row=prow, column=1, sticky=tk.W)
            prow += 1
        else:
            self.tracelabel.grid_forget()
            self.trace.grid_forget()

        self.grexlabel.grid(row=prow, column=0, sticky=tk.E)
        self.grex.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        self.grid_columnconfigure(1, weight=1)

        self._layout_informfrm(mode)
        self.informfrm.grid(row=prow, column=0, columnspan=2,
                            sticky=tk.EW)

    def _layout_informfrm(self, mode):
        self.inform.layout(mode)
        self.inform.pack()

    def bind_with_balloonhelp(self, b):
        b.bind(self.drnglabel, balloonHelp=self.drnglabelballoonhelp)
        for w, h in zip(self.drng.array, self.drngballoonhelps):
            b.bind(w, balloonHelp=h)
        b.bind(self.lcslabel, balloonHelp=self.lcsballoonhelp)
        b.bind(self.lcs, balloonHelp=self.lcsballoonhelp)
        b.bind(self.tracelabel, balloonHelp=self.traceballoonhelp)
        b.bind(self.trace, balloonHelp=self.traceballoonhelp)
        b.bind(self.looklabel, balloonHelp=self.lookballoonhelp)
        b.bind(self.look, balloonHelp=self.lookballoonhelp)
        b.bind(self.grexlabel, balloonHelp=self.grexballoonhelp)
        b.bind(self.grex, balloonHelp=self.grexballoonhelp)

        self.inform.bind_with_balloonhelp(b)
