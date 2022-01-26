import json
import time

import pytest
import requests

from exoedge.data_queuing import DB, Queuing
from murano_client.client import MuranoClient


@pytest.fixture
def device():
    device = MuranoClient(**{'murano_host': 'https://xyu7kqqdgf0w0000.m2.exosite.io',
                             'murano_id': 'demo',
                             'murano_token': '012b8f2357699d37a723ce0ff2a1d6d75e615f6f',
                             'watchlist': ['data_in'],
                             'murano_port': 443,
                             'memory_queue': False
                             }
                          )
    device.start_client()
    return device


@pytest.fixture
def queuing(device, mocker):
    device.outbound_protocol = 'https'
    queuing = Queuing('https://xyu7kqqdgf0w0000.m2.exosite.io/',
                      'j1939', device)
    return queuing


def test_Retention_by_real_device(queuing, device):
    data = json.dumps({'test': time.time()})
    queuing.tell('data_in', time.time(), data)
    res = device.http_read(['data_in'])
    assert res.body == 'data_in={}'.format(data)


def test_consume_table(mocker, device):
    device.outbound_protocol = 'https'
    mocker.patch.object(DB, 'read_table', return_value=[])
    queuing = Queuing(
        'https://xyu7kqqdgf0w0000.m2.exosite.io/', 'j1939', device)
    # can break loop when table is empty
    queuing.enable_dequeue()
    queuing.db.read_table.assert_called_once_with(amount=0, auto=True)
    assert queuing.dequeue_enabled == False

    # Should call https when table has data
    mocker.patch.object(queuing, 'https')
    mocker.patch.object(DB, 'read_table', return_value=[{}])
    queuing.enable_dequeue()
    queuing.https.assert_called_once_with([{}])


def test_product_id(queuing):
    assert queuing.product_id(
        'mqtt://xyu7kqqdgf0w0000.m2.exosite.io/') == 'xyu7kqqdgf0w0000'
    assert queuing.product_id(
        'https://xyu7kqqdgf0w0000.m2.exosite.io/') == 'xyu7kqqdgf0w0000'
    assert queuing.product_id('https://abc.m2.exosite.io') == 'abc'
    with pytest.raises(AttributeError):
        queuing.product_id('abc')


@pytest.mark.parametrize('protocol', ['https', 'mqtt'])
def test_tell(mocker, protocol, device):
    timestamp = time.time()
    data = json.dumps({'test': timestamp})
    device.outbound_protocol = protocol
    queuing = Queuing(protocol+'://xyu7kqqdgf0w0000.m2.exosite.io/',
                      'j1939', device)
    # test table is empty
    queuing.is_table_empty = True
    mocker.patch.object(device, 'tell', return_value=(True, ''))
    queuing.tell(resource='data_in', timestamp=timestamp, payload=data)
    device.tell.assert_called_once_with(payload=data, resource='data_in', timestamp=timestamp)

    # test table is empty and https/mqtt sent data fail
    queuing.is_table_empty = True
    mocker.patch.object(device, 'tell', return_value=(False, ''))
    mocker.patch.object(queuing.db, 'insert_record')
    queuing.tell('data_in', timestamp, data)
    queuing.db.insert_record.assert_called_once_with(timestamp, data)

    # test table is not empty
    queuing.is_table_empty = False
    mocker.patch.object(queuing.db, 'insert_record')
    queuing.tell('data_in', timestamp, data)
    queuing.db.insert_record.assert_called_once_with(timestamp, data)


class TestBD():
    @pytest.fixture
    def db(self, mocker):
        return DB('/tmp', 'queue.producid.deviceid', '5000000', 'oldest')

    def test_limit_data_size(self, mocker, db):
        # auto=True
        mocker.patch.object(db.table, 'read', return_value=[
                            (1, 1559628846.9537978, '1234567890')])
        res = db.limit_data_size(auto=True)
        # Single record is 10 byte (1234567890), '1559628846.9537978%3D1234567890%26' length is 34
        # 64000/34 = 1882.3529411764705
        assert len(res) == 1882

        # auto=False, amount = 100
        mocker.patch.object(db.table, 'read', return_value=[
                            (1, 1559628846.9537978, '1234567890') for i in range(100)])
        res = db.limit_data_size(auto=False, amount=100)
        assert len(res) == 100

        # auto=False, amount = 9999
        mocker.patch.object(db.table, 'read', return_value=[
                            (1, 1559628846.9537978, '1234567890') for i in range(9999)])
        res = db.limit_data_size(auto=False, amount=9999)
        assert len(res) == 1882


    def test_the_oldest_record_table(self, mocker, db):
        mocker.patch.object(db.table,
                            'all_table_name',
                            return_value=['queue.abcdcdkk2ls00000.device',
                                          'queue.abcdcdkk2ls00000.device2',
                                          'queue.abcdcdkk2ls00000.device3',
                                          'queue.abcdcdkk2ls00000.device4'])
        mocker.patch.object(db.table, 'query_db',
                            side_effect=[9999999, 666, 2, 1])
        res = db.table.the_oldest_record_table()
        assert res == ('queue.abcdcdkk2ls00000.device4', 1)

    def test_drop_oldest_10mins_record_and_data_in_last_10_mins(self, mocker, db):
        mocker.patch.object(db.table, 'the_oldest_record_table',
                            return_value=('queue.abcdcdkk2ls00000.device4', time.time()))
        res = db.table.drop_oldest_records()
        assert res == False

    def test_delete_unused_table(self, mocker, db):
        mocker.patch.object(db.table, 'all_table_name',
                            return_value=['queue.abcdcdkk2ls00000.device',
                                          'queue.abcdcdkk2ls00000.device2',
                                          'queue.abcdcdkk2ls00000.device3',
                                          'queue.abcdcdkk2ls00000.device4'])
        mocker.patch.object(db.table, 'delete_table', return_value=[])
        res = db.delete_unused_table()
        assert res == True
