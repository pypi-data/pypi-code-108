from pgzero import ptext
from pgzero.keyboard import keyboard as k

input_text = {'设置温度': '', '设置湿度': ''}


class InputBox:
    def __init__(self, screen, rect, boxname='None', fontcolor='black',
                 rectcolor='black', fontname='fangsong.ttf', fontsize=18):
        self.screen = screen
        self.rect = rect
        self.boxname = boxname
        self.fontcolor = fontcolor
        self.rectcolor = rectcolor
        self.fontname = fontname
        self.fontsize = fontsize
        self.list = []
        self.keys_list = []
        self.keys_list2 = []
        # 是否激活
        self.active = False
        # 是否绘制光标
        self.cursor = True
        # 光标绘制计数器
        self.count = 0
        # 控制删除键
        self.count_time = 0

    def draw(self):
        # 画框
        # self.screen.draw.filled_rect(self.rect, color=(255,255,255))
        self.screen.draw.rect(self.rect, color=self.rectcolor)
        # text_pic = self.screen.draw.textbox(''.join(self.list), self.rect)
        text = ''.join(self.list)
        text_pic = ptext.draw(self.boxname + '：' + text, pos=(self.rect.x, self.rect.y),
                              color=self.fontcolor, fontsize=self.fontsize, fontname=self.fontname)
        # self.screen.draw.text(text, pos=text_pic[1],
        #                       color=self.color, fontsize=self.fontsize)
        # 更新光标计数器
        self.count += 1
        if self.count == 20:
            self.count = 0
            self.cursor = not self.cursor
        # 绘制光标
        if self.active and self.cursor:
            text_pic_rect = text_pic[0].get_rect()
            x = self.rect.x+5+text_pic_rect.width
            self.screen.draw.line(color=(0, 0, 0),
                                  start=(x, self.rect.y),
                                  end=(x, self.rect.y + self.rect.height))

        self.keys_list = ['k.kp' + str(i) for i in range(10)] + \
                         ['k.k_' + str(i) for i in range(10)]
        self.keys_list2 = ['k.kp_enter', 'k.RETURN', 'k.backspace']
        # ['k.backspace', 'k.tab', 'k.clear', 'k.return', 'k.pause',
        #  'k.escape', 'k.space', 'k.exclaim', 'k.quotedbl', 'k.hash',
        #  'k.dollar', 'k.ampersand', 'k.quote', 'k.leftparen', 'k.rightparen',
        #  'k.asterrisk', 'k.plus', 'k.comma', 'k.minus', 'k.reriod', 'k.slash',
        #  'k.shift']
        self.get_text()

    def get_text(self):
        if self.active:
            key = "@"
            for key in (self.keys_list + self.keys_list2):
                if eval(key):
                    self.count_time += 1
                    key = key
                    break
                # else:
                #     self.count_time = 0
            if (self.count_time == 1 or self.count_time >= 40) and self.list and (key in self.keys_list2):
                # 删除
                if k.backspace:
                    self.list.pop()
                # 回车
                elif k.kp_enter or k.RETURN:
                    # self.list.append('\n')
                    input_text[self.boxname] = ''.join(self.list)
            if (self.count_time == 1 or self.count_time >= 40) and (key in self.keys_list):
                self.list.append(key[-1])

    @property
    def text(self):
        return ''.join(self.list)
