import typing

from nubium_schemas import dc, pdc, AvroModel

ebb_job_init_fields = {
    "name": "EbbJobInitFields",
    "type": "record",
    "fields": [
        {"name": "eloqua_source_name", "type": "string", "default": ""},
        {"name": "eloqua_fields_out", "type": "string", "default": ""},
        {"name": "eloqua_field_filters", "type": "string", "default": ""},
        {"name": "from_timestamp", "type": "string", "default": ""},
        {"name": "to_timestamp", "type": "string", "default": ""},
        {"name": "nubium_created_by_app_name", "type": "string", "default": ""},
        {"name": "nubium_bulk_output_topic", "type": "string", "default": ""},
        {"name": "nubium_rest_timestamp_topic", "type": "string", "default": ""}
    ]
}

ebb_job_eloqua_metadata = {
    "name": "EbbJobEloquaMetadata",
    "type": "record",
    "fields": [
        {"name": "bulk_export_definition", "type": "string", "default": ""},
        {"name": "bulk_sync_uri", "type": "string", "default": ""},
        {"name": "bulk_total_records", "type": "string", "default": ""}
    ]
}

ebb_worker_task_fields = {
    "name": "EbbWorkerTaskFields",
    "type": "record",
    "fields": [
        {"name": "task_command", "type": "string", "default": ""},
        {"name": "task_attempt", "type": "string", "default": ""},
        {"name": "bulk_offset", "type": "string", "default": ""},
        {"name": "bulk_batch_size", "type": "string", "default": ""}
    ]
}

eloqua_cdo_record = {
    "name": "EloquaCdoRecord",
    "type": "record",
    "fields": [
        {"name": "cdo_id", "type": "string", "default": ""},
        {"name": "cdo_record_id", "type": "string", "default": ""},
        {"name": "field_map", "type": {"type": "map", "values": "string"}, "default": {}}
    ]
}

eloqua_cdo_record_unique_field = {
    "name": "EloquaCdoRecordUniqueField",
    "type": "record",
    "fields": [
        {"name": "cdo_unique_field", "type": "string", "default": ""},
        {"name": "record_unique_field_value", "type": "string", "default": ""}
    ]
}


@pdc
class EloquaContactRecord(AvroModel):
    class Meta:
        schema_doc = False

    contact_id: str = ""
    field_map: typing.Dict[str, str] = dc.field(default_factory=dict)
