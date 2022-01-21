'''_657.py

WormGrindingProcessPitchCalculation
'''


from mastapy.utility_gui.charts import (
    _1626, _1617, _1622, _1623
)
from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _621, _654
from mastapy._internal.python_net import python_net_import

_WORM_GRINDING_PROCESS_PITCH_CALCULATION = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'WormGrindingProcessPitchCalculation')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGrindingProcessPitchCalculation',)


class WormGrindingProcessPitchCalculation(_654.WormGrindingProcessCalculation):
    '''WormGrindingProcessPitchCalculation

    This is a mastapy class.
    '''

    TYPE = _WORM_GRINDING_PROCESS_PITCH_CALCULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGrindingProcessPitchCalculation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pitch_modification_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'PitchModificationChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.PitchModificationChart.__class__.__mro__:
            raise CastException('Failed to cast pitch_modification_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.PitchModificationChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.PitchModificationChart.__class__)(self.wrapped.PitchModificationChart) if self.wrapped.PitchModificationChart is not None else None

    @property
    def result_z_plane(self) -> 'float':
        '''float: 'ResultZPlane' is the original name of this property.'''

        return self.wrapped.ResultZPlane

    @result_z_plane.setter
    def result_z_plane(self, value: 'float'):
        self.wrapped.ResultZPlane = float(value) if value else 0.0

    @property
    def right_flank(self) -> '_621.CalculatePitchDeviationAccuracy':
        '''CalculatePitchDeviationAccuracy: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_621.CalculatePitchDeviationAccuracy)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None

    @property
    def left_flank(self) -> '_621.CalculatePitchDeviationAccuracy':
        '''CalculatePitchDeviationAccuracy: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_621.CalculatePitchDeviationAccuracy)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None
