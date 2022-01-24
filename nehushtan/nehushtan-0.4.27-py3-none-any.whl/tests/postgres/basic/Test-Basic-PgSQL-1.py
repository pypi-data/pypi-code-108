from nehushtan.helper.CommonHelper import CommonHelper
from tests.postgres.PgSQLTestEnv import PgSQLTestEnv


class TestBasic1:
    def __init__(self):
        self.__env = PgSQLTestEnv()
        self.__kit = self.__env.get_pg_kit_instance()

    def test(self):
        # self.__create_schema()
        # self.__create_table_1()
        self.__insert_some()
        self.__query_all()
        self.__query_some_1()
        self.__query_some_2()
        self.__done_transcation()
        self.__undone_transcation()
        # self.__drop_schema_cascade()

    def __create_schema(self):
        result = self.__kit.execute('create schema nehushtan_test_basic')
        self.__env.log_for_result_set(result)

    def __create_table_1(self):
        result = self.__kit.execute(
            '''create table nehushtan_test_basic.table_1 (
                id serial,
                name varchar(255) COLLATE "pg_catalog"."default",
                content varchar(255),
                act_time timestamp,
                primary key (id)
            );'''
        )
        self.__env.log_for_result_set(result)

    def __insert_some(self):
        content = CommonHelper.generate_a_password_string(16)
        result = self.__kit.execute(
            """insert into nehushtan_test_basic.table_1(name,content,act_time)values(%s,%s,now()) returning id""",
            ('a', content)
        )
        self.__env.log_for_result_set(result)

    def __query_all(self):
        result = self.__kit.execute(
            """select * from nehushtan_test_basic.table_1"""
        )
        self.__env.log_for_result_set(result)

    def __query_some_1(self):
        result = self.__kit.execute(
            """select 
                name,to_timestamp(avg(EXTRACT(epoch FROM act_time)))
            from nehushtan_test_basic.table_1
            where name='a' 
            group by name"""
        )
        self.__env.log_for_result_set(result)

    def __query_some_2(self):
        result = self.__kit.execute(
            """select
                id,name,content,'do not use value binding, one percent char for one'
            from nehushtan_test_basic.table_1
            where content like '%a%'
            """
        )
        self.__env.log_for_result_set(result)
        result = self.__kit.execute(
            """select
                id,name,content,'use value binding, two percent chars for one'
            from nehushtan_test_basic.table_1
            where content like '%%a%%'
            and id = %s
            """,
            (7,)
        )
        self.__env.log_for_result_set(result)

        result = self.__kit.execute(
            """select
                id,name,content,'use value binding, just put percent into value'
            from nehushtan_test_basic.table_1
            where content like %s
            """,
            ('%a%',)
        )
        self.__env.log_for_result_set(result)

    def __done_transcation(self):
        with self.__kit.get_raw_connection():
            content = CommonHelper.generate_a_password_string(16)
            result = self.__kit.execute(
                """insert into nehushtan_test_basic.table_1(name,content,act_time)
                values(%s,%s,now()) 
                returning id""",
                ('transcation_done', content)
            )
            self.__env.log_for_result_set(result)

    def __undone_transcation(self):
        try:
            with self.__kit.get_raw_connection():
                content = CommonHelper.generate_a_password_string(16)
                result = self.__kit.execute(
                    """insert into nehushtan_test_basic.table_1(name,content,act_time)
                    values(%s,%s,now()) 
                    returning id""",
                    ('transcation_undone', content)
                )
                self.__env.log_for_result_set(result)
                raise Exception('let us rollback!')
        except:
            self.__env.log('ROLLBACK')

    def __drop_schema_cascade(self):
        result = self.__kit.execute('drop schema nehushtan_test_basic CASCADE')
        self.__env.log_for_result_set(result)


if __name__ == '__main__':
    x = TestBasic1()
    x.test()
