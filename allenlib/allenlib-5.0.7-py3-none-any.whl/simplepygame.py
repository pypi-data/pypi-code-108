# -*- coding: UTF-8 -*-
import pygame, sys
from pygame.locals import *
pygame.init()
def font(filename,size):
    pygame.font.Font(filename, size)
def text(text,color,bgcolor=None):
    pygame.font.Font.render(text,False,tuple(color),background=bgcolor)
def update():
    pygame.display.update()
def isquit():
    if event.type == QUIT:
        return True
    else:
        return False
def autoquit():
    pygame.quit()
    sys.exit()
def quitis():
    if isquit():
        autoquit()
def quitwhile():
    if isquit():
        return False
        autoquit()
    else:
        return True
def bgmsc(filename):
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(-1,0.0)
def msc(filename):
    return pygame.mixer.Sound(filename)
def playmsc(msc):
    msc(msc).play()
def nobgm():
    pygame.mixer.music.stop()