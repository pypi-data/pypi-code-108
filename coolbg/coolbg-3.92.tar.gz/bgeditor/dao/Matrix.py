from bgeditor.dao.Summon import Summon
import random
from PIL import Image
from bgeditor.common.image_helper import ReduceOpacity
import numpy as np
from moviepy.editor import *
from bgeditor.common.utils import change_color_alpha
class Matrix:
    def __init__(self, bg_clip, rate_summon, arr_summon_tempalte, arr_direction, rang_locx, rang_locy,
                 rang_speedx=[20,200], rang_speedy=[20, 200], rang_opacity=[20,800], rang_size=[1,100],
                 arr_color=[], delay=3, m_w=1920, m_h=1080):
        """
        :param bg_clip:
        :param rate_summon:
        :param arr_summon_tempalte:
        :param duration: time of audio
        :param arr_direction:0,1,2,3,4,5,6,7 :12h,1h,3h,4h,6h,8h,10h
        :param rang_locx: [x1,x2], randge of location x asis
        :param rang_locy: [y1,y2], randge of location y asis
        :param rang_speedx:[v1,v2], speed of x asis
        :param rang_speedy:[v1,v2], speed of y asis
        :param rang_opacity:[0,1000], range of opacity
        :param rang_delay:[0,duration], time appear of star
        :param m_w:1920
        :param m_h:1080
        """
        self.rate_summon= rate_summon
        self.arr_summon_tempalte_path = arr_summon_tempalte
        self.arr_summon_tempalte_image = []
        self.m_w = m_w
        self.m_h = m_h
        self.arr_direction= arr_direction
        self.rang_locx=rang_locx
        self.rang_locy=rang_locy
        self.rang_speedx = rang_speedx
        self.rang_speedy= rang_speedy
        self.rang_opacity=rang_opacity
        self.arr_color=arr_color
        self.delay = delay
        self.rang_size= rang_size
        self.bg_clip=bg_clip
        self.t_summon= self.delay
    def setup_summon_template(self):
        for summon_template_path in self.arr_summon_tempalte_path:
            template_a = Image.open(summon_template_path).convert('RGBA')
            if len(self.arr_color) > 0:
                for color in self.arr_color:
                    img_layer = Image.fromarray(
                        change_color_alpha(np.asarray(template_a), color))
                    self.arr_summon_tempalte_image.append(img_layer)
            else:
                self.arr_summon_tempalte_image.append(template_a)
    def setup(self):
        try:
            self.list_summon = []
            self.setup_summon_template()
            return True
        except:
            pass
        return False
    def add_sumon(self,t):
        if t>= self.t_summon and t < self.t_summon+1:
            for i in range(self.rate_summon):
                summon = {}
                summon['template'] = random.choice(self.arr_summon_tempalte_image)
                s_h = s_w = random.randint(self.rang_size[0],self.rang_size[1])
                summon['skill'] = summon['template'].resize((s_w, s_h), Image.ANTIALIAS)
                summon['algorithm'] = Summon.setup(self.arr_direction, self.rang_locx, self.rang_locy, self.rang_speedx,
                                                   self.rang_speedy, self.rang_opacity, [self.t_summon, self.t_summon+1], s_w, s_h, self.m_w, self.m_h)
                summon['skill']= self.style_summon(summon)
                self.list_summon.append(summon)
            self.t_summon+=1

    def style_summon(self,summon):
        img_layer = summon['skill']
        return ReduceOpacity(img_layer, summon['algorithm'].opacity)

    def make_frame(self, t):
        img_tmp = Image.fromarray(self.bg_clip.get_frame(t))
        self.add_sumon(t)
        for summon in self.list_summon:
            x, y = summon['algorithm'].move(t)
            if x and y:
                img_rd = summon['skill']
                img_tmp.paste(img_rd, (int(x), int(y)), img_rd)
        return np.asarray(img_tmp)
    def make(self):
        return VideoClip(self.make_frame, duration = 3600)






