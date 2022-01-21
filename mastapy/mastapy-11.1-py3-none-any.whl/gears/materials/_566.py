'''_566.py

RawMaterial
'''


from mastapy._internal import constructor
from mastapy.utility.databases import _1597
from mastapy._internal.python_net import python_net_import

_RAW_MATERIAL = python_net_import('SMT.MastaAPI.Gears.Materials', 'RawMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('RawMaterial',)


class RawMaterial(_1597.NamedDatabaseItem):
    '''RawMaterial

    This is a mastapy class.
    '''

    TYPE = _RAW_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RawMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cost_per_kilogram(self) -> 'float':
        '''float: 'CostPerKilogram' is the original name of this property.'''

        return self.wrapped.CostPerKilogram

    @cost_per_kilogram.setter
    def cost_per_kilogram(self, value: 'float'):
        self.wrapped.CostPerKilogram = float(value) if value else 0.0
