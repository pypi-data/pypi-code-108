'''_7270.py

MarshalByRefObjects
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_MARSHAL_BY_REF_OBJECTS = python_net_import('SMT.MastaAPIUtility', 'MarshalByRefObjects')


__docformat__ = 'restructuredtext en'
__all__ = ('MarshalByRefObjects',)


class MarshalByRefObjects:
    '''MarshalByRefObjects

    This is a mastapy class.
    '''

    TYPE = _MARSHAL_BY_REF_OBJECTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MarshalByRefObjects.TYPE'):
        self.wrapped = instance_to_wrap

    @staticmethod
    def add(item: 'object'):
        ''' 'Add' is the original name of this method.

        Args:
            item (object)
        '''

        MarshalByRefObjects.TYPE.Add(item)

    @staticmethod
    def remove(item: 'object'):
        ''' 'Remove' is the original name of this method.

        Args:
            item (object)
        '''

        MarshalByRefObjects.TYPE.Remove(item)

    @staticmethod
    def disconnect(item: 'object'):
        ''' 'Disconnect' is the original name of this method.

        Args:
            item (object)
        '''

        MarshalByRefObjects.TYPE.Disconnect(item)

    @staticmethod
    def clear():
        ''' 'Clear' is the original name of this method.'''

        MarshalByRefObjects.TYPE.Clear()
