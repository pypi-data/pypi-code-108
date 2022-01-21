'''_2169.py

PlanetCarrierFELink
'''


from mastapy.system_model.fe.links import _2168
from mastapy._internal.python_net import python_net_import

_PLANET_CARRIER_FE_LINK = python_net_import('SMT.MastaAPI.SystemModel.FE.Links', 'PlanetCarrierFELink')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetCarrierFELink',)


class PlanetCarrierFELink(_2168.PlanetBasedFELink):
    '''PlanetCarrierFELink

    This is a mastapy class.
    '''

    TYPE = _PLANET_CARRIER_FE_LINK

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetCarrierFELink.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
