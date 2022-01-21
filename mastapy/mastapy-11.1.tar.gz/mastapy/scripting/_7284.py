'''_7284.py

ScriptingCommand
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_SCRIPTING_COMMAND = python_net_import('SMT.MastaAPIUtility.Scripting', 'ScriptingCommand')


__docformat__ = 'restructuredtext en'
__all__ = ('ScriptingCommand',)


class ScriptingCommand:
    '''ScriptingCommand

    This is a mastapy class.
    '''

    TYPE = _SCRIPTING_COMMAND

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ScriptingCommand.TYPE'):
        self.wrapped = instance_to_wrap
        self._freeze()

    __frozen = False

    def __setattr__(self, attr, value):
        prop = getattr(self.__class__, attr, None)
        if isinstance(prop, property):
            prop.fset(self, value)
        else:
            if self.__frozen and attr not in self.__dict__:
                raise AttributeError((
                    'Attempted to set unknown '
                    'attribute: \'{}\''.format(attr))) from None

            super().__setattr__(attr, value)

    def __delattr__(self, name):
        raise AttributeError(
            'Cannot delete the attributes of a mastapy object.') from None

    def _freeze(self):
        self.__frozen = True

    def execute(self):
        ''' 'Execute' is the original name of this method.'''

        self.wrapped.Execute()

    def initialize_lifetime_service(self) -> 'object':
        ''' 'InitializeLifetimeService' is the original name of this method.

        Returns:
            object
        '''

        method_result = self.wrapped.InitializeLifetimeService()
        return method_result
