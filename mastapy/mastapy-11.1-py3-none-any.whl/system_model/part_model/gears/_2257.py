'''_2257.py

BevelDifferentialPlanetGear
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model.gears import _2255
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_PLANET_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'BevelDifferentialPlanetGear')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialPlanetGear',)


class BevelDifferentialPlanetGear(_2255.BevelDifferentialGear):
    '''BevelDifferentialPlanetGear

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_PLANET_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialPlanetGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_planets(self) -> 'int':
        '''int: 'NumberOfPlanets' is the original name of this property.'''

        return self.wrapped.NumberOfPlanets

    @number_of_planets.setter
    def number_of_planets(self, value: 'int'):
        self.wrapped.NumberOfPlanets = int(value) if value else 0
