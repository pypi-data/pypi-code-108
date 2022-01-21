'''_1052.py

CylindricalGearMicroGeometry
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.utility.report import _1559
from mastapy.gears.gear_designs.cylindrical import _969, _996, _981
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1047, _1070
from mastapy.gears.analysis import _1165
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_MICRO_GEOMETRY = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'CylindricalGearMicroGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMicroGeometry',)


class CylindricalGearMicroGeometry(_1165.GearImplementationDetail):
    '''CylindricalGearMicroGeometry

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MICRO_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMicroGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_same_micro_geometry_on_both_flanks(self) -> 'bool':
        '''bool: 'UseSameMicroGeometryOnBothFlanks' is the original name of this property.'''

        return self.wrapped.UseSameMicroGeometryOnBothFlanks

    @use_same_micro_geometry_on_both_flanks.setter
    def use_same_micro_geometry_on_both_flanks(self, value: 'bool'):
        self.wrapped.UseSameMicroGeometryOnBothFlanks = bool(value) if value else False

    @property
    def profile_control_point_is_user_specified(self) -> 'bool':
        '''bool: 'ProfileControlPointIsUserSpecified' is the original name of this property.'''

        return self.wrapped.ProfileControlPointIsUserSpecified

    @profile_control_point_is_user_specified.setter
    def profile_control_point_is_user_specified(self, value: 'bool'):
        self.wrapped.ProfileControlPointIsUserSpecified = bool(value) if value else False

    @property
    def lead_form_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'LeadFormChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.LeadFormChart) if self.wrapped.LeadFormChart is not None else None

    @property
    def lead_slope_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'LeadSlopeChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.LeadSlopeChart) if self.wrapped.LeadSlopeChart is not None else None

    @property
    def lead_total_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'LeadTotalChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.LeadTotalChart) if self.wrapped.LeadTotalChart is not None else None

    @property
    def lead_total_nominal_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'LeadTotalNominalChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.LeadTotalNominalChart) if self.wrapped.LeadTotalNominalChart is not None else None

    @property
    def profile_form_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'ProfileFormChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.ProfileFormChart) if self.wrapped.ProfileFormChart is not None else None

    @property
    def profile_form_10_percent_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'ProfileForm10PercentChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.ProfileForm10PercentChart) if self.wrapped.ProfileForm10PercentChart is not None else None

    @property
    def profile_form_50_percent_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'ProfileForm50PercentChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.ProfileForm50PercentChart) if self.wrapped.ProfileForm50PercentChart is not None else None

    @property
    def profile_form_90_percent_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'ProfileForm90PercentChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.ProfileForm90PercentChart) if self.wrapped.ProfileForm90PercentChart is not None else None

    @property
    def profile_total_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'ProfileTotalChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.ProfileTotalChart) if self.wrapped.ProfileTotalChart is not None else None

    @property
    def profile_total_nominal_chart(self) -> '_1559.LegacyChartDefinition':
        '''LegacyChartDefinition: 'ProfileTotalNominalChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1559.LegacyChartDefinition)(self.wrapped.ProfileTotalNominalChart) if self.wrapped.ProfileTotalNominalChart is not None else None

    @property
    def cylindrical_gear(self) -> '_969.CylindricalGearDesign':
        '''CylindricalGearDesign: 'CylindricalGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _969.CylindricalGearDesign.TYPE not in self.wrapped.CylindricalGear.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear to CylindricalGearDesign. Expected: {}.'.format(self.wrapped.CylindricalGear.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGear.__class__)(self.wrapped.CylindricalGear) if self.wrapped.CylindricalGear is not None else None

    @property
    def left_flank(self) -> '_1047.CylindricalGearFlankMicroGeometry':
        '''CylindricalGearFlankMicroGeometry: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1047.CylindricalGearFlankMicroGeometry)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None

    @property
    def right_flank(self) -> '_1047.CylindricalGearFlankMicroGeometry':
        '''CylindricalGearFlankMicroGeometry: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1047.CylindricalGearFlankMicroGeometry)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None

    @property
    def profile_control_point(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ProfileControlPoint' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ProfileControlPoint) if self.wrapped.ProfileControlPoint is not None else None

    @property
    def flanks(self) -> 'List[_1047.CylindricalGearFlankMicroGeometry]':
        '''List[CylindricalGearFlankMicroGeometry]: 'Flanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Flanks, constructor.new(_1047.CylindricalGearFlankMicroGeometry))
        return value

    @property
    def meshed_gears(self) -> 'List[_1070.MeshedCylindricalGearMicroGeometry]':
        '''List[MeshedCylindricalGearMicroGeometry]: 'MeshedGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshedGears, constructor.new(_1070.MeshedCylindricalGearMicroGeometry))
        return value

    @property
    def both_flanks(self) -> '_1047.CylindricalGearFlankMicroGeometry':
        '''CylindricalGearFlankMicroGeometry: 'BothFlanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1047.CylindricalGearFlankMicroGeometry)(self.wrapped.BothFlanks) if self.wrapped.BothFlanks is not None else None
