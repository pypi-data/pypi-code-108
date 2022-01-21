from abc import ABC
from .common import ColorsNormal, ColorsNormalExt

# --- COLOURS FOR CHARTS ------------------------------------------------------

COLORS_25 = ["#e7d4eb", "#bfd7fc", "#ffe4bf", "#f7c8db", "#bff0c8", "#c3d5e2"]
COLORS_50 = ["#cfaad8", "#80aff8", "#ffc980", "#ef90b6", "#80e190", "#88aac5"]
COLORS_75 = ["#b67fc4", "#4087f5", "#ffae40", "#e75992", "#40d159", "#4c80a7"]
COLOR_SCALE = [[0, '#bfd7fc'], [0.25, '#c3d5e2'], [0.5, '#88aac5'], [0.75, '#4c80a7'], [1.0, '#10558a ']]
COLORS_NORMAL = ColorsNormal.to_list()


# --- MIXIN CLASSES FOR STYLING CHARTS ----------------------------------------

class BaseMixin(ABC):
    """
    Base class used for mixing chart attributes.
    Classes for assigning attributes under:
        - ChartMeta ("chart")
        - ChartDataMeta ("data")
        - LayoutMeta ("layout")
        - NodeMeta ("data:node")

    """
    COLORS = COLORS_75[:]

    class ChartMeta:
        type: str

    class ChartDataMeta:
        pass

    class LayoutMeta:
        pass

    class NodeMeta:
        pass

    class MarkerMeta:
        pass

    class AnnotationMeta:
        pass

    @staticmethod
    def _parse_meta(klass) -> dict:
        return {k: getattr(klass, k) for k in dir(klass) if not k.startswith('_')}

    @classmethod
    def chart_dict(cls) -> dict:
        return cls._parse_meta(cls.ChartMeta)

    @classmethod
    def chartdata_dict(cls) -> dict:
        return cls._parse_meta(cls.ChartDataMeta)

    @classmethod
    def layout_dict(cls) -> dict:
        return cls._parse_meta(cls.LayoutMeta)

    @classmethod
    def node_dict(cls) -> dict:
        return cls._parse_meta(cls.NodeMeta)

    @classmethod
    def marker_dict(cls) -> dict:
        return cls._parse_meta(cls.MarkerMeta)

    @classmethod
    def annotation_dict(cls) -> dict:
        return cls._parse_meta(cls.AnnotationMeta)


# --- CUSTOM CHART TYPES ------------------------------------------------------

class PieMixin(BaseMixin):
    class ChartMeta:
        type = 'pie'

    class ChartDataMeta:
        hoverinfo = 'name+x'
        textinfo = 'value'


class DonutMixin(PieMixin):
    class ChartDataMeta(PieMixin.ChartDataMeta):
        hole = 0.4


class BarMixin(BaseMixin):
    class ChartMeta:
        type = 'bar'

    class ChartDataMeta:
        hoverinfo = 'name+x+y'


class BarStackMixin(BarMixin):
    class LayoutMeta:
        barmode = 'stack'


class RelativeBarStackMixin(BarStackMixin):
    class LayoutMeta:
        barmode = 'relative'


class MultiLineMixin(BaseMixin):
    class ChartMeta:
        type = 'scatter'
        mode = 'lines'

    class ChartDataMeta:
        line = dict(shape='spline')
        hoverinfo = 'name+x'


class MultiSteppedLineMixin(MultiLineMixin):
    class ChartDataMeta(MultiLineMixin.ChartDataMeta):
        line = dict(shape='hv')


class MultiStraightLineMixin(MultiLineMixin):
    class ChartDataMeta(MultiLineMixin.ChartDataMeta):
        hoverinfo = 'name+x'
        line = dict(shape='linear')


class SankeyMixin(BaseMixin):
    COLORS_LINK = [*COLORS_25, *COLORS_50]
    COLORS_NODE = [*COLORS_75, *COLORS_NORMAL]

    class ChartMeta:
        type = 'sankey'

    class LayoutMeta:
        font = dict(size=12)
        updatemenus = [
            dict(
                y=1,
                buttons=[
                    dict(label='Horizontal', method='restyle', args=['orientation', 'h']),
                    dict(label='Vertical', method='restyle', args=['orientation', 'v'])
                ]
            )
        ]

    class NodeMeta:
        pad = 5
        thickness = 15
        line = dict(color=ColorsNormalExt.WHITE, width=0.5)
        # color = 'navy'

    class ChartDataMeta:
        domain = dict(x=[0, 1], y=[0, 1])
        orientation = 'h'
        arrangement = 'snap'
        valueformat = '.0f'
        textfont = dict(size=10)


class StaticSankeyMixin(SankeyMixin):

    class LayoutMeta:
        font = dict(size=12)


class SunburstMixin(BaseMixin):
    COLORS = [*COLORS_75, *COLORS_25, *COLORS_50]

    class ChartMeta:
        type = 'sunburst'

    class LayoutMeta:
        margin = dict(t=0, l=0, r=0, b=0)


class FallenTreePlotMixin(BaseMixin):
    class ChartMeta:
        type = 'scatter'

    class MarkerMeta:
        opacity = 1.0
        symbol = [141, 101, 141]

    class LayoutMeta:
        margin = {'l': 210}
        shapes = [
            {
                'x0': 0,
                'x1': 25,
                'y0': 0,
                'y1': 0,
                'line': {'color': ColorsNormalExt.BLACK, 'width': 1.5},
                'type': 'line',
                'yref': 'y',
                'layer': 'below'
            }
        ]
        yaxis = {'zeroline': False}
        xaxis = {'zeroline': False}


class WaterfallMixin(BaseMixin):
    class ChartMeta:
        type = 'waterfall'

    class ChartDataMeta:
        orientation = 'v'
        totals = {'marker': {'color': ColorsNormal.NAVY}}
        increasing = {'marker': {'color': ColorsNormal.GREEN}}
        decreasing = {'marker': {'color': ColorsNormal.RED}}
        showlegend = False

    class LayoutMeta:
        waterfallgroupgap = 0.5


class TableMixin(BaseMixin):
    class ChartMeta:
        type = 'table'

    class LayoutMeta:
        titlefont = dict(color=ColorsNormalExt.BLUE, size=20)


class ScatterMixin(BaseMixin):
    class ChartMeta:
        type = 'scatter'

    class ChartDataMeta:
        mode = "markers"


class ForestMixin(ScatterMixin):
    class LayoutMeta:
        yaxis = {'zeroline': False, 'visible': True, 'showline': True}
        xaxis = {'zeroline': False, 'visible': True, 'showline': True}


class BoxMixin(BaseMixin):
    class LayoutMeta:
        font = dict(size=12)

    class ChartMeta:
        type = 'box'


class HeatmapMixin(BaseMixin):

    class LayoutMeta:
        font = dict(size=12)

    class ChartMeta:
        type = 'heatmap'

    class ChartDataMeta:
        colorscale = COLOR_SCALE
        colorbar = dict(title=None)


class ViolinMixin(BaseMixin):
    class LayoutMeta:
        yaxis = {'zeroline': False, 'visible': True, 'showline': True}
        xaxis = {'zeroline': False, 'visible': True, 'showline': True}

    class ChartMeta:
        type = 'violin'

    class ChartDataMeta:
        box = {'visible': True}
        boxpoints = False
        meanline = {'visible': True}


class SubplotMixin(ForestMixin):
    class ChartDataMeta:
        mode = "line"
