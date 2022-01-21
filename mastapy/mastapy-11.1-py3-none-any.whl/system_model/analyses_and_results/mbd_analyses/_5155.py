'''_5155.py

CylindricalPlanetGearMultibodyDynamicsAnalysis
'''


from mastapy.system_model.part_model.gears import _2267
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.mbd_analyses import _5153
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'CylindricalPlanetGearMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGearMultibodyDynamicsAnalysis',)


class CylindricalPlanetGearMultibodyDynamicsAnalysis(_5153.CylindricalGearMultibodyDynamicsAnalysis):
    '''CylindricalPlanetGearMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGearMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2267.CylindricalPlanetGear':
        '''CylindricalPlanetGear: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2267.CylindricalPlanetGear)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None
