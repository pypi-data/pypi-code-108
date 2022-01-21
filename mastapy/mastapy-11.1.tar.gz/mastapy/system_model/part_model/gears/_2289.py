'''_2289.py

StraightBevelPlanetGear
'''


from mastapy.gears import _306
from mastapy._internal import constructor
from mastapy.system_model.part_model.gears import _2285
from mastapy._internal.python_net import python_net_import

_STRAIGHT_BEVEL_PLANET_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'StraightBevelPlanetGear')


__docformat__ = 'restructuredtext en'
__all__ = ('StraightBevelPlanetGear',)


class StraightBevelPlanetGear(_2285.StraightBevelDiffGear):
    '''StraightBevelPlanetGear

    This is a mastapy class.
    '''

    TYPE = _STRAIGHT_BEVEL_PLANET_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StraightBevelPlanetGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetary_details(self) -> '_306.PlanetaryDetail':
        '''PlanetaryDetail: 'PlanetaryDetails' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_306.PlanetaryDetail)(self.wrapped.PlanetaryDetails) if self.wrapped.PlanetaryDetails is not None else None
