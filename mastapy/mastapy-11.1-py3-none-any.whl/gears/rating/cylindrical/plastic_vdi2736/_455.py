'''_455.py

PlasticPlasticVDI2736MeshSingleFlankRating
'''


from mastapy.gears.rating.cylindrical.plastic_vdi2736 import _453
from mastapy._internal.python_net import python_net_import

_PLASTIC_PLASTIC_VDI2736_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.PlasticVDI2736', 'PlasticPlasticVDI2736MeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('PlasticPlasticVDI2736MeshSingleFlankRating',)


class PlasticPlasticVDI2736MeshSingleFlankRating(_453.PlasticGearVDI2736AbstractMeshSingleFlankRating):
    '''PlasticPlasticVDI2736MeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _PLASTIC_PLASTIC_VDI2736_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlasticPlasticVDI2736MeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
