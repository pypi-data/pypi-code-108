from enum import Enum
from serialclass import SerialClass

class ConfigKeys(str, Enum):
    attributes = "attributes"

class ConfigAttributeKeys(str, Enum):
    name = "name"
    type = "type"
    min = "min"
    max = "max"
    default = "default"

class ConfigValidation:
    def _key_validation(valid_dict, keys):
        required_keys = list(keys)
        for req_key in required_keys:
            if req_key.value not in valid_dict:
                raise RuntimeError(f"Invalid object missing key ({req_key}): {valid_dict}")
    def attribute(func):
        """Validate the arguments to construct a ConfigAttribute"""
        def wrap(*args, **kwargs):
            attr_dict = args[1]
            ConfigValidation._key_validation(attr_dict, ConfigAttributeKeys)
            return func(*args, **kwargs)
        return wrap
    
    def config(func):
        """Validate the arguments to construct a Config"""
        def wrap(*args, **kwargs):
            cfg_dict = args[1]
            ConfigValidation._key_validation(cfg_dict, ConfigKeys)
            return func(*args, **kwargs)
        return wrap

class ConfigAttribute(SerialClass):

    @ConfigValidation.attribute
    def __init__(self, attr_dict: dict):
        self.name = attr_dict[ConfigAttributeKeys.name]
        self.type = attr_dict[ConfigAttributeKeys.type]
        self.min = attr_dict[ConfigAttributeKeys.min]
        self.max = attr_dict[ConfigAttributeKeys.max]
        self.default = attr_dict[ConfigAttributeKeys.default]

class Config(SerialClass):

    schema = {
        ConfigKeys.attributes: [
            {
                ConfigAttributeKeys.name: None,
                ConfigAttributeKeys.type: None,
                ConfigAttributeKeys.min: None,
                ConfigAttributeKeys.max: None,
                ConfigAttributeKeys.default: None,
            },
        ]
    }

    @ConfigValidation.config
    def __init__(self, cfg_dict: dict):
        self._attr_dicts = cfg_dict[ConfigKeys.attributes]
        self.attrs = [ConfigAttribute(attr_dict) for attr_dict in self._attr_dicts]
