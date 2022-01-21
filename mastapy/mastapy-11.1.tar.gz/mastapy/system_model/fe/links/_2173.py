'''_2173.py

SingleNodeFELink
'''


from mastapy.system_model.fe.links import _2159
from mastapy._internal.python_net import python_net_import

_SINGLE_NODE_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'SingleNodeFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('SingleNodeFELink',)


class SingleNodeFELink(_2159.FELink):
    '''SingleNodeFELink

    This is a mastapy class.
    '''

    TYPE = _SINGLE_NODE_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SingleNodeFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
