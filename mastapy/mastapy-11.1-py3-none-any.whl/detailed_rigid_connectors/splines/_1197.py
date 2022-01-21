'''_1197.py

GBT3478SplineJointDesign
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.bearings.tolerances import _1666
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.detailed_rigid_connectors.splines import _1200
from mastapy._internal.python_net import python_net_import

_GBT3478_SPLINE_JOINT_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'GBT3478SplineJointDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('GBT3478SplineJointDesign',)


class GBT3478SplineJointDesign(_1200.ISO4156SplineJointDesign):
    '''GBT3478SplineJointDesign

    This is a mastapy class.
    '''

    TYPE = _GBT3478_SPLINE_JOINT_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GBT3478SplineJointDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def external_minimum_major_diameter(self) -> 'float':
        '''float: 'ExternalMinimumMajorDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ExternalMinimumMajorDiameter

    @property
    def major_diameter_standard_tolerance_grade(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ITDesignation':
        '''enum_with_selected_value.EnumWithSelectedValue_ITDesignation: 'MajorDiameterStandardToleranceGrade' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ITDesignation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.MajorDiameterStandardToleranceGrade, value) if self.wrapped.MajorDiameterStandardToleranceGrade is not None else None

    @major_diameter_standard_tolerance_grade.setter
    def major_diameter_standard_tolerance_grade(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ITDesignation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ITDesignation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.MajorDiameterStandardToleranceGrade = value

    @property
    def minor_diameter_standard_tolerance_grade(self) -> 'enum_with_selected_value.EnumWithSelectedValue_ITDesignation':
        '''enum_with_selected_value.EnumWithSelectedValue_ITDesignation: 'MinorDiameterStandardToleranceGrade' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_ITDesignation.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.MinorDiameterStandardToleranceGrade, value) if self.wrapped.MinorDiameterStandardToleranceGrade is not None else None

    @minor_diameter_standard_tolerance_grade.setter
    def minor_diameter_standard_tolerance_grade(self, value: 'enum_with_selected_value.EnumWithSelectedValue_ITDesignation.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ITDesignation.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.MinorDiameterStandardToleranceGrade = value
