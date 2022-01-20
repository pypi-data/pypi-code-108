import os
import urllib.parse
import yaml
import netrc
from cnvrgv2.config import error_messages
from cnvrgv2.errors import CnvrgError, CnvrgFileError, CnvrgArgumentsError

CONFIG_VERSION = 2
CONFIG_FILE_NAME = "cnvrg.config"
CONFIG_FOLDER_NAME = ".cnvrg"

NETRC_FILE_NAME = ".netrc"
LEGACY_IDX_FILE_NAME = "idx.yml"
LEGACY_CONFIG_FILE_NAME = "config.yml"

LEGACY_NETRC_PATH = os.path.join(os.path.expanduser("~"), NETRC_FILE_NAME)  # TODO: might break on windows
GLOBAL_CNVRG_PATH = os.path.join(os.path.expanduser("~"), CONFIG_FOLDER_NAME)  # TODO: might break on windows


class Config:

    global_config_attributes = {
        "organization": str,
        "domain": str,
        "token": str,
        "user": str,
        "check_certificate": bool,
        "keep_duration_days": int,
        "version": float
    }

    local_config_attributes = {
        "git": bool,
        "commit_sha1": str,
        "project_slug": str,
        "dataset_slug": str,
    }

    def __init__(self):
        self.local_config = {}
        self.global_config = {}

        # Support legacy config files
        self._load_legacy_config()

        if self.global_config_exists:
            global_config = yaml.safe_load(open(self.global_config_file_path, "r")) or {}
            for key in Config.global_config_attributes.keys():
                default = False if Config.global_config_attributes[key] == bool else None
                self.global_config[key] = global_config.get(key, default) or self.global_config.get(key, default)

        if self.local_config_exists:
            local_config = yaml.safe_load(open(self.local_config_file_path, "r")) or {}
            for key in Config.local_config_attributes.keys():
                default = False if Config.local_config_attributes[key] == bool else None
                self.local_config[key] = local_config.get(key, default) or self.local_config.get(key, default)

    @property
    def data_owner_slug(self):
        return self.project_slug or self.dataset_slug

    @property
    def global_cnvrg_path(self):
        return GLOBAL_CNVRG_PATH

    @property
    def local_cnvrg_path(self):
        return os.path.join(os.getcwd(), CONFIG_FOLDER_NAME)

    @property
    def local_config_file_path(self):
        return os.path.join(self.local_cnvrg_path, CONFIG_FILE_NAME)

    @property
    def global_config_file_path(self):
        return os.path.join(self.global_cnvrg_path, CONFIG_FILE_NAME)

    @property
    def local_config_exists(self):
        return os.path.exists(self.local_config_file_path)

    @property
    def global_config_exists(self):
        return os.path.exists(self.global_config_file_path)

    def _load_legacy_config(self):
        legacy_global_config_file_path = os.path.join(self.global_cnvrg_path, LEGACY_CONFIG_FILE_NAME)
        legacy_idx_file_path = os.path.join(self.local_cnvrg_path, LEGACY_IDX_FILE_NAME)
        legacy_config_file_path = os.path.join(self.local_cnvrg_path, LEGACY_CONFIG_FILE_NAME)

        legacy_global_config_exists = os.path.exists(legacy_global_config_file_path)
        legacy_netrc_exists = os.path.exists(LEGACY_NETRC_PATH)

        legacy_idx_exists = os.path.exists(legacy_idx_file_path)
        legacy_config_exists = os.path.exists(legacy_config_file_path)

        # We want to try and load legacy config file BEFORE the new config file so we can override if needed
        if legacy_global_config_exists:
            legacy_global_config = yaml.safe_load(open(legacy_global_config_file_path, "r"))
            api = legacy_global_config.get(":api", None) or legacy_global_config.get("api", None)
            uri = urllib.parse.urlparse(api)
            self.domain = '{uri.scheme}://{uri.hostname}/'.format(uri=uri)

        if legacy_netrc_exists:
            netrc_file = netrc.netrc()
            authTokens = netrc_file.authenticators("cnvrg.io")
            # 0 is login, 1 is account, 2 is password
            self.user = authTokens[0]
            self.token = authTokens[2]

        if legacy_config_exists:
            legacy_config = yaml.safe_load(open(legacy_config_file_path, "r"))
            self.organization = legacy_config.get(":owner", None) or legacy_config.get("owner", None)
            self.project_slug = legacy_config.get("project_slug", None) or legacy_config.get(":project_slug", None)
            self.dataset_slug = legacy_config.get("dataset_slug", None) or legacy_config.get(":dataset_slug", None)
            self.git = legacy_config.get(":git", False) or legacy_config.get("git", False)

        if legacy_idx_exists:
            legacy_idx_config = yaml.safe_load(open(legacy_idx_file_path, "r"))
            self.commit_sha1 = legacy_idx_config.get(":commit", None) or legacy_idx_config.get("commit", None)

    def __getattr__(self, name):
        """
        Returns an attribute value from the local/global config attributes
        @param name: Name of the attribute to return
        @return: The value of the given attribute
        """
        is_global = name in Config.global_config_attributes.keys()
        is_local = name in Config.local_config_attributes.keys()

        if not (is_global or is_local):
            raise AttributeError("type object {} has no attribute {}".format(self.__class__.__name__, name))

        if is_global:
            return self.global_config.get(name, None)
        else:
            return self.local_config.get(name, None)

    def __setattr__(self, name, value):
        """
        Sets an attribute to global/local config
        @param name: Attribute name
        @param value: Attribute value
        @return: None
        """
        is_global = name in Config.global_config_attributes.keys()
        is_local = name in Config.local_config_attributes.keys()

        config_available_attributes = Config.global_config_attributes if is_global else Config.local_config_attributes

        if not (is_global or is_local):
            super().__setattr__(name, value)
        else:
            value_type = type(value)

            expected_type = config_available_attributes[name]
            if value_type != expected_type and value is not None:
                bad_format_message = error_messages.ARGUMENT_BAD_TYPE.format(expected_type, value_type)
                raise CnvrgArgumentsError({name: bad_format_message})

            if is_global:
                self.global_config[name] = value
            else:
                self.local_config[name] = value

    def update(self, local_config_path=None, **kwargs):
        """
        Updates the config file and changes the attributes of the current object.
        Unknown keys will be ignored.
        @param local_config_path: Override the local config path - can be used to create new cnvrg project or dataset
        @param kwargs: Dict of new values
        @return: None
        """
        updated_global_attributes = {}
        updated_local_attributes = {}

        for key, value in kwargs.items():
            if key in Config.global_config_attributes.keys():
                updated_global_attributes[key] = value
            if key in Config.local_config_attributes.keys():
                updated_local_attributes[key] = value

        self.global_config = {
            **self.global_config,
            **updated_global_attributes
        }

        self.local_config = {
            **self.local_config,
            **updated_local_attributes
        }

        self.save(local_config_path=local_config_path)

    def save(self, local_config_path=None):
        """
        Updates the config file with the current attributes
        @return: None
        """

        if local_config_path is None:
            local_config_path = self.local_cnvrg_path

        path_to_attrs = {}
        if self.global_config:
            path_to_attrs[os.path.join(GLOBAL_CNVRG_PATH, CONFIG_FILE_NAME)] = self.global_config
        if self.local_config:
            path_to_attrs[os.path.join(local_config_path, CONFIG_FILE_NAME)] = self.local_config

        for config_path, new_config in path_to_attrs.items():
            if not os.path.exists(os.path.dirname(config_path)):
                os.makedirs(os.path.dirname(config_path))

            if not os.path.exists(config_path):
                open(config_path, "w").close()

            with open(config_path, 'r+') as config_file:
                config = yaml.safe_load(config_file) or {}
                config = {**config, **new_config}
                config_file.seek(0)
                config_file.truncate(0)
                yaml.dump(config, config_file)

    def remove_config_fields(self, *args):
        """
        Removes fields from the config file according to given keys
        @param args: keys to remove
        @return: None
        """

        paths_to_keys = {}
        for key in args:
            key_exists = False
            if key in Config.global_config_attributes.keys():
                paths_to_keys.setdefault(self.global_config_file_path, []).append(key)
                key_exists = True
            if key in Config.local_config_attributes.keys():
                paths_to_keys.setdefault(self.local_config_file_path, []).append(key)
                key_exists = True

            if not key_exists:
                raise CnvrgError(error_messages.FAULTY_KEY.format(key))

        for config_path, keys_to_remove in paths_to_keys.items():
            if not os.path.exists(os.path.dirname(config_path)):
                raise CnvrgFileError(error_messages.CONFIG_FILE_MISSING)

            with open(config_path, 'r+') as config_file:
                config = yaml.safe_load(config_file) or {}
                for key in keys_to_remove:
                    config.pop(key, None)
                config_file.seek(0)
                config_file.truncate(0)
                yaml.dump(config, config_file)

    def get_credential_variables(self):
        """
        Returns the variables forming user credentials
        @return: token, domain, user
        """
        if not self.global_config:
            return False, False, False

        # Credential variables
        token = self.token
        domain = self.domain
        user = self.user

        return token, domain, user
