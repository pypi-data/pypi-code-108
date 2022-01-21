'''_2671.py

PlanetaryGearSetCompoundSystemDeflection
'''


from mastapy.system_model.analyses_and_results.system_deflections.compound import _2635
from mastapy._internal.python_net import python_net_import

_PLANETARY_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound', 'PlanetaryGearSetCompoundSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryGearSetCompoundSystemDeflection',)


class PlanetaryGearSetCompoundSystemDeflection(_2635.CylindricalGearSetCompoundSystemDeflection):
    '''PlanetaryGearSetCompoundSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryGearSetCompoundSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
