'''_1241.py

KeywayHalfRating
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_KEYWAY_HALF_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.KeyedJoints.Rating', 'KeywayHalfRating')


__docformat__ = 'restructuredtext en'
__all__ = ('KeywayHalfRating',)


class KeywayHalfRating(_0.APIBase):
    '''KeywayHalfRating

    This is a mastapy class.
    '''

    TYPE = _KEYWAY_HALF_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KeywayHalfRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
