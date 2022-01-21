'''_692.py

CylindricalGearShaper
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.cylindrical import _1028
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.manufacturing.cylindrical.cutters import _696
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SHAPER = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical.Cutters', 'CylindricalGearShaper')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearShaper',)


class CylindricalGearShaper(_696.InvoluteCutterDesign):
    '''CylindricalGearShaper

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SHAPER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearShaper.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def nominal_diameter(self) -> 'float':
        '''float: 'NominalDiameter' is the original name of this property.'''

        return self.wrapped.NominalDiameter

    @nominal_diameter.setter
    def nominal_diameter(self, value: 'float'):
        self.wrapped.NominalDiameter = float(value) if value else 0.0

    @property
    def nominal_addendum(self) -> 'float':
        '''float: 'NominalAddendum' is the original name of this property.'''

        return self.wrapped.NominalAddendum

    @nominal_addendum.setter
    def nominal_addendum(self, value: 'float'):
        self.wrapped.NominalAddendum = float(value) if value else 0.0

    @property
    def nominal_addendum_factor(self) -> 'float':
        '''float: 'NominalAddendumFactor' is the original name of this property.'''

        return self.wrapped.NominalAddendumFactor

    @nominal_addendum_factor.setter
    def nominal_addendum_factor(self, value: 'float'):
        self.wrapped.NominalAddendumFactor = float(value) if value else 0.0

    @property
    def nominal_dedendum(self) -> 'float':
        '''float: 'NominalDedendum' is the original name of this property.'''

        return self.wrapped.NominalDedendum

    @nominal_dedendum.setter
    def nominal_dedendum(self, value: 'float'):
        self.wrapped.NominalDedendum = float(value) if value else 0.0

    @property
    def nominal_dedendum_factor(self) -> 'float':
        '''float: 'NominalDedendumFactor' is the original name of this property.'''

        return self.wrapped.NominalDedendumFactor

    @nominal_dedendum_factor.setter
    def nominal_dedendum_factor(self, value: 'float'):
        self.wrapped.NominalDedendumFactor = float(value) if value else 0.0

    @property
    def use_maximum_edge_radius(self) -> 'bool':
        '''bool: 'UseMaximumEdgeRadius' is the original name of this property.'''

        return self.wrapped.UseMaximumEdgeRadius

    @use_maximum_edge_radius.setter
    def use_maximum_edge_radius(self, value: 'bool'):
        self.wrapped.UseMaximumEdgeRadius = bool(value) if value else False

    @property
    def edge_radius(self) -> 'float':
        '''float: 'EdgeRadius' is the original name of this property.'''

        return self.wrapped.EdgeRadius

    @edge_radius.setter
    def edge_radius(self, value: 'float'):
        self.wrapped.EdgeRadius = float(value) if value else 0.0

    @property
    def has_protuberance(self) -> 'bool':
        '''bool: 'HasProtuberance' is the original name of this property.'''

        return self.wrapped.HasProtuberance

    @has_protuberance.setter
    def has_protuberance(self, value: 'bool'):
        self.wrapped.HasProtuberance = bool(value) if value else False

    @property
    def protuberance(self) -> 'float':
        '''float: 'Protuberance' is the original name of this property.'''

        return self.wrapped.Protuberance

    @protuberance.setter
    def protuberance(self, value: 'float'):
        self.wrapped.Protuberance = float(value) if value else 0.0

    @property
    def protuberance_angle(self) -> 'float':
        '''float: 'ProtuberanceAngle' is the original name of this property.'''

        return self.wrapped.ProtuberanceAngle

    @protuberance_angle.setter
    def protuberance_angle(self, value: 'float'):
        self.wrapped.ProtuberanceAngle = float(value) if value else 0.0

    @property
    def actual_protuberance(self) -> 'float':
        '''float: 'ActualProtuberance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActualProtuberance

    @property
    def has_semi_topping_blade(self) -> 'bool':
        '''bool: 'HasSemiToppingBlade' is the original name of this property.'''

        return self.wrapped.HasSemiToppingBlade

    @has_semi_topping_blade.setter
    def has_semi_topping_blade(self, value: 'bool'):
        self.wrapped.HasSemiToppingBlade = bool(value) if value else False

    @property
    def root_form_diameter(self) -> 'float':
        '''float: 'RootFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFormDiameter

    @property
    def circle_blade_rake_angle(self) -> 'float':
        '''float: 'CircleBladeRakeAngle' is the original name of this property.'''

        return self.wrapped.CircleBladeRakeAngle

    @circle_blade_rake_angle.setter
    def circle_blade_rake_angle(self, value: 'float'):
        self.wrapped.CircleBladeRakeAngle = float(value) if value else 0.0

    @property
    def circle_blade_flank_angle(self) -> 'float':
        '''float: 'CircleBladeFlankAngle' is the original name of this property.'''

        return self.wrapped.CircleBladeFlankAngle

    @circle_blade_flank_angle.setter
    def circle_blade_flank_angle(self, value: 'float'):
        self.wrapped.CircleBladeFlankAngle = float(value) if value else 0.0

    @property
    def shaper_edge_type(self) -> '_1028.ShaperEdgeTypes':
        '''ShaperEdgeTypes: 'ShaperEdgeType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ShaperEdgeType)
        return constructor.new(_1028.ShaperEdgeTypes)(value) if value is not None else None

    @shaper_edge_type.setter
    def shaper_edge_type(self, value: '_1028.ShaperEdgeTypes'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ShaperEdgeType = value

    @property
    def tip_diameter(self) -> 'float':
        '''float: 'TipDiameter' is the original name of this property.'''

        return self.wrapped.TipDiameter

    @tip_diameter.setter
    def tip_diameter(self, value: 'float'):
        self.wrapped.TipDiameter = float(value) if value else 0.0

    @property
    def root_diameter(self) -> 'float':
        '''float: 'RootDiameter' is the original name of this property.'''

        return self.wrapped.RootDiameter

    @root_diameter.setter
    def root_diameter(self, value: 'float'):
        self.wrapped.RootDiameter = float(value) if value else 0.0

    @property
    def semi_topping_angle(self) -> 'float':
        '''float: 'SemiToppingAngle' is the original name of this property.'''

        return self.wrapped.SemiToppingAngle

    @semi_topping_angle.setter
    def semi_topping_angle(self, value: 'float'):
        self.wrapped.SemiToppingAngle = float(value) if value else 0.0

    @property
    def semi_topping_pressure_angle(self) -> 'float':
        '''float: 'SemiToppingPressureAngle' is the original name of this property.'''

        return self.wrapped.SemiToppingPressureAngle

    @semi_topping_pressure_angle.setter
    def semi_topping_pressure_angle(self, value: 'float'):
        self.wrapped.SemiToppingPressureAngle = float(value) if value else 0.0

    @property
    def semi_topping_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SemiToppingDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SemiToppingDiameter) if self.wrapped.SemiToppingDiameter is not None else None

    @semi_topping_diameter.setter
    def semi_topping_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.SemiToppingDiameter = value

    @property
    def diametral_height_at_semi_topping_thickness_measurement(self) -> 'float':
        '''float: 'DiametralHeightAtSemiToppingThicknessMeasurement' is the original name of this property.'''

        return self.wrapped.DiametralHeightAtSemiToppingThicknessMeasurement

    @diametral_height_at_semi_topping_thickness_measurement.setter
    def diametral_height_at_semi_topping_thickness_measurement(self, value: 'float'):
        self.wrapped.DiametralHeightAtSemiToppingThicknessMeasurement = float(value) if value else 0.0

    @property
    def normal_thickness_at_specified_diameter_for_semi_topping(self) -> 'float':
        '''float: 'NormalThicknessAtSpecifiedDiameterForSemiTopping' is the original name of this property.'''

        return self.wrapped.NormalThicknessAtSpecifiedDiameterForSemiTopping

    @normal_thickness_at_specified_diameter_for_semi_topping.setter
    def normal_thickness_at_specified_diameter_for_semi_topping(self, value: 'float'):
        self.wrapped.NormalThicknessAtSpecifiedDiameterForSemiTopping = float(value) if value else 0.0

    @property
    def tip_thickness(self) -> 'float':
        '''float: 'TipThickness' is the original name of this property.'''

        return self.wrapped.TipThickness

    @tip_thickness.setter
    def tip_thickness(self, value: 'float'):
        self.wrapped.TipThickness = float(value) if value else 0.0

    @property
    def tip_control_distance(self) -> 'float':
        '''float: 'TipControlDistance' is the original name of this property.'''

        return self.wrapped.TipControlDistance

    @tip_control_distance.setter
    def tip_control_distance(self, value: 'float'):
        self.wrapped.TipControlDistance = float(value) if value else 0.0

    @property
    def blade_control_distance(self) -> 'float':
        '''float: 'BladeControlDistance' is the original name of this property.'''

        return self.wrapped.BladeControlDistance

    @blade_control_distance.setter
    def blade_control_distance(self, value: 'float'):
        self.wrapped.BladeControlDistance = float(value) if value else 0.0

    @property
    def protuberance_height(self) -> 'float':
        '''float: 'ProtuberanceHeight' is the original name of this property.'''

        return self.wrapped.ProtuberanceHeight

    @protuberance_height.setter
    def protuberance_height(self, value: 'float'):
        self.wrapped.ProtuberanceHeight = float(value) if value else 0.0

    @property
    def edge_height(self) -> 'float':
        '''float: 'EdgeHeight' is the original name of this property.'''

        return self.wrapped.EdgeHeight

    @edge_height.setter
    def edge_height(self, value: 'float'):
        self.wrapped.EdgeHeight = float(value) if value else 0.0

    @property
    def whole_depth(self) -> 'float':
        '''float: 'WholeDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WholeDepth

    @property
    def virtual_tooth_number(self) -> 'float':
        '''float: 'VirtualToothNumber' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualToothNumber

    @property
    def radius_to_centre_s_of_tool_tip_radius(self) -> 'float':
        '''float: 'RadiusToCentreSOfToolTipRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RadiusToCentreSOfToolTipRadius
