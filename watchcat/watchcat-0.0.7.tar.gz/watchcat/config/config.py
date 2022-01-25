import os
import os.path
from typing import Dict, List, Union

import yaml
from requests.auth import AuthBase, HTTPBasicAuth
from watchcat.config.errors import (
    ConfigEmptyError,
    ConfigLoadError,
    ConfigVersionMissmatchError,
    ConfigVersionNotFoundError,
)
from watchcat.filter.command import CommandFilter
from watchcat.filter.css_selector import CssSelectorFilter
from watchcat.filter.filter import Filter
from watchcat.filter.textcontent import TextContentFilter
from watchcat.notifier.command import CommandNotifier
from watchcat.notifier.file import FileNotifier
from watchcat.notifier.notifier import Notifier
from watchcat.notifier.slack_bot import SlackBotNotifier
from watchcat.notifier.slack_webhook import SlackWebhookNotifier
from watchcat.resource.command_resource import CommandResource
from watchcat.resource.http_resource import HttpResource
from watchcat.resource.resource import Resource
from watchcat.util import expand_environment_variables, recursive_update


class ConfigLoader:
    def __init__(self, config_path: str, use_environment_variables=True) -> None:
        self.version = "1"

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"config file not found {config_path}")

        with open(config_path, "rt", encoding="utf-8") as f:
            content = f.read()
            if use_environment_variables:
                content = expand_environment_variables(content)
            config = yaml.load(content, yaml.FullLoader)
            if not config:
                raise ConfigEmptyError()

        self._load_config(config)

    def _load_config(self, config: Dict[str, Dict]):
        # load version
        if version := config.get("version"):
            if version != self.version:
                raise ConfigVersionMissmatchError()
        else:
            raise ConfigVersionNotFoundError()

        # load notifiers
        self.default_notifier = config.get("default_notifier")
        if notifiers_config := config.get("notifiers"):
            self.notifiers = self._load_notifiers(notifiers_config)
        else:
            self.notifiers = dict()

        # load templates
        if templates_config := config.get("templates"):
            self.templates = self._load_templates(templates_config)
        else:
            self.templates = dict()

        # load resources
        if resources_config := config.get("resources"):
            self.resources = self._load_resources(resources_config)
        else:
            self.resources = dict()

    def _get_notifier(self, notifier_id: Union[str, None]) -> Notifier:
        try:
            if not self.notifiers:
                raise ConfigLoadError("You need to set `notifiers`")
            if notifier_id:
                return self.notifiers[notifier_id]
            else:
                if self.default_notifier:
                    return self.notifiers[self.default_notifier]
                else:
                    raise ConfigLoadError("You need to set `default_notifier`")
        except KeyError as e:
            raise ConfigLoadError(f"No such notifier: {e}")

    def _load_notifiers(self, notifiers_config: Dict[str, Dict]) -> Dict[str, Notifier]:
        if not isinstance(notifiers_config, dict):
            raise ConfigLoadError("`notifiers` must be dict")

        notifiers = dict()
        for notifier_key, notifier_config in notifiers_config.items():
            notifier = self._load_notifier(notifier_key, notifier_config)
            notifiers[notifier_key] = notifier
        return notifiers

    def _load_notifier(self, notifier_id: str, notifier_config: Dict[str, str]) -> Notifier:
        if not isinstance(notifier_config, dict):
            raise ConfigLoadError(f"`notifiers.{notifier_id}` must be dict: {notifier_config}")

        try:
            notifier_type = notifier_config["type"]
            if notifier_type == "slack":
                webhook_url = notifier_config["webhook"]
                return SlackWebhookNotifier(notifier_id, webhook_url)
            elif notifier_type == "slackbot":
                token = notifier_config["token"]
                channel = notifier_config["channel"]
                return SlackBotNotifier(notifier_id, token, channel)
            elif notifier_type == "cmd":
                command = notifier_config["cmd"]
                return CommandNotifier(notifier_id, command)
            elif notifier_type == "file":
                path = notifier_config["path"]
                return FileNotifier(notifier_id, path)
            else:
                raise ConfigLoadError(f"Unsupported notifier type: {notifier_type}")
        except KeyError as e:
            raise ConfigLoadError(f"KeyError on loading notifier: {notifier_id}, key: {e}")

    def _load_resources(self, resources_config: Dict[str, Dict[str, str]]) -> Dict[str, Resource]:
        if not isinstance(resources_config, dict):
            raise ConfigLoadError("`resources` must be dict")

        resources = dict()
        for resource_id, resource_config in resources_config.items():
            resources[resource_id] = self._load_resource(resource_id, resource_config)

        return resources

    def _load_resource(self, resource_id: str, resource_config: Dict[str, str]) -> Resource:
        if not isinstance(resource_config, dict):
            raise ConfigLoadError(f"item of `resources` must be dict: {resource_config}")
        import copy

        # upgrade resource config with template
        if template_id := resource_config.get("template"):
            template = self._get_template(template_id)
            resource_config = recursive_update(copy.deepcopy(template), resource_config)

        title = resource_config.get("title")
        url = resource_config.get("url")
        enabled = resource_config.get("enabled", True)
        notifier_id = resource_config.get("notifier")
        notifier = self._get_notifier(notifier_id)
        env = resource_config.get("env")
        cmd = resource_config.get("cmd")
        encoding = resource_config.get("encoding")
        wait = int(resource_config.get("wait") or 1)
        if auth_config := resource_config.get("auth"):
            auth = self._load_auth(auth_config)
        else:
            auth = None

        if filters_config := resource_config.get("filters"):
            filters = self._load_filters(filters_config)
        else:
            filters = []

        if not ((url is not None) ^ ((cmd or env) is not None)):
            raise ConfigLoadError(f"we couldn't determine resource type: {resource_config}")

        if url:
            return HttpResource(
                resource_id=resource_id,
                notifier=notifier,
                url=url,
                enabled=enabled,
                title=title,
                auth=auth,
                filters=filters,
                wait=wait,
                encoding=encoding,
            )
        elif cmd:
            return CommandResource(
                resource_id=resource_id,
                notifier=notifier,
                cmd=cmd,
                env=env or dict(),
                enabled=enabled,
                title=title,
                filters=filters,
                wait=wait,
            )
        else:
            raise NotImplementedError()

    def _get_template(self, template_id: str) -> Dict[str, Dict]:
        if self.templates:
            try:
                return self.templates[template_id]
            except KeyError:
                raise ConfigLoadError(f"No such template: {template_id}")
        else:
            raise ConfigLoadError("You need to set `templates`")

    def _load_templates(self, templates_config: Dict[str, Dict]) -> Dict[str, Dict]:
        if not isinstance(templates_config, dict):
            raise ConfigLoadError(f"`templates` must be dict")
        templates = dict()
        for template_key, template_config in templates_config.items():
            templates[template_key] = template_config
        return templates

    def _load_auth(self, auth_config: Dict[str, Dict]) -> AuthBase:
        if not isinstance(auth_config, dict):
            raise ConfigLoadError(f"`auth` must be dict: {auth_config}")

        if basic := auth_config.get("basic"):
            try:
                username = basic["username"]
                password = basic["password"]
                return HTTPBasicAuth(username, password)
            except Exception:
                raise ConfigLoadError(f"format error on basic auth config: {basic}")
        else:
            raise ConfigLoadError(f"Unsupported authentication method")

    def _load_filters(self, filters_config: List) -> List[Filter]:
        if not isinstance(filters_config, list):
            raise ConfigLoadError(f"`filters` must be list: {filters_config}")

        filters = []
        for filter_config in filters_config:
            filters.append(self._load_filter(filter_config))
        return filters

    def _load_filter(self, filter_config: Dict[str, Dict]) -> Filter:
        if not isinstance(filter_config, dict):
            raise ConfigLoadError(f"`filter` must be dict: {filter_config}")

        if _type := filter_config.get("type"):
            try:
                if _type == "selector":
                    return CssSelectorFilter(filter_config["selector"])
                elif _type == "cmd":
                    return CommandFilter(filter_config["cmd"])
                elif _type == "text":
                    return TextContentFilter()
                else:
                    raise ConfigLoadError(f"Unsupported filter type")
            except KeyError as e:
                raise ConfigLoadError(f"KeyError occurred on parsing: {filter_config}, {e}")
        else:
            raise ConfigLoadError(f"`filter` must specify type: {filter_config}")
