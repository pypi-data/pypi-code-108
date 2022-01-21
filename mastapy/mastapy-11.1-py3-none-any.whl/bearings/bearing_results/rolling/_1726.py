'''_1726.py

InternalClearance
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_INTERNAL_CLEARANCE = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling', 'InternalClearance')


__docformat__ = 'restructuredtext en'
__all__ = ('InternalClearance',)


class InternalClearance(_0.APIBase):
    '''InternalClearance

    This is a mastapy class.
    '''

    TYPE = _INTERNAL_CLEARANCE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InternalClearance.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def radial(self) -> 'float':
        '''float: 'Radial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Radial

    @property
    def axial(self) -> 'float':
        '''float: 'Axial' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Axial
