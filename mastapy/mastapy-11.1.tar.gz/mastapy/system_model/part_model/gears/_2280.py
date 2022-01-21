'''_2280.py

KlingelnbergCycloPalloidSpiralBevelGear
'''


from mastapy.gears.gear_designs.klingelnberg_spiral_bevel import _930
from mastapy._internal import constructor
from mastapy.system_model.part_model.gears import _2276
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'KlingelnbergCycloPalloidSpiralBevelGear')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGear',)


class KlingelnbergCycloPalloidSpiralBevelGear(_2276.KlingelnbergCycloPalloidConicalGear):
    '''KlingelnbergCycloPalloidSpiralBevelGear

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def conical_gear_design(self) -> '_930.KlingelnbergCycloPalloidSpiralBevelGearDesign':
        '''KlingelnbergCycloPalloidSpiralBevelGearDesign: 'ConicalGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_930.KlingelnbergCycloPalloidSpiralBevelGearDesign)(self.wrapped.ConicalGearDesign) if self.wrapped.ConicalGearDesign is not None else None

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_design(self) -> '_930.KlingelnbergCycloPalloidSpiralBevelGearDesign':
        '''KlingelnbergCycloPalloidSpiralBevelGearDesign: 'KlingelnbergCycloPalloidSpiralBevelGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_930.KlingelnbergCycloPalloidSpiralBevelGearDesign)(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearDesign) if self.wrapped.KlingelnbergCycloPalloidSpiralBevelGearDesign is not None else None
