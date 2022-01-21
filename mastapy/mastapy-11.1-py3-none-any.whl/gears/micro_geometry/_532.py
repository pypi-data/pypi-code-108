'''_532.py

LeadModification
'''


from mastapy._internal import constructor
from mastapy.math_utility import _1333
from mastapy.gears.micro_geometry import _539
from mastapy._internal.python_net import python_net_import

_LEAD_MODIFICATION = python_net_import('SMT.MastaAPI.Gears.MicroGeometry', 'LeadModification')


__docformat__ = 'restructuredtext en'
__all__ = ('LeadModification',)


class LeadModification(_539.Modification):
    '''LeadModification

    This is a mastapy class.
    '''

    TYPE = _LEAD_MODIFICATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LeadModification.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def linear_relief(self) -> 'float':
        '''float: 'LinearRelief' is the original name of this property.'''

        return self.wrapped.LinearRelief

    @linear_relief.setter
    def linear_relief(self, value: 'float'):
        self.wrapped.LinearRelief = float(value) if value else 0.0

    @property
    def crowning_relief(self) -> 'float':
        '''float: 'CrowningRelief' is the original name of this property.'''

        return self.wrapped.CrowningRelief

    @crowning_relief.setter
    def crowning_relief(self, value: 'float'):
        self.wrapped.CrowningRelief = float(value) if value else 0.0

    @property
    def linear_left_relief(self) -> 'float':
        '''float: 'LinearLeftRelief' is the original name of this property.'''

        return self.wrapped.LinearLeftRelief

    @linear_left_relief.setter
    def linear_left_relief(self, value: 'float'):
        self.wrapped.LinearLeftRelief = float(value) if value else 0.0

    @property
    def start_of_linear_left_relief_factor(self) -> 'float':
        '''float: 'StartOfLinearLeftReliefFactor' is the original name of this property.'''

        return self.wrapped.StartOfLinearLeftReliefFactor

    @start_of_linear_left_relief_factor.setter
    def start_of_linear_left_relief_factor(self, value: 'float'):
        self.wrapped.StartOfLinearLeftReliefFactor = float(value) if value else 0.0

    @property
    def linear_right_relief(self) -> 'float':
        '''float: 'LinearRightRelief' is the original name of this property.'''

        return self.wrapped.LinearRightRelief

    @linear_right_relief.setter
    def linear_right_relief(self, value: 'float'):
        self.wrapped.LinearRightRelief = float(value) if value else 0.0

    @property
    def start_of_linear_right_relief_factor(self) -> 'float':
        '''float: 'StartOfLinearRightReliefFactor' is the original name of this property.'''

        return self.wrapped.StartOfLinearRightReliefFactor

    @start_of_linear_right_relief_factor.setter
    def start_of_linear_right_relief_factor(self, value: 'float'):
        self.wrapped.StartOfLinearRightReliefFactor = float(value) if value else 0.0

    @property
    def parabolic_left_relief(self) -> 'float':
        '''float: 'ParabolicLeftRelief' is the original name of this property.'''

        return self.wrapped.ParabolicLeftRelief

    @parabolic_left_relief.setter
    def parabolic_left_relief(self, value: 'float'):
        self.wrapped.ParabolicLeftRelief = float(value) if value else 0.0

    @property
    def start_of_parabolic_left_relief_factor(self) -> 'float':
        '''float: 'StartOfParabolicLeftReliefFactor' is the original name of this property.'''

        return self.wrapped.StartOfParabolicLeftReliefFactor

    @start_of_parabolic_left_relief_factor.setter
    def start_of_parabolic_left_relief_factor(self, value: 'float'):
        self.wrapped.StartOfParabolicLeftReliefFactor = float(value) if value else 0.0

    @property
    def parabolic_right_relief(self) -> 'float':
        '''float: 'ParabolicRightRelief' is the original name of this property.'''

        return self.wrapped.ParabolicRightRelief

    @parabolic_right_relief.setter
    def parabolic_right_relief(self, value: 'float'):
        self.wrapped.ParabolicRightRelief = float(value) if value else 0.0

    @property
    def start_of_parabolic_right_relief_factor(self) -> 'float':
        '''float: 'StartOfParabolicRightReliefFactor' is the original name of this property.'''

        return self.wrapped.StartOfParabolicRightReliefFactor

    @start_of_parabolic_right_relief_factor.setter
    def start_of_parabolic_right_relief_factor(self, value: 'float'):
        self.wrapped.StartOfParabolicRightReliefFactor = float(value) if value else 0.0

    @property
    def evaluation_left_limit_factor(self) -> 'float':
        '''float: 'EvaluationLeftLimitFactor' is the original name of this property.'''

        return self.wrapped.EvaluationLeftLimitFactor

    @evaluation_left_limit_factor.setter
    def evaluation_left_limit_factor(self, value: 'float'):
        self.wrapped.EvaluationLeftLimitFactor = float(value) if value else 0.0

    @property
    def evaluation_right_limit_factor(self) -> 'float':
        '''float: 'EvaluationRightLimitFactor' is the original name of this property.'''

        return self.wrapped.EvaluationRightLimitFactor

    @evaluation_right_limit_factor.setter
    def evaluation_right_limit_factor(self, value: 'float'):
        self.wrapped.EvaluationRightLimitFactor = float(value) if value else 0.0

    @property
    def use_measured_data(self) -> 'bool':
        '''bool: 'UseMeasuredData' is the original name of this property.'''

        return self.wrapped.UseMeasuredData

    @use_measured_data.setter
    def use_measured_data(self, value: 'bool'):
        self.wrapped.UseMeasuredData = bool(value) if value else False

    @property
    def measured_data(self) -> '_1333.Vector2DListAccessor':
        '''Vector2DListAccessor: 'MeasuredData' is the original name of this property.'''

        return constructor.new(_1333.Vector2DListAccessor)(self.wrapped.MeasuredData) if self.wrapped.MeasuredData is not None else None

    @measured_data.setter
    def measured_data(self, value: '_1333.Vector2DListAccessor'):
        value = value.wrapped if value else None
        self.wrapped.MeasuredData = value
