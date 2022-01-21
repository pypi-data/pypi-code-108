'''_1368.py

TwodimensionalFunctionLookupTable
'''


from mastapy.math_utility.measured_data import _1365, _1366
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_TWODIMENSIONAL_FUNCTION_LOOKUP_TABLE = python_net_import('SMT.MastaAPI.MathUtility.MeasuredData', 'TwodimensionalFunctionLookupTable')


__docformat__ = 'restructuredtext en'
__all__ = ('TwodimensionalFunctionLookupTable',)


class TwodimensionalFunctionLookupTable(_1366.LookupTableBase['TwodimensionalFunctionLookupTable']):
    '''TwodimensionalFunctionLookupTable

    This is a mastapy class.
    '''

    TYPE = _TWODIMENSIONAL_FUNCTION_LOOKUP_TABLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TwodimensionalFunctionLookupTable.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def lookup_table(self) -> '_1365.GriddedSurfaceAccessor':
        '''GriddedSurfaceAccessor: 'LookupTable' is the original name of this property.'''

        return constructor.new(_1365.GriddedSurfaceAccessor)(self.wrapped.LookupTable) if self.wrapped.LookupTable is not None else None

    @lookup_table.setter
    def lookup_table(self, value: '_1365.GriddedSurfaceAccessor'):
        value = value.wrapped if value else None
        self.wrapped.LookupTable = value
