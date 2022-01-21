'''_1912.py

RollingBearing
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import enum_with_selected_value, overridable
from mastapy.bearings import (
    _1649, _1652, _1628, _1629,
    _1630, _1631
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.bearings.bearing_designs.rolling import (
    _1922, _1905, _1899, _1895,
    _1915, _1892, _1902, _1914
)
from mastapy._internal.python_net import python_net_import
from mastapy.utility import _1379
from mastapy.materials import _217
from mastapy.bearings.bearing_designs import _1880

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_ROLLING_BEARING = python_net_import('SMT.MastaAPI.Bearings.BearingDesigns.Rolling', 'RollingBearing')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingBearing',)


class RollingBearing(_1880.DetailedBearing):
    '''RollingBearing

    This is a mastapy class.
    '''

    TYPE = _ROLLING_BEARING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingBearing.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def no_history(self) -> 'str':
        '''str: 'NoHistory' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NoHistory

    @property
    def arrangement(self) -> 'enum_with_selected_value.EnumWithSelectedValue_RollingBearingArrangement':
        '''enum_with_selected_value.EnumWithSelectedValue_RollingBearingArrangement: 'Arrangement' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_RollingBearingArrangement.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.Arrangement, value) if self.wrapped.Arrangement is not None else None

    @arrangement.setter
    def arrangement(self, value: 'enum_with_selected_value.EnumWithSelectedValue_RollingBearingArrangement.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_RollingBearingArrangement.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.Arrangement = value

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

    @property
    def inner_ring_width(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRingWidth' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRingWidth) if self.wrapped.InnerRingWidth is not None else None

    @inner_ring_width.setter
    def inner_ring_width(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRingWidth = value

    @property
    def outer_ring_width(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterRingWidth' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterRingWidth) if self.wrapped.OuterRingWidth is not None else None

    @outer_ring_width.setter
    def outer_ring_width(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterRingWidth = value

    @property
    def outer_ring_offset(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterRingOffset' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterRingOffset) if self.wrapped.OuterRingOffset is not None else None

    @outer_ring_offset.setter
    def outer_ring_offset(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterRingOffset = value

    @property
    def inner_race_outer_diameter(self) -> 'float':
        '''float: 'InnerRaceOuterDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InnerRaceOuterDiameter

    @property
    def outer_race_inner_diameter(self) -> 'float':
        '''float: 'OuterRaceInnerDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterRaceInnerDiameter

    @property
    def inner_race_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType':
        '''enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType: 'InnerRaceType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.InnerRaceType, value) if self.wrapped.InnerRaceType is not None else None

    @inner_race_type.setter
    def inner_race_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.InnerRaceType = value

    @property
    def outer_race_type(self) -> 'enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType':
        '''enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType: 'OuterRaceType' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.OuterRaceType, value) if self.wrapped.OuterRaceType is not None else None

    @outer_race_type.setter
    def outer_race_type(self, value: 'enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_RollingBearingRaceType.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.OuterRaceType = value

    @property
    def catalogue(self) -> '_1628.BearingCatalog':
        '''BearingCatalog: 'Catalogue' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.Catalogue)
        return constructor.new(_1628.BearingCatalog)(value) if value is not None else None

    @property
    def designation(self) -> 'str':
        '''str: 'Designation' is the original name of this property.'''

        return self.wrapped.Designation

    @designation.setter
    def designation(self, value: 'str'):
        self.wrapped.Designation = str(value) if value else ''

    @property
    def manufacturer(self) -> 'str':
        '''str: 'Manufacturer' is the original name of this property.'''

        return self.wrapped.Manufacturer

    @manufacturer.setter
    def manufacturer(self, value: 'str'):
        self.wrapped.Manufacturer = str(value) if value else ''

    @property
    def width_series(self) -> 'overridable.Overridable_WidthSeries':
        '''overridable.Overridable_WidthSeries: 'WidthSeries' is the original name of this property.'''

        value = overridable.Overridable_WidthSeries.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.WidthSeries, value) if self.wrapped.WidthSeries is not None else None

    @width_series.setter
    def width_series(self, value: 'overridable.Overridable_WidthSeries.implicit_type()'):
        wrapper_type = overridable.Overridable_WidthSeries.wrapper_type()
        enclosed_type = overridable.Overridable_WidthSeries.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.WidthSeries = value

    @property
    def height_series(self) -> 'overridable.Overridable_HeightSeries':
        '''overridable.Overridable_HeightSeries: 'HeightSeries' is the original name of this property.'''

        value = overridable.Overridable_HeightSeries.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.HeightSeries, value) if self.wrapped.HeightSeries is not None else None

    @height_series.setter
    def height_series(self, value: 'overridable.Overridable_HeightSeries.implicit_type()'):
        wrapper_type = overridable.Overridable_HeightSeries.wrapper_type()
        enclosed_type = overridable.Overridable_HeightSeries.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.HeightSeries = value

    @property
    def diameter_series(self) -> 'overridable.Overridable_DiameterSeries':
        '''overridable.Overridable_DiameterSeries: 'DiameterSeries' is the original name of this property.'''

        value = overridable.Overridable_DiameterSeries.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.DiameterSeries, value) if self.wrapped.DiameterSeries is not None else None

    @diameter_series.setter
    def diameter_series(self, value: 'overridable.Overridable_DiameterSeries.implicit_type()'):
        wrapper_type = overridable.Overridable_DiameterSeries.wrapper_type()
        enclosed_type = overridable.Overridable_DiameterSeries.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value if value is not None else None, is_overridden)
        self.wrapped.DiameterSeries = value

    @property
    def fatigue_load_limit(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'FatigueLoadLimit' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.FatigueLoadLimit) if self.wrapped.FatigueLoadLimit is not None else None

    @fatigue_load_limit.setter
    def fatigue_load_limit(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.FatigueLoadLimit = value

    @property
    def is_full_complement(self) -> 'overridable.Overridable_bool':
        '''overridable.Overridable_bool: 'IsFullComplement' is the original name of this property.'''

        return constructor.new(overridable.Overridable_bool)(self.wrapped.IsFullComplement) if self.wrapped.IsFullComplement is not None else None

    @is_full_complement.setter
    def is_full_complement(self, value: 'overridable.Overridable_bool.implicit_type()'):
        wrapper_type = overridable.Overridable_bool.wrapper_type()
        enclosed_type = overridable.Overridable_bool.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else False, is_overridden)
        self.wrapped.IsFullComplement = value

    @property
    def type_(self) -> 'str':
        '''str: 'Type' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Type

    @property
    def number_of_rows(self) -> 'int':
        '''int: 'NumberOfRows' is the original name of this property.'''

        return self.wrapped.NumberOfRows

    @number_of_rows.setter
    def number_of_rows(self, value: 'int'):
        self.wrapped.NumberOfRows = int(value) if value else 0

    @property
    def maximum_oil_speed(self) -> 'float':
        '''float: 'MaximumOilSpeed' is the original name of this property.'''

        return self.wrapped.MaximumOilSpeed

    @maximum_oil_speed.setter
    def maximum_oil_speed(self, value: 'float'):
        self.wrapped.MaximumOilSpeed = float(value) if value else 0.0

    @property
    def maximum_grease_speed(self) -> 'float':
        '''float: 'MaximumGreaseSpeed' is the original name of this property.'''

        return self.wrapped.MaximumGreaseSpeed

    @maximum_grease_speed.setter
    def maximum_grease_speed(self, value: 'float'):
        self.wrapped.MaximumGreaseSpeed = float(value) if value else 0.0

    @property
    def element_material_reportable(self) -> 'str':
        '''str: 'ElementMaterialReportable' is the original name of this property.'''

        return self.wrapped.ElementMaterialReportable.SelectedItemName

    @element_material_reportable.setter
    def element_material_reportable(self, value: 'str'):
        self.wrapped.ElementMaterialReportable.SetSelectedItem(str(value) if value else '')

    @property
    def inner_race_material_reportable(self) -> 'str':
        '''str: 'InnerRaceMaterialReportable' is the original name of this property.'''

        return self.wrapped.InnerRaceMaterialReportable.SelectedItemName

    @inner_race_material_reportable.setter
    def inner_race_material_reportable(self, value: 'str'):
        self.wrapped.InnerRaceMaterialReportable.SetSelectedItem(str(value) if value else '')

    @property
    def outer_race_material_reportable(self) -> 'str':
        '''str: 'OuterRaceMaterialReportable' is the original name of this property.'''

        return self.wrapped.OuterRaceMaterialReportable.SelectedItemName

    @outer_race_material_reportable.setter
    def outer_race_material_reportable(self, value: 'str'):
        self.wrapped.OuterRaceMaterialReportable.SetSelectedItem(str(value) if value else '')

    @property
    def inner_race_hardness_depth(self) -> 'float':
        '''float: 'InnerRaceHardnessDepth' is the original name of this property.'''

        return self.wrapped.InnerRaceHardnessDepth

    @inner_race_hardness_depth.setter
    def inner_race_hardness_depth(self, value: 'float'):
        self.wrapped.InnerRaceHardnessDepth = float(value) if value else 0.0

    @property
    def outer_race_hardness_depth(self) -> 'float':
        '''float: 'OuterRaceHardnessDepth' is the original name of this property.'''

        return self.wrapped.OuterRaceHardnessDepth

    @outer_race_hardness_depth.setter
    def outer_race_hardness_depth(self, value: 'float'):
        self.wrapped.OuterRaceHardnessDepth = float(value) if value else 0.0

    @property
    def element_surface_roughness_ra(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ElementSurfaceRoughnessRa' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ElementSurfaceRoughnessRa) if self.wrapped.ElementSurfaceRoughnessRa is not None else None

    @element_surface_roughness_ra.setter
    def element_surface_roughness_ra(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ElementSurfaceRoughnessRa = value

    @property
    def element_surface_roughness_rms(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ElementSurfaceRoughnessRMS' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ElementSurfaceRoughnessRMS) if self.wrapped.ElementSurfaceRoughnessRMS is not None else None

    @element_surface_roughness_rms.setter
    def element_surface_roughness_rms(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ElementSurfaceRoughnessRMS = value

    @property
    def minimum_surface_roughness_ra(self) -> 'float':
        '''float: 'MinimumSurfaceRoughnessRa' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumSurfaceRoughnessRa

    @property
    def minimum_surface_roughness_rms(self) -> 'float':
        '''float: 'MinimumSurfaceRoughnessRMS' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumSurfaceRoughnessRMS

    @property
    def raceway_surface_roughness_ra_inner(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RacewaySurfaceRoughnessRaInner' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RacewaySurfaceRoughnessRaInner) if self.wrapped.RacewaySurfaceRoughnessRaInner is not None else None

    @raceway_surface_roughness_ra_inner.setter
    def raceway_surface_roughness_ra_inner(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RacewaySurfaceRoughnessRaInner = value

    @property
    def raceway_surface_roughness_ra_outer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RacewaySurfaceRoughnessRaOuter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RacewaySurfaceRoughnessRaOuter) if self.wrapped.RacewaySurfaceRoughnessRaOuter is not None else None

    @raceway_surface_roughness_ra_outer.setter
    def raceway_surface_roughness_ra_outer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RacewaySurfaceRoughnessRaOuter = value

    @property
    def raceway_surface_roughness_rms_inner(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RacewaySurfaceRoughnessRMSInner' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RacewaySurfaceRoughnessRMSInner) if self.wrapped.RacewaySurfaceRoughnessRMSInner is not None else None

    @raceway_surface_roughness_rms_inner.setter
    def raceway_surface_roughness_rms_inner(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RacewaySurfaceRoughnessRMSInner = value

    @property
    def raceway_surface_roughness_rms_outer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RacewaySurfaceRoughnessRMSOuter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RacewaySurfaceRoughnessRMSOuter) if self.wrapped.RacewaySurfaceRoughnessRMSOuter is not None else None

    @raceway_surface_roughness_rms_outer.setter
    def raceway_surface_roughness_rms_outer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RacewaySurfaceRoughnessRMSOuter = value

    @property
    def combined_surface_roughness_outer(self) -> 'float':
        '''float: 'CombinedSurfaceRoughnessOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CombinedSurfaceRoughnessOuter

    @property
    def combined_surface_roughness_inner(self) -> 'float':
        '''float: 'CombinedSurfaceRoughnessInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CombinedSurfaceRoughnessInner

    @property
    def number_of_elements(self) -> 'overridable.Overridable_int':
        '''overridable.Overridable_int: 'NumberOfElements' is the original name of this property.'''

        return constructor.new(overridable.Overridable_int)(self.wrapped.NumberOfElements) if self.wrapped.NumberOfElements is not None else None

    @number_of_elements.setter
    def number_of_elements(self, value: 'overridable.Overridable_int.implicit_type()'):
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0, is_overridden)
        self.wrapped.NumberOfElements = value

    @property
    def theoretical_maximum_number_of_elements(self) -> 'float':
        '''float: 'TheoreticalMaximumNumberOfElements' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TheoreticalMaximumNumberOfElements

    @property
    def total_free_space_between_elements(self) -> 'float':
        '''float: 'TotalFreeSpaceBetweenElements' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalFreeSpaceBetweenElements

    @property
    def free_space_between_elements(self) -> 'float':
        '''float: 'FreeSpaceBetweenElements' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FreeSpaceBetweenElements

    @property
    def element_offset(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ElementOffset' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ElementOffset) if self.wrapped.ElementOffset is not None else None

    @element_offset.setter
    def element_offset(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ElementOffset = value

    @property
    def distance_between_element_centres(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DistanceBetweenElementCentres' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DistanceBetweenElementCentres) if self.wrapped.DistanceBetweenElementCentres is not None else None

    @distance_between_element_centres.setter
    def distance_between_element_centres(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DistanceBetweenElementCentres = value

    @property
    def pitch_circle_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PitchCircleDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PitchCircleDiameter) if self.wrapped.PitchCircleDiameter is not None else None

    @pitch_circle_diameter.setter
    def pitch_circle_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PitchCircleDiameter = value

    @property
    def element_radius(self) -> 'float':
        '''float: 'ElementRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ElementRadius

    @property
    def element_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ElementDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ElementDiameter) if self.wrapped.ElementDiameter is not None else None

    @element_diameter.setter
    def element_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ElementDiameter = value

    @property
    def contact_angle(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ContactAngle' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ContactAngle) if self.wrapped.ContactAngle is not None else None

    @contact_angle.setter
    def contact_angle(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ContactAngle = value

    @property
    def limiting_value_for_axial_load_ratio(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'LimitingValueForAxialLoadRatio' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.LimitingValueForAxialLoadRatio) if self.wrapped.LimitingValueForAxialLoadRatio is not None else None

    @limiting_value_for_axial_load_ratio.setter
    def limiting_value_for_axial_load_ratio(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.LimitingValueForAxialLoadRatio = value

    @property
    def dynamic_equivalent_load_factors_can_be_specified(self) -> 'bool':
        '''bool: 'DynamicEquivalentLoadFactorsCanBeSpecified' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicEquivalentLoadFactorsCanBeSpecified

    @property
    def dynamic_radial_load_factor_for_low_axial_radial_load_ratios(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicRadialLoadFactorForLowAxialRadialLoadRatios' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicRadialLoadFactorForLowAxialRadialLoadRatios) if self.wrapped.DynamicRadialLoadFactorForLowAxialRadialLoadRatios is not None else None

    @dynamic_radial_load_factor_for_low_axial_radial_load_ratios.setter
    def dynamic_radial_load_factor_for_low_axial_radial_load_ratios(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DynamicRadialLoadFactorForLowAxialRadialLoadRatios = value

    @property
    def dynamic_axial_load_factor_for_low_axial_radial_load_ratios(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicAxialLoadFactorForLowAxialRadialLoadRatios' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicAxialLoadFactorForLowAxialRadialLoadRatios) if self.wrapped.DynamicAxialLoadFactorForLowAxialRadialLoadRatios is not None else None

    @dynamic_axial_load_factor_for_low_axial_radial_load_ratios.setter
    def dynamic_axial_load_factor_for_low_axial_radial_load_ratios(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DynamicAxialLoadFactorForLowAxialRadialLoadRatios = value

    @property
    def dynamic_radial_load_factor_for_high_axial_radial_load_ratios(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicRadialLoadFactorForHighAxialRadialLoadRatios' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicRadialLoadFactorForHighAxialRadialLoadRatios) if self.wrapped.DynamicRadialLoadFactorForHighAxialRadialLoadRatios is not None else None

    @dynamic_radial_load_factor_for_high_axial_radial_load_ratios.setter
    def dynamic_radial_load_factor_for_high_axial_radial_load_ratios(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DynamicRadialLoadFactorForHighAxialRadialLoadRatios = value

    @property
    def dynamic_axial_load_factor_for_high_axial_radial_load_ratios(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'DynamicAxialLoadFactorForHighAxialRadialLoadRatios' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.DynamicAxialLoadFactorForHighAxialRadialLoadRatios) if self.wrapped.DynamicAxialLoadFactorForHighAxialRadialLoadRatios is not None else None

    @dynamic_axial_load_factor_for_high_axial_radial_load_ratios.setter
    def dynamic_axial_load_factor_for_high_axial_radial_load_ratios(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.DynamicAxialLoadFactorForHighAxialRadialLoadRatios = value

    @property
    def factor_for_basic_dynamic_load_rating_in_ansiabma(self) -> 'float':
        '''float: 'FactorForBasicDynamicLoadRatingInANSIABMA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FactorForBasicDynamicLoadRatingInANSIABMA

    @property
    def iso_material_factor(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ISOMaterialFactor' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ISOMaterialFactor) if self.wrapped.ISOMaterialFactor is not None else None

    @iso_material_factor.setter
    def iso_material_factor(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ISOMaterialFactor = value

    @property
    def basic_dynamic_load_rating(self) -> 'float':
        '''float: 'BasicDynamicLoadRating' is the original name of this property.'''

        return self.wrapped.BasicDynamicLoadRating

    @basic_dynamic_load_rating.setter
    def basic_dynamic_load_rating(self, value: 'float'):
        self.wrapped.BasicDynamicLoadRating = float(value) if value else 0.0

    @property
    def basic_dynamic_load_rating_divided_by_correction_factors(self) -> 'float':
        '''float: 'BasicDynamicLoadRatingDividedByCorrectionFactors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicDynamicLoadRatingDividedByCorrectionFactors

    @property
    def basic_static_load_rating(self) -> 'float':
        '''float: 'BasicStaticLoadRating' is the original name of this property.'''

        return self.wrapped.BasicStaticLoadRating

    @basic_static_load_rating.setter
    def basic_static_load_rating(self, value: 'float'):
        self.wrapped.BasicStaticLoadRating = float(value) if value else 0.0

    @property
    def basic_static_load_rating_factor(self) -> 'float':
        '''float: 'BasicStaticLoadRatingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicStaticLoadRatingFactor

    @property
    def basic_static_load_rating_source(self) -> 'str':
        '''str: 'BasicStaticLoadRatingSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicStaticLoadRatingSource

    @property
    def basic_dynamic_load_rating_source(self) -> 'str':
        '''str: 'BasicDynamicLoadRatingSource' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicDynamicLoadRatingSource

    @property
    def basic_dynamic_load_rating_calculation(self) -> 'enum_with_selected_value.EnumWithSelectedValue_BasicDynamicLoadRatingCalculationMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_BasicDynamicLoadRatingCalculationMethod: 'BasicDynamicLoadRatingCalculation' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_BasicDynamicLoadRatingCalculationMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.BasicDynamicLoadRatingCalculation, value) if self.wrapped.BasicDynamicLoadRatingCalculation is not None else None

    @basic_dynamic_load_rating_calculation.setter
    def basic_dynamic_load_rating_calculation(self, value: 'enum_with_selected_value.EnumWithSelectedValue_BasicDynamicLoadRatingCalculationMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_BasicDynamicLoadRatingCalculationMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.BasicDynamicLoadRatingCalculation = value

    @property
    def basic_static_load_rating_calculation(self) -> 'enum_with_selected_value.EnumWithSelectedValue_BasicStaticLoadRatingCalculationMethod':
        '''enum_with_selected_value.EnumWithSelectedValue_BasicStaticLoadRatingCalculationMethod: 'BasicStaticLoadRatingCalculation' is the original name of this property.'''

        value = enum_with_selected_value.EnumWithSelectedValue_BasicStaticLoadRatingCalculationMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(self.wrapped.BasicStaticLoadRatingCalculation, value) if self.wrapped.BasicStaticLoadRatingCalculation is not None else None

    @basic_static_load_rating_calculation.setter
    def basic_static_load_rating_calculation(self, value: 'enum_with_selected_value.EnumWithSelectedValue_BasicStaticLoadRatingCalculationMethod.implicit_type()'):
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_BasicStaticLoadRatingCalculationMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value)
        value = wrapper_type[enclosed_type](value)
        self.wrapped.BasicStaticLoadRatingCalculation = value

    @property
    def inner_ring_left_corner_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRingLeftCornerRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRingLeftCornerRadius) if self.wrapped.InnerRingLeftCornerRadius is not None else None

    @inner_ring_left_corner_radius.setter
    def inner_ring_left_corner_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRingLeftCornerRadius = value

    @property
    def inner_ring_right_corner_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'InnerRingRightCornerRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.InnerRingRightCornerRadius) if self.wrapped.InnerRingRightCornerRadius is not None else None

    @inner_ring_right_corner_radius.setter
    def inner_ring_right_corner_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.InnerRingRightCornerRadius = value

    @property
    def outer_ring_left_corner_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterRingLeftCornerRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterRingLeftCornerRadius) if self.wrapped.OuterRingLeftCornerRadius is not None else None

    @outer_ring_left_corner_radius.setter
    def outer_ring_left_corner_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterRingLeftCornerRadius = value

    @property
    def outer_ring_right_corner_radius(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'OuterRingRightCornerRadius' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.OuterRingRightCornerRadius) if self.wrapped.OuterRingRightCornerRadius is not None else None

    @outer_ring_right_corner_radius.setter
    def outer_ring_right_corner_radius(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.OuterRingRightCornerRadius = value

    @property
    def are_the_outer_rings_a_single_piece_of_metal(self) -> 'overridable.Overridable_bool':
        '''overridable.Overridable_bool: 'AreTheOuterRingsASinglePieceOfMetal' is the original name of this property.'''

        return constructor.new(overridable.Overridable_bool)(self.wrapped.AreTheOuterRingsASinglePieceOfMetal) if self.wrapped.AreTheOuterRingsASinglePieceOfMetal is not None else None

    @are_the_outer_rings_a_single_piece_of_metal.setter
    def are_the_outer_rings_a_single_piece_of_metal(self, value: 'overridable.Overridable_bool.implicit_type()'):
        wrapper_type = overridable.Overridable_bool.wrapper_type()
        enclosed_type = overridable.Overridable_bool.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else False, is_overridden)
        self.wrapped.AreTheOuterRingsASinglePieceOfMetal = value

    @property
    def are_the_inner_rings_a_single_piece_of_metal(self) -> 'overridable.Overridable_bool':
        '''overridable.Overridable_bool: 'AreTheInnerRingsASinglePieceOfMetal' is the original name of this property.'''

        return constructor.new(overridable.Overridable_bool)(self.wrapped.AreTheInnerRingsASinglePieceOfMetal) if self.wrapped.AreTheInnerRingsASinglePieceOfMetal is not None else None

    @are_the_inner_rings_a_single_piece_of_metal.setter
    def are_the_inner_rings_a_single_piece_of_metal(self, value: 'overridable.Overridable_bool.implicit_type()'):
        wrapper_type = overridable.Overridable_bool.wrapper_type()
        enclosed_type = overridable.Overridable_bool.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else False, is_overridden)
        self.wrapped.AreTheInnerRingsASinglePieceOfMetal = value

    @property
    def extra_information(self) -> 'str':
        '''str: 'ExtraInformation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ExtraInformation

    @property
    def type_information(self) -> '_1895.BearingTypeExtraInformation':
        '''BearingTypeExtraInformation: 'TypeInformation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.TypeInformation)
        return constructor.new(_1895.BearingTypeExtraInformation)(value) if value is not None else None

    @property
    def is_skf_popular_item(self) -> 'bool':
        '''bool: 'IsSKFPopularItem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsSKFPopularItem

    @property
    def contact_radius_in_rolling_direction_inner(self) -> 'float':
        '''float: 'ContactRadiusInRollingDirectionInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRadiusInRollingDirectionInner

    @property
    def contact_radius_in_rolling_direction_outer(self) -> 'float':
        '''float: 'ContactRadiusInRollingDirectionOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRadiusInRollingDirectionOuter

    @property
    def cage_material(self) -> '_1631.BearingCageMaterial':
        '''BearingCageMaterial: 'CageMaterial' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.CageMaterial)
        return constructor.new(_1631.BearingCageMaterial)(value) if value is not None else None

    @cage_material.setter
    def cage_material(self, value: '_1631.BearingCageMaterial'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.CageMaterial = value

    @property
    def sleeve_type(self) -> '_1915.SleeveType':
        '''SleeveType: 'SleeveType' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.SleeveType)
        return constructor.new(_1915.SleeveType)(value) if value is not None else None

    @property
    def maximum_permissible_contact_stress_for_static_failure_inner(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumPermissibleContactStressForStaticFailureInner' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumPermissibleContactStressForStaticFailureInner) if self.wrapped.MaximumPermissibleContactStressForStaticFailureInner is not None else None

    @maximum_permissible_contact_stress_for_static_failure_inner.setter
    def maximum_permissible_contact_stress_for_static_failure_inner(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumPermissibleContactStressForStaticFailureInner = value

    @property
    def maximum_permissible_contact_stress_for_static_failure_outer(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'MaximumPermissibleContactStressForStaticFailureOuter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.MaximumPermissibleContactStressForStaticFailureOuter) if self.wrapped.MaximumPermissibleContactStressForStaticFailureOuter is not None else None

    @maximum_permissible_contact_stress_for_static_failure_outer.setter
    def maximum_permissible_contact_stress_for_static_failure_outer(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.MaximumPermissibleContactStressForStaticFailureOuter = value

    @property
    def power_for_maximum_contact_stress_safety_factor(self) -> 'float':
        '''float: 'PowerForMaximumContactStressSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PowerForMaximumContactStressSafetyFactor

    @property
    def kz(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'KZ' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.KZ) if self.wrapped.KZ is not None else None

    @kz.setter
    def kz(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.KZ = value

    @property
    def history(self) -> '_1379.FileHistory':
        '''FileHistory: 'History' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1379.FileHistory)(self.wrapped.History) if self.wrapped.History is not None else None

    @property
    def protection(self) -> '_1892.BearingProtection':
        '''BearingProtection: 'Protection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1892.BearingProtection)(self.wrapped.Protection) if self.wrapped.Protection is not None else None

    @property
    def element_material(self) -> '_217.BearingMaterial':
        '''BearingMaterial: 'ElementMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_217.BearingMaterial)(self.wrapped.ElementMaterial) if self.wrapped.ElementMaterial is not None else None

    @property
    def inner_ring_material(self) -> '_217.BearingMaterial':
        '''BearingMaterial: 'InnerRingMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_217.BearingMaterial)(self.wrapped.InnerRingMaterial) if self.wrapped.InnerRingMaterial is not None else None

    @property
    def outer_ring_material(self) -> '_217.BearingMaterial':
        '''BearingMaterial: 'OuterRingMaterial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_217.BearingMaterial)(self.wrapped.OuterRingMaterial) if self.wrapped.OuterRingMaterial is not None else None

    @property
    def geometric_constants(self) -> '_1902.GeometricConstants':
        '''GeometricConstants: 'GeometricConstants' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1902.GeometricConstants)(self.wrapped.GeometricConstants) if self.wrapped.GeometricConstants is not None else None

    @property
    def skf_seal_frictional_moment_constants(self) -> '_1914.SKFSealFrictionalMomentConstants':
        '''SKFSealFrictionalMomentConstants: 'SKFSealFrictionalMomentConstants' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1914.SKFSealFrictionalMomentConstants)(self.wrapped.SKFSealFrictionalMomentConstants) if self.wrapped.SKFSealFrictionalMomentConstants is not None else None

    def __copy__(self) -> 'RollingBearing':
        ''' 'Copy' is the original name of this method.

        Returns:
            mastapy.bearings.bearing_designs.rolling.RollingBearing
        '''

        method_result = self.wrapped.Copy()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def __deepcopy__(self, memo) -> 'RollingBearing':
        ''' 'Copy' is the original name of this method.

        Returns:
            mastapy.bearings.bearing_designs.rolling.RollingBearing
        '''

        method_result = self.wrapped.Copy()
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def link_to_online_catalogue(self):
        ''' 'LinkToOnlineCatalogue' is the original name of this method.'''

        self.wrapped.LinkToOnlineCatalogue()
