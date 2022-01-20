# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class SmartNodeSelector(Component):
    """A SmartNodeSelector component.
SmartNodeSelector is a component that allows to create tags by selecting data from a tree structure.
The tree structure can also provide meta data that is displayed as color or icon.

Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- caseInsensitiveMatching (boolean; default False):
    Set to True if case-wise incorrect values should be accepted
    anyways.

- data (list; required):
    A JSON object holding all tags.

- delimiter (string; default ":"):
    The delimiter used to separate input levels.

- label (string; optional):
    A label that will be printed when this component is rendered.

- lineBreakAfterTag (boolean; default False):
    If set to True, tags will be separated by a line break.

- maxNumSelectedNodes (number; default -1):
    The max number of tags that can be selected.

- numMetaNodes (number; default 0):
    The number of meta data used. Meta data is not shown as text in
    the final tag but used to set properties like border color or
    icons.

- numSecondsUntilSuggestionsAreShown (number; default 0.5):
    Number of seconds until suggestions are shown.

- persisted_props (list of a value equal to: "selectedTags"s; default ["selectedTags"]):
    Properties whose user interactions will persist after refreshing
    the component or the page.

- persistence (boolean | string | number; optional):
    Used to allow user interactions in this component to be persisted
    when the component - or the page - is refreshed. If `persisted` is
    truthy and hasn't changed from its previous value, a `value` that
    the user has changed while using the app will keep that change, as
    long as the new `value` also matches what was given originally.
    Used in conjunction with `persistence_type`.

- persistence_type (a value equal to: "local", "session", "memory"; default "local"):
    Where persisted user changes will be stored: memory: only kept in
    memory, reset on page refresh. local: window.localStorage, data is
    kept after the browser quit. session: window.sessionStorage, data
    is cleared once the browser quit.

- placeholder (string; default "Add new tag..."):
    Placeholder text for input field.

- selectedTags (list of strings; default undefined):
    Selected tags.

- showSuggestions (boolean; default True):
    Stating of suggestions should be shown or not.

- useBetaFeatures (boolean; default False):
    Set to True to enable beta features."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, maxNumSelectedNodes=Component.UNDEFINED, delimiter=Component.UNDEFINED, numMetaNodes=Component.UNDEFINED, data=Component.REQUIRED, label=Component.UNDEFINED, showSuggestions=Component.UNDEFINED, selectedTags=Component.UNDEFINED, placeholder=Component.UNDEFINED, numSecondsUntilSuggestionsAreShown=Component.UNDEFINED, lineBreakAfterTag=Component.UNDEFINED, caseInsensitiveMatching=Component.UNDEFINED, useBetaFeatures=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'caseInsensitiveMatching', 'data', 'delimiter', 'label', 'lineBreakAfterTag', 'maxNumSelectedNodes', 'numMetaNodes', 'numSecondsUntilSuggestionsAreShown', 'persisted_props', 'persistence', 'persistence_type', 'placeholder', 'selectedTags', 'showSuggestions', 'useBetaFeatures']
        self._type = 'SmartNodeSelector'
        self._namespace = 'webviz_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'caseInsensitiveMatching', 'data', 'delimiter', 'label', 'lineBreakAfterTag', 'maxNumSelectedNodes', 'numMetaNodes', 'numSecondsUntilSuggestionsAreShown', 'persisted_props', 'persistence', 'persistence_type', 'placeholder', 'selectedTags', 'showSuggestions', 'useBetaFeatures']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id', 'data']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(SmartNodeSelector, self).__init__(**args)
