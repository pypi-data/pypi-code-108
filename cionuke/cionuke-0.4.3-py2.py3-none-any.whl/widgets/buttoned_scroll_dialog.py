from PySide2 import QtWidgets

STYLESHEET = """
QToolButton {{ border: none; margin: none; padding:none;}}
"""

def clear_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())

 

class ButtonedScrollDialog(QtWidgets.QDialog):
    def __init__(self, 
        submitter, 
        title="Button Scroll Window", 
        buttons=[("cancel", "Cancel"), ("go", "Go")], 
        direction="column"):
        super(ButtonedScrollDialog, self).__init__(parent=QtWidgets.QApplication.activeWindow())
        self.setWindowTitle(title)
        self.submitter = submitter
        self.screen_scale = self.logicalDpiX() / 96
        self.setStyleSheet(STYLESHEET)

    
        self.buttons = {}

        vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(vlayout)

        vlayout.setMargin(0)
        vlayout.setSpacing(0)
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


    def populate(self, widgets):
        for widget in widgets:
            self.layout.addWidget(widget)
        self.layout.addStretch()