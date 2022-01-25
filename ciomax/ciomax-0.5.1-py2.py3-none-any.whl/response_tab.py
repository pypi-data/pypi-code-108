from PySide2 import QtWidgets, QtGui
from ciomax.components.buttoned_scroll_panel import ButtonedScrollPanel
from ciomax.components.notice_grp import NoticeGrp
from ciomax import submit
from ciocore import config
import urllib.parse

class ResponseTab(ButtonedScrollPanel):

    def __init__(self, dialog):
        super(ResponseTab, self).__init__(dialog,
            buttons=[("back","Back") ])

    def populate(self,response):
        cfg = config.config().config

        print("response:", response)
        if response.get("code") in [200, 201, 204]:
            success_uri = response["response"]["uri"].replace("jobs", "job")
            url = urllib.parse.urljoin(cfg["url"], success_uri)
            message = "Success!\nClick to go to the Dashboard.\n{}".format(url)
            widget = NoticeGrp(message, "success", url)

        else:
            widget = NoticeGrp(response["response"], "error")

        self.layout.addWidget(widget)
        self.layout.addStretch()

        self.configure_signals()

    def configure_signals(self):
        self.buttons["back"].clicked.connect(self.on_back)
