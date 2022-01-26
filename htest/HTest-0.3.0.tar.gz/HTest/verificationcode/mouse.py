#!/usr/bin/env python3.7
# encoding: utf-8
# 获取鼠标的实时坐标

from pyautogui import position, size, click
from HTest import BasePage


def mouse_point():

    last_point = position()
    screen = size()
    try:
        while click:
            new_point = position()
            if new_point != last_point:
                print("鼠标的实时坐标是:")
                print(new_point)
                last_point = new_point
                print("屏幕大小是:" + screen)
    except KeyboardInterrupt:
        print("\nExit")


if __name__ == '__main__':
    mouse_point()
