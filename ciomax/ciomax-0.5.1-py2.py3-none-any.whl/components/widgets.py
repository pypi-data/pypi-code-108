from PySide2 import QtWidgets, QtCore


class FormLabel(QtWidgets.QLabel):

    def __init__(self, label, tooltip=None):
        super(FormLabel, self).__init__()
        self.scale_factor = self.logicalDpiX() / 96.0

        self.setText(label)
        self.setFixedWidth(120 * self.scale_factor)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.setIndent(5)

        if tooltip:
            self.setToolTip(tooltip)


def add_checkbox(layout, do_checkbox=True, label=""):
    scale_factor = layout.parentWidget().logicalDpiX() / 96.0
    if do_checkbox:
        checkbox = QtWidgets.QCheckBox(label)
        checkbox.setFixedWidth(80* scale_factor)
        layout.addWidget(checkbox)
        return checkbox
    else:
        layout.addSpacing(85* scale_factor)


def add_button(layout, do_button=True, label=""):
    scale_factor = layout.parentWidget().logicalDpiX() / 96.0
    if do_button:
        button = QtWidgets.QPushButton(label)
        button.setFixedWidth(80* scale_factor)
        button.setAutoDefault(False)
        layout.addWidget(button)
        return button
    else:
        layout.addSpacing(85* scale_factor)

