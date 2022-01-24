import logging

from typing import List, Optional, Dict, Any

import numpy as np

from bokeh.layouts import row, column
from bokeh.models import (ColumnDataSource, LayoutDOM, Range1d, TapTool, HoverTool, Slider, Div)
from bokeh.plotting import figure

from shyft.dashboard.base import constants
from shyft.dashboard.base.ports import (States, StatePorts, Receiver)
from shyft.dashboard.base.app import LayoutComponents, Widget
from shyft.dashboard.widgets.zoomables import LabelSetZoomable, CheckboxGroupZoomable
from shyft.util.layoutgraph import WaterRouteGraph


class WaterRouteWidget(Widget):
    """
    Simple water route graph app with a single port to receive a list of hydro power system objects to visualize the
    graph based on the internal topology of the hydro power systems.
    """
    def __init__(self,
                 water_route_graph: WaterRouteGraph,
                 logger: Optional[logging.Logger] = None,
                 padding: Optional[int] = None,
                 sizing_mode: Optional[str] = None,
                 widget_width: int = 300,
                 widget_height: int = 70,
                 height: int = 1024,
                 aspect_factor: float = 1.4,
                 auto_reload: bool = True) -> None:

        super(WaterRouteWidget, self).__init__(logger)

        self.auto_reload: bool = auto_reload

        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        if not logger:
            logger = logging.getLogger('WaterGraphFigure')
        self.logger = logger

        # 1. initialize figure aspect ration
        self.aspect_factor = aspect_factor
        self.figure_width = int(height * self.aspect_factor)
        self.figure_height = height

        self.fig = figure(plot_width=int(self.figure_width), plot_height=int(self.figure_height),
                          x_axis_location=None, y_axis_location=None,
                          toolbar_location=None, tools=['pan'])
        self.fig.grid.grid_line_color = None

        # 2. water route graph
        self.water_route_graph = water_route_graph
        self.receive_selected_water_route = Receiver(parent=self,
                                                     name='receive selected water route',
                                                     func=self._receive_selected_water_route,
                                                     signal_type=Any)

        # 3. set up zoom ranges and initial _state
        self.view_ranges = [4000, 2000, 1000, 750, 500]  # range of the view in y direction
        self.zoom_state_init = 2
        self.fig.x_range = Range1d(0, self.view_ranges[self.zoom_state_init] * self.aspect_factor)
        self.fig.y_range = Range1d(0, self.view_ranges[self.zoom_state_init])
        # 4. define data sources

        # 4.1 water routes
        self.ds_main_water = ColumnDataSource({k: [] for k in ['sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y']})
        self.ds_bypass = ColumnDataSource({k: [] for k in ['sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y']})
        self.ds_spillage = ColumnDataSource({k: [] for k in ['sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y']})

        # 4.2 reservoir and power stations

        # 4.2.1 shadows
        self.shadow_offset = 2
        self.ds_shadows_reservoirs = ColumnDataSource({k: [] for k in ['xs', 'ys']})
        self.ds_shadow_power_stations = ColumnDataSource({k: [] for k in ['xs', 'ys']})

        # 4.2.2 mad
        self.ds_reservoirs = ColumnDataSource({k: [] for k in ['xs', 'ys']})
        self.reservoirs_data_dict = {}
        self.reservoirs_numerical_data = {}

        self.ds_power_stations = ColumnDataSource({k: [] for k in ['xs', 'ys']})
        self.power_station_data_dict = {}

        # 4.2.3 oceans
        self.ds_oceans = ColumnDataSource({k: [] for k in ['sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y']})
        self.ds_oceans_spillage = ColumnDataSource(
            {k: [] for k in ['sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y']})
        self.ds_oceans_bypass = ColumnDataSource({k: [] for k in ['sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y']})

        # 4.3 text
        self.ds_names = ColumnDataSource(data={key: [] for key in ['x', 'y', 'texts']})

        self.ds_info_text = ColumnDataSource(data={key: [] for key in ['x', 'y', 'texts']})
        self.font_sizes_info = ['0pt', '6pt', '9pt', '11.8pt', '13.4pt']  # not visible if font_size == 0

        # 5. graph glyphs
        # 5.1 water routes
        self.bezier_main = self.fig.bezier('sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y',
                                           source=self.ds_main_water, color='#282370',
                                           line_dash='solid', line_width=2, visible=True)
        self.bezier_bypass = self.fig.bezier('sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y',
                                             source=self.ds_bypass, color='#235170', line_dash='dashed', line_width=2,
                                             visible=False)
        self.bezier_spillage = self.fig.bezier('sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y',
                                               source=self.ds_spillage, color='#237067', line_dash='dotted',
                                               line_width=2, visible=False)

        # 5.2 reservoir and power stations
        self.fig.patches('xs', 'ys', source=self.ds_shadows_reservoirs,
                         alpha=1.0, line_width=2, color='black')
        self.fig.patches('xs', 'ys', source=self.ds_shadow_power_stations,
                         alpha=1, line_width=2, color='black')

        self.patches_reservoirs = self.fig.patches('xs', 'ys', source=self.ds_reservoirs,
                                                   alpha=1.0, color='#dae8e3',
                                                   hover_line_color="#ce7f00",
                                                   hover_fill_color='#dae8e3',
                                                   # set visual properties for selected glyphs
                                                   selection_line_color="#bc3b00",
                                                   selection_fill_color='#76bec1',
                                                   selection_fill_alpha=1.0,
                                                   # set visual properties for non-selected glyphs
                                                   nonselection_alpha=1.0,
                                                   nonselection_color='#dae8e3',
                                                   nonselection_line_color='#dae8e3',
                                                   # nonselection_line_alpha=0.4
                                                   )

        self.patches_powers_stations = self.fig.patches('xs', 'ys', source=self.ds_power_stations,
                                                        alpha=1.0, color='#e8d992',
                                                        hover_line_color="#ce7f00",
                                                        hover_fill_color='#e8d992',
                                                        # set visual properties for selected glyphs
                                                        selection_line_color="#bc3b00",
                                                        selection_fill_color='#d1a23c',
                                                        selection_fill_alpha=1.0,
                                                        # set visual properties for non-selected glyphs
                                                        nonselection_alpha=1.0,
                                                        nonselection_color='#e8d992',
                                                        nonselection_line_color='#e8d992',
                                                        # nonselection_line_alpha=0.4
                                                        )

        # 5.3 oceans
        self.bezier_oceans = self.fig.bezier('sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y',
                                             source=self.ds_oceans, line_color='#5896b5', line_dash='solid',
                                             line_width=2, visible=True)
        self.bezier_oceans_bypass = self.fig.bezier('sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y',
                                                    source=self.ds_oceans_bypass, line_color='#5896b5',
                                                    line_dash='solid',
                                                    line_width=2, visible=True)
        self.bezier_oceans_spillage = self.fig.bezier('sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y',
                                                      source=self.ds_oceans_spillage, line_color='#5896b5',
                                                      line_dash='solid',
                                                      line_width=2, visible=True)

        # 5.4 text
        self.text_names = LabelSetZoomable(dict(x='x', x_units='data', y='y', y_units='data', text='texts',
                                                source=self.ds_names, text_color='black'),
                                           ['0pt', '6pt', '9pt', '11.8pt', '13.4pt'],  # 6
                                           self.zoom_state_init)
        self.text_names.set_update_callback(self._update_name_text)

        self.fig.add_layout(self.text_names.glyph)

        self.text_info = LabelSetZoomable(dict(x='x', x_units='data', y='y', y_units='data', text='texts',
                                               source=self.ds_info_text, text_color='black'),
                                          ['0pt', '0pt', '9pt', '11.8pt', '13.4pt'],
                                          self.zoom_state_init)
        self.text_info.set_update_callback(self._update_info_text)

        self.fig.add_layout(self.text_info.glyph)

        # 6. widget definitions
        self.checkbox_water_way_visibility = CheckboxGroupZoomable(dict(labels=["Bypass", "Spillage"],
                                                                        active=[], inline=True, width=140,
                                                                        height=widget_height,
                                                                        margin=(5 + 40, 5 + padding, 5, 5)),
                                                                   [False, False, True, True, True],
                                                                   self.zoom_state_init,
                                                                   self._change_glyph_visibility)

        # callback for zoom
        self.zoom_state = self.zoom_state_init
        self.zoom_state_old = self.zoom_state_init
        self.zoom_objects = [self.text_info, self.text_names, self.checkbox_water_way_visibility]

        self.zoom_slider = Slider(start=0, end=len(self.view_ranges) - 1, value=self.zoom_state_init,
                                  step=1, title="Zoom", default_size=widget_width, width=widget_width,
                                  height=widget_height
                                  )
        self.zoom_slider.on_change('value', self._updated_zoom)

        # 7. Tools
        # Tap tool
        tap_tool = TapTool(renderers=[self.patches_reservoirs, self.patches_powers_stations])
        self.fig.add_tools(tap_tool)

        # # Hover tools
        self.hover_reservoir = HoverTool()
        self.hover_reservoir.tooltips = [("Type", "@type"),
                                         ("Name", "@name"),
                                         ("Id", "@id")]
        self.hover_reservoir.renderers = [self.patches_reservoirs]
        self.fig.add_tools(self.hover_reservoir)

        self.hover_power_stations = HoverTool()
        self.hover_power_stations.tooltips = [("Type", "@type"),
                                              ("Name", "@name"),
                                              ("Id", "@id")]
        self.hover_power_stations.renderers = [self.patches_powers_stations]
        self.fig.add_tools(self.hover_power_stations)

        # x. layout
        self.widgets = [self.checkbox_water_way_visibility.checkbox, self.zoom_slider]
        widgets = row(self.checkbox_water_way_visibility.layout,
                      column(Div(height=constants.text_height), self.zoom_slider),
                      width=self.figure_width, height=widget_height + padding, sizing_mode=sizing_mode)
        self._layout = column(widgets,
                              self.fig,
                              width=self.figure_width + padding, height=self.figure_height + widget_height,
                              sizing_mode=sizing_mode)

        # register ports
        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        self.state = States.ACTIVE

    @property
    def layout(self) -> LayoutDOM:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        return {'widgets': self.widgets, 'figures': [self.fig]}

    def _receive_state(self, state: States) -> None:
        if state == self.state:
            return
        if state == States.ACTIVE:
            self.state = state
            # Not sending active state since this only done if we can send data to the next widget
        elif state == States.DEACTIVE:
            self.state = state
            self._change_figure_visibility(visible=False)
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)

    def _receive_selected_water_route(self, water_route: Any) -> None:
        self._generate_graph(water_route[0])

    def _generate_graph(self, water_route: Any) -> None:
        self.water_route_graph.__init__()
        self.water_route_graph.generate_graph(water_route)
        self._update_graph()

    def _change_glyph_visibility(self, attrm, old, new):

        self.bezier_bypass.visible = 0 in new
        self.bezier_oceans_bypass.visible = 0 in new
        self.bezier_spillage.visible = 1 in new
        self.bezier_oceans_spillage.visible = 1 in new

    def _updated_zoom(self, attrm, old, new):
        if new != self.zoom_state:
            self.zoom_state_old = self.zoom_state
            self.zoom_state = int(new)
            range_diff = (self.view_ranges[self.zoom_state_old] - self.view_ranges[self.zoom_state]) * 0.5
            self.fig.x_range.start += range_diff * self.aspect_factor
            self.fig.x_range.end -= range_diff * self.aspect_factor
            self.fig.y_range.start += range_diff
            self.fig.y_range.end -= range_diff

            self._update_zoom_visibility(self.zoom_state)

    def _update_zoom_visibility(self, zoom_state: int) -> None:
        # adjust all texts defined in zoom_now_show_texts
        for zoom_obj in self.zoom_objects:
            zoom_obj.update_zoom_visibility(zoom_state)

    def _change_figure_visibility(self, visible: bool) -> None:
        if visible and self.water_route_graph:
            self.fig.x_range.start = self.water_route_graph.origin_x + \
                                     (self.water_route_graph.width -
                                      self.view_ranges[self.zoom_state_init] * self.aspect_factor) * 0.5
            self.fig.x_range.end = self.water_route_graph.origin_x + \
                                   (self.view_ranges[self.zoom_state_init] * self.aspect_factor +
                                    self.water_route_graph.width) * 0.5
        else:
            self.fig.x_range.start = 1
            self.fig.x_range.end = 1

    def _update_graph(self) -> None:
        # 3.1 update the figure ranges
        # put graph in the middle of the canvas in x direction
        self.fig.x_range.start = self.water_route_graph.origin_x + \
                                 (self.water_route_graph.width -
                                  self.view_ranges[self.zoom_state_init] * self.aspect_factor) * 0.5
        self.fig.x_range.end = self.water_route_graph.origin_x + \
                               (self.view_ranges[self.zoom_state_init] * self.aspect_factor +
                                self.water_route_graph.width) * 0.5

        self.fig.y_range.start = self.water_route_graph.origin_y + (self.water_route_graph.height -
                                                                    self.view_ranges[self.zoom_state_init]) * 0.5
        self.fig.y_range.end = self.water_route_graph.origin_y + (self.water_route_graph.height +
                                                                  self.view_ranges[self.zoom_state_init]) * 0.5

        self.text_names.initialized = True
        self.text_info.initialized = True
        self._update_zoom_visibility(self.zoom_state_init)
        self.zoom_state = self.zoom_state_init
        self.zoom_state_old = self.zoom_state_init
        self.zoom_slider.value = self.zoom_state_init

        # 1. generate data dicts

        # 1.1 Water routes
        self.ds_main_water.data = self.water_route_graph.main_water_route_beziers
        self.ds_bypass.data = self.water_route_graph.bypass_routes_beziers
        self.ds_spillage.data = self.water_route_graph.spill_routes_beziers

        # Oceans
        self.ds_oceans.data = self._generate_ocean_beziers(self.water_route_graph.oceans_coordinates)
        self.ds_oceans_bypass.data = self._generate_ocean_beziers(self.water_route_graph.oceans_bypass_coordinates)
        self.ds_oceans_spillage.data = self._generate_ocean_beziers(self.water_route_graph.oceans_spillage_coordinates)

        # 1.2 reservoirs
        self.reservoirs_data_dict = self.water_route_graph.reservoir_coordinates
        reservoirs_dummy = {k: v for k, v in self.reservoirs_data_dict.items()}
        reservoirs_dummy['xs'] = list(reservoirs_dummy['xs'])
        reservoirs_dummy['ys'] = list(reservoirs_dummy['ys'])
        reservoirs_dummy['x'] = list(reservoirs_dummy['x'])
        reservoirs_dummy['y'] = list(reservoirs_dummy['y'])
        self.ds_reservoirs.data = reservoirs_dummy

        # shadows reservoirs
        shadow_dict_res = {}
        if len(self.reservoirs_data_dict['x']) > 0:
            shadow_dict_res['xs'] = list(self.reservoirs_data_dict['x'] + self.shadow_offset)
            shadow_dict_res['ys'] = list(self.reservoirs_data_dict['y'] + self.shadow_offset)
        else:
            shadow_dict_res['xs'] = list()
            shadow_dict_res['ys'] = list()
        self.ds_shadows_reservoirs.data = shadow_dict_res

        # 1.3 power stations
        self.power_station_data_dict = self.water_route_graph.all_power_stations_coordinates
        # self.ds_power_stations.data = {k: list(v) for k, v in self.power_station_data_dict.items()}  # 1

        # shadows power stations
        shadow_dict_ps = {}  # self.power_station_data_dict.copy()
        if len(self.power_station_data_dict['x']) > 0:
            shadow_dict_ps['xs'] = list(self.power_station_data_dict['x'] + self.shadow_offset)
            shadow_dict_ps['ys'] = list(self.power_station_data_dict['y'] + self.shadow_offset)
        else:
            shadow_dict_ps['xs'] = list()
            shadow_dict_ps['ys'] = list()
        self.ds_shadow_power_stations.data = shadow_dict_ps

        # 1.3.1 power stations meta info
        self._generate_power_station_meta_info(
            list(self.water_route_graph.dh_tag_obj['power_stations'].values()) +
            list(self.water_route_graph.dh_tag_obj['pump_stations'].values()) +
            list(self.water_route_graph.dh_tag_obj['pure_pumps'].values()))
        self.ds_power_stations.data = {k: list(v) for k, v in self.power_station_data_dict.items()}  # 2

        # 1.2.1 reservoir meta info at the end since it takes time
        self._generate_reservoir_meta_info(list(self.water_route_graph.dh_tag_obj['reservoirs'].values()))
        reservoirs_dummy = {k: v for k, v in self.reservoirs_data_dict.items()}
        reservoirs_dummy['xs'] = list(reservoirs_dummy['xs'])
        reservoirs_dummy['ys'] = list(reservoirs_dummy['ys'])
        reservoirs_dummy['x'] = list(reservoirs_dummy['x'])
        reservoirs_dummy['y'] = list(reservoirs_dummy['y'])
        self.ds_reservoirs.data = reservoirs_dummy

        # 2.5 Text
        self.text_names.initialized = False
        self.text_names.update_callback()
        self.text_info.initialized = False
        self.text_info.update_callback()

    def _clear_figure(self) -> None:
        """
        clear the figure
        """
        self.ds_main_water.data = {k: [] for k in self.ds_main_water.data.keys()}
        self.ds_bypass.data = {k: [] for k in self.ds_bypass.data.keys()}
        self.ds_spillage.data = {k: [] for k in self.ds_spillage.data.keys()}

        # 4.2 reservoir and power stations
        # 4.2.1 shadows
        self.ds_shadows_reservoirs.data = {k: [] for k in self.ds_shadows_reservoirs.data.keys()}
        self.ds_shadow_power_stations.data = {k: [] for k in self.ds_shadow_power_stations.data.keys()}

        # 4.2.2 mad
        self.ds_reservoirs.data = {k: [] for k in self.ds_reservoirs.data.keys()}
        self.ds_power_stations.data = {k: [] for k in self.ds_power_stations.data.keys()}
        self.reservoirs_data_dict = {}
        self.power_station_data_dict = {}

        # 4.2.3 oceans
        self.ds_oceans.data = {k: [] for k in self.ds_oceans.data.keys()}
        self.ds_oceans_spillage.data = {k: [] for k in self.ds_oceans_spillage.data.keys()}
        self.ds_oceans_bypass.data = {k: [] for k in self.ds_oceans_bypass.data.keys()}

        # texts
        self.ds_names.data = {k: [] for k in self.ds_names.data.keys()}
        self.ds_info_text.data = {k: [] for k in self.ds_info_text.data.keys()}

    def _generate_reservoir_meta_info(self, reservoirs: List[Any]) -> None:
        """"
        Generate meta info for reservoirs and add it to the reservoir patches dict

        :param
               reservoirs: list

        :return reservoir_dict: dict
        """
        if len(reservoirs) == 0:
            return
        raw_data = list(zip(*[[rs.name, 'Reservoir', rs.id] for rs in reservoirs]))

        self.reservoirs_data_dict['name'] = list(raw_data[0])
        self.reservoirs_data_dict['type'] = list(raw_data[1])
        self.reservoirs_data_dict['id'] = list(raw_data[2])

    def _generate_power_station_meta_info(self, power_stations: List[Any]) -> None:
        """"
        Generate meta info for power-stations and add it to the reservoir patches dict

        :param power_stations: list
        """
        if len(power_stations) == 0:
            return
        raw_data = list(zip(*[[ps.name, 'Power Station', ps.id] for ps in power_stations]))
        self.power_station_data_dict['name'] = list(raw_data[0])
        self.power_station_data_dict['type'] = list(raw_data[1])
        self.power_station_data_dict['id'] = list(raw_data[2])

    @staticmethod
    def _generate_ocean_beziers(ocean_dict: Dict[str, List[np.ndarray]]) -> Dict[str, List[np.ndarray]]:
        """
        Generate data dictionary for ocean glyphs

        2 wave like beziers as symbol for each ocean

        :param ocean_dict: dict

        :return bezier_dict: dict
        """
        if ocean_dict['tags']:
            offset_y = ocean_dict['height'] * 0.2
            x_min = ocean_dict['origin_x']
            x_max = ocean_dict['origin_x'] + ocean_dict['width']
            x_mid = ocean_dict['origin_x'] + ocean_dict['width'] * 0.5

            y_mean = ocean_dict['origin_y'] + ocean_dict['height'] * 0.5
            y_m = y_mean - offset_y
            y_p = y_mean + offset_y
            n_oceans = len(x_min)

            bezier_dict = {'sx': np.array([x_min, x_min]).reshape(2 * n_oceans),
                           'sy': np.array([y_m, y_p]).reshape(2 * n_oceans),
                           'ex': np.array([x_max, x_max]).reshape(2 * n_oceans),
                           'ey': np.array([y_m, y_p]).reshape(2 * n_oceans),
                           'c1x': np.array([x_mid, x_mid]).reshape(2 * n_oceans),
                           'c1y': np.array([y_mean, y_p + offset_y]).reshape(2 * n_oceans),
                           'c2x': np.array([x_mid, x_mid]).reshape(2 * n_oceans),
                           'c2y': np.array([y_m - offset_y, y_mean]).reshape(2 * n_oceans)
                           }
        else:
            bezier_dict = {'sx': [],
                           'sy': [],
                           'ex': [],
                           'ey': [],
                           'c1x': [],
                           'c1y': [],
                           'c2x': [],
                           'c2y': [],
                           }
        return bezier_dict

    def _update_name_text(self) -> None:
        text_name_data_dict = {'x': [], 'y': [], 'texts': []}
        for dict_i in [self.reservoirs_data_dict, self.power_station_data_dict]:
            if len(dict_i['origin_x']) == 0:
                continue
            text_name_data_dict['x'].extend(dict_i['origin_x'] + 2)
            text_name_data_dict['y'].extend(
                dict_i['origin_y'] + dict_i['height'] - self.text_names.current_font_size - 5)
            text_name_data_dict['texts'].extend([name[:14].replace('_', ' ') for name in dict_i['name']])

        self.ds_names.data = text_name_data_dict

    def _update_info_text(self) -> None:
        text_info_data_dict = {'x': [], 'y': [], 'texts': []}
        for dict_i in [self.reservoirs_data_dict, self.power_station_data_dict]:
            text_info_data_dict['x'].extend(dict_i['origin_x'] + 0.28 * dict_i['width'])
            text_info_data_dict['y'].extend(dict_i['origin_y'] + 0.45 * dict_i['height'])
            text_info_data_dict['texts'].extend([f'{tag}' for tag in dict_i['tags']])
        self.ds_info_text.data = text_info_data_dict

