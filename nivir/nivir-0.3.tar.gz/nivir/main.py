from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile
from nivir.window import Window

def loadConfig(config:str):
    loadPrcFile(config)

class Nivir:
    def __init__(self) -> None:
        self.window = Window()

    def disableMoveCamWithMouse(self):
        self.window.disable_mouse()

    def run(self):
        self.window.run()