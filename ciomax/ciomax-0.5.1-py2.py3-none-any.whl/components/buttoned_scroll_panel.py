from PySide2 import QtWidgets


def clear_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())


class ButtonedScrollPanel(QtWidgets.QWidget):

    def __init__(self, dialog, buttons=[("cancel", "Cancel"), ("go", "Go")], direction="column"):
        super(ButtonedScrollPanel, self).__init__()
        self.dialog = dialog

        self.buttons = {}

        vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(vlayout)

        scroll_area = QtWidgets.QScrollArea()
        vlayout.addWidget(scroll_area)
        scroll_area.setWidgetResizable(1)

        button_row_widget = QtWidgets.QWidget()
        button_row_layout = QtWidgets.QHBoxLayout()
        button_row_widget.setLayout(button_row_layout)

        for key, label in buttons:
            button = QtWidgets.QPushButton(label)
            button.setAutoDefault(False)
            button_row_layout.addWidget(button)
            self.buttons[key] = button
        vlayout.addWidget(button_row_widget)

        self.widget = QtWidgets.QWidget()
        scroll_area.setWidget(self.widget)

        if direction == "column":
            self.layout = QtWidgets.QVBoxLayout()
        else:
            self.layout = QtWidgets.QHBoxLayout()
        self.widget.setLayout(self.layout)

    def clear(self):
        clear_layout(self.layout)

    def on_back(self):
        self.dialog.tab_widget.setCurrentWidget(self.dialog.main_tab)
