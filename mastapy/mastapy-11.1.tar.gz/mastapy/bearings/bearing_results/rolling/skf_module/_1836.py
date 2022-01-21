'''_1836.py

Grease
'''


from mastapy._internal import constructor
from mastapy.bearings.bearing_results.rolling.skf_module import _1846
from mastapy._internal.python_net import python_net_import

_GREASE = python_net_import('SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule', 'Grease')


__docformat__ = 'restructuredtext en'
__all__ = ('Grease',)


class Grease(_1846.SKFCalculationResult):
    '''Grease

    This is a mastapy class.
    '''

    TYPE = _GREASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Grease.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def relubrication_interval(self) -> 'float':
        '''float: 'RelubricationInterval' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelubricationInterval

    @property
    def grease_life(self) -> 'float':
        '''float: 'GreaseLife' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GreaseLife
