import math
import random
class Summon:
    def __init__(self, direction, locx, locy, speedx, speedy, opacity, delay,s_w=100,s_h=100,m_w=1920,m_h=1080):
        self.direction = direction
        self.locx = locx
        self.locy = locy
        self.speedx = speedx
        self.speedy = speedy
        self.opacity = opacity #1000 is max
        self.delay = delay
        self.s_w = s_w
        self.s_h = s_h
        self.m_w = m_w
        self.m_h = m_h

    @staticmethod
    def setup(arr_direction, rang_locx, rang_locy, rang_speedx=[20,200], rang_speedy=[20, 200], rang_opacity=[0,800], rang_delay=[0,15], s_w=100, s_h=100, m_w=1920, m_h=1080):
        direction = random.choice(arr_direction)
        locx = random.randint(*rang_locx)
        locy = random.randint(*rang_locy)
        speedx = random.randint(*rang_speedx)
        speedy = random.randint(*rang_speedy)
        opacity = random.randint(*rang_opacity)/1000.0
        delay = random.uniform(*rang_delay)
        return  Summon(direction,locx,locy,speedx,speedy,opacity, delay,s_w,s_h,m_w,m_h)

    def to_middle_left(self, t):
        y = self.locy + self.speedy * math.sin(t)
        x = self.locx - self.speedx * t * 2
        return x, y

    def to_middle_right(self, t):
        y = self.locy + self.speedy * math.sin(t)
        x = self.locx + self.speedx * t * 2
        return x, y

    def to_top_left(self, t):
        y = self.locy - self.speedy * (1.5 * t + math.sin(2 * t))
        x = self.locx - self.speedx * t * 2
        return x, y

    def to_top_center(self, t):
        y = self.locy - self.speedy * (1.5 * t)
        # x=self.locx+random.choice([-1,1])*self.speedx*math.sin(t) #nhap nhay
        x = self.locx - self.speedx * math.sin(t)
        return x, y

    def to_top_right(self, t):
        y = self.locy - self.speedy * (1.5 * t + math.sin(2 * t))
        x = self.locx + self.speedx * t * 2
        return x, y

    def to_buttom_left(self, t):
        y = self.locy + self.speedy * (1.5 * t + math.sin(2 * t))
        x = self.locx - self.speedx * t * 2
        return x, y

    def to_buttom_center(self, t):
        y = self.locy + self.speedy * (1.5 * t)
        x = self.locx + self.speedx * math.sin(t)
        return x, y

    def to_buttom_right(self, t):
        y = self.locy + self.speedy * (1.5 * t + math.sin(2 * t))
        x = self.locx + self.speedx * t * 2
        return x, y

    def move(self, t):
        if t - self.delay < 0:
            return None, None
        t = t - self.delay
        if self.direction == 0:
            (x, y) = self.to_top_center(t)
        if self.direction == 1:
            (x, y) = self.to_top_right(t)
        if self.direction == 2:
            (x, y) = self.to_middle_right(t)
        if self.direction == 3:
            (x, y) = self.to_buttom_right(t)
        if self.direction == 4:
            (x, y) = self.to_buttom_center(t)
        if self.direction == 5:
            (x, y) = self.to_buttom_left(t)
        if self.direction == 6:
            (x, y) = self.to_middle_left(t)
        if self.direction == 7:
            (x, y) = self.to_top_left(t)
        if x > self.m_w or y > self.m_h or x+ self.s_w  < 0 or  y + self.s_h < 0:
            #print(x, y)
            return None, None
        return x, y

