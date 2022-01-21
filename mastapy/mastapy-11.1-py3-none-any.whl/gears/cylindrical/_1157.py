'''_1157.py

GearLTCAContactChartDataAsTextFile
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_LTCA_CONTACT_CHART_DATA_AS_TEXT_FILE = python_net_import('SMT.MastaAPI.Gears.Cylindrical', 'GearLTCAContactChartDataAsTextFile')


__docformat__ = 'restructuredtext en'
__all__ = ('GearLTCAContactChartDataAsTextFile',)


class GearLTCAContactChartDataAsTextFile(_0.APIBase):
    '''GearLTCAContactChartDataAsTextFile

    This is a mastapy class.
    '''

    TYPE = _GEAR_LTCA_CONTACT_CHART_DATA_AS_TEXT_FILE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearLTCAContactChartDataAsTextFile.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def max_pressure(self):
        ''' 'MaxPressure' is the original name of this method.'''

        self.wrapped.MaxPressure()

    def force_per_unit_length(self):
        ''' 'ForcePerUnitLength' is the original name of this method.'''

        self.wrapped.ForcePerUnitLength()

    def hertzian_contact_half_width(self):
        ''' 'HertzianContactHalfWidth' is the original name of this method.'''

        self.wrapped.HertzianContactHalfWidth()

    def max_shear_stress(self):
        ''' 'MaxShearStress' is the original name of this method.'''

        self.wrapped.MaxShearStress()

    def depth_of_max_shear_stress(self):
        ''' 'DepthOfMaxShearStress' is the original name of this method.'''

        self.wrapped.DepthOfMaxShearStress()

    def total_deflection_for_mesh(self):
        ''' 'TotalDeflectionForMesh' is the original name of this method.'''

        self.wrapped.TotalDeflectionForMesh()

    def gap_between_loaded_flanks_transverse(self):
        ''' 'GapBetweenLoadedFlanksTransverse' is the original name of this method.'''

        self.wrapped.GapBetweenLoadedFlanksTransverse()
