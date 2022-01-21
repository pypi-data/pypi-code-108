'''_2090.py

PartToPartShearCouplingConnection
'''


from mastapy.system_model.connections_and_sockets.couplings import _2088
from mastapy._internal.python_net import python_net_import

_PART_TO_PART_SHEAR_COUPLING_CONNECTION = python_net_import('SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings', 'PartToPartShearCouplingConnection')


__docformat__ = 'restructuredtext en'
__all__ = ('PartToPartShearCouplingConnection',)


class PartToPartShearCouplingConnection(_2088.CouplingConnection):
    '''PartToPartShearCouplingConnection

    This is a mastapy class.
    '''

    TYPE = _PART_TO_PART_SHEAR_COUPLING_CONNECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartToPartShearCouplingConnection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
