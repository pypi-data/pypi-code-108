'''_266.py

OilPumpDetail
'''


from mastapy.materials.efficiency import _267
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.math_utility import _1333
from mastapy.utility import _1382
from mastapy._internal.python_net import python_net_import

_OIL_PUMP_DETAIL = python_net_import('SMT.MastaAPI.Materials.Efficiency', 'OilPumpDetail')


__docformat__ = 'restructuredtext en'
__all__ = ('OilPumpDetail',)


class OilPumpDetail(_1382.IndependentReportablePropertiesBase['OilPumpDetail']):
    '''OilPumpDetail

    This is a mastapy class.
    '''

    TYPE = _OIL_PUMP_DETAIL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OilPumpDetail.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def oil_pump_drive_type(self) -> '_267.OilPumpDriveType':
        '''OilPumpDriveType: 'OilPumpDriveType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.OilPumpDriveType)
        return constructor.new(_267.OilPumpDriveType)(value) if value is not None else None

    @oil_pump_drive_type.setter
    def oil_pump_drive_type(self, value: '_267.OilPumpDriveType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.OilPumpDriveType = value

    @property
    def oil_flow_rate_vs_speed(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'OilFlowRateVsSpeed' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.OilFlowRateVsSpeed) if self.wrapped.OilFlowRateVsSpeed is not None else None

    @oil_flow_rate_vs_speed.setter
    def oil_flow_rate_vs_speed(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.OilFlowRateVsSpeed = value

    @property
    def operating_oil_pressure_vs_speed(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'OperatingOilPressureVsSpeed' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.OperatingOilPressureVsSpeed) if self.wrapped.OperatingOilPressureVsSpeed is not None else None

    @operating_oil_pressure_vs_speed.setter
    def operating_oil_pressure_vs_speed(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.OperatingOilPressureVsSpeed = value

    @property
    def oil_pump_efficiency(self) -> 'float':
        '''float: 'OilPumpEfficiency' is the original name of this property.'''

        return self.wrapped.OilPumpEfficiency

    @oil_pump_efficiency.setter
    def oil_pump_efficiency(self, value: 'float'):
        self.wrapped.OilPumpEfficiency = float(value) if value else 0.0

    @property
    def electric_power_consumed_vs_speed(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'ElectricPowerConsumedVsSpeed' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.ElectricPowerConsumedVsSpeed) if self.wrapped.ElectricPowerConsumedVsSpeed is not None else None

    @electric_power_consumed_vs_speed.setter
    def electric_power_consumed_vs_speed(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.ElectricPowerConsumedVsSpeed = value

    @property
    def electric_motor_efficiency(self) -> 'float':
        '''float: 'ElectricMotorEfficiency' is the original name of this property.'''

        return self.wrapped.ElectricMotorEfficiency

    @electric_motor_efficiency.setter
    def electric_motor_efficiency(self, value: 'float'):
        self.wrapped.ElectricMotorEfficiency = float(value) if value else 0.0
