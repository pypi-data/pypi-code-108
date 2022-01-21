'''_1314.py

GriddedSurface
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.math_utility import _1309
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GRIDDED_SURFACE = python_net_import('SMT.MastaAPI.MathUtility', 'GriddedSurface')


__docformat__ = 'restructuredtext en'
__all__ = ('GriddedSurface',)


class GriddedSurface(_0.APIBase):
    '''GriddedSurface

    This is a mastapy class.
    '''

    TYPE = _GRIDDED_SURFACE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GriddedSurface.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def has_data(self) -> 'bool':
        '''bool: 'HasData' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasData

    @property
    def has_non_zero_data(self) -> 'bool':
        '''bool: 'HasNonZeroData' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasNonZeroData

    @property
    def is_sorted(self) -> 'bool':
        '''bool: 'IsSorted' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsSorted

    @property
    def x_values(self) -> 'List[float]':
        '''List[float]: 'XValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.XValues, float)
        return value

    @property
    def y_values(self) -> 'List[float]':
        '''List[float]: 'YValues' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.YValues, float)
        return value

    def data_value_interpolated_at(self, row_value: 'float', column_value: 'float', row_extrapolation_option: '_1309.ExtrapolationOptions', column_extrapolation_option: '_1309.ExtrapolationOptions') -> 'float':
        ''' 'DataValueInterpolatedAt' is the original name of this method.

        Args:
            row_value (float)
            column_value (float)
            row_extrapolation_option (mastapy.math_utility.ExtrapolationOptions)
            column_extrapolation_option (mastapy.math_utility.ExtrapolationOptions)

        Returns:
            float
        '''

        row_value = float(row_value)
        column_value = float(column_value)
        row_extrapolation_option = conversion.mp_to_pn_enum(row_extrapolation_option)
        column_extrapolation_option = conversion.mp_to_pn_enum(column_extrapolation_option)
        method_result = self.wrapped.DataValueInterpolatedAt(row_value if row_value else 0.0, column_value if column_value else 0.0, row_extrapolation_option, column_extrapolation_option)
        return method_result

    def get_row(self, row_id: 'int') -> 'List[float]':
        ''' 'GetRow' is the original name of this method.

        Args:
            row_id (int)

        Returns:
            List[float]
        '''

        row_id = int(row_id)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.GetRow(row_id if row_id else 0), float)

    def get_column(self, column_id: 'int') -> 'List[float]':
        ''' 'GetColumn' is the original name of this method.

        Args:
            column_id (int)

        Returns:
            List[float]
        '''

        column_id = int(column_id)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.GetColumn(column_id if column_id else 0), float)

    def get_value(self, x_index: 'int', y_index: 'int') -> 'float':
        ''' 'GetValue' is the original name of this method.

        Args:
            x_index (int)
            y_index (int)

        Returns:
            float
        '''

        x_index = int(x_index)
        y_index = int(y_index)
        method_result = self.wrapped.GetValue(x_index if x_index else 0, y_index if y_index else 0)
        return method_result
