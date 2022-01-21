'''_1598.py

NamedKey
'''


from mastapy._internal import constructor
from mastapy.utility.databases import _1594
from mastapy._internal.python_net import python_net_import

_NAMED_KEY = python_net_import('SMT.MastaAPI.Utility.Databases', 'NamedKey')


__docformat__ = 'restructuredtext en'
__all__ = ('NamedKey',)


class NamedKey(_1594.DatabaseKey):
    '''NamedKey

    This is a mastapy class.
    '''

    TYPE = _NAMED_KEY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NamedKey.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''
