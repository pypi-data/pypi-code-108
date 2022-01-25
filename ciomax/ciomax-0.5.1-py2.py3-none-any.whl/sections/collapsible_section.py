
from PySide2 import QtWidgets, QtCore, QtGui

EXPANDED_STYLESHEET = "CollapsibleSection { border: 1px solid #555; border-radius: 2px;}"
COLLAPSED_STYLESHEET = "CollapsibleSection { border: none;}"



class CollapsibleSection(QtWidgets.QFrame):

    def __init__(self, dialog, title ):

        super(CollapsibleSection, self).__init__()

        self.dialog = dialog
        self.content_area = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_area.setLayout(self.content_layout)
        self.toggle_button = QtWidgets.QToolButton()
        self.toggle_button.setIconSize(QtCore.QSize(7,7))

        font=QtGui.QFont()
        font.setBold(True)
        self.toggle_button.setFont(font)

        self._configure_toggle_button(title)

        self._configure_content_area()
        self._configure_main_layout()

        self.toggle_button.clicked.connect(self.set_expanded)
        self.toggle_button.clicked.connect(self.on_toggle)
     
    def on_toggle(self, expand):
        self.dialog.store.set_section_open(self.__class__.__name__, expand)
        self.toggle_button.setChecked(expand)

    def set_expanded(self, expand):
        if expand:
            self.toggle_button.setArrowType(QtCore.Qt.DownArrow)
            self.content_area.show()
            self.setStyleSheet(EXPANDED_STYLESHEET)
        else:
            self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
            self.content_area.hide()
            self.setStyleSheet(COLLAPSED_STYLESHEET)


    # PRIVATE
    def _configure_toggle_button(self, title):
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
   
    def _configure_content_area(self):
        self.content_area.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)

    def _configure_main_layout(self):
        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(
            self.toggle_button, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        layout.addWidget(self.content_area, 1, 0, 1, 3)
        self.setLayout(layout)

    def populate_from_store(self, store):
        expanded = store.section_open(self.__class__.__name__)
        self.set_expanded(expanded)
        self.toggle_button.setChecked(expanded)
        


    def resolve(self, _, **__):
        return {}

    def add_separator(self):
        separator = QtWidgets.QFrame()
        separator.setLineWidth(1)
        separator.setFrameStyle(QtWidgets.QFrame.HLine |
                                QtWidgets.QFrame.Raised)
        self.content_layout.addWidget(separator)