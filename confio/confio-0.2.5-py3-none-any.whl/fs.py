import json
import os
from typing import Any, Dict, List, Union, Tuple, Optional

from .base import ConfItem, IConf, logger
from .parser import ValueParser


class ConfFS(IConf):
    """
    基于文件系统的配置存储
    此模块基于文件进行缓存，缓存的文件绝对路径

    此模块会自动根据配置文件的修改时间来判断是否需要更新缓存

    _cached_items 存储了文件的最后修改时间以及文件内的配置项
    """

    def __init__(self, conf_root: str, ignore_file_fn=None, parser: ValueParser = None):
        """

        :param conf_root:
        :param ignore_file_fn: 扫描配置文件时，用于判断是否需要忽略指定的配置文件。当返回 True 要忽略
        :param parser:
        """
        self.conf_root = os.path.abspath(conf_root)
        self.ignore_file_fn = ignore_file_fn
        self._cached_items = {}
        logger.debug('Initialize filesystem configuration with path ' + self.conf_root)
        super(ConfFS, self).__init__(parser)

    def load(self, filename: str = None) -> List[ConfItem]:
        """

        :param filename:
        :return:
        """
        if filename is not None:
            # 文件如果不存在，返回空集合
            if not os.path.isfile(filename):
                return []

            # 获取此文件的最后修改时间
            mtime = os.path.getmtime(filename)
            # 从缓存查询此文件的配置项
            if filename in self._cached_items:
                [last_mtime, items] = self._cached_items[filename]
                if last_mtime == mtime:
                    return items
            # 最后修改时间不一致，那么更新
            items = self._load_conf_file(filename)
            self._cached_items[filename] = [mtime, items]
            return items

        items = []
        for filename in self._get_conf_files():
            items += self._load_conf_file(filename)

        return items

    def get(self, id_: str, default=None, value_only=True) -> Union[ConfItem, Any]:
        id_ = id_.lower()
        conf_prefix, conf_file = self._resolve_conf_file(id_)
        if conf_file is None:
            return default

        items = self.load(conf_file)

        for item in items:
            if item.id != id_:
                continue
            return item.value if value_only else item

        if id_ != self.VERSION_KEY:
            logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
        return default

    def match(self, prefix: str, value_only=True, fullkey=False) -> Dict[str, Union[ConfItem, Any]]:
        prefix = prefix.lower()
        if prefix[-1] != '.':
            prefix = prefix + '.'
        prefix_len = len(prefix)

        matched_files = self._resolve_matched_files(prefix)

        items = {}
        for filename in matched_files:
            for item in self.load(filename):
                if not item.id.startswith(prefix):
                    continue
                items[item.id if fullkey else item.id[prefix_len:]] = item.value if value_only else item
        return items

    def set(self, id_: str, value, update_sys_value=False, allow_add=False):
        id_ = id_.lower()
        conf_prefix, conf_file = self._resolve_conf_file(id_, True)

        found = False
        items = self.load(conf_file)
        for item in items:
            if item.id != id_:
                continue

            self._update_item(item, value, update_sys_value)
            found = True
            break

        if not found:
            if not allow_add:
                logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
                return
            item = self._add_item(id_, value, update_sys_value)
            items.append(item)

        # 将改动写入文件
        with open(conf_file, mode='w', encoding='utf8') as fp:
            json.dump(items, fp, indent=2, ensure_ascii=False, cls=ConfItem.JSONEncoder)

        if id_ != self.VERSION_KEY:
            self.version(True)

    def batch_set(self, items: Union[Dict[str, Any], List[ConfItem]], prefix: str = None, update_sys_value=False,
                  allow_add=False):
        if prefix:
            if prefix[-1] != '.':
                prefix = prefix + '.'
        else:
            prefix = ''

        if isinstance(items, list):
            items = {
                item.id: item
                for item in items
            }

        all_items = self.load()
        data_map = {}
        file_buffer = {}
        for item in all_items:
            data_map[item.id] = item
            pkg = '.'.join(item.id.split('.')[0:-1]).lower()
            if pkg not in file_buffer:
                conf_prefix, conf_file = self._resolve_conf_file(item.id, True)
                file_buffer[pkg] = {
                    'file': conf_file,
                    'changed': False,
                    'items': []
                }
            file_buffer[pkg]['items'].append(item)

        for key in items:
            id_ = prefix + key
            if id_ == self.VERSION_KEY:
                # ignore this item
                continue
            pkg = '.'.join(id_.split('.')[0:-1]).lower()
            item = items[key]
            if id_ in data_map:
                self._update_item(data_map[id_], item, update_sys_value)
            else:
                if not allow_add:
                    logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
                    continue
                if pkg not in file_buffer:
                    _, conf_file = self._resolve_conf_file(id_, True)
                    file_buffer[pkg] = {
                        'file': conf_file,
                        'changed': True,
                        'items': []
                    }
                item = self._add_item(id_, item, update_sys_value)
                file_buffer[pkg]['items'].append(item)

            file_buffer[pkg]['changed'] = True

        self._persist_changes(file_buffer)

    def remove(self, id_: Union[str, List[str], Tuple[str]]) -> Optional[Union[ConfItem, List[ConfItem]]]:
        is_list = isinstance(id_, (list, tuple))
        if is_list:
            id_list = id_
        else:
            id_list = (id_,)

        all_items = self.load()
        data_map = {}
        file_buffer = {}
        for item in all_items:
            data_map[item.id] = item
            pkg = '.'.join(item.id.split('.')[0:-1]).lower()
            if pkg not in file_buffer:
                conf_prefix, conf_file = self._resolve_conf_file(item.id, True)
                file_buffer[pkg] = {
                    'file': conf_file,
                    'changed': False,
                    'items': []
                }
            file_buffer[pkg]['items'].append(item)

        remove_list = []

        for id_ in id_list:
            if id_ == self.VERSION_KEY:
                # ignore this item
                continue
            if id_ not in data_map:
                logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
                continue
            pkg = '.'.join(id_.split('.')[0:-1]).lower()
            item = data_map[id_]
            file_buffer[pkg]['items'].remove(item)
            file_buffer[pkg]['changed'] = True
            remove_list.append(item)

        self._persist_changes(file_buffer)

        if is_list:
            return remove_list
        return None if len(remove_list) == 0 else remove_list[0]

    def _persist_changes(self, file_buffer: dict):
        has_changed = False
        for item in file_buffer.values():
            if not item['changed']:
                continue
            has_changed = True
            # 将改动写入文件
            with open(item['file'], mode='w', encoding='utf8') as fp:
                json.dump(item['items'], fp, indent=2, ensure_ascii=False, cls=ConfItem.JSONEncoder)

        if has_changed:
            self.version(True)

    @classmethod
    def _update_item(cls, item: ConfItem, value, update_sys_value):
        if isinstance(value, ConfItem):
            item.name = value.name
            item.raw_sys_value = value.raw_sys_value
            item.raw_user_value = value.raw_user_value
            item.raw_user_value = value.raw_user_value
            item.type = value.type
            item.desc = value.desc
        else:
            item.update(value, update_sys_value)

    @classmethod
    def _add_item(cls, id_, value, update_sys_value):
        if isinstance(value, ConfItem):
            item = value
        else:
            item = ConfItem()
            item.update(value, update_sys_value)

        item.id = id_

        return item

    def _resolve_conf_file(self, id_: str, auto_create=False):
        # 1. 去掉配置名称里面的最后一项(即得到配置文件路径)
        conf_dir = id_.split('.')[:-1]
        conf_prefix = '.'.join(conf_dir)
        # 2. 得到配置文件名称
        filename = conf_dir.pop() + '.json'

        # 3. 附加上配置文件目录（如果有）
        if len(conf_dir) > 0:
            conf_dir = os.path.join(self.conf_root, os.path.sep.join(conf_dir))
        else:
            conf_dir = self.conf_root

        fullname = os.path.join(conf_dir, filename)

        if os.path.isfile(fullname):
            return conf_prefix, fullname

        if id_ == self.VERSION_KEY or auto_create:
            if not os.path.isdir(conf_dir):
                os.makedirs(conf_dir, exist_ok=True)
            return conf_prefix, fullname

        logger.error('Cannot resolve id "%s": file "%s" not found' % (id_, fullname))
        return conf_prefix, None

    def _resolve_matched_files(self, key_prefix: str):
        files = []

        # 1. 去掉配置名称里面的 . 符号，得到路径
        path_prefix = key_prefix.rstrip('.').replace('.', os.path.pathsep)

        # 此时有两种可能性（可能同时存在）
        # 1. 配置前缀匹配到文件
        # 2. 配置前缀匹配到目录

        filename = os.path.join(self.conf_root, path_prefix + '.json')
        if os.path.isfile(filename):
            files.append(filename)

        dirname = os.path.join(self.conf_root, path_prefix)
        if os.path.isdir(dirname):
            for f in self._get_conf_files(dirname):
                files.append(f)

        if not files:
            logger.error('Cannot resolve id prefix "%s": path not found' % key_prefix)

        return files

    def _load_conf_file(self, filename: str) -> List[ConfItem]:
        with open(filename, mode='r', encoding='utf8') as fp:
            try:
                json_content = json.load(fp)
            except Exception as ex:
                logger.warning('Failed to load file: ' + filename)
                raise ex

        pkg_prefix = os.path.splitext(os.path.relpath(filename, self.conf_root))[0].replace(os.path.sep, '.')

        items = []

        for json_item in json_content:
            item = ConfItem.decode(json_item, filename, self.parser)
            if not item:
                continue
            item.id = '%s.%s' % (pkg_prefix, item.id)
            items.append(item)

        return items

    def _get_conf_files(self, target_path: str = None):
        for current_dir, dirs, files in os.walk(target_path or self.conf_root):
            for filename in files:
                if filename.endswith('.json'):
                    if self.ignore_file_fn and self.ignore_file_fn(os.path.join(current_dir, filename)):
                        continue
                    yield os.path.join(current_dir, filename)
