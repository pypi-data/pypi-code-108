# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Desc: 
"""
import os
import re
import sys

from .ospath import Path


def insert(root):
    """
    将路径插入sys.path
    :param root:
    :return:
    """
    if root in sys.path:
        sys.path.remove(root)
    sys.path.insert(0, root)
    return root


def find_project_root(path):
    """
    查找py工程根目录
    :param path:
    :return:
    """
    path = os.path.abspath(path)
    path = Path(path)
    root = path.parent if os.path.isfile(str(path)) else path
    while os.path.exists(os.path.join(root, '__init__.py')):
        root = root.parent
    return root


def get_object(name: str, raise_error=True):
    """
    根据名称获取对象
    :param name: 对象全名称，比如 demo.test.TestClass.my_method
    :param raise_error: 是否抛出异常
    :return: module/type/function
    """
    if not name:
        return
    if os.path.exists(name) and os.path.isabs(name):
        root = find_project_root(name)
        insert(root)
        if os.path.isfile(name):
            name = re.sub(r'[/\\]', '.', name[:-3][len(root) + 1:])
        else:
            name = re.sub(r'[/\\]', '.', name[len(root) + 1:])
        return get_object(name, raise_error=raise_error)
    else:
        nodes = name.split('.')
        o, module_name = None, ''
        for i in range(len(nodes)):
            module_name = '.'.join(nodes[:i + 1])
            try:
                o = __import__(module_name)
                i += 1
            except ModuleNotFoundError:
                break
        if o:
            for node in nodes[1:]:
                o = getattr(o, node, None)  # 如果py文件中直接写该函数调用，可能取不到，但不是问题
        if not o and raise_error:
            raise ModuleNotFoundError(module_name)
        return o
