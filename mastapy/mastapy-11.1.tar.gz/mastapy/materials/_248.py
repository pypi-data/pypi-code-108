'''_248.py

SafetyFactorItem
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SAFETY_FACTOR_ITEM = python_net_import('SMT.MastaAPI.Materials', 'SafetyFactorItem')


__docformat__ = 'restructuredtext en'
__all__ = ('SafetyFactorItem',)


class SafetyFactorItem(_0.APIBase):
    '''SafetyFactorItem

    This is a mastapy class.
    '''

    TYPE = _SAFETY_FACTOR_ITEM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SafetyFactorItem.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def description(self) -> 'str':
        '''str: 'Description' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Description

    @property
    def safety_factor(self) -> 'float':
        '''float: 'SafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactor

    @property
    def minimum_required_safety_factor(self) -> 'float':
        '''float: 'MinimumRequiredSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumRequiredSafetyFactor

    @property
    def reliability(self) -> 'float':
        '''float: 'Reliability' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Reliability

    @property
    def damage(self) -> 'float':
        '''float: 'Damage' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Damage

    @property
    def time_until_failure(self) -> 'float':
        '''float: 'TimeUntilFailure' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TimeUntilFailure
