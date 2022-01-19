import pygame
import math
import re

if __name__ == '__main__':
    from draw_text_list import text_draw
else:
    from .draw_text_list import text_draw


class InputBox:
    def __init__(self,  x, y, width, height, input_color_active=(235, 235, 235), input_color_passive=(130, 130, 130),
                 standard_input_text="", input_max_len=None, mit_spacer=True, mit_zeilen_umbruch=False,
                 input_anfangs_active=False, umrandung="rect", input_max_len_automatic=False,
                 input_font_size=None, input_max_len_font_size=None, max_len_info_anzeigen=True,
                 anfangs_anzeige_text="", vergroserungs_richtung="beide", font_size_height_rel=0.75,
                 zeilen_abstand_rel=1, binde_seite="mitte", mit_user_next_line=False, input_max_len_rendered=None,
                 font_path=None, font_scale=1, custom_format=False, label = None, label_x = None, label_abstand_x = None):
        """umrandung: "rect", "line"
            vergroserungs_richtung: "beide", "oben", "unten"  
            binde_seite: "mitte", "rechts", "links"
        """

        self.width = width
        self.height = height
        self.anfangs_height = self.height
        self.anfangs_y = y + self.width/2
        self.anfangs_x = x + self.height/2
        self.input_color_active = input_color_active
        self.input_color_passive = input_color_passive
        self.input_color = self.input_color_passive

        self.input_max_len = input_max_len
        self.mit_spacer = mit_spacer
        self.mit_zeilen_umbruch = mit_zeilen_umbruch
        self.input_active = input_anfangs_active
        self.umrandung = umrandung
        self.max_len_info_anzeigen = max_len_info_anzeigen
        self.vergroserungs_richtung = vergroserungs_richtung
        self.font_size_height_rel = font_size_height_rel
        self.zeilen_abstand_rel = zeilen_abstand_rel
        self.binde_seite = binde_seite
        self.mit_user_next_line = mit_user_next_line
        self.input_max_len_rendered = input_max_len_rendered
        self.font_path = font_path
        self.font_scale = font_scale
        self.custom_format = custom_format

        self.label = label
        input_rect_x = x
        if label:
            self.label_x = label_x
            input_rect_x = label_x + label_abstand_x
            self.label_y = y

        self.input_rect = pygame.Rect(
            input_rect_x, y, self.width, self.height)

        self.input_spacer_counter = 0
        self.backspace_counter = 0

        self.backspace_active = False
        self.backspace_active_counter = 0
        self.backspace_fast = False
        self.backspace_interval_anfang = 7
        self.backspace_interval = self.backspace_interval_anfang
        self.backspace_interval_fast = 2

        self.input_text_ist_max_len = False
        self.zeilen_umbruch_rel = 0.9

        self.input_font_size = input_font_size
        self.input_max_len_font_size = input_max_len_font_size

        self.schonmal_gezeichnet = False

        self.set_input_font_sizes()

        self.input_max_len_automatic = input_max_len_automatic

        self.anfangs_anzeige_text_list = self.get_str_or_list(
            anfangs_anzeige_text)
        self.input_text_list = self.get_str_or_list(standard_input_text)

        if self.anfangs_anzeige_text_list != [""]:
            self.input_text_list = self.anfangs_anzeige_text_list

        self.input_text_index = len(self.input_text_list) - 1

        for _ in range(1, len(self.input_text_list)):
            self.rect_verschiebung_add_zeile()

    def get_str_or_list(self, obj):
        if type(obj) == str:
            new_obj = [obj]
        else:
            new_obj = obj

        return new_obj

    def get_input_text(self):
        return self.input_text_list

    def get_input_text_gesamt_len(self):
        """returns lenght of whole text

        Returns:
            int: text len
        """

        lange = 0
        for zeile in self.input_text_list:
            lange += len(zeile)

        return lange

    def set_input_font_sizes(self):
        """sets font sizes depending on prefrence (input_font_size, input_max_len_font_size) or
        sets it to be 80 percent of height
        """

        if self.font_path:
            font_name = self.font_path

            if self.input_font_size:
                self.input_font = pygame.font.Font(
                    font_name, self.input_font_size)
            else:
                input_font_height = int(
                    self.height * self.font_size_height_rel)
                self.input_font = pygame.font.Font(
                    font_name, input_font_height)

            if self.input_max_len_font_size:
                self.input_max_len_font = pygame.font.Font(
                    font_name, self.input_max_len_font_size)
            else:
                input_max_font_height = int(
                    input_font_height * self.font_size_height_rel)
                self.input_max_len_font = pygame.font.Font(
                    font_name, input_max_font_height)
        else:
            font_name = "comicsans"

            if self.input_font_size:
                self.input_font = pygame.font.SysFont(
                    font_name, self.input_font_size)
            else:
                input_font_height = int(
                    self.height * self.font_size_height_rel)
                self.input_font = pygame.font.SysFont(
                    font_name, input_font_height)

            if self.input_max_len_font_size:
                self.input_max_len_font = pygame.font.SysFont(
                    font_name, self.input_max_len_font_size)
            else:
                input_max_font_height = int(
                    input_font_height * self.font_size_height_rel)
                self.input_max_len_font = pygame.font.SysFont(
                    font_name, input_max_font_height)

        self.input_font_test_width, self.input_font_test_height = self.input_font.size(
            "A")

    def remove_one_character(self):
        """is called when backspace is pressed and removes one character or eliminates empty line
        """

        if len(self.input_text_list[self.input_text_index]) == 0 and self.input_text_index != 0:
            # line is removed
            self.input_text_list.pop(self.input_text_index)
            self.rect_verschiebung_remove_zeile()
            self.input_text_index -= 1
            self.backspace_counter = 0
        else:
            # single character is removed
            self.input_text_list[self.input_text_index] = self.input_text_list[self.input_text_index][:-1]
            self.backspace_counter = 0
        self.backspace_active_counter += 1

    def update(self):
        """ removes character/empty line when backspace is continuesly pressed
            adds new line (if possible) if current text runs over its boundaries
        """

        self.backspace_counter += 1

        if self.mit_spacer:
            self.input_spacer_counter += 1

        # if backspace button is still pressed and counter is over the maximum interval one character is removed and
        # after some time the backspace interval is reduced
        if self.backspace_active and self.backspace_counter >= self.backspace_interval:
            self.remove_one_character()

            if self.backspace_active_counter > 3:
                self.backspace_interval = self.backspace_interval_fast
            else:
                self.backspace_interval = self.backspace_interval_anfang

        # if mit_zeilen_umbruch is on and the line is larger than it's bounardies new line might be created
        # rect and text position is changed in order to fit with the added line
        if self.mit_zeilen_umbruch and self.schonmal_gezeichnet:
            self.t_problem_zeile = self.input_font.render(
                self.input_text_list[self.input_text_index], True, (self.input_color_active))
            if self.t_problem_zeile.get_width() > self.width * self.zeilen_umbruch_rel:

                # problem_index festgelegt und in aktuellen index des textes erhoht
                problem_index = self.input_text_index
                self.input_text_index += 1

                while self.t_problem_zeile.get_width() > self.width * self.zeilen_umbruch_rel:

                    # wenn es in zeile getrennte worter gibt dann wird gesamtes wort als letzter character geonommen
                    if len(self.input_text_list[problem_index].split(" ")) > 1:
                        last_characters = self.input_text_list[problem_index].split(
                            " ")[-1]
                        split_index = len(
                            self.input_text_list[problem_index]) - 1 - len(last_characters)
                    else:
                        last_characters = self.input_text_list[problem_index][-1]
                        split_index = -1

                    # alte (problem) zeile wird um last characters verkürzt
                    self.input_text_list[problem_index] = self.input_text_list[problem_index][:split_index]
                    problem_zeile = self.input_text_list[problem_index]

                    # wenn eine weitere zeile existiert (sollte eigentlich nicht) wird dahin zugefugt sonst wird neue zeile erschaffen
                    if len(self.input_text_list) - 1 == problem_index:
                        self.input_text_list.append(last_characters)
                    else:
                        self.input_text_list[self.input_text_index] = last_characters + \
                            self.input_text_list[self.input_text_index]

                    self.t_problem_zeile = self.input_font.render(
                        problem_zeile, True, (self.input_color_active))

                self.rect_verschiebung_add_zeile()

    def set_input_text_value(self, value):
        self.input_text_list = [value]

    def rect_verschiebung_add_zeile(self):
        """changes rect position because of new line
        """
        height_faktor = self.zeilen_abstand_rel

        # anpassungen fur die erweiterungsrichtungen
        if self.vergroserungs_richtung == "beide":
            y_faktor = 1 * height_faktor
        elif self.vergroserungs_richtung == "oben":
            y_faktor = 2 * height_faktor
        elif self.vergroserungs_richtung == "unten":
            y_faktor = 0

        self.input_rect.y -= (self.anfangs_height * y_faktor)/2
        self.input_rect.height += self.anfangs_height * height_faktor

    def rect_verschiebung_remove_zeile(self):
        """changes rect position because of removed line
        """
        height_faktor = self.zeilen_abstand_rel

        if self.vergroserungs_richtung == "beide":
            y_faktor = 1 * height_faktor
        elif self.vergroserungs_richtung == "oben":
            y_faktor = 2 * height_faktor
        elif self.vergroserungs_richtung == "unten":
            y_faktor = 0

        self.input_rect.y += (self.anfangs_height * y_faktor)/2
        self.input_rect.height -= self.anfangs_height * height_faktor

    def reset_box(self):

        for _ in range(1, len(self.input_text_list)):
            self.rect_verschiebung_remove_zeile()

        self.input_text_list = [""]
        self.input_text_index = 0

    def event_check(self, event):
        """reacts to all keypresses and if possible adds it to line/new line 
            removes when backspace 
            creates new line when enter

            also reaction on activation of field by mouse event

        Args:
            event ([type]): [description]
        """

        

        # activation of field based on mouse activity
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # fokus nun auf feld
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.input_color = self.input_color_active

                # wenn in aktueller input_text_list items existieren dann zu letztem item sonst immer zu 0
                if len(self.input_text_list) == 0 or self.input_text_list == self.anfangs_anzeige_text_list:
                    self.input_text_index = 0
                else:
                    self.input_text_index = len(self.input_text_list) - 1

                # wenn erst anfangs_anzeige text in feld stand dann verschwindet dieser auf fokus und feld passt sich an
                if self.anfangs_anzeige_text_list and self.input_text_list == self.anfangs_anzeige_text_list:
                    for _ in range(1, len(self.input_text_list)):
                        self.rect_verschiebung_remove_zeile()
                    self.input_text_list = [""]

            # woanders hin geklickt (fokus nicht auf feld)
            else:
                self.input_active = False
                self.input_color = self.input_color_passive
                # wenn es anfangs anzeige text gibt und das feld leer ist so wird wieder dieser text angezeigt wenn es fokus verliert
                if self.anfangs_anzeige_text_list and self.input_text_list == [""]:
                    self.input_text_list = self.anfangs_anzeige_text_list
                    self.index = len(self.input_text_list) - 1
                    for _ in range(1, len(self.input_text_list)):
                        self.rect_verschiebung_add_zeile()

        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_BACKSPACE:
                    # if not self.backspace_active the event is registert for the first time in a row so removes character immediately
                    if not self.backspace_active:
                        self.remove_one_character()
                        self.backspace_counter = 0

                    self.backspace_active = True

                elif event.key == pygame.K_RETURN:
                    if self.mit_user_next_line:
                        if not self.input_text_ist_max_len:
                            self.input_text_list.append("")
                            self.input_text_index += 1
                            self.rect_verschiebung_add_zeile()

                elif event.key == pygame.K_ESCAPE:
                    self.reset_box()

                # if normal character is pressed
                else:
                    add_character = True
                    # character isn't added to text under following conditions

                    # 1. max input lenght is determined automatically and adding a large character would be over the bounaries
                    if self.input_max_len_automatic and not self.input_max_len:
                        if self.t_current_row.get_width() + self.input_font_test_width > self.width * self.zeilen_umbruch_rel:
                            add_character = False

                    # 2. the initially given character limit is reached
                    if self.input_max_len_rendered:
                        text_width = self.input_font.render(
                            self.input_text_list[self.input_text_index], True, (0, 0, 0)).get_width()
                        if text_width + self.input_font_test_width > self.input_max_len_rendered:
                            add_character = False

                    if self.input_max_len:
                        if self.get_input_text_gesamt_len() > self.input_max_len:
                            add_character = False

                    if not add_character:
                        # if no character is added something went wrong and so the input_text must be at it's maximum
                        self.input_text_ist_max_len = True

                    # 3. sting has diffent format than wished for
                    if self.custom_format == "ip":
                        character = event.unicode

                        number_list = self.input_text_list[0].split(".")
                        last_number_block = number_list[-1]

                        # wenn zusatzliches zeichen keine zahl oder punkt ist
                        pattern =  re.compile("\d|\.")
                        if pattern.match(character) is None:
                            add_character = False

                        # wenn schon drei ziffern und darauf kein punkt folgt
                        if len(last_number_block) >= 3:
                            if character != ".":
                                add_character = False

                        # wenn zweiter punkt hinter anderen soll oder schon 3 punkte verwendet werden
                        if self.input_text_list[0].count(".") >= 3 or len(last_number_block) == 0:
                            if character == ".":
                                add_character = False

                    if add_character:
                        self.input_text_ist_max_len = False
                        self.input_text_list[self.input_text_index] += event.unicode
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.backspace_active = False
                self.backspace_active_counter = 0
        

    def draw(self, win):

        self.schonmal_gezeichnet = True

        if self.umrandung == "rect":
            pygame.draw.rect(win, self.input_color, self.input_rect, 2)
        elif self.umrandung == "line":
            pygame.draw.line(win, self.input_color, (self.input_rect.x, self.input_rect.y + self.input_rect.height),
                             (self.input_rect.x + self.width, self.input_rect.y + self.input_rect.height))

        color = self.input_color_active
        # wird Grau (passiv) wenn input nicht aktiv und der angezeigte text der anfangs anzeige text ist
        if not self.input_active and self.input_text_list == self.anfangs_anzeige_text_list:
            color = self.input_color_passive

        text_draw(win, self.input_text_list, self.input_rect, color, self.input_font,
                  input_spacer_counter=self.input_spacer_counter, input_active=self.input_active,
                  binde_seite=self.binde_seite)

        # is a warning at maximal lenght of text should be displayed and the input text is at it's maximum the info is drawn
        if self.input_text_ist_max_len and self.max_len_info_anzeigen:
            t_input = self.input_max_len_font.render(
                f"Maximale Länge Erreicht!", True, (255, 255, 255))
            win.blit(t_input, (self.anfangs_x - t_input.get_width()//2,
                               self.input_rect.y + self.input_rect.height + t_input.get_height()//2))

        if self.label:
            y = self.label_y + ((1 - self.font_size_height_rel) * self.input_rect.height)
            t_label = self.input_font.render(
                self.label, True, (255, 255, 255))
            win.blit(t_label, (self.label_x, y))


if __name__ == '__main__':

    import os
    import sys

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

    FPS = 24

    pygame.init()
    WIN = pygame.display.set_mode((SCRWIDTH, SCRHEIGHT))
    pygame.display.set_caption("Space Game")
    FONT = pygame.font.SysFont("comicsans", 30)
    directory_of_file = os.path.normpath(sys.argv[0] + os.sep + os.pardir)

    CLOCK = pygame.time.Clock()

    def draw():
        WIN.fill((0, 0, 0))

    def main():
        run = True
        input_box = InputBox(100, 100, 250, 50,  anfangs_anzeige_text=["lol", "rutsch"],
                             umrandung="rect", input_anfangs_active=False, vergroserungs_richtung="beide",
                             font_size_height_rel=1, zeilen_abstand_rel=0.7, binde_seite="links", label= "Test:", label_x= 200, 
                              label_abstand_x= 100)

        while run:
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        input_box.set_input_text_value("34:54")
                    
                input_box.event_check(event)

            input_box.update()

            draw()
            input_box.draw(WIN)

            pygame.display.update()

    main()
    pygame.quit()
