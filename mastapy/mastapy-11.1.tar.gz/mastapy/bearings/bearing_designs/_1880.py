'''_1880.py

DetailedBearing
'''


from mastapy.bearings.bearing_designs import _1883
from mastapy._internal.python_net import python_net_import

_DETAILED_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns', 'DetailedBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('DetailedBearing',)


class DetailedBearing(_1883.NonLinearBearing):
    '''DetailedBearing

    This is a mastapy class.
    '''

    TYPE = _DETAILED_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DetailedBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
