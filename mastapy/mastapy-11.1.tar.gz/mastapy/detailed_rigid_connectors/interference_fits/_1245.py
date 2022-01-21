'''_1245.py

InterferenceFitDesign
'''


from mastapy._internal.implicit import overridable, enum_with_selected_value
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.detailed_rigid_connectors.interference_fits import _1244, _1243, _1248
from mastapy.detailed_rigid_connectors import _1187
from mastapy._internal.python_net import python_net_import

_INTERFERENCE_FIT_DESIGN = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.InterferenceFits', 'InterferenceFitDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('InterferenceFitDesign',)


class InterferenceFitDesign(_1187.DetailedRigidConnectorDesign):
    '''InterferenceFitDesign

    This is a mastapy class.
    '''

    TYPE = _INTERFERENCE_FIT_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterferenceFitDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def diameter_of_joint(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DiameterOfJoint' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DiameterOfJoint) if self.wrapped.DiameterOfJoint is not None else None

    @diameter_of_joint.setter
    def diameter_of_joint(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DiameterOfJoint = value

    @property
    def specified_joint_pressure(self) -> 'float':
        '''float: 'SpecifiedJointPressure' is the original name of this property.'''

        return self.wrapped.SpecifiedJointPressure

    @specified_joint_pressure.setter
    def specified_joint_pressure(self, value: 'float'):
        self.wrapped.SpecifiedJointPressure = float(value) if value else 0.0

    @property
    def average_joint_pressure(self) -> 'float':
        '''float: 'AverageJointPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageJointPressure

    @property
    def maximum_joint_pressure(self) -> 'float':
        '''float: 'MaximumJointPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumJointPressure

    @property
    def minimum_joint_pressure(self) -> 'float':
        '''float: 'MinimumJointPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumJointPressure

    @property
    def average_relative_interference(self) -> 'float':
        '''float: 'AverageRelativeInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageRelativeInterference

    @property
    def maximum_relative_interference(self) -> 'float':
        '''float: 'MaximumRelativeInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumRelativeInterference

    @property
    def minimum_relative_interference(self) -> 'float':
        '''float: 'MinimumRelativeInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumRelativeInterference

    @property
    def calculation_method(self) -> '_1244.CalculationMethods':
        '''CalculationMethods: 'CalculationMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.CalculationMethod)
        return constructor.new(_1244.CalculationMethods)(value) if value is not None else None

    @calculation_method.setter
    def calculation_method(self, value: '_1244.CalculationMethods'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.CalculationMethod = value

    @property
    def dimensionless_plasticity_diameter(self) -> 'float':
        '''float: 'DimensionlessPlasticityDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DimensionlessPlasticityDiameter

    @property
    def room_temperature_during_assembly(self) -> 'float':
        '''float: 'RoomTemperatureDuringAssembly' is the original name of this property.'''

        return self.wrapped.RoomTemperatureDuringAssembly

    @room_temperature_during_assembly.setter
    def room_temperature_during_assembly(self, value: 'float'):
        self.wrapped.RoomTemperatureDuringAssembly = float(value) if value else 0.0

    @property
    def temperature_of_inner_part_during_assembly(self) -> 'float':
        '''float: 'TemperatureOfInnerPartDuringAssembly' is the original name of this property.'''

        return self.wrapped.TemperatureOfInnerPartDuringAssembly

    @temperature_of_inner_part_during_assembly.setter
    def temperature_of_inner_part_during_assembly(self, value: 'float'):
        self.wrapped.TemperatureOfInnerPartDuringAssembly = float(value) if value else 0.0

    @property
    def assembly_method(self) -> '_1243.AssemblyMethods':
        '''AssemblyMethods: 'AssemblyMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.AssemblyMethod)
        return constructor.new(_1243.AssemblyMethods)(value) if value is not None else None

    @assembly_method.setter
    def assembly_method(self, value: '_1243.AssemblyMethods'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.AssemblyMethod = value

    @property
    def average_allowable_torque(self) -> 'float':
        '''float: 'AverageAllowableTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageAllowableTorque

    @property
    def maximum_allowable_torque(self) -> 'float':
        '''float: 'MaximumAllowableTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumAllowableTorque

    @property
    def minimum_allowable_torque(self) -> 'float':
        '''float: 'MinimumAllowableTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumAllowableTorque

    @property
    def average_permissible_torque(self) -> 'float':
        '''float: 'AveragePermissibleTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AveragePermissibleTorque

    @property
    def maximum_permissible_torque(self) -> 'float':
        '''float: 'MaximumPermissibleTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPermissibleTorque

    @property
    def minimum_permissible_torque(self) -> 'float':
        '''float: 'MinimumPermissibleTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumPermissibleTorque

    @property
    def average_allowable_axial_force(self) -> 'float':
        '''float: 'AverageAllowableAxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageAllowableAxialForce

    @property
    def maximum_allowable_axial_force(self) -> 'float':
        '''float: 'MaximumAllowableAxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumAllowableAxialForce

    @property
    def minimum_allowable_axial_force(self) -> 'float':
        '''float: 'MinimumAllowableAxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumAllowableAxialForce

    @property
    def average_permissible_axial_force(self) -> 'float':
        '''float: 'AveragePermissibleAxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AveragePermissibleAxialForce

    @property
    def maximum_permissible_axial_force(self) -> 'float':
        '''float: 'MaximumPermissibleAxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPermissibleAxialForce

    @property
    def minimum_permissible_axial_force(self) -> 'float':
        '''float: 'MinimumPermissibleAxialForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumPermissibleAxialForce

    @property
    def average_interference(self) -> 'float':
        '''float: 'AverageInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageInterference

    @property
    def maximum_interference(self) -> 'float':
        '''float: 'MaximumInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumInterference

    @property
    def minimum_interference(self) -> 'float':
        '''float: 'MinimumInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumInterference

    @property
    def average_effective_interference(self) -> 'float':
        '''float: 'AverageEffectiveInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageEffectiveInterference

    @property
    def maximum_effective_interference(self) -> 'float':
        '''float: 'MaximumEffectiveInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumEffectiveInterference

    @property
    def minimum_effective_interference(self) -> 'float':
        '''float: 'MinimumEffectiveInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumEffectiveInterference

    @property
    def auxiliary_elasticity_parameter(self) -> 'float':
        '''float: 'AuxiliaryElasticityParameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryElasticityParameter

    @property
    def proportion_of_outer_plastically_stressed(self) -> 'float':
        '''float: 'ProportionOfOuterPlasticallyStressed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProportionOfOuterPlasticallyStressed

    @property
    def permissible_dimensionless_plasticity_diameter(self) -> 'float':
        '''float: 'PermissibleDimensionlessPlasticityDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleDimensionlessPlasticityDiameter

    @property
    def ratio_of_joint_length_to_joint_diameter(self) -> 'float':
        '''float: 'RatioOfJointLengthToJointDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatioOfJointLengthToJointDiameter

    @property
    def joint_interface_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_Table4JointInterfaceTypes':
        '''enum_with_selected_value.EnumWithSelectedValue_Table4JointInterfaceTypes: 'JointInterfaceType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_Table4JointInterfaceTypes.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.JointInterfaceType, value) if self.wrapped.JointInterfaceType is not None else None

    @joint_interface_type.setter
    def joint_interface_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_Table4JointInterfaceTypes.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_Table4JointInterfaceTypes.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.JointInterfaceType = value

    @property
    def coefficient_of_friction_circumferential(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CoefficientOfFrictionCircumferential' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CoefficientOfFrictionCircumferential) if self.wrapped.CoefficientOfFrictionCircumferential is not None else None

    @coefficient_of_friction_circumferential.setter
    def coefficient_of_friction_circumferential(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CoefficientOfFrictionCircumferential = value

    @property
    def coefficient_of_friction_longitudinal(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CoefficientOfFrictionLongitudinal' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CoefficientOfFrictionLongitudinal) if self.wrapped.CoefficientOfFrictionLongitudinal is not None else None

    @coefficient_of_friction_longitudinal.setter
    def coefficient_of_friction_longitudinal(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CoefficientOfFrictionLongitudinal = value

    @property
    def coefficient_of_friction_assembly(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'CoefficientOfFrictionAssembly' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.CoefficientOfFrictionAssembly) if self.wrapped.CoefficientOfFrictionAssembly is not None else None

    @coefficient_of_friction_assembly.setter
    def coefficient_of_friction_assembly(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.CoefficientOfFrictionAssembly = value

    @property
    def insertion_force(self) -> 'float':
        '''float: 'InsertionForce' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InsertionForce

    @property
    def joining_play(self) -> 'float':
        '''float: 'JoiningPlay' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.JoiningPlay

    @property
    def assembly_interference(self) -> 'float':
        '''float: 'AssemblyInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AssemblyInterference

    @property
    def required_assembly_temperature_of_the_outer_part(self) -> 'float':
        '''float: 'RequiredAssemblyTemperatureOfTheOuterPart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RequiredAssemblyTemperatureOfTheOuterPart

    @property
    def maximum_assembly_interference(self) -> 'float':
        '''float: 'MaximumAssemblyInterference' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumAssemblyInterference
