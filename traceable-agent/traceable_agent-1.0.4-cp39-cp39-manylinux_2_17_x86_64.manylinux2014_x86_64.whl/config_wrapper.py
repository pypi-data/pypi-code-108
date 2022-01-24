
class ConfigWrapper: # pylint:disable=R0903
    def __init__(self, ht_config, ta_config):
        self.observability = ht_config
        self.traceable = ta_config
