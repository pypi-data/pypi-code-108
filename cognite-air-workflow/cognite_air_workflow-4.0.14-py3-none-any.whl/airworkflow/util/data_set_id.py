from cognite.experimental import CogniteClient


def data_set_id(client: CogniteClient, name: str) -> int:
    data_sets = client.data_sets.list(limit=-1).dump()
    for ds in data_sets:
        if ("archived" not in ds["metadata"] or ds["metadata"]["archived"] != "true") and ds["name"] == name:
            return ds["id"]
    raise LookupError(f"Not able to find dataset named {name}")
