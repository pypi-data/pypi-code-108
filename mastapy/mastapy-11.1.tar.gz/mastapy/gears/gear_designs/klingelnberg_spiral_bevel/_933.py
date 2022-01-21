'''_933.py

KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign
'''


from mastapy.gears.gear_designs.klingelnberg_conical import _941
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_MESHED_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.KlingelnbergSpiralBevel', 'KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign',)


class KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign(_941.KlingelnbergConicalMeshedGearDesign):
    '''KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_MESHED_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
