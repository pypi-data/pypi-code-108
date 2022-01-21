'''_257.py

VehicleDynamicsProperties
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_VEHICLE_DYNAMICS_PROPERTIES = python_net_import('SMT.MastaAPI.Materials', 'VehicleDynamicsProperties')


__docformat__ = 'restructuredtext en'
__all__ = ('VehicleDynamicsProperties',)


class VehicleDynamicsProperties(_0.APIBase):
    '''VehicleDynamicsProperties

    This is a mastapy class.
    '''

    TYPE = _VEHICLE_DYNAMICS_PROPERTIES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VehicleDynamicsProperties.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def vehicle_frontal_area(self) -> 'float':
        '''float: 'VehicleFrontalArea' is the original name of this property.'''

        return self.wrapped.VehicleFrontalArea

    @vehicle_frontal_area.setter
    def vehicle_frontal_area(self, value: 'float'):
        self.wrapped.VehicleFrontalArea = float(value) if value else 0.0

    @property
    def air_density(self) -> 'float':
        '''float: 'AirDensity' is the original name of this property.'''

        return self.wrapped.AirDensity

    @air_density.setter
    def air_density(self, value: 'float'):
        self.wrapped.AirDensity = float(value) if value else 0.0

    @property
    def vehicle_mass(self) -> 'float':
        '''float: 'VehicleMass' is the original name of this property.'''

        return self.wrapped.VehicleMass

    @vehicle_mass.setter
    def vehicle_mass(self, value: 'float'):
        self.wrapped.VehicleMass = float(value) if value else 0.0

    @property
    def vehicle_effective_inertia(self) -> 'float':
        '''float: 'VehicleEffectiveInertia' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VehicleEffectiveInertia

    @property
    def vehicle_effective_mass(self) -> 'float':
        '''float: 'VehicleEffectiveMass' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VehicleEffectiveMass

    @property
    def rolling_radius(self) -> 'float':
        '''float: 'RollingRadius' is the original name of this property.'''

        return self.wrapped.RollingRadius

    @rolling_radius.setter
    def rolling_radius(self, value: 'float'):
        self.wrapped.RollingRadius = float(value) if value else 0.0

    @property
    def drag_coefficient(self) -> 'float':
        '''float: 'DragCoefficient' is the original name of this property.'''

        return self.wrapped.DragCoefficient

    @drag_coefficient.setter
    def drag_coefficient(self, value: 'float'):
        self.wrapped.DragCoefficient = float(value) if value else 0.0

    @property
    def rolling_resistance_coefficient(self) -> 'float':
        '''float: 'RollingResistanceCoefficient' is the original name of this property.'''

        return self.wrapped.RollingResistanceCoefficient

    @rolling_resistance_coefficient.setter
    def rolling_resistance_coefficient(self, value: 'float'):
        self.wrapped.RollingResistanceCoefficient = float(value) if value else 0.0

    @property
    def aerodynamic_drag_coefficient(self) -> 'float':
        '''float: 'AerodynamicDragCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AerodynamicDragCoefficient

    @property
    def rolling_resistance(self) -> 'float':
        '''float: 'RollingResistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RollingResistance

    @property
    def number_of_wheels(self) -> 'int':
        '''int: 'NumberOfWheels' is the original name of this property.'''

        return self.wrapped.NumberOfWheels

    @number_of_wheels.setter
    def number_of_wheels(self, value: 'int'):
        self.wrapped.NumberOfWheels = int(value) if value else 0

    @property
    def wheel_inertia(self) -> 'float':
        '''float: 'WheelInertia' is the original name of this property.'''

        return self.wrapped.WheelInertia

    @wheel_inertia.setter
    def wheel_inertia(self, value: 'float'):
        self.wrapped.WheelInertia = float(value) if value else 0.0
