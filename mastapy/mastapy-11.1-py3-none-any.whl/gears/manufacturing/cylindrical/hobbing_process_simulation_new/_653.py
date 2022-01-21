'''_653.py

WormGrindingLeadCalculation
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.utility_gui.charts import (
    _1626, _1617, _1622, _1623
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import _620, _654
from mastapy._internal.python_net import python_net_import

_WORM_GRINDING_LEAD_CALCULATION = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'WormGrindingLeadCalculation')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGrindingLeadCalculation',)


class WormGrindingLeadCalculation(_654.WormGrindingProcessCalculation):
    '''WormGrindingLeadCalculation

    This is a mastapy class.
    '''

    TYPE = _WORM_GRINDING_LEAD_CALCULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGrindingLeadCalculation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_lead_bands(self) -> 'int':
        '''int: 'NumberOfLeadBands' is the original name of this property.'''

        return self.wrapped.NumberOfLeadBands

    @number_of_lead_bands.setter
    def number_of_lead_bands(self, value: 'int'):
        self.wrapped.NumberOfLeadBands = int(value) if value else 0

    @property
    def radius_for_lead_modification_calculation(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RadiusForLeadModificationCalculation' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RadiusForLeadModificationCalculation) if self.wrapped.RadiusForLeadModificationCalculation is not None else None

    @radius_for_lead_modification_calculation.setter
    def radius_for_lead_modification_calculation(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RadiusForLeadModificationCalculation = value

    @property
    def right_flank_lead_modification_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'RightFlankLeadModificationChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.RightFlankLeadModificationChart.__class__.__mro__:
            raise CastException('Failed to cast right_flank_lead_modification_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.RightFlankLeadModificationChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RightFlankLeadModificationChart.__class__)(self.wrapped.RightFlankLeadModificationChart) if self.wrapped.RightFlankLeadModificationChart is not None else None

    @property
    def left_flank_lead_modification_chart(self) -> '_1626.TwoDChartDefinition':
        '''TwoDChartDefinition: 'LeftFlankLeadModificationChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1626.TwoDChartDefinition.TYPE not in self.wrapped.LeftFlankLeadModificationChart.__class__.__mro__:
            raise CastException('Failed to cast left_flank_lead_modification_chart to TwoDChartDefinition. Expected: {}.'.format(self.wrapped.LeftFlankLeadModificationChart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LeftFlankLeadModificationChart.__class__)(self.wrapped.LeftFlankLeadModificationChart) if self.wrapped.LeftFlankLeadModificationChart is not None else None

    @property
    def right_flank(self) -> '_620.CalculateLeadDeviationAccuracy':
        '''CalculateLeadDeviationAccuracy: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_620.CalculateLeadDeviationAccuracy)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None

    @property
    def left_flank(self) -> '_620.CalculateLeadDeviationAccuracy':
        '''CalculateLeadDeviationAccuracy: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_620.CalculateLeadDeviationAccuracy)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None
