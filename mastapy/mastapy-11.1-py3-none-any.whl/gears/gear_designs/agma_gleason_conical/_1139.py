'''_1139.py

AGMAGleasonConicalAccuracyGrades
'''


from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.gears import _280
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_ACCURACY_GRADES = python_net_import('SMT.MastaAPI.Gears.GearDesigns.AGMAGleasonConical', 'AGMAGleasonConicalAccuracyGrades')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalAccuracyGrades',)


class AGMAGleasonConicalAccuracyGrades(_280.AccuracyGrades):
    '''AGMAGleasonConicalAccuracyGrades

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_ACCURACY_GRADES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalAccuracyGrades.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def single_pitch_deviation(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SinglePitchDeviation' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SinglePitchDeviation) if self.wrapped.SinglePitchDeviation is not None else None

    @single_pitch_deviation.setter
    def single_pitch_deviation(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.SinglePitchDeviation = value

    @property
    def agma_quality_grade_new(self) -> 'int':
        '''int: 'AGMAQualityGradeNew' is the original name of this property.'''

        return self.wrapped.AGMAQualityGradeNew

    @agma_quality_grade_new.setter
    def agma_quality_grade_new(self, value: 'int'):
        self.wrapped.AGMAQualityGradeNew = int(value) if value else 0

    @property
    def agma_quality_grade_old(self) -> 'int':
        '''int: 'AGMAQualityGradeOld' is the original name of this property.'''

        return self.wrapped.AGMAQualityGradeOld

    @agma_quality_grade_old.setter
    def agma_quality_grade_old(self, value: 'int'):
        self.wrapped.AGMAQualityGradeOld = int(value) if value else 0
