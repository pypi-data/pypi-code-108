'''_759.py

ManufacturingMachine
'''


from mastapy.gears.manufacturing.bevel import _758, _772
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.utility.databases import _1597
from mastapy._internal.python_net import python_net_import

_MANUFACTURING_MACHINE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'ManufacturingMachine')


__docformat__ = 'restructuredtext en'
__all__ = ('ManufacturingMachine',)


class ManufacturingMachine(_1597.NamedDatabaseItem):
    '''ManufacturingMachine

    This is a mastapy class.
    '''

    TYPE = _MANUFACTURING_MACHINE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ManufacturingMachine.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def machine_type(self) -> '_758.MachineTypes':
        '''MachineTypes: 'MachineType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MachineType)
        return constructor.new(_758.MachineTypes)(value) if value is not None else None

    @machine_type.setter
    def machine_type(self, value: '_758.MachineTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MachineType = value

    @property
    def can_work_for_formate(self) -> 'bool':
        '''bool: 'CanWorkForFormate' is the original name of this property.'''

        return self.wrapped.CanWorkForFormate

    @can_work_for_formate.setter
    def can_work_for_formate(self, value: 'bool'):
        self.wrapped.CanWorkForFormate = bool(value) if value else False

    @property
    def can_work_for_generating(self) -> 'bool':
        '''bool: 'CanWorkForGenerating' is the original name of this property.'''

        return self.wrapped.CanWorkForGenerating

    @can_work_for_generating.setter
    def can_work_for_generating(self, value: 'bool'):
        self.wrapped.CanWorkForGenerating = bool(value) if value else False

    @property
    def can_work_for_tilt(self) -> 'bool':
        '''bool: 'CanWorkForTilt' is the original name of this property.'''

        return self.wrapped.CanWorkForTilt

    @can_work_for_tilt.setter
    def can_work_for_tilt(self, value: 'bool'):
        self.wrapped.CanWorkForTilt = bool(value) if value else False

    @property
    def wheel_formate_machine_type(self) -> '_772.WheelFormatMachineTypes':
        '''WheelFormatMachineTypes: 'WheelFormateMachineType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.WheelFormateMachineType)
        return constructor.new(_772.WheelFormatMachineTypes)(value) if value is not None else None

    @wheel_formate_machine_type.setter
    def wheel_formate_machine_type(self, value: '_772.WheelFormatMachineTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.WheelFormateMachineType = value

    @property
    def can_work_for_roller_modification(self) -> 'bool':
        '''bool: 'CanWorkForRollerModification' is the original name of this property.'''

        return self.wrapped.CanWorkForRollerModification

    @can_work_for_roller_modification.setter
    def can_work_for_roller_modification(self, value: 'bool'):
        self.wrapped.CanWorkForRollerModification = bool(value) if value else False

    @property
    def maximum_tilt_angle(self) -> 'float':
        '''float: 'MaximumTiltAngle' is the original name of this property.'''

        return self.wrapped.MaximumTiltAngle

    @maximum_tilt_angle.setter
    def maximum_tilt_angle(self, value: 'float'):
        self.wrapped.MaximumTiltAngle = float(value) if value else 0.0

    @property
    def tilt_distance(self) -> 'float':
        '''float: 'TiltDistance' is the original name of this property.'''

        return self.wrapped.TiltDistance

    @tilt_distance.setter
    def tilt_distance(self, value: 'float'):
        self.wrapped.TiltDistance = float(value) if value else 0.0

    @property
    def eccentric_distance(self) -> 'float':
        '''float: 'EccentricDistance' is the original name of this property.'''

        return self.wrapped.EccentricDistance

    @eccentric_distance.setter
    def eccentric_distance(self, value: 'float'):
        self.wrapped.EccentricDistance = float(value) if value else 0.0

    @property
    def tilt_body_angle(self) -> 'float':
        '''float: 'TiltBodyAngle' is the original name of this property.'''

        return self.wrapped.TiltBodyAngle

    @tilt_body_angle.setter
    def tilt_body_angle(self, value: 'float'):
        self.wrapped.TiltBodyAngle = float(value) if value else 0.0
