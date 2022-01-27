class BorderNode:
    """
    Border 中每一个位置的对象

    保存这个位置分别有哪个方向的边框

    不需要手动实例化
    """

    def __init__(self, n=False, s=False, w=False, e=False):
        """
        初始化

        :param n: 上方向边框
        :param s: 下方向边框
        :param w: 左方向边框
        :param e: 右方向边框
        """
        self.n = n
        self.s = s
        self.w = w
        self.e = e

    def __str__(self):
        """
        将 BorderNode 对象转换成边框字符

        注意：当该位置只有一个方向的制表符时，返回值为空字符

        :return: 转换的字符
        """
        if self.n:
            if self.s:
                if self.w:
                    if self.e:
                        return '╋'
                    else:
                        return '┫'
                else:
                    if self.e:
                        return '┣'
                    else:
                        return '┃'
            else:
                if self.w:
                    if self.e:
                        return '┻'
                    else:
                        return '┛'
                else:
                    if self.e:
                        return '┗'
                    else:
                        return ''
        else:
            if self.s:
                if self.w:
                    if self.e:
                        return '┳'
                    else:
                        return '┓'
                else:
                    if self.e:
                        return '┏'
                    else:
                        return ''
            else:
                if self.w and self.e:
                    return '━'
                else:
                    return ''

    def empty(self):
        """
        判断该位置是否无任意方向的边框

        注意即使判断为 True，__str__ 返回值依然可能为空

        """
        return not (self.n or self.s or self.w or self.e)


class Border:
    """
    保存边框的画布对象

    一般搭配 moceris.console.ui.Scene 使用，不需要手动实例化
    """

    def __init__(self, width, height):
        """
        初始化

        :param width: 画布宽
        :param height: 画布高
        """
        self.width = width
        self.height = height
        self.data = [[BorderNode() for i in range(width)] for j in range(height)]

    def draw_vertical(self, x, y1, y2) -> None:
        """
        画竖边框

        :param x: 边框的 x 坐标
        :param y1: 边框一端的 y 坐标
        :param y2: 边框另一端的 y 坐标
        """
        if y1 > y2:
            [y1, y2] = [y2, y1]
        for i in range(y1, y2):
            if 0 <= i < self.height:
                self.data[i][x].s = True
        for i in range(y1 + 1, y2 + 1):
            if 0 <= i < self.height:
                self.data[i][x].n = True

    def draw_horizontal(self, y, x1, x2) -> None:
        """
        画横边框

        :param y: 边框的 y 坐标
        :param x1: 边框一端的 x 坐标
        :param x2: 边框另一端的 x 坐标
        """
        if x1 > x2:
            [x1, x2] = [x2, x1]
        for i in range(x1, x2):
            if 0 <= i < self.width:
                self.data[y][i].e = True
        for i in range(x1 + 1, x2 + 1):
            if 0 <= i < self.width:
                self.data[y][i].w = True

    def display(self) -> None:
        """
        将边框呈现在控制台上

        注意输出受 Console.rect 的影响（问题大了可能会修）
        """
        from moceris.console import moprint
        for i, row in enumerate(self.data):
            for j, node in enumerate(row):
                if not node.empty():
                    moprint.set_pos(i, j)
                    moprint(str(node))
