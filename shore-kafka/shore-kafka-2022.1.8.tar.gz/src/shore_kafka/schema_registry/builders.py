from typing import List, Union

from genson import SchemaBuilder


def build_json_schema_from_records(
    records: Union[List[dict], dict],
    required: str = "any",
    extend: dict = None,
) -> dict:
    """Build json schema from sample records.

    Args:
        records (Union[List[dict], dict]): [{"field_a": 10.0, "field_b": 0, "field_c": "something", ...}, ]
        required (str, optional): list of required fields, "any", or "all". Defaults to "any".
        extend (dict, optional): schema will be extended from <extend> schema dictionary. Defaults to None.

    Returns:
        dict: dict form of json schema.
    """

    # for confluent
    DEFAULT_SCHEMA_URI = "http://json-schema.org/draft-07/schema#"

    # create schema builder
    if extend:
        builder = SchemaBuilder()
        builder.add_schema(extend)
    else:
        builder = SchemaBuilder(schema_uri=DEFAULT_SCHEMA_URI)

    # add sample record to infer schema
    records = records if isinstance(records, list) else [records]
    [builder.add_object(record) for record in records]

    # overwrite required
    assert isinstance(required, list) or required in [
        "all",
        "any",
    ], "wrong param for required!"
    if required == "all":
        required = list({k for record in records for k in record.keys()})
    if required == "any":
        required = []
    builder.add_schema({"required": required})

    # log if required is changed
    if extend is not None:
        parent_required = extend.get("required", []) if extend else []
        added = [_ for _ in required if _ not in parent_required]
        removed = [_ for _ in parent_required if _ not in required]
        if len(added) > 0:
            print(f"Added required fields: {', '.join(added)}")
        if len(removed) > 0:
            print(f"Removed required fields: {', '.join(removed)}")

    return builder.to_schema()
