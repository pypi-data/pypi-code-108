import pygame as pg
import numpy as np

def distance(start_point,end_point):
    length = ((start_point[0]-end_point[0])**2+(start_point[1]-end_point[1])**2)**0.5
    return length 
def dot_line(Surface,color,start_point,end_point,width=2,line_pix = 5,blank_pix = 5):
    #step 1: Dividing the whole line segment into the blank area and drawing area.
    start_point = np.array(start_point)
    end_point   = np.array(end_point)
    if np.random.rand()<0.5:
        key = 1
    else:
        key = 2
    while True:
        if key == 1:   # means line area
            if  distance(start_point,end_point) <=line_pix:
                pg.draw.line(surface=Surface,color=color,start_pos = start_point,end_pos = end_point,width = width)
                break
            else:
                pos_1 = end_point-start_point
                l = distance([0,0],pos_1)
                end_1 = start_point + pos_1*(line_pix/l)
                pg.draw.line(surface=Surface,color=color,start_pos = start_point,end_pos = end_1,width = width)
                start_point = end_1.copy()
                key = 2
            
        else:
            if  distance(start_point,end_point) <=blank_pix:
                #pg.draw.line(surface=Surface,color=color,start_pos = start_point,end_pos = end_point,width = width)
                break
            else:
                pos_1 = end_point-start_point
                l = distance([0,0],pos_1)
                end_1 = start_point + pos_1*(blank_pix/l)
                #pg.draw.line(surface=Surface,color=[0,255,0],start_pos = start_point,end_pos = end_1,width = width)
                start_point = end_1.copy()
                key = 1
    



