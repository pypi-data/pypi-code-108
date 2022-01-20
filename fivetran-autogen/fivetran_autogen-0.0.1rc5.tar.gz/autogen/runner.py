from autogen.client import FivetranClient


class Runner:
    def __init__(self, api_key, api_secret):
        self.client = FivetranClient(api_key, api_secret)

    def get_groups(self):
        all_groups = self.client.get_all_groups()
        groups = {}
        for group in all_groups["data"]["items"]:
            groups[group["name"]] = group["id"]
        return groups

    def get_connector_types(self, group_id):
        all_connectors = self.client.get_all_connectors_in_group(group_id)
        services = set()
        for connector in all_connectors["data"]["items"]:
            services.add(connector["service"])
        return list(services)

    def get_connectors(self, group_id, connector_type):
        all_connectors = self.client.get_all_connectors_in_group(group_id)
        connectors = {}
        for connector in all_connectors["data"]["items"]:
            if connector["service"] == connector_type:
                connectors[connector["schema"]] = connector["id"]
        return connectors
