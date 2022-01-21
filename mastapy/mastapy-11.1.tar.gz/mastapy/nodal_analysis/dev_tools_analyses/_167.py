'''_167.py

FEModelTransparencyDrawStyle
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_MODEL_TRANSPARENCY_DRAW_STYLE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'FEModelTransparencyDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('FEModelTransparencyDrawStyle',)


class FEModelTransparencyDrawStyle(_0.APIBase):
    '''FEModelTransparencyDrawStyle

    This is a mastapy class.
    '''

    TYPE = _FE_MODEL_TRANSPARENCY_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEModelTransparencyDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def show_fe3d_axes(self) -> 'bool':
        '''bool: 'ShowFE3DAxes' is the original name of this property.'''

        return self.wrapped.ShowFE3DAxes

    @show_fe3d_axes.setter
    def show_fe3d_axes(self, value: 'bool'):
        self.wrapped.ShowFE3DAxes = bool(value) if value else False
