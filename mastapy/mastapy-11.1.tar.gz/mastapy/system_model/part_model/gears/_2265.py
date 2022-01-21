'''_2265.py

CylindricalGear
'''


from typing import List, Optional

from mastapy._internal import constructor, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.gear_designs.cylindrical import _969, _996
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.connections_and_sockets.gears import _2051
from mastapy.system_model.part_model.gears import _2270
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'CylindricalGear')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGear',)


class CylindricalGear(_2270.Gear):
    '''CylindricalGear

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def has_concept_synchroniser(self) -> 'bool':
        '''bool: 'HasConceptSynchroniser' is the original name of this property.'''

        return self.wrapped.HasConceptSynchroniser

    @has_concept_synchroniser.setter
    def has_concept_synchroniser(self, value: 'bool'):
        self.wrapped.HasConceptSynchroniser = bool(value) if value else False

    @property
    def estimated_crowning(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'EstimatedCrowning' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.EstimatedCrowning) if self.wrapped.EstimatedCrowning is not None else None

    @estimated_crowning.setter
    def estimated_crowning(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.EstimatedCrowning = value

    @property
    def centre_of_estimated_micro_geometry_range(self) -> 'float':
        '''float: 'CentreOfEstimatedMicroGeometryRange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CentreOfEstimatedMicroGeometryRange

    @property
    def left_limit_of_estimated_micro_geometry_range(self) -> 'float':
        '''float: 'LeftLimitOfEstimatedMicroGeometryRange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LeftLimitOfEstimatedMicroGeometryRange

    @property
    def right_limit_of_estimated_micro_geometry_range(self) -> 'float':
        '''float: 'RightLimitOfEstimatedMicroGeometryRange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RightLimitOfEstimatedMicroGeometryRange

    @property
    def linear_relief(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'LinearRelief' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.LinearRelief) if self.wrapped.LinearRelief is not None else None

    @linear_relief.setter
    def linear_relief(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.LinearRelief = value

    @property
    def extra_backlash(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ExtraBacklash' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ExtraBacklash) if self.wrapped.ExtraBacklash is not None else None

    @extra_backlash.setter
    def extra_backlash(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ExtraBacklash = value

    @property
    def clocking_angle_error(self) -> 'float':
        '''float: 'ClockingAngleError' is the original name of this property.'''

        return self.wrapped.ClockingAngleError

    @clocking_angle_error.setter
    def clocking_angle_error(self, value: 'float'):
        self.wrapped.ClockingAngleError = float(value) if value else 0.0

    @property
    def reference_axis_angle_about_local_z_axis_from_y_axis(self) -> 'float':
        '''float: 'ReferenceAxisAngleAboutLocalZAxisFromYAxis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceAxisAngleAboutLocalZAxisFromYAxis

    @property
    def maximum_tip_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumTipDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumTipDiameter) if self.wrapped.MaximumTipDiameter is not None else None

    @maximum_tip_diameter.setter
    def maximum_tip_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumTipDiameter = value

    @property
    def clearance_to_maximum_tip_diameter(self) -> 'float':
        '''float: 'ClearanceToMaximumTipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ClearanceToMaximumTipDiameter

    @property
    def minimum_root_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MinimumRootDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MinimumRootDiameter) if self.wrapped.MinimumRootDiameter is not None else None

    @minimum_root_diameter.setter
    def minimum_root_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MinimumRootDiameter = value

    @property
    def is_position_fixed_for_centre_distance_modification(self) -> 'bool':
        '''bool: 'IsPositionFixedForCentreDistanceModification' is the original name of this property.'''

        return self.wrapped.IsPositionFixedForCentreDistanceModification

    @is_position_fixed_for_centre_distance_modification.setter
    def is_position_fixed_for_centre_distance_modification(self, value: 'bool'):
        self.wrapped.IsPositionFixedForCentreDistanceModification = bool(value) if value else False

    @property
    def active_gear_design(self) -> '_969.CylindricalGearDesign':
        '''CylindricalGearDesign: 'ActiveGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _969.CylindricalGearDesign.TYPE not in self.wrapped.ActiveGearDesign.__class__.__mro__:
            raise CastException('Failed to cast active_gear_design to CylindricalGearDesign. Expected: {}.'.format(self.wrapped.ActiveGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ActiveGearDesign.__class__)(self.wrapped.ActiveGearDesign) if self.wrapped.ActiveGearDesign is not None else None

    @property
    def cylindrical_gear_design(self) -> '_969.CylindricalGearDesign':
        '''CylindricalGearDesign: 'CylindricalGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _969.CylindricalGearDesign.TYPE not in self.wrapped.CylindricalGearDesign.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear_design to CylindricalGearDesign. Expected: {}.'.format(self.wrapped.CylindricalGearDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGearDesign.__class__)(self.wrapped.CylindricalGearDesign) if self.wrapped.CylindricalGearDesign is not None else None

    @property
    def cylindrical_meshes(self) -> 'List[_2051.CylindricalGearMesh]':
        '''List[CylindricalGearMesh]: 'CylindricalMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshes, constructor.new(_2051.CylindricalGearMesh))
        return value

    def make_carrier_assembly(self, number_of_radial_bearings: 'int', add_left_thrust_bearing: 'bool', add_right_thrust_bearing: 'bool', gear_bore: 'float', carrier_bore: 'float', carrier_width: 'float', gear_offset: Optional['float'] = 0.0, left_bearing_indent: Optional['float'] = 0.0, right_bearing_indent: Optional['float'] = 0.0, thrust_pad_clearance: Optional['float'] = 0.0, adding_bearing: Optional['bool'] = True, left_thurst_pad_contact_diameter: Optional['float'] = None, right_thurst_pad_contact_diameter: Optional['float'] = None):
        ''' 'MakeCarrierAssembly' is the original name of this method.

        Args:
            number_of_radial_bearings (int)
            add_left_thrust_bearing (bool)
            add_right_thrust_bearing (bool)
            gear_bore (float)
            carrier_bore (float)
            carrier_width (float)
            gear_offset (float, optional)
            left_bearing_indent (float, optional)
            right_bearing_indent (float, optional)
            thrust_pad_clearance (float, optional)
            adding_bearing (bool, optional)
            left_thurst_pad_contact_diameter (float, optional)
            right_thurst_pad_contact_diameter (float, optional)
        '''

        number_of_radial_bearings = int(number_of_radial_bearings)
        add_left_thrust_bearing = bool(add_left_thrust_bearing)
        add_right_thrust_bearing = bool(add_right_thrust_bearing)
        gear_bore = float(gear_bore)
        carrier_bore = float(carrier_bore)
        carrier_width = float(carrier_width)
        gear_offset = float(gear_offset)
        left_bearing_indent = float(left_bearing_indent)
        right_bearing_indent = float(right_bearing_indent)
        thrust_pad_clearance = float(thrust_pad_clearance)
        adding_bearing = bool(adding_bearing)
        left_thurst_pad_contact_diameter = float(left_thurst_pad_contact_diameter)
        right_thurst_pad_contact_diameter = float(right_thurst_pad_contact_diameter)
        self.wrapped.MakeCarrierAssembly(number_of_radial_bearings if number_of_radial_bearings else 0, add_left_thrust_bearing if add_left_thrust_bearing else False, add_right_thrust_bearing if add_right_thrust_bearing else False, gear_bore if gear_bore else 0.0, carrier_bore if carrier_bore else 0.0, carrier_width if carrier_width else 0.0, gear_offset if gear_offset else 0.0, left_bearing_indent if left_bearing_indent else 0.0, right_bearing_indent if right_bearing_indent else 0.0, thrust_pad_clearance if thrust_pad_clearance else 0.0, adding_bearing if adding_bearing else False, left_thurst_pad_contact_diameter if left_thurst_pad_contact_diameter else 0.0, right_thurst_pad_contact_diameter if right_thurst_pad_contact_diameter else 0.0)
