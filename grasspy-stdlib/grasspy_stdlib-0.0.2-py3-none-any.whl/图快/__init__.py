"""Tcl/Tk 的功能封装, 简单直观的图形编程 (GUI) 模块. 英文名为 tkinter.

使用 GUI 可实现很多直观的功能. 比如想开发一个计算器，有一个图形化的小窗口就是非常必要的。

对于图形编程，可以用两个比喻来理解：
第一个，作画。我们都见过美术生写生的情景，先支一个画架，放上画板，蒙上画布，构思内容，用铅笔画草图，组织结构和比例，调色板调色，最后画笔勾勒。
相应的，对应到图形编程，我们的显示屏就是支起来的画架，根窗体就是画板，在tkinter中则是顶级窗口 (Toplevel)，画布就是 tkinter 中的容器 (Frame)，
画板上可以放很多张画布 (Canvas)，tkinter 中的容器中也可以放很多个容器，绘画中的构图布局则是 tkinter 中的布局管理器（几何管理器），
绘画的内容就是 tkinter 中的一个个小组件，一幅画由许多元素构成，而我们的 GUI 界面，就是由一个个组件拼装起来的，它们就是 widget。
第二个，我们小时候都玩过积木，只要发挥创意，相同的积木可以堆出各种造型。tkinter 的组件也可以看做一个个积木，形状或许不同，其本质都是一样的，
就是一个积木，不管它长什么样子，它始终就是积木！

顶层积木是 <〇主窗口> 和 <〇顶级窗口>, 其他积木有: <〇框架>, <〇标签>, <〇输入框>, <〇文本框>, <〇画布>, <〇按钮>, <〇单选按钮>, <〇复选按钮>,
<〇刻度条>, <〇列表框>, <〇滚动条>, <〇选项菜单>, <〇旋钮控件>, <〇标签框架>, <〇菜单> 和 <〇格窗>.

各种积木的布局方法有三种: 常规布局, 网格布局, 位置布局.

积木的属性可用关键词参数指定.

动作通过资源 (例如关键词参数 '命令') 或 '绑定' 方法绑定到事件.

示例:
导入 图快
窗口 = 图快.〇主窗口()
框架 = 图快.〇框架(窗口, 边框宽度=2)
框架.常规布局(填充='同时',扩展=1)
标签 = 图快.〇标签(框架, 文本="小美 你吃了吗")
标签.常规布局(填充='x', 扩展=1)
按钮 = 图快.〇按钮(框架, 文本="退出", 命令=窗口.销毁)
按钮.常规布局(边='底边')
窗口.主循环()
"""

import enum
import sys

import _tkinter # If this fails your Python may not be configured for Tk
TclError = _tkinter.TclError
from .constants import *
import re

导入 tkinter
导入 图快.messagebox 为 _msgbox
从 .通用字典 导入 _锚点字典, _部件通用选项字典, _部件通用选项值字典, \
    _颜色字典, _对齐字典, _边框样式字典, _验证字典, _菜单配置选项字典
从 汉化通用 导入 _关键词参数中转英, _星号参数中转英

wantobjects = 1

TkVersion = float(_tkinter.TK_VERSION)
TclVersion = float(_tkinter.TCL_VERSION)

READABLE = _tkinter.READABLE
WRITABLE = _tkinter.WRITABLE
EXCEPTION = _tkinter.EXCEPTION


_magic_re = re.compile(r'([\\{}])')
_space_re = re.compile(r'([\s])', re.ASCII)


def _join(value):
    """Internal function."""
    return ' '.join(map(_stringify, value))


def _stringify(value):
    """Internal function."""
    if isinstance(value, (list, tuple)):
        if len(value) == 1:
            value = _stringify(value[0])
            if _magic_re.search(value):
                value = '{%s}' % value
        else:
            value = '{%s}' % _join(value)
    else:
        value = str(value)
        if not value:
            value = '{}'
        elif _magic_re.search(value):
            # add '\' before special characters and spaces
            value = _magic_re.sub(r'\\\1', value)
            value = value.replace('\n', r'\n')
            value = _space_re.sub(r'\\\1', value)
            if value[0] == '"':
                value = '\\' + value
        elif value[0] == '"' or _space_re.search(value):
            value = '{%s}' % value
    return value


def _flatten(seq):
    """Internal function."""
    res = ()
    for item in seq:
        if isinstance(item, (tuple, list)):
            res = res + _flatten(item)
        elif item is not None:
            res = res + (item,)
    return res


try: _flatten = _tkinter._flatten
except AttributeError: pass


def _cnfmerge(cnfs):
    """Internal function."""
    if isinstance(cnfs, dict):
        return cnfs
    elif isinstance(cnfs, (type(None), str)):
        return cnfs
    else:
        cnf = {}
        for c in _flatten(cnfs):
            try:
                cnf.update(c)
            except (AttributeError, TypeError) as msg:
                print("_cnfmerge: fallback due to:", msg)
                for k, v in c.items():
                    cnf[k] = v
        return cnf


try: _cnfmerge = _tkinter._cnfmerge
except AttributeError: pass


def _splitdict(tk, v, cut_minus=True, conv=None):
    """Return a properly formatted dict built from Tcl list pairs.

    If cut_minus is True, the supposed '-' prefix will be removed from
    keys. If conv is specified, it is used to convert values.

    Tcl list is expected to contain an even number of elements.
    """
    t = tk.splitlist(v)
    if len(t) % 2:
        raise RuntimeError('代表字典的 Tcl 列表应当包含偶数个元素')
    it = iter(t)
    dict = {}
    for key, value in zip(it, it):
        key = str(key)
        if cut_minus and key[0] == '-':
            key = key[1:]
        if conv:
            value = conv(value)
        dict[key] = value
    return dict


class EventType(str, enum.Enum):
    KeyPress = '2'
    Key = KeyPress,
    KeyRelease = '3'
    ButtonPress = '4'
    Button = ButtonPress,
    ButtonRelease = '5'
    Motion = '6'
    Enter = '7'
    Leave = '8'
    FocusIn = '9'
    FocusOut = '10'
    Keymap = '11'           # undocumented
    Expose = '12'
    GraphicsExpose = '13'   # undocumented
    NoExpose = '14'         # undocumented
    Visibility = '15'
    Create = '16'
    Destroy = '17'
    Unmap = '18'
    Map = '19'
    MapRequest = '20'
    Reparent = '21'
    Configure = '22'
    ConfigureRequest = '23'
    Gravity = '24'
    ResizeRequest = '25'
    Circulate = '26'
    CirculateRequest = '27'
    Property = '28'
    SelectionClear = '29'   # undocumented
    SelectionRequest = '30' # undocumented
    Selection = '31'        # undocumented
    Colormap = '32'
    ClientMessage = '33'    # undocumented
    Mapping = '34'          # undocumented
    VirtualEvent = '35',    # undocumented
    Activate = '36',
    Deactivate = '37',
    MouseWheel = '38',

    def __str__(self):
        return self.name


class Event:
    """事件属性的容器.

    如果发生下列事件之一, 就会生成此类型的实例:

    KeyPress, KeyRelease - 键盘事件
    ButtonPress, ButtonRelease, Motion, Enter, Leave, MouseWheel - for mouse events
    Visibility, Unmap, Map, Expose, FocusIn, FocusOut, Circulate,
    Colormap, Gravity, Reparent, Property, Destroy, Activate,
    Deactivate - 窗口事件

    If a callback function for one of these events is registered
    using bind, bind_all, bind_class, or tag_bind, the callback is
    called with an Event as first argument. It will have the
    following attributes (in braces are the event types for which
    the attribute is valid):

        serial - serial number of event
    num - mouse button pressed (ButtonPress, ButtonRelease)
    focus - whether the window has the focus (Enter, Leave)
    height - height of the exposed window (Configure, Expose)
    width - width of the exposed window (Configure, Expose)
    keycode - keycode of the pressed key (KeyPress, KeyRelease)
    state - state of the event as a number (ButtonPress, ButtonRelease,
                            Enter, KeyPress, KeyRelease,
                            Leave, Motion)
    state - state as a string (Visibility)
    time - when the event occurred
    x - x-position of the mouse
    y - y-position of the mouse
    x_root - x-position of the mouse on the screen
             (ButtonPress, ButtonRelease, KeyPress, KeyRelease, Motion)
    y_root - y-position of the mouse on the screen
             (ButtonPress, ButtonRelease, KeyPress, KeyRelease, Motion)
    char - pressed character (KeyPress, KeyRelease)
    send_event - see X/Windows documentation
    keysym - keysym of the event as a string (KeyPress, KeyRelease)
    keysym_num - keysym of the event as a number (KeyPress, KeyRelease)
    type - type of the event as a number
    widget - widget in which the event occurred
    delta - delta of wheel movement (MouseWheel)
    """

    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if v != '??'}
        if not self.char:
            del attrs['char']
        elif self.char != '??':
            attrs['char'] = repr(self.char)
        if not getattr(self, 'send_event', True):
            del attrs['send_event']
        if self.state == 0:
            del attrs['state']
        elif isinstance(self.state, int):
            state = self.state
            mods = ('Shift', 'Lock', 'Control',
                    'Mod1', 'Mod2', 'Mod3', 'Mod4', 'Mod5',
                    'Button1', 'Button2', 'Button3', 'Button4', 'Button5')
            s = []
            for i, n in enumerate(mods):
                if state & (1 << i):
                    s.append(n)
            state = state & ~((1<< len(mods)) - 1)
            if state or not s:
                s.append(hex(state))
            attrs['state'] = '|'.join(s)
        if self.delta == 0:
            del attrs['delta']
        # widget usually is known
        # serial and time are not very interesting
        # keysym_num duplicates keysym
        # x_root and y_root mostly duplicate x and y
        keys = ('send_event',
                'state', 'keysym', 'keycode', 'char',
                'num', 'delta', 'focus',
                'x', 'y', 'width', 'height')
        return '<%s event%s>' % (
            self.type,
            ''.join(' %s=%s' % (k, attrs[k]) for k in keys if k in attrs)
        )

事件类 = Event

_support_default_root = 1
_default_root = None


def NoDefaultRoot():
    """Inhibit setting of default root window.

    Call this function to inhibit that the first instance of
    Tk is used for windows without an explicit parent window.
    """
    global _support_default_root
    _support_default_root = 0
    global _default_root
    _default_root = None
    del _default_root

套路 无默认根窗口():
    """禁止设置默认根窗口.

    调用此函数将禁止 〇主窗口 的第一个实例用于无明示父窗口的窗口.
    """
    global _support_default_root
    _support_default_root = 0
    global _default_root
    _default_root = None
    del _default_root

def _tkerror(err):
    """Internal function."""
    pass


def _exit(code=0):
    """Internal function. Calling it will raise the exception SystemExit."""
    try:
        code = int(code)
    except ValueError:
        pass
    raise SystemExit(code)


_varnum = 0


class Variable:
    """Class to define value holders for e.g. buttons.

    Subclasses StringVar, IntVar, DoubleVar, BooleanVar are specializations
    that constrain the type of the value returned from get()."""
    _default = ""
    _tk = None
    _tclCommands = None

    def __init__(self, master=None, value=None, name=None):
        """Construct a variable

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to "")
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        # check for type of NAME parameter to override weird error message
        # raised from Modules/_tkinter.c:SetVar like:
        # TypeError: setvar() takes exactly 3 arguments (2 given)
        if name is not None and not isinstance(name, str):
            raise TypeError("名称须为字符串")
        global _varnum
        if not master:
            master = _default_root
        self._root = master._root()
        self._tk = master.tk
        if name:
            self._name = name
        else:
            self._name = 'PY_VAR' + repr(_varnum)
            _varnum += 1
        if value is not None:
            self.initialize(value)
        elif not self._tk.getboolean(self._tk.call("info", "exists", self._name)):
            self.initialize(self._default)

    def __del__(self):
        """Unset the variable in Tcl."""
        if self._tk is None:
            return
        if self._tk.getboolean(self._tk.call("info", "exists", self._name)):
            self._tk.globalunsetvar(self._name)
        if self._tclCommands is not None:
            for name in self._tclCommands:
                #print '- Tkinter: deleted command', name
                self._tk.deletecommand(name)
            self._tclCommands = None

    def __str__(self):
        """Return the name of the variable in Tcl."""
        return self._name

    def set(self, value):
        """Set the variable to VALUE."""
        return self._tk.globalsetvar(self._name, value)

    initialize = set

    套路 设置(分身, 值):
        """将变量设置为 '值'."""
        返回 分身._tk.globalsetvar(分身._name, 值)

    初始化 = 设置

    def get(self):
        """Return value of variable."""
        return self._tk.globalgetvar(self._name)

    套路 获取(分身):
        """返回变量的值."""
        返回 分身._tk.globalgetvar(分身._name)

    def _register(self, callback):
        f = CallWrapper(callback, None, self._root).__call__
        cbname = repr(id(f))
        try:
            callback = callback.__func__
        except AttributeError:
            pass
        try:
            cbname = cbname + callback.__name__
        except AttributeError:
            pass
        self._tk.createcommand(cbname, f)
        if self._tclCommands is None:
            self._tclCommands = []
        self._tclCommands.append(cbname)
        return cbname

    def trace_add(self, mode, callback):
        """Define a trace callback for the variable.

        Mode is one of "read", "write", "unset", or a list or tuple of
        such strings.
        Callback must be a function which is called when the variable is
        read, written or unset.

        Return the name of the callback.
        """
        cbname = self._register(callback)
        self._tk.call('trace', 'add', 'variable',
                      self._name, mode, (cbname,))
        return cbname

    套路 跟踪_添加(分身, 模式, 回调):
        """为变量定义一个跟踪回调函数.

        '模式' 为 "读"、"写"、"取消设置", 或由这些字符串组成的列表或元素.
        '回调' 须为一个函数, 当读取、写入或取消设置变量时调用.

        返回回调函数的名称.
        """
        返回 分身.trace_add(模式, 回调)

    def trace_remove(self, mode, cbname):
        """Delete the trace callback for a variable.

        Mode is one of "read", "write", "unset" or a list or tuple of
        such strings.  Must be same as were specified in trace_add().
        cbname is the name of the callback returned from trace_add().
        """
        self._tk.call('trace', 'remove', 'variable',
                      self._name, mode, cbname)
        for m, ca in self.trace_info():
            if self._tk.splitlist(ca)[0] == cbname:
                break
        else:
            self._tk.deletecommand(cbname)
            try:
                self._tclCommands.remove(cbname)
            except ValueError:
                pass

    套路 跟踪_移除(分身, 模式, 回调名称):
        """删除变量的跟踪回调函数.

        '模式' 为 "读"、"写"、"取消设置", 或由这些字符串组成的列表或元素.
        必须与 '跟踪_添加()' 指定的相同.
        回调名称为 '跟踪_添加()' 返回的回调函数名称.
        """
        分身.trace_remove(模式, 回调名称)

    def trace_info(self):
        """Return all trace callback information."""
        splitlist = self._tk.splitlist
        return [(splitlist(k), v) for k, v in map(splitlist,
            splitlist(self._tk.call('trace', 'info', 'variable', self._name)))]

    套路 跟踪_信息(分身):
        """返回所有跟踪回调信息."""
        返回 分身.trace_info()

    def trace_variable(self, mode, callback):
        """Define a trace callback for the variable.

        MODE is one of "r", "w", "u" for read, write, undefine.
        CALLBACK must be a function which is called when
        the variable is read, written or undefined.

        Return the name of the callback.

        This deprecated method wraps a deprecated Tcl method that will
        likely be removed in the future.  Use trace_add() instead.
        """
        # TODO: Add deprecation warning
        cbname = self._register(callback)
        self._tk.call("trace", "variable", self._name, mode, cbname)
        return cbname

    trace = trace_variable

    def trace_vdelete(self, mode, cbname):
        """Delete the trace callback for a variable.

        MODE is one of "r", "w", "u" for read, write, undefine.
        CBNAME is the name of the callback returned from trace_variable or trace.

        This deprecated method wraps a deprecated Tcl method that will
        likely be removed in the future.  Use trace_remove() instead.
        """
        # TODO: Add deprecation warning
        self._tk.call("trace", "vdelete", self._name, mode, cbname)
        cbname = self._tk.splitlist(cbname)[0]
        for m, ca in self.trace_info():
            if self._tk.splitlist(ca)[0] == cbname:
                break
        else:
            self._tk.deletecommand(cbname)
            try:
                self._tclCommands.remove(cbname)
            except ValueError:
                pass

    def trace_vinfo(self):
        """Return all trace callback information.

        This deprecated method wraps a deprecated Tcl method that will
        likely be removed in the future.  Use trace_info() instead.
        """
        # TODO: Add deprecation warning
        return [self._tk.splitlist(x) for x in self._tk.splitlist(
            self._tk.call("trace", "vinfo", self._name))]

    def __eq__(self, other):
        """Comparison for equality (==).

        Note: if the Variable's master matters to behavior
        also compare self._master == other._master
        """
        return self.__class__.__name__ == other.__class__.__name__ \
            and self._name == other._name

类 〇变量(Variable):
    """为按钮等对象定义值容器的类.

    '〇字符串型变量'、'〇整型变量'、'〇双精度变量'、'〇布尔型变量' 是对 '获取()'
    方法返回的值类型有约束的专门子类.
    """
    套路 __init__(分身, 主对象=空, 值=空, 名称=空):
        """构造一个变量

        '主对象' 可以是主部件.
        '值' 为可选值 (默认为 "")
        '名称' 为可选 Tcl 名称 (默认为 PY_VARnum).

        如果 '名称' 匹配一个现有变量且 '值' 未给出, 则保留现有值.
        """
        super().__init__(master=主对象, value=值, name=名称)

class StringVar(Variable):
    """Value holder for strings variables."""
    _default = ""

    def __init__(self, master=None, value=None, name=None):
        """Construct a string variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to "")
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        Variable.__init__(self, master, value, name)

    def get(self):
        """变量的值以字符串返回."""
        value = self._tk.globalgetvar(self._name)
        if isinstance(value, str):
            return value
        return str(value)

    获取 = get

类 〇字符串型变量(StringVar):
    """字符串变量的值容器"""
    套路 __init__(分身, 主对象=空, 值=空, 名称=空):
        """构造一个字符串变量

        '主对象' 可以是主部件.
        '值' 为可选值 (默认为 "")
        '名称' 为可选 Tcl 名称 (默认为 PY_VARnum).

        如果 '名称' 匹配一个现有变量且 '值' 未给出, 则保留现有值.
        """
        StringVar.__init__(分身, master=主对象, value=值, name=名称)

class IntVar(Variable):
    """Value holder for integer variables."""
    _default = 0

    def __init__(self, master=None, value=None, name=None):
        """Construct an integer variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        Variable.__init__(self, master, value, name)

    def get(self):
        """变量的值以整数返回."""
        value = self._tk.globalgetvar(self._name)
        try:
            return self._tk.getint(value)
        except (TypeError, TclError):
            return int(self._tk.getdouble(value))

    获取 = get

类 〇整型变量(IntVar):
    """整型变量的值容器"""
    套路 __init__(分身, 主对象=空, 值=空, 名称=空):
        """构造一个整型变量

        '主对象' 可以是主部件.
        '值' 为可选值 (默认为 0)
        '名称' 为可选 Tcl 名称 (默认为 PY_VARnum).

        如果 '名称' 匹配一个现有变量且 '值' 未给出, 则保留现有值.
        """
        IntVar.__init__(分身, master=主对象, value=值, name=名称)

class DoubleVar(Variable):
    """Value holder for float variables."""
    _default = 0.0

    def __init__(self, master=None, value=None, name=None):
        """Construct a float variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0.0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        Variable.__init__(self, master, value, name)

    def get(self):
        """变量的值以浮点数返回."""
        return self._tk.getdouble(self._tk.globalgetvar(self._name))

    获取 = get

类 〇双精度变量(DoubleVar):
    """浮点变量的值容器"""
    套路 __init__(分身, 主对象=空, 值=空, 名称=空):
        """构造一个浮点变量

        '主对象' 可以是主部件.
        '值' 为可选值 (默认为 0.0)
        '名称' 为可选 Tcl 名称 (默认为 PY_VARnum).

        如果 '名称' 匹配一个现有变量且 '值' 未给出, 则保留现有值.
        """
        DoubleVar.__init__(分身, master=主对象, value=值, name=名称)

class BooleanVar(Variable):
    """Value holder for boolean variables."""
    _default = False

    def __init__(self, master=None, value=None, name=None):
        """Construct a boolean variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to False)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        Variable.__init__(self, master, value, name)

    def set(self, value):
        """Set the variable to VALUE."""
        return self._tk.globalsetvar(self._name, self._tk.getboolean(value))

    initialize = set

    def 设置(self, 值):
        """将变量设置为 '值'."""
        return self._tk.globalsetvar(self._name, self._tk.getboolean(值))

    初始化 = 设置

    def get(self):
        """变量的值以布尔值返回."""
        try:
            return self._tk.getboolean(self._tk.globalgetvar(self._name))
        except TclError:
            raise ValueError("getboolean() 的字面值无效")

    获取 = get

类 〇布尔型变量(BooleanVar):
    """布尔型变量的值容器"""
    套路 __init__(分身, 主对象=空, 值=空, 名称=空):
        """构造一个布尔型变量

        '主对象' 可以是主部件.
        '值' 为可选值 (默认为 假)
        '名称' 为可选 Tcl 名称 (默认为 PY_VARnum).

        如果 '名称' 匹配一个现有变量且 '值' 未给出, 则保留现有值.
        """
        BooleanVar.__init__(分身, master=主对象, value=值, name=名称)

def mainloop(n=0):
    """Run the main loop of Tcl."""
    _default_root.tk.mainloop(n)

def 主循环(n=0):
    """运行 Tcl 的主循环."""
    _default_root.tk.mainloop(n)

getint = int

getdouble = float


def getboolean(s):
    """Convert true and false to integer values 1 and 0."""
    try:
        return _default_root.tk.getboolean(s)
    except TclError:
        raise ValueError("invalid literal for getboolean()")


# Methods defined on both toplevel and interior widgets

class Misc:
    """Internal class.

    Base class which defines methods common for interior widgets."""

    # used for generating child widget names
    _last_child_ids = None

    # XXX font command?
    _tclCommands = None

    def destroy(self):
        """内部函数.

        删除 Tcl 解释器中为此部件创建的所有 Tcl 命令.
        """
        if self._tclCommands is not None:
            for name in self._tclCommands:
                #print '- Tkinter: deleted command', name
                self.tk.deletecommand(name)
            self._tclCommands = None
    
    销毁 = destroy

    def deletecommand(self, name):
        """Internal function.

        Delete the Tcl command provided in NAME."""
        #print '- Tkinter: deleted command', name
        self.tk.deletecommand(name)
        try:
            self._tclCommands.remove(name)
        except ValueError:
            pass

    套路 删除命令(分身, 名称):
        """内部函数.

        删除 '名称' 提供的 Tcl 命令."""
        分身.deletecommand(名称)

    def tk_strictMotif(self, boolean=None):
        """Set Tcl internal variable, whether the look and feel
        should adhere to Motif.

        A parameter of 1 means adhere to Motif (e.g. no color
        change if mouse passes over slider).
        Returns the set value."""
        return self.tk.getboolean(self.tk.call(
            'set', 'tk_strictMotif', boolean))

    def tk_bisque(self):
        """Change the color scheme to light brown as used in Tk 3.6 and before."""
        self.tk.call('tk_bisque')

    def tk_setPalette(self, *args, **kw):
        """Set a new color scheme for all widget elements.

        A single color as argument will cause that all colors of Tk
        widget elements are derived from this.
        Alternatively several keyword parameters and its associated
        colors can be given. The following keywords are valid:
        activeBackground, foreground, selectColor,
        activeForeground, highlightBackground, selectBackground,
        background, highlightColor, selectForeground,
        disabledForeground, insertBackground, troughColor."""
        self.tk.call(('tk_setPalette',)
              + _flatten(args) + _flatten(list(kw.items())))

    def wait_variable(self, name='PY_VAR'):
        """Wait until the variable is modified.

        A parameter of type IntVar, StringVar, DoubleVar or
        BooleanVar must be given."""
        self.tk.call('tkwait', 'variable', name)
    waitvar = wait_variable # XXX b/w compat

    套路 等待变量修改(分身, 名称='PY_VAR'):
        """等待变量被修改.

        必须指定整型变量、字符串型变量、双精度变量或布尔型变量的参数.
        """
        分身.wait_variable(名称)

    def wait_window(self, window=None):
        """Wait until a WIDGET is destroyed.

        If no parameter is given self is used."""
        if window is None:
            window = self
        self.tk.call('tkwait', 'window', window._w)

    套路 等待部件销毁(分身, 窗口=空):
        """等待一个部件被销毁.

        如果没有指定参数，则使用自身."""
        分身.wait_window(窗口)

    def wait_visibility(self, window=None):
        """Wait until the visibility of a WIDGET changes
        (e.g. it appears).

        If no parameter is given self is used."""
        if window is None:
            window = self
        self.tk.call('tkwait', 'visibility', window._w)

    套路 等待可见性变化(分身, 窗口=空):
        """等待一个部件的可见性发生变化 (例如出现).

        如果没有指定参数，则使用自身."""
        分身.wait_visibility(窗口)

    def setvar(self, name='PY_VAR', value='1'):
        """Set Tcl variable NAME to VALUE."""
        self.tk.setvar(name, value)

    套路 设置变量(分身, 名称='PY_VAR', 值='1'):
        """将 Tcl 变量 '名称' 设置为 '值'."""
        分身.setvar(name=名称, value=值)

    def getvar(self, name='PY_VAR'):
        """Return value of Tcl variable NAME."""
        return self.tk.getvar(name)

    套路 获取变量(分身, 名称='PY_VAR'):
        """返回 Tcl 变量 '名称' 的值."""
        返回 分身.getvar(名称)

    def getint(self, s):
        try:
            return self.tk.getint(s)
        except TclError as exc:
            raise ValueError(str(exc))

    def getdouble(self, s):
        try:
            return self.tk.getdouble(s)
        except TclError as exc:
            raise ValueError(str(exc))

    def getboolean(self, s):
        """Return a boolean value for Tcl boolean values true and false given as parameter."""
        try:
            return self.tk.getboolean(s)
        except TclError:
            raise ValueError("invalid literal for getboolean()")

    def focus_set(self):
        """将输入焦点赋予此部件.

        如果应用程序当前没有焦点，则当它通过窗口管理器获得焦点时，
        此部件将获得焦点."""
        self.tk.call('focus', self._w)
    focus = focus_set # XXX b/w compat?

    焦点 = 设置焦点 = focus_set

    def focus_force(self):
        """将输入焦点赋予此部件，无论应用程序有无焦点。谨慎使用！"""
        self.tk.call('focus', '-force', self._w)

    抢夺焦点 = focus_force

    def focus_get(self):
        """返回应用程序中当前有焦点的部件.

        如果应用程序当前没有焦点，返回空。
        Use focus_displayof to allow working with several displays.
        """
        name = self.tk.call('focus')
        if name == 'none' or not name: return None
        return self._nametowidget(name)

    焦点部件 = focus_get

    def focus_displayof(self):
        """返回与此部件相同的显示区域上当前有焦点的窗口 (也是部件?).

        如果应用程序当前没有焦点，返回空。"""
        name = self.tk.call('focus', '-displayof', self._w)
        if name == 'none' or not name: return None
        return self._nametowidget(name)

    焦点窗口 = focus_displayof # 依据 tkinter.pdf 的注释

    def focus_lastfor(self):
        """返回包含此部件的顶级窗口中上次拥有输入焦点的部件，或者当
        顶级窗口获得焦点时将拥有焦点的部件."""
        name = self.tk.call('focus', '-lastfor', self._w)
        if name == 'none' or not name: return None
        return self._nametowidget(name)

    上次焦点 = focus_lastfor # 依据 tkinter.pdf 的注释

    def tk_focusFollowsMouse(self):
        """鼠标下的部件将自动获得焦点。无法轻易禁用"""
        self.tk.call('tk_focusFollowsMouse')

    焦点跟随鼠标_tk = tk_focusFollowsMouse

    def tk_focusNext(self):
        """返回焦点遍历顺序中在此部件之后拥有焦点的部件.

        The focus order first goes to the next child, then to
        the children of the child recursively and then to the
        next sibling which is higher in the stacking order.  A
        widget is omitted if it has the takefocus resource set
        to 0."""
        name = self.tk.call('tk_focusNext', self._w)
        if not name: return None
        return self._nametowidget(name)

    下一焦点_tk = tk_focusNext

    def tk_focusPrev(self):
        """返回焦点遍历顺序中在此部件之前拥有焦点的部件.
        See tk_focusNext for details."""
        name = self.tk.call('tk_focusPrev', self._w)
        if not name: return None
        return self._nametowidget(name)

    上一焦点_tk = tk_focusPrev

    def after(self, ms, func=None, *args):
        """Call function once after given time.

        MS specifies the time in milliseconds. FUNC gives the
        function which shall be called. Additional parameters
        are given as parameters to the function call.  Return
        identifier to cancel scheduling with after_cancel."""
        if not func:
            # I'd rather use time.sleep(ms*0.001)
            self.tk.call('after', ms)
            return None
        else:
            def callit():
                try:
                    func(*args)
                finally:
                    try:
                        self.deletecommand(name)
                    except TclError:
                        pass
            callit.__name__ = func.__name__
            name = self._register(callit)
            return self.tk.call('after', ms, name)

    套路 之后(分身, 毫秒数, 函数=空, *参数):
        """在给定时间后调用指定函数一次.

        返回一个 ID，'之后_取消' 使用该 ID 取消预定计划."""
        返回 分身.after(毫秒数, 函数, *参数)

    def after_idle(self, func, *args):
        """Call FUNC once if the Tcl main loop has no event to
        process.

        Return an identifier to cancel the scheduling with
        after_cancel."""
        return self.after('idle', func, *args)

    套路 空闲后(分身, 函数, *参数):
        """当 Tcl 主循环没有事件要处理时，调用指定函数一次.

        返回一个 ID，'之后_取消' 使用该 ID 取消预定计划."""
        返回 分身.after_idle(函数, *参数)

    def after_cancel(self, id):
        """取消 id 所代表的函数的预定计划.

        须将 '之后' 或 '空闲后' 返回的 id 作为第一个参数.
        """
        if not id:
            raise ValueError("id 必须为 'after' 或 'after_idle' 返回的有效 id")
        try:
            data = self.tk.call('after', 'info', id)
            script = self.tk.splitlist(data)[0]
            self.deletecommand(script)
        except TclError:
            pass
        self.tk.call('after', 'cancel', id)

    之后_取消 = after_cancel

    def bell(self, displayof=0):
        """Ring a display's bell."""
        self.tk.call(('bell',) + self._displayof(displayof))

    套路 响铃(分身, 显示区=0):
        """发出哔哔声."""
        分身.bell(显示)

    # Clipboard handling:
    def clipboard_get(self, **kw):
        """Retrieve data from the clipboard on window's display.

        The window keyword defaults to the root window of the Tkinter
        application.

        The type keyword specifies the form in which the data is
        to be returned and should be an atom name such as STRING
        or FILE_NAME.  Type defaults to STRING, except on X11, where the default
        is to try UTF8_STRING and fall back to STRING.

        This command is equivalent to:

        selection_get(CLIPBOARD)
        """
        if 'type' not in kw and self._windowingsystem == 'x11':
            try:
                kw['type'] = 'UTF8_STRING'
                return self.tk.call(('clipboard', 'get') + self._options(kw))
            except TclError:
                del kw['type']
        return self.tk.call(('clipboard', 'get') + self._options(kw))

    套路 获取剪贴板(分身, **关键词参数):
        """从剪贴板中获取窗口显示区的数据.

        关键词 '窗口' 默认为 Tkinter 应用程序的根窗口.

        关键词 '类型' 指定要返回的数据形式，应当是 STRING
        或 FILE_NAME 等原子名称， 默认值为 STRING.

        此命令等效于:

        selection_get(CLIPBOARD)
        """
        如果 窗口 在 关键词参数:
            关键词参数['window'] = 关键词参数['窗口']
            删  关键词参数['窗口']
        如果 类型 在 关键词参数:
            关键词参数['type'] = 关键词参数['类型']
            删  关键词参数['类型']
        返回 分身.clipboard_get(**关键词参数)

    def clipboard_clear(self, **kw):
        """Clear the data in the Tk clipboard.

        A widget specified for the optional displayof keyword
        argument specifies the target display."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        self.tk.call(('clipboard', 'clear') + self._options(kw))

    套路 清除剪贴板(分身, **关键词参数):
        """清除 Tk 剪贴板中的数据.

        可选关键词参数 '显示区' 指定的部件指定目标显示区."""
        如果 显示区 在 关键词参数:
            关键词参数['displayof'] = 关键词参数['显示区']
            删  关键词参数['显示区']
        分身.clipboard_clear(**关键词参数)

    def clipboard_append(self, string, **kw):
        """Append STRING to the Tk clipboard.

        A widget specified at the optional displayof keyword
        argument specifies the target display. The clipboard
        can be retrieved with selection_get."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        self.tk.call(('clipboard', 'append') + self._options(kw)
              + ('--', string))

    套路 追加剪贴板(分身, 字符串, **关键词参数):
        """将给定 '字符串' 追加到 Tk 剪贴板.

        可选关键词参数 '显示区' 指定的部件指定目标显示区.
        可利用 '获取选定内容' 获取剪贴板数据."""
        如果 显示区 在 关键词参数:
            关键词参数['displayof'] = 关键词参数['显示区']
            删  关键词参数['显示区']
        分身.clipboard_append(字符串, **关键词参数)
    # XXX grab current w/o window argument

    def grab_current(self):
        """Return widget which has currently the grab in this application
        or None."""
        name = self.tk.call('grab', 'current', self._w)
        if not name: return None
        return self._nametowidget(name)

    def grab_release(self):
        """Release grab for this widget if currently set."""
        self.tk.call('grab', 'release', self._w)

    def grab_set(self):
        """Set grab for this widget.

        A grab directs all events to this and descendant
        widgets in the application."""
        self.tk.call('grab', 'set', self._w)

    def grab_set_global(self):
        """Set global grab for this widget.

        A global grab directs all events to this and
        descendant widgets on the display. Use with caution -
        other applications do not get events anymore."""
        self.tk.call('grab', 'set', '-global', self._w)

    def grab_status(self):
        """Return None, "local" or "global" if this widget has
        no, a local or a global grab."""
        status = self.tk.call('grab', 'status', self._w)
        if status == 'none': status = None
        return status

    def option_add(self, pattern, value, priority = None):
        """Set a VALUE (second parameter) for an option
        PATTERN (first parameter).

        An optional third parameter gives the numeric priority
        (defaults to 80)."""
        self.tk.call('option', 'add', pattern, value, priority)

    def option_clear(self):
        """Clear the option database.

        It will be reloaded if option_add is called."""
        self.tk.call('option', 'clear')

    def option_get(self, name, className):
        """Return the value for an option NAME for this widget
        with CLASSNAME.

        Values with higher priority override lower values."""
        return self.tk.call('option', 'get', self._w, name, className)

    def option_readfile(self, fileName, priority = None):
        """Read file FILENAME into the option database.

        An optional second parameter gives the numeric
        priority."""
        self.tk.call('option', 'readfile', fileName, priority)

    def selection_clear(self, **kw):
        """Clear the current X selection."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        self.tk.call(('selection', 'clear') + self._options(kw))

    套路 选定内容_清除(分身, **关键词参数):
        """清除当前选定内容"""
        分身.selection_clear(**关键词参数)

    def selection_get(self, **kw):
        """Return the contents of the current X selection.

        A keyword parameter selection specifies the name of
        the selection and defaults to PRIMARY.  A keyword
        parameter displayof specifies a widget on the display
        to use. A keyword parameter type specifies the form of data to be
        fetched, defaulting to STRING except on X11, where UTF8_STRING is tried
        before STRING."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        if 'type' not in kw and self._windowingsystem == 'x11':
            try:
                kw['type'] = 'UTF8_STRING'
                return self.tk.call(('selection', 'get') + self._options(kw))
            except TclError:
                del kw['type']
        return self.tk.call(('selection', 'get') + self._options(kw))

    套路 选定内容_获取(分身, **关键词参数):
        """返回当前选定内容"""
        返回 分身.selection_get(**关键词参数)

    def selection_handle(self, command, **kw):
        """Specify a function COMMAND to call if the X
        selection owned by this widget is queried by another
        application.

        This function must return the contents of the
        selection. The function will be called with the
        arguments OFFSET and LENGTH which allows the chunking
        of very long selections. The following keyword
        parameters can be provided:
        selection - name of the selection (default PRIMARY),
        type - type of the selection (e.g. STRING, FILE_NAME)."""
        name = self._register(command)
        self.tk.call(('selection', 'handle') + self._options(kw)
              + (self._w, name))

    套路 选定内容_处理(分身, 命令, **关键词参数):
        """指定当另一应用程序查询此部件拥有的选定内容时要调用的函数 '命令'."""
        分身.selection_handle(命令, **关键词参数)

    def selection_own(self, **kw):
        """Become owner of X selection.

        A keyword parameter selection specifies the name of
        the selection (default PRIMARY)."""
        self.tk.call(('selection', 'own') +
                 self._options(kw) + (self._w,))

    套路 选定内容_拥有(分身, **关键词参数):
        """成为选定内容的所有者."""
        分身.selection_own(**关键词参数)

    def selection_own_get(self, **kw):
        """Return owner of X selection.

        The following keyword parameter can
        be provided:
        selection - name of the selection (default PRIMARY),
        type - type of the selection (e.g. STRING, FILE_NAME)."""
        if 'displayof' not in kw: kw['displayof'] = self._w
        name = self.tk.call(('selection', 'own') + self._options(kw))
        if not name: return None
        return self._nametowidget(name)

    套路 选定内容_获取所有者(分身, **关键词参数):
        """返回选定内容的所有者."""
        分身.selection_own_get(**关键词参数)

    def send(self, interp, cmd, *args):
        """Send Tcl command CMD to different interpreter INTERP to be executed."""
        return self.tk.call(('send', interp, cmd) + args)

    套路 发送(分身, 解释器, 命令, *参数):
        """将 Tcl 命令发送给其他解释器执行"""
        返回 分身.send(解释器, 命令, *参数)

    def lower(self, belowThis=None):
        """Lower this widget in the stacking order."""
        self.tk.call('lower', self._w, belowThis)

    套路 下移(分身, 低于此=空):
        """下移部件的叠放顺序"""
        分身.tk.call('lower', 分身._w, 低于此)

    def tkraise(self, aboveThis=None):
        """Raise this widget in the stacking order."""
        self.tk.call('raise', self._w, aboveThis)

    套路 上移(分身, 高于此=空):
        """上移部件的叠放顺序"""
        分身.tk.call('raise', 分身._w, 高于此)

    lift = tkraise

    def winfo_atom(self, name, displayof=0):
        """Return integer which represents atom NAME."""
        args = ('winfo', 'atom') + self._displayof(displayof) + (name,)
        return self.tk.getint(self.tk.call(args))

    def winfo_atomname(self, id, displayof=0):
        """Return name of atom with identifier ID."""
        args = ('winfo', 'atomname') \
               + self._displayof(displayof) + (id,)
        return self.tk.call(args)

    def winfo_cells(self):
        """返回此部件的颜色映射中的单元数."""
        return self.tk.getint(
            self.tk.call('winfo', 'cells', self._w))

    信息_单元数 = winfo_cells

    def winfo_children(self):
        """返回此部件的所有子部件的列表."""
        result = []
        for child in self.tk.splitlist(
            self.tk.call('winfo', 'children', self._w)):
            try:
                # Tcl sometimes returns extra windows, e.g. for
                # menus; those need to be skipped
                result.append(self._nametowidget(child))
            except KeyError:
                pass
        return result

    信息_子部件列表 = winfo_children

    def winfo_class(self):
        """返回此部件的窗口类名."""
        return self.tk.call('winfo', 'class', self._w)

    信息_类名 = winfo_class

    def winfo_colormapfull(self):
        """如果上次颜色请求时颜色映射已满, 则返回 真."""
        return self.tk.getboolean(
            self.tk.call('winfo', 'colormapfull', self._w))

    信息_颜色映射已满 = winfo_colormapfull

    def winfo_containing(self, rootX, rootY, displayof=0):
        """Return the widget which is at the root coordinates ROOTX, ROOTY."""
        args = ('winfo', 'containing') \
               + self._displayof(displayof) + (rootX, rootY)
        name = self.tk.call(args)
        if not name: return None
        return self._nametowidget(name)

    套路 信息_包含(分身, 根x, 根y, 显示区=0):
        """返回位于根窗口坐标 (根x, 根y) 的部件"""
        返回 分身.winfo_containing(根x, 根y, 显示区)

    def winfo_depth(self):
        """返回每个像素的位数."""
        return self.tk.getint(self.tk.call('winfo', 'depth', self._w))

    信息_深度 = winfo_depth

    def winfo_exists(self):
        """如果此部件存在, 则返回 真."""
        return self.tk.getint(
            self.tk.call('winfo', 'exists', self._w))

    信息_存在 = winfo_exists

    def winfo_fpixels(self, number):
        """Return the number of pixels for the given distance NUMBER
        (e.g. "3c") as float."""
        return self.tk.getdouble(self.tk.call(
            'winfo', 'fpixels', self._w, number))

    套路 信息_浮点像素数(分身, 距离):
        """返回给定距离 (例如 '3c') 的像素数, 结果为浮点数"""
        返回 分身.winfo_fpixels(距离)

    def winfo_geometry(self):
        """返回此部件的几何尺寸, 结果为 '宽x高+X+Y' 形式的字符串."""
        return self.tk.call('winfo', 'geometry', self._w)

    信息_尺寸 = winfo_geometry

    def winfo_height(self):
        """返回此部件的高度."""
        return self.tk.getint(
            self.tk.call('winfo', 'height', self._w))

    信息_高度 = winfo_height

    def winfo_id(self):
        """返回此部件的 ID."""
        return int(self.tk.call('winfo', 'id', self._w), 0)

    信息_id = winfo_id

    def winfo_interps(self, displayof=0):
        """Return the name of all Tcl interpreters for this display."""
        args = ('winfo', 'interps') + self._displayof(displayof)
        return self.tk.splitlist(self.tk.call(args))

    套路 信息_解释器(分身, 显示区=0):
        """返回此显示区的所有 Tcl 解释器的名称"""
        返回 winfo_interps(显示区)  # display 到底是什么鬼?

    def winfo_ismapped(self):
        """如果此窗口被映射, 则返回 真."""
        return self.tk.getint(
            self.tk.call('winfo', 'ismapped', self._w))

    信息_被映射 = winfo_ismapped

    def winfo_manager(self):
        """返回此部件的窗口管理器名称."""
        return self.tk.call('winfo', 'manager', self._w)

    信息_管理器 = winfo_manager

    def winfo_name(self):
        """返回此部件的名称."""
        return self.tk.call('winfo', 'name', self._w)

    信息_名称 = winfo_name

    def winfo_parent(self):
        """返回此部件的父对象的名称."""
        return self.tk.call('winfo', 'parent', self._w)

    信息_父对象 = winfo_parent

    def winfo_pathname(self, id, displayof=0):
        """Return the pathname of the widget given by ID."""
        args = ('winfo', 'pathname') \
               + self._displayof(displayof) + (id,)
        return self.tk.call(args)

    套路 信息_路径名(分身, id, 显示区=0):
        """返回 id 所代表部件的路径名"""
        返回 分身.winfo_pathname(id, 显示区)

    def winfo_pixels(self, number):
        """Rounded integer value of winfo_fpixels."""
        return self.tk.getint(
            self.tk.call('winfo', 'pixels', self._w, number))

    套路 信息_像素数(分身, 距离):
        """返回给定距离 (例如 '3c') 的像素数, 结果为舍入后的整数"""
        返回 分身.winfo_pixels(距离)

    def winfo_pointerx(self):
        """返回鼠标指针在根窗口上的 x 坐标."""
        return self.tk.getint(
            self.tk.call('winfo', 'pointerx', self._w))

    信息_指针x = winfo_pointerx

    def winfo_pointerxy(self):
        """返回鼠标指针在根窗口上的 (x, y) 坐标元组."""
        return self._getints(
            self.tk.call('winfo', 'pointerxy', self._w))

    信息_指针xy = winfo_pointerxy

    def winfo_pointery(self):
        """返回鼠标指针在根窗口上的 y 坐标."""
        return self.tk.getint(
            self.tk.call('winfo', 'pointery', self._w))

    信息_指针y = winfo_pointery

    def winfo_reqheight(self):
        """返回此部件的请求高度."""
        return self.tk.getint(
            self.tk.call('winfo', 'reqheight', self._w))

    信息_请求高度 = winfo_reqheight

    def winfo_reqwidth(self):
        """返回此部件的请求宽度."""
        return self.tk.getint(
            self.tk.call('winfo', 'reqwidth', self._w))

    信息_请求宽度 = winfo_reqwidth

    def winfo_rgb(self, color):
        """Return tuple of decimal values for red, green, blue for
        COLOR in this widget."""
        return self._getints(
            self.tk.call('winfo', 'rgb', self._w, color))

    套路 信息_rgb(分身, 颜色):
        """返回此部件中 '颜色' 的红/绿/蓝小数值三元组"""
        返回 分身.winfo_rgb(颜色)

    def winfo_rootx(self):
        """返回此部件的左上角在根窗口上的 x 坐标."""
        return self.tk.getint(
            self.tk.call('winfo', 'rootx', self._w))

    信息_根x = winfo_rootx

    def winfo_rooty(self):
        """返回此部件的左上角在根窗口上的 y 坐标."""
        return self.tk.getint(
            self.tk.call('winfo', 'rooty', self._w))

    信息_根y = winfo_rooty

    def winfo_screen(self):
        """返回此部件的屏幕名称."""
        return self.tk.call('winfo', 'screen', self._w)

    信息_屏幕 = winfo_screen

    def winfo_screencells(self):
        """返回此部件的屏幕的颜色映射的单元数."""
        return self.tk.getint(
            self.tk.call('winfo', 'screencells', self._w))

    信息_屏幕单元数 = winfo_screencells

    def winfo_screendepth(self):
        """返回此部件的屏幕的根窗口的每像素位数."""
        return self.tk.getint(
            self.tk.call('winfo', 'screendepth', self._w))

    信息_屏幕深度 = winfo_screendepth

    def winfo_screenheight(self):
        """返回此部件的屏幕的高度, 以像素为单位."""
        return self.tk.getint(
            self.tk.call('winfo', 'screenheight', self._w))

    信息_屏幕高度 = winfo_screenheight

    def winfo_screenmmheight(self):
        """返回此部件的屏幕的高度, 以 mm 为单位."""
        return self.tk.getint(
            self.tk.call('winfo', 'screenmmheight', self._w))

    信息_屏幕高度mm = winfo_screenmmheight

    def winfo_screenmmwidth(self):
        """返回此部件的屏幕的宽度, 以 mm 为单位."""
        return self.tk.getint(
            self.tk.call('winfo', 'screenmmwidth', self._w))

    信息_屏幕宽度mm = winfo_screenmmwidth

    def winfo_screenvisual(self):
        """Return one of the strings directcolor, grayscale, pseudocolor,
        staticcolor, staticgray, or truecolor for the default
        colormodel of this screen."""
        return self.tk.call('winfo', 'screenvisual', self._w)

    def winfo_screenwidth(self):
        """返回此部件的屏幕的宽度, 以像素为单位."""
        return self.tk.getint(
            self.tk.call('winfo', 'screenwidth', self._w))

    信息_屏幕宽度 = winfo_screenwidth

    def winfo_server(self):
        """Return information of the X-Server of the screen of this widget in
        the form "XmajorRminor vendor vendorVersion"."""
        return self.tk.call('winfo', 'server', self._w)

    def winfo_toplevel(self):
        """返回此部件的顶级部件."""
        return self._nametowidget(self.tk.call(
            'winfo', 'toplevel', self._w))

    信息_顶级 = winfo_toplevel

    def winfo_viewable(self):
        """如果此部件及其所有更高祖先部件都被映射 (即可见), 则返回 真."""
        return self.tk.getint(
            self.tk.call('winfo', 'viewable', self._w))

    信息_可见 = winfo_viewable

    def winfo_visual(self):
        """Return one of the strings directcolor, grayscale, pseudocolor,
        staticcolor, staticgray, or truecolor for the
        colormodel of this widget."""
        return self.tk.call('winfo', 'visual', self._w)

    def winfo_visualid(self):
        """Return the X identifier for the visual for this widget."""
        return self.tk.call('winfo', 'visualid', self._w)

    def winfo_visualsavailable(self, includeids=False):
        """Return a list of all visuals available for the screen
        of this widget.

        Each item in the list consists of a visual name (see winfo_visual), a
        depth and if includeids is true is given also the X identifier."""
        data = self.tk.call('winfo', 'visualsavailable', self._w,
                            'includeids' if includeids else None)
        data = [self.tk.splitlist(x) for x in self.tk.splitlist(data)]
        return [self.__winfo_parseitem(x) for x in data]

    def __winfo_parseitem(self, t):
        """Internal function."""
        return t[:1] + tuple(map(self.__winfo_getint, t[1:]))

    def __winfo_getint(self, x):
        """Internal function."""
        return int(x, 0)

    def winfo_vrootheight(self):
        """Return the height of the virtual root window associated with this
        widget in pixels. If there is no virtual root window return the
        height of the screen."""
        return self.tk.getint(
            self.tk.call('winfo', 'vrootheight', self._w))

    def winfo_vrootwidth(self):
        """Return the width of the virtual root window associated with this
        widget in pixel. If there is no virtual root window return the
        width of the screen."""
        return self.tk.getint(
            self.tk.call('winfo', 'vrootwidth', self._w))

    def winfo_vrootx(self):
        """Return the x offset of the virtual root relative to the root
        window of the screen of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'vrootx', self._w))

    def winfo_vrooty(self):
        """Return the y offset of the virtual root relative to the root
        window of the screen of this widget."""
        return self.tk.getint(
            self.tk.call('winfo', 'vrooty', self._w))

    def winfo_width(self):
        """返回此部件的宽度."""
        return self.tk.getint(
            self.tk.call('winfo', 'width', self._w))

    信息_宽度 = winfo_width

    def winfo_x(self):
        """返回此部件左上角在父对象中的 x 坐标."""
        return self.tk.getint(
            self.tk.call('winfo', 'x', self._w))

    信息_x = winfo_x

    def winfo_y(self):
        """返回此部件左上角在父对象中的 y 坐标."""
        return self.tk.getint(
            self.tk.call('winfo', 'y', self._w))

    信息_y = winfo_y

    def update(self):
        """进入事件循环, 直到所有挂起的事件都已被 Tcl 处理."""
        self.tk.call('update')

    更新 = update

    def update_idletasks(self):
        """进入事件循环, 直到所有空闲回调都已被调用. 窗口显示会被更新, 但用户
        引起的事件不会被处理."""
        self.tk.call('update', 'idletasks')

    更新_空闲任务 = update_idletasks

    def bindtags(self, tagList=None):
        """Set or get the list of bindtags for this widget.

        With no argument return the list of all bindtags associated with
        this widget. With a list of strings as argument the bindtags are
        set to this list. The bindtags determine in which order events are
        processed (see bind)."""
        if tagList is None:
            return self.tk.splitlist(
                self.tk.call('bindtags', self._w))
        else:
            self.tk.call('bindtags', self._w, tagList)

    套路 绑定标志(分身, 标志列表=空):
        """设置或获取此部件的绑定标志的列表.

        无参数时, 返回与此部件相关的所有绑定标志的列表. 以字符串列表作为参数时,
        绑定标志设置为该列表. 绑定标志决定事件的处理顺序 (参见 '绑定')."""
        返回 分身.bindtags(标志列表)

    def _bind(self, what, sequence, func, add, needcleanup=1):
        """Internal function."""
        if isinstance(func, str):
            self.tk.call(what + (sequence, func))
        elif func:
            funcid = self._register(func, self._substitute,
                        needcleanup)
            cmd = ('%sif {"[%s %s]" == "break"} break\n'
                   %
                   (add and '+' or '',
                funcid, self._subst_format_str))
            self.tk.call(what + (sequence, cmd))
            return funcid
        elif sequence:
            return self.tk.call(what + (sequence,))
        else:
            return self.tk.splitlist(self.tk.call(what))

    def bind(self, sequence=None, func=None, add=None):
        """Bind to this widget at event SEQUENCE a call to function FUNC.

        SEQUENCE is a string of concatenated event
        patterns. An event pattern is of the form
        <MODIFIER-MODIFIER-TYPE-DETAIL> where MODIFIER is one
        of Control, Mod2, M2, Shift, Mod3, M3, Lock, Mod4, M4,
        Button1, B1, Mod5, M5 Button2, B2, Meta, M, Button3,
        B3, Alt, Button4, B4, Double, Button5, B5 Triple,
        Mod1, M1. TYPE is one of Activate, Enter, Map,
        ButtonPress, Button, Expose, Motion, ButtonRelease
        FocusIn, MouseWheel, Circulate, FocusOut, Property,
        Colormap, Gravity Reparent, Configure, KeyPress, Key,
        Unmap, Deactivate, KeyRelease Visibility, Destroy,
        Leave and DETAIL is the button number for ButtonPress,
        ButtonRelease and DETAIL is the Keysym for KeyPress and
        KeyRelease. Examples are
        <Control-Button-1> for pressing Control and mouse button 1 or
        <Alt-A> for pressing A and the Alt key (KeyPress can be omitted).
        An event pattern can also be a virtual event of the form
        <<AString>> where AString can be arbitrary. This
        event can be generated by event_generate.
        If events are concatenated they must appear shortly
        after each other.

        FUNC will be called if the event sequence occurs with an
        instance of Event as argument. If the return value of FUNC is
        "break" no further bound function is invoked.

        An additional boolean parameter ADD specifies whether FUNC will
        be called additionally to the other bound function or whether
        it will replace the previous function.

        Bind will return an identifier to allow deletion of the bound function with
        unbind without memory leak.

        If FUNC or SEQUENCE is omitted the bound function or list
        of bound events are returned."""

        return self._bind(('bind', self._w), sequence, func, add)

    套路 绑定(分身, 序列=空, 函数=空, 添加=空):
        """给部件绑定一个事件. 
        
        参数 '序列' 描述期待的事件, 例如 <Control-Button-1>.

        参数 '函数' 为此部件发生该事件时要调用的函数. 
        
        参数 '添加' 为布尔值, 决定是否保留已有的事件绑定.
        
        返回一个 ID, '解除绑定' 方法可利用该 ID 删除绑定的函数.
        
        如果未指定 '函数' 或 '序列', 则返回绑定的函数或绑定事件列表."""
        返回 分身.bind(sequence=序列, func=函数, add=添加)

    def unbind(self, sequence, funcid=None):
        """Unbind for this widget for event SEQUENCE  the
        function identified with FUNCID."""
        self.tk.call('bind', self._w, sequence, '')
        if funcid:
            self.deletecommand(funcid)

    套路 解除绑定(分身, 序列, 函数id=空):
        """解除此部件的事件 ('序列') 绑定的函数 ('函数id')."""
        分身.unbind(序列, 函数id)

    def bind_all(self, sequence=None, func=None, add=None):
        """Bind to all widgets at an event SEQUENCE a call to function FUNC.
        An additional boolean parameter ADD specifies whether FUNC will
        be called additionally to the other bound function or whether
        it will replace the previous function. See bind for the return value."""
        return self._bind(('bind', 'all'), sequence, func, add, 0)

    套路 绑定_全部(分身, 序列=空, 函数=空, 添加=空):
        """给所有部件的事件 ('序列') 绑定 '函数'."""
        返回 分身.bind_all(sequence=序列, func=函数, add=添加)

    def unbind_all(self, sequence):
        """Unbind for all widgets for event SEQUENCE all functions."""
        self.tk.call('bind', 'all' , sequence, '')

    套路 解除绑定_全部(分身, 序列):
        """解除所有部件的事件 ('序列') 绑定的所有函数."""
        分身.unbind_all(序列)

    def bind_class(self, className, sequence=None, func=None, add=None):
        """Bind to widgets with bindtag CLASSNAME at event
        SEQUENCE a call of function FUNC. An additional
        boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function or
        whether it will replace the previous function. See bind for
        the return value."""

        return self._bind(('bind', className), sequence, func, add, 0)

    套路 绑定_类名(分身, 类名, 序列=空, 函数=空, 添加=空):
        """给有 '类名' 绑定标志的部件的事件 ('序列') 绑定 '函数'."""
        返回 分身.bind_class(类名, sequence=序列, func=函数, add=添加)

    def unbind_class(self, className, sequence):
        """Unbind for all widgets with bindtag CLASSNAME for event SEQUENCE
        all functions."""
        self.tk.call('bind', className , sequence, '')

    套路 解除绑定_类名(分身, 类名, 序列):
        """解除所有带 '类名' 绑定标志的部件的事件 ('序列') 绑定的所有函数."""
        分身.unbind_class(类名, 序列)

    def mainloop(self, n=0):
        """调用 Tk 的主循环."""
        self.tk.mainloop(n)

    主循环 = mainloop

    def quit(self):
        """退出 Tcl 解释器. 所有部件都会被销毁."""
        self.tk.quit()

    退出 = quit

    def _getints(self, string):
        """Internal function."""
        if string:
            return tuple(map(self.tk.getint, self.tk.splitlist(string)))

    def _getdoubles(self, string):
        """Internal function."""
        if string:
            return tuple(map(self.tk.getdouble, self.tk.splitlist(string)))

    def _getboolean(self, string):
        """Internal function."""
        if string:
            return self.tk.getboolean(string)

    def _displayof(self, displayof):
        """Internal function."""
        if displayof:
            return ('-displayof', displayof)
        if displayof is None:
            return ('-displayof', self._w)
        return ()

    @property
    def _windowingsystem(self):
        """Internal function."""
        try:
            return self._root()._windowingsystem_cached
        except AttributeError:
            ws = self._root()._windowingsystem_cached = \
                        self.tk.call('tk', 'windowingsystem')
            return ws

    def _options(self, cnf, kw = None):
        """Internal function."""
        if kw:
            cnf = _cnfmerge((cnf, kw))
        else:
            cnf = _cnfmerge(cnf)
        res = ()
        for k, v in cnf.items():
            if v is not None:
                if k[-1] == '_': k = k[:-1]
                if callable(v):
                    v = self._register(v)
                elif isinstance(v, (tuple, list)):
                    nv = []
                    for item in v:
                        if isinstance(item, int):
                            nv.append(str(item))
                        elif isinstance(item, str):
                            nv.append(_stringify(item))
                        else:
                            break
                    else:
                        v = ' '.join(nv)
                res = res + ('-'+k, v)
        return res

    def nametowidget(self, name):
        """Return the Tkinter instance of a widget identified by
        its Tcl name NAME."""
        name = str(name).split('.')
        w = self

        if not name[0]:
            w = w._root()
            name = name[1:]

        for n in name:
            if not n:
                break
            w = w.children[n]

        return w

    _nametowidget = nametowidget

    def _register(self, func, subst=None, needcleanup=1):
        """Return a newly created Tcl function. If this
        function is called, the Python function FUNC will
        be executed. An optional function SUBST can
        be given which will be executed before FUNC."""
        f = CallWrapper(func, subst, self).__call__
        name = repr(id(f))
        try:
            func = func.__func__
        except AttributeError:
            pass
        try:
            name = name + func.__name__
        except AttributeError:
            pass
        self.tk.createcommand(name, f)
        if needcleanup:
            if self._tclCommands is None:
                self._tclCommands = []
            self._tclCommands.append(name)
        return name

    register = _register

    def _root(self):
        """Internal function."""
        w = self
        while w.master: w = w.master
        return w
    _subst_format = ('%#', '%b', '%f', '%h', '%k',
             '%s', '%t', '%w', '%x', '%y',
             '%A', '%E', '%K', '%N', '%W', '%T', '%X', '%Y', '%D')
    _subst_format_str = " ".join(_subst_format)

    def _substitute(self, *args):
        """Internal function."""
        if len(args) != len(self._subst_format): return args
        getboolean = self.tk.getboolean

        getint = self.tk.getint
        def getint_event(s):
            """Tk changed behavior in 8.4.2, returning "??" rather more often."""
            try:
                return getint(s)
            except (ValueError, TclError):
                return s

        nsign, b, f, h, k, s, t, w, x, y, A, E, K, N, W, T, X, Y, D = args
        # Missing: (a, c, d, m, o, v, B, R)
        e = Event()
        # serial field: valid for all events
        # number of button: ButtonPress and ButtonRelease events only
        # height field: Configure, ConfigureRequest, Create,
        # ResizeRequest, and Expose events only
        # keycode field: KeyPress and KeyRelease events only
        # time field: "valid for events that contain a time field"
        # width field: Configure, ConfigureRequest, Create, ResizeRequest,
        # and Expose events only
        # x field: "valid for events that contain an x field"
        # y field: "valid for events that contain a y field"
        # keysym as decimal: KeyPress and KeyRelease events only
        # x_root, y_root fields: ButtonPress, ButtonRelease, KeyPress,
        # KeyRelease, and Motion events
        e.serial = getint(nsign)
        e.num = getint_event(b)
        try: e.focus = getboolean(f)
        except TclError: pass
        e.height = getint_event(h)
        e.keycode = getint_event(k)
        e.state = getint_event(s)
        e.time = getint_event(t)
        e.width = getint_event(w)
        e.x = getint_event(x)
        e.y = getint_event(y)
        e.char = A
        try: e.send_event = getboolean(E)
        except TclError: pass
        e.keysym = K
        e.keysym_num = getint_event(N)
        try:
            e.type = EventType(T)
        except ValueError:
            e.type = T
        try:
            e.widget = self._nametowidget(W)
        except KeyError:
            e.widget = W
        e.x_root = getint_event(X)
        e.y_root = getint_event(Y)
        try:
            e.delta = getint(D)
        except (ValueError, TclError):
            e.delta = 0
        return (e,)

    def _report_exception(self):
        """Internal function."""
        exc, val, tb = sys.exc_info()
        root = self._root()
        root.report_callback_exception(exc, val, tb)

    def _getconfigure(self, *args):
        """Call Tcl configure command and return the result as a dict."""
        cnf = {}
        for x in self.tk.splitlist(self.tk.call(*args)):
            x = self.tk.splitlist(x)
            cnf[x[0][1:]] = (x[0][1:],) + x[1:]
        return cnf

    def _getconfigure1(self, *args):
        x = self.tk.splitlist(self.tk.call(*args))
        return (x[0][1:],) + x[1:]

    def _configure(self, cmd, cnf, kw):
        """Internal function."""
        if kw:
            cnf = _cnfmerge((cnf, kw))
        elif cnf:
            cnf = _cnfmerge(cnf)
        if cnf is None:
            return self._getconfigure(_flatten((self._w, cmd)))
        if isinstance(cnf, str):
            return self._getconfigure1(_flatten((self._w, cmd, '-'+cnf)))
        self.tk.call(_flatten((self._w, cmd)) + self._options(cnf))
    # These used to be defined in Widget:

    def configure(self, cnf=None, **kw):
        """Configure resources of a widget.

        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method keys.
        """
        return self._configure('configure', cnf, kw)

    套路 配置(分身, 配置字典=空, **关键词参数):
        """配置部件的选项. 要了解有哪些关键词参数, 请调用 '键列表' 方法."""
        返回 分身.configure(cnf=配置字典, **关键词参数)

    config = configure

    def cget(self, key):
        """Return the resource value for a KEY given as string."""
        return self.tk.call(self._w, 'cget', '-' + key)

    套路 获取配置(分身, 键):
        """返回字符串参数 '键' 对应的配置选项值."""
        返回 分身.cget(键)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        """返回此部件的所有配置选项的列表."""
        splitlist = self.tk.splitlist
        return [splitlist(x)[0][1:] for x in
                splitlist(self.tk.call(self._w, 'configure'))]

    键列表 = keys

    def __str__(self):
        """Return the window path name of this widget."""
        return self._w

    def __repr__(self):
        return '<%s.%s object %s>' % (
            self.__class__.__module__, self.__class__.__qualname__, self._w)

    # Pack methods that apply to the master
    _noarg_ = ['_noarg_']

    def pack_propagate(self, flag=_noarg_):
        """Set or get the status for propagation of geometry information.

        A boolean argument specifies whether the geometry information
        of the slaves will determine the size of this widget. If no argument
        is given the current setting will be returned.
        """
        if flag is Misc._noarg_:
            return self._getboolean(self.tk.call(
                'pack', 'propagate', self._w))
        else:
            self.tk.call('pack', 'propagate', self._w, flag)

    套路 常规布局_自适应尺寸(分身, 标志=['_noarg_']):
        """设置或获取部件尺寸是否自动调整以适应内容. 参数为布尔值"""
        返回 分身.pack_propagate(标志)

    propagate = pack_propagate

    def pack_slaves(self):
        """返回此部件的所有从属对象的列表, 按照布局顺序."""
        return [self._nametowidget(x) for x in
                self.tk.splitlist(
                   self.tk.call('pack', 'slaves', self._w))]

    常规布局_从属对象 = pack_slaves

    slaves = pack_slaves

    # Place method that applies to the master
    def place_slaves(self):
        """返回此部件的所有从属对象的列表, 按照布局顺序."""
        return [self._nametowidget(x) for x in
                self.tk.splitlist(
                   self.tk.call(
                       'place', 'slaves', self._w))]

    位置布局_从属对象 = place_slaves

    # Grid methods that apply to the master

    def grid_anchor(self, anchor=None): # new in Tk 8.5
        """The anchor value controls how to place the grid within the
        master when no row/column has any weight.

        The default anchor is nw."""
        self.tk.call('grid', 'anchor', self._w, anchor)

    套路 网格布局_锚点(分身, 锚点=空):
        """锚点值控制如何在主对象内放置网格 (行/列均无重量时).

        默认锚点为 '左上'."""
        分身.grid_anchor(锚点)

    anchor = grid_anchor

    def grid_bbox(self, column=None, row=None, col2=None, row2=None):
        """Return a tuple of integer coordinates for the bounding
        box of this widget controlled by the geometry manager grid.

        If COLUMN, ROW is given the bounding box applies from
        the cell with row and column 0 to the specified
        cell. If COL2 and ROW2 are given the bounding box
        starts at that cell.

        The returned integers specify the offset of the upper left
        corner in the master widget and the width and height.
        """
        args = ('grid', 'bbox', self._w)
        if column is not None and row is not None:
            args = args + (column, row)
        if col2 is not None and row2 is not None:
            args = args + (col2, row2)
        return self._getints(self.tk.call(*args)) or None

    套路 网格布局_包围盒(分身, 列=空, 行=空, 列2=空, 行2=空):
        """返回此部件的包围盒的整数坐标元组. 指定此部件左上角在主部件
        中的偏移量及高度和宽度. 
        
        例如: (0, 0, 1, 1) 返回四个单元组成的包围盒, 而非一个单元.
        """
        返回 分身.grid_bbox(column=列, row=行, col2=列2, row2=行2)

    bbox = grid_bbox

    def _gridconvvalue(self, value):
        if isinstance(value, (str, _tkinter.Tcl_Obj)):
            try:
                svalue = str(value)
                if not svalue:
                    return None
                elif '.' in svalue:
                    return self.tk.getdouble(svalue)
                else:
                    return self.tk.getint(svalue)
            except (ValueError, TclError):
                pass
        return value

    def _grid_configure(self, command, index, cnf, kw):
        """Internal function."""
        if isinstance(cnf, str) and not kw:
            if cnf[-1:] == '_':
                cnf = cnf[:-1]
            if cnf[:1] != '-':
                cnf = '-'+cnf
            options = (cnf,)
        else:
            options = self._options(cnf, kw)
        if not options:
            return _splitdict(
                self.tk,
                self.tk.call('grid', command, self._w, index),
                conv=self._gridconvvalue)
        res = self.tk.call(
                  ('grid', command, self._w, index)
                  + options)
        if len(options) == 1:
            return self._gridconvvalue(res)

    def grid_columnconfigure(self, index, cnf={}, **kw):
        """Configure column INDEX of a grid.

        Valid resources are minsize (minimum size of the column),
        weight (how much does additional space propagate to this column)
        and pad (how much space to let additionally)."""
        return self._grid_configure('columnconfigure', index, cnf, kw)

    套路 网格布局_列配置(分身, 索引, 配置字典={}, **关键词参数):
        """配置网格的指定列. 选项有: 最小大小, 重量, 边距."""
        选项字典 = {
            '最小大小' : 'minsize',
            '重量' : 'weight',
            '边距' : 'pad'
        }
        关键词参数副本 = 关键词参数.复制()
        取 键 于 关键词参数:
            如果 键 在 选项字典:
                关键词参数副本[选项字典[键]] = 关键词参数副本[键]
                删 关键词参数副本[键]
        返回 分身.grid_columnconfigure(索引, cnf=配置字典, **关键词参数副本)

    columnconfigure = grid_columnconfigure

    def grid_location(self, x, y):
        """返回列和行的元组, x/y 表示的像素位于该元组所表示的单元上."""
        return self._getints(
            self.tk.call(
                'grid', 'location', self._w, x, y)) or None

    网格布局_位置 = grid_location

    def grid_propagate(self, flag=_noarg_):
        """Set or get the status for propagation of geometry information.

        A boolean argument specifies whether the geometry information
        of the slaves will determine the size of this widget. If no argument
        is given, the current setting will be returned.
        """
        if flag is Misc._noarg_:
            return self._getboolean(self.tk.call(
                'grid', 'propagate', self._w))
        else:
            self.tk.call('grid', 'propagate', self._w, flag)

    套路 网格布局_自适应尺寸(分身, 标志=_noarg_):
        """设置或获取部件尺寸是否自动调整以适应内容. 参数为布尔值"""
        返回 分身.grid_propagate(标志)

    def grid_rowconfigure(self, index, cnf={}, **kw):
        """Configure row INDEX of a grid.

        Valid resources are minsize (minimum size of the row),
        weight (how much does additional space propagate to this row)
        and pad (how much space to let additionally)."""
        return self._grid_configure('rowconfigure', index, cnf, kw)

    套路 网格布局_行配置(分身, 索引, 配置字典={}, **关键词参数):
        """配置网格的指定行. 选项有: 最小大小, 重量, 边距."""
        选项字典 = {
            '最小大小' : 'minsize',
            '重量' : 'weight',
            '边距' : 'pad'
        }
        关键词参数副本 = 关键词参数.复制()
        取 键 于 关键词参数:
            如果 键 在 选项字典:
                关键词参数副本[选项字典[键]] = 关键词参数副本[键]
                删 关键词参数副本[键]
        返回 分身.grid_rowconfigure(索引, cnf=配置字典, **关键词参数副本)

    rowconfigure = grid_rowconfigure

    def grid_size(self):
        """返回网格中列数和行数的元组."""
        return self._getints(
            self.tk.call('grid', 'size', self._w)) or None

    网格布局_大小 = grid_size

    size = grid_size

    def grid_slaves(self, row=None, column=None):
        """Return a list of all slaves of this widget
        in its packing order."""
        args = ()
        if row is not None:
            args = args + ('-row', row)
        if column is not None:
            args = args + ('-column', column)
        return [self._nametowidget(x) for x in
                self.tk.splitlist(self.tk.call(
                   ('grid', 'slaves', self._w) + args))]

    套路 网格布局_从属对象(分身, 行=空, 列=空):
        """返回此部件的所有从属对象的列表, 按照布局顺序."""
        返回 分身.grid_slaves(row=行, column=列)

    # Support for the "event" command, new in Tk 4.2.
    # By Case Roole.

    def event_add(self, virtual, *sequences):
        """Bind a virtual event VIRTUAL (of the form <<Name>>)
        to an event SEQUENCE such that the virtual event is triggered
        whenever SEQUENCE occurs."""
        args = ('event', 'add', virtual) + sequences
        self.tk.call(args)

    def event_delete(self, virtual, *sequences):
        """Unbind a virtual event VIRTUAL from SEQUENCE."""
        args = ('event', 'delete', virtual) + sequences
        self.tk.call(args)

    def event_generate(self, sequence, **kw):
        """Generate an event SEQUENCE. Additional
        keyword arguments specify parameter of the event
        (e.g. x, y, rootx, rooty)."""
        args = ('event', 'generate', self._w, sequence)
        for k, v in kw.items():
            args = args + ('-%s' % k, str(v))
        self.tk.call(args)

    def event_info(self, virtual=None):
        """Return a list of all virtual events or the information
        about the SEQUENCE bound to the virtual event VIRTUAL."""
        return self.tk.splitlist(
            self.tk.call('event', 'info', virtual))

    # Image related commands

    def image_names(self):
        """返回全部现有图像名称的列表."""
        return self.tk.splitlist(self.tk.call('image', 'names'))

    图像名称 = image_names

    def image_types(self):
        """返回全部可用图像类型 (例如位图) 的列表."""
        return self.tk.splitlist(self.tk.call('image', 'types'))

    图像类型 = image_types


class CallWrapper:
    """Internal class. Stores function to call when some user
    defined Tcl function is called e.g. after an event occurred."""

    def __init__(self, func, subst, widget):
        """Store FUNC, SUBST and WIDGET as members."""
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        """Apply first function SUBST to arguments, than FUNC."""
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except SystemExit:
            raise
        except:
            self.widget._report_exception()


class XView:
    """用于查询和改变部件窗口水平位置的混合类."""

    def xview(self, *args):
        """Query and change the horizontal position of the view."""
        res = self.tk.call(self._w, 'xview', *args)
        if not args:
            return self._getdoubles(res)

    套路 视图x(分身, *参数):
        """查询和改变视图的水平位置"""
        返回 分身.xview(*参数)

    def xview_moveto(self, fraction):
        """Adjusts the view in the window so that FRACTION of the
        total width of the canvas is off-screen to the left."""
        self.tk.call(self._w, 'xview', 'moveto', fraction)

    套路 视图x_移至(分身, 分数):
        """调整窗口中的视图, 使得画布总宽度的 '分数' 比例部分左移离开屏幕"""
        分身.xview_moveto(分数)

    def xview_scroll(self, number, what):
        """Shift the x-view according to NUMBER which is measured in "units"
        or "pages" (WHAT)."""
        self.tk.call(self._w, 'xview', 'scroll', number, what)

    套路 视图x_滚动(分身, 数值, 单位):
        """移动水平视图"""
        分身.xview_scroll(数值, 单位)

视图X类 = XView

class YView:
    """用于查询和改变部件窗口垂直位置的混合类."""

    def yview(self, *args):
        """Query and change the vertical position of the view."""
        res = self.tk.call(self._w, 'yview', *args)
        if not args:
            return self._getdoubles(res)

    套路 视图y(分身, *参数):
        """查询和改变视图的垂直位置"""
        返回 分身.yview(*参数)

    def yview_moveto(self, fraction):
        """Adjusts the view in the window so that FRACTION of the
        total height of the canvas is off-screen to the top."""
        self.tk.call(self._w, 'yview', 'moveto', fraction)

    套路 视图y_移至(分身, 分数):
        """调整窗口中的视图, 使得画布总高度的 '分数' 比例部分上移离开屏幕"""
        分身.yview_moveto(分数)

    def yview_scroll(self, number, what):
        """Shift the y-view according to NUMBER which is measured in
        "units" or "pages" (WHAT)."""
        self.tk.call(self._w, 'yview', 'scroll', number, what)

    套路 视图y_滚动(分身, 数值, 单位):
        """移动垂直视图"""
        分身.yview_scroll(数值, 单位)

视图Y类 = YView

class Wm:
    """提供与窗口管理器通信的函数."""

    def wm_aspect(self,
              minNumer=None, minDenom=None,
              maxNumer=None, maxDenom=None):
        """Instruct the window manager to set the aspect ratio (width/height)
        of this widget to be between MINNUMER/MINDENOM and MAXNUMER/MAXDENOM. Return a tuple
        of the actual values if no argument is given."""
        return self._getints(
            self.tk.call('wm', 'aspect', self._w,
                     minNumer, minDenom,
                     maxNumer, maxDenom))

    套路 管理_纵横比(分身, 最小数=空, 最小分母=空, 最大数=空, 最大分母=空):
        """设置或获取此部件的纵横比"""
        返回 分身.wm_aspect(minNumer=最小数, minDenom=最小分母, 
                            maxNumer=最大数, maxDenom=最大分母)

    aspect = wm_aspect
    纵横比 = 管理_纵横比

    def wm_attributes(self, *args):
        """This subcommand returns or sets platform specific attributes

        The first form returns a list of the platform specific flags and
        their values. The second form returns the value for the specific
        option. The third form sets one or more of the values. The values
        are as follows:

        On Windows, -disabled gets or sets whether the window is in a
        disabled state. -toolwindow gets or sets the style of the window
        to toolwindow (as defined in the MSDN). -topmost gets or sets
        whether this is a topmost window (displays above all other
        windows).

        On Macintosh, XXXXX

        On Unix, there are currently no special attribute values.
        """
        args = ('wm', 'attributes', self._w) + args
        return self.tk.call(args)

    套路 管理_特性(分身, *参数):
        """返回或设置平台特定的属性"""
        返回 分身.wm_attributes(*参数)

    attributes = wm_attributes
    特性 = 管理_特性

    def wm_client(self, name=None):
        """Store NAME in WM_CLIENT_MACHINE property of this widget. Return
        current value."""
        return self.tk.call('wm', 'client', self._w, name)

    套路 管理_客户端(分身, 名称=空):
        """将 '名称' 保存在此部件的 WM_CLIENT_MACHINE 属性中. 返回当前值"""
        返回 分身.wm_client(名称)

    client = wm_client
    客户端 = 管理_客户端

    def wm_colormapwindows(self, *wlist):
        """Store list of window names (WLIST) into WM_COLORMAPWINDOWS property
        of this widget. This list contains windows whose colormaps differ from their
        parents. Return current list of widgets if WLIST is empty."""
        if len(wlist) > 1:
            wlist = (wlist,) # Tk needs a list of windows here
        args = ('wm', 'colormapwindows', self._w) + wlist
        if wlist:
            self.tk.call(args)
        else:
            return [self._nametowidget(x)
                    for x in self.tk.splitlist(self.tk.call(args))]

    套路 管理_颜色映射窗口(分身, *窗口列表):
        """将窗口名称列表存储在此部件的 WM_COLORMAPWINDOWS 属性中."""
        返回 分身.wm_colormapwindows(*窗口列表)

    colormapwindows = wm_colormapwindows
    颜色映射窗口 = 管理_颜色映射窗口

    def wm_command(self, value=None):
        """Store VALUE in WM_COMMAND property. It is the command
        which shall be used to invoke the application. Return current
        command if VALUE is None."""
        return self.tk.call('wm', 'command', self._w, value)

    套路 管理_命令(分身, 值=空):
        """将 '值' 存储在 WM_COMMAND 属性中. 调用应用程序应使用该命令.
        如果 '值' 为空, 则返回当前命令."""
        返回 分身.wm_command(值)

    command = wm_command
    命令 = 管理_命令

    def wm_deiconify(self):
        """将此部件解除图标化. 如果它从未被映射, 则不会被映射 (可见).
        在 Windows 上, 此部件会凸起并获得焦点."""
        return self.tk.call('wm', 'deiconify', self._w)

    解除图标化 = 管理_解除图标化 = wm_deiconify

    deiconify = wm_deiconify


    def wm_focusmodel(self, model=None):
        """Set focus model to MODEL. "active" means that this widget will claim
        the focus itself, "passive" means that the window manager shall give
        the focus. Return current focus model if MODEL is None."""
        return self.tk.call('wm', 'focusmodel', self._w, model)

    套路 管理_焦点模式(分身, 模式=空):
        """设置或返回焦点模式. 模式为 '主动' 表示此部件自己会索取焦点,
        '被动' 表示由窗口管理器赋予其焦点."""
        返回 分身.wm_focusmodel(模式)

    focusmodel = wm_focusmodel
    焦点模式 = 管理_焦点模式

    def wm_forget(self, window): # new in Tk 8.5
        """The window will be unmapped from the screen and will no longer
        be managed by wm. toplevel windows will be treated like frame
        windows once they are no longer managed by wm, however, the menu
        option configuration will be remembered and the menus will return
        once the widget is managed again."""
        self.tk.call('wm', 'forget', window)

    套路 管理_忽略(分身, 窗口):
        """窗口将不再由 wm 管理."""
        分身.wm_forget(窗口)

    forget = wm_forget
    忽略 = 管理_忽略

    def wm_frame(self):
        """返回此部件的装饰性框架的 id, 如果有的话."""
        return self.tk.call('wm', 'frame', self._w)

    框架 = 管理_框架 = wm_frame

    frame = wm_frame

    def wm_geometry(self, newGeometry=None):
        """Set geometry to NEWGEOMETRY of the form =widthxheight+x+y. Return
        current value if None is given."""
        return self.tk.call('wm', 'geometry', self._w, newGeometry)

    套路 管理_尺寸(分身, 新尺寸=空):
        """设置或返回几何尺寸, 格式为：'宽x高+水平偏移+垂直偏移'."""
        返回 分身.wm_geometry(新尺寸)

    geometry = wm_geometry
    尺寸 = 管理_尺寸

    def wm_grid(self,
         baseWidth=None, baseHeight=None,
         widthInc=None, heightInc=None):
        """Instruct the window manager that this widget shall only be
        resized on grid boundaries. WIDTHINC and HEIGHTINC are the width and
        height of a grid unit in pixels. BASEWIDTH and BASEHEIGHT are the
        number of grid units requested in Tk_GeometryRequest."""
        return self._getints(self.tk.call(
            'wm', 'grid', self._w,
            baseWidth, baseHeight, widthInc, heightInc))

    套路 管理_网格(分身, 基本宽度=空, 基本高度=空, 宽度增量=空, 高度增量=空):
        """指示窗口管理器, 此部件只应在网格边界上调整大小"""
        返回 分身.wm_grid(baseWidth=基本宽度, baseHeight=基本高度,
                        widthInc=宽度增量, heightInc=高度增量)

    grid = wm_grid
    网格 = 管理_网格

    def wm_group(self, pathName=None):
        """Set the group leader widgets for related widgets to PATHNAME. Return
        the group leader of this widget if None is given."""
        return self.tk.call('wm', 'group', self._w, pathName)

    套路 管理_分组(分身, 路径名=空):
        """设置或返回相关部件的分组主导部件"""
        返回 分身.wm_group(路径名)

    group = wm_group
    分组 = 管理_分组

    def wm_iconbitmap(self, bitmap=None, default=None):
        """Set bitmap for the iconified widget to BITMAP. Return
        the bitmap if None is given.

        Under Windows, the DEFAULT parameter can be used to set the icon
        for the widget and any descendents that don't have an icon set
        explicitly.  DEFAULT can be the relative path to a .ico file
        (example: root.iconbitmap(default='myicon.ico') ).  See Tk
        documentation for more information."""
        if default:
            return self.tk.call('wm', 'iconbitmap', self._w, '-default', default)
        else:
            return self.tk.call('wm', 'iconbitmap', self._w, bitmap)

    套路 管理_图标位图(分身, 位图=空, 默认值=空):
        "设置或返回图标化部件的位图"
        返回 分身.wm_iconbitmap(bitmap=位图, default=默认值)

    iconbitmap = wm_iconbitmap
    图标位图 = 管理_图标位图

    def wm_iconify(self):
        """将部件显示为图标."""
        return self.tk.call('wm', 'iconify', self._w)

    图标化 = 管理_图标化 = wm_iconify

    iconify = wm_iconify

    def wm_iconmask(self, bitmap=None):
        """Set mask for the icon bitmap of this widget. Return the
        mask if None is given."""
        return self.tk.call('wm', 'iconmask', self._w, bitmap)

    套路 管理_图标蒙版(分身, 位图=空):
        """设置或返回此部件的图标位图的蒙版"""
        返回 分身.wm_iconmask(位图)

    iconmask = wm_iconmask
    图标蒙版 = 管理_图标蒙版

    def wm_iconname(self, newName=None):
        """Set the name of the icon for this widget. Return the name if
        None is given."""
        return self.tk.call('wm', 'iconname', self._w, newName)

    套路 管理_图标名称(分身, 新名称=空):
        """设置或返回此部件的图标名称"""
        返回 分身.wm_iconname(新名称)

    iconname = wm_iconname
    图标名称 = 管理_图标名称

    def wm_iconphoto(self, default=False, *args): # new in Tk 8.5
        """Sets the titlebar icon for this window based on the named photo
        images passed through args. If default is True, this is applied to
        all future created toplevels as well.

        The data in the images is taken as a snapshot at the time of
        invocation. If the images are later changed, this is not reflected
        to the titlebar icons. Multiple images are accepted to allow
        different images sizes to be provided. The window manager may scale
        provided icons to an appropriate size.

        On Windows, the images are packed into a Windows icon structure.
        This will override an icon specified to wm_iconbitmap, and vice
        versa.

        On X, the images are arranged into the _NET_WM_ICON X property,
        which most modern window managers support. An icon specified by
        wm_iconbitmap may exist simultaneously.

        On Macintosh, this currently does nothing."""
        if default:
            self.tk.call('wm', 'iconphoto', self._w, "-default", *args)
        else:
            self.tk.call('wm', 'iconphoto', self._w, *args)

    套路 管理_图标照片(分身, 默认值=假, *参数):
        """基于参数传递的照片图像设置此窗口的标题栏图标. 如果 '默认值' 为真,
        则这也将应用于所有未来创建的顶级窗口."""
        分身.wm_iconphoto(默认值, *参数)

    iconphoto = wm_iconphoto
    图标照片 = 管理_图标照片

    def wm_iconposition(self, x=None, y=None):
        """设置或返回此部件的图标位置 X 和 Y."""
        return self._getints(self.tk.call(
            'wm', 'iconposition', self._w, x, y))

    图标位置 = 管理_图标位置 = wm_iconposition

    iconposition = wm_iconposition

    def wm_iconwindow(self, pathName=None):
        """Set widget PATHNAME to be displayed instead of icon. Return the current
        value if None is given."""
        return self.tk.call('wm', 'iconwindow', self._w, pathName)

    套路 管理_图标窗口(分身, 路径名=空):
        """设置或返回要代替图标显示的部件 '路径名'."""
        返回 分身.wm_iconwindow(路径名)

    iconwindow = wm_iconwindow
    图标窗口 = 管理_图标窗口

    def wm_manage(self, widget): # new in Tk 8.5
        """The widget specified will become a stand alone top-level window.
        The window will be decorated with the window managers title bar,
        etc."""
        self.tk.call('wm', 'manage', widget)

    套路 管理_管理(分身, 部件):
        """指定的部件将成为独立的顶级窗口. 该窗口将用窗口管理器的标题栏等装饰."""
        分身.wm_manage(部件)

    manage = wm_manage
    管理 = 管理_管理

    def wm_maxsize(self, width=None, height=None):
        """Set max WIDTH and HEIGHT for this widget. If the window is gridded
        the values are given in grid units. Return the current values if None
        is given."""
        return self._getints(self.tk.call(
            'wm', 'maxsize', self._w, width, height))
    
    套路 管理_最大大小(分身, 宽度=空, 高度=空):
        """设置或返回此部件的最大宽度和高度"""
        返回 分身.wm_maxsize(width=宽度, height=高度)

    maxsize = wm_maxsize
    最大大小 = 管理_最大大小

    def wm_minsize(self, width=None, height=None):
        """Set min WIDTH and HEIGHT for this widget. If the window is gridded
        the values are given in grid units. Return the current values if None
        is given."""
        return self._getints(self.tk.call(
            'wm', 'minsize', self._w, width, height))

    套路 管理_最小大小(分身, 宽度=空, 高度=空):
        """设置或返回此部件的最小宽度和高度"""
        返回 分身.wm_minsize(width=宽度, height=高度)

    minsize = wm_minsize
    最小大小 = 管理_最小大小

    def wm_overrideredirect(self, boolean=None):
        """Instruct the window manager to ignore this widget
        if BOOLEAN is given with 1. Return the current value if None
        is given."""
        return self._getboolean(self.tk.call(
            'wm', 'overrideredirect', self._w, boolean))

    套路 管理_无视(分身, 布尔值=空):
        """如果 '布尔值' 为 1, 则指示窗口管理器忽略此部件. 如果未给定 '布尔值',
        则返回当前值."""
        返回 分身.wm_overrideredirect(布尔值)

    overrideredirect = wm_overrideredirect
    无视 = 管理_无视

    def wm_positionfrom(self, who=None):
        """Instruct the window manager that the position of this widget shall
        be defined by the user if WHO is "user", and by its own policy if WHO is
        "program"."""
        return self.tk.call('wm', 'positionfrom', self._w, who)

    套路 管理_定位者(分身, 定位者=空):
        """指示此部件应当由何者定位. 定位者可以是 '用户' 或 '程序'."""
        如果 定位者 == '用户':
            定位者 = 'user'
        或如 定位者 == '程序':
            定位者 = 'program'
        返回 分身.wm_positionfrom(定位者)

    positionfrom = wm_positionfrom
    定位者 = 管理_定位者

    def wm_protocol(self, name=None, func=None):
        """Bind function FUNC to command NAME for this widget.
        Return the function bound to NAME if None is given. NAME could be
        e.g. "WM_SAVE_YOURSELF" or "WM_DELETE_WINDOW"."""
        if callable(func):
            command = self._register(func)
        else:
            command = func
        return self.tk.call(
            'wm', 'protocol', self._w, name, command)

    套路 管理_协议(分身, 名称=空, 函数=空):
        """将 '函数' 绑定到此部件的 '名称' 命令.
        如果未指定, 则返回绑定到 '名称' 的函数."""
        返回 分身.wm_protocol(name=名称, func=函数)

    protocol = wm_protocol
    协议 = 管理_协议

    def wm_resizable(self, width=None, height=None):
        """Instruct the window manager whether this width can be resized
        in WIDTH or HEIGHT. Both values are boolean values."""
        return self.tk.call('wm', 'resizable', self._w, width, height)

    套路 管理_可调整(分身, 宽度=空, 高度=空):
        """指示此部件的宽度或高度是否可以调整. 两个参数均为布尔值."""
        返回 分身.wm_resizable(width=宽度, height=高度)

    resizable = wm_resizable
    可调整 = 管理_可调整

    def wm_sizefrom(self, who=None):
        """Instruct the window manager that the size of this widget shall
        be defined by the user if WHO is "user", and by its own policy if WHO is
        "program"."""
        return self.tk.call('wm', 'sizefrom', self._w, who)

    套路 管理_定大小者(分身, 定大小者=空):
        """指示此部件应当由何者确定大小. 定大小者可以是 '用户' 或 '程序'."""
        如果 定大小者 == '用户':
            定大小者 = 'user'
        或如 定大小者 == '程序':
            定大小者 = 'program'
        返回 分身.wm_sizefrom(定大小者)

    sizefrom = wm_sizefrom
    定大小者 = 管理_定大小者

    def wm_state(self, newstate=None):
        """Query or set the state of this widget as one of normal, icon,
        iconic (see wm_iconwindow), withdrawn, or zoomed (Windows only)."""
        return self.tk.call('wm', 'state', self._w, newstate)

    套路 管理_状态(分身, 新状态=空):
        """返回或设置此部件的状态."""
        返回 分身.wm_state(新状态)

    state = wm_state
    状态 = 管理_状态

    def wm_title(self, string=None):
        """Set the title of this widget."""
        return self.tk.call('wm', 'title', self._w, string)

    套路 管理_标题(分身, 字符串=空):
        """设置此部件的标题"""
        返回 分身.wm_title(字符串)

    title = wm_title
    标题 = 管理_标题

    def wm_transient(self, master=None):
        """Instruct the window manager that this widget is transient
        with regard to widget MASTER."""
        return self.tk.call('wm', 'transient', self._w, master)

    套路 管理_短暂(分身, 主对象=空):
        """告知窗口管理器此部件相对于主对象是转瞬即逝的"""
        返回 分身.wm_transient(主对象)

    transient = wm_transient
    短暂 = 管理_短暂

    def wm_withdraw(self):
        """从屏幕撤回此部件, 使它被窗口管理器解除映射并遗忘.
        当调用 '管理_解除图标化()' 时会重绘."""
        return self.tk.call('wm', 'withdraw', self._w)

    撤回 = 管理_撤回 = wm_withdraw

    withdraw = wm_withdraw

窗口管理类 = Wm


class Tk(Misc, Wm):
    """Toplevel widget of Tk which represents mostly the main window
    of an application. It has an associated Tcl interpreter."""
    _w = '.'

    def __init__(self, screenName=None, baseName=None, className='Tk',
                 useTk=1, sync=0, use=None):
        """Return a new Toplevel widget on screen SCREENNAME. A new Tcl interpreter will
        be created. BASENAME will be used for the identification of the profile file (see
        readprofile).
        It is constructed from sys.argv[0] without extensions if None is given. CLASSNAME
        is the name of the widget class."""
        self.master = None
        self.children = {}
        self._tkloaded = 0
        # to avoid recursions in the getattr code in case of failure, we
        # ensure that self.tk is always _something_.
        self.tk = None
        if baseName is None:
            import os
            baseName = os.path.basename(sys.argv[0])
            baseName, ext = os.path.splitext(baseName)
            if ext not in ('.py', '.pyc'):
                baseName = baseName + ext
        interactive = 0
        self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
        if useTk:
            self._loadtk()
        if not sys.flags.ignore_environment:
            # Issue #16248: Honor the -E flag to avoid code injection.
            self.readprofile(baseName, className)

    def loadtk(self):
        if not self._tkloaded:
            self.tk.loadtk()
            self._loadtk()

    def _loadtk(self):
        self._tkloaded = 1
        global _default_root
        # Version sanity checks
        tk_version = self.tk.getvar('tk_version')
        if tk_version != _tkinter.TK_VERSION:
            raise RuntimeError("tk.h version (%s) doesn't match libtk.a version (%s)"
                               % (_tkinter.TK_VERSION, tk_version))
        # Under unknown circumstances, tcl_version gets coerced to float
        tcl_version = str(self.tk.getvar('tcl_version'))
        if tcl_version != _tkinter.TCL_VERSION:
            raise RuntimeError("tcl.h version (%s) doesn't match libtcl.a version (%s)" \
                               % (_tkinter.TCL_VERSION, tcl_version))
        # Create and register the tkerror and exit commands
        # We need to inline parts of _register here, _ register
        # would register differently-named commands.
        if self._tclCommands is None:
            self._tclCommands = []
        self.tk.createcommand('tkerror', _tkerror)
        self.tk.createcommand('exit', _exit)
        self._tclCommands.append('tkerror')
        self._tclCommands.append('exit')
        if _support_default_root and not _default_root:
            _default_root = self
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def destroy(self):
        """Destroy this and all descendants widgets. This will
        end the application of this Tcl interpreter."""
        for c in list(self.children.values()): c.destroy()
        self.tk.call('destroy', self._w)
        Misc.destroy(self)
        global _default_root
        if _support_default_root and _default_root is self:
            _default_root = None

    # 销毁 = destroy

    def readprofile(self, baseName, className):
        """Internal function. It reads BASENAME.tcl and CLASSNAME.tcl into
        the Tcl Interpreter and calls exec on the contents of BASENAME.py and
        CLASSNAME.py if such a file exists in the home directory."""
        import os
        if 'HOME' in os.environ: home = os.environ['HOME']
        else: home = os.curdir
        class_tcl = os.path.join(home, '.%s.tcl' % className)
        class_py = os.path.join(home, '.%s.py' % className)
        base_tcl = os.path.join(home, '.%s.tcl' % baseName)
        base_py = os.path.join(home, '.%s.py' % baseName)
        dir = {'self': self}
        exec('from tkinter import *', dir)
        if os.path.isfile(class_tcl):
            self.tk.call('source', class_tcl)
        if os.path.isfile(class_py):
            exec(open(class_py).read(), dir)
        if os.path.isfile(base_tcl):
            self.tk.call('source', base_tcl)
        if os.path.isfile(base_py):
            exec(open(base_py).read(), dir)

    def report_callback_exception(self, exc, val, tb):
        """Report callback exception on sys.stderr.

        Applications may want to override this internal function, and
        should when sys.stderr is None."""
        import traceback
        print("Exception in Tkinter callback", file=sys.stderr)
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        traceback.print_exception(exc, val, tb)

    def __getattr__(self, attr):
        "Delegate attribute access to the interpreter object"
        return getattr(self.tk, attr)


类 〇主窗口(tkinter.Tk, Tk): 
    """大多数情况下代表应用程序的主窗口."""
    # 待解决: 使用 Tk() 或仅继承 Tk 的话, 弹出消息框的同时会弹出一个 tk 窗口.
    套路 __init__(分身, 屏幕名称=空, 基本名称=空, 类名='Tk', 使用Tk=1, 同步=0, 使用=空):
        全局 _default_root
        tkinter.Tk.__init__(分身, screenName=屏幕名称, baseName=基本名称, className=类名,
                    useTk=使用Tk, sync=同步, use=使用)
        _default_root = 分身 # 为 '变量类' 及其子类提供默认根

    套路 配置(分身, 配置字典=空, **关键词参数):
        _选项字典 = {
            '菜单': 'menu',
        }
        关键词参数 = _关键词参数中转英(关键词参数, _选项字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)

    套路 销毁(分身):
        """销毁自身及所有子孙部件. 终结应用程序."""
        分身.destroy()
    

# Ideally, the classes Pack, Place and Grid disappear, the
# pack/place/grid methods are defined on the Widget class, and
# everybody uses w.pack_whatever(...) instead of Pack.whatever(w,
# ...), with pack(), place() and grid() being short for
# pack_configure(), place_configure() and grid_columnconfigure(), and
# forget() being short for pack_forget().  As a practical matter, I'm
# afraid that there is too much code out there that may be using the
# Pack, Place or Grid class, so I leave them intact -- but only as
# backwards compatibility features.  Also note that those methods that
# take a master as argument (e.g. pack_propagate) have been moved to
# the Misc class (which now incorporates all methods common between
# toplevel and interior widgets).  Again, for compatibility, these are
# copied into the Pack, Place or Grid class.


def Tcl(screenName=None, baseName=None, className='Tk', useTk=0):
    return Tk(screenName, baseName, className, useTk)


class Pack:
    """在每个部件中提供 '常规布局_*' 之类方法的基本类."""

    def pack_configure(self, cnf={}, **kw):
        """Pack a widget in the parent widget. Use as options:
        after=widget - pack it after you have packed widget
        anchor=NSEW (or subset) - position widget according to
                                  given direction
        before=widget - pack it before you will pack widget
        expand=bool - expand widget if parent size grows
        fill=NONE or X or Y or BOTH - fill widget if widget grows
        in=master - use master to contain this widget
        in_=master - see 'in' option description
        ipadx=amount - add internal padding in x direction
        ipady=amount - add internal padding in y direction
        padx=amount - add padding in x direction
        pady=amount - add padding in y direction
        side=TOP or BOTTOM or LEFT or RIGHT -  where to add this widget.
        """
        self.tk.call(
              ('pack', 'configure', self._w)
              + self._options(cnf, kw))

    pack = configure = config = pack_configure

    套路 常规布局(分身, 配置字典={}, **关键词参数):
        """以常规布局在父部件中放置一个部件. 选项如下:\n
        前面部件: 此部件之前的部件\n
        锚点='上下左右'(或其任意子集) 或 '居中'\n
        后面部件: 此部件之后的部件\n
        扩展=真/假, 是否随着父部件扩大而扩大\n
        填充='无' 或 'x' 或 'y' 或 '同时', 随着部件扩大而填充部件\n
        主对象: 使用主对象来包含此部件\n
        内水平边距: x 方向的内边距\n
        内垂直边距: y 方向的内边距\n
        水平边距: x 方向的边距\n
        垂直边距: y 方向的边距\n
        边='左边' 或 '右边' 或 '顶边' 或 '底边', 把部件添加到哪里
        """
        常规布局选项字典 = {
            '前面部件':     'after',
            '锚点':         'anchor',
            '后面部件':     'before',
            '扩展':         'expand',
            '填充':         'fill',
            '主对象':       'in_',
            '内水平边距':   'ipadx',
            '内垂直边距':   'ipady',
            '水平边距':     'padx',
            '垂直边距':     'pady',
            '边':           'side'
        }
        常规布局选项值字典 = {
            '无':   'none',
            '水平': 'x',
            '垂直': 'y',
            '同时': 'both',
            '左边': 'left',
            '右边': 'right',
            '顶边': 'top',
            '底边': 'bottom',
        }
        常规布局选项值字典.更新(_锚点字典)
        关键词参数 = _关键词参数中转英(关键词参数, 常规布局选项字典, 常规布局选项值字典)
        分身.pack_configure(cnf=配置字典, **关键词参数)

    def pack_forget(self):
        """取消映射此部件, 使其不在布局顺序中."""
        self.tk.call('pack', 'forget', self._w)

    常规布局_忽略 = pack_forget

    forget = pack_forget

    def pack_info(self):
        """返回有关此部件的常规布局选项的信息."""
        d = _splitdict(self.tk, self.tk.call('pack', 'info', self._w))
        if 'in' in d:
            d['in'] = self.nametowidget(d['in'])
        return d

    常规布局_信息 = pack_info

    info = pack_info
    propagate = pack_propagate = Misc.pack_propagate
    slaves = pack_slaves = Misc.pack_slaves

    常规布局_自适应尺寸 = Misc.常规布局_自适应尺寸
    常规布局_从属对象 = Misc.常规布局_从属对象

常规布局类 = Pack

class Place:
    """在每个部件中提供 '位置布局_*' 之类方法的基本类."""

    def place_configure(self, cnf={}, **kw):
        """Place a widget in the parent widget. Use as options:
        in=master - master relative to which the widget is placed
        in_=master - see 'in' option description
        x=amount - locate anchor of this widget at position x of master
        y=amount - locate anchor of this widget at position y of master
        relx=amount - locate anchor of this widget between 0.0 and 1.0
                      relative to width of master (1.0 is right edge)
        rely=amount - locate anchor of this widget between 0.0 and 1.0
                      relative to height of master (1.0 is bottom edge)
        anchor=NSEW (or subset) - position anchor according to given direction
        width=amount - width of this widget in pixel
        height=amount - height of this widget in pixel
        relwidth=amount - width of this widget between 0.0 and 1.0
                          relative to width of master (1.0 is the same width
                          as the master)
        relheight=amount - height of this widget between 0.0 and 1.0
                           relative to height of master (1.0 is the same
                           height as the master)
        bordermode="inside" or "outside" - whether to take border width of
                                           master widget into account
        """
        self.tk.call(
              ('place', 'configure', self._w)
              + self._options(cnf, kw))

    套路 位置布局(分身, 配置字典={}, **关键词参数):
        """以位置布局在父部件中放置一个部件. 选项如下:\n
        主对象: 此部件相对于主对象放置\n
        x: 将此部件的锚点放在主对象的位置 x\n
        y: 将此部件的锚点放在主对象的位置 y\n
        相对x: 将此部件的锚点放在相对于主对象宽度的 0.0 到 1.0 倍之间 (1.0 为右边)\n
        相对y: 将此部件的锚点放在相对于主对象高度的 0.0 到 1.0 倍之间 (1.0 为底边)\n
        锚点='上下左右'(或其任意子集) 或 '居中'\n
        宽度: 此部件的宽度, 以像素为单位\n
        高度: 此部件的高度, 以像素为单位\n
        相对宽度: 此部件宽度相对于主对象宽度的比例, 0.0 到 1.0 之间, 1.0 为同宽\n
        相对高度: 此部件高度相对于主对象高度的比例, 0.0 到 1.0 之间, 1.0 为同高\n
        边框模式 = '内部' 或 '外部', 是否考虑主部件的边框宽度
        """
        位置布局选项字典 = {
            '主对象':   'in_',
            '相对x':    'relx',
            '相对y':    'rely',
            '锚点':     'anchor',
            '宽度':     'width',
            '高度':     'height',
            '相对宽度': 'relwidth',
            '相对高度': 'relheight',
            '边框模式': 'bordermode'
        }
        位置布局选项值字典 = {
            '内部': 'inside',
            '外部': 'outside'
        }
        位置布局选项值字典.更新(_锚点字典)
        关键词参数 = _关键词参数中转英(关键词参数, 位置布局选项字典, 位置布局选项值字典)
        分身.place_configure(cnf=配置字典, **关键词参数)

    place = configure = config = place_configure

    def place_forget(self):
        """取消映射此部件."""
        self.tk.call('place', 'forget', self._w)

    位置布局_忽略 = place_forget

    forget = place_forget

    def place_info(self):
        """返回有关此部件的位置布局选项的信息."""
        d = _splitdict(self.tk, self.tk.call('place', 'info', self._w))
        if 'in' in d:
            d['in'] = self.nametowidget(d['in'])
        return d

    位置布局_信息 = place_info

    info = place_info
    slaves = place_slaves = Misc.place_slaves

    位置布局_从属对象 = Misc.位置布局_从属对象

位置布局类 = Place

class Grid:
    """在每个部件中提供 '网格布局_*' 之类方法的基本类."""
    # Thanks to Masazumi Yoshikawa (yosikawa@isi.edu)

    def grid_configure(self, cnf={}, **kw):
        """Position a widget in the parent widget in a grid. Use as options:
        column=number - use cell identified with given column (starting with 0)
        columnspan=number - this widget will span several columns
        in=master - use master to contain this widget
        in_=master - see 'in' option description
        ipadx=amount - add internal padding in x direction
        ipady=amount - add internal padding in y direction
        padx=amount - add padding in x direction
        pady=amount - add padding in y direction
        row=number - use cell identified with given row (starting with 0)
        rowspan=number - this widget will span several rows
        sticky=NSEW - if cell is larger on which sides will this
                      widget stick to the cell boundary
        """
        self.tk.call(
              ('grid', 'configure', self._w)
              + self._options(cnf, kw))

    套路 网格布局(分身, 配置字典={}, **关键词参数):
        """以网格布局在父部件中放置一个部件. 选项如下:\n
        列: 使用给定列号 (从 0 开始) 表示的单元\n
        跨列: 此部件将跨几列\n
        行: 使用给定行号 (从 0 开始) 表示的单元\n
        跨行: 此部件将跨几行\n
        主对象: 使用主对象来包含此部件\n
        内水平边距: x 方向的内边距\n
        内垂直边距: y 方向的内边距\n
        水平边距: x 方向的边距\n
        垂直边距: y 方向的边距\n
        贴边='上下左右'(或其任意子集) 或 '居中';
        如果单元较大, 此部件应贴哪些 (哪一) 边放置
        """
        网格布局选项字典 = {
            '列':           'column',
            '跨列':         'columnspan',
            '行':           'row',
            '跨行':         'rowspan',
            '主对象':       'in_',
            '内水平边距':   'ipadx',
            '内垂直边距':   'ipady',
            '水平边距':     'padx',
            '垂直边距':     'pady',
            '贴边':         'sticky'
        }
        网格布局选项值字典 = _锚点字典
        关键词参数 = _关键词参数中转英(关键词参数, 网格布局选项字典, 网格布局选项值字典)
        分身.grid_configure(cnf=配置字典, **关键词参数)

    grid = configure = config = grid_configure
    bbox = grid_bbox = Misc.grid_bbox
    columnconfigure = grid_columnconfigure = Misc.grid_columnconfigure

    网格布局_包围盒 = Misc.网格布局_包围盒
    网格布局_列配置 = Misc.网格布局_列配置

    def grid_forget(self):
        """取消映射此部件."""
        self.tk.call('grid', 'forget', self._w)

    网格布局_忽略 = grid_forget

    forget = grid_forget

    def grid_remove(self):
        """取消映射此部件, 但记住网格布局选项."""
        self.tk.call('grid', 'remove', self._w)

    网格布局_移除 = grid_remove

    def grid_info(self):
        """返回有关此部件的网格布局选项的信息."""
        d = _splitdict(self.tk, self.tk.call('grid', 'info', self._w))
        if 'in' in d:
            d['in'] = self.nametowidget(d['in'])
        return d

    网格布局_信息 = grid_info

    info = grid_info
    location = grid_location = Misc.grid_location
    propagate = grid_propagate = Misc.grid_propagate
    rowconfigure = grid_rowconfigure = Misc.grid_rowconfigure
    size = grid_size = Misc.grid_size
    slaves = grid_slaves = Misc.grid_slaves

    网格布局_位置 = Misc.网格布局_位置
    网格布局_自适应尺寸 = Misc.网格布局_自适应尺寸
    网格布局_行配置 = Misc.网格布局_行配置
    网格布局_大小 = Misc.网格布局_大小
    网格布局_从属对象 = Misc.网格布局_从属对象

网格布局类 = Grid

class BaseWidget(Misc):
    """Internal class."""

    def _setup(self, master, cnf):
        """Internal function. Sets up information about children."""
        if _support_default_root:
            global _default_root
            if not master:
                if not _default_root:
                    _default_root = Tk()
                master = _default_root
        self.master = master
        self.tk = master.tk
        name = None
        if 'name' in cnf:
            name = cnf['name']
            del cnf['name']
        if not name:
            name = self.__class__.__name__.lower()
            if master._last_child_ids is None:
                master._last_child_ids = {}
            count = master._last_child_ids.get(name, 0) + 1
            master._last_child_ids[name] = count
            if count == 1:
                name = '!%s' % (name,)
            else:
                name = '!%s%d' % (name, count)
        self._name = name
        if master._w=='.':
            self._w = '.' + name
        else:
            self._w = master._w + '.' + name
        self.children = {}
        if self._name in self.master.children:
            self.master.children[self._name].destroy()
        self.master.children[self._name] = self

    def __init__(self, master, widgetName, cnf={}, kw={}, extra=()):
        """Construct a widget with the parent widget MASTER, a name WIDGETNAME
        and appropriate options."""
        if kw:
            cnf = _cnfmerge((cnf, kw))
        self.widgetName = widgetName
        BaseWidget._setup(self, master, cnf)
        if self._tclCommands is None:
            self._tclCommands = []
        classes = [(k, v) for k, v in cnf.items() if isinstance(k, type)]
        for k, v in classes:
            del cnf[k]
        self.tk.call(
            (widgetName, self._w) + extra + self._options(cnf))
        for k, v in classes:
            k.configure(self, v)

    def destroy(self):
        """销毁此部件及其所有子孙部件."""
        for c in list(self.children.values()): c.destroy()
        self.tk.call('destroy', self._w)
        if self._name in self.master.children:
            del self.master.children[self._name]
        Misc.destroy(self)

    销毁 = destroy

    def _do(self, name, args=()):
        # XXX Obsolete -- better use self.tk.call directly!
        return self.tk.call((self._w, name) + args)


class Widget(BaseWidget, Pack, Place, Grid):
    """Internal class.

    Base class for a widget which can be positioned with the geometry managers
    Pack, Place or Grid."""
    pass


class Toplevel(BaseWidget, Wm):
    """Toplevel widget, e.g. for dialogs."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a toplevel widget with the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, menu, relief, screen, takefocus,
        use, visual, width."""
        if kw:
            cnf = _cnfmerge((cnf, kw))
        extra = ()
        for wmkey in ['screen', 'class_', 'class', 'visual',
                  'colormap']:
            if wmkey in cnf:
                val = cnf[wmkey]
                # TBD: a hack needed because some keys
                # are not valid as keyword arguments
                if wmkey[-1] == '_': opt = '-'+wmkey[:-1]
                else: opt = '-'+wmkey
                extra = extra + (opt, val)
                del cnf[wmkey]
        BaseWidget.__init__(self, master, 'toplevel', cnf, {}, extra)
        root = self._root()
        self.iconname(root.iconname())
        self.title(root.title())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

类 〇顶级窗口(Toplevel):
    """顶级部件, 例如用于对话框."""
    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """使用父级主对象构造一个顶级部件. 选项如下:

        背景色, 边框宽度, 类_, 颜色映射, 容器, 鼠标样式, 高度, 高亮背景,
        高亮颜色, 高亮厚度, 菜单, 边框样式, 屏幕, 获得焦点, 使用, 视觉, 宽度.
        """
        分身._顶级选项字典 = {
            '背景色':       'background', 
            '边框宽度':     'borderwidth',
            '类_':          'class_',
            '颜色映射':     'colormap', 
            '容器':         'container', 
            '鼠标样式':     'cursor',
            '高度':         'height', 
            '高亮背景':     'highlightbackground', 
            '高亮颜色':     'highlightcolor',
            '高亮厚度':     'highlightthickness', 
            '菜单':         'menu', 
            '边框样式':     'relief', 
            '屏幕':         'screen', 
            '获得焦点':     'takefocus', 
            '使用':         'use', 
            '视觉':         'visual', 
            '宽度':         'width'
        }
        分身._顶级选项值字典 = {

        }
        分身._顶级选项值字典.更新(_颜色字典)
        分身._顶级选项值字典.更新(_边框样式字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._顶级选项字典, 分身._顶级选项值字典)
        Toplevel.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)

    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._顶级选项字典, 分身._顶级选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Button(Widget):
    """Button widget."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a button widget with the parent MASTER.

        STANDARD OPTIONS

            activebackground, activeforeground, anchor,
            background, bitmap, borderwidth, cursor,
            disabledforeground, font, foreground
            highlightbackground, highlightcolor,
            highlightthickness, image, justify,
            padx, pady, relief, repeatdelay,
            repeatinterval, takefocus, text,
            textvariable, underline, wraplength

        WIDGET-SPECIFIC OPTIONS

            command, compound, default, height,
            overrelief, state, width
        """
        Widget.__init__(self, master, 'button', cnf, kw)

    def flash(self):
        """让按钮闪烁.

        This is accomplished by redisplaying
        the button several times, alternating between active and
        normal colors. At the end of the flash the button is left
        in the same normal/active state as when the command was
        invoked. This command is ignored if the button's state is
        disabled.
        """
        self.tk.call(self._w, 'flash')

    闪烁 = flash

    def invoke(self):
        """调用与此按钮相关联的命令.

        返回值为命令的返回值, 如果按钮没有关联命令则返回空字符串.
        如果按钮的状态为禁用, 则忽略此命令.
        """
        return self.tk.call(self._w, 'invoke')

    调用 = invoke

类 〇按钮(Button):
    """按钮部件."""
    
    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """在父级主对象中构建一个按钮部件.

        标准选项: 活动背景色, 活动前景色, 锚点, 背景色, 位图, 边框宽度, 鼠标样式,
        禁用时前景色, 字体, 前景色, 高亮背景, 高亮颜色, 高亮厚度, 图像, 对齐,
        水平边距, 垂直边距, 边框样式, 重复延迟, 重复间隔, 获得焦点, 文本,
        文本变量, 下划线, 分行长度

        该部件特定的选项: 命令, 混合模式, 默认值, 高度, 悬停样式, 状态, 宽度

        """
        分身._按钮选项字典 = {
            '命令':     'command', 
            '混合模式': 'compound', 
            '默认值':     'default', 
            '高度':     'height',
            '悬停样式': 'overrelief', 
            '重复延迟': 'repeatdelay',
            '重复间隔': 'repeatinterval',             
            '状态':     'state', 
            '宽度':     'width'
        }
        分身._按钮选项字典.更新(_部件通用选项字典)
        分身._按钮选项值字典 = {
            '上方': 'top',
            '下方': 'bottom',
            '无':   'none',
            '正常': 'normal',
            '活动': 'active',
            '禁用': 'disabled'
        }
        分身._按钮选项值字典.更新(_部件通用选项值字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._按钮选项字典, 分身._按钮选项值字典)
        Button.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)
    
    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._按钮选项字典, 分身._按钮选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Canvas(Widget, XView, YView):
    """Canvas widget to display graphical elements like lines or text."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a canvas widget with the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, closeenough,
        confine, cursor, height, highlightbackground, highlightcolor,
        highlightthickness, insertbackground, insertborderwidth,
        insertofftime, insertontime, insertwidth, offset, relief,
        scrollregion, selectbackground, selectborderwidth, selectforeground,
        state, takefocus, width, xscrollcommand, xscrollincrement,
        yscrollcommand, yscrollincrement."""
        Widget.__init__(self, master, 'canvas', cnf, kw)

    def addtag(self, *args):
        """Internal function."""
        self.tk.call((self._w, 'addtag') + args)

    def addtag_above(self, newtag, tagOrId):
        """Add tag NEWTAG to all items above TAGORID."""
        self.addtag(newtag, 'above', tagOrId)

    套路 添加标志_之上(分身, 新标志, 标志或Id):
        """给 '标志或Id' 之上的所有项目添加 '新标志'."""
        分身.addtag(新标志, 'above', 标志或Id)

    def addtag_all(self, newtag):
        """Add tag NEWTAG to all items."""
        self.addtag(newtag, 'all')

    套路 添加标志_全部(分身, 新标志):
        """给所有项目添加 '新标志'."""
        分身.addtag(新标志, 'all')

    def addtag_below(self, newtag, tagOrId):
        """Add tag NEWTAG to all items below TAGORID."""
        self.addtag(newtag, 'below', tagOrId)

    套路 添加标志_之下(分身, 新标志, 标志或Id):
        """给 '标志或Id' 之下的所有项目添加 '新标志'."""
        分身.addtag(新标志, 'below', 标志或Id)

    def addtag_closest(self, newtag, x, y, halo=None, start=None):
        """Add tag NEWTAG to item which is closest to pixel at X, Y.
        If several match take the top-most.
        All items closer than HALO are considered overlapping (all are
        closests). If START is specified the next below this tag is taken."""
        self.addtag(newtag, 'closest', x, y, halo, start)

    套路 添加标志_最接近(分身, 新标志, x, y, 环=空, 起始=空):
        """给最接近 (x, y) 像素的项目添加 '新标志'.
        如有多个匹配, 取最上方的.
        所有比 '环' 还近的项目被认为重叠 (全都是最接近的).
        如果指定了 '起始', 则取此标志之下的下一个."""
        分身.addtag(新标志, 'closest', x, y, halo=环, start=起始)

    def addtag_enclosed(self, newtag, x1, y1, x2, y2):
        """Add tag NEWTAG to all items in the rectangle defined
        by X1,Y1,X2,Y2."""
        self.addtag(newtag, 'enclosed', x1, y1, x2, y2)

    套路 添加标志_矩形内(分身, 新标志, x1, y1, x2, y2):
        """给 X1,Y1,X2,Y2 定义的矩形内的所有项目添加 '新标志'."""
        分身.addtag(新标志, 'enclosed', x1, y1, x2, y2)

    def addtag_overlapping(self, newtag, x1, y1, x2, y2):
        """Add tag NEWTAG to all items which overlap the rectangle
        defined by X1,Y1,X2,Y2."""
        self.addtag(newtag, 'overlapping', x1, y1, x2, y2)

    套路 添加标志_交叠(分身, 新标志, x1, y1, x2, y2):
        """给与 X1,Y1,X2,Y2 定义的矩形交叠的所有项目添加 '新标志'."""
        分身.addtag(新标志, 'overlapping', x1, y1, x2, y2)

    def addtag_withtag(self, newtag, tagOrId):
        """Add tag NEWTAG to all items with TAGORID."""
        self.addtag(newtag, 'withtag', tagOrId)

    套路 添加标志_有标志(分身, 新标志, 标志或Id):
        """给所有具 '标志或Id' 的项目添加 '新标志'."""
        分身.addtag(新标志, 'withtag', 标志或Id)

    def bbox(self, *args):
        """Return a tuple of X1,Y1,X2,Y2 coordinates for a rectangle
        which encloses all items with tags specified as arguments."""
        return self._getints(
            self.tk.call((self._w, 'bbox') + args)) or None

    套路 包围盒(分身, *参数):
        """返回一个矩形的 X1,Y1,X2,Y2 坐标元组, 该矩形包围所有具有
        '参数' 所指定标志的项目."""
        返回 分身._getints(
            分身.tk.call((分身._w, 'bbox') + 参数)) or None

    def tag_unbind(self, tagOrId, sequence, funcid=None):
        """Unbind for all items with TAGORID for event SEQUENCE  the
        function identified with FUNCID."""
        self.tk.call(self._w, 'bind', tagOrId, sequence, '')
        if funcid:
            self.deletecommand(funcid)

    套路 标志_解除绑定(分身, 标志或Id, 序列, 函数id=空):
        """解除所有具有 '标志或Id' 的项目的事件 '序列' 绑定的 '函数id'."""
        分身.tk.call(分身._w, 'bind', 标志或Id, 序列, '')
        if 函数id:
            分身.deletecommand(函数id)

    def tag_bind(self, tagOrId, sequence=None, func=None, add=None):
        """Bind to all items with TAGORID at event SEQUENCE a call to function FUNC.

        An additional boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function or whether it will
        replace the previous function. See bind for the return value."""
        return self._bind((self._w, 'bind', tagOrId),
                  sequence, func, add)

    套路 标志_绑定(分身, 标志或Id, 序列=空, 函数=空, 添加=空):
        """给所有具有 '标志或Id' 的项目的事件 '序列' 绑定对 '函数' 的调用.

        '添加' 为布尔值参数, 决定 '函数' 是取代先前绑定的函数还是另外添加.
        返回值参见 '绑定' 方法."""
        返回 分身._bind((分身._w, 'bind', 标志或Id),
                  sequence=序列, func=函数, add=添加)

    def canvasx(self, screenx, gridspacing=None):
        """Return the canvas x coordinate of pixel position SCREENX rounded
        to nearest multiple of GRIDSPACING units."""
        return self.tk.getdouble(self.tk.call(
            self._w, 'canvasx', screenx, gridspacing))

    套路 画布x(分身, 屏幕x, 网格间距=空):
        """返回像素位置 '屏幕x' 的画布 x 坐标,
        舍入到最接近的 '网格间距' 整数倍."""
        返回 分身.tk.getdouble(分身.tk.call(
            分身._w, 'canvasx', 屏幕x, 网格间距))

    def canvasy(self, screeny, gridspacing=None):
        """Return the canvas y coordinate of pixel position SCREENY rounded
        to nearest multiple of GRIDSPACING units."""
        return self.tk.getdouble(self.tk.call(
            self._w, 'canvasy', screeny, gridspacing))

    套路 画布y(分身, 屏幕y, 网格间距=空):
        """返回像素位置 '屏幕y' 的画布 y 坐标,
        舍入到最接近的 '网格间距' 整数倍."""
        返回 分身.tk.getdouble(分身.tk.call(
            分身._w, 'canvasy', 屏幕y, 网格间距))

    def coords(self, *args):
        """Return a list of coordinates for the item given in ARGS."""
        # XXX Should use _flatten on args
        return [self.tk.getdouble(x) for x in
                           self.tk.splitlist(
                   self.tk.call((self._w, 'coords') + args))]

    套路 坐标(分身, *参数):
        """返回 '参数' 给定的项目的坐标列表."""
        返回 [分身.tk.getdouble(x) for x in
                           分身.tk.splitlist(
                   分身.tk.call((分身._w, 'coords') + 参数))]

    def _create(self, itemType, args, kw): # Args: (val, val, ..., cnf={})
        """Internal function."""
        args = _flatten(args)
        cnf = args[-1]
        if isinstance(cnf, (dict, tuple)):
            args = args[:-1]
        else:
            cnf = {}
        return self.tk.getint(self.tk.call(
            self._w, 'create', itemType,
            *(args + self._options(cnf, kw))))

    def create_arc(self, *args, **kw):
        """Create arc shaped region with coordinates x1,y1,x2,y2."""
        return self._create('arc', args, kw)

    套路 创建弧(分身, *参数, **关键词参数):
        """用坐标 x1,y1,x2,y2 创建弧形区域."""
        返回 分身._create('arc', 参数, 关键词参数)

    def create_bitmap(self, *args, **kw):
        """Create bitmap with coordinates x1,y1."""
        return self._create('bitmap', args, kw)

    套路 创建位图(分身, *参数, **关键词参数):
        """用坐标 x1,y1 创建位图."""
        返回 分身._create('bitmap', 参数, 关键词参数)

    def create_image(self, *args, **kw):
        """Create image item with coordinates x1,y1."""
        return self._create('image', args, kw)

    套路 创建图像(分身, *参数, **关键词参数):
        """用坐标 x1,y1 创建图像."""
        返回 分身._create('image', 参数, 关键词参数)

    def create_line(self, *args, **kw):
        """Create line with coordinates x1,y1,...,xn,yn."""
        return self._create('line', args, kw)

    套路 创建线段(分身, *参数, **关键词参数):
        """用坐标 x1,y1,...,xn,yn 创建线段."""
        返回 分身._create('line', 参数, 关键词参数)

    def create_oval(self, *args, **kw):
        """Create oval with coordinates x1,y1,x2,y2."""
        return self._create('oval', args, kw)

    套路 创建椭圆(分身, *参数, **关键词参数):
        """用坐标 x1,y1,x2,y2 创建椭圆."""
        返回 分身._create('oval', 参数, 关键词参数)

    def create_polygon(self, *args, **kw):
        """Create polygon with coordinates x1,y1,...,xn,yn."""
        return self._create('polygon', args, kw)

    套路 创建多边形(分身, *参数, **关键词参数):
        """用坐标 x1,y1,...,xn,yn 创建多边形."""
        返回 分身._create('polygon', 参数, 关键词参数)

    def create_rectangle(self, *args, **kw):
        """Create rectangle with coordinates x1,y1,x2,y2."""
        return self._create('rectangle', args, kw)

    套路 创建矩形(分身, *参数, **关键词参数):
        """用坐标 x1,y1,x2,y2 创建矩形."""
        返回 分身._create('rectangle', 参数, 关键词参数)

    def create_text(self, *args, **kw):
        """Create text with coordinates x1,y1."""
        return self._create('text', args, kw)

    套路 创建文本框(分身, *参数, **关键词参数):
        """用坐标 x1,y1 创建文本框."""
        返回 分身._create('text', 参数, 关键词参数)

    def create_window(self, *args, **kw):
        """Create window with coordinates x1,y1,x2,y2."""
        return self._create('window', args, kw)

    套路 创建窗口(分身, *参数, **关键词参数):
        """用坐标 x1,y1,x2,y2 创建窗口."""
        返回 分身._create('window', 参数, 关键词参数)

    def dchars(self, *args):
        """Delete characters of text items identified by tag or id in ARGS (possibly
        several times) from FIRST to LAST character (including)."""
        self.tk.call((self._w, 'dchars') + args)

    套路 删除字符(分身, *参数):
        """删除 '参数' 中的标志或 id 所确定的文本框项目的字符 (可能多次),
        从 '首' 字符删到 '尾' 字符 (包含)."""
        分身.tk.call((分身._w, 'dchars') + 参数)

    def delete(self, *args):
        """Delete items identified by all tag or ids contained in ARGS."""
        self.tk.call((self._w, 'delete') + args)

    套路 删除(分身, *参数):
        """删除 '参数' 中的所有标志或 id 所确定的项目."""
        分身.tk.call((分身._w, 'delete') + 参数)

    def dtag(self, *args):
        """Delete tag or id given as last arguments in ARGS from items
        identified by first argument in ARGS."""
        self.tk.call((self._w, 'dtag') + args)

    套路 删除标志(分身, *参数):
        """从 '参数' 的第一个参数所确定的项目中删除 '参数' 的最后若干参数
        给出的标志或 id."""
        分身.tk.call((分身._w, 'dtag') + 参数)

    def find(self, *args):
        """Internal function."""
        return self._getints(
            self.tk.call((self._w, 'find') + args)) or ()

    def find_above(self, tagOrId):
        """Return items above TAGORID."""
        return self.find('above', tagOrId)

    套路 查找_之上(分身, 标签或Id):
        """返回 '标签或Id' 之上的项目."""
        返回 分身.find('above', 标签或Id)

    def find_all(self):
        """返回所有项目."""
        return self.find('all')

    查找_全部 = find_all

    def find_below(self, tagOrId):
        """Return all items below TAGORID."""
        return self.find('below', tagOrId)

    套路 查找_之下(分身, 标签或Id):
        """返回 '标签或Id' 之下的所有项目."""
        返回 分身.find('below', 标签或Id)

    def find_closest(self, x, y, halo=None, start=None):
        """Return item which is closest to pixel at X, Y.
        If several match take the top-most.
        All items closer than HALO are considered overlapping (all are
        closest). If START is specified the next below this tag is taken."""
        return self.find('closest', x, y, halo, start)

    套路 查找_最接近(分身, x, y, 环=空, 起始=空):
        """返回最接近 (x, y) 像素的项目.
        如有多个匹配, 取最上方的.
        所有比 '环' 还近的项目被认为重叠 (全都是最接近的).
        如果指定了 '起始', 则取此标志之下的下一个."""
        返回 分身.find('closest', x, y, 环, 起始)

    def find_enclosed(self, x1, y1, x2, y2):
        """Return all items in rectangle defined
        by X1,Y1,X2,Y2."""
        return self.find('enclosed', x1, y1, x2, y2)

    套路 查找_矩形内(分身, x1, y1, x2, y2):
        """返回 X1,Y1,X2,Y2 定义的矩形内的所有项目."""
        返回 分身.find('enclosed', x1, y1, x2, y2)

    def find_overlapping(self, x1, y1, x2, y2):
        """Return all items which overlap the rectangle
        defined by X1,Y1,X2,Y2."""
        return self.find('overlapping', x1, y1, x2, y2)

    套路 查找_交叠(分身, x1, y1, x2, y2):
        """返回与 X1,Y1,X2,Y2 定义的矩形交叠的所有项目."""
        返回 分身.find('overlapping', x1, y1, x2, y2)

    def find_withtag(self, tagOrId):
        """Return all items with TAGORID."""
        return self.find('withtag', tagOrId)

    套路 查找__有标志(分身, 标志或Id):
        """返回所有具 '标志或Id' 的项目."""
        返回 分身.find('withtag', 标志或Id)

    def focus(self, *args):
        """Set focus to the first item specified in ARGS."""
        return self.tk.call((self._w, 'focus') + args)

    套路 焦点(分身, *参数):
        """将焦点设置到 '参数' 中指定的第一个项目."""
        返回 分身.tk.call((分身._w, 'focus') + 参数)

    def gettags(self, *args):
        """Return tags associated with the first item specified in ARGS."""
        return self.tk.splitlist(
            self.tk.call((self._w, 'gettags') + args))

    套路 获取标志(分身, *参数):
        """返回与 '参数' 中指定的第一个项目相关联的标志."""
        返回 分身.tk.splitlist(
            分身.tk.call((分身._w, 'gettags') + 参数))

    def icursor(self, *args):
        """Set cursor at position POS in the item identified by TAGORID.
        In ARGS TAGORID must be first."""
        self.tk.call((self._w, 'icursor') + args)

    套路 插入光标(分身, *参数):
        """将光标设置在 '标志或Id' 表示的项目的指定位置.
        在参数中, '标志或Id' 必须是第一个."""
        分身.tk.call((分身._w, 'icursor') + 参数)

    def index(self, *args):
        """Return position of cursor as integer in item specified in ARGS."""
        return self.tk.getint(self.tk.call((self._w, 'index') + args))

    套路 索引(分身, *参数):
        """返回光标在 '参数' 所指定项目中的位置, 整数值."""
        返回 分身.tk.getint(分身.tk.call((分身._w, 'index') + 参数))

    def insert(self, *args):
        """Insert TEXT in item TAGORID at position POS. ARGS must
        be TAGORID POS TEXT."""
        self.tk.call((self._w, 'insert') + args)

    套路 插入(分身, *参数):
        """在指定项目的指定位置插入文本. '参数' 必须是 (标签或Id, 位置, 文本)."""
        分身.tk.call((分身._w, 'insert') + 参数)

    def itemcget(self, tagOrId, option):
        """Return the resource value for an OPTION for item TAGORID."""
        return self.tk.call(
            (self._w, 'itemcget') + (tagOrId, '-'+option))

    套路 获取项目配置(分身, 标志或Id, 选项):
        """返回指定项目的 '选项' 的值."""
        返回 分身.tk.call(
            (分身._w, 'itemcget') + (标志或Id, '-'+选项))

    def itemconfigure(self, tagOrId, cnf=None, **kw):
        """Configure resources of an item TAGORID.

        The values for resources are specified as keyword
        arguments. To get an overview about
        the allowed keyword arguments call the method without arguments.
        """
        return self._configure(('itemconfigure', tagOrId), cnf, kw)

    套路 项目配置(分身, 标志或Id, 配置字典=空, **关键词参数):
        """配置指定项目的选项.

        选项值由关键词参数指定. 要了解所有允许的关键词,
        请以不带参数的方式调用该方法.
        """
        返回 分身._configure(('itemconfigure', 标志或Id), 配置字典, 关键词参数)

    itemconfig = itemconfigure

    # lower, tkraise/lift hide Misc.lower, Misc.tkraise/lift,
    # so the preferred name for them is tag_lower, tag_raise
    # (similar to tag_bind, and similar to the Text widget);
    # unfortunately can't delete the old ones yet (maybe in 1.6)
    def tag_lower(self, *args):
        """Lower an item TAGORID given in ARGS
        (optional below another item)."""
        self.tk.call((self._w, 'lower') + args)

    套路 标志_下移(分身, *参数):
        """下移 '参数' 中指定的项目 (可以选择低于另一项目)."""
        分身.tk.call((分身._w, 'lower') + 参数)

    lower = tag_lower
    下移 = 标志_下移

    def move(self, *args):
        """Move an item TAGORID given in ARGS."""
        self.tk.call((self._w, 'move') + args)

    套路 移动(分身, *参数):
        """移动 '参数' 中指定的项目."""
        分身.tk.call((分身._w, 'move') + 参数)

    def moveto(self, tagOrId, x='', y=''):
        """Move the items given by TAGORID in the canvas coordinate
        space so that the first coordinate pair of the bottommost
        item with tag TAGORID is located at position (X,Y).
        X and Y may be the empty string, in which case the
        corresponding coordinate will be unchanged. All items matching
        TAGORID remain in the same positions relative to each other."""
        self.tk.call(self._w, 'moveto', tagOrId, x, y)

    套路 移至(分身, 标志或Id, x='', y=''):
        """在画布坐标空间中移动 '标志或Id' 指定的项目, 使得具有该标志的
        最下方项目的第一个坐标对位于 (X,Y).

        X 和 Y 如果是空字符串, 则相应的坐标不变. 
        
        所有匹配项目的相对位置保持不变."""
        分身.tk.call(分身._w, 'moveto', 标志或Id, x, y)

    def postscript(self, cnf={}, **kw):
        """Print the contents of the canvas to a postscript
        file. Valid options: colormap, colormode, file, fontmap,
        height, pageanchor, pageheight, pagewidth, pagex, pagey,
        rotate, width, x, y."""
        return self.tk.call((self._w, 'postscript') +
                    self._options(cnf, kw))

    套路 打印到PS(分身, 配置字典={}, **关键词参数):
        """将画布内容打印到 postscript 文件. 有效选项如下:

        colormap, colormode, file, fontmap,
        height, pageanchor, pageheight, pagewidth, pagex, pagey,
        rotate, width, x, y."""
        返回 分身.tk.call((分身._w, 'postscript') +
                    分身._options(配置字典, 关键词参数))

    def tag_raise(self, *args):
        """Raise an item TAGORID given in ARGS
        (optional above another item)."""
        self.tk.call((self._w, 'raise') + args)

    套路 标志_上移(分身, *参数):
        """上移 '参数' 中指定的项目 (可以选择高于另一项目)."""
        分身.tk.call((分身._w, 'raise') + 参数)

    lift = tkraise = tag_raise
    上移 = 标志_上移

    def scale(self, *args):
        """Scale item TAGORID with XORIGIN, YORIGIN, XSCALE, YSCALE."""
        self.tk.call((self._w, 'scale') + args)

    套路 缩放(分身, *参数):
        """缩放指定项目, 参数形式为 (标志或Id, 起点X, 起点Y, X比例, Y比例)."""
        分身.tk.call((分身._w, 'scale') + 参数)

    def scan_mark(self, x, y):
        """Remember the current X, Y coordinates."""
        self.tk.call(self._w, 'scan', 'mark', x, y)

    套路 扫描_标记(分身, x, y):
        """记住当前 X, Y 坐标."""
        分身.tk.call(分身._w, 'scan', 'mark', x, y)

    def scan_dragto(self, x, y, gain=10):
        """Adjust the view of the canvas to GAIN times the
        difference between X and Y and the coordinates given in
        scan_mark."""
        self.tk.call(self._w, 'scan', 'dragto', x, y, gain)

    套路 扫描_拖至(分身, x, y, 倍数=10):
        """调整画布视图, 以将 (x, y) 与 '扫描_标记' 给出的坐标
        之差放大指定倍数."""
        分身.tk.call(分身._w, 'scan', 'dragto', x, y, 倍数)
        
    def select_adjust(self, tagOrId, index):
        """Adjust the end of the selection near the cursor of an item TAGORID to index."""
        self.tk.call(self._w, 'select', 'adjust', tagOrId, index)

    套路 选择_调整(分身, 标志或Id, 索引):
        """将指定项目的光标附近的选定内容的末尾调整到索引位置."""
        self.tk.call(self._w, 'select', 'adjust', tagOrId, index)

    def select_clear(self):
        """清除选定内容 (如果它在此部件内)."""
        self.tk.call(self._w, 'select', 'clear')

    选择_清除 = select_clear

    def select_from(self, tagOrId, index):
        """Set the fixed end of a selection in item TAGORID to INDEX."""
        self.tk.call(self._w, 'select', 'from', tagOrId, index)

    套路 选择_从(分身, 标志或Id, 索引):
        """将指定项目中选定内容的固定端设置为索引位置."""
        分身.tk.call(分身._w, 'select', 'from', 标志或Id, 索引)
        
    def select_item(self):
        """返回具有选定内容的项目."""
        return self.tk.call(self._w, 'select', 'item') or None

    选择_项目 = select_item

    def select_to(self, tagOrId, index):
        """Set the variable end of a selection in item TAGORID to INDEX."""
        self.tk.call(self._w, 'select', 'to', tagOrId, index)

    套路 选择_至(分身, 标志或Id, 索引):
        """将指定项目中选定内容的可变端设置为索引位置."""
        分身.tk.call(分身._w, 'select', 'to', 标志或Id, 索引)

    def type(self, tagOrId):
        """Return the type of the item TAGORID."""
        return self.tk.call(self._w, 'type', tagOrId) or None

    套路 类型(分身, 标志或Id):
        """返回指定项目的类型."""
        返回 分身.tk.call(分身._w, 'type', 标志或Id) or None


class Checkbutton(Widget):
    """Checkbutton widget which is either in on- or off-state."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a checkbutton widget with the parent MASTER.

        Valid resource names: activebackground, activeforeground, anchor,
        background, bd, bg, bitmap, borderwidth, command, cursor,
        disabledforeground, fg, font, foreground, height,
        highlightbackground, highlightcolor, highlightthickness, image,
        indicatoron, justify, offvalue, onvalue, padx, pady, relief,
        selectcolor, selectimage, state, takefocus, text, textvariable,
        underline, variable, width, wraplength."""
        Widget.__init__(self, master, 'checkbutton', cnf, kw)

    def deselect(self):
        """清除复选按钮."""
        self.tk.call(self._w, 'deselect')

    取消选择 = deselect

    def flash(self):
        """让按钮闪烁."""
        self.tk.call(self._w, 'flash')

    闪烁 = flash

    def invoke(self):
        """切换按钮并调用作为资源的命令 (如有)."""
        return self.tk.call(self._w, 'invoke')

    调用 = invoke

    def select(self):
        """选中复选按钮."""
        self.tk.call(self._w, 'select')

    选择 = select

    def toggle(self):
        """切换按钮状态."""
        self.tk.call(self._w, 'toggle')

    切换 = toggle

类 〇复选按钮(Checkbutton):
    """复选按钮部件, 处于选中或未选中状态"""
    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个复选按钮部件. 选项如下:\n
        活动背景色, 活动前景色, 锚点, 背景色, 位图, 边框宽度, 鼠标样式,
        禁用时前景色, 字体, 前景色, 高亮背景, 高亮颜色, 高亮厚度, 图像, 对齐,
        水平边距, 垂直边距, 边框样式, 获得焦点, 文本, 文本变量, 下划线, 分行长度

        命令, 混合模式, 高度, 指示开, 未选中值, 选中值, 选中时颜色, 选中时图像,
        状态, 变量, 宽度
        """
        分身._复选按钮选项字典 = {
            '命令':         'command', 
            '混合模式':     'compound', 
            '高度':         'height',
            '指示开':       'indicatoron',
            '未选中值':     'offvalue', 
            '选中值':       'onvalue',
            '选中时颜色':   'selectcolor', 
            '选中时图像':   'selectimage',
            '状态':         'state', 
            '变量':         'variable',
            '宽度':         'width'
        }
        分身._复选按钮选项字典.更新(_部件通用选项字典)
        分身._复选按钮选项值字典 = {
            '上方': 'top',
            '下方': 'bottom',
            '无':   'none',
            '正常': 'normal',
            '活动': 'active',
            '禁用': 'disabled'
        }
        分身._复选按钮选项值字典.更新(_部件通用选项值字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._复选按钮选项字典, 分身._复选按钮选项值字典)
        Checkbutton.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)

    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._复选按钮选项字典, 分身._复选按钮选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Entry(Widget, XView):
    """Entry widget which allows displaying simple text."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct an entry widget with the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, cursor,
        exportselection, fg, font, foreground, highlightbackground,
        highlightcolor, highlightthickness, insertbackground,
        insertborderwidth, insertofftime, insertontime, insertwidth,
        invalidcommand, invcmd, justify, relief, selectbackground,
        selectborderwidth, selectforeground, show, state, takefocus,
        textvariable, validate, validatecommand, vcmd, width,
        xscrollcommand."""
        Widget.__init__(self, master, 'entry', cnf, kw)

    def delete(self, first, last=None):
        """Delete text from FIRST to LAST (not included)."""
        self.tk.call(self._w, 'delete', first, last)

    套路 删除(分身, 首, 尾=空):
        """删除从 '首' 到 '尾' (不包含) 的文本."""
        如果 尾 == '末尾':
            尾 = 'end'
        分身.tk.call(分身._w, 'delete', 首, 尾)

    def get(self):
        """返回文本."""
        return self.tk.call(self._w, 'get')

    获取 = get

    def icursor(self, index):
        """Insert cursor at INDEX."""
        self.tk.call(self._w, 'icursor', index)

    套路 插入光标(分身, 索引):
        """将光标插在 '索引' 处."""
        分身.tk.call(分身._w, 'icursor', 索引)

    def index(self, index):
        """Return position of cursor."""
        return self.tk.getint(self.tk.call(
            self._w, 'index', index))

    套路 索引(分身, 索引):
        """返回光标的位置."""
        返回 分身.tk.getint(分身.tk.call(
            分身._w, 'index', 索引))

    def insert(self, index, string):
        """Insert STRING at INDEX."""
        self.tk.call(self._w, 'insert', index, string)

    套路 插入(分身, 索引, 字符串):
        """在索引处插入字符串."""
        如果 索引 == '末尾':
            索引 = 'end'
        或如 索引 == '光标':
            索引 = 'insert'
        分身.tk.call(分身._w, 'insert', 索引, 字符串)

    def scan_mark(self, x):
        """记住当前 X, Y 坐标."""
        self.tk.call(self._w, 'scan', 'mark', x)

    扫描_标记 = scan_mark

    def scan_dragto(self, x):
        """调整画布视图, 以将 (x, y) 与 '扫描_标记' 给出的坐标
        之差放大 10 倍."""
        self.tk.call(self._w, 'scan', 'dragto', x)

    扫描_拖至 = scan_dragto

    def selection_adjust(self, index):
        """Adjust the end of the selection near the cursor to INDEX."""
        self.tk.call(self._w, 'selection', 'adjust', index)

    套路 选定内容_调整(分身, 索引):
        """将光标附近的选定内容的末尾调整到索引位置."""
        分身.tk.call(分身._w, 'selection', 'adjust', 索引)

    select_adjust = selection_adjust
    选择_调整 = 选定内容_调整

    def selection_clear(self):
        """清除选定内容 (如果它在此部件内)."""
        self.tk.call(self._w, 'selection', 'clear')

    选择_清除 = select_clear = selection_clear
    
    def selection_from(self, index):
        """Set the fixed end of a selection to INDEX."""
        self.tk.call(self._w, 'selection', 'from', index)

    套路 选定内容_从(分身, 索引):
        """将选定内容的固定端设置为索引位置."""
        分身.tk.call(分身._w, 'selection', 'from', 索引)

    select_from = selection_from
    选择_从 = 选定内容_从

    def selection_present(self):
        """如果选择了输入框中的字符, 则返回 真, 否则返回 假."""
        return self.tk.getboolean(
            self.tk.call(self._w, 'selection', 'present'))

    选择_存在 = 选定内容_存在 = select_present = selection_present

    def selection_range(self, start, end):
        """Set the selection from START to END (not included)."""
        self.tk.call(self._w, 'selection', 'range', start, end)

    套路 选定内容_范围(分身, 起, 止):
        """设置从 '起' 到 '止' (不包含) 的选定内容."""
        分身.tk.call(分身._w, 'selection', 'range', 起, 止)

    select_range = selection_range
    选择_范围 = 选定内容_范围

    def selection_to(self, index):
        """Set the variable end of a selection to INDEX."""
        self.tk.call(self._w, 'selection', 'to', index)

    套路 选定内容_至(分身, 索引):
        """将选定内容的可变端设置为索引位置."""
        分身.tk.call(分身._w, 'selection', 'to', 索引)

    select_to = selection_to
    选择_至 = 选定内容_至


类 〇输入框(Entry):
    """输入框部件, 用于显示简单文本"""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个输入框部件. 选项如下:

        背景色, 边框宽度, 鼠标样式, 选定内容可复制, 字体, 前景色, 高亮背景,
        高亮颜色, 高亮厚度, 光标颜色, 光标边框宽度, 光标灭时间, 光标亮时间,
        光标宽度, 无效命令, 对齐, 边框样式, 选中时背景色, 选中时边框宽度,
        选中时前景色, 显示, 状态, 获得焦点, 文本变量, 验证, 验证命令,
        宽度, 水平滚动命令
        """
        分身._输入框选项字典 = {
            '背景色':           'background',
            '边框宽度':         'borderwidth', 
            '鼠标样式':         'cursor',
            '选定内容可复制':    'exportselection', 
            '字体':             'font', 
            '前景色':           'foreground',
            '高亮背景':         'highlightbackground', 
            '高亮颜色':         'highlightcolor',
            '高亮厚度':         'highlightthickness', 
            '光标颜色':         'insertbackground', 
            '光标边框宽度':     'insertborderwidth', 
            '光标灭时间':       'insertofftime', 
            '光标亮时间':       'insertontime', 
            '光标宽度':         'insertwidth', 
            '无效命令':         'invalidcommand', 
            '对齐':             'justify',
            '边框样式':         'relief', 
            '选中时背景色':     'selectbackground', 
            '选中时边框宽度':   'selectborderwidth', 
            '选中时前景色':     'selectforeground',  
            '显示':             'show', 
            '状态':             'state', 
            '获得焦点':         'takefocus',
            '文本变量':         'textvariable', 
            '验证':             'validate', 
            '验证命令':         'validatecommand', 
            '宽度':             'width',
            '水平滚动命令':     'xscrollcommand', 
        }
        #分身._输入框选项字典.更新(_部件通用选项字典)
        分身._输入框选项值字典 = {
            '正常': 'normal',
            '只读': 'readonly',
            '禁用': 'disabled'
        }
        分身._输入框选项值字典.更新(_颜色字典)
        分身._输入框选项值字典.更新(_边框样式字典)
        分身._输入框选项值字典.更新(_验证字典)
        分身._输入框选项值字典.更新(_对齐字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._输入框选项字典, 分身._输入框选项值字典)
        Entry.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)

    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._输入框选项字典, 分身._输入框选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Frame(Widget):
    """Frame widget which may contain other widgets and can have a 3D border."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a frame widget with the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, class,
        colormap, container, cursor, height, highlightbackground,
        highlightcolor, highlightthickness, relief, takefocus, visual, width."""
        cnf = _cnfmerge((cnf, kw))
        extra = ()
        if 'class_' in cnf:
            extra = ('-class', cnf['class_'])
            del cnf['class_']
        elif 'class' in cnf:
            extra = ('-class', cnf['class'])
            del cnf['class']
        Widget.__init__(self, master, 'frame', cnf, {}, extra)

类 〇框架(Frame):
    """框架部件, 可包含其他部件, 并且可以有 3D 边框"""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个框架部件. 选项如下:

        背景色, 边框宽度, 类_, 颜色映射, 容器, 鼠标样式, 高度, 高亮背景,
        高亮颜色, 高亮厚度, 水平边距, 垂直边距, 边框样式, 获得焦点, 
        视觉, 宽度
        """
        分身._框架选项字典 = {
            '背景色':       'background', 
            '边框宽度':     'borderwidth',
            '类_':          'class_',
            '颜色映射':     'colormap', 
            '容器':         'container', 
            '鼠标样式':     'cursor',
            '高度':         'height', 
            '高亮背景':     'highlightbackground', 
            '高亮颜色':     'highlightcolor',
            '高亮厚度':     'highlightthickness', 
            '水平边距':     'padx', 
            '垂直边距':     'pady', 
            '边框样式':     'relief', 
            '获得焦点':     'takefocus', 
            '视觉':         'visual', 
            '宽度':         'width'
        }
        #分身._框架选项字典.更新(_部件通用选项字典)
        分身._框架选项值字典 = {

        }
        分身._框架选项值字典.更新(_颜色字典)
        分身._框架选项值字典.更新(_边框样式字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._框架选项字典, 分身._框架选项值字典)
        Frame.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)
    
    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._框架选项字典, 分身._框架选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Label(Widget):
    """Label widget which can display text and bitmaps."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a label widget with the parent MASTER.

        STANDARD OPTIONS

            activebackground, activeforeground, anchor,
            background, bitmap, borderwidth, cursor,
            disabledforeground, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, image, justify,
            padx, pady, relief, takefocus, text,
            textvariable, underline, wraplength

        WIDGET-SPECIFIC OPTIONS

            height, state, width

        """
        Widget.__init__(self, master, 'label', cnf, kw)

类 〇标签(Label):
    """标签部件, 可显示文本和位图"""
    
    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个标签部件, 选项有:

        活动背景色, 活动前景色, 锚点, 背景色, 位图, 边框宽度, 鼠标样式,
        禁用时前景色, 字体, 前景色, 高亮背景, 高亮颜色, 高亮厚度, 图像, 对齐,
        水平边距, 垂直边距, 边框样式, 获得焦点, 文本, 文本变量, 下划线, 分行长度

        混合模式, 高度, 状态, 宽度
        """
        分身._标签选项字典 = {
            '混合模式': 'compound',
            '高度':     'height', 
            '状态':     'state', 
            '宽度':     'width'
        }
        分身._标签选项字典.更新(_部件通用选项字典)
        分身._标签选项值字典 = {
            '上方': 'top',
            '下方': 'bottom',
            '无':   'none',
            '正常': 'normal',
            '活动': 'active',
            '禁用': 'disabled'
        }
        分身._标签选项值字典.更新(_部件通用选项值字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._标签选项字典, 分身._标签选项值字典)
        Label.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)
    
    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._标签选项字典, 分身._标签选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Listbox(Widget, XView, YView):
    """Listbox widget which can display a list of strings."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a listbox widget with the parent MASTER.

        Valid resource names: background, bd, bg, borderwidth, cursor,
        exportselection, fg, font, foreground, height, highlightbackground,
        highlightcolor, highlightthickness, relief, selectbackground,
        selectborderwidth, selectforeground, selectmode, setgrid, takefocus,
        width, xscrollcommand, yscrollcommand, listvariable."""
        Widget.__init__(self, master, 'listbox', cnf, kw)

    def activate(self, index):
        """Activate item identified by INDEX."""
        self.tk.call(self._w, 'activate', index)

    套路 激活(分身, 索引):
        """激活索引表示的项目."""
        分身.tk.call(分身._w, 'activate', 索引)

    def bbox(self, index):
        """Return a tuple of X1,Y1,X2,Y2 coordinates for a rectangle
        which encloses the item identified by the given index."""
        return self._getints(self.tk.call(self._w, 'bbox', index)) or None

    套路 包围盒(分身, 索引):
        """返回一个矩形坐标元组 X1,Y1,X2,Y2, 该矩形包围给定索引
        表示的项目."""
        返回 分身._getints(分身.tk.call(分身._w, 'bbox', 索引)) or None

    def curselection(self):
        """返回当前选定项目的索引."""
        return self._getints(self.tk.call(self._w, 'curselection')) or ()

    当前选择 = curselection

    def delete(self, first, last=None):
        """Delete items from FIRST to LAST (included)."""
        self.tk.call(self._w, 'delete', first, last)

    套路 删除(分身, 首, 尾=空):
        """删除从 '首' 到 '尾' (包含) 的项目."""
        如果 尾 == '末尾':
            尾 = 'end'
        分身.tk.call(分身._w, 'delete', 首, 尾)

    def get(self, first, last=None):
        """Get list of items from FIRST to LAST (included)."""
        if last is not None:
            return self.tk.splitlist(self.tk.call(
                self._w, 'get', first, last))
        else:
            return self.tk.call(self._w, 'get', first)

    套路 获取(分身, 首, 尾=空):
        """获取从 '首' 到 '尾' (包含) 的项目列表."""
        返回 分身.get(首, 尾)

    def index(self, index):
        """Return index of item identified with INDEX."""
        i = self.tk.call(self._w, 'index', index)
        if i == 'none': return None
        return self.tk.getint(i)

    套路 索引(分身, 索引):
        """返回 '索引' 表示的项目的索引."""
        如果 索引 == '末尾':
            索引 = 'end'
        返回 分身.index(索引)

    def insert(self, index, *elements):
        """Insert ELEMENTS at INDEX."""
        self.tk.call((self._w, 'insert', index) + elements)
    
    套路 插入(分身, 索引, *元素):
        """在 '索引' 处插入 '元素'."""
        如果 索引 == '末尾':
            索引 = 'end'
        分身.tk.call((分身._w, 'insert', 索引) + 元素)

    def nearest(self, y):
        """Get index of item which is nearest to y coordinate Y."""
        return self.tk.getint(self.tk.call(
            self._w, 'nearest', y))

    套路 最近(分身, y):
        """获取最接近 y 坐标 'y' 的项目的索引."""
        返回 分身.tk.getint(分身.tk.call(
            分身._w, 'nearest', y))

    def scan_mark(self, x, y):
        """记住当前 X, Y 坐标."""
        self.tk.call(self._w, 'scan', 'mark', x, y)

    扫描_标记 = scan_mark

    def scan_dragto(self, x, y):
        """调整列表框视图, 以将 (x, y) 与 '扫描_标记' 给出的坐标
        之差放大 10 倍."""
        self.tk.call(self._w, 'scan', 'dragto', x, y)

    扫描_拖至 = scan_dragto

    def see(self, index):
        """Scroll such that INDEX is visible."""
        self.tk.call(self._w, 'see', index)

    套路 看见(分身, 索引):
        """滚动列表框使得 '索引' 表示的项目可见."""
        分身.tk.call(分身._w, 'see', 索引)

    def selection_anchor(self, index):
        """Set the fixed end oft the selection to INDEX."""
        self.tk.call(self._w, 'selection', 'anchor', index)

    套路 选定内容_锚点(分身, 索引):
        """将选定内容的固定端设置为 '索引'."""
        分身.tk.call(分身._w, 'selection', 'anchor', 索引)

    select_anchor = selection_anchor
    选择_锚点 = 选定内容_锚点

    def selection_clear(self, first, last=None):
        """Clear the selection from FIRST to LAST (included)."""
        self.tk.call(self._w,
                 'selection', 'clear', first, last)

    套路 选定内容_清除(分身, 首, 尾=空):
        """清除从 '首' 到 '尾' (包含) 的选定内容."""
        分身.tk.call(分身._w,
                 'selection', 'clear', 首, 尾)

    select_clear = selection_clear
    选择_清除 = 选定内容_清除

    def selection_includes(self, index):
        """Return 1 if INDEX is part of the selection."""
        return self.tk.getboolean(self.tk.call(
            self._w, 'selection', 'includes', index))

    套路 选定内容_包括(分身, 索引):
        """如果 '索引' 是选定内容的一部分, 则返回 1."""
        返回 分身.tk.getboolean(分身.tk.call(
            分身._w, 'selection', 'includes', 索引))

    select_includes = selection_includes
    选择_包括 = 选定内容_包括

    def selection_set(self, first, last=None):
        """Set the selection from FIRST to LAST (included) without
        changing the currently selected elements."""
        self.tk.call(self._w, 'selection', 'set', first, last)

    套路 选定内容_设置(分身, 首, 尾=空):
        """设置从 '首' 到 '尾' (包含) 的选定内容, 而不
        改变当前选定的元素."""
        分身.tk.call(分身._w, 'selection', 'set', 首, 尾)

    select_set = selection_set
    选择_设置 = 选定内容_设置

    def size(self):
        """返回列表框中的元素数量."""
        return self.tk.getint(self.tk.call(self._w, 'size'))

    大小 = size

    def itemcget(self, index, option):
        """Return the resource value for an ITEM and an OPTION."""
        return self.tk.call(
            (self._w, 'itemcget') + (index, '-'+option))

    套路 获取项目配置(分身, 索引, 选项):
        """返回 '索引' 所指项目的 '选项' 的值."""
        返回 分身.tk.call(
            (分身._w, 'itemcget') + (索引, '-'+选项))

    def itemconfigure(self, index, cnf=None, **kw):
        """Configure resources of an ITEM.

        The values for resources are specified as keyword arguments.
        To get an overview about the allowed keyword arguments
        call the method without arguments.
        Valid resource names: background, bg, foreground, fg,
        selectbackground, selectforeground."""
        return self._configure(('itemconfigure', index), cnf, kw)

    套路 项目配置(分身, 索引, 配置字典=空, **关键词参数):
        """配置指定项目的选项.

        选项值由关键词参数指定. 要了解所有允许的关键词,
        请以不带参数的方式调用该方法.

        有效选项: 背景色, 前景色, 选中时背景色, 选中时前景色
        """
        项目选项字典 = {
            '背景色':           'background',
            '前景色':           'foreground',
            '选中时背景色':     'selectbackground', 
            '选中时前景色':     'selectforeground' 
        }
        关键词参数 = _关键词参数中转英(关键词参数, 项目选项字典)
        返回 分身._configure(('itemconfigure', 索引), 配置字典, 关键词参数)

    itemconfig = itemconfigure

类 〇列表框(Listbox):
    """列表框部件, 可显示一系列字符串"""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个列表框部件. 选项如下:

        背景色, 边框宽度, 鼠标样式, 选定内容可复制, 字体, 前景色, 高度, 高亮背景,
        高亮颜色, 高亮厚度, 边框样式, 选中时背景色, 选中时边框宽度, 选中时前景色,
        选择模式, 设置网格, 获得焦点, 宽度, 水平滚动命令, 垂直滚动命令, 列表变量
        """
        分身._列表框选项字典 = {
            '背景色':       'background',
            '边框宽度':     'borderwidth', 
            '鼠标样式':     'cursor',
            '选定内容可复制':    'exportselection',  
            '字体':         'font', 
            '前景色':       'foreground',
            '高度':         'height', 
            '高亮背景':     'highlightbackground', 
            '高亮颜色':     'highlightcolor',
            '高亮厚度':     'highlightthickness',
            '边框样式':     'relief',
            '选中时背景色':     'selectbackground', 
            '选中时边框宽度':   'selectborderwidth', 
            '选中时前景色':     'selectforeground', 
            '选择模式':         'selectmode', 
            '设置网格':         'setgrid', 
            '获得焦点':         'takefocus',
            '宽度':             'width', 
            '水平滚动命令':      'xscrollcommand', 
            '垂直滚动命令':      'yscrollcommand', 
            '列表变量':         'listvariable'
        }
        #分身._列表框选项字典.更新(_部件通用选项字典)
        分身._列表框选项值字典 = {
            '单选': 'single',
            '浏览': 'browse',
            '多选': 'multiple',
            '扩展': 'extended'
        }
        分身._列表框选项值字典.更新(_颜色字典)
        分身._列表框选项值字典.更新(_边框样式字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._列表框选项字典, 分身._列表框选项值字典)
        Listbox.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)

    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._列表框选项字典, 分身._列表框选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Menu(Widget):
    """Menu widget which allows displaying menu bars, pull-down menus and pop-up menus."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct menu widget with the parent MASTER.

        Valid resource names: activebackground, activeborderwidth,
        activeforeground, background, bd, bg, borderwidth, cursor,
        disabledforeground, fg, font, foreground, postcommand, relief,
        selectcolor, takefocus, tearoff, tearoffcommand, title, type."""
        Widget.__init__(self, master, 'menu', cnf, kw)

    def tk_popup(self, x, y, entry=""):
        """Post the menu at position X,Y with entry ENTRY."""
        self.tk.call('tk_popup', self._w, x, y, entry)

    套路 弹出_tk(分身, x, y, 条目=""):
        """在位置 X,Y 弹出含给定条目的菜单."""
        分身.tk.call('tk_popup', 分身._w, x, y, 条目)

    def activate(self, index):
        """Activate entry at INDEX."""
        self.tk.call(self._w, 'activate', index)

    套路 激活(分身, 索引):
        """激活 '索引' 对应的条目."""
        分身.tk.call(分身._w, 'activate', 索引)

    def add(self, itemType, cnf={}, **kw):
        """Internal function."""
        self.tk.call((self._w, 'add', itemType) +
                 self._options(cnf, kw))

    def add_cascade(self, cnf={}, **kw):
        """Add hierarchical menu item."""
        self.add('cascade', cnf or kw)

    套路 添加子菜单(分身, 配置字典={}, **关键词参数):
        """添加分级式菜单项."""
        关键词参数 = _关键词参数中转英(关键词参数, _菜单配置选项字典)
        分身.add('cascade', 配置字典 or 关键词参数)

    def add_checkbutton(self, cnf={}, **kw):
        """Add checkbutton menu item."""
        self.add('checkbutton', cnf or kw)

    套路 添加复选按钮(分身, 配置字典={}, **关键词参数):
        """添加复选按钮菜单项."""
        _菜单配置选项字典.更新({'变量': 'variable', '值': 'value'})
        关键词参数 = _关键词参数中转英(关键词参数, _菜单配置选项字典)
        分身.add('checkbutton', 配置字典 or 关键词参数)

    def add_command(self, cnf={}, **kw):
        """Add command menu item."""
        self.add('command', cnf or kw)

    套路 添加命令(分身, 配置字典={}, **关键词参数):
        """添加命令菜单项."""
        关键词参数 = _关键词参数中转英(关键词参数, _菜单配置选项字典)
        分身.add('command', 配置字典 or 关键词参数)

    def add_radiobutton(self, cnf={}, **kw):
        """Addd radio menu item."""
        self.add('radiobutton', cnf or kw)

    套路 添加单选按钮(分身, 配置字典={}, **关键词参数):
        """添加单选按钮菜单项."""
        _菜单配置选项字典.更新({'变量': 'variable', '值': 'value'})
        关键词参数 = _关键词参数中转英(关键词参数, _菜单配置选项字典)
        分身.add('radiobutton', 配置字典 or 关键词参数)

    def add_separator(self, cnf={}, **kw):
        """Add separator."""
        self.add('separator', cnf or kw)

    套路 添加分割线(分身, 配置字典={}, **关键词参数):
        """添加分割线."""
        分身.add('separator', 配置字典 or 关键词参数)

    def insert(self, index, itemType, cnf={}, **kw):
        """Internal function."""
        self.tk.call((self._w, 'insert', index, itemType) +
                 self._options(cnf, kw))

    def insert_cascade(self, index, cnf={}, **kw):
        """Add hierarchical menu item at INDEX."""
        self.insert(index, 'cascade', cnf or kw)

    套路 插入子菜单(分身, 索引, 配置字典={}, **关键词参数):
        """在 '索引' 处添加分级式菜单项."""
        关键词参数 = _关键词参数中转英(关键词参数, _菜单配置选项字典)
        分身.insert(索引, 'cascade', 配置字典 or 关键词参数)

    def insert_checkbutton(self, index, cnf={}, **kw):
        """Add checkbutton menu item at INDEX."""
        self.insert(index, 'checkbutton', cnf or kw)

    套路 插入复选按钮(分身, 索引, 配置字典={}, **关键词参数):
        """在 '索引' 处添加复选按钮菜单项."""
        _菜单配置选项字典.更新({'变量': 'variable', '值': 'value'})
        关键词参数 = _关键词参数中转英(关键词参数, _菜单配置选项字典)
        分身.insert(索引, 'checkbutton', 配置字典 or 关键词参数)

    def insert_command(self, index, cnf={}, **kw):
        """Add command menu item at INDEX."""
        self.insert(index, 'command', cnf or kw)

    套路 插入命令(分身, 索引, 配置字典={}, **关键词参数):
        """在 '索引' 处添加命令菜单项."""
        关键词参数 = _关键词参数中转英(关键词参数, _菜单配置选项字典)
        分身.insert(索引, 'command', 配置字典 or 关键词参数)

    def insert_radiobutton(self, index, cnf={}, **kw):
        """Addd radio menu item at INDEX."""
        self.insert(index, 'radiobutton', cnf or kw)

    套路 插入单选按钮(分身, 索引, 配置字典={}, **关键词参数):
        """在 '索引' 处添加单选按钮菜单项."""
        _菜单配置选项字典.更新({'变量': 'variable', '值': 'value'})
        关键词参数 = _关键词参数中转英(关键词参数, _菜单配置选项字典)
        分身.insert(索引, 'radiobutton', 配置字典 or 关键词参数)

    def insert_separator(self, index, cnf={}, **kw):
        """Add separator at INDEX."""
        self.insert(index, 'separator', cnf or kw)

    套路 插入分割线(分身, 索引, 配置字典={}, **关键词参数):
        """在 '索引' 处添加分割线."""
        分身.insert(索引, 'separator', 配置字典 or 关键词参数)

    def delete(self, index1, index2=None):
        """Delete menu items between INDEX1 and INDEX2 (included)."""
        if index2 is None:
            index2 = index1

        num_index1, num_index2 = self.index(index1), self.index(index2)
        if (num_index1 is None) or (num_index2 is None):
            num_index1, num_index2 = 0, -1

        for i in range(num_index1, num_index2 + 1):
            if 'command' in self.entryconfig(i):
                c = str(self.entrycget(i, 'command'))
                if c:
                    self.deletecommand(c)
        self.tk.call(self._w, 'delete', index1, index2)

    套路 删除(分身, 索引1, 索引2=空):
        """删除 '索引1' 和 '索引2' (包含) 之间的菜单项."""
        分身.delete(分身, 索引1, 索引2)

    def entrycget(self, index, option):
        """Return the resource value of a menu item for OPTION at INDEX."""
        return self.tk.call(self._w, 'entrycget', index, '-' + option)

    套路 获取条目配置(分身, 索引, 选项):
        """返回 '索引' 处菜单项的 '选项' 值."""
        返回 分身.tk.call(分身._w, 'entrycget', 索引, '-' + 选项)

    def entryconfigure(self, index, cnf=None, **kw):
        """Configure a menu item at INDEX."""
        return self._configure(('entryconfigure', index), cnf, kw)

    套路 条目配置(分身, 索引, 配置字典=空, **关键词参数):
        """配置 '索引' 处的菜单项."""
        返回 分身._configure(('entryconfigure', 索引), 配置字典, 关键词参数)

    entryconfig = entryconfigure

    def index(self, index):
        """Return the index of a menu item identified by INDEX."""
        i = self.tk.call(self._w, 'index', index)
        if i == 'none': return None
        return self.tk.getint(i)

    套路 索引(分身, 索引):
        """返回 '索引' 确定的菜单项的索引."""
        返回 分身.index(索引)

    def invoke(self, index):
        """Invoke a menu item identified by INDEX and execute
        the associated command."""
        return self.tk.call(self._w, 'invoke', index)

    套路 调用(分身, 索引):
        """调用 '索引' 确定的菜单项并执行相关联的命令."""
        返回 分身.tk.call(分身._w, 'invoke', 索引)

    def post(self, x, y):
        """在位置 X,Y 显示菜单."""
        self.tk.call(self._w, 'post', x, y)

    弹出 = post

    def type(self, index):
        """Return the type of the menu item at INDEX."""
        return self.tk.call(self._w, 'type', index)

    套路 类型(分身, 索引):
        """返回 '索引' 对应菜单项的类型."""
        返回 分身.tk.call(分身._w, 'type', 索引)

    def unpost(self):
        """取消显示菜单."""
        self.tk.call(self._w, 'unpost')

    取消弹出 = unpost

    def xposition(self, index): # new in Tk 8.5
        """Return the x-position of the leftmost pixel of the menu item
        at INDEX."""
        return self.tk.getint(self.tk.call(self._w, 'xposition', index))

    套路 x位置(分身, 索引): # new in Tk 8.5
        """返回 '索引' 对应菜单项的最左边像素的 x 位置."""
        返回 分身.tk.getint(分身.tk.call(分身._w, 'xposition', 索引))

    def yposition(self, index):
        """Return the y-position of the topmost pixel of the menu item at INDEX."""
        return self.tk.getint(self.tk.call(
            self._w, 'yposition', index))

    套路 y位置(分身, 索引): # new in Tk 8.5
        """返回 '索引' 对应菜单项的最上边像素的 y 位置."""
        返回 分身.tk.getint(分身.tk.call(分身._w, 'yposition', 索引))

类 〇菜单(Menu):
    """菜单部件, 可以显示菜单栏/下拉菜单/弹出菜单"""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造菜单部件. 选项如下:

        活动背景色, 活动边框宽度, 活动前景色, 背景色, 边框宽度, 鼠标样式,
        禁用时前景色, 字体, 前景色, 打开后命令, 边框样式, 选中时颜色,
        获得焦点, 撕下, 撕下时命令, 标题, 类型_
        """
        分身._菜单选项字典 = {
            '活动背景色':   'activebackground', 
            '活动边框宽度': 'activeborderwidth',
            '活动前景色':   'activeforeground',
            '背景色':       'background',
            '边框宽度':     'borderwidth', 
            '鼠标样式':     'cursor',
            '禁用时前景色':  'disabledforeground', 
            '字体':         'font', 
            '前景色':       'foreground',
            '打开后命令':   'postcommand', 
            '边框样式':     'relief', 
            '选中时颜色':   'selectcolor', 
            '获得焦点':     'takefocus',  
            '撕下':         'tearoff', 
            '撕下时命令':   'tearoffcommand', 
            '标题':         'title', 
            '类型_':        'type_'
        }
        #分身._菜单选项字典.更新(_部件通用选项字典)
        分身._菜单选项值字典 = {
            '上方': 'top',
            '下方': 'bottom',
            '无':   'none',
            '正常': 'normal',
            '活动': 'active',
            '禁用': 'disabled'
        }
        分身._菜单选项值字典.更新(_部件通用选项值字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._菜单选项字典, 分身._菜单选项值字典)
        Menu.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)

    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._菜单选项字典, 分身._菜单选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Menubutton(Widget):
    """Menubutton widget, obsolete since Tk8.0."""

    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, 'menubutton', cnf, kw)


class Message(Widget):
    """Message widget to display multiline text. Obsolete since Label does it too."""

    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, 'message', cnf, kw)


class Radiobutton(Widget):
    """Radiobutton widget which shows only one of several buttons in on-state."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a radiobutton widget with the parent MASTER.

        Valid resource names: activebackground, activeforeground, anchor,
        background, bd, bg, bitmap, borderwidth, command, cursor,
        disabledforeground, fg, font, foreground, height,
        highlightbackground, highlightcolor, highlightthickness, image,
        indicatoron, justify, padx, pady, relief, selectcolor, selectimage,
        state, takefocus, text, textvariable, underline, value, variable,
        width, wraplength."""
        Widget.__init__(self, master, 'radiobutton', cnf, kw)

    def deselect(self):
        """将按钮置于未选中状态."""
        self.tk.call(self._w, 'deselect')

    取消选择 = deselect

    def flash(self):
        """让按钮闪烁."""
        self.tk.call(self._w, 'flash')

    闪烁 = flash

    def invoke(self):
        """切换按钮, 调用相关命令 (如有)."""
        return self.tk.call(self._w, 'invoke')

    调用 = invoke

    def select(self):
        """将按钮置于选中状态."""
        self.tk.call(self._w, 'select')

    选择 = select

类 〇单选按钮(Radiobutton):
    """单选按钮部件, 多个按钮中仅有一个处于选中状态"""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个单选按钮部件. 选项如下:

        活动背景色, 活动前景色, 锚点, 背景色, 位图, 边框宽度, 鼠标样式,
        禁用时前景色, 字体, 前景色, 高亮背景, 高亮颜色, 高亮厚度, 图像, 对齐,
        水平边距, 垂直边距, 边框样式, 重复延迟, 重复间隔, 获得焦点, 文本,
        文本变量, 下划线, 分行长度

        命令, 混合模式, 高度, 指示开, 选中时颜色, 选中时图像, 状态, 值,
        变量, 宽度
        """
        分身._单选按钮选项字典 = {
            '命令':         'command', 
            '混合模式':     'compound', 
            '高度':         'height',
            '指示开':       'indicatoron',
            '选中时颜色':   'selectcolor', 
            '选中时图像':   'selectimage',
            '状态':         'state',  
            '值':           'value', 
            '变量':         'variable',
            '宽度':         'width' 
        }
        分身._单选按钮选项字典.更新(_部件通用选项字典)
        分身._单选按钮选项值字典 = {
            '上方': 'top',
            '下方': 'bottom',
            '无':   'none',
            '正常': 'normal',
            '活动': 'active',
            '禁用': 'disabled'
        }
        分身._单选按钮选项值字典.更新(_部件通用选项值字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._单选按钮选项字典, 分身._单选按钮选项值字典)
        Radiobutton.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)

    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._单选按钮选项字典, 分身._单选按钮选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Scale(Widget):
    """Scale widget which can display a numerical scale."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a scale widget with the parent MASTER.

        Valid resource names: activebackground, background, bigincrement, bd,
        bg, borderwidth, command, cursor, digits, fg, font, foreground, from,
        highlightbackground, highlightcolor, highlightthickness, label,
        length, orient, relief, repeatdelay, repeatinterval, resolution,
        showvalue, sliderlength, sliderrelief, state, takefocus,
        tickinterval, to, troughcolor, variable, width."""
        Widget.__init__(self, master, 'scale', cnf, kw)

    def get(self):
        """获取当前值: 整数或浮点数."""
        value = self.tk.call(self._w, 'get')
        try:
            return self.tk.getint(value)
        except (ValueError, TypeError, TclError):
            return self.tk.getdouble(value)

    获取 = get

    def set(self, value):
        """Set the value to VALUE."""
        self.tk.call(self._w, 'set', value)

    套路 设置(分身, 值):
        """将其值设置为给定的值."""
        分身.tk.call(分身._w, 'set', 值)
    
    def coords(self, value=None):
        """Return a tuple (X,Y) of the point along the centerline of the
        trough that corresponds to VALUE or the current value if None is
        given."""

        return self._getints(self.tk.call(self._w, 'coords', value))

    套路 坐标(分身, 值=空):
        """返回凹槽中心线上对应于 '值' (如果未给定则为当前值) 的点的 (X,Y) 元组."""
        返回 分身._getints(分身.tk.call(分身._w, 'coords', 值))

    def identify(self, x, y):
        """返回  X,Y 位于何处. 有效返回值为 "slider" (刻度),
        "though1" (凹槽1) 和 "though2" (凹槽2)."""
        return self.tk.call(self._w, 'identify', x, y)

    识别 = identify

类 〇刻度条(Scale):
    """刻度条部件, 可以显示带数值的刻度"""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造刻度条部件. 选项如下:

        活动背景色, 背景色, 大增量, 边框宽度, 命令, 鼠标样式, 位数, 字体,
        前景色, 起, 高亮背景, 高亮颜色, 高亮厚度, 标签, 长度, 方向, 边框样式,
        重复延迟, 重复间隔, 分辨率, 显示值, 滑块长度, 滑块样式, 状态, 获得焦点,
        刻度间隔, 止, 凹槽颜色, 变量, 宽度
        """
        分身._刻度条选项字典 = {
            '活动背景色':   'activebackground',
            '背景色':       'background',
            '大增量':       'bigincrement', 
            '边框宽度':     'borderwidth',
            '命令':         'command', 
            '鼠标样式':     'cursor',
            '位数':         'digits', 
            '字体':         'font', 
            '前景色':       'foreground',
            '起':          'from_',
            '高亮背景':     'highlightbackground', 
            '高亮颜色':     'highlightcolor',
            '高亮厚度':     'highlightthickness',
            '标签':         'label',
            '长度':         'length', 
            '方向':         'orient', 
            '边框样式':     'relief', 
            '重复延迟':     'repeatdelay',
            '重复间隔':     'repeatinterval',
            '分辨率':       'resolution',
            '显示值':       'showvalue', 
            '滑块长度':      'sliderlength', 
            '滑块样式':      'sliderrelief', 
            '状态':         'state', 
            '获得焦点':     'takefocus',
            '刻度间隔':     'tickinterval', 
            '止':           'to', 
            '凹槽颜色':     'troughcolor', 
            '变量':         'variable', 
            '宽度':         'width'
        }
        #分身._刻度条选项字典.更新(_部件通用选项字典)
        分身._刻度条选项值字典 = {
            '横向': 'horizontal',
            '纵向': 'vertical'
        }
        分身._刻度条选项值字典.更新(_颜色字典)
        分身._刻度条选项值字典.更新(_边框样式字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._刻度条选项字典, 分身._刻度条选项值字典)
        Scale.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)
    
    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._刻度条选项字典, 分身._刻度条选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Scrollbar(Widget):
    """Scrollbar widget which displays a slider at a certain position."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a scrollbar widget with the parent MASTER.

        Valid resource names: activebackground, activerelief,
        background, bd, bg, borderwidth, command, cursor,
        elementborderwidth, highlightbackground,
        highlightcolor, highlightthickness, jump, orient,
        relief, repeatdelay, repeatinterval, takefocus,
        troughcolor, width."""
        Widget.__init__(self, master, 'scrollbar', cnf, kw)

    def activate(self, index=None):
        """Marks the element indicated by index as active.
        The only index values understood by this method are "arrow1",
        "slider", or "arrow2".  If any other value is specified then no
        element of the scrollbar will be active.  If index is not specified,
        the method returns the name of the element that is currently active,
        or None if no element is active."""
        return self.tk.call(self._w, 'activate', index) or None

    套路 激活(分身, 索引=空):
        """将索引指示的项目标志为活动. 有效索引值为 '箭头1'/'滑块'/'箭头2'.
        如果未指定索引, 则返回当前活动的元素 (或 空, 如果无活动元素)."""
        索引字典 = {
            '箭头1' : 'arrow1',
            '箭头2' : 'arrow2',
            '滑块' : 'slider'
        }
        索引 = 索引字典.获取(索引, 索引)
        返回 分身.tk.call(分身._w, 'activate', 索引) or None

    def delta(self, deltax, deltay):
        """Return the fractional change of the scrollbar setting if it
        would be moved by DELTAX or DELTAY pixels."""
        return self.tk.getdouble(
            self.tk.call(self._w, 'delta', deltax, deltay))

    套路 变化量(分身, 移动量x, 移动量y):
        """假设滚动条移动指定像素 (移动量x 或 移动量y), 返回
        滚动条设置的分数变化量."""
        返回 分身.tk.getdouble(
            分身.tk.call(分身._w, 'delta', 移动量x, 移动量x))

    def fraction(self, x, y):
        """返回对应于滑块位置 X,Y 的分数值."""
        return self.tk.getdouble(self.tk.call(self._w, 'fraction', x, y))

    分数 = fraction

    def identify(self, x, y):
        """返回位置  X,Y 下的元素: "arrow1" (箭头1), "slider" (滑块), 
        "arrow2" (箭头2) 或 ""."""
        return self.tk.call(self._w, 'identify', x, y)

    识别 = identify

    def get(self):
        """返回滑块位置的当前分数值 (上端和下端)."""
        return self._getdoubles(self.tk.call(self._w, 'get'))

    获取 = get

    def set(self, first, last):
        """Set the fractional values of the slider position (upper and
        lower ends as value between 0 and 1)."""
        self.tk.call(self._w, 'set', first, last)

    套路 设置(分身, 首, 尾):
        """设置滑块位置的分数值 (上端和下端的值介于 0 和 1 之间)."""
        分身.tk.call(分身._w, 'set', 首, 尾)

类 〇滚动条(Scrollbar):
    """滚动条部件, 在一定位置显示一个滑块."""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个滚动条部件. 选项如下:

        活动背景色, 活动滑块样式, 背景色, 边框宽度, 命令, 鼠标样式,
        元素边框宽度, 高亮背景, 高亮颜色, 高亮厚度, 跳过, 方向, 边框样式,
        重复延迟, 重复间隔, 获得焦点, 凹槽颜色, 宽度
        """
        分身._滚动条选项字典 = {
            '活动背景色':   'activebackground', 
            '活动滑块样式': 'activerelief',
            '背景色':       'background',  
            '边框宽度':     'borderwidth', 
            '命令':         'command', 
            '鼠标样式':     'cursor',
            '元素边框宽度': 'elementborderwidth', 
            '高亮背景':     'highlightbackground', 
            '高亮颜色':     'highlightcolor',
            '高亮厚度':     'highlightthickness', 
            '跳过':         'jump', 
            '方向':         'orient',
            '边框样式':     'relief', 
            '重复延迟':     'repeatdelay',
            '重复间隔':     'repeatinterval',
            '获得焦点':     'takefocus', 
            '凹槽颜色':     'troughcolor', 
            '宽度':         'width'
        }
        #分身._滚动条选项字典.更新(_部件通用选项字典)
        分身._滚动条选项值字典 = {
            '横向': 'horizontal',
            '纵向': 'vertical'
        }
        分身._滚动条选项值字典.更新(_颜色字典)
        分身._滚动条选项值字典.更新(_边框样式字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._滚动条选项字典, 分身._滚动条选项值字典)
        Scrollbar.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)
    
    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._滚动条选项字典, 分身._滚动条选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class Text(Widget, XView, YView):
    """Text widget which can display text in various forms."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a text widget with the parent MASTER.

        STANDARD OPTIONS

            background, borderwidth, cursor,
            exportselection, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, insertbackground,
            insertborderwidth, insertofftime,
            insertontime, insertwidth, padx, pady,
            relief, selectbackground,
            selectborderwidth, selectforeground,
            setgrid, takefocus,
            xscrollcommand, yscrollcommand,

        WIDGET-SPECIFIC OPTIONS

            autoseparators, height, maxundo,
            spacing1, spacing2, spacing3,
            state, tabs, undo, width, wrap,

        """
        Widget.__init__(self, master, 'text', cnf, kw)

    def bbox(self, index):
        """Return a tuple of (x,y,width,height) which gives the bounding
        box of the visible part of the character at the given index."""
        return self._getints(
                self.tk.call(self._w, 'bbox', index)) or None

    套路 包围盒(分身, 索引):
        """返回一个元组 (x,y,宽,高), 它表示给定索引对应字符的可见部分的
        包围盒."""
        返回 分身._getints(
                分身.tk.call(分身._w, 'bbox', 索引)) or None

    def compare(self, index1, op, index2):
        """Return whether between index INDEX1 and index INDEX2 the
        relation OP is satisfied. OP is one of <, <=, ==, >=, >, or !=."""
        return self.tk.getboolean(self.tk.call(
            self._w, 'compare', index1, op, index2))

    套路 比较(分身, 索引1, 操作符, 索引2):
        """返回 '索引1' 和 '索引2' 之间是否满足 '操作符' 所表示的关系.
        有效操作符为: <, <=, ==, >=, >, !=."""
        返回 分身.tk.getboolean(分身.tk.call(
            分身._w, 'compare', 索引1, 操作符, 索引2))

    def count(self, index1, index2, *args): # new in Tk 8.5
        """Counts the number of relevant things between the two indices.
        If index1 is after index2, the result will be a negative number
        (and this holds for each of the possible options).

        The actual items which are counted depends on the options given by
        args. The result is a list of integers, one for the result of each
        counting option given. Valid counting options are "chars",
        "displaychars", "displayindices", "displaylines", "indices",
        "lines", "xpixels" and "ypixels". There is an additional possible
        option "update", which if given then all subsequent options ensure
        that any possible out of date information is recalculated."""
        args = ['-%s' % arg for arg in args if not arg.startswith('-')]
        args += [index1, index2]
        res = self.tk.call(self._w, 'count', *args) or None
        if res is not None and len(args) <= 3:
            return (res, )
        else:
            return res

    套路 计数(分身, 索引1, 索引2, *参数):
        """计数两个索引之间的相关项目的数量. 如果 '索引1' 在 '索引2' 后面,
        则结果为负数.

        计数的实际项目取决于 '参数' 给出的选项. 结果为一个整数列表. 有效
        计数选项为: "chars", "displaychars", "displayindices",
        "displaylines", "indices", "lines", "xpixels", "ypixels". 还有
        一个可能选项为 'update'，如有该选项，则所有随后的选项会确保任何过期
        的信息得到重新计算。  
        """
        参数字典 = {
            '字符数' : 'chars',
            '显示字符数' : 'displaychars',
            '显示索引数' : 'displayindices',
            '显示行数' : 'displaylines',
            '索引数' : 'indices',
            '行数' : 'lines',
            'x像素数' : 'xpixels',
            'y像素数' : 'ypixels',
            '更新' : 'update'
        }
        参数 = _星号参数中转英(参数, 参数字典)
        返回 分身.count(索引1, 索引2, *参数)

    def debug(self, boolean=None):
        """Turn on the internal consistency checks of the B-Tree inside the text
        widget according to BOOLEAN."""
        if boolean is None:
            return self.tk.getboolean(self.tk.call(self._w, 'debug'))
        self.tk.call(self._w, 'debug', boolean)

    套路 调试(分身, 布尔值=空):
        """根据布尔值开启文本框部件内部的 B 树的内部一致性检查."""
        if 布尔值 is None:
            return 分身.tk.getboolean(分身.tk.call(分身._w, 'debug'))
        分身.tk.call(分身._w, 'debug', 布尔值)

    def delete(self, index1, index2=None):
        """Delete the characters between INDEX1 and INDEX2 (not included)."""
        self.tk.call(self._w, 'delete', index1, index2)

    套路 删除(分身, 索引1, 索引2=空):
        """删除 '索引1' 和 '索引2' (不含) 之间的字符."""
        如果 索引2 == '末尾':
            索引2 = 'end'
        分身.tk.call(分身._w, 'delete', 索引1, 索引2)

    def dlineinfo(self, index):
        """Return tuple (x,y,width,height,baseline) giving the bounding box
        and baseline position of the visible part of the line containing
        the character at INDEX."""
        return self._getints(self.tk.call(self._w, 'dlineinfo', index))

    套路 双重行信息(分身, 索引):
        """返回元组 (x,y,宽,高,基线), 表示索引对应字符所在行的可见部分的
        包围框和基线位置."""
        return 分身._getints(分身.tk.call(分身._w, 'dlineinfo', 索引))

    def dump(self, index1, index2=None, command=None, **kw):
        """Return the contents of the widget between index1 and index2.

        The type of contents returned in filtered based on the keyword
        parameters; if 'all', 'image', 'mark', 'tag', 'text', or 'window' are
        given and true, then the corresponding items are returned. The result
        is a list of triples of the form (key, value, index). If none of the
        keywords are true then 'all' is used by default.

        If the 'command' argument is given, it is called once for each element
        of the list of triples, with the values of each triple serving as the
        arguments to the function. In this case the list is not returned."""
        args = []
        func_name = None
        result = None
        if not command:
            # Never call the dump command without the -command flag, since the
            # output could involve Tcl quoting and would be a pain to parse
            # right. Instead just set the command to build a list of triples
            # as if we had done the parsing.
            result = []
            def append_triple(key, value, index, result=result):
                result.append((key, value, index))
            command = append_triple
        try:
            if not isinstance(command, str):
                func_name = command = self._register(command)
            args += ["-command", command]
            for key in kw:
                if kw[key]: args.append("-" + key)
            args.append(index1)
            if index2:
                args.append(index2)
            self.tk.call(self._w, "dump", *args)
            return result
        finally:
            if func_name:
                self.deletecommand(func_name)

    套路 转储(分身, 索引1, 索引2=空, 命令=空, **关键词参数):
        """返回 '索引1' 和 '索引2' 之间部件的内容."""
        返回 分身.dump(分身, 索引1, index2=索引2, command=命令, **关键词参数)

    ## new in tk8.4
    def edit(self, *args):
        """Internal method

        This method controls the undo mechanism and
        the modified flag. The exact behavior of the
        command depends on the option argument that
        follows the edit argument. The following forms
        of the command are currently supported:

        edit_modified, edit_redo, edit_reset, edit_separator
        and edit_undo

        """
        return self.tk.call(self._w, 'edit', *args)

    def edit_modified(self, arg=None):
        """Get or Set the modified flag

        If arg is not specified, returns the modified
        flag of the widget. The insert, delete, edit undo and
        edit redo commands or the user can set or clear the
        modified flag. If boolean is specified, sets the
        modified flag of the widget to arg.
        """
        return self.edit("modified", arg)

    套路 编辑_已修改(分身, 参数=空):
        """获取或设置已修改标志"""
        return 分身.edit("modified", 参数)

    def edit_redo(self):
        """恢复上次撤消的编辑

        When the undo option is true, reapplies the last
        undone edits provided no other edits were done since
        then. Generates an error when the redo stack is empty.
        Does nothing when the undo option is false.
        """
        return self.edit("redo")

    编辑_恢复 = edit_redo

    def edit_reset(self):
        """清除撤消和恢复栈
        """
        return self.edit("reset")

    编辑_重置 = edit_reset

    def edit_separator(self):
        """在撤消栈中插入一个分隔符 (边界).

        当撤消选项为 假 时, 不执行任何操作.
        """
        return self.edit("separator")

    编辑_分隔符 = edit_separator

    def edit_undo(self):
        """撤消上次编辑操作

        If the undo option is true. An edit action is defined
        as all the insert and delete commands that are recorded
        on the undo stack in between two separators. Generates
        an error when the undo stack is empty. Does nothing
        when the undo option is false
        """
        return self.edit("undo")

    编辑_撤消 = edit_undo

    def get(self, index1, index2=None):
        """Return the text from INDEX1 to INDEX2 (not included)."""
        return self.tk.call(self._w, 'get', index1, index2)

    套路 获取(分身, 索引1, 索引2=空):
        """返回从 '索引1' 到 '索引2' (不含) 的文本."""
        return 分身.tk.call(分身._w, 'get', 索引1, 索引2)

    # (Image commands are new in 8.0)

    def image_cget(self, index, option):
        """Return the value of OPTION of an embedded image at INDEX."""
        if option[:1] != "-":
            option = "-" + option
        if option[-1:] == "_":
            option = option[:-1]
        return self.tk.call(self._w, "image", "cget", index, option)

    套路 图像_获取配置(分身, 索引, 选项):
        """返回 '索引' 对应的嵌入式图像的 '选项' 值."""
        返回 分身.image_cget(索引, 选项)

    def image_configure(self, index, cnf=None, **kw):
        """Configure an embedded image at INDEX."""
        return self._configure(('image', 'configure', index), cnf, kw)

    套路 图像_配置(分身, 索引, 配置=空, **关键词参数):
        """配置 '索引' 对应的嵌入式图像."""
        return 分身._configure(('image', 'configure', 索引), 配置, 关键词参数)

    def image_create(self, index, cnf={}, **kw):
        """Create an embedded image at INDEX."""
        return self.tk.call(
                 self._w, "image", "create", index,
                 *self._options(cnf, kw))

    套路 图像_创建(分身, 索引, 配置={}, **关键词参数):
        """在 '索引' 处创建一个嵌入式图像."""
        return 分身.tk.call(
                 分身._w, "image", "create", 索引,
                 *分身._options(配置, 关键词参数))

    def image_names(self):
        """返回此部件中的嵌入式图像的所有名称."""
        return self.tk.call(self._w, "image", "names")

    图像_名称列表 = image_names

    def index(self, index):
        """Return the index in the form line.char for INDEX."""
        return str(self.tk.call(self._w, 'index', index))

    套路 索引(分身, 索引):
        """返回 '索引' 的 '行.字符' 形式的索引."""
        return str(分身.tk.call(分身._w, 'index', 索引))

    def insert(self, index, chars, *args):
        """Insert CHARS before the characters at INDEX. An additional
        tag can be given in ARGS. Additional CHARS and tags can follow in ARGS."""
        self.tk.call((self._w, 'insert', index, chars) + args)

    套路 插入(分身, 索引, 字符串, *参数):
        """在 '索引' 对应字符的前面插入 '字符串'. '参数' 中可以给出
        附加标志, 然后还可以给出其他字符串和标志."""
        如果 索引 == '末尾':
            索引 = 'end'
        或如 索引 == '光标':
            索引 = 'insert'
        分身.tk.call((分身._w, 'insert', 索引, 字符串) + 参数)

    def mark_gravity(self, markName, direction=None):
        """Change the gravity of a mark MARKNAME to DIRECTION (LEFT or RIGHT).
        Return the current value if None is given for DIRECTION."""
        return self.tk.call(
            (self._w, 'mark', 'gravity', markName, direction))

    套路 标记_引力(分身, 标记名称, 方向=空):
        """将指定标记的引力更改到指定方向 ('左' 或 '右').
        如果 '方向' 为 空, 则返回当前值."""
        如果 方向 == '左':
            方向 = 'left'
        或如 方向 == '右':
            方向 = 'right'
        return 分身.tk.call(
            (分身._w, 'mark', 'gravity', 标记名称, 方向))

    def mark_names(self):
        """返回所有标记名称."""
        return self.tk.splitlist(self.tk.call(
            self._w, 'mark', 'names'))

    标记_名称列表 = mark_names

    def mark_set(self, markName, index):
        """Set mark MARKNAME before the character at INDEX."""
        self.tk.call(self._w, 'mark', 'set', markName, index)

    套路 标记_设置(分身, 标记名称, 索引):
        """在 '索引' 对应字符的前面设置指定标记."""
        分身.tk.call(分身._w, 'mark', 'set', 标记名称, 索引)

    def mark_unset(self, *markNames):
        """Delete all marks in MARKNAMES."""
        self.tk.call((self._w, 'mark', 'unset') + markNames)

    套路 标记_取消设置(分身, *标记名称):
        """删除 '标记名称' 中的所有标记."""
        分身.tk.call((分身._w, 'mark', 'unset') + 标记名称)

    def mark_next(self, index):
        """Return the name of the next mark after INDEX."""
        return self.tk.call(self._w, 'mark', 'next', index) or None

    套路 标记_下一个(分身, 索引):
        """返回 '索引' 之后的下一标记的名称."""
        返回 分身.tk.call(分身._w, 'mark', 'next', 索引) or None

    def mark_previous(self, index):
        """Return the name of the previous mark before INDEX."""
        return self.tk.call(self._w, 'mark', 'previous', index) or None

    套路 标记_上一个(分身, 索引):
        """返回 '索引' 之前的上一标记的名称."""
        返回 分身.tk.call(分身._w, 'mark', 'previous', 索引) or None

    def peer_create(self, newPathName, cnf={}, **kw): # new in Tk 8.5
        """Creates a peer text widget with the given newPathName, and any
        optional standard configuration options. By default the peer will
        have the same start and end line as the parent widget, but
        these can be overridden with the standard configuration options."""
        self.tk.call(self._w, 'peer', 'create', newPathName,
            *self._options(cnf, kw))

    套路 创建基友(分身, 新路径名, 配置={}, **关键词参数):
        """用给定 '新路径名' 和可选标准配置选项创建一个同辈文本框部件.
        """
        分身.tk.call(分身._w, 'peer', 'create', 新路径名,
            *分身._options(配置, 关键词参数))

    def peer_names(self): # new in Tk 8.5
        """返回此部件的同辈部件的列表 (不包括此部件本身)."""
        return self.tk.splitlist(self.tk.call(self._w, 'peer', 'names'))

    基友名称列表 = peer_names

    def replace(self, index1, index2, chars, *args): # new in Tk 8.5
        """Replaces the range of characters between index1 and index2 with
        the given characters and tags specified by args.

        See the method insert for some more information about args, and the
        method delete for information about the indices."""
        self.tk.call(self._w, 'replace', index1, index2, chars, *args)

    套路 替换(分身, 索引1, 索引2, 字符串, *参数): # new in Tk 8.5
        """用给定字符串和参数指定的标志替换 '索引1' 和 '索引2' 之间的字符串.

        参数信息参见 '插入' 方法, 索引信息参见 '删除' 方法."""
        分身.tk.call(分身._w, 'replace', 索引1, 索引2, 字符串, *参数)

    def scan_mark(self, x, y):
        """记住当前 X, Y 坐标."""
        self.tk.call(self._w, 'scan', 'mark', x, y)

    扫描_标记 = scan_mark

    def scan_dragto(self, x, y):
        """调整文本框视图, 以将 (x, y) 与 '扫描_标记' 给出的坐标
        之差放大 10 倍."""
        self.tk.call(self._w, 'scan', 'dragto', x, y)

    扫描_移至 = scan_dragto

    def search(self, pattern, index, stopindex=None,
           forwards=None, backwards=None, exact=None,
           regexp=None, nocase=None, count=None, elide=None):
        """Search PATTERN beginning from INDEX until STOPINDEX.
        Return the index of the first character of a match or an
        empty string."""
        args = [self._w, 'search']
        if forwards: args.append('-forwards')
        if backwards: args.append('-backwards')
        if exact: args.append('-exact')
        if regexp: args.append('-regexp')
        if nocase: args.append('-nocase')
        if elide: args.append('-elide')
        if count: args.append('-count'); args.append(count)
        if pattern and pattern[0] == '-': args.append('--')
        args.append(pattern)
        args.append(index)
        if stopindex: args.append(stopindex)
        return str(self.tk.call(tuple(args)))

    套路 搜索(分身, 模式, 索引, 停止索引=空, 向前=空, 
            向后=空, 完全匹配=空, 正则表达式=空, 
            忽略大小写=空, 个数=空, 省略=空):
        """搜索 '模式', 始于 '索引', 终于 '停止索引'.
        返回匹配的第一个字符的索引或空字符串."""
        args = [self._w, 'search']
        if 向前: args.append('-forwards')
        if 向后: args.append('-backwards')
        if 完全匹配: args.append('-exact')
        if 正则表达式: args.append('-regexp')
        if 忽略大小写: args.append('-nocase')
        if 省略: args.append('-elide')
        if 个数: args.append('-count'); args.append(个数)
        if 模式 and 模式[0] == '-': args.append('--')
        args.append(模式)
        args.append(索引)
        if 停止索引: args.append(停止索引)
        return str(分身.tk.call(tuple(args)))

    def see(self, index):
        """Scroll such that the character at INDEX is visible."""
        self.tk.call(self._w, 'see', index)

    套路 看见(分身, 索引):
        """滚动以使 '索引' 对应的字符可见."""
        分身.tk.call(分身._w, 'see', 索引)

    def tag_add(self, tagName, index1, *args):
        """Add tag TAGNAME to all characters between INDEX1 and index2 in ARGS.
        Additional pairs of indices may follow in ARGS."""
        self.tk.call(
            (self._w, 'tag', 'add', tagName, index1) + args)

    套路 标志_添加(分身, 标志名称, 索引1, *参数):
        """给 '索引1' 和参数中的索引2之间的所有字符添加给定标志.
        参数中还可以有其他索引对."""
        分身.tk.call(
            (分身._w, 'tag', 'add', 标志名称, 索引1) + 参数)

    def tag_unbind(self, tagName, sequence, funcid=None):
        """Unbind for all characters with TAGNAME for event SEQUENCE  the
        function identified with FUNCID."""
        self.tk.call(self._w, 'tag', 'bind', tagName, sequence, '')
        if funcid:
            self.deletecommand(funcid)

    套路 标志_解除绑定(分身, 标志名称, 序列, 函数id=空):
        """解除所有具给定标志的字符的事件 '序列' 绑定的 '函数id'."""
        分身.tk.call(分身._w, 'tag', 'bind', 标志名称, 序列, '')
        if 函数id:
            分身.deletecommand(函数id)

    def tag_bind(self, tagName, sequence, func, add=None):
        """Bind to all characters with TAGNAME at event SEQUENCE a call to function FUNC.

        An additional boolean parameter ADD specifies whether FUNC will be
        called additionally to the other bound function or whether it will
        replace the previous function. See bind for the return value."""
        return self._bind((self._w, 'tag', 'bind', tagName),
                  sequence, func, add)

    套路 标志_绑定(分身, 标志名称, 序列, 函数, 添加=空):
        """给所有具给定标志的字符的事件 '序列' 绑定对 '函数' 的调用.

        '添加' 为布尔值参数, 决定 '函数' 是取代先前绑定的函数还是另外添加.
        返回值参见 '绑定' 方法."""
        返回 分身._bind((分身._w, 'tag', 'bind', 标志名称),
                  序列, 函数, 添加)

    def tag_cget(self, tagName, option):
        """Return the value of OPTION for tag TAGNAME."""
        if option[:1] != '-':
            option = '-' + option
        if option[-1:] == '_':
            option = option[:-1]
        return self.tk.call(self._w, 'tag', 'cget', tagName, option)

    套路 标志_获取配置(分身, 标志名称, 选项):
        """返回给定标志的选项值."""
        if 选项[:1] != '-':
            选项 = '-' + 选项
        if 选项[-1:] == '_':
            选项 = 选项[:-1]
        返回 分身.tk.call(分身._w, 'tag', 'cget', 标志名称, 选项)

    def tag_configure(self, tagName, cnf=None, **kw):
        """Configure a tag TAGNAME."""
        return self._configure(('tag', 'configure', tagName), cnf, kw)

    套路 标志_配置(分身, 标志名称, 配置=空, **关键词参数):
        """配置给定标志."""
        返回 分身._configure(('tag', 'configure', 标志名称), 配置, 关键词参数)

    tag_config = tag_configure

    def tag_delete(self, *tagNames):
        """Delete all tags in TAGNAMES."""
        self.tk.call((self._w, 'tag', 'delete') + tagNames)

    套路 标志_删除(分身, *标志名称):
        """删除 '标志名称' 中的所有标志."""
        分身.tk.call((分身._w, 'tag', 'delete') + 标志名称)

    def tag_lower(self, tagName, belowThis=None):
        """Change the priority of tag TAGNAME such that it is lower
        than the priority of BELOWTHIS."""
        self.tk.call(self._w, 'tag', 'lower', tagName, belowThis)

    套路 标志_下移(分身, 标志名称, 低于此=空):
        """更改给定标志的优先级, 使其低于 '低于此' 标志的优先级."""
        分身.tk.call(分身._w, 'tag', 'lower', 标志名称, 低于此)

    def tag_names(self, index=None):
        """Return a list of all tag names."""
        return self.tk.splitlist(
            self.tk.call(self._w, 'tag', 'names', index))

    套路 标志_名称列表(分身, 索引=空):
        """返回所有标志名称的列表."""
        返回 分身.tk.splitlist(
            分身.tk.call(分身._w, 'tag', 'names', 索引))

    def tag_nextrange(self, tagName, index1, index2=None):
        """Return a list of start and end index for the first sequence of
        characters between INDEX1 and INDEX2 which all have tag TAGNAME.
        The text is searched forward from INDEX1."""
        return self.tk.splitlist(self.tk.call(
            self._w, 'tag', 'nextrange', tagName, index1, index2))

    套路 标志_下一范围(分身, 标志名称, 索引1, 索引2=空):
        """返回 '索引1' 和 '索引2' 之间所有具给定标志的字符的第一个序列的首尾
        索引列表. 从 '索引1' 开始向前搜索文本."""
        返回 分身.tk.splitlist(分身.tk.call(
            分身._w, 'tag', 'nextrange', 标志名称, 索引1, 索引2))

    def tag_prevrange(self, tagName, index1, index2=None):
        """Return a list of start and end index for the first sequence of
        characters between INDEX1 and INDEX2 which all have tag TAGNAME.
        The text is searched backwards from INDEX1."""
        return self.tk.splitlist(self.tk.call(
            self._w, 'tag', 'prevrange', tagName, index1, index2))

    套路 标志_上一范围(分身, 标志名称, 索引1, 索引2=空):
        """返回 '索引1' 和 '索引2' 之间所有具给定标志的字符的第一个序列的首尾
        索引列表. 从 '索引1' 开始向后搜索文本."""
        返回 分身.tk.splitlist(分身.tk.call(
            分身._w, 'tag', 'prevrange', 标志名称, 索引1, 索引2))

    def tag_raise(self, tagName, aboveThis=None):
        """Change the priority of tag TAGNAME such that it is higher
        than the priority of ABOVETHIS."""
        self.tk.call(
            self._w, 'tag', 'raise', tagName, aboveThis)

    套路 标志_上移(分身, 标志名称, 高于此=空):
        """更改给定标志的优先级, 使其高于 '高于此' 标志的优先级."""
        分身.tk.call(
            分身._w, 'tag', 'raise', 标志名称, 高于此)

    def tag_ranges(self, tagName):
        """Return a list of ranges of text which have tag TAGNAME."""
        return self.tk.splitlist(self.tk.call(
            self._w, 'tag', 'ranges', tagName))

    套路 标志_范围列表(分身, 标志名称):
        """返回具有给定标志的文本的范围列表."""
        返回 分身.tk.splitlist(分身.tk.call(
            分身._w, 'tag', 'ranges', 标志名称))

    def tag_remove(self, tagName, index1, index2=None):
        """Remove tag TAGNAME from all characters between INDEX1 and INDEX2."""
        self.tk.call(
            self._w, 'tag', 'remove', tagName, index1, index2)

    套路 标志_移除(分身, 标志名称, 索引1, 索引2=空):
        """从 '索引1' 和 '索引2' 之间的所有字符中移除给定标志."""
        分身.tk.call(
            分身._w, 'tag', 'remove', 标志名称, 索引1, 索引2)

    def window_cget(self, index, option):
        """Return the value of OPTION of an embedded window at INDEX."""
        if option[:1] != '-':
            option = '-' + option
        if option[-1:] == '_':
            option = option[:-1]
        return self.tk.call(self._w, 'window', 'cget', index, option)

    套路 窗口_获取配置(分身, 索引, 选项):
        """返回 '索引' 处的嵌入式窗口的 '选项' 值."""
        if 选项[:1] != '-':
            选项 = '-' + 选项
        if 选项[-1:] == '_':
            选项 = 选项[:-1]
        返回 分身.tk.call(分身._w, 'window', 'cget', 索引, 选项)

    def window_configure(self, index, cnf=None, **kw):
        """Configure an embedded window at INDEX."""
        return self._configure(('window', 'configure', index), cnf, kw)

    套路 窗口_配置(分身, 索引, 配置=空, **关键词参数):
        """配置 '索引' 处的嵌入式窗口."""
        返回 分身._configure(('window', 'configure', 索引), 配置, 关键词参数)

    window_config = window_configure

    def window_create(self, index, cnf={}, **kw):
        """Create a window at INDEX."""
        self.tk.call(
              (self._w, 'window', 'create', index)
              + self._options(cnf, kw))

    套路 窗口_创建(分身, 索引, 配置={}, **关键词参数):
        """在 '索引' 处创建一个窗口."""
        分身.tk.call(
              (分身._w, 'window', 'create', 索引)
              + 分身._options(配置, 关键词参数))

    def window_names(self):
        """返回此部件中的所有嵌入式窗口名称."""
        return self.tk.splitlist(
            self.tk.call(self._w, 'window', 'names'))

    窗口_名称列表 = window_names

    def yview_pickplace(self, *what):
        """Obsolete function, use see."""
        self.tk.call((self._w, 'yview', '-pickplace') + what)

类 〇文本框(Text):
    """文本框部件, 可以显示各种形式的文本."""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个文本框部件.
        
        背景色, 边框宽度, 鼠标样式, 选定内容可复制, 字体, 前景色, 高亮背景,
        高亮颜色, 高亮厚度, 光标颜色, 光标边框宽度, 光标灭时间, 光标亮时间,
        光标宽度, 水平边距, 垂直边距, 边框样式, 选中时背景色, 选中时边框宽度,
        选中时前景色, 设置网格, 获得焦点, 水平滚动命令, 垂直滚动命令, 自动分隔符,
        高度, 最大撤消次数, 间距1, 间距2, 间距3, 状态, 制表符宽, 撤消, 宽度, 自动换行 
        """
        分身._文本框选项字典 = {
            '背景色':           'background',
            '边框宽度':         'borderwidth', 
            '鼠标样式':         'cursor',
            '选定内容可复制':    'exportselection', 
            '字体':             'font', 
            '前景色':           'foreground',
            '高亮背景':         'highlightbackground', 
            '高亮颜色':         'highlightcolor',
            '高亮厚度':         'highlightthickness', 
            '光标颜色':         'insertbackground', 
            '光标边框宽度':     'insertborderwidth', 
            '光标灭时间':       'insertofftime', 
            '光标亮时间':       'insertontime', 
            '光标宽度':         'insertwidth', 
            '水平边距':         'padx', 
            '垂直边距':         'pady',
            '边框样式':         'relief', 
            '选中时背景色':     'selectbackground', 
            '选中时边框宽度':   'selectborderwidth', 
            '选中时前景色':     'selectforeground',  
            '设置网格':         'setgrid', 
            '获得焦点':         'takefocus',
            '水平滚动命令':     'xscrollcommand',
            '垂直滚动命令':     'yscrollcommand',
            '自动分隔符':       'autoseparators', 
            '高度':             'height', 
            '最大撤消次数':     'maxundo',
            '间距1':            'spacing1', 
            '间距2':            'spacing2', 
            '间距3':            'spacing3',
            '状态':             'state', 
            '制表符宽':         'tabs', 
            '撤消':             'undo', 
            '宽度':             'width', 
            '自动换行':         'wrap'
        }
        #分身._文本框选项字典.更新(_部件通用选项字典)
        分身._文本框选项值字典 = {
            '正常': 'normal',
            '禁用': 'disabled',
            '无':   'none',
            '字符': 'char',
            '单词': 'word'
        }
        分身._文本框选项值字典.更新(_颜色字典)
        分身._文本框选项值字典.更新(_边框样式字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._文本框选项字典, 分身._文本框选项值字典)
        Text.__init__(分身, 主对象, 配置字典, **关键词参数)
    
    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._文本框选项字典, 分身._文本框选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


class _setit:
    """Internal class. It wraps the command in the widget OptionMenu."""

    def __init__(self, var, value, callback=None):
        self.__value = value
        self.__var = var
        self.__callback = callback

    def __call__(self, *args):
        self.__var.set(self.__value)
        if self.__callback:
            self.__callback(self.__value, *args)


class OptionMenu(Menubutton):
    """OptionMenu which allows the user to select a value from a menu."""

    def __init__(self, master, variable, value, *values, **kwargs):
        """Construct an optionmenu widget with the parent MASTER, with
        the resource textvariable set to VARIABLE, the initially selected
        value VALUE, the other menu values VALUES and an additional
        keyword argument command."""
        kw = {"borderwidth": 2, "textvariable": variable,
              "indicatoron": 1, "relief": RAISED, "anchor": "c",
              "highlightthickness": 2}
        Widget.__init__(self, master, "menubutton", kw)
        self.widgetName = 'tk_optionMenu'
        menu = self.__menu = Menu(self, name="menu", tearoff=0)
        self.menuname = menu._w
        # 'command' is the only supported keyword
        callback = kwargs.get('command')
        if 'command' in kwargs:
            del kwargs['command']
        if kwargs:
            raise TclError('unknown option -'+kwargs.keys()[0])
        menu.add_command(label=value,
                 command=_setit(variable, value, callback))
        for v in values:
            menu.add_command(label=v,
                     command=_setit(variable, v, callback))
        self["menu"] = menu

    def __getitem__(self, name):
        if name == 'menu' or name == '菜单':
            return self.__menu
        return Widget.__getitem__(self, name)

    def destroy(self):
        """销毁此部件及相关菜单."""
        Menubutton.destroy(self)
        self.__menu = None

    销毁 = destroy

类 〇选项菜单(OptionMenu):
    """事实上是下拉菜单的改版，它弥补了列表框无法实现下拉列表框的遗憾.\n
    <变量> - 用于存放选定的选项值.\n
    <值>/<其他值> - 选项值
    """
    套路 __init__(分身, 主对象, 变量, 值, *其他值, **关键词参数):
        """关键词参数仅支持 '命令'. """
        如果 '命令' 在 关键词参数:
            关键词参数['command'] = 关键词参数['命令']
            删 关键词参数['命令']
        OptionMenu.__init__(分身, 主对象, 变量, 值, *其他值, **关键词参数)


class Image:
    """Base class for images."""
    _last_id = 0

    def __init__(self, imgtype, name=None, cnf={}, master=None, **kw):
        self.name = None
        if not master:
            master = _default_root
            if not master:
                raise RuntimeError('创建图像为时过早')
        self.tk = getattr(master, 'tk', master)
        if not name:
            Image._last_id += 1
            name = "pyimage%r" % (Image._last_id,) # tk itself would use image<x>
        if kw and cnf: cnf = _cnfmerge((cnf, kw))
        elif kw: cnf = kw
        options = ()
        for k, v in cnf.items():
            if callable(v):
                v = self._register(v)
            options = options + ('-'+k, v)
        self.tk.call(('image', 'create', imgtype, name,) + options)
        self.name = name

    def __str__(self): return self.name

    def __del__(self):
        if self.name:
            try:
                self.tk.call('image', 'delete', self.name)
            except TclError:
                # May happen if the root was destroyed
                pass

    def __setitem__(self, key, value):
        self.tk.call(self.name, 'configure', '-'+key, value)

    def __getitem__(self, key):
        return self.tk.call(self.name, 'configure', '-'+key)

    def configure(self, **kw):
        """Configure the image."""
        res = ()
        for k, v in _cnfmerge(kw).items():
            if v is not None:
                if k[-1] == '_': k = k[:-1]
                if callable(v):
                    v = self._register(v)
                res = res + ('-'+k, v)
        self.tk.call((self.name, 'config') + res)

    config = configure

    def height(self):
        """返回图像的高度."""
        return self.tk.getint(
            self.tk.call('image', 'height', self.name))

    高度 = height

    def type(self):
        """返回图像类型, 例如 "photo" (照片) 或 "bitmap" (位图)."""
        return self.tk.call('image', 'type', self.name)

    类型 = type

    def width(self):
        """返回图像宽度."""
        return self.tk.getint(
            self.tk.call('image', 'width', self.name))

    宽度 = width

类 〇图像(Image):
    '''图像基类'''

    套路 __init__(分身, 图像类型, 名称=空, 配置字典={}, 主对象=空, **关键词参数):
        Image.__init__(分身, 图像类型, name=名称, cnf=配置字典, master=主对象, **关键词参数)

    套路 配置(分身, **关键词参数):
        分身.configure(**关键词参数)


class PhotoImage(Image):
    """Widget which can display images in PGM, PPM, GIF, PNG format."""

    def __init__(self, name=None, cnf={}, master=None, **kw):
        """Create an image with NAME.

        Valid resource names: data, format, file, gamma, height, palette,
        width."""
        Image.__init__(self, 'photo', name, cnf, master, **kw)

    def blank(self):
        """显示一幅透明图像."""
        self.tk.call(self.name, 'blank')

    空白 = blank

    def cget(self, option):
        """Return the value of OPTION."""
        return self.tk.call(self.name, 'cget', '-' + option)
    
    套路 获取配置(分身, 选项):
        """返回 '选项' 的值."""
        返回 分身.tk.call(分身.name, 'cget', '-' + 选项)

    # XXX config

    def __getitem__(self, key):
        return self.tk.call(self.name, 'cget', '-' + key)
    # XXX copy -from, -to, ...?

    def copy(self):
        """返回一幅具有与此部件相同图像的新照片图像."""
        destImage = PhotoImage(master=self.tk)
        self.tk.call(destImage, 'copy', self.name)
        return destImage

    复制 = copy

    def zoom(self, x, y=''):
        """返回一幅具有与此部件相同图像的新照片图像, 但 x 方向缩放 x 倍,
        y 方向缩放 y 倍. 如果 y 未给出, 则默认值与 x 相同.
        """
        destImage = PhotoImage(master=self.tk)
        if y=='': y=x
        self.tk.call(destImage, 'copy', self.name, '-zoom',x,y)
        return destImage

    缩放 = zoom

    def subsample(self, x, y=''):
        """返回一幅具有与此部件相同图像的新照片图像, 但每 x 或 y 个像素
        仅使用最后一个像素. 如果 y 未给出, 则默认值与 x 相同.
        """
        destImage = PhotoImage(master=self.tk)
        if y=='': y=x
        self.tk.call(destImage, 'copy', self.name, '-subsample',x,y)
        return destImage

    子样本 = subsample

    def get(self, x, y):
        """返回 (x,y) 像素的颜色三元组."""
        return self.tk.call(self.name, 'get', x, y)

    获取 = get

    def put(self, data, to=None):
        """Put row formatted colors to image starting from
        position TO, e.g. image.put("{red green} {blue yellow}", to=(4,6))"""
        args = (self.name, 'put', data)
        if to:
            if to[0] == '-to':
                to = to[1:]
            args = args + ('-to',) + tuple(to)
        self.tk.call(args)

    套路 放置(分身, 数据, 位置=空):
        """将行格式化颜色放到从给定位置开始的图像. 例如:
        图像.放置("{red green} {blue yellow}", 位置=(4,6))"""
        返回 分身.put(分身, 数据, 位置)
    # XXX read

    def write(self, filename, format=None, from_coords=None):
        """Write image to file FILENAME in FORMAT starting from
        position FROM_COORDS."""
        args = (self.name, 'write', filename)
        if format:
            args = args + ('-format', format)
        if from_coords:
            args = args + ('-from',) + tuple(from_coords)
        self.tk.call(args)

    套路 写入(分身, 文件名, 格式=空, 从坐标=空):
        """以给定格式将从从给定坐标位置开始的图像写入给定文件"""
        返回 分身.write(分身, 文件名, 格式, 从坐标)

    def transparency_get(self, x, y):
        """如果 (x,y) 像素为透明, 则返回 真."""
        return self.tk.getboolean(self.tk.call(
            self.name, 'transparency', 'get', x, y))

    获取透明性 = transparency_get

    def transparency_set(self, x, y, boolean):
        """Set the transparency of the pixel at x,y."""
        self.tk.call(self.name, 'transparency', 'set', x, y, boolean)

    套路 设置透明性(分身, x, y, 布尔值):
        """设置 (x,y) 像素的透明性."""
        分身.tk.call(分身.name, 'transparency', 'set', x, y, 布尔值)

类 〇照片图像(PhotoImage):
    """可以显示 pgm/ppm/gif/png 格式图像的部件"""

    套路 __init__(分身, 名称=空, 配置字典={}, 主对象=空, **关键词参数):
        """创建给定名称的图像.

        选项有: 数据, 格式, 文件, 伽马值, 高度, 调色板, 宽度
        """
        照片选项字典 = {
            '数据' : 'data',
            '格式' : 'format',
            '文件' : 'file',
            '伽马值' : 'gamma',
            '高度' : 'height',
            '调色板' : 'palette',
            '宽度' : 'width'
        }
        关键词参数 = _关键词参数中转英(关键词参数, 照片选项字典)
        PhotoImage.__init__(分身, name=名称, cnf=配置字典, master=主对象, **关键词参数)


class BitmapImage(Image):
    """Widget which can display images in XBM format."""

    def __init__(self, name=None, cnf={}, master=None, **kw):
        """Create a bitmap with NAME.

        Valid resource names: background, data, file, foreground, maskdata, maskfile."""
        Image.__init__(self, 'bitmap', name, cnf, master, **kw)

类 〇位图图像(BitmapImage):
    """可以显示 xbm 格式图像的部件"""
    
    套路 __init__(分身, 名称=空, 配置字典={}, 主对象=空, **关键词参数):
        """创建给定名称的位图
        
        选项有: 背景, 数据, 文件, 前景, 掩码数据, 掩码文件
        """
        位图选项字典 = {
            '背景' : 'background',
            '数据' : 'data',
            '文件' : 'file',
            '前景' : 'foreground',
            '掩码数据' : 'maskdata',
            '掩码文件' : 'maskfile'
        }
        关键词参数 = _关键词参数中转英(关键词参数, 位图选项字典)
        BitmapImage.__init__(分身, name=名称, cnf=配置字典, master=主对象, **关键词参数)


def image_names():
    return _default_root.tk.splitlist(_default_root.tk.call('image', 'names'))

图像名称列表 = image_names

def image_types():
    return _default_root.tk.splitlist(_default_root.tk.call('image', 'types'))

图像类型列表 = image_types


class Spinbox(Widget, XView):
    """spinbox widget."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a spinbox widget with the parent MASTER.

        STANDARD OPTIONS

            activebackground, background, borderwidth,
            cursor, exportselection, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, insertbackground,
            insertborderwidth, insertofftime,
            insertontime, insertwidth, justify, relief,
            repeatdelay, repeatinterval,
            selectbackground, selectborderwidth
            selectforeground, takefocus, textvariable
            xscrollcommand.

        WIDGET-SPECIFIC OPTIONS

            buttonbackground, buttoncursor,
            buttondownrelief, buttonuprelief,
            command, disabledbackground,
            disabledforeground, format, from,
            invalidcommand, increment,
            readonlybackground, state, to,
            validate, validatecommand values,
            width, wrap,
        """
        Widget.__init__(self, master, 'spinbox', cnf, kw)

    def bbox(self, index):
        """Return a tuple of X1,Y1,X2,Y2 coordinates for a
        rectangle which encloses the character given by index.

        The first two elements of the list give the x and y
        coordinates of the upper-left corner of the screen
        area covered by the character (in pixels relative
        to the widget) and the last two elements give the
        width and height of the character, in pixels. The
        bounding box may refer to a region outside the
        visible area of the window.
        """
        return self._getints(self.tk.call(self._w, 'bbox', index)) or None

    套路 包围盒(分身, 索引):
        """返回一个矩形的 X1,Y1,X2,Y2 坐标元组, 该矩形包围索引对应的字符.

        元组的前两个元素表示该字符所覆盖屏幕区域左上角的 x 和 y 坐标 (相对于部件,
        单位为像素). 后两个元素表示该字符的宽度和高度, 单位为像素. 包围盒可以是窗口
        可见区域外部的区域.
        """
        返回 分身._getints(分身.tk.call(分身._w, 'bbox', 索引)) or None

    def delete(self, first, last=None):
        """Delete one or more elements of the spinbox.

        First is the index of the first character to delete,
        and last is the index of the character just after
        the last one to delete. If last isn't specified it
        defaults to first+1, i.e. a single character is
        deleted.  This command returns an empty string.
        """
        return self.tk.call(self._w, 'delete', first, last)

    套路 删除(分身, 首, 尾=空):
        """删除旋钮控件的一个或多个元素.

        '首' 是要删除的第一个字符的索引, '尾' 是要删除的最后一个字符之后的字符的索引.
        如果未指定 '尾', 则其默认值为 '首+1', 即删除单个字符. 此命令返回空字符串.
        """
        返回 分身.tk.call(分身._w, 'delete', 首, 尾)

    def get(self):
        """返回旋钮控件的字符串"""
        return self.tk.call(self._w, 'get')

    获取 = get

    def icursor(self, index):
        """Alter the position of the insertion cursor.

        The insertion cursor will be displayed just before
        the character given by index. Returns an empty string
        """
        return self.tk.call(self._w, 'icursor', index)

    套路 插入光标(分身, 索引):
        """改变插入光标的位置.

        插入光标将显示在 '索引' 对应的字符之后. 返回空字符串.
        """
        返回 分身.tk.call(分身._w, 'icursor', 索引)

    def identify(self, x, y):
        """返回部件位置 x, y 的名称.

        返回值为如下值之一:
        none (空), buttondown (下箭头), buttonup (上箭头), entry (输入框)
        """
        return self.tk.call(self._w, 'identify', x, y)

    识别 = identify

    def index(self, index):
        """Returns the numerical index corresponding to index
        """
        return self.tk.call(self._w, 'index', index)

    套路 索引(分身, 索引):
        """返回 '索引' 对应的数值索引
        """
        返回 分身.tk.call(分身._w, 'index', 索引)

    def insert(self, index, s):
        """Insert string s at index

         Returns an empty string.
        """
        return self.tk.call(self._w, 'insert', index, s)

    套路 插入(分身, 索引, 字符串):
        """在索引处插入指定字符串

        返回空字符串.
        """
        返回 分身.tk.call(分身._w, 'insert', 索引, 字符串)

    def invoke(self, element):
        """Causes the specified element to be invoked

        The element could be buttondown or buttonup
        triggering the action associated with it.
        """
        return self.tk.call(self._w, 'invoke', element)

    套路 调用(分身, 元素):
        """致使指定元素被调用

        元素可以是 buttondown (下箭头) 或 buttonup (上箭头),
        触发与之相关联的动作.
        """
        返回 分身.tk.call(分身._w, 'invoke', 元素)

    def scan(self, *args):
        """Internal function."""
        return self._getints(
            self.tk.call((self._w, 'scan') + args)) or ()

    def scan_mark(self, x):
        """记录旋钮控件窗口中当前视图的 x, 与 '扫描_移至' 命令一同使用.

        此命令通常与鼠标按钮在该部件中按下相关联. 返回空字符串.
        """
        return self.scan("mark", x)

    扫描_标记 = scan_mark

    def scan_dragto(self, x):
        """计算给定 x 参数与上次 '扫描_标记' 命令的 x 参数之差,
        然后以 x 坐标差的 10 倍左移或右移视图.

        此命令通常与部件中的鼠标移动事件相关联, 产生在窗口中高速拖动
        旋钮控件的效果. 返回值为空字符串.
        """
        return self.scan("dragto", x)

    扫描_移至 = scan_dragto

    def selection(self, *args):
        """Internal function."""
        return self._getints(
            self.tk.call((self._w, 'selection') + args)) or ()

    def selection_adjust(self, index):
        """Locate the end of the selection nearest to the character
        given by index,

        Then adjust that end of the selection to be at index
        (i.e including but not going beyond index). The other
        end of the selection is made the anchor point for future
        select to commands. If the selection isn't currently in
        the spinbox, then a new selection is created to include
        the characters between index and the most recent selection
        anchor point, inclusive.
        """
        return self.selection("adjust", index)

    套路 选定内容_调整(分身, 索引):
        """将选定内容的末端定位在最靠近索引对应字符的位置, 然后将该末端调整到
        索引位置 (包括但不超出索引). 选定内容的另一端是未来的 '选定内容_至' 
        命令的锚点.
        
        如果选定内容当前不在旋钮控件中, 则创建一个新的选定内容,
        以包括索引和最近选定内容锚点 (包含) 之间的字符.
        """
        返回 分身.selection("adjust", 索引)

    def selection_clear(self):
        """清除选定内容

        如果选定内容不在此部件中, 则不起作用.
        """
        return self.selection("clear")

    选定内容_清除 = selection_clear

    def selection_element(self, element=None):
        """Sets or gets the currently selected element.

        If a spinbutton element is specified, it will be
        displayed depressed.
        """
        return self.tk.call(self._w, 'selection', 'element', element)

    套路 选定内容_元素(分身, 元素=空):
        """设置或获取当前选定的元素.

        如果指定旋钮元素, 其将以按下状态显示.
        """
        返回 分身.tk.call(分身._w, 'selection', 'element', 元素)

    def selection_from(self, index):
        """Set the fixed end of a selection to INDEX."""
        self.selection('from', index)

    套路 选定内容_从(分身, 索引):
        """将选定内容的固定端设置为索引位置."""
        分身.selection('from', 索引)

    def selection_present(self):
        """如果旋钮控件中有字符被选中, 则返回 真, 否则返回 假."""
        return self.tk.getboolean(
            self.tk.call(self._w, 'selection', 'present'))

    选定内容_存在 = selection_present

    def selection_range(self, start, end):
        """Set the selection from START to END (not included)."""
        self.selection('range', start, end)

    套路 选定内容_范围(分身, 起, 止):
        """将选定内容设置为从 '起' 到 '止' (不包含)."""
        分身.selection('range', 起, 止)

    def selection_to(self, index):
        """Set the variable end of a selection to INDEX."""
        self.selection('to', index)

    套路 选定内容_至(分身, 索引):
        """将选定内容的可变端设置为索引位置."""
        分身.selection('to', 索引)


类 〇旋钮控件(Spinbox):
    """旋钮控件部件"""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个旋钮控件. 选项如下:
        
        活动背景色, 背景色, 边框宽度, 鼠标样式, 选定内容可复制, 字体, 前景色,
        高亮背景, 高亮颜色, 高亮厚度, 光标颜色, 光标边框宽度, 光标灭时间, 光标亮时间,
        光标宽度, 对齐, 边框样式, 重复延迟, 重复间隔, 选中时背景色, 选中时边框宽度,
        选中时前景色, 获得焦点, 文本变量, 水平滚动命令, 旋钮背景色, 旋钮鼠标,
        下箭头样式, 上箭头样式, 命令, 禁用时背景色, 禁用时前景色, 格式, 起, 无效命令,
        增量, 只读背景色, 状态, 止, 验证, 验证命令, 值序列, 宽度, 换行
        """
        分身._旋钮控件选项字典 = {
            '活动背景色':   'activebackground', 
            '背景色':           'background',
            '边框宽度':         'borderwidth', 
            '鼠标样式':         'cursor',
            '选定内容可复制':    'exportselection', 
            '字体':             'font', 
            '前景色':           'foreground',
            '高亮背景':         'highlightbackground', 
            '高亮颜色':         'highlightcolor',
            '高亮厚度':         'highlightthickness', 
            '光标颜色':         'insertbackground', 
            '光标边框宽度':     'insertborderwidth', 
            '光标灭时间':       'insertofftime', 
            '光标亮时间':       'insertontime', 
            '光标宽度':         'insertwidth', 
            '对齐':             'justify',
            '边框样式':         'relief', 
            '重复延迟':         'repeatdelay',
            '重复间隔':         'repeatinterval',
            '选中时背景色':     'selectbackground', 
            '选中时边框宽度':   'selectborderwidth', 
            '选中时前景色':     'selectforeground',  
            '获得焦点':         'takefocus',
            '文本变量':         'textvariable', 
            '水平滚动命令':     'xscrollcommand', 
            '旋钮背景色':       'buttonbackground', 
            '旋钮鼠标':         'buttoncursor',
            '下箭头样式':       'buttondownrelief', 
            '上箭头样式':       'buttonuprelief',
            '命令':             'command', 
            '禁用时背景色':     'disabledbackground',
            '禁用时前景色':     'disabledforeground', 
            '格式':             'format', 
            '起':               'from_',
            '无效命令':         'invalidcommand', 
            '增量':             'increment',
            '只读背景色':       'readonlybackground', 
            '状态':             'state', 
            '止':               'to',
            '验证':             'validate', 
            '验证命令':         'validatecommand', 
            '值序列':               'values',
            '宽度':             'width', 
            '换行':             'wrap'
        }
        #分身._旋钮控件选项字典.更新(_部件通用选项字典)
        分身._旋钮控件选项值字典 = {
            '正常': 'normal',
            '只读': 'readonly',
            '禁用': 'disabled'
        }
        分身._旋钮控件选项值字典.更新(_颜色字典)
        分身._旋钮控件选项值字典.更新(_对齐字典)
        分身._旋钮控件选项值字典.更新(_边框样式字典)
        分身._旋钮控件选项值字典.更新(_验证字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._旋钮控件选项字典, 分身._旋钮控件选项值字典)
        Spinbox.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)
    
    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._旋钮控件选项字典, 分身._旋钮控件选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)

###########################################################################


class LabelFrame(Widget):
    """labelframe widget."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a labelframe widget with the parent MASTER.

        STANDARD OPTIONS

            borderwidth, cursor, font, foreground,
            highlightbackground, highlightcolor,
            highlightthickness, padx, pady, relief,
            takefocus, text

        WIDGET-SPECIFIC OPTIONS

            background, class, colormap, container,
            height, labelanchor, labelwidget,
            visual, width
        """
        Widget.__init__(self, master, 'labelframe', cnf, kw)


类 〇标签框架(LabelFrame):
    """标签框架部件"""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个标签框架部件. 选项如下:
        
        背景色, 边框宽度, 类_, 颜色映射, 容器, 鼠标样式, 高度, 高亮背景,
        高亮颜色, 高亮厚度, 水平边距, 垂直边距, 边框样式, 获得焦点, 视觉,
        宽度, 字体, 前景色, 文本, 标签锚点, 标签部件
        """
        分身._标签框架选项字典 = {
            '背景色':       'background', 
            '边框宽度':     'borderwidth',
            '类_':          'class_',
            '颜色映射':     'colormap', 
            '容器':         'container', 
            '鼠标样式':     'cursor',
            '高度':         'height', 
            '高亮背景':     'highlightbackground', 
            '高亮颜色':     'highlightcolor',
            '高亮厚度':     'highlightthickness', 
            '水平边距':     'padx', 
            '垂直边距':     'pady', 
            '边框样式':     'relief', 
            '获得焦点':     'takefocus', 
            '视觉':         'visual', 
            '宽度':         'width',
            '字体':         'font', 
            '前景色':       'foreground',
            '文本':         'text',
            '标签锚点':     'labelanchor', 
            '标签部件':     'labelwidget'
        }
        #分身._标签框架选项字典.更新(_部件通用选项字典)
        分身._标签框架选项值字典 = {

        }
        分身._标签框架选项值字典.更新(_锚点字典)
        分身._标签框架选项值字典.更新(_颜色字典)
        分身._标签框架选项值字典.更新(_边框样式字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._标签框架选项字典, 分身._标签框架选项值字典)
        LabelFrame.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)
    
    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._标签框架选项字典, 分身._标签框架选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)

########################################################################


class PanedWindow(Widget):
    """panedwindow widget."""

    def __init__(self, master=None, cnf={}, **kw):
        """Construct a panedwindow widget with the parent MASTER.

        STANDARD OPTIONS

            background, borderwidth, cursor, height,
            orient, relief, width

        WIDGET-SPECIFIC OPTIONS

            handlepad, handlesize, opaqueresize,
            sashcursor, sashpad, sashrelief,
            sashwidth, showhandle,
        """
        Widget.__init__(self, master, 'panedwindow', cnf, kw)
        self._窗格配置选项字典 = {
            '之后' : 'after',
            '之前' : 'before',
            '高度' : 'height',
            '最小尺寸' : 'minsize',
            '水平边距' : 'padx',
            '垂直边距' : 'pady',
            '贴边' : 'sticky',
            '宽度' : 'width'
        }

    def add(self, child, **kw):
        """Add a child widget to the panedwindow in a new pane.

        The child argument is the name of the child widget
        followed by pairs of arguments that specify how to
        manage the windows. The possible options and values
        are the ones accepted by the paneconfigure method.
        """
        self.tk.call((self._w, 'add', child) + self._options(kw))

    套路 添加(分身, 子部件, **关键词参数):
        """在格窗的新窗格中添加一个子部件.
        
        选项和值同 '窗格_配置' 方法
        """
        关键词参数 = _关键词参数中转英(关键词参数, 分身._窗格配置选项字典)
        分身.add(子部件, **关键词参数)

    def remove(self, child):
        """Remove the pane containing child from the panedwindow

        All geometry management options for child will be forgotten.
        """
        self.tk.call(self._w, 'forget', child)

    套路 移除(分身, 子部件):
        """从格窗中移除包含子部件的窗格.

        子部件的所有几何管理选项都会被移除.
        """
        分身.tk.call(分身._w, 'forget', 子部件)

    forget = remove

    def identify(self, x, y):
        """识别点 x,y 处的格窗组件.

        If the point is over a sash or a sash handle, the result
        is a two element list containing the index of the sash or
        handle, and a word indicating whether it is over a sash
        or a handle, such as {0 sash} or {2 handle}. If the point
        is over any other part of the panedwindow, the result is
        an empty list.
        """
        return self.tk.call(self._w, 'identify', x, y)

    识别 = identify

    def proxy(self, *args):
        """Internal function."""
        return self._getints(
            self.tk.call((self._w, 'proxy') + args)) or ()

    def proxy_coord(self):
        """返回最近代理位置的 x,y 对
        """
        return self.proxy("coord")

    代理_坐标 = proxy_coord

    def proxy_forget(self):
        """从显示区中移除代理.
        """
        return self.proxy("forget")

    代理_移除 = proxy_forget

    def proxy_place(self, x, y):
        """将代理放在给定的 x,y 坐标.
        """
        return self.proxy("place", x, y)

    代理_放置 = proxy_place

    def sash(self, *args):
        """Internal function."""
        return self._getints(
            self.tk.call((self._w, 'sash') + args)) or ()

    def sash_coord(self, index):
        """Return the current x and y pair for the sash given by index.

        Index must be an integer between 0 and 1 less than the
        number of panes in the panedwindow. The coordinates given are
        those of the top left corner of the region containing the sash.
        pathName sash dragto index x y This command computes the
        difference between the given coordinates and the coordinates
        given to the last sash coord command for the given sash. It then
        moves that sash the computed difference. The return value is the
        empty string.
        """
        return self.sash("coord", index)

    套路 窗框_坐标(分身, 索引):
        """返回索引对应窗框的 x,y 对.

        Index must be an integer between 0 and 1 less than the
        number of panes in the panedwindow. The coordinates given are
        those of the top left corner of the region containing the sash.
        pathName sash dragto index x y This command computes the
        difference between the given coordinates and the coordinates
        given to the last sash coord command for the given sash. It then
        moves that sash the computed difference. The return value is the
        empty string.
        """
        返回 分身.sash("coord", 索引)

    def sash_mark(self, index):
        """Records x and y for the sash given by index;

        Used in conjunction with later dragto commands to move the sash.
        """
        return self.sash("mark", index)

    套路 窗框_标记(分身, 索引):
        """记录索引对应窗框的 x 和 y 坐标; 与随后的 '移至' 命令一起使用以移动窗框.
        """
        返回 分身.sash("mark", 索引)

    def sash_place(self, index, x, y):
        """Place the sash given by index at the given coordinates
        """
        return self.sash("place", index, x, y)

    套路 窗框_放置(分身, 索引, x, y):
        """将索引指定的窗框放在给定坐标
        """
        返回 分身.sash("place", 索引, x, y)

    def panecget(self, child, option):
        """Query a management option for window.

        Option may be any value allowed by the paneconfigure subcommand
        """
        return self.tk.call(
            (self._w, 'panecget') + (child, '-'+option))

    套路 窗格_获取配置(分身, 子部件, 选项):
        """查询窗口的管理选项.

        选项可以是 '窗格_配置' 子命令允许的任何值
        """        
        选项 = _关键词参数中转英(选项, 分身._窗格配置选项字典)
        返回 分身.tk.call(
            (分身._w, 'panecget') + (子部件, '-'+选项))

    def paneconfigure(self, tagOrId, cnf=None, **kw):
        """Query or modify the management options for window.

        If no option is specified, returns a list describing all
        of the available options for pathName.  If option is
        specified with no value, then the command returns a list
        describing the one named option (this list will be identical
        to the corresponding sublist of the value returned if no
        option is specified). If one or more option-value pairs are
        specified, then the command modifies the given widget
        option(s) to have the given value(s); in this case the
        command returns an empty string. The following options
        are supported:

        after window
            Insert the window after the window specified. window
            should be the name of a window already managed by pathName.
        before window
            Insert the window before the window specified. window
            should be the name of a window already managed by pathName.
        height size
            Specify a height for the window. The height will be the
            outer dimension of the window including its border, if
            any. If size is an empty string, or if -height is not
            specified, then the height requested internally by the
            window will be used initially; the height may later be
            adjusted by the movement of sashes in the panedwindow.
            Size may be any value accepted by Tk_GetPixels.
        minsize n
            Specifies that the size of the window cannot be made
            less than n. This constraint only affects the size of
            the widget in the paned dimension -- the x dimension
            for horizontal panedwindows, the y dimension for
            vertical panedwindows. May be any value accepted by
            Tk_GetPixels.
        padx n
            Specifies a non-negative value indicating how much
            extra space to leave on each side of the window in
            the X-direction. The value may have any of the forms
            accepted by Tk_GetPixels.
        pady n
            Specifies a non-negative value indicating how much
            extra space to leave on each side of the window in
            the Y-direction. The value may have any of the forms
            accepted by Tk_GetPixels.
        sticky style
            If a window's pane is larger than the requested
            dimensions of the window, this option may be used
            to position (or stretch) the window within its pane.
            Style is a string that contains zero or more of the
            characters n, s, e or w. The string can optionally
            contains spaces or commas, but they are ignored. Each
            letter refers to a side (north, south, east, or west)
            that the window will "stick" to. If both n and s
            (or e and w) are specified, the window will be
            stretched to fill the entire height (or width) of
            its cavity.
        width size
            Specify a width for the window. The width will be
            the outer dimension of the window including its
            border, if any. If size is an empty string, or
            if -width is not specified, then the width requested
            internally by the window will be used initially; the
            width may later be adjusted by the movement of sashes
            in the panedwindow. Size may be any value accepted by
            Tk_GetPixels.

        """
        if cnf is None and not kw:
            return self._getconfigure(self._w, 'paneconfigure', tagOrId)
        if isinstance(cnf, str) and not kw:
            return self._getconfigure1(
                self._w, 'paneconfigure', tagOrId, '-'+cnf)
        self.tk.call((self._w, 'paneconfigure', tagOrId) +
                 self._options(cnf, kw))

    套路 窗格_配置(分身, 标志或Id, 配置字典=空, **关键词参数):
        """查询或修改窗口的管理选项. 选项如下:

        之后 : 将此窗口插在给定窗口之后.\n
        之前 : 将此窗口插在给定窗口之前.\n
        高度 : 窗口高度\n
        最小尺寸 : 窗口不能小于该尺寸\n
        水平边距, 垂直边距, 宽度, 贴边
        """
        关键词参数 = _关键词参数中转英(关键词参数, 分身._窗格配置选项字典)
        返回 tk.PanedWindow.paneconfigure(分身, 标志或Id, cnf=配置字典, **关键词参数)

    paneconfig = paneconfigure

    def panes(self):
        """返回子窗格的有序列表."""
        return self.tk.splitlist(self.tk.call(self._w, 'panes'))

    窗格列表 = panes

类 〇格窗(PanedWindow):
    """格窗部件, 可用来为每一个子部件生成一个独立窗格，用户可以自由调整窗格的大小."""

    套路 __init__(分身, 主对象=空, 配置字典={}, **关键词参数):
        """构造一个格窗部件.

        标准选项

            背景色, 边框宽度, 鼠标样式, 高度, 方向, 边框样式, 宽度

        部件特定选项

            手柄边距, 手柄大小, 跟随鼠标调整, 窗框鼠标, 窗框边距, 窗框样式,
            窗框宽度, 显示手柄
        """
        分身._格窗选项字典 = {
            '背景色':       'background', 
            '边框宽度':     'borderwidth',
            '鼠标样式':     'cursor',
            '高度':         'height', 
            '方向':         'orient', 
            '边框样式':     'relief', 
            '宽度':         'width',
            '手柄边距':     'handlepad', 
            '手柄大小':     'handlesize', 
            '跟随鼠标调整':  'opaqueresize',
            '窗框鼠标':     'sashcursor', 
            '窗框边距':     'sashpad', 
            '窗框样式':     'sashrelief',
            '窗框宽度':     'sashwidth', 
            '显示手柄':     'showhandle'
        }
        #分身._格窗选项字典.更新(_部件通用选项字典)
        分身._格窗选项值字典 = {
            '横向': 'horizontal',
            '纵向': 'vertical'
        }
        分身._格窗选项值字典.更新(_边框样式字典)
        分身._格窗选项值字典.更新(_颜色字典)
        关键词参数 = _关键词参数中转英(关键词参数, 分身._格窗选项字典, 分身._格窗选项值字典)
        PanedWindow.__init__(分身, master=主对象, cnf=配置字典, **关键词参数)
    
    套路 配置(分身, 配置字典=空, **关键词参数):
        关键词参数 = _关键词参数中转英(关键词参数, 分身._格窗选项字典, 分身._格窗选项值字典)
        返回 分身.configure(cnf=配置字典, **关键词参数)


# 各种消息框

套路 消息框_信息(标题=空, 消息=空, **选项):
    "显示一条普通消息"
    返回 _msgbox.showinfo(标题, 消息, **选项)

套路 消息框_警告(标题=空, 消息=空, **选项):
    "显示一条警告消息"
    返回 _msgbox.showwarning(标题, 消息, **选项)

套路 消息框_出错(标题=空, 消息=空, **选项):
    "显示一条出错消息"
    返回 _msgbox.showerror(标题, 消息, **选项)

套路 消息框_询问(标题=空, 消息=空, **选项):
    "问一个问题"
    返回 '是' 如果 _msgbox.askquestion(标题, 消息, **选项) == 'yes' 否则 '否'

套路 消息框_确定取消(标题=空, 消息=空, **选项):
    "询问是否执行操作; 如果答案为 <确定> 则返回 <真> "
    返回 _msgbox.askokcancel(标题, 消息, **选项)

套路 消息框_是否(标题=空, 消息=空, **选项):
    "问一个问题; 如果答案为 <是> 则返回 <真> "
    返回 _msgbox.askyesno(标题, 消息, **选项)

套路 消息框_是否取消(标题=空, 消息=空, **选项):
    "问一个问题; 如果答案为 <是> 则返回 <真>, 如果取消则返回<空> "
    返回 _msgbox.askyesnocancel(标题, 消息, **选项)

套路 消息框_重试取消(标题=空, 消息=空, **选项):
    "询问是否再次尝试执行操作; 如果答案为 <是> 则返回 <真> "
    返回 _msgbox.askretrycancel(标题, 消息, **选项)


# Test:


def _test():
    root = Tk()
    text = "This is Tcl/Tk version %s" % TclVersion
    text += "\nThis should be a cedilla: \xe7"
    label = Label(root, text=text)
    label.pack()
    test = Button(root, text="Click me!",
              command=lambda root=root: root.test.configure(
                  text="[%s]" % root.test['text']))
    test.pack()
    root.test = test
    quit = Button(root, text="QUIT", command=root.destroy)
    quit.pack()
    # The following three commands are needed so the window pops
    # up on top on Windows...
    root.iconify()
    root.update()
    root.deiconify()
    root.mainloop()


if __name__ == '__main__':
    _test()
