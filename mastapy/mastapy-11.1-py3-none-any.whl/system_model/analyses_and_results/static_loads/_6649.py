'''_6649.py

PartToPartShearCouplingLoadCase
'''


from mastapy.system_model.part_model.couplings import _2328
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6567
from mastapy._internal.python_net import python_net_import

_PART_TO_PART_SHEAR_COUPLING_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'PartToPartShearCouplingLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('PartToPartShearCouplingLoadCase',)


class PartToPartShearCouplingLoadCase(_6567.CouplingLoadCase):
    '''PartToPartShearCouplingLoadCase

    This is a mastapy class.
    '''

    TYPE = _PART_TO_PART_SHEAR_COUPLING_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartToPartShearCouplingLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2328.PartToPartShearCoupling':
        '''PartToPartShearCoupling: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2328.PartToPartShearCoupling)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None
