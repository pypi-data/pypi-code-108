# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Desc: 
"""
import inspect
import io
import re
import sys
import traceback

from makit.lib import py


class CallInfo:
    def __init__(self, frame):
        self.__frame = frame
        self._filename = None
        self._lineno = None
        self._caller = None

    @property
    def filename(self):
        return self.__frame.f_code.co_filename

    @property
    def lineno(self):
        return self.__frame.f_lineno

    @property
    def func_name(self):
        return self.__frame.f_code.co_name

    @property
    def caller(self):
        frame_str = str(self.__frame)
        caller_name = re.findall(r'code (.+)>', frame_str)[0]
        f_locals = self.__frame.f_locals
        if 'self' in f_locals:
            instance = f_locals.get('self')
            return getattr(instance, caller_name)
        elif 'cls' in f_locals:
            cls = f_locals.get('cls')
            return getattr(cls, caller_name)

    @property
    def module(self):
        return py.get_object(self.filename, raise_error=False)

    def get_stack(self):
        sio = io.StringIO()
        sio.write('Stack (most recent call last):\n')
        traceback.print_stack(self.__frame, file=sio)
        stack_info = sio.getvalue()
        if stack_info[-1] == '\n':
            stack_info = stack_info[:-1]
        sio.close()
        return stack_info

    def flat(self):
        return self.filename, self.module, self.func_name, self.lineno, self.get_stack()


# def parse_caller(initial_depth=2, frame_depth=1):
#     frame_depth = frame_depth or 1
#     f = getattr(sys, '_getframe')(initial_depth)
#     while f and frame_depth > 1:
#         f = f.f_back
#         frame_depth -= 1
#     if not f:
#         return
#     return CallInfo(f)


def parse_caller(invoked_file):
    """
    用于解析函数调用者信息
    :param invoked_file: 被调用函数所在的py文件路径
    :return:
    """
    f = getattr(sys, '_getframe')(0)
    found, changed = None, False
    while f:
        code_file = f.f_code.co_filename
        if code_file == invoked_file and found is None:
            found = True
        if found and code_file != invoked_file:
            changed = True
        if found and changed:
            break
        f = f.f_back
    if not f:
        return
    return CallInfo(f)


def get_name(func):
    """
    获取函数名称
    :param func:
    :return:
    """
    if inspect.isfunction(func):
        name = re.search(r'<function (\S+) at', str(func)).groups()[0]
    elif inspect.ismethod(func):
        name = re.search(r'<bound method (\S+) of', str(func)).groups()[0]
    elif inspect.ismodule(func):
        return func.__name__
    else:
        return func.__class__.__name__
    return name


def get_class(routine, module=None):
    if inspect.isclass(routine):
        return routine
    module = module or inspect.getmodule(routine)
    name = get_name(routine)
    class_name = name[:name.rindex('.')] if '.' in name else None
    if class_name:  # 如果是类方法
        # reload(module)
        cls = getattr(module, class_name, None)
        return cls


class _Arg:
    def __init__(self, name, required, default=None):
        self.name = name
        self.required = required
        self.default = default

    def __repr__(self):
        return f'<Arg {self.name}{"" if self.required else "=" + str(self.default)}>'


class Func:
    def __init__(self, fn):
        self.fn = fn
        self.default_kw = {}  # 默认参数
        self.called_by_defaults = True  # 是否使用默认值调用，用于恢复执行

    @property
    def name(self):
        if self.cls:
            if inspect.isclass(self.fn):
                return f'{self.cls.__name__}.__init__'
            return f'{self.cls.__name__}.{self.fn.__name__}'
        return get_name(self.fn)

    def __call__(self, *args, **kwargs):
        self.module = inspect.getmodule(self.fn)
        self.cls = get_class(self.fn, module=self.module)

        if inspect.isclass(self.fn):
            full_args = inspect.getfullargspec(self.fn.__init__)
            varargs, varkw = full_args.varargs, full_args.varkw
            if self.fn.__init__ == object.__init__:
                varargs, varkw = None, None
        else:
            full_args = inspect.getfullargspec(self.fn)
            varargs, varkw = full_args.varargs, full_args.varkw
        _args = full_args.args

        if any([
            inspect.ismethod(self.fn),  # 如果是实例方法，则忽略掉第一个参数 self
            inspect.isclass(self.fn),  # 如果是类
            (not inspect.ismodule(self.fn) and not inspect.isfunction(self.fn))  # 如果是__call__
        ]):
            _args = full_args.args[1:]
        actual_args, actual_kw, args = [], {}, list(args)
        for i in range(len(_args)):
            name = _args[i]
            required = len(full_args.defaults or []) < len(_args) - i
            index = len(_args) - i
            if not required:
                default = full_args.defaults[-index] if full_args.defaults else None
                self.default_kw[name] = default
            else:
                default = None
            if name in kwargs:
                if required:
                    actual_args.append(kwargs.pop(name))
                else:
                    v = kwargs.pop(name)
                    actual_args.append(v)
                    if default != v:
                        self.called_by_defaults = False
            else:
                if args:
                    v = args.pop(0)
                    if not required and default != v:
                        self.called_by_defaults = False
                    actual_args.append(v)
                else:
                    if required:
                        raise TypeError(f"{self.name}() missing 1 required positional argument: '{name}'")
        if varkw:
            actual_kw.update(**kwargs)
        if varargs:
            actual_args = [*actual_args, *args]
        return self.fn(*actual_args, **actual_kw)


def run(_func, *args, **kwargs):
    """
    调用函数，可正确处理参数，不会因为参数给多或者顺序错乱而导致错误
    :param _func:
    :param args:
    :param kwargs:
    :return:
    """
    return Func(_func)(*args, **kwargs)


call = run
