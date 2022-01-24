from typing import Optional, Dict, Any
from shyft.dashboard.base.ports import connect_ports, Receiver
from shyft.dashboard.widgets.date_selector import DateSelector
from bokeh.layouts import column
from shyft.dashboard.base.app import AppBase
from shyft.dashboard.widgets.logger_box import LoggerBox


class DateSelectorExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "date_selector_example"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name
        start_date_picker = DateSelector(title='From', width=300, logger=logger)
        end_date_picker = DateSelector(title='Until', width=300, logger=logger)

        connect_ports(end_date_picker.send_selected_date, start_date_picker.receive_max_date)
        connect_ports(start_date_picker.send_selected_date, end_date_picker.receive_min_date)

        def print_from_date(d: int):
            print(f"\nYou selected from date: {d}\n")
            if logger:
                logger.info(f"\nYou selected from date: {d}\n")

        receive_from_date = Receiver(parent="test", name="from date", func=print_from_date, signal_type=int)
        connect_ports(start_date_picker.send_selected_date, receive_from_date)

        def print_until_date(d: int):
            print(f"\nYou selected until date: {d}\n")
            if logger:
                logger.info(f"\nYou selected until date: {d}\n")

        receive_until_date = Receiver(parent="test", name="until date", func=print_until_date, signal_type=int)
        connect_ports(end_date_picker.send_selected_date, receive_until_date)

        return column(*start_date_picker.layout_components['widgets'], *end_date_picker.layout_components['widgets'])
