'''_2165.py

MultiNodeConnectorFELink
'''


from mastapy.system_model.fe.links import _2166
from mastapy._internal.python_net import python_net_import

_MULTI_NODE_CONNECTOR_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'MultiNodeConnectorFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('MultiNodeConnectorFELink',)


class MultiNodeConnectorFELink(_2166.MultiNodeFELink):
    '''MultiNodeConnectorFELink

    This is a mastapy class.
    '''

    TYPE = _MULTI_NODE_CONNECTOR_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MultiNodeConnectorFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
