from typing import Union, List


class CSISequence:
    """
    Since 0.4.13
    """

    def __init__(self, parameter='', intermediate='', final=''):
        """
        CSI序列由ESC [、若干个（包括0个）“参数字节”、若干个“中间字节”，以及一个“最终字节”组成。

        参数字节	0x30–0x3F	0–9:;<=>?
        中间字节	0x20–0x2F	空格、!"#$%&'()*+,-./
        最终字节	0x40–0x7E	@A–Z[\]^_`a–z{|}~

        """

        self.parameter = parameter
        self.intermediate = intermediate
        self.final = final

    def to_string(self):
        return '\033[' + self.parameter + self.intermediate + self.final

    def __str__(self):
        return self.to_string()

    # 光标向指定的方向移动{\displaystyle n}n（默认1）格。如果光标已在屏幕边缘，则无效。

    @staticmethod
    def csi_for_cursor_up(n: int = 1):
        return CSISequence(f'{n}', '', 'A')

    @staticmethod
    def csi_for_cursor_down(n: int = 1):
        return CSISequence(f'{n}', '', 'B')

    @staticmethod
    def csi_for_cursor_forward(n: int = 1):
        return CSISequence(f'{n}', '', 'C')

    @staticmethod
    def csi_for_cursor_back(n: int = 1):
        return CSISequence(f'{n}', '', 'D')

    @staticmethod
    def csi_for_cursor_next_line(n: int = 1):
        """
        光标移动到下面第 n（默认1）行的开头。（非ANSI.SYS）
        """
        return CSISequence(f'{n}', '', 'E')

    @staticmethod
    def csi_for_cursor_previous_line(n: int = 1):
        """
        光标移动到上面第 n（默认1）行的开头。（非ANSI.SYS）
        """
        return CSISequence(f'{n}', '', 'F')

    @staticmethod
    def csi_for_cursor_horizontal_absolute(n: int = 1):
        """
        光标移动到第 n（默认1）列。（非ANSI.SYS）
        """
        return CSISequence(f'{n}', '', 'G')

    @staticmethod
    def csi_for_cursor_move_to_position(row_number: int = 1, column_number: int = 1):
        """
        光标移动到第 row_number 行、第 column_number 列。
        值从1开始，且默认为1（左上角）。
        例如CSI ;5H和CSI 1;5H含义相同；
        CSI 17;H、CSI 17H和CSI 17;1H三者含义相同。
        """
        return CSISequence(f'{row_number};{column_number}', '', 'H')

    @staticmethod
    def csi_for_cursor_format_to_position(row_number: int = 1, column_number: int = 1):
        """
        Horizontal Vertical Position
        Same as CUP, but counts as a format effector function (like CR or LF)
            rather than an editor function (like CUD or CNL).
        This can lead to different handling in certain terminal modes.
        """
        return CSISequence(f'{row_number};{column_number}', '', 'f')

    @staticmethod
    def csi_for_erase_area(n: int = 0):
        """
        清除屏幕的部分区域。
        如果n是0（或缺失），则清除从光标位置到屏幕末尾的部分。
        如果n是1，则清除从光标位置到屏幕开头的部分。
        如果n是2，则清除整个屏幕（在DOS ANSI.SYS中，光标还会向左上方移动）。
        如果n是3，则清除整个屏幕，并删除回滚缓存区中的所有行（这个特性是xterm添加的，其他终端应用程序也支持）。
        """
        return CSISequence(f'{n}', '', 'J')

    @staticmethod
    def csi_for_erase_line(n: int = 0):
        """
        清除行内的部分区域。
        如果n是0（或缺失），清除从光标位置到该行末尾的部分。
        如果n是1，清除从光标位置到该行开头的部分。
        如果n是2，清除整行。光标位置不变。
        """
        return CSISequence(f'{n}', '', 'K')

    @staticmethod
    def csi_for_scroll_up(n: int = 1):
        """
        整页向上滚动n（默认1）行。新行添加到底部。（非ANSI.SYS）
        """
        return CSISequence(f'{n}', '', 'S')

    @staticmethod
    def csi_for_scroll_down(n: int = 1):
        """
        整页向下滚动n（默认1）行。新行添加到顶部。（非ANSI.SYS）
        """
        return CSISequence(f'{n}', '', 'T')

    @staticmethod
    def csi_for_select_graphic_redition(sgr: Union[str, int, List[Union[str, int]]] = None):
        """
        选择图形再现（Select Graphic Rendition）
        """
        if type(sgr) is str:
            parameters = [sgr]
        elif type(sgr) is int:
            parameters = [f'{sgr}']
        elif type(sgr) is list:
            parameters = []
            for x in sgr:
                if type(x) is str:
                    parameters.append(x)
                elif type(x) is int:
                    parameters.append(f'{x}')
                else:
                    raise SyntaxError('SGR FORMAT ERROR')
        else:
            raise SyntaxError('SGR FORMAT ERROR')

        return CSISequence(';'.join(parameters), '', 'm')

    @staticmethod
    def csi_for_device_status_report():
        """
        Reports the cursor position (CPR) by transmitting `ESC[n;mR`, where n is the row and m is the column.)
        """
        return CSISequence('6', '', 'n')
