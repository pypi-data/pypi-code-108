'''_854.py

CylindricalGearMeshTIFFAnalysis
'''


from mastapy.gears.analysis import _1166
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_MESH_TIFF_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.GearTwoDFEAnalysis', 'CylindricalGearMeshTIFFAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMeshTIFFAnalysis',)


class CylindricalGearMeshTIFFAnalysis(_1166.GearMeshDesignAnalysis):
    '''CylindricalGearMeshTIFFAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MESH_TIFF_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMeshTIFFAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
