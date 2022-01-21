'''_1342.py

OptimisationHistory
'''


from typing import List

from mastapy.math_utility.optimisation import _1344
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_OPTIMISATION_HISTORY = python_net_import('SMT.MastaAPI.MathUtility.Optimisation', 'OptimisationHistory')


__docformat__ = 'restructuredtext en'
__all__ = ('OptimisationHistory',)


class OptimisationHistory(_0.APIBase):
    '''OptimisationHistory

    This is a mastapy class.
    '''

    TYPE = _OPTIMISATION_HISTORY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'OptimisationHistory.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def input_history(self) -> 'List[_1344.OptimizationVariable]':
        '''List[OptimizationVariable]: 'InputHistory' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.InputHistory, constructor.new(_1344.OptimizationVariable))
        return value

    @property
    def target_history(self) -> 'List[_1344.OptimizationVariable]':
        '''List[OptimizationVariable]: 'TargetHistory' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TargetHistory, constructor.new(_1344.OptimizationVariable))
        return value

    @property
    def input_names(self) -> 'List[str]':
        '''List[str]: 'InputNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.InputNames, str)
        return value

    @property
    def target_names(self) -> 'List[str]':
        '''List[str]: 'TargetNames' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.TargetNames, str)
        return value

    def add_input_history(self, value: '_1344.OptimizationVariable'):
        ''' 'AddInputHistory' is the original name of this method.

        Args:
            value (mastapy.math_utility.optimisation.OptimizationVariable)
        '''

        self.wrapped.AddInputHistory(value.wrapped if value else None)

    def add_target_history(self, value: '_1344.OptimizationVariable'):
        ''' 'AddTargetHistory' is the original name of this method.

        Args:
            value (mastapy.math_utility.optimisation.OptimizationVariable)
        '''

        self.wrapped.AddTargetHistory(value.wrapped if value else None)
