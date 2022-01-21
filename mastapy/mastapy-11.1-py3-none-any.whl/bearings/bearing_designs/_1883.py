'''_1883.py

NonLinearBearing
'''


from mastapy.bearings.bearing_designs import _1879
from mastapy._internal.python_net import python_net_import

_NON_LINEAR_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns', 'NonLinearBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('NonLinearBearing',)


class NonLinearBearing(_1879.BearingDesign):
    '''NonLinearBearing

    This is a mastapy class.
    '''

    TYPE = _NON_LINEAR_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NonLinearBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
