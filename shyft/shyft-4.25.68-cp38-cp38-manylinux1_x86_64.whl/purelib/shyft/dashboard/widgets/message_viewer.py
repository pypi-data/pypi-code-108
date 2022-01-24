import logging

from typing import Optional
import bokeh.models
import bokeh.layouts
from bokeh.io import curdoc
import shyft.time_series as sa
from shyft.dashboard.base.ports import Receiver
from shyft.dashboard.widgets.logger_box import LoggerBox
from threading import RLock

class MessageViewer:

    def __init__(self,
                 title: str='Notification:',
                 rows=10,
                 width=300,
                 height=200,
                 title_hight=20,
                 sizing_mode: Optional[str]=None,
                 show_time: bool=True,
                 time_zone: str='Europe/Oslo',
                 logger: Optional[LoggerBox]=None):
        """
        Simple Message Viewer using a Div in the browser

        Parameters
        ----------
        title:
            Title of the MSG box default er Notification:
        rows:
            number of msg rows which should be shown
        width:
            width of the msg div
        height:
            height of the msg div, this will be influenced by rows.
        title_hight:
            heigth of the title div default is 20
        sizing_mode:
            sizing mode of the divs
        """
        self.logger = logger or logging.getLogger(__file__)
        self.title = title
        sizing_mode = sizing_mode or 'fixed'
        self.rows = rows
        self.show_time = show_time
        self.cal = sa.Calendar(time_zone)
        self._title_div = bokeh.models.Div(text=title, width=width, height=title_hight, sizing_mode=sizing_mode)
        self._message_div = bokeh.models.Div(text='', width=width, height=height, sizing_mode=sizing_mode)

        self.receive_message = Receiver(parent=self, name='receive a message to plot', func=self._receive_message, signal_type=str)

        self.info_msg_style = "color:black;font-size:10pt;font-weight:bold;font-family:Courier, monospace;"
        self.warning_msg_style = "color:red;font-size:10pt;font-weight:bold;font-family:Courier, monospace;"
        self.standard_msg_style = ""

        self.rmx: RLock = RLock()  # ensure self.msg is protected
        self.msgs = []
        self.layout = bokeh.layouts.column(self._title_div, self._message_div)

    def _receive_message(self, text: str) -> None:
        self.add_message(text, self.standard_msg_style)

    def receive_info_message(self, text: str) -> None:
        self.add_message(text, self.info_msg_style)

    def receive_warning_message(self, text: str) -> None:
        self.add_message(text, self.warning_msg_style)

    def add_message(self, text, style):
        """ Receiver function for messages"""
        if self.show_time:
            now = self.cal.calendar_units(sa.utctime_now())
            text = self._format_text_with_time_prefix(now, text)
        with self.rmx:
            self.msgs.insert(0, f'<span style="{style}"">{text}</span>')
        self.logger.debug(f'MessageViewer {self.title} - {text}')
        curdoc().add_next_tick_callback(self._safe_modify_log)

    @staticmethod
    def _format_text_with_time_prefix(time, text):
        text = '[{:02d}:{:02d}:{:02d}] - {}'.format(time.hour, time.minute, time.second, text)
        return text

    def _safe_modify_log(self):
        n_rows = len(self.msgs)
        self._message_div.text = '<br>'.join([self.msgs[i] for i in range(self.rows) if n_rows >= i+1])