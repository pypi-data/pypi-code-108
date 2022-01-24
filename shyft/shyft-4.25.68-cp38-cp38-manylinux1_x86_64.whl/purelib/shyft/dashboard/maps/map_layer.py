from enum import Enum
from typing import Dict, Union, List, Optional, Tuple, Set
import numpy as np
import bokeh.models
from shyft.dashboard.base.hashable import Hashable
from shyft.dashboard.time_series.bindable import Bindable, BindableError


class MapLayerError(RuntimeError):
    pass


class MapLayerType(Enum):
    """
    Enum defining expected keys to create a bokeh glyph
    Note:
        First variable should be x coordinates
        Second variable should be y coordinates
    """
    POINT = ('x', 'y')
    POLYGON = ('xs', 'ys')
    LABEL = ('x', 'y', 'text')


layer_type_glyph_reference = {MapLayerType.POINT: bokeh.models.Circle,
                              MapLayerType.POLYGON: bokeh.models.Patches,
                              MapLayerType.LABEL: bokeh.models.Text}


def find_tags_from_tooltips(tool_tips: List[Tuple[str, str]]) -> Set[str]:
    """
    This function evaluates tooltips for bokeh.Hover for required fields in data source

    Parameters
    ----------
    tool_tips:
        List of Tuples with 2 strings as defiend in bokeh

    Examples
    --------
    | tt = [("Type", "@type"),
    |       ("Name", "@name")]
    | find_tags_from_tooltips(tt)
    | >>> {'type', 'name'}

    Returns
    -------
    a set of required field names
    """
    recording = False
    tag_with_space = False
    new_tag = []
    tags = []
    for _, tag in tool_tips:
        for t in tag:
            if t == '@' and not recording:
                new_tag = []
                recording, tag_with_space = True, False
            elif t == '@' and recording:
                tags.append(new_tag)
                new_tag = []
                recording, tag_with_space = True, False
            elif not recording:
                continue
            elif t == '{' and len(new_tag) == 0:  # start of tag with space
                tag_with_space = True
            elif t == '{' and len(new_tag) > 0:  # start of tag formatting
                tags.append(new_tag)
                new_tag = []
                recording, tag_with_space = False, False
            elif t == ' ' and not tag_with_space:
                tags.append(new_tag)
                new_tag = []
                recording, tag_with_space = False, False
            elif t in ['}', '$']:  # just closing
                tags.append(new_tag)
                new_tag = []
                recording, tag_with_space = False, False
            else:
                new_tag.append(t)
        if new_tag:
            tags.append(new_tag)
            new_tag = []
        recording, tag_with_space = False, False
    return {''.join(t) for t in tags}


class MapLayer(Bindable, Hashable):
    def __init__(self, *,
                 map_viewer: 'statkraft.bokeh.maps.map_viewer.MapViewer',
                 name: str,
                 layer_type: MapLayerType,
                 glyph_variable_kwargs: Dict[str, Union[str, float, int]],
                 glyph_fixed_kwargs: Dict[str, Union[str, float, int]],
                 visible: bool = True,
                 selectable: bool = False,
                 update_axes: bool = True,
                 hover_tool_tips: Optional[List[Tuple[str, str]]] = None) -> None:
        """
        Layer of Map Viewer

        Each layer adds a bokeh glyph to the map. The draw order is controlled by the order the layers are created.
        The type of bokeh glyphs are controlled by the LayerType:
            LayerType.POINT => Circles
            LayerType.POLYGON => Patches

        Labels are only supported for LayerType.POINT

        Parameters
        ----------
        map_viewer:
            MapViewer instance to add this layer to
        name:
            name of the layer
        layer_type:
            type of the layer
        glyph_variable_kwargs:
            glyph variable kwargs which are controlled in the data source e.g. {'xs': 'x_values'}
        glyph_fixed_kwargs:
            glyph fixed kwargs which are set only by initialisation e.g {'color': 'red'}
        visible:
            visibility of the layer at initialisation
        selectable:
            if glyphs can be selected with the selction tool
        update_axes:
            if the bbox of this layer should be used in MapViewer.figure_axis
        hover_tool_tips:
            hover over information
        """
        Hashable.__init__(self)
        Bindable.__init__(self)

        self.name = name
        self.hover_tool_tips = hover_tool_tips
        self.hover_tool = None
        self.selectable = selectable
        self._visible = visible
        self.update_axes = update_axes

        if glyph_variable_kwargs is None:
            raise MapLayerError(f'Map layer {name}: No glyph_variable_kwargs for source defined!')
        tag_diff = set(glyph_variable_kwargs.keys()).symmetric_difference(glyph_fixed_kwargs.keys())
        if len(tag_diff) != len(glyph_variable_kwargs.keys()) + len(glyph_fixed_kwargs.keys()):
            msg = f"""Map layer {self.name}: kwargs are double defined in glyph_variable_kwargs 
            and glyph_fixed_kwargs: {tag_diff} in both!"""
            raise MapLayerError(msg)
        self.source_keys = {v for v in glyph_variable_kwargs.values()}
        if hover_tool_tips:
            required_source_keys = find_tags_from_tooltips(hover_tool_tips)
            self.source_keys.update(required_source_keys)
        # check layer type
        for coordinate_ref in layer_type.value:
            if coordinate_ref not in glyph_variable_kwargs.keys():
                raise MapLayerError(f'Map layer {name}: {coordinate_ref} not defined in bokeh_source_kwargs!')
        self.layer_type = layer_type

        # create bokeh data source
        self.source = bokeh.models.ColumnDataSource({k: [] for k in self.source_keys})
        # create bokeh glyph
        try:
            self.glyph = layer_type_glyph_reference[self.layer_type](**glyph_variable_kwargs, **glyph_fixed_kwargs)
        except (RuntimeError, AttributeError) as e:
            raise MapLayerError(f'Map layer {name}: cannot create bokeh glyph! {e}')

        # bokeh renderer
        self.renderer = None
        self.hover_tool = None
        # bind to the map provided
        self.bind(parent=map_viewer)

    def on_bind(self, *, parent: 'statkraft.bokeh.maps.map_viewer.MapViewer') -> None:
        """
        Function which is call when bound to a figure
        """
        try:
            self.renderer, self.hover_tool = parent.add_layer(self)
        except (RuntimeError, AttributeError) as e:
            raise BindableError(f"Cannot bind to {parent}: {e}")
        # set visibility of the renderer
        self.renderer.visible = self._visible

    @property
    def bbox(self) -> Optional[Tuple[float, float, float, float]]:
        """
        returns bounding box of defined geometry i.e x_min, y_min, x_max, y_max if data is defined
        """
        layer_ref = self.layer_type.value
        if len(layer_ref) < 2:
            raise MapLayerError(f"Layer type not proper defined {self.layer_type}")
        x_ref, y_ref = layer_ref[0], layer_ref[1]
        x_coords = self.source.data[x_ref]
        y_coords = self.source.data[y_ref]
        if len(x_coords) == 0 or len(y_coords) == 0:
            return None
        return np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords)

    def check_data_compatibility(self, new_data: Dict[str, Union[List[str], List[int], List[float]]]) -> None:
        """
        This function checks if new data is compatible with layer
        Raises
        ------
        LayerError when incompatible
        """
        expected_keys = self.source_keys
        if len(set(new_data.keys()).symmetric_difference(expected_keys)):
            diff = set(new_data.keys()).symmetric_difference(expected_keys)
            raise MapLayerError(f'Map layer {self.name}: cannot update data, different keys defined {diff}!')
        if not all(isinstance(x, list) for x in new_data.values()):
            t = ' '.join([f'{k}: {type(v)}' for k, v in new_data.items()])
            raise MapLayerError(f'Map layer {self.name}: cannot update data, not all values of data are type list: {t}!')
        n = len(list(new_data.values())[0])
        if not all(len(x) == n for x in new_data.values()):
            l = ' '.join([f'{k}: {len(v)}' for k, v in new_data.items()])
            raise MapLayerError(f'Map layer {self.name}: cannot update data, different variable lengths defined: {l}!')

    def updated_data(self, new_data: Dict[str, Union[List[str], List[int], List[float]]]) -> None:
        """
        This function is updates the layer data if proper defined
        """
        self.check_data_compatibility(new_data)
        self.source.data = new_data

    @property
    def visible(self) -> bool:
        """
        Visibility of the glyph
        """
        return self._visible

    @visible.setter
    def visible(self, vis: bool) -> None:
        """
        Setter of visibility
        """
        if vis == self._visible:
            return
        self._visible = vis
        if self.renderer is not None:
            self.renderer.visible = self._visible
