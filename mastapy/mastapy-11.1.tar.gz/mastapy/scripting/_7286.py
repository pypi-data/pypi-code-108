'''_7286.py

ScriptingObjectCommand
'''


from typing import Generic, TypeVar

from mastapy._internal import constructor
from mastapy.scripting import _7284
from mastapy._internal.python_net import python_net_import

_SCRIPTING_OBJECT_COMMAND = python_net_import('SMT.MastaAPIUtility.Scripting', 'ScriptingObjectCommand')


__docformat__ = 'restructuredtext en'
__all__ = ('ScriptingObjectCommand',)


T = TypeVar('T', bound='object')


class ScriptingObjectCommand(_7284.ScriptingCommand, Generic[T]):
    '''ScriptingObjectCommand

    This is a mastapy class.

    Generic Types:
        T
    '''

    TYPE = _SCRIPTING_OBJECT_COMMAND

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ScriptingObjectCommand.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def execute(self):
        ''' 'Execute' is the original name of this method.'''

        self.wrapped.Execute()
