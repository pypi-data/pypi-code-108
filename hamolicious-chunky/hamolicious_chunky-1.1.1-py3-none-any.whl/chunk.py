from vector import Vec2d

class Chunk:
	size = None

	def __init__(self, pos:Vec2d) -> None:
		self.pos = Vec2d(pos)
		self.size = Vec2d(Chunk.size)

		self.objects = []
