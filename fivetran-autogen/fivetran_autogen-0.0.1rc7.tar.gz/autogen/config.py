import yaml
from . import packages

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


class Config:
    def __init__(self, connector_selection):
        input = load_configuration(connector_selection)
        self.connector = connector_selection
        self.name = input["name"]
        self.version = input["version"]
        self.schema_variable = input["source_data_location"]["schema_variable"]
        self.database_variable = input["source_data_location"]["database_variable"]
        self.enabled_variables = input.get("enabled_variables", [])
        self.preset_variables = input.get("preset_variables", [])


def load_configuration(name: str):

    file = pkg_resources.read_text(packages, f"{name}.yml")
    configuration = yaml.safe_load(file)

    return configuration
