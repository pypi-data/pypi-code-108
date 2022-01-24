'''
Created on 23. 4. 2014

@author: Vancikv
'''

from bmcs_beam.mxn.mxn_class_extension import \
    MxNClassExt
from bmcs_beam.mxn.reinf_laws import \
    ReinfLawBase, ReinfLawBilinear, \
    ReinfLawCubic, ReinfLawFBM, \
    ReinfLawLinear
from traits.api import \
    Property, cached_property, Dict, Str, \
    Float, Trait
from traitsui.api import \
    View, Item, EnumEditor

from .material_type_base import \
    MaterialTypeBase
from .material_type_handler import \
    MaterialTypeHandler


class MTReinfFabric(MaterialTypeBase):

    A_roving = Float(0.461, auto_set=False, enter_set=True, geo_input=True)
    '''Cross section of one roving [mm**2]'''

    s_0 = Float(0.0083, auto_set=False, enter_set=True, geo_input=True)
    '''Distance between rovings oriented in 0-direction [m]'''

    s_90 = Float(0.02, auto_set=False, enter_set=True, geo_input=True)
    '''Distance between rovings oriented in 90-direction [m]'''

    mtrl_laws = Dict((Str, ReinfLawBase))

    def _mtrl_laws_default(self):
        basic_laws = {'bilinear':
                      ReinfLawBilinear(sig_tex_u=1216., eps_u=0.014,
                                       var_a=0.8, eps_el_fraction=0.0001),
                      'cubic':
                      ReinfLawCubic(sig_tex_u=1216., eps_u=0.016,
                                    var_a=-5e+6),
                      'fbm':
                      ReinfLawFBM(sig_tex_u=1216., eps_u=0.014,
                                  m=0.5),
                      'linear':
                      ReinfLawLinear(eps_u=0.014, E_tex=80000.),
                      }

        return basic_laws

    possible_laws = {'fbm': ReinfLawFBM, 'linear': ReinfLawLinear,
                     'cubic': ReinfLawCubic, 'bilinear': ReinfLawBilinear}

    named_mtrl_laws = Property(depends_on='mtrl_laws')

    @cached_property
    def _get_named_mtrl_laws(self):
        for key, mtrl_law in list(self.mtrl_laws.items()):
            mtrl_law.node_name = key
        return self.mtrl_laws

    #=========================================================================
    # UI-related functionality
    #=========================================================================

    tree_view = View(Item('A_roving'),
                     Item('s_0'),
                     Item('s_90'),
                     Item('new_law', show_label=False),
                     Item('chosen_law',
                          editor=EnumEditor(name='law_keys'),
                          show_label=False),
                     Item('del_law', show_label=False),
                     handler=MaterialTypeHandler()
                     )

MTReinfFabric.db = MxNClassExt(
    klass=MTReinfFabric,
    verbose='io',
    node_name='Reinforcement fabrics'
)

if MTReinfFabric.db.get('default_fabric', None):
    del MTReinfFabric.db['default_fabric']
MTReinfFabric.db['default_fabric'] = MTReinfFabric()
