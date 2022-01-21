'''_6520.py

TimeSeriesLoadCase
'''


from typing import Optional

from mastapy.system_model.analyses_and_results import _2379, _2360
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5187
from mastapy.system_model.analyses_and_results.load_case_groups import _5396
from mastapy.system_model.analyses_and_results.static_loads import _6532, _6518
from mastapy._internal.python_net import python_net_import

_TIME_SERIES_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'TimeSeriesLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('TimeSeriesLoadCase',)


class TimeSeriesLoadCase(_6518.LoadCase):
    '''TimeSeriesLoadCase

    This is a mastapy class.
    '''

    TYPE = _TIME_SERIES_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TimeSeriesLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def multibody_dynamics_analysis(self) -> '_2379.MultibodyDynamicsAnalysis':
        '''MultibodyDynamicsAnalysis: 'MultibodyDynamicsAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2379.MultibodyDynamicsAnalysis)(self.wrapped.MultibodyDynamicsAnalysis) if self.wrapped.MultibodyDynamicsAnalysis is not None else None

    @property
    def duration_for_rating(self) -> 'float':
        '''float: 'DurationForRating' is the original name of this property.'''

        return self.wrapped.DurationForRating

    @duration_for_rating.setter
    def duration_for_rating(self, value: 'float'):
        self.wrapped.DurationForRating = float(value) if value else 0.0

    @property
    def driva_analysis_options(self) -> '_5187.MBDAnalysisOptions':
        '''MBDAnalysisOptions: 'DRIVAAnalysisOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5187.MBDAnalysisOptions)(self.wrapped.DRIVAAnalysisOptions) if self.wrapped.DRIVAAnalysisOptions is not None else None

    @property
    def time_series_load_case_group(self) -> '_5396.TimeSeriesLoadCaseGroup':
        '''TimeSeriesLoadCaseGroup: 'TimeSeriesLoadCaseGroup' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_5396.TimeSeriesLoadCaseGroup)(self.wrapped.TimeSeriesLoadCaseGroup) if self.wrapped.TimeSeriesLoadCaseGroup is not None else None

    def analysis_of(self, analysis_type: '_6532.AnalysisType') -> '_2360.SingleAnalysis':
        ''' 'AnalysisOf' is the original name of this method.

        Args:
            analysis_type (mastapy.system_model.analyses_and_results.static_loads.AnalysisType)

        Returns:
            mastapy.system_model.analyses_and_results.SingleAnalysis
        '''

        analysis_type = conversion.mp_to_pn_enum(analysis_type)
        method_result = self.wrapped.AnalysisOf(analysis_type)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def duplicate(self, new_load_case_group: '_5396.TimeSeriesLoadCaseGroup', name: Optional['str'] = 'None') -> 'TimeSeriesLoadCase':
        ''' 'Duplicate' is the original name of this method.

        Args:
            new_load_case_group (mastapy.system_model.analyses_and_results.load_case_groups.TimeSeriesLoadCaseGroup)
            name (str, optional)

        Returns:
            mastapy.system_model.analyses_and_results.static_loads.TimeSeriesLoadCase
        '''

        name = str(name)
        method_result = self.wrapped.Duplicate(new_load_case_group.wrapped if new_load_case_group else None, name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
