'''_1380.py

FileHistoryItem
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FILE_HISTORY_ITEM = python_net_import('SMT.MastaAPI.Utility', 'FileHistoryItem')


__docformat__ = 'restructuredtext en'
__all__ = ('FileHistoryItem',)


class FileHistoryItem(_0.APIBase):
    '''FileHistoryItem

    This is a mastapy class.
    '''

    TYPE = _FILE_HISTORY_ITEM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FileHistoryItem.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def save_date(self) -> 'str':
        '''str: 'SaveDate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SaveDate

    @property
    def save_date_and_age(self) -> 'str':
        '''str: 'SaveDateAndAge' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SaveDateAndAge

    @property
    def user_name(self) -> 'str':
        '''str: 'UserName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UserName

    @property
    def comment(self) -> 'str':
        '''str: 'Comment' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Comment

    @property
    def version(self) -> 'str':
        '''str: 'Version' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Version

    @property
    def hash_code(self) -> 'str':
        '''str: 'HashCode' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HashCode

    @property
    def licence_id(self) -> 'str':
        '''str: 'LicenceID' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LicenceID
