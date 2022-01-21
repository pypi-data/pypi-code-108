'''_410.py

HypoidRateableMesh
'''


from mastapy.gears.rating.agma_gleason_conical import _528
from mastapy._internal.python_net import python_net_import

_HYPOID_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.Hypoid.Standards', 'HypoidRateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('HypoidRateableMesh',)


class HypoidRateableMesh(_528.AGMAGleasonConicalRateableMesh):
    '''HypoidRateableMesh

    This is a mastapy class.
    '''

    TYPE = _HYPOID_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HypoidRateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
