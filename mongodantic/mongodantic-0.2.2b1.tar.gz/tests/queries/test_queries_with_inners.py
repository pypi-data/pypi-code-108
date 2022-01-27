from mongodantic.models import MongoModel
from mongodantic import connect


class TestQueriesWithInners:
    def setup(self):
        connect("mongodb://127.0.0.1:27017", "test")

        class InnerTicket(MongoModel):
            name: str
            position: int
            config: dict
            params: dict
            sign: int = 1
            type_: str = 'ga'

            class Config:
                excluded_query_fields = ('sign', 'type')

        InnerTicket.querybuilder.drop_collection(force=True)
        self.InnerTicket = InnerTicket

    def create_documents(self):
        self.InnerTicket.querybuilder.insert_one(
            name='first',
            position=1,
            config={'url': 'localhost', 'username': 'admin'},
            params={},
        )
        self.InnerTicket.querybuilder.insert_one(
            name='second',
            position=2,
            config={'url': 'google.com', 'username': 'staff'},
            params={},
        )
        self.InnerTicket.querybuilder.insert_one(
            name='third',
            position=3,
            config={'url': 'yahoo.com', 'username': 'trololo'},
            params={'1': 1},
        )
        self.InnerTicket.querybuilder.insert_one(
            name='fourth',
            position=4,
            config={'url': 'yahoo.com', 'username': 'trololo'},
            params={'2': 2},
        )

    def test_update_many(self):
        self.create_documents()
        updated = self.InnerTicket.querybuilder.update_many(
            position__range=[3, 4], name__ne='hhh', config__url__set='test.io'
        )
        assert updated == 2
        last = self.InnerTicket.querybuilder.find_one(sort=-1)
        assert last.config['url'] == 'test.io'

    def test_inner_find_one(self):
        self.create_documents()
        data = self.InnerTicket.querybuilder.find_one(
            config__url__startswith='yahoo', params__1=1
        )
        assert data.name == 'third'

        data = self.InnerTicket.querybuilder.find_one(
            config__url__startswith='yahoo', params__1='qwwe'
        )
        assert data is None

    def test_inner_update_one(self):
        self.create_documents()
        updated = self.InnerTicket.querybuilder.update_one(
            config__url__startswith='goo', config__url__set='test.io'
        )
        assert updated == 1
        data = self.InnerTicket.querybuilder.find_one(config__url__startswith='test')
        assert data.name == 'second'
