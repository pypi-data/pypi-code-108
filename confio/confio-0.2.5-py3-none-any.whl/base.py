import json
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, Dict, List, Union, Tuple, Optional

from .__meta__ import name
from .parser import ConfTypes, ValueParser

logger = getLogger('confio')


class ConfItem:
    """
    配置项结构定义
    """

    def __init__(self, parser: ValueParser = None):
        self.id = None
        self.name = None
        self.raw_sys_value = None
        self.raw_user_value = None
        self.desc = None
        self.enabled = True
        self.type = ConfTypes.NONE
        self.parser = parser or ValueParser()

    def update(self, value, update_sys_value=False):
        """
        更新值
        :param value: 新的值
        :param update_sys_value: 为 True 时表示更新系统值，为 False 表示更新用户值
        :return:
        """
        if update_sys_value:
            self.raw_sys_value = value
        else:
            self.raw_user_value = value

    def __str__(self):
        return '<ConfItem %s:%s=%s -%s>' % (self.id, self.type.name, self.value, self.name)

    def _parse_value(self, raw_value):
        """
        将原始值解析出来
        :param raw_value:
        :return:
        """
        if raw_value is None:
            return None

        if self.type == ConfTypes.NONE:
            return raw_value

        return getattr(self.parser, 'parse_%s' % self.type.value)(raw_value)

    @property
    def sys_value(self):
        """
        系统值
        :return:
        """
        return self._parse_value(self.raw_sys_value)

    @property
    def user_value(self):
        """
        用户值
        :return:
        """
        return self._parse_value(self.raw_user_value)

    @property
    def raw_value(self):
        return self.raw_sys_value if self.raw_user_value is None else self.raw_user_value

    @property
    def value(self):
        """
        获取用户值或者系统值（用户值未指定：为 None 时，返回系统值）
        :return:
        """
        if self.raw_user_value is None:
            return self.sys_value
        return self.user_value

    class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            if not isinstance(o, ConfItem):
                return json.JSONEncoder().default(o)

            result = {
                'name': o.name,
                'key': o.id.split('.')[-1]
            }

            if o.type == ConfTypes.NONE:
                result['value'] = o.raw_sys_value
            else:
                result['value:%s' % o.type.value] = o.raw_sys_value

            if o.raw_user_value is not None:
                result['user_value'] = o.raw_user_value

            if o.desc:
                result['desc'] = o.desc

            # 仅在 false 时才写此值输出
            # 默认值即为 True
            if o.enabled is False:
                result['enabled'] = o.enabled

            return result

    @classmethod
    def decode(cls, json_data: dict, filename: str, parser: ValueParser = None):
        """
        从 JSON 解析数据，生成 ConfItem 对象
        :param json_data:
        :param filename:
        :param parser:
        :return:
        """
        if not isinstance(json_data, dict):
            return None

        key = cls._get_value(json_data, 'key')

        if not key or not isinstance(key, str) or '.' in key:
            raise Exception('Invalid config key in file "%s": %s' % (filename, key))

        if not key.islower():
            logger.debug('Conf key should be lowercase: %s' % key)
            key = key.lower()

        item = ConfItem(parser)
        item.id = key
        item.raw_user_value = cls._get_value(json_data, 'user_value')
        item.name = cls._get_value(json_data, 'name')
        item.desc = cls._get_value(json_data, 'desc')
        item.enabled = cls._get_value(json_data, 'enabled', True)

        value, item_type = cls._get_value_and_type(json_data)

        item.raw_sys_value = value
        item.type = item_type

        return item

    @classmethod
    def _get_value(cls, source: dict, field: str, default=None):
        return source[field] if field in source else default

    @classmethod
    def _get_value_and_type(cls, json_data: dict):
        value = None
        type_name = None
        for field in json_data:
            temp = field.split(':')
            if len(temp) == 1:
                continue
            type_name = temp[1]
            value = json_data[field]
            break

        if type_name is None:
            return cls._get_value(json_data, 'value'), ConfTypes.NONE

        try:
            item_type = ConfTypes(type_name)
        except Exception:
            logger.error('Cannot cast value %r into type "ConfTypes"' % type_name)
            item_type = ConfTypes.NONE

        return value, item_type


class IConf(ABC):
    STACK_INFO = False
    """
    在找不到配置项时，是否显示堆栈信息
    """

    VERSION_KEY = '%s.options.version' % name
    """
    版本号标识项名称
    """

    def __init__(self, parser: ValueParser = None):
        self.parser = parser

    def exists(self, id_: str) -> bool:
        """
        检查指定的配置项是否存在
        """
        return self.get(id_, value_only=False) is not None

    @abstractmethod
    def load(self, **kwargs) -> List[ConfItem]:
        """
        加载所有配置项（列表）
        """
        pass

    @abstractmethod
    def get(self, id_: str, default=None, value_only=True) -> Union[ConfItem, Any]:
        """
        获取指定的配置项的值，当配置项不存在时，使用指定的默认值
        """
        pass

    @abstractmethod
    def match(self, prefix: str, value_only=True, fullkey=False) -> Dict[str, Union[ConfItem, Any]]:
        """
        匹配指定前缀的项，返回的每个配置
        """
        pass

    @abstractmethod
    def set(self, id_: str, value, update_sys_value=False, allow_add=False):
        """
        设置指定配置项的值
        :param id_: 需要更新/添加项的键名称
        :param value: 需要更新/添加项的值
        :param update_sys_value: 为 True 时表示更新系统值，为 False 表示更新用户值
        :param allow_add: 在配置项不存在时，是否允许添加
        :return:
        """
        pass

    @abstractmethod
    def batch_set(self, items: Union[Dict[str, Any], List[ConfItem]], prefix: str = None, update_sys_value=False,
                  allow_add=False):
        """
        批量设置配置项
        :param items: 要更新的配置项集合
        :param prefix: 前缀，会被添加到 items 的 key 的前面，不需要填写 `.` 符号
        :param update_sys_value: 是否更新 sys_value ，默认更新 user_value
        :param allow_add: 在配置项不存在时，是否允许添加
        :return:
        """
        pass

    @abstractmethod
    def remove(self, id_: Union[str, List[str], Tuple[str]]) -> Optional[Union[ConfItem, List[ConfItem]]]:
        """
        根据配置项的ID移除一个或多个
        :param id_:
        :return:
        """
        pass

    def version(self, update=False):
        old = self.get(self.VERSION_KEY, value_only=False)
        if old is None:
            old = ConfItem()
            old.name = 'Confio options version identifier'
            old.raw_sys_value = 0
            self.set(self.VERSION_KEY, old, allow_add=True)

        if update:
            old.raw_sys_value = old.raw_sys_value + 1
            self.set(self.VERSION_KEY, old.raw_sys_value, update_sys_value=True)

        return old.value

    def export(self, filename: str, title: str = None):
        """
        导出为 markdown 格式文件
        :param title:
        :param filename:
        :return:
        """
        items = self.load()
        items.sort(key=lambda item: item.id)

        from .__meta__ import website, name

        headings = []

        with open(filename, mode='w', encoding='utf8') as fp:
            fp.write('# %s\n\n此文档由 [%s](%s) 生成\n' % (
                title or '配置项说明',
                name,
                website
            ))
            for item in items:
                if item.id == self.VERSION_KEY:
                    continue
                temp = item.id.split('.')
                heading = temp[0]
                if heading not in headings:
                    headings.append(heading)
                    fp.write('\n## %s\n\n' % heading)
                fp.write('- `{id}` {name}\n\t> 描述: {desc}\n'.format(
                    id=item.id,
                    name=item.name or '_未命名_',
                    desc=item.desc or '_无_')
                )
