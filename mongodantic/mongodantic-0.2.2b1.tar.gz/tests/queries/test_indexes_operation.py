import pymongo
import unittest
import pytest
from pymongo import IndexModel
from mongodantic.models import MongoModel
from mongodantic import connect
from mongodantic.exceptions import MongoIndexError


class TestIndexOperation:
    def setup(self, drop=False, basic_indexes=True):
        connect("mongodb://127.0.0.1:27017", "test")

        class Ticket(MongoModel):
            name: str
            position: int
            config: dict

            class Config:
                if basic_indexes:
                    indexes = [IndexModel([('position', 1)]), IndexModel([('name', 1)])]
                else:
                    indexes = indexes = [IndexModel([('position', 1)])]

        if drop:
            Ticket.querybuilder.drop_collection(force=True)
        self.Ticket = Ticket
        self.Ticket.execute_indexes()

    def test_check_indexes(self):
        self.setup(False)
        result = self.Ticket.querybuilder.check_indexes()
        assert result == {
            '_id_': {'key': {'_id': 1}},
            'position_1': {'key': {'position': 1}},
            'name_1': {'key': {'name': 1}},
        }

    def test_check_indexes_if_remove(self):
        self.setup(False, False)
        result = self.Ticket.querybuilder.check_indexes()
        assert result == {
            '_id_': {'key': {'_id': 1}},
            'position_1': {'key': {'position': 1}},
        }

    def test_drop_index(self):
        self.setup(False)
        with pytest.raises(MongoIndexError):
            result = self.Ticket.querybuilder.drop_index('position1111')

        result = self.Ticket.querybuilder.drop_index('position_1')
        assert result == 'position_1 dropped.'
        self.setup(True, False)
