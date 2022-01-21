'''_1841.py

MinimumLoad
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling.skf_module import _1846
from mastapy._internal.python_net import python_net_import

_MINIMUM_LOAD = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule', 'MinimumLoad')


__docformat__ = 'restructuredtext en'
__all__ = ('MinimumLoad',)


class MinimumLoad(_1846.SKFCalculationResult):
    '''MinimumLoad

    This is a mastapy class.
    '''

    TYPE = _MINIMUM_LOAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MinimumLoad.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def requirement_met(self) -> 'bool':
        '''bool: 'RequirementMet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RequirementMet
