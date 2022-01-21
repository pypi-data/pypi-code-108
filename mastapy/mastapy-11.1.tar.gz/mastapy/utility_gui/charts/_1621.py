'''_1621.py

NDChartDefinition
'''


from mastapy._internal import constructor
from mastapy.utility.report import _1523
from mastapy._internal.python_net import python_net_import

_ND_CHART_DEFINITION = python_net_import('SMT.MastaAPI.UtilityGUI.Charts', 'NDChartDefinition')


__docformat__ = 'restructuredtext en'
__all__ = ('NDChartDefinition',)


class NDChartDefinition(_1523.ChartDefinition):
    '''NDChartDefinition

    This is a mastapy class.
    '''

    TYPE = _ND_CHART_DEFINITION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'NDChartDefinition.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def specify_shared_chart_settings(self) -> 'bool':
        '''bool: 'SpecifySharedChartSettings' is the original name of this property.'''

        return self.wrapped.SpecifySharedChartSettings

    @specify_shared_chart_settings.setter
    def specify_shared_chart_settings(self, value: 'bool'):
        self.wrapped.SpecifySharedChartSettings = bool(value) if value else False
