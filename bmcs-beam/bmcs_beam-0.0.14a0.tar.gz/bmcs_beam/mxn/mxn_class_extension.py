'''
Created on 14. 4. 2014

@author: Vancikv
'''

from traits.api import \
    Property, Button, Str, Event, WeakRef

from .matresdev.db.simdb import \
    SimDBClassExt

from bmcs_beam.mxn.mxn_tree_node import \
    MxNTreeNode

from traitsui.api import \
    View, Item, EnumEditor, Group

from bmcs_beam.mxn.mxn_class_extension_handler import \
    MxNClassExtHandler

class MxNClassExt(SimDBClassExt, MxNTreeNode):
    node_name = 'Material database'

    def __setitem__(self, key, value):
        value.key = key
        value.node_name = key
        super(MxNClassExt, self).__setitem__(key, value)

    new_material = Button(label='Add new material')
    def _new_material_fired(self):
        pass

    del_material = Button(label='Delete material')
    def _del_material_fired(self):
        pass

    save_database = Button(label='Save database')
    def _save_database_fired(self):
        for inst in list(self.instances.values()):
            inst.save()

    tree_node_list = Property(depends_on='instances')
    def _get_tree_node_list(self):
        for inst in self.inst_list:
            inst.node_name = inst.key
        return self.inst_list

    instance_keys = Property()
    def _get_instance_keys(self):
        return list(self.instances.keys())

    chosen_instance = Str()
    def _chosen_instance_default(self):
        return list(self.instances.keys())[0]

    tree_view = View(Item('new_material', show_label=False),
                     Item('save_database', show_label=False),
                     Group(
                     Item('chosen_instance', editor=EnumEditor(name='instance_keys'),
                          show_label=False),
                     Item('del_material', show_label=False)
                           )
                     , handler=MxNClassExtHandler())

