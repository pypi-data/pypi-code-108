
from draw_assistance import draw_aacircle
import pygame
import os
import sys
from pygame import gfxdraw


SCRWIDTH = 600
SCRHEIGHT = 600

HW = SCRWIDTH //2
HH = SCRHEIGHT //2

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
FONT = pygame.font.SysFont("comicsans", 30)
directory_of_file = os.path.normpath(sys.argv[0] + os.sep + os.pardir)


CLOCK = pygame.time.Clock()

def draw():
    WIN.fill((0, 0, 0))
    radius = 70
    color = RED
    x = 150  
    y = 300
    # draw_aacircle(WIN, RED, (150, 150) , radius)
    pygame.draw.circle(WIN, RED, (300, 150), radius)    
    # pygame.gfxdraw.aacircle(WIN, 450, 150, radius, RED)
    # for i in range(20):      
    #     gfxdraw.aacircle(WIN, x, y, radius- i , color)

    # gfxdraw.aacircle(WIN, x, y, radius-1, color)
    # gfxdraw.aacircle(WIN, x, y, radius-2, color)
    gfxdraw.filled_circle(WIN, x, y, radius, color)


 
input_font = pygame.font.SysFont("comicsans",30)

def main():
    run = True

    while run:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        draw()

        pygame.display.update()


main()
pygame.quit()
