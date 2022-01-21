'''_7271.py

EnvironmentVariableUtility
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_ENVIRONMENT_VARIABLE_UTILITY = python_net_import('SMT.MastaAPIUtility', 'EnvironmentVariableUtility')


__docformat__ = 'restructuredtext en'
__all__ = ('EnvironmentVariableUtility',)


class EnvironmentVariableUtility:
    '''EnvironmentVariableUtility

    This is a mastapy class.
    '''

    TYPE = _ENVIRONMENT_VARIABLE_UTILITY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'EnvironmentVariableUtility.TYPE'):
        self.wrapped = instance_to_wrap

    @staticmethod
    def add_to_path_if_necessary(directory: 'str'):
        ''' 'AddToPathIfNecessary' is the original name of this method.

        Args:
            directory (str)
        '''

        directory = str(directory)
        EnvironmentVariableUtility.TYPE.AddToPathIfNecessary(directory if directory else '')
