'''_1386.py

NumberFormatInfoSummary
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NUMBER_FORMAT_INFO_SUMMARY = python_net_import('SMT.MastaAPI.Utility', 'NumberFormatInfoSummary')


__docformat__ = 'restructuredtext en'
__all__ = ('NumberFormatInfoSummary',)


class NumberFormatInfoSummary(_0.APIBase):
    '''NumberFormatInfoSummary

    This is a mastapy class.
    '''

    TYPE = _NUMBER_FORMAT_INFO_SUMMARY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NumberFormatInfoSummary.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def decimal_symbol(self) -> 'str':
        '''str: 'DecimalSymbol' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DecimalSymbol

    @property
    def negative_symbol(self) -> 'str':
        '''str: 'NegativeSymbol' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NegativeSymbol

    @property
    def native_digits(self) -> 'str':
        '''str: 'NativeDigits' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NativeDigits

    @property
    def negative_pattern(self) -> 'str':
        '''str: 'NegativePattern' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NegativePattern

    @property
    def sample_negative_number(self) -> 'str':
        '''str: 'SampleNegativeNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SampleNegativeNumber

    @property
    def sample_positive_number(self) -> 'str':
        '''str: 'SamplePositiveNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SamplePositiveNumber
