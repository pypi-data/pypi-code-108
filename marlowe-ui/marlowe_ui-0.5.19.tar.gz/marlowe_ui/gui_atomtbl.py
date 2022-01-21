import tkinter as tk

from . import scon
from . import guidata
from . import layoutmode
from . import balloonhelp

from .physics import element as elem

from .tktool import validateentry
from .tktool import truncatedentry


class AtomTbl(
        tk.Frame,
        layoutmode.LayoutModeImplement,
        balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None, ntype=1, *args, **kw):
        tk.Frame.__init__(self, master)

        # number of valid atoms
        self.ntypefrm = tk.Frame(self)
        self.ntypelabel = tk.Label(self.ntypefrm, text='Num. of Species')
        self.ntypevar = tk.IntVar(self)

        self.ntype = tk.Spinbox(self.ntypefrm, textvariable=self.ntypevar,
                                values=list(range(0, scon.kind+1)),
                                command=self.ntype_action)
        self.ntype.config(width=5)

        # generate widgets
        self.widgets = []

        for i in range(scon.kind):
            # label
            label = tk.Label(self, text='{0:d}'.format(i+1))
            # type
            type = truncatedentry.TruncatedEntry(self, limitwidth=2, width=3)
            # fill button
            fill = tk.Button(self, text='>',
                             command=self.fill_by_type_skel(i))
            # z
            z = validateentry.DoublePositive(self, width=8)
            # w
            w = validateentry.DoublePositive(self, width=8)
            # inel
            inelval = tk.IntVar(self)
            inel = tk.Spinbox(self, values=(0, 1, 2, 3, 4),
                              textvariable=inelval, width=2)

            # equit
            equit = validateentry.DoublePositive(self, width=8)

            self.widgets.append({'label': label, 'type': type, 'fill': fill,
                                 'z': z, 'w': w, 'equit': equit,
                                 'inelval': inelval, 'inel': inel})

        # header
        self.header_type = tk.Label(self, text='TYPE')
        self.header_z = tk.Label(self, text='Z')
        self.header_w = tk.Label(self, text='W')
        self.header_inel = tk.Label(self, text='INEL')
        self.header_equit = tk.Label(self, text='EQUIT')

        # set valid entries
        self.clear()

        # layout
        self.layout()

    def layout(self, mode=0):
        # layout widgets with labels
        #
        #   | type | (fill button) | z | m | (pad) inel | equit
        # --+------+---------------+---+---+------------+------+
        #  1| ....

        prow = 0

        self._layout_ntypefrm(mode)  # inside ntypfrm
        self.ntypefrm.grid(row=prow, column=0, columnspan=8, sticky=tk.W)
        prow += 1

        inel_padx = (5, 0)

        self.header_type.grid(row=prow, column=1)
        self.header_z.grid(row=prow, column=3)
        self.header_w.grid(row=prow, column=4)
        if mode == 0:
            self.header_inel.grid(row=prow, column=5, padx=inel_padx)
            self.header_equit.grid(row=prow, column=6)
        else:
            self.header_inel.grid_forget()
            self.header_equit.grid_forget()
        prow += 1

        for i in range(scon.kind):
            # label
            self.widgets[i]['label'].grid(row=prow, column=0)
            self.widgets[i]['type'].grid(row=prow, column=1)
            self.widgets[i]['fill'].grid(row=prow, column=2)
            self.widgets[i]['z'].grid(row=prow, column=3)
            self.widgets[i]['w'].grid(row=prow, column=4)
            if mode == 0:
                self.widgets[i]['inel'].grid(row=prow, column=5, padx=inel_padx)
                self.widgets[i]['equit'].grid(row=prow, column=6)
            else:
                self.widgets[i]['inel'].grid_forget()
                self.widgets[i]['equit'].grid_forget()

            prow += 1

    def _layout_ntypefrm(self, mode=0):
        self.ntypelabel.pack(side=tk.LEFT)
        self.ntype.pack(side=tk.LEFT)

    def bind_with_balloonhelp(self, b):
        # KIND
        ntypemsg = 'The number of kinds of atom in the calculation (NTYPE)'
        b.bind(self.ntypelabel, balloonHelp=ntypemsg)
        b.bind(self.ntype, balloonHelp=ntypemsg)

        for w in self.widgets:
            # TYPE
            typemsg = 'Chemical Symbol (TYPE)'
            b.bind(w['type'], balloonHelp=typemsg)
            # Type -> param button
            pbuttonmsg = 'Fill Z and W by TYPE'
            b.bind(w['fill'], balloonHelp=pbuttonmsg)
            # Atomic Number
            zmsg = 'Atomic Number (Z)'
            b.bind(w['z'], balloonHelp=zmsg)
            # atomic mass
            wmsg = 'Atomic Mass (W)'
            b.bind(w['w'], balloonHelp=wmsg)

    def fill_by_type_skel(self, index):
        def fill_by_type():
            symbol = self.widgets[index]['type'].get()
            if symbol in elem.table_bysym:
                e = elem.table_bysym[symbol]
                self.widgets[index]['z'].set(e.z)
                self.widgets[index]['w'].set(e.mass)
        return fill_by_type

    def set(self, d):
        # decide ntype
        self.ntypevar.set(min(len(d), scon.kind))

        ntype = self.ntypevar.get()

        # valid widgets
        for i in range(ntype):
            self.widgets[i]['type'].set(
                d[i].get('type',
                         guidata.atom_elem_default['type']))
            self.widgets[i]['z'].set(
                d[i].get('z',
                         guidata.atom_elem_default['z']))
            self.widgets[i]['w'].set(
                d[i].get('w',
                         guidata.atom_elem_default['w']))
            self.widgets[i]['inelval'].set(
                d[i].get('inel',
                         guidata.atom_elem_default['inel']))
            self.widgets[i]['equit'].set(
                d[i].get('equit',
                         guidata.atom_elem_default['equit']))
            self._enable_elem(i)

        # invalid widgets
        for i in range(ntype, scon.kind):
            self.widgets[i]['type'].set(guidata.atom_elem_default['type'])
            self.widgets[i]['z'].set(guidata.atom_elem_default['z'])
            self.widgets[i]['w'].set(guidata.atom_elem_default['w'])
            self.widgets[i]['inelval'].set(guidata.atom_elem_default['inel'])
            self.widgets[i]['equit'].set(guidata.atom_elem_default['equit'])
            self._disable_elem(i)

    def _enable_elem(self, i):
        """enable i-th atom element"""
        self.widgets[i]['type'].config(state='normal')
        self.widgets[i]['fill'].config(state='normal')
        self.widgets[i]['z'].config(state='normal')
        self.widgets[i]['w'].config(state='normal')
        self.widgets[i]['inel'].config(state='normal')
        self.widgets[i]['equit'].config(state='normal')

    def _disable_elem(self, i):
        """enable i-th atom element"""
        self.widgets[i]['type'].config(state='disabled')
        self.widgets[i]['fill'].config(state='disabled')
        self.widgets[i]['z'].config(state='disabled')
        self.widgets[i]['w'].config(state='disabled')
        self.widgets[i]['inel'].config(state='disabled')
        self.widgets[i]['equit'].config(state='disabled')

    def _set_ntype(self, v):
        """change number of valid atom type widgets
        contents of atom type widgets are not changed.
        """
        # cap v range to [0..scon.kind]
        if v < 0:
            self.ntypevar.set(0)
        elif v > scon.nlay:
            self.ntypevar.set(scon.nlay)
        else:
            self.ntypevar.set(v)

        ntype = self.ntypevar.get()

        for i in range(scon.kind):
            if i < ntype:
                self._enable_elem(i)
            else:
                self._disable_elem(i)

    def ntype_action(self):
        """called when klay spinbox is changed"""
        self._set_ntype(self.ntypevar.get())

    def get(self):
        d = []
        for i in range(self.ntypevar.get()):
            d.append({
                'type': self.widgets[i]['type'].get(),
                'z': self.widgets[i]['z'].get(),
                'w': self.widgets[i]['w'].get(),
                'inel': self.widgets[i]['inelval'].get(),
                'equit': self.widgets[i]['equit'].get()})
        return d

    def clear(self):
        self.set(guidata.atom_tbl_default)

    @staticmethod
    def validate_wunit(w):
        """
        @param w widget mapping
        """
        err = []
        # test 'type' should be 1 or 2 characters
        try:
            v = w['type'].get()
            if len(v) < 1 or len(v) > 2:
                err.append(('type', 'char length is not valid'))
        except:
            err.append(('type', 'exception orruced'))
        # --- we need some code to turn face of 'type' widget

        # test z, w, equit, these should be positive floating value
        for name in ['z', 'w', 'equit']:
            e = w[name].validate()
            if e:
                err.append((name, e))

        # test inel, it should be range 0~4
        try:
            v = w['inelval'].get()
            if v < 0 or v > 4:
                err.append(('inel', 'out of range, should be [0..4]'))
        except:
            err.append(('inel', 'exception orruced'))
        # --- we need some code to turn face of 'inel' widget

        return err if err else None

    def validate(self):
        err = []
        for i in range(self.ntypevar.get()):
            e = self.validate_wunit(self.widgets[i])
            if e:
                err.append(('atom {0:d}'.format(i+1), e))

        return err if err else None
