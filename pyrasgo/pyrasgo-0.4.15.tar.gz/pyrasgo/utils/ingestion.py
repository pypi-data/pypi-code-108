from types import FunctionType

from collections import OrderedDict
import logging
import os
import yaml

from pyrasgo.primitives import DataSource
from pyrasgo.schemas import DataType, FeaturesYML


RASGO_DICT: dict = {
"name": "optional name for DataSource",
"sourceTable": "mandatory DB.SCHEMA.TABLE features are stored in",
"features": [
                {
                    "columnName": "mandatory_field_name_in_table",
                    "displayName": "Optional Pretty Name",
                    "dataType": "mandatory sql type",
                    "description": "optional display text",
                    "status": "Productionized | Sandboxed",
                    "tags": [
                                "optional",
                                "list of strings",
                                "apply only to this feature"
                            ],
                    "attributes":  [
                                        {"key": "value"},
                                        {"optional": "apply only to this features"}
                                   ]
                }
            ],
"dimensions": [
                {
                    "columnName": "mandatory_field_name_in_table",
                    "displayName": "Optional Pretty Name",
                    "dataType": "mandatory sql type",
                    "granularity": "mandatory noun ..."
                }
            ],
"tags": [
            "optional",
            "list of strings",
            "apply to all features"
        ],
"attributes": [
                {"key": "value"},
                {"optional": "apply to all features"}
              ],
"sourceCode": "Optional valid SQL or python string",
"sourceType": "Table | CSV | Dataframe"
}

def load_features_from_yaml(*, file_name: str, directory: str = None) -> DataSource:
    if directory is None:
        directory = os.getcwd()

    if os.path.splitext(f"{directory}/{file_name}")[1] in ['yaml', 'yml']:
        raise ValueError("Must provide valid yaml file")

    with open(f"{directory}/{file_name}") as _yaml:
        return DataSource(api_object=yaml.load(_yaml, Loader=yaml.SafeLoader))

def load_features_from_dict(*, features_dict: dict) -> DataSource:
    return DataSource(api_object=features_dict)

def save_features_to_yaml(data_source: FeaturesYML, *,
                          file_name: str,
                          directory: str = None,
                          overwrite: bool = True) -> None:
    if directory is None:
        directory = os.getcwd()

    if directory[-1] == "/":
        directory = directory[:-1]

    if file_name.split(".")[-1] not in ['yaml', 'yml']:
        file_name += ".yaml"

    if os.path.exists(f"{directory}/{file_name}") and overwrite:
        logging.warning(f"Overwriting existing file {file_name} in directory: {directory}")

    safe_dumper = yaml.SafeDumper
    safe_dumper.add_representer(DataType, lambda self, data: self.represent_str(str(data.value)))
    safe_dumper.add_representer(OrderedDict, lambda self, data: self.represent_mapping('tag:yaml.org,2002:map',
                                                                                       data.items()))
    safe_dumper.ignore_aliases = lambda self, data: True

    with open(f"{directory}/{file_name}", "w") as _yaml:
        yaml.dump(data=OrderedDict(data_source.dict(exclude_unset=True, by_alias=True)), Dumper=safe_dumper, stream=_yaml)

def save_features_to_dict(data_source: DataSource, overwrite: bool = True) -> dict:
    return FeaturesYML(
        name = data_source.name,
        sourceTable = data_source.dataTable.fqtn,
        dimensions = [{"columnName": d.columnName, "dataType": d.dataType, "granularity": d.granularity.name} for d in data_source.dimensions],
        features = data_source.features,
        sourceCode = data_source.sourceCode,
        sourceType = data_source.sourceType
    ).dict(exclude_unset=False, by_alias=True)

def _confirm_valid_dict(dict_in: dict, version: int = None) -> bool:
    if not dict_in.get("sourceTable"):
        print("Missing table")
        return False
    if not dict_in.get("features"):
        print("Missing features")
        return False
    for f in dict_in.get("features"):
        if not f.get("columnName") or not f.get("dataType"):
            print("Missing feature attributes")
            return False
    if not dict_in.get("dimensions"):
        print("Missing dimensions")
        return False
    for d in dict_in.get("dimensions"):
        if not d.get("columnName") or not d.get("dataType") or not d.get("granularity"):
            print("Missing dimension attributes")
            return False
    return True