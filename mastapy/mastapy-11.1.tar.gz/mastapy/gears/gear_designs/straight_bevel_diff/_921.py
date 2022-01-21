'''_921.py

StraightBevelDiffMeshedGearDesign
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.bevel import _1130
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_MESHED_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.StraightBevelDiff', 'StraightBevelDiffMeshedGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffMeshedGearDesign',)


class StraightBevelDiffMeshedGearDesign(_1130.BevelMeshedGearDesign):
    '''StraightBevelDiffMeshedGearDesign

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_MESHED_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffMeshedGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def strength_factor(self) -> 'float':
        '''float: 'StrengthFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthFactor

    @property
    def geometry_factor_j(self) -> 'float':
        '''float: 'GeometryFactorJ' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorJ

    @property
    def mean_topland(self) -> 'float':
        '''float: 'MeanTopland' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanTopland
