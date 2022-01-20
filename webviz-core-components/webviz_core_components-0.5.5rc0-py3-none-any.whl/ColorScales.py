# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ColorScales(Component):
    """A ColorScales component.
ColorScales is a Dash wrapper for `react-colorscales`.
It takes an array of colors, `colorscale`, and
displays a UI for modifying it or choosing a new scale.

Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- colorscale (list; optional):
    Optional: Initial colorscale to display. Default is Viridis.

- fixSwatches (boolean; optional):
    Optional: Set to `True` to fix the number of colors in the scale.

- nSwatches (number; optional):
    Optional: Initial number of colors in scale to display."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, colorscale=Component.UNDEFINED, nSwatches=Component.UNDEFINED, fixSwatches=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'colorscale', 'fixSwatches', 'nSwatches']
        self._type = 'ColorScales'
        self._namespace = 'webviz_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'colorscale', 'fixSwatches', 'nSwatches']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(ColorScales, self).__init__(**args)
