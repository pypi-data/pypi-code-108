from PySide2.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton
from PySide2.QtCore import Qt


class InfoWindow(QDialog):
    """
    Info window
    """
    def __init__(self, info_msg):
        super(InfoWindow, self).__init__()
        self.setWindowTitle("alert")

        Vbox = QVBoxLayout()
        msg = QLabel(text=info_msg)
        msg.setAlignment(Qt.AlignCenter)
        button = QPushButton("ОК")
        button.resize(100, 20)
        button.clicked.connect(self.close)
        Vbox.addWidget(msg)
        Vbox.addWidget(button)
        self.setLayout(Vbox)