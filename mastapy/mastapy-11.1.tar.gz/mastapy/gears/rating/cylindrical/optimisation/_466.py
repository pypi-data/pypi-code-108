'''_466.py

SafetyFactorOptimisationStepResultAngle
'''


from mastapy._internal import constructor
from mastapy.gears.rating.cylindrical.optimisation import _465
from mastapy._internal.python_net import python_net_import

_SAFETY_FACTOR_OPTIMISATION_STEP_RESULT_ANGLE = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.Optimisation', 'SafetyFactorOptimisationStepResultAngle')


__docformat__ = 'restructuredtext en'
__all__ = ('SafetyFactorOptimisationStepResultAngle',)


class SafetyFactorOptimisationStepResultAngle(_465.SafetyFactorOptimisationStepResult):
    '''SafetyFactorOptimisationStepResultAngle

    This is a mastapy class.
    '''

    TYPE = _SAFETY_FACTOR_OPTIMISATION_STEP_RESULT_ANGLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SafetyFactorOptimisationStepResultAngle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angle(self) -> 'float':
        '''float: 'Angle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Angle
