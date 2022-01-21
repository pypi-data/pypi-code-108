'''_2324.py

CouplingHalf
'''


from mastapy._internal import constructor
from mastapy.system_model.part_model import _2205
from mastapy._internal.python_net import python_net_import

_COUPLING_HALF = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'CouplingHalf')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingHalf',)


class CouplingHalf(_2205.MountableComponent):
    '''CouplingHalf

    This is a mastapy class.
    '''

    TYPE = _COUPLING_HALF

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingHalf.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def diameter(self) -> 'float':
        '''float: 'Diameter' is the original name of this property.'''

        return self.wrapped.Diameter

    @diameter.setter
    def diameter(self, value: 'float'):
        self.wrapped.Diameter = float(value) if value else 0.0

    @property
    def width(self) -> 'float':
        '''float: 'Width' is the original name of this property.'''

        return self.wrapped.Width

    @width.setter
    def width(self, value: 'float'):
        self.wrapped.Width = float(value) if value else 0.0

    @property
    def bore(self) -> 'float':
        '''float: 'Bore' is the original name of this property.'''

        return self.wrapped.Bore

    @bore.setter
    def bore(self, value: 'float'):
        self.wrapped.Bore = float(value) if value else 0.0
