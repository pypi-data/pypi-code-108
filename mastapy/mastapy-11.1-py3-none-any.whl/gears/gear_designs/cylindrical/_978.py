'''_978.py

CylindricalGearMicroGeometrySettings
'''


from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1071
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.gears.gear_designs.cylindrical import _999
from mastapy.gears.micro_geometry import _531
from mastapy.utility import _1382
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_MICRO_GEOMETRY_SETTINGS = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearMicroGeometrySettings')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMicroGeometrySettings',)


class CylindricalGearMicroGeometrySettings(_1382.IndependentReportablePropertiesBase['CylindricalGearMicroGeometrySettings']):
    '''CylindricalGearMicroGeometrySettings

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MICRO_GEOMETRY_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMicroGeometrySettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def micro_geometry_lead_tolerance_chart_view(self) -> '_1071.MicroGeometryLeadToleranceChartView':
        '''MicroGeometryLeadToleranceChartView: 'MicroGeometryLeadToleranceChartView' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.MicroGeometryLeadToleranceChartView)
        return constructor.new(_1071.MicroGeometryLeadToleranceChartView)(value) if value is not None else None

    @micro_geometry_lead_tolerance_chart_view.setter
    def micro_geometry_lead_tolerance_chart_view(self, value: '_1071.MicroGeometryLeadToleranceChartView'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.MicroGeometryLeadToleranceChartView = value

    @property
    def scale_and_range_of_flank_relief_axes_for_micro_geometry_tolerance_charts(self) -> '_999.DoubleAxisScaleAndRange':
        '''DoubleAxisScaleAndRange: 'ScaleAndRangeOfFlankReliefAxesForMicroGeometryToleranceCharts' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.ScaleAndRangeOfFlankReliefAxesForMicroGeometryToleranceCharts)
        return constructor.new(_999.DoubleAxisScaleAndRange)(value) if value is not None else None

    @scale_and_range_of_flank_relief_axes_for_micro_geometry_tolerance_charts.setter
    def scale_and_range_of_flank_relief_axes_for_micro_geometry_tolerance_charts(self, value: '_999.DoubleAxisScaleAndRange'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.ScaleAndRangeOfFlankReliefAxesForMicroGeometryToleranceCharts = value

    @property
    def flank_side_with_zero_face_width(self) -> '_531.FlankSide':
        '''FlankSide: 'FlankSideWithZeroFaceWidth' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.FlankSideWithZeroFaceWidth)
        return constructor.new(_531.FlankSide)(value) if value is not None else None

    @flank_side_with_zero_face_width.setter
    def flank_side_with_zero_face_width(self, value: '_531.FlankSide'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.FlankSideWithZeroFaceWidth = value
