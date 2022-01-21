'''_1885.py

AngularContactThrustBallBearing
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_designs.rolling import _1884
from mastapy._internal.python_net import python_net_import

_ANGULAR_CONTACT_THRUST_BALL_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'AngularContactThrustBallBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('AngularContactThrustBallBearing',)


class AngularContactThrustBallBearing(_1884.AngularContactBallBearing):
    '''AngularContactThrustBallBearing

    This is a mastapy class.
    '''

    TYPE = _ANGULAR_CONTACT_THRUST_BALL_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AngularContactThrustBallBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0
