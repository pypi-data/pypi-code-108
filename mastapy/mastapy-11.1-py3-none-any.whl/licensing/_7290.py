'''_7290.py

ModuleLicenceStatus
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_MODULE_LICENCE_STATUS = python_net_import('SMT.MastaAPIUtility.Licensing', 'ModuleLicenceStatus')


__docformat__ = 'restructuredtext en'
__all__ = ('ModuleLicenceStatus',)


class ModuleLicenceStatus:
    '''ModuleLicenceStatus

    This is a mastapy class.
    '''

    TYPE = _MODULE_LICENCE_STATUS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ModuleLicenceStatus.TYPE'):
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

    @property
    def module_code(self) -> 'str':
        '''str: 'ModuleCode' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModuleCode

    @property
    def module_name(self) -> 'str':
        '''str: 'ModuleName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModuleName

    @property
    def status(self) -> 'str':
        '''str: 'Status' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Status

    @property
    def is_licensed(self) -> 'bool':
        '''bool: 'IsLicensed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsLicensed

    def to_string(self) -> 'str':
        ''' 'ToString' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.ToString()
        return method_result
