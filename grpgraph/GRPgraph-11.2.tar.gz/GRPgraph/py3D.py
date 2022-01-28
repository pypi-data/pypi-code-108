from ursina import Entity as En
from ursina import window
from ursina import camera as cam
from ursina import Ursina as Us
from ursina import color
import keyboard

def Colorize_text(col):
    if col == 'red':col2 = color.red
    elif col == 'green':col2 = color.green
    elif col == 'orange':col2 = color.orange
    elif col == 'blue':col2 = color.blue
    elif col == 'yellow':col2 = color.yellow
    elif col == '':col2 = color.black
    return col2

def colorize_rgb(col=()):
    col2 = color.rgb(col[0],col[1],col[2],col[3])
    return col2

class App:
    def __init__(self,title='',bordles = False,size=[],positions=[],bg_col2=''):
        self.app = Us()
        
        



        if size == 'FULL' or size == 'full':self.size = window.fullscreen_size
        else: self.size = size
        self.title = title
        self.bordles = bordles
        self.pos = [positions[0],positions[1]]
        self.col = bg_col2
        if type(self.col) == str:self.bg_col = Colorize_text(self.col)
        else:self.bg_col = colorize_rgb(bg_col2)
        

        window.position = self.pos
        window.color = self.bg_col
        window.title = self.title
        window.size = self.size
        window.borderless = self.bordles
    def Set_size(self,size=[]):
        self.size = size
        window.size = self.size
    def Set_pos(self,pos=[]):
        self.pos = pos
        window.position = self.pos
    def Set_col(self,col=''):
        self.col = col
        if col == str():self.bg_col = Colorize_text(self.col)
        else:self.bg_col = colorize_rgb(self.col)
        window.color = self.bg_col
    def Get_color(self):
        return self.col
    def Get_size(self):
        return self.size
    def Get_pos(self):
        return self.pos
    def Run(self):
        self.app.run()

class KB0rd:
    def __init__(self):
        pass
    def On_kee_press(self,key=""):
        on = keyboard.is_pressed(key)
        return on

class Object_s:
    def __init__(self,modeles='cube' , col='red' , positions=(0,0,0) , scale = 0, scale_x = 1 , scale_y = 1 , scale_z = 1 , texture=None):
        self.modeles = modeles
        self.col = col
        self.scl_x = scale_x
        self.scl_y = scale_y
        self.scl_z = scale_z
        self.positions = positions
        if scale != 0:
            self.scale = scale
        else:
            self.scale = None
        self.texture = texture
        if type(self.col) == str:self.msh_col = Colorize_text(self.col)
        else:self.msh_col = colorize_rgb(self.col)

        ent = En(model = self.modeles,
                color = self.msh_col,
                position = self.positions,
                scale = self.scale,
                scale_x = self.scl_x,
                scale_y = self.scl_y,
                scale_z = self.scl_z,
                texture = self.texture) 
        self.ent = ent
    def Rotation_Z(self,ugl):
        self.ent.rotation_z = ugl
    def Rotation_X(self,ugl):
        self.ent.rotation_x = ugl
    def Rotation_Y(self,ugl):
        self.ent.rotation_y = ugl
    def Rotation(self,ugles=[]):
        self.ent.rotation_y = ugles[1]
        self.ent.rotation_x = ugles[0]
        self.ent.rotation_z = ugles[2]

class Camera:
    def __init__(self,positions=[]):
        self.positions = positions
        self.c = cam
        self.c.position = self.positions  
    def Set_pos(self,pos):
        self.positions = pos
        self.c.position = self.positions




