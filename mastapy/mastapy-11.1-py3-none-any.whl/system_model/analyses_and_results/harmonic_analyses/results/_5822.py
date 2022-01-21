'''_5822.py

ExcitationSourceSelectionBase
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_EXCITATION_SOURCE_SELECTION_BASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Results', 'ExcitationSourceSelectionBase')


__docformat__ = 'restructuredtext en'
__all__ = ('ExcitationSourceSelectionBase',)


class ExcitationSourceSelectionBase(_0.APIBase):
    '''ExcitationSourceSelectionBase

    This is a mastapy class.
    '''

    TYPE = _EXCITATION_SOURCE_SELECTION_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExcitationSourceSelectionBase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def included(self) -> 'bool':
        '''bool: 'Included' is the original name of this property.'''

        return self.wrapped.Included

    @included.setter
    def included(self, value: 'bool'):
        self.wrapped.Included = bool(value) if value else False
