from typing import Optional, Dict, Any

from shyft.dashboard.base.app import AppBase
from shyft.dashboard.base.ports import connect_ports, Sender

import random
import string
import bokeh.models
import bokeh.layouts

from shyft.dashboard.widgets.logger_box import LoggerBox
from shyft.dashboard.widgets.message_viewer import MessageViewer


class MessageViewerExample(AppBase):

    def __init__(self, thread_pool, app_kwargs: Optional[Dict[str, Any]]=None):
        super().__init__(thread_pool=thread_pool)

    @property
    def name(self) -> str:
        """
        This property returns the name of the app
        """
        return "message viewer"

    def get_layout(self, doc: "bokeh.document.Document", logger: Optional[LoggerBox]=None) -> "bokeh.layouts.LayoutDOM":
        """
        This function returns the full page layout for the app
        """
        doc.title = self.name

        random_text = bokeh.models.Button()

        send_msg = Sender(parent=self, name='send msg', signal_type=str)
        size = 40
        msgs = [''.join(random.choice(string.ascii_uppercase + string.digits + ' ') for x in range(size))  # nosec
                for i in range(20)]
        counter = [0]

        def send_random_text(event):
            send_msg(msgs[counter[0]])
            counter[0] += 1
            if counter[0] == 20:
                counter[0] = 0

        random_text.on_click(send_random_text)

        message_viewer = MessageViewer(title='Example Notifications', logger=logger)
        # connect our function to selector model
        connect_ports(send_msg, message_viewer.receive_message)

        return bokeh.layouts.row(random_text, message_viewer.layout)


