'''_6654.py

PlanetManufactureError
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PLANET_MANUFACTURE_ERROR = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'PlanetManufactureError')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetManufactureError',)


class PlanetManufactureError(_0.APIBase):
    '''PlanetManufactureError

    This is a mastapy class.
    '''

    TYPE = _PLANET_MANUFACTURE_ERROR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetManufactureError.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def radial_error(self) -> 'float':
        '''float: 'RadialError' is the original name of this property.'''

        return self.wrapped.RadialError

    @radial_error.setter
    def radial_error(self, value: 'float'):
        self.wrapped.RadialError = float(value) if value else 0.0

    @property
    def tangential_error(self) -> 'float':
        '''float: 'TangentialError' is the original name of this property.'''

        return self.wrapped.TangentialError

    @tangential_error.setter
    def tangential_error(self, value: 'float'):
        self.wrapped.TangentialError = float(value) if value else 0.0

    @property
    def radial_tilt_error(self) -> 'float':
        '''float: 'RadialTiltError' is the original name of this property.'''

        return self.wrapped.RadialTiltError

    @radial_tilt_error.setter
    def radial_tilt_error(self, value: 'float'):
        self.wrapped.RadialTiltError = float(value) if value else 0.0

    @property
    def tangential_tilt_error(self) -> 'float':
        '''float: 'TangentialTiltError' is the original name of this property.'''

        return self.wrapped.TangentialTiltError

    @tangential_tilt_error.setter
    def tangential_tilt_error(self, value: 'float'):
        self.wrapped.TangentialTiltError = float(value) if value else 0.0

    @property
    def x_tilt_error(self) -> 'float':
        '''float: 'XTiltError' is the original name of this property.'''

        return self.wrapped.XTiltError

    @x_tilt_error.setter
    def x_tilt_error(self, value: 'float'):
        self.wrapped.XTiltError = float(value) if value else 0.0

    @property
    def y_tilt_error(self) -> 'float':
        '''float: 'YTiltError' is the original name of this property.'''

        return self.wrapped.YTiltError

    @y_tilt_error.setter
    def y_tilt_error(self, value: 'float'):
        self.wrapped.YTiltError = float(value) if value else 0.0

    @property
    def x_error(self) -> 'float':
        '''float: 'XError' is the original name of this property.'''

        return self.wrapped.XError

    @x_error.setter
    def x_error(self, value: 'float'):
        self.wrapped.XError = float(value) if value else 0.0

    @property
    def y_error(self) -> 'float':
        '''float: 'YError' is the original name of this property.'''

        return self.wrapped.YError

    @y_error.setter
    def y_error(self, value: 'float'):
        self.wrapped.YError = float(value) if value else 0.0

    @property
    def angular_error(self) -> 'float':
        '''float: 'AngularError' is the original name of this property.'''

        return self.wrapped.AngularError

    @angular_error.setter
    def angular_error(self, value: 'float'):
        self.wrapped.AngularError = float(value) if value else 0.0

    @property
    def radial_error_carrier(self) -> 'float':
        '''float: 'RadialErrorCarrier' is the original name of this property.'''

        return self.wrapped.RadialErrorCarrier

    @radial_error_carrier.setter
    def radial_error_carrier(self, value: 'float'):
        self.wrapped.RadialErrorCarrier = float(value) if value else 0.0

    @property
    def angle_of_error_in_pin_coordinate_system(self) -> 'float':
        '''float: 'AngleOfErrorInPinCoordinateSystem' is the original name of this property.'''

        return self.wrapped.AngleOfErrorInPinCoordinateSystem

    @angle_of_error_in_pin_coordinate_system.setter
    def angle_of_error_in_pin_coordinate_system(self, value: 'float'):
        self.wrapped.AngleOfErrorInPinCoordinateSystem = float(value) if value else 0.0

    @property
    def hole_radial_displacement(self) -> 'float':
        '''float: 'HoleRadialDisplacement' is the original name of this property.'''

        return self.wrapped.HoleRadialDisplacement

    @hole_radial_displacement.setter
    def hole_radial_displacement(self, value: 'float'):
        self.wrapped.HoleRadialDisplacement = float(value) if value else 0.0
