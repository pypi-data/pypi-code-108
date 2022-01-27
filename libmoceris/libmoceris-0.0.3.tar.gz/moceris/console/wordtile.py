class WordTile:
    """字符块"""

    def __init__(self, char: str, fore_color, back_color, wide=False):
        """
        初始化，一般由 mocio.Printer 代理，不需要手动调用。

        :param char: 字符，请保证其长度为 1
        :param fore_color: 前景色
        :param back_color: 背景色
        :param wide: 是否为宽字符
        """
        # assert (len(char) == 1)
        self.char = char
        self.fore_color = fore_color
        self.back_color = back_color
        self.wide = wide
        self.is_new = True
