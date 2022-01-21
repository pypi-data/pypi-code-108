'''_6648.py

PartToPartShearCouplingHalfLoadCase
'''


from mastapy.system_model.part_model.couplings import _2329
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6566
from mastapy._internal.python_net import python_net_import

_PART_TO_PART_SHEAR_COUPLING_HALF_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'PartToPartShearCouplingHalfLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('PartToPartShearCouplingHalfLoadCase',)


class PartToPartShearCouplingHalfLoadCase(_6566.CouplingHalfLoadCase):
    '''PartToPartShearCouplingHalfLoadCase

    This is a mastapy class.
    '''

    TYPE = _PART_TO_PART_SHEAR_COUPLING_HALF_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartToPartShearCouplingHalfLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2329.PartToPartShearCouplingHalf':
        '''PartToPartShearCouplingHalf: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2329.PartToPartShearCouplingHalf)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
