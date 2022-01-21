'''_1113.py

KimosBevelHypoidSingleLoadCaseResultsData
'''


from typing import List

from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.conical import _1114
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_KIMOS_BEVEL_HYPOID_SINGLE_LOAD_CASE_RESULTS_DATA = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Conical', 'KimosBevelHypoidSingleLoadCaseResultsData')


__docformat__ = 'restructuredtext en'
__all__ = ('KimosBevelHypoidSingleLoadCaseResultsData',)


class KimosBevelHypoidSingleLoadCaseResultsData(_0.APIBase):
    '''KimosBevelHypoidSingleLoadCaseResultsData

    This is a mastapy class.
    '''

    TYPE = _KIMOS_BEVEL_HYPOID_SINGLE_LOAD_CASE_RESULTS_DATA

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KimosBevelHypoidSingleLoadCaseResultsData.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def average_mesh_stiffness_per_unit_face_width(self) -> 'float':
        '''float: 'AverageMeshStiffnessPerUnitFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AverageMeshStiffnessPerUnitFaceWidth

    @property
    def maximum_contact_pressure(self) -> 'float':
        '''float: 'MaximumContactPressure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumContactPressure

    @property
    def maximum_pinion_root_stress(self) -> 'float':
        '''float: 'MaximumPinionRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumPinionRootStress

    @property
    def maximum_wheel_root_stress(self) -> 'float':
        '''float: 'MaximumWheelRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumWheelRootStress

    @property
    def maximum_flash_temperature(self) -> 'float':
        '''float: 'MaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumFlashTemperature

    @property
    def maximum_friction_coefficient(self) -> 'float':
        '''float: 'MaximumFrictionCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumFrictionCoefficient

    @property
    def maximum_sliding_velocity(self) -> 'float':
        '''float: 'MaximumSlidingVelocity' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumSlidingVelocity

    @property
    def peak_to_peak_te_linear_loaded(self) -> 'float':
        '''float: 'PeakToPeakTELinearLoaded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PeakToPeakTELinearLoaded

    @property
    def peak_to_peak_te_linear_unloaded(self) -> 'float':
        '''float: 'PeakToPeakTELinearUnloaded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PeakToPeakTELinearUnloaded

    @property
    def efficiency(self) -> 'float':
        '''float: 'Efficiency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Efficiency

    @property
    def contact_ratio_under_load(self) -> 'float':
        '''float: 'ContactRatioUnderLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRatioUnderLoad

    @property
    def contact_pressure_chart(self) -> 'Image':
        '''Image: 'ContactPressureChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.ContactPressureChart)
        return value

    @property
    def pinion_root_stress_chart(self) -> 'Image':
        '''Image: 'PinionRootStressChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.PinionRootStressChart)
        return value

    @property
    def wheel_root_stress_chart(self) -> 'Image':
        '''Image: 'WheelRootStressChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.WheelRootStressChart)
        return value

    @property
    def sliding_velocity_chart(self) -> 'Image':
        '''Image: 'SlidingVelocityChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.SlidingVelocityChart)
        return value

    @property
    def flash_temperature_chart(self) -> 'Image':
        '''Image: 'FlashTemperatureChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.FlashTemperatureChart)
        return value

    @property
    def friction_coefficient_chart(self) -> 'Image':
        '''Image: 'FrictionCoefficientChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.FrictionCoefficientChart)
        return value

    @property
    def pressure_velocity_pv_chart(self) -> 'Image':
        '''Image: 'PressureVelocityPVChart' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.PressureVelocityPVChart)
        return value

    @property
    def single_rotation_angle_results(self) -> 'List[_1114.KimosBevelHypoidSingleRotationAngleResult]':
        '''List[KimosBevelHypoidSingleRotationAngleResult]: 'SingleRotationAngleResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SingleRotationAngleResults, constructor.new(_1114.KimosBevelHypoidSingleRotationAngleResult))
        return value
