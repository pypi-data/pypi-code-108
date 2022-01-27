import abc
import numpy as np
import logging
from typing import List, Tuple, Any, Callable, Optional

import bokeh.models
import bokeh.models.markers
from shyft.time_series import TsVector, UtcPeriod, TimeAxis, statistics_property, utctime_now, Calendar
from shyft.dashboard.time_series.state import Quantity, UnitRegistry
from shyft.dashboard.time_series.bindable import Bindable
from shyft.dashboard.base.hashable import Hashable
from shyft.dashboard.time_series.data_utility import data_to_patch_values, calculate_dead_band_indices, convert_ts_to_plot_vectors
from shyft.dashboard.time_series.axes import YAxis
from shyft.dashboard.base.ports import States, StatePorts

VALID_LINE_STYLES = ['solid', 'dashed', 'dotted', 'dotdash', 'dashdot']


class RendererError(RuntimeError):
    pass


def to_bokeh_datetime_rep(t: np.ndarray) -> np.ndarray:
    """ for datetime axies bokeh uses ms, so we scale up time with 1000."""
    return t*1000.0


class BaseFigureRenderer(Bindable, Hashable):
    def __init__(self, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Base renderer class for all figure renderer

        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        Bindable.__init__(self)
        Hashable.__init__(self)

        self.logger = logger or logging.getLogger()
        self.do_log = self.logger.isEnabledFor(logging.DEBUG)
        self.view = None
        self.y_axis = None
        self.unit_registry = unit_registry
        self.time_zone = 'UTC'
        self._cal: Calendar = None  # corresponding to self.time_zone, used/updated in self.calendar
        self._min_y = np.nan
        self._max_y = np.nan
        self._bokeh_renderers = []
        self._ts_vector = None
        self.next_new_data_update_y_range = False

        self._state = States.ACTIVE
        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)

        self.notify_figure_y_range_update = notify_figure_y_range_update

    @property
    def calendar(self) -> Calendar:
        """ return Calendar of self.parent.parent, cached, side-effect self.time_zone== parent.parent.time_zone """
        if not self._cal or self.time_zone != self.parent.parent.time_zone:
            self.time_zone = self.parent.parent.time_zone
            self._cal = Calendar(self.time_zone)
        return self._cal

    @abc.abstractmethod
    def y_range(self, view_range: UtcPeriod) -> np.ndarray:
        """
        Returns an np.ndarray with min, and max y values for given view period
        """
        # pass

    def set_view(self, *, view: "shyft.dashboard.time_series.view.FigureView",
                 y_axis: YAxis) -> None:
        """ Set the view for this renderer """
        self.clear_view()
        self.view = view
        self.y_axis = y_axis
        # add callbacks
        self.view.on_change(obj=self, attr="visible", callback=self.visible_callback)
        self.view.on_change(obj=self, attr="color", callback=self.color_callback)
        # run child set view
        self.on_set_view()

    def on_set_view(self) -> None:
        """
        optional Set view method which can be used in the Child classes for specialised behaviour
        """
        # pass

    def clear_view(self):
        """ Resets the render instance, removing the viewer instance and clears the sources """
        self.reset_bokeh_data_source()
        if self.view:
            self.view.remove_all_callbacks(obj=self)
            self.view = None
            self.y_axis = None
        self._ts_vector = None

    def update_view_data(self, *, ts_vector: Quantity[TsVector]) -> None:
        """ Update Renderer with new data"""
        # Check if empty tsv
        if not ts_vector:
            self.reset_bokeh_data_source()
            self._ts_vector = None
            self.notify_figure_y_range_update()
            return
        update_y_range = False
        # Check if to y range needs to be updated
        if self.ts_vector is None or self.next_new_data_update_y_range:
            update_y_range = True
            self.next_new_data_update_y_range = False
        self._ts_vector = ts_vector
        if update_y_range:
            self.notify_figure_y_range_update()
        self.update_bokeh_data_source()

    def draw(self) -> None:
        """
        This function triggers a redrawing of the renderer
        """
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()
        self.notify_figure_y_range_update()

    @property
    def visible(self) -> Optional[bool]:
        """
        Returns if renderer is visible
        """
        if self.view is not None:
            return self.view.visible
        else:
            return None

    @property
    def ts_vector(self) -> Optional[Quantity[TsVector]]:
        """
        This property returns the unit converted ts_vector
        """
        if self._ts_vector is None:
            return self._ts_vector
        try:
            _ts_vector = self._ts_vector.to(self.unit_registry.Unit(self.y_axis.unit))
        except RuntimeError as e:
            self.logger.error(f"{self}: UnitConversionError: {e}")
            _ts_vector = None
        return _ts_vector

    @abc.abstractmethod
    def update_bokeh_data_source(self) -> None:
        """
        This function updates ColumnDataSource in the bokeh document
        """
        # pass

    @abc.abstractmethod
    def reset_bokeh_data_source(self) -> None:
        """
        This function resets ColumnDataSource in the bokeh document
        """
        # pass

    @property
    @abc.abstractmethod
    def glyphs(self) -> List[Tuple[bokeh.models.ColumnDataSource, bokeh.models.Glyph]]:
        """
        This function returns a list of tuples of the glyph and the corresponding ColumnDataSource
        """
        # pass

    def set_bokeh_renderers(self, *, bokeh_renderers: List[Any]) -> None:
        self._bokeh_renderers = bokeh_renderers

    def get_bokeh_renderers(self) -> List["bokeh.models.Glyph"]:
        return self._bokeh_renderers

    def visible_callback(self, obj, attr, old_value, new_value) -> None:
        """
        Callback when visible of view is changed
        """
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if attr != "visible":
            return
        for r in self._bokeh_renderers:
            r.visible = new_value
        self.notify_figure_y_range_update()

    @abc.abstractmethod
    def color_callback(self, obj, attr, old_value, new_value) -> None:
        """
        Sets the color for the bokeh patches
        """
        # pass

    def _receive_state(self, state: States) -> None:
        """
        Recieving state function
        """
        if state == self._state:
            return
        if state == States.ACTIVE:
            self._state = state
        elif state == States.DEACTIVE:
            self._state = state


class SingleGlyphRenderer(BaseFigureRenderer):
    """
    This object is the base class for single glyphs such as LineRendrer and FillInBetweenRenderer
    """

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)
        self.bokeh_data_source = bokeh.models.ColumnDataSource({k: [] for k in self.bokeh_ds_keys})
        self.reset_bokeh_data_source()

    def reset_bokeh_data_source(self):
        """
        This function updates the properties of a glyph which can be dynamically set,
        color, fill_alpha, etc.
        """
        self.bokeh_data_source.data = dict({k: [] for k in self.bokeh_ds_keys})

    @property
    @abc.abstractmethod
    def _glyph(self) -> bokeh.models.Model:
        """
        This function returns the glyph of the current renderer
        """
        # pass

    @property
    @abc.abstractmethod
    def bokeh_ds_keys(self) -> List[str]:
        """
        This function returns a list of strings of the data source keys which are in the renderer
        """
        # pass

    @property
    def glyphs(self) -> List[Tuple[bokeh.models.ColumnDataSource, bokeh.models.Model]]:
        """
        This function adds source data to bokeh glyphs
        """
        return [(self.bokeh_data_source, self._glyph)]

    def color_callback(self, obj, attr, old_value, new_value) -> None:
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        color_patches = [(i, self.view.color) for i, d in enumerate((self.bokeh_data_source.data["f"]))]
        self.bokeh_data_source.patch({"color": color_patches})


class LineRenderer(SingleGlyphRenderer):
    """
    This object contains meta-data and initialisation/update functions for the renderers
    of a single line
    """

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)

    @property
    def _glyph(self) -> bokeh.models.Model:
        """ This function returns a glyph of a line

        Remark: line_dash is not supposed to be changed with the data source so we need to change the bokeh.renderer
        it self directly see self.line_style_callback
        """
        return bokeh.models.MultiLine(xs="t", ys="f", line_color="color", line_dash="solid", line_width="line_width")

    @property
    def bokeh_ds_keys(self) -> List[str]:
        """
        This function returns the keys of the dynamically changeable properties of the renderer
        """
        tooltips = {"t", "f", "color", "label", "line_width"}
        if self.view:
            for tt in self.view.tooltips:
                tooltips.add(tt[0])
        return list(tooltips)

    def on_set_view(self) -> None:
        self.view.on_change(obj=self, attr="index", callback=self.index_callback)
        self.view.on_change(obj=self, attr="line_style", callback=self.line_style_callback)
        self.view.on_change(obj=self, attr='line_width', callback=self.line_width_callback)
        # init line sytle callback
        self.line_style_callback(obj=self.view, attr='line_style', old_value='solid', new_value=self.view.line_style)

    def y_range(self, view_range: UtcPeriod) -> np.ndarray:
        """
        This function returns an np.ndarray with min, and max y values for given view period

        Parameters
        ----------
        view_range (UtcPeriod): a utcperiod from which to extract the

        Return
        ------
        return_array (np.ndarray): a numpy array with the minimum and maximum value

        Notes
        -----
        Returns np.nan if the renderer does not have a TS vector or a view or the time series is empty
        """
        if not self.ts_vector or self.ts_vector is None or not self.view or self.view and self.view.no_y_rescaling:
            return np.array([np.nan, np.nan])
        ta = TimeAxis(view_range.start, view_range.timespan(), 1)

        ts = self.ts_vector[self.view.index]
        if len(ts) == 0:
            return np.array([np.nan, np.nan])
        min_ts, max_ts = TsVector([ts.magnitude]). \
            percentiles(ta, [statistics_property.MIN_EXTREME, statistics_property.MAX_EXTREME])

        _y_range = np.array([min_ts.values.to_numpy()[0], max_ts.values.to_numpy()[0]])

        if np.isnan(_y_range).all():
            return np.array([np.nan, np.nan])
        elif np.isnan(_y_range).any():
            return np.array([np.nanmin(_y_range[0]), np.nanmax(_y_range[1])])
        else:
            return _y_range

    def update_bokeh_data_source(self) -> None:
        """
        This function updates the data source of the plot,
        data points, color, etc.
        """
        if self.do_log:
            ts = utctime_now()
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} updating data source")

        t, f = convert_ts_to_plot_vectors(ts=self.ts_vector.magnitude[self.view.index], cal=self.calendar, interpret_point_interpretation=True, crop_nan=True)

        curve_data = {k: [] for k in self.bokeh_ds_keys}
        curve_data["f"] = [f]
        curve_data["t"] = [t]
        curve_data["color"] = [self.view.color for _ in range(len(curve_data["f"]))]
        curve_data["line_width"] = [self.view.line_width for _ in range(len(curve_data["f"]))]
        curve_data["label"] = [self.view.label for _ in range(len(curve_data["f"]))]
        self.bokeh_data_source.data = curve_data
        if self.do_log:
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} update took {utctime_now() - ts}")
        self.view.view_container.update_y_range()

    def index_callback(self, obj, attr, old_value, new_value) -> None:
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()
        self.notify_figure_y_range_update()

    def line_style_callback(self, obj, attr, old_value, new_value) -> None:
        if attr != 'line_style':
            return
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if new_value not in VALID_LINE_STYLES:
            obj.line_style = old_value
            return
        for renderer in self._bokeh_renderers:
            renderer.glyph.line_dash = new_value
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()

    def line_width_callback(self, obj, attr, old_value, new_value) -> None:
        if attr != 'line_width':
            return
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()
        self.notify_figure_y_range_update()


class ScatterRenderer(SingleGlyphRenderer):
    """
    This object contains meta-data and initialisation/update functions for scatter renderers!
    All scatter renderer are i principle the same just the _glyph function is different!
    """

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)

    @property
    @abc.abstractmethod
    def _glyph(self) -> bokeh.models.Model:
        """
        This function returns the glyph of the current renderer
        """
        # pass

    @property
    def bokeh_ds_keys(self) -> List[str]:
        """
        This function returns the keys of the dynamically changeable properties of the renderer
        """
        tooltips = {"t", "f", "color", "label", "size", 'fill_alpha', 'line_alpha', 'fill_color'}
        # if self.view:
        #     for tt in self.view.tooltips:
        #         tooltips.add(tt[0])
        return list(tooltips)

    def on_set_view(self) -> None:
        self.view.on_change(obj=self, attr="index", callback=self.index_callback)
        self.view.on_change(obj=self, attr="size", callback=self.patch_attr_callback)
        self.view.on_change(obj=self, attr="fill_alpha", callback=self.patch_attr_callback)
        self.view.on_change(obj=self, attr="line_alpha", callback=self.patch_attr_callback)
        self.view.on_change(obj=self, attr="fill_color", callback=self.patch_attr_callback)

    def y_range(self, view_range: UtcPeriod) -> np.ndarray:
        """
        This function returns an np.ndarray with min, and max y values for given view period

        Parameters
        ----------
        view_range (UtcPeriod): a utcperiod from which to extract the

        Return
        ------
        return_array (np.ndarray): a numpy array with the minimum and maximum value

        Notes
        -----
        Returns np.nan if the renderer does not have a TS vector or a view or the time series is empty
        """
        if not self.ts_vector or self.ts_vector is None or not self.view or self.view and self.view.no_y_rescaling:
            return np.array([np.nan, np.nan])
        ta = TimeAxis(view_range.start, view_range.timespan(), 1)

        ts = self.ts_vector[self.view.index]
        if len(ts) == 0:
            return np.array([np.nan, np.nan])
        min_ts, max_ts = TsVector([ts.magnitude]). \
            percentiles(ta, [statistics_property.MIN_EXTREME, statistics_property.MAX_EXTREME])

        # TODO: May return NaN, running y_range
        return np.array([min_ts.values.to_numpy()[0], max_ts.values.to_numpy()[0]])

    def update_bokeh_data_source(self) -> None:
        """
        This function updates the data source of the plot,
        data points, color, etc.
        """
        if self.do_log:
            ts = utctime_now()
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} updating data source")

        t, f = convert_ts_to_plot_vectors(ts=self.ts_vector.magnitude[self.view.index], cal=self.calendar, interpret_point_interpretation=False, crop_nan=True)

        curve_data = {k: [] for k in self.bokeh_ds_keys}
        curve_data["f"] = f
        curve_data["t"] = t
        curve_data["color"] = [self.view.color for _ in range(len(curve_data["f"]))]
        curve_data["label"] = [self.view.label for _ in range(len(curve_data["f"]))]
        curve_data["size"] = [self.view.size for _ in range(len(curve_data["f"]))]
        curve_data["fill_alpha"] = [self.view.fill_alpha for _ in range(len(curve_data["f"]))]
        curve_data["line_alpha"] = [self.view.line_alpha for _ in range(len(curve_data["f"]))]
        curve_data["fill_color"] = [self.view.fill_color for _ in range(len(curve_data["f"]))]

        self.bokeh_data_source.data = curve_data
        if self.do_log:
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} update took {utctime_now() - ts}")

    def index_callback(self, obj, attr, old_value, new_value) -> None:
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()
        self.notify_figure_y_range_update()

    def patch_attr_callback(self, obj, attr, old_value, new_value) -> None:
        if attr not in ['size', 'fill_alpha', 'line_alpha', 'fill_color']:
            obj.__setattr__(attr, new_value)
            return
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        size_patches = [(i, new_value) for i, d in enumerate((self.bokeh_data_source.data["f"]))]
        self.bokeh_data_source.patch({attr: size_patches})


class DiamondScatterRenderer(ScatterRenderer):
    """This object contains meta-data and initialisation/update functions for diamond scatter renderer"""

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)

    @property
    def _glyph(self) -> bokeh.models.Model:
        """ This function returns a glyph of a diamond """
        return bokeh.models.markers.Diamond(x="t", y="f", size="size", line_color="color", fill_color="fill_color",
                                            fill_alpha="fill_alpha", line_alpha='line_alpha',
                                            line_width=2)


class CircleScatterRenderer(ScatterRenderer):
    """This object contains meta-data and initialisation/update functions for circle scatter renderer"""

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)

    @property
    def _glyph(self) -> bokeh.models.Model:
        """ This function returns a glyph of a diamond """
        return bokeh.models.markers.Circle(x="t", y="f", size="size", line_color="color", fill_color="fill_color",
                                           fill_alpha="fill_alpha", line_alpha='line_alpha',
                                           line_width=2)


class SquareScatterRenderer(ScatterRenderer):
    """This object contains meta-data and initialisation/update functions for square scatter renderer"""

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)

    @property
    def _glyph(self) -> bokeh.models.Model:
        """ This function returns a glyph of a diamond """
        return bokeh.models.markers.Square(x="t", y="f", size="size", line_color="color", fill_color="fill_color",
                                           fill_alpha="fill_alpha", line_alpha='line_alpha',
                                           line_width=2)


class TriangleScatterRenderer(ScatterRenderer):
    """This object contains meta-data and initialisation/update functions for triangle scatter renderer"""

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)

    @property
    def _glyph(self) -> bokeh.models.Model:
        """ This function returns a glyph of a diamond """
        return bokeh.models.markers.Triangle(x="t", y="f", size="size", line_color="color", fill_color="fill_color",
                                             fill_alpha="fill_alpha", line_alpha='line_alpha',
                                             line_width=2)


class FillInBetweenRenderer(SingleGlyphRenderer):
    """
    This object contains the meta-data and initialisation/update functions of the renderers with
    lines with filled color in between
    """

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)

    @property
    def _glyph(self) -> bokeh.models.Model:
        """ This function returns a glyph of a line with spread """
        return bokeh.models.Patches(xs="t", ys="f", fill_alpha="fill_alpha", line_alpha=0.0, line_width=0,
                                    fill_color="color")

    @property
    def bokeh_ds_keys(self) -> List[str]:
        """
        This function keeps the keys of the dynamically changeable properties of the renderer
        """
        tooltips = {"t", "f", "color", "fill_alpha", "label"}
        if self.view:
            for tt in self.view.tooltips:
                tooltips.add(tt[0])
        return list(tooltips)

    def on_set_view(self) -> None:
        self.view.on_change(obj=self, attr="indices", callback=self.indices_callback)

    def update_bokeh_data_source(self) -> None:
        """
        This function updates the data source of the plot,
        data points, color, etc.
        """
        if self.do_log:
            ts = utctime_now()
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} updating data source")

        t1, f1 = convert_ts_to_plot_vectors(ts=self.ts_vector.magnitude[self.view.indices[0]], cal=self.calendar, interpret_point_interpretation=True, crop_nan=True)
        t2, f2 = convert_ts_to_plot_vectors(ts=self.ts_vector.magnitude[self.view.indices[1]], cal=self.calendar, interpret_point_interpretation=True, crop_nan=True)
        non_nan_slices = np.ma.masked_invalid(f1)
        if len(non_nan_slices) != 0:
            non_nan_slices = np.ma.clump_unmasked(non_nan_slices)

        time_patches = data_to_patch_values(t1, t2, non_nan_slices)
        data_patches = data_to_patch_values(f1, f2, non_nan_slices)

        curve_data = {k: [] for k in self.bokeh_ds_keys}
        curve_data["f"] = data_patches
        curve_data["t"] = time_patches
        curve_data["color"] = [self.view.color for _ in range(len(curve_data["f"]))]
        curve_data["fill_alpha"] = [self.view.fill_alpha for _ in range(len(curve_data["f"]))]
        curve_data["label"] = [self.view.label for _ in range(len(curve_data["f"]))]

        self.bokeh_data_source.data = curve_data
        if self.do_log:
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} update took {utctime_now() - ts}")

    def y_range(self, view_range: UtcPeriod) -> np.ndarray:
        """
        This function returns an np.ndarray with min, and max y values for given view period
        """
        ts_vector = self.ts_vector
        if not ts_vector or ts_vector is None or not self.view or \
                self.view and self.view.no_y_rescaling:
            return np.array([np.nan, np.nan])
        ta = TimeAxis(view_range.start, view_range.timespan(), 1)
        ts1 = ts_vector[self.view.indices[0]]
        ts2 = ts_vector[self.view.indices[1]]
        if len(ts1) == 0 or len(ts2) == 0:
            return np.array([np.nan, np.nan])

        min_ts1, max_ts1 = TsVector([ts1.magnitude]). \
            percentiles(ta, [statistics_property.MIN_EXTREME, statistics_property.MAX_EXTREME])
        min_ts2, max_ts2 = TsVector([ts2.magnitude]). \
            percentiles(ta, [statistics_property.MIN_EXTREME, statistics_property.MAX_EXTREME])
        minimum = [min_ts1.values.to_numpy()[0], min_ts2.values.to_numpy()[0]]
        maximum = [max_ts1.values.to_numpy()[0], max_ts2.values.to_numpy()[0]]
        if np.isnan(minimum).all() or np.isnan(maximum).all():
            return np.array([np.nan, np.nan])

        return np.array([np.nanmin(minimum), np.nanmax(maximum)])
        # return np.array([np.nanmin([min_ts1.values.to_numpy()[0], min_ts2.values.to_numpy()[0]]),
        #                 np.nanmax([max_ts1.values.to_numpy()[0], max_ts2.values.to_numpy()[0]])])

    def indices_callback(self, obj, attr, old_value, new_value) -> None:
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        if len(new_value) != 2:
            # print("ERROR ... wrong index assigned to {obj}.{label}")
            return
        self.update_bokeh_data_source()
        self.notify_figure_y_range_update()


class MultiLineRenderer(SingleGlyphRenderer):
    """
    This object contains meta-data and initialisation/update functions for the renderers
    of a MultiLine
    """

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)

    @property
    def _glyph(self) -> bokeh.models.Model:
        """ This function returns a glyph of a multiline """
        return bokeh.models.MultiLine(xs="t", ys="f", line_color="color", line_dash="solid", line_width="line_width")

    @property
    def bokeh_ds_keys(self) -> List[str]:
        """
        This function returns the keys of the dynamically changeable properties of the renderer
        """
        tooltips = {"t", "f", "color", "line_width"}
        if self.view:
            for tt in self.view.tooltips:
                tooltips.add(tt[0])
        return list(tooltips)

    def on_set_view(self) -> None:
        self.view.on_change(obj=self, attr="indices", callback=self.index_callback)
        self.view.on_change(obj=self, attr="line_styles", callback=self.line_style_callback)
        self.view.on_change(obj=self, attr='line_widths', callback=self.line_width_callback)
        # init line style callback
        self.line_style_callback(obj=self.view, attr='line_styles', old_value='solid',
                                 new_value=self.view.line_styles)

    def y_range(self, view_range: UtcPeriod) -> np.ndarray:
        """
        This function returns an np.ndarray with min, and max y values for given view period

        Parameters
        ----------
        view_range (UtcPeriod): a utcperiod from which to extract the

        Return
        ------
        return_array (np.ndarray): a numpy array with the minimum and maximum value

        Notes
        -----
        Returns np.nan if the renderer does not have a TS vector or a view or the time series is empty
        """
        if not self.ts_vector or self.ts_vector is None or not self.view or self.view and self.view.no_y_rescaling:
            return np.array([np.nan, np.nan])
        ta = TimeAxis(view_range.start, view_range.timespan(), 1)

        _y_range = np.empty(shape=(len(self.view.indices), 2))
        for i, index in enumerate(self.view.indices):
            ts = self.ts_vector[index]
            if len(ts) != 0:
                min_ts, max_ts = TsVector([ts.magnitude]). \
                    percentiles(ta, [statistics_property.MIN_EXTREME, statistics_property.MAX_EXTREME])
                _y_range[i, 0] = min_ts.values.to_numpy()[0]
                _y_range[i, 1] = max_ts.values.to_numpy()[0]
            else:
                _y_range[i, 0] = np.nan
                _y_range[i, 1] = np.nan
        if np.isnan(_y_range).all():
            return np.array([np.nan, np.nan])
        elif np.isnan(_y_range).any():
            return np.array([np.nanmin(_y_range), np.nanmax(_y_range)])
        else:
            return np.array([np.amin(_y_range), np.amax(_y_range)])

    def update_bokeh_data_source(self) -> None:
        """
        This function updates the data source of the plot,
        data points, color, etc.
        """
        if self.do_log:
            ts = utctime_now()
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} updating data source")

        cal = self.calendar
        tv, fv = [], []
        for i, index in enumerate(self.view.indices):
            t, f = convert_ts_to_plot_vectors(ts=self.ts_vector.magnitude[index], cal=cal, interpret_point_interpretation=True, crop_nan=True)
            tv.append(t)
            fv.append(f)

        curve_data = {k: [] for k in self.bokeh_ds_keys}
        curve_data["f"] = fv
        curve_data["t"] = tv
        curve_data["color"] = self.view.color
        curve_data["line_width"] = self.view.line_widths
        # curve_data["label"] = self.view.labels
        for tt in self.view.tooltips:
            curve_data[tt[0]] = getattr(self.view, tt[0])

        self.bokeh_data_source.data = curve_data
        if self.do_log:
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} update took {utctime_now() - ts}")
        self.view.view_container.update_y_range()

    def index_callback(self, obj, attr, old_value, new_value) -> None:
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()
        self.notify_figure_y_range_update()

    def line_style_callback(self, obj, attr, old_value, new_value) -> None:
        if attr != 'line_styles':
            return
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if new_value not in VALID_LINE_STYLES:
            obj.line_styles = old_value
            return
        for renderer in self._bokeh_renderers:
            renderer.glyph.line_dash = new_value
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()

    def line_width_callback(self, obj, attr, old_value, new_value) -> None:
        if attr != 'line_widths':
            return
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()
        self.notify_figure_y_range_update()


class BackgroundDataRenderer(SingleGlyphRenderer):
    """
    This object contains the meta-data and initialisation/update functions of the renderers with
    lines with filled color in between
    """

    def __init__(self, *, unit_registry: UnitRegistry,
                 notify_figure_y_range_update: Callable,
                 logger: logging.Logger = None) -> None:
        """
        Parameters
        ----------
        unit_registry: unit registry to use to verify data
        notify_figure_y_range_update: function to trigger y_range_update of the figure renderer is connected to
        """
        super().__init__(unit_registry=unit_registry,
                         notify_figure_y_range_update=notify_figure_y_range_update,
                         logger=logger)

    @property
    def _glyph(self) -> bokeh.models.Model:
        """ This function returns a glyph of a line with spread """
        return bokeh.models.Quad(left="left", right="right",
                                 top="top", bottom="bottom", fill_alpha="fill_alpha", line_alpha=0.0, line_width=0,
                                 fill_color="colors")

    @property
    def bokeh_ds_keys(self) -> List[str]:
        """
        This function keeps the keys of the dynamically changeable properties of the renderer
        """
        return ["left", "right", "top", "bottom", "colors", "fill_alpha"]

    def on_set_view(self) -> None:
        self.view.on_change(obj=self, attr="index", callback=self.redraw_callback)
        self.view.on_change(obj=self, attr="fill_alpha", callback=self.redraw_callback)
        self.view.on_change(obj=self, attr="values_color_map", callback=self.values_color_map_callback)
        self.view.on_change(obj=self, attr="index", callback=self.redraw_callback)
        self.view.on_change(obj=self, attr="y_max", callback=self.redraw_callback)
        self.view.on_change(obj=self, attr="y_min", callback=self.redraw_callback)
        self.view.on_change(obj=self, attr="show_not_defined", callback=self.redraw_callback)

    def update_bokeh_data_source(self) -> None:
        """
        This function updates the data source of the plot,
        data points, color, etc.
        """
        if self.do_log:
            ts = utctime_now()
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} updating data source")

        t, f = convert_ts_to_plot_vectors(ts=self.ts_vector.magnitude[self.view.index], cal=self.calendar, interpret_point_interpretation=True, crop_nan=True)
        line_indices, scatter_indices = calculate_dead_band_indices(ts_input=f)
        left_indices = line_indices[:, 0]
        right_indices = line_indices[:, 1]

        values_color_map = {k: v['color'] for k, v in self.view.values_color_map.items()}

        # remove values not in view.values_color_map if view.show_not_defined == True
        if not self.view.show_not_defined:
            to_keep = list(values_color_map.keys())

            def map(entry):
                return entry in to_keep

            mask = np.nonzero(np.vectorize(map)(f))
            left_indices = np.intersect1d(mask, left_indices)
            right_indices = np.intersect1d(mask, right_indices)

        n = len(left_indices)
        curve_data = {k: [] for k in self.bokeh_ds_keys}
        curve_data["left"] = t[left_indices]
        curve_data["right"] = t[right_indices]
        curve_data["top"] = [self.view.y_max]*n
        curve_data["bottom"] = [self.view.y_min]*n

        def map(entry):
            return values_color_map.get(entry, self.view.color)

        v = np.vectorize(map)

        curve_data["colors"] = v(f[left_indices])
        curve_data["fill_alpha"] = [self.view.fill_alpha]*n

        self.bokeh_data_source.data = curve_data
        if self.do_log:
            self.logger.debug(f"{self.__class__.__name__} {self.view.label} update took {utctime_now() - ts}")

    def y_range(self, view_range: UtcPeriod) -> np.ndarray:
        """
        This function returns an np.ndarray with min, and max y values for given view period

        It is hardcoded set in the view that self.view.no_y_rescaling = False,
        just in case some messes with that we return self.view.y_min, self.view.y_max if the check fails
        """
        ts_vector = self.ts_vector
        if not ts_vector or ts_vector is None or not self.view or \
                self.view and self.view.no_y_rescaling:
            return np.array([np.nan, np.nan])
        return np.array([self.view.y_min, self.view.y_max])

    def redraw_callback(self, obj, attr, old_value, new_value) -> None:
        """
        Callback to redraw the renderer user for all view. variables which require a redrawing of the renderer to
        be effective
        """
        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()
        self.notify_figure_y_range_update()

    def values_color_map_callback(self, obj, attr, old_value, new_value) -> None:
        """
        Callback to redraw the renderer user for all view. variables which require a redrawing of the renderer to
        be effective
        """
        if not isinstance(new_value, dict):
            raise ValueError(
                f"BackgroundData in values_color_map: expect dict got {type(new_value)}")
        for k, v in new_value.items():
            if not isinstance(v, dict):
                raise ValueError(
                    f"BackgroundData in values_color_map: expect values in "
                    f"form of Dict[str, str] with keys `label` and `color` got {v}")
            for label in ['color', 'label']:
                if label not in v:
                    raise KeyError(f"BackgroundData in values_color_map: `{label}` not in dict of {k}: got {v}")
                if not isinstance(v[label], str):
                    raise ValueError(f"BackgroundData in values_color_map: `{label}` not of type str: got {v[label]} {type(v[label])}")

        if self._state == States.DEACTIVE:
            return
        if obj != self.view:
            obj.remove_all_callbacks(self)
            return
        if not self.ts_vector:
            self.reset_bokeh_data_source()
            return
        self.update_bokeh_data_source()
        self.notify_figure_y_range_update()
