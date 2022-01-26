#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：kevinleong1011@hotmail.com
@desc: 
"""
import fnmatch
import glob
import os
import re
import shutil
import sys
from datetime import datetime


def name(filename):
    """
    获取文件名，不带后缀
    :param filename: 文件路径
    :return:
    """
    return os.path.basename(filename).rsplit('.', maxsplit=1)[0]


def extension(filename):
    """
    获取文件扩展名
    :param filename:
    :return:
    """
    basename = os.path.basename(filename)
    try:
        dot_index = basename.rindex('.')
    except ValueError:
        dot_index = None
    return basename[dot_index:] if dot_index else None


def join(p, *paths):
    """
    拼接路径，支持父级符号 ..
    :param p:
    :param paths:
    :return:
    """
    for path in paths:
        parts = re.split(r'[/\\]', path)
        if len(parts) > 1:
            p = join(p, *parts)
        else:
            if path == '..':
                p = os.path.dirname(p)
            else:
                p = os.path.join(p, path)
    return Path(p.replace('\\', '/'))


def getdrive(path):
    """
    获取系统盘符
    :param path:
    :return:
    """
    return os.path.splitdrive(path)[0]


def delete(path):
    """
    删除路径
    :param path:
    :return:
    """
    if not os.path.exists(path):
        return False
    if os.path.isfile(path):
        os.remove(path)
    else:
        os.removedirs(path)
    return True


def search(pattern, path=None, recursive=True):
    """
    根据通配符查找文件
    :param pattern: 通配符
    :param path: 查找路径
    :param recursive: 是否递归查找
    :return:
    """
    if path is not None:
        if recursive:
            pattern = join(path, '**', pattern)
        else:
            pattern = join(path, pattern)
    return glob.glob(pattern, recursive=recursive)


def reverse_search(path, pattern):
    if not pattern:
        raise Exception('Pattern for searching is required!')
    if os.path.isfile(path):
        for _name in reverse_search(os.path.dirname(path), pattern):
            yield _name
    else:
        for _name in search(pattern, path):
            yield _name
        if os.path.ismount(path):
            return
        parent_dir = os.path.dirname(path)
        if parent_dir:
            for f in reverse_search(parent_dir, pattern):
                yield f


def copy(src, dest):
    # 支持通配符
    if os.path.isfile(src):
        shutil.copy(src, dest)
    else:
        if os.path.isdir(dest) and os.path.exists(dest):
            dest = os.path
        shutil.copytree(src, dest)


def rename(filename, new):
    """
    Rename a file or a directory.

    :param filename:
    :param new: new name
    :return:
    """
    shutil.move(filename, join(filename, '..', new))


def nodes(path):
    return re.split(r'[\\/]', path)


def list_dir(p):
    """
    枚举文件夹下的所有文件或子文件夹
    :param p: 路径，如果是文件，则取其所在文件夹
    :return: (filename, fullpath)
    """
    p = os.path.abspath(p)
    if os.path.isfile(p):
        p = os.path.dirname(p)
    for filename in os.listdir(p):
        yield filename, os.path.join(p, filename)

#
# def move(src, dest, overwrite=False, backfile=True):
#     """
#     移动文件
#     :param src: 源文件
#     :param dest: 目标目录
#     :param overwrite: 是否覆写
#     :param backfile: 如果目标位置有同名文件，是否备份
#     :return:
#     """
#     _dest = Path(dest)
#     if _dest.isfile and _dest.basename != src.basename:
#         dest = os.path.dirname(dest)
#     try:
#         shutil.move(src, dest)
#         return True
#     except shutil.Error as e:
#         if 'already exists' in str(e) and overwrite:
#             shutil.copy()
#             os.remove(os.path.join(dest, self.basename))
#             return move(src, dest)
#         return False


def __getattr__(item):
    v = getattr(os.path, item, None)
    if v is None:
        return getattr(shutil, item)
    return v


class Path(str):
    def __new__(cls, o, *args, **kwargs):  # 重写 __new__ 否则无法正常重写 __init__
        return super().__new__(cls, o)

    @property
    def basename(self) -> str:
        return os.path.basename(self)

    @property
    def extension(self):
        basename = self.basename
        try:
            dot_index = basename.rindex('.')
        except ValueError:
            dot_index = None
        return basename[dot_index:] if dot_index else None

    @property
    def pure_name(self):
        return self.basename.rsplit('.', maxsplit=1)[0]

    @property
    def name_without_extension(self):
        """名称（不包含扩展名）"""
        return self.basename.rsplit('.', maxsplit=1)[0]

    @property
    def name_no_ext(self):
        return self.basename.rsplit('.', maxsplit=1)[0]

    @property
    def size(self):
        return os.path.getsize(self)

    @property
    def create_time(self):
        return datetime.fromtimestamp(os.path.getctime(self))

    @property
    def mod_time(self):
        return datetime.fromtimestamp(os.path.getmtime(self))

    @property
    def last_access_time(self):
        return datetime.fromtimestamp(os.path.getatime(self))

    @property
    def isfile(self):
        return os.path.isfile(self)

    @property
    def isdir(self):
        return os.path.isdir(self)

    @property
    def ismount(self):
        """是否盘符"""
        return os.path.ismount(self)

    @property
    def parent(self):
        return self.__class__(os.path.dirname(self)) if not self.ismount else None

    @property
    def exists(self):
        return os.path.exists(self)

    @property
    def nodes(self):
        """将路径拆分成节点列表"""
        return re.split(r'[\\/]', self)

    def info(self, related: str = None):
        info = dict(name=self.basename,
                    path=self,
                    size=self.size,
                    create_time=self.create_time,
                    mod_time=self.mod_time,
                    last_access_time=self.last_access_time)
        if self.isfile:
            info['size'] = self.size
            info['type'] = 'file'
        else:
            info['type'] = 'dir'
        if related:
            related = related.strip(os.sep)
            info['relative_path'] = self.replace(related, '')
        return info

    def search(self, pattern, recursive=True):
        if not pattern:
            raise PathError('Pattern for searching is required!')
        for item in self.list():
            if fnmatch.fnmatch(item.basename, pattern):
                yield item
            if item.isdir and recursive:
                for f in item.search(pattern):
                    yield f

    def list(self, pattern=None):
        for _name in os.listdir(self):
            if pattern is None or (pattern and fnmatch.fnmatch(_name, pattern)):
                yield self.__class__(os.path.join(self, _name))

    def files(self, pattern=None):
        """
        列出所有子文件
        :param pattern:
        :return:
        """
        for item in self.list(pattern):
            if item.isfile:
                yield item

    def dirs(self, pattern=None):
        """
        列出目录中的所有文件夹
        :param pattern:
        :return:
        """
        for item in self.list(pattern):
            if item.isdir:
                yield item

    def walk_files(self, pattern=None, ):
        for root, dirs, files in os.walk(self):
            for file in files:
                if pattern is None or (pattern and fnmatch.fnmatch(file, pattern)):
                    yield file, self.__class__(root) / file

    def walk(self, pattern=None):
        for root, dirs, files in os.walk(self):
            for d in dirs:
                if pattern is None or (pattern and fnmatch.fnmatch(d, pattern)):
                    yield d, self.__class__(root) / d, 'dir'
            for file in files:
                if pattern is None or (pattern and fnmatch.fnmatch(file, pattern)):
                    yield file, self.__class__(root) / file, 'file'

    def reserve_search(self, pattern):
        """
        方向查找文件或文件夹
        :param pattern: 通配符
        :return:
        """
        if not pattern:
            raise PathError('Pattern for searching is required!')
        if self.isfile:
            for f in self.parent.reserve_search(pattern):
                yield f
        else:
            for f in self.list(pattern):
                yield f
            if self.parent:
                for f in self.parent.reserve_search(pattern):
                    yield f

    def open(self):
        if self.isfile:
            return open(self)
        else:
            raise PathError('Can not open a dir!')

    def makedirs(self, mode=0o777, exist_ok=False):
        path = self.parent if self.isfile else self
        os.makedirs(path, mode=mode, exist_ok=exist_ok)
        return self

    mkdirs = makedirs  # 别名

    def copy(self, dest):
        if self.isfile:
            shutil.copy(self, dest)
        else:
            shutil.copytree(self, dest)

    def move(self, dest, overwrite=False):
        """

        :param dest:
        :param overwrite:
        :return:
        """
        _dest = Path(dest)
        if _dest.isfile and _dest.basename != self.basename:
            dest = os.path.dirname(dest)
        try:
            shutil.move(self, dest)
            return True
        except shutil.Error as e:
            if 'already exists' in str(e) and overwrite:
                os.remove(os.path.join(dest, self.basename))
                return self.move(dest)
            return False

    def delete(self):
        """
        删除路径指向的文件或文件夹
        :return:
        """
        if not self.exists:
            return
        if self.isfile:
            os.remove(self)
        else:
            os.removedirs(self)

    def rename(self, new):
        """
        Rename a file or a directory.
        :param new: new name
        :return:
        """
        shutil.move(self, os.path.join(self.parent, new))

    @staticmethod
    def abspath(rel_path: str, base_dir=None):
        if os.path.isabs(rel_path):
            return rel_path
        if not base_dir:
            try:
                raise Exception('')
            except Exception:
                frame_str = str(sys.exc_info()[2].tb_frame.f_back)
                base_dir = os.path.normpath(re.findall(r'(?<=file \')(.+)(?=\', line)', frame_str)[0])
        if os.path.isfile(base_dir):
            base_dir = os.path.dirname(base_dir)
        cur_dir_parts = base_dir.split(os.sep)
        parts = re.split(r'[\\/]', rel_path)
        for part in parts:
            if part == '':
                parts = parts[1:]
            elif part == '..':
                cur_dir_parts = cur_dir_parts[:-1]
                parts = parts[1:]
            elif part == '.':
                parts = parts[1:]
            else:
                cur_dir_parts.extend([part])
        return Path(os.sep.join(cur_dir_parts))

    def join(self, *paths):
        return join(self, *paths)

    def expend(self, *paths):
        result = self
        for path in paths:
            result = result / path if result else Path(path)
        return result

    def __truediv__(self, other):
        if other:
            return self.__class__(os.path.join(self, other))
        return self

    @staticmethod
    def user_path(*paths):
        return Path(os.path.expanduser('~')).join(*paths)


class PathError(Exception):
    """
    """
