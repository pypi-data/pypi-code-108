"""
This module contains the GatePresenter

Gates are used to control the signal flow of Sender to its Receiver.

This is very useful whenever we want to only send data to a widget whenever the user
e.g.
 * opens a tab
 * clicks on a button
 * triggers a selection

Different then the selectors for the gates, the GatePresenter ties the the GateModel and the GateView together:
GatePresenter(GateView, GateModel)
See also ref::gate_presenter.

The information flow is:
GateView -> GatePresenter -> GateModel

Whenever the user triggers a GateView, a signal (open/close) is send to the GatePresenter.
The GatePresenter triggers the GateModel.
The Gate model connects/disconnects its ports.
"""

import logging
from typing import Union, List, Optional

from bokeh.models.widgets.buttons import Button, Toggle
from bokeh.models.widgets.groups import RadioButtonGroup, RadioGroup, CheckboxGroup, CheckboxButtonGroup
from bokeh.models.widgets.panels import Tabs

from shyft.dashboard.base.ports import (StatePorts, States)
from shyft.dashboard.base.gate_model import SingleGate, AggregatedGate
from shyft.dashboard.widgets.logger_box import LoggerBox

GateViews = Union[Button, Tabs, RadioButtonGroup, RadioGroup, CheckboxGroup, CheckboxButtonGroup, Toggle]


class GatePresenter:

    def __init__(self, view: GateViews, gates: List[Union[SingleGate, AggregatedGate]],
                 logger: Optional[LoggerBox]=None) -> None:
        """
        Connect a view to gates, i.e. if view is clicked or activated a gate will be opened or closed

        Current views are:
            Button, Tabs, RadioButtonGroup, RadioGroup, CheckboxGroup,
            CheckboxButtonGroup, Toggle

        Behavior
        --------
            - Button: on_click will open and close all gates
            - Toggle: toggled button will open all gates, enabled toggle will close all gates

            NB: For the following views: same amount of gates and Tab-panels/Buttons/Checkboxes are required

            - Tabs: The active tab will open the gate with the index in the gates list, all others closed
            - RadioGroup, RadioButtonGroup: The active radio button will open with the index in the gates list,
            all others closed
            -  CheckboxGroup, CheckboxButtonGroup: The checked boxes will open gates with the indices in the gates list,
            all will be others closed

        Parameters
        ----------
        view:
            view to connect gates to
        gates:
            gates to be triggered by view selection
        logger:
            logger to use

        """
        self.logger = logger or logging.getLogger()
        self.view = view
        self.gates = gates
        if isinstance(view, Button):
            view.on_click(self._on_click_button)
        elif isinstance(view, Toggle):
            view.on_click(self._on_click_toggle)
        elif isinstance(view, Tabs):
            if len(view.tabs) != len(gates):
                raise ValueError(f"Number of Panels in {view} and Gates are not the same!")
            view.on_change('active', self._on_change_multiple_gates)
            self._on_change_multiple_gates('active', 0, view.active)
        elif isinstance(view, (RadioButtonGroup, RadioGroup, CheckboxGroup, CheckboxButtonGroup)):
            if len(view.labels) != len(gates):
                raise ValueError(f"Number of Buttons in {view} and Gates are not the same!")
            view.on_change('active', self._on_change_multiple_gates)
            self._on_change_multiple_gates('active', 0, view.active)
        else:
            raise NotImplementedError(f"GatePresenter: no connection for View {view} implemented yet")

        self.state = States.ACTIVE
        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)

    def _on_click_button(self, event) -> None:
        """
        Callback for button view
        """
        for gate in self.gates:
            gate.open()
            gate.close()

    def _on_click_toggle(self, new) -> None:
        """
        Callback for toggle view
        new = True : pressed down i.e open
        """
        if new:
            for gate in self.gates:
                gate.open()
        else:
            for gate in self.gates:
                gate.close()

    def _on_change_multiple_gates(self, attrn, old, new) -> None:
        """
        Callback for Views: Tabs, RadioButtonGroup, RadioGroup, CheckboxGroup, CheckboxButtonGroup
        """
        if new is None:
            new = []
        if not isinstance(new, list):
            new = [new]
        for i, gate in enumerate(self.gates):
            if gate is None:
                continue
            if i in new:
                gate.open()
            else:
                gate.close()

    def _receive_state(self, state: States) -> None:
        """
        Receiver function for the state of the GatePresenter

        Parameters
        ----------
        state:
            State to change to
        """
        if state == States.ACTIVE:
            self.view.disabled = False
        elif state == States.DEACTIVE:
            self.view.disabled = True
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)
