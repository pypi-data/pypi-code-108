import time
import typing

from botocore.client import BaseClient

from dynamo_io import definitions
from dynamo_io import recorder


def insert_records(
    client: BaseClient,
    table_name: str,
    records: typing.Iterable["recorder.Record"],
) -> "definitions.Response":
    """
    Batch inserts records into the specified table. This method does
    not support upserting. It will only function if the records are
    being created. The method will retry up to 10 times to ensure that
    the records are inserted. However, if after 10 attempts, with
    exponential backoff, the insertion fails for 1 or more of the
    records the function will fail with a False return value. If it
    succeeds the function will return True.

    :param client:
        Boto client used to insert the records.
    :param table_name:
        Name of the table to insert the records into.
    :param records:
        A list of Record objects to insert into the specified table.
        These records will be converted to DynamoDB row format prior
        to the insert call.
    """
    initial_unprocessed_items = {
        table_name: [{"PutRequest": {"Item": r.to_row()}} for r in records]
    }
    unprocessed_items = initial_unprocessed_items

    for i in range(10):
        time.sleep(i * 0.5)
        response = client.batch_write_item(RequestItems=unprocessed_items)
        unprocessed_items = response.get("UnprocessedItems") or {}
        if not unprocessed_items:
            return definitions.Response(
                response=response,
                request=initial_unprocessed_items,
            )

    raise RuntimeError("Failed to insert all records.")


def upsert(
    client: BaseClient,
    table_name: str,
    record: "recorder.Record",
) -> "recorder.SingleRecordResponse":
    """
    Upserts the specified record to DynamoDB.

    :param client:
        Boto client that will be used to upsert the record into the table.
    :param table_name:
        Name of the table that will be written to.
    :param record:
        A Record object configured for writing to the specified table.
    """
    request = {
        "TableName": table_name,
        "Key": record.table_key,
        "ExpressionAttributeNames": record.to_attribute_names(),
        "ExpressionAttributeValues": record.to_attribute_values(),
        "UpdateExpression": record.to_update_expression(),
        "ReturnValues": "ALL_NEW",
    }
    response = client.update_item(**request)

    return recorder.SingleRecordResponse(
        response=response,
        request=request,
        row=response["Attributes"],
        record=record.from_row(response["Attributes"]),
    )


def remove(
    client: BaseClient,
    table_name: str,
    record: "recorder.Record",
) -> "definitions.Response":
    """..."""
    request = {"TableName": table_name, "Key": record.table_key}
    response = client.delete_item(**request)
    return definitions.Response(
        response=response,
        request=request,
    )


def transacts(
    client: BaseClient,
    table_name: str,
    puts: typing.Iterable["recorder.Record"] = None,
    updates: typing.Iterable["recorder.Record"] = None,
    deletes: typing.Iterable["recorder.Record"] = None,
) -> "definitions.Response":
    """..."""
    put_items = [
        {
            "Put": dict(
                TableName=table_name,
                Item=record.to_row(),
            )
        }
        for record in (puts or [])
    ]

    update_items = [
        {
            "Update": dict(
                TableName=table_name,
                Key=record.table_key,
                ExpressionAttributeNames=record.to_attribute_names(),
                ExpressionAttributeValues=record.to_attribute_values(),
                UpdateExpression=record.to_update_expression(),
            )
        }
        for record in (updates or [])
    ]

    delete_items = [
        {
            "Delete": dict(
                TableName=table_name,
                Key=record.table_key,
            )
        }
        for record in (deletes or [])
    ]

    request = {
        "TransactItems": [
            *put_items,
            *update_items,
            *delete_items,
        ]
    }
    response = client.transact_write_items(**request)

    return definitions.Response(
        response=response,
        request=request,
    )
