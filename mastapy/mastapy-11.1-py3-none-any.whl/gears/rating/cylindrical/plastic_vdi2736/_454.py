'''_454.py

PlasticGearVDI2736AbstractRateableMesh
'''


from mastapy.gears.rating.cylindrical.iso6336 import _484
from mastapy._internal.python_net import python_net_import

_PLASTIC_GEAR_VDI2736_ABSTRACT_RATEABLE_MESH = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.PlasticVDI2736', 'PlasticGearVDI2736AbstractRateableMesh')


__docformat__ = 'restructuredtext en'
__all__ = ('PlasticGearVDI2736AbstractRateableMesh',)


class PlasticGearVDI2736AbstractRateableMesh(_484.ISO6336RateableMesh):
    '''PlasticGearVDI2736AbstractRateableMesh

    This is a mastapy class.
    '''

    TYPE = _PLASTIC_GEAR_VDI2736_ABSTRACT_RATEABLE_MESH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlasticGearVDI2736AbstractRateableMesh.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
