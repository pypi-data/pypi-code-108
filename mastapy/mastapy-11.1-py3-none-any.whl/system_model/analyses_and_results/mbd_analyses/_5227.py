'''_5227.py

StraightBevelPlanetGearMultibodyDynamicsAnalysis
'''


from mastapy.system_model.part_model.gears import _2289
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.mbd_analyses import _5222
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_PLANET_GEAR_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'StraightBevelPlanetGearMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelPlanetGearMultibodyDynamicsAnalysis',)


class StraightBevelPlanetGearMultibodyDynamicsAnalysis(_5222.StraightBevelDiffGearMultibodyDynamicsAnalysis):
    '''StraightBevelPlanetGearMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_PLANET_GEAR_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelPlanetGearMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2289.StraightBevelPlanetGear':
        '''StraightBevelPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2289.StraightBevelPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
