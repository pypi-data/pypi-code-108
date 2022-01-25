from execpeewee.mapping import PeeweeFields
import inspect
import pymysql
import re


class PeeweeModel:
    def __init__(self, peewee_db):
        """
        peewee model builder connect args.
        """
        self.peewee_db = peewee_db
        self.db_name = [k for k, v in inspect.currentframe().f_back.f_locals.items() if v is peewee_db][0]
        self.db = pymysql.connect(database=peewee_db.database, **peewee_db.connect_params)
        self.fields = PeeweeFields.get()
        self.unknown = PeeweeFields.UnknownField.__name__

    def __del__(self):
        """
        finish func then close.
        """
        self.db.close()

    def build_model(self, table: str, exc_fields: list = None):
        """
        pymysql get single database table fields build peewee model.
        :param table: the table name of mysql database which one to build peewee model
        :param exc_fields: don't display item according mysql fields type e.g: ['datetime']
        """
        sql, exc_fields, s = f'show columns from {table}', exc_fields or [], lambda num: ''.rjust(num, ' ')
        fields = '\n'+''.join([self.__fields_filter(i, exc_fields, s) for i in self.__connect(sql)])
        class_name = ''.join([i.capitalize() for i in table.split('_')])
        subclass = f'{s(4)}class Meta:\n' \
                   f'{s(8)}database = {self.db_name}\n' \
                   f"{s(8)}table_name = '{table}'\n" \
                   # f'{s(8)}# primary_key = CompositeKey("fields_1", "fields_2")\n'
        print(f'\nclass {class_name}(Model): {fields}\n{subclass}')

    def build_models(self, table=None, exc_fields: list = None):
        """
        pymysql get all or single database table fields build peewee model.
        :param table: the table name which one to build peewee model
        :param exc_fields: don't display item according mysql fields type e.g: ['datetime']
        """
        tables, exc_fields = [table] if table else self.__tables(), exc_fields or []
        [self.build_model(table_, exc_fields=exc_fields) for table_ in tables]

    def __connect(self, sql):
        cursor = self.db.cursor()
        cursor.execute(sql)
        query = cursor.fetchall()
        cursor.close()
        return query

    def __tables(self) -> list:
        """
        pymysql get database table names.
        """
        tables = self.peewee_db.get_tables()
        table_list = ['All Tables'] + tables
        [print(f'{k} -> {v}') for k, v in enumerate(table_list)]
        choose = input('enter index num which table name choosed (split with ","):').replace(' ', '').split(',')
        return tables if '0' in choose else [table_list[int(i)] for i in choose]

    def __fields_filter(self, columns_info, exc_fields, s):
        pattern = r'\(.*$'
        fields_type = re.sub(pattern, '', columns_info[1])
        return (f'{s(4)}{columns_info[0]} = {self.fields.get(fields_type, self.unknown)}()  # {columns_info[1]}\n'
                if self.__check_exc(columns_info, exc_fields) else '')

    @classmethod
    def __check_exc(cls, columns_info, exc_fields):
        return [1 for i in exc_fields if i in columns_info[0]].count(1) == 0
