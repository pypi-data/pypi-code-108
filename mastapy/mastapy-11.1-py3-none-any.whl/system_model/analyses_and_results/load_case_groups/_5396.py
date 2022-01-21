'''_5396.py

TimeSeriesLoadCaseGroup
'''


from typing import List

from mastapy.system_model.analyses_and_results.static_loads import _6520, _6532
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results import _2415, _2359
from mastapy.system_model.analyses_and_results.load_case_groups import _5384
from mastapy._internal.python_net import python_net_import

_TIME_SERIES_LOAD_CASE_GROUP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.LoadCaseGroups', 'TimeSeriesLoadCaseGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('TimeSeriesLoadCaseGroup',)


class TimeSeriesLoadCaseGroup(_5384.AbstractLoadCaseGroup):
    '''TimeSeriesLoadCaseGroup

    This is a mastapy class.
    '''

    TYPE = _TIME_SERIES_LOAD_CASE_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TimeSeriesLoadCaseGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_cases(self) -> 'List[_6520.TimeSeriesLoadCase]':
        '''List[TimeSeriesLoadCase]: 'LoadCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadCases, constructor.new(_6520.TimeSeriesLoadCase))
        return value

    @property
    def compound_multibody_dynamics_analysis(self) -> '_2415.CompoundMultibodyDynamicsAnalysis':
        '''CompoundMultibodyDynamicsAnalysis: 'CompoundMultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2415.CompoundMultibodyDynamicsAnalysis)(self.wrapped.CompoundMultibodyDynamicsAnalysis) if self.wrapped.CompoundMultibodyDynamicsAnalysis is not None else None

    def delete(self):
        ''' 'Delete' is the original name of this method.'''

        self.wrapped.Delete()

    def analysis_of(self, analysis_type: '_6532.AnalysisType') -> '_2359.CompoundAnalysis':
        ''' 'AnalysisOf' is the original name of this method.

        Args:
            analysis_type (mastapy.system_model.analyses_and_results.static_loads.AnalysisType)

        Returns:
            mastapy.system_model.analyses_and_results.CompoundAnalysis
        '''

        analysis_type = conversion.mp_to_pn_enum(analysis_type)
        method_result = self.wrapped.AnalysisOf(analysis_type)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
