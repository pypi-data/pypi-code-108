'''_2245.py

PlanetShaftFromCAD
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model.import_from_cad import _2233
from mastapy._internal.python_net import python_net_import

_PLANET_SHAFT_FROM_CAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD', 'PlanetShaftFromCAD')


__docformat__ = 'restructuredtext en'
__all__ = ('PlanetShaftFromCAD',)


class PlanetShaftFromCAD(_2233.AbstractShaftFromCAD):
    '''PlanetShaftFromCAD

    This is a mastapy class.
    '''

    TYPE = _PLANET_SHAFT_FROM_CAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PlanetShaftFromCAD.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planet_diameter(self) -> 'float':
        '''float: 'PlanetDiameter' is the original name of this property.'''

        return self.wrapped.PlanetDiameter

    @planet_diameter.setter
    def planet_diameter(self, value: 'float'):
        self.wrapped.PlanetDiameter = float(value) if value else 0.0
