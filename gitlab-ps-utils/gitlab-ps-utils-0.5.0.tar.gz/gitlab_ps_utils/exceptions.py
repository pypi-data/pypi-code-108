class ConfigurationException(Exception):
    def __init__(self, failed_config, msg=None):
        Exception.__init__(self, f"Incorrect configuration found in {failed_config} (Response - {msg})")
