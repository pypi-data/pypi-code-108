from .wordtile import *
from .console import *
from .mocio import *
from .border import *
from .ui import *
import threading
import pygame

window = Console()


def __init() -> None:
    """自动生成控制台界面的函数，不要手动调用

    """
    ok = False

    def create_console():
        global window
        window.init(80, 25, 20, 'console')
        nonlocal ok
        ok = True
        window.start()

    thread = threading.Thread(target=create_console)
    thread.start()
    while not ok:
        pygame.time.wait(10)


__init()
moprint = Printer(window)
moinput = Reader(window, moprint)
