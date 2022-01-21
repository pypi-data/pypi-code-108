'''_1562.py

Fix
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FIX = python_net_import('SMT.MastaAPI.Utility.ModelValidation', 'Fix')


__docformat__ = 'restructuredtext en'
__all__ = ('Fix',)


class Fix(_0.APIBase):
    '''Fix

    This is a mastapy class.
    '''

    TYPE = _FIX

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Fix.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def description(self) -> 'str':
        '''str: 'Description' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Description

    def perform(self):
        ''' 'Perform' is the original name of this method.'''

        self.wrapped.Perform()
