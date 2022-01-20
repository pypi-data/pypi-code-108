from nautilus_trader.model.events.account import AccountState

from nacre.serialization.avro.patch_registry import schema


NAUTILUS_AVRO_SCHEMA = {
    AccountState: schema.AvroSchema(
        {
            "type": "record",
            "name": "AccountState",
            "namespace": "nautilus_trader.model.events",
            "fields": [
                {"name": "account_id", "type": "string"},
                {"name": "account_type", "type": "string"},
                {"name": "base_currency", "type": ["string", "null"], "default": "null"},
                {"name": "balances", "type": "string"},
                {"name": "positions", "type": "string"},
                {"name": "reported", "type": "boolean"},
                {"name": "event_id", "type": "string"},
                {"name": "ts_event", "type": "long"},
                {"name": "ts_init", "type": "long"},
                {"name": "equity", "type": "float"},
            ],
        }
    ),
}
