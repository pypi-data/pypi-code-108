'''_6045.py

DynamicAnalysisDrawStyle
'''


from mastapy._internal import constructor
from mastapy.system_model.drawing import _1987
from mastapy._internal.python_net import python_net_import

_DYNAMIC_ANALYSIS_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses', 'DynamicAnalysisDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicAnalysisDrawStyle',)


class DynamicAnalysisDrawStyle(_1987.ContourDrawStyle):
    '''DynamicAnalysisDrawStyle

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_ANALYSIS_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicAnalysisDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def animate_contour(self) -> 'bool':
        '''bool: 'AnimateContour' is the original name of this property.'''

        return self.wrapped.AnimateContour

    @animate_contour.setter
    def animate_contour(self, value: 'bool'):
        self.wrapped.AnimateContour = bool(value) if value else False
