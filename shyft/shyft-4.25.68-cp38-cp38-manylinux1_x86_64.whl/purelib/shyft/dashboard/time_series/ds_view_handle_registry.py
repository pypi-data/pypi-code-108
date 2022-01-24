import logging

from typing import Tuple, List, Dict, Optional
from enum import Enum

import bokeh.models
from bokeh.layouts import row, column

from shyft.dashboard.base import constants
from shyft.dashboard.base.app import LayoutComponents, update_value_factory
from shyft.dashboard.base.ports import Receiver, Sender, States, StatePorts
from shyft.dashboard.time_series.ds_view_handle import DsViewHandle
from shyft.dashboard.widgets.logger_box import LoggerBox


class DsViewHandleRegistry:
    """
    This Object helps to keep track of DsViewHandles in apps, what did we send what to remove etc.
    For the book-keeping the app relyes on the .tag attribute of a dsvh.
    If a dsvh is send with either replace or add method to the registry and there is another dsvh in the registry with
    the same tag, it does not have to be the same dsvh, it will NOT be added!
    """
    def __init__(self):
        """
        Initialize the ds view handle registry
        """
        self._ds_view_handles = {}  # a dictionary containing current dsvh

    def __len__(self):
        """
        Returns len of registered ds view handles
        """
        return len(self._ds_view_handles)

    @property
    def ds_view_handles(self) -> List[DsViewHandle]:
        """
        Returns a list of registered ds view handles
        """
        return [dsvh for dsvh in self._ds_view_handles.values()]

    @property
    def registry(self) -> Dict[str, DsViewHandle]:
        """
        Returns the full registry
        """
        return {k: v for k, v in self._ds_view_handles.items()}

    def empty_registry(self) -> None:
        """
        Removes all obj from the registry
        """
        self._ds_view_handles = {}

    def replace(self, ds_view_handles: List[DsViewHandle]) -> Tuple[List[DsViewHandle], List[DsViewHandle]]:
        """
        This function will do 2 operations at once:

            - all dsvh in ds_view_handles are added to the registry if there is not a dsvh with the same tag already in
              the registry
            - remove all dsvh from the registry which tags are not equal to one of the dsvh in ds_view_handles

        Returns
        -------
        Tuple(List[DsViewHandle], List[DsViewHandle]):
                where the first List[DsViewHandle] corresponds to dsvh which are added to the registry
                where the first List[DsViewHandle] corresponds to dsvh which are removed from the registry
        """
        ds_view_handles_dict = {d.tag: d for d in ds_view_handles}

        # find out which ds view handle to remove, add or keep in the ds_view_handle
        current_tags = set(self._ds_view_handles)
        new_tags = set(ds_view_handles_dict)

        tags_to_remove = current_tags.difference(new_tags)
        tags_to_keep = current_tags.intersection(new_tags)
        tags_to_add = new_tags.difference(current_tags)

        # Loop over self._ds_view_handles to preserve dsvh order
        ds_view_handles_to_remove = [self._ds_view_handles[t] for t in self._ds_view_handles if t in tags_to_remove]
        ds_view_handles_to_add = [ds_view_handles_dict[t] for t in ds_view_handles_dict if t in tags_to_add]

        # update ds view handles
        # Loop over self._ds_view_handles to preserve dsvh order
        self._ds_view_handles = {t: self._ds_view_handles[t] for t in self._ds_view_handles if t in tags_to_keep}
        self._ds_view_handles.update({t: ds_view_handles_dict[t] for t in ds_view_handles_dict if t in tags_to_add})

        return ds_view_handles_to_add, ds_view_handles_to_remove

    def add(self, ds_view_handles: List[DsViewHandle]) -> Tuple[List[DsViewHandle], List[DsViewHandle]]:
        """
        This function will do 1 operations at once:

            - all dsvh in ds_view_handles are added to the registry if there is not a dsvh with the same tag already in
              the registry

        Returns
        -------
        Tuple(List[DsViewHandle], List[DsViewHandle]):
                where the first List[DsViewHandle] corresponds to dsvh which are added to the registry
                where the first List[DsViewHandle] corresponds to dsvh which are removed from the registry
        """
        ds_view_handles_dict = {d.tag: d for d in ds_view_handles}

        # find out which ds view handle to remove, add or keep in the ds_view_handle
        current_tags = set(self._ds_view_handles)
        new_tags = set(ds_view_handles_dict)

        tags_to_add = new_tags.difference(current_tags)

        ds_view_handles_to_add = [ds_view_handles_dict[t] for t in ds_view_handles_dict if t in tags_to_add]

        # update ds view handles
        self._ds_view_handles.update({t: ds_view_handles_dict[t] for t in ds_view_handles_dict if t in tags_to_add})

        return ds_view_handles_to_add, []

    def remove(self, ds_view_handles: List[DsViewHandle]) -> Tuple[List[DsViewHandle], List[DsViewHandle]]:
        """
        This function will do 1 operations at once:

            - all dsvh in ds_view_handles are removed from the registry

        Returns
        -------
        Tuple(List[DsViewHandle], List[DsViewHandle]):
                where the first List[DsViewHandle] corresponds to dsvh which are added to the registry
                where the first List[DsViewHandle] corresponds to dsvh which are removed from the registry
        """
        current_tags = set(self._ds_view_handles)
        tags_to_remove = current_tags.intersection({d.tag for d in ds_view_handles})
        tags_to_keep = current_tags.difference(tags_to_remove)
        ds_view_handles_to_remove = [self._ds_view_handles[t] for t in self._ds_view_handles if t in tags_to_remove]

        self._ds_view_handles = {t: self._ds_view_handles[t] for t in self._ds_view_handles if t in tags_to_keep}

        return [], ds_view_handles_to_remove

    def remove_by_tag(self, tag_to_remove: str) -> Tuple[List[DsViewHandle], List[DsViewHandle]]:
        """
        This function will do 1 operations at once:

            - all dsvh in which cointaing tag_to_remove in their tag are removed from the registry

        Returns
        -------
        Tuple(List[DsViewHandle], List[DsViewHandle]):
                where the first List[DsViewHandle] corresponds to dsvh which are added to the registry
                where the first List[DsViewHandle] corresponds to dsvh which are removed from the registry
        """
        current_tags = set(self._ds_view_handles)
        tags_to_remove = current_tags.intersection({tag for tag in current_tags if tag_to_remove in tag})
        tags_to_keep = current_tags.difference(tags_to_remove)
        ds_view_handles_to_remove = [self._ds_view_handles[t] for t in self._ds_view_handles if t in tags_to_remove]

        self._ds_view_handles = {t: self._ds_view_handles[t] for t in self._ds_view_handles if t in tags_to_keep}

        return [], ds_view_handles_to_remove


class DsvhRegistryPolicy(Enum):
    """
    Describing policy of DsViewHandleRegistryApp
    """
    REPLACE = 0
    ADD = 1


class DsViewHandleRegistryApp:
    """
    This Object is an composable app for DsViewHandleRegistry with buttons controlling the registry
    """

    def __init__(self,
                 policy: Optional[DsvhRegistryPolicy]=None,
                 padding: Optional[int]=None,
                 sizing_mode: Optional[str]=None,
                 logger: Optional[LoggerBox]=None
                 ) -> None:
        """
        Initialize the ds view handle registry

        Parameters
        ----------
        policy: decied if new dsvhs should be added or relplaced when register ports are used
        """
        self.logger = logger or logging.getLogger(__file__)
        self.dsvh_registry = DsViewHandleRegistry()
        self.policy = policy or DsvhRegistryPolicy.REPLACE

        button_height = 30
        padding = padding or constants.widget_padding
        sizing_mode = sizing_mode or constants.sizing_mode

        # Button to remove all
        self.clear_button = bokeh.models.Button(label="Clear TsViewer", width=120, height=button_height,
                                                sizing_mode=sizing_mode)
        self.clear_button.on_click(self._clear_all)
        self.clear_button_layout = column(self.clear_button, width=120 + padding)

        # RadioButtonGroup to change policy
        self.policy_buttons = bokeh.models.RadioButtonGroup(labels=[i.name.capitalize() for i in DsvhRegistryPolicy],
                                                            active=self.policy.value, width=140, height=button_height,
                                                            sizing_mode=sizing_mode)
        self.policy_buttons.on_change('active', self._change_policy)
        self.set_policy_button = update_value_factory(self.policy_buttons, 'active')
        self.policy_buttons_layout = column(self.policy_buttons, width=140 + padding, height=button_height)

        # ports to receive DsViewHandles from apps
        name = "Receive List[DsViewHandles] to register using the current active policy"
        self.receive_ds_view_handles_to_register = Receiver(parent=self, name=name, signal_type=List[DsViewHandle],
                                                            func=self._register_ds_view_handles)

        name = "Receive List[DsViewHandles] to register using the replace policy"
        self.receive_ds_view_handles_to_replace = Receiver(parent=self, name=name, signal_type=List[DsViewHandle],
                                                           func=self._replace_ds_view_handles)

        name = "Receive List[DsViewHandles] to register using add policy"
        self.receive_ds_view_handles_to_add = Receiver(parent=self, name=name, signal_type=List[DsViewHandle],
                                                       func=self._add_ds_view_handles)

        name = "Receive List[DsViewHandles] to remove"
        self.receive_ds_view_handles_to_remove = Receiver(parent=self, name=name, signal_type=List[DsViewHandle],
                                                          func=self._remove_ds_view_handles)

        name = "Receive List[DsViewHandles] to remove by tag"
        self.receive_ds_view_handles_to_remove_by_tag = Receiver(parent=self, name=name, signal_type=str,
                                                                 func=self._remove_ds_view_handles_by_tag)

        # port connections to TsViewer app
        self.send_ds_view_handles_to_add = Sender(parent=self, name='send ds view handles to add to viewer',
                                                  signal_type=List[DsViewHandle])
        self.send_ds_view_handles_to_remove = Sender(parent=self, name="send ds view handles to remove from viewer",
                                                     signal_type=List[DsViewHandle])
        self.send_ts_viewer_state = Sender(parent=self, name="send state to ts_viewer", signal_type=States)

        self._layout = row(self.policy_buttons_layout, self.clear_button_layout)

    @property
    def layout(self) -> row:
        return self._layout

    @property
    def layout_components(self) -> LayoutComponents:
        """
        Returns all layout components of the app
        """
        return {'widgets': [self.clear_button, self.policy_buttons]}

    def _clear_all(self) -> None:
        self._remove_ds_view_handles(self.dsvh_registry.ds_view_handles)

    def _change_policy(self, attr, old, new) -> None:
        """
        Callback for the policy radio buttons
        """
        if new >= len(DsvhRegistryPolicy):
            return
        self.policy = DsvhRegistryPolicy(new)

    def _register_ds_view_handles(self, ds_view_handles: List[DsViewHandle]) -> None:
        if self.policy == DsvhRegistryPolicy.REPLACE:
            self._replace_ds_view_handles(ds_view_handles=ds_view_handles)
        elif self.policy == DsvhRegistryPolicy.ADD:
            self._add_ds_view_handles(ds_view_handles=ds_view_handles)
        else:
            return

    def _replace_ds_view_handles(self, ds_view_handles: List[DsViewHandle]) -> None:
        """
        Receiver function to receive dsvh to merge
        """
        dsvh_to_add, dsvh_to_remove = self.dsvh_registry.replace(ds_view_handles=ds_view_handles)
        self.send_ts_viewer_state(States.DEACTIVE)
        # first remove
        if dsvh_to_remove:
            self.send_ds_view_handles_to_remove(dsvh_to_remove)
        # then add
        if dsvh_to_add:
            self.send_ds_view_handles_to_add(dsvh_to_add)
        self.send_ts_viewer_state(States.ACTIVE)

    def _add_ds_view_handles(self, ds_view_handles: List[DsViewHandle]) -> None:
        """
        Receiver function to receive dsvh to add
        """
        dsvh_to_add, _ = self.dsvh_registry.add(ds_view_handles=ds_view_handles)
        if not dsvh_to_add:
            return
        self.send_ds_view_handles_to_add(dsvh_to_add)

    def _remove_ds_view_handles(self, ds_view_handles: List[DsViewHandle]) -> None:
        """
        Receiver function to receive dsvh to remove
        """
        _, dsvh_to_remove = self.dsvh_registry.remove(ds_view_handles=ds_view_handles)
        if not dsvh_to_remove:
            return
        self.send_ts_viewer_state(States.DEACTIVE)
        self.send_ds_view_handles_to_remove(dsvh_to_remove)
        self.send_ts_viewer_state(States.ACTIVE)

    def _remove_ds_view_handles_by_tag(self, tag: str) -> None:
        """
        Receiver function to receive dsvh to remove
        """
        _, dsvh_to_remove = self.dsvh_registry.remove_by_tag(tag_to_remove=tag)
        if not dsvh_to_remove:
            return
        self.send_ts_viewer_state(States.DEACTIVE)
        self.send_ds_view_handles_to_remove(dsvh_to_remove)
        self.send_ts_viewer_state(States.ACTIVE)
