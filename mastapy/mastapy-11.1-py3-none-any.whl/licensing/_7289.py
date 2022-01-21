'''_7289.py

ModuleDetails
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_MODULE_DETAILS = python_net_import('SMT.MastaAPIUtility.Licensing', 'ModuleDetails')


__docformat__ = 'restructuredtext en'
__all__ = ('ModuleDetails',)


class ModuleDetails:
    '''ModuleDetails

    This is a mastapy class.
    '''

    TYPE = _MODULE_DETAILS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ModuleDetails.TYPE'):
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
    def is_licensed(self) -> 'bool':
        '''bool: 'IsLicensed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsLicensed

    @property
    def expiry_date(self) -> 'str':
        '''str: 'ExpiryDate' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ExpiryDate

    @property
    def user_count(self) -> 'str':
        '''str: 'UserCount' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.UserCount

    @property
    def maximum_users(self) -> 'int':
        '''int: 'MaximumUsers' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumUsers

    @property
    def code(self) -> 'str':
        '''str: 'Code' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Code

    @property
    def description(self) -> 'str':
        '''str: 'Description' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Description

    @property
    def scope(self) -> 'str':
        '''str: 'Scope' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Scope

    def to_string(self) -> 'str':
        ''' 'ToString' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.ToString()
        return method_result
