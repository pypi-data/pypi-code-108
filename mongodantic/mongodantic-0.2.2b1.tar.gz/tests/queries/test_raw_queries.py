import unittest
import pytest
from bson import ObjectId
from uuid import uuid4, UUID

from mongodantic.models import MongoModel
from mongodantic import connect
from mongodantic.exceptions import MongoValidationError


class TestBasicOperation:
    def setup(self):
        connect("mongodb://127.0.0.1:27017", "test")

        class User(MongoModel):
            id: UUID
            name: str
            email: str

            class Config:
                excluded_query_fields = ('sign', 'type')

        User.Q.drop_collection(force=True)
        self.User = User

    def test_raw_insert_one(self):
        with pytest.raises(MongoValidationError):
            result = self.User.Q.raw_query(
                'insert_one', {'id': uuid4(), 'name': {}, 'email': []}
            )
        result = self.User.Q.raw_query(
            'insert_one', {'id': uuid4(), 'name': 'first', 'email': 'first@mail.ru'}
        )
        assert isinstance(result.inserted_id, ObjectId)

    # @pytest.mark.asyncio
    # async def test_async_raw_insert_one(self):
    #     with pytest.raises(MongoValidationError):
    #         result = await self.User.AQ.raw_query(
    #             'insert_one', {'id': uuid4(), 'name': {}, 'email': []}
    #         )
    #     result = await self.User.AQ.raw_query(
    #         'insert_one', {'id': uuid4(), 'name': 'first', 'email': 'first@mail.ru'}
    #     )
    #     assert isinstance(result.inserted_id, ObjectId)

    # @pytest.mark.asyncio
    # async def test_async_raw_insert_many(self):
    #     with pytest.raises(MongoValidationError):
    #         result = await self.User.AQ.raw_query(
    #             'insert_many', [{'id': uuid4(), 'name': {}, 'email': []}]
    #         )
    #     result = await self.User.AQ.raw_query(
    #         'insert_many', [{'id': uuid4(), 'name': 'first', 'email': 'first@mail.ru'}]
    #     )
    #     assert len(result.inserted_ids) == 1

    def test_raw_find_one(self):
        self.test_raw_insert_one()
        result = self.User.Q.raw_query('find_one', {'name': 'first'})
        assert result['name'] == 'first'
        assert result['email'] == 'first@mail.ru'

    # @pytest.mark.asyncio
    # async def test_async_raw_find_one(self):
    #     await self.test_async_raw_insert_one()
    #     result = await self.User.AQ.raw_query('find_one', {'name': 'first'})
    #     assert result['name'] == 'first'
    #     assert result['email'] == 'first@mail.ru'

    def test_raw_update_one(self):
        self.test_raw_insert_one()
        with pytest.raises(MongoValidationError):
            result = self.User.Q.raw_query(
                'update_one', [{'id': uuid4(), 'name': {}, 'email': []}]
            )
        result = self.User.Q.raw_query(
            'update_one', raw_query=({'name': 'first'}, {'$set': {'name': 'updated'}})
        )

        assert result.modified_count == 1

        modifed_result = self.User.Q.find_one(email='first@mail.ru')
        assert modifed_result.name == 'updated'

    # @pytest.mark.asyncio
    # async def test_async_raw_update_one(self):
    #     await self.test_async_raw_insert_one()
    #     with pytest.raises(MongoValidationError):
    #         result = await self.User.AQ.raw_query(
    #             'update_one', [{'id': uuid4(), 'name': {}, 'email': []}]
    #         )
    #     result = await self.User.AQ.raw_query(
    #         'update_one', raw_query=({'name': 'first'}, {'$set': {'name': 'updated'}})
    #     )

    #     assert result.modified_count == 1

    #     modifed_result = await self.User.AQ.find_one(email='first@mail.ru')
    #     assert modifed_result.name == 'updated'
