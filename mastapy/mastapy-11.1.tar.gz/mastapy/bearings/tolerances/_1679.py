'''_1679.py

ToleranceCombination
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.bearings.tolerances import _1661
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TOLERANCE_COMBINATION = python_net_import('SMT.MastaAPI.Bearings.Tolerances', 'ToleranceCombination')


__docformat__ = 'restructuredtext en'
__all__ = ('ToleranceCombination',)


class ToleranceCombination(_0.APIBase):
    '''ToleranceCombination

    This is a mastapy class.
    '''

    TYPE = _TOLERANCE_COMBINATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ToleranceCombination.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def lower_value(self) -> 'float':
        '''float: 'LowerValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LowerValue

    @property
    def upper_value(self) -> 'float':
        '''float: 'UpperValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UpperValue

    @property
    def fit(self) -> '_1661.FitType':
        '''FitType: 'Fit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.Fit)
        return constructor.new(_1661.FitType)(value) if value is not None else None

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
