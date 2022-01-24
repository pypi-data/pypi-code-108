import unittest

from nehushtan.mysql.MySQLAnyTable import MySQLAnyTable
from nehushtan.mysql.MySQLCondition import MySQLCondition
from nehushtan.mysql.MySQLKit import MySQLKit
from nehushtan.mysql.MySQLKitConfig import MySQLKitConfig
from nehushtan.mysql.MySQLUnionSelection import MySQLUnionSeletion
from tests.config import MYSQL_CONFIG


class TestForMySQLSelection(unittest.TestCase):
    def setUp(self) -> None:
        self.table = MySQLAnyTable(
            MySQLKit(MySQLKitConfig(MYSQL_CONFIG)),
            'c'
        )

        self.table.truncate()
        for i in range(100):
            self.table.insert_one_row({'value': i * i, 'name': f'item [{i}]'})

    def test_1(self):
        result = self.table.select_in_table() \
            .add_condition(MySQLCondition.make_between('value', 100, 200)) \
            .query_for_result_as_tuple_of_dict()

        the_tuple = result.get_fetched_rows_as_tuple()
        print(len(the_tuple))
        for i in the_tuple:
            print(i)

    def test_2(self):
        result = self.table.select_in_table() \
            .add_condition(MySQLCondition.make_between('value', 400, 800)) \
            .query_for_result_as_tuple_of_dict()

        the_tuple = result.get_fetched_rows_as_tuple()
        print(len(the_tuple))
        for i in the_tuple:
            print(i)

    def test_3(self):
        s1 = self.table.select_in_table() \
            .add_condition(MySQLCondition.make_between('value', 100, 200))
        s2 = self.table.select_in_table() \
            .add_condition(MySQLCondition.make_between('value', 400, 800))

        result = MySQLUnionSeletion() \
            .add_sub_selection(s1) \
            .add_sub_selection(s2) \
            .query_for_result_as_tuple_of_dict()

        print(result.get_sql())
        print(result.get_error())

        the_tuple = result.get_fetched_rows_as_tuple()
        print(len(the_tuple))
        for i in the_tuple:
            print(i)

    def test_4(self):
        s1 = self.table.select_in_table() \
            .add_condition(MySQLCondition.make_between('value', 100, 500))
        s2 = self.table.select_in_table() \
            .add_condition(MySQLCondition.make_between('value', 200, 800))

        result = MySQLUnionSeletion() \
            .add_sub_selection(s1) \
            .add_sub_selection(s2, True) \
            .query_for_result_as_tuple_of_dict()

        print(result.get_sql())
        print(result.get_error())

        the_tuple = result.get_fetched_rows_as_tuple()
        print(len(the_tuple))
        for i in the_tuple:
            print(i)
