'''_6770.py

CVTPulleyAdvancedTimeSteppingAnalysisForModulation
'''


from mastapy.system_model.part_model.couplings import _2327
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.system_deflections import _2468
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6817
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'CVTPulleyAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulleyAdvancedTimeSteppingAnalysisForModulation',)


class CVTPulleyAdvancedTimeSteppingAnalysisForModulation(_6817.PulleyAdvancedTimeSteppingAnalysisForModulation):
    '''CVTPulleyAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulleyAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2327.CVTPulley':
        '''CVTPulley: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2327.CVTPulley)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def system_deflection_results(self) -> '_2468.CVTPulleySystemDeflection':
        '''CVTPulleySystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2468.CVTPulleySystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None
