'''_521.py

SpiralBevelGearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.conical import _503
from mastapy._internal.python_net import python_net_import

_SPIRAL_BEVEL_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Bevel.Standards', 'SpiralBevelGearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('SpiralBevelGearSingleFlankRating',)


class SpiralBevelGearSingleFlankRating(_503.ConicalGearSingleFlankRating):
    '''SpiralBevelGearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _SPIRAL_BEVEL_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpiralBevelGearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def thermal_constant(self) -> 'float':
        '''float: 'ThermalConstant' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermalConstant

    @property
    def distance_factor(self) -> 'float':
        '''float: 'DistanceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DistanceFactor

    @property
    def geometry_factor_j(self) -> 'float':
        '''float: 'GeometryFactorJ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorJ

    @property
    def bending_strength_geometry_factor(self) -> 'float':
        '''float: 'BendingStrengthGeometryFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BendingStrengthGeometryFactor

    @property
    def durability_factor(self) -> 'float':
        '''float: 'DurabilityFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DurabilityFactor

    @property
    def life_factor_contact(self) -> 'float':
        '''float: 'LifeFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorContact

    @property
    def life_factor_bending(self) -> 'float':
        '''float: 'LifeFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LifeFactorBending

    @property
    def surface_condition_factor(self) -> 'float':
        '''float: 'SurfaceConditionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SurfaceConditionFactor

    @property
    def damage_contact(self) -> 'float':
        '''float: 'DamageContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DamageContact

    @property
    def damage_bending(self) -> 'float':
        '''float: 'DamageBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DamageBending
