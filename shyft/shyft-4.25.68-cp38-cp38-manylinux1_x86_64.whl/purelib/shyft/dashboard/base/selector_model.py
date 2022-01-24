import logging
from abc import ABCMeta, abstractmethod
from typing import List

from shyft.dashboard.base.ports import (States, Receiver, connect_ports, StatePorts, Sender)
from shyft.dashboard.base.selector_presenter import (SelectorPresenter, TextInputPresenter)


def processing_wrapper(loading_function):
    def wrapper(cls, *args, **kwargs):
        presenter = cls.presenter
        presenter.state_ports.receive_state(States.PROCESSING)
        return_value = loading_function(cls, *args, **kwargs)
        if return_value:
            presenter.state_ports.receive_state(States.READY)
        else:
            presenter.state_ports.receive_state(States.INVALID)
            cls.logger.info(f"Processing Wrapper of {cls} <function {loading_function.__name__}> returned None/False")
        return return_value
    return wrapper


class SelectorModelBase(metaclass=ABCMeta):
    """
    Abstract base class for a composables selector.

    The selector needs a presenter (the view controller) as input argument.
    In __init__ will be automatically connected to the on_change port.

    The on change port is the only abstract method which is required to set.
    This function receives a List of str, which are the selected values in the view of the presenter.
    Even for a single select this will be a list, then containing a single value.

    To populate the presenter with options, use the public methods of the presenter:
    E.g.:
        self.presenter.set_selector_options(['a', 'b', 'c'], callback=False, sort=True,
                                                sort_reverse=False, selector_values=None)

    In this manner it is also possible to set a value in the view from the backend:
    E.g.:
        self.presenter.set_selector_value(value='a', callback=False)

    Note that when a value is already selected, and one sets the selection again, bokeh won't trigger a callback

    (see also example for custom selector model)
    """

    def __init__(self, presenter: SelectorPresenter, logger=None):
        if not logger:
            logger = logging.getLogger(__file__)
        self.logger = logger

        if not isinstance(presenter, SelectorPresenter):
            raise RuntimeError(f'arg presenter must be of type SelectorPresenter, was {type(presenter)}')
        self.presenter = presenter
        self._receive_selection = Receiver(parent=self, name='receive selection', func=self.on_change_selected,
                                           signal_type=List[str])
        connect_ports(self.presenter.send_selection_to_model, self._receive_selection)

        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        self.state = States.ACTIVE

    def __dir__(self) -> List[str]:
        return ["presenter"]

    def __repr__(self) -> str:
        return f"SelectorModelBase with presenter {self.presenter}"

    @abstractmethod
    def on_change_selected(self, new_values: List[str]) -> None:
        pass

    def _receive_state(self, state: States) -> None:
        if state == self.state:
            return
        if state == States.ACTIVE:
            self.state = state
            self.presenter.state_ports.receive_state(state)
            # Not sending active state since this only done if we can send data to the next widget
        elif state == States.DEACTIVE:
            self.state = state
            self.presenter.state_ports.receive_state(state)
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)


class BasicSelector(SelectorModelBase):
    """
    The most basic implementation of SelectorModelBase which simply sends the new selected value when it is changed.
    """

    def __init__(self, presenter: SelectorPresenter, logger=None):
        super().__init__(presenter=presenter, logger=logger)
        self.send_selection = Sender(parent=self, name='send new selection', signal_type=List[str])

    def on_change_selected(self, new_values: List[str]) -> None:
        self.send_selection(new_values)


class TextInputModelBase(metaclass=ABCMeta):
    """
    Abstract base class for a text input.

    The text input needs a presenter (the view controller) as input argument.
    In __init__ will be automatically connected to the on_change port.

    The on change port is the only abstract method which is required to set.
    This function receives a string, which is typed in by the user in the view of the presenter.
    """

    def __init__(self, presenter: TextInputPresenter, logger=None):
        """
        Constructor.

        :param presenter: a TextInputPresenter object
        :param logger: a logger
        """
        if not logger:
            logger = logging.getLogger(__file__)
        self.logger = logger

        if not isinstance(presenter, TextInputPresenter):
            raise RuntimeError(f'arg presenter must be of type TextInputPresenter, was {type(presenter)}')

        self.presenter = presenter
        self._receive_text_input = Receiver(parent=self, name='receive text input', func=self.on_change_text_input,
                                            signal_type=str)
        connect_ports(self.presenter.send_text_input_to_model, self._receive_text_input)

        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        self.state = States.ACTIVE

    def __dir__(self) -> List[str]:
        return ["presenter"]

    def __repr__(self) -> str:
        return f"TextInputModelBase with presenter {self.presenter}"

    @abstractmethod
    def on_change_text_input(self, new_values: List[str]) -> None:
        pass

    def _receive_state(self, state: States) -> None:
        """
        Receives a state.

        :param state: a State object
        """
        if state == self.state:
            return
        if state == States.ACTIVE:
            self.state = state
            self.presenter.state_ports.receive_state(state)
        elif state == States.DEACTIVE:
            self.state = state
            self.presenter.state_ports.receive_state(state)
            self.state_port.send_state(state)
        else:
            self.logger.error(f"ERROR: {self} - not handel for received state {state} implemented")
            self.state_port.send_state(state)




