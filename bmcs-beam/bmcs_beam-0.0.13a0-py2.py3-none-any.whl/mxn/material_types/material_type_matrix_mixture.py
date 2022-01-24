'''
Created on Aug 23, 2012

@author: rch
'''

from bmcs_beam.mxn.matrix_laws import \
    MatrixLawBilinear, MatrixLawBlock, \
    MatrixLawLinear, MatrixLawQuad, \
    MatrixLawQuadratic, MatrixLawBase
from bmcs_beam.mxn.mxn_class_extension import \
    MxNClassExt
from traits.api import \
    Property, cached_property, Dict, Str, \
    Float
from traitsui.api import \
    View, Item, EnumEditor

from .material_type_base import \
    MaterialTypeBase
from .material_type_handler import \
    MaterialTypeHandler


class MTMatrixMixture(MaterialTypeBase):
    '''Base class for concrete constitutive laws.'''

    f_ck = Float(55.7, auto_set=False, enter_set=True,
                 law_input=True)
    '''Ultimate compression stress  [MPa]
    '''

    eps_c_u = Float(0.0033, auto_set=False, enter_set=True,
                    law_input=True)
    '''Strain at failure of the matrix in compression [-]
    '''

    E_c = Float(28e+3, auto_set=False, enter_set=True,
                law_input=True)

    mtrl_laws = Dict((Str, MatrixLawBase))

    def _mtrl_laws_default(self):
        basic_laws = {'bilinear':
                      MatrixLawBilinear(f_ck=55.7, eps_c_u=0.0033),
                      'constant':
                      MatrixLawBlock(f_ck=55.7, eps_c_u=0.0033,
                                     high_strength_level=50.0, E_c=28e+3),
                      'linear':
                      MatrixLawLinear(),
                      'quad':
                      MatrixLawQuad(f_ck=55.7, eps_c_u=0.0033,
                                    high_strength_level=50.0, E_c=28e+3),
                      'quadratic':
                      MatrixLawQuadratic(f_ck=55.7, eps_c_u=0.0033,
                                         high_strength_level=50.0, E_c=28e+3)
                      }
        return basic_laws

    possible_laws = {'bilinear': MatrixLawBilinear, 'constant': MatrixLawBlock,
                     'linear': MatrixLawLinear, 'quad': MatrixLawQuad,
                     'quadratic': MatrixLawQuadratic}

    named_mtrl_laws = Property(depends_on='mtrl_laws,+law_input')

    @cached_property
    def _get_named_mtrl_laws(self):
        for key, mtrl_law in list(self.mtrl_laws.items()):
            mtrl_law.node_name = key
            mtrl_law.f_ck = self.f_ck
            mtrl_law.eps_c_u = self.eps_c_u
            mtrl_law.E_c = self.E_c
        return self.mtrl_laws

    #=========================================================================
    # UI-related functionality
    #=========================================================================

    tree_view = View(Item('f_ck'),
                     Item('eps_c_u'),
                     Item('E_c'),
                     Item('new_law', show_label=False),
                     Item('chosen_law',
                          editor=EnumEditor(name='law_keys'),
                          show_label=False),
                     Item('del_law', show_label=False),
                     handler=MaterialTypeHandler()
                     )

MTMatrixMixture.db = MxNClassExt(
    klass=MTMatrixMixture,
    verbose='io',
    node_name='Matrix mixtures'
)

if MTMatrixMixture.db.get('default_mixture', None):
    del MTMatrixMixture.db['default_mixture']
MTMatrixMixture.db['default_mixture'] = MTMatrixMixture()
