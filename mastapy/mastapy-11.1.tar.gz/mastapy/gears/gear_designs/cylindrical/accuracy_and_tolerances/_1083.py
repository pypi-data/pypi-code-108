'''_1083.py

AGMA20151AccuracyGrades
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical.accuracy_and_tolerances import _1087
from mastapy._internal.python_net import python_net_import

_AGMA20151_ACCURACY_GRADES = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.AccuracyAndTolerances', 'AGMA20151AccuracyGrades')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMA20151AccuracyGrades',)


class AGMA20151AccuracyGrades(_1087.CylindricalAccuracyGrades):
    '''AGMA20151AccuracyGrades

    This is a mastapy class.
    '''

    TYPE = _AGMA20151_ACCURACY_GRADES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMA20151AccuracyGrades.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def input_single_pitch_deviation(self) -> 'bool':
        '''bool: 'InputSinglePitchDeviation' is the original name of this property.'''

        return self.wrapped.InputSinglePitchDeviation

    @input_single_pitch_deviation.setter
    def input_single_pitch_deviation(self, value: 'bool'):
        self.wrapped.InputSinglePitchDeviation = bool(value) if value else False

    @property
    def single_pitch_deviation_agma(self) -> 'float':
        '''float: 'SinglePitchDeviationAGMA' is the original name of this property.'''

        return self.wrapped.SinglePitchDeviationAGMA

    @single_pitch_deviation_agma.setter
    def single_pitch_deviation_agma(self, value: 'float'):
        self.wrapped.SinglePitchDeviationAGMA = float(value) if value else 0.0

    @property
    def profile_agma_quality_grade_new(self) -> 'int':
        '''int: 'ProfileAGMAQualityGradeNew' is the original name of this property.'''

        return self.wrapped.ProfileAGMAQualityGradeNew

    @profile_agma_quality_grade_new.setter
    def profile_agma_quality_grade_new(self, value: 'int'):
        self.wrapped.ProfileAGMAQualityGradeNew = int(value) if value else 0

    @property
    def helix_agma_quality_grade_new(self) -> 'int':
        '''int: 'HelixAGMAQualityGradeNew' is the original name of this property.'''

        return self.wrapped.HelixAGMAQualityGradeNew

    @helix_agma_quality_grade_new.setter
    def helix_agma_quality_grade_new(self, value: 'int'):
        self.wrapped.HelixAGMAQualityGradeNew = int(value) if value else 0

    @property
    def pitch_agma_quality_grade_new(self) -> 'int':
        '''int: 'PitchAGMAQualityGradeNew' is the original name of this property.'''

        return self.wrapped.PitchAGMAQualityGradeNew

    @pitch_agma_quality_grade_new.setter
    def pitch_agma_quality_grade_new(self, value: 'int'):
        self.wrapped.PitchAGMAQualityGradeNew = int(value) if value else 0

    @property
    def profile_agma_quality_grade_old(self) -> 'int':
        '''int: 'ProfileAGMAQualityGradeOld' is the original name of this property.'''

        return self.wrapped.ProfileAGMAQualityGradeOld

    @profile_agma_quality_grade_old.setter
    def profile_agma_quality_grade_old(self, value: 'int'):
        self.wrapped.ProfileAGMAQualityGradeOld = int(value) if value else 0

    @property
    def helix_agma_quality_grade_old(self) -> 'int':
        '''int: 'HelixAGMAQualityGradeOld' is the original name of this property.'''

        return self.wrapped.HelixAGMAQualityGradeOld

    @helix_agma_quality_grade_old.setter
    def helix_agma_quality_grade_old(self, value: 'int'):
        self.wrapped.HelixAGMAQualityGradeOld = int(value) if value else 0

    @property
    def pitch_agma_quality_grade_old(self) -> 'int':
        '''int: 'PitchAGMAQualityGradeOld' is the original name of this property.'''

        return self.wrapped.PitchAGMAQualityGradeOld

    @pitch_agma_quality_grade_old.setter
    def pitch_agma_quality_grade_old(self, value: 'int'):
        self.wrapped.PitchAGMAQualityGradeOld = int(value) if value else 0

    @property
    def radial_agma_quality_grade_new(self) -> 'int':
        '''int: 'RadialAGMAQualityGradeNew' is the original name of this property.'''

        return self.wrapped.RadialAGMAQualityGradeNew

    @radial_agma_quality_grade_new.setter
    def radial_agma_quality_grade_new(self, value: 'int'):
        self.wrapped.RadialAGMAQualityGradeNew = int(value) if value else 0

    @property
    def radial_agma_quality_grade_old(self) -> 'int':
        '''int: 'RadialAGMAQualityGradeOld' is the original name of this property.'''

        return self.wrapped.RadialAGMAQualityGradeOld

    @radial_agma_quality_grade_old.setter
    def radial_agma_quality_grade_old(self, value: 'int'):
        self.wrapped.RadialAGMAQualityGradeOld = int(value) if value else 0
