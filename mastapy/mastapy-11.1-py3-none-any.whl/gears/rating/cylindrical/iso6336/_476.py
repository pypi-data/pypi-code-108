'''_476.py

ISO63362019GearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.iso6336 import _474
from mastapy._internal.python_net import python_net_import

_ISO63362019_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO63362019GearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO63362019GearSingleFlankRating',)


class ISO63362019GearSingleFlankRating(_474.ISO63362006GearSingleFlankRating):
    '''ISO63362019GearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _ISO63362019_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO63362019GearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_distribution_influence_factor(self) -> 'float':
        '''float: 'LoadDistributionInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionInfluenceFactor
