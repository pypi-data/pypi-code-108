'''_477.py

ISO63362019MeshSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.iso6336 import _475
from mastapy._internal.python_net import python_net_import

_ISO63362019_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO63362019MeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO63362019MeshSingleFlankRating',)


class ISO63362019MeshSingleFlankRating(_475.ISO63362006MeshSingleFlankRating):
    '''ISO63362019MeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _ISO63362019_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO63362019MeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rating_standard_name(self) -> 'str':
        '''str: 'RatingStandardName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatingStandardName

    @property
    def micro_geometry_factor(self) -> 'float':
        '''float: 'MicroGeometryFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MicroGeometryFactor
