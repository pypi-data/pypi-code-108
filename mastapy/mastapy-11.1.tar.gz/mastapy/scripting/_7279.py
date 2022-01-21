'''_7279.py

ApiVersion
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_API_VERSION = python_net_import('SMT.MastaAPIUtility.Scripting', 'ApiVersion')


__docformat__ = 'restructuredtext en'
__all__ = ('ApiVersion',)


class ApiVersion:
    '''ApiVersion

    This is a mastapy class.
    '''

    TYPE = _API_VERSION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ApiVersion.TYPE'):
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
    def file_name(self) -> 'str':
        '''str: 'FileName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FileName

    @property
    def assembly_name(self) -> 'str':
        '''str: 'AssemblyName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AssemblyName

    @property
    def assembly_name_without_version(self) -> 'str':
        '''str: 'AssemblyNameWithoutVersion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AssemblyNameWithoutVersion

    @property
    def file_path(self) -> 'str':
        '''str: 'FilePath' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FilePath

    def compare_to(self, other: 'ApiVersion') -> 'int':
        ''' 'CompareTo' is the original name of this method.

        Args:
            other (mastapy.scripting.ApiVersion)

        Returns:
            int
        '''

        method_result = self.wrapped.CompareTo(other.wrapped if other else None)
        return method_result

    def to_string(self) -> 'str':
        ''' 'ToString' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.ToString()
        return method_result
