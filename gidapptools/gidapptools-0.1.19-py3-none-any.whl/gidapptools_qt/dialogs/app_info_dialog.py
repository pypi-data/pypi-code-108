"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Qt Imports --------------------------------------------------------------------------------------->
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QLabel, QDialog, QLineEdit, QVBoxLayout

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AppInfoDialog(QDialog):

    def __init__(self) -> None:
        super().__init__()

        self.label_font = self.create_label_font()
        self.parts = []
        self.setup()

    def create_label_font(self) -> QFont:
        font = QFont()
        font.setPointSize(19)
        font.setBold(True)
        return font

    def create_new_part(self, label_text: str, data_text: str) -> None:
        label = QLabel(self)
        label.setText(label_text)
        label.setFont(self.label_font)
        label.setAlignment(Qt.AlignCenter)

        data = QLineEdit(self)
        data.setReadOnly(True)
        data.setText(data_text)
        data.setAlignment(Qt.AlignCenter)

        self.parts.append((label, data))

    def setup(self):
        self.resize(400, 100)
        self.setMaximumSize(QSize(400, 100))
        self.verticalLayout = QVBoxLayout(self)

        for label, data in self.parts:
            self.verticalLayout.addWidget(label)
            self.verticalLayout.addWidget(data)


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
