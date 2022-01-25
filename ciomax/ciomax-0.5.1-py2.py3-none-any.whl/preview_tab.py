from PySide2 import QtWidgets, QtGui
import json
from ciomax.components.buttoned_scroll_panel import ButtonedScrollPanel


class PreviewTab(ButtonedScrollPanel):

    def __init__(self, dialog):
        super(PreviewTab, self).__init__(
            dialog,
            buttons=[("export", "Export Script")])
        self.text_area = QtWidgets.QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.layout.addWidget(self.text_area)
        self.buttons["export"].setEnabled(False)

    def populate(self, submission):
        self.text_area.setText(json.dumps(submission, indent=3))
