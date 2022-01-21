'''_5191.py

OilSealMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2207
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6644
from mastapy.system_model.analyses_and_results.mbd_analyses import _5141
from mastapy._internal.python_net import python_net_import

_OIL_SEAL_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'OilSealMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('OilSealMultibodyDynamicsAnalysis',)


class OilSealMultibodyDynamicsAnalysis(_5141.ConnectorMultibodyDynamicsAnalysis):
    '''OilSealMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _OIL_SEAL_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OilSealMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2207.OilSeal':
        '''OilSeal: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2207.OilSeal)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6644.OilSealLoadCase':
        '''OilSealLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6644.OilSealLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None

    @property
    def planetaries(self) -> 'List[OilSealMultibodyDynamicsAnalysis]':
        '''List[OilSealMultibodyDynamicsAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(OilSealMultibodyDynamicsAnalysis))
        return value
