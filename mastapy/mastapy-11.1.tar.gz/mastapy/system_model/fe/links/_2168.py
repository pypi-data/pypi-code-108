'''_2168.py

PlanetBasedFELink
'''


from mastapy.system_model.fe.links import _2166
from mastapy._internal.python_net import python_net_import

_PLANET_BASED_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'PlanetBasedFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetBasedFELink',)


class PlanetBasedFELink(_2166.MultiNodeFELink):
    '''PlanetBasedFELink

    This is a mastapy class.
    '''

    TYPE = _PLANET_BASED_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetBasedFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
