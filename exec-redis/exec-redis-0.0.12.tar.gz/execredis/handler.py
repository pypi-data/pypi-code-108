from json import dumps, loads


class ExecMappingData:
    def __init__(self, proj_name, redis_app):
        self.proj_name = proj_name
        self.redis_app = redis_app

    def hget(self, name: str, default_value):
        return loads(self.redis_app.hget(
            f"{self.proj_name}." + 'MappingData', key=name.lower()) or b'null') or default_value


class ExecMappingAction:
    def __init__(self, mapping_data, proj_name, redis_app, logger_func=print):
        self.mapping_data = mapping_data
        self.proj_name = proj_name
        self.logger = logger_func
        self.redis_app = redis_app

    def setup_mapping_data(self, mapping_data_default, value=None):
        default_value = mapping_data_default
        mapping_data = self.mapping_data.__dict__
        name = list(mapping_data.keys())[list(mapping_data.values()).index(default_value)]
        if not value:
            mapping_value = default_value
        else:
            if not isinstance(value, type(default_value)):
                raise ValueError(f'Value: {value} type not match default.')
            mapping_value = value
        self.__setup_mapping_data(name, mapping_value)

    def setup_all_mapping_data(self, support_types=(list, int, dict, str)):
        self.logger(f'Will set all MappingData with default value on Redis.')
        for k, v in self.mapping_data.__dict__.items():
            if "__" not in k and isinstance(v, support_types):
                self.__setup_mapping_data(k, v)

    def __setup_mapping_data(self, name: str, value):
        self.logger(f"Setup MappingData.{name}: {self.__hset_mapping_data(name.lower(), dumps(value))}")

    def __hset_mapping_data(self, key=None, value=None, mapping=None):
        return self.redis_app.hset(f"{self.proj_name}." + 'MappingData', key=key, value=value, mapping=mapping)
