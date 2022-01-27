from .console import Console
from .wordtile import WordTile
from typing import Tuple
import queue
import pygame


def is_wide_char(char: str) -> bool:
    """
    判断一个字符（请保证其为 1 长度）是否为宽字符
    :param char: 要判断的字符
    :return: 判断结果
    """
    assert (len(char) == 1)
    widths = [
        (126, 1), (159, 0), (687, 1), (710, 0), (711, 1),
        (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
        (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1),
        (8426, 0), (9000, 1), (9002, 2), (11021, 1), (12350, 2),
        (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1),
        (55203, 2), (63743, 1), (64106, 2), (65039, 1), (65059, 0),
        (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
        (120831, 1), (262141, 2), (1114109, 1),
    ]

    def get_width(o):
        """Return the screen column width for unicode ordinal o."""
        nonlocal widths
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    return get_width(ord(char)) == 2


class Printer:
    """
    Console 的输出管理器

    因为离用户最近所以很多方法作了隐藏处理
    """

    def __init__(self, target):
        """
        初始化

        :param target: 要绑定的 Console 对象
        """
        self.x = 0
        self.y = 0
        self.console = target
        self.fore_color = pygame.Color('#39C5BB')
        self.back_color = pygame.Color('white')
        self.rect = (0, 0, self.console.width - 1, self.console.height - 1)

    def __call__(self, *args) -> None:
        """
        重载 () 作为输出函数。

        格式和 py 原生 print() 类似，不过没有 sep 和 end （傻子才用）

        一些独有用法：

        - 一个单独字符串，第一个字符为 $，将视为控制命令，其后接命令字符（不带空格），单独的一个 '$' 将正常输出：

            - f：修改前景色，后跟 pygame.color 的字符串形式（预设定颜色或#000000形式），如'$fwhite'或'$f#39C5BB'

            - b: 修改背景色，用法同上

        :param args: 输出的内容
        """
        for obj in args:
            if isinstance(obj, str) and len(obj) == 0:
                continue
            if isinstance(obj, str) and obj[0] == '$' and len(obj) > 1:
                if obj[1] == 'f':
                    self.fore_color = pygame.Color(obj[2:])
                elif obj[1] == 'b':
                    self.back_color = pygame.Color(obj[2:])
                else:
                    raise ValueError
            else:
                self.__print(str(obj))
        self.console.update_cursor_pos(self.x, self.y)

    def __out_of_rect(self) -> bool:
        """
        判断指针是否出界

        :return: 判断结果
        """
        return not (self.rect[0] <= self.y <= self.rect[2] and self.rect[1] <= self.x <= self.rect[3])

    def __print(self, string) -> None:
        """
        内部输出函数

        :param string: 传入的字符串
        """
        if not self.console.is_open:
            return
        if self.__out_of_rect():
            self.x = self.rect[1]
            self.y = self.rect[0]
        for char in string:
            if is_wide_char(char):
                if self.y == self.rect[2]:
                    self.__print(' ')
                self.console.put_char(self.x, self.y, WordTile(char, self.fore_color, self.back_color, True))
                self.__scroll_next()
                self.console.put_char(self.x, self.y, WordTile(' ', self.fore_color, self.back_color))
                self.__scroll_next()
            else:
                if char == '\n':
                    self.__scroll_next_line()
                elif char == '\r':
                    self.y = self.rect[0]
                elif char == '\b':
                    self.__scroll_back()
                elif char == '\t':
                    self.__print(' ' * (4 - (self.y - self.rect[0]) % 4))
                else:
                    self.console.put_char(self.x, self.y, WordTile(char, self.fore_color, self.back_color))
                    self.__scroll_next()

    def __scroll_next(self) -> None:
        """
        输出一个字符后，将光标向右推
        """
        if self.y == self.rect[2]:
            self.__scroll_next_line()
        else:
            self.y += 1

    def __scroll_next_line(self) -> None:
        """
        回车处理
        """
        if self.x == self.rect[3]:
            self.x = self.rect[1]
        else:
            self.x += 1
        self.y = self.rect[0]

    def __scroll_back(self) -> None:
        """
        __scroll_next 的逆操作
        """
        if self.y == self.rect[0]:
            self.__scroll_back_line()
        else:
            self.y -= 1

    def __scroll_back_line(self) -> None:
        """
        __scroll_next_line 的逆操作
        """
        if self.x == self.rect[1]:
            self.x = self.rect[3]
        else:
            self.x -= 1
        self.y = self.rect[2]

    def clear_screen(self, move_cursor=True) -> None:
        """
        清屏
        :param move_cursor: 是否将光标移至输出区域的左上角，默认为 True。
        """
        for i in range(self.console.height):
            for j in range(self.console.width):
                self.console.put_char(i, j, WordTile(' ', self.fore_color, self.back_color))
        if move_cursor:
            x = self.rect[1]
            y = self.rect[0]

    def get_pos(self) -> Tuple[int, int]:
        """
        获取光标位置
        :return: 获取的位置，一个 Tuple[int,int]
        """
        return self.x, self.y

    def set_pos(self, x, y) -> None:
        """
        设置光标位置。

        如果设置了输出区域，且该位置处于区域之外，则下次输出前会被直接拉回来。

        :param x: x 坐标
        :param y: y 坐标
        """
        self.x = x
        self.y = y
        self.console.update_cursor_pos(self.x, self.y)

    def set_rect(self, rect: Tuple[int, int, int, int], move_cursor=True) -> None:
        """
        设置输出区域，rect 的四个参数分别表示左、上、右、下，闭区间。

        这个 API 创建的有点晚了，其他文件里可能有直接操作 moprint.rect 的，懒得改（

        :param rect: 新的输出区域
        :param move_cursor: 是否将指针移至新输出区域的左上角，默认为是
        """
        self.rect = rect
        if move_cursor:
            self.x = self.rect[1]
            self.y = self.rect[0]

    def clear_rect(self, move_cursor=True) -> None:
        """
        清空当前输出区域

        :param move_cursor: 是否将光标移至输出区域的左上角，默认为 True。
        """
        for i in range(self.rect[1], self.rect[3] + 1):
            for j in range(self.rect[0], self.rect[2] + 1):
                self.console.put_char(i, j, WordTile(' ', self.fore_color, self.back_color))
        if move_cursor:
            x = self.rect[1]
            y = self.rect[0]

    def get_rect(self) -> Tuple[int, int, int, int]:
        """获取当前输出区域"""
        return self.rect

    def default_rect(self) -> None:
        """
        将输出区域还原为全屏。
        """
        self.rect = (0, 0, self.console.width - 1, self.console.height - 1)


class Reader:
    """输入管理器，从 Console.raw_key 中读取原始输入并处理。"""
    console: Console
    printer: Printer

    def __init__(self, target, printer):
        """
        初始化

        :param target: 绑定的控制台
        :param printer: 绑定的输出管理器
        """
        self.console = target
        self.printer = printer
        self.buffer = queue.Queue()

    def __read_raw_key(self):
        """
        从 console.raw_key 读取按键事件

        :return: 按键事件（看清楚了是事件不是字符编号）
        """
        while self.console.is_open and self.console.raw_key.empty():
            pygame.time.wait(10)
        if not self.console.is_open:
            return None
        else:
            return self.console.raw_key.get()

    def read_key(self) -> int:
        """
        读取一个按键，返回它的字符编号

        :return: 字符编号
        """
        key = self.__read_raw_key()
        if key is None:
            return pygame.K_UNKNOWN
        return key.key

    def __call__(self, hint='') -> str:
        """
        与 py input() 用法一致
        :param hint: 输入提示词
        :return: 一行字符串
        """
        assert (self.buffer.empty())
        buf = []
        if len(hint) > 0:
            self.printer(hint)
        while True:
            key = self.__read_raw_key()
            if key is None:
                break
            if key.key == pygame.K_RETURN:
                res = ''
                for obj in buf:
                    res += obj.unicode
                self.printer('\n')
                return res
            elif key.key == pygame.K_BACKSPACE:
                if len(buf) > 0:
                    if is_wide_char(buf.pop().unicode):
                        self.printer('\b')
                    self.printer('\b \b')
            elif len(key.unicode) > 0:
                buf.append(key)
                self.printer(key.unicode)
        return ''

    def pause(self) -> None:
        """
        就是字面意思
        """
        self.printer('请按任意键继续. . .')
        self.__read_raw_key()
        self.printer('\n')
