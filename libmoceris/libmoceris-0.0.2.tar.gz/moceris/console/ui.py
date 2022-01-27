import pygame
import moceris.console


class Element:
    """
    一切 UI 控件的虚基类
    """

    def __init__(self, class_name):
        """
        初始化

        :param class_name: 控件的类名，可以为 None，用于更新时对象间的交互
        """
        self.class_name = class_name
        self.rect = pygame.Rect(0, 0, 0, 0)

    def display(self, *args) -> None:
        """
        绘制对象

        :param args: 备用，目前一般为空
        """
        pass

    def register(self, r_border, r_dict, rect) -> None:
        """
        向 Scene 注册本控件，不需要手动调用此函数

        欲重写该函数请参照基类格式

        :param r_border: Scene 或上层 Element 传递的 Border 引用
        :param r_dict:  Scene 或上层 Element 传递的 class_name 字典引用
        :param rect: Scene 或上层 Element 传递的 rect，表示该元素将被限制在此 rect 内绘制（可以直接改 Console.rect 突破）
        """
        self.rect = rect
        if self.class_name is not None:
            if self.class_name in r_dict:
                raise KeyError('class name:{0} existed.'.format(self.class_name))
            else:
                r_dict[self.class_name] = self

    def update(self, *args) -> None:
        """
        更新元素，通过 Scene 调用

        :param args: 用户定义的形参
        """
        pass


class FuncElement(Element):
    """
    对 Element 的简单封装，使用函数指针的方式简化构建，避免大量继承

    构建：提前定义 display 函数和 update 函数，参数为 (self,*args)，即控件指针和用户定义参数，然后在 init 中传入
    """

    def __init__(self, class_name, pt_display, pt_update):
        """
        初始化

        :param class_name: 同基类
        :param pt_display: display 的函数指针
        :param pt_update: update 的函数指针
        """
        Element.__init__(self, class_name)
        self.pt_display = pt_display
        self.pt_update = pt_update

    def display(self, *args):
        if self.pt_display is not None:
            self.pt_display(self, *args)

    def update(self, *args):
        if self.pt_update is not None:
            self.pt_update(self, *args)


class VerticalPanel(Element):
    """
    竖直排版
    """

    def __init__(self, class_name, n_child, s_child, have_border: bool, n_height):
        """
        初始化

        :param class_name: 同基类
        :param n_child: 上方子控件
        :param s_child: 下方子控件
        :param have_border: 是否显示边框
        :param n_height: 上方子控件的高度
        """
        Element.__init__(self, class_name)
        self.n_child = n_child
        self.s_child = s_child
        self.have_border = have_border
        self.n_height = n_height

    def register(self, r_border, r_dict, rect: pygame.Rect):
        self.rect = rect
        if self.have_border:
            r_border.draw_horizontal(self.rect.y + self.n_height, self.rect.x - 1, self.rect.x + self.rect.width + 1)
        self.n_child.register(r_border, r_dict, pygame.Rect(rect.x, rect.y, rect.width, self.n_height))
        self.s_child.register(r_border, r_dict, pygame.Rect(rect.x, rect.y + self.n_height + 1, rect.width,
                                                            rect.height - self.n_height - 1))

    def display(self, *args):
        if self.n_child is not None:
            moceris.console.moprint.rect = self.n_child.rect
            self.n_child.display(*args)
        if self.s_child is not None:
            moceris.console.moprint.rect = self.s_child.rect
            self.s_child.display(*args)


class HorizontalPanel(Element):
    """
    水平排版
    """

    def __init__(self, class_name, w_child, e_child, have_border: bool, w_width):
        """
        初始化

        :param class_name: 同基类
        :param w_child: 左方子控件
        :param e_child: 右方子控件
        :param have_border: 是否显示边框
        :param w_width: 左方子控件宽度
        """
        Element.__init__(self, class_name)
        self.w_child = w_child
        self.e_child = e_child
        self.have_border = have_border
        self.w_width = w_width

    def register(self, r_border, r_dict: dict, rect):
        self.rect = rect
        if self.have_border:
            r_border.draw_vertical(self.rect.x + self.w_width, self.rect.y - 1, self.rect.y + self.rect.height + 1)
        self.w_child.register(r_border, r_dict, pygame.Rect(rect.x, rect.y, self.w_width, rect.height))
        self.e_child.register(r_border, r_dict,
                              pygame.Rect(rect.x + self.w_width + 1, rect.y, rect.width - self.w_width - 1,
                                          rect.height))

    def display(self, *args):
        if self.w_child is not None:
            moceris.console.moprint.rect = self.w_child.rect
            self.w_child.display(*args)
        if self.e_child is not None:
            moceris.console.moprint.rect = self.e_child.rect
            self.e_child.display(*args)


class Scene:
    """
    场景类，将通过读 moceris.console.window 获得窗口大小并铺满全屏

    很傻逼且强制但是不想弄得太开
    """

    def __init__(self, layout):
        from moceris.console import window
        self.width = window.width
        self.height = window.height
        self.layout = layout
        self.element_dict = {}
        from .border import Border
        self.border = Border(self.width, self.height)
        self.layout.register(self.border, self.element_dict, pygame.Rect(0, 0, self.width, self.height))

    def display(self, *args) -> None:
        """
        绘制场景，由外部调用

        :param args: 暂时保留为空
        """
        from moceris.console import moprint
        moprint.default_rect()
        moprint.clear_screen(True)
        if self.layout is not None:
            self.layout.display(args)
        moprint.default_rect()
        self.border.display()

    def update(self, class_name, *args) -> None:
        """
        更新对象，可由外部调用也可用于控件之间传递信息

        :param class_name: 目标控件的类名
        :param args: 用户定义参数
        """
        if class_name not in self.element_dict:
            raise IndexError()
        self.element_dict[class_name].update(*args)

    def get_element(self, class_name) -> Element:
        if class_name not in self.element_dict:
            raise IndexError()
        return self.element_dict[class_name]
