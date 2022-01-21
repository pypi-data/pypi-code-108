'''_2087.py

ConceptCouplingSocket
'''


from mastapy.system_model.connections_and_sockets.couplings import _2089
from mastapy._internal.python_net import python_net_import

_CONCEPT_COUPLING_SOCKET = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'ConceptCouplingSocket')


__docformat__ = 'restructuredtext en'
__all__ = ('ConceptCouplingSocket',)


class ConceptCouplingSocket(_2089.CouplingSocket):
    '''ConceptCouplingSocket

    This is a mastapy class.
    '''

    TYPE = _CONCEPT_COUPLING_SOCKET

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConceptCouplingSocket.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
