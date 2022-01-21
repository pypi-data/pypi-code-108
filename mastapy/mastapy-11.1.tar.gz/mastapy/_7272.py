'''_7272.py

Remoting
'''


from typing import Iterable, Optional

from mastapy._internal import constructor, conversion
from mastapy._internal.class_property import classproperty
from mastapy._internal.python_net import python_net_import

_REMOTING = python_net_import('SMT.MastaAPIUtility', 'Remoting')


__docformat__ = 'restructuredtext en'
__all__ = ('Remoting',)


class Remoting:
    '''Remoting

    This is a mastapy class.
    '''

    TYPE = _REMOTING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Remoting.TYPE'):
        self.wrapped = instance_to_wrap

    @classproperty
    def masta_processes(cls) -> 'Iterable[int]':
        '''Iterable[int]: 'MastaProcesses' is the original name of this property.'''

        value = conversion.pn_to_mp_objects_in_iterable(Remoting.TYPE.MastaProcesses, int)
        return value

    @classproperty
    def remote_identifier(cls) -> 'str':
        '''str: 'RemoteIdentifier' is the original name of this property.'''

        return Remoting.TYPE.RemoteIdentifier

    @staticmethod
    def initialise(process_id: 'int'):
        ''' 'Initialise' is the original name of this method.

        Args:
            process_id (int)
        '''

        process_id = int(process_id)
        Remoting.TYPE.Initialise(process_id if process_id else 0)

    @staticmethod
    def stop():
        ''' 'Stop' is the original name of this method.'''

        Remoting.TYPE.Stop()

    @staticmethod
    def url_for_process_id(process_id: 'int') -> 'str':
        ''' 'UrlForProcessId' is the original name of this method.

        Args:
            process_id (int)

        Returns:
            str
        '''

        process_id = int(process_id)
        method_result = Remoting.TYPE.UrlForProcessId(process_id if process_id else 0)
        return method_result

    @staticmethod
    def is_remoting(process_id: Optional['int'] = 0) -> 'bool':
        ''' 'IsRemoting' is the original name of this method.

        Args:
            process_id (int, optional)

        Returns:
            bool
        '''

        process_id = int(process_id)
        method_result = Remoting.TYPE.IsRemoting(process_id if process_id else 0)
        return method_result

    @staticmethod
    def remoting_port_name(process_id: 'int') -> 'str':
        ''' 'RemotingPortName' is the original name of this method.

        Args:
            process_id (int)

        Returns:
            str
        '''

        process_id = int(process_id)
        method_result = Remoting.TYPE.RemotingPortName(process_id if process_id else 0)
        return method_result

    @staticmethod
    def remoting_port_name_for_current_process() -> 'str':
        ''' 'RemotingPortNameForCurrentProcess' is the original name of this method.

        Returns:
            str
        '''

        method_result = Remoting.TYPE.RemotingPortNameForCurrentProcess()
        return method_result
