'''_138.py

NodalEntity
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_NODAL_ENTITY = python_net_import('SMT.MastaAPI.NodalAnalysis.NodalEntities', 'NodalEntity')


__docformat__ = 'restructuredtext en'
__all__ = ('NodalEntity',)


class NodalEntity(_0.APIBase):
    '''NodalEntity

    This is a mastapy class.
    '''

    TYPE = _NODAL_ENTITY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NodalEntity.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
