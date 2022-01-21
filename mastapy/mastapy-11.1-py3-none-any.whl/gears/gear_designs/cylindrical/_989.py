'''_989.py

CylindricalGearTableWithMGCharts
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.cylindrical import _988
from mastapy.utility.report import _1553
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_TABLE_WITH_MG_CHARTS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearTableWithMGCharts')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearTableWithMGCharts',)


class CylindricalGearTableWithMGCharts(_1553.CustomTable):
    '''CylindricalGearTableWithMGCharts

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_TABLE_WITH_MG_CHARTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearTableWithMGCharts.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def chart_height(self) -> 'int':
        '''int: 'ChartHeight' is the original name of this property.'''

        return self.wrapped.ChartHeight

    @chart_height.setter
    def chart_height(self, value: 'int'):
        self.wrapped.ChartHeight = int(value) if value else 0

    @property
    def chart_width(self) -> 'int':
        '''int: 'ChartWidth' is the original name of this property.'''

        return self.wrapped.ChartWidth

    @chart_width.setter
    def chart_width(self, value: 'int'):
        self.wrapped.ChartWidth = int(value) if value else 0

    @property
    def item_detail(self) -> '_988.CylindricalGearTableMGItemDetail':
        '''CylindricalGearTableMGItemDetail: 'ItemDetail' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ItemDetail)
        return constructor.new(_988.CylindricalGearTableMGItemDetail)(value) if value is not None else None

    @item_detail.setter
    def item_detail(self, value: '_988.CylindricalGearTableMGItemDetail'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ItemDetail = value
