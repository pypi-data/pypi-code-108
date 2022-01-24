'''
Created on Aug 23, 2012

@author: rch
'''

from traits.api import \
    HasStrictTraits, Property, WeakRef, \
    cached_property, on_trait_change, List

from traitsui.api import \
    View, Item

import numpy as np

from bmcs_beam.mxn.mfn import MFnLineArray

import weakref


class CLBase(HasStrictTraits):

    '''Base class for Effective Crack Bridge Laws.'''

    def __init__(self, *args, **kw):
        super(HasStrictTraits, self).__init__(*args, **kw)

    def set_cparams(self, *args):
        for name, value in zip(self.cnames, args):
            setattr(self, name, value)

    arr = Property()

    def _get_arr(self):
        return self.eps_arr, self.sig_arr

    mfn = Property()

    def _get_mfn(self):
        return MFnLineArray(xdata=self.eps_arr,
                            ydata=self.sig_arr)

    mfn_vct = Property()

    def _get_mfn_vct(self):
        return np.vectorize(self.mfn.get_value, otypes=[np.float])

    def plot(self, fig):
        ax = fig.add_subplot(1, 1, 1)
        self.plot_ax(ax)

    def plot_ax(self, ax):
        ax.plot(*self.arr)

    def plot_custom(self, ax, color='blue', linestyle='-', linewidth=2, label='<unnamed>'):
        ax.plot(
            *self.arr, lw=linewidth, color=color, ls=linestyle, label=label)

    #=========================================================================
    # Management of backward links
    #=========================================================================

    state_link_lst = List(transient=True)
    '''List of backward links to objects using the fabric
    '''

    def _state_link_lst_default(self):
        return []

    @on_trait_change('+input')
    def notify_change(self):
        for link in self.state_link_lst:
            if link():
                link().law_changed = True

    def add_link(self, link_to_add):
        '''Adding a backward link to the list - to be called
        from objects using the law
        '''
        if link_to_add not in self.state_link_lst:
            self.state_link_lst.append(weakref.ref(link_to_add))

    def del_link(self, link_to_del):
        '''Removing a backward link from the list - to be called
        from objects using the law
        '''
        self.state_link_lst[:] = [
            link for link in self.state_link_lst if link() != link_to_del]

    def default_traits_view(self):

        input_traits = self.traits(input=lambda x: x != None)

        citems = [Item(name) for name in input_traits]
        return View(*citems,
                    buttons=['OK', 'Cancel']
                    )
