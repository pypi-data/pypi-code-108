class WebappSettings:
    def __init__(self,
                 resource_group: str,
                 webapp_name: str,
                 setting_key: str,
                 setting_value: str):
        self.resource_group = resource_group
        self.webapp_name = webapp_name
        self.setting_key = setting_key
        self.setting_value = setting_value
