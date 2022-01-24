'''
Created on 23. 4. 2014

@author: Vancikv
'''

from bmcs_beam.mxn.mxn_class_extension import \
    MxNClassExt
from bmcs_beam.mxn.reinf_laws import \
    ReinfLawBase, ReinfLawSteel
from traits.api import \
    Property, cached_property, Dict, Str, \
    Float
from traitsui.api import \
    View, Item, EnumEditor

from .material_type_base import \
    MaterialTypeBase
from .material_type_handler import \
    MaterialTypeHandler


class MTReinfBar(MaterialTypeBase):

    area = Float(0.0000785, auto_set=False, enter_set=True, geo_input=True)
    '''Cross section area [m**2]'''

    mtrl_laws = Dict((Str, ReinfLawBase))

    def _mtrl_laws_default(self):
        basic_laws = {'steel':
                      ReinfLawSteel(f_yk=500., E_s=200000., eps_u=0.025),
                      }
        return basic_laws

    possible_laws = {'steel': ReinfLawSteel}

    named_mtrl_laws = Property(depends_on='mtrl_laws')

    @cached_property
    def _get_named_mtrl_laws(self):
        for key, mtrl_law in list(self.mtrl_laws.items()):
            mtrl_law.node_name = key
        return self.mtrl_laws

    #=========================================================================
    # UI-related functionality
    #=========================================================================

    tree_view = View(Item('area'),
                     Item('new_law', show_label=False),
                     Item('chosen_law',
                          editor=EnumEditor(name='law_keys'),
                          show_label=False),
                     Item('del_law', show_label=False),
                     handler=MaterialTypeHandler()
                     )

MTReinfBar.db = MxNClassExt(
    klass=MTReinfBar,
    verbose='io',
    node_name='Reinforcement bars'
)

if MTReinfBar.db.get('bar_d10', None):
    del MTReinfBar.db['bar_d10']
MTReinfBar.db['bar_d10'] = MTReinfBar(area=0.0000785)
