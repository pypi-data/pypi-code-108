#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# xtConfig.py: reads and writes the config.yaml file, used to persist user settings for XT

import os
import yaml
import shutil
import logging
import importlib

from xtlib import utils
from xtlib import errors
from xtlib import constants
from xtlib import pc_utils
from xtlib import file_utils
from xtlib.console import console
from .dot_dict import DotDict
from .validator import Validator

logger = logging.getLogger(__name__)

class XTConfig():

    def __init__(self, fn=None, create_if_needed=False):
        self.create_if_needed = create_if_needed
        self.data = self.read_config(fn)
        self.explicit_options = {}
        self.vault = None

    def name_exists(self, group, name):
        return group in self.data and name in self.data[group]

    def warning(self, *msg_args):
        msg = "WARNING: xt_config file -"
        for arg in msg_args:
            msg += " " + str(arg)
        if self.get("internal", "raise", suppress_warning=True):
            errors.config_error(msg)
        else:
            console.print(msg)

    def get_explicit_option(self, name):
        return self.explicit_options[name] if name in self.explicit_options else None

    def get_groups(self):
        return self.data

    def get_group_properties(self, group):
        return self.data[group]

    def set_explicit_option(self, name, value):
        self.explicit_options[name] = value

    # use "*" to require dict_key and default_value to be a named arguments
    def get(self, group, name=None, dict_key=None, default_value=None, suppress_warning=False, group_error=None, 
        prop_error=None, key_error=None):
        
        value = default_value

        if group in self.data:
            value = self.data[group]
            if name:
                if name in value:
                    value = value[name]
                    if dict_key:
                        if dict_key in value:
                            value = value[dict_key]
                        else:
                            if key_error:
                                errors.config_error(key_error)
                            if not suppress_warning:
                                self.warning("GET option dict_key not found: ", group, name, dict_key, default_value)
                            value = default_value
                else:
                    if prop_error:
                        errors.config_error(prop_error)
                    if not suppress_warning:
                        self.warning("GET option not found: ",  group, name, dict_key, default_value)
                    value = default_value
        else:
            if group_error:
                errors.config_error(group_error)
            if not suppress_warning:
                self.warning("GET option GROUP not found: ", group, name, dict_key, default_value)
            value = default_value

        # expand values containing a "$" id
        if isinstance(value, str) and "$" in value:
            value = self.expand_system_symbols(value, name)
        elif isinstance(value, dict):
            for key, val in value.items():
                if isinstance(val, str) and "$" in val:
                    val = self.expand_system_symbols(val, name, key)
                    value[key] = val

        return value

    # use "*" to require dict_key and value to be a named arguments
    def set(self, group, name, *, dict_key=None, value=None, suppress_warning=False):
        if group in self.data:
            gv = self.data[group]
            if name in gv:
                if dict_key:
                    obj = gv[name]
                    if not dict_key in obj:
                        if not suppress_warning:
                            self.warning("SET option dict_key not found: ", group, name, dict_key, value)
                    #console.print("set: obj=", obj, ", dict_key=", dict_key, ", value=", value)
                    obj[dict_key] = value
                    #console.print("set: post obj=", obj)
                else:
                    gv[name] = value
            else:
                if not suppress_warning:
                    self.warning("SET option name not found: ", group, name, dict_key, value)
                gv[name] = value
        else:
            raise Exception("SET option group not found: ", group, name, dict_key, value)
        
    def get_vault_key(self, name):
        self.create_vault_if_needed()
        return self.vault.get_secret(name)
        
    def create_vault_if_needed(self):
        if not self.vault:
            console.diag("before vault login")
            from xtlib import xt_vault 

            # create our vault manager
            vault_creds = self.get_vault_creds()

            if not "url" in vault_creds:
                vault_name = vault_creds["name"]

                errors.config_error("URL not specified for '{}' in [external-services] section of XT config file".\
                    format(vault_name))

            vault_url = vault_creds["url"]
            secret_name = utils.safe_value(vault_creds, "secret-name", "xt-keys")
            store_name = self.get("store")

            self.vault = xt_vault.XTVault(vault_url, store_name, secret_name)

            authentication = self.get("general", "authentication")
            self.vault.init_creds(authentication)

            console.diag("after vault login")

    def expand_system_symbols(self, text, section=None, prop_name=None):
        if text == "$vault":
            if not self.vault:
                # create on-demand
                self.create_vault_if_needed()

            assert section 
            text = self.vault.get_secret(section)

        if text and "$username" in text:
            ev_user = "USERNAME" if pc_utils.is_windows() else "USER"
            username = os.getenv(ev_user, os.getenv("XT_USERNAME"))
            username = username if username else ""
            text = text.replace("$username", username)

        if text and "$current_conda_env" in text:
            conda = os.getenv("CONDA_DEFAULT_ENV")
            if conda:
                text = text.replace("$current_conda_env", conda)

        return text

    def read_config(self, fn=None):
        if fn is None:
            fn = file_utils.get_xtlib_dir() + "/helpers/" + constants.FACTORY_CONFIG
        self.fn = fn

        if not os.path.exists(fn):
            errors.internal_error("missing default_config file: " + fn)
            # if self.create_if_needed:
            #     console.print("XT config file not found; creating it from default settings...")
            #     file_dir = file_utils.get_xtlib_dir() + "/helpers"
            #     from_fn = file_dir + constants.FACTORY_CONFIG

            #     # read default file, update, write to fn
            #     text = file_utils.read_text_file(from_fn)
            #     text = self.expand_system_symbols(text)
            #     utils.write_text_file(fn, text)
            # else:
            #     errors.user_error("XT config file doesn't exist: {}".format(fn))

        # read config file
        try:
            with open(fn, "rt") as file:
                config = yaml.safe_load(file)  # , Loader=yaml.FullLoader)
        except BaseException as ex:
            logger.exception("Error in read_config, ex={}".format(ex))
            raise Exception ("The config file '{}' is not valid YAML, error: {}".format(fn, ex))

        return config

    def get_box_def(self, box_name):
        box_def = self.get("boxes", box_name, suppress_warning=True)
        if not box_def:
            if box_name == pc_utils.get_hostname():
                # try "local"
                box_def = self.get("boxes", "local", suppress_warning=True)

        return box_def

    def get_setup_from_box(self, box_name):
        setup_def = None

        box_def = self.get_box_def(box_name)
        if box_def and "setup" in box_def:
            setup_name = box_def["setup"]
            setup_def = self.get("setups", setup_name, suppress_warning=True)

        return setup_def

    def get_setup_from_target_def(self, target_def, setup_name=None):
        setup_def = None

        if not setup_name and target_def and "setup" in target_def:
            setup_name = target_def["setup"]

        if setup_name:
            setup_def = self.get("setups", setup_name, suppress_warning=True)

        return setup_def

    def get_targets(self):
        targets = self.get("compute-targets")
        targets = list(targets.keys())
        return targets

    def get_service(self, service_name):
        service = self.get("external-services", service_name, suppress_warning=True)
        if not service:
            errors.config_error("'{}' must be defined in the [external-services] section of XT config file".format(service_name))

        service["name"] = service_name
        #self.expand_symbols_in_creds(service, service_name)
        return service

    def get_target_def(self, target_name): 
        compute_def = self.get("compute-targets", target_name, suppress_warning=True)

        if not compute_def:
            # is this target a box name?
            box_info = self.get("boxes", target_name, suppress_warning=True)
            if not box_info:
                errors.config_error("target '{}' must be defined in the [compute-targets] section of XT config file (or be a box name)".format(target_name))
            # make box look like a target
            compute_def = {"service": "pool", "boxes": [target_name]}

            # use setup and docker from first box 
            if "setup" in box_info:
                compute_def["setup"] = box_info["setup"]
            if "docker" in box_info:
                compute_def["docker"] = box_info["docker"]

        compute_def["name"] = target_name
        #self.expand_symbols_in_creds(target, target_name)
        return compute_def        

    def get_external_service_from_target(self, target_name):
        target = self.get_target_def(target_name)
        
        if not "service" in target:
                errors.config_error("'service' property must be defined for target={} in the XT config file".format(target))
        service_name = target["service"]

        service = self.get_service(service_name)
        #self.expand_symbols_in_creds(service, service_name)
        return service

    # def expand_symbols_in_creds(self, creds, creds_name):
    #     for key, value in creds.items():
    #         if "$" in value:
    #             value = self.expand_system_symbols(value, creds_name, key)
    #             creds[key] = value

    def get_storage_creds(self):
        # validate STORAGE service
        ss_info = self.get_store_info()
        storage_name = utils.safe_value(ss_info, "storage")
        if not storage_name:
            errors.config_error("'storage' property must be set in store '{}'".format(ss_info["name"]))

        # validate STORAGE_NAME credentials
        storage_creds = self.get("external-services", storage_name, suppress_warning=True)
        if not storage_creds:
            errors.config_error("'{}' must be specified in [external-services] section of XT config file".format(storage_name))

        #self.expand_symbols_in_creds(storage_creds, storage_name)
        storage_creds["name"] = storage_name
        return storage_creds

    def get_database_creds(self):
        # validate database service
        ss_info = self.get_store_info()
        db_name = utils.safe_value(ss_info, "database")
        if not db_name:
            errors.config_error("'database' property must be set in store '{}'".format(ss_info["name"]))

        # validate database credentials
        db_creds = self.get("external-services", db_name, suppress_warning=True)
        if not db_creds:
            errors.config_error("'{}' must be specified in [external-services] section of XT config file".format(db_name))

        #self.expand_symbols_in_creds(db_creds, db_name)
        db_creds["name"] = db_name
        return db_creds

    def get_vault_creds(self):
        # validate VAULT service
        ss_info = self.get_store_info()
        vault_name = utils.safe_value(ss_info, "vault")
        if not vault_name:
            # empty value name is acceptable for some service sets
            return None

        # validate VAULT credentials
        vault_creds = self.get("external-services", vault_name, suppress_warning=True)
        if not vault_creds:
            errors.config_error("'{}' must be specified in [external-services] section of XT config file".format(vault_name))

        vault_creds["name"] = vault_name
        return vault_creds

    def get_storage_type(self):
        return "azure-store"

    def get_service_type(self, service_name):
        if service_name == "pool":
            service_type = "pool"
        else:
            service = self.get("external-services", service_name, suppress_warning=True)
            if not service:
                errors.config_error("'{}' must be defined in the [external-services] section of XT config file".format(service_name))
                
            if not "type" in service:
                errors.config_error("'type' must be defined for the '{}' service in the XT config file".format(service_name))

            service_type = service["type"]

        return service_type

    def get_required_service_property(self, creds, prop_name, service_name):
        value = utils.safe_value(creds, prop_name)
        if not value:
            errors.config_error("Missing '{}' property for service '{}' defined in [external-services] section of the XT config file".format(prop_name, service_name))

        return value

    def get_docker_def(self, name): 
        environemnt_def = self.get("dockers", name, suppress_warning=True)
        return environemnt_def        

    def get_storage_provider_code_path(self, storage_creds):
        # get the provider_code_path
        provider_name = storage_creds["provider"]
        providers = self.get("providers", "storage")
        if not provider_name in providers:
            errors.config_error("{} provider='{}' not registered in XT config file".format("storage", provider_name))

        code_path = providers[provider_name]
        return code_path

    def get_provider_class_ctr(self, provider_type, name):
        '''
        return the class constructor method for the specified provider.
        '''
        providers = self.get("providers", provider_type)

        if not name in providers:
            errors.config_error("{} provider='{}' not registered in XT config file".\
                format(provider_type, name))

        code_path = providers[name]
        return utils.get_class_ctr(code_path)

    def get_docker_info(self, target: str, docker_name: str, required: bool):
        docker_image = None
        login_server = None
        docker_registry = None

        compute_def = self.get_target_def(target)

        if not docker_name:
            docker_name = utils.safe_value(compute_def, "docker")
            
        if docker_name:
            env = self.get("dockers", docker_name, default_value=None)
            if not env:
                errors.config_error("docker '{}' definition not found in XT config file".format(docker_name))

            docker_image = utils.safe_value(env, "image")
            if not docker_image:
                errors.config_error("Definition for docker '{}' is missing the required 'image' property".format(docker_name))

            registry_name = utils.safe_value(env, "registry")
            # if not registry_name:
            #     errors.config_error("Definition for docker '{}' is missing the required 'registry' property".format(docker_name))

            if registry_name:
                docker_registry = self.get("external-services", registry_name, default_value=None)
                if not docker_registry:
                    errors.config_error("Definition for docker registry '{}' is missing in the external-services section".format(registry_name))

                login_server = utils.safe_value(docker_registry, "login-server")
                if not login_server:
                    errors.config_error("Definition for registry '{}' is missing the required 'login-server' property".format(registry_name))
        elif required:
            # all philly compute targets must specify a docker image
            errors.config_error("Philly compute target '{}' is missing the required 'docker' property (in XT config file)".format(target))

        return docker_image, login_server, docker_registry

    def get_target_desc(self, target, backend):
        '''
        returns a string describing the target (for logging and monitoring)
        '''
        backend_name = backend.get_name()
        compute_def = backend.compute_def

        if backend_name == "philly":
            cluster = backend.cluster
            vc = backend.vc
            queue = backend.queue
            target_str = "target={}, backend={}, cluster={}, vc={}, queue={}".format(target, backend_name, cluster, vc, queue)

        elif backend_name in ["aml", "itp"]:
            service = compute_def["service"]
            compute = compute_def["compute"]
            target_str = "target={}, backend={}, service={}, compute={}".format(target, backend_name, service, compute)

        elif backend_name == "batch":
            service = compute_def["service"]
            target_str = "target={}, backend={}, service={}".format(target, backend_name, service)

        elif backend_name == "pool":
            target_str = "target={}, backend={}".format(target, backend_name)

        else:
            errors.internal_error("unknown backend name=", backend_name)

        return target_str

    def get_store_info(self, store_name=None):
        if not store_name:
            store_name = self.get("store", suppress_warning=True)
            
        if not store_name:
            errors.config_error("XT config file is missing required property: store")
        
        store_info = self.get("stores", store_name, suppress_warning=True)
        if not store_info:
            errors.config_error("XT config file is missing definition for store: {}".format(store_name))

        store_info["name"] = store_name
        return store_info

# flat functions

def load_yaml(fn): 
    with open(fn, "rt") as file:
        data = yaml.safe_load(file) #, Loader=yaml.FullLoader)
    return data

def _merge_configs(config, overrides):
    # note: a simple dict "update()" is too blunt; we need a fine-grained key/value update
    config_data = config.data

    # MERGE local config with default config
    for section_name, section_value in overrides.data.items():
        if not section_name in config_data:
            config_data[section_name] = {}

        # section_value could be a simple str
        if isinstance(section_value, str):
            # just replace list as a single value
            config_data[section_name] = section_value
        elif isinstance(section_value, list):
            # just replace list as a single value
            config_data[section_name] = section_value
        else:
            # process dict
            section = config_data[section_name]

            for key, value in section_value.items():
                # note: entries in a dict like compute-targets should be overwritten in whole (not prop by prop)
                if False:   # isinstance(value, dict):
                    # handle [section.subsection] 
                    if not key in config_data[section_name]:
                        section[key] = {}
                    for inner_key, inner_value in value.items():
                        #console.print("overridding: [{}.{}] {} = {}".format(section_name, key, inner_key, inner_value))
                        section[key][inner_key] = inner_value
                else:
                    # handle [section]
                    #console.print("overridding: [{}] {} = {}".format(section_name, key, value))
                    section[key] = value    

def _apply_override(validator, config, schema, fn_schema, fn_override):
    
    overrides = XTConfig(fn=fn_override, create_if_needed=False)

    if overrides.data:
        # validate the local overrides config file
        validator.validate(schema, fn_schema, overrides.data, fn_override, False)

        # merge the overrides config with the default config
        _merge_configs(config, overrides)
    
def _apply_basic_mode_rules(config):
    sc = os.getenv("XT_STORE_CREDS")
    mc = os.getenv("XT_DB_CREDS")
    if sc and mc:
        # we are running on compute node (launched by script)
        #console.print("XT: detected run on compute node; setting advanced mode ON")
        config.set("general", "advanced-mode", value=True)

    if not config.get("general", "advanced-mode"):
        # single workspace
        # leave the workspace name from FACTORY
        #config.data["general"]["workspace"] = "txt"

        # single target
        # TODO: are we going to support "local" for basic mode?  
        ss_info = config.get_store_info()
        ss_info["target"] = "batch"

def get_merged_config(create_if_needed=True, local_overrides_path=None, suppress_warning=False):

    # load the FACTORY config
    config = XTConfig()    

    # load the schema for XT CONFIG files
    fn_schema = os.path.join(file_utils.get_xtlib_dir(), "helpers", "xt_config_schema.yaml")
    schema = load_yaml(fn_schema)

    # validate the default config file
    validator = Validator()
    validator.validate(schema, fn_schema, config.data, config.fn, True)
    fn_complete = config.fn

    # is there a GLOBAL config?
    fn_global = os.path.expanduser(os.getenv("XT_GLOBAL_CONFIG", "~/.xt/xt_config.yaml"))
    if os.path.isfile(fn_global):    
        _apply_override(validator, config, schema, fn_schema, fn_global)
        fn_complete = fn_global

    # is there a LOCAL config?
    fn_local = local_overrides_path if local_overrides_path else constants.CONFIG_FN
    if os.path.isfile(fn_local):    
        _apply_override(validator, config, schema, fn_schema, fn_local)
        fn_complete = fn_local

    # now that merging is complete, validate all references in the config data
    validator.validate_references(config.data, fn_complete)

    # apply special BASIC MODE rules
    _apply_basic_mode_rules(config)

    console.detail("after loading/validation of merged config files")
    return config

