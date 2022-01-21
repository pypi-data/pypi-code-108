'''_515.py

BevelGearRating
'''


from mastapy.gears.rating.agma_gleason_conical import _526
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Bevel', 'BevelGearRating')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearRating',)


class BevelGearRating(_526.AGMAGleasonConicalGearRating):
    '''BevelGearRating

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
