
import pygame
import os
import sys


if __name__ == '__main__' or os.path.normpath(sys.argv[0] + os.sep + os.pardir) == os.path.normpath(__file__ + os.sep + os.pardir):
    from help_functions import get_font_size
else:
    from .help_functions import get_font_size


class CheckBox():
    def __init__(self, x, y, text=None, given_height=None, color=(255, 255, 255), font_name="comicsans",
                 given_font_size=40, relative_box_size=0.7, border_thickness=None, is_checked=False, draw_mouse_hover=False,
                 fps=None, tick_color=(30, 130, 255), check_mouse_button_index=0):

        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font_name = font_name
        self.given_font_size = given_font_size
        self.relative_box_size = relative_box_size

        self.draw_mouse_hover = draw_mouse_hover

        self.is_checked = is_checked
        self.fps = fps
        self.tick_color = tick_color
        self.given_height = given_height

        self.click_counter = 0
        self.check_mouse_button_index = check_mouse_button_index

        self.set_up()

        if border_thickness:
            self.standart_border_thickness = border_thickness
            self.border_thickness = border_thickness
        else:
            self.standart_border_thickness = int(
                round(self.box_rect.width * 0.1, 0))
            self.border_thickness = self.standart_border_thickness

        self.box_rect.x -= self.border_thickness//2
        self.box_rect.y -= self.border_thickness//2

        self.haken_rect = pygame.Rect(100, 100, 300, 300)

    def set_up(self):

        if self.given_height:
            font_size = get_font_size(self.font_name, self.given_height)
        else:
            font_size = self.given_font_size

        self.font = pygame.font.SysFont(self.font_name, font_size)
        self.t_text = self.font.render(self.text, True, (255, 255, 255))
        self.text_width = self.t_text.get_width()
        self.text_height = self.t_text.get_height()

        self.box_lenght = self.text_height * self.relative_box_size
        self.abstand = (self.text_height * (1 - self.relative_box_size))/2

        self.box_rect = pygame.Rect(
            self.x,  self.y + self.abstand*0.75, self.box_lenght, self.box_lenght)

    def haken_draw(self, win):
        rect = self.box_rect
        # pygame.draw.rect(win, self.tick_color, rect, 5)

        x = [1.05, 0.4, 0.15]
        y = [0, 0.7, 0.45]
        x = [i*rect.width + rect.x for i in x]
        y = [i*rect.height + rect.y for i in y]

        for i in range(2):
            pygame.draw.line(win, self.tick_color,
                             (x[i], y[i]), (x[i+1], y[i+1]), int(self.border_thickness*2))

    def draw(self, win):

        if self.draw_mouse_hover and self.mouse_hover:
            thickness = int(round(self.border_thickness * 1.7, 0))
            pygame.draw.rect(win, self.color, (self.box_rect.x, self.box_rect.y,
                                               self.box_rect.width, self.box_rect.height), thickness)
        else:
            pygame.draw.rect(win, self.color, self.box_rect,
                             self.border_thickness)

        win.blit(self.t_text, (self.x + self.box_lenght + self.abstand * 2, self.y))

        if self.is_checked:
            self.haken_draw(win)

            # pygame.draw.rect(win, (255, 0, 0), self.box_rect)

        # pygame.draw.rect(win, (255,0,0), (self.x, self.y, self.text_width+ + self.box_lenght + 4 * self.abstand, self.text_height), self.border_thickness)

    def update(self):
        self.changed = False

        mouse = pygame.mouse.get_pos()

        button_pressed = pygame.mouse.get_pressed()[
            self.check_mouse_button_index]

        if self.click_counter > 0:
            self.click_counter -= 1

        if self.box_rect.collidepoint(mouse):
            if button_pressed and self.click_counter == 0:
                self.is_checked = not self.is_checked
                self.changed = True
                if self.fps:
                    self.click_counter = int(self.fps/5)
                else:
                    self.click_counter = 10
            self.mouse_hover = True
        else:
            self.mouse_hover = False


if __name__ == '__main__':

    FPS = 60

    c = CheckBox(100, 100, text="Beispiel", fps=FPS,
                 draw_mouse_hover=True, given_height=50)

    SCRWIDTH = 600
    SCRHEIGHT = 600

    HW = SCRWIDTH // 2
    HH = SCRHEIGHT // 2

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (100, 100, 100)
    RED = (255, 30, 30)
    GREEN = (30, 255, 30)
    BLUE = (30, 30, 255)

    WIN = pygame.display.set_mode((SCRWIDTH, SCRHEIGHT))
    pygame.display.set_caption("Space Game")

    CLOCK = pygame.time.Clock()

    def draw():
        WIN.fill((0, 0, 0))
        c.draw(WIN)

    def main():
        run = True

        while run:
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            c.update()

            draw()

            pygame.display.update()

    main()
    pygame.quit()
