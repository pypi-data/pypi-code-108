'''_2523.py

PartToPartShearCouplingSystemDeflection
'''


from mastapy.system_model.analyses_and_results.system_deflections import _2521, _2466
from mastapy._internal import constructor
from mastapy.system_model.part_model.couplings import _2328
from mastapy.system_model.analyses_and_results.static_loads import _6649
from mastapy.system_model.analyses_and_results.power_flows import _3848
from mastapy._internal.python_net import python_net_import

_PART_TO_PART_SHEAR_COUPLING_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'PartToPartShearCouplingSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('PartToPartShearCouplingSystemDeflection',)


class PartToPartShearCouplingSystemDeflection(_2466.CouplingSystemDeflection):
    '''PartToPartShearCouplingSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _PART_TO_PART_SHEAR_COUPLING_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartToPartShearCouplingSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def part_to_part_shear_coupling_connection(self) -> '_2521.PartToPartShearCouplingConnectionSystemDeflection':
        '''PartToPartShearCouplingConnectionSystemDeflection: 'PartToPartShearCouplingConnection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2521.PartToPartShearCouplingConnectionSystemDeflection)(self.wrapped.PartToPartShearCouplingConnection) if self.wrapped.PartToPartShearCouplingConnection is not None else None

    @property
    def assembly_design(self) -> '_2328.PartToPartShearCoupling':
        '''PartToPartShearCoupling: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2328.PartToPartShearCoupling)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6649.PartToPartShearCouplingLoadCase':
        '''PartToPartShearCouplingLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6649.PartToPartShearCouplingLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None

    @property
    def power_flow_results(self) -> '_3848.PartToPartShearCouplingPowerFlow':
        '''PartToPartShearCouplingPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3848.PartToPartShearCouplingPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None
