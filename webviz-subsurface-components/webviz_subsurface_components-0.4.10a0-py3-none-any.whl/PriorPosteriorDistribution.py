# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class PriorPosteriorDistribution(Component):
    """A PriorPosteriorDistribution component.


Keyword arguments:

- id (string; required)

- data (dict; default { iterations: [], labels: [], values: [] })

- height (number; default 700)"""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, height=Component.UNDEFINED, data=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'data', 'height']
        self._type = 'PriorPosteriorDistribution'
        self._namespace = 'webviz_subsurface_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'data', 'height']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(PriorPosteriorDistribution, self).__init__(**args)
