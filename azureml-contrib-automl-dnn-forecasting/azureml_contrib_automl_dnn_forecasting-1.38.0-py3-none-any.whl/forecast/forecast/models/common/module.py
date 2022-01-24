"""A module which defines an extension of a PyTorch module which explicitly notes its receptive field."""

import abc

from torch import nn as nn


class RFModule(nn.Module, abc.ABC):
    """An RFModule is a PyTorch module which also explicitly notes its receptive field."""

    def __init__(self, *args, **kwargs):  # type: ignore
        """Initializes the nn.Module."""
        super().__init__(*args, **kwargs)

    @property
    @abc.abstractmethod
    def receptive_field(self) -> int:
        """Returns the PyTorch module's receptive field.

        Returns
        -------
        int
            The module's receptive field

        """
        raise NotImplementedError()


class StatefulModule(RFModule):
    """A `StatefulModule` is a PyTorch Module whose state can be marked for retention, exported, and imported."""

    def __init__(self, *args, **kwargs):  # type: ignore
        """Defaults to not retaining state."""
        super().__init__(*args, **kwargs)
        self._retain_state = False

    @property
    def retaining_state(self) -> bool:
        """Returns whether the module is currently retaining state.

        Returns:
        --------
        bool

        """
        return self._retain_state

    def retain_state(self, retain: bool) -> None:
        """Allows the caller to signal that the module should begin/end retaining state.

        Note: Ending the retention of state also clears any retained state.

        Parameters:
        -----------
        retain: bool
            Whether state should be retained

        Returns:
        --------
        None

        """
        if retain != self._retain_state:
            self.reset_state()
        self._retain_state = retain

    @abc.abstractmethod
    def reset_state(self) -> None:
        """Resets the state of the module.

        Returns
        -------
        None

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def export_state(self) -> dict:
        """Exports the state of the module to a `dict` whose structure is module-dependent.

        Returns:
        -------
        dict
            The persisted state of the module

        """
        raise NotImplementedError()

    @abc.abstractmethod
    def import_state(self, state: dict) -> None:
        """Sets the state of the module to that described by the parameter `state`.

        Parameters
        ----------
        state: dict
            The state which should be loaded into the module

        Returns
        -------
        None

        """
        raise NotImplementedError()
