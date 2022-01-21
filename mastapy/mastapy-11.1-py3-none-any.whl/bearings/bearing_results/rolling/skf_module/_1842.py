'''_1842.py

OperatingViscosity
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_OPERATING_VISCOSITY = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule', 'OperatingViscosity')


__docformat__ = 'restructuredtext en'
__all__ = ('OperatingViscosity',)


class OperatingViscosity(_0.APIBase):
    '''OperatingViscosity

    This is a mastapy class.
    '''

    TYPE = _OPERATING_VISCOSITY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OperatingViscosity.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def actual(self) -> 'float':
        '''float: 'Actual' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Actual

    @property
    def rated(self) -> 'float':
        '''float: 'Rated' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Rated

    @property
    def rated_at_40_degrees_c(self) -> 'float':
        '''float: 'RatedAt40DegreesC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatedAt40DegreesC
