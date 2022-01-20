# coding=utf-8
import unittest
import pyclickhouse


class TestPy23Compatibility(unittest.TestCase):
    """Test compatibility of insert operations with Unicode text"""

    def setUp(self):
        self.conn = pyclickhouse.Connection('localhost:8124')
        self.cursor=self.conn.cursor()
        self.cursor.ddl("create database if not exists test")
        self.cursor.ddl("drop table if exists test")


    def tearDown(self):
        self.cursor.ddl("drop database if exists test")

    def test_insert(self):
        self.cursor.ddl("create table IF NOT EXISTS test.test (geoid String, objektanzahl UInt64) Engine=TinyLog")
        self.cursor.insert(u"insert into test.test values ('ŋéöìð',123)")

    def test_bulkinsert(self):
        self.cursor.ddl("create table IF NOT EXISTS test.test (geoid String, objektanzahl UInt64) Engine=TinyLog")
        values = [dict(geoid=u'ŋéöìð', objektanzahl=123)]
        self.cursor.bulkinsert(table='test.test', values=values)

    def test_insert_list(self):
        self.cursor.ddl("create table IF NOT EXISTS test.test_list (geoid Array(String), objektanzahl UInt64) Engine=TinyLog")
        self.cursor.insert(u"insert into test.test_list values (array('ŋéöìð','ŋéöìð'),123)")

    def test_bulkinsert_list(self):
        self.cursor.ddl("create table IF NOT EXISTS test.test_list (geoid Array(String), objektanzahl UInt64) Engine=TinyLog")
        values = [dict(geoid=[u'ŋéöìð',u'ŋéöìð'], objektanzahl=123)]
        self.cursor.bulkinsert(table='test.test_list', values=values)

