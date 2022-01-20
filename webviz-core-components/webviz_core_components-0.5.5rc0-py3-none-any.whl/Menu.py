# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Menu(Component):
    """A Menu component.
Menu is a component that allows to create an interactive menu with flexible depth that
can be pinned and filtered.

Keyword arguments:

- id (string; default "some-id"):
    The ID used to identify this component in Dash callbacks.

- initiallyCollapsed (boolean; optional):
    Set to True if you want all groups in the menu to be initially
    collapsed.

- initiallyPinned (boolean; default False):
    Set to True if the menu shall be initially shown as pinned.

- menuBarPosition (a value equal to: "left", "top", "right", "bottom"; default "left"):
    Define the position the menu bar shall be displayed at.

- menuDrawerPosition (a value equal to: "left", "right"; default "left"):
    Define the position the menu drawer shall be displayed at.

- navigationItems (boolean | number | string | dict | list; required):
    A list of navigation items to show in the menu.

- showLogo (boolean; default True):
    Set to True if a logo shall be shown, False if not.

- url (string; default ""):
    Currently selected URL. Leave blank."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, initiallyPinned=Component.UNDEFINED, initiallyCollapsed=Component.UNDEFINED, menuBarPosition=Component.UNDEFINED, menuDrawerPosition=Component.UNDEFINED, showLogo=Component.UNDEFINED, navigationItems=Component.REQUIRED, url=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'initiallyCollapsed', 'initiallyPinned', 'menuBarPosition', 'menuDrawerPosition', 'navigationItems', 'showLogo', 'url']
        self._type = 'Menu'
        self._namespace = 'webviz_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'initiallyCollapsed', 'initiallyPinned', 'menuBarPosition', 'menuDrawerPosition', 'navigationItems', 'showLogo', 'url']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['navigationItems']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Menu, self).__init__(**args)
