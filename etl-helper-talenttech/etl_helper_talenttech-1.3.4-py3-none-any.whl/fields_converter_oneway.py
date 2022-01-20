from converter.database_worker import DataBaseWorker
from converter.config.config_converter import base_converter_params
import logging
import warnings
import sys
import json

warnings.filterwarnings("ignore")


def save_ddl_to_file(ddl, table_name, ddl_dir):
    """
    save ddl to file if you wish
    :param table_name:
    :param ddl_dir:
    :return:
    """
    f = open(
        ddl_dir + "/" + table_name + ".sql",
        "w",
    )
    f.write(ddl)
    f.close()


class FieldsConverterOneWay:
    """
    class to upload just one way (from list of dicts to sql table)
    """

    def __init__(self, sql_credentials, db, debug=True, tables=None):
        """
        :param sql_credentials:
        :param db: ch, vertica, mysql, pg or others
        :param debug: show debug text
        :param tables:  converter only for list of tables. Will process more rapid
        """
        log_format = "%(asctime)-15s %(name)s:%(levelname)s: %(message)s"
        logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)
        logging.basicConfig(format=log_format, stream=sys.stderr, level=logging.ERROR)
        logging.captureWarnings(True)
        self.logger = logging.getLogger(__class__.__name__)

        if sql_credentials is not None:
            self.db_worker = DataBaseWorker(sql_credentials, db, debug, tables)
        else:
            self.db_worker = None
        self.db = db

    @property
    def __str__(self):
        return "FieldsConverterOneWay_{}".format(self.db)

    @property
    def quote_char(self):
        return base_converter_params[self.db]["quote"]

    @property
    def __repr__(self):
        return "FieldsConverterOneWay_{}".format(self.db)

    def __del__(self):
        del self.db_worker

    def __get_python_type(self, type_sql):
        """
        Get type to convert in python
        :param   type_sql
        :return: type_python
        """
        type_python = "str"
        update_types_dict = base_converter_params[self.db]["to_python_dict"]
        for type_old in update_types_dict:
            if type_sql.lower().find(type_old) > -1:
                type_python = update_types_dict[type_old]
                return type_python
        return type_python

    def __get_sql_type(self, type_python):
        """
        Get type to convert in sql from python
        :param   type_
        :return: type_python
        """
        update_types_dict = base_converter_params[self.db]["from_python_dict"]
        type_sql = update_types_dict["str"]
        for type_old in update_types_dict:
            if type_python.lower().find(type_old) > -1:
                type_sql = update_types_dict[type_old]
                return type_sql
        return type_sql

    def update_value_df_type(self, table_name, dataframe, dict_replace_str={}):
        """
        :param table_name:
        :param fields:
        :param dataframe:
        :param dict_replace_str:
        :return: updated dataframe
        """
        fields = self.db_worker.get_columns(table_name)
        for key in list(dataframe.columns):
            type_python = self.__get_python_type(fields[key])
            dataframe[key] = dataframe[key].astype(type_python)
            if type == "str":
                dataframe[key] = dataframe[key].replace(to_replace=dict_replace_str)
        return dataframe

    def __update_value_type(
            self, fields, item, key, dict_replace_str={}, json_fields=None
    ):
        """
        :param dict_replace_str: - replace params to
        :param amocrm.db: amocrm.db to update
        :param fields: dict - key  type
        :param item: - to update item
        :param key: key to update
        :param json_fields: fields that need to make as valid json
        :return: converted item
        """
        json_fields = json_fields or []

        if item is None:
            return item
        if key not in item:
            return item
        if item[key] is None:
            return item

        type_python = self.__get_python_type(fields[key])
        if type_python == "int":
            item[key] = int(item[key])
        elif type_python == "float":
            item[key] = float(item[key])
        elif type_python == "json" or key in json_fields:
            try:
                item[key] = json.dumps(item[key], ensure_ascii=False)
            except (TypeError, ValueError):
                item[key] = item[key]
        elif type_python == "bool":
            item[key] = bool(item[key])
        elif type_python == "datetime":
            from dateutil import parser
            item[key] = parser.parse(str(item[key]))
        else:
            item[key] = str(item[key])
            for key_replace in dict_replace_str:
                item[key] = item[key].replace(
                    key_replace, dict_replace_str[key_replace]
                )
        return item

    def update_value_type(
            self, table_name, items, dict_replace_str={}, fields=None, json_fields=None
    ):
        """
        :param json_fields:
        :param fields:
        :param dict_replace_str: replace in string dict
        :param items: list of dicts to update
        :param table_name: table_name to insert
        :return: updated dictionary
        """
        fields = fields or self.db_worker.get_columns(table_name=table_name)
        if len(fields) == 0:
            raise Exception("No table {} in metadata".format(table_name))
        keys = fields.keys()
        for item in items:
            for key in keys:
                item = self.__update_value_type(
                    fields,
                    item,
                    key,
                    dict_replace_str=dict_replace_str,
                    json_fields=json_fields,
                )
        return items

    def create_table_from_python(
            self, fields_python, table_name, to_create=True, ddl_dir=None, schema=None
    ):
        """create tables using python types"""
        txt = "\n\nCREATE TABLE {schema}.{table} (".format(
            schema=schema or self.schema, table=table_name
        )
        res_list = []
        for field in fields_python:
            type_python = fields_python[field]
            type_sql = self.__get_sql_type(type_python)
            res_list.append(self.quote_char + field + self.quote_char + " " + type_sql)
        txt += ",\n".join(res_list)
        txt += ")"
        if to_create:
            self.conn.execute(txt)
            self.logger.info("creating table {} is successful".format(table_name))
        if ddl_dir is not None:
            save_ddl_to_file(ddl=txt, ddl_dir=ddl_dir, table_name=table_name)
        return txt

    def create_table_from_dataframe(
            self, dataframe, table_name, to_create=True, ddl_dir=None, schema=None
    ):
        """create tables using python types"""
        txt = "\n\nCREATE TABLE {schema}.{table} (".format(
            schema=schema or self.schema, table=table_name
        )
        fields_python = dataframe.dtypes.apply(lambda x: x.name).to_dict()
        res_list = []
        for field in fields_python:
            type_python = fields_python[field]
            type_sql = self.__get_sql_type(type_python)
            res_list.append(self.quote_char + field + self.quote_char + " " + type_sql)
        txt += ",\n".join(res_list)
        txt += ")"
        if to_create:
            self.conn.execute(txt)
            self.logger.info("creating table {} is successful".format(table_name))
        if ddl_dir is not None:
            save_ddl_to_file(ddl=txt, ddl_dir=ddl_dir, table_name=table_name)
        return txt
