'''_829.py

ConicalMeshedGearLoadDistributionAnalysis
'''


from mastapy._internal import constructor
from mastapy.gears.ltca.conical import _827
from mastapy.gears.cylindrical import (
    _1158, _1156, _1157, _1155
)
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONICAL_MESHED_GEAR_LOAD_DISTRIBUTION_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.LTCA.Conical', 'ConicalMeshedGearLoadDistributionAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalMeshedGearLoadDistributionAnalysis',)


class ConicalMeshedGearLoadDistributionAnalysis(_0.APIBase):
    '''ConicalMeshedGearLoadDistributionAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MESHED_GEAR_LOAD_DISTRIBUTION_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalMeshedGearLoadDistributionAnalysis.TYPE'):
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
    def torque(self) -> 'float':
        '''float: 'Torque' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Torque

    @property
    def estimated_gear_stiffness_from_fe_model(self) -> 'float':
        '''float: 'EstimatedGearStiffnessFromFEModel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EstimatedGearStiffnessFromFEModel

    @property
    def maximum_von_mises_root_stress_tension_side(self) -> 'float':
        '''float: 'MaximumVonMisesRootStressTensionSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumVonMisesRootStressTensionSide

    @property
    def maximum_von_mises_root_stress_compression_side(self) -> 'float':
        '''float: 'MaximumVonMisesRootStressCompressionSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumVonMisesRootStressCompressionSide

    @property
    def max_tensile_principal_root_stress_tension_side(self) -> 'float':
        '''float: 'MaxTensilePrincipalRootStressTensionSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaxTensilePrincipalRootStressTensionSide

    @property
    def max_tensile_principal_root_stress_compression_side(self) -> 'float':
        '''float: 'MaxTensilePrincipalRootStressCompressionSide' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaxTensilePrincipalRootStressCompressionSide

    @property
    def gear_load_distribution_analysis(self) -> '_827.ConicalGearLoadDistributionAnalysis':
        '''ConicalGearLoadDistributionAnalysis: 'GearLoadDistributionAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_827.ConicalGearLoadDistributionAnalysis)(self.wrapped.GearLoadDistributionAnalysis) if self.wrapped.GearLoadDistributionAnalysis is not None else None

    @property
    def contact_charts(self) -> '_1158.GearLTCAContactCharts':
        '''GearLTCAContactCharts: 'ContactCharts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1158.GearLTCAContactCharts.TYPE not in self.wrapped.ContactCharts.__class__.__mro__:
            raise CastException('Failed to cast contact_charts to GearLTCAContactCharts. Expected: {}.'.format(self.wrapped.ContactCharts.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContactCharts.__class__)(self.wrapped.ContactCharts) if self.wrapped.ContactCharts is not None else None

    @property
    def contact_charts_as_text_file(self) -> '_1157.GearLTCAContactChartDataAsTextFile':
        '''GearLTCAContactChartDataAsTextFile: 'ContactChartsAsTextFile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1157.GearLTCAContactChartDataAsTextFile.TYPE not in self.wrapped.ContactChartsAsTextFile.__class__.__mro__:
            raise CastException('Failed to cast contact_charts_as_text_file to GearLTCAContactChartDataAsTextFile. Expected: {}.'.format(self.wrapped.ContactChartsAsTextFile.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContactChartsAsTextFile.__class__)(self.wrapped.ContactChartsAsTextFile) if self.wrapped.ContactChartsAsTextFile is not None else None
