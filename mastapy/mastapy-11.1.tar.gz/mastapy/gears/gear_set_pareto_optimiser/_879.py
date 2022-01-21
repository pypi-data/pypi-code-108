'''_879.py

MicroGeometryGearSetDesignSpaceSearch
'''


from mastapy._internal.python_net import python_net_import
from mastapy._internal import constructor
from mastapy.gears.gear_set_pareto_optimiser import _876

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_MICRO_GEOMETRY_GEAR_SET_DESIGN_SPACE_SEARCH = python_net_import('SMT.MastaAPI.Gears.GearSetParetoOptimiser', 'MicroGeometryGearSetDesignSpaceSearch')


__docformat__ = 'restructuredtext en'
__all__ = ('MicroGeometryGearSetDesignSpaceSearch',)


class MicroGeometryGearSetDesignSpaceSearch(_876.MicroGeometryDesignSpaceSearch):
    '''MicroGeometryGearSetDesignSpaceSearch

    This is a mastapy class.
    '''

    TYPE = _MICRO_GEOMETRY_GEAR_SET_DESIGN_SPACE_SEARCH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MicroGeometryGearSetDesignSpaceSearch.TYPE'):
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
