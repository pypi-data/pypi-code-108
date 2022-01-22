# form of consumer configuration
# (detail) https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
# (NOTE)
#  - For referenced schema (n event types per topic), Producer Conf Only,
#   . auto.register.schemas = False for
#   . use.latest.version = True for "referenced schema ~ n event types per topic"
PRODUCER_CONF = {
    "bootstrap.servers": None,
    "client.id": None,
    "key.serializer": None,
    "value.serializer": None,
    "acks": -1,  # alias for request.required.acks
    "message.timeout.ms": 300000,
    "delivery.timeout.ms": 300000,
    "auto.register.schemas": False,
    "use.latest.version": True,
    "error_cb": None,
    "log_cb": None,
    "stats_cb": None,
    "throttle_cb": None,
}

CONSUMER_CONF = {
    "bootstrap.servers": None,
    "group.id": None,
    "client.id": None,
    "key.deserializer": None,
    "value.deserializer": None,
    "enable.auto.commit": True,
    "auto.offset.reset": "earliest",
    "error_cb": None,
    "log_cb": None,
    "stats_cb": None,
    "throttle_cb": None,
}

# Multiple Event Types in the Same Topic
# https://docs.confluent.io/platform/current/schema-registry/serdes-develop/serdes-json.html#referenced-schemas-json
REFERENCED_SCHEMA_JSON = {
    "oneOf": [{"$ref": "VilageFcstModel.schema.json"}, {"$ref": "UltraSrtNcstModel.schema.json"}]
}
