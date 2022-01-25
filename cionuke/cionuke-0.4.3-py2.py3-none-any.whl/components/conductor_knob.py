
"""
Base class for custom knobs. 

Custom knobs are used when the knobs available through Nuke's Python API are not sufficient.

Specifically:
* Extra Environment table.
* Metadata table.
* Extra Assets list and buttons to browse.
* Preview panel

Derived classes must implement updateValue.
"""

from PySide2 import QtWidgets

STYLESHEET = "ConductorKnob { border: 1px solid #555; border-radius: 2px;}"

class ConductorKnob(QtWidgets.QFrame):

    def __init__(self, submitter):

        super(ConductorKnob, self).__init__()

        self.submitter = submitter

        self.content_layout = QtWidgets.QVBoxLayout()

        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.content_layout)
        self.setStyleSheet(STYLESHEET)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Minimum)

    # Needed by Nuke to add the widget
    def makeUI(self):
        return self

    def updateValue(self):
        raise NotImplementedError
