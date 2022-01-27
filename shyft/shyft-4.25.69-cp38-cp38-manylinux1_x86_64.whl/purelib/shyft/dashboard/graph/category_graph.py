import numpy as np
from packaging import version
from typing import List, Tuple, NamedTuple, Dict, Any, Optional

import bokeh
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.core.properties import value
from bokeh.models import ColumnDataSource, Range1d, TapTool, WheelPanTool, Patches, Model, LayoutDOM

from shyft.dashboard.base.app import Widget
from shyft.dashboard.widgets.zoomables import LabelSetZoomable
from shyft.util.layoutgraph import LayoutGraph, ghost_object_factory
from shyft.dashboard.base.ports import (States, Receiver, Sender, connect_ports, StatePorts)


# Graph category objects
class BaseGraphObject:
    def __init__(self, tag, name, config_key) -> None:
        self.tag = tag
        self.name = name
        self.config_key = config_key


class GraphConnectionData(NamedTuple):
    edge_objects: List[BaseGraphObject]
    start_objects: List[BaseGraphObject]
    end_objects: List[BaseGraphObject]
    edge_layout_keys: List[str]
    revers_dirs: List[bool] = None


class GraphContainerData(NamedTuple):
    node_objects: List[BaseGraphObject]
    object_layout_keys: List[str]


class ExpandCollapseIcons(Widget):

    def __init__(self, color_expandable: str='', color_collapsible: str= '') -> None:
        super(ExpandCollapseIcons, self).__init__()

        self.ds_keys = ['xs', 'ys', 'color', 'tags']
        self.ds = ColumnDataSource({k: [] for k in self.ds_keys})
        self.patches = Patches(xs="xs", ys="ys", fill_alpha=0.51, line_alpha=1.0, line_width=1.0, fill_color='color',
                               line_color='black')
        self.data = {k: [] for k in self.ds_keys}
        self.ds.selected.on_change('indices', self.expand_collapse)

        self.color_expandable = color_expandable or '#279171'
        self.color_collapsible = color_collapsible or '#ff8446'
        self.color_toggle = {self.color_expandable: self.color_collapsible,
                             self.color_collapsible: self.color_expandable}
        self.set_selection = self.update_value_factory(self.ds.selected, 'indices')

        self.send_selected_icons = Sender(parent=self, name='send selected icons', signal_type=str)

    @property
    def layout(self) -> Optional[LayoutDOM]:
        return None

    @property
    def glyphs(self) -> Tuple[ColumnDataSource, Model]:
        return self.ds, self.patches

    @property
    def layout_components(self) -> Dict[str, List[Any]]:
        return {'widgets': [], 'figures': []}

    def add_icons(self,
                  tags: np.ndarray,
                  x_origin: np.ndarray,
                  y_origin: np.ndarray,
                  size: np.ndarray,
                  visibility: List[bool]) -> None:

        self.data['tags'].extend(tags)
        self.data['color'].extend([[self.color_expandable, self.color_collapsible][m] for m in visibility])

        self.data['xs'].extend(np.array([x_origin, x_origin+size, x_origin+size, x_origin]).T)
        self.data['ys'].extend(np.array([y_origin, y_origin, y_origin + size, y_origin + size]).T)

    def update_data_source(self) -> None:
        self.ds.data = self.data.copy()

    def clear(self) -> None:
        self.ds.data = {k: [] for k in self.ds_keys}
        self.data = {k: [] for k in self.ds_keys}

    def expand_collapse(self, attr, old, new):
        self.set_selection([])
        selected_indices = new
        if not selected_indices:
            return
        index = selected_indices[0]
        self.ds.patch({'color': [(index, self.color_toggle[self.data['color'][index]])]})

        selected_tag = self.data['tags'][index]
        self.send_selected_icons(selected_tag)


class CategoryGraph(Widget):

    def __init__(self, *,
                 height: int,
                 width: int = None,
                 aspect_factor: float = 4.5,
                 text_font: str = 'monospace',
                 text_font_style: str = 'bold') -> None:
        """
        Draws a categorical graph of items in a Bokeh plot.
        The graph layout is created with graphiz and pydot, based on the shyft.util.layput_graph pkg.

        The graph objects and graph connections are added with the function generate_graph.

        Args:
            height: figure height
            width: figure width
            aspect_factor: aspect factor between with and height, can be added instead of width default 4.5
            text_font: the text font (options: 'monospace','verdana', 'times', 'helvetica', etc.)
            text_font_style: style of the font (options: 'normal', 'italic' or 'bold')
        """

        super(CategoryGraph, self).__init__()
        if width:
            aspect_factor = width/height

        self.aspect_factor = aspect_factor or 4.5
        figure_width = height * self.aspect_factor
        figure_height = height
        self.wheel_pan = WheelPanTool()
        self.wheel_pan.dimension = 'width'

        self.layout_graph = None

        self.fig = figure(plot_width=int(figure_width), plot_height=int(figure_height),
                          x_axis_location=None, y_axis_location=None,
                          toolbar_location=None, tools=[self.wheel_pan, 'pan', 'zoom_in', 'zoom_out'])
        self.fig.grid.grid_line_color = None
        self.fig.toolbar.active_scroll = self.wheel_pan

        self.view_ranges = [750, 500, 300, 100, 75]  # range of the view in y direction
        self.zoom_state_init = 2
        self.fig.x_range = Range1d(0, self.view_ranges[self.zoom_state_init] * self.aspect_factor)
        self.fig.y_range = Range1d(0, self.view_ranges[self.zoom_state_init])

        self.ds_connections = ColumnDataSource({k: [] for k in ['sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y', 'color']})

        self.ds_category_keys = ['xs', 'ys', 'alpha', 'color', 'selection_line_color', 'selection_fill_color',
                                 'nonselection_color', 'tags']
        self.ds_category = ColumnDataSource({k: [] for k in self.ds_category_keys})
        self.category_dict = {}

        self.ds_names = ColumnDataSource({key: [] for key in ['x', 'y', 'texts']})
        self.bezier_connections = self.fig.bezier('sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y',
                                                  source=self.ds_connections, color='color', alpha=0.8,
                                                  line_dash='solid', line_width=1.5, visible=True)

        patches_category = self.fig.patches('xs', 'ys',
                                            source=self.ds_category,
                                            alpha='alpha',
                                            line_width=0,
                                            color='color',
                                            hover_line_color="#ce7f00",
                                            hover_fill_color='#dae8e3',
                                            selection_line_color='selection_line_color',
                                            selection_fill_color='selection_fill_color',
                                            selection_fill_alpha=1.0,
                                            nonselection_alpha=0.4,
                                            nonselection_color='nonselection_color'
                                            )

        self.exp_coll_single = ExpandCollapseIcons('#16a5d1', '#d14e15')
        renders_exp_coll = self.fig.add_glyph(*self.exp_coll_single.glyphs)

        self.exp_coll_all = ExpandCollapseIcons('#c2c031', '#cc3aa0')
        renders_exp_coll_all = self.fig.add_glyph(*self.exp_coll_all.glyphs)

        text_font = text_font if version.parse(bokeh.__version__) < version.Version("2.3.0") else value(text_font)

        self.text_names = LabelSetZoomable(dict(x='x', x_units='data', y='y', y_units='data', text='texts',
                                                source=self.ds_names, text_color='black',
                                                text_font=text_font, text_font_style=text_font_style),
                                           ['0pt', '6pt', '10pt', '11.8pt', '13.4pt'],
                                           self.zoom_state_init)
        self.text_names.set_update_callback(self._update_name_text)
        self.fig.add_layout(self.text_names.glyph)
        # callback for zooom
        #       self.zoom_state = self.zoom_state_init
        #        self.zoom_state_old = self.zoom_state_init
        #        self.zoom_objects = [self.text_info, self.text_names, checkbox_water_way_visibility]
        #        self.zoom_slider = Slider(start=0, end=len(self.view_ranges) - 1, value=self.zoom_state_init, step=1, title="Zoom", width=300)
        #        self.zoom_slider.on_change('value', self._updated_zoom)

        self.tap_tool = TapTool(renderers=[patches_category, renders_exp_coll, renders_exp_coll_all])
        self.fig.add_tools(self.tap_tool)
        self.ds_category.selected.on_change('indices', self._callback_selection_category)
        self.set_selected_category = self.update_value_factory(self.ds_category.selected, 'indices')

        self._layout = row(self.fig)

        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        self.state = States.ACTIVE

        self.receive_expand_single = Receiver(parent=self, name='receive selected icons single',
                                              func=self._receive_expand_single, signal_type=str)

        connect_ports(self.exp_coll_single.send_selected_icons,
                      self.receive_expand_single)

        self.receive_expand_all = Receiver(parent=self, name='receive selected icons all',
                                           func=self._receive_expand_all, signal_type=str)

        connect_ports(self.exp_coll_all.send_selected_icons,
                      self.receive_expand_all)

        self.send_selected_categories = Sender(parent=self, name='send selected categories', signal_type=Optional[List[BaseGraphObject]])

        self.category_bokeh_attrib = {'alpha': 1,
                                      'color': '#cc990e',
                                      'selection_line_color': "#cc990e",
                                      'selection_fill_color': '#b2bfc1',
                                      'nonselection_color': '#FF9900'
                                      }
        self.connection_bokeh_attrib = {'color': '#030203'}

        self.bokeh_config = {}
        self.bezier_tags = {}
        self.container_tags = {}

    @property
    def layout(self) -> LayoutDOM:
        return self._layout

    def _receive_state(self, state: States) -> None:
        """
        This function handles receiving of States connected to the state_port
        """
        if state == States.ACTIVE:
            self.state = state
            # Not sending active state since this only done if we can send data to the next widget
        elif state == States.DEACTIVE:
            self.clear_figure()
            self.state = state
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)

    def generate_graph(self,
                       container: List[GraphContainerData],
                       connections: List[GraphConnectionData],
                       collapse_children: List[str]=None,
                       pydot_config: Dict=None,
                       bokeh_config: Dict=None) -> None:
        """
        Main function to generate a category graph

        Parameters
        ----------
        container:
            all graph objects with config keys
        connections:
            all graph connection objects with config keys
        collapse_children:
            name of all graph objects which are collapsable
        pydot_config:
            Optional dict with graph configuration to adapt layout
        bokeh_config:
            Optional dict with visual configuration of categories or elements
        """
        self.bezier_tags = {}
        self.container_tags = {}

        pydot_config = pydot_config or {}
        self.bokeh_config = bokeh_config or {}

        graph_obj = ghost_object_factory('Graph', 'Graph_01')
        self.layout_graph = LayoutGraph(graph_obj, pydot_config, 'graph')

        for container_data in container:
            self.layout_graph.add_container(container_data.node_objects, container_data.object_layout_keys)
            self.container_tags.update({obj.tag: obj for obj in container_data.node_objects})

        for connection_data in connections:
            self.layout_graph.add_connections(connection_data.edge_objects, connection_data.start_objects,
                                              connection_data.end_objects, connection_data.edge_layout_keys,
                                              revers_dirs=connection_data.revers_dirs)
            self.bezier_tags.update({obj.tag: obj for obj in connection_data.edge_objects})

        # update container widths to make space for the expand collapse buttons
        for uid, container in self.layout_graph.layout_containers.items():
            tag = container.obj.tag
            if not container.has_children:
                continue
            if tag not in pydot_config:
                continue
            if 'width' in pydot_config[tag] and 'height' in pydot_config[tag]:
                w = float(pydot_config[tag]['width']) + float(pydot_config[tag]['height']) * 2.
                pydot_config[tag]['width'] = str(w)
        self.layout_graph.update_graph_layout(pydot_config)

        if collapse_children:
            for tag in collapse_children:
                self.layout_graph.update_children_visibility(tag, True)

        self.layout_graph.generate_graph_coordinates(mirror_graph=True)

    @property
    def tag_children_visibility(self) -> Dict[int, bool]:
        """Figure out which graph elements have visible children, i.e are not collapsed"""
        twc_vis = {}
        for uid, container in self.layout_graph.root_container.layout_containers.items():
            twc_vis[self.layout_graph.inv_tag_uid_map[uid]] = container.has_visible_children
        return twc_vis

    def draw_graph(self) -> None:
        """ This function draws the graph, i.e, updates all patches and the figure"""

        self.clear_figure()
        # 3.1 update the figure ranges
        # put graph in the middle of the canvas in x direction
        self.fig.x_range.start = self.layout_graph.origin_x+(self.layout_graph.width -
                                                               self.view_ranges[self.zoom_state_init] *
                                                               self.aspect_factor)*0.5
        self.fig.x_range.end = self.layout_graph.origin_x + (self.view_ranges[self.zoom_state_init] *
                                                               self.aspect_factor
                                                               + self.layout_graph.width) * 0.5

        self.fig.y_range.start = self.layout_graph.origin_y + (self.layout_graph.height
                                                                 - self.view_ranges[self.zoom_state_init]) * 0.5
        self.fig.y_range.end = self.layout_graph.origin_y + (self.layout_graph.height
                                                               + self.view_ranges[self.zoom_state_init]) * 0.5

        # add connections
        if self.bezier_tags:
            data = self.layout_graph.get_connection_beziers(self.bezier_tags.keys())

            for bokeh_style_attrib, default_val in self.connection_bokeh_attrib.items():
                if bokeh_style_attrib not in data:
                    data[bokeh_style_attrib] = []
                data[bokeh_style_attrib].extend([self.bokeh_config[self.bezier_tags[tag].config_key][bokeh_style_attrib]
                                                 if self.bezier_tags[tag].config_key in self.bokeh_config and
                                                 bokeh_style_attrib in self.bokeh_config[self.bezier_tags[tag].config_key]
                                                 else default_val for tag in data['tags']])
            self.ds_connections.data = data

        tag_children_visibility = self.tag_children_visibility

        self.category_dict = {}
        d = {k: [] for k in self.ds_category_keys}
        if self.container_tags:
            data = self.layout_graph.get_container_coordinates(self.container_tags.keys())
            for bokeh_style_attrib, default_val in self.category_bokeh_attrib.items():
                if bokeh_style_attrib not in d:
                    d[bokeh_style_attrib] = []
                d[bokeh_style_attrib].extend([self.bokeh_config[self.container_tags[tag].config_key][bokeh_style_attrib]
                                              if self.container_tags[tag].config_key in self.bokeh_config and
                                              bokeh_style_attrib in self.bokeh_config[self.container_tags[tag].config_key]
                                              else default_val for tag in data['tags']])

            d['tags'].extend(data['tags'])

            has_children = np.array([tag_children_visibility[tag] in [True, False] for tag in data['tags']])
            color_mask = [tag_children_visibility[tag] for tag in data['tags'] if tag_children_visibility[tag] is not None]

            ox = data['origin_x'] + data['width'] - data['height']
            self.exp_coll_all.add_icons(np.array(data['tags'])[has_children],
                                        ox[has_children],
                                        data['origin_y'][has_children],
                                        data['height'][has_children],
                                        visibility=color_mask)
            ox2 = ox - data['height']
            self.exp_coll_single.add_icons(np.array(data['tags'])[has_children],
                                           ox2[has_children],
                                           data['origin_y'][has_children],
                                           data['height'][has_children],
                                           visibility=color_mask)

            data['xs'] = np.array(data['xs'])
            for i in [0, 3, 4]:
                data['xs'][:, i][has_children] = data['xs'][:, i][has_children]-2.*data['height'][has_children]

            d['xs'].extend(data['xs'])
            d['ys'].extend(data['ys'])
            self.category_dict = data

        self.ds_category.data = d
        self.exp_coll_single.update_data_source()
        self.exp_coll_all.update_data_source()

        self._update_name_text()

    def _update_name_text(self) -> None:
        """Writes the name in the patches of the categories"""
        text_name_data_dict = {'x': [], 'y': [], 'texts': []}
        if len(self.category_dict['origin_x']) > 0:
            text_name_data_dict['x'].extend(self.category_dict['origin_x'] + 1.)
            text_name_data_dict['y'].extend(self.category_dict['origin_y'] + 1.)
            text_name_data_dict['texts'].extend([self.container_tags[tag].name.title() for tag in self.category_dict['tags']])

        self.ds_names.data = text_name_data_dict

    def clear_figure(self) -> None:
        """
        clear the figure
        """
        # reset data sources
        self.ds_category.data = {k: [] for k in self.ds_category_keys}
        self.ds_connections.data = {k: [] for k in ['sx', 'sy', 'ex', 'ey', 'c1x', 'c1y', 'c2x', 'c2y', 'color']}
        self.ds_names.data = {key: [] for key in ['x', 'y', 'texts']}
        self.set_selected_category([])
        self.exp_coll_single.clear()
        self.exp_coll_all.clear()
        self.fig.y_range.start = 0
        self.fig.y_range.end = 0

    def _receive_expand_single(self, tag: str) -> None:
        """
        Handle receive of collapse/expand signal of on layer
        """
        self.layout_graph.update_children_visibility(tag, False)
        self.layout_graph.generate_graph_coordinates(mirror_graph=True)
        self.draw_graph()

    def _receive_expand_all(self, tag: str) -> None:
        """
        Handle receive of collapse/expand signal of all child layer
        """
        self.layout_graph.update_children_visibility(tag, True)
        self.layout_graph.generate_graph_coordinates(mirror_graph=True)
        self.draw_graph()

    def _callback_selection_category(self, attrnm, old, new):
        """
        Callback on click selected category
        """
        selected_indices = new
        if not selected_indices:
            return
        selected_tags = [self.ds_category.data['tags'][index] for index in selected_indices]
        graph_obj = [self.container_tags[tag] for tag in selected_tags if tag in self.container_tags]
        self.send_selected_categories(graph_obj)

    @property
    def layout_components(self)-> Dict[str, List[Any]]:
        """Returns layout components"""
        return {'widgets': [], 'figures': [self.fig]}
