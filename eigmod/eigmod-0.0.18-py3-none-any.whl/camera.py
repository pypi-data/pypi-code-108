
import pygame
vec = pygame.math.Vector2


class Camera:
    def __init__(self, borders, SCRWIDTH, SCRHEIGHT):
        self.SCRWIDTH, self.SCRHEIGHT = SCRWIDTH, SCRHEIGHT
        self.HW, self.HH = self.SCRWIDTH//2, self.SCRHEIGHT//2
        self.offset = vec(0, 0)
        self.scale = 1
        self.leftb, self.topb, self.rightb, self.bottemb = borders
        self.veranderungs_schwelle = 0

    def scroll(self, pl):
        """with new_player cords given it updates to offset 

        Args:   
            pl (obj.x, obj.y): player_x, player_y
        """

        self.player = vec(pl.x, pl.y)

        # als basis dient die world Koordinate des Players, da der offset immer von oben links ausgeht wird die halbe screenbreite
        # mal 1/scale (relative screenbreite) abgezogen
        self.offset.x = self.player.x - (1/self.scale) * self.HW

        # wenn linke border (0) groser ist als der offset (lniks oben gemessen) ist, so ist die border (0) oder neue offset
        self.offset.x = max(self.offset.x, self.leftb)

        # selbes spiel nur muss von der rechten border noch die relative screenbreite abgezogen werden, damit sie auf der hohe des
        # offsets ist (auf der linken seite des fensters)
        self.offset.x = min(self.offset.x, self.rightb -
                            self.SCRWIDTH * (1/self.scale))

        self.offset.y = self.player.y - (1/self.scale) * self.HH
        self.offset.y = max(self.offset.y, self.topb)
        self.offset.y = min(self.offset.y, self.bottemb -
                            self.SCRHEIGHT * (1/self.scale))

    def world_to_screen(self, wx, wy):
        """converts world cords to relative screen cords you can actually draw

        Args:
            wx (numb): world_x
            wy (numb): world y

        Returns:
            tuple: (screen_x, screen_y)
        """
        sx = (wx - self.offset.x) * self.scale
        sy = (wy - self.offset.y) * self.scale
        return sx, sy

    def screen_to_world(self, sx, sy):
        """converts relative screen cords to global ones
        example mouse cords to global

        Args:
            sx (numb): screen_x
            sy (numb): screen y

        Returns:
            tuple: (world_x, world_y)
        """
        wx = (sx/self.scale) + self.offset.x
        wy = (sy/self.scale) + self.offset.y
        return wx, wy

    def get_zoom_lange(self, lange):
        """returns length of obj when scale is applied

        Args:
            lange (numb): lange

        Returns:
            numb: new_lange
        """
        return lange * self.scale

    def get_view_dims_world(self):
        """returns relative screen dimentions with scale applied

        Returns:
            tuple: (length, height)
        """
        sicht_x = self.SCRWIDTH * (1/self.scale)
        sicht_y = self.SCRHEIGHT * (1/self.scale)
        return sicht_x, sicht_y

    def get_draw_cords(self, x, y, *langen):
        """retruns cords to draw on the screen
        (basically only converts world to screen Cords)

        Args:
            x (numb): world_x
            y (numb): world_y
            langen (numb, numb...) : langen to covert 

        Returns:
            int, int: draw_x, draw_y
            opitonal langen
        """

        draw_x, draw_y = self.world_to_screen(x, y)

        zoom_langen = []
        for lange in langen:
            zoom_langen.append(int(self.get_zoom_lange(lange)))

        if zoom_langen:
            return int(draw_x), int(draw_y), zoom_langen
        else:
            return int(draw_x), int(draw_y)
