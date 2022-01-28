# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DeckGLMap(Component):
    """A DeckGLMap component.


Keyword arguments:

- id (string; required):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- bounds (list of numbers; optional):
    Coordinate boundary for the view defined as [left, bottom, right,
    top].

- colorTables (list of dicts; default colorTables):
    Prop containing color table data.

- coordinateUnit (string; optional):
    Parameters for the Distance Scale component Unit for the scale
    ruler.

- coords (dict; default {    visible: True,    multiPicking: True,    pickDepth: 10,}):
    Parameters for the InfoCard component.

    `coords` is a dict with keys:

    - multiPicking (boolean; optional):
        Enable or disable multi picking. Might have a performance
        penalty. See
        https://deck.gl/docs/api-reference/core/deck#pickmultipleobjects.

    - pickDepth (number; optional):
        Number of objects to pick. The more objects picked, the more
        picking operations will be done. See
        https://deck.gl/docs/api-reference/core/deck#pickmultipleobjects.

    - visible (boolean; optional):
        Toggle component visibility.

- editedData (dict; optional):
    Prop containing edited data from layers.

- layers (list of dicts; optional):
    List of JSON object containing layer specific data. Each JSON
    object will consist of layer type with key as \"@@type\" and layer
    specific data, if any. Supports both upstream Deck.gl layers and
    custom WebViz layers. See Storybook examples for example layer
    stacks. See also:
    https://deck.gl/docs/api-reference/core/deck#layers.

- legend (dict; default {    visible: True,    position: [5, 10],    horizontal: True,}):
    Parameters for the legend.

    `legend` is a dict with keys:

    - horizontal (boolean; optional):
        Legend layout.

    - position (list of numbers; optional):
        Legend position in pixels.

    - visible (boolean; optional):
        Toggle component visibility.

- resources (dict; optional):
    Resource dictionary made available in the DeckGL specification as
    an enum. The values can be accessed like this:
    `\"@@#resources.resourceId\"`, where `resourceId` is the key in
    the `resources` dict. For more information, see the DeckGL
    documentation on enums in the json spec:
    https://deck.gl/docs/api-reference/json/conversion-reference#enumerations-and-using-the--prefix.

- scale (dict; default {    visible: True,    incrementValue: 100,    widthPerUnit: 100,    position: [10, 10],}):
    Parameters for the Distance Scale component.

    `scale` is a dict with keys:

    - incrementValue (number; optional):
        Increment value for the scale.

    - position (list of numbers; optional):
        Scale bar position in pixels.

    - visible (boolean; optional):
        Toggle component visibility.

    - widthPerUnit (number; optional):
        Scale bar width in pixels per unit value.

- views (dict; default {    layout: [1, 1],    viewport: [{ id: "main-view", show3D: False, layerIds: [] }],}):
    Views configuration for map. If not specified, all the layers will
    be displayed in a single 2D viewport.

    `views` is a dict with keys:

    - layout (list of numbers; optional):
        Layout for viewport in specified as [row, column].

    - viewports (list of dicts; optional):
        Layers configuration for multiple viewport.

        `viewports` is a list of dicts with keys:

        - id (string; optional):

            Viewport id.

        - layerIds (list of strings; optional):

            Layers to be displayed on viewport.

        - show3D (boolean; optional):

            If True, displays map in 3D view, default is 2D view.

- zoom (number; default -3):
    Zoom level for the view."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, resources=Component.UNDEFINED, bounds=Component.UNDEFINED, zoom=Component.UNDEFINED, views=Component.UNDEFINED, layers=Component.UNDEFINED, coords=Component.UNDEFINED, scale=Component.UNDEFINED, coordinateUnit=Component.UNDEFINED, legend=Component.UNDEFINED, editedData=Component.UNDEFINED, colorTables=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'bounds', 'colorTables', 'coordinateUnit', 'coords', 'editedData', 'layers', 'legend', 'resources', 'scale', 'views', 'zoom']
        self._type = 'DeckGLMap'
        self._namespace = 'webviz_subsurface_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'bounds', 'colorTables', 'coordinateUnit', 'coords', 'editedData', 'layers', 'legend', 'resources', 'scale', 'views', 'zoom']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DeckGLMap, self).__init__(**args)
