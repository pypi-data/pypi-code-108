'''_1907.py

NeedleRollerBearing
'''


from mastapy.bearings.bearing_designs.rolling import _1897
from mastapy._internal.python_net import python_net_import

_NEEDLE_ROLLER_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'NeedleRollerBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('NeedleRollerBearing',)


class NeedleRollerBearing(_1897.CylindricalRollerBearing):
    '''NeedleRollerBearing

    This is a mastapy class.
    '''

    TYPE = _NEEDLE_ROLLER_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NeedleRollerBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
