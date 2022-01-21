'''_516.py

BevelGearSetRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.agma_gleason_conical import _527
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_SET_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Bevel', 'BevelGearSetRating')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearSetRating',)


class BevelGearSetRating(_527.AGMAGleasonConicalGearSetRating):
    '''BevelGearSetRating

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_SET_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearSetRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rating(self) -> 'str':
        '''str: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Rating
