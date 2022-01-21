'''_1270.py

BoltSection
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_BOLT_SECTION = python_net_import('SMT.MastaAPI.Bolts', 'BoltSection')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltSection',)


class BoltSection(_0.APIBase):
    '''BoltSection

    This is a mastapy class.
    '''

    TYPE = _BOLT_SECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltSection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.'''

        return self.wrapped.Length

    @length.setter
    def length(self, value: 'float'):
        self.wrapped.Length = float(value) if value else 0.0

    @property
    def diameter(self) -> 'float':
        '''float: 'Diameter' is the original name of this property.'''

        return self.wrapped.Diameter

    @diameter.setter
    def diameter(self, value: 'float'):
        self.wrapped.Diameter = float(value) if value else 0.0

    @property
    def inner_diameter(self) -> 'float':
        '''float: 'InnerDiameter' is the original name of this property.'''

        return self.wrapped.InnerDiameter

    @inner_diameter.setter
    def inner_diameter(self, value: 'float'):
        self.wrapped.InnerDiameter = float(value) if value else 0.0
