'''_600.py

FormWheelGrindingProcessSimulation
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical.process_simulation import _599
from mastapy._internal.python_net import python_net_import

_FORM_WHEEL_GRINDING_PROCESS_SIMULATION = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.ProcessSimulation', 'FormWheelGrindingProcessSimulation')


__docformat__ = 'restructuredtext en'
__all__ = ('FormWheelGrindingProcessSimulation',)


class FormWheelGrindingProcessSimulation(_599.CutterProcessSimulation):
    '''FormWheelGrindingProcessSimulation

    This is a mastapy class.
    '''

    TYPE = _FORM_WHEEL_GRINDING_PROCESS_SIMULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FormWheelGrindingProcessSimulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def left_starting_angle(self) -> 'float':
        '''float: 'LeftStartingAngle' is the original name of this property.'''

        return self.wrapped.LeftStartingAngle

    @left_starting_angle.setter
    def left_starting_angle(self, value: 'float'):
        self.wrapped.LeftStartingAngle = float(value) if value else 0.0

    @property
    def left_amplitude(self) -> 'float':
        '''float: 'LeftAmplitude' is the original name of this property.'''

        return self.wrapped.LeftAmplitude

    @left_amplitude.setter
    def left_amplitude(self, value: 'float'):
        self.wrapped.LeftAmplitude = float(value) if value else 0.0

    @property
    def left_number_of_cycles(self) -> 'float':
        '''float: 'LeftNumberOfCycles' is the original name of this property.'''

        return self.wrapped.LeftNumberOfCycles

    @left_number_of_cycles.setter
    def left_number_of_cycles(self, value: 'float'):
        self.wrapped.LeftNumberOfCycles = float(value) if value else 0.0

    @property
    def right_starting_angle(self) -> 'float':
        '''float: 'RightStartingAngle' is the original name of this property.'''

        return self.wrapped.RightStartingAngle

    @right_starting_angle.setter
    def right_starting_angle(self, value: 'float'):
        self.wrapped.RightStartingAngle = float(value) if value else 0.0

    @property
    def right_amplitude(self) -> 'float':
        '''float: 'RightAmplitude' is the original name of this property.'''

        return self.wrapped.RightAmplitude

    @right_amplitude.setter
    def right_amplitude(self, value: 'float'):
        self.wrapped.RightAmplitude = float(value) if value else 0.0

    @property
    def right_number_of_cycles(self) -> 'float':
        '''float: 'RightNumberOfCycles' is the original name of this property.'''

        return self.wrapped.RightNumberOfCycles

    @right_number_of_cycles.setter
    def right_number_of_cycles(self, value: 'float'):
        self.wrapped.RightNumberOfCycles = float(value) if value else 0.0

    @property
    def grind_wheel_axial_offset(self) -> 'float':
        '''float: 'GrindWheelAxialOffset' is the original name of this property.'''

        return self.wrapped.GrindWheelAxialOffset

    @grind_wheel_axial_offset.setter
    def grind_wheel_axial_offset(self, value: 'float'):
        self.wrapped.GrindWheelAxialOffset = float(value) if value else 0.0

    @property
    def grind_wheel_tilt_radius(self) -> 'float':
        '''float: 'GrindWheelTiltRadius' is the original name of this property.'''

        return self.wrapped.GrindWheelTiltRadius

    @grind_wheel_tilt_radius.setter
    def grind_wheel_tilt_radius(self, value: 'float'):
        self.wrapped.GrindWheelTiltRadius = float(value) if value else 0.0

    @property
    def grind_wheel_tilt_angle(self) -> 'float':
        '''float: 'GrindWheelTiltAngle' is the original name of this property.'''

        return self.wrapped.GrindWheelTiltAngle

    @grind_wheel_tilt_angle.setter
    def grind_wheel_tilt_angle(self, value: 'float'):
        self.wrapped.GrindWheelTiltAngle = float(value) if value else 0.0

    @property
    def grind_wheel_diameter_deviation(self) -> 'float':
        '''float: 'GrindWheelDiameterDeviation' is the original name of this property.'''

        return self.wrapped.GrindWheelDiameterDeviation

    @grind_wheel_diameter_deviation.setter
    def grind_wheel_diameter_deviation(self, value: 'float'):
        self.wrapped.GrindWheelDiameterDeviation = float(value) if value else 0.0

    @property
    def grind_wheel_axial_runout_reading(self) -> 'float':
        '''float: 'GrindWheelAxialRunoutReading' is the original name of this property.'''

        return self.wrapped.GrindWheelAxialRunoutReading

    @grind_wheel_axial_runout_reading.setter
    def grind_wheel_axial_runout_reading(self, value: 'float'):
        self.wrapped.GrindWheelAxialRunoutReading = float(value) if value else 0.0

    @property
    def grind_wheel_axial_runout_radius(self) -> 'float':
        '''float: 'GrindWheelAxialRunoutRadius' is the original name of this property.'''

        return self.wrapped.GrindWheelAxialRunoutRadius

    @grind_wheel_axial_runout_radius.setter
    def grind_wheel_axial_runout_radius(self, value: 'float'):
        self.wrapped.GrindWheelAxialRunoutRadius = float(value) if value else 0.0

    @property
    def gear_relative_tilt_x(self) -> 'float':
        '''float: 'GearRelativeTiltX' is the original name of this property.'''

        return self.wrapped.GearRelativeTiltX

    @gear_relative_tilt_x.setter
    def gear_relative_tilt_x(self, value: 'float'):
        self.wrapped.GearRelativeTiltX = float(value) if value else 0.0

    @property
    def gear_relative_tilt_y(self) -> 'float':
        '''float: 'GearRelativeTiltY' is the original name of this property.'''

        return self.wrapped.GearRelativeTiltY

    @gear_relative_tilt_y.setter
    def gear_relative_tilt_y(self, value: 'float'):
        self.wrapped.GearRelativeTiltY = float(value) if value else 0.0
