'''_334.py

SafetyFactorResults
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SAFETY_FACTOR_RESULTS = python_net_import('SMT.MastaAPI.Gears.Rating', 'SafetyFactorResults')


__docformat__ = 'restructuredtext en'
__all__ = ('SafetyFactorResults',)


class SafetyFactorResults(_0.APIBase):
    '''SafetyFactorResults

    This is a mastapy class.
    '''

    TYPE = _SAFETY_FACTOR_RESULTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SafetyFactorResults.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def safety_factor(self) -> 'float':
        '''float: 'SafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactor

    @property
    def fatigue_safety_factor(self) -> 'float':
        '''float: 'FatigueSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueSafetyFactor

    @property
    def static_safety_factor(self) -> 'float':
        '''float: 'StaticSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticSafetyFactor

    @property
    def fatigue_bending_safety_factor(self) -> 'float':
        '''float: 'FatigueBendingSafetyFactor' is the original name of this property.'''

        return self.wrapped.FatigueBendingSafetyFactor

    @fatigue_bending_safety_factor.setter
    def fatigue_bending_safety_factor(self, value: 'float'):
        self.wrapped.FatigueBendingSafetyFactor = float(value) if value else 0.0

    @property
    def fatigue_contact_safety_factor(self) -> 'float':
        '''float: 'FatigueContactSafetyFactor' is the original name of this property.'''

        return self.wrapped.FatigueContactSafetyFactor

    @fatigue_contact_safety_factor.setter
    def fatigue_contact_safety_factor(self, value: 'float'):
        self.wrapped.FatigueContactSafetyFactor = float(value) if value else 0.0

    @property
    def static_bending_safety_factor(self) -> 'float':
        '''float: 'StaticBendingSafetyFactor' is the original name of this property.'''

        return self.wrapped.StaticBendingSafetyFactor

    @static_bending_safety_factor.setter
    def static_bending_safety_factor(self, value: 'float'):
        self.wrapped.StaticBendingSafetyFactor = float(value) if value else 0.0

    @property
    def static_contact_safety_factor(self) -> 'float':
        '''float: 'StaticContactSafetyFactor' is the original name of this property.'''

        return self.wrapped.StaticContactSafetyFactor

    @static_contact_safety_factor.setter
    def static_contact_safety_factor(self, value: 'float'):
        self.wrapped.StaticContactSafetyFactor = float(value) if value else 0.0
