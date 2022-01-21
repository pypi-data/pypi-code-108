# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ScheduleCard(Component):
    """A ScheduleCard component.


Keyword arguments:

- id (string | dict; optional):
    The ID used to identify this component in Dash callbacks.

- onOffValue (a value equal to: 'On', 'Off'; optional)

- openCloseOnValue (a value equal to: 'Open', 'Close', 'On'; optional)

- scheduleChanged (number; optional)

- scheduleType (string; optional)

- shiftEndTime (string; optional)

- shiftStartTime (string; optional)

- showOpenCloseBtns (boolean; optional)

- showViewModeCard (boolean; optional)

- vacTrnOffValue (a value equal to: 'Off', 'TRN', 'VAC'; optional)"""
    @_explicitize_args
    def __init__(self, scheduleChanged=Component.UNDEFINED, id=Component.UNDEFINED, onOffValue=Component.UNDEFINED, openCloseOnValue=Component.UNDEFINED, vacTrnOffValue=Component.UNDEFINED, showOpenCloseBtns=Component.UNDEFINED, showViewModeCard=Component.UNDEFINED, scheduleType=Component.UNDEFINED, shiftStartTime=Component.UNDEFINED, shiftEndTime=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'onOffValue', 'openCloseOnValue', 'scheduleChanged', 'scheduleType', 'shiftEndTime', 'shiftStartTime', 'showOpenCloseBtns', 'showViewModeCard', 'vacTrnOffValue']
        self._type = 'ScheduleCard'
        self._namespace = 'rsa_scheduler_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'onOffValue', 'openCloseOnValue', 'scheduleChanged', 'scheduleType', 'shiftEndTime', 'shiftStartTime', 'showOpenCloseBtns', 'showViewModeCard', 'vacTrnOffValue']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(ScheduleCard, self).__init__(**args)
