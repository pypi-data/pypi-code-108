'''_5388.py

DesignState
'''


from typing import List, Optional

from mastapy.system_model.analyses_and_results.load_case_groups import _5386, _5387, _5383
from mastapy._internal import constructor, conversion
from mastapy.system_model.connections_and_sockets.couplings import _2084
from mastapy.system_model.part_model.gears import _2265
from mastapy.system_model.analyses_and_results.static_loads import _6519
from mastapy._internal.python_net import python_net_import

_DESIGN_STATE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.LoadCaseGroups', 'DesignState')


__docformat__ = 'restructuredtext en'
__all__ = ('DesignState',)


class DesignState(_5383.AbstractDesignStateLoadCaseGroup):
    '''DesignState

    This is a mastapy class.
    '''

    TYPE = _DESIGN_STATE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DesignState.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def clutches(self) -> 'List[_5386.ClutchEngagementStatus]':
        '''List[ClutchEngagementStatus]: 'Clutches' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Clutches, constructor.new(_5386.ClutchEngagementStatus))
        return value

    @property
    def concept_synchro_mounted_gears(self) -> 'List[_5387.ConceptSynchroGearEngagementStatus]':
        '''List[ConceptSynchroGearEngagementStatus]: 'ConceptSynchroMountedGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConceptSynchroMountedGears, constructor.new(_5387.ConceptSynchroGearEngagementStatus))
        return value

    def clutch_engagement_status_for(self, clutch_connection: '_2084.ClutchConnection') -> '_5386.ClutchEngagementStatus':
        ''' 'ClutchEngagementStatusFor' is the original name of this method.

        Args:
            clutch_connection (mastapy.system_model.connections_and_sockets.couplings.ClutchConnection)

        Returns:
            mastapy.system_model.analyses_and_results.load_case_groups.ClutchEngagementStatus
        '''

        method_result = self.wrapped.ClutchEngagementStatusFor(clutch_connection.wrapped if clutch_connection else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def concept_synchro_gear_engagement_status_for(self, gear: '_2265.CylindricalGear') -> '_5387.ConceptSynchroGearEngagementStatus':
        ''' 'ConceptSynchroGearEngagementStatusFor' is the original name of this method.

        Args:
            gear (mastapy.system_model.part_model.gears.CylindricalGear)

        Returns:
            mastapy.system_model.analyses_and_results.load_case_groups.ConceptSynchroGearEngagementStatus
        '''

        method_result = self.wrapped.ConceptSynchroGearEngagementStatusFor(gear.wrapped if gear else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def duplicate(self, duplicate_static_loads: Optional['bool'] = True) -> 'DesignState':
        ''' 'Duplicate' is the original name of this method.

        Args:
            duplicate_static_loads (bool, optional)

        Returns:
            mastapy.system_model.analyses_and_results.load_case_groups.DesignState
        '''

        duplicate_static_loads = bool(duplicate_static_loads)
        method_result = self.wrapped.Duplicate(duplicate_static_loads if duplicate_static_loads else False)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def create_load_case(self, name: Optional['str'] = 'New Static Load') -> '_6519.StaticLoadCase':
        ''' 'CreateLoadCase' is the original name of this method.

        Args:
            name (str, optional)

        Returns:
            mastapy.system_model.analyses_and_results.static_loads.StaticLoadCase
        '''

        name = str(name)
        method_result = self.wrapped.CreateLoadCase(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def delete(self):
        ''' 'Delete' is the original name of this method.'''

        self.wrapped.Delete()
