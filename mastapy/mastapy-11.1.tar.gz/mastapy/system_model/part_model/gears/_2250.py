'''_2250.py

ActiveCylindricalGearSetDesignSelection
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.system_model.part_model.gears import _2251
from mastapy._internal.python_net import python_net_import

_ACTIVE_CYLINDRICAL_GEAR_SET_DESIGN_SELECTION = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'ActiveCylindricalGearSetDesignSelection')


__docformat__ = 'restructuredtext en'
__all__ = ('ActiveCylindricalGearSetDesignSelection',)


class ActiveCylindricalGearSetDesignSelection(_2251.ActiveGearSetDesignSelection):
    '''ActiveCylindricalGearSetDesignSelection

    This is a mastapy class.
    '''

    TYPE = _ACTIVE_CYLINDRICAL_GEAR_SET_DESIGN_SELECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ActiveCylindricalGearSetDesignSelection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def micro_geometry_selection(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'MicroGeometrySelection' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.MicroGeometrySelection) if self.wrapped.MicroGeometrySelection is not None else None

    @micro_geometry_selection.setter
    def micro_geometry_selection(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.MicroGeometrySelection = value
