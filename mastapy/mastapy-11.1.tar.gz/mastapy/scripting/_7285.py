'''_7285.py

ScriptingExecutionCommand
'''


from mastapy._internal import constructor
from mastapy.scripting import _7284
from mastapy._internal.python_net import python_net_import

_SCRIPTING_EXECUTION_COMMAND = python_net_import('SMT.MastaAPIUtility.Scripting', 'ScriptingExecutionCommand')


__docformat__ = 'restructuredtext en'
__all__ = ('ScriptingExecutionCommand',)


class ScriptingExecutionCommand(_7284.ScriptingCommand):
    '''ScriptingExecutionCommand

    This is a mastapy class.
    '''

    TYPE = _SCRIPTING_EXECUTION_COMMAND

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ScriptingExecutionCommand.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def execute(self):
        ''' 'Execute' is the original name of this method.'''

        self.wrapped.Execute()
