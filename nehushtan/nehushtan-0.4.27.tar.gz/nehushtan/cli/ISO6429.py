class ISO6429:
    """
    Since 0.4.14
    @see https://en.wikipedia.org/wiki/ANSI_escape_code
    """

    # SGR (Select Graphic Rendition) Parameters

    SGR_RESET = 0
    SGR_BOLD = 1
    SGR_FAINT = 2  # 未广泛支持。
    SGR_ITALIC = 3  # 未广泛支持。有时视为反相显示。
    SGR_UNDERLINE = 4
    SGR_SLOW_BLINK = 5
    SGR_RAPID_BLINK = 6  # MS-DOS ANSI.SYS；每分钟150以上；未广泛支持。
    SGR_INVERT = 7
    SGR_HIDE = 8  # 未广泛支持。
    SGR_STRIKE = 9  # 未广泛支持。

    SGR_USE_DEFAULT_FONT = 10
    SGR_USE_FONT_1 = 11
    SGR_USE_FONT_2 = 12
    SGR_USE_FONT_3 = 13
    SGR_USE_FONT_4 = 14
    SGR_USE_FONT_5 = 15
    SGR_USE_FONT_6 = 16
    SGR_USE_FONT_7 = 17
    SGR_USE_FONT_8 = 18
    SGR_USE_FONT_9 = 19
    SGR_BLACKLETTER_FONT = 20  # 几乎无支持。

    SGR_DOUBLY_UNDERLINED = 21
    SGR_NOT_BOLD = 21

    SGR_NORMAL_INTENSITY = 22  # 正常颜色或强度
    SGR_NEITHER_ITALIC_NOR_BLACKLETTER = 23  # 非斜体、非尖角体
    SGR_NOT_UNDERLINED = 24  # 关闭下划线	去掉单双下划线。
    SGR_NOT_BLINKING = 25  # 关闭闪烁
    SGR_NOT_REVERSED = 27  # 关闭反显
    SGR_REVEAL = 28  # 关闭隐藏
    SGR_NOT_STRIKE = 29  # 关闭划除

    # 30–37	设置前景色	参见下面的颜色表。
    # 38	设置前景色	下一个参数是5;n或2;r;g;b，见下。
    # 39	默认前景色	由具体实现定义（按照标准）。

    SGR_SET_FOREGROUND_COLOR = 38

    SGR_FOREGROUND_COLOR_BLACK = 30
    SGR_FOREGROUND_COLOR_RED = 31
    SGR_FOREGROUND_COLOR_GREEN = 32
    SGR_FOREGROUND_COLOR_YELLOW = 33
    SGR_FOREGROUND_COLOR_BLUE = 34
    SGR_FOREGROUND_COLOR_MAGENTA = 35
    SGR_FOREGROUND_COLOR_CYAN = 36
    SGR_FOREGROUND_COLOR_WHITE = 37

    SGR_DEFAULT_FOREGROUND_COLOR = 39

    # 40–47	设置背景色	参见下面的颜色表。
    # 48	设置背景色	下一个参数是5;n或2;r;g;b，见下。
    # 49	默认背景色	由具体实现定义（按照标准）。

    SGR_Set_background_color = 48

    SGR_BACKGROUND_COLOR_BLACK = 40
    SGR_BACKGROUND_COLOR_RED = 41
    SGR_BACKGROUND_COLOR_GREEN = 42
    SGR_BACKGROUND_COLOR_YELLOW = 43
    SGR_BACKGROUND_COLOR_BLUE = 44
    SGR_BACKGROUND_COLOR_MAGENTA = 45
    SGR_BACKGROUND_COLOR_CYAN = 46
    SGR_BACKGROUND_COLOR_WHITE = 47

    SGR_DEFAULT_background_COLOR = 49

    # Implemented as "emoji variation selector" in mintty.
    # see https://github.com/mintty/mintty/wiki/Tips#text-attributes-and-rendering
    SGR_FRAMED = 51
    SGR_ENCIRCLED = 52
    SGR_NOT_FRAMED_OR_ENCIRCLED = 54

    SGR_OVERLINED = 53  # 上划线
    SGR_NOT_OVERLINED = 55  # 关闭上划线
