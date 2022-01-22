from .config_group import ConfigGroup


class Configger(object):
    """
    Wrapped ApolloClient with specific namespace

    :param client: ApolloClient, pyapollo client
    :param namespace: str, config namespace
    """
    def __init__(self, client, namespace):
        self.client = client
        self.namespace = namespace

    def get_value(self, key):
        """
        Get value from Apollo by key

        :param key: str, config key
        :return: str, config value
        """
        return self.client.get_value(key, namespace=self.namespace)

    def get_group(self, group):
        """
        Get ConfigGroup by prefix and namespace

        :param group: str, config common prefix
        :return: ConfigGroup
        """
        return ConfigGroup(self.client, self.namespace, group)
