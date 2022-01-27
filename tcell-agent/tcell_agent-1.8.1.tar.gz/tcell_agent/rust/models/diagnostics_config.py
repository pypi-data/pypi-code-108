class DiagnosticsConfig(dict):
    def __init__(self, config):
        dict.__init__(self)
        self['config_filename'] = config.config_filename
        self['demomode'] = config.demomode
        self['enabled'] = config.enabled
        self['enabled_instrumentations'] = config.enabled_instrumentations
        self['max_data_ex_db_records_per_request'] = config.max_data_ex_db_records_per_request
        self['preload_policy_filename'] = config.preload_policy_filename
        self['reverse_proxy'] = config.reverse_proxy
        self['tcell_home'] = config.tcell_home

    def to_properties(self):
        properties = []
        for key, value in self.items():
            properties.append({'name': key, 'value': str(value)})
        return properties
