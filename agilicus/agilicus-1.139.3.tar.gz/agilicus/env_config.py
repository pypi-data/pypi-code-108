import os
import tempfile
import agilicus
import yaml

from . import apps, context, files
from .output.table import (
    format_table,
    column,
)


def add(
    ctx,
    application,
    env_name,
    org_id=None,
    config_type=None,
    mount_src_path=None,
    username=None,
    password=None,
    share=None,
    domain=None,
    hostname=None,
    file_store_uri=None,
    filename=None,
    env_config_vars=None,
    **kwargs,
):
    token = context.get_token(ctx)
    if not org_id:
        org_id = context.get_org_id(ctx, token)

    if filename:
        _file = files.upload(
            ctx,
            filename,
            org_id=org_id,
            label=config_type,
            tag=env_name,
            name=os.path.basename(filename),
        )
        file_store_uri = f"/v1/files/{_file['id']}"

    app = apps.get_app(ctx, org_id, application, maintained=True)
    _config = agilicus.EnvironmentConfig(
        maintenance_org_id=org_id,
        config_type=config_type,
        file_store_uri=file_store_uri,
        mount_src_path=mount_src_path,
        mount_username=username,
        mount_password=password,
        mount_share=share,
        mount_domain=domain,
        mount_hostname=hostname,
        env_config_vars=env_config_vars,
        **kwargs,
    )
    apiclient = context.get_apiclient(ctx, token)
    return apiclient.application_api.add_config(app["id"], env_name, _config)


def update(
    ctx,
    application,
    env_name,
    id,
    org_id=None,
    config_type=None,
    mount_path=None,
    file_store_uri=None,
    env_config_vars=None,
    **kwargs,
):
    token = context.get_token(ctx)
    if not org_id:
        org_id = context.get_org_id(ctx, token)

    app = apps.get_app(ctx, org_id, application, maintained=True)

    apiclient = context.get_apiclient(ctx, token)
    _config = apiclient.application_api.get_config(
        app["id"], env_name, id, maintenance_org_id=org_id
    )

    _update = agilicus.EnvironmentConfig(
        maintenance_org_id=org_id,
        id=id,
        mount_path=_config.mount_path,
        config_type=_config.config_type,
        file_store_uri=_config.file_store_uri,
        env_config_vars=env_config_vars,
    )

    if mount_path:
        _update.mount_path = mount_path

    if config_type:
        _update.config_type = config_type

    if file_store_uri:
        _update.file_store_uri = file_store_uri
    return apiclient.application_api.replace_config(app["id"], env_name, id, _update)


def delete(ctx, application, env_name, id, org_id=None, **kwargs):
    token = context.get_token(ctx)
    if not org_id:
        org_id = context.get_org_id(ctx, token)

    app = apps.get_app(ctx, org_id, application, maintained=True)
    apiclient = context.get_apiclient(ctx, token)

    _config = apiclient.application_api.get_config(
        app["id"], env_name, id, maintenance_org_id=org_id
    )

    if _config.file_store_uri:
        file_id = os.path.basename(_config.file_store_uri)
        try:
            files.delete(ctx, file_id, org_id=org_id, _continue_on_error=True)
        except Exception:
            print(f"Failed to delete the {_config.file_store_uri}")

    return apiclient.application_api.delete_config(app["id"], env_name, id, org_id)


def query(ctx, application, env_name, org_id=None, **kwargs):
    token = context.get_token(ctx)
    if not org_id:
        org_id = context.get_org_id(ctx, token)

    app = apps.get_app(ctx, org_id, application, maintained=True)
    apiclient = context.get_apiclient(ctx, token)
    return apiclient.application_api.list_configs(app["id"], env_name, org_id).configs


def convert_to_env_config_var(env_config_dict):
    env_list = []
    for k, v in env_config_dict.items():
        env_var_obj = agilicus.EnvironmentConfigVar(name=k, value=v)
        env_list.append(env_var_obj)
    return env_list


class EnvVarConfigObj:
    def __init__(self, ctx, application, env_name, org_id=None, secret=False):
        self.ctx = ctx
        self.application = application
        self.env_name = env_name
        self.org_id = org_id
        if secret:
            self.env_file = "secret-env.yaml"
            self.config_type = "secret_env"
        else:
            self.env_file = "config-env.yaml"
            self.config_type = "configmap_env"
        self.env_config = None
        self.old_file_envs = {}
        self.old_env_configs = {}
        self.env_vars = {}
        self.env_var_list = []
        self.build_env_list()

    def get_env_list(self):
        return self.env_var_list

    def get_old_env(self, env_config_vars):
        self.old_env_configs = {}
        if env_config_vars:
            for env in env_config_vars:
                self.old_env_configs[env.name] = env.value

    def merge_env(self, file_env, env_config):
        self.env_vars = file_env
        self.env_vars.update(env_config)

    def build_env_list(self):
        configs = query(self.ctx, self.application, self.env_name, self.org_id)
        for config in configs:
            if config.config_type.upper() == self.config_type.upper():
                if config.file_store_uri:
                    with tempfile.TemporaryDirectory() as tempdir:
                        destination = os.path.join(tempdir, self.env_file)
                        files.download(
                            self.ctx,
                            os.path.basename(config.file_store_uri),
                            org_id=self.org_id,
                            destination=destination,
                        )
                        with open(destination) as stream:
                            self.old_file_envs = yaml.safe_load(stream)
                self.get_old_env(config.env_config_vars)
                self.merge_env(self.old_file_envs, self.old_env_configs)
                self.env_var_list = convert_to_env_config_var(self.env_vars)
                self.env_config = config
                return

    def write_env_vars(self, data):
        self.env_vars.update(data)

    def write_env_list(self):
        self.env_var_list = convert_to_env_config_var(self.env_vars)
        filename = None
        if self.env_config:
            delete(
                self.ctx,
                self.application,
                self.env_name,
                self.env_config.id,
                self.org_id,
            )
        with tempfile.TemporaryDirectory() as tempdir:
            filename = os.path.join(tempdir, self.env_file)
            with open(filename, "w") as outfile:
                yaml.dump(self.env_vars, outfile, default_flow_style=False)
            self.env_config = add(
                self.ctx,
                self.application,
                self.env_name,
                org_id=self.org_id,
                config_type=self.config_type,
                filename=None,
                file_store_uri=None,
                env_config_vars=self.env_var_list,
            )

    def add_env_var(self, env_name, env_value):
        env_data = {}
        env_data[env_name] = env_value
        self.write_env_vars(env_data)
        self.write_env_list()

    def del_env_var(self, env_var_name):
        self.env_vars.pop(env_var_name, None)
        self.write_env_list()

    def update_env_var(self, env_config_name, env_config_value):
        env_data = {}
        env_data[env_config_name] = env_config_value
        self.write_env_vars(env_data)
        self.write_env_list()


def format_env_vars_as_text(ctx, env_vars):
    columns = [
        column("name"),
        column("value"),
    ]
    return format_table(ctx, env_vars, columns)
