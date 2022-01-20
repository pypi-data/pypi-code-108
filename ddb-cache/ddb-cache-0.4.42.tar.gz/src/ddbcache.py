# StdLib
from datetime import datetime
from decimal import Decimal
import json
from time import time
from typing import Any, Union

import boto3
from botocore.exceptions import ClientError
from helpers import Logger, NormalSleeper, RetryHandler

LOGGER = Logger()
SLEEPER = NormalSleeper()


def _client_error(error_obj):
    err_msg = str(error_obj)
    if "ProvisionedThroughputExceededException" not in err_msg:
        raise error_obj
    else:
        LOGGER.print_error(err_msg)
        SLEEPER.sleep(10)


class DDBCache:
    TTL_DAYS = 30

    def __init__(self, table_name, access_key, secret_key, region):
        self.table_name = table_name
        self._setup_session(access_key, secret_key, region)

    def _setup_session(self, access_key, secret_key, region):
        _session_config = {
            "region_name": region,
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
        }
        _service_config = {
            "service_name": "dynamodb",
        }
        self._SESSION = boto3.Session(**_session_config)
        self._DDB = self._SESSION.resource(**_service_config)
        self._DDB_CLIENT = self._SESSION.client(**_service_config)

    @RetryHandler(
        (ClientError),
        max_retries=10,
        wait_time=0,
        err_callbacks={"ClientError": (_client_error, {})},
    ).wrap
    def create_table(
        self,
        key_schema: list[dict[str, Any]] = [],
        attr_schema: list[dict[str, Any]] = [],
        **create_kwargs,
    ):
        try:
            tbl = self._DDB.Table(self.table_name)
            tbl.reload()
            self.TABLE = tbl
        except:  # noqa
            print("Table does not exist. Creating...")
            tbl = self._DDB.create_table(
                TableName=self.table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attr_schema,
                **create_kwargs,
            )
            self.TABLE = tbl

    def create_backup(self):
        response = self._DDB_CLIENT.create_backup(
            TableName=self.table_name,
            BackupName=datetime.now().isoformat().replace(":", "_"),
        )
        print(f"Backup: {response}")

    @RetryHandler(
        (ClientError),
        max_retries=10,
        wait_time=0,
        err_callbacks={"ClientError": (_client_error, {})},
    ).wrap
    def put_item(self, data: dict[str, Any]):
        response = self.TABLE.put_item(Item=data)
        return response

    @RetryHandler(
        (ClientError),
        max_retries=10,
        wait_time=0,
        err_callbacks={"ClientError": (_client_error, {})},
    ).wrap
    def get_item(self, key: dict[str, Any]) -> dict[str, Any]:
        response = self.TABLE.get_item(Key=key)
        return response.get("Item", None)

    @RetryHandler(
        (ClientError),
        max_retries=10,
        wait_time=0,
        err_callbacks={"ClientError": (_client_error, {})},
    ).wrap
    def delete_item(self, key: dict[str, Any]):
        response = self.TABLE.delete_item(Key=key)
        return response

    def del_update_item(self, key: dict[str, Any], data: dict[str, Any]):
        self.delete_item(key)
        return self.put_item(data)

    @RetryHandler(
        (ClientError),
        max_retries=10,
        wait_time=0,
        err_callbacks={"ClientError": (_client_error, {})},
    ).wrap
    def update_item(self, key_dict: dict[str, Any], data_dict: dict[str, Any]):

        data_formatted = {key: {"Value": value, "Action": "PUT"} for (key, value) in data_dict.items()}
        for k in key_dict.keys():
            del data_formatted[k]

        response = self.TABLE.update_item(
            Key=key_dict,
            AttributeUpdates=data_formatted,
            ReturnValues="ALL_NEW",
        )
        return response

    @RetryHandler(
        (ClientError),
        max_retries=10,
        wait_time=0,
        err_callbacks={"ClientError": (_client_error, {})},
    ).wrap
    def scan_items(self) -> list[dict[str, Any]]:
        scan_kwargs: dict[str, Any] = {
            "Select": "ALL_ATTRIBUTES",
        }
        done = False
        start_key = None

        items: list = []

        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = self.TABLE.scan(**scan_kwargs)
            for item in response.get("Items", []):
                items.append(item)
            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

        return items

    @RetryHandler(
        (ClientError),
        max_retries=10,
        wait_time=0,
        err_callbacks={"ClientError": (_client_error, {})},
    ).wrap
    def query_items(self, query_conditions) -> list[dict[str, Any]]:
        response = self.TABLE.query(**query_conditions)
        return response["Items"]

    @RetryHandler(
        (ClientError),
        max_retries=10,
        wait_time=0,
        err_callbacks={"ClientError": (_client_error, {})},
    ).wrap
    def fetch_cache(self, key: dict[str, Any], with_ttl: bool = True) -> dict[str, Any]:
        cache = self.get_item(key)
        if cache and isinstance(cache, dict):
            if with_ttl:
                cache["ttl"] = self._get_item_ttl()
                self.update_item(key, cache)
            if cache.get("ttl", None):
                del cache["ttl"]
            return _decimal_to_float(cache)
        else:
            return {}

    @RetryHandler(
        (ClientError),
        max_retries=10,
        wait_time=0,
        err_callbacks={"ClientError": (_client_error, {})},
    ).wrap
    def put_cache(self, cache: dict[str, Any], with_ttl=True):
        cache_for_db = _float_to_decimal(cache)
        if with_ttl:
            cache_for_db["ttl"] = self._get_item_ttl()
        self.put_item(data=cache_for_db)
        if with_ttl and cache_for_db.get("ttl", None):
            del cache_for_db["ttl"]

    def _get_item_ttl(self):
        return int(time()) + int(60 * 60 * 24 * self.TTL_DAYS)


def _float_to_decimal(obj: Any):
    if not obj or type(obj) not in [dict, list]:
        return obj
    else:
        return json.loads(json.dumps(obj), parse_float=Decimal)


def _decimal_to_float(obj: Any):
    if not obj:
        return obj
    if type(obj) is Decimal:
        return float(obj)
    if type(obj) is dict:
        return {k: _decimal_to_float(v) for k, v in obj.items()}
    if type(obj) is list:
        return [_decimal_to_float(o) for o in obj]
    return obj
