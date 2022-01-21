'''_2017.py

CylindricalComponentConnection
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets import _2012
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_COMPONENT_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'CylindricalComponentConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalComponentConnection',)


class CylindricalComponentConnection(_2012.ComponentConnection):
    '''CylindricalComponentConnection

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_COMPONENT_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalComponentConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def measuring_position_for_component(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'MeasuringPositionForComponent' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.MeasuringPositionForComponent) if self.wrapped.MeasuringPositionForComponent is not None else None

    @measuring_position_for_component.setter
    def measuring_position_for_component(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.MeasuringPositionForComponent = value

    @property
    def measuring_position_for_connected_component(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'MeasuringPositionForConnectedComponent' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.MeasuringPositionForConnectedComponent) if self.wrapped.MeasuringPositionForConnectedComponent is not None else None

    @measuring_position_for_connected_component.setter
    def measuring_position_for_connected_component(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.MeasuringPositionForConnectedComponent = value
