from enum import Enum
from typing import List, Optional
from collections import OrderedDict

from shyft.dashboard.base.ports import Sender, Receiver, States
from shyft.dashboard.base.selector_model import SelectorModelBase
from shyft.dashboard.base.selector_presenter import SelectorPresenter


class LabelDataSelectorClickPolicy(Enum):
    SEND_SELECTED = 1
    REMOVE_SELECTED_AND_SEND_REST = 2


LabelData = List[str]


class LabelDataSelector(SelectorModelBase):
    def __init__(self, presenter: SelectorPresenter, logger=None,
                 on_click_policy: LabelDataSelectorClickPolicy = LabelDataSelectorClickPolicy.SEND_SELECTED,
                 sort: bool = True) -> None:
        """
        Simple label selector model showing a label data in the selector view.
        Label data is a list of str.

        The Selector provides 2 on_click_policies:
            - SEND_SELECTED: (default) send the selection via send_selected_labels port
            - REMOVE_SELECTED_AND_SEND_REST: remove the selected values and send the remaining via send_labels port

        Ports

        send_selected_labels:
            (Sender) send selected labels
        send_labels:
            (Sender) send all available labels
        receive_labels:
            (Receiver)receive a new list of labels to set
        receive_labels_to_add:
            (Receiver) receive additional labels to show in the view. This will trigger send_labels

        Parameters
        ----------
        presenter:
            SelectorPresenter instance
        logger:
            Optional logger
        on_click_policy:
            on click selected policy
        sort:
            sort labels or not
        """
        super().__init__(presenter=presenter, logger=logger)

        self.on_click_policy = on_click_policy
        self.sort = sort

        self.send_selected_labels = Sender(parent=self, name='send selected labels', signal_type=List[str])
        self.send_labels = Sender(parent=self, name='send all labels', signal_type=List[str])

        self.receive_labels = Receiver(parent=self, name='receive labels', func=self._receive_labels,
                                       signal_type=LabelData)
        self.receive_labels_to_add = Receiver(parent=self, name='receive labels to add',
                                              func=self._receive_labels_to_add, signal_type=LabelData)

    def __dir__(self) -> List[str]:
        return super().__dir__() + ["send_selected_labels", "send_labels", "receive_labels",
                                    "receive_labels_to_add"]

    #  run selector call back
    def on_change_selected(self, selected_values: List[str]) -> None:
        self.state_port.send_state(States.ACTIVE)
        if self.on_click_policy == LabelDataSelectorClickPolicy.SEND_SELECTED:
            # have this an policy if really needed
            # self.presenter.set_selector_value(value=self.presenter.default, callback=False)
            self.send_selected_labels(selected_values)
        elif self.on_click_policy == LabelDataSelectorClickPolicy.REMOVE_SELECTED_AND_SEND_REST:
            options = [o for o in self.presenter.selector_options if
                       o not in selected_values and o != self.presenter.default]
            self.presenter.set_selector_options(options=options, sort=self.sort, callback=False)
            self.send_labels(options)

    def _receive_labels(self, label_data: LabelData):
        options = list(OrderedDict.fromkeys(label_data))
        self.presenter.set_selector_options(options=options, sort=self.sort, callback=False)

    def _receive_labels_to_add(self, label_data: LabelData):
        # TODO: the option creation changes the order of all options! fix it
        options = list(set(label_data).union(self.presenter.selector_options))
        options.remove(self.presenter.default)
        self.presenter.set_selector_options(options=options, sort=self.sort, callback=False)
        self.send_labels(options)
