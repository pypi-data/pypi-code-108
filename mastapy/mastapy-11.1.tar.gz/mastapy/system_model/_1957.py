'''_1957.py

IncludeDutyCycleOption
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_INCLUDE_DUTY_CYCLE_OPTION = python_net_import('SMT.MastaAPI.SystemModel', 'IncludeDutyCycleOption')


__docformat__ = 'restructuredtext en'
__all__ = ('IncludeDutyCycleOption',)


class IncludeDutyCycleOption(_0.APIBase):
    '''IncludeDutyCycleOption

    This is a mastapy class.
    '''

    TYPE = _INCLUDE_DUTY_CYCLE_OPTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'IncludeDutyCycleOption.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def import_(self) -> 'bool':
        '''bool: 'Import' is the original name of this property.'''

        return self.wrapped.Import

    @import_.setter
    def import_(self, value: 'bool'):
        self.wrapped.Import = bool(value) if value else False
