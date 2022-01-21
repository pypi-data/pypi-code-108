'''_1838.py

GreaseQuantity
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling.skf_module import _1846
from mastapy._internal.python_net import python_net_import

_GREASE_QUANTITY = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule', 'GreaseQuantity')


__docformat__ = 'restructuredtext en'
__all__ = ('GreaseQuantity',)


class GreaseQuantity(_1846.SKFCalculationResult):
    '''GreaseQuantity

    This is a mastapy class.
    '''

    TYPE = _GREASE_QUANTITY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GreaseQuantity.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def side(self) -> 'float':
        '''float: 'Side' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Side

    @property
    def ring(self) -> 'float':
        '''float: 'Ring' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Ring
