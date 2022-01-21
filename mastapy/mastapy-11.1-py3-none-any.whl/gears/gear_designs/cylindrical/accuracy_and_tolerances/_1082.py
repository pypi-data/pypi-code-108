'''_1082.py

AGMA20151AccuracyGrader
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical.accuracy_and_tolerances import _1086
from mastapy._internal.python_net import python_net_import

_AGMA20151_ACCURACY_GRADER = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.AccuracyAndTolerances', 'AGMA20151AccuracyGrader')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMA20151AccuracyGrader',)


class AGMA20151AccuracyGrader(_1086.CylindricalAccuracyGraderWithProfileFormAndSlope):
    '''AGMA20151AccuracyGrader

    This is a mastapy class.
    '''

    TYPE = _AGMA20151_ACCURACY_GRADER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMA20151AccuracyGrader.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def profile_form_tolerance(self) -> 'float':
        '''float: 'ProfileFormTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileFormTolerance

    @property
    def profile_slope_tolerance(self) -> 'float':
        '''float: 'ProfileSlopeTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileSlopeTolerance

    @property
    def total_profile_tolerance(self) -> 'float':
        '''float: 'TotalProfileTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalProfileTolerance

    @property
    def helix_form_tolerance(self) -> 'float':
        '''float: 'HelixFormTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixFormTolerance

    @property
    def helix_slope_tolerance(self) -> 'float':
        '''float: 'HelixSlopeTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixSlopeTolerance

    @property
    def total_helix_tolerance(self) -> 'float':
        '''float: 'TotalHelixTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalHelixTolerance

    @property
    def single_pitch_tolerance(self) -> 'float':
        '''float: 'SinglePitchTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SinglePitchTolerance

    @property
    def specified_single_pitch_deviation(self) -> 'float':
        '''float: 'SpecifiedSinglePitchDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpecifiedSinglePitchDeviation

    @property
    def sector_pitch_deviation_tolerance(self) -> 'float':
        '''float: 'SectorPitchDeviationTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SectorPitchDeviationTolerance

    @property
    def cumulative_pitch_tolerance(self) -> 'float':
        '''float: 'CumulativePitchTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CumulativePitchTolerance

    @property
    def single_flank_tooth_to_tooth_composite_tolerance(self) -> 'float':
        '''float: 'SingleFlankToothToToothCompositeTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SingleFlankToothToToothCompositeTolerance

    @property
    def single_flank_total_composite_tolerance(self) -> 'float':
        '''float: 'SingleFlankTotalCompositeTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SingleFlankTotalCompositeTolerance

    @property
    def runout(self) -> 'float':
        '''float: 'Runout' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Runout

    @property
    def toothto_tooth_radial_composite_deviation(self) -> 'float':
        '''float: 'ToothtoToothRadialCompositeDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothtoToothRadialCompositeDeviation

    @property
    def total_radial_composite_deviation(self) -> 'float':
        '''float: 'TotalRadialCompositeDeviation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalRadialCompositeDeviation
