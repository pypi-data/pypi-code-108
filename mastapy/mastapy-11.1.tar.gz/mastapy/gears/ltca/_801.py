'''_801.py

GearMeshLoadDistributionAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.math_utility import _1312
from mastapy.gears.ltca import _802, _800
from mastapy.gears import _292
from mastapy.nodal_analysis import _82
from mastapy._internal.python_net import python_net_import
from mastapy.gears.analysis import _1167

_GEAR_LOAD_DISTRIBUTION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'GearLoadDistributionAnalysis')
_GEAR_MESH_LOAD_DISTRIBUTION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'GearMeshLoadDistributionAnalysis')
_GEAR_FLANKS = python_net_import('SMT.MastaAPI.Gears', 'GearFlanks')
_STRESS_RESULTS_TYPE = python_net_import('SMT.MastaAPI.NodalAnalysis', 'StressResultsType')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshLoadDistributionAnalysis',)


class GearMeshLoadDistributionAnalysis(_1167.GearMeshImplementationAnalysis):
    '''GearMeshLoadDistributionAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_LOAD_DISTRIBUTION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshLoadDistributionAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_case_name(self) -> 'str':
        '''str: 'LoadCaseName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadCaseName

    @property
    def actual_total_contact_ratio(self) -> 'float':
        '''float: 'ActualTotalContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActualTotalContactRatio

    @property
    def analysis_name(self) -> 'str':
        '''str: 'AnalysisName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AnalysisName

    @property
    def is_advanced_ltca(self) -> 'bool':
        '''bool: 'IsAdvancedLTCA' is the original name of this property.'''

        return self.wrapped.IsAdvancedLTCA

    @is_advanced_ltca.setter
    def is_advanced_ltca(self, value: 'bool'):
        self.wrapped.IsAdvancedLTCA = bool(value) if value else False

    @property
    def number_of_roll_angles(self) -> 'int':
        '''int: 'NumberOfRollAngles' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfRollAngles

    @property
    def minimum_force_per_unit_length(self) -> 'float':
        '''float: 'MinimumForcePerUnitLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumForcePerUnitLength

    @property
    def maximum_force_per_unit_length(self) -> 'float':
        '''float: 'MaximumForcePerUnitLength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumForcePerUnitLength

    @property
    def peakto_peak_moment_about_centre(self) -> 'float':
        '''float: 'PeaktoPeakMomentAboutCentre' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PeaktoPeakMomentAboutCentre

    @property
    def maximum_pressure_velocity(self) -> 'float':
        '''float: 'MaximumPressureVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPressureVelocity

    @property
    def maximum_contact_stress(self) -> 'float':
        '''float: 'MaximumContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactStress

    @property
    def index_of_roll_angle_with_maximum_contact_stress(self) -> 'int':
        '''int: 'IndexOfRollAngleWithMaximumContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IndexOfRollAngleWithMaximumContactStress

    @property
    def transmission_error_fourier_series(self) -> '_1312.FourierSeries':
        '''FourierSeries: 'TransmissionErrorFourierSeries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1312.FourierSeries)(self.wrapped.TransmissionErrorFourierSeries) if self.wrapped.TransmissionErrorFourierSeries is not None else None

    @property
    def load_distribution_analyses_at_single_rotation(self) -> 'List[_802.GearMeshLoadDistributionAtRotation]':
        '''List[GearMeshLoadDistributionAtRotation]: 'LoadDistributionAnalysesAtSingleRotation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LoadDistributionAnalysesAtSingleRotation, constructor.new(_802.GearMeshLoadDistributionAtRotation))
        return value

    def maximum_root_stress_with_flanks(self, gear: '_800.GearLoadDistributionAnalysis', flank: '_292.GearFlanks', stress_type: '_82.StressResultsType') -> 'float':
        ''' 'MaximumRootStress' is the original name of this method.

        Args:
            gear (mastapy.gears.ltca.GearLoadDistributionAnalysis)
            flank (mastapy.gears.GearFlanks)
            stress_type (mastapy.nodal_analysis.StressResultsType)

        Returns:
            float
        '''

        flank = conversion.mp_to_pn_enum(flank)
        stress_type = conversion.mp_to_pn_enum(stress_type)
        method_result = self.wrapped.MaximumRootStress.Overloads[_GEAR_LOAD_DISTRIBUTION_ANALYSIS, _GEAR_FLANKS, _STRESS_RESULTS_TYPE](gear.wrapped if gear else None, flank, stress_type)
        return method_result

    def maximum_root_stress(self, gear: '_800.GearLoadDistributionAnalysis', stress_type: '_82.StressResultsType') -> 'float':
        ''' 'MaximumRootStress' is the original name of this method.

        Args:
            gear (mastapy.gears.ltca.GearLoadDistributionAnalysis)
            stress_type (mastapy.nodal_analysis.StressResultsType)

        Returns:
            float
        '''

        stress_type = conversion.mp_to_pn_enum(stress_type)
        method_result = self.wrapped.MaximumRootStress.Overloads[_GEAR_LOAD_DISTRIBUTION_ANALYSIS, _STRESS_RESULTS_TYPE](gear.wrapped if gear else None, stress_type)
        return method_result
