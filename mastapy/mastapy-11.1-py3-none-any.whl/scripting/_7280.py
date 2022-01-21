'''_7280.py

SMTBitmap
'''


from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_SMT_BITMAP = python_net_import('SMT.MastaAPIUtility.Scripting', 'SMTBitmap')


__docformat__ = 'restructuredtext en'
__all__ = ('SMTBitmap',)


class SMTBitmap:
    '''SMTBitmap

    This is a mastapy class.
    '''

    TYPE = _SMT_BITMAP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SMTBitmap.TYPE'):
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

    def to_image(self) -> 'Image':
        ''' 'ToImage' is the original name of this method.

        Returns:
            Image
        '''

        return conversion.pn_to_mp_image(self.wrapped.ToImage())

    def to_bytes(self) -> 'bytes':
        ''' 'ToBytes' is the original name of this method.

        Returns:
            bytes
        '''

        return conversion.pn_to_mp_bytes(self.wrapped.ToBytes())

    def initialize_lifetime_service(self) -> 'object':
        ''' 'InitializeLifetimeService' is the original name of this method.

        Returns:
            object
        '''

        method_result = self.wrapped.InitializeLifetimeService()
        return method_result
