'''_3854.py

PowerFlowDrawStyle
'''


from mastapy._internal import constructor
from mastapy.geometry import _275
from mastapy._internal.python_net import python_net_import

_POWER_FLOW_DRAW_STYLE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows', 'PowerFlowDrawStyle')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerFlowDrawStyle',)


class PowerFlowDrawStyle(_275.DrawStyle):
    '''PowerFlowDrawStyle

    This is a mastapy class.
    '''

    TYPE = _POWER_FLOW_DRAW_STYLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerFlowDrawStyle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def colour_loaded_flanks(self) -> 'bool':
        '''bool: 'ColourLoadedFlanks' is the original name of this property.'''

        return self.wrapped.ColourLoadedFlanks

    @colour_loaded_flanks.setter
    def colour_loaded_flanks(self, value: 'bool'):
        self.wrapped.ColourLoadedFlanks = bool(value) if value else False
