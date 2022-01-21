'''_48.py

BarGeometry
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_BAR_GEOMETRY = python_net_import('SMT.MastaAPI.NodalAnalysis', 'BarGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('BarGeometry',)


class BarGeometry(_0.APIBase):
    '''BarGeometry

    This is a mastapy class.
    '''

    TYPE = _BAR_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BarGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Length

    @property
    def cross_sectional_area_ratio(self) -> 'float':
        '''float: 'CrossSectionalAreaRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CrossSectionalAreaRatio

    @property
    def polar_area_moment_of_inertia_ratio(self) -> 'float':
        '''float: 'PolarAreaMomentOfInertiaRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PolarAreaMomentOfInertiaRatio
