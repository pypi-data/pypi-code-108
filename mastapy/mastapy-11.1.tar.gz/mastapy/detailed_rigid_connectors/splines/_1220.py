'''_1220.py

StandardSplineJointDesign
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value
from mastapy.detailed_rigid_connectors.splines import (
    _1203, _1204, _1205, _1215
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal.python_net import python_net_import

_STANDARD_SPLINE_JOINT_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines', 'StandardSplineJointDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('StandardSplineJointDesign',)


class StandardSplineJointDesign(_1215.SplineJointDesign):
    '''StandardSplineJointDesign

    This is a mastapy class.
    '''

    TYPE = _STANDARD_SPLINE_JOINT_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StandardSplineJointDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def diametral_pitch(self) -> 'float':
        '''float: 'DiametralPitch' is the original name of this property.'''

        return self.wrapped.DiametralPitch

    @diametral_pitch.setter
    def diametral_pitch(self, value: 'float'):
        self.wrapped.DiametralPitch = float(value) if value else 0.0

    @property
    def module(self) -> 'float':
        '''float: 'Module' is the original name of this property.'''

        return self.wrapped.Module

    @module.setter
    def module(self, value: 'float'):
        self.wrapped.Module = float(value) if value else 0.0

    @property
    def module_preferred(self) -> 'enum_with_selected_value.EnumWithSelectedValue_Modules':
        '''enum_with_selected_value.EnumWithSelectedValue_Modules: 'ModulePreferred' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_Modules.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ModulePreferred, value) if self.wrapped.ModulePreferred is not None else None

    @module_preferred.setter
    def module_preferred(self, value: 'enum_with_selected_value.EnumWithSelectedValue_Modules.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_Modules.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ModulePreferred = value

    @property
    def module_from_preferred_series(self) -> 'bool':
        '''bool: 'ModuleFromPreferredSeries' is the original name of this property.'''

        return self.wrapped.ModuleFromPreferredSeries

    @module_from_preferred_series.setter
    def module_from_preferred_series(self, value: 'bool'):
        self.wrapped.ModuleFromPreferredSeries = bool(value) if value else False

    @property
    def pressure_angle_preferred(self) -> 'enum_with_selected_value.EnumWithSelectedValue_PressureAngleTypes':
        '''enum_with_selected_value.EnumWithSelectedValue_PressureAngleTypes: 'PressureAnglePreferred' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_PressureAngleTypes.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.PressureAnglePreferred, value) if self.wrapped.PressureAnglePreferred is not None else None

    @pressure_angle_preferred.setter
    def pressure_angle_preferred(self, value: 'enum_with_selected_value.EnumWithSelectedValue_PressureAngleTypes.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_PressureAngleTypes.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.PressureAnglePreferred = value

    @property
    def pressure_angle(self) -> 'float':
        '''float: 'PressureAngle' is the original name of this property.'''

        return self.wrapped.PressureAngle

    @pressure_angle.setter
    def pressure_angle(self, value: 'float'):
        self.wrapped.PressureAngle = float(value) if value else 0.0

    @property
    def root_type(self) -> '_1205.RootTypes':
        '''RootTypes: 'RootType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.RootType)
        return constructor.new(_1205.RootTypes)(value) if value is not None else None

    @root_type.setter
    def root_type(self, value: '_1205.RootTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.RootType = value
