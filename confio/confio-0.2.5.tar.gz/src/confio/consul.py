from typing import Union, List, Tuple, Optional, Dict, Any

from .base import ConfItem, IConf, logger
from .parser import ValueParser


class ConfConsul(IConf):
    def __init__(self, host='127.0.0.1', port=8900, schema='http', verify=True, cert=None,
                 separator='/',
                 parser: ValueParser = None, ):
        """

        :param host:
        :param port:
        :param schema:
        :param verify:
        :param cert:
        :param separator: Consul 中心使用的路径分隔符
        :param parser:
        """
        super(ConfConsul, self).__init__(parser)

        self.host = host
        self.port = port
        self.schema = schema
        self.verify = verify
        self.separator = separator
        import consul
        self.consul = consul.Consul(host=host, port=port, scheme=schema, verify=verify, cert=cert)
        self.cache = {}

    def load(self, **kwargs) -> List[Union[str, bytes]]:
        pass

    def get(self, id_: str, default=None, value_only=True) -> Union[ConfItem, Any]:
        """

        :param id_:
        :param default:
        :param value_only:
        :return:
        """
        index, value = self.consul.kv.get(id_)

        if value is None:
            logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
            return default
        item = self.parse_item(value)
        return item.value if value_only else item

    def match(self, prefix: str, value_only=True, fullkey=False) -> Dict[str, Union[ConfItem, Any]]:
        """

        :param prefix:
        :param value_only:
        :param fullkey:
        :return:
        """
        if prefix[-1] != self.separator:
            prefix = prefix + self.separator
        prefix_len = len(prefix)

        index, value = self.consul.kv.get(prefix, recurse=True)

        items = {}
        if value is None:
            return items

        for item in value:
            item = self.parse_item(item)
            items[item.id if fullkey else item.id[prefix_len:]] = item.value if value_only else item
        return items

    def set(self, id_: str, value: Optional[Union[str, bytes]], update_sys_value=False, allow_add=False):
        index, exists_value = self.consul.kv.get(id_)
        if exists_value is None:
            if not allow_add:
                logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
                return
        elif self.parse_item(exists_value) == value:
            return

        self.consul.kv.put(id_, value)

    def batch_set(self, items: Union[Dict[str, Optional[Union[str, bytes]]], List[ConfItem]], prefix: str = None, update_sys_value=False,
                  allow_add=False):
        if prefix:
            if prefix[-1] != self.separator:
                prefix = prefix + self.separator
        else:
            prefix = ''

        if isinstance(items, list):
            items = {
                item.id: item
                for item in items
            }

        all_items = self.load()
        data_map = {}

        for item in all_items:
            data_map[item.id] = item

        for key in items:
            id_ = prefix + key
            item = items[key]
            if id_ in data_map:
                self._set_item(id_, item, update_sys_value)
                continue
            if not allow_add:
                logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
                continue
            self._add_item(id_, item, update_sys_value)

    def remove(self, id_: Union[str, List[str], Tuple[str]]) -> Optional[Union[ConfItem, List[ConfItem]]]:
        is_list = isinstance(id_, (list, tuple))
        if is_list:
            id_list = id_
        else:
            id_list = (id_,)

        all_items = self.load()
        data_map = {}

        for item in all_items:
            data_map[item.id] = item

        remove_list = []

        for id_ in id_list:
            if id_ not in data_map:
                logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
                continue
            self._execute(self.SQL['remove_item'].format(table_name=self.table_name), id_)
            remove_list.append(data_map[id_])

        if is_list:
            return remove_list
        return None if len(remove_list) == 0 else remove_list[0]

    def parse_item(self, consul_value: dict):
        value = consul_value['Value']
        item = ConfItem(self.parser)
        item.id = consul_value['Key']
        if not isinstance(value, bytes):
            item.raw_sys_value = value
        else:
            try:
                item.raw_sys_value = value.decode()
            except:
                item.raw_sys_value = value

        return item
