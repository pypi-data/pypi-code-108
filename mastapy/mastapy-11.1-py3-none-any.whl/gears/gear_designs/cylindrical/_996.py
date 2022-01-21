'''_996.py

CylindricalPlanetGearDesign
'''


from typing import List

from mastapy.geometry.two_d import _278
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.gears import _306
from mastapy.gears.gear_designs.cylindrical import _1020, _1019, _969
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalPlanetGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearDesign',)


class CylindricalPlanetGearDesign(_969.CylindricalGearDesign):
    '''CylindricalPlanetGearDesign

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def internal_external(self) -> '_278.InternalExternalType':
        '''InternalExternalType: 'InternalExternal' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.InternalExternal)
        return constructor.new(_278.InternalExternalType)(value) if value is not None else None

    @internal_external.setter
    def internal_external(self, value: '_278.InternalExternalType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.InternalExternal = value

    @property
    def has_factorising_sun(self) -> 'bool':
        '''bool: 'HasFactorisingSun' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasFactorisingSun

    @property
    def has_factorising_annulus(self) -> 'bool':
        '''bool: 'HasFactorisingAnnulus' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasFactorisingAnnulus

    @property
    def planetary_details(self) -> '_306.PlanetaryDetail':
        '''PlanetaryDetail: 'PlanetaryDetails' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_306.PlanetaryDetail)(self.wrapped.PlanetaryDetails) if self.wrapped.PlanetaryDetails is not None else None

    @property
    def planetary_sidebands_amplitude_factors(self) -> 'List[_1020.NamedPlanetSideBandAmplitudeFactor]':
        '''List[NamedPlanetSideBandAmplitudeFactor]: 'PlanetarySidebandsAmplitudeFactors' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetarySidebandsAmplitudeFactors, constructor.new(_1020.NamedPlanetSideBandAmplitudeFactor))
        return value

    @property
    def planet_assembly_indices(self) -> 'List[_1019.NamedPlanetAssemblyIndex]':
        '''List[NamedPlanetAssemblyIndex]: 'PlanetAssemblyIndices' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.PlanetAssemblyIndices, constructor.new(_1019.NamedPlanetAssemblyIndex))
        return value
