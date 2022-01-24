import abc
from typing import Dict, List, Any, Optional
from shyft.time_series import TsVector

from shyft.dashboard.time_series.bindable import Bindable
from shyft.dashboard.base.hashable import Hashable
from shyft.dashboard.time_series.view import BaseView
from shyft.dashboard.time_series.state import Quantity, UnitRegistry

from shyft.dashboard.base.ports import Receiver, States, StatePorts


class BaseViewContainer(Bindable, Hashable):
    """
    This object is the base class of view container
    """
    def __init__(self, *, viewer: 'shyft.dashboard.time_series.ts_viewer.TsViewer'):
        """
        Parameters
        ----------
        viewer:
            ts viewer instance the base view container should be bound to
        """
        Bindable.__init__(self)
        Hashable.__init__(self)
        # pre bind attributes
        self._visible = True
        self.unit_registry = None
        self._state = States.ACTIVE
        self.state_port = StatePorts(parent=self, _receive_state=self._receive_state)
        # bind to viewer
        viewer.add_view_container(self)
        # post bind attributes
        self.view_time_axis = viewer.view_time_axis
        self.receive_dt = Receiver(parent=self, name='receive a selected dt', signal_type=int,
                                   func=self._receive_dt)

    def set_unit_registry(self, unit_registry: UnitRegistry) -> None:
        """
        Set the unt registry of this view container
        """
        self.unit_registry = unit_registry

    def _receive_dt(self, dt: int) -> None:
        """
        This is an optional function for ViewContainer to receive the new dt selected by the time axis handle/user

        Hint:
          to connect the ViewContainer use the following line in the __init__ of the class:

            # connect to dt-selector of viewer if available:
            viewer.connect_to_dt_selector(self)
        """
        pass

    @property
    @abc.abstractmethod
    def layout(self) -> Any:
        """
        This property returns the preferred layout of the view_container
        """
        pass

    @property
    @abc.abstractmethod
    def layout_components(self) -> Dict[str, List[Any]]:
        """
        This property returns all layout components of the view_container
        """
        pass

    @abc.abstractmethod
    def add_view(self, *, view: BaseView) -> None:
        """
        This function adds a new view to the view_container
        """
        pass

    @abc.abstractmethod
    def update_view_data(self, *, view_data: Dict[BaseView, Quantity[TsVector]]) -> None:
        """
        This function updates the views with new data
        """
        pass

    @abc.abstractmethod
    def clear(self) -> None:
        """
        This function removes all views from the view_container and resets the meta information
        """
        pass

    @abc.abstractmethod
    def clear_views(self, *, specific_views: Optional[List[BaseView]] = None) -> None:
        """
        This function removes all or specific views from the view_container
        """
        pass

    @property
    def visible(self) -> bool:
        """
        Visible property is an optional property for all view container,
        """
        return self._visible

    @visible.setter
    def visible(self, visible: bool) -> None:
        """
        Optional setter of visibility, defaults to doing nothing if the visibility is changed
        """
        self._visible = visible

    @abc.abstractmethod
    def _receive_state(self, state) -> None:
        """
        State method to be implemented by the specific container method
        """
        pass
