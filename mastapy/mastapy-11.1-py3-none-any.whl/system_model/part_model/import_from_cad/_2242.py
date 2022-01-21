'''_2242.py

CylindricalSunGearFromCAD
'''


from mastapy.system_model.part_model.import_from_cad import _2239
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_SUN_GEAR_FROM_CAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD', 'CylindricalSunGearFromCAD')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalSunGearFromCAD',)


class CylindricalSunGearFromCAD(_2239.CylindricalGearInPlanetarySetFromCAD):
    '''CylindricalSunGearFromCAD

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_SUN_GEAR_FROM_CAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalSunGearFromCAD.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
