'''_239.py

Material
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.materials import _242, _228
from mastapy.utility.databases import _1597
from mastapy._internal.python_net import python_net_import

_MATERIAL = python_net_import('SMT.MastaAPI.Materials', 'Material')


__docformat__ = 'restructuredtext en'
__all__ = ('Material',)


class Material(_1597.NamedDatabaseItem):
    '''Material

    This is a mastapy class.
    '''

    TYPE = _MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Material.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def material_name(self) -> 'str':
        '''str: 'MaterialName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaterialName

    @property
    def density(self) -> 'float':
        '''float: 'Density' is the original name of this property.'''

        return self.wrapped.Density

    @density.setter
    def density(self, value: 'float'):
        self.wrapped.Density = float(value) if value else 0.0

    @property
    def modulus_of_elasticity(self) -> 'float':
        '''float: 'ModulusOfElasticity' is the original name of this property.'''

        return self.wrapped.ModulusOfElasticity

    @modulus_of_elasticity.setter
    def modulus_of_elasticity(self, value: 'float'):
        self.wrapped.ModulusOfElasticity = float(value) if value else 0.0

    @property
    def poissons_ratio(self) -> 'float':
        '''float: 'PoissonsRatio' is the original name of this property.'''

        return self.wrapped.PoissonsRatio

    @poissons_ratio.setter
    def poissons_ratio(self, value: 'float'):
        self.wrapped.PoissonsRatio = float(value) if value else 0.0

    @property
    def plane_strain_modulus(self) -> 'float':
        '''float: 'PlaneStrainModulus' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PlaneStrainModulus

    @property
    def coefficient_of_thermal_expansion(self) -> 'float':
        '''float: 'CoefficientOfThermalExpansion' is the original name of this property.'''

        return self.wrapped.CoefficientOfThermalExpansion

    @coefficient_of_thermal_expansion.setter
    def coefficient_of_thermal_expansion(self, value: 'float'):
        self.wrapped.CoefficientOfThermalExpansion = float(value) if value else 0.0

    @property
    def shear_modulus(self) -> 'float':
        '''float: 'ShearModulus' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShearModulus

    @property
    def shear_yield_stress(self) -> 'float':
        '''float: 'ShearYieldStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShearYieldStress

    @property
    def shear_fatigue_strength(self) -> 'float':
        '''float: 'ShearFatigueStrength' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShearFatigueStrength

    @property
    def standard(self) -> '_242.MaterialStandards':
        '''MaterialStandards: 'Standard' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Standard)
        return constructor.new(_242.MaterialStandards)(value) if value is not None else None

    @standard.setter
    def standard(self, value: '_242.MaterialStandards'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Standard = value

    @property
    def hardness_type(self) -> '_228.HardnessType':
        '''HardnessType: 'HardnessType' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.HardnessType)
        return constructor.new(_228.HardnessType)(value) if value is not None else None

    @hardness_type.setter
    def hardness_type(self, value: '_228.HardnessType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.HardnessType = value

    @property
    def surface_hardness(self) -> 'float':
        '''float: 'SurfaceHardness' is the original name of this property.'''

        return self.wrapped.SurfaceHardness

    @surface_hardness.setter
    def surface_hardness(self, value: 'float'):
        self.wrapped.SurfaceHardness = float(value) if value else 0.0

    @property
    def surface_hardness_range_max_in_hrc(self) -> 'float':
        '''float: 'SurfaceHardnessRangeMaxInHRC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceHardnessRangeMaxInHRC

    @property
    def surface_hardness_range_min_in_hrc(self) -> 'float':
        '''float: 'SurfaceHardnessRangeMinInHRC' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceHardnessRangeMinInHRC

    @property
    def surface_hardness_range_max_in_hb(self) -> 'float':
        '''float: 'SurfaceHardnessRangeMaxInHB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceHardnessRangeMaxInHB

    @property
    def surface_hardness_range_min_in_hb(self) -> 'float':
        '''float: 'SurfaceHardnessRangeMinInHB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceHardnessRangeMinInHB

    @property
    def surface_hardness_range_max_in_hv(self) -> 'float':
        '''float: 'SurfaceHardnessRangeMaxInHV' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceHardnessRangeMaxInHV

    @property
    def surface_hardness_range_min_in_hv(self) -> 'float':
        '''float: 'SurfaceHardnessRangeMinInHV' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceHardnessRangeMinInHV

    @property
    def tensile_yield_strength(self) -> 'float':
        '''float: 'TensileYieldStrength' is the original name of this property.'''

        return self.wrapped.TensileYieldStrength

    @tensile_yield_strength.setter
    def tensile_yield_strength(self, value: 'float'):
        self.wrapped.TensileYieldStrength = float(value) if value else 0.0

    @property
    def ultimate_tensile_strength(self) -> 'float':
        '''float: 'UltimateTensileStrength' is the original name of this property.'''

        return self.wrapped.UltimateTensileStrength

    @ultimate_tensile_strength.setter
    def ultimate_tensile_strength(self, value: 'float'):
        self.wrapped.UltimateTensileStrength = float(value) if value else 0.0

    @property
    def maximum_allowable_temperature(self) -> 'float':
        '''float: 'MaximumAllowableTemperature' is the original name of this property.'''

        return self.wrapped.MaximumAllowableTemperature

    @maximum_allowable_temperature.setter
    def maximum_allowable_temperature(self, value: 'float'):
        self.wrapped.MaximumAllowableTemperature = float(value) if value else 0.0
