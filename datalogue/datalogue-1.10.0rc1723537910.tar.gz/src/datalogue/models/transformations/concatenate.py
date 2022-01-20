from datalogue.models.transformations.commons import Transformation
from datalogue.dtl_utils import _parse_string_list, _parse_list
from datalogue.errors import DtlError, _property_not_found
from typing import List, Union


class MergeFields(Transformation):
    """
    Concatenates data at different paths into a given output path.
    This transformation can be used to derive a new field or to replace
    an existing one with the concatenation output value.
    """

    type_str = "MergeFields"

    def __init__(self, paths: List[List[str]], output_path: List[str], delimiter: str):
        """
        :param paths: list of paths that point to the input data that
        will be concatenated.
        :param output_path: path for output of concatenation.
        :param delimiter: character used to concatenate all inputs together. 
        """
        Transformation.__init__(self, MergeFields.type_str)
        self.paths = paths
        self.output_path = output_path
        self.delimiter = delimiter

    def __eq__(self, other: "MergeFields"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"MergeFields(paths= {self.paths}, output_path= {self.output_path}, delimiter= {self.delimiter})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["inputFields"] = self.paths
        base["outputField"] = self.output_path
        base["delimiter"] = self.delimiter
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "MergeFields"]:
        paths = json.get("inputFields")
        output_path = json.get("outputField")
        delimiter = json.get("delimiter")

        if paths is None:
            return _property_not_found("inputFields", json)
        if output_path is None:
            return _property_not_found("outputField", json)
        if delimiter is None:
            return _property_not_found("delimiter", json)
        return MergeFields(paths=paths, output_path=output_path, delimiter=delimiter)


class ConcatenateAtPaths(Transformation):
    """
    Concatenates the data that reside at specified sibling nodes,
    This operation is performed[ in-place: specified nodes are collapsed to one node containing the result of the concatenation as the value,
    and the same label as in the original.
    """

    type_str = "ConcatenateAtPaths"

    def __init__(self, paths: List[List[str]]):
        """
        Paths --> List of Paths where the data to concatenate resides
        """
        Transformation.__init__(self, ConcatenateAtPaths.type_str)
        self.paths = paths

    def __eq__(self, other: "ConcatenateAtPaths"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ConcatenateAtPaths(paths= {self.paths})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["paths"] = self.paths
        return base

    @staticmethod
    def _list_paths_from_payload(value: dict) -> Union[List[List[str]], DtlError]:
        def is_list_of_list():
            return isinstance(value, List) and all(isinstance(item, List) for item in value)

        if value is not None and is_list_of_list():
            return _parse_list(_parse_string_list)(value)

        return DtlError(f"Could not parse operand: {value}")

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "ConcatenateAtPaths"]:
        paths = json.get("paths")
        if paths is None:
            return _property_not_found("paths", json)
        paths = ConcatenateAtPaths._list_paths_from_payload(paths)
        if isinstance(paths, DtlError):
            return paths

        return ConcatenateAtPaths(paths)
