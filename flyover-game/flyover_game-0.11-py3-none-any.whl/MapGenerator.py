import random
from importlib import resources

import pygame


class Map:
    def __init__(self, map_size):
        self.tile_size = 64
        self.map_width = map_size[0]
        self.map_height = map_size[1]
        self.tiles = []

        with resources.path("flyover.assets.tiles", "Grass.png") as path:
            self.tiles.append(path)
        with resources.path("flyover.assets.tiles", "Sea.png") as path:
            self.tiles.append(path)

        self.tile_map = []
        for column in range(0, self.map_width, self.tile_size):
            for row in range(0, self.map_height, self.tile_size):
                tile_coordinate = (column, row)
                tile = self.select_tile()
                self.tile_map.append((tile_coordinate, pygame.image.load(tile)))

    def select_tile(self):
        # TODO draw more terrain tiles and come up with code to arrange semi - not totally randomly
        tile = random.choice(self.tiles)
        return tile
