'''_528.py

AGMAGleasonConicalRateableMesh
'''


from mastapy.gears.rating.conical import _507
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.AGMAGleasonConical', 'AGMAGleasonConicalRateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalRateableMesh',)


class AGMAGleasonConicalRateableMesh(_507.ConicalRateableMesh):
    '''AGMAGleasonConicalRateableMesh

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalRateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
