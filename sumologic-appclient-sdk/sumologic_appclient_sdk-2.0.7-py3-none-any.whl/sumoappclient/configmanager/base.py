# -*- coding: future_fstrings -*-
import os
import re
from abc import ABCMeta, abstractmethod
import six
from sumoappclient.common.errors import InValidConfigException
from sumoappclient.common.logger import get_logger
from sumoappclient.common.utils import convert_if_digit, merge_dict, read_yaml_file


@six.add_metaclass(ABCMeta)
class BaseConfigHandler(object):
    SUMO_CONFIG_FOLDER = "sumo"

    # This class will have the private methods.
    # In order to fetch the config for a specific env, call the generate_user_config method.
    # this helps in handling the decrypt at root level rather than
    # each implementing class handle the decryption separately.
    def __init__(self, *args, **kwargs):
        self.root_dir = kwargs.get('root_dir')
        self.cfgpath = kwargs.get('cfgpath')
        self.config_filename = kwargs.get('filename')
        base_config_path = os.path.join(self.root_dir, self.config_filename)
        self.base_config = read_yaml_file(base_config_path)
        self.log = get_logger(__name__, **self.base_config['Logging'])
        self.setup(*args, **kwargs)

    def get_config(self):
        """ reads and merges user config with base config"""

        user_config = self.generate_user_config()
        self.log.info(f'''user cfg: {user_config.keys()}''')
        config = merge_dict(self.base_config, user_config)
        # Decrypt all values as mentioned
        config = self.decrypt_keys(config)
        self.validate_config(config)
        self.log.debug(f"config object created")
        return config

    def validate_config(self, config):
        has_all_params = True
        missing_parameters = []
        for section, section_cfg in config.items():
            if not section_cfg:
                raise InValidConfigException(f'''{section_cfg} is empty''')
            if section == "Secrets":
                continue
            for k, v in section_cfg.items():
                if v is None:
                    self.log.error(f"Missing parameter {k} from config")
                    missing_parameters.append(k)
                    has_all_params = False
                elif "endpoint" in k.lower():
                    self.is_valid_url(v)
                else:
                    section_cfg[k] = convert_if_digit(v)

        if not has_all_params:
            raise InValidConfigException(f"Missing Parameters are {missing_parameters}")

    def is_valid_url(self, url):
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, url) is None:
            raise InValidConfigException(f"{url} does not match valid url regex")

    def generate_user_config(self):
        # this method will call the _fetch_user_config and
        # for all the configs which are encrypted will call decrypt method.
        return self.fetch_user_config()

    def decrypt_keys(self, config):
        if "Secrets" in config and "DECRYPT_KEYS" in config['Secrets'] and "KEYS" in config['Secrets'] \
                and config['Secrets']['DECRYPT_KEYS']:
            all_secrets = config["Secrets"]["KEYS"]
            for section, section_cfg in config.items():
                for key, value in section_cfg.items():
                    if key in all_secrets and "Secrets" != section:
                        decrypted_value = self.decrypt(all_secrets[key], key, value)
                        config[section][key] = decrypted_value
        return config

    def _override_section_config(self, other_config):
        cfg = {}
        for section, section_cfg in self.base_config.items():
            new_section_cfg = {}
            for k, v in section_cfg.items():
                if k in other_config:
                    new_section_cfg[k] = other_config[k]
                else:
                    new_section_cfg[k] = v
            cfg[section] = new_section_cfg
        return cfg

    @classmethod
    def get_file_locations(cls, input_path, filename):
        home_dir = os.path.expanduser("~")
        hom_dir_path = os.path.join(home_dir, filename)
        sumo_dir_path = os.path.join(home_dir, cls.SUMO_CONFIG_FOLDER, filename)
        cfg_locations = [input_path, sumo_dir_path, hom_dir_path, os.getenv("SUMO_API_COLLECTOR_CONF", '')]
        return filter(lambda p: os.path.isfile(p), cfg_locations)

    @abstractmethod
    def fetch_user_config(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def decrypt(self, decrypt_type, key, value):
        raise NotImplementedError()

    @abstractmethod
    def setup(self, *args, **kwargs):
        raise NotImplementedError()
