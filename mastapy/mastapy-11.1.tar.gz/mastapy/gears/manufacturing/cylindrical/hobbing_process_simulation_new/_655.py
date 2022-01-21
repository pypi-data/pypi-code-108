'''_655.py

WormGrindingProcessGearShape
'''


from mastapy._internal import constructor
from mastapy.utility_gui.charts import (
    _1626, _1617, _1622, _1623
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _654
from mastapy._internal.python_net import python_net_import

_WORM_GRINDING_PROCESS_GEAR_SHAPE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'WormGrindingProcessGearShape')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGrindingProcessGearShape',)


class WormGrindingProcessGearShape(_654.WormGrindingProcessCalculation):
    '''WormGrindingProcessGearShape

    This is a mastapy class.
    '''

    TYPE = _WORM_GRINDING_PROCESS_GEAR_SHAPE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGrindingProcessGearShape.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def result_z_plane(self) -> 'float':
        '''float: 'ResultZPlane' is the original name of this property.'''

        return self.wrapped.ResultZPlane

    @result_z_plane.setter
    def result_z_plane(self, value: 'float'):
        self.wrapped.ResultZPlane = float(value) if value else 0.0

    @property
    def gear_tooth_shape_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'GearToothShapeChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.GearToothShapeChart.__class__.__mro__:
            raise CastException('Failed to cast gear_tooth_shape_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.GearToothShapeChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearToothShapeChart.__class__)(self.wrapped.GearToothShapeChart) if self.wrapped.GearToothShapeChart is not None else None

    @property
    def number_of_gear_shape_bands(self) -> 'int':
        '''int: 'NumberOfGearShapeBands' is the original name of this property.'''

        return self.wrapped.NumberOfGearShapeBands

    @number_of_gear_shape_bands.setter
    def number_of_gear_shape_bands(self, value: 'int'):
        self.wrapped.NumberOfGearShapeBands = int(value) if value else 0
