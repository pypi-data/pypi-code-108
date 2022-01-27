from typing import Dict, List, Tuple

import bokeh.models
from bokeh.plotting import figure as bokeh_figure

from shyft.dashboard.base.ports import Receiver

from shyft.dashboard.maps.map_layer import MapLayer
from shyft.dashboard.maps.base_map import BaseMap
from shyft.dashboard.maps.map_axes import MapAxesRanges
from shyft.dashboard.maps.layer_data import LayerDataHandle


class MapViewer:
    """
    MapViewer
    Backend for plots of Maps with custom layers

    Examples
    --------
    | from statkraft.bokeh.maps.map_viewer import MapViewer
    | from statkraft.bokeh.maps.layer_data import LayerDataHandle
    | from statkraft.bokeh.maps.map_layer import MapLayer
    | from statkraft.bokeh.test.maps.test_map_fixtures import basemap_factory
    |
    | # initialisation
    | base_map = basemap_factory()
    | # create map viewer
    | map_viewer = MapViewer(width=300, height=300, base_map=base_map, extent_padding=10)
    | # add layer
    | layer1 = MapLayer(map_viewer=map_viewer, name='first layer', layer_type=LayerType.POINT,
    |                   glyph_fixed_kwargs={'radius': 5},
    |                   glyph_variable_kwargs={'x': 'x', 'y': 'y'},
    |                   )
    | # update the data with layer_data_handle
    | min_x = 26621 + 22373*0.5 + 50
    | min_y = 6599653 + 18731*0.5 + 50
    | max_x = 26621 + 22373*0.5 + 100
    | max_y = 6599653 + 18731*0.5 + 100
    |
    | updated_data = {'x': [min_x, max_x],
    |                 'y': [min_y, max_y]}
    | layer_data_handle = LayerDataHandle(map_layer=layer1, data=updated_data)
    |
    | map_viewer.receive_layer_data_handles([layer_data_handle])
    """

    def __init__(self, *, base_map: BaseMap, width: int = 300, height: int = 300, extent_padding: float = 0) -> None:
        """
        MapViewer
        Backend for plots of Maps with custom layers

        Parameters
        ----------
        base_map:
            BaseMap instance to use in the back ground
        width:
            with of the figure
        height:
            height of the figure
        extent_padding:
            extra padding for the axis, when snapping to all objects in layers
        """
        self.base_map = base_map
        self.fig_axes_ranges = MapAxesRanges(width=width, height=height, padding=extent_padding)

        self.zoom = bokeh.models.WheelZoomTool()
        self.pan = bokeh.models.PanTool()

        self.layers: Dict['statkraft.bokeh.composables.aqua_composables.Layer': bokeh.models.Renderer] = {}

        self.base_tools = [self.zoom, self.pan]
        self.hover_tools = []

        self.legend = bokeh.models.Legend()
        self.bokeh_figure = bokeh_figure(tools=self.base_tools,
                                         lod_threshold=None,
                                         plot_width=width,
                                         plot_height=height,
                                         background_fill_color='white',
                                         active_scroll=self.zoom,
                                         active_drag=self.pan,
                                         match_aspect=True  # TODO: Map needs equal axes. This arg implemented in bokeh 0.12.7. For now, map must be square.
                                         )
        self.bokeh_figure.axis.visible = False
        self.fig_axes_ranges.bind(parent=self)

        self.receive_layer_data_handles = Receiver(parent=self, name="receive layer data to update map layer",
                                                   signal_type=List[LayerDataHandle], func=self._receive_layer_data_handles)

        if self.base_map:
            self.bokeh_figure.add_tile(self.base_map.tiles)

        self.layout = self.bokeh_figure

    def add_layer(self, map_layer: MapLayer) -> Tuple[bokeh.models.Renderer, bokeh.models.HoverTool]:
        """
        Function to add a new layer to the Map
        This is called from the Layer constructor
        """
        renderer = self.bokeh_figure.add_glyph(map_layer.source, map_layer.glyph)
        hover_tool = None
        if map_layer.hover_tool_tips is not None:
            hover_tool = bokeh.models.HoverTool(renderers=[renderer], tooltips=map_layer.hover_tool_tips)
            self.bokeh_figure.add_tools(hover_tool)
        # register renderer
        self.layers[map_layer] = renderer
        return renderer, hover_tool

    # def _add_legend_items(self, *, text: str, glyphs: list) -> None:
    #     self.legend.items = [item for item in self.legend.items if
    #                          not item.label == text]  # Remove previous items with matching labels.
    #     self.legend.items.append(bokeh.models.LegendItem(label=text, renderers=glyphs))

    def update_axes(self) -> None:
        """
        This function updates the figure axis based on layer bbox
        """
        bounds_list = []
        for layer in self.layers.keys():
            if not layer.update_axes:
                continue
            bbox = layer.bbox
            if bbox is None:
                continue
            bounds_list.append(bbox)

        if bounds_list:
            self.fig_axes_ranges.set_axes_bounds_from_bounds_list(bounds_list)

    def _receive_layer_data_handles(self, layer_data_list: List[LayerDataHandle]) -> None:
        """
        receiver function to receive new data handles
        """
        # update data of layers
        for layer_data_handle in layer_data_list:
            if layer_data_handle.map_layer not in self.layers.keys():
                continue
            layer_data_handle.map_layer.updated_data(new_data=layer_data_handle.data)
        # update axes
        self.update_axes()
