from . import builders
from . import styles
from . import utils
from . import models

# --- SHORTCUTS ---------------------------------------------------------------

GroupedVisualisations = builders.GroupedVisualisations
StrataFactory = utils.StrataFactory
Measures = models.Measures


# --- SIMPLE CHARTS -----------------------------------------------------------


class ScatterPlotVisualisation(builders.BaseAxesVisualisation, styles.ScatterMixin):
    """Scatter plot for VRS"""
    pass


class PieVisualisation(builders.BasePropVisualisation, styles.PieMixin):
    """Pie Chart for VRS"""
    pass


class DonutVisualisation(builders.BasePropVisualisation, styles.DonutMixin):
    """Donut Chart for VRS"""
    pass


class BarVisualisation(builders.BaseAxesVisualisation, styles.BarMixin):
    """Bar Chart for VRS"""
    pass


class BarStackVisualisation(builders.BaseAxesVisualisation, styles.BarStackMixin):
    """Stacked Bar Chart for VRS"""
    pass


class RelativeBarStackVisualisation(builders.BaseAxesVisualisation, styles.RelativeBarStackMixin):
    """Relative Stacked Bar Chart for VRS"""
    pass


class MultiLineVisualisation(builders.BaseAxesVisualisation, styles.MultiLineMixin):
    """MultiLine Chart for VRS"""
    pass


class MultiSteppedLineVisualisation(builders.BaseAxesVisualisation, styles.MultiSteppedLineMixin):
    """MultiLine Chart for VRS"""
    pass


class FallenTreePlotVisualisation(builders.BaseAxesVisualisation, styles.FallenTreePlotMixin):
    """MultiLine Fallen Tree Plot Chart for VRS"""
    pass


class MultiChartAxesVisualisation(builders.BaseAxesVisualisation, styles.BarMixin):
    """Multi Chart (Bar and Line) for VRS"""
    extra_charts = [styles.MultiLineMixin]


class ForestPlotVisualisation(builders.BaseAxesArrayVisualisation, styles.ForestMixin):
    """Forest Plot Visualisation"""
    pass


class BoxPlotVisualisation(builders.BaseAxesVisualisation, styles.BoxMixin):
    pass


class HeatmapPlotVisualisation(builders.BaseAxesVisualisation, styles.HeatmapMixin):
    pass


class ViolinPlotVisualisation(builders.BaseAxesVisualisation, styles.ViolinMixin):
    pass


class SubplotVisualisation(builders.BaseAxesVisualisation, styles.SubplotMixin):
    pass


class PhewasPlotVisualisation(builders.PhewasVisualisation, styles.ForestMixin):
    pass

# --- STRATIFIED CHARTS -------------------------------------------------------


class BarStratifiedVisualisation(builders.BaseStratifiedVisualisation, styles.BarMixin):
    """Bar Stratified Chart for VRS"""
    pass


class BarStackStratifiedVisualisation(builders.BaseStratifiedVisualisation, styles.BarStackMixin):
    """Stacked Bar Stratified Chart for VRS"""
    pass


class RelativeBarStackStratifiedVisualisation(builders.BaseStratifiedVisualisation, styles.RelativeBarStackMixin):
    """Stacked Bar Stratified Chart for VRS"""
    pass


class MultiLineStratifiedVisualisation(builders.BaseStratifiedVisualisation, styles.MultiLineMixin):
    """MultiLine Stratified Chart for VRS"""
    pass


class MultiSteppedLineStratifiedVisualisation(builders.BaseStratifiedVisualisation, styles.MultiSteppedLineMixin):
    """MultiLine Stratified Chart for VRS"""
    pass


class MultiStraightLineStratifiedVisualisation(builders.BaseStratifiedVisualisation, styles.MultiStraightLineMixin):
    """MultiLine Stratified Chart for VRS"""
    pass


class FallenTreePlotStratifiedVisualisation(builders.BaseStratifiedVisualisation, styles.FallenTreePlotMixin):
    """
    UNTESTED!
    MultiLine Fallen Tree Plote Stratified Chart for VRS
    """
    pass


class WaterfallStratifiedVisualisation(builders.BaseMeasureStratifiedVisualisation, styles.WaterfallMixin):
    """
    Waterfall Stratified Chart for VRS
    """
    pass


class ForestStratifiedVisualisation(builders.BaseAxesArrayStratifiedVisualisation, styles.ForestMixin):
    pass


# --- DATA TABLES -------------------------------------------------------------

class TableVisualisation(builders.BaseTableVisualisation, styles.TableMixin):
    """Data table for VRS"""
    pass


class TableStratifiedVisualisation(builders.BaseStratifiedTableVisualisation, styles.TableMixin):
    """Stratified data table for VRS"""
    pass


# --- SPECIAL CHARTS ----------------------------------------------------------

class SankeyVisualisation(builders.BaseLinkVisualisation, styles.SankeyMixin):
    """Sankey Chart for VRS"""
    pass


class StaticSankeyVisualisation(builders.BaseLinkVisualisation, styles.StaticSankeyMixin):
    """Static Sankey Chart for VRS without horizontal/vertical flip"""
    pass


class SunburstVisualisation(builders.BasePropParentVisualisation, styles.SunburstMixin):
    """Sunburst Chart for VRS"""
    pass


class WaterfallVisualisation(builders.BaseMeasureVisualisation, styles.WaterfallMixin):
    """Waterfall Chart for VRS"""
    pass
