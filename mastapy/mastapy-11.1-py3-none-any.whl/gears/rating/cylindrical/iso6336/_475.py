'''_475.py

ISO63362006MeshSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.iso6336 import _481
from mastapy._internal.python_net import python_net_import

_ISO63362006_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO63362006MeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO63362006MeshSingleFlankRating',)


class ISO63362006MeshSingleFlankRating(_481.ISO6336AbstractMetalMeshSingleFlankRating):
    '''ISO63362006MeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _ISO63362006_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO63362006MeshSingleFlankRating.TYPE'):
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
    def mesh_stiffness_transverse(self) -> 'float':
        '''float: 'MeshStiffnessTransverse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshStiffnessTransverse

    @property
    def mesh_stiffness_face(self) -> 'float':
        '''float: 'MeshStiffnessFace' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshStiffnessFace

    @property
    def transverse_load_factor_bending(self) -> 'float':
        '''float: 'TransverseLoadFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseLoadFactorBending

    @property
    def helix_angle_factor_contact(self) -> 'float':
        '''float: 'HelixAngleFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngleFactorContact

    @property
    def deep_tooth_factor(self) -> 'float':
        '''float: 'DeepToothFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DeepToothFactor

    @property
    def dynamic_factor_source(self) -> 'str':
        '''str: 'DynamicFactorSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactorSource
