'''_5389.py

DutyCycle
'''


from typing import List

from mastapy.system_model.analyses_and_results.load_case_groups import _5392, _5385
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads.duty_cycle_definition import _6720
from mastapy.system_model.analyses_and_results.static_loads import _6519
from mastapy._internal.python_net import python_net_import

_DUTY_CYCLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.LoadCaseGroups', 'DutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('DutyCycle',)


class DutyCycle(_5385.AbstractStaticLoadCaseGroup):
    '''DutyCycle

    This is a mastapy class.
    '''

    TYPE = _DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def duty_cycle_design_states(self) -> 'List[_5392.SubGroupInSingleDesignState]':
        '''List[SubGroupInSingleDesignState]: 'DutyCycleDesignStates' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.DutyCycleDesignStates, constructor.new(_5392.SubGroupInSingleDesignState))
        return value

    @property
    def time_series_importer(self) -> '_6720.TimeSeriesImporter':
        '''TimeSeriesImporter: 'TimeSeriesImporter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6720.TimeSeriesImporter)(self.wrapped.TimeSeriesImporter) if self.wrapped.TimeSeriesImporter is not None else None

    def convert_to_condensed_parametric_study_tool_duty_cycle(self):
        ''' 'ConvertToCondensedParametricStudyToolDutyCycle' is the original name of this method.'''

        self.wrapped.ConvertToCondensedParametricStudyToolDutyCycle()

    def add_static_load(self, static_load: '_6519.StaticLoadCase'):
        ''' 'AddStaticLoad' is the original name of this method.

        Args:
            static_load (mastapy.system_model.analyses_and_results.static_loads.StaticLoadCase)
        '''

        self.wrapped.AddStaticLoad(static_load.wrapped if static_load else None)

    def remove_static_load(self, static_load: '_6519.StaticLoadCase'):
        ''' 'RemoveStaticLoad' is the original name of this method.

        Args:
            static_load (mastapy.system_model.analyses_and_results.static_loads.StaticLoadCase)
        '''

        self.wrapped.RemoveStaticLoad(static_load.wrapped if static_load else None)

    def remove_design_state_sub_group(self, sub_group: '_5392.SubGroupInSingleDesignState'):
        ''' 'RemoveDesignStateSubGroup' is the original name of this method.

        Args:
            sub_group (mastapy.system_model.analyses_and_results.load_case_groups.SubGroupInSingleDesignState)
        '''

        self.wrapped.RemoveDesignStateSubGroup(sub_group.wrapped if sub_group else None)

    def delete(self):
        ''' 'Delete' is the original name of this method.'''

        self.wrapped.Delete()
