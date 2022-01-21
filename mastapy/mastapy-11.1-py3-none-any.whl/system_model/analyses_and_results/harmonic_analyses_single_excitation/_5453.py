'''_5453.py

CylindricalPlanetGearHarmonicAnalysisOfSingleExcitation
'''


from mastapy.system_model.part_model.gears import _2267
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation import _5450
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation', 'CylindricalPlanetGearHarmonicAnalysisOfSingleExcitation')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearHarmonicAnalysisOfSingleExcitation',)


class CylindricalPlanetGearHarmonicAnalysisOfSingleExcitation(_5450.CylindricalGearHarmonicAnalysisOfSingleExcitation):
    '''CylindricalPlanetGearHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearHarmonicAnalysisOfSingleExcitation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2267.CylindricalPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
