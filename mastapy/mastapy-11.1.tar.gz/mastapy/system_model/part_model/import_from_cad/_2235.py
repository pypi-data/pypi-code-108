'''_2235.py

ComponentFromCAD
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_COMPONENT_FROM_CAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD', 'ComponentFromCAD')


__docformat__ = 'restructuredtext en'
__all__ = ('ComponentFromCAD',)


class ComponentFromCAD(_0.APIBase):
    '''ComponentFromCAD

    This is a mastapy class.
    '''

    TYPE = _COMPONENT_FROM_CAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ComponentFromCAD.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.'''

        return self.wrapped.Name

    @name.setter
    def name(self, value: 'str'):
        self.wrapped.Name = str(value) if value else ''
