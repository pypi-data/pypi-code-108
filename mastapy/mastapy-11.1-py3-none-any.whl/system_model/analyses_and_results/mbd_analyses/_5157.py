'''_5157.py

ExternalCADModelMultibodyDynamicsAnalysis
'''


from mastapy.system_model.part_model import _2193
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6598
from mastapy.system_model.analyses_and_results.mbd_analyses import _5130
from mastapy._internal.python_net import python_net_import

_EXTERNAL_CAD_MODEL_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses', 'ExternalCADModelMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ExternalCADModelMultibodyDynamicsAnalysis',)


class ExternalCADModelMultibodyDynamicsAnalysis(_5130.ComponentMultibodyDynamicsAnalysis):
    '''ExternalCADModelMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _EXTERNAL_CAD_MODEL_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExternalCADModelMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2193.ExternalCADModel':
        '''ExternalCADModel: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2193.ExternalCADModel)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_load_case(self) -> '_6598.ExternalCADModelLoadCase':
        '''ExternalCADModelLoadCase: 'ComponentLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6598.ExternalCADModelLoadCase)(self.wrapped.ComponentLoadCase) if self.wrapped.ComponentLoadCase is not None else None
