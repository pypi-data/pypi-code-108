'''_1616.py

DataLoggerWithCharts
'''


from mastapy.math_utility.convergence import _1372
from mastapy._internal.python_net import python_net_import

_DATA_LOGGER_WITH_CHARTS = python_net_import('SMT.MastaAPI.UtilityGUI', 'DataLoggerWithCharts')


__docformat__ = 'restructuredtext en'
__all__ = ('DataLoggerWithCharts',)


class DataLoggerWithCharts(_1372.DataLogger):
    '''DataLoggerWithCharts

    This is a mastapy class.
    '''

    TYPE = _DATA_LOGGER_WITH_CHARTS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DataLoggerWithCharts.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
