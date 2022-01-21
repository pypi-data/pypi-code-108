'''_557.py

ISOCylindricalGearMaterial
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import overridable, list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.materials import _246
from mastapy.gears.materials import _551
from mastapy._internal.python_net import python_net_import

_ISO_CYLINDRICAL_GEAR_MATERIAL = python_net_import('SMT.MastaAPI.Gears.Materials', 'ISOCylindricalGearMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('ISOCylindricalGearMaterial',)


class ISOCylindricalGearMaterial(_551.CylindricalGearMaterial):
    '''ISOCylindricalGearMaterial

    This is a mastapy class.
    '''

    TYPE = _ISO_CYLINDRICAL_GEAR_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISOCylindricalGearMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def long_life_life_factor_bending(self) -> 'float':
        '''float: 'LongLifeLifeFactorBending' is the original name of this property.'''

        return self.wrapped.LongLifeLifeFactorBending

    @long_life_life_factor_bending.setter
    def long_life_life_factor_bending(self, value: 'float'):
        self.wrapped.LongLifeLifeFactorBending = float(value) if value else 0.0

    @property
    def long_life_life_factor_contact(self) -> 'float':
        '''float: 'LongLifeLifeFactorContact' is the original name of this property.'''

        return self.wrapped.LongLifeLifeFactorContact

    @long_life_life_factor_contact.setter
    def long_life_life_factor_contact(self, value: 'float'):
        self.wrapped.LongLifeLifeFactorContact = float(value) if value else 0.0

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
    def shot_peening_bending_stress_benefit(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ShotPeeningBendingStressBenefit' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ShotPeeningBendingStressBenefit) if self.wrapped.ShotPeeningBendingStressBenefit is not None else None

    @shot_peening_bending_stress_benefit.setter
    def shot_peening_bending_stress_benefit(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ShotPeeningBendingStressBenefit = value

    @property
    def quality_grade(self) -> '_246.QualityGrade':
        '''QualityGrade: 'QualityGrade' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.QualityGrade)
        return constructor.new(_246.QualityGrade)(value) if value is not None else None

    @quality_grade.setter
    def quality_grade(self, value: '_246.QualityGrade'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.QualityGrade = value

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
    def use_iso633652003_material_definitions(self) -> 'bool':
        '''bool: 'UseISO633652003MaterialDefinitions' is the original name of this property.'''

        return self.wrapped.UseISO633652003MaterialDefinitions

    @use_iso633652003_material_definitions.setter
    def use_iso633652003_material_definitions(self, value: 'bool'):
        self.wrapped.UseISO633652003MaterialDefinitions = bool(value) if value else False

    @property
    def limited_pitting_allowed(self) -> 'bool':
        '''bool: 'LimitedPittingAllowed' is the original name of this property.'''

        return self.wrapped.LimitedPittingAllowed

    @limited_pitting_allowed.setter
    def limited_pitting_allowed(self, value: 'bool'):
        self.wrapped.LimitedPittingAllowed = bool(value) if value else False

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

    @property
    def material_has_a_well_defined_yield_point(self) -> 'bool':
        '''bool: 'MaterialHasAWellDefinedYieldPoint' is the original name of this property.'''

        return self.wrapped.MaterialHasAWellDefinedYieldPoint

    @material_has_a_well_defined_yield_point.setter
    def material_has_a_well_defined_yield_point(self, value: 'bool'):
        self.wrapped.MaterialHasAWellDefinedYieldPoint = bool(value) if value else False

    @property
    def proof_stress(self) -> 'float':
        '''float: 'ProofStress' is the original name of this property.'''

        return self.wrapped.ProofStress

    @proof_stress.setter
    def proof_stress(self, value: 'float'):
        self.wrapped.ProofStress = float(value) if value else 0.0
