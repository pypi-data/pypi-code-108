'''_1896.py

CrossedRollerBearing
'''


from mastapy.bearings.bearing_designs.rolling import _1909
from mastapy._internal.python_net import python_net_import

_CROSSED_ROLLER_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'CrossedRollerBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('CrossedRollerBearing',)


class CrossedRollerBearing(_1909.RollerBearing):
    '''CrossedRollerBearing

    This is a mastapy class.
    '''

    TYPE = _CROSSED_ROLLER_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CrossedRollerBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
