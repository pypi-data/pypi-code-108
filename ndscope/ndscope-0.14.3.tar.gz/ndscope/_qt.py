import os

from qtpy import uic
from qtpy.QtWidgets import QApplication, QStyleFactory


def load_ui(fname):
    return uic.loadUiType(
        os.path.join(os.path.dirname(__file__), fname))


def create_app():
    app = QApplication([])
    app.setStyle(QStyleFactory.create("Plastique"))
    app.setStyleSheet("QPushButton { background-color: #CCC }")
    app.setDesktopFileName("ndscope")
    return app
