'''_6717.py

PowerLoadInputOptions
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.part_model import _2213
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.utility_gui import _1614
from mastapy._internal.python_net import python_net_import

_POWER_LOAD_INPUT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads.DutyCycleDefinition', 'PowerLoadInputOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadInputOptions',)


class PowerLoadInputOptions(_1614.ColumnInputOptions):
    '''PowerLoadInputOptions

    This is a mastapy class.
    '''

    TYPE = _POWER_LOAD_INPUT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerLoadInputOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def power_load(self) -> 'list_with_selected_item.ListWithSelectedItem_PowerLoad':
        '''list_with_selected_item.ListWithSelectedItem_PowerLoad: 'PowerLoad' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_PowerLoad)(self.wrapped.PowerLoad) if self.wrapped.PowerLoad is not None else None

    @power_load.setter
    def power_load(self, value: 'list_with_selected_item.ListWithSelectedItem_PowerLoad.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_PowerLoad.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_PowerLoad.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.PowerLoad = value
