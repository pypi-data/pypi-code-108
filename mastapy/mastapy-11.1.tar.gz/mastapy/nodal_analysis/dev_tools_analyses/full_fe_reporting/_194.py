'''_194.py

ShearModulusOrthotropicComponents
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHEAR_MODULUS_ORTHOTROPIC_COMPONENTS = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'ShearModulusOrthotropicComponents')


__docformat__ = 'restructuredtext en'
__all__ = ('ShearModulusOrthotropicComponents',)


class ShearModulusOrthotropicComponents(_0.APIBase):
    '''ShearModulusOrthotropicComponents

    This is a mastapy class.
    '''

    TYPE = _SHEAR_MODULUS_ORTHOTROPIC_COMPONENTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShearModulusOrthotropicComponents.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gxy(self) -> 'float':
        '''float: 'GXY' is the original name of this property.'''

        return self.wrapped.GXY

    @gxy.setter
    def gxy(self, value: 'float'):
        self.wrapped.GXY = float(value) if value else 0.0

    @property
    def gyz(self) -> 'float':
        '''float: 'GYZ' is the original name of this property.'''

        return self.wrapped.GYZ

    @gyz.setter
    def gyz(self, value: 'float'):
        self.wrapped.GYZ = float(value) if value else 0.0

    @property
    def gxz(self) -> 'float':
        '''float: 'GXZ' is the original name of this property.'''

        return self.wrapped.GXZ

    @gxz.setter
    def gxz(self, value: 'float'):
        self.wrapped.GXZ = float(value) if value else 0.0
