'''_5823.py

ExcitationSourceSelectionGroup
'''


from typing import List

from mastapy.system_model.analyses_and_results.harmonic_analyses.results import _5822
from mastapy._internal import constructor, conversion
from mastapy._internal.python_net import python_net_import

_EXCITATION_SOURCE_SELECTION_GROUP = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Results', 'ExcitationSourceSelectionGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('ExcitationSourceSelectionGroup',)


class ExcitationSourceSelectionGroup(_5822.ExcitationSourceSelectionBase):
    '''ExcitationSourceSelectionGroup

    This is a mastapy class.
    '''

    TYPE = _EXCITATION_SOURCE_SELECTION_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ExcitationSourceSelectionGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def sub_items(self) -> 'List[_5822.ExcitationSourceSelectionBase]':
        '''List[ExcitationSourceSelectionBase]: 'SubItems' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SubItems, constructor.new(_5822.ExcitationSourceSelectionBase))
        return value
