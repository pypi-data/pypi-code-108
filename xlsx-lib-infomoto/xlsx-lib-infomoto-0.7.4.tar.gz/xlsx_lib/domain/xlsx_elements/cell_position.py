abc = 'ABCDEFGHIJKLMNSOPQRSTUVWXYZ'


class CellPosition:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y + 1
        self.position = abc[self.x] + str(self.y)
