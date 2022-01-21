'''_1849.py

StaticSafetyFactors
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling.skf_module import _1846
from mastapy._internal.python_net import python_net_import

_STATIC_SAFETY_FACTORS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule', 'StaticSafetyFactors')


__docformat__ = 'restructuredtext en'
__all__ = ('StaticSafetyFactors',)


class StaticSafetyFactors(_1846.SKFCalculationResult):
    '''StaticSafetyFactors

    This is a mastapy class.
    '''

    TYPE = _STATIC_SAFETY_FACTORS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StaticSafetyFactors.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def equivalent_static_load(self) -> 'float':
        '''float: 'EquivalentStaticLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EquivalentStaticLoad

    @property
    def static_safety_factor(self) -> 'float':
        '''float: 'StaticSafetyFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StaticSafetyFactor
