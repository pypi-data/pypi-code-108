import bokeh
import bokeh.models
import bokeh.plotting
from bokeh.core.properties import value

import logging
import numpy as np
from packaging import version
from typing import List, Optional, Dict

from shyft.time_series import TsVector
from shyft.dashboard.time_series.state import Quantity
from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.base.ports import States, StatePorts
from shyft.dashboard.base.app import LayoutComponents, update_value_factory
from shyft.dashboard.time_series.view import LegendItem, Line, FillInBetween, MultiLine
from shyft.dashboard.time_series.view_container.view_container_base import BaseViewContainer


class Legend(BaseViewContainer):
    """
    Examples
    --------
    | # create the viewer app
    | viewer = TsViewer(bokeh_document=doc, title='Example Ts Viewer')
    | # create the view container
    | figure = Figure(viewer=viewer)
    | # create the legend container
    | legend = Legend(viewer=viewer)
    | # set up a data source
    | data_source = DataSource(ts_adapter=TsAdapter(), unit='MW')
    | # create views
    | fill_in_between = FillInBetween(view_container=figure, color='purple', label='Example Percentile', unit='MW',
    |                                 indices=(0, 1))
    | line = Line(view_container=figure, color='blue', unit='MW', label='Example Line', index=1)
    | # add views to a legend item
    | legend_item = LegendItem(view_container=legend, label='Example Legend Item', views=[line, fill_in_between])
    | # add data source and views to a DsViewHandle
    | ds_view_handle = DsViewHandle(data_source=data_source, views=[line, fill_in_between, legend_item])
"""

    def __init__(self, *,
                 viewer: "shyft.dashboard.time_series.ts_viewer.TsViewer",
                 title: Optional[str] = '',
                 width: int = 200,
                 height: int = 300,
                 text_font_size: int = 8,
                 text_font: str = 'verdana',
                 title_text_font_style: str = 'bold',
                 title_text_font_size: str = '10pt',
                 logger: Optional[LoggerBox] = None) -> None:
        """
        Parameters
        ----------
        viewer:
            the TsViewer this legend belongs to
        title:
            legend title text
        width:
            pixel width of the legend box
        height:
            pixel height of the legend box
        text_font_size:
            text font size for legend items
        text_font:
            text font for legend items (options: 'monospace','verdana', 'times', 'helvetica', etc.)
        title_text_font_style:
            text font style (bold, italic, ...) for legend title
        title_text_font_size:
            text font size for legend title
        logger:
            optional logger or LoggerBox instance
        """
        super().__init__(viewer=viewer)
        self.logger = logger or logging.getLogger(__file__)

        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        self._state = States.ACTIVE

        self.height = max(200, height)
        self.width = width

        # empirical tested y range conversion
        coeff = np.array([-1.56666667e+02, 1.77500000e+00, 4.16666667e-05])
        self.y_range_start = -(coeff[0] + coeff[1]*self.height + coeff[2]*self.height**2)

        # text_font_size
        self.text_font_size = f'{int(text_font_size)}pt'
        self.item_height = min(-2.5*text_font_size, -10)
        self.max_y_range = 20*self.item_height
        self.space_between_items = -2

        self.bokeh_figure = bokeh.plotting.figure(width=self.width, plot_height=self.height, title=title,
                                                  tools=['ywheel_pan'], x_axis_location=None, y_axis_location=None,
                                                  toolbar_location=None, )
        self.bokeh_figure.grid.grid_line_color = None
        self.bokeh_figure.y_range = bokeh.models.Range1d(self.y_range_start, 0, bounds=None)
        self.x_range = bokeh.models.Range1d(0, width)
        self.bokeh_figure.x_range = self.x_range
        if title:  # set title border if title available
            self.bokeh_figure.min_border_top = 30
        self.bokeh_figure.title.text_font = text_font
        self.bokeh_figure.title.text_font_style = title_text_font_style
        self.bokeh_figure.title.text_font_size = title_text_font_size

        self.legend_items = {}
        self.legend_view_legend_item_map = {}
        self.ds_keys = {'tag', 'xs', 'ys', 'ox', 'oy', 'color_box', 'xs_box', 'ys_box',
                        'color_line', 'xs_line', 'ys_line', 'alpha', 'label'}
        self.ds = bokeh.models.ColumnDataSource({k: [] for k in self.ds_keys})

        self.color_patches = '#fffdf9'
        self.color_patches_hover = '#fff7eb'
        self.alpha_visible = 1
        self.alpha_invisible = 0.4
        self.patches = self.bokeh_figure.patches('xs', 'ys', source=self.ds,
                                                 alpha=0.0, line_color='#bcbcbc',
                                                 fill_color=self.color_patches,
                                                 hover_line_color=self.color_patches_hover,
                                                 hover_fill_color=self.color_patches_hover,
                                                 # set visual properties for selected glyphs
                                                 selection_line_color=self.color_patches,
                                                 selection_fill_color=self.color_patches,
                                                 selection_fill_alpha=0.0,
                                                 # set visual properties for non-selected glyphs
                                                 nonselection_alpha=0.0,
                                                 nonselection_color=self.color_patches,
                                                 nonselection_line_color=self.color_patches,
                                                 # nonselection_line_alpha=0.4
                                                 )

        if version.parse(bokeh.__version__) < version.Version("2.3.0"):
            text_font = text_font
            text_font_size = self.text_font_size
        else:
            text_font = value(text_font)
            text_font_size = value(self.text_font_size)
        self.labels = bokeh.models.LabelSet(text='label', x='ox', y='oy', source=self.ds, text_color='#1c1b1e',
                                            text_alpha='alpha', text_font_style='normal', text_font=text_font,
                                            text_font_size=text_font_size)

        self.bokeh_figure.add_layout(self.labels)
        self.patches_box = self.bokeh_figure.patches(xs='xs_box', ys='ys_box', source=self.ds,
                                                     alpha='alpha', color='color_box')
        self.multi_lines = self.bokeh_figure.multi_line(xs='xs_line', ys='ys_line', source=self.ds,
                                                        line_alpha='alpha', line_color='color_line')
        self.hover_tool = bokeh.models.HoverTool(renderers=[self.patches], attachment='horizontal',
                                                 anchor='center_right', mode='mouse', point_policy='follow_mouse',
                                                 show_arrow=False)
        self.hover_tool.tooltips = [("", "@label"), ]
        self.bokeh_figure.add_tools(self.hover_tool)
        # self.bokeh_figure.toolbar.active_inspect = []
        self.tap_tool = bokeh.models.TapTool(renderers=[self.patches])
        self.bokeh_figure.add_tools(self.tap_tool)
        self.ds.selected.on_change('indices', self._callback_selected)
        self.set_selected = update_value_factory(self.ds.selected, 'indices')

    # --- LAYOUT

    @property
    def layout(self):
        return self.bokeh_figure

    @property
    def layout_components(self) -> LayoutComponents:
        return {"widgets": [],
                "figures": [self.bokeh_figure]}

    def add_view(self, *, view: LegendItem) -> None:
        """
        This function adds a new view to the view_container
        """
        self.legend_items[str(view.uid)] = view
        for v in view.views:
            if str(v.uid) not in self.legend_view_legend_item_map:
                self.legend_view_legend_item_map[str(v.uid)] = [str(view.uid)]
            else:
                self.legend_view_legend_item_map[str(v.uid)].append(str(view.uid))

            if isinstance(v, MultiLine):
                if not v.expandable:
                    v.on_change(obj=self, attr='visible', callback=self.visible_callback)
            else:
                v.on_change(obj=self, attr='visible', callback=self.visible_callback)
        view.on_change(obj=view, attr="label", callback=self.label_callback)

        self.update_data_source()

    def label_callback(self, obj, attr, old_value, new_value) -> None:
        if self._state == States.DEACTIVE:
            return
        if obj not in self.legend_items.values():
            obj.remove_all_callbacks(self)
            return
        self.update_data_source()

    def update_view_data(self, *, view_data: Dict[LegendItem, Quantity[TsVector]]) -> None:
        """
        This function updates the views with new data
        """
        pass

    def clear(self) -> None:
        """
        This function removes all views from the view_container and resets the meta information
        """
        self.clear_views()

    def clear_views(self, *, specific_views: Optional[List[LegendItem]] = None) -> None:
        """
        This function removes all or specific views from the view_container
        """
        if specific_views:
            views = specific_views
            self.legend_items = {str(v.uid): v for v in self.legend_items.values() if v not in views}
        else:
            views = [v for v in self.legend_items.values()]
            self.legend_items = {}
        # remove callbacks of view
        for view in views:
            view.remove_all_callbacks(self)
            for v in view.views:
                v.remove_all_callbacks(self)
                self.legend_view_legend_item_map[str(v.uid)].remove(str(view.uid))
                if len(self.legend_view_legend_item_map[str(v.uid)]) == 0:
                    self.legend_view_legend_item_map.pop(str(v.uid))
        # update data source
        self.update_data_source()

    def update_data_source(self):
        """
        This function updates the legend data source and shows the legend items
        """
        ds_dict = {k: [] for k in self.ds_keys}
        label_length = 0
        legend_index = 0
        for n, (uid, legend_item) in enumerate(self.legend_items.items()):
            label_length = max(label_length, len(legend_item.label))

            xs_line = []
            ys_line = []
            color_line = ''
            xs_box = []
            ys_box = []
            color_box = ''

            n_line = 0
            n_fill_in_between = 0
            visible = True
            for i, v in enumerate(legend_item.views):
                visible = v.visible

                if isinstance(v, Line):
                    oy = 2 * self.space_between_items + (self.item_height + self.space_between_items) * legend_index
                    mid_point = oy - abs(self.item_height / 2)
                    ds_dict['tag'].append(uid)
                    ds_dict['ox'].append(21)
                    ds_dict['oy'].append(oy + self.item_height + self.space_between_items)

                    ds_dict['xs'].append([0, self.width, self.width, 0])
                    ds_dict['ys'].append([oy, oy, oy + self.item_height, oy + self.item_height])
                    ds_dict['label'].append(legend_item.label)
                    color_line = v.color
                    if n_line > 0:
                        ds_dict['alpha'].append(0)
                        ds_dict['color_box'].append('')
                        ds_dict['color_line'].append(color_line)
                        xs_box = []
                        ys_box = []
                        ds_dict['xs_box'].append(xs_box)
                        ds_dict['ys_box'].append(ys_box)
                        ds_dict['xs_line'].append([])
                        ds_dict['ys_line'].append([])
                        continue
                    xs_line = [0, 20]
                    ys_line = [mid_point, mid_point]
                    n_line += 1
                    ds_dict['xs_box'].append(xs_box)
                    ds_dict['ys_box'].append(ys_box)
                    ds_dict['color_box'].append(color_box)
                    ds_dict['alpha'].append([self.alpha_invisible, self.alpha_visible][visible])
                    ds_dict['xs_line'].append(xs_line)
                    ds_dict['ys_line'].append(ys_line)
                    ds_dict['color_line'].append(color_line)
                    legend_index += 1

                if isinstance(v, FillInBetween):
                    oy = 2 * self.space_between_items + (self.item_height + self.space_between_items) * legend_index
                    mid_point = oy - abs(self.item_height / 2)
                    ds_dict['tag'].append(uid)
                    ds_dict['ox'].append(21)
                    ds_dict['oy'].append(oy + self.item_height + self.space_between_items)

                    ds_dict['xs'].append([0, self.width, self.width, 0])
                    ds_dict['ys'].append([oy, oy, oy + self.item_height, oy + self.item_height])
                    color_box = v.color

                    if n_fill_in_between > 0:
                        ds_dict['label'].append('')
                        xs_box = []
                        ys_box = []
                        ds_dict['xs_box'].append(xs_box)
                        ds_dict['ys_box'].append(ys_box)
                        ds_dict['color_box'].append(color_box)
                        ds_dict['alpha'].append([self.alpha_invisible, self.alpha_visible][visible])
                        ds_dict['xs_line'].append(xs_line)
                        ds_dict['ys_line'].append(ys_line)
                        ds_dict['color_line'].append(color_line)
                        continue
                    ds_dict['label'].append(legend_item.label)
                    xs_box = [6, 14, 14, 6]
                    ys_box = [oy - 2, oy - 2, oy - abs(self.item_height) + 2, oy - abs(self.item_height) + 2]
                    n_fill_in_between += 1
                    ds_dict['xs_box'].append(xs_box)
                    ds_dict['ys_box'].append(ys_box)
                    ds_dict['color_box'].append(color_box)
                    ds_dict['alpha'].append([self.alpha_invisible, self.alpha_visible][visible])
                    ds_dict['xs_line'].append(xs_line)
                    ds_dict['ys_line'].append(ys_line)
                    ds_dict['color_line'].append(color_line)
                    legend_index += 1

                if isinstance(v, MultiLine) and len(v.color) > 1:
                    if v.expanded and v.expandable:
                        oy = 2 * self.space_between_items + (self.item_height + self.space_between_items) * legend_index
                        mid_point = oy - abs(self.item_height / 2)
                        xs_line = [0, 20]
                        ys_line = [mid_point, mid_point]
                        ds_dict['tag'].append(uid)
                        ds_dict['alpha'].append([self.alpha_invisible, self.alpha_visible][visible])
                        ds_dict['xs_line'].append(xs_line)
                        ds_dict['ys_line'].append(ys_line)
                        ds_dict['color_line'].append(v.color[0])
                        ds_dict['label'].append(legend_item.label)
                        ds_dict['xs_box'].append(xs_box)
                        ds_dict['ys_box'].append(ys_box)
                        ds_dict['color_box'].append(color_box)
                        ds_dict['ox'].append(21)
                        ds_dict['oy'].append(oy + self.item_height + self.space_between_items)
                        ds_dict['xs'].append([0, self.width, self.width, 0])
                        ds_dict['ys'].append([oy, oy, oy + self.item_height, oy + self.item_height])
                        legend_index += 1
                        for k in range(len(v.color)):
                            oy = 2 * self.space_between_items + (self.item_height + self.space_between_items) * legend_index
                            mid_point = oy - abs(self.item_height / 2)
                            ds_dict['tag'].append(uid)
                            xs_line = [7, 20]
                            ys_line = [mid_point, mid_point]
                            ds_dict['alpha'].append([self.alpha_invisible, self.alpha_visible][visible])
                            ds_dict['xs_line'].append(xs_line)
                            ds_dict['ys_line'].append(ys_line)
                            ds_dict['color_line'].append(v.color[k])
                            ds_dict['label'].append(v.label[k])
                            ds_dict['xs_box'].append(xs_box)
                            ds_dict['ys_box'].append(ys_box)
                            ds_dict['color_box'].append(color_box)
                            ds_dict['ox'].append(21)
                            ds_dict['oy'].append(oy + self.item_height + self.space_between_items)
                            ds_dict['xs'].append([0, self.width, self.width, 0])
                            ds_dict['ys'].append([oy, oy, oy + self.item_height, oy + self.item_height])
                            legend_index += 1
                    elif not v.expanded and v.expandable:
                        oy = 2 * self.space_between_items + (self.item_height + self.space_between_items) * legend_index
                        mid_point = oy - abs(self.item_height / 2)
                        xs_line = [0, 20]
                        ys_line = [mid_point, mid_point]
                        ds_dict['tag'].append(uid)
                        ds_dict['alpha'].append([self.alpha_invisible, self.alpha_visible][visible])
                        ds_dict['xs_line'].append(xs_line)
                        ds_dict['ys_line'].append(ys_line)
                        ds_dict['color_line'].append(v.color[0])
                        ds_dict['label'].append(legend_item.label)
                        ds_dict['xs_box'].append(xs_box)
                        ds_dict['ys_box'].append(ys_box)
                        ds_dict['color_box'].append(color_box)
                        ds_dict['ox'].append(21)
                        ds_dict['oy'].append(oy + self.item_height + self.space_between_items)
                        ds_dict['xs'].append([0, self.width, self.width, 0])
                        ds_dict['ys'].append([oy, oy, oy + self.item_height, oy + self.item_height])
                        legend_index += 1
                    elif not v.expandable:
                        oy = 2 * self.space_between_items + (self.item_height + self.space_between_items) * legend_index
                        mid_point = oy - abs(self.item_height / 2)
                        xs_line = [0, 20]
                        ys_line = [mid_point, mid_point]
                        ds_dict['tag'].append(uid)
                        alpha = [self.alpha_invisible, self.alpha_visible][visible]
                        ds_dict['alpha'].append(alpha)
                        ds_dict['xs_line'].append(xs_line)
                        ds_dict['ys_line'].append(ys_line)
                        ds_dict['color_line'].append(v.color[0])
                        ds_dict['label'].append(legend_item.label)
                        ds_dict['xs_box'].append(xs_box)
                        ds_dict['ys_box'].append(ys_box)
                        ds_dict['color_box'].append(color_box)
                        ds_dict['ox'].append(21)
                        ds_dict['oy'].append(oy + self.item_height + self.space_between_items)
                        ds_dict['xs'].append([0, self.width, self.width, 0])
                        ds_dict['ys'].append([oy, oy, oy + self.item_height, oy + self.item_height])
                        legend_index += 1
                        for k in range(len(v.color)):
                            oy = 2 * self.space_between_items + (
                                        self.item_height + self.space_between_items) * legend_index
                            mid_point = oy - abs(self.item_height / 2)
                            ds_dict['tag'].append(uid)
                            xs_line = [7, 20]
                            ys_line = [mid_point, mid_point]
                            ds_dict['alpha'].append(alpha)
                            ds_dict['xs_line'].append(xs_line)
                            ds_dict['ys_line'].append(ys_line)
                            ds_dict['color_line'].append(v.color[k])
                            ds_dict['label'].append(v.label[k])
                            ds_dict['xs_box'].append(xs_box)
                            ds_dict['ys_box'].append(ys_box)
                            ds_dict['color_box'].append(color_box)
                            ds_dict['ox'].append(21)
                            ds_dict['oy'].append(oy + self.item_height + self.space_between_items)
                            ds_dict['xs'].append([0, self.width, self.width, 0])
                            ds_dict['ys'].append([oy, oy, oy + self.item_height, oy + self.item_height])
                            legend_index += 1
                if isinstance(v, MultiLine) and len(v.color) == 1:
                    oy = 2 * self.space_between_items + (self.item_height + self.space_between_items) * legend_index
                    mid_point = oy - abs(self.item_height / 2)
                    xs_line = [0, 20]
                    ys_line = [mid_point, mid_point]
                    ds_dict['tag'].append(uid)
                    ds_dict['alpha'].append([self.alpha_invisible, self.alpha_visible][visible])
                    ds_dict['xs_line'].append(xs_line)
                    ds_dict['ys_line'].append(ys_line)
                    ds_dict['color_line'].append(v.color[0])
                    ds_dict['label'].append(legend_item.label)
                    ds_dict['xs_box'].append(xs_box)
                    ds_dict['ys_box'].append(ys_box)
                    ds_dict['color_box'].append(color_box)
                    ds_dict['ox'].append(21)
                    ds_dict['oy'].append(oy + self.item_height + self.space_between_items)
                    ds_dict['xs'].append([0, self.width, self.width, 0])
                    ds_dict['ys'].append([oy, oy, oy + self.item_height, oy + self.item_height])
                    legend_index += 1
            legend_item.visible = visible
        self.ds.data = ds_dict

    def _collapse(self, view):
        view.expanded = False
        self.update_data_source()

    def _expand(self, view):
        view.expanded = True
        self.update_data_source()

    def _callback_selected(self, attrnm, old, new):
        """
        This callback triggers when legend item was clicked
        """
        selected_indices = new
        if selected_indices:
            index = selected_indices[0]  # Dont support multi select
            if index >= len(self.ds.data['tag']):
                return
            color = "#fcf9ef"
            self.bokeh_figure.border_fill_color = color
            self.bokeh_figure.background_fill_color = color
            tag = self.ds.data['tag'][index]
            self.legend_items[tag].visible = not self.legend_items[tag].visible
            for view in self.legend_items[tag].views:
                if isinstance(view, MultiLine):
                    if view.expanded and view.expandable:
                        self._collapse(view)
                    elif not view.expanded and view.expandable:
                        self._expand(view)
                    elif not view.expandable:
                        view.visible = self.legend_items[tag].visible
                        self.update_data_source()
                    else:
                        print("something undefined with the indices happened")
                else:
                    view.visible = self.legend_items[tag].visible
            self.set_selected([])
            self.bokeh_figure.border_fill_color = 'white'
            self.bokeh_figure.background_fill_color = 'white'

    def visible_callback(self, obj, attr, old_value, new_value) -> None:
        """
        This function triggers the in change callback for visible attribute in legend_views
        """
        if self._state == States.DEACTIVE:
            return
        if attr != 'visible':
            return
        tags = self.legend_view_legend_item_map[str(obj.uid)]
        for tag in tags:
            legend_item = self.legend_items[tag]
            view_visibility = set([v.visible for v in legend_item.views])
            # change to visible as soon as one is visible!
            if len(view_visibility) != 1:
                continue
            index = self.ds.data['tag'].index(tag)
            current_value = self.ds.data['alpha'][index]
            new_alpha = [self.alpha_invisible, self.alpha_visible][new_value]
            legend_item.visible = new_value
            if current_value != new_alpha:
                self.ds.patch({'alpha': [(index, new_alpha)]})

    def expand_callback(self, obj, attr, old_value, new_value) -> None:
        """
        This function triggers the in change callback for visible attribute in legend_views
        """
        if self._state == States.DEACTIVE:
            return
        if attr != 'expanded':
            return

        # Add code for making visible new legend items for each line in multiline

    # --- STATES
    def _receive_state(self, state: States) -> None:
        if state == self._state:
            return
        self._state = state
        if state == States.LOADING:
            color = "#fcf9ef"
            self.bokeh_figure.border_fill_color = color
            self.bokeh_figure.background_fill_color = color
            self.state_port.send_state(state)
        elif state == States.READY:
            self.bokeh_figure.border_fill_color = 'white'
            self.bokeh_figure.background_fill_color = 'white'
            self.state_port.send_state(state)
        elif state == States.ACTIVE:
            self.bokeh_figure.border_fill_color = 'white'
            self.bokeh_figure.background_fill_color = 'white'
            self.state_port.send_state(state)
        elif state == States.DEACTIVE:
            color = "#fcf9ef"
            self.bokeh_figure.border_fill_color = color
            self.bokeh_figure.background_fill_color = color
