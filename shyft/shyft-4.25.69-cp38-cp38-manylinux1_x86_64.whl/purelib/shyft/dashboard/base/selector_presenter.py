from abc import abstractmethod
from enum import Enum
from typing import Optional, Union, List, Tuple
import logging

from shyft.dashboard.base.ports import (States, Sender, StatePorts, Receiver, connect_ports,
                                        connect_state_ports)
from shyft.dashboard.base.selector_views import SelectorViewBase
from shyft.dashboard.widgets.logger_box import LoggerBox

Option = Union[str, Tuple[str, str]]
Options = List[Option]


class SelectorPresenterError(RuntimeError):
    pass


class SelectorPresenter:

    def __init__(self, name: str, view: SelectorViewBase, default: Option = '', logger=None) -> None:
        """
        The presenter is used as connection between Model and View.
        The presenter is meant to be composed with a Model class as its attribute.
        Whereas the view is added to the presenter as attribute.

        E.i.: model.presenter.view

        The Model interacts with the class methods:

            - set_selector_value
            - set_selector_options
            - selector_options

            and the port function:

             - receive_state: to receive an the state of the model ACTIVE or DEACTIVE

        The selection is passed back to the view with the send_selection_to_model port.
        This needs to be connected to a receiver in the model class.

        Parameters
        ----------
        name:
            name of the presenter - used in debug msg
        view:
            the view-instance the presenter should connect to
        default:
            default selection primarily used to be able to deselect the selector view, defaults to ''
            if you do not want an empty select option set default=None
        logger:
            logger instance


        """
        self.logger = logger or logging.getLogger()

        if not isinstance(view, SelectorViewBase):
            raise SelectorPresenterError(f"SelectorPresenter {name}: View {view} is not of type SelectViewBase!")
        self.selector_view = view
        self.init_default = default or ''
        self.selector_values = [self.init_default]
        self.selected_values = [self.init_default]
        self.default = default
        self.options = [self.init_default]
        self.options_map = {}
        self.inverse_options_map = {}

        self.state = States.ACTIVE
        self.name = name

        # interface to model
        self.send_selection_to_model = Sender(parent=self, name='send selection to model', signal_type=List[str])

        # interface to view
        self.send_view_selection = Sender(parent=self, name='set the selection of the view', signal_type=List[str])
        self.send_view_options = Sender(parent=self, name='set the selection of the view', signal_type=List[str])
        self.receive_view_selection = Receiver(parent=self, name='receive the selection of a view',
                                               func=self._receive_view_selection,
                                               signal_type=List[str])
        self.state_ports = StatePorts(parent=self, _receive_state=self._receive_state)

        connect_ports(self.send_view_options, view.receive_options)
        connect_ports(self.send_view_selection, view.receive_selection)
        connect_ports(view.send_selection, self.receive_view_selection)
        connect_state_ports(self.state_ports, view.state_ports)

        # initialize
        self.set_selector_options(self._unpack_options(options=self.options), callback=False)
        self.set_selector_value(self.init_default)

    @staticmethod
    def _unpack_options(*, options: Options, tuple_index: int = 1) -> List[str]:
        return [o[tuple_index] if isinstance(o, tuple) else o for o in options]

    def __dir__(self) -> List[str]:
        return ["selector_view", 'selector_values', 'set_selector_value', 'set_selector_options', 'selector_options',
                'selected_values']

    def __repr__(self) -> str:
        return f"SelectorPresenter '{self.name}' with view: {self.selector_view}"

    def _receive_state(self, state: States) -> None:
        if state != self.state:
            self.state = state
            # TODO: REMOVE THIS IF BOKEH VERSION IS UPGRADED AND DISABLE PROPERTY WORKS AGAIN
            if state == States.DEACTIVE:
                self.send_view_options([self.init_default])
                # TODO: Commented this because of an error in the self.default variable being a tuple instead of a string, works now
                # self.set_view_selection([self.default])
            if state == States.ACTIVE:
                self.send_view_options(self._unpack_options(options=self.options, tuple_index=1))
            self.state_ports.send_state(state)

    def _receive_view_selection(self, new_selection: List[str]) -> None:
        self.selected_values = [self.options_map[s] for s in new_selection if s in self.options_map]
        self.send_selection_to_model(self.selected_values)

    def set_selector_value(self, value: Union[str, List[str]], callback: bool = False) -> None:
        """
        Method to set the value of the view
        if options are defined with (key, label), value here should be the key of the option

        Parameters
        ----------
        value:
             value the presenter should set the view
        callback:
            if True, the callback is triggered and the selected value is turned back via
            the send_selection_to_model Port

        """
        if isinstance(value, str):
            value = [value]
        options = self._unpack_options(options=self.selector_options, tuple_index=0)
        value = self._unpack_options(options=value, tuple_index=0)
        if not all(v in options for v in value):
            self.logger.debug(f"{self}: '{value}' is not in options of selector")
            return
        self.selector_values = [self.inverse_options_map[s] for s in value if s in self.inverse_options_map]
        self.selected_values = value
        self.send_view_selection(self.selector_values)
        if callback:
            self.send_selection_to_model(self.selected_values)

    def set_selector_options(self, options: Optional[Options] = None, sort: bool = True,
                             selected_value: Optional[Union[str, List[str]]] = None,
                             sort_reverse: bool = False, callback: bool = True) -> None:
        """
        Method to set the selector options

        Options is either List[str] or a List[Tuple[str, str]].
        The Tuple[str, str] is equivalent to (key, label) where the label is shown in the selector, but the key
        is return to the model.

        Parameters
        ----------
        options:
            options for the selector
        sort:
            if True sort the selector options alphabetically
        selected_value:
            value to set the selector, needs to be in the options
        sort_reverse:
            if True sort the selector options in reverse order
        callback:
            if True the selected value or default is set with triggering the callback

        """
        if isinstance(options, list):
            options = options.copy()
            if sort:
                options = sorted(options, reverse=sort_reverse, key=lambda x: x[1] if isinstance(x, tuple) else x)
            if self.default in options:
                options.remove(self.default)

            if self.default is not None:
                options.insert(0, self.default)

            self.options = options
            self.options_map = {o[1] if isinstance(o, tuple) else o: o[0] if isinstance(o, tuple) else o for o in options}
            self.inverse_options_map = {o[0] if isinstance(o, tuple) else o: o[1] if isinstance(o, tuple) else o for o in
                                        options}
            self.send_view_options(self._unpack_options(options=options, tuple_index=1))

            if selected_value:
                self.set_selector_value(selected_value, callback=callback)
            elif self.default:
                self.set_selector_value(self.default, callback=callback)
        else:
            self.state_ports.receive_state(States.INVALID)
            self.logger.error(f'Presenter {self} received invalid options')
            self.set_selector_value(self.init_default, callback=False)

    @property
    def selector_options(self) -> Options:
        if self.state == States.DEACTIVE:
            return [self.init_default]
        else:
            return [o for o in self.options]

#   self._options = {o[0] if isinstance(o, tuple) else o: o for o in opts}


class TextInputPresenter:
    """
    The TextInputPresenter connects a Model with a TextInput View.
    The presenter receives a string from the View, which then will be passed to the Model with the
    send_text_input_to_model port.
    """
    def __init__(self, name: str, view, logger=None) -> None:

        self.logger = logger or logging.getLogger()

        self.text_input_view = view

        self.state = States.ACTIVE
        self.name = name
        self.view = view
        # interface to model
        self.send_text_input_to_model = Sender(parent=self, name='send text input to model', signal_type=str)

        # interface to view
        self.receive_view_text_input = Receiver(parent=self, name='receive the text input of a view',
                                                func=self._receive_view_text_input,
                                                signal_type=str)
        self.state_ports = StatePorts(parent=self, _receive_state=self._receive_state)

        connect_ports(view.send_text_input, self.receive_view_text_input)
        connect_state_ports(self.state_ports, view.state_port)

    def _receive_state(self, state: States) -> None:
        """
        Receives a state.

        :param state: a State object
        """
        if state != self.state:
            self.state = state
            self.state_ports.send_state(state)

    def _receive_view_text_input(self, new_text: str) -> None:
        """
        Method to respond to an active or deactive state

        :param state: state
        :return: None
        """
        self.input_value = new_text
        self.send_text_input_to_model(self.input_value)
