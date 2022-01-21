'''_7283.py

PythonCommand
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy.scripting import _7284
from mastapy._internal.python_net import python_net_import

_PYTHON_COMMAND = python_net_import('SMT.MastaAPIUtility.Scripting', 'PythonCommand')


__docformat__ = 'restructuredtext en'
__all__ = ('PythonCommand',)


T = TypeVar('T')


class PythonCommand(_7284.ScriptingCommand, Generic[T]):
    '''PythonCommand

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _PYTHON_COMMAND

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PythonCommand.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def execute(self):
        ''' 'Execute' is the original name of this method.'''

        self.wrapped.Execute()
