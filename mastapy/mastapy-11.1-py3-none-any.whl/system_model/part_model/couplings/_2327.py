'''_2327.py

CVTPulley
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.part_model.couplings import _2338, _2330
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import

_CVT_PULLEY = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'CVTPulley')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTPulley',)


class CVTPulley(_2330.Pulley):
    '''CVTPulley

    This is a mastapy class.
    '''

    TYPE = _CVT_PULLEY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTPulley.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_moving_sheave_on_the_left(self) -> 'bool':
        '''bool: 'IsMovingSheaveOnTheLeft' is the original name of this property.'''

        return self.wrapped.IsMovingSheaveOnTheLeft

    @is_moving_sheave_on_the_left.setter
    def is_moving_sheave_on_the_left(self, value: 'bool'):
        self.wrapped.IsMovingSheaveOnTheLeft = bool(value) if value else False

    @property
    def sliding_connection(self) -> 'list_with_selected_item.ListWithSelectedItem_ShaftHubConnection':
        '''list_with_selected_item.ListWithSelectedItem_ShaftHubConnection: 'SlidingConnection' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_ShaftHubConnection)(self.wrapped.SlidingConnection) if self.wrapped.SlidingConnection is not None else None

    @sliding_connection.setter
    def sliding_connection(self, value: 'list_with_selected_item.ListWithSelectedItem_ShaftHubConnection.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_ShaftHubConnection.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_ShaftHubConnection.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.SlidingConnection = value
