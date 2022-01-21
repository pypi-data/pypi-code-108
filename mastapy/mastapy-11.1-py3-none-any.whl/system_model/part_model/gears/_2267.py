'''_2267.py

CylindricalPlanetGear
'''


from mastapy.system_model.part_model.gears import _2265
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_PLANET_GEAR = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Gears', 'CylindricalPlanetGear')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalPlanetGear',)


class CylindricalPlanetGear(_2265.CylindricalGear):
    '''CylindricalPlanetGear

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_PLANET_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalPlanetGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
