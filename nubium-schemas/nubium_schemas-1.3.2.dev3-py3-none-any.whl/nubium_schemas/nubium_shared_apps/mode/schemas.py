
bulk_data_chunk = {
  "name": "BulkDataChunk",
  "type": "array",
  "items": {
    "type": "map",
    "values": "string"},
  "default": []
}

bulk_data_record = {
  "name": "BulkDataRecord",
  "type": "record",
  "fields": [
    {"name": "record", "type": {"type": "map", "values": "string"}, "default": {}}
  ]
}