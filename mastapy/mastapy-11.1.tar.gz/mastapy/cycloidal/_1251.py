'''_1251.py

ContactSpecification
'''


from mastapy._internal import constructor, conversion
from mastapy._math.vector_2d import Vector2D
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONTACT_SPECIFICATION = python_net_import('SMT.MastaAPI.Cycloidal', 'ContactSpecification')


__docformat__ = 'restructuredtext en'
__all__ = ('ContactSpecification',)


class ContactSpecification(_0.APIBase):
    '''ContactSpecification

    This is a mastapy class.
    '''

    TYPE = _CONTACT_SPECIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ContactSpecification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def clearance(self) -> 'float':
        '''float: 'Clearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Clearance

    @property
    def contact_line_point_1(self) -> 'Vector2D':
        '''Vector2D: 'ContactLinePoint1' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector2d(self.wrapped.ContactLinePoint1)
        return value

    @property
    def contact_line_point_2(self) -> 'Vector2D':
        '''Vector2D: 'ContactLinePoint2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector2d(self.wrapped.ContactLinePoint2)
        return value

    @property
    def contact_line_direction(self) -> 'Vector2D':
        '''Vector2D: 'ContactLineDirection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector2d(self.wrapped.ContactLineDirection)
        return value

    @property
    def contact_point(self) -> 'Vector2D':
        '''Vector2D: 'ContactPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector2d(self.wrapped.ContactPoint)
        return value

    @property
    def estimate_contact_point(self) -> 'Vector2D':
        '''Vector2D: 'EstimateContactPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector2d(self.wrapped.EstimateContactPoint)
        return value
