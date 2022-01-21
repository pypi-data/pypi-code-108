'''_1832.py

FrequencyOfOverRolling
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FREQUENCY_OF_OVER_ROLLING = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule', 'FrequencyOfOverRolling')


__docformat__ = 'restructuredtext en'
__all__ = ('FrequencyOfOverRolling',)


class FrequencyOfOverRolling(_0.APIBase):
    '''FrequencyOfOverRolling

    This is a mastapy class.
    '''

    TYPE = _FREQUENCY_OF_OVER_ROLLING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FrequencyOfOverRolling.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def point_on_inner_ring(self) -> 'float':
        '''float: 'PointOnInnerRing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PointOnInnerRing

    @property
    def point_on_outer_ring(self) -> 'float':
        '''float: 'PointOnOuterRing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PointOnOuterRing

    @property
    def rolling_element(self) -> 'float':
        '''float: 'RollingElement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RollingElement
