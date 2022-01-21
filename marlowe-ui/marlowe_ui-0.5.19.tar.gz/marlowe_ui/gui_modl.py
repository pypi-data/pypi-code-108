import copy
import tkinter as tk

from . import guidata
from . import layoutmode
from . import balloonhelp
from . import gui_filepath

from .tktool import validateentry
from .tktool import codedoptionmenu


class Modl(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):

    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        # FILE
        self.files = [tk.StringVar(self) for i in range(5)]
        self.fileframe = tk.LabelFrame(self, text='FILE')
        filelabels = ['1', '2', '3', '4', '5']
        self.filewidgetsballonhelp = [
            '''Transfers data from Phase 1 to both Phase 2 and Phase 3:
  it is connected to the unit LAGER(1).''',
            '''Transfers data from Phase 1 to Phase 2 only:
  it is connected to the unit LAGER(2).''',
            '''Transfers data from Phase 2 to Phase 3:
  it is connected to the unit LAGER(3).''',
            '''Records the individual cascade data from Phase 2:
  it is connected to the unit LAGER(4).''',
            '''Records the output of Phase 3:
  it is connected to the unit LAGER(5).''']

        self.filewidgets = []
        for i in range(5):
            frame = tk.Frame(self.fileframe)
            label = tk.Label(frame, text=filelabels[i])
            filewidget = gui_filepath.Saveas(frame, textvariable=self.files[i])
            label.pack(side=tk.LEFT)
            filewidget.pack(side=tk.LEFT, expand=True, fill=tk.X)
            frame.pack(side=tk.TOP, expand=True, fill=tk.X)
            self.filewidgets.append(frame)

        # RDNML
        # It might be better to show at each correpond record

        # METRIC (1=AA, 2=nm)
        self.metricframe = tk.Frame(self)
        self.metriclabel = tk.Label(self.metricframe, text='METRIC')
        self.metricoptions = [(1, '1: Ang.'), (2, '2: nm')]
        self.metricwidget = codedoptionmenu.CodedOptionMenu(self.metricframe,
                                                            self.metricoptions)

        self.metricballoonhelp = 'Absolute distance units used in the program'
        self.metriclabel.pack(side=tk.LEFT)
        self.metricwidget.pack(side=tk.LEFT)

        # TRAM
        self.tramframe = tk.Frame(self)
        self.tramlabel = tk.Label(self.tramframe, text='TRAM')
        self.tramoptions = [(False, 'F: output as INTERNAL coord.'),
                            (True, 'T: output as EXTERNAL coord.')]
        self.tramwidget = codedoptionmenu.CodedOptionMenu(
            self.tramframe, self.tramoptions)
        self.tramballoonhelp = '''\
On output, vectors are transformed to external(T) or internal(F) coordinate'''
        self.tramlabel.pack(side=tk.LEFT)
        self.tramwidget.pack(side=tk.LEFT)

        # surface
        # moved to gui_surf.py

        # KLAY
        # this value is automatically decided by the number of layers
        # described in &XTAL record

        # NM
        self.nmvar = tk.IntVar(self, 4)
        self.nmframe = tk.Frame(self)
        self.nmlabel = tk.Label(self.nmframe, text='NM')
        self.nmwidget = validateentry.IntPositive(self.nmframe,
                                                  textvariable=self.nmvar, width=4)
        self.nmballoonhelp = '''\
The number of points in the numerical quadrature used
for the classical scattering integrals.'''

        self.nmlabel.pack(side=tk.LEFT)
        self.nmwidget.pack(side=tk.LEFT)

        # LORG (0~8)
        self.lorgframe = tk.Frame(self)
        self.lorglabel = tk.Label(self.lorgframe, text='LORG')
        self.lorgoptions = [
            (0, '0: No pairs of any kind are identified'),
            (1, '1: Replacements and close and near pairs are identified'),
            (2, '2: The remaining vacant sites and interstitial atoms are paired in so far as possible'),
            (3, '3: Like LORG = 1, but atoms may also be paired with internal or external target surfaces.'),
            (4, '4: Like LORG = 2, but atoms may also be paired with the target surfaces.'),
            (5, '5: Like LORG = 1, but pairing is restricted to defects of the same type.'),
            (6, '6: Like LORG = 2, but pairing is restricted to defects of the same type.'),
            (7, '7: Like LORG = 3, but pairing is restricted to defects of the same type.'),
            (8, '8: Like LORG = 4, but pairing is restricted to defects of the same type.')]  # 0,1,...,8
        self.lorgwidget = codedoptionmenu.CodedOptionMenu(
            self.lorgframe, self.lorgoptions)
        self.lorgwidget.config(width=20, anchor='w')
        self.lorgballoonhelp = '''\
Controls the rules for identifying pairs of displaced atoms
and vacated lattice sites in cascades'''

        self.lorglabel.pack(side=tk.LEFT)
        self.lorgwidget.pack(side=tk.LEFT)

        # ICHAN
        self.ichanframe = tk.LabelFrame(self, text='ICHAN')
        self.ichanlabels = ['1', '2', '3', '4']
        self.ichanvar = [tk.IntVar(self) for i in range(4)]
        self.ichanentries = []
        self.ichanframeballoonhelp = 'Controls trajectory truncation processes'
        for i in range(4):
            frame = tk.Frame(self.ichanframe)
            label = tk.Label(frame, text=self.ichanlabels[i])
            entry = validateentry.Int(
                frame, textvariable=self.ichanvar[i])
            self.ichanentries.append(entry)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.LEFT)
            frame.pack(side=tk.TOP)

        # DELTA
        self.deltaframe = tk.LabelFrame(self, text='DELTA')
        self.deltalabels = ['1', '2', '3', '4']
        self.deltavar = [tk.DoubleVar(self) for i in range(4)]
        self.deltaentries = []
        self.deltaframeballoonhelp = 'Controls various comparisons and truncations'
        for i in range(4):
            frame = tk.Frame(self.deltaframe)
            label = tk.Label(frame, text=self.deltalabels[i])
            entry = validateentry.Double(
                frame, textvariable=self.deltavar[i])
            self.deltaentries.append(entry)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.LEFT)
            frame.pack(side=tk.TOP)

        # TIM

        self.layout()

    def layout(self, mode=0):
        prow = 0
        if mode == 0:
            self.fileframe.grid(row=prow, column=0, sticky=tk.EW)
            prow += 1
        else:
            self.fileframe.grid_forget()

        self.metricframe.grid(row=prow, column=0, sticky=tk.EW)
        prow += 1

        self.tramframe.grid(row=prow, column=0, sticky=tk.EW)
        prow += 1

        if mode == 0:
            self.nmframe.grid(row=prow, column=0, sticky=tk.EW)
            prow += 1
            self.lorgframe.grid(row=prow, column=0, sticky=tk.EW)
            prow += 1
            self.ichanframe.grid(row=prow, column=0, sticky=tk.EW)
            prow += 1
            self.deltaframe.grid(row=prow, column=0, sticky=tk.EW)
            prow += 1
        else:
            self.nmframe.grid_forget()
            self.lorgframe.grid_forget()
            self.ichanframe.grid_forget()
            self.deltaframe.grid_forget()

    def bind_with_balloonhelp(self, b):
        for w, m in zip(self.filewidgets, self.filewidgetsballonhelp):
            b.bind(w, balloonHelp=m)
        b.bind(self.metricframe, balloonHelp=self.metricballoonhelp)
        b.bind(self.tramframe, balloonHelp=self.tramballoonhelp)
        b.bind(self.nmframe, balloonHelp=self.nmballoonhelp)
        b.bind(self.lorgframe, balloonHelp=self.lorgballoonhelp)
        b.bind(self.ichanframe, balloonHelp=self.ichanframeballoonhelp)

    def set(self, v):
        if 'file' in v:
            for i, w in zip(v['file'], self.files):
                if i is not None:
                    w.set(i)
                else:
                    w.set('')

        # metric
        if 'metric' in v:
            self.metricwidget.set(v['metric'])

        # tram
        if 'tram' in v:
            self.tramwidget.set(v['tram'])

        # surfce
        # klay

        # nm
        if 'nm' in v:
            self.nmvar.set(v['nm'])

        # lorg
        if 'lorg' in v:
            self.lorgwidget.set(v['lorg'])

        # ichan
        if 'ichan' in v:
            for s, d in zip(v['ichan'], self.ichanvar):
                d.set(s)

        # delta
        if 'delta' in v:
            for s, d in zip(v['delta'], self.deltavar):
                d.set(s)

    def get_file(self):
        a = []
        for w in self.files:
            s = w.get()
            # we need some operation to identify null entry
            s = s.strip()
            if s:
                a.append(s)
            else:
                a.append(None)
        return a

    def get(self):
        # It should be considered, why not d = {} ?
        d = copy.deepcopy(guidata.modl_default)
        # file
        d['file'] = self.get_file()
        # metric
        d['metric'] = self.metricwidget.get()
        # tram
        d['tram'] = self.tramwidget.get()

        # surfce
        # klay

        # nm
        d['nm'] = self.nmvar.get()

        # lorg
        d['lorg'] = self.lorgwidget.get()

        # ichan
        d['ichan'] = [w.get() for w in self.ichanvar]

        # ichan
        d['delta'] = [w.get() for w in self.deltavar]

        return d

    def clear(self):
        self.set(guidata.modl_default)

    def validate(self):
        err = []
        for i, w in enumerate(self.ichanentries):
            e = w.validate()
            if e:
                err.append(('ICHAN({0:d})'.format(i + 1), e))
        for i, w in enumerate(self.deltaentries):
            e = w.validate()
            if e:
                err.append(('DELTA({0:d})'.format(i + 1), e))
        return err if err else None
