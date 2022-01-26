from panda3d.core import loadPrcFile
from direct.showbase.ShowBase import ShowBase
from nivir.window import Window
from nivir.main import Nivir

class EntityModel:
    def __init__(self, window:Nivir, model:str, pos=(0, 5, 0)):
        self.model = model
        self.pos = pos
        self.window = window

    def render(self):
        self.modelP = self.window.window.loader.loadModel(self.model)
        self.modelP.setPos(
            self.pos[0],
            self.pos[1],
            self.pos[2]
        )
        self.modelP.reparentTo(self.window.window.render)