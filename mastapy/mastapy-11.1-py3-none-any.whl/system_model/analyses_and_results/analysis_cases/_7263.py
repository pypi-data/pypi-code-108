'''_7263.py

PartCompoundAnalysis
'''


from PIL.Image import Image

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.analysis_cases import _7260
from mastapy._internal.python_net import python_net_import

_PART_COMPOUND_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'PartCompoundAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PartCompoundAnalysis',)


class PartCompoundAnalysis(_7260.DesignEntityCompoundAnalysis):
    '''PartCompoundAnalysis

    This is a mastapy class.
    '''

    TYPE = _PART_COMPOUND_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PartCompoundAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def two_d_drawing(self) -> 'Image':
        '''Image: 'TwoDDrawing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.TwoDDrawing)
        return value
