import re
from typing import Union, List

from nehushtan.cli.CSISequence import CSISequence
from nehushtan.cli.ISO6429 import ISO6429


class ANSITermialHelper:
    """
    Since 0.4.13
    """

    def __init__(self):
        pass

    @staticmethod
    def write(text: Union[str, CSISequence], end: str = ''):
        # if type(text) is not str:
        #     print('<CSI-DEBUG>'+text.__str__()+'</CSI-DEBUG>')
        print(text.__str__(), end=end, flush=True)

    # 光标向指定的方向移动{\displaystyle n}n（默认1）格。如果光标已在屏幕边缘，则无效。

    def cursor_up(self, n: int = 1):
        self.write(CSISequence.csi_for_cursor_up(n))

    def cursor_down(self, n: int = 1):
        self.write(CSISequence.csi_for_cursor_down(n))

    def cursor_forward(self, n: int = 1):
        self.write(CSISequence.csi_for_cursor_forward(n))

    def cursor_back(self, n: int = 1):
        self.write(CSISequence.csi_for_cursor_back(n))

    def cursor_next_line(self, n: int = 1):
        """
        光标移动到下面第 n（默认1）行的开头。（非ANSI.SYS）
        """
        self.write(CSISequence.csi_for_cursor_next_line(n))

    def cursor_previous_line(self, n: int = 1):
        """
        光标移动到上面第 n（默认1）行的开头。（非ANSI.SYS）
        """
        self.write(CSISequence.csi_for_cursor_previous_line(n))

    def cursor_horizontal_absolute(self, n: int = 1):
        """
        光标移动到第 n（默认1）列。（非ANSI.SYS）
        """
        self.write(CSISequence.csi_for_cursor_horizontal_absolute(n))

    def cursor_move_to_position(self, row_number: int = 1, column_number: int = 1):
        """
        光标移动到第 row_number 行、第 column_number 列。
        值从1开始，且默认为1（左上角）。
        例如CSI ;5H和CSI 1;5H含义相同；
        CSI 17;H、CSI 17H和CSI 17;1H三者含义相同。
        """
        self.write(CSISequence.csi_for_cursor_move_to_position(row_number, column_number))

    def cursor_format_to_position(self, row_number: int = 1, column_number: int = 1):
        """
        Horizontal Vertical Position
        Same as CUP, but counts as a format effector function (like CR or LF)
            rather than an editor function (like CUD or CNL).
        This can lead to different handling in certain terminal modes.
        """
        self.write(CSISequence.csi_for_cursor_format_to_position(row_number, column_number))

    def erase_area(self, n: int = 0):
        """
        清除屏幕的部分区域。
        如果n是0（或缺失），则清除从光标位置到屏幕末尾的部分。
        如果n是1，则清除从光标位置到屏幕开头的部分。
        如果n是2，则清除整个屏幕（在DOS ANSI.SYS中，光标还会向左上方移动）。
        如果n是3，则清除整个屏幕，并删除回滚缓存区中的所有行（这个特性是xterm添加的，其他终端应用程序也支持）。
        """
        self.write(CSISequence.csi_for_erase_area(n))

    def erase_area_future(self):
        """
        清除从光标位置到屏幕末尾的部分
        """
        self.erase_area(0)

    def erase_area_past(self):
        """
        清除从光标位置到屏幕开头的部分
        """
        self.erase_area(1)

    def erase_area_all(self):
        """
        清除整个屏幕（在DOS ANSI.SYS中，光标还会向左上方移动）
        """
        self.erase_area(2)

    def erase_area_all_and_clean_buffer(self):
        """
        清除整个屏幕，并删除回滚缓存区中的所有行
        （这个特性是xterm添加的，其他终端应用程序也支持）
        """
        self.erase_area(3)

    def erase_line(self, n: int = 0):
        """
        清除行内的部分区域。
        如果n是0（或缺失），清除从光标位置到该行末尾的部分。
        如果n是1，清除从光标位置到该行开头的部分。
        如果n是2，清除整行。光标位置不变。
        """
        self.write(CSISequence.csi_for_erase_line(n))

    def erase_line_after(self):
        """
        清除从光标位置到该行末尾的部分
        """
        self.erase_line(0)

    def erase_line_before(self):
        """
        清除从光标位置到该行开头的部分
        """
        self.erase_line(1)

    def erase_line_all(self):
        """
        清除整行。光标位置不变
        """
        self.erase_line(2)

    def scroll_up(self, n: int = 1):
        """
        整页向上滚动n（默认1）行。新行添加到底部。（非ANSI.SYS）
        """
        self.write(CSISequence.csi_for_scroll_up(n))

    def scroll_down(self, n: int = 1):
        """
        整页向下滚动n（默认1）行。新行添加到顶部。（非ANSI.SYS）
        """
        self.write(CSISequence.csi_for_scroll_down(n))

    def select_graphic_redition(self, sgr: Union[str, int, List[Union[str, int]]] = None):
        """
        选择图形再现（Select Graphic Rendition）
        """
        self.write(CSISequence.csi_for_select_graphic_redition(sgr))

    def device_status_report(self):
        """
        Reports the cursor position (CPR) by transmitting `ESC[n;mR`, where n is the row and m is the column.)
        """
        self.write(CSISequence.csi_for_device_status_report())

    @staticmethod
    def parse_device_status_report():
        """
        read for the response of `device_status_report`
        """
        x = input()
        matches = re.match(r'\033\[(\d+);(\d+)R', x)
        if matches:
            return matches.group(1), matches.group(2)
        else:
            raise IOError(f'Expected `ESC[n;mR` but `{x}` read.')

    def print_colorful_text(self, text: str, foreground_color: int, background_color: int):
        """
        Since 0.4.14
        """
        self.select_graphic_redition([foreground_color, background_color])
        self.write(text)
        self.select_graphic_redition(ISO6429.SGR_RESET)
