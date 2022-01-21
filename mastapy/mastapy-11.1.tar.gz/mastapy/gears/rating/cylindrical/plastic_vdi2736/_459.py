'''_459.py

VDI2736MetalPlasticRateableMesh
'''


from mastapy.gears.rating.cylindrical.plastic_vdi2736 import _454
from mastapy._internal.python_net import python_net_import

_VDI2736_METAL_PLASTIC_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.PlasticVDI2736', 'VDI2736MetalPlasticRateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('VDI2736MetalPlasticRateableMesh',)


class VDI2736MetalPlasticRateableMesh(_454.PlasticGearVDI2736AbstractRateableMesh):
    '''VDI2736MetalPlasticRateableMesh

    This is a mastapy class.
    '''

    TYPE = _VDI2736_METAL_PLASTIC_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VDI2736MetalPlasticRateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
