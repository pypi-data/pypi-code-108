'''_1336.py

SurfaceToSurfaceContact
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SURFACE_TO_SURFACE_CONTACT = python_net_import('SMT.MastaAPI.MathUtility.StiffnessCalculators', 'SurfaceToSurfaceContact')


__docformat__ = 'restructuredtext en'
__all__ = ('SurfaceToSurfaceContact',)


class SurfaceToSurfaceContact(_0.APIBase):
    '''SurfaceToSurfaceContact

    This is a mastapy class.
    '''

    TYPE = _SURFACE_TO_SURFACE_CONTACT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SurfaceToSurfaceContact.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def normal_stiffness(self) -> 'float':
        '''float: 'NormalStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalStiffness

    @property
    def normal_deflection(self) -> 'float':
        '''float: 'NormalDeflection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalDeflection

    @property
    def surface_penetration(self) -> 'float':
        '''float: 'SurfacePenetration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfacePenetration

    @property
    def normal_force(self) -> 'float':
        '''float: 'NormalForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalForce
