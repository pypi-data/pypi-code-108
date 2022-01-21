'''_792.py

CylindricalMeshedGearLoadDistributionAnalysis
'''


from mastapy._internal import constructor, conversion
from mastapy.gears.ltca.cylindrical import _816
from mastapy.gears.cylindrical import _1156, _1155
from mastapy.gears.ltca import _787
from mastapy.math_utility import _1314
from mastapy._internal.python_net import python_net_import
from mastapy import _0

_CONTACT_RESULT_TYPE = python_net_import('SMT.MastaAPI.Gears.LTCA', 'ContactResultType')
_CYLINDRICAL_MESHED_GEAR_LOAD_DISTRIBUTION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.LTCA', 'CylindricalMeshedGearLoadDistributionAnalysis')
_INT_32 = python_net_import('System', 'Int32')
_BOOLEAN = python_net_import('System', 'Boolean')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalMeshedGearLoadDistributionAnalysis',)


class CylindricalMeshedGearLoadDistributionAnalysis(_0.APIBase):
    '''CylindricalMeshedGearLoadDistributionAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_MESHED_GEAR_LOAD_DISTRIBUTION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalMeshedGearLoadDistributionAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def nominal_torque(self) -> 'float':
        '''float: 'NominalTorque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NominalTorque

    @property
    def torque_scaled_by_application_and_dynamic_factors(self) -> 'float':
        '''float: 'TorqueScaledByApplicationAndDynamicFactors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TorqueScaledByApplicationAndDynamicFactors

    @property
    def is_loaded_on_tip(self) -> 'bool':
        '''bool: 'IsLoadedOnTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsLoadedOnTip

    @property
    def maximum_von_mises_root_stress_tension(self) -> 'float':
        '''float: 'MaximumVonMisesRootStressTension' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumVonMisesRootStressTension

    @property
    def maximum_principal_root_stress_tension(self) -> 'float':
        '''float: 'MaximumPrincipalRootStressTension' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPrincipalRootStressTension

    @property
    def maximum_von_mises_root_stress_compression(self) -> 'float':
        '''float: 'MaximumVonMisesRootStressCompression' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumVonMisesRootStressCompression

    @property
    def maximum_principal_root_stress_compression(self) -> 'float':
        '''float: 'MaximumPrincipalRootStressCompression' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPrincipalRootStressCompression

    @property
    def percentage_of_potential_contact_area_loaded(self) -> 'float':
        '''float: 'PercentageOfPotentialContactAreaLoaded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PercentageOfPotentialContactAreaLoaded

    @property
    def percentage_of_potential_contact_area_utilized(self) -> 'float':
        '''float: 'PercentageOfPotentialContactAreaUtilized' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PercentageOfPotentialContactAreaUtilized

    @property
    def percentage_of_effective_face_width_utilized(self) -> 'float':
        '''float: 'PercentageOfEffectiveFaceWidthUtilized' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PercentageOfEffectiveFaceWidthUtilized

    @property
    def percentage_of_effective_profile_utilized(self) -> 'float':
        '''float: 'PercentageOfEffectiveProfileUtilized' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PercentageOfEffectiveProfileUtilized

    @property
    def contact_patch_edge_loading_factor(self) -> 'float':
        '''float: 'ContactPatchEdgeLoadingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactPatchEdgeLoadingFactor

    @property
    def contact_patch_tip_loading_factor(self) -> 'float':
        '''float: 'ContactPatchTipLoadingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactPatchTipLoadingFactor

    @property
    def contact_patch_offset_factor(self) -> 'float':
        '''float: 'ContactPatchOffsetFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactPatchOffsetFactor

    @property
    def gear_load_distribution_analysis(self) -> '_816.CylindricalGearLoadDistributionAnalysis':
        '''CylindricalGearLoadDistributionAnalysis: 'GearLoadDistributionAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_816.CylindricalGearLoadDistributionAnalysis)(self.wrapped.GearLoadDistributionAnalysis) if self.wrapped.GearLoadDistributionAnalysis is not None else None

    @property
    def other_gear_load_distribution_analysis(self) -> '_816.CylindricalGearLoadDistributionAnalysis':
        '''CylindricalGearLoadDistributionAnalysis: 'OtherGearLoadDistributionAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_816.CylindricalGearLoadDistributionAnalysis)(self.wrapped.OtherGearLoadDistributionAnalysis) if self.wrapped.OtherGearLoadDistributionAnalysis is not None else None

    @property
    def contact_charts(self) -> '_1156.CylindricalGearLTCAContactCharts':
        '''CylindricalGearLTCAContactCharts: 'ContactCharts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1156.CylindricalGearLTCAContactCharts)(self.wrapped.ContactCharts) if self.wrapped.ContactCharts is not None else None

    @property
    def contact_charts_as_text_file(self) -> '_1155.CylindricalGearLTCAContactChartDataAsTextFile':
        '''CylindricalGearLTCAContactChartDataAsTextFile: 'ContactChartsAsTextFile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1155.CylindricalGearLTCAContactChartDataAsTextFile)(self.wrapped.ContactChartsAsTextFile) if self.wrapped.ContactChartsAsTextFile is not None else None

    def contact_patch_detailed(self, result_type: '_787.ContactResultType', number_of_face_width_steps: 'int', number_of_roll_distance_steps: 'int') -> '_1314.GriddedSurface':
        ''' 'ContactPatch' is the original name of this method.

        Args:
            result_type (mastapy.gears.ltca.ContactResultType)
            number_of_face_width_steps (int)
            number_of_roll_distance_steps (int)

        Returns:
            mastapy.math_utility.GriddedSurface
        '''

        result_type = conversion.mp_to_pn_enum(result_type)
        number_of_face_width_steps = int(number_of_face_width_steps)
        number_of_roll_distance_steps = int(number_of_roll_distance_steps)
        method_result = self.wrapped.ContactPatch.Overloads[_CONTACT_RESULT_TYPE, _INT_32, _INT_32](result_type, number_of_face_width_steps if number_of_face_width_steps else 0, number_of_roll_distance_steps if number_of_roll_distance_steps else 0)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def contact_patch(self, result_type: '_787.ContactResultType', include_tip_contact: 'bool') -> '_1314.GriddedSurface':
        ''' 'ContactPatch' is the original name of this method.

        Args:
            result_type (mastapy.gears.ltca.ContactResultType)
            include_tip_contact (bool)

        Returns:
            mastapy.math_utility.GriddedSurface
        '''

        result_type = conversion.mp_to_pn_enum(result_type)
        include_tip_contact = bool(include_tip_contact)
        method_result = self.wrapped.ContactPatch.Overloads[_CONTACT_RESULT_TYPE, _BOOLEAN](result_type, include_tip_contact if include_tip_contact else False)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def contact_patch_as_text(self, result_type: '_787.ContactResultType', include_tip_contact: 'bool', file_name_with_path: 'str'):
        ''' 'ContactPatchAsText' is the original name of this method.

        Args:
            result_type (mastapy.gears.ltca.ContactResultType)
            include_tip_contact (bool)
            file_name_with_path (str)
        '''

        result_type = conversion.mp_to_pn_enum(result_type)
        include_tip_contact = bool(include_tip_contact)
        file_name_with_path = str(file_name_with_path)
        self.wrapped.ContactPatchAsText(result_type, include_tip_contact if include_tip_contact else False, file_name_with_path if file_name_with_path else '')
