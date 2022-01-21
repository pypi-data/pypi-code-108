'''_1617.py

BubbleChartDefinition
'''


from mastapy.utility_gui.charts import _1623
from mastapy._internal.python_net import python_net_import

_BUBBLE_CHART_DEFINITION = python_net_import('SMT.MastaAPI.UtilityGUI.Charts', 'BubbleChartDefinition')


__docformat__ = 'restructuredtext en'
__all__ = ('BubbleChartDefinition',)


class BubbleChartDefinition(_1623.ScatterChartDefinition):
    '''BubbleChartDefinition

    This is a mastapy class.
    '''

    TYPE = _BUBBLE_CHART_DEFINITION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BubbleChartDefinition.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
