'''_2326.py

CVT
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model.couplings import _2316
from mastapy._internal.python_net import python_net_import

_CVT = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'CVT')


__docformat__ = 'restructuredtext en'
__all__ = ('CVT',)


class CVT(_2316.BeltDrive):
    '''CVT

    This is a mastapy class.
    '''

    TYPE = _CVT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVT.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def use_improved_model(self) -> 'bool':
        '''bool: 'UseImprovedModel' is the original name of this property.'''

        return self.wrapped.UseImprovedModel

    @use_improved_model.setter
    def use_improved_model(self, value: 'bool'):
        self.wrapped.UseImprovedModel = bool(value) if value else False

    @property
    def pulley_sheave_angle(self) -> 'float':
        '''float: 'PulleySheaveAngle' is the original name of this property.'''

        return self.wrapped.PulleySheaveAngle

    @pulley_sheave_angle.setter
    def pulley_sheave_angle(self, value: 'float'):
        self.wrapped.PulleySheaveAngle = float(value) if value else 0.0

    @property
    def coefficient_of_static_friction_with_lubrication(self) -> 'float':
        '''float: 'CoefficientOfStaticFrictionWithLubrication' is the original name of this property.'''

        return self.wrapped.CoefficientOfStaticFrictionWithLubrication

    @coefficient_of_static_friction_with_lubrication.setter
    def coefficient_of_static_friction_with_lubrication(self, value: 'float'):
        self.wrapped.CoefficientOfStaticFrictionWithLubrication = float(value) if value else 0.0

    @property
    def belt_loss_constant(self) -> 'float':
        '''float: 'BeltLossConstant' is the original name of this property.'''

        return self.wrapped.BeltLossConstant

    @belt_loss_constant.setter
    def belt_loss_constant(self, value: 'float'):
        self.wrapped.BeltLossConstant = float(value) if value else 0.0

    @property
    def pump_pressure_loss_constant(self) -> 'float':
        '''float: 'PumpPressureLossConstant' is the original name of this property.'''

        return self.wrapped.PumpPressureLossConstant

    @pump_pressure_loss_constant.setter
    def pump_pressure_loss_constant(self, value: 'float'):
        self.wrapped.PumpPressureLossConstant = float(value) if value else 0.0

    @property
    def pump_speed_loss_constant(self) -> 'float':
        '''float: 'PumpSpeedLossConstant' is the original name of this property.'''

        return self.wrapped.PumpSpeedLossConstant

    @pump_speed_loss_constant.setter
    def pump_speed_loss_constant(self, value: 'float'):
        self.wrapped.PumpSpeedLossConstant = float(value) if value else 0.0

    @property
    def pump_displacement_per_revolution(self) -> 'float':
        '''float: 'PumpDisplacementPerRevolution' is the original name of this property.'''

        return self.wrapped.PumpDisplacementPerRevolution

    @pump_displacement_per_revolution.setter
    def pump_displacement_per_revolution(self, value: 'float'):
        self.wrapped.PumpDisplacementPerRevolution = float(value) if value else 0.0

    @property
    def cross_sectional_area_of_the_pump_outlet(self) -> 'float':
        '''float: 'CrossSectionalAreaOfThePumpOutlet' is the original name of this property.'''

        return self.wrapped.CrossSectionalAreaOfThePumpOutlet

    @cross_sectional_area_of_the_pump_outlet.setter
    def cross_sectional_area_of_the_pump_outlet(self, value: 'float'):
        self.wrapped.CrossSectionalAreaOfThePumpOutlet = float(value) if value else 0.0

    @property
    def pump_speed_factor(self) -> 'float':
        '''float: 'PumpSpeedFactor' is the original name of this property.'''

        return self.wrapped.PumpSpeedFactor

    @pump_speed_factor.setter
    def pump_speed_factor(self, value: 'float'):
        self.wrapped.PumpSpeedFactor = float(value) if value else 0.0

    @property
    def contact_stiffness_for_unit_length(self) -> 'float':
        '''float: 'ContactStiffnessForUnitLength' is the original name of this property.'''

        return self.wrapped.ContactStiffnessForUnitLength

    @contact_stiffness_for_unit_length.setter
    def contact_stiffness_for_unit_length(self, value: 'float'):
        self.wrapped.ContactStiffnessForUnitLength = float(value) if value else 0.0

    @property
    def tangential_stiffness(self) -> 'float':
        '''float: 'TangentialStiffness' is the original name of this property.'''

        return self.wrapped.TangentialStiffness

    @tangential_stiffness.setter
    def tangential_stiffness(self, value: 'float'):
        self.wrapped.TangentialStiffness = float(value) if value else 0.0
