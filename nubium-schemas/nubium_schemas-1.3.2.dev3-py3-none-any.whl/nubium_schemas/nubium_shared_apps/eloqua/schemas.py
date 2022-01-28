from nubium_schemas.nubium_integrations.eloqua import (
    eloqua_cdo_record_data,
    eloqua_cdo_record_update_data,
    eloqua_contact_record_data)

eloqua_retriever_timestamp = {
    "name": "EloquaRetrieverTimestamp",
    "type": "record",
    "fields": [
        {"name": "timestamp", "type": "string", "default": ""}
    ]
}
