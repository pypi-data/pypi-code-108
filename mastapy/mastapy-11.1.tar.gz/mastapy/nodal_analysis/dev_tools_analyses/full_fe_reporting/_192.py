'''_192.py

PoissonRatioOrthotropicComponents
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_POISSON_RATIO_ORTHOTROPIC_COMPONENTS = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses.FullFEReporting', 'PoissonRatioOrthotropicComponents')


__docformat__ = 'restructuredtext en'
__all__ = ('PoissonRatioOrthotropicComponents',)


class PoissonRatioOrthotropicComponents(_0.APIBase):
    '''PoissonRatioOrthotropicComponents

    This is a mastapy class.
    '''

    TYPE = _POISSON_RATIO_ORTHOTROPIC_COMPONENTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PoissonRatioOrthotropicComponents.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def nu_xy(self) -> 'float':
        '''float: 'NuXY' is the original name of this property.'''

        return self.wrapped.NuXY

    @nu_xy.setter
    def nu_xy(self, value: 'float'):
        self.wrapped.NuXY = float(value) if value else 0.0

    @property
    def nu_yz(self) -> 'float':
        '''float: 'NuYZ' is the original name of this property.'''

        return self.wrapped.NuYZ

    @nu_yz.setter
    def nu_yz(self, value: 'float'):
        self.wrapped.NuYZ = float(value) if value else 0.0

    @property
    def nu_xz(self) -> 'float':
        '''float: 'NuXZ' is the original name of this property.'''

        return self.wrapped.NuXZ

    @nu_xz.setter
    def nu_xz(self, value: 'float'):
        self.wrapped.NuXZ = float(value) if value else 0.0
