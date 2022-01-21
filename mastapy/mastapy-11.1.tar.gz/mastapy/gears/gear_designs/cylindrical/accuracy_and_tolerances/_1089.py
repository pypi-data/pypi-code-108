'''_1089.py

ISO13282013AccuracyGrader
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical.accuracy_and_tolerances import _1091
from mastapy._internal.python_net import python_net_import

_ISO13282013_ACCURACY_GRADER = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.AccuracyAndTolerances', 'ISO13282013AccuracyGrader')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO13282013AccuracyGrader',)


class ISO13282013AccuracyGrader(_1091.ISO1328AccuracyGraderCommon):
    '''ISO13282013AccuracyGrader

    This is a mastapy class.
    '''

    TYPE = _ISO13282013_ACCURACY_GRADER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO13282013AccuracyGrader.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def single_pitch_tolerance(self) -> 'float':
        '''float: 'SinglePitchTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SinglePitchTolerance

    @property
    def cumulative_pitch_index_tolerance(self) -> 'float':
        '''float: 'CumulativePitchIndexTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CumulativePitchIndexTolerance

    @property
    def profile_slope_tolerance(self) -> 'float':
        '''float: 'ProfileSlopeTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileSlopeTolerance

    @property
    def profile_form_tolerance(self) -> 'float':
        '''float: 'ProfileFormTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileFormTolerance

    @property
    def total_profile_tolerance(self) -> 'float':
        '''float: 'TotalProfileTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalProfileTolerance

    @property
    def helix_slope_tolerance(self) -> 'float':
        '''float: 'HelixSlopeTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixSlopeTolerance

    @property
    def helix_form_tolerance(self) -> 'float':
        '''float: 'HelixFormTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixFormTolerance

    @property
    def total_helix_tolerance(self) -> 'float':
        '''float: 'TotalHelixTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalHelixTolerance

    @property
    def total_radial_composite_tolerance(self) -> 'float':
        '''float: 'TotalRadialCompositeTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalRadialCompositeTolerance

    @property
    def toothto_tooth_radial_composite_tolerance(self) -> 'float':
        '''float: 'ToothtoToothRadialCompositeTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothtoToothRadialCompositeTolerance

    @property
    def runout_tolerance(self) -> 'float':
        '''float: 'RunoutTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RunoutTolerance

    @property
    def sector_pitch_deviation_tolerance(self) -> 'float':
        '''float: 'SectorPitchDeviationTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SectorPitchDeviationTolerance

    @property
    def adjacent_pitch_difference_tolerance(self) -> 'float':
        '''float: 'AdjacentPitchDifferenceTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdjacentPitchDifferenceTolerance
