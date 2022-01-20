import logging
import sys
import warnings
from converter.database_worker import DataBaseWorker
from converter.config.config_converter import (
    types_converter_dict,
    base_converter_params,
    excluded_fields,
)
from converter.advanced_ddl.advanced_ddl_creator import AdvancedDDLCreator

warnings.filterwarnings("ignore")


def save_ddl_to_file(sql, table_name, ddl_dir):
    """
    save ddl to file if you wish
    :param sql: ddl to save
    :param table_name:
    :param ddl_dir:
    :return:
    """
    f = open(ddl_dir + "/" + table_name + ".sql", "w", )
    f.write(sql)
    f.close()


class FieldsConverter:
    def __init__(
            self,
            sql_credentials,
            from_db,
            to_db,
            debug=True,
            tables=None,
            advanced_features=None,
    ):
        """
        Class ddl-converter from one database to another
        :param sql_credentials:
        :param from_db:
        :param to_db:
        :param debug: show debug text
        :param tables: converter only for list of tables. Will process more rapidly
        :param advanced_features: 0 - get sizes of text, 1 - to primary key constraint
        """
        log_format = "%(asctime)-15s %(name)s:%(levelname)s: %(message)s"
        logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)
        logging.basicConfig(format=log_format, stream=sys.stderr, level=logging.ERROR)
        logging.captureWarnings(True)
        self.logger = logging.getLogger(__class__.__name__)

        self.advanced_features = advanced_features or []
        self.tables = tables or []
        self.from_db = from_db
        self.to_db = to_db
        self.key = self.from_db + ":" + self.to_db
        self.__check_converter()
        self.debug = debug
        self.sql_credentials = sql_credentials
        self.db_worker_from = DataBaseWorker(sql_credentials, from_db, debug, tables)
        self.db_worker_to = DataBaseWorker(
            sql_credentials, to_db, debug, tables, table_checker=False
        )

    def __check_converter(self):
        if self.key not in types_converter_dict:
            raise NotImplementedError(
                "table converter from {} to {} is not implemented".format(
                    self.from_db, self.to_db
                )
            )

    @property
    def __str__(self):
        return "FieldsConverter_{}_{}".format(self.from_db, self.to_db)

    @property
    def __repr__(self):
        return "FieldsConverter_{}_{}".format(self.from_db, self.to_db)

    def __get_fields_definition(
            self, table_name, field_name, field_type, attributes={}
    ):
        """
        Get field definition result
        :param field_name:
        :param field_type:
        :param attributes: a
        :return: result field
        """
        if "text_sizes" in attributes and field_name in attributes["text_sizes"]:
            if (
                    field_type == "long varchar"
                    and attributes["text_sizes"][field_name] < 65000
            ):
                field_type = "varchar"
            text_size = "(" + str(attributes["text_sizes"][field_name]) + ")"
        else:
            text_size = ""
        if (
                "constrained_columns" in attributes
                and field_name in attributes["constrained_columns"]
        ):
            constrained = " " + base_converter_params[self.to_db][
                "constrained_columns_str"
            ].format(table_name=table_name)
        else:
            constrained = ""

        return "{quote}{field_name}{quote} {field_type}{text_size}{constrained}".format(
            quote=self.db_worker_to.quote_char,
            field_name=field_name,
            field_type=field_type,
            text_size=text_size,
            constrained=constrained,
        )

    def update_column_type(self, column):
        """convert types between source and destination"""
        type_from = column["data_type"]
        types_conv = types_converter_dict[self.key]["type"]
        if type_from in types_conv:
            type_to = types_conv[type_from]
        else:
            type_to = type_from

        if column["character_maximum_length"] is not None and type_to not in "text" and self.to_db != 'ch':
            max_length_mult = base_converter_params[self.to_db]["max_length_mult"]
            type_to += "({character_maximum_length})".format(
                character_maximum_length=int(
                    column["character_maximum_length"] * max_length_mult
                )
            )
            return type_to
        if column["column_default"] is not None:
            default_from = column["column_default"].lower()
            if default_from in types_converter_dict[self.key]["default"]:
                default_to = types_converter_dict[self.key]["default"][default_from]
            else:
                default_to = default_from
            type_to += " DEFAULT {column_default}".format(column_default=default_to)

        return type_to

    def generate_create(self, fields_new, table_name):
        """
        :param fields_new:
        :param table_name:
        :return: ddl
        """
        attributes = {}
        if len(self.advanced_features) > 0:
            self.logger.info("advanced ddl creator. get additional attributes")
            adv_ddl = AdvancedDDLCreator(
                fields_converter=self, advanced_features=self.advanced_features
            )
            attributes = adv_ddl.get_attributes(table_name)
        print(attributes)
        ddl = "\n\nCREATE TABLE {schema}.{table}\n(\n".format(
            schema=self.db_worker_to.schema, table=table_name
        )

        ddl += ",\n".join(
            [
                "    "
                + self.__get_fields_definition(
                    table_name=table_name,
                    field_name=field,
                    field_type=fields_new[field],
                    attributes=attributes,
                )
                for field in fields_new
                if field not in excluded_fields
            ]
        )
        ddl += "\n);\n\n\n"
        return ddl

    def create_ddl(self, table_name):
        self.db_worker_from.check_if_table_availible(table_name)
        fields = self.db_worker_from.get_table_schema(table_name)
        fields_new = {}
        for f in fields:
            fields_new[f["column_name"]] = self.update_column_type(f)
        return self.generate_create(fields_new, table_name)

    def drop_list_of_tables(self, tables):
        """drop every fkn table in a list"""
        for table in tables:
            sql = "drop table {schema}.{table} cascade ".format(
                schema=self.db_worker_to.schema, table=table
            )
            self.db_worker_to.conn.execute(sql)

    def create_list_of_tables(self, tables, to_create=True, dir_ddl=None, suffix=None):
        result_list = []
        for table in tables:
            sql = self.create_ddl(table_name=table)
            if suffix:
                sql = sql.replace(");", ") " + suffix + ";")
            result_list.append(sql)
            if to_create:
                self.db_worker_to.conn.execute(sql)
                self.logger.info("creating table {} is successful".format(table))
            if dir_ddl is not None:
                save_ddl_to_file(sql=sql, table_name=table, ddl_dir=dir_ddl)
        return result_list
