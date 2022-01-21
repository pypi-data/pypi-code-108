'''_1609.py

DutyCyclePropertySummaryStress
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy.utility.property import _1605
from mastapy.utility.units_and_measurements.measurements import _1491
from mastapy._internal.python_net import python_net_import

_DUTY_CYCLE_PROPERTY_SUMMARY_STRESS = python_net_import('SMT.MastaAPI.Utility.Property', 'DutyCyclePropertySummaryStress')


__docformat__ = 'restructuredtext en'
__all__ = ('DutyCyclePropertySummaryStress',)


T = TypeVar('T')


class DutyCyclePropertySummaryStress(_1605.DutyCyclePropertySummary['_1491.Stress', 'T'], Generic[T]):
    '''DutyCyclePropertySummaryStress

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _DUTY_CYCLE_PROPERTY_SUMMARY_STRESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DutyCyclePropertySummaryStress.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def maximum_value(self) -> 'float':
        '''float: 'MaximumValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumValue

    @property
    def minimum_value(self) -> 'float':
        '''float: 'MinimumValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumValue

    @property
    def average_value(self) -> 'float':
        '''float: 'AverageValue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageValue
