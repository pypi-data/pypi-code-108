import sys
import time
import random
import threading
from .colorain import *
from .engine import *


class Snake(Sprite):
    def __init__(self, head_init, scene):
        if isinstance(head_init, tuple):
            head_init = Coord2D(*head_init)
        self.positions =  [head_init, Coord2D(head_init.x-1, head_init.y), Coord2D(head_init.x-2, head_init.y)]
        super().__init__(scene, self.positions)
    
    def draw(self):
        self.scene.edit_pixel(self.positions[0], Stx(f"<f=lg;b=b>-</>").parsed)
        for pos in self.positions[1:]:
            self.scene.edit_pixel(pos, Stx(f"<f=lr;b=y>{BLOCKS[2]}</>").parsed)

    def grow(self, direction):
        tail = self.positions[-1]
        if isinstance(direction, Coord2D):
            self.positions.append(direction)
        elif direction == 'VER':
            self.positions.append(Coord2D(tail.x, tail.y-1))
        elif direction == 'HOR':
            self.positions.append(Coord2D(tail.x-1, tail.y))
        elif direction in ['w', 'a', 's', 'd']:
            dx = -1 if direction=='d' else (1 if direction=='a' else 0)
            dy = -1 if direction=='s' else (1 if direction=='w' else 0)
            self.positions.append(Coord2D((tail.x + dx)%self.scene.width, (tail.y + dy)%self.scene.height))
        self.draw()

    def move(self, direction):
        if direction == Coord2D(0,0): 
            return self.positions[-1]
        self.erase()

        predecessor_old_pos = self.positions[0]
        self.positions[0] += direction

        for i in range(1,len(self.positions)):
            curr_node_old_pos = self.positions[i]
            self.positions[i] = predecessor_old_pos
            predecessor_old_pos = curr_node_old_pos
            
        self.draw()
        return curr_node_old_pos


def spawn_apple(scene, snake):
    width = scene.width
    height = scene.height
    ok = False
    while not ok:
        ok = True
        apple_x = random.randint(0, width-1)
        apple_y = random.randint(0, height-1)
        apple_pos = Coord2D(apple_x, apple_y)

        for pos in snake.positions:
            if pos == apple_pos:
                ok = False
    scene.paint_pixel(apple_pos, 'lightred')
    
    return apple_pos

def update_scoreboard(prev_score, scoreboard):
    curr_score = prev_score + 1
    scoreboard_text = f"Score: {curr_score}"
    
    for i in range(len(scoreboard_text)):
        scoreboard.scene[0][i] = Stx(f"<f=b;b=gr>{scoreboard_text[i]}</>").parsed
    
    return curr_score, scoreboard


def key_to_coord(key):
    if key == 'w':
        return Coord2D(0,-1)
    elif key == 's':
        return Coord2D(0, 1)
    elif key == 'a':
        return Coord2D(-1,0)
    elif key == 'd':
        return Coord2D(1, 0)
    else:
        return Coord2D(0,0)


def handle_input(dirn):
    key = ''

    while key != 'q':
        key = getChar()
        if key=='q': 
            dirn[0] =  None
            break
        elif key=='r':
            dirn[1] = 'r'
        else:
            dirn[0] = key_to_coord(key)
    


def snake_game(width = 20, height = 20, start_pos = (5,3), fps = 2):
    gamesc = Scene2D(width, height)
    
    scoreboard = Scene2D(width, 1)
    score, scoreboard = update_scoreboard(-1, scoreboard)

    snake = Snake(Coord2D(*start_pos), gamesc)
    dirn = [key_to_coord('d'), '']
    apple_pos = spawn_apple(gamesc, snake)
    
    inp_thread = threading.Thread(target = handle_input, args=(dirn,))
    inp_thread.start()

    while True:
        scoreboard.render(reset=False)
        gamesc.render()

        if dirn[0] is not None:
            tail_last_pos = snake.move(dirn[0])
            if dirn[1]=='r':
                snake.rotate(math.pi/2)
        else:
            break
    
        if snake.positions[0] == apple_pos:
            score, scoreboard = update_scoreboard(score, scoreboard)
            snake.grow(tail_last_pos)
            apple_pos = spawn_apple(gamesc, snake)
        
        move_cursor(-1,-1)
        time.sleep(1/fps)
    
    return gamesc, snake