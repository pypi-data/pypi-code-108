import json
from typing import Any, Dict, List, Union, Tuple, Optional

from .base import ConfItem, IConf, ConfTypes, logger
from .parser import ValueParser


class ConfDB(IConf):
    """
    基于数据加的配置存储
    """
    SQL = {
        # 查询表是否存在
        'table_exists': """SELECT * FROM `information_schema`.`TABLES`
            WHERE `TABLE_SCHEMA`='{db_name}' AND `TABLE_NAME`='{table_name}' LIMIT 1""",
        # 创建表结构
        'create_table': """CREATE TABLE `{table_name}` (
        `id` VARCHAR(128) PRIMARY KEY NOT NULL,
        `name` VARCHAR(64),
        `type` VARCHAR(32) DEFAULT '',
        `value` TEXT,
        `user_value` TEXT,
        `value_type` VARCHAR(32),
        `enabled` BIT DEFAULT 1,
        `desc` VARCHAR(256)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8""",
        # 加载所有数据
        'load_all': 'SELECT * FROM `{table_name}`',
        # 通过 id 查询一项数据
        'get_by_id': 'SELECT * FROM `{table_name}` WHERE `id`=%s',
        # 加载匹配指定前缀的数据
        'match_items': 'SELECT * FROM `{table_name}` WHERE `id` LIKE %s',
        # 更新数据值
        'update_value_by_id': 'UPDATE `{table_name}` SET `{value_field}`=%s, `value_type`=%s WHERE `id`=%s',
        # 更新所有字段
        'update_by_id': 'UPDATE `{table_name}` SET '
                        '`name`=%s,'
                        '`value`=%s,'
                        '`user_value`=%s,'
                        '`value_type`=%s,'
                        '`type`=%s,'
                        '`desc`=%s,'
                        '`enabled`=%s'
                        ' WHERE `id`=%s',
        # 添加项
        'add_item': 'INSERT INTO `{table_name}`'
                    '(`id`,`name`,`value`,`user_value`,`value_type`,`type`,`desc`,`enabled`)'
                    'VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
        # 移除项
        'remove_item': 'DELETE FROM `{table_name}` WHERE `id`=%s',
        # 清空数据
        'clear_table': 'TRUNCATE TABLE `{table_name}`'
    }

    def __init__(self,
                 database: str,
                 host='127.0.0.1',
                 port=3306,
                 user='root',
                 password='',
                 creator=None,
                 parser: ValueParser = None,
                 table_name='conf_items'):

        self.table_name = table_name
        self.con_option = {
            'database': database,
            'host': host,
            'port': port,
            'user': user,
            'password': password
        }
        logger.debug(
            'Initialize database configuration with table "{table_name}" via URI '
            'mysql://{host}:{port}/{database}'.format(
                table_name=table_name,
                **self.con_option
            )
        )
        self._tested = False
        super(ConfDB, self).__init__(parser)

    def _execute(self, sql: str, *args):
        if not self._tested:
            self._tested = True
            if not self._table_exists():
                self._create_table()

        import pymysql
        conn = pymysql.connect(**self.con_option)
        # try:
        #     print('[ConfDB] ' + (sql % args if args else sql))
        # except:
        #     print('[ConfDB] ' + sql)

        cursor = None
        is_query = sql.startswith('SELECT')
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            rows = cursor.execute(sql, args)
            if is_query:
                data = cursor.fetchall()
            else:
                data = None
        except Exception as e:
            print(str(e))
            return 0, None
        else:
            if not is_query:
                conn.commit()
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

        return rows, data

    def _table_exists(self) -> bool:
        rows, _ = self._execute(self.SQL['table_exists'].format(
            db_name=self.con_option['database'],
            table_name=self.table_name
        ))
        return rows > 0

    def _create_table(self):
        self._execute(self.SQL['create_table'].format(table_name=self.table_name))

    def load(self) -> List[ConfItem]:
        rows, data = self._execute(self.SQL['load_all'].format(table_name=self.table_name))
        return [
            self.row2item(data_item)
            for data_item in data
        ]

    def get(self, id_: str, default=None, value_only=True) -> Union[ConfItem, Any]:
        rows, data = self._execute(self.SQL['get_by_id'].format(table_name=self.table_name), id_)

        if rows:
            item = self.row2item(data[0])
            return item.value if value_only else item
        if id_ != self.VERSION_KEY:
            logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
        return default

    def match(self, prefix: str, value_only=True, fullkey=False) -> Dict[str, Union[ConfItem, Any]]:
        if prefix[-1] != '.':
            prefix = prefix + '.'
        prefix_len = len(prefix)

        rows, data = self._execute(self.SQL['match_items'].format(table_name=self.table_name), prefix + '%')

        items = {}
        for data_item in data:
            item = self.row2item(data_item)
            items[item.id if fullkey else item.id[prefix_len:]] = item.value if value_only else item

        return items

    def set(self, id_: str, value, update_sys_value=False, allow_add=False):
        rows, _ = self._execute(self.SQL['get_by_id'].format(table_name=self.table_name), id_)
        if not rows:
            if not allow_add:
                logger.warning('Conf item "%s" not found' % id_, stack_info=self.STACK_INFO)
                return
            self._add_item(id_, value, update_sys_value)
            return

        self._set_item(id_, value, update_sys_value)

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

    def clear(self):
        """
        清空配置表
        :return:
        """
        self._execute(self.SQL['clear_table'].format(table_name=self.table_name))

    def row2item(self, model: dict) -> ConfItem:
        value_type = model['value_type']
        id_ = model['id']

        item = ConfItem(self.parser)
        item.id = id_
        item.name = model['name']
        item.raw_sys_value = self._load_value(id_, value_type, model['value'])
        item.raw_user_value = self._load_value(id_, value_type, model['user_value'])
        item.type = ConfTypes(model['type'])
        item.desc = model['desc']
        item.enabled = model['enabled'] == b'\x01'

        return item

    def _set_item(self, id_, value, update_sys_value: bool):
        if isinstance(value, ConfItem):
            sys_value = value.raw_sys_value
            user_value = value.raw_user_value
            # 仅使用系统值的类型
            value_type = None if sys_value is None else type(sys_value).__name__
            sys_value = self._dump_value(sys_value)
            user_value = self._dump_value(user_value)
            self._execute(self.SQL['update_by_id'].format(table_name=self.table_name),
                          value.name, sys_value, user_value, value_type,
                          value.type.value, value.desc, value.enabled, id_)
        else:
            value_type = None if value is None else type(value).__name__
            value = self._dump_value(value)

            value_field = 'value' if update_sys_value else 'user_value'
            self._execute(self.SQL['update_value_by_id'].format(
                table_name=self.table_name, value_field=value_field
            ), value, value_type, id_)

    def _add_item(self, id_, value, update_sys_value):
        if isinstance(value, ConfItem):
            sys_value = value.raw_sys_value
            user_value = value.raw_user_value
            # 仅使用系统值的类型
            item = value
            item.value_type = None if sys_value is None else type(sys_value).__name__
            item.raw_sys_value = self._dump_value(sys_value)
            item.raw_user_value = self._dump_value(user_value)
        else:
            item = ConfItem()
            item.value_type = None if value is None else type(value).__name__
            item.update(value, update_sys_value)

        item.id = id_

        self._execute(self.SQL['add_item'].format(table_name=self.table_name),
                      item.id, item.name, item.raw_sys_value, item.raw_user_value, item.value_type,
                      item.type.value, item.desc, item.enabled)

    @classmethod
    def _load_value(cls, id_, value_type, value):
        if value_type is None or value_type == 'NoneType':
            return value

        if value is None:
            return value

        if value_type == 'int':
            return int(value)

        if value_type == 'bool':
            return value.lower() == 'true'

        if value_type == 'float':
            return float(value)

        if value_type in (dict, list):
            return json.loads(value)

        if value_type == 'str':
            return value

        if value_type in ('list', 'dict', 'tuple'):
            if value is None:
                return value

            return json.loads(value)

        logger.error('Cannot resolve value type "%s" of "%s"' % (value_type, id_))
        return value

    @classmethod
    def _dump_value(cls, value):
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        elif isinstance(value, (dict, list, tuple)):
            value = None if value is None else json.dumps(value, ensure_ascii=False)

        return value
