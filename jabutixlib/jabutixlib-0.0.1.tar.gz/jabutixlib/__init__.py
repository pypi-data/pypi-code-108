import websocket

msgtype_commandMoveForward = 'c'
msgtype_commandMoveLeft = 'd'
msgtype_commandMoveRight = 'e'

msgtype_callbackMovedForward = 'h'
msgtype_callbackMovedLeft = 'i'
msgtype_callbackMovedRight = 'j'

class JabutiXAPI:
    def __init__(self):
        #websocket.enableTrace(True)
        self.ws = websocket.create_connection("ws://raspberrypi:3000/api")

    def MoveForward(self):
        print("Movendo o jabuti físico à frente...")
        self.ws.send(msgtype_commandMoveForward)
        self.ws.recv()
        print("Jabuti finalizou movimento à frente")

    def MoveLeft(self):
        print("Movendo o jabuti físico à esquerda...")
        self.ws.send(msgtype_commandMoveLeft)
        self.ws.recv()
        print("Jabuti finalizou movimento à esquerda")

    def MoveRight(self):
        print("Movendo o jabuti físico à direita...")
        self.ws.send(msgtype_commandMoveRight)
        self.ws.recv()
        print("Jabuti finalizou movimento à direita")