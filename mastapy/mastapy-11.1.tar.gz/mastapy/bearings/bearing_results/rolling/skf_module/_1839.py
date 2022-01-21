'''_1839.py

InitialFill
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling.skf_module import _1846
from mastapy._internal.python_net import python_net_import

_INITIAL_FILL = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule', 'InitialFill')


__docformat__ = 'restructuredtext en'
__all__ = ('InitialFill',)


class InitialFill(_1846.SKFCalculationResult):
    '''InitialFill

    This is a mastapy class.
    '''

    TYPE = _INITIAL_FILL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InitialFill.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def side(self) -> 'float':
        '''float: 'Side' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Side

    @property
    def ring(self) -> 'float':
        '''float: 'Ring' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Ring
