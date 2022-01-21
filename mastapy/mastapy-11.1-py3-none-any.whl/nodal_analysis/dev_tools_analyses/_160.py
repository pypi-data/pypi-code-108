'''_160.py

FEModelComponentDrawStyle
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_MODEL_COMPONENT_DRAW_STYLE = python_net_import('SMT.MastaAPI.NodalAnalysis.DevToolsAnalyses', 'FEModelComponentDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('FEModelComponentDrawStyle',)


class FEModelComponentDrawStyle(_0.APIBase):
    '''FEModelComponentDrawStyle

    This is a mastapy class.
    '''

    TYPE = _FE_MODEL_COMPONENT_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FEModelComponentDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connectable_components(self) -> 'bool':
        '''bool: 'ConnectableComponents' is the original name of this property.'''

        return self.wrapped.ConnectableComponents

    @connectable_components.setter
    def connectable_components(self, value: 'bool'):
        self.wrapped.ConnectableComponents = bool(value) if value else False

    @property
    def solid_shafts(self) -> 'bool':
        '''bool: 'SolidShafts' is the original name of this property.'''

        return self.wrapped.SolidShafts

    @solid_shafts.setter
    def solid_shafts(self, value: 'bool'):
        self.wrapped.SolidShafts = bool(value) if value else False

    @property
    def solid_components(self) -> 'bool':
        '''bool: 'SolidComponents' is the original name of this property.'''

        return self.wrapped.SolidComponents

    @solid_components.setter
    def solid_components(self, value: 'bool'):
        self.wrapped.SolidComponents = bool(value) if value else False

    @property
    def transparent_model(self) -> 'bool':
        '''bool: 'TransparentModel' is the original name of this property.'''

        return self.wrapped.TransparentModel

    @transparent_model.setter
    def transparent_model(self, value: 'bool'):
        self.wrapped.TransparentModel = bool(value) if value else False
