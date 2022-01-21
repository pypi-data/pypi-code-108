'''_1320.py

MultipleFourierSeriesInterpolator
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.math_utility import _1312
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MULTIPLE_FOURIER_SERIES_INTERPOLATOR = python_net_import('SMT.MastaAPI.MathUtility', 'MultipleFourierSeriesInterpolator')


__docformat__ = 'restructuredtext en'
__all__ = ('MultipleFourierSeriesInterpolator',)


class MultipleFourierSeriesInterpolator(_0.APIBase):
    '''MultipleFourierSeriesInterpolator

    This is a mastapy class.
    '''

    TYPE = _MULTIPLE_FOURIER_SERIES_INTERPOLATOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MultipleFourierSeriesInterpolator.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def x_values_where_data_has_been_specified(self) -> 'List[float]':
        '''List[float]: 'XValuesWhereDataHasBeenSpecified' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.XValuesWhereDataHasBeenSpecified, float)
        return value

    def remove_fourier_series_at(self, x_value: 'float'):
        ''' 'RemoveFourierSeriesAt' is the original name of this method.

        Args:
            x_value (float)
        '''

        x_value = float(x_value)
        self.wrapped.RemoveFourierSeriesAt(x_value if x_value else 0.0)

    def fourier_series_for(self, x_value: 'float') -> '_1312.FourierSeries':
        ''' 'FourierSeriesFor' is the original name of this method.

        Args:
            x_value (float)

        Returns:
            mastapy.math_utility.FourierSeries
        '''

        x_value = float(x_value)
        method_result = self.wrapped.FourierSeriesFor(x_value if x_value else 0.0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
