'''_526.py

AGMAGleasonConicalGearRating
'''


from mastapy.gears.rating.conical import _500
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.AGMAGleasonConical', 'AGMAGleasonConicalGearRating')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearRating',)


class AGMAGleasonConicalGearRating(_500.ConicalGearRating):
    '''AGMAGleasonConicalGearRating

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
