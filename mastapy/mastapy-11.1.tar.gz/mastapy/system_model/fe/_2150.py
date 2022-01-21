'''_2150.py

ReplacedShaftSelectionHelper
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_REPLACED_SHAFT_SELECTION_HELPER = python_net_import('SMT.MastaAPI.SystemModel.FE', 'ReplacedShaftSelectionHelper')


__docformat__ = 'restructuredtext en'
__all__ = ('ReplacedShaftSelectionHelper',)


class ReplacedShaftSelectionHelper(_0.APIBase):
    '''ReplacedShaftSelectionHelper

    This is a mastapy class.
    '''

    TYPE = _REPLACED_SHAFT_SELECTION_HELPER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ReplacedShaftSelectionHelper.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def is_replaced_by_fe(self) -> 'bool':
        '''bool: 'IsReplacedByFE' is the original name of this property.'''

        return self.wrapped.IsReplacedByFE

    @is_replaced_by_fe.setter
    def is_replaced_by_fe(self, value: 'bool'):
        self.wrapped.IsReplacedByFE = bool(value) if value else False
