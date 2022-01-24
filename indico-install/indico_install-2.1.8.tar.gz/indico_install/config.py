import os
from collections import OrderedDict
from pathlib import Path

import yaml

CLUSTER_NAME = os.getenv("CLUSTER_NAME", "cluster")
REMOTE_TEMPLATES_PATH = os.getenv("REMOTE_TEMPLATES_PATH", "https://storage.googleapis.com/indico-templates/")
D_ROOT = os.getenv("INDICO_DEPLOYMENT_ROOT", os.getcwd())
D_PATH = Path(D_ROOT)

INPUT_YAML = D_PATH / "values" / f"{CLUSTER_NAME}.yaml"
SERVICES_YAML = D_PATH / "values" / "services.yaml"


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode("tag:yaml.org,2002:map", value)


yaml.add_representer(OrderedDict, represent_ordereddict)


def merge_dicts(dict1, dict2):
    # dict2 overwrites dict1
    return dict(_merge_dicts(dict1, dict2))


def _merge_dicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(_merge_dicts(dict1[k], dict2[k])))
            elif (
                k == "env" and isinstance(dict1[k], list) and isinstance(dict2[k], list)
            ):
                resulting_envs = {}
                order = []
                for envvar in dict1[k] + dict2[k]:
                    name = envvar.pop("name")
                    if name not in order:
                        order.append(name)
                    resulting_envs[name] = envvar

                if "PODNAME" in order:
                    # We want to prioritize PODNAME because we tend to use it in other vars
                    order.remove("PODNAME")
                    order.append("PODNAME")

                yield (
                    k,
                    [dict(name=name, **resulting_envs[name]) for name in order[::-1]],
                )
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


class ConfigsHolder(dict):
    def __init__(self, config):
        self.config_path = config if isinstance(config, Path) else Path(config)
        self.config_path = self.config_path.resolve()
        assert self.config_path.is_file(), f"Cannot find {self.config_path}."
        self.reload()

    def reset(self, key):
        path = self
        path_keys = key.split(".")
        val_key = path_keys.pop()
        for k in path_keys:
            path = path[k]
        if isinstance(path[val_key], dict):
            for k in path[val_key].keys():
                if path[val_key][k] is not None:
                    self.reset(f"{key}.{k}")
        elif isinstance(path[val_key], list):
            path[val_key] = []
        elif isinstance(path[val_key], int):
            path[val_key] = 0
        else:
            path[val_key] = ""

    def reload(self):
        with open(self.config_path, "r") as f:
            _configs = yaml.safe_load(f)
            self.ordered_keys = list(_configs.keys())
        self.update(merge_dicts(self, _configs))

    def save(self):
        with open(self.config_path, "w") as f:
            resulting_dict = OrderedDict()
            for key in self.ordered_keys:
                resulting_dict[key] = self[key]
            for key, value in self.items():
                if key not in self.ordered_keys:
                    resulting_dict[key] = value
            yaml.dump(resulting_dict, f, default_flow_style=False)


class ConfigsLoader(dict):
    def __init__(self, *configs, **override):
        resolved = {}
        for config in configs:
            resolved = merge_dicts(resolved, self.load(config))

        resolved = merge_dicts(resolved, override)
        self.update(resolved)

    def load(self, config):
        with open(config, "r") as f:
            _configs = yaml.safe_load(f)
        return _configs

    def save(self, output):
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, "w") as f:
            yaml.dump(dict(self.items()), f, default_flow_style=False)
