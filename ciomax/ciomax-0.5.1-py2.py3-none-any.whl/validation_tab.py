from PySide2 import QtWidgets, QtGui
from ciomax.components.buttoned_scroll_panel import ButtonedScrollPanel
from ciomax.components.notice_grp import NoticeGrp
from ciomax import submit


class ValidationTab(ButtonedScrollPanel):

    def __init__(self, dialog):
        super(ValidationTab, self).__init__(
            dialog,
            buttons=[("back", "Back"), ("continue", "Continue Submission")])
        self.configure_signals()

    def configure_signals(self):
        self.buttons["back"].clicked.connect(self.on_back)
        self.buttons["continue"].clicked.connect(self.on_continue)

    def populate(self, errors, warnings, infos):
        obj = {
            "error": errors,
            "warning": warnings,
            "info": infos
        }
        for severity in ["error", "warning", "info"]:
            for entry in obj[severity]:
                widget = NoticeGrp(entry, severity)

                self.layout.addWidget(widget)
        self.layout.addStretch()

        self.buttons["continue"].setEnabled(not errors)

    def on_continue(self):
        submit.do_submit(self.dialog)
