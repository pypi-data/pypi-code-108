import logging
import os
from logging import Logger
from threading import Lock

from django.conf import settings

logger1 = logging.getLogger(__name__)


def dictinct_list(l, _sorted=False, key=None):
    if l is None:
        return None

    ds = []
    if isinstance(l, list):
        ds = list(set(l.copy()))

    if isinstance(l, map):
        ds = list(set(list(l).copy()))

    if _sorted:
        return sorted(ds, key=lambda x: x[key])
    return ds


def setAttr(o, name, value):
    if not isinstance(o, dict):
        return o

    o[name] = value
    return o


def delAttr(o, name):
    if not isinstance(o, dict):
        return o

    if name in o:
        del o[name]
        return True
    else:
        return False


def delAttr1(o, name):
    if not isinstance(o, dict):
        return o

    _o = o.copy()
    if name in _o:
        del _o[name]
        return _o
    else:
        return _o


def isEmptyDict(dictionary):
    for element in dictionary:
        if element:
            return True
        return False


def delete_drive_leter(path):
    altsep = os.path.altsep
    if altsep is None:
        altsep = '\\'

    path = path.replace(os.path.sep, altsep)
    if path.find(':') != -1:
        path = (path.split(':')[1]).replace(os.path.sep, altsep)
        path = ''.join(path)

    if path.startswith(altsep):
        return path[1:]
    return path


def get_drive_leter(path):
    path = path.replace(os.path.sep, os.path.altsep)
    if path.find(':') != -1:
        return f"{(path.split(':')[0])}:"
    return None


def replace_alt_set(path):
    from isc_common.fields.files import FieldFileEx
    if isinstance(path, FieldFileEx):
        path = path.path
        return path.replace(os.altsep, os.sep).replace(f'{os.sep}{os.sep}', os.sep)
    else:
        return path.replace(os.altsep, os.sep).replace(f'{os.sep}{os.sep}', os.sep)


def replace_sep(path):
    return path.replace(os.sep, os.altsep)


def del_last_not_digit(str):
    res = ''
    flag = False
    for ch in reversed(str):
        if flag or ch.isdigit():
            res += ch
            flag = True

    return res[::-1]


def str_to_bool(s):
    if s in ['True', 'true']:
        return True
    elif s in ['False', 'false']:
        return False
    else:
        raise ValueError(f'{s} is not a good boolean string')


def bool_to_jsBool(value):
    if value is True:
        return "true"
    return "false"


class StackElementNotExist(Exception):
    def __init__(self, *args, **kwargs):  # real signature unknown
        if kwargs.get('message'):
            super().__init__(kwargs.get('message'))
        else:
            super().__init__('Соответствие не найдено.')


class MultipleStackElement(Exception):
    def __init__(self, *args, **kwargs):  # real signature unknown
        super().__init__('Неоднозначный выбор.')


def cleanProgresses(id_progresses=None, exclude_processes=None):
    from isc_common.models.deleted_progresses import Deleted_progresses
    from isc_common.models.progresses import Progresses

    key = 'cleanProgresses'
    if settings.LOCKS.locked(key):
        return

    settings.LOCKS.acquire(key)
    try:
        if isinstance(id_progresses, str):
            _id_progresses = []
            _id_progresses.append(id_progresses)
            id_progresses = _id_progresses

        if isinstance(exclude_processes, str):
            _exclude_processes = []
            _exclude_processes.append(exclude_processes)
            exclude_processes = _exclude_processes

        if isinstance(id_progresses, list):
            for process in Progresses.objects.filter():
                for p in id_progresses:
                    if str(process.id_progress).find(p) != -1:
                        if isinstance(exclude_processes, list):
                            exc = False
                            for ep in exclude_processes:
                                if str(process.id_progress).find(ep) != -1:
                                    exc = True
                                    break
                            if not exc:
                                Progresses.objects.filter(id=process.id).delete()
                        else:
                            Progresses.objects.filter(id=process.id).delete()

            for process in Deleted_progresses.objects.filter():
                for p in id_progresses:
                    if str(process.id_progress).find(p) != -1:
                        if isinstance(exclude_processes, list):
                            exc = False
                            for ep in exclude_processes:
                                if str(process.id_progress).find(ep) != -1:
                                    exc = True
                                    break
                            if not exc:
                                Deleted_progresses.objects.filter(id=process.id).delete()
                        else:
                            Deleted_progresses.objects.filter(id=process.id).delete()
        else:
            if isinstance(exclude_processes, list):
                for process in Progresses.objects.filter():
                    if isinstance(exclude_processes, list):
                        exc = False
                        for ep in exclude_processes:
                            if str(process.id_progress).find(ep) != -1:
                                exc = True
                                break
                        if not exc:
                            Progresses.objects.filter(id=process.id).delete()
                    else:
                        Progresses.objects.filter(id=process.id).delete()

                for process in Deleted_progresses.objects.filter():
                    if isinstance(exclude_processes, list):
                        exc = False
                        for ep in exclude_processes:
                            if str(process.id_progress).find(ep) != -1:
                                exc = True
                                break
                        if not exc:
                            Deleted_progresses.objects.filter(id=process.id).delete()
                    else:
                        Deleted_progresses.objects.filter(id=process.id).delete()
            else:
                Progresses.objects.filter().delete()
                Deleted_progresses.objects.filter().delete()
        settings.LOCKS.release(key)
    except:
        settings.LOCKS.release(key)


class NotImplement(Exception):
    def __init__(self, text=''):
        super().__init__(f'{text} Нет реализации !!!!!!')


class Stack:
    stack = []

    def __iter__(self):
        return self.stack.__iter__()

    def __init__(self, stack=[]):
        self.stack = stack.copy()

    def top(self, index=1):
        if len(self.stack) < index:
            return None
        return self.stack[len(self.stack) - index]

    def clear(self):
        self.stack = []

    def extend(self, arr):
        self.stack.extend(arr)

    def pop(self):
        if len(self.stack) < 1:
            return None
        return self.stack.pop()

    def reverse(self):
        return Stack(stack=list(reversed(self.stack)))

    def distinct(self):
        return list(set(self.stack))

    def extend(self, lst):
        if isinstance(lst, list):
            for itm in lst:
                self.push(itm)

    def push(self, item, exists_function=None, logger=None):
        if callable(exists_function):
            if exists_function(item, self.stack) == False:
                self.stack.append(item)
                if isinstance(logger, Logger):
                    logger.debug(f'self.stack.append: {item}')
                return True
            else:
                if isinstance(logger, Logger):
                    logger.debug(f'self.stack.not append: {item}')
                return False
        else:
            self.stack.append(item)
            if isinstance(logger, Logger):
                logger.debug(f'self.stack.append: {item}')
            return True

        if isinstance(logger, Logger):
            logger.debug(f'size stack: {len(self.stack)}')
        return True

    def size(self):
        return len(self.stack)

    def copy(self):
        return Stack(self.stack)

    def find(self, function):
        return [item for item in self.stack if function(item)].copy()

    def exists(self, function):
        return len(self.find(function=function)) > 0

    def print_all(self):
        if self.size() > 0:
            logger1.warning('====================================dump===========================================================================')
            for item in self.stack:
                logger1.warning(item)
            logger1.warning('====================================end dump=======================================================================')

    def find_one(self, function):
        res = self.find(function=function).copy()
        if len(res) == 0:
            # self.print_all()
            raise StackElementNotExist()
        elif len(res) > 1:
            raise MultipleStackElement()

        return res[0]

    def __str__(self):
        return "[" + ",".join([str(item) for item in self.stack]) + "]"


class StackLocs(Stack):
    def acquire(self, id):
        try:
            id, lock = self.find_one(lambda x: x[0] == id)
        except StackElementNotExist:
            lock = Lock()
            self.push((id, lock))
        lock.acquire()
        logger1.debug(f'lock.acquire() ID: {id}')

    def locked(self, id):
        try:
            id, lock = self.find_one(lambda x: x[0] == id)
            return lock.locked()
        except StackElementNotExist:
            return False

    def release(self, id):
        try:
            id, lock = self.find_one(lambda x: x[0] == id)
            if lock.locked():
                lock.release()
                logger1.debug(f'lock.release() ID: {id}')
        except StackElementNotExist:
            pass


class StackWithId(Stack):
    def __init__(self, id='id', raise_on_dublicate=True):
        self.id = id
        self.raise_on_dublicate = raise_on_dublicate
        super().__init__()

    def push(self, item, logger=None):
        if item is None:
            return

        if not isinstance(item, dict):
            raise Exception(f'{item} must be dict')

        if not self.exists(item.get(self.id)):
            self.stack.append(item)
            if isinstance(logger, Logger):
                logger.debug(f'self.stack.append: {item}')
                logger.debug(f'self.stack.size: {self.size()}')

            if isinstance(logger, Logger):
                logger.debug(f'size stack: {len(self.stack)}')

            return True
        else:
            if self.raise_on_dublicate is True:
                raise Exception(f'{item} will be doublicate')
            else:
                if isinstance(logger, Logger):
                    logger.warning(f'{item} will be doublicate')

    def exists(self, id):
        return len(self.find(id)) > 0

    def find(self, id):
        if not isinstance(id, int):
            raise Exception(f'{id} must be int')
        return list(filter(lambda x: x.get(self.id) == id, self.stack))

    def find_one(self, id):
        if not isinstance(id, int):
            raise Exception(f'{id} must be int')

        res = self.find(id=id).copy()
        if len(res) == 0:
            raise StackElementNotExist()
        elif len(res) > 1:
            raise MultipleStackElement()

        return res[0]


def get_list_nums_key_dict(data):
    res = []
    if isinstance(data, dict):
        if data.get('0'):
            idx = 0
            while True:
                _data = data.get(str(idx))
                if isinstance(_data, dict):
                    res.append(_data)
                else:
                    break
                idx += 1
        else:
            res.append(data)
    return res


class Wrapper:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

    @property
    def dict(self):
        return self.__dict__

    def __str__(self):
        return str(self.dict)


user_name_anonim = "anonim"


def delNonePropFromDict(in_dict):
    if not isinstance(in_dict, dict):
        raise Exception(f'{in_dict} must be dict')

    res = dict()
    for k, v in in_dict.items():
        if v is not None:
            setAttr(res, k, v)
    return res


def delZeroPropFromDict(in_dict):
    if not isinstance(in_dict, dict):
        raise Exception(f'{in_dict} must be dict')

    res = dict()
    for k, v in in_dict.items():
        if v != 0:
            setAttr(res, k, v)
    return res
