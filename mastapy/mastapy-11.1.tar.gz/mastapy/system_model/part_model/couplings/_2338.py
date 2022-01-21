'''_2338.py

ShaftHubConnection
'''


from typing import List

from PIL.Image import Image

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import overridable, enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.system_model.part_model.couplings import (
    _2332, _2335, _2331, _2334,
    _2339, _2333
)
from mastapy.detailed_rigid_connectors.splines import (
    _1210, _1195, _1215, _1190,
    _1193, _1197, _1200, _1201,
    _1208, _1220
)
from mastapy._internal.python_net import python_net_import
from mastapy._internal.cast_exception import CastException
from mastapy.detailed_rigid_connectors.interference_fits import _1245
from mastapy.detailed_rigid_connectors.keyed_joints import _1237
from mastapy.nodal_analysis import _54
from mastapy.system_model.part_model import _2189

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_ARRAY = python_net_import('System', 'Array')
_SHAFT_HUB_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'ShaftHubConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftHubConnection',)


class ShaftHubConnection(_2189.Connector):
    '''ShaftHubConnection

    This is a mastapy class.
    '''

    TYPE = _SHAFT_HUB_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftHubConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.'''

        return self.wrapped.Length

    @length.setter
    def length(self, value: 'float'):
        self.wrapped.Length = float(value) if value else 0.0

    @property
    def radial_clearance(self) -> 'float':
        '''float: 'RadialClearance' is the original name of this property.'''

        return self.wrapped.RadialClearance

    @radial_clearance.setter
    def radial_clearance(self, value: 'float'):
        self.wrapped.RadialClearance = float(value) if value else 0.0

    @property
    def tilt_clearance(self) -> 'float':
        '''float: 'TiltClearance' is the original name of this property.'''

        return self.wrapped.TiltClearance

    @tilt_clearance.setter
    def tilt_clearance(self, value: 'float'):
        self.wrapped.TiltClearance = float(value) if value else 0.0

    @property
    def major_diameter_diametral_clearance(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MajorDiameterDiametralClearance' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MajorDiameterDiametralClearance) if self.wrapped.MajorDiameterDiametralClearance is not None else None

    @major_diameter_diametral_clearance.setter
    def major_diameter_diametral_clearance(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MajorDiameterDiametralClearance = value

    @property
    def torsional_stiffness_shaft_hub_connection(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TorsionalStiffnessShaftHubConnection' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TorsionalStiffnessShaftHubConnection) if self.wrapped.TorsionalStiffnessShaftHubConnection is not None else None

    @torsional_stiffness_shaft_hub_connection.setter
    def torsional_stiffness_shaft_hub_connection(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TorsionalStiffnessShaftHubConnection = value

    @property
    def radial_stiffness_shaft_hub_connection(self) -> 'float':
        '''float: 'RadialStiffnessShaftHubConnection' is the original name of this property.'''

        return self.wrapped.RadialStiffnessShaftHubConnection

    @radial_stiffness_shaft_hub_connection.setter
    def radial_stiffness_shaft_hub_connection(self, value: 'float'):
        self.wrapped.RadialStiffnessShaftHubConnection = float(value) if value else 0.0

    @property
    def axial_stiffness_shaft_hub_connection(self) -> 'float':
        '''float: 'AxialStiffnessShaftHubConnection' is the original name of this property.'''

        return self.wrapped.AxialStiffnessShaftHubConnection

    @axial_stiffness_shaft_hub_connection.setter
    def axial_stiffness_shaft_hub_connection(self, value: 'float'):
        self.wrapped.AxialStiffnessShaftHubConnection = float(value) if value else 0.0

    @property
    def additional_tilt_stiffness(self) -> 'float':
        '''float: 'AdditionalTiltStiffness' is the original name of this property.'''

        return self.wrapped.AdditionalTiltStiffness

    @additional_tilt_stiffness.setter
    def additional_tilt_stiffness(self, value: 'float'):
        self.wrapped.AdditionalTiltStiffness = float(value) if value else 0.0

    @property
    def tilt_stiffness_shaft_hub_connection(self) -> 'float':
        '''float: 'TiltStiffnessShaftHubConnection' is the original name of this property.'''

        return self.wrapped.TiltStiffnessShaftHubConnection

    @tilt_stiffness_shaft_hub_connection.setter
    def tilt_stiffness_shaft_hub_connection(self, value: 'float'):
        self.wrapped.TiltStiffnessShaftHubConnection = float(value) if value else 0.0

    @property
    def outer_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterDiameter) if self.wrapped.OuterDiameter is not None else None

    @outer_diameter.setter
    def outer_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterDiameter = value

    @property
    def inner_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerDiameter) if self.wrapped.InnerDiameter is not None else None

    @inner_diameter.setter
    def inner_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerDiameter = value

    @property
    def tilt_stiffness_type(self) -> '_2332.RigidConnectorTiltStiffnessTypes':
        '''RigidConnectorTiltStiffnessTypes: 'TiltStiffnessType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.TiltStiffnessType)
        return constructor.new(_2332.RigidConnectorTiltStiffnessTypes)(value) if value is not None else None

    @tilt_stiffness_type.setter
    def tilt_stiffness_type(self, value: '_2332.RigidConnectorTiltStiffnessTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.TiltStiffnessType = value

    @property
    def type_(self) -> 'enum_with_selected_value.EnumWithSelectedValue_RigidConnectorTypes':
        '''enum_with_selected_value.EnumWithSelectedValue_RigidConnectorTypes: 'Type' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_RigidConnectorTypes.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.Type, value) if self.wrapped.Type is not None else None

    @type_.setter
    def type_(self, value: 'enum_with_selected_value.EnumWithSelectedValue_RigidConnectorTypes.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_RigidConnectorTypes.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.Type = value

    @property
    def spline_type(self) -> '_1210.SplineDesignTypes':
        '''SplineDesignTypes: 'SplineType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.SplineType)
        return constructor.new(_1210.SplineDesignTypes)(value) if value is not None else None

    @spline_type.setter
    def spline_type(self, value: '_1210.SplineDesignTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.SplineType = value

    @property
    def torsional_twist_preload(self) -> 'float':
        '''float: 'TorsionalTwistPreload' is the original name of this property.'''

        return self.wrapped.TorsionalTwistPreload

    @torsional_twist_preload.setter
    def torsional_twist_preload(self, value: 'float'):
        self.wrapped.TorsionalTwistPreload = float(value) if value else 0.0

    @property
    def axial_preload(self) -> 'float':
        '''float: 'AxialPreload' is the original name of this property.'''

        return self.wrapped.AxialPreload

    @axial_preload.setter
    def axial_preload(self, value: 'float'):
        self.wrapped.AxialPreload = float(value) if value else 0.0

    @property
    def two_d_spline_drawing(self) -> 'Image':
        '''Image: 'TwoDSplineDrawing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.TwoDSplineDrawing)
        return value

    @property
    def inner_half_material(self) -> 'str':
        '''str: 'InnerHalfMaterial' is the original name of this property.'''

        return self.wrapped.InnerHalfMaterial.SelectedItemName

    @inner_half_material.setter
    def inner_half_material(self, value: 'str'):
        self.wrapped.InnerHalfMaterial.SetSelectedItem(str(value) if value else '')

    @property
    def outer_half_material(self) -> 'str':
        '''str: 'OuterHalfMaterial' is the original name of this property.'''

        return self.wrapped.OuterHalfMaterial.SelectedItemName

    @outer_half_material.setter
    def outer_half_material(self, value: 'str'):
        self.wrapped.OuterHalfMaterial.SetSelectedItem(str(value) if value else '')

    @property
    def stiffness_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_RigidConnectorStiffnessType':
        '''enum_with_selected_value.EnumWithSelectedValue_RigidConnectorStiffnessType: 'StiffnessType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_RigidConnectorStiffnessType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.StiffnessType, value) if self.wrapped.StiffnessType is not None else None

    @stiffness_type.setter
    def stiffness_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_RigidConnectorStiffnessType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_RigidConnectorStiffnessType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.StiffnessType = value

    @property
    def contact_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ContactDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ContactDiameter) if self.wrapped.ContactDiameter is not None else None

    @contact_diameter.setter
    def contact_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ContactDiameter = value

    @property
    def number_of_connection_points(self) -> 'int':
        '''int: 'NumberOfConnectionPoints' is the original name of this property.'''

        return self.wrapped.NumberOfConnectionPoints

    @number_of_connection_points.setter
    def number_of_connection_points(self, value: 'int'):
        self.wrapped.NumberOfConnectionPoints = int(value) if value else 0

    @property
    def number_of_contacts_per_direction(self) -> 'int':
        '''int: 'NumberOfContactsPerDirection' is the original name of this property.'''

        return self.wrapped.NumberOfContactsPerDirection

    @number_of_contacts_per_direction.setter
    def number_of_contacts_per_direction(self, value: 'int'):
        self.wrapped.NumberOfContactsPerDirection = int(value) if value else 0

    @property
    def angular_extent_of_external_teeth(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AngularExtentOfExternalTeeth' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AngularExtentOfExternalTeeth) if self.wrapped.AngularExtentOfExternalTeeth is not None else None

    @angular_extent_of_external_teeth.setter
    def angular_extent_of_external_teeth(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AngularExtentOfExternalTeeth = value

    @property
    def angle_of_first_connection_point(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'AngleOfFirstConnectionPoint' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.AngleOfFirstConnectionPoint) if self.wrapped.AngleOfFirstConnectionPoint is not None else None

    @angle_of_first_connection_point.setter
    def angle_of_first_connection_point(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.AngleOfFirstConnectionPoint = value

    @property
    def centre_angle_of_first_external_tooth(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CentreAngleOfFirstExternalTooth' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CentreAngleOfFirstExternalTooth) if self.wrapped.CentreAngleOfFirstExternalTooth is not None else None

    @centre_angle_of_first_external_tooth.setter
    def centre_angle_of_first_external_tooth(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CentreAngleOfFirstExternalTooth = value

    @property
    def flank_contact_stiffness(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'FlankContactStiffness' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.FlankContactStiffness) if self.wrapped.FlankContactStiffness is not None else None

    @flank_contact_stiffness.setter
    def flank_contact_stiffness(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.FlankContactStiffness = value

    @property
    def major_diameter_contact_stiffness(self) -> 'float':
        '''float: 'MajorDiameterContactStiffness' is the original name of this property.'''

        return self.wrapped.MajorDiameterContactStiffness

    @major_diameter_contact_stiffness.setter
    def major_diameter_contact_stiffness(self, value: 'float'):
        self.wrapped.MajorDiameterContactStiffness = float(value) if value else 0.0

    @property
    def pressure_angle(self) -> 'float':
        '''float: 'PressureAngle' is the original name of this property.'''

        return self.wrapped.PressureAngle

    @pressure_angle.setter
    def pressure_angle(self, value: 'float'):
        self.wrapped.PressureAngle = float(value) if value else 0.0

    @property
    def normal_clearance(self) -> 'float':
        '''float: 'NormalClearance' is the original name of this property.'''

        return self.wrapped.NormalClearance

    @normal_clearance.setter
    def normal_clearance(self, value: 'float'):
        self.wrapped.NormalClearance = float(value) if value else 0.0

    @property
    def angular_backlash(self) -> 'float':
        '''float: 'AngularBacklash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularBacklash

    @property
    def helix_angle(self) -> 'float':
        '''float: 'HelixAngle' is the original name of this property.'''

        return self.wrapped.HelixAngle

    @helix_angle.setter
    def helix_angle(self, value: 'float'):
        self.wrapped.HelixAngle = float(value) if value else 0.0

    @property
    def left_flank_helix_angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'LeftFlankHelixAngle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.LeftFlankHelixAngle) if self.wrapped.LeftFlankHelixAngle is not None else None

    @left_flank_helix_angle.setter
    def left_flank_helix_angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.LeftFlankHelixAngle = value

    @property
    def right_flank_helix_angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RightFlankHelixAngle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RightFlankHelixAngle) if self.wrapped.RightFlankHelixAngle is not None else None

    @right_flank_helix_angle.setter
    def right_flank_helix_angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RightFlankHelixAngle = value

    @property
    def type_of_fit(self) -> 'enum_with_selected_value.EnumWithSelectedValue_FitTypes':
        '''enum_with_selected_value.EnumWithSelectedValue_FitTypes: 'TypeOfFit' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_FitTypes.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.TypeOfFit, value) if self.wrapped.TypeOfFit is not None else None

    @type_of_fit.setter
    def type_of_fit(self, value: 'enum_with_selected_value.EnumWithSelectedValue_FitTypes.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_FitTypes.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.TypeOfFit = value

    @property
    def tooth_spacing_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_RigidConnectorToothSpacingType':
        '''enum_with_selected_value.EnumWithSelectedValue_RigidConnectorToothSpacingType: 'ToothSpacingType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_RigidConnectorToothSpacingType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.ToothSpacingType, value) if self.wrapped.ToothSpacingType is not None else None

    @tooth_spacing_type.setter
    def tooth_spacing_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_RigidConnectorToothSpacingType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_RigidConnectorToothSpacingType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.ToothSpacingType = value

    @property
    def coefficient_of_friction(self) -> 'float':
        '''float: 'CoefficientOfFriction' is the original name of this property.'''

        return self.wrapped.CoefficientOfFriction

    @coefficient_of_friction.setter
    def coefficient_of_friction(self, value: 'float'):
        self.wrapped.CoefficientOfFriction = float(value) if value else 0.0

    @property
    def tangential_stiffness(self) -> 'float':
        '''float: 'TangentialStiffness' is the original name of this property.'''

        return self.wrapped.TangentialStiffness

    @tangential_stiffness.setter
    def tangential_stiffness(self, value: 'float'):
        self.wrapped.TangentialStiffness = float(value) if value else 0.0

    @property
    def spline_joint_design(self) -> '_1215.SplineJointDesign':
        '''SplineJointDesign: 'SplineJointDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1215.SplineJointDesign.TYPE not in self.wrapped.SplineJointDesign.__class__.__mro__:
            raise CastException('Failed to cast spline_joint_design to SplineJointDesign. Expected: {}.'.format(self.wrapped.SplineJointDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SplineJointDesign.__class__)(self.wrapped.SplineJointDesign) if self.wrapped.SplineJointDesign is not None else None

    @property
    def spline_joint_design_of_type_custom_spline_joint_design(self) -> '_1190.CustomSplineJointDesign':
        '''CustomSplineJointDesign: 'SplineJointDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1190.CustomSplineJointDesign.TYPE not in self.wrapped.SplineJointDesign.__class__.__mro__:
            raise CastException('Failed to cast spline_joint_design to CustomSplineJointDesign. Expected: {}.'.format(self.wrapped.SplineJointDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SplineJointDesign.__class__)(self.wrapped.SplineJointDesign) if self.wrapped.SplineJointDesign is not None else None

    @property
    def spline_joint_design_of_type_din5480_spline_joint_design(self) -> '_1193.DIN5480SplineJointDesign':
        '''DIN5480SplineJointDesign: 'SplineJointDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1193.DIN5480SplineJointDesign.TYPE not in self.wrapped.SplineJointDesign.__class__.__mro__:
            raise CastException('Failed to cast spline_joint_design to DIN5480SplineJointDesign. Expected: {}.'.format(self.wrapped.SplineJointDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SplineJointDesign.__class__)(self.wrapped.SplineJointDesign) if self.wrapped.SplineJointDesign is not None else None

    @property
    def spline_joint_design_of_type_gbt3478_spline_joint_design(self) -> '_1197.GBT3478SplineJointDesign':
        '''GBT3478SplineJointDesign: 'SplineJointDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1197.GBT3478SplineJointDesign.TYPE not in self.wrapped.SplineJointDesign.__class__.__mro__:
            raise CastException('Failed to cast spline_joint_design to GBT3478SplineJointDesign. Expected: {}.'.format(self.wrapped.SplineJointDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SplineJointDesign.__class__)(self.wrapped.SplineJointDesign) if self.wrapped.SplineJointDesign is not None else None

    @property
    def spline_joint_design_of_type_iso4156_spline_joint_design(self) -> '_1200.ISO4156SplineJointDesign':
        '''ISO4156SplineJointDesign: 'SplineJointDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1200.ISO4156SplineJointDesign.TYPE not in self.wrapped.SplineJointDesign.__class__.__mro__:
            raise CastException('Failed to cast spline_joint_design to ISO4156SplineJointDesign. Expected: {}.'.format(self.wrapped.SplineJointDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SplineJointDesign.__class__)(self.wrapped.SplineJointDesign) if self.wrapped.SplineJointDesign is not None else None

    @property
    def spline_joint_design_of_type_jisb1603_spline_joint_design(self) -> '_1201.JISB1603SplineJointDesign':
        '''JISB1603SplineJointDesign: 'SplineJointDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1201.JISB1603SplineJointDesign.TYPE not in self.wrapped.SplineJointDesign.__class__.__mro__:
            raise CastException('Failed to cast spline_joint_design to JISB1603SplineJointDesign. Expected: {}.'.format(self.wrapped.SplineJointDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SplineJointDesign.__class__)(self.wrapped.SplineJointDesign) if self.wrapped.SplineJointDesign is not None else None

    @property
    def spline_joint_design_of_type_sae_spline_joint_design(self) -> '_1208.SAESplineJointDesign':
        '''SAESplineJointDesign: 'SplineJointDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1208.SAESplineJointDesign.TYPE not in self.wrapped.SplineJointDesign.__class__.__mro__:
            raise CastException('Failed to cast spline_joint_design to SAESplineJointDesign. Expected: {}.'.format(self.wrapped.SplineJointDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SplineJointDesign.__class__)(self.wrapped.SplineJointDesign) if self.wrapped.SplineJointDesign is not None else None

    @property
    def spline_joint_design_of_type_standard_spline_joint_design(self) -> '_1220.StandardSplineJointDesign':
        '''StandardSplineJointDesign: 'SplineJointDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1220.StandardSplineJointDesign.TYPE not in self.wrapped.SplineJointDesign.__class__.__mro__:
            raise CastException('Failed to cast spline_joint_design to StandardSplineJointDesign. Expected: {}.'.format(self.wrapped.SplineJointDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.SplineJointDesign.__class__)(self.wrapped.SplineJointDesign) if self.wrapped.SplineJointDesign is not None else None

    @property
    def interference_fit_design(self) -> '_1245.InterferenceFitDesign':
        '''InterferenceFitDesign: 'InterferenceFitDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1245.InterferenceFitDesign.TYPE not in self.wrapped.InterferenceFitDesign.__class__.__mro__:
            raise CastException('Failed to cast interference_fit_design to InterferenceFitDesign. Expected: {}.'.format(self.wrapped.InterferenceFitDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.InterferenceFitDesign.__class__)(self.wrapped.InterferenceFitDesign) if self.wrapped.InterferenceFitDesign is not None else None

    @property
    def nonlinear_stiffness(self) -> '_54.DiagonalNonlinearStiffness':
        '''DiagonalNonlinearStiffness: 'NonlinearStiffness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_54.DiagonalNonlinearStiffness)(self.wrapped.NonlinearStiffness) if self.wrapped.NonlinearStiffness is not None else None

    @property
    def left_flank_lead_relief(self) -> '_2339.SplineLeadRelief':
        '''SplineLeadRelief: 'LeftFlankLeadRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2339.SplineLeadRelief)(self.wrapped.LeftFlankLeadRelief) if self.wrapped.LeftFlankLeadRelief is not None else None

    @property
    def right_flank_lead_relief(self) -> '_2339.SplineLeadRelief':
        '''SplineLeadRelief: 'RightFlankLeadRelief' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2339.SplineLeadRelief)(self.wrapped.RightFlankLeadRelief) if self.wrapped.RightFlankLeadRelief is not None else None

    @property
    def tooth_locations_external_spline_half(self) -> 'List[_2333.RigidConnectorToothLocation]':
        '''List[RigidConnectorToothLocation]: 'ToothLocationsExternalSplineHalf' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ToothLocationsExternalSplineHalf, constructor.new(_2333.RigidConnectorToothLocation))
        return value

    @property
    def lead_reliefs(self) -> 'List[_2339.SplineLeadRelief]':
        '''List[SplineLeadRelief]: 'LeadReliefs' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LeadReliefs, constructor.new(_2339.SplineLeadRelief))
        return value

    @property
    def full_stiffness_matrix(self) -> 'List[List[float]]':
        '''List[List[float]]: 'FullStiffnessMatrix' is the original name of this property.'''

        value = conversion.pn_to_mp_list_float_2d(self.wrapped.FullStiffnessMatrix)
        return value

    @full_stiffness_matrix.setter
    def full_stiffness_matrix(self, value: 'List[List[float]]'):
        value = value if value else None
        value = conversion.mp_to_pn_list_float_2d(value)
        self.wrapped.FullStiffnessMatrix = value
