'''_457.py

PlasticVDI2736GearSingleFlankRatingInAMetalPlasticOrAPlasticMetalMesh
'''


from mastapy.gears.rating.cylindrical.plastic_vdi2736 import _452
from mastapy._internal.python_net import python_net_import

_PLASTIC_VDI2736_GEAR_SINGLE_FLANK_RATING_IN_A_METAL_PLASTIC_OR_A_PLASTIC_METAL_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.PlasticVDI2736', 'PlasticVDI2736GearSingleFlankRatingInAMetalPlasticOrAPlasticMetalMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('PlasticVDI2736GearSingleFlankRatingInAMetalPlasticOrAPlasticMetalMesh',)


class PlasticVDI2736GearSingleFlankRatingInAMetalPlasticOrAPlasticMetalMesh(_452.PlasticGearVDI2736AbstractGearSingleFlankRating):
    '''PlasticVDI2736GearSingleFlankRatingInAMetalPlasticOrAPlasticMetalMesh

    This is a mastapy class.
    '''

    TYPE = _PLASTIC_VDI2736_GEAR_SINGLE_FLANK_RATING_IN_A_METAL_PLASTIC_OR_A_PLASTIC_METAL_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlasticVDI2736GearSingleFlankRatingInAMetalPlasticOrAPlasticMetalMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
