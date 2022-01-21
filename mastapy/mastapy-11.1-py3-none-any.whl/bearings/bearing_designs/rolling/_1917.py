'''_1917.py

SphericalRollerThrustBearing
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_designs.rolling import _1891
from mastapy._internal.python_net import python_net_import

_SPHERICAL_ROLLER_THRUST_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'SphericalRollerThrustBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('SphericalRollerThrustBearing',)


class SphericalRollerThrustBearing(_1891.BarrelRollerBearing):
    '''SphericalRollerThrustBearing

    This is a mastapy class.
    '''

    TYPE = _SPHERICAL_ROLLER_THRUST_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SphericalRollerThrustBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angle_between_roller_end_and_bearing_axis(self) -> 'float':
        '''float: 'AngleBetweenRollerEndAndBearingAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleBetweenRollerEndAndBearingAxis

    @property
    def element_centre_point_diameter(self) -> 'float':
        '''float: 'ElementCentrePointDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElementCentrePointDiameter

    @property
    def distance_to_pressure_point_from_left_face(self) -> 'float':
        '''float: 'DistanceToPressurePointFromLeftFace' is the original name of this property.'''

        return self.wrapped.DistanceToPressurePointFromLeftFace

    @distance_to_pressure_point_from_left_face.setter
    def distance_to_pressure_point_from_left_face(self, value: 'float'):
        self.wrapped.DistanceToPressurePointFromLeftFace = float(value) if value else 0.0

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0
