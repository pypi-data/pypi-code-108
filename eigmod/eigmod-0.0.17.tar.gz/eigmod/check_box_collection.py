if __name__ == '__main__':
    from check_box import CheckBox
else:
    from .check_box import CheckBox


import pygame
import os
import sys

# test Kommentar


class CheckBoxCollection():
    def __init__(self, x, y,  texts, over_all_height=None, individual_height=None, realtive_height_of_element=0.8, only_one_simultaneous_ckeck=False,
                 layout="vertical", horizontal_box_distance=None,
                 color=(255, 255, 255), font_name="comicsans",
                 relative_box_size=0.7, border_thickness=None, draw_mouse_hover=False,
                 fps=60, tick_color=(30, 130, 255), checked_texts=None, check_mouse_button_index=0):

        if not over_all_height and not individual_height or only_one_simultaneous_ckeck and len(checked_texts) > 1:
            raise ValueError

        amount = len(texts)
        self.y = y

        self.only_one_simultaneous_ckeck = only_one_simultaneous_ckeck

        self.height = over_all_height
        if individual_height:
            self.height = individual_height * amount

        # distance between checkboxes
        self.element_height = int(
            round((realtive_height_of_element * self.height / amount), 0))
        distance = ((1-realtive_height_of_element) *
                    (self.height/amount))//3 + self.element_height

        self.check_boxes = []

        for i in range(amount):
            if layout == "horizontal":
                pos_x = x + horizontal_box_distance * i
                pos_y = y
            else:
                pos_x = x
                pos_y = y + (distance) * i

            box_checked = False
            if texts[i] in checked_texts:
                box_checked = True

            self.check_boxes.append(CheckBox(pos_x, pos_y, texts[i], self.element_height, color=color, font_name=font_name,
                                             relative_box_size=relative_box_size, border_thickness=border_thickness,
                                             draw_mouse_hover=draw_mouse_hover, fps=fps, tick_color=tick_color,
                                             is_checked=box_checked, check_mouse_button_index=check_mouse_button_index))

    def draw(self, win):
        for check_box in self.check_boxes:
            check_box.draw(win)

    def update(self):

        self.box_changed = False

        before = [i.is_checked for i in self.check_boxes]

        for check_box in self.check_boxes:
            check_box.update()

        after = [i.is_checked for i in self.check_boxes]

        diffrence = [a - b for a, b in zip(before, after)]

        if self.only_one_simultaneous_ckeck:
            if any(diffrence):
                if any(before) and sum(diffrence) < 0:
                    change_index = [i for i, x in enumerate(before) if x][0]
                    self.check_boxes[change_index].is_checked = not self.check_boxes[change_index].is_checked
                    self.box_changed = True

    def get_checked_texts(self):
        checked_texts = [i.text for i in self.check_boxes if i.is_checked]
        return checked_texts


if __name__ == '__main__':

    FPS = 60

    c = CheckBoxCollection(
        100, 100, ["text1", "text2", "text3", "text4"], over_all_height=400, draw_mouse_hover=True,
        only_one_simultaneous_ckeck=False, checked_texts=["text2"])

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
        c.draw(WIN)

    def main():
        run = True

        while run:
            click_event = False

            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False


            keys = pygame.key.get_pressed()
            c.update()

            draw()

            pygame.display.update()

    main()
    pygame.quit()
