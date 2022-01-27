import sys
import os

sys.path.insert(0, os.path.abspath('../'))
from moceris.console import moprint, moinput, Border, Scene, VerticalPanel, HorizontalPanel, FuncElement
import pygame
import time


def print_in_rect():
    moprint.rect = (10, 10, 50, 20)
    for i in range(100000):
        moprint(i, ' ')

def test_input():
    s = moinput('─输入点什么：')
    moprint('输入的内容：', s)


def border_test():
    moprint('hello\nworld你好')
    border = Border(80, 25)
    border.draw_vertical(10, 5, 24)
    border.draw_horizontal(5, 10, 50)
    border.draw_vertical(20, 5, 20)
    border.draw_horizontal(10, 0, 79)
    border.display()


def ui_test():
    def caption_display(elem, *args):
        moprint('━' * elem.rect.width, '\nthis is caption!\n\t\t\t\tMove arrow keys to choose element!')

    data = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pt = 0
    textbox_str = 'Monday'

    def list_display(elem, *args):
        for i, obj in enumerate(data):
            if i == pt:
                moprint('>')
            else:
                moprint(' ')
            moprint(obj, '\n')

    def list_update(elem, *args):
        nonlocal pt, data, textbox_str
        d = args[0]
        if d == 0:
            if pt > 0:
                pt -= 1
        elif d == 1:
            if pt < len(data) - 1:
                pt += 1
        textbox_str = data[pt]

    def textbox_display(elem, *args):
        moprint('selected:', textbox_str)

    def inputbox_display(elem, *args):
        moprint('press [i] to input here')

    scene = Scene(
        VerticalPanel(None,
                      FuncElement('caption', pt_display=caption_display, pt_update=None),
                      HorizontalPanel(None,
                                      FuncElement('list', pt_display=list_display, pt_update=list_update),
                                      VerticalPanel(None,
                                                    FuncElement('textbox', pt_display=textbox_display, pt_update=None),
                                                    FuncElement('inputbox', pt_display=inputbox_display, pt_update=None), True, 16
                                                    )
                                      , True, 20),
                      True, 3))
    while True:
        scene.display()
        key = moinput.read_key()
        if key == pygame.K_UP:
            scene.update('list', 0)
        elif key == pygame.K_DOWN:
            scene.update('list', 1)
        if key == pygame.K_UNKNOWN:
            break
        if key == pygame.K_i:
            [x, y, width, height] = scene.get_element('inputbox').rect
            moprint.set_rect((x, y, x + width - 1, y + height - 1))
            moprint.clear_rect()
            res = moinput('Input here:')
            if res in data:
                pt = data.index(res)
                textbox_str = res


if __name__ == '__main__':
    # print_in_rect()
    # test_input()
    # border_test()
    # ui_test()
    moprint('$bblack','h','$bgreen','f')
