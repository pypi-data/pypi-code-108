'''_472.py

ISO63361996GearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.iso6336 import _480
from mastapy._internal.python_net import python_net_import

_ISO63361996_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO63361996GearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO63361996GearSingleFlankRating',)


class ISO63361996GearSingleFlankRating(_480.ISO6336AbstractMetalGearSingleFlankRating):
    '''ISO63361996GearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _ISO63361996_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO63361996GearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def nominal_tooth_root_stress(self) -> 'float':
        '''float: 'NominalToothRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalToothRootStress
