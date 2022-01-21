'''_5824.py

HarmonicSelection
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_HARMONIC_SELECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Results', 'HarmonicSelection')


__docformat__ = 'restructuredtext en'
__all__ = ('HarmonicSelection',)


class HarmonicSelection(_0.APIBase):
    '''HarmonicSelection

    This is a mastapy class.
    '''

    TYPE = _HARMONIC_SELECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'HarmonicSelection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def harmonic(self) -> 'int':
        '''int: 'Harmonic' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Harmonic

    @property
    def order(self) -> 'float':
        '''float: 'Order' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Order

    @property
    def included(self) -> 'bool':
        '''bool: 'Included' is the original name of this property.'''

        return self.wrapped.Included

    @included.setter
    def included(self, value: 'bool'):
        self.wrapped.Included = bool(value) if value else False

    @property
    def is_included_in_excitations(self) -> 'bool':
        '''bool: 'IsIncludedInExcitations' is the original name of this property.'''

        return self.wrapped.IsIncludedInExcitations

    @is_included_in_excitations.setter
    def is_included_in_excitations(self, value: 'bool'):
        self.wrapped.IsIncludedInExcitations = bool(value) if value else False
