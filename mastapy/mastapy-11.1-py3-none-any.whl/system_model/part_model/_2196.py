'''_2196.py

GuideDxfModel
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy.utility.units_and_measurements import _1403
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.system_model.part_model import _2186
from mastapy._internal.python_net import python_net_import

_GUIDE_DXF_MODEL = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'GuideDxfModel')


__docformat__ = 'restructuredtext en'
__all__ = ('GuideDxfModel',)


class GuideDxfModel(_2186.Component):
    '''GuideDxfModel

    This is a mastapy class.
    '''

    TYPE = _GUIDE_DXF_MODEL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GuideDxfModel.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def length_unit(self) -> 'list_with_selected_item.ListWithSelectedItem_Unit':
        '''list_with_selected_item.ListWithSelectedItem_Unit: 'LengthUnit' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_Unit)(self.wrapped.LengthUnit) if self.wrapped.LengthUnit is not None else None

    @length_unit.setter
    def length_unit(self, value: 'list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_Unit.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.LengthUnit = value

    @property
    def scale_factor(self) -> 'float':
        '''float: 'ScaleFactor' is the original name of this property.'''

        return self.wrapped.ScaleFactor

    @scale_factor.setter
    def scale_factor(self, value: 'float'):
        self.wrapped.ScaleFactor = float(value) if value else 0.0
