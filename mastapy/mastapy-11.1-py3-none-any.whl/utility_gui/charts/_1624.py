'''_1624.py

ThreeDChartDefinition
'''


from mastapy.math_utility import _1287
from mastapy._internal import constructor
from mastapy.math_utility.measured_ranges import _1364
from mastapy._internal.cast_exception import CastException
from mastapy.utility_gui.charts import _1621
from mastapy._internal.python_net import python_net_import

_THREE_D_CHART_DEFINITION = python_net_import('SMT.MastaAPI.UtilityGUI.Charts', 'ThreeDChartDefinition')


__docformat__ = 'restructuredtext en'
__all__ = ('ThreeDChartDefinition',)


class ThreeDChartDefinition(_1621.NDChartDefinition):
    '''ThreeDChartDefinition

    This is a mastapy class.
    '''

    TYPE = _THREE_D_CHART_DEFINITION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ThreeDChartDefinition.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def x_axis_range(self) -> '_1287.Range':
        '''Range: 'XAxisRange' is the original name of this property.'''

        if _1287.Range.TYPE not in self.wrapped.XAxisRange.__class__.__mro__:
            raise CastException('Failed to cast x_axis_range to Range. Expected: {}.'.format(self.wrapped.XAxisRange.__class__.__qualname__))

        return constructor.new_override(self.wrapped.XAxisRange.__class__)(self.wrapped.XAxisRange) if self.wrapped.XAxisRange is not None else None

    @x_axis_range.setter
    def x_axis_range(self, value: '_1287.Range'):
        value = value.wrapped if value else None
        self.wrapped.XAxisRange = value

    @property
    def y_axis_range(self) -> '_1287.Range':
        '''Range: 'YAxisRange' is the original name of this property.'''

        if _1287.Range.TYPE not in self.wrapped.YAxisRange.__class__.__mro__:
            raise CastException('Failed to cast y_axis_range to Range. Expected: {}.'.format(self.wrapped.YAxisRange.__class__.__qualname__))

        return constructor.new_override(self.wrapped.YAxisRange.__class__)(self.wrapped.YAxisRange) if self.wrapped.YAxisRange is not None else None

    @y_axis_range.setter
    def y_axis_range(self, value: '_1287.Range'):
        value = value.wrapped if value else None
        self.wrapped.YAxisRange = value

    @property
    def z_axis_range(self) -> '_1287.Range':
        '''Range: 'ZAxisRange' is the original name of this property.'''

        if _1287.Range.TYPE not in self.wrapped.ZAxisRange.__class__.__mro__:
            raise CastException('Failed to cast z_axis_range to Range. Expected: {}.'.format(self.wrapped.ZAxisRange.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ZAxisRange.__class__)(self.wrapped.ZAxisRange) if self.wrapped.ZAxisRange is not None else None

    @z_axis_range.setter
    def z_axis_range(self, value: '_1287.Range'):
        value = value.wrapped if value else None
        self.wrapped.ZAxisRange = value
