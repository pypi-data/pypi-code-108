'''_483.py

ISO6336MetalRateableMesh
'''


from mastapy.gears.rating.cylindrical.iso6336 import _484
from mastapy._internal.python_net import python_net_import

_ISO6336_METAL_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO6336MetalRateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO6336MetalRateableMesh',)


class ISO6336MetalRateableMesh(_484.ISO6336RateableMesh):
    '''ISO6336MetalRateableMesh

    This is a mastapy class.
    '''

    TYPE = _ISO6336_METAL_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO6336MetalRateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
