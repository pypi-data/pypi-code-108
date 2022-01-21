'''_1835.py

FrictionSources
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FRICTION_SOURCES = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule', 'FrictionSources')


__docformat__ = 'restructuredtext en'
__all__ = ('FrictionSources',)


class FrictionSources(_0.APIBase):
    '''FrictionSources

    This is a mastapy class.
    '''

    TYPE = _FRICTION_SOURCES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FrictionSources.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rolling(self) -> 'float':
        '''float: 'Rolling' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Rolling

    @property
    def sliding(self) -> 'float':
        '''float: 'Sliding' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Sliding

    @property
    def seals(self) -> 'float':
        '''float: 'Seals' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Seals

    @property
    def drag_loss(self) -> 'float':
        '''float: 'DragLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DragLoss
