'''_2167.py

PlanetaryConnectorMultiNodeFELink
'''


from mastapy.system_model.fe.links import _2168
from mastapy._internal.python_net import python_net_import

_PLANETARY_CONNECTOR_MULTI_NODE_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'PlanetaryConnectorMultiNodeFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetaryConnectorMultiNodeFELink',)


class PlanetaryConnectorMultiNodeFELink(_2168.PlanetBasedFELink):
    '''PlanetaryConnectorMultiNodeFELink

    This is a mastapy class.
    '''

    TYPE = _PLANETARY_CONNECTOR_MULTI_NODE_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetaryConnectorMultiNodeFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
