'''_179.py

ElasticModulusOrthotropicComponents
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ELASTIC_MODULUS_ORTHOTROPIC_COMPONENTS = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'ElasticModulusOrthotropicComponents')


__docformat__ = 'restructuredtext en'
__all__ = ('ElasticModulusOrthotropicComponents',)


class ElasticModulusOrthotropicComponents(_0.APIBase):
    '''ElasticModulusOrthotropicComponents

    This is a mastapy class.
    '''

    TYPE = _ELASTIC_MODULUS_ORTHOTROPIC_COMPONENTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ElasticModulusOrthotropicComponents.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def ex(self) -> 'float':
        '''float: 'EX' is the original name of this property.'''

        return self.wrapped.EX

    @ex.setter
    def ex(self, value: 'float'):
        self.wrapped.EX = float(value) if value else 0.0

    @property
    def ey(self) -> 'float':
        '''float: 'EY' is the original name of this property.'''

        return self.wrapped.EY

    @ey.setter
    def ey(self, value: 'float'):
        self.wrapped.EY = float(value) if value else 0.0

    @property
    def ez(self) -> 'float':
        '''float: 'EZ' is the original name of this property.'''

        return self.wrapped.EZ

    @ez.setter
    def ez(self, value: 'float'):
        self.wrapped.EZ = float(value) if value else 0.0
