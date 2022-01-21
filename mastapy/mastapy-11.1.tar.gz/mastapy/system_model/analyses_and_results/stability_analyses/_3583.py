'''_3583.py

PlanetaryGearSetStabilityAnalysis
'''


from mastapy.system_model.part_model.gears import _2282
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.stability_analyses import _3547
from mastapy._internal.python_net import python_net_import

_PLANETARY_GEAR_SET_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses', 'PlanetaryGearSetStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryGearSetStabilityAnalysis',)


class PlanetaryGearSetStabilityAnalysis(_3547.CylindricalGearSetStabilityAnalysis):
    '''PlanetaryGearSetStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_GEAR_SET_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryGearSetStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_design(self) -> '_2282.PlanetaryGearSet':
        '''PlanetaryGearSet: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2282.PlanetaryGearSet)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None
