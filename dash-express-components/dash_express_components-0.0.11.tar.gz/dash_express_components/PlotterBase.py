# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class PlotterBase(Component):
    """A PlotterBase component.


Keyword arguments:

- id (optional):
    The config the user sets in this component.

- allColOptions (optional):
    All currently available column options.

- catColOptions (optional):
    Currently available categorical options.

- config (optional):
    The config the user sets in this component.

- numColOptions (optional):
    Currently available numerical options.

- numOptions (optional):
    Currently available options without grouping.

- setProps (optional):
    Dash-assigned callback that should be called to report property
    changes to Dash, to make them available for callbacks."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, config=Component.UNDEFINED, allColOptions=Component.UNDEFINED, catColOptions=Component.UNDEFINED, numColOptions=Component.UNDEFINED, numOptions=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'allColOptions', 'catColOptions', 'config', 'numColOptions', 'numOptions', 'setProps']
        self._type = 'PlotterBase'
        self._namespace = 'dash_express_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'allColOptions', 'catColOptions', 'config', 'numColOptions', 'numOptions', 'setProps']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(PlotterBase, self).__init__(**args)
