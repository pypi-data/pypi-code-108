'''_1806.py

LoadedToroidalRollerBearingElement
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling import _1777
from mastapy._internal.python_net import python_net_import

_LOADED_TOROIDAL_ROLLER_BEARING_ELEMENT = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'LoadedToroidalRollerBearingElement')


__docformat__ = 'restructuredtext en'
__all__ = ('LoadedToroidalRollerBearingElement',)


class LoadedToroidalRollerBearingElement(_1777.LoadedRollerBearingElement):
    '''LoadedToroidalRollerBearingElement

    This is a mastapy class.
    '''

    TYPE = _LOADED_TOROIDAL_ROLLER_BEARING_ELEMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LoadedToroidalRollerBearingElement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contact_angle(self) -> 'float':
        '''float: 'ContactAngle' is the original name of this property.'''

        return self.wrapped.ContactAngle

    @contact_angle.setter
    def contact_angle(self, value: 'float'):
        self.wrapped.ContactAngle = float(value) if value else 0.0
