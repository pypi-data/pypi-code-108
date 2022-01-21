'''_6850.py

UnbalancedMassAdvancedTimeSteppingAnalysisForModulation
'''


from mastapy.system_model.part_model import _2218
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6699
from mastapy.system_model.analyses_and_results.system_deflections import _2569
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6851
from mastapy._internal.python_net import python_net_import

_UNBALANCED_MASS_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'UnbalancedMassAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('UnbalancedMassAdvancedTimeSteppingAnalysisForModulation',)


class UnbalancedMassAdvancedTimeSteppingAnalysisForModulation(_6851.VirtualComponentAdvancedTimeSteppingAnalysisForModulation):
    '''UnbalancedMassAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _UNBALANCED_MASS_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'UnbalancedMassAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2218.UnbalancedMass':
        '''UnbalancedMass: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2218.UnbalancedMass)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6699.UnbalancedMassLoadCase':
        '''UnbalancedMassLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6699.UnbalancedMassLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2569.UnbalancedMassSystemDeflection':
        '''UnbalancedMassSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2569.UnbalancedMassSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None
