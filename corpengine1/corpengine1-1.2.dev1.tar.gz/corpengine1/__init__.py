"""
>>>>>    CORP ENGINE    <<<<<
A free & open-source toolkit for making games in Python programming language.
Made by @PyxleDev0 & Contributors
https://github.com/pyxledev0/corp-engine
https://github.com/pyxledev0/corp-engine-examples
"""


import pygame
import time
import sys
import inspect
import easygui
from pygame.locals import *


# COLORS MODULE
class Colors:
    def __init__(self) -> None:
        self.CORPWHITE = (224, 224, 224)
        self.DARKGREEN = (0, 100, 0)
        self.FORESTGREEN = (39, 139, 34)
        self.LIME = (0, 255, 0)
        self.GREEN = (0, 128, 0)
        self.BLUE = (0, 0, 255)
        self.AQUA = self.mix(self.LIME, self.BLUE)
        self.BABYBLUE = (137, 207, 240)
        self.LIGHTBLUE = (0, 150, 255)
        self.DARKRED = (139, 0, 0)
        self.RED = (255, 0, 0)
        self.MAGENTA = self.mix(self.RED, self.BLUE)
        self.PINK = (255, 105, 180)
        self.VIOLET = (238, 130, 238)
        self.BROWN = (139, 69, 19)
        self.TAN = (210, 180, 140)
        self.WHITE = self.mix(self.RED, self.LIME, self.BLUE)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHTGRAY = (211, 211, 211)
        self.SILVER = (192, 192, 192)

    # Merged from @Lercdsgn (mix function from Pytility.colors) Thanks for the credit, pyxle :p
    def mix(self, *colors: tuple) -> tuple:
        res = [0]*3
        for color in colors:
            for index, param in enumerate(color):
                if 0 >= res[index]+param >= 255: # Patch-1: Fixed range not including 255 and 0 
                    res[index] += param
        return tuple(res)

colors = Colors()

# CONSTANTS MODULE
class Constants:
    def __init__(self) -> None:
        self.ENGINEVERSION: str = '1.2.dev1'
        self.DEFAULTSCREENSIZE: tuple = (640, 360)
        self.WINDOWTITLE: str = 'CORP Engine window'
        self.FLAGS: int
        self.RUNNING: bool = True
        self.FPS_CAP: int = 60
        self.BACKGROUND_COLOR: tuple = colors.CORPWHITE

constants = Constants()

# FLAGS MODULE
class Flags:
    def __init__(self):
        self.RESIZABLE = RESIZABLE
        self.SCALED = SCALED
        self.FULLSCREEN = FULLSCREEN | SCALED

flags = Flags()

# VERSION FUNCTION
def version(target) -> str:
    return pygame.version.ver if target=="pygame" else (pygame.version.SDL if target.lower()=="sdl" else constants.ENGINEVERSION)

def openErrorWindow(text, engine) -> None:
    callerFrame = sys._getframe(2)
    easygui.msgbox(f'file: {inspect.getmodule(callerFrame)} in line {callerFrame.f_lineno}\n\n -- {text}\n\nReach PyxleDev0 on github out with the error location to help me out.', 'CORPEngine crashed!')
    engine.status = not constants.RUNNING
    sys.exit()

# ROOT CLASSES:
class GameObject(object):
    def __init__(self, parent: object) -> None:
        self.name = self.type = 'Object'
        self.parent: object = parent

    def setAttributeOfObject(self, object: object) -> None:
        if not hasattr(self, object.name):
            setattr(self, object.name, object)

    def getGameService(self) -> object:
        game = self.parent
        while game.type != 'GameService':
            game = game.parent
        return game

    def getEngine(self) -> object:
        engine = self.parent
        while engine.type != 'Engine':
            engine = engine.parent
        return engine

# SERVICES:

class Assets(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'Assets'
        self.images: dict = {}
        self.fonts: dict = {}
        self.sounds: dict = {}

    def getImage(self, name) -> pygame.Surface:
        try:
            return self.images[name].copy()
        except KeyError:
            openErrorWindow(f'No asset found named "{name}".', self.parent.parent)

    def loadImage(self, path: str, name: str) -> None:
        try:
            img = pygame.image.load(path).convert_alpha()
            self.images.update({name: img})
        except Exception:
            openErrorWindow('Image path invalid or image file unsupported.', self.parent.parent)

    def loadFont(self, path: str, name: str, size: int=16, bold: bool=False, italic: bool=False, underline: bool=False) -> None:
        try:
            self.fonts.update({name: pygame.font.Font(path, size)})
            self.fonts[name].bold = bold
            self.fonts[name].italic = italic
            self.fonts[name].underline = underline
        except Exception:
            openErrorWindow('No such file or directory.', self.parent.parent)

    def loadSound(self, path: str, name: str) -> None:
        try:
            self.sounds.update({name: pygame.mixer.Sound(path)})
        except Exception:
            openErrorWindow('Sound path invalid or sound file unsupported.', self.parent.parent)

class EngineEventService(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'EngineEventService'

    def events(self) -> None:
        game = self.parent
        window = game.parent.window
        input = game.getService('UserInputService')
        input.mouseStatus = [False, False, False]
        input.mouseWheelStatus = [0, 0]

        # pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                game.parent.status = not constants.RUNNING

            if event.type == KEYUP:
                # fullscreen toggling
                if event.key == K_F11:
                    window.fullscreen = not window.fullscreen
                    if window.fullscreen:
                        fl = flags.FULLSCREEN
                    else:
                        fl = constants.FLAGS
                    window.screen = pygame.display.set_mode(constants.DEFAULTSCREENSIZE, fl, 32)

            if event.type == MOUSEWHEEL:
                input.mouseWheelStatus = [event.x, event.y]

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    input.mouseStatus[0] = True
                if event.button == 3:
                    input.mouseStatus[2] = True
                if event.button == 2:
                    input.mouseStatus[1] = True

            # controller hotplugging
            if event.type == JOYDEVICEADDED or event.type == JOYDEVICEREMOVED:
                input.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

class EngineRenderService(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'EngineRenderService'
        self.totalEntitiesRendered: int = 0
        self.totalParticlesRendered: int = 0

    def render(self) -> None:
        self.renderEntities()

    def renderEntities(self) -> None:
        self.totalEntitiesRendered = 0
        game = self.getGameService()
        workspace = self.parent.getService('Workspace')
        window = game.parent.window
        windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])
        camX, camY = self.getCameraPosition(workspace)
        fov = self.getCameraFOV(workspace)

        for child in workspace.getChildren():
            if child.type == 'Entity' and child.image != None and child.render:
                self.renderEntity(child, window, windowResolutionRatio, camX, camY, fov)
            elif child.type == 'Folder':
                for child2 in child.getChildren():
                    if child2.type == 'Entity' and child2.image != None and child2.render:
                        self.renderEntity(child2, window, windowResolutionRatio, camX, camY, fov)

    def renderEntity(self, child: object, window: object, windowResolutionRatio: list, camX: float, camY: float, fov: float) -> None:
        image = child.image
        imageSize = (image.get_width(), image.get_height())
        image = pygame.transform.scale(image, (imageSize[0]*child.size[0], imageSize[1]*child.size[1]))
        imageSize = (image.get_width(), image.get_height())
        image = pygame.transform.scale(image, (imageSize[0]*windowResolutionRatio[1], imageSize[1]*windowResolutionRatio[1]))
        imageSize = (image.get_width(), image.get_height())
        image = pygame.transform.scale(image, (imageSize[0], imageSize[1]))
        image = pygame.transform.rotate(image, child.rotation)
        x = ((child.position[0] - camX) * windowResolutionRatio[0]) - image.get_width()/2
        y = ((child.position[1] - camY) * windowResolutionRatio[1]) - image.get_height()/2
        pos = [x, y]
        window.renderWindow.blit(image, pos)
        # scale surface by camera FOV
        if fov != 100:
            size = (window.renderWindow.get_width(), window.renderWindow.get_height())
            window.renderWindow = pygame.transform.scale(window.renderWindow, (size[0]*(fov/100), size[1]*(fov/100)))
        self.totalEntitiesRendered += 1
        for childA in child.getChildren():
            self.renderEntity(childA, window, windowResolutionRatio, camX, camY, fov)

    def getCameraPosition(self, workspace: object) -> tuple:
        if workspace.currentCamera != None:  # if a default camera exists:
            camX, camY = workspace.currentCamera.position
        else:
            camX, camY = (0, 0)
        return camX, camY

    def getCameraFOV(self, workspace: object) -> float:
        if workspace.currentCamera == None:
            fov = 100
        else:
            fov = workspace.currentCamera.fieldOfView
        return fov

class GUIService(GameObject):
    def __init__(self, parent: object) -> None:
        self.name = 'GUIService'
        self.type = 'GUIService'
        super().__init__(parent)
        self.children: list = []
        self.childrenQueue: list = []

    def update(self) -> None:
        self.updateQueue()
        self.childrenEvents()

    def updateQueue(self) -> None:
        # load the next member of the queue
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        for child in self.children:
            if hasattr(child, 'update') and child.enabled == True:
                child.update()
            child._update()

    def getChild(self, name) -> object:
        try:
            return getattr(self, name)
        except Exception:
            for child in self.children:
                if child.name == name:
                    return child
            return None

class Object(GameObject):
    def __init__(self, parent: object) -> None:
        self.name = self.type = 'Object'
        super().__init__(parent)

    def new(self, object: object, putInQueue: bool=False, addAsAttr: bool=True) -> None:
        parent = object.parent
        if putInQueue:
            parent.childrenQueue.append(object)
        else:
            parent.children.append(object)
            if addAsAttr:
                setattr(object.parent, object.name, object)
            if hasattr(object, 'setup'):
                object.setup()
        object.name = type(object).__name__  # set name automatically

    def remove(self, object: object) -> None:
        parent = object.parent
        parent.children.remove(object)
        delattr(parent, object.name)

class ScriptService(GameObject):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.name = self.type = 'ScriptService'
        self.children: list = []
        self.childrenQueue: list = []

    def getChild(self, name: str) -> object:
        try:
            return getattr(self, name)
        except Exception:
            for child in self.children:
                if child.name == name:
                    return child
            return None

    def update(self) -> None:
        self.updateQueue()
        self.childrenEvents()

    def updateQueue(self) -> None:
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        window = self.parent.parent.window
        for child in self.children:
            if hasattr(child, 'update') and child.type == 'GlobalScript':
                child.update(window.dt)

    def getChildren(self) -> list:
        return self.children.copy()

class SoundService(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'SoundService'
        self.children: list = []
        self.childrenQueue: list = []

    def playFile(self, name: str) -> None:
        assets = self.parent.getService('Assets')
        try:
            assets.sounds[name].play()
        except Exception:
            openErrorWindow(f'No sound file named "{name}".', self.parent.parent)

    def stopFile(self, name: str) -> None:
        assets = self.parent.getService('Assets')
        try:
            assets.sounds[name].stop()
        except Exception:
            openErrorWindow(f'No sound file named "{name}".', self.parent.parent)

    def setVolume(self, name: str, value: float) -> None:
        assets = self.parent.getService('Assets')
        try:
            assets.sounds[name].set_volume(value)
        except Exception:
            openErrorWindow(f'Invalid value for volume or file not found.', self.parent.parent)

    def getVolume(self, name: str) -> float:
        assets = self.parent.getService('Assets')
        try:
            return assets.sounds[name].get_volume()
        except Exception:
            openErrorWindow('Sound file not found.', self.parent.parent)

    def getLength(self, name) -> float:
        assets = self.parent.getService('Assets')
        try:
            return assets.sounds[name].get_length()
        except Exception:
            openErrorWindow(f'Invalid value for volume or file not found.', self.parent.parent)

class UserInputService(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'UserInputService'
        self.inputs: dict = {}
        self.mouseStatus: list = [False, False, False]
        self.mouseWheelStatus: list = [0, 0]
        self.mouseFocus: str = 'Game'
        self.axisDeadzone = 0.1
        self.joysticks: list = []
        self.setupJoysticks()

    def setupJoysticks(self) -> None:
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

    def keyPressed(self, name: str) -> bool:
        keys = pygame.key.get_pressed()
        try:
            input = self.inputs[name]
            for key in input:
                if keys[key]:
                    return True
            return False
        except KeyError:
            openErrorWindow(f'unknown input "{name}".', self.parent.parent)

    def keyMultiplePressed(self, name: str) -> bool:
        keys = pygame.key.get_pressed()
        input = self.inputs[name]
        for key in input:
            if not keys[key]:
                return False
        return True

    def getMouseWheel(self) -> tuple:
        input = self.getGameService().getService('UserInputService')
        return input.mouseWheelStatus.copy()

    def addInput(self, name: str, value: list) -> None:
        self.inputs.update({name: value})

    def isCollidingWithMouse(self, object: object) -> bool:
        objRect = object.image.get_rect()
        objRect.x = object.position[0] - object.image.get_width()/2
        objRect.y = object.position[1] - object.image.get_height()/2
        camX, camY = self.getCameraPosition(self.getGameService().getService('Workspace'))
        mx, my = self.getMousePosition()
        return objRect.collidepoint(mx+camX, my+camY)

    def isMouseButtonDown(self, num: str) -> bool:
        mouseButtons = {
            'left': 0,
            'middle': 1,
            'right': 2
        }
        mouse = pygame.mouse.get_pressed()
        return mouse[mouseButtons[num]]

    def isMouseButtonPressed(self, button: str) -> bool:
        mouseButtons = {
            'left': 0,
            'middle': 1,
            'right': 2
        }
        try:
            return self.mouseStatus[mouseButtons[button]]
        except Exception:
            openErrorWindow('Unknown mouse button "{button}".', self.getEngine())

    def getMousePosition(self, ratio=False) -> tuple:
        mx, my = pygame.mouse.get_pos()
        if ratio: # divide it with the resolution of the window
            window = self.getEngine().window
            windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])
            mx /= windowResolutionRatio[0]
            my /= windowResolutionRatio[1]
        return mx, my

    def getMouseRel(self) -> tuple:
        rx, ry = pygame.mouse.get_rel()
        return rx, ry

    def getCameraPosition(self, workspace) -> tuple:
        if workspace.currentCamera != None:  # if a default camera exists:
            camX, camY = workspace.currentCamera.position
        else:
            camX, camY = (0, 0)
        return camX, camY

    def getControllerName(self, id: int) -> str:
        try:
            return self.joysticks[id].get_name()
        except Exception:
            openErrorWindow(f'No controller with the id {id} found.', self.getEngine())

    def getControllerAxis(self, id: int, num: int) -> float:
        try:
            axis = self.joysticks[id].get_axis(num)
            if self.axisDeadzone > abs(axis):
                axis = 0
            return axis
        except Exception:
            openErrorWindow(f'No controller with the id {id} found.\n    (Or invalid value.)', self.getEngine())

    def getControllerPowerLevel(self, id: int) -> str:
        try:
            return self.joysticks[id].get_power_level()
        except Exception:
            openErrorWindow(f'No controller with the id {id} found.', self.getEngine())

    def setAxisDeadzone(self, value: float) -> None:
        self.axisDeadzone = value

    def getControllerButton(self, id: int, num: int) -> bool:
        return self.joysticks[id].get_button(num)

class Workspace(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'Workspace'
        self.children: list = []
        self.childrenQueue: list = []
        self.currentCamera = None

    def setCurrentCamera(self, object: object) -> None:
        self.currentCamera = object

    def getChild(self, name: str) -> object:
        try:
            return getattr(self, name)
        except Exception:
            for child in self.children:
                if child.name == name:
                    return child
            return None

    def update(self) -> None:
        self.updateQueue()
        self.childrenEvents()

    def updateQueue(self) -> None:
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # update current camera
            if newChild.type == 'Camera' and self.currentCamera == None:
                self.currentCamera = newChild
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        window = self.parent.parent.window
        for child in self.children:
            if hasattr(child, 'update'):
                child.update(window.dt)
                if child.type == 'ParticleEmitter':
                    if hasattr(child, 'update'):
                        child.update(window.dt)
                    child.render(window.dt)
            if hasattr(child, '_update'):
                child._update()

    def getChildren(self) -> list:
        return self.children.copy()

class GameService(object):
    def __init__(self, parent: object) -> None:
        self.parent = parent
        # TODO this code fricking sucks, fix it pls :)
        self.name = self.type = 'GameService'
        self.Assets = Assets(self)
        self.EngineRenderService = EngineRenderService(self)
        self.EngineEventService = EngineEventService(self)
        self.UserInputService = UserInputService(self)
        self.Object = Object(self)
        self.Workspace = Workspace(self)
        self.GUIService = GUIService(self)
        self.ScriptService = ScriptService(self)
        self.SoundService = SoundService(self)
        self.children: list = [
            self.Assets, self.EngineRenderService, self.EngineEventService,
            self.UserInputService, self.Object, self.Workspace, self.GUIService,
            self.ScriptService, self.SoundService
        ]

    def getService(self, name: str) -> object:
        try:
            return getattr(self, name)
        except Exception:
            openErrorWindow(f'No service named "{name}".', self.parent)

    def update(self) -> None:
        # update children
        for service in self.children:
            if hasattr(service, 'update'):
                service.update()


# OBJECT CLASSES:

class Camera(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'Camera'
        self.position: list = [0, 0]
        self.fieldOfView: float = 100

    def setAttribute(self, name: str, val) -> None:
        self.attributes.update({name: val})

    def getAttribute(self, name: str) -> any:
        try:
            return self.attributes[name]
        except Exception:
            openErrorWindow(f'unknown attribute "{name}".', self.getEngine())

class Entity(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'Entity'
        self.image = None
        self.position: list = [0, 0]
        self.render: bool = True
        self.children: list = []
        self.childrenQueue: list = []
        self.collisionGroup: int = 0
        self.size: list = [1, 1]
        self.rotation: float = 0

    def isColliding(self, name, parent='Workspace') -> bool:
        game = self.getGameService()
        workspace = game.getService('Workspace')
        if parent == 'Workspace':
            parentObj = workspace
        else:
            parentObj = parent
        # collision
        if parentObj != None:
            child = parentObj.getChild(name)
            if child != None:
                childRect = pygame.Rect(child.position[0], child.position[1], child.image.get_width(), child.image.get_height())
                childRect.width *= child.size[0]
                childRect.height *= child.size[1]
                selfRect = pygame.Rect(self.position[0], self.position[1], self.image.get_width(), self.image.get_height())
                selfRect.width *= self.size[0]
                selfRect.height *= self.size[1]
                return selfRect.colliderect(childRect)
        return False

    def getChild(self, name) -> object:
        try:
            return getattr(self, name)
        except Exception:
            for child in self.children:
                if child.name == name:
                    return child
            return None

    def _update(self) -> None:
        self.updateQueue()
        self.childrenEvents()

    def updateQueue(self) -> None:
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        window = self.getEngine().window
        for child in self.children:
            if hasattr(child, 'update'):
                child.update(window.dt)
                if child.type == 'ParticleEmitter':
                    if hasattr(child, 'update'):
                        child.update(window.dt)
                    child.render(window.dt)
            if hasattr(child, '_update'):
                child._update()

    def getChildren(self) -> list:
        return self.children.copy()

class Folder(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'Folder'
        self.children: list = []
        self.childrenQueue: list = []

    def getChild(self, name: str) -> object:
        try:
            return getattr(self, name)
        except Exception:
            return None

    def _update(self) -> None:
        self.updateQueue()
        self.childrenEvents()

    def updateQueue(self) -> None:
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        window = self.getEngine().window
        for child in self.children:
            if hasattr(child, 'update'):
                if child.type == 'ScreenGUI':
                    if child.enabled:
                        child.update(window.dt)
                else:
                    child.update(window.dt)
                if child.type == 'ParticleEmitter':
                    child.render(window.dt)
            if hasattr(child, '_update'):
                child._update()

    def getChildren(self) -> list:
        return self.children.copy()

class GlobalScript(GameObject):
    def __init__(self, parent: object):
        super().__init__(parent)
        self.name = self.type = 'GlobalScript'

class ParticleEmitter(GameObject):
    def __init__(self, parent: object):
        super().__init__(parent)
        self.name = self.type = 'ParticleEmitter'
        self.children: list = []
        self.childrenQueue: list = []
        self.particleData: list= []
        # particle 2D list:
        # [pos, vel, color, size, acc, sizeAccel, shape, collidable, collisionGroup]

    def create(self, position: list, velocity: list, color: tuple, size:float, acceleration: tuple=(0, 0), sizeAccel: float=0, shape: str='circle', collidable: bool=False, collisionGroup: int=0) -> None:
        self.particleData.append([position, velocity, color, size, acceleration, sizeAccel, shape, collidable, collisionGroup])

    def updateParticleVelocity(self, particle: list, dt: float):
        game = self.getGameService()
        workspace = game.getService('Workspace')
        camX, camY = self.getCameraPosition(workspace)
        particle[1][0] += particle[4][0]*dt
        if particle[7]: # check if collidable
            for child in workspace.getChildren():
                if child.type == 'Entity' and child.collisionGroup == particle[8] and child.image != None:
                    self.particleCollision(child, particle, camX, camY, dt)
                if child.type == 'Folder':
                    for child2 in child.getChildren():
                        self.particleCollision(child2, particle, camX, camY, dt)
        else:
            particle[1][1] += particle[4][1]*dt

    def particleCollision(self, child: object, particle: list, camX: float, camY: float, dt: float) -> None:
        childRect = pygame.Rect(child.position[0], child.position[1], child.image.get_width(), child.image.get_height())
        childRect.width *= child.size[0]
        childRect.height *= child.size[1]
        childRect.x = (child.position[0] - camX)-childRect.width/2
        childRect.y = (child.position[1] - camY)-childRect.height/2
        selfRect = pygame.Rect(particle[0][0]-camX, particle[0][1]-camY, particle[3], particle[3])
        if childRect.colliderect(selfRect):
            # reset y velocity
            particle[0][1] -= particle[1][1]
            particle[1][1] = 0
        else:
            particle[1][1] += particle[4][1]*dt
        for child2 in child.getChildren():
            self.particleCollision(child2, particle, camX, camY, dt)


    def render(self, dt: float) -> None:
        # FIXME THIS PLACE HAS MAJOR CAMERA ISSUES AND MOSTLY NEEDS THE CAMERA POS TO BE MANUALLY ADDED BY THE USER.
        # FIX THIS!!!!!!!!
        game = self.getGameService()
        workspace = game.getService('Workspace')
        window = game.parent.window
        windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])
        renderService = game.getService('EngineRenderService')
        camX, camY = self.getCameraPosition(workspace)
        # updating the particles
        for particle in self.particleData:
            # update position
            particle[0][0] += particle[1][0]*dt
            particle[0][1] += particle[1][1]*dt
            self.updateParticleVelocity(particle, dt)
            # update size
            particle[3] += particle[5]*dt
            # delete any small particle
            if particle[3] < 0.1:
                self.particleData.remove(particle)

        # rendering
        for particle in self.particleData:
            if not particle[0][0] > constants.DEFAULTSCREENSIZE[0] and not particle[0][1] > constants.DEFAULTSCREENSIZE[1]:
                x = (particle[0][0]-camX) * windowResolutionRatio[0]
                y = (particle[0][1]-camY) * windowResolutionRatio[1]
                if particle[6] == 'circle':
                    pygame.draw.circle(window.particleWindow, particle[2], (x, y), particle[3] * windowResolutionRatio[1])
                elif particle[6] == 'rectangle':
                    size = particle[3]*windowResolutionRatio[1]
                    pygame.draw.rect(window.particleWindow, particle[2], (x, y, size, size))
                renderService.totalParticlesRendered += 1

    def getCameraPosition(self, workspace: object) -> tuple:
        if workspace.currentCamera != None:  # if a default camera exists:
            camX, camY = workspace.currentCamera.position
        else:
            camX, camY = (0, 0)
        return camX, camY

    def getChild(self, name) -> object:
        try:
            return getattr(self, name)
        except Exception:
            for child in self.children:
                if child.name == name:
                    return child
            return None

    def _update(self) -> None:
        self.updateQueue()
        self.childrenEvents()

    def updateQueue(self) -> None:
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        window = self.getEngine().window
        for child in self.children:
            if hasattr(child, 'update'):
                child.update(window.dt)
                if child.type == 'ParticleEmitter':
                    if hasattr(child, 'update'):
                        child.render(window.dt)
            if hasattr(child, '_update'):
                child._update()

    def getChildren(self) -> list:
        return self.children.copy()

class Raycaster(GameObject):
    def __init__(self, parent: object) -> None:
        self.name = self.type = 'Raycaster'
        super().__init__(parent)
        self.children: list = []
        self.childrenQueue: list = []

    def getCameraPosition(self, workspace: object) -> tuple:
        if workspace.currentCamera != None:  # if a default camera exists:
            camX, camY = workspace.currentCamera.position
        else:
            camX, camY = (0, 0)
        return camX, camY

    def getChild(self, name) -> object:
        try:
            return getattr(self, name)
        except Exception:
            for child in self.children:
                if child.name == name:
                    return child
            return None

    def _update(self) -> None:
        self.updateQueue()
        self.childrenEvents()

    def updateQueue(self) -> None:
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        window = self.getEngine().window
        for child in self.children:
            if hasattr(child, 'update'):
                child.update(window.dt)
                if child.type == 'ParticleEmitter':
                    if hasattr(child, 'update'):
                        child.render(window.dt)
            if hasattr(child, '_update'):
                child._update()

    def getChildren(self) -> list:
        return self.children.copy()

    def drawRect(self, color: tuple, rect, rounded: int=0) -> None:
        game = self.getGameService()
        window = game.parent.window
        windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])
        camX, camY = self.getCameraPosition(game.getService('Workspace'))

        newRect = rect.copy()
        x = (newRect.x - camX) * windowResolutionRatio[0]
        y = (newRect.y - camY) * windowResolutionRatio[1]
        w = newRect.width * windowResolutionRatio[1]
        h = newRect.height * windowResolutionRatio[1]
        pygame.draw.rect(window.renderWindow, color, (x, y, w, h), border_radius=rounded)

    def drawImage(self, name: str, position: list) -> None:
        game = self.getGameService()
        window = game.parent.window
        windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])
        assets = game.getService('Assets')
        camX, camY = self.getCameraPosition(game.getService('Workspace'))

        image = assets.getImage(name)
        pos = [position[0], position[1]]
        x = (pos[0] - camX) * windowResolutionRatio[0]
        y = (pos[1] - camY) * windowResolutionRatio[1]
        w = image.get_width() * windowResolutionRatio[1]
        h = image.get_height() * windowResolutionRatio[1]
        image = pygame.transform.scale(image, (w, h))
        window.renderWindow.blit(image, (x, y))

    def drawPolygon(self, color: tuple, points: list, outline: int=0) -> None:
        engine = self.getEngine()
        window = engine.window
        camX, camY = self.getCameraPosition(engine.game.Workspace)
        windowResolutionRatio = (window.screen.get_width() / constants.DEFAULTSCREENSIZE[0],window.screen.get_height() / constants.DEFAULTSCREENSIZE[1])
        newPoints = []
        for point in points:
            newPoints.append(((point[0]-camX)*windowResolutionRatio[0], (point[1]-camY)*windowResolutionRatio[1]))
        pygame.draw.polygon(engine.window.renderWindow, color, newPoints, outline)

class ScreenGui(GameObject):
    def __init__(self, parent: object) -> None:
        self.parent: object = parent
        self.name = self.type = 'ScreenGui'
        self.enabled: bool = True
        self.primaryRect: pygame.Rect = None
        self.offsetPosition: list = [0, 0]
        self.children: list = []
        self.childrenQueue: list = []

    def writeText(self, text: str, position: list, size: float, color: tuple, font: str='hp_simplified', backgroundColor: tuple=None) -> None:
        window = self.getEngine().window
        assets = self.getGameService().getService('Assets')
        fonts = assets.fonts
        windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])

        textObj = fonts[font].render(str(text), True, color, backgroundColor)
        newPosition = [position[0]+self.offsetPosition[0], position[1]+self.offsetPosition[1]]
        objSize = [textObj.get_width(), textObj.get_height()]
        textObj = pygame.transform.scale(textObj, (objSize[0]*size, objSize[1]*size))
        objSize = [textObj.get_width(), textObj.get_height()]
        textObj = pygame.transform.scale(textObj, (objSize[0]*windowResolutionRatio[1], objSize[1]*windowResolutionRatio[1]))
        x = newPosition[0]*windowResolutionRatio[0]
        y = newPosition[1]*windowResolutionRatio[1]
        textObj = textObj.convert_alpha()
        pos = [x, y]
        window.guiWindow.blit(textObj, pos)

    def drawRect(self, color: tuple, rect, rounded: int=0) -> None:
        game = self.getGameService()
        window = game.parent.window
        windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])

        newRect = rect.copy()
        x = (newRect.x + self.offsetPosition[0]) * windowResolutionRatio[0]
        y = (newRect.y + self.offsetPosition[1]) * windowResolutionRatio[1]
        w = newRect.width * windowResolutionRatio[1]
        h = newRect.height * windowResolutionRatio[1]
        pygame.draw.rect(window.guiWindow, color, (x, y, w, h), border_radius=rounded)

    def drawImage(self, name: str, position: list) -> None:
        game = self.getGameService()
        window = game.parent.window
        windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])
        assets = game.getService('Assets')

        image = assets.getImage(name)
        pos = [position[0], position[1]]
        x = (pos[0] + self.offsetPosition[0]) * windowResolutionRatio[0]
        y = (pos[1] + self.offsetPosition[1]) * windowResolutionRatio[1]
        w = image.get_width() * windowResolutionRatio[1]
        h = image.get_height() * windowResolutionRatio[1]
        image = pygame.transform.scale(image, (w, h))
        window.guiWindow.blit(image, (x, y))

    def drawCheckBox(self, value, position: list) -> None:
        game = self.getGameService()
        assets = game.getService('Assets')
        input = game.getService('UserInputService')
        debugValues = self.getEngine().settings.debugValues
        window = self.getEngine().window
        windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])

        if debugValues[value]:
            image = assets.getImage('checkbox_true')
        else:
            image = assets.getImage('checkbox_false')
        pos = [(position[0] + self.offsetPosition[0]) * windowResolutionRatio[0], (position[1] + self.offsetPosition[1]) * windowResolutionRatio[1]]

        # updating the value
        imageSize = [image.get_width(), image.get_height()]
        checkboxRect = pygame.Rect(pos[0], pos[1], imageSize[0]*windowResolutionRatio[1], imageSize[1]*windowResolutionRatio[1])
        mx, my = input.getMousePosition()
        if checkboxRect.collidepoint(mx, my) and input.mouseStatus[0]:
            debugValues[value] = not debugValues[value]

        # rendering
        image = pygame.transform.scale(image, (imageSize[0]*windowResolutionRatio[1], imageSize[1]*windowResolutionRatio[1]))
        window.guiWindow.blit(image, pos)

    def updateMouseFocus(self) -> None:
        if self.primaryRect != None and self.enabled:
            window = self.getEngine().window
            input = self.getGameService().getService('UserInputService')
            x = self.primaryRect.x + self.offsetPosition[0]
            y = self.primaryRect.y + self.offsetPosition[1]
            w = self.primaryRect.width
            h = self.primaryRect.height
            windowResolutionRatio = (window.screen.get_width()/constants.DEFAULTSCREENSIZE[0], window.screen.get_height()/constants.DEFAULTSCREENSIZE[1])
            rect = pygame.Rect(x*windowResolutionRatio[0], y*windowResolutionRatio[1], w*windowResolutionRatio[1], h*windowResolutionRatio[1])
            mx, my = input.getMousePosition()
            if rect.collidepoint(mx, my):
                input.mouseFocus = self.name
            else:
                input.mouseFocus = 'Game'
            # NOTE mouse focus may have some issues

    def _update(self) -> None:
        input = self.getGameService().getService('UserInputService')
        self.updateQueue()
        self.childrenEvents()
        self.updateMouseFocus()
        if not self.enabled and input.mouseFocus == self.name:
            input.mouseFocus = 'Game'

    def getChild(self, name: str) -> object:
        try:
            return getattr(self, name)
        except Exception:
            for child in self.children:
                if child.name == name:
                    return child
            return None

    def updateQueue(self) -> None:
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        window = self.getEngine().window
        for child in self.children:
            if hasattr(child, 'update'):
                child.update(window.dt)
                if child.type == 'ParticleEmitter':
                    if hasattr(child, 'update'):
                        child.update(window.dt)
                    child.render(window.dt)
            if hasattr(child, '_update'):
                child._update()

    def getChildren(self) -> list:
        return self.children.copy()

class Viewport(GameObject):
    def __init__(self, parent: object) -> None:
        self.name = self.type = 'Viewport'
        super().__init__(parent)
        self.background: list = [45, 45, 45]
        self.outline: float = 0
        self.size: list = [75, 50]
        self.enabled: bool = True
        self.transparency: int = 100
        self.position: list = [0, 0]
        self.children: list = []
        self.childrenQueue: list = []

    def updateViewport(self) -> None:
        engine = self.getEngine()
        window = engine.window

        surface = pygame.Surface(self.size)
        surface = surface.convert()
        surface.fill(self.background)
        # rendering object inside:
        windowResolutionRatio = [self.size[0]/constants.DEFAULTSCREENSIZE[0], self.size[1]/constants.DEFAULTSCREENSIZE[1]]

        for child in self.getChildren():
            if child.type == 'Entity' and child.image != None:
                pos = [child.position[0], child.position[1]]
                size = [child.image.get_width(), child.image.get_height()]
                size[0] *= windowResolutionRatio[1]
                size[1] *= windowResolutionRatio[1]
                img = pygame.transform.scale(child.image, size)
                img = pygame.transform.rotate(img, child.rotation)
                pos[0] *= windowResolutionRatio[0]
                pos[1] *= windowResolutionRatio[1]
                pos[0] -= img.get_width()/2
                pos[1] -= img.get_height()/2
                surface.blit(img, pos)

        window.gui_window.blit(surface, self.position)

    def getChild(self, name) -> object:
        try:
            return getattr(self, name)
        except Exception:
            for child in self.children:
                if child.name == name:
                    return child
            return None

    def _update(self) -> None:
        self.updateQueue()
        self.childrenEvents()
        if self.enabled:
            self.updateViewport()

    def updateQueue(self) -> None:
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        window = self.getEngine().window
        for child in self.children:
            if hasattr(child, 'update'):
                child.update(window.dt)
                if child.type == 'ParticleEmitter':
                    if hasattr(child, 'update'):
                        child.render(window.dt)
            if hasattr(child, '_update'):
                child._update()

    def getChildren(self) -> list:
        return self.children.copy()

class Folder(GameObject):
    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self.name = self.type = 'Folder'
        self.children: list = []
        self.childrenQueue: list = []

    def getChild(self, name: str) -> object:
        try:
            return getattr(self, name)
        except Exception:
            for child in self.children:
                if child.name == name:
                    return child
            return None

    def _update(self) -> None:
        self.updateQueue()
        self.childrenEvents()

    def updateQueue(self) -> None:
        if len(self.childrenQueue) > 0:
            newChild = self.childrenQueue[0]
            self.children.append(self.childrenQueue[0])
            del self.childrenQueue[0]
            # SETUP/PARENT EVENTS:
            if hasattr(newChild, 'setup'):
                self.setAttributeOfObject(newChild)
                newChild.setup()

    def childrenEvents(self) -> None:
        window = self.getEngine().window
        for child in self.children:
            if hasattr(child, 'update'):
                if child.type == 'ScreenGUI':
                    if child.enabled:
                        child.update(window.dt)
                else:
                    child.update(window.dt)
                if child.type == 'ParticleEmitter':
                    child.render(window.dt)
            if hasattr(child, '_update'):
                child._update()

    def getChildren(self) -> list:
        return self.children.copy()

# OTHER:
def Rectangle(x: float, y: float, width: float, height: float) -> pygame.Rect:
    return pygame.Rect(x, y, width, height)

# ENGINE CLASSES & FUNCTIONS:

class Window(object):
    def __init__(self, parent: object) -> None:
        pygame.display.set_caption(constants.WINDOWTITLE)

        self.parent: object = parent
        self.screen: pygame.Surface = pygame.display.set_mode(constants.DEFAULTSCREENSIZE, constants.FLAGS, 32)
        self.renderWindow: pygame.Surface = self.screen.copy()
        self.guiWindow: pygame.Surface = self.screen.copy()
        self.particleWindow: pygame.Surface = self.screen.copy()

        self.dt: float = 0
        self.last_time: float = time.time()
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.performance = 'Very Good'
        self.fullscreen: bool = False
        self.cursors: dict = {
            'i-beam': SYSTEM_CURSOR_IBEAM,
            'hand': SYSTEM_CURSOR_HAND,
            'wait': SYSTEM_CURSOR_WAIT,
            'arrow': SYSTEM_CURSOR_ARROW,
            'crosshair': SYSTEM_CURSOR_CROSSHAIR
        }
        self.cursor: str = 'arrow'

        pygame.font.init()

    def getWindowSize(self) -> tuple:
        return self.screen.get_size()

    def setBackgroundColor(self, color: tuple) -> None:
        global constants
        constants.BACKGROUND_COLOR = color

    def getBackgroundColor(self) -> tuple:
        return constants.BACKGROUND_COLOR

    def setMouseVisible(self, val: bool) -> None:
        try:
            pygame.mouse.set_visible(val)
        except Exception:
            openErrorWindow(f'Boolean expected, got {val}', self.parent)

    def getMouseVisible(self) -> bool:
        return pygame.mouse.get_visible()

    def setTargetFPS(self, value: int) -> None:
        constants.FPS_CAP = value

    def getFPS(self) -> int:
        return int(self.clock.get_fps())

    def setup(self) -> None:
        assets = self.parent.game.getService('Assets')
        pygame.display.set_caption(f'{constants.WINDOWTITLE}')

    def update(self) -> None:
        self.updateSurfaceSizes()
        self.screen.fill(constants.BACKGROUND_COLOR)
        self.renderWindow.fill(constants.BACKGROUND_COLOR)
        self.guiWindow.fill(constants.BACKGROUND_COLOR)
        self.particleWindow.fill(constants.BACKGROUND_COLOR)
        game = self.parent.game
        RenderService = game.getService('EngineRenderService')
        EventService = game.getService('EngineEventService')
        input = self.parent.game.getService('UserInputService')
        engine = self.parent
        # update delta time:
        self.dt = time.time() - self.last_time
        self.last_time = time.time()
        self.dt *= 60

        RenderService.totalParticlesRendered = 0

        # events
        game.update()
        EventService.events()
        # rendering stuff
        RenderService.render()
        # update the screen:
        self.screen.blit(self.renderWindow, (0, 0))
        self.screen.blit(self.particleWindow, (0, 0))
        self.screen.blit(self.guiWindow, (0, 0))
        self.clock.tick(constants.FPS_CAP)

        if input.mouseFocus != 'Game':
            self.setCursor(self.cursor)
        else:
            self.setCursor('arrow')
        pygame.display.flip()

    def updateSurfaceSizes(self) -> None:
        self.renderWindow = self.screen.copy()
        self.guiWindow = self.screen.copy()
        self.particleWindow = self.screen.copy()
        self.guiWindow.set_colorkey(constants.BACKGROUND_COLOR)
        self.particleWindow.set_colorkey(constants.BACKGROUND_COLOR)

    def setCursor(self, name: str) -> None:
        try:
            pygame.mouse.set_cursor(self.cursors[name])
        except Exception:
            openErrorWindow(f'No cursor named "{name}".', self.parent)

class Engine(object):
    def __init__(self, windowSize: tuple=(640, 360), windowTitle: str='CORP Engine window', flags: int=0) -> None:
        global constants
        pygame.mixer.init()
        constants.DEFAULTSCREENSIZE = windowSize
        constants.WINDOWTITLE = windowTitle
        constants.FLAGS = flags
        self.window: Window = Window(self)
        if flags == -2147483136:  # detect fullscreen
            self.window.fullscreen = True

        self.game: GameService = GameService(self)
        self.status: any = None
        self.type: str = 'Engine'

    def mainloop(self) -> None:
        print(f'Powered by pygame v{pygame.version.ver} & CORP Engine v{constants.ENGINEVERSION}\nMade by PyxleDev0.')
        if self.status == None:
            self.window.setup()
            self.status = constants.RUNNING
            while self.status:
                self.window.update()

def init(windowSize: tuple=(640, 360), windowTitle: str='CORP Engine Window', flags: int=0) -> Engine:
    return Engine(windowSize, windowTitle, flags)
