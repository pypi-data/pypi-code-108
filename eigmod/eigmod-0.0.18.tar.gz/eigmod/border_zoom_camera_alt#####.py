from .constants import HW,HH, SCRWIDTH, SCRHEIGHT

import pygame
vec = pygame.math.Vector2

class Camera:
    def __init__(self, borders):
        self.offset = vec(0,0)
        self.zoom_offset = vec(0,0)
        self.scale = 1
        self.leftb, self.topb, self.rightb, self.bottemb = borders

    def scroll(self, pl):
        self.player = vec(pl["x"], pl["y"]) 
 
        self.offset.x += int(self.player.x - self.offset.x - HW)
        self.offset.y += int(self.player.y - self.offset.y - HH)

        zoom_ausgeleichx = (HW * (1/self.scale)) - HW
        zoom_ausgeleichy = (HH * (1/self.scale)) - HH

        self.offset.x = max(self.offset.x, self.leftb + zoom_ausgeleichx) 
        self.offset.x = min(self.offset.x, self.rightb - SCRWIDTH - zoom_ausgeleichx)
        self.offset.y = max(self.offset.y, self.topb + zoom_ausgeleichy)
        self.offset.y = min(self.offset.y, self.bottemb - SCRHEIGHT - zoom_ausgeleichy)


    def world_to_screen(self, wx, wy):
        sx = wx - self.offset.x
        sy = wy - self.offset.y
        return sx, sy

    def screen_to_world(self, sx, sy):
        wx = (sx) + self.offset.x 
        wy = (sy) + self.offset.y 
        return wx, wy
    
    def get_zoom_lange(self, lange):
        return lange * self.scale

    def get_zoom_borders(self):
        # berechner neuen border der welt mit kamera zoom eingerechner (stoßen an anderen koordinaten an je nach zoom)
        zoom_border_cords = HW * (1/self.scale),  self.rightb - HW * (1/self.scale), HH * (1/self.scale), self.bottemb - HH * (1/self.scale)
        return zoom_border_cords

    def get_draw_cords(self, x, y, *langen):

            # für bezugspunkt angepasste borders im fall das figur an wand und kamera sttationär ist 
        # dann soll der stattionäre punkt der bezugspunkte sein 
        zoomb_left, zoomb_right, zoomb_top, zoomb_bottem = self.get_zoom_borders()

        # als standart werte erstmal spieler position
        zoom_bezug_x, zoom_bezug_y = self.player.x, self.player.y
        zoom_bezug_x = max(zoom_bezug_x, zoomb_left)
        zoom_bezug_x = min(zoom_bezug_x, zoomb_right)
        zoom_bezug_y = max(zoom_bezug_y, zoomb_top)
        zoom_bezug_y = min(zoom_bezug_y, zoomb_bottem)

        # Differenz objekt positon und bezugpunkt
        dx, dy =  x - zoom_bezug_x,  y - zoom_bezug_y
        # zoomkonstante nur auf differenz der zwischen pnkt und bezugspunkt und nicht absolte werte angewand
        dx *= self.scale
        dy *= self.scale
        draw_x = dx + zoom_bezug_x
        draw_y = dy + zoom_bezug_y

        draw_x, draw_y = self.world_to_screen(draw_x, draw_y)

        zoom_langen = []
        for lange in langen:
            zoom_langen.append(int(self.get_zoom_lange(lange)))

        if zoom_langen:
            return int(draw_x), int(draw_y), zoom_langen
        else:
            return int(draw_x), int(draw_y)
            
      
    def zoom(self, delta):

        mid_davor = vec(self.world_to_screen(self.player.x, self.player.y))

        self.scale *= delta

        player_screen =  vec(self.world_to_screen(self.player.x, self.player.y))
        

        # if HW - player_screen.x < 10:
        #     self.zoom_offset.x -= (HW - player_screen.x) 
        #     self.zoom_offset.y -= (HH - player_screen.y) 
        # else:
        #     print("self.zoom_offset nicht verandert")

