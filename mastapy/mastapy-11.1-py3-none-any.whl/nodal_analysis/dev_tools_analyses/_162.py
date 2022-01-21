'''_162.py

FEModelInstanceDrawStyle
'''


from mastapy.nodal_analysis.dev_tools_analyses import _153
from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_MODEL_INSTANCE_DRAW_STYLE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'FEModelInstanceDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('FEModelInstanceDrawStyle',)


class FEModelInstanceDrawStyle(_0.APIBase):
    '''FEModelInstanceDrawStyle

    This is a mastapy class.
    '''

    TYPE = _FE_MODEL_INSTANCE_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEModelInstanceDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def model_draw_style(self) -> '_153.DrawStyleForFE':
        '''DrawStyleForFE: 'ModelDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_153.DrawStyleForFE)(self.wrapped.ModelDrawStyle) if self.wrapped.ModelDrawStyle is not None else None
