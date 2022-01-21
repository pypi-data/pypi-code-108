'''_697.py

MutatableCommon
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.gears.manufacturing.cylindrical import _569
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.manufacturing.cylindrical.cutters import _681
from mastapy._internal.python_net import python_net_import

_MUTATABLE_COMMON = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters', 'MutatableCommon')


__docformat__ = 'restructuredtext en'
__all__ = ('MutatableCommon',)


class MutatableCommon(_681.CurveInLinkedList):
    '''MutatableCommon

    This is a mastapy class.
    '''

    TYPE = _MUTATABLE_COMMON

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MutatableCommon.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.'''

        return self.wrapped.Radius

    @radius.setter
    def radius(self, value: 'float'):
        self.wrapped.Radius = float(value) if value else 0.0

    @property
    def section(self) -> 'enum_with_selected_value.EnumWithSelectedValue_CutterFlankSections':
        '''enum_with_selected_value.EnumWithSelectedValue_CutterFlankSections: 'Section' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_CutterFlankSections.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.Section, value) if self.wrapped.Section is not None else None

    @section.setter
    def section(self, value: 'enum_with_selected_value.EnumWithSelectedValue_CutterFlankSections.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_CutterFlankSections.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.Section = value

    @property
    def protuberance(self) -> 'float':
        '''float: 'Protuberance' is the original name of this property.'''

        return self.wrapped.Protuberance

    @protuberance.setter
    def protuberance(self, value: 'float'):
        self.wrapped.Protuberance = float(value) if value else 0.0

    def split(self):
        ''' 'Split' is the original name of this method.'''

        self.wrapped.Split()

    def remove(self):
        ''' 'Remove' is the original name of this method.'''

        self.wrapped.Remove()
