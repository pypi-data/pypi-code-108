'''_563.py

PlasticCylindricalGearMaterial
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.gears.materials import _551
from mastapy._internal.python_net import python_net_import

_PLASTIC_CYLINDRICAL_GEAR_MATERIAL = python_net_import('SMT.MastaAPI.Gears.Materials', 'PlasticCylindricalGearMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('PlasticCylindricalGearMaterial',)


class PlasticCylindricalGearMaterial(_551.CylindricalGearMaterial):
    '''PlasticCylindricalGearMaterial

    This is a mastapy class.
    '''

    TYPE = _PLASTIC_CYLINDRICAL_GEAR_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlasticCylindricalGearMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def material_type(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'MaterialType' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.MaterialType) if self.wrapped.MaterialType is not None else None

    @material_type.setter
    def material_type(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.MaterialType = value

    @property
    def heat_conductivity(self) -> 'float':
        '''float: 'HeatConductivity' is the original name of this property.'''

        return self.wrapped.HeatConductivity

    @heat_conductivity.setter
    def heat_conductivity(self, value: 'float'):
        self.wrapped.HeatConductivity = float(value) if value else 0.0

    @property
    def modulus_of_elasticity(self) -> 'float':
        '''float: 'ModulusOfElasticity' is the original name of this property.'''

        return self.wrapped.ModulusOfElasticity

    @modulus_of_elasticity.setter
    def modulus_of_elasticity(self, value: 'float'):
        self.wrapped.ModulusOfElasticity = float(value) if value else 0.0

    @property
    def permissible_temperature_for_continuous_operation(self) -> 'float':
        '''float: 'PermissibleTemperatureForContinuousOperation' is the original name of this property.'''

        return self.wrapped.PermissibleTemperatureForContinuousOperation

    @permissible_temperature_for_continuous_operation.setter
    def permissible_temperature_for_continuous_operation(self, value: 'float'):
        self.wrapped.PermissibleTemperatureForContinuousOperation = float(value) if value else 0.0

    @property
    def permissible_temperature_for_intermittent_operation(self) -> 'float':
        '''float: 'PermissibleTemperatureForIntermittentOperation' is the original name of this property.'''

        return self.wrapped.PermissibleTemperatureForIntermittentOperation

    @permissible_temperature_for_intermittent_operation.setter
    def permissible_temperature_for_intermittent_operation(self, value: 'float'):
        self.wrapped.PermissibleTemperatureForIntermittentOperation = float(value) if value else 0.0

    @property
    def glass_transition_temperature(self) -> 'float':
        '''float: 'GlassTransitionTemperature' is the original name of this property.'''

        return self.wrapped.GlassTransitionTemperature

    @glass_transition_temperature.setter
    def glass_transition_temperature(self, value: 'float'):
        self.wrapped.GlassTransitionTemperature = float(value) if value else 0.0

    @property
    def melting_temperature(self) -> 'float':
        '''float: 'MeltingTemperature' is the original name of this property.'''

        return self.wrapped.MeltingTemperature

    @melting_temperature.setter
    def melting_temperature(self, value: 'float'):
        self.wrapped.MeltingTemperature = float(value) if value else 0.0

    @property
    def use_custom_material_for_contact(self) -> 'bool':
        '''bool: 'UseCustomMaterialForContact' is the original name of this property.'''

        return self.wrapped.UseCustomMaterialForContact

    @use_custom_material_for_contact.setter
    def use_custom_material_for_contact(self, value: 'bool'):
        self.wrapped.UseCustomMaterialForContact = bool(value) if value else False

    @property
    def use_custom_material_for_bending(self) -> 'bool':
        '''bool: 'UseCustomMaterialForBending' is the original name of this property.'''

        return self.wrapped.UseCustomMaterialForBending

    @use_custom_material_for_bending.setter
    def use_custom_material_for_bending(self, value: 'bool'):
        self.wrapped.UseCustomMaterialForBending = bool(value) if value else False

    @property
    def n0_contact(self) -> 'float':
        '''float: 'N0Contact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.N0Contact

    @property
    def n0_bending(self) -> 'float':
        '''float: 'N0Bending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.N0Bending
