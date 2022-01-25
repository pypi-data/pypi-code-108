"""
Loading and interpretation of model metadata.
"""
import io
import json
import os
import typing
import jsonschema
import yaml


class Metadata(object):
    """
    Information about a model, including metadata/schema about parameters, inputs and outputs.

    The mlflow MLProject file is used as a point of reference.  We extend it in various ways but aspire to remain
    compatible with it.
    """
    def __init__(self, entry_points: dict=None, uri: str=None):
        """
        :param entry_points:    Definition of each entry point.  A mapping from a name to a {} compatible with the schema.
        :param uri:             Uniquely identifies the model.
        """
        self.uri = uri or ""
        self.entry_points = {name: EntryPoint(**ep_info) for name, ep_info in (entry_points or {}).items()}

    @staticmethod
    def from_json(data):
        jsonschema.validate(data, METADATA_SCHEMA)
        return Metadata(**data)

    def to_json(self):
        return {
            "uri": self.uri,
            "entry_points": {name: info.to_json() for name, info in self.entry_points.items()}
        }

    @staticmethod
    def from_file(source: (str, io.IOBase)):
        """
        Load from a JSON or YAML file.

        :param source:   A filename or file-like object.
        """
        if isinstance(source, str):
            with open(source, 'r') as f_r:
                return Metadata.from_file(f_r)
        raw = source.read().strip()
        if not isinstance(raw, str):
            raw = raw.decode("utf-8")
        if raw.startswith("{"):
            data = json.loads(raw)
        else:
            data = yaml.safe_load(raw)
        return Metadata.from_json(data)

    @staticmethod
    def from_folder(folder: str, fill_default: bool=True):
        """
        Load metadata from specially named files in a given folder.
        """
        for f in ("metadata.yaml", "metadata.json", "MLProject"):
            fn = os.path.join(folder, f)
            if os.path.exists(fn):
                return Metadata.from_file(fn)
        # TODO check for mlflow schemas defined as YAML (where???)
        if fill_default:
            return Metadata()


class EntryPoint(object):
    """
    Describes one 'entry point' for a model, i.e. 'main', 'training', etc..
    """
    def __init__(self, command: str = None, parameters: dict = None, inputs: typing.Iterable[dict] = None,
                 outputs: typing.Iterable[dict] = None):
        self.command = command or ""
        self.parameters = {param: ParameterMetadata(**param_spec) for param, param_spec in
                           (parameters or {}).items()}
        self.inputs = {name: TableMetadata(name, **table) for name, table in (inputs or {}).items()}
        self.outputs = {name: TableMetadata(name, **table) for name, table in (outputs or {}).items()}

    def source_path(self):
        """
        Parse the source path out of the command.
        """
        # TODO code me

    @staticmethod
    def from_json(data):
        jsonschema.validate(data, METADATA_SCHEMA)
        return EntryPoint(**data)

    def to_json(self):
        return {
            "parameters": {param: param_info.to_json() for param, param_info in self.parameters.items()},
            "inputs": {name: table.to_json() for name, table in self.inputs.items()},
            "outputs": {name: table.to_json() for name, table in self.outputs.items()}
        }


class ParameterMetadata(object):
    """
    Description of parameters.
    """
    def __init__(self, type: str=None, default=None, schema: dict=None):
        self.type = type
        self.default = default
        self.schema = schema

    def to_json(self):
        out = {}
        if self.type:
            out["type"] = self.type
        if self.default is not None:
            out["default"] = self.default
        if self.schema:
            out["schema"] = self.schema
        return out

    def process_value(self, value):
        """
        Validate an input value, fill in default, and coerce to expected type.
        """
        if value is None:
            value = self.default
        if self.type == "float":
            value = float(value)
        else:
            value = str(value)
        # TODO validate 'path' and 'uri'
        if self.schema:
            value = json.loads(value)
            jsonschema.validate(value, self.schema)
        return value


class TableMetadata(object):
    """
    Description of input and output data.
    """
    def __init__(self, name: str, columns: list):
        self.name = name
        self.columns = columns

    def to_json(self):
        out = {
            "columns": self.columns
        }
        return out


METADATA_SCHEMA = {
    "comment": "Information about each distinct function the model is capable of performing.",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "uri": {
            "comment": "Unique identifier for the model.",
            "type": "string"
        },
        # TODO add in remaining defined values for MLProject: https://www.mlflow.org/docs/latest/projects.html
        "entry_points": {
            "type": "object",
            "patternProperties": {
                ".+": {
                    "comment": "Each entry point is described here.",
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "parameters": {
                            "comment": "Parameters the model can accept for this entry point.",
                            "type": "object",
                            "patternProperties": {
                                ".+": {
                                    "comment": "Parameter is described here.",
                                    "oneOf": [
                                        {
                                            "comment": "MLProject files let you specify a very constrained data type",
                                            "type": "string", "enum": ["path", "uri", "float", "string"]
                                        },
                                        {
                                            "comment": "MLProject files let you define a parameter with these fields.",
                                            "type": "object",
                                            "required": ["type"],
                                            "additionalProperties": False,
                                            "properties": {
                                                # NOTE: the 'path' and 'uri' types imply a file-like input data source
                                                "type": {"type": "string", "enum": ["path", "uri", "float", "string"]},
                                                "default": {"comment": "Default value"},
                                                "schema": {
                                                    # EXTENSION to MLProject to support validation of structured data types
                                                    "comment": "For type=string, a JSON schema can be imposed.",
                                                    "type": "object",
                                                    "properties": {
                                                        "type": {},
                                                        "required": {"type": "array"},
                                                        "properties": {},
                                                        "additionalProperties": {"type": "boolean"},
                                                        "pattern": {"type": "string"}
                                                        # additional JSON schema fields are allowed here
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        "command": {
                            "comment": "Command to execute for this model",
                            "type": "string"
                        },
                        # EXTENSION to MLProject to define schemas for input data sources
                        "inputs": {
                            "comment": "Information about data inputs",
                            "type": "object",
                            "patternProperties": {
                                ".+": {
                                    "$ref": "#/definitions/table"
                                }
                            }
                        },
                        # EXTENSION to MLProject to define schemas for data outputs
                        "outputs": {
                            "comment": "Information about data inputs",
                            "type": "object",
                            "patternProperties": {
                                ".+": {
                                    "$ref": "#/definitions/table"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "table": {
            "type": "object",
            "properties": {
                "columns": {
                    "comment": "Column names and data types, for columnar data.",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name"],
                        "properties": {
                            "name": {
                                "comment": "Short name by which the data will be referenced from the code.",
                                "type": "string"
                            },
                            "type": {
                                "comment": "Broad data type",
                                "enum": ["number", "string", "integer", "boolean"]
                            },
                            "required": {
                                "comment": "Which fields are required.",
                                "type": "array"
                            }
                        }
                    }
                }
            }
        }
    }
}
