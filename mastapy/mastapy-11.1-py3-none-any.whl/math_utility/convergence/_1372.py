'''_1372.py

DataLogger
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._math.vector_3d import Vector3D
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DATA_LOGGER = python_net_import('SMT.MastaAPI.MathUtility.Convergence', 'DataLogger')


__docformat__ = 'restructuredtext en'
__all__ = ('DataLogger',)


class DataLogger(_0.APIBase):
    '''DataLogger

    This is a mastapy class.
    '''

    TYPE = _DATA_LOGGER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DataLogger.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def available_properties(self) -> 'List[str]':
        '''List[str]: 'AvailableProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AvailableProperties, str)
        return value

    @property
    def has_logged_data(self) -> 'bool':
        '''bool: 'HasLoggedData' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasLoggedData

    def get_double_data_for(self, property_name: 'str') -> 'List[float]':
        ''' 'GetDoubleDataFor' is the original name of this method.

        Args:
            property_name (str)

        Returns:
            List[float]
        '''

        property_name = str(property_name)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.GetDoubleDataFor(property_name if property_name else ''), float)

    def get_int_data_for(self, property_name: 'str') -> 'List[int]':
        ''' 'GetIntDataFor' is the original name of this method.

        Args:
            property_name (str)

        Returns:
            List[int]
        '''

        property_name = str(property_name)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.GetIntDataFor(property_name if property_name else ''), int)

    def get_vector_data_for(self, property_name: 'str') -> 'List[Vector3D]':
        ''' 'GetVectorDataFor' is the original name of this method.

        Args:
            property_name (str)

        Returns:
            List[Vector3D]
        '''

        property_name = str(property_name)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.GetVectorDataFor(property_name if property_name else ''), Vector3D)
