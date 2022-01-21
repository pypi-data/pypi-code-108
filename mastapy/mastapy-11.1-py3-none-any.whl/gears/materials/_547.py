'''_547.py

BevelGearMaterial
'''


from mastapy.gears.materials import _568, _554
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_MATERIAL = python_net_import('SMT.MastaAPI.Gears.Materials', 'BevelGearMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearMaterial',)


class BevelGearMaterial(_554.GearMaterial):
    '''BevelGearMaterial

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def sn_curve_definition(self) -> '_568.SNCurveDefinition':
        '''SNCurveDefinition: 'SNCurveDefinition' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.SNCurveDefinition)
        return constructor.new(_568.SNCurveDefinition)(value) if value is not None else None

    @sn_curve_definition.setter
    def sn_curve_definition(self, value: '_568.SNCurveDefinition'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.SNCurveDefinition = value

    @property
    def allowable_bending_stress(self) -> 'float':
        '''float: 'AllowableBendingStress' is the original name of this property.'''

        return self.wrapped.AllowableBendingStress

    @allowable_bending_stress.setter
    def allowable_bending_stress(self, value: 'float'):
        self.wrapped.AllowableBendingStress = float(value) if value else 0.0

    @property
    def allowable_contact_stress(self) -> 'float':
        '''float: 'AllowableContactStress' is the original name of this property.'''

        return self.wrapped.AllowableContactStress

    @allowable_contact_stress.setter
    def allowable_contact_stress(self, value: 'float'):
        self.wrapped.AllowableContactStress = float(value) if value else 0.0

    @property
    def thermal_constant(self) -> 'float':
        '''float: 'ThermalConstant' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalConstant
