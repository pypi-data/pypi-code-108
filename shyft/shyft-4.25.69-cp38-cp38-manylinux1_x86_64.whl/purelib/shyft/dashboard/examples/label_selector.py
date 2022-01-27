from typing import Optional, Dict, Any

from bokeh.layouts import column

from shyft.dashboard.base.ports import connect_ports, Receiver
from shyft.dashboard.base.selector_presenter import SelectorPresenter
from shyft.dashboard.base.selector_views import MultiSelect
from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.widgets.selector_models import LabelDataSelector, LabelData, LabelDataSelectorClickPolicy
from shyft.dashboard.base.app import AppBase


class LabelSelectorExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "label_selector_example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name

        labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

        label_view = MultiSelect(title='Available Labels', size=10, width=300, height=200, logger=logger)
        label_presenter = SelectorPresenter(name='Available Labels', view=label_view, logger=logger)
        label_selector = LabelDataSelector(presenter=label_presenter,
                                           on_click_policy=LabelDataSelectorClickPolicy.SEND_SELECTED,
                                           logger=logger)

        def _receive_selection_to_assert(selection: LabelData):
            print(f"\n You selected labels: `{selection}`\n")
            if logger:
                logger.info(f" You selected labels: `{selection}`")

        receive_selection_to_assert = Receiver(parent='parent', name='assert_selection',
                                               func=_receive_selection_to_assert, signal_type=LabelData)
        # connect our function to selector model
        connect_ports(label_selector.send_selected_labels, receive_selection_to_assert)

        label_view2 = MultiSelect(title='Available Labels', size=10, width=300, logger=logger)
        label_presenter2 = SelectorPresenter(name='Available Labels', view=label_view2, logger=logger)
        label_selector2 = LabelDataSelector(presenter=label_presenter2,
                                            on_click_policy=LabelDataSelectorClickPolicy.REMOVE_SELECTED_AND_SEND_REST,
                                            logger=logger)

        def _receive_selection_to_assert2(selection: LabelData):
            print(f"\n The remaining labels are: `{selection}`\n")
            if logger:
                logger.info((f" The remaining labels are: `{selection}`"))
            if not selection:
                print("\n You removed all labels, time for a refill")
                if logger:
                    logger.info(" You removed all labels, time for a refill")
                label_selector2.receive_labels(labels)

        receive_selection_to_assert2 = Receiver(parent='parent', name='assert_selection2',
                                                func=_receive_selection_to_assert2,
                                                signal_type=LabelData)
        # connect our function to selector model
        connect_ports(label_selector2.send_labels, receive_selection_to_assert2)

        # initialize
        label_selector.receive_labels(labels)
        label_selector2.receive_labels(labels)

        return column(*label_view.layout_components['widgets'], *label_view2.layout_components['widgets'], width=300)
