'''
Created on 26. 6. 2014

@author: Vancikv
'''

import weakref
import copy

from bmcs_beam.mxn.constitutive_law import \
    CLBase
from bmcs_beam.mxn.mxn_tree_node import \
    MxNTreeNode
from traits.api import \
    Property, cached_property, Dict, Str, \
    on_trait_change, List, Button

from bmcs_beam.mxn.matresdev.db.simdb import \
    SimDBClass


class MaterialTypeBase(MxNTreeNode, SimDBClass):

    mtrl_laws = Dict((Str, CLBase))

    #=========================================================================
    # Management of backward links
    #=========================================================================

    state_link_lst = List(transient=True)
    '''List of backward links to objects using the fabric
    '''

    def _state_link_lst_default(self):
        return []

    @on_trait_change('+geo_input,+law_input')
    def notify_change(self):
        for link in self.state_link_lst:
            if link():
                link().material_changed = True

    def add_link(self, link_to_add):
        '''Adding a backward link to the list - to be called
        from objects using the fabric
        '''
        if link_to_add not in self.state_link_lst:
            self.state_link_lst.append(weakref.ref(link_to_add))

    def del_link(self, link_to_del):
        '''Removing a backward link from the list - to be called
        from objects using the fabric
        '''
        self.state_link_lst[:] = [
            link for link in self.state_link_lst if link() != link_to_del]

    #=========================================================================
    # UI-related functionality
    #=========================================================================

    new_law = Button(label='Add new law')

    def _new_material_fired(self):
        pass

    del_law = Button(label='Delete law')

    def _del_material_fired(self):
        pass

    law_keys = Property

    def _get_law_keys(self):
        return list(self.mtrl_laws.keys())

    chosen_law = Str()

    def _chosen_law_default(self):
        return list(self.mtrl_laws.keys())[0]

    tree_node_list = Property(depends_on='mtrl_laws')

    @cached_property
    def _get_tree_node_list(self):
        return list(self.named_mtrl_laws.values())

    @on_trait_change('node_name')
    def update_key(self):
        if self.key != self.node_name and self.key != '':
            old_key = self.key
            self.key = self.node_name
            self.db[self.node_name] = self
            self.save()
            del self.db[old_key]
