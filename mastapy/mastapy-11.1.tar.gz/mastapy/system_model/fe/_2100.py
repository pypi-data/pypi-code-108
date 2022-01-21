'''_2100.py

AlignmentUsingAxialNodePositions
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.math_utility import _1289
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ALIGNMENT_USING_AXIAL_NODE_POSITIONS = python_net_import('SMT.MastaAPI.SystemModel.FE', 'AlignmentUsingAxialNodePositions')


__docformat__ = 'restructuredtext en'
__all__ = ('AlignmentUsingAxialNodePositions',)


class AlignmentUsingAxialNodePositions(_0.APIBase):
    '''AlignmentUsingAxialNodePositions

    This is a mastapy class.
    '''

    TYPE = _ALIGNMENT_USING_AXIAL_NODE_POSITIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AlignmentUsingAxialNodePositions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rotation_angle(self) -> 'float':
        '''float: 'RotationAngle' is the original name of this property.'''

        return self.wrapped.RotationAngle

    @rotation_angle.setter
    def rotation_angle(self, value: 'float'):
        self.wrapped.RotationAngle = float(value) if value else 0.0

    @property
    def fe_axis_for_angle_alignment(self) -> 'enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis':
        '''enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis: 'FEAxisForAngleAlignment' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.FEAxisForAngleAlignment, value) if self.wrapped.FEAxisForAngleAlignment is not None else None

    @fe_axis_for_angle_alignment.setter
    def fe_axis_for_angle_alignment(self, value: 'enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_AlignmentAxis.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.FEAxisForAngleAlignment = value
