'''_855.py

CylindricalGearMeshTIFFAnalysisDutyCycle
'''


from mastapy.gears.analysis import _1166
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_MESH_TIFF_ANALYSIS_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Gears.GearTwoDFEAnalysis', 'CylindricalGearMeshTIFFAnalysisDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMeshTIFFAnalysisDutyCycle',)


class CylindricalGearMeshTIFFAnalysisDutyCycle(_1166.GearMeshDesignAnalysis):
    '''CylindricalGearMeshTIFFAnalysisDutyCycle

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MESH_TIFF_ANALYSIS_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMeshTIFFAnalysisDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
