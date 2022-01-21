'''_858.py

CylindricalGearTIFFAnalysis
'''


from mastapy.gears.gear_two_d_fe_analysis import _860
from mastapy._internal import constructor
from mastapy.gears.analysis import _1162
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_TIFF_ANALYSIS = python_net_import('SMT.MastaAPI.Gears.GearTwoDFEAnalysis', 'CylindricalGearTIFFAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearTIFFAnalysis',)


class CylindricalGearTIFFAnalysis(_1162.GearDesignAnalysis):
    '''CylindricalGearTIFFAnalysis

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_TIFF_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearTIFFAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def analysis(self) -> '_860.CylindricalGearTwoDimensionalFEAnalysis':
        '''CylindricalGearTwoDimensionalFEAnalysis: 'Analysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_860.CylindricalGearTwoDimensionalFEAnalysis)(self.wrapped.Analysis) if self.wrapped.Analysis is not None else None
