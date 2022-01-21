'''_660.py

WormGrindingProcessSimulationNew
'''


from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
    _653, _658, _655, _656,
    _652, _662, _657, _646,
    _659
)
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_WORM_GRINDING_PROCESS_SIMULATION_NEW = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'WormGrindingProcessSimulationNew')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGrindingProcessSimulationNew',)


class WormGrindingProcessSimulationNew(_646.ProcessSimulationNew['_659.WormGrindingProcessSimulationInput']):
    '''WormGrindingProcessSimulationNew

    This is a mastapy class.
    '''

    TYPE = _WORM_GRINDING_PROCESS_SIMULATION_NEW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGrindingProcessSimulationNew.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def worm_grinding_process_lead_calculation(self) -> '_653.WormGrindingLeadCalculation':
        '''WormGrindingLeadCalculation: 'WormGrindingProcessLeadCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_653.WormGrindingLeadCalculation)(self.wrapped.WormGrindingProcessLeadCalculation) if self.wrapped.WormGrindingProcessLeadCalculation is not None else None

    @property
    def worm_grinding_process_profile_calculation(self) -> '_658.WormGrindingProcessProfileCalculation':
        '''WormGrindingProcessProfileCalculation: 'WormGrindingProcessProfileCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_658.WormGrindingProcessProfileCalculation)(self.wrapped.WormGrindingProcessProfileCalculation) if self.wrapped.WormGrindingProcessProfileCalculation is not None else None

    @property
    def worm_grinding_process_gear_shape_calculation(self) -> '_655.WormGrindingProcessGearShape':
        '''WormGrindingProcessGearShape: 'WormGrindingProcessGearShapeCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_655.WormGrindingProcessGearShape)(self.wrapped.WormGrindingProcessGearShapeCalculation) if self.wrapped.WormGrindingProcessGearShapeCalculation is not None else None

    @property
    def worm_grinding_process_mark_on_shaft_calculation(self) -> '_656.WormGrindingProcessMarkOnShaft':
        '''WormGrindingProcessMarkOnShaft: 'WormGrindingProcessMarkOnShaftCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_656.WormGrindingProcessMarkOnShaft)(self.wrapped.WormGrindingProcessMarkOnShaftCalculation) if self.wrapped.WormGrindingProcessMarkOnShaftCalculation is not None else None

    @property
    def worm_grinding_cutter_calculation(self) -> '_652.WormGrindingCutterCalculation':
        '''WormGrindingCutterCalculation: 'WormGrindingCutterCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_652.WormGrindingCutterCalculation)(self.wrapped.WormGrindingCutterCalculation) if self.wrapped.WormGrindingCutterCalculation is not None else None

    @property
    def worm_grinding_process_total_modification_calculation(self) -> '_662.WormGrindingProcessTotalModificationCalculation':
        '''WormGrindingProcessTotalModificationCalculation: 'WormGrindingProcessTotalModificationCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_662.WormGrindingProcessTotalModificationCalculation)(self.wrapped.WormGrindingProcessTotalModificationCalculation) if self.wrapped.WormGrindingProcessTotalModificationCalculation is not None else None

    @property
    def worm_grinding_process_pitch_calculation(self) -> '_657.WormGrindingProcessPitchCalculation':
        '''WormGrindingProcessPitchCalculation: 'WormGrindingProcessPitchCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_657.WormGrindingProcessPitchCalculation)(self.wrapped.WormGrindingProcessPitchCalculation) if self.wrapped.WormGrindingProcessPitchCalculation is not None else None
