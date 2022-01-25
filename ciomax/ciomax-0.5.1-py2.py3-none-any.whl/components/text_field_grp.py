from PySide2 import QtWidgets, QtCore

from ciomax.components import widgets


class TextFieldGrp(QtWidgets.QWidget):

    def __init__(self, **kwargs):
        super(TextFieldGrp, self).__init__()
        self.scale_factor = self.logicalDpiX() / 96.0
        self.hidable = kwargs.get("hidable")
        self.enablable = kwargs.get("enablable")
        self.is_directory = kwargs.get("directory")
        self.is_file = kwargs.get("file")
        self.custom_button = kwargs.get("custom_button", False)
        self.checkbox = None
        self.button = None
        

        if self.hidable:
            self.enablable = False


        placeholder = kwargs.get("placeholder")

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(
            widgets.FormLabel(
                kwargs.get("label", ""),
                tooltip=kwargs.get("tooltip")
                )
            )

        # hidable checkbox
        if self.hidable or self.enablable:
            self.display_checkbox = QtWidgets.QCheckBox()
            layout.addWidget(self.display_checkbox)
            self.display_checkbox.stateChanged.connect(self.set_active)


        # field
        self.field = QtWidgets.QLineEdit()
        # self.field.setStyleSheet("QLineEdit { background: rgb(48, 48, 48); }")
        layout.addWidget(self.field)
        if placeholder:
            self.field.setPlaceholderText(placeholder)

        # optional checkbox or file browse button
        
        if self.is_directory or self.is_file:
            self.button = QtWidgets.QPushButton("Browse")
            self.button.setFixedWidth(80* self.scale_factor)
            self.button.setAutoDefault(False)
            layout.addWidget(self.button)
            self.button.clicked.connect(self.browse)
        elif self.custom_button:
            self.button = QtWidgets.QPushButton(self.custom_button)
            self.button.setFixedWidth(80* self.scale_factor)
            self.button.setAutoDefault(False)
            layout.addWidget(self.button)
        elif kwargs.get("checkbox"):
            self.checkbox =QtWidgets.QCheckBox(kwargs.get("check_label", ""))
            self.checkbox.setFixedWidth(80* self.scale_factor)
            layout.addWidget(self.checkbox)
        else:
            layout.addSpacing(85* self.scale_factor)



    def set_active(self, value=None):
        if not (self.hidable or self.enablable):
            return
        if self.hidable:
            self._show() if value else self._hide()

        self._enable() if value else self._disable()

    # TODO - Put all the extras in a widget and show/hide/enable/disable the widget
    def _hide(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.field.hide()
        if self.checkbox:
            self.checkbox.hide()
        if self.button:
            self.button.hide()

    def _show(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Checked)
        self.field.show()
        if self.checkbox:
            self.checkbox.show()
        if self.button:
            self.button.show()

    def _disable(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.field.setEnabled(False)
        if self.checkbox:
            self.checkbox.setEnabled(False)
        if self.button:
            self.button.setEnabled(False)

    def _enable(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Checked)
        self.field.setEnabled(True)
        if self.checkbox:
            self.checkbox.setEnabled(True)
        if self.button:
            self.button.setEnabled(True)

    def browse(self):
        if self.is_file:
            result = QtWidgets.QFileDialog.getOpenFileName()
        elif self.is_directory:
            result = QtWidgets.QFileDialog.getExistingDirectory()
        else:
            return
        if result:
            self.field.setText(result)