'''_5.py

Versioning
'''


from mastapy._internal import constructor
from mastapy._internal.class_property import classproperty
from mastapy._internal.python_net import python_net_import

_VERSIONING = python_net_import('SMT.MastaAPI', 'Versioning')


__docformat__ = 'restructuredtext en'
__all__ = ('Versioning',)


class Versioning:
    '''Versioning

    This is a mastapy class.
    '''

    TYPE = _VERSIONING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Versioning.TYPE'):
        self.wrapped = instance_to_wrap

    @classproperty
    def api_release_version_string(cls) -> 'str':
        '''str: 'APIReleaseVersionString' is the original name of this property.'''

        return Versioning.TYPE.APIReleaseVersionString

    @classproperty
    def masta_version_string(cls) -> 'str':
        '''str: 'MastaVersionString' is the original name of this property.'''

        return Versioning.TYPE.MastaVersionString

    @classproperty
    def is_backwards_compatible_case(cls) -> 'bool':
        '''bool: 'IsBackwardsCompatibleCase' is the original name of this property.'''

        return Versioning.TYPE.IsBackwardsCompatibleCase
