import tkinter as tk

from . import layoutmode
from . import balloonhelp

from . import tktool

from . import scon
from . import guidata


class SiteElem(tk.Frame,
               layoutmode.LayoutModeImplement,
               balloonhelp.BalloonHelpImplement):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        # RZ (position of site in repects of a, b, c axis)
        self.rzlabel = tk.Label(self, text='RZ:')
        self.rz = tktool.validateentry.Vec3d(self)
        self.rz.config(width=10)
        self.rzballoonhelp = '''\
The position vectors of each unique site in the elementary crystal unit
of the current layer. (RZ)'''

        # ATOM.LOCK
        # options are
        # 1, 2, ... scon.kind : (single atom with atom number)
        # 0: full vacancy
        # -1: multiple atom and vacancy site (enable ... array)
        options_atom = [(i, '{0:d}: Atom {0:d} only'.format(i))
                        for i in range(1, scon.kind+1)]

        self.lockoption = options_atom
        self.lockoption.append((0, '0: Vacancy'))
        self.lockoption.append((-1, '-1: Multiple atoms'))
        self.locklabel = tk.Label(self, text='LOCK:')
        self.lock = tktool.codedoptionmenu.CodedOptionMenu(self, self.lockoption)
        self.lock.config(anchor='w')
        # reset option in order to introduce command when menu is selected
        self.lock.set_new_option(self.lockoption, command=self._lock_action)
        self.lockballoonhelp = 'Assignment of atoms to the crystal lattice sites (LOCK)'

        # ATOM.ORDER
        # orders[0, 1, ..., scon.kind-1] atom i ratio
        # orders[scon.kind] = vacancy ratio
        self.orderframe = tk.Frame(self)
        self.orders = []
        for i in range(scon.kind):
            order = tktool.validateentry.Double(self.orderframe)
            order.config(width=6)
            self.orders.append(order)
        # Vacancy
        self.orderframe2 = tk.Frame(self.orderframe)
        self.vacancylabel = tk.Label(self.orderframe2, text='VACANCY')
        self.vacancy = tktool.validateentry.Double(self.orderframe2)
        self.vacancy.config(width=6)
        self.orders.append(self.vacancy)
        # adjust order button
        self.adjust = tk.Button(self.orderframe2, text='adjust order',
                                command=self._adjust_action)

        self.orderlabel = tk.Label(self, text='ORDER:')

        self.orderframeballoonhelp = '''\
The fraction of lattice sites (ORDER).
  This frame is enabled when LOCK=-1.
  ADJUST button for normalize occupation and vacacy fraction.'''

        # ATOM.EBND
        self.ebndframe = tk.Frame(self)
        self.ebndlabel = tk.Label(self.ebndframe, text='&ATOM.EBND')
        self.ebnd = tktool.validateentry.Vec3d(self.ebndframe)
        self.ebnd.config(width='6')
        self.ebndballoonhelp = '''\
The energy parameters of the binding model in eV (EBND)'''

        self.clear()

        self.layout()

    def layout(self, mode=0):
        # toplevel widgets
        prow = 0
        self.rzlabel.grid(row=prow, column=0, sticky=tk.E)
        self.rz.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
        self.locklabel.grid(row=prow, column=0, sticky=tk.E)
        self.lock.grid(row=prow, column=1, sticky=tk.W+tk.E)
        prow += 1
        self.orderlabel.grid(row=prow, column=0, sticky=tk.W)
        self.orderframe.grid(row=prow, column=1, sticky=tk.E)
        prow += 1
        if mode == 0:
            self.ebndframe.grid(row=prow, column=0, columnspan=2,
                                sticky=tk.W+tk.E)
        else:
            self.ebndframe.grid_forget()

        # layout subwidget contents with _layout_WIDGET method
        self._layout_orderframe(mode)
        self._layout_ebndframe(mode)

    def _layout_orderframe(self, mode=0):
        # toplevel widget
        # layout order[0,1,2,...,-2] only, because order[-1] is vacancy
        # and shown in orderframe2
        for i, order in enumerate(self.orders[:-1]):
            order.grid(row=0, column=i)
        self.orderframe2.grid(row=1, column=0, columnspan=len(self.orders)-1)

        # layout subwidget contents with _layout_WIDGET method
        self._layout_orderframe2(mode)

    def _layout_orderframe2(self, mode=0):
        self.vacancylabel.grid(row=0, column=0, sticky=tk.E)
        self.vacancy.grid(row=0, column=1, sticky=tk.W)
        self.adjust.grid(row=0, column=2)

    def _layout_ebndframe(self, mode=0):
        self.ebndlabel.pack(side=tk.LEFT)
        self.ebnd.pack(side=tk.LEFT)

    def bind_with_balloonhelp(self, b):
        b.bind(self.rz, balloonHelp=self.rzballoonhelp)
        b.bind(self.lock, balloonHelp=self.lockballoonhelp)
        b.bind(self.orderframe, balloonHelp=self.orderframeballoonhelp)
        b.bind(self.ebnd, balloonHelp=self.ebndballoonhelp)

    def set(self, d):
        self.rz.set(d.get('rz', guidata.site_elem_default['rz']))
        self.lock.set(d.get('lock', guidata.site_elem_default['lock']))
        if 'order' in d:
            for v, w in zip(d['order'], self.orders):
                w.set(v)
        self.set_order_state()
        self.ebnd.set(d.get('ebnd', guidata.site_elem_default['ebnd']))

    def get(self):
        d = {}
        d['rz'] = self.rz.get()
        d['lock'] = self.lock.get()
        if d['lock'] == -1:
            d['order'] = [w.get() for w in self.orders]
        d['ebnd'] = self.ebnd.get()
        return d

    def _lock_action(self, value):
        """action when lock widget is changed"""
        self.set_order_state()

    def _adjust_action(self):
        """actions when order value is changed"""
        self.adjust_order_value()

    def adjust_order_value(self):
        """normalize order values as sum orders = 1"""
        # calculate sum of
        try:
            vs = [w.get() for w in self.orders[:-1]]
            t = sum(vs)
            if 0 <= t <= 1.0:
                self.orders[-1].set(1.0 - t)
        except:
            pass

    def set_order_state(self):
        """set order value and state depending on self.lock"""
        l = self.lock.get()
        # l = 1, 2, ...
        if l > 0 and l <= scon.kind:
            for i, w in enumerate(self.orders):
                if i == l-1:
                    w.set(1.00)
                else:
                    w.set(0.00)
                w.config(state=tk.DISABLED)
            self.adjust.config(state=tk.DISABLED)
        # vacant
        elif l == 0:
            for w in self.orders[:-1]:
                w.set(0.00)
                w.config(state=tk.DISABLED)
            # vacancy widget
            self.orders[-1].set(1.00)
            self.orders[-1].config(state=tk.DISABLED)
            self.adjust.config(state=tk.DISABLED)
        # l == -1 enable all widget execpt vacancy
        elif l == -1:
            for w in self.orders[:-1]:
                # w.set(0.00)
                w.config(state=tk.NORMAL)
            # vacancy widget
            # self.orders[-1].set(1.00)
            self.orders[-1].config(state=tk.DISABLED)
            self.adjust.config(state=tk.NORMAL)

    def clear(self):
        self.set(guidata.site_elem_default)

    def validate(self):
        err = []
        for n, w in [
                ('rz', self.rz),
                ('ebnd', self.ebnd)]:
            e = w.validate()
            if e:
                err.append(e)
        return err if err else None

    def enable(self):
        self.rz.config(state=tk.NORMAL)
        self.lock.config(state=tk.NORMAL)
        self.ebnd.enable()
        self.set_order_state()

    def disable(self):
        self.rz.config(state=tk.DISABLED)
        self.lock.config(state=tk.DISABLED)
        for w in self.orders:
            w.config(state=tk.DISABLED)
        self.adjust.config(state=tk.DISABLED)
        self.ebnd.disable()
