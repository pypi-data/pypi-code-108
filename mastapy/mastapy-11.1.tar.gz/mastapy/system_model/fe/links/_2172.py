'''_2172.py

ShaftHubConnectionFELink
'''


from mastapy.system_model.fe.links import _2165
from mastapy._internal.python_net import python_net_import

_SHAFT_HUB_CONNECTION_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'ShaftHubConnectionFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftHubConnectionFELink',)


class ShaftHubConnectionFELink(_2165.MultiNodeConnectorFELink):
    '''ShaftHubConnectionFELink

    This is a mastapy class.
    '''

    TYPE = _SHAFT_HUB_CONNECTION_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftHubConnectionFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
