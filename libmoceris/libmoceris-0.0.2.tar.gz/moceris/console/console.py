from .wordtile import WordTile
import pygame
from typing import Tuple, List
import queue
import os


class Console:
    """
    万 恶 之 源
    """
    width: int
    height: int
    font: pygame.font.Font
    font_width: int
    font_height: int
    window_width: int
    window_height: int
    data: List[List[WordTile]]
    data_updated: bool
    window: pygame.Surface
    raw_key: queue.Queue
    is_open: bool
    cursor_x: int
    cursor_y: int
    cursor_visible: bool
    cursor_tick: int
    cursor_last_change_time: int
    screen_last_update_time: int
    cursor_width: int
    fps: int
    height_offset: int
    fps_last_update_time: int
    fps_cnt: int

    def __init__(self):
        """
        初始化，别问我为什么不在这里定义成员变量，因为 pygame 的所有绘制相关函数必须在一个线程里执行，包括 init。
        """
        pass

    def init(self, width, height, font_height, title) -> None:
        """
        真正的 init

        :param width: 控制台宽
        :param height: 控制台高
        :param font_height: 字体高度
        :param title: 标题
        """
        self.width = width
        self.height = height
        self.height_offset = 0
        pygame.init()
        self.font = pygame.font.Font(os.path.dirname(os.path.abspath(__file__)) + r'\Apple Hei.ttf', font_height)
        [self.font_width, self.font_height] = self.font.size('a')
        self.font_height -= self.height_offset * 2
        [self.window_width, self.window_height] = [self.width * self.font_width,
                                                   self.height * self.font_height]
        self.data = [[WordTile(' ', pygame.Color('#39C5BB'), pygame.Color('white')) for i in range(width)] for j in
                     range(height)]
        self.data_updated = True
        self.window = pygame.display.set_mode((self.window_width, self.window_height), flags=pygame.DOUBLEBUF)
        pygame.display.set_caption(title)
        self.raw_key = queue.Queue()
        self.is_open = True
        self.cursor_x = 0
        self.cursor_y = 0
        self.cursor_visible = True
        self.cursor_tick = 500
        self.screen_last_update_time = pygame.time.get_ticks()
        self.cursor_last_change_time = pygame.time.get_ticks()
        self.cursor_width = 2
        self.fps = 120
        self.fps_last_update_time = pygame.time.get_ticks()
        self.fps_cnt = 0

    def start(self) -> None:
        """
        开启控制台的事件监听和更新操作，请在一个独立的线程执行 init 和此方法。
        """
        while True:
            now = pygame.time.get_ticks()
            if (now - self.screen_last_update_time) * self.fps >= 1000:
                self.fps_cnt += 1
                self.screen_last_update_time = now
                if now - self.cursor_last_change_time >= self.cursor_tick:
                    self.cursor_visible = not self.cursor_visible
                    self.cursor_last_change_time = now
                if self.data_updated:
                    self.data_updated = False
                    for i, row in enumerate(self.data):
                        """render"""
                        wide = False
                        for j, obj in enumerate(row):
                            skip = False
                            if not obj.is_new:
                                skip = True
                            if wide:
                                wide = False
                                skip = True
                            if skip:
                                continue
                            obj.is_new = False
                            [x, y] = [j * self.font_width, i * self.font_height]
                            if obj.wide:
                                wide = True
                                pygame.draw.rect(self.window, obj.back_color,
                                                 (x, y, x + self.font_width * 2, y + self.font_height))
                            else:
                                pygame.draw.rect(self.window, obj.back_color,
                                                 (x, y, x + self.font_width, y + self.font_height))
                            text = self.font.render(obj.char, True, obj.fore_color, obj.back_color)
                            self.window.blit(text.subsurface(pygame.Rect(0, self.height_offset, text.get_width(),
                                                                         text.get_height() - self.height_offset * 2)),
                                             (x, y))
                cursor_color = pygame.color.Color('black') if self.cursor_visible else self.data[self.cursor_x][self.cursor_y].back_color
                pygame.draw.line(self.window, cursor_color,
                                 (self.cursor_y * self.font_width, self.cursor_x * self.font_height),
                                 (self.cursor_y * self.font_width,
                                  self.cursor_x * self.font_height + self.font_height - 1), self.cursor_width)
                pygame.display.flip()

            if now - self.fps_last_update_time >= 1000:
                print('fps:', self.fps_cnt * 1000 / (now - self.fps_last_update_time))
                self.fps_cnt = 0
                self.fps_last_update_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.is_open = False
                    return

                elif event.type == pygame.KEYDOWN:
                    self.raw_key.put(event)

    def put_char(self, x, y, tile) -> None:
        """
        在给定的位置放置一个文字

        :param x: x 坐标
        :param y: y 坐标
        :param tile: 一个 WordTile 对象，表示一个文字
        """
        self.data_updated = True
        self.data[x][y] = tile

    def update_cursor_pos(self, x, y) -> None:
        """
        修改控制台光标的位置，一般由 mocio.Printer 对象代理，不需要手动操作。

        :param x: x 坐标
        :param y: y 坐标
        """
        self.cursor_x = x
        self.cursor_y = y
        self.cursor_visible = True
        self.cursor_last_change_time = pygame.time.get_ticks()
