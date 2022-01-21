'''_2086.py

ConceptCouplingConnection
'''


from mastapy.system_model.connections_and_sockets.couplings import _2088
from mastapy._internal.python_net import python_net_import

_CONCEPT_COUPLING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'ConceptCouplingConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptCouplingConnection',)


class ConceptCouplingConnection(_2088.CouplingConnection):
    '''ConceptCouplingConnection

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_COUPLING_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptCouplingConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
