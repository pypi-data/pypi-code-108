import pygame
import math
pygame.init()


def get_font_size(font_name, given_height):
    test_size = 100
    test_font = pygame.font.SysFont(font_name, test_size)
    t_test_font = test_font.render("test", True, (255, 255, 255))
    font_height = t_test_font.get_height()
    height_per_size = font_height/test_size
    font_size = int(round(given_height / height_per_size, 0))

    return font_size


def get_croped_rect(bigrect, smallrect):

    croped_rect = pygame.Rect(0, 0, 0, 0)

    if not bigrect.contains(smallrect):
        r = smallrect.clip(bigrect)
        croped_rect.width = r.width
        croped_rect.height = r.height
        croped_rect.x = bigrect.x - \
            smallrect.x if bigrect.x - smallrect.x > 0 else 0
        croped_rect.y = bigrect.y - \
            smallrect.y if bigrect.y - smallrect.y > 0 else 0
    else:
        croped_rect = pygame.Rect(0, 0, smallrect.width,
                                  smallrect.height)

    return croped_rect


def clip(value, vmin, vmax):

    if vmin >= vmax:
        raise ValueError

    if value > vmax:
        value = vmax
    if value < vmin:
        value = vmin

    return value


def iround(v):
    return int(round(v, 1))


def center_rect(big_rect, small_rect):
    

    x = big_rect.x + (big_rect.width - small_rect.width)/2
    y = big_rect.y + (big_rect.height - small_rect.height)/2

    return x, y


def sort_to_mid(items, right_border, opt_width):

    if "space_amount" not in items.keys() or "space_width" not in items.keys() or "letter" not in items.keys() or "letter_width" not in items.keys():
        raise ValueError

    opt_right = right_border - opt_width/2 + items["letter_width"]/2
    spaces = math.floor((right_border - opt_right) / items["space_width"])
    string = " " * (items["space_amount"] - spaces) + \
        items["letter"] + (spaces * " ")
    return string


def count_charaters(s):
    print(len(s))


if __name__ == '__main__':
    count_charaters("================================================================")
