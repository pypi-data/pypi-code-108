'''_6019.py

ConceptCouplingConnectionDynamicAnalysis
'''


from mastapy.system_model.connections_and_sockets.couplings import _2086
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6552
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6030
from mastapy._internal.python_net import python_net_import

_CONCEPT_COUPLING_CONNECTION_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses', 'ConceptCouplingConnectionDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptCouplingConnectionDynamicAnalysis',)


class ConceptCouplingConnectionDynamicAnalysis(_6030.CouplingConnectionDynamicAnalysis):
    '''ConceptCouplingConnectionDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_COUPLING_CONNECTION_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptCouplingConnectionDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2086.ConceptCouplingConnection':
        '''ConceptCouplingConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2086.ConceptCouplingConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6552.ConceptCouplingConnectionLoadCase':
        '''ConceptCouplingConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6552.ConceptCouplingConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None
