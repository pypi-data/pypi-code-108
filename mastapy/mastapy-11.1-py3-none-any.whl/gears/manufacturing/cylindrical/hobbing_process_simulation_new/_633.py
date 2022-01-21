'''_633.py

HobbingProcessSimulationNew
'''


from mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
    _628, _630, _631, _627,
    _629, _635, _646, _632
)
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_HOBBING_PROCESS_SIMULATION_NEW = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew', 'HobbingProcessSimulationNew')


__docformat__ = 'restructuredtext en'
__all__ = ('HobbingProcessSimulationNew',)


class HobbingProcessSimulationNew(_646.ProcessSimulationNew['_632.HobbingProcessSimulationInput']):
    '''HobbingProcessSimulationNew

    This is a mastapy class.
    '''

    TYPE = _HOBBING_PROCESS_SIMULATION_NEW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HobbingProcessSimulationNew.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def hobbing_process_lead_calculation(self) -> '_628.HobbingProcessLeadCalculation':
        '''HobbingProcessLeadCalculation: 'HobbingProcessLeadCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_628.HobbingProcessLeadCalculation)(self.wrapped.HobbingProcessLeadCalculation) if self.wrapped.HobbingProcessLeadCalculation is not None else None

    @property
    def hobbing_process_pitch_calculation(self) -> '_630.HobbingProcessPitchCalculation':
        '''HobbingProcessPitchCalculation: 'HobbingProcessPitchCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_630.HobbingProcessPitchCalculation)(self.wrapped.HobbingProcessPitchCalculation) if self.wrapped.HobbingProcessPitchCalculation is not None else None

    @property
    def hobbing_process_profile_calculation(self) -> '_631.HobbingProcessProfileCalculation':
        '''HobbingProcessProfileCalculation: 'HobbingProcessProfileCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_631.HobbingProcessProfileCalculation)(self.wrapped.HobbingProcessProfileCalculation) if self.wrapped.HobbingProcessProfileCalculation is not None else None

    @property
    def hobbing_process_gear_shape_calculation(self) -> '_627.HobbingProcessGearShape':
        '''HobbingProcessGearShape: 'HobbingProcessGearShapeCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_627.HobbingProcessGearShape)(self.wrapped.HobbingProcessGearShapeCalculation) if self.wrapped.HobbingProcessGearShapeCalculation is not None else None

    @property
    def hobbing_process_mark_on_shaft_calculation(self) -> '_629.HobbingProcessMarkOnShaft':
        '''HobbingProcessMarkOnShaft: 'HobbingProcessMarkOnShaftCalculation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_629.HobbingProcessMarkOnShaft)(self.wrapped.HobbingProcessMarkOnShaftCalculation) if self.wrapped.HobbingProcessMarkOnShaftCalculation is not None else None

    @property
    def hobbing_process_total_modification(self) -> '_635.HobbingProcessTotalModificationCalculation':
        '''HobbingProcessTotalModificationCalculation: 'HobbingProcessTotalModification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_635.HobbingProcessTotalModificationCalculation)(self.wrapped.HobbingProcessTotalModification) if self.wrapped.HobbingProcessTotalModification is not None else None
