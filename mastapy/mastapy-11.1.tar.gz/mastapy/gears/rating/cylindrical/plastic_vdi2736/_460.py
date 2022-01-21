'''_460.py

VDI2736PlasticMetalRateableMesh
'''


from mastapy.gears.rating.cylindrical.plastic_vdi2736 import _454
from mastapy._internal.python_net import python_net_import

_VDI2736_PLASTIC_METAL_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.PlasticVDI2736', 'VDI2736PlasticMetalRateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('VDI2736PlasticMetalRateableMesh',)


class VDI2736PlasticMetalRateableMesh(_454.PlasticGearVDI2736AbstractRateableMesh):
    '''VDI2736PlasticMetalRateableMesh

    This is a mastapy class.
    '''

    TYPE = _VDI2736_PLASTIC_METAL_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VDI2736PlasticMetalRateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
