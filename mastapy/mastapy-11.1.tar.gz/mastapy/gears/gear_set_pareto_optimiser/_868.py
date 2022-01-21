'''_868.py

FaceGearSetParetoOptimiser
'''


from typing import List

from mastapy._internal.python_net import python_net_import
from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.face import _952
from mastapy.gears.gear_set_pareto_optimiser import _872

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_FACE_GEAR_SET_PARETO_OPTIMISER = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'FaceGearSetParetoOptimiser')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearSetParetoOptimiser',)


class FaceGearSetParetoOptimiser(_872.GearSetParetoOptimiser):
    '''FaceGearSetParetoOptimiser

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_SET_PARETO_OPTIMISER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearSetParetoOptimiser.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def design_space_search_strategy(self) -> 'str':
        '''str: 'DesignSpaceSearchStrategy' is the original name of this property.'''

        return self.wrapped.DesignSpaceSearchStrategy.SelectedItemName

    @design_space_search_strategy.setter
    def design_space_search_strategy(self, value: 'str'):
        self.wrapped.DesignSpaceSearchStrategy.SetSelectedItem(str(value) if value else '')

    @property
    def design_space_search_strategy_duty_cycle(self) -> 'str':
        '''str: 'DesignSpaceSearchStrategyDutyCycle' is the original name of this property.'''

        return self.wrapped.DesignSpaceSearchStrategyDutyCycle.SelectedItemName

    @design_space_search_strategy_duty_cycle.setter
    def design_space_search_strategy_duty_cycle(self, value: 'str'):
        self.wrapped.DesignSpaceSearchStrategyDutyCycle.SetSelectedItem(str(value) if value else '')

    @property
    def selected_candidate_geometry(self) -> '_952.FaceGearSetDesign':
        '''FaceGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_952.FaceGearSetDesign)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def candidate_gear_sets(self) -> 'List[_952.FaceGearSetDesign]':
        '''List[FaceGearSetDesign]: 'CandidateGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CandidateGearSets, constructor.new(_952.FaceGearSetDesign))
        return value

    @property
    def all_candidate_gear_sets(self) -> 'List[_952.FaceGearSetDesign]':
        '''List[FaceGearSetDesign]: 'AllCandidateGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AllCandidateGearSets, constructor.new(_952.FaceGearSetDesign))
        return value
