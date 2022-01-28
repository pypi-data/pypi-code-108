import pymysql
from pymysql.cursors import Cursor

from easysql.setting import *

try:
    from printf import printf, color

    print_error = printf.Format(_type=color.TYPE.ERROR).print
    print_warning = printf.Format(_type=color.TYPE.WARNING).print
    print_data = printf.Format(_type=color.TYPE.DATA).print
    print_success = printf.Format(_type=color.TYPE.SUCCESS).print
    printf = print
except:
    print_error = print
    print_warning = print
    print_data = print
    print_success = print
    printf = print

attribute_find_sql = """SELECT column_name from information_schema.columns where table_schema='%s' and table_name='%s' order By ORDINAL_POSITION"""
table_find_sql = """select table_name from information_schema.tables where table_schema='%s'"""


class DatabaseSql:
    """
    数据库类
    """

    def __init__(self, _database_name, _user="root", _passwd="123456", _host="127.0.0.1"):
        self.database = _database_name
        self.user = _user
        self.passwd = _passwd
        self.host = _host

    @property
    def database(self):
        return self.__database

    @database.setter
    def database(self, value):
        self.__database = str(value)

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, value):
        self.__user = str(value)

    @property
    def passwd(self):
        return self.__passwd

    @passwd.setter
    def passwd(self, value):
        self.__passwd = str(value)

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, value):
        self.__host = str(value)

    def connect(self):
        database = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database)
        return database


class TableSql:
    """
    数据表类
    """

    def __init__(self, _table_name, _engine="InnoDB", _charset="utf8mb4"):
        self.table = _table_name
        self.engine = _engine
        self.charset = _charset
        self.index_i = 0
        self.attribute_info_list = list()
        self.primary_keys = list()

    @property
    def table(self):
        return self.__table

    @table.setter
    def table(self, value):
        self.__table = str(value)

    @property
    def engine(self):
        return self.__engine

    @engine.setter
    def engine(self, value):
        if value in database_table_engine:
            self.__engine = value
        else:
            print_warning("未找到对应的引擎，使用默认引擎。")
            self.__engine = "InnoDB"

    @property
    def charset(self):
        return self.__charset

    @charset.setter
    def charset(self, value):
        if value in database_table_charset:
            self.__charset = value
        else:
            print_warning("未找到对应字符集，使用默认字符集。")

    def reset(self, _tableSql_table):
        """
        将值替换为目标数据表（方便等于操作）
        """
        if isinstance(_tableSql_table, TableSql):
            self.table = _tableSql_table.table
            self.engine = _tableSql_table.engine
            self.charset = _tableSql_table.charset
            self.index_i = _tableSql_table.index_i
            self.attribute_info_list = _tableSql_table.attribute_info_list
            self.primary_keys = _tableSql_table.primary_keys
        else:
            print_error("%s无法替换为%s" % (self.table, _tableSql_table))

    def add_attribute(
            self,
            _attribute_name: str,
            _attribute_type: str,
            _attribute_long=None,
            default=None,
            is_not_null=False,
            is_primary_key=False,
            is_auto=False,
            is_unique=False,
            is_unsigned=False
    ):
        """
        添加字段
        :param _attribute_name: [str] 字段名
        :param _attribute_type: [str] 字段类型
        :param _attribute_long: [int] or [tuple, list] 字段长度
        :param default: 字段默认值
        :param is_not_null: 字段非空设置
        :param is_primary_key: 字段主键设置
        :param is_auto: 字段自增设置
        :param is_unique: 字段非空设置
        :param is_unsigned: 字段无符号设置
        :return: 无
        """
        if _attribute_type.upper() in char_list:
            if default is not None:
                default = '"%s"' % default
        if _attribute_type.upper() in type_unused_long:
            if _attribute_long is not None:
                print_warning("该字段不需要输入长度")
            _attribute_long = None
        elif _attribute_type.upper() in type_used_long_1:
            if _attribute_long is None:
                print_warning("该字段需要输入一位长度，目前默认值为255")
                _attribute_long = 255
            elif isinstance(_attribute_long, int):
                pass
            elif isinstance(_attribute_long, (tuple, list)):
                print_warning("该字段需要输入一位长度，目前默认值为255")
                _attribute_long = 255
            else:
                print_warning("该字段需要输入一位长度，目前默认值为255")
                _attribute_long = 255
        elif _attribute_type.upper() in type_used_long_2:
            if _attribute_long is None:
                print_warning("该字段需要输入二位长度，目前默认值为(5,2)")
                _attribute_long = (5, 2)
            elif isinstance(_attribute_long, int):
                print_warning("该字段需要输入二位长度，目前默认值为(%s,2)" % _attribute_long)
                _attribute_long = (_attribute_long, 2)
            elif isinstance(_attribute_long, (tuple, list)):
                if len(_attribute_long) == 2:
                    if isinstance(_attribute_long, (tuple[int, int], list[int, int])):
                        pass
                    else:
                        print_warning("该字段需要输入二位长度，目前默认值为(5,2)")
                        _attribute_long = (5, 2)
                else:
                    print_warning("该字段需要输入二位长度，目前默认值为(5,2)")
                    _attribute_long = (5, 2)
            else:
                print_warning("该字段需要输入二位长度，目前默认值为(5,2)")
                _attribute_long = (5, 2)
        else:
            _attribute_long = None
        self.attribute_info_list.append({
            "name": _attribute_name,
            "type": _attribute_type,
            "long": _attribute_long,
            "notnull": is_not_null,
            "primarykey": is_primary_key,
            "auto": is_auto,
            "unique": is_unique,
            "unsigned": is_unsigned,
            "default": default
        })
        if is_primary_key:
            self.primary_keys.append(_attribute_name)

    def create_language(self):
        """
        生成创建表语句
        :return: SQL语句（str）
        """
        _create_language = ""
        for attribute in self.attribute_info_list:
            if attribute["long"] is None:
                _create_language += "`%s` %s" % (attribute["name"], attribute["type"])
            elif isinstance(attribute["long"], int):
                _create_language += "`%s` %s(%s)" % (attribute["name"], attribute["type"], attribute["long"])
            else:
                _create_language += "`%s` %s(%s,%s)" % (
                    attribute["name"], attribute["type"], attribute["long"][0], attribute["long"][1])

            if attribute["type"].upper() in int_list:
                if attribute["unsigned"]:
                    _create_language += " UNSIGNED"
                if attribute["auto"]:
                    _create_language += " AUTO_INCREMENT"

            if attribute["notnull"] and not attribute["primarykey"]:
                _create_language += " NOT NULL"

            if attribute["unique"]:
                _create_language += " UNIQUE"

            if attribute["default"] is not None:
                _create_language += " DEFAULT %s" % attribute["default"]
            _create_language += ","
        if self.primary_keys:
            _create_language += "PRIMARY KEY("
            for primary_key in self.primary_keys:
                _create_language += "`%s`," % primary_key
        if _create_language != "":
            _create_language = _create_language[:-1] + ")"
            _create_language_temp = """CREATE TABLE %s (%s)ENGINE=%s DEFAULT CHARSET=%s""" % (
                self.table, _create_language, self.engine, self.charset)
        else:
            _create_language_temp = """CREATE TABLE %s ENGINE=%s DEFAULT CHARSET=%s""" % (
                self.table, self.engine, self.charset)
        return _create_language_temp

    def __str__(self):
        return self.create_language()

    def belong(self, tableSql_table):
        """
        判断数据表类型归属
        用于创建数据表时判断重复问题
        所有非主键的字段全属于另一个表
        :param tableSql_table:
        :return:
        """
        if isinstance(tableSql_table, TableSql):
            for attribute in self.attribute_info_list:
                if not attribute["primarykey"]:
                    if attribute not in tableSql_table.attribute_info_list:
                        return False
            return True
        else:
            return False

    def belong_list(self, *tableSql_list):
        for table in tableSql_list:
            if self.belong(table):
                return True
        return False

    def add_same_table_list(self, *tableSql_list):
        if self.belong_list(*tableSql_list):
            return tableSql_list
        else:
            for tableSql_temp_i in tableSql_list:
                if tableSql_temp_i.belong(self):
                    tableSql_temp_i.reset(self)
                    return tableSql_list
            tableSql_list += (self,)
            return tableSql_list


def add_table_list(tableSql_list_1: list or tuple, tableSql_list_2: list):
    """
    :param tableSql_list_1:
    :param tableSql_list_2: 添加之前确保该列表符合唯一
    :return:
    """
    for tableSQL_table in tableSql_list_1:
        tableSql_list_2 = tableSQL_table.add_same_table_list(*tableSql_list_2)
    return tableSql_list_2


class DataSql:
    """
    数据类
    """

    def __init__(self, _database_name, _table_name, _attribute=None, _results=None, find_info=None):
        self.database = _database_name
        self.table = _table_name
        self.attribute = _attribute
        self.value_list = _results
        self.data_list = _results
        self.find_info = find_info

    @property
    def attribute(self):
        return self.__attribute

    @attribute.setter
    def attribute(self, value):
        if value is None:
            self.__attribute = list()
        elif isinstance(value, Cursor):
            value.execute(attribute_find_sql % (self.database, self.table))
            results = value.fetchall()
            self.__attribute = list(map(lambda x: x[0], results))
        elif isinstance(value, (tuple, list)):
            self.__attribute = list(value)
        else:
            print_error("属性字段数据种类错误")

    def add_attribute(self, value):
        if value is None:
            pass
        elif isinstance(value, (tuple, list)):
            self.__attribute.extend(list(value))
        elif isinstance(value, str):
            self.__attribute.append(value)
        else:
            print_error("属性字段数据种类错误")

    @property
    def value_list(self):
        return self.__value_list

    @value_list.setter
    def value_list(self, value):
        if value is None:
            self.__value_list = list()
        elif isinstance(value, (tuple, list)):
            self.__value_list = list(value)
        else:
            print_error("属性字段数据种类错误")

    @property
    def data_list(self):
        return self.__data_list

    @data_list.setter
    def data_list(self, value):
        if self.attribute:
            if value is None:
                self.__data_list = list()
            elif isinstance(value, (tuple, list)):
                self.__data_list = list(
                    map(lambda x: {self.attribute[i]: x[i] for i in range(len(self.attribute))}, value)
                )
            else:
                print_error("属性字段数据种类错误")
        else:
            self.__data_list = list()

    def __str__(self):
        return str(self.data_list) if self.data_list else "没有数据"

    def show(self):
        """
        展示数据
        :return:
        """
        if not self.data_list:
            print_warning("没有数据")
        else:
            for dataSQL_data in self.data_list:
                print_data(dataSQL_data)

    def add(self, data_from_dataSQL):
        """
        数据集加，只支持相同字段的数据集
        :param data_from_dataSQL:
        :return:
        """
        if self.attribute == data_from_dataSQL.attribute:
            self.data_list += data_from_dataSQL.data_list
            self.find_info += " OR" + data_from_dataSQL.find_info[6:]
            self.value_list += data_from_dataSQL.value_list

    def get(self, *args):
        """
        获取对应字段的数据集
        :param args:
        :return:
        """
        if not args:
            return self.value_list
        elif len(args) == 1:
            get_data_list = list()
            for dataSQL_data in self.data_list:
                get_data_list.append(dataSQL_data.get(args[0], None))
            return get_data_list
        else:
            get_data_list = list()
            for dataSQL_data in self.data_list:
                get_data = list()
                for arg in args:
                    get_data.append(dataSQL_data.get(arg, None))
                get_data_list.append(tuple(get_data))
            return get_data_list

    # 仅限于单一key唯一
    def get_dic(self, *args, data_dic=None, _model="LD", key=None) -> list or dict:
        """
        1.
        获取以data_dic为格式的字段集
        模式LD为列表[dict,dict]
        模式DL为字典{key1=[],key2=[]}
        默认为list-dict
        2.
        获取以key为dict.key的字段集
        :param args: 字段
        :param data_dic: 字典格式
        :param _model: 模式
        :param key: key
        :return:
        """
        if data_dic is not None:
            if _model == "DL":
                index = 0
                for key in data_dic:
                    data_dic[key] = self.get(args[index])
                    index += 1
                return data_dic
            else:
                if _model != "LD":
                    print_warning("未找到对应模式，使用默认模式list-dict")
                dataSql_data_dic_list = list()
                for dataSql_data in self.data_list:
                    index = 0
                    dataSql_data_dic = {}
                    for key in data_dic:
                        dataSql_data_dic[key] = dataSql_data.get(args[index])
                        index += 1
                    dataSql_data_dic_list.append(dataSql_data_dic)
                return dataSql_data_dic_list

        data_index = 0

        def unique_id():
            """
            获取唯一名
            :return:
            """
            nonlocal data_index
            data_index += 1
            return "noKey_%s" % data_index

        if key is None:
            if not args:
                return self.data_list
            else:
                get_data_list = list()
                for dataSql_data in self.data_list:
                    get_data = dict()
                    for arg in args:
                        get_data[arg] = dataSql_data.get(arg, None)
                    get_data_list.append(get_data)
                return get_data_list
        else:
            if not args:
                get_data_dic = dict()
                for dataSql_data in self.data_list:
                    get_data = dict()
                    for arg in self.attribute:
                        if arg != key:
                            get_data[arg] = dataSql_data.get(arg, None)
                    get_data_dic[dataSql_data.get(key, unique_id())] = get_data
                return get_data_dic
            elif len(args) == 1:
                get_data_dic = dict()
                for dataSql_data in self.data_list:
                    get_data_dic[dataSql_data.get(key, unique_id())] = dataSql_data.get(args[0], None)
                return get_data_dic
            else:
                get_data_dic = dict()
                for dataSql_data in self.data_list:
                    get_data = dict()
                    for arg in args:
                        get_data[arg] = dataSql_data.get(arg, None)
                    get_data_dic[dataSql_data.get(key, unique_id())] = get_data
                return get_data_dic

    def read_file(self, filename, _encoding=None, _sep=None):
        if self.is_empty():
            with open(filename, encoding=_encoding) as f:
                first_line = f.readline()
                self.attribute = first_line.split(_sep)
                results = list()
                for data_line in f.readlines():
                    results.append(data_line.split(_sep))
                self.value_list = results
                self.data_list = results
            f.close()
        else:
            print_error("该数据类非空，请使用空数据类读取")

    def is_empty(self):
        if self.attribute:
            return False
        else:
            return True


class EasySql:
    """
    主功能类，利用前面结构类进行简化
    """

    def __init__(
            self, database, _user="root", _passwd="123456", _host="127.0.0.1",
    ):
        """
        初始化连接数据库
        :param database:
        :param _user:
        :param _passwd:
        :param _host:
        """
        if isinstance(database, DatabaseSql):
            self.database = database.database
            self.user = database.user
            self.host = database.host
            self.passwd = database.passwd
        else:
            self.database = str(database)
            self.user = _user
            self.host = _host
            self.passwd = _passwd
        self.db = True
        self.sql_list = list()

    @property
    def cursor(self):
        return self.__cursor

    @property
    def db(self):
        return self.__db

    @db.setter
    def db(self, value):
        if value is None:
            self.__db = None
            self.__cursor = None
        elif isinstance(value, bool):
            if value:
                self.__db = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database)
                self.__cursor = self.__db.cursor()
            else:
                self.__db.close()
                self.__db = None
                self.__cursor = None
        else:
            print_error("<db>不能自行设置")

    def creat(self, *args, _table_name=None, _last_table_name=None, _child_deep=0, **kwargs):
        """
        根据字典创建数据表（可匹配JSON使用）只能创建简单表
        :param args: json列表
        :param _table_name:
        :param _last_table_name:
        :param _child_deep: _child_deep = x(>0) :进行x次分层; _child_deep = 0 :不进行分层; _child_deep = x(<0) :直到无法分层
        :param kwargs: json字典或自定义字典
        :return:
        表名：输入则为输入，不输入则：1. 字典仅为1层时取第一层的键为表名 2. 1失败则使用默认名
        方式：若为纯字典格式，则直到最后一次分层前都是前一层为表，后一层为值嵌套，若为列表格式，则列表内的值为数据
        主键为默认生成的自增id
        args和kwargs只能输入一项，均输入会优先使用args而不使用kwargs
        暂时不确定是否通用以及没有使用deep
        """
        __table_name = ""
        _child_deep = 0  # 暂未实现迭代
        if _table_name is None:
            __table_name = self.get_temp_table_name(_last_table_name)
        else:
            __table_name = str(_table_name)
        __table_name_id = "%s_id" % __table_name
        dataSql_data = DataSql(self.database, __table_name)
        dataSql_data.attribute = [__table_name_id]
        attribute_value_type_dict = dict()
        if args:
            """
            列表元素一定是数据集
            """
            _temp_index = 0
            for __dict_arg in args:
                if isinstance(__dict_arg, dict):
                    _temp_data_dict = dict()
                    for _key, _value in __dict_arg:
                        if _key not in dataSql_data.attribute and _value is not None:
                            dataSql_data.add_attribute(_key)
                            attribute_value_type_dict[_key] = get_mysql_type(_value)
                        if _child_deep == 0:
                            _temp_data_dict[_key] = _value
                        else:
                            if isinstance(_value, list):
                                """
                                使用args新构建一个表，并在之后该字段都使用该表储存，该字段储存对应主键，每次使用对应deep减1
                                """
                                _temp_data_dict[_key] = _value
                                pass
                            elif isinstance(_value, dict):
                                """
                                使用kwargs新构建一个表，并在之后该字段都使用该表储存，该字段储存对应主键，每次使用对应deep减1
                                """
                                _temp_data_dict[_key] = _value
                                pass
                            else:
                                _temp_data_dict[_key] = _value
                    dataSql_data.data_list.append(_temp_data_dict)
                    _temp_index += 1
                else:
                    print_warning("未能读取对应的数据格式，跳过该行")
        elif kwargs:
            """
            字典元素如果字段相似则仍为数据集，字典的键设为主键，如果不相似则为字段
            """
            _temp_index = 0
            for _key, _value in kwargs:
                _temp_data_dict = dict()
                if _key not in dataSql_data.attribute and _value is not None:
                    dataSql_data.add_attribute(_key)
                    attribute_value_type_dict[_key] = get_mysql_type(_value)
                if _child_deep == 0:
                    _temp_data_dict[_key] = _value
                else:
                    if isinstance(_value, list):
                        """
                        使用args新构建一个表，并在之后该字段都使用该表储存，该字段储存对应主键，每次使用对应deep减1
                        """
                        _temp_data_dict[_key] = _value
                        pass
                    elif isinstance(_value, dict):
                        """
                        使用kwargs新构建一个表，并在之后该字段都使用该表储存，该字段储存对应主键，每次使用对应deep减1
                        """
                        _temp_data_dict[_key] = _value
                        pass
                    else:
                        _temp_data_dict[_key] = _value
                dataSql_data.data_list.append(_temp_data_dict)
                _temp_index += 1
            pass
        else:
            print_error("没有可以使用的数据")
        # 创建数据表
        tableSql_table = TableSql(__table_name)
        tableSql_table.add_attribute(__table_name_id, "INT", is_primary_key=True)
        for _attribute_temp, _attribute_temp_type in attribute_value_type_dict:
            tableSql_table.add_attribute(_attribute_temp, _attribute_temp_type)
        _table_create_sql = tableSql_table.create_language()
        self.cursor.execute(_table_create_sql)
        self.db.commit()
        # 添加数据
        self.add(__table_name, data_from_dataSql=dataSql_data)

    def add(self, table_name, is_commit: bool = True, data_from_dataSql=None, **kwargs):
        _insert_language = """INSERT INTO %s""" % table_name
        if isinstance(data_from_dataSql, DataSql):
            for _data_temp_i in data_from_dataSql.data_list:
                _insert_language_temp_0 = """("""
                _insert_language_temp_1 = """) VALUE ("""
                for _key, _value in _data_temp_i:
                    _insert_language_temp_0 += """`%s`,""" % _key
                    if _value is None:
                        _insert_language_temp_1 += """NULL,"""
                    elif isinstance(_value, str):
                        _insert_language_temp_1 += """"%s",""" % _value.replace('"', "'")
                    else:
                        _insert_language_temp_1 += """%s,""" % _value
                self.sql_list.append(
                    """%s%s%s)""" % (_insert_language, _insert_language_temp_0[:-1], _insert_language_temp_1[:-1])
                )
        else:
            _insert_language_temp_0 = """("""
            _insert_language_temp_1 = """) VALUE ("""
            for attribute, value in kwargs:
                _insert_language_temp_0 += """`%s`,""" % attribute
                if value is None:
                    _insert_language_temp_1 += """NULL,"""
                elif isinstance(value, str):
                    _insert_language_temp_1 += """"%s",""" % value.replace('"', "'")
                else:
                    _insert_language_temp_1 += """%s,""" % kwargs[attribute]
            _insert_language_temp_0 = _insert_language_temp_0[:-1]
            _insert_language_temp_1 = _insert_language_temp_1[:-1] + """)"""
            self.sql_list.append(
                """%s%s%s)""" % (_insert_language, _insert_language_temp_0[:-1], _insert_language_temp_1[:-1])
            )
        if is_commit:
            self.commit()

    def add_list(self, table_name, **kwargs):
        """
        添加数据列
        :param table_name:
        :param kwargs:
        :return:
        """
        temp = 0
        for key in kwargs.keys():
            if not isinstance(kwargs[key], (tuple, list)):
                if kwargs[key] == "":
                    return
            else:
                if len(kwargs[key]) == 0:
                    return
                if isinstance(kwargs[key], tuple):
                    kwargs[key] = list(kwargs[key])
                if temp != 0:
                    if len(kwargs[key]) != temp:
                        return
                else:
                    temp = len(kwargs[key])
        tKwargs = {}
        for key in kwargs.keys():
            if not isinstance(kwargs[key], (tuple, list)):
                kwargs[key] = [kwargs[key]] * temp
        for i in range(0, temp):
            for key in kwargs.keys():
                tKwargs[key] = kwargs[key][i]
            self.add(table_name, is_commit=False, **tKwargs)
        self.commit()

    def delete(self, table_name, data_from_dataSql=None, **kwargs):
        """
        删除数据
        :param table_name:
        :param data_from_dataSql:
        :param kwargs:
        :return:
        """
        if isinstance(data_from_dataSql, DataSql):
            _delete_language = """DELETE FROM %s%s""" % (data_from_dataSql.table, data_from_dataSql.find_info)
            self.execute(_delete_language)
        else:
            findInfo = _find_info(**kwargs)
            _delete_language = """DELETE FROM %s%s""" % (table_name, findInfo)
            self.execute(_delete_language)

    def find(self, table_name, **kwargs):
        """
        查找数据
        :param table_name:
        :param kwargs:
        :return:
        """
        find_info = _find_info(**kwargs)
        _find_language = """SELECT * FROM %s%s""" % (table_name, find_info)
        return DataSql(self.database, table_name, self.cursor, self.get_data(_find_language), find_info=find_info)

    def update(self, data_from_dataSql: DataSql, **kwargs):
        """
        更新数据
        准备重写逻辑！！！！！
        """
        if not kwargs:
            return
        _update_language = """UPDATE %s SET """ % data_from_dataSql.table
        for key in kwargs.keys():
            if type(kwargs[key]) == str:
                kwargs[key] = kwargs[key].replace('"', "'")
                _update_language += '`%s`="%s",' % (key, kwargs[key])
            else:
                _update_language += "`%s`=%s," % (key, kwargs[key])
        _update_language = _update_language[:-1] + data_from_dataSql.find_info
        self.execute(_update_language)

    def add_sql(self, *sql_list: str):
        for sql in sql_list:
            self.sql_list.append(sql)

    def show_sql(self, index: int = None):
        if index is None:
            for i in range(len(self.sql_list)):
                print_data("%s: %s" % (i, self.sql_list[i]))
        else:
            print_data("%s: %s" % (index, self.sql_list[index]))

    def delete_sql(self, index: int = None):
        if index is None:
            self.sql_list = list()
        else:
            self.sql_list.pop(index)

    def execute(self, sql: str):
        """
        执行并提交事务
        :param sql:
        :return:
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print_error("事务执行异常！", e)
            print_error(sql)

    def commit(self):
        """
        批量执行并提交已储存事务
        :param sql:
        :return:
        """
        try:
            for sql in self.sql_list:
                self.cursor.execute(sql)
            self.sql_list = list()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print_error("事务执行异常！", e)
            print_error(self.sql_list)

    def get_data(self, sql: str):
        """
        查找事务并返回数据
        """
        try:
            self.cursor.execute(sql)
        except Exception as e:
            self.db.rollback()
            print_error("数据查找异常！", e)
            print_error(sql)
        else:
            return self.cursor.fetchall()

    def get_temp_table_name(self, _last_table_name=None):
        self.cursor.execute(table_find_sql % self.database)
        results = self.cursor.fetchall()
        table_name_list_temp = tuple(map(lambda x: x[0], results))
        __index_temp = 0
        __temp_table_name = "temp_table_name_" if _last_table_name is None else "%s_" % _last_table_name
        while True:
            __temp_name = "%s%s" % (__temp_table_name, __index_temp)
            if __temp_name in table_name_list_temp:
                __index_temp += 1
            else:
                return __temp_name


def _find_info(**kwargs):
    """
    合成条件语句
    :param kwargs:
    :return:
    """
    if kwargs:
        find_info = " WHERE ("
        for key in kwargs.keys():
            if type(kwargs[key]) == str:
                kwargs[key] = kwargs[key].replace('"', "'")
                kwargs[key] = '"%s"' % kwargs[key]
            find_info += " `%s`=%s AND" % (key, kwargs[key])
        find_info = find_info[:-4] + " )"
    else:
        find_info = ""
    return find_info


def get_mysql_type(value):
    return mysql_type_to.get(type(value), "VARCHAR")


if __name__ == "__main__":
    db = EasySql(database="mysql", _user="root", _passwd="Fiachia123+")
