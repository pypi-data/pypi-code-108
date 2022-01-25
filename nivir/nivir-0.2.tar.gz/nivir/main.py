from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

class Nivir:
    def __init__(
        self,
        title: str = "Nivir",
        width: int = 800,
        height: int = 600,
        bgcolor = 'black'
    ) -> None:
        self.title = title
        self.width = width
        self.height = height
        self.bgcolor =  bgcolor
        self.shouldShow = True
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle(self.title)
        self.window.setFixedSize(QSize(self.width, self.height))
        self.window.setStyleSheet(f"background-color: {self.bgcolor};")
        self.window.show()

    def custom(
        self,
        title:str = "New Custom Title",
        width:int = 800,
        height:int = 600,
        bgcolor = 'black'
    ):
        self.title = title
        self.width = width
        self.height = height
        self.bgcolor = bgcolor
        
        self.window.setWindowTitle(self.title)
        self.window.setFixedSize(QSize(self.width, self.height))
        self.window.setStyleSheet(f"background-color: {self.bgcolor};")

    def run(self):
        self.app.exec()

if __name__ == '__main__':
    NIVIR_TEST_APP = Nivir()

    NIVIR_TEST_APP.run()