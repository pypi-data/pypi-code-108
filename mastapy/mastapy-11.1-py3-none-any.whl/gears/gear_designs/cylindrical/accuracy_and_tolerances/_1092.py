'''_1092.py

ISO1328AccuracyGrades
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical.accuracy_and_tolerances import _1087
from mastapy._internal.python_net import python_net_import

_ISO1328_ACCURACY_GRADES = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.AccuracyAndTolerances', 'ISO1328AccuracyGrades')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO1328AccuracyGrades',)


class ISO1328AccuracyGrades(_1087.CylindricalAccuracyGrades):
    '''ISO1328AccuracyGrades

    This is a mastapy class.
    '''

    TYPE = _ISO1328_ACCURACY_GRADES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO1328AccuracyGrades.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def profile_iso_quality_grade(self) -> 'int':
        '''int: 'ProfileISOQualityGrade' is the original name of this property.'''

        return self.wrapped.ProfileISOQualityGrade

    @profile_iso_quality_grade.setter
    def profile_iso_quality_grade(self, value: 'int'):
        self.wrapped.ProfileISOQualityGrade = int(value) if value else 0

    @property
    def helix_iso_quality_grade(self) -> 'int':
        '''int: 'HelixISOQualityGrade' is the original name of this property.'''

        return self.wrapped.HelixISOQualityGrade

    @helix_iso_quality_grade.setter
    def helix_iso_quality_grade(self, value: 'int'):
        self.wrapped.HelixISOQualityGrade = int(value) if value else 0

    @property
    def pitch_iso_quality_grade(self) -> 'int':
        '''int: 'PitchISOQualityGrade' is the original name of this property.'''

        return self.wrapped.PitchISOQualityGrade

    @pitch_iso_quality_grade.setter
    def pitch_iso_quality_grade(self, value: 'int'):
        self.wrapped.PitchISOQualityGrade = int(value) if value else 0

    @property
    def radial_iso_quality_grade(self) -> 'int':
        '''int: 'RadialISOQualityGrade' is the original name of this property.'''

        return self.wrapped.RadialISOQualityGrade

    @radial_iso_quality_grade.setter
    def radial_iso_quality_grade(self, value: 'int'):
        self.wrapped.RadialISOQualityGrade = int(value) if value else 0
