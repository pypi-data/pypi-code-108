from vector import Vec2d
from chunky import DidntReturnChunk, Chunk


class World:
	render_dist = Vec2d(3)

	@staticmethod
	def to_world_space(pos:Vec2d):
		return pos.mult(Chunk.size)

	@staticmethod
	def to_chunk_space(pos:Vec2d):
		x = pos.x // Chunk.size.w
		y = pos.y // Chunk.size.h

		return Vec2d(x, y)

	@staticmethod
	def get_render_dist():
		return World.render_dist.copy()

	def __init__(self, player_pos:Vec2d) -> None:
		self.min_loc = World.to_chunk_space(player_pos).sub(self.get_render_dist())
		self.max_loc = World.to_chunk_space(player_pos).add(self.get_render_dist())

		self.__chunks = {}
		self.__loaded_chunks = []

		self.__pre_generate_chunks(player_pos)


	def get_chunks(self):
		return self.__chunks.copy()

	def get_loaded_chunks(self):
		return self.__loaded_chunks.copy()

	def get_active_chunk(self, player_pos:Vec2d):
		pos = World.to_chunk_space(player_pos)
		return self.__chunks.get(self.__generate_key(int(pos.x), int(pos.y)))

	def __generate_key(self, j, i):
		return f'{j}:{i}'

	def __check_chunk(self, chunk):
		if type(chunk) is not Chunk : raise DidntReturnChunk('generate_chunk() didn\'t return chunky.Chunk')

	def __add_chunk(self, j, i):
		chunk = self.generate_chunk(Vec2d(j, i))
		self.__check_chunk(chunk)
		self.__chunks[self.__generate_key(j, i)] = chunk

	def __pre_generate_chunks(self, player_pos:Vec2d):
		for i in range(int(self.min_loc.y), int(self.max_loc.y)):
			for j in range(int(self.min_loc.x), int(self.max_loc.x)):
				self.__add_chunk(j, i)


	def generate_chunk(self, pos:Vec2d):
		raise NotImplementedError('Implement Chunk Generation, has to return a chunky.Chunk')

	def update(self, player_pos:Vec2d):
		self.min_loc = World.to_chunk_space(player_pos).sub(self.get_render_dist())
		self.max_loc = World.to_chunk_space(player_pos).add(self.get_render_dist())

		self.__loaded_chunks = []

		for i in range(int(self.min_loc.y), int(self.max_loc.y)):
			for j in range(int(self.min_loc.x), int(self.max_loc.x)):
				if self.__chunks.get(self.__generate_key(j, i)) is None:
					self.__add_chunk(j, i)
				else:
					self.__loaded_chunks.append(self.__chunks.get(self.__generate_key(j, i)))


