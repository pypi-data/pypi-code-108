from cnvrgv2.config.error_messages import SERIES_NOT_A_LIST, SERIES_NOT_A_HEATMAP, \
    SERIES_NOT_A_VALID_LIST, ONLY_HEATMAP_CAN_HAVE_GROUPS, BOTH_GROUP_AND_STEP
from cnvrgv2.errors import CnvrgArgumentsError
import numbers


# Chart types ENUM
class CHART_TYPES:
    LINE = "none"
    SCATTER = "scatter"
    BAR = "bar"
    HEATMAP = "heatmap"


# Helpers


# To use numpy lists and such without errors
def sanitize_list(lst):
    if hasattr(lst, 'tolist'):
        return lst.tolist()
    return lst


def create_series_data(Ys: list):
    y_values = sanitize_list(Ys)

    # If no data was sent, do nothing.
    if not y_values:
        return None
    return y_values


def check_heatmap_series(series, matrix_size):
    # Verifying data format is heatmap - tuples of the same length made of real numbers
    # for ex. [(1,2), (1,2)], [(1,2,3), (1,2,3)], etc.

    # Skip verifications on empty series
    if len(series) == 0:
        return

    if not isinstance(series[0], tuple):
        raise CnvrgArgumentsError(SERIES_NOT_A_HEATMAP)

    value_length = matrix_size

    for value in series:
        if (not isinstance(value, tuple)
                or not len(value) == value_length
                or not all(isinstance(n, numbers.Real) for n in value)):
            raise CnvrgArgumentsError(SERIES_NOT_A_HEATMAP)


# Charts
class Chart:
    def __init__(self, key, chart_type, **kwargs):
        """
        Represents a chart
        @param key: Identifier of the chart.
        @param chart_type: Type of the chart, from CHART_TYPES Enum.
        @param kwargs: additional arguments:
            title: chart title,
            group: chart group,
            step: data steps,
            x_axis: X axis custom title,
            y_axis: Y axis custom title,
            Ys / y_ticks: Y axis data, this is optional as user can add serieses later.
            Xs / x_ticks / bars: X axis custom ticks (X values that will correspond to Y values sent / bar names),
            series_name: Name of the initial series to be built (the series that's based on Ys & Xs)
            stops: list of color stops,
            max_val: max boundary for Y axis,
            min_val: min boundary for Y axis,
            colors: custom colors to use on each series
        """
        self.series_list = []
        self.chart_type = chart_type
        self.key = key
        self.kwargs = {
            **kwargs,
            'x_ticks': kwargs.get('Xs', None) or kwargs.get('bars', None) or kwargs.get('x_ticks', None),
            'min': kwargs.get('min_val', None),
            'max': kwargs.get('max_val', None)
        }

        # Make sure only heatmap can get group and step
        if chart_type != CHART_TYPES.HEATMAP and (self.kwargs.get('step', None) or self.kwargs.get('group', None)):
            raise CnvrgArgumentsError(ONLY_HEATMAP_CAN_HAVE_GROUPS)

        # Values for initial series or heatmap. This is optional. Users can add data manually later.
        init_matrix = self.kwargs.get('matrix', None)
        init_series_name = self.kwargs.get('series_name', None)
        if init_matrix:
            self.add_series(data=init_matrix, name=init_series_name)
        else:
            init_series_ys = self.kwargs.get('Ys', None)
            init_series_data = create_series_data(Ys=init_series_ys)
            self.add_series(data=init_series_data, name=init_series_name)

    def add_series(self, data, name=None):
        """
        Adds series to the chart
        @param data: list of data points.
        In case of regular charts, will be a list of numbers or Point objects.
        In case of bar charts, will only be a list of numbers.
        In case of Heatmap, list of tuples that form a matrix. e.g, 3x3 matrix: [(1,2,3),(4,5,6),(7,8,9)]
        @param name: name of the series
        @return: None
        """
        if not data:
            return

        formatted_data = self.validate_series(data)

        # If series already exists add new data to that series, else add the series
        existing_series = list(map(lambda series: series.get('name', None), self.series_list))
        if name in existing_series:
            index, current_series = next(series for series in enumerate(self.series_list) if series.name == name)
            current_series["data"].extend(current_series)
            self.series_list[index] = current_series
        else:
            self.series_list.append({
                "name": name,
                "data": formatted_data
            })

    def to_dict(self):
        """
        @return: The chart's attributes as dictionary
        """
        return {
            "chart_type": self.chart_type,
            "key": self.key,
            "series": self.series_list,
            **self.kwargs
        }

    def validate_series(self, series):
        """
        Validates series before adding to series_list.
        In base class, only verifies series is made of real numbers
        @param series: Series to convert
        @return: The series converted
        """
        if not isinstance(series, list):
            raise CnvrgArgumentsError(SERIES_NOT_A_LIST)

        if not all(isinstance(value, numbers.Real) for value in series):
            raise CnvrgArgumentsError(SERIES_NOT_A_VALID_LIST)
        return series


class Heatmap(Chart):
    def __init__(self, key, **kwargs):
        # Set Ys as y_ticks so user can use both
        y_ticks = kwargs.get('Ys', None) or kwargs.get('y_ticks', None)
        self.matrix_size = kwargs.get('matrix_size', None)
        self.matrix_last_pos = kwargs.get('matrix_last_pos', 0)
        formatted_kwargs = {**kwargs, 'y_ticks': y_ticks}

        # Validate group and step are always both available
        self.group = kwargs.get('group', None)
        self.step = kwargs.get('step', None)
        if (self.group and not self.step) or (self.step and not self.group):
            raise CnvrgArgumentsError(BOTH_GROUP_AND_STEP)

        super().__init__(key=key, chart_type=CHART_TYPES.HEATMAP, **formatted_kwargs)

    def _convert_series(self, series):
        matrix = []
        for i, y in enumerate(range(self.matrix_last_pos, self.matrix_last_pos + len(series))):
            for x in range(len(series[0])):
                matrix.append((x, y, series[i][x]))
        return matrix

    def validate_series(self, series):
        """
        Validates and converts series to heatmap format before adding to series_list.
        @param series: Series to convert
        @return: The series converted
        """

        if not isinstance(series, list):
            raise CnvrgArgumentsError(SERIES_NOT_A_LIST)

        # This means this a new matrix being created
        if not (self.matrix_size and self.matrix_size > 1):
            self.matrix_size = len(series[0])

        check_heatmap_series(series, self.matrix_size)
        return self._convert_series(series)


class BarChart(Chart):
    def __init__(self, key, **kwargs):
        super().__init__(key=key, chart_type=CHART_TYPES.BAR, **kwargs)


class ScatterPlot(Chart):
    def __init__(self, key, **kwargs):
        super().__init__(key=key, chart_type=CHART_TYPES.SCATTER, **kwargs)


class LineChart(Chart):
    def __init__(self, key, **kwargs):
        super().__init__(key=key, chart_type=CHART_TYPES.LINE, **kwargs)
