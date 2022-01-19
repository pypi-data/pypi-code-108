import pygame
import os
import sys


if __name__ == '__main__' or os.path.normpath(sys.argv[0] + os.sep + os.pardir) == os.path.normpath(__file__ + os.sep + os.pardir):
    from help_functions import iround
else:
    from .help_functions import iround

pygame.init()


class Slider():
    def __init__(self, x, y, width, height,   bg_color=(150, 150, 150), slider_color=(30, 130, 255), value_range=[0, 1],
                 start_value=1.2, scale_distance=0, only_values_scale=False, value_display=False, font_name="comicsans",
                 scale_number_show=False, slide_mouse_button_index=0, label = None, label_abstand_x = None, 
                 label_color = (255, 255, 255), label_x = None):

        self.max_value = value_range[-1]
        self.min_value = value_range[0]
        self.value_range = value_range


        if start_value > self.max_value or scale_distance > self.max_value or self.min_value >= self.max_value:
            raise ValueError

        
        rel_silder_width = 0.06
        rel_silder_height = 0.7


        rel_height = height * rel_silder_height

        font_size = iround((rel_height))
        self.font = pygame.font.SysFont(font_name, font_size)

        self.label = label

        if self.label:

            

            if not label_abstand_x:
                self.label_abstand_x = width * 0.1
            else:
                self.label_abstand_x = label_abstand_x


            self.label_color = label_color
            self.label_x = label_x

            self.t_label = self.font.render(self.label, True, self.label_color)
            font_width = self.t_label.get_width()
            font_height = self.t_label.get_height()

            self.label_y = y + (height - font_height)//2

            if self.label_x:
                x = self.label_x + self.label_abstand_x + font_width
            else:
                self.label_x = x - font_width - self.label_abstand_x


        if not start_value <= self.max_value or not start_value >= self.min_value:
            start_value = round(
                (self.max_value - self.min_value)/2 + self.min_value, 2)

        self.rect = pygame.Rect(x, y, width, height)


        self.slider_rect = pygame.Rect(
            x, y + height * (1-rel_silder_height)//2, int(round(width * rel_silder_width)), int(round(height * rel_silder_height)))

        abstand_x = (self.slider_rect.width)//2
        abstand_y = (height - self.slider_rect.height)//2

        self.base_line_rect = pygame.Rect(
            x + abstand_x, y + abstand_y, width - 2 * abstand_x, height - 2 * abstand_y)

        self.bg_color = bg_color
        self.slider_color = slider_color
        self.slider_thickness = int(round(height/20))

        # aktueller wert wird als start wert festgelegt
        self.current_value = start_value
        self.scale_distance = scale_distance
        self.only_values_scale = only_values_scale
        self.hold = False
        self.value_display = value_display
        self.scale_number_show = scale_number_show
        self.value_changed = False
        self.slide_mouse_button_index = slide_mouse_button_index

        if scale_distance:
            x = self.min_value
            self.intervall_dict = {}
            while x < self.max_value:
                self.intervall_dict[x] = round(self.base_line_rect.x + (
                    (x - self.min_value)/(self.max_value-self.min_value)) * self.base_line_rect.width, 2)
                x += scale_distance
            self.intervall_dict[self.max_value] = self.base_line_rect.right

            if start_value not in self.intervall_dict.keys():
                print(start_value, self.intervall_dict.keys())
                raise ValueError

        if self.scale_number_show:
            font_size = iround(self.base_line_rect.height/3.5)
            self.scale_font = pygame.font.SysFont(font_name, font_size)

        


        
            

        self.position_slider()

    def position_slider(self):
        """sets slider to current_value which is calculated in calc_current_value and set in the init funciton
        """
        rel_pos = (self.current_value - self.min_value) / \
            (self.max_value-self.min_value)
        self.slider_rect.x = self.base_line_rect.x + \
            self.base_line_rect.width * rel_pos - self.slider_rect.width//2

    def draw(self, win):
        pygame.draw.line(win, self.bg_color, (self.base_line_rect.midleft),
                         (self.base_line_rect.midright), self.slider_thickness)

        # if scale lines are also drawn
        if self.scale_distance:
            half_lenght = int(self.base_line_rect.height//15)
            mid_y = self.base_line_rect.center[1]

            for value, x in self.intervall_dict.items():
                pygame.draw.line(win, self.bg_color, (x, mid_y - half_lenght),
                                 (x, mid_y + half_lenght), int(self.slider_thickness//1.7))

                if self.scale_number_show:
                    t_scale = self.scale_font.render(
                        str(value), True, (255, 255, 255))
                    text_width = t_scale.get_width()
                    win.blit(t_scale, (x - text_width //
                                       2, mid_y + half_lenght * 3))

        pygame.draw.rect(win, self.slider_color, self.slider_rect, 0, 10)

        # draws currently selescted value on the right if slider
        if self.value_display:
            t_value = self.font.render(
                str(self.current_value), True, (255, 255, 255))
            text_height = t_value.get_height()
            win.blit(t_value, (self.base_line_rect.right + self.base_line_rect.width * 0.1,
                               self.base_line_rect.y + (self.base_line_rect.height - text_height)//2))

        if self.label:
            win.blit(self.t_label, (self.label_x, self.label_y))
            

    def calc_current_value(self):
        """calculates the value of the slider based on the position onscreen
        """

        rel_slider_x = self.slider_rect.center[0] - self.base_line_rect.x

        # if only certain inveralls are allowed
        if self.only_values_scale:

            min_distance = [-1, float("inf")]
            for key, value in self.intervall_dict.items():
                if abs(value-self.slider_rect.center[0]) < min_distance[1]:
                    min_distance = [key, abs(value-self.slider_rect.center[0])]

            # f = [abs(value-self.slider_rect.center[0])
            #      for value in self.intervall_dict.values()]

            self.current_value = round(min_distance[0], 2)
        else:
            rel_max_x = self.base_line_rect.width
            rel_pos = rel_slider_x/rel_max_x
            self.current_value = round(
                rel_pos * (self.max_value - self.min_value) + self.min_value, 2)

    def set_current_value(self, value):
        if round(value, 2) in self.intervall_dict.keys():
            self.current_value = value
            self.slider_rect.center = (self.intervall_dict[value], self.slider_rect.center[1])

        else:
            raise ValueError

    def update(self):

        button_pressed = pygame.mouse.get_pressed()[
            self.slide_mouse_button_index]

        mouse = pygame.mouse.get_pos()

        if button_pressed:
            if self.slider_rect.collidepoint(mouse):
                self.hold = True
        else:
            self.hold = False

        # if mousebutton is pressed and was initially pressed on slider
        vorher = self.current_value

        if self.hold:

            if mouse[0] < self.base_line_rect.x:
                self.slider_rect.x = self.base_line_rect.x - self.slider_rect.width//2
            elif mouse[0] > self.base_line_rect.x + self.base_line_rect.width:
                self.slider_rect.x = self.base_line_rect.x + \
                    self.base_line_rect.width - self.slider_rect.width // 2
            else:
                self.slider_rect.x = mouse[0] - self.slider_rect.width//2

            value_before = self.current_value
            self.calc_current_value()
            self.delta_value = self.current_value - value_before

            if self.only_values_scale:
                self.position_slider()

        nachher = self.current_value

        if vorher != nachher:
            self.value_changed = True
        else:
            self.value_changed = False


if __name__ == '__main__':

    FPS = 60

    #####
    s = Slider(100, 100, 300, 70, value_display=True,
               value_range=(1, 2), scale_distance=0.2, only_values_scale=True)
    #####

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
    directory_of_file = os.path.normpath(sys.argv[0] + os.sep + os.pardir)

    CLOCK = pygame.time.Clock()

    def draw():
        WIN.fill((0, 0, 0))

        #####
        s.draw(WIN)
        #####

    def main():
        run = True

        while run:

            #####
            mouse_pressed = False
            mouse_released = False
            #####

            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            ######
            s.update()
            ######

            draw()

            pygame.display.update()

    main()
    pygame.quit()
