import math
import random
from importlib import resources

import pygame

class Camera:
    def __init__(self, player, window_size, map):
        self.camera_width = window_size[0]
        self.camera_height = window_size[1]
        self.player = player
        self.map = map
        self.move()

    def move(self):
        self.rect = (self.player.collision_box.centerx - int(self.camera_width / 2),
                     self.player.collision_box.centery - int(self.camera_height / 2),
                     self.player.collision_box.centerx + int(self.camera_width / 2),
                     self.player.collision_box.centery + int(self.camera_height / 2))

    def active_tiles(self):
        # returns a list of tile tuples(x,y,img) that are currently around the player
        # and within the range of the camera
        active_tiles = []
        for tile in self.map.tile_map:
            if tile[0][0] in range(self.rect[0] - 64, self.rect[2] + 64):
                if tile[0][1] in range(self.rect[1] - 64, self.rect[3] + 64):
                    active_tiles.append(tile)
        return active_tiles


class Jet:
    speed = 2
    acceleration = 1
    rotation_speed = 5
    maximum_speed = 20
    minimum_speed = 2
    sprite_size = (64, 64)

    def __init__(self, starting_coordinates, map_size):
        self.angle = starting_coordinates[2]
        # x and y = center of entity, blitx and blity = top left corner
        # angle defined as 0 degrees North, 90 deg East etc.
        # Collision box defined as the inner 1/4 of the sprite
        self.collision_box = pygame.Rect((starting_coordinates[0] - self.sprite_size[0] / 4,
                                          starting_coordinates[1] - self.sprite_size[1] / 4),
                                         (self.sprite_size[0] / 2, self.sprite_size[1] / 2))
        # initialise game and blit coordinates
        self.update_coordinates()
        self.map_size = map_size
        self.state = 'level'

    def update_coordinates(self):
        # Draw x and draw y give the top left of the sprite - the coordinates passed to blit
        self.blit_x = self.collision_box.centerx - self.sprite_size[0] / 2
        self.blit_y = self.collision_box.centery - self.sprite_size[1] / 2
        self.x = self.collision_box.centerx
        self.y = self.collision_box.centery
        self.coord = (self.x, self.y)

    def stay_within_map(self):
        if self.x <= 0:
            self.angle = 90
        if self.y <= 0:
            self.angle = 180
        if self.x >= self.map_size[0]:
            self.angle = 270
        if self.y >= self.map_size[1]:
            self.angle = 0

    def within_active_area(self, camera):
        if self.x in range(camera.rect[0], camera.rect[2]):
            if self.y in range(camera.rect[1], camera.rect[3]):
                return True

    def move(self):
        x_diff = int(self.speed * math.sin(math.radians(self.angle)))
        y_diff = int(self.speed * math.cos(math.radians(self.angle))) * -1
        self.collision_box.move_ip(x_diff, y_diff)
        self.update_coordinates()
        self.stay_within_map()

    def normalize_angle(self, angle):
        if angle < 0:
            angle += 360
        elif angle >= 360:
            angle -= 360
        return int(angle)

    def rotate(self, direction):
        self.angle += direction * self.rotation_speed
        self.angle = self.normalize_angle(self.angle)

    def accelerate(self, direction):
        if self.speed == self.maximum_speed:
            if direction == -1:
                self.speed += direction * self.acceleration
        elif self.speed == self.minimum_speed:
            if direction == 1:
                self.speed += direction * self.acceleration
        else:
            self.speed += direction * self.acceleration

    def player_angle(self, player):
        # tells you what angle entity needs to point at to face player
        dist, x_diff, y_diff = self.distance_to_player(player)
        if dist == 0:  # Currently at the player's position
            return int(player.angle)

        angle = math.degrees(math.acos(x_diff / dist))
        if angle == 0:
            return 90
        elif angle == 180:
            return 270
        if y_diff > 0:
            angle += 90
        elif y_diff < 0:
            angle = 90 - angle

        return int(self.normalize_angle(angle))

    def distance_to_player(self, player):
        x_diff = player.x - self.x
        y_diff = player.y - self.y
        dist = math.hypot(x_diff, y_diff)
        return dist, x_diff, y_diff

    def shoot_missile(self):
        return Missile((self.x, self.y, self.angle), str(self), self.map_size)


class Player(Jet):
    def __init__(self, starting_coordinates, map_size):
        Jet.__init__(self, starting_coordinates, map_size)
        with resources.path("flyover.assets.sprites", "player.png") as path:
            self.sprite_level = pygame.image.load(path)
        with resources.path("flyover.assets.sprites", "player_left.png") as path:
            self.sprite_left = pygame.image.load(path)
        with resources.path("flyover.assets.sprites", "player_right.png") as path:
            self.sprite_right = pygame.image.load(path)

    def __str__(self):
        return 'Player'


class Enemy(Jet):
    def __init__(self, starting_coordinates, map_size):
        Jet.__init__(self, starting_coordinates, map_size)
        self.behaviours = (self.turn_left, self.turn_right, self.do_nothing,
                           self.speed_up, self.slow_down, self.follow_player)
        self.speed = 2
        self.firing_range = 200
        # starting behaviours
        self.behaviour = self.do_nothing
        self.last_behaviour = self.do_nothing
        self.last_behaviour_time = 0
        self.hit = False

    def __repr__(self):
        return 'Enemy @ ' + str(self.coord)

    def __str__(self):
        return 'Enemy'

    def move(self):
        super().move()
        # add to the behaviour counter after every move
        self.last_behaviour_time += 1

    def choose_behaviour(self, player):  # All behaviours need optional kwargs so player can be passed to follow player
        if self.last_behaviour == self.turn_left:
            self.behaviour = self.do_nothing
        elif self.last_behaviour == self.turn_right:
            self.behaviour = self.do_nothing
        else:
            self.behaviour = random.choice(self.behaviours)
            self.behaviour_duration = random.randint(5, 30)
        self.behaviour(player=player)
        self.last_behaviour = self.behaviour

    def turn_left(self, **kwargs):
        if self.last_behaviour_time < self.behaviour_duration:
            self.rotate(-1)
            self.state = 'left'
        else:
            self.state = 'level'

    def turn_right(self, **kwargs):
        if self.last_behaviour_time < self.behaviour_duration:
            self.rotate(1)
            self.state = 'right'
        else:
            self.state = 'level'

    def slow_down(self, **kwargs):
        self.state = 'level'
        if self.last_behaviour_time < int(self.behaviour_duration / 10):  # /10 to avoid hitting min/max speed in one go
            self.accelerate(-1)

    def speed_up(self, **kwargs):
        self.state = 'level'
        if self.last_behaviour_time < int(self.behaviour_duration / 10):
            self.accelerate(1)

    def follow_player(self, player):
        if self.last_behaviour_time < int(self.behaviour_duration):
            target_angle = self.player_angle(player)
            angle_change = abs(target_angle - self.angle)
            # check to make sure won't try to turn more than 180 degrees
            opposite = False  # if angle is more than 180 it's quicker to go the other way
            if angle_change > 180:
                opposite = True
            elif angle_change == 180:  # don't get stuck flying away from player
                self.turn_right()
            # choose direction to turn
            if self.angle > target_angle:
                if opposite:
                    self.turn_right()
                else:
                    self.turn_left()
            elif self.angle < target_angle:
                if opposite:
                    self.turn_left()
                else:
                    self.turn_right()

    def do_nothing(self, **kwargs):
        self.state = 'level'
        pass

    def check_sights(self, player):
        dist = self.distance_to_player(player)[0]
        if dist <= self.firing_range:
            # check nose is +- 10 degrees of player
            if self.angle in range(self.player_angle(player) - 10, self.player_angle(player) + 10):
                return self.shoot_missile()


class Missile(Jet):
    speed = Jet.maximum_speed + 10
    fuse = 20

    def __init__(self, starting_coordinates, shooter, map_size):
        Jet.__init__(self, starting_coordinates, map_size)
        self.x = starting_coordinates[0]  # start in sprite's center
        self.y = starting_coordinates[1]
        self.angle = starting_coordinates[2]
        self.shooter = shooter
        self.time_alive = 0
        width, height = 2, 6
        if self.angle in range(315, 360):
            x, y = width, height
        elif self.angle in range(0, 46):
            x, y = width, height
        elif self.angle in range(135, 226):
            x, y = width, height
        else:
            x, y = height, width
        self.surface = pygame.Surface((x, y))
        self.surface.fill((255, 255, 255))
        self.collision_box = pygame.Rect((self.x - 1, self.y - 1), (width, height))

    def __str__(self):
        return 'Missile shot by ' + self.shooter

    def move(self):
        super().move()
        self.time_alive += 1

    def check_hits(self, entity):
        if self.collision_box.colliderect(entity.collision_box):
            return True

    def stay_within_map(self):
        pass


class Mig35(Enemy):
    def __init__(self, starting_coordinates, map_size):
        Enemy.__init__(self, starting_coordinates, map_size)
        with resources.path("flyover.assets.sprites", "Mig35.png") as path:
            self.sprite_level = pygame.image.load(path)
        with resources.path("flyover.assets.sprites", "Mig35_left.png") as path:
            self.sprite_left = pygame.image.load(path)
        with resources.path("flyover.assets.sprites", "Mig35_right.png") as path:
            self.sprite_right = pygame.image.load(path)



class Mig21(Enemy):
    def __init__(self, starting_coordinates, map_size):
        Enemy.__init__(self, starting_coordinates, map_size)
        with resources.path("flyover.assets.sprites", "Mig21.png") as path:
            self.sprite_level = pygame.image.load(path)
        with resources.path("flyover.assets.sprites", "Mig21_left.png") as path:
            self.sprite_left = pygame.image.load(path)
        with resources.path("flyover.assets.sprites", "Mig21_right.png") as path:
            self.sprite_right = pygame.image.load(path)
