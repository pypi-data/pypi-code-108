import sys
import random
import os
from importlib import resources

import pygame

import flyover.MapGenerator as MapGenerator
import flyover.Entities as Entities


class GameEngine:
    def __init__(self, settings):
        self.settings = settings
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.settings['window_position'][0],
                                                        self.settings['window_position'][1])
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        self.enemy_kill_sfx = []
        for sound in ["explosion_1.ogg", "explosion_2.ogg", "explosion_3.ogg"]:
            with resources.path("flyover.assets.sound_effects.ogg", sound) as path:
                self.enemy_kill_sfx.append(pygame.mixer.Sound(path))

        self.shooting_sfx = []
        for sound in ["shooting_1.ogg", "shooting_2.ogg", "shooting_3.ogg"]:
            with resources.path("flyover.assets.sound_effects.ogg", sound) as path:
                self.shooting_sfx.append(pygame.mixer.Sound(path))

        with resources.path("flyover.assets.sound_effects.ogg", "player_death.ogg") as path:
            self.death_sfx = pygame.mixer.Sound(path)

        self.FPS_clock = pygame.time.Clock()
        self.window = pygame.display.set_mode(self.settings['window_size'])
        pygame.display.set_caption('Flyover')
        pygame.key.set_repeat(10)  # Enables direction button to be held
        self.start_game()

    def start_game(self):
        self.loading_screen()
        self.map = MapGenerator.Map(self.settings['map_size'])
        self.Player = Entities.Player((int(self.settings['window_size'][0] / 2),
                                       int(self.settings['window_size'][1] / 2),
                                       180),
                                      self.settings['map_size'])
        self.entities = self.create_entities()
        self.projectiles = []
        self.Camera = Entities.Camera(self.Player, self.settings['window_size'],
                                      self.map)
        self.score = 0
        self.game_loop()

    def game_loop(self):
        game_over = False
        while True:
            if game_over:
                self.game_over_screen()
            if self.score == self.settings['number_of_enemies'] * 10:
                self.victory_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_program()

                self.Player.state = 'level'

                # Key bindings
                # todo can't press two keys at once, like turn and fire at the same time
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.Player.accelerate(1)
                    if event.key == pygame.K_DOWN:
                        self.Player.accelerate(-1)
                    if event.key == pygame.K_LEFT:
                        self.Player.rotate(-1)
                        self.Player.state = 'left'
                    if event.key == pygame.K_RIGHT:
                        self.Player.rotate(1)
                        self.Player.state = 'right'
                    if event.key == pygame.K_ESCAPE:
                        self.close_program()
                    if event.key == pygame.K_SPACE:
                        self.projectiles.append(self.Player.shoot_missile())
                        random.choice(self.shooting_sfx).play()

            # Player update
            self.Player.move()
            self.reset_screen()
            if self.Player.state == 'right':
                sprite = self.Player.sprite_right
            elif self.Player.state == 'left':
                sprite = self.Player.sprite_left
            else:
                sprite = self.Player.sprite_level

            player_sprite = pygame.transform.rotate(sprite, self.Player.angle * -1)
            self.window.blit(player_sprite, (int(self.settings['window_size'][0] / 2 - 32),
                                             int(self.settings['window_size'][1] / 2 - 32)))

            # Enemy updates
            for entity in self.entities:
                if entity.last_behaviour_time > self.settings['FPS'] * self.settings['enemy_behaviour_time']:
                    entity.choose_behaviour(self.Player)
                    entity.last_behaviour_time = 0
                else:
                    entity.behaviour(player=self.Player)
                    entity.move()
                shoot = entity.check_sights(self.Player)
                if shoot:
                    self.projectiles.append(shoot)
                    random.choice(self.shooting_sfx).play()

                # Draw enemies
                if entity.within_active_area(self.Camera):
                    if entity.state == 'right':
                        enemy_sprite = pygame.transform.rotate(entity.sprite_right, entity.angle * -1)
                    elif entity.state == 'left':
                        enemy_sprite = pygame.transform.rotate(entity.sprite_left, entity.angle * -1)
                    else:
                        enemy_sprite = pygame.transform.rotate(entity.sprite_level, entity.angle * -1)

                    self.window.blit(enemy_sprite, (self.convert_to_screen_coordinates
                                                    ((entity.blit_x, entity.blit_y))))

            # Projectile updates
            for projectile in self.projectiles:
                if projectile.time_alive > projectile.fuse:
                    del projectile
                    continue
                projectile.move()
                # Check player hits
                if projectile.check_hits(self.Player):
                    if projectile.shooter != str(self.Player):
                        self.death_sfx.play()
                        if not self.settings['invulnerable']:
                            game_over = True
                # Check enemy hits
                for entity in self.entities:
                    if projectile.check_hits(entity):
                        if projectile.shooter == str(self.Player):  # only allow player to hit enemies
                            entity.hit = True
                            random.choice(self.enemy_kill_sfx).play()
                            self.score += 10
                if projectile.within_active_area(self.Camera):
                    self.window.blit(projectile.surface,
                                     (self.convert_to_screen_coordinates((projectile.x, projectile.y))))

                    # delete hit enemies
                    self.entities[:] = [entity for entity in self.entities if not entity.hit]

            # UI
            if self.settings['debug_mode']:
                self.debug_window('Player x = ' + str(self.Player.x) + '   '
                                                                       'Player y = ' + str(self.Player.y))
            self.score_overlay()

            # Game update
            pygame.display.update()
            self.FPS_clock.tick(self.settings['FPS'])

    def loading_screen(self):
        window_size = self.settings['window_size']
        window_x = window_size[0]
        window_y = window_size[1]
        background = pygame.Surface(window_size)
        background.fill((0, 0, 0))
        game_over_font = pygame.font.SysFont(self.settings['game_font'], size=30)

        text_surf = game_over_font.render('Loading', False, (255, 255, 255))
        background.blit(text_surf, (window_x / 2 - 100, window_y / 2))
        self.window.blit(background, (0, 0))
        pygame.display.update()

    def victory_screen(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_program()

                # Key bindings
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.start_game()
                    if event.key == pygame.K_ESCAPE:
                        self.close_program()

            window_size = self.settings['window_size']
            window_x = window_size[0]
            window_y = window_size[1]
            background = pygame.Surface(window_size)
            background.fill((0, 0, 0))
            game_over_font = pygame.font.SysFont(self.settings['game_font'], size=30)

            text_surf = game_over_font.render('You shot down all the planes, you win!', False, (255, 255, 255))
            background.blit(text_surf, (window_x / 2 - 100, window_y / 2))

            text_surf = game_over_font.render('Press r to restart or escape to exit!', False, (255, 255, 255))
            background.blit(text_surf, (window_x / 2 - 150, window_y / 2 + 50))

            text_surf = game_over_font.render('Your score was ' + str(self.score), False, (255, 255, 255))
            background.blit(text_surf, (window_x / 2 - 150, window_y / 2 + 75))

            self.window.blit(background, (0, 0))
            pygame.display.update()
            self.FPS_clock.tick(self.settings['FPS'])

    def game_over_screen(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close_program()

                # Key bindings
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.start_game()
                    if event.key == pygame.K_ESCAPE:
                        self.close_program()

            window_size = self.settings['window_size']
            window_x = window_size[0]
            window_y = window_size[1]
            background = pygame.Surface(window_size)
            background.fill((0, 0, 0))
            game_over_font = pygame.font.SysFont(self.settings['game_font'], size=30)

            text_surf = game_over_font.render('Game over!', False, (255, 255, 255))
            background.blit(text_surf, (window_x / 2 - 100, window_y / 2))

            text_surf = game_over_font.render('Press r to restart or escape to exit!', False, (255, 255, 255))
            background.blit(text_surf, (window_x / 2 - 150, window_y / 2 + 50))

            text_surf = game_over_font.render('Your score was ' + str(self.score), False, (255, 255, 255))
            background.blit(text_surf, (window_x / 2 - 150, window_y / 2 + 75))

            self.window.blit(background, (0, 0))
            pygame.display.update()
            self.FPS_clock.tick(self.settings['FPS'])

    def close_program(self):
        pygame.quit()
        sys.exit()

    def reset_screen(self):
        self.window.fill((0, 0, 0))
        self.Camera.move()
        background = self.Camera.active_tiles()
        for tile in background:
            # Need to turn game coordinates into screen coordinates relative to the player
            screen_coord = self.convert_to_screen_coordinates((tile[0][0], tile[0][1]))
            self.window.blit(tile[1], screen_coord)

    def create_entities(self):
        entities = []
        for i in range(self.settings['number_of_enemies']):
            x = random.randint(0, self.settings['map_size'][0])
            y = random.randint(0, self.settings['map_size'][1])
            angle = random.randint(0, 359)
            aircraft = random.choice(['Mig21', 'Mig35'])
            if aircraft == 'Mig21':
                entities.append(Entities.Mig21((x, y, angle), self.settings['map_size']))
            elif aircraft == 'Mig35':
                entities.append(Entities.Mig35((x, y, angle), self.settings['map_size']))
        return entities

    def convert_to_screen_coordinates(self, coord):
        # takes game coordinates and converts it to screen (pixel) coordinates for blitting
        screen_x = coord[0] - self.Camera.rect[0]
        screen_y = coord[1] - self.Camera.rect[1]
        return screen_x, screen_y

    def debug_window(self, content):
        box_size = (200, 100)
        debug_box = pygame.Surface(box_size, flags=pygame.SRCALPHA)
        debug_box.fill((255, 255, 255, 150))
        debug_font = pygame.font.SysFont(self.settings['game_font'], size=18)
        text_surf = debug_font.render(content, False, (0, 0, 0))
        debug_box.blit(text_surf, (10, 10))
        self.window.blit(debug_box, (self.settings['window_size'][0] - box_size[0],
                                     self.settings['window_size'][1] - box_size[1]))

    def score_overlay(self):
        score_bar = pygame.Surface((self.settings['window_size'][0], 25))
        score_bar.fill((255, 255, 255))
        score_font = pygame.font.SysFont(self.settings['game_font'], size=18)
        score_text = score_font.render('Current score: ' + str(self.score), False, (0, 0, 0))
        score_bar.blit(score_text, (10, 2))
        self.window.blit(score_bar, (0, 0))

def main():
    settings = {'FPS': 30,
                'window_size': (1200, 600),
                'window_position': (50, 50),
                'map_size': (6500, 4000),
                'player_start': (100, 100),
                'debug_mode': False,
                'enemy_behaviour_time': 1.5,
                'number_of_enemies': 50,
                'game_font': 'Arial',
                'invulnerable': False}
    game = GameEngine(settings)


if __name__ == '__main__':
    main()