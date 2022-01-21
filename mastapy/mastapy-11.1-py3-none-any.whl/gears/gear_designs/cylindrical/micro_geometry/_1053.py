'''_1053.py

CylindricalGearMicroGeometryDutyCycle
'''


from mastapy.gears.gear_two_d_fe_analysis import _859
from mastapy._internal import constructor
from mastapy.gears.analysis import _1162
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_MICRO_GEOMETRY_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'CylindricalGearMicroGeometryDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMicroGeometryDutyCycle',)


class CylindricalGearMicroGeometryDutyCycle(_1162.GearDesignAnalysis):
    '''CylindricalGearMicroGeometryDutyCycle

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MICRO_GEOMETRY_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMicroGeometryDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def tiff_analysis(self) -> '_859.CylindricalGearTIFFAnalysisDutyCycle':
        '''CylindricalGearTIFFAnalysisDutyCycle: 'TIFFAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_859.CylindricalGearTIFFAnalysisDutyCycle)(self.wrapped.TIFFAnalysis) if self.wrapped.TIFFAnalysis is not None else None
