'''_2239.py

CylindricalGearInPlanetarySetFromCAD
'''


from mastapy.system_model.part_model.import_from_cad import _2238
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_IN_PLANETARY_SET_FROM_CAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD', 'CylindricalGearInPlanetarySetFromCAD')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearInPlanetarySetFromCAD',)


class CylindricalGearInPlanetarySetFromCAD(_2238.CylindricalGearFromCAD):
    '''CylindricalGearInPlanetarySetFromCAD

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_IN_PLANETARY_SET_FROM_CAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearInPlanetarySetFromCAD.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
