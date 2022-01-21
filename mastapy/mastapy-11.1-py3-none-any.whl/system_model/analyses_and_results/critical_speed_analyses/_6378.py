'''_6378.py

TorqueConverterCriticalSpeedAnalysis
'''


from mastapy.system_model.part_model.couplings import _2347
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6692
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6296
from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'TorqueConverterCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterCriticalSpeedAnalysis',)


class TorqueConverterCriticalSpeedAnalysis(_6296.CouplingCriticalSpeedAnalysis):
    '''TorqueConverterCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _TORQUE_CONVERTER_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorqueConverterCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2347.TorqueConverter':
        '''TorqueConverter: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2347.TorqueConverter)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_load_case(self) -> '_6692.TorqueConverterLoadCase':
        '''TorqueConverterLoadCase: 'AssemblyLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6692.TorqueConverterLoadCase)(self.wrapped.AssemblyLoadCase) if self.wrapped.AssemblyLoadCase is not None else None
