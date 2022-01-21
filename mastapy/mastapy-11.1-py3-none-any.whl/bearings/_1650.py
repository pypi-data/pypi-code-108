'''_1650.py

RollingBearingDatabase
'''


from typing import List, Optional

from mastapy.bearings.bearing_designs.rolling import _1912
from mastapy._internal import constructor, conversion
from mastapy.bearings import (
    _1628, _1653, _1642, _1651
)
from mastapy.math_utility import _1287
from mastapy._internal.python_net import python_net_import
from mastapy.utility.databases import _1599

_STRING = python_net_import('System', 'String')
_INT_32 = python_net_import('System', 'Int32')
_BEARING_CATALOG = python_net_import('SMT.MastaAPI.Bearings', 'BearingCatalog')
_ROLLING_BEARING_TYPE = python_net_import('SMT.MastaAPI.Bearings', 'RollingBearingType')
_HYBRID_STEEL_ALL = python_net_import('SMT.MastaAPI.Bearings', 'HybridSteelAll')
_ROLLING_BEARING_DATABASE = python_net_import('SMT.MastaAPI.Bearings', 'RollingBearingDatabase')
_RANGE = python_net_import('SMT.MastaAPI.MathUtility', 'Range')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingBearingDatabase',)


class RollingBearingDatabase(_1599.SQLDatabase['_1651.RollingBearingKey', '_1912.RollingBearing']):
    '''RollingBearingDatabase

    This is a mastapy class.
    '''

    TYPE = _ROLLING_BEARING_DATABASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingBearingDatabase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def add_to_database(self, bearing: '_1912.RollingBearing'):
        ''' 'AddToDatabase' is the original name of this method.

        Args:
            bearing (mastapy.bearings.bearing_designs.rolling.RollingBearing)
        '''

        self.wrapped.AddToDatabase(bearing.wrapped if bearing else None)

    def remove_from_database(self, bearing: '_1912.RollingBearing'):
        ''' 'RemoveFromDatabase' is the original name of this method.

        Args:
            bearing (mastapy.bearings.bearing_designs.rolling.RollingBearing)
        '''

        self.wrapped.RemoveFromDatabase(bearing.wrapped if bearing else None)

    def search_for_rolling_bearing(self, designation: 'str', catalog: '_1628.BearingCatalog', type_: '_1653.RollingBearingType', bore_range: '_1287.Range', outer_diameter_range: '_1287.Range', width_range: '_1287.Range', dynamic_capacity_range: '_1287.Range', number_of_rows: 'int', material_type: '_1642.HybridSteelAll') -> 'List[_1912.RollingBearing]':
        ''' 'SearchForRollingBearing' is the original name of this method.

        Args:
            designation (str)
            catalog (mastapy.bearings.BearingCatalog)
            type_ (mastapy.bearings.RollingBearingType)
            bore_range (mastapy.math_utility.Range)
            outer_diameter_range (mastapy.math_utility.Range)
            width_range (mastapy.math_utility.Range)
            dynamic_capacity_range (mastapy.math_utility.Range)
            number_of_rows (int)
            material_type (mastapy.bearings.HybridSteelAll)

        Returns:
            List[mastapy.bearings.bearing_designs.rolling.RollingBearing]
        '''

        designation = str(designation)
        catalog = conversion.mp_to_pn_enum(catalog)
        type_ = conversion.mp_to_pn_enum(type_)
        number_of_rows = int(number_of_rows)
        material_type = conversion.mp_to_pn_enum(material_type)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.SearchForRollingBearing.Overloads[_STRING, _BEARING_CATALOG, _ROLLING_BEARING_TYPE, _RANGE, _RANGE, _RANGE, _RANGE, _INT_32, _HYBRID_STEEL_ALL](designation if designation else '', catalog, type_, bore_range.wrapped if bore_range else None, outer_diameter_range.wrapped if outer_diameter_range else None, width_range.wrapped if width_range else None, dynamic_capacity_range.wrapped if dynamic_capacity_range else None, number_of_rows if number_of_rows else 0, material_type), constructor.new(_1912.RollingBearing))

    def search_for_rolling_bearing_with_name_catalog_and_type(self, designation: 'str', catalog: '_1628.BearingCatalog', type_: '_1653.RollingBearingType') -> 'List[_1912.RollingBearing]':
        ''' 'SearchForRollingBearing' is the original name of this method.

        Args:
            designation (str)
            catalog (mastapy.bearings.BearingCatalog)
            type_ (mastapy.bearings.RollingBearingType)

        Returns:
            List[mastapy.bearings.bearing_designs.rolling.RollingBearing]
        '''

        designation = str(designation)
        catalog = conversion.mp_to_pn_enum(catalog)
        type_ = conversion.mp_to_pn_enum(type_)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.SearchForRollingBearing.Overloads[_STRING, _BEARING_CATALOG, _ROLLING_BEARING_TYPE](designation if designation else '', catalog, type_), constructor.new(_1912.RollingBearing))

    def search_for_rolling_bearing_with_name_and_catalog(self, designation: 'str', catalog: '_1628.BearingCatalog') -> '_1912.RollingBearing':
        ''' 'SearchForRollingBearing' is the original name of this method.

        Args:
            designation (str)
            catalog (mastapy.bearings.BearingCatalog)

        Returns:
            mastapy.bearings.bearing_designs.rolling.RollingBearing
        '''

        designation = str(designation)
        catalog = conversion.mp_to_pn_enum(catalog)
        method_result = self.wrapped.SearchForRollingBearing.Overloads[_STRING, _BEARING_CATALOG](designation if designation else '', catalog)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def search_for_rolling_bearing_with_catalog(self, catalog: '_1628.BearingCatalog') -> 'List[_1912.RollingBearing]':
        ''' 'SearchForRollingBearing' is the original name of this method.

        Args:
            catalog (mastapy.bearings.BearingCatalog)

        Returns:
            List[mastapy.bearings.bearing_designs.rolling.RollingBearing]
        '''

        catalog = conversion.mp_to_pn_enum(catalog)
        return conversion.pn_to_mp_objects_in_list(self.wrapped.SearchForRollingBearing.Overloads[_BEARING_CATALOG](catalog), constructor.new(_1912.RollingBearing))

    def create_bearing(self, type_: '_1653.RollingBearingType', designation: Optional['str'] = 'None') -> '_1912.RollingBearing':
        ''' 'CreateBearing' is the original name of this method.

        Args:
            type_ (mastapy.bearings.RollingBearingType)
            designation (str, optional)

        Returns:
            mastapy.bearings.bearing_designs.rolling.RollingBearing
        '''

        type_ = conversion.mp_to_pn_enum(type_)
        designation = str(designation)
        method_result = self.wrapped.CreateBearing.Overloads[_ROLLING_BEARING_TYPE, _STRING](type_, designation if designation else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def create_bearing_with_type_name(self, type_: 'str', designation: Optional['str'] = 'None') -> '_1912.RollingBearing':
        ''' 'CreateBearing' is the original name of this method.

        Args:
            type_ (str)
            designation (str, optional)

        Returns:
            mastapy.bearings.bearing_designs.rolling.RollingBearing
        '''

        type_ = str(type_)
        designation = str(designation)
        method_result = self.wrapped.CreateBearing.Overloads[_STRING, _STRING](type_ if type_ else '', designation if designation else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def create_key(self, type_: '_1653.RollingBearingType', designation: Optional['str'] = 'None') -> '_1651.RollingBearingKey':
        ''' 'CreateKey' is the original name of this method.

        Args:
            type_ (mastapy.bearings.RollingBearingType)
            designation (str, optional)

        Returns:
            mastapy.bearings.RollingBearingKey
        '''

        type_ = conversion.mp_to_pn_enum(type_)
        designation = str(designation)
        method_result = self.wrapped.CreateKey.Overloads[_ROLLING_BEARING_TYPE, _STRING](type_, designation if designation else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def create_key_with_type_name(self, type_: 'str', designation: Optional['str'] = 'None') -> '_1651.RollingBearingKey':
        ''' 'CreateKey' is the original name of this method.

        Args:
            type_ (str)
            designation (str, optional)

        Returns:
            mastapy.bearings.RollingBearingKey
        '''

        type_ = str(type_)
        designation = str(designation)
        method_result = self.wrapped.CreateKey.Overloads[_STRING, _STRING](type_ if type_ else '', designation if designation else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
