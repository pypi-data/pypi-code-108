'''_6552.py

ConceptCouplingConnectionLoadCase
'''


from mastapy.system_model.connections_and_sockets.couplings import _2086
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6565
from mastapy._internal.python_net import python_net_import

_CONCEPT_COUPLING_CONNECTION_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'ConceptCouplingConnectionLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptCouplingConnectionLoadCase',)


class ConceptCouplingConnectionLoadCase(_6565.CouplingConnectionLoadCase):
    '''ConceptCouplingConnectionLoadCase

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_COUPLING_CONNECTION_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptCouplingConnectionLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2086.ConceptCouplingConnection':
        '''ConceptCouplingConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2086.ConceptCouplingConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None
