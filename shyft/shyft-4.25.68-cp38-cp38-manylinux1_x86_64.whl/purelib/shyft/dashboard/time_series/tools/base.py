import abc
import logging
from typing import Any

from shyft.dashboard.base.hashable import Hashable
from shyft.dashboard.time_series.bindable import BindableToMany
from shyft.dashboard.base.ports import States, StatePorts


class BaseTool(Hashable, BindableToMany):

    def __init__(self, logger=None, *, parent_limit=None):
        """
        Parameters
        ----------
        logger:
            optional logger
        parent_limit:
            number of max parents to be bound to
        """
        Hashable.__init__(self)
        BindableToMany.__init__(self, parent_limit=parent_limit)
        self.logger = logger or logging.getLogger()
        self._state: States = States.ACTIVE
        self.state_port: StatePorts = StatePorts(parent=self, _receive_state=self._receive_state)

    @abc.abstractmethod
    def on_bind(self, *, parent: Any) -> None:
        """
        Abstract method which is call on bind to a parent
        """
        pass

    def _receive_state(self, state: States) -> None:
        """
        State port function on receiving state, can be overwritten by inherited class
        """
        if self._state == state:
            return
        if state in [States.ACTIVE, States.DEACTIVE]:
            self._state = state
            self.state_port.send_state(self._state)
