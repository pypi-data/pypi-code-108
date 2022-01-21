'''_502.py

ConicalGearSetRating
'''


from mastapy.gears.rating import _329
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_SET_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Conical', 'ConicalGearSetRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearSetRating',)


class ConicalGearSetRating(_329.GearSetRating):
    '''ConicalGearSetRating

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_SET_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearSetRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
