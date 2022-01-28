# This is a CORP Engine example about getting keyboard input and
# using it to move an Entity.

# Importing ----------------------------------------------------|
import corpengine1 as corp

# Initilization ------------------------------------------------|
engine = corp.init(windowTitle='Examples - Keyboard Input', windowSize=(960, 720))

# Entity Class -------------------------------------------------|
class MyEntity(corp.Entity):
    def setup(self) -> None:
        # loading & setting image
        assets = engine.game.Assets
        assets.loadImage('assets/square.png', 'square')
        self.image = assets.getImage('square')
        # adding input keys:
        input = engine.game.UserInputService
        input.addInput('move left', [corp.K_LEFT, corp.K_a])
        input.addInput('move right', [corp.K_RIGHT, corp.K_d])
        input.addInput('move up', [corp.K_UP, corp.K_w])
        input.addInput('move down', [corp.K_DOWN, corp.K_s])
        # setting start position:
        self.position = [480, 360]

    def update(self, deltaTime: float) -> None:
        input = engine.game.UserInputService
        SPEED = 5 * deltaTime
        if input.keyPressed('move left'):
            self.position[0] -= SPEED
        if input.keyPressed('move right'):
            self.position[0] += SPEED
        if input.keyPressed('move up'):
            self.position[1] -= SPEED
        if input.keyPressed('move down'):
            self.position[1] += SPEED

# User Interface -----------------------------------------------|
class Ui(corp.ScreenGui):
    def setup(self) -> None:
        # load font:
        assets = engine.game.Assets
        assets.loadFont('assets/Dongle-Regular.ttf', 'font', 64)

    def update(self) -> None:
        self.writeText('Use WASD or Arrow Keys to Move', [160, 0], 1, corp.colors.BLACK, 'font')

# Adding objects -----------------------------------------------|
obj = engine.game.Object
workspace = engine.game.Workspace
guiService = engine.game.GUIService
obj.new(MyEntity(workspace), putInQueue=True)
obj.new(Ui(guiService), putInQueue=True)
# when putInQueue is set to True, the game will put the child in a queue
# before instantly loading it. This may improve startup performance in yo-
# ur games.

engine.window.setTargetFPS(120)  # set the maximum FPS to 120
# Mainloop -----------------------------------------------------|
engine.mainloop()