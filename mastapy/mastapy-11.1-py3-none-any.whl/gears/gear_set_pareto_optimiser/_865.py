'''_865.py

CylindricalGearSetParetoOptimiser
'''


from typing import List

from mastapy._internal.python_net import python_net_import
from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.cylindrical import _984, _995
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_set_pareto_optimiser import _872

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_CYLINDRICAL_GEAR_SET_PARETO_OPTIMISER = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'CylindricalGearSetParetoOptimiser')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetParetoOptimiser',)


class CylindricalGearSetParetoOptimiser(_872.GearSetParetoOptimiser):
    '''CylindricalGearSetParetoOptimiser

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_PARETO_OPTIMISER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetParetoOptimiser.TYPE'):
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
    def selected_candidate_geometry(self) -> '_984.CylindricalGearSetDesign':
        '''CylindricalGearSetDesign: 'SelectedCandidateGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _984.CylindricalGearSetDesign.TYPE not in self.wrapped.SelectedCandidateGeometry.__class__.__mro__:
            raise CastException('Failed to cast selected_candidate_geometry to CylindricalGearSetDesign. Expected: {}.'.format(self.wrapped.SelectedCandidateGeometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SelectedCandidateGeometry.__class__)(self.wrapped.SelectedCandidateGeometry) if self.wrapped.SelectedCandidateGeometry is not None else None

    @property
    def candidate_gear_sets(self) -> 'List[_984.CylindricalGearSetDesign]':
        '''List[CylindricalGearSetDesign]: 'CandidateGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CandidateGearSets, constructor.new(_984.CylindricalGearSetDesign))
        return value

    @property
    def all_candidate_gear_sets(self) -> 'List[_984.CylindricalGearSetDesign]':
        '''List[CylindricalGearSetDesign]: 'AllCandidateGearSets' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AllCandidateGearSets, constructor.new(_984.CylindricalGearSetDesign))
        return value
