'''_6697.py

TransmissionEfficiencySettings
'''


from mastapy._internal import constructor
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_TRANSMISSION_EFFICIENCY_SETTINGS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'TransmissionEfficiencySettings')


__docformat__ = 'restructuredtext en'
__all__ = ('TransmissionEfficiencySettings',)


class TransmissionEfficiencySettings(_0.APIBase):
    '''TransmissionEfficiencySettings

    This is a mastapy class.
    '''

    TYPE = _TRANSMISSION_EFFICIENCY_SETTINGS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TransmissionEfficiencySettings.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def include_efficiency(self) -> 'bool':
        '''bool: 'IncludeEfficiency' is the original name of this property.'''

        return self.wrapped.IncludeEfficiency

    @include_efficiency.setter
    def include_efficiency(self, value: 'bool'):
        self.wrapped.IncludeEfficiency = bool(value) if value else False

    @property
    def include_shaft_windage_loss(self) -> 'bool':
        '''bool: 'IncludeShaftWindageLoss' is the original name of this property.'''

        return self.wrapped.IncludeShaftWindageLoss

    @include_shaft_windage_loss.setter
    def include_shaft_windage_loss(self, value: 'bool'):
        self.wrapped.IncludeShaftWindageLoss = bool(value) if value else False

    @property
    def include_gear_windage_loss(self) -> 'bool':
        '''bool: 'IncludeGearWindageLoss' is the original name of this property.'''

        return self.wrapped.IncludeGearWindageLoss

    @include_gear_windage_loss.setter
    def include_gear_windage_loss(self, value: 'bool'):
        self.wrapped.IncludeGearWindageLoss = bool(value) if value else False

    @property
    def include_bearing_and_seal_loss(self) -> 'bool':
        '''bool: 'IncludeBearingAndSealLoss' is the original name of this property.'''

        return self.wrapped.IncludeBearingAndSealLoss

    @include_bearing_and_seal_loss.setter
    def include_bearing_and_seal_loss(self, value: 'bool'):
        self.wrapped.IncludeBearingAndSealLoss = bool(value) if value else False

    @property
    def include_clearance_bearing_loss(self) -> 'bool':
        '''bool: 'IncludeClearanceBearingLoss' is the original name of this property.'''

        return self.wrapped.IncludeClearanceBearingLoss

    @include_clearance_bearing_loss.setter
    def include_clearance_bearing_loss(self, value: 'bool'):
        self.wrapped.IncludeClearanceBearingLoss = bool(value) if value else False

    @property
    def use_advanced_needle_roller_bearing_power_loss_calculation(self) -> 'bool':
        '''bool: 'UseAdvancedNeedleRollerBearingPowerLossCalculation' is the original name of this property.'''

        return self.wrapped.UseAdvancedNeedleRollerBearingPowerLossCalculation

    @use_advanced_needle_roller_bearing_power_loss_calculation.setter
    def use_advanced_needle_roller_bearing_power_loss_calculation(self, value: 'bool'):
        self.wrapped.UseAdvancedNeedleRollerBearingPowerLossCalculation = bool(value) if value else False

    @property
    def include_gear_mesh_loss(self) -> 'bool':
        '''bool: 'IncludeGearMeshLoss' is the original name of this property.'''

        return self.wrapped.IncludeGearMeshLoss

    @include_gear_mesh_loss.setter
    def include_gear_mesh_loss(self, value: 'bool'):
        self.wrapped.IncludeGearMeshLoss = bool(value) if value else False

    @property
    def include_belt_loss(self) -> 'bool':
        '''bool: 'IncludeBeltLoss' is the original name of this property.'''

        return self.wrapped.IncludeBeltLoss

    @include_belt_loss.setter
    def include_belt_loss(self, value: 'bool'):
        self.wrapped.IncludeBeltLoss = bool(value) if value else False

    @property
    def include_oil_pump_loss(self) -> 'bool':
        '''bool: 'IncludeOilPumpLoss' is the original name of this property.'''

        return self.wrapped.IncludeOilPumpLoss

    @include_oil_pump_loss.setter
    def include_oil_pump_loss(self, value: 'bool'):
        self.wrapped.IncludeOilPumpLoss = bool(value) if value else False

    @property
    def include_clutch_loss(self) -> 'bool':
        '''bool: 'IncludeClutchLoss' is the original name of this property.'''

        return self.wrapped.IncludeClutchLoss

    @include_clutch_loss.setter
    def include_clutch_loss(self, value: 'bool'):
        self.wrapped.IncludeClutchLoss = bool(value) if value else False

    @property
    def volumetric_oil_air_mixture_ratio(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'VolumetricOilAirMixtureRatio' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.VolumetricOilAirMixtureRatio) if self.wrapped.VolumetricOilAirMixtureRatio is not None else None

    @volumetric_oil_air_mixture_ratio.setter
    def volumetric_oil_air_mixture_ratio(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.VolumetricOilAirMixtureRatio = value
