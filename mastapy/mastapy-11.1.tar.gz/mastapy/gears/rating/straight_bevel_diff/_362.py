'''_362.py

StraightBevelDiffGearRating
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.straight_bevel_diff import _918
from mastapy.gears.rating.conical import _500
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.StraightBevelDiff', 'StraightBevelDiffGearRating')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGearRating',)


class StraightBevelDiffGearRating(_500.ConicalGearRating):
    '''StraightBevelDiffGearRating

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGearRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cycles_to_fail(self) -> 'float':
        '''float: 'CyclesToFail' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CyclesToFail

    @property
    def cycles_to_fail_bending(self) -> 'float':
        '''float: 'CyclesToFailBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CyclesToFailBending

    @property
    def time_to_fail_bending(self) -> 'float':
        '''float: 'TimeToFailBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TimeToFailBending

    @property
    def cycles_to_fail_contact(self) -> 'float':
        '''float: 'CyclesToFailContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CyclesToFailContact

    @property
    def time_to_fail_contact(self) -> 'float':
        '''float: 'TimeToFailContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TimeToFailContact

    @property
    def time_to_fail(self) -> 'float':
        '''float: 'TimeToFail' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TimeToFail

    @property
    def straight_bevel_diff_gear(self) -> '_918.StraightBevelDiffGearDesign':
        '''StraightBevelDiffGearDesign: 'StraightBevelDiffGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_918.StraightBevelDiffGearDesign)(self.wrapped.StraightBevelDiffGear) if self.wrapped.StraightBevelDiffGear is not None else None
