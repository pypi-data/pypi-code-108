import defusedxml.ElementTree as ET
import os
import collections.abc

from typing import Any, Iterable


class Model(collections.abc.MutableMapping):
    """Connects a model source file with its associated XML parameter file"""

    def __init__(self, modelica_file: str, xml_model_file: str = None) -> None:
        """Initialise a new model instance from a modelica file

        Parameters
        ----------
        modelica_file : str
            Modelica model source file
        xml_model_file : str, optional
            XML file containing model parameters, by default None

        Raises
        ------
        FileNotFoundError
            if specified XML file does not exist
        """
        self._model_source = modelica_file
        if xml_model_file:
            self._model_xml = xml_model_file

            if not os.path.exists(xml_model_file):
                raise FileNotFoundError(
                    "Could not extract parameters, " f"no such file '{xml_model_file}"
                )

            self._parameters = {}

            with open(xml_model_file) as f:
                _xml_obj = ET.parse(xml_model_file).getroot()
                _vars = list(_xml_obj.iterfind("ModelVariables"))[0]

            for i, var in enumerate(_vars):
                # Do not store derivatives etc
                if "(" in var.attrib["name"]:
                    continue
                _type_info = list(var)[0].attrib
                _om_type = list(var)[0].tag

                _value = _type_info["start"] if "start" in _type_info else None

                _type, _value = self._get_type(_value, _om_type)

                self._parameters[var.attrib["name"]] = {
                    "id": i,
                    "value": _value,
                    "type": _type,
                }

    def _get_type(self, value, om_type):
        if om_type == "Boolean":
            return bool, value.title() == "True" if value else value
        elif om_type == "Integer":
            return int, int(value) if value else value
        elif om_type == "Real":
            return float, float(value) if value else value
        elif om_type == "String":
            return str, value or value
        else:
            # TODO: Definitely other types
            return None, value

    def get_source_path(self) -> str:
        """Retrieve the Modelica source file path

        Returns
        -------
        str
            path to the Modelica source file
        """
        return self._model_source

    def write_params(self) -> None:
        """Write parameter values to the XML file"""
        _xml_obj = ET.parse(self._model_xml)
        _iter_obj = _xml_obj.findall("ModelVariables/ScalarVariable")

        for i, item in enumerate(_iter_obj):
            # Do not write derivatives/functions
            if "(" in item.attrib["name"]:
                continue

            _name = item.attrib["name"]

            if (
                not self._parameters[_name]["value"]
                and self._parameters[_name]["value"] != 0
            ):
                continue

            # Booleans are lower case in the XML
            if self._parameters[_name]["type"] == bool:
                _new_val = str(self._parameters[_name]["value"]).lower()
            else:
                _new_val = str(self._parameters[_name]["value"])

            if _new_val:
                _xml_obj.findall("ModelVariables/ScalarVariable")[i][0].set(
                    "start", _new_val
                )
        _xml_obj.write(self._model_xml)

    def set_parameter(self, param_name: str, value: Any) -> None:
        """Set parameter in XML to a given value

        Parameters
        ----------
        param_name : str
            name of parameter within XML file
        value : Any
            new value for the parameter
        """
        self._parameters[param_name]["value"] = value

    def get_parameter(self, param_name: str) -> Any:
        """Retrieve a parameter value by name

        Parameters
        ----------
        param_name : str
            name of the parameter to retrieve the value of

        Returns
        -------
        Any
            value of the given parameter

        Raises
        ------
        AssertionError
            If the returned value is a dictionary as opposed to numeric/string
        """
        if isinstance(self._parameters[param_name]["value"], dict):
            raise AssertionError(
                "Expected non-mutable value for requested parameter"
                f"'{param_name}' but got type 'dict'"
            )
        return self._parameters[param_name]["value"]

    def get_om_parameter_type(self, param_name: str):
        """Returns parameter OM Type as Python type.

        E.g. "Boolean" -> bool

        Parameters
        ----------
        param_name : str
            name of parameter to search for
        """
        return self._parameters[param_name]["type"]

    def __iter__(self) -> Iterable:
        return iter(self._parameters)

    def __len__(self) -> int:
        return len(self._parameters)

    def __getitem__(self, key) -> Any:
        return self._parameters[key]

    def __setitem__(self, key, value) -> None:
        self._parameters[key] = value

    def __str__(self) -> str:
        return self.__repr__()

    def __delitem__(self, key) -> None:
        del self._parameters[key]

    def __repr__(self) -> str:
        _params = {k: v["value"] for k, v in self._parameters.items()}
        return f"OMModelProperties(params={_params})"

    def update(self, other) -> None:
        self._parameters.update(other._parameters)
