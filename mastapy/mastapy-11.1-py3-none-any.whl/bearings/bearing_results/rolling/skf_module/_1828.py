'''_1828.py

BearingLoads
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling.skf_module import _1846
from mastapy._internal.python_net import python_net_import

_BEARING_LOADS = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule', 'BearingLoads')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingLoads',)


class BearingLoads(_1846.SKFCalculationResult):
    '''BearingLoads

    This is a mastapy class.
    '''

    TYPE = _BEARING_LOADS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingLoads.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def equivalent_dynamic_load(self) -> 'float':
        '''float: 'EquivalentDynamicLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EquivalentDynamicLoad

    @property
    def load_ratio(self) -> 'float':
        '''float: 'LoadRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadRatio
