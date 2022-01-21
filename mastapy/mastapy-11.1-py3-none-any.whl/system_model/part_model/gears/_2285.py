'''_2285.py

StraightBevelDiffGear
'''


from mastapy.gears.gear_designs.straight_bevel_diff import _918
from mastapy._internal import constructor
from mastapy.system_model.part_model.gears import _2259
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_DIFF_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'StraightBevelDiffGear')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelDiffGear',)


class StraightBevelDiffGear(_2259.BevelGear):
    '''StraightBevelDiffGear

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_DIFF_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelDiffGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def bevel_gear_design(self) -> '_918.StraightBevelDiffGearDesign':
        '''StraightBevelDiffGearDesign: 'BevelGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_918.StraightBevelDiffGearDesign)(self.wrapped.BevelGearDesign) if self.wrapped.BevelGearDesign is not None else None

    @property
    def straight_bevel_diff_gear_design(self) -> '_918.StraightBevelDiffGearDesign':
        '''StraightBevelDiffGearDesign: 'StraightBevelDiffGearDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_918.StraightBevelDiffGearDesign)(self.wrapped.StraightBevelDiffGearDesign) if self.wrapped.StraightBevelDiffGearDesign is not None else None
