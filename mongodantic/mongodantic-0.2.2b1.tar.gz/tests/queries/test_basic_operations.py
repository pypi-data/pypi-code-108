import pytest
from bson import ObjectId

from mongodantic import connect
from mongodantic.models import MongoModel
from mongodantic.session import Session
from mongodantic.exceptions import DoesNotExist


class TestBasicOperation:
    def setup(self):
        connect("mongodb://127.0.0.1:27017", "test")

        class Ticket(MongoModel):
            name: str
            position: int
            config: dict
            sign: int = 1
            type_: str = 'ga'
            array: list = [1, 2]

            class Config:
                excluded_query_fields = ('sign', 'type')

        Ticket.Q.drop_collection(force=True)
        self.Ticket = Ticket

    def test_save(self):
        self.test_get_or_create()
        obj = self.Ticket.Q.find_one(name='testerino1', position=222222)
        obj.position = 2310
        obj.name = 'updated'
        obj.save()
        none_obj = self.Ticket.Q.find_one(name='testerino1', position=222222)
        assert none_obj is None
        new_obj = self.Ticket.Q.find_one(_id=obj._id)
        assert new_obj.name == 'updated'
        assert new_obj.position == 2310

    def test_json(self):
        self.test_save()
        obj = self.Ticket.Q.find_one(name='updated', position=2310)
        js = obj.json()
        assert js != {}

    @pytest.mark.asyncio
    async def test_async_save(self):
        self.test_get_or_create()
        obj = await self.Ticket.AQ.find_one(name='testerino1', position=222222)
        obj.position = 2310
        obj.name = 'updated'
        await obj.save_async()
        none_obj = await self.Ticket.AQ.find_one(name='testerino1', position=222222)
        assert none_obj is None
        new_obj = await self.Ticket.AQ.find_one(_id=obj._id)
        assert new_obj.name == 'updated'
        assert new_obj.position == 2310

    @pytest.mark.asyncio
    async def test_async_bulk(self):
        self.test_get_or_create()
        obj = await self.Ticket.AQ.find_one(name='testerino1', position=222222)
        obj.position = 2310
        obj.name = 'updated'
        await self.Ticket.AQ.bulk_update([obj], ['name', 'position'])
        new_obj = await self.Ticket.AQ.find_one(_id=obj._id)
        assert new_obj.name == 'updated'
        assert new_obj.position == 2310

    def test_get_or_create(self):
        obj, created = self.Ticket.Q.get_or_create(
            name='testerino1', position=222222, config={}, defaults={'array': [22, 23]}
        )
        assert created is True
        new_obj, created = self.Ticket.Q.get_or_create(
            name='testerino1', position=222222, config={}, defaults={'array': [22, 23]}
        )
        assert created is False
        assert new_obj._id == obj._id

    @pytest.mark.asyncio
    async def test_async_get_or_create(self):
        old_obj, created = await self.Ticket.AQ.get_or_create(
            name='testerino1',
            position=444343434,
            config={},
            defaults={'array': [22, 23]},
        )
        assert created is True
        obj, created = await self.Ticket.AQ.get_or_create(
            name='testerino1',
            position=444343434,
            config={},
            defaults={'array': [22, 23]},
        )
        assert created is False
        assert str(obj._id) == str(old_obj._id)

    def test_update_or_create(self):
        self.test_get_or_create()
        obj, created = self.Ticket.Q.update_or_create(
            name='testerino1', position=222222, config={}, defaults={'array': [23, 23]}
        )
        assert created is False
        assert obj.array[0] == 23

    @pytest.mark.asyncio
    async def test_async_update_or_create(self):
        old_obj, created = await self.Ticket.AQ.update_or_create(
            name='testerino1', position=222222, config={}, defaults={'array': [23, 23]}
        )
        assert created is True
        assert old_obj.array[0] == 23
        obj, created = await self.Ticket.AQ.update_or_create(
            name='testerino1', position=222222, config={}, defaults={'array': [24, 23]}
        )
        assert obj.array[0] == 24
        assert str(old_obj._id) == str(obj._id)

    def test_reconnect(self):
        old_connection = self.Ticket._connection._mongo_connection
        self.Ticket._reconnect()
        new_connection = self.Ticket._connection._mongo_connection
        assert id(old_connection) != id(new_connection)

    def test_collection_name(self):
        assert self.Ticket._collection_name == 'ticket'

    def test_insert_one(self):
        data = {
            'name': 'first',
            'position': 1,
            'config': {'param1': 'value'},
            'array': ['test', 'adv'],
        }
        object_id = self.Ticket.Q.insert_one(**data)
        assert isinstance(object_id, ObjectId)

    @pytest.mark.asyncio
    async def test_async_insert_one(self):
        data = {
            'name': 'first',
            'position': 1,
            'config': {'param1': 'value'},
            'array': ['test', 'adv'],
        }
        object_id = await self.Ticket.AQ.insert_one(**data)
        assert isinstance(object_id, ObjectId)

    def test_serialize(self):
        self.test_insert_one()
        data = self.Ticket.Q.find_one().serialize(('position', 'type_', 'sign'))
        keys = list(data.keys())
        assert 1 == keys.index('type_')
        assert 0 == keys.index('position')
        assert 2 == keys.index('sign')

    def test_insert_many(self):
        data = [
            self.Ticket(
                name='second',
                position=2,
                config={'param1': '2222'},
                array=['test', 'google'],
            ),
            self.Ticket(
                name='second',
                position=2,
                config={'param1': '3333'},
                array=['test', 'adv'],
            ),
        ]
        inserted = self.Ticket.Q.insert_many(data)
        assert inserted == 2

    @pytest.mark.asyncio
    async def test_async_insert_many(self):
        data = [
            self.Ticket(
                name='second',
                position=2,
                config={'param1': '2222'},
                array=['test', 'google'],
            ),
            self.Ticket(
                name='second',
                position=2,
                config={'param1': '3333'},
                array=['test', 'adv'],
            ),
        ]
        inserted = await self.Ticket.AQ.insert_many(data)
        assert inserted == 2

        data = [
            self.Ticket(
                name='third',
                position=3,
                config={'param1': '2222'},
                array=['test', 'google'],
            ).data,
            self.Ticket(
                name='four',
                position=4,
                config={'param1': '3333'},
                array=['test', 'adv'],
            ).data,
        ]
        inserted = await self.Ticket.AQ.insert_many(data)
        assert inserted == 2

    def test_insert_many_with_dict(self):
        data = [
            self.Ticket(
                name='third',
                position=3,
                config={'param1': '2222'},
                array=['test', 'google'],
            ).data,
            self.Ticket(
                name='four',
                position=4,
                config={'param1': '3333'},
                array=['test', 'adv'],
            ).data,
        ]
        inserted = self.Ticket.Q.insert_many(data)
        assert inserted == 2

    def test_find_in_array(self):
        self.test_insert_many()
        data = self.Ticket.Q.find_one(array__in=['google']).data
        assert data['array'] == ['test', 'google']
        miss = self.Ticket.Q.find_one(array__in=['miss_data'])
        assert miss is None

    def test_find_with_regex(self):
        self.test_insert_many()
        data = self.Ticket.Q.find_one(name__iregex="seCoNd")
        assert data.name == 'second'

    def test_count(self):
        self.test_insert_many()
        count = self.Ticket.Q.count()
        assert count == 2

    def test_find_one(self):
        self.test_insert_one()
        data = self.Ticket.Q.find_one(name='first')
        second = self.Ticket.Q.find_one(_id=data._id)
        assert isinstance(data, MongoModel)
        assert data.name == 'first'
        assert data.position == 1
        assert second._id == data._id

    @pytest.mark.asyncio
    async def test_async_find_one(self):
        await self.test_async_insert_one()
        data = await self.Ticket.AQ.find_one(name='first')
        second = await self.Ticket.AQ.find_one(_id=data._id)
        assert isinstance(data, MongoModel)
        assert data.name == 'first'
        assert data.position == 1
        assert second._id == data._id

    def test_find(self):
        self.test_insert_many()
        data = self.Ticket.Q.find(name='second').list
        sort = self.Ticket.Q.find(name='second', sort=-1, sort_fields=('_id',)).first()
        assert sort.config == {'param1': '3333'}
        assert isinstance(data, list)
        assert len(data) == 2
        assert isinstance(data[0], MongoModel)

    @pytest.mark.asyncio
    async def test_async_find(self):
        self.test_insert_many()
        r = await self.Ticket.AQ.find(name='second')
        data = r.list
        r = await self.Ticket.AQ.find(name='second', sort=-1, sort_fields=('_id',))
        sort = r.first()
        assert sort.config == {'param1': '3333'}
        assert isinstance(data, list)
        assert len(data) == 2
        assert isinstance(data[0], MongoModel)

    def test_get(self):
        self.test_insert_one()
        data = self.Ticket.Q.get(name='first')
        second = self.Ticket.Q.get(_id=data._id)
        assert isinstance(data, MongoModel)
        assert data.name == 'first'
        assert data.position == 1
        assert second._id == data._id
        with pytest.raises(DoesNotExist):
            _ = self.Ticket.Q.get(name='invalid_name')

    @pytest.mark.asyncio
    async def test_async_get(self):
        await self.test_async_insert_one()
        data = await self.Ticket.AQ.get(name='first')
        second = await self.Ticket.AQ.get(_id=data._id)
        assert isinstance(data, MongoModel)
        assert data.name == 'first'
        assert data.position == 1
        assert second._id == data._id
        with pytest.raises(DoesNotExist):
            _ = self.Ticket.Q.get(name='invalid_name')

    def test_distinct(self):
        self.test_insert_many()
        data = self.Ticket.Q.distinct('config.param1', name='second')
        assert data == ['2222', '3333']

    def test_queryset_serialize(self):
        self.test_insert_many()
        data = self.Ticket.Q.find(name='second').serialize(fields=['name', 'config'])
        assert len(data[0]) == 2
        assert data[0]['config'] == {'param1': '2222'}
        assert data[0]['name'] == 'second'
        assert isinstance(data, list)

    def test_delete_one(self):
        self.test_insert_one()
        deleted = self.Ticket.Q.delete_one(position=1)
        assert deleted == 1

    @pytest.mark.asyncio
    async def test_async_delete_one(self):
        await self.test_async_insert_one()
        deleted = await self.Ticket.AQ.delete_one(position=1)
        assert deleted == 1

    def test_delete_many(self):
        self.test_insert_many()
        deleted = self.Ticket.Q.delete_many(position=2)
        assert deleted == 2
        self.test_insert_many()
        items = self.Ticket.Q.find().list
        deleted = self.Ticket.Q.delete_many(_id__in=[i._id for i in items])
        assert deleted == 2

    @pytest.mark.asyncio
    async def test_async_delete_many(self):
        self.test_insert_many()
        deleted = await self.Ticket.AQ.delete_many(position=2)
        assert deleted == 2
        self.test_insert_many()
        r = await self.Ticket.AQ.find()
        items = r.list
        deleted = await self.Ticket.AQ.delete_many(_id__in=[i._id for i in items])
        assert deleted == 2

    def test_update_one(self):
        self.test_insert_one()
        data = self.Ticket.Q.update_one(name='first', config__set={'updated': 1})
        updated = self.Ticket.Q.find_one(name='first')
        assert data == 1
        assert updated.config == {'updated': 1}

    @pytest.mark.asyncio
    async def test_async_update_one(self):
        self.test_insert_one()
        data = await self.Ticket.AQ.update_one(name='first', config__set={'updated': 1})
        updated = await self.Ticket.AQ.find_one(name='first')
        assert data == 1
        assert updated.config == {'updated': 1}

    def test_update_many(self):
        self.test_insert_many()
        data = self.Ticket.Q.update_many(name='second', config__set={'updated': 3})
        updated = self.Ticket.Q.find_one(name='second')
        assert data == 2
        assert updated.config == {'updated': 3}

    @pytest.mark.asyncio
    async def test_async_update_many(self):
        self.test_insert_many()
        data = await self.Ticket.AQ.update_many(
            name='second', config__set={'updated': 3}
        )
        updated = await self.Ticket.AQ.find_one(name='second')
        assert data == 2
        assert updated.config == {'updated': 3}

    def test_find_and_update(self):
        self.test_insert_one()
        data_default = self.Ticket.Q.find_one_and_update(name='first', position__set=23)
        assert data_default.position == 23

        data_with_prejection = self.Ticket.Q.find_one_and_update(
            name='first', position__set=12, projection_fields=['position']
        )
        assert isinstance(data_with_prejection, dict)
        assert data_with_prejection['position'] == 12

    @pytest.mark.asyncio
    async def test_async_find_and_update(self):
        self.test_insert_one()
        data_default = await self.Ticket.AQ.find_one_and_update(
            name='first', position__set=23
        )
        assert data_default.position == 23

        data_with_prejection = await self.Ticket.AQ.find_one_and_update(
            name='first', position__set=12, projection_fields=['position']
        )
        assert isinstance(data_with_prejection, dict)
        assert data_with_prejection['position'] == 12

    def test_delete_method(self):
        self.test_insert_one()
        ticket = self.Ticket.Q.find_one(name='first')
        ticket.delete()
        data = self.Ticket.Q.find_one(name='first')
        assert data is None

    @pytest.mark.asyncio
    async def test_async_delete_method(self):
        self.test_insert_one()
        ticket = await self.Ticket.AQ.find_one(name='first')
        await ticket.delete_async()
        data = await self.Ticket.AQ.find_one(name='first')
        assert data is None

    def test_session(self):
        self.test_insert_one()
        with Session(self.Ticket) as session:
            result = self.Ticket.Q.find_one(name='first', session=session)
        assert result.name == 'first'

    # def test_session_with_transaction(self):

    #     with Session(self.Ticket) as session:
    #         with session.start_transaction():
    #             result = self.Ticket.Q.insert_one(
    #                 name='last', position=33333, config={}, session=session
    #             )
    #     assert result.name == 'first'
