import eigmod.collisionen
import sys
import os
import eigmod
import pygame
import random
vec = pygame.math.Vector2


class Buttons:

    def __init__(self, win, scrwidth, scrheight, index, anzahl, inhalt, abstand=40,
                 width=200, height=70, gesamt_verschiebung_y=0, gesamt_verschiebung_x=0, font_name="comicsans", font_path=None,
                 color_normal=(90, 230, 90), color_active=(0, 0, 0), text_color=None, font_size=None, verschiebung_hintergrund=8,
                 buttons_vertical=True, with_draw_activation=True, button_aufbau_ist_mitte=True, start_x=None, start_y=None,
                 is_disabled=False, disabled_color_erhohung=40, nur_schrift=False, nur_umrandung=False,
                 umrandungs_dicke=0, font_size_height_rel=0.6, x=None, y=None):

        standard_normal = (90, 230, 90)
        standard_active = (0, 0, 0)

        # nessesary arguments
        self.win = win
        self.scrwidth = scrwidth
        self.scrheight = scrheight
        self.index = index
        self.anzahl = anzahl  # anzahl an buttons
        self.inhalt = inhalt  # text für den button

        # optinal
        self.abstand = abstand  # abstand zwischen den buttons
        self.width = width
        self.height = height

        # alle buttons werden um die zahl in y richtung verschoben
        self.gesamt_verschiebung_y = gesamt_verschiebung_y
        self.gesamt_verschiebung_x = gesamt_verschiebung_x  # x richtung

        if not font_size:
            self.font_size = int(self.height * font_size_height_rel)
        else:
            self.font_size = font_size

        if font_path:
            self.font = pygame.font.Font(font_path, self.font_size)
        else:
            self.font = pygame.font.SysFont(font_name,  self.font_size)

        # top (haupt) farbe wenn nicht auf button drauf
        self.color_normal = color_normal
        self.color_active = color_active  # farbe wenn auf button drauf sonst drunter
        # um wie viel der schatten hintergrund verschoben ist
        self.verschiebung_hintergrund = verschiebung_hintergrund
        # wenn true dann sind buttons vertikal aufgestellen, wenn false horizontal
        self.buttons_vertical = buttons_vertical
        # wenn true verandern buttons farbe wenn mousecurser drauf
        self.with_draw_activation = with_draw_activation
        # wenn true ist der aufbau in der mitte gecentert
        self.button_aufbau_ist_mitte = button_aufbau_ist_mitte
        # wenn nicht in der mitte gecentert dann ist dies start koordinate x
        self.start_x = start_x
        self.start_y = start_y  # start koordinate y

        # ob button am anfang diabled ist und wenn ja um wieviel die Farb werte gehoben werden um dies zu zeigen
        self.is_disabled = is_disabled
        self.disabled_color_erhohung = disabled_color_erhohung

        self.text_color = text_color  # frabe des gezeicheten textes

        if self.text_color and self.color_active == standard_active and self.color_normal == standard_normal:
            self.color_normal = self.color_active = self.text_color
        # wenn nicht bestimmt dann immer die bottem farbe (bei nicht aktivierung ist es active color)
        if not self.text_color:
            self.text_color = self.color_active

        # wenn aktiviert schrift ohne hintergrund is displayed
        self.nur_schrift = nur_schrift
        # wenn aktiviert nur rumrandung des rect als hintergrund
        self.nur_umrandung = nur_umrandung
        self.umrandungs_dicke = umrandungs_dicke
        if self.umrandungs_dicke:
            self.nur_umrandung = True
        # later
        self.text_cords = None  # koordinaten des textes

        # dynamic
        self.is_active = False  # ob mousecurser auf button
        self.is_actively_pressed = False

        if x != None and y != None:
            self.x = x
            self.y = y
        else:
            self.set_botton_position()

        self.set_text_position()

    def set_botton_position(self):
        """finds out position of button and sets its cords
        """

        if self.buttons_vertical:
            if self.button_aufbau_ist_mitte:
                x = int(self.scrwidth/2 - self.width /
                        2 + self.gesamt_verschiebung_x)

                gesamt = self.anzahl * self.height + \
                    (self.anzahl - 1) * self.abstand
                abstand_oben_unten = (self.scrheight - gesamt)/2
                y = int(abstand_oben_unten + self.index *
                        (self.height + self.abstand)) + self.gesamt_verschiebung_y
            else:
                # button haben start position
                x = self.start_x
                y = int(self.start_y + self.index *
                        (self.height + self.abstand))

        else:
            if self.button_aufbau_ist_mitte:
                y = int(self.scrheight/2 - self.height /
                        2 + self.gesamt_verschiebung_y)

                gesamt = self.anzahl * self.width + \
                    (self.anzahl - 1) * self.abstand
                abstand_rechts_links = (self.scrwidth - gesamt)/2
                x = int(abstand_rechts_links + self.index *
                        (self.width + self.abstand)) - self.gesamt_verschiebung_x
            else:
                # button haben start position
                y = self.start_y
                x = int(self.start_x + self.index *
                        (self.width + self.abstand))

        self.x, self.y = x, y

    def set_text_position(self):
        """sets the position at which the text will be drawn
        """

        text = self.font.render(self.inhalt, True, (0, 0, 0))
        mitte_x = int((self.x + self.width/2) - (text.get_width()/2))
        mitte_y = int((self.y + self.height/2) - (text.get_height()/2))

        self.text_cords = vec(mitte_x, mitte_y)

    def get_if_clicked(self, mouse=None, mouse_event = None):
        """checks of mouse is on button and if mouse presses

        Args:
            mouse (tuple): mouse position got by pygame.mouse.get_pos()
            mouse_event (bool): if mousebutton you want to monitor is pressed

        Returns:
            bool: if on button clicked
        """
        if not mouse or not mouse_event:
            mouse = pygame.mouse.get_pos()
            mouse_event = pygame.mouse.get_pressed()[0]
            
        hover = self.get_mouse_collision(mouse)

        if hover and mouse_event:
            return True
        return False

    def get_mouse_collision(self, maus, ignore_disabled=False):
        """returns if the mouse is on the button

        Args:
            maus (tuple): mouse position

        Returns:
            bool: if mouse on button
        """
        if not self.is_disabled or ignore_disabled:
            # wenn collision entweder mit dem square des buttons oder dessen schatten
            if eigmod.collisionen.point_square(maus, (self.x, self.y), (self.width, self.height))\
                    or eigmod.collisionen.point_square(maus, (self.x + self.verschiebung_hintergrund, self.y + self.verschiebung_hintergrund), (self.width, self.height)) and not self.nur_schrift:
                self.is_active = True
                return True
            else:
                self.is_active = False
                return False
        else:
            self.is_active = False
            return False

    def draw(self):
        """draws button with text and also considers the state so weather the mouse is on the button or not
        """

        top_color = self.color_normal
        bottem_color = self.color_active

        if self.is_active and self.with_draw_activation:
            top_color = self.color_active
            bottem_color = self.color_normal

        if self.text_color == top_color:
            self.text_color = bottem_color

        draw_text_color = self.text_color

        if self.is_disabled:
            # wenn disabled kommt helles overlay also alle farben nach oben

            top_color = color_erhohen(top_color, self.disabled_color_erhohung)
            bottem_color = color_erhohen(
                bottem_color, self.disabled_color_erhohung)
            draw_text_color = color_erhohen(
                draw_text_color, self.disabled_color_erhohung)

        if not self.nur_schrift:

            if self.verschiebung_hintergrund != 0:
                pygame.draw.rect(self.win, bottem_color,
                                 (self.x + self.verschiebung_hintergrund, self.y + self.verschiebung_hintergrund, self.width, self.height), self.umrandungs_dicke)

            pygame.draw.rect(self.win, top_color,
                             (self.x, self.y, self.width, self.height), self.umrandungs_dicke)

        text = self.font.render(self.inhalt, True, draw_text_color)
        self.win.blit(text, (self.text_cords.x, self.text_cords.y))


def color_erhohen(color, delta):
    """erhoht farbwerte wenn button disabled ist 

    Args:
        color (tuple): color
        delta (int): umwieviel erhoht werden muss

    Returns:
        tuple: new color
    """
    r, g, b = color
    new_color = (wert_max_255(r, delta), wert_max_255(
        g, delta), wert_max_255(b, delta))
    return new_color


def wert_max_255(x, delta):
    if x + delta <= 255:
        return x + delta
    else:
        return 255

################### chekc button activation ###################

# menübuttons = [["Continue"], ["Highscores"], ["Shop"],
#                    ["Credits"]]

# buttons = []
# for index, menübutton in enumerate(menübuttons):
#     buttons.append(Buttons(WIN, SCRWIDTH, SCRHEIGHT, index, len(
#         menübuttons), menübutton[0],  gesamt_verschiebung_y=-20))


# mouse_button_down = False
# for event in pygame.event.get():
#     if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#         mouse_button_down = True

# mouse = pygame.mouse.get_pos()
# for button in buttons:
#     pressed = button.get_if_clicked(mouse, mouse_button_down)
#     title = button.inhalt
#     if pressed:
#         if title == "Continue":
#             menu_run = False

if __name__ == '__main__':
    SCRWIDTH = 800
    SCRHEIGHT = 600

    HW = SCRWIDTH // 2
    HH = SCRHEIGHT // 2

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (100, 100, 100)
    RED = (255, 30, 30)
    GREEN = (30, 255, 30)
    BLUE = (30, 30, 255)

    FPS = 60

    pygame.init()
    WIN = pygame.display.set_mode((SCRWIDTH, SCRHEIGHT))
    pygame.display.set_caption("Space Game")
    directory_of_file = os.path.normpath(sys.argv[0] + os.sep + os.pardir)

    CLOCK = pygame.time.Clock()

    def draw():
        WIN.fill(RED)
        for button in buttons:
            button.draw()

    # menübuttons = ["<", ">", "fd", "hallo"]

    # buttons = []
    # for index, menübutton in enumerate(menübuttons):
    #     buttons.append(Buttons(WIN, SCRWIDTH, SCRHEIGHT, index, len(
    #         menübuttons), menübutton, buttons_vertical=False, width=70, height=70,
    #         nur_schrift=False,
    #         verschiebung_hintergrund=5))

    menübuttons = [["Continue"], ["Highscores"], ["Shop"],
                   ["Credits"]]

    buttons = []
    for index, menübutton in enumerate(menübuttons):
        buttons.append(Buttons(WIN, SCRWIDTH, SCRHEIGHT, index, len(
            menübuttons), menübutton[0],  gesamt_verschiebung_y=-20, font_size_height_rel=0.4))

    def main():
        run = True

        while run:
            mouse_button_down = False
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_button_down = True

            keys = pygame.key.get_pressed()

            mouse = pygame.mouse.get_pos()
            for button in buttons:
                pressed = button.get_if_clicked(mouse, mouse_button_down)
                title = button.inhalt

                if title == "Continue" and pressed:
                    print("con")

                # if pressed:
                #     button.is_disabled = not button.is_disabled

                # if random.randint(0, 100) == 0:
                #     button.is_disabled = False

            draw()

            pygame.display.update()

    main()
    pygame.quit()
