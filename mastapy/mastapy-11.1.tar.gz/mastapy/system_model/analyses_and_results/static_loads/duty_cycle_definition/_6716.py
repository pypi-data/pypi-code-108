'''_6716.py

PointLoadInputOptions
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.part_model import _2212
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.math_utility import _1290
from mastapy.system_model.analyses_and_results.static_loads.duty_cycle_definition import _6707
from mastapy.utility_gui import _1614
from mastapy._internal.python_net import python_net_import

_POINT_LOAD_INPUT_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads.DutyCycleDefinition', 'PointLoadInputOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoadInputOptions',)


class PointLoadInputOptions(_1614.ColumnInputOptions):
    '''PointLoadInputOptions

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD_INPUT_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoadInputOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def point_load(self) -> 'list_with_selected_item.ListWithSelectedItem_PointLoad':
        '''list_with_selected_item.ListWithSelectedItem_PointLoad: 'PointLoad' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_PointLoad)(self.wrapped.PointLoad) if self.wrapped.PointLoad is not None else None

    @point_load.setter
    def point_load(self, value: 'list_with_selected_item.ListWithSelectedItem_PointLoad.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_PointLoad.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_PointLoad.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.PointLoad = value

    @property
    def axis(self) -> '_1290.Axis':
        '''Axis: 'Axis' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Axis)
        return constructor.new(_1290.Axis)(value) if value is not None else None

    @axis.setter
    def axis(self, value: '_1290.Axis'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Axis = value

    @property
    def conversion_to_load_case(self) -> '_6707.AdditionalForcesObtainedFrom':
        '''AdditionalForcesObtainedFrom: 'ConversionToLoadCase' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ConversionToLoadCase)
        return constructor.new(_6707.AdditionalForcesObtainedFrom)(value) if value is not None else None

    @conversion_to_load_case.setter
    def conversion_to_load_case(self, value: '_6707.AdditionalForcesObtainedFrom'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ConversionToLoadCase = value
