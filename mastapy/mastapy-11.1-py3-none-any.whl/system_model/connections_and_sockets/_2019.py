'''_2019.py

DatumMeasurement
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.system_model.connections_and_sockets import _2013
from mastapy._internal.python_net import python_net_import

_DATUM_MEASUREMENT = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets', 'DatumMeasurement')


__docformat__ = 'restructuredtext en'
__all__ = ('DatumMeasurement',)


class DatumMeasurement(_2013.ComponentMeasurer):
    '''DatumMeasurement

    This is a mastapy class.
    '''

    TYPE = _DATUM_MEASUREMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DatumMeasurement.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def measuring_position(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'MeasuringPosition' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.MeasuringPosition) if self.wrapped.MeasuringPosition is not None else None

    @measuring_position.setter
    def measuring_position(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.MeasuringPosition = value
