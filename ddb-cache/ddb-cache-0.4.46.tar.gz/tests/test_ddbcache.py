# StdLib
import os
from random import randint
from time import sleep

from boto3.dynamodb import types
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from ddbcache import DDBCache
from moto import mock_dynamodb2
import pytest


@pytest.fixture()
def aws_credentials():  # noqa: PT004
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture()
def ddb_cache(aws_credentials):
    with mock_dynamodb2():
        cache = DDBCache(
            table_name="Testing",
            access_key=os.environ["AWS_ACCESS_KEY_ID"],
            secret_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region="us-east-1",
        )
        key_schema = [
            {
                "AttributeName": "id",
                "KeyType": "HASH",
            },
        ]
        attr_schema = [
            {
                "AttributeName": "id",
                "AttributeType": types.STRING,
            },
        ]
        create_kwargs = {
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1,
            },
        }
        cache.create_table(key_schema, attr_schema, **create_kwargs)
        yield cache


@pytest.fixture()
def init_get(ddb_cache: DDBCache):  # noqa: PT004
    ddb_cache.put_item({"id": "test_get", "data": "test_get"})


@pytest.fixture()
def init_delete(ddb_cache: DDBCache):  # noqa: PT004
    ddb_cache.put_item({"id": "test_delete", "data": "test_delete"})


@pytest.fixture()
def init_update(ddb_cache: DDBCache):  # noqa: PT004
    ddb_cache.put_item({"id": "test_update", "data": "test_update"})


@pytest.fixture()
def init_fetch_cache(ddb_cache: DDBCache):  # noqa: PT004
    ddb_cache.put_cache({"id": "test_fetch_cache", "data": "test_fetch_cache"})


def test_client_error(ddb_cache: DDBCache):
    data = randint(1, 100)  # noqa: S311
    with pytest.raises(ClientError) as err:
        ddb_cache.put_item({"not-id": data, "data": data})
    assert err.value.response["Error"]["Code"] == "ValidationException"
    assert "Missing the key id" in err.value.response["Error"]["Message"]


def test_put(ddb_cache: DDBCache):
    data = randint(1, 100)  # noqa: S311
    ddb_cache.put_item({"id": "test_put", "data": data})
    item = ddb_cache.get_item({"id": "test_put"})
    assert item
    assert item["id"] == "test_put"
    assert item["data"] == data


def test_put_cache(ddb_cache: DDBCache):
    data = randint(1, 100)  # noqa: S311
    ddb_cache.put_cache({"id": "test_put_cache", "data": data})
    item = ddb_cache.get_item({"id": "test_put_cache"})
    assert item
    assert item["id"] == "test_put_cache"
    assert item["data"] == data
    assert item["ttl"]


def test_put_cache_no_ttl(ddb_cache: DDBCache):
    data = randint(1, 100)  # noqa: S311
    ddb_cache.put_cache({"id": "test_put_cache", "data": data}, with_ttl=False)
    item = ddb_cache.get_item({"id": "test_put_cache"})
    assert item
    assert item["id"] == "test_put_cache"
    assert item["data"] == data
    with pytest.raises(KeyError):
        item["ttl"]


def test_fetch_cache(ddb_cache: DDBCache, init_fetch_cache):
    item = ddb_cache.get_item({"id": "test_fetch_cache"})
    assert item
    assert item["id"] == "test_fetch_cache"
    assert item["data"] == "test_fetch_cache"
    ttl = item["ttl"]
    assert ttl
    sleep(1)
    item = ddb_cache.fetch_cache({"id": "test_fetch_cache"})
    assert item
    assert item["id"] == "test_fetch_cache"
    assert item["data"] == "test_fetch_cache"
    with pytest.raises(KeyError):
        item["ttl"]
    item = ddb_cache.get_item({"id": "test_fetch_cache"})
    assert item
    assert item["id"] == "test_fetch_cache"
    assert item["data"] == "test_fetch_cache"
    ttl2 = item["ttl"]
    assert ttl2
    assert ttl != ttl2


def test_fetch_cache_no_ttl_update(ddb_cache: DDBCache, init_fetch_cache):
    item = ddb_cache.get_item({"id": "test_fetch_cache"})
    assert item
    assert item["id"] == "test_fetch_cache"
    assert item["data"] == "test_fetch_cache"
    ttl = item["ttl"]
    assert ttl
    item = ddb_cache.fetch_cache({"id": "test_fetch_cache"}, with_ttl=False)
    assert item
    assert item["id"] == "test_fetch_cache"
    assert item["data"] == "test_fetch_cache"
    with pytest.raises(KeyError):
        item["ttl"]
    item = ddb_cache.get_item({"id": "test_fetch_cache"})
    assert item
    assert item["id"] == "test_fetch_cache"
    assert item["data"] == "test_fetch_cache"
    ttl2 = item["ttl"]
    assert ttl2
    assert ttl == ttl2


def test_get(ddb_cache: DDBCache, init_get):
    item = ddb_cache.get_item({"id": "test_get"})
    assert item
    assert item["id"] == "test_get"
    assert item["data"] == "test_get"


def test_delete(ddb_cache: DDBCache, init_delete):
    item = ddb_cache.get_item({"id": "test_delete"})
    assert item
    assert item["id"] == "test_delete"
    assert item["data"] == "test_delete"
    ddb_cache.delete_item({"id": "test_delete"})
    item = ddb_cache.get_item({"id": "test_delete"})
    assert not item


def test_update(ddb_cache: DDBCache, init_update):
    data = randint(1, 100)  # noqa: S311
    item = ddb_cache.get_item({"id": "test_update"})
    assert item
    assert item["id"] == "test_update"
    assert item["data"] == "test_update"
    ddb_cache.update_item({"id": "test_update"}, {"id": "test_update", "data": data})
    item = ddb_cache.get_item({"id": "test_update"})
    assert item
    assert item["id"] == "test_update"
    assert item["data"] == data


def test_delete_update(ddb_cache: DDBCache, init_update):
    data = randint(101, 200)  # noqa: S311
    item = ddb_cache.get_item({"id": "test_update"})
    assert item
    assert item["id"] == "test_update"
    assert item["data"] == "test_update"
    ddb_cache.del_update_item({"id": "test_update"}, {"id": "test_update", "data": data})
    item = ddb_cache.get_item({"id": "test_update"})
    assert item
    assert item["id"] == "test_update"
    assert item["data"] == data


def test_scan(ddb_cache: DDBCache, init_get, init_delete, init_update):
    items = ddb_cache.scan_items()
    assert len(items) >= 1


def test_query(ddb_cache: DDBCache, init_get, init_update, init_delete):
    items = ddb_cache.query_items({"KeyConditionExpression": Key("id").eq("test_get")})
    assert len(items) == 1
    items = ddb_cache.query_items({"KeyConditionExpression": Key("id").eq("test_update")})
    assert len(items) == 1
    items = ddb_cache.query_items({"KeyConditionExpression": Key("id").eq("test_delete")})
    assert len(items) == 1


def test_cache_floats(ddb_cache: DDBCache):
    data = float(2 / 3)
    input = {"id": "test_cache_floats", "data": data}
    print(input)
    ddb_cache.put_cache(input, with_ttl=False)
    item = ddb_cache.fetch_cache({"id": "test_cache_floats"})
    assert item
    assert item["id"] == "test_cache_floats"
    assert str(item["data"]) == str(data)
    assert type(item["data"]) is float
    item = ddb_cache.get_item({"id": "test_cache_floats"})
    assert item
    assert item["id"] == "test_cache_floats"
    assert str(item["data"]) == str(data)


def test_cache_floats_in_list(ddb_cache: DDBCache):
    data = float(2 / 3)
    ddb_cache.put_cache({"id": "test_cache_floats_in_list", "data": [data]}, with_ttl=False)
    item = ddb_cache.fetch_cache({"id": "test_cache_floats_in_list"})
    assert item
    assert item["id"] == "test_cache_floats_in_list"
    assert str(item["data"][0]) == str(data)
    assert type(item["data"][0]) is float
    item = ddb_cache.get_item({"id": "test_cache_floats_in_list"})
    assert item
    assert item["id"] == "test_cache_floats_in_list"
    assert str(item["data"][0]) == str(data)


def test_cache_floats_in_dict(ddb_cache: DDBCache):
    data = float(2 / 3)
    ddb_cache.put_cache({"id": "test_put_cache", "data": {"node": data}}, with_ttl=False)
    item = ddb_cache.fetch_cache({"id": "test_put_cache"})
    assert item
    assert item["id"] == "test_put_cache"
    assert str(item["data"]["node"]) == str(data)
    assert type(item["data"]["node"]) is float
    item = ddb_cache.get_item({"id": "test_put_cache"})
    assert item
    assert item["id"] == "test_put_cache"
    assert str(item["data"]["node"]) == str(data)


def test_cache_floats_in_tuples(ddb_cache: DDBCache):
    data = float(2 / 3)
    ddb_cache.put_cache({"id": "test_cache_floats_in_tuples", "data": ("val", data)}, with_ttl=False)
    item = ddb_cache.get_item({"id": "test_cache_floats_in_tuples"})
    assert item
    assert item["id"] == "test_cache_floats_in_tuples"
    assert str(item["data"][1]) == str(data)
    item = ddb_cache.fetch_cache({"id": "test_cache_floats_in_tuples"})
    assert item
    assert item["id"] == "test_cache_floats_in_tuples"
    assert str(item["data"][1]) == str(data)
    assert type(item["data"][1]) is float
