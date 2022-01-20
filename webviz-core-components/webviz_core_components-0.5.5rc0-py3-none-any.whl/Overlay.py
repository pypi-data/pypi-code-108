# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Overlay(Component):
    """An Overlay component.


Keyword arguments:

- visible (boolean; required)"""
    @_explicitize_args
    def __init__(self, visible=Component.REQUIRED, onClick=Component.REQUIRED, **kwargs):
        self._prop_names = ['visible']
        self._type = 'Overlay'
        self._namespace = 'webviz_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['visible']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['visible', 'onClick']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Overlay, self).__init__(**args)
