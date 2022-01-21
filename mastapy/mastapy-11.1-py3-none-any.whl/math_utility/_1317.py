'''_1317.py

MassProperties
'''


from mastapy._internal import constructor, conversion
from mastapy._math.vector_3d import Vector3D
from mastapy.math_utility import _1316
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MASS_PROPERTIES = python_net_import('SMT.MastaAPI.MathUtility', 'MassProperties')


__docformat__ = 'restructuredtext en'
__all__ = ('MassProperties',)


class MassProperties(_0.APIBase):
    '''MassProperties

    This is a mastapy class.
    '''

    TYPE = _MASS_PROPERTIES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassProperties.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mass(self) -> 'float':
        '''float: 'Mass' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Mass

    @property
    def centre_of_mass(self) -> 'Vector3D':
        '''Vector3D: 'CentreOfMass' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector3d(self.wrapped.CentreOfMass)
        return value

    @property
    def inertia_tensor_about_origin(self) -> '_1316.InertiaTensor':
        '''InertiaTensor: 'InertiaTensorAboutOrigin' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1316.InertiaTensor)(self.wrapped.InertiaTensorAboutOrigin) if self.wrapped.InertiaTensorAboutOrigin is not None else None

    @property
    def inertia_tensor_about_centre_of_mass(self) -> '_1316.InertiaTensor':
        '''InertiaTensor: 'InertiaTensorAboutCentreOfMass' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1316.InertiaTensor)(self.wrapped.InertiaTensorAboutCentreOfMass) if self.wrapped.InertiaTensorAboutCentreOfMass is not None else None
