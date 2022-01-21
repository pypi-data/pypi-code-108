'''_1297.py

CoordinateSystem3D
'''


from mastapy._math.vector_3d import Vector3D
from mastapy._internal import constructor, conversion
from mastapy.math_utility import _1302
from mastapy._math.matrix_4x4 import Matrix4x4
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_COORDINATE_SYSTEM_3D = python_net_import('SMT.MastaAPI.MathUtility', 'CoordinateSystem3D')


__docformat__ = 'restructuredtext en'
__all__ = ('CoordinateSystem3D',)


class CoordinateSystem3D(_0.APIBase):
    '''CoordinateSystem3D

    This is a mastapy class.
    '''

    TYPE = _COORDINATE_SYSTEM_3D

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CoordinateSystem3D.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def origin(self) -> 'Vector3D':
        '''Vector3D: 'Origin' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.Origin)
        return value

    @property
    def x_axis(self) -> 'Vector3D':
        '''Vector3D: 'XAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.XAxis)
        return value

    @property
    def y_axis(self) -> 'Vector3D':
        '''Vector3D: 'YAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.YAxis)
        return value

    @property
    def z_axis(self) -> 'Vector3D':
        '''Vector3D: 'ZAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.ZAxis)
        return value

    def rotated_about_axis(self, axis: 'Vector3D', angle: 'float') -> 'CoordinateSystem3D':
        ''' 'RotatedAboutAxis' is the original name of this method.

        Args:
            axis (Vector3D)
            angle (float)

        Returns:
            mastapy.math_utility.CoordinateSystem3D
        '''

        axis = conversion.mp_to_pn_vector3d(axis)
        angle = float(angle)
        method_result = self.wrapped.RotatedAboutAxis(axis, angle if angle else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def axis(self, degree_of_freedom: '_1302.DegreesOfFreedom') -> 'Vector3D':
        ''' 'Axis' is the original name of this method.

        Args:
            degree_of_freedom (mastapy.math_utility.DegreesOfFreedom)

        Returns:
            Vector3D
        '''

        degree_of_freedom = conversion.mp_to_pn_enum(degree_of_freedom)
        return conversion.pn_to_mp_vector3d(self.wrapped.Axis(degree_of_freedom))

    def transform_to_world_from_this(self) -> 'Matrix4x4':
        ''' 'TransformToWorldFromThis' is the original name of this method.

        Returns:
            Matrix4x4
        '''

        return conversion.pn_to_mp_matrix4x4(self.wrapped.TransformToWorldFromThis())

    def transform_from_world_to_this(self) -> 'Matrix4x4':
        ''' 'TransformFromWorldToThis' is the original name of this method.

        Returns:
            Matrix4x4
        '''

        return conversion.pn_to_mp_matrix4x4(self.wrapped.TransformFromWorldToThis())

    def transformed_by(self, transform: 'Matrix4x4') -> 'CoordinateSystem3D':
        ''' 'TransformedBy' is the original name of this method.

        Args:
            transform (Matrix4x4)

        Returns:
            mastapy.math_utility.CoordinateSystem3D
        '''

        transform = conversion.mp_to_pn_matrix4x4(transform)
        method_result = self.wrapped.TransformedBy(transform)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def without_translation(self) -> 'CoordinateSystem3D':
        ''' 'WithoutTranslation' is the original name of this method.

        Returns:
            mastapy.math_utility.CoordinateSystem3D
        '''

        method_result = self.wrapped.WithoutTranslation()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
