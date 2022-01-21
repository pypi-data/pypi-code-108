'''_545.py

BevelGearISOMaterial
'''


from mastapy.materials import _246
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.materials import _547
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_ISO_MATERIAL = python_net_import('SMT.MastaAPI.Gears.Materials', 'BevelGearISOMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearISOMaterial',)


class BevelGearISOMaterial(_547.BevelGearMaterial):
    '''BevelGearISOMaterial

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_ISO_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearISOMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

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

    @property
    def iso_material_type(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'ISOMaterialType' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.ISOMaterialType) if self.wrapped.ISOMaterialType is not None else None

    @iso_material_type.setter
    def iso_material_type(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.ISOMaterialType = value

    @property
    def use_iso633652003_material_definitions(self) -> 'bool':
        '''bool: 'UseISO633652003MaterialDefinitions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UseISO633652003MaterialDefinitions

    @property
    def limited_pitting_allowed(self) -> 'bool':
        '''bool: 'LimitedPittingAllowed' is the original name of this property.'''

        return self.wrapped.LimitedPittingAllowed

    @limited_pitting_allowed.setter
    def limited_pitting_allowed(self, value: 'bool'):
        self.wrapped.LimitedPittingAllowed = bool(value) if value else False

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
    def specify_allowable_stress_numbers(self) -> 'bool':
        '''bool: 'SpecifyAllowableStressNumbers' is the original name of this property.'''

        return self.wrapped.SpecifyAllowableStressNumbers

    @specify_allowable_stress_numbers.setter
    def specify_allowable_stress_numbers(self, value: 'bool'):
        self.wrapped.SpecifyAllowableStressNumbers = bool(value) if value else False

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
