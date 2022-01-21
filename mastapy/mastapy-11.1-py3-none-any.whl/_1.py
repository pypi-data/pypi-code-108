'''_1.py

Initialiser
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_INITIALISER = python_net_import('SMT.MastaAPI', 'Initialiser')


__docformat__ = 'restructuredtext en'
__all__ = ('Initialiser',)


class Initialiser:
    '''Initialiser

    This is a mastapy class.
    '''

    TYPE = _INITIALISER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Initialiser.TYPE'):
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

    def initialise_api_access(self, installation_directory: 'str'):
        ''' 'InitialiseApiAccess' is the original name of this method.

        Args:
            installation_directory (str)
        '''

        installation_directory = str(installation_directory)
        self.wrapped.InitialiseApiAccess(installation_directory if installation_directory else '')
