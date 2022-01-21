'''_1594.py

DatabaseKey
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_DATABASE_KEY = python_net_import('SMT.MastaAPI.Utility.Databases', 'DatabaseKey')


__docformat__ = 'restructuredtext en'
__all__ = ('DatabaseKey',)


class DatabaseKey(_0.APIBase):
    '''DatabaseKey

    This is a mastapy class.
    '''

    TYPE = _DATABASE_KEY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DatabaseKey.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
