'''_6310.py

CylindricalPlanetGearCriticalSpeedAnalysis
'''


from mastapy.system_model.part_model.gears import _2267
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6307
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_CRITICAL_SPEED_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses', 'CylindricalPlanetGearCriticalSpeedAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearCriticalSpeedAnalysis',)


class CylindricalPlanetGearCriticalSpeedAnalysis(_6307.CylindricalGearCriticalSpeedAnalysis):
    '''CylindricalPlanetGearCriticalSpeedAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_CRITICAL_SPEED_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearCriticalSpeedAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2267.CylindricalPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
