from typing import List, Union, Optional
from uuid import UUID
from datalogue.errors import DtlError, _property_not_found
from datalogue.models.transformations.commons import RegexTransformation


class SplitLabelAndValue(RegexTransformation):
    """
    Finds all nodes that has a label matching to the given regex and attaches two child nodes. 
    One of the node contains the label as a value and the other contains the same value
    """

    type_str = "SplitLabelAndValue"

    def __init__(
        self, regex: Optional[str], regex_id: Optional[UUID], labelKey: str, valueKey: str,
    ):
        """
        :param regex: a string input to find which nodes should be split into two
        :param labelKey: label of node for label
        :param valueKey: label of node for value
        """
        RegexTransformation.__init__(self, regex, regex_id, SplitLabelAndValue.type_str)
        self.regex = regex
        self.regex_id = regex_id
        self.labelKey = labelKey
        self.valueKey = valueKey

    def __eq__(self, other: "SplitLabelAndValue"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"SplitLabelAndValue(regex= {self.regex}, regex_id= {self.regex_id}, labelKey= {self.labelKey}, valueKey= {self.valueKey})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        if self.regex is not None:
            base["regex"] = self.regex
        if self.regex_id is not None:
            base["regexId"] = str(self.regex_id)
        base["labelKey"] = self.labelKey
        base["valueKey"] = self.valueKey
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "SplitLabelAndValue"]:
        regex = json.get("regex")
        regex_id = json.get("regexId")

        if regex is None and regex_id is None:
            return _property_not_found("neither 'regex' nor 'regexId", json)

        labelKey = json.get("labelKey")
        if not isinstance(labelKey, str):
            return DtlError("labelKey field is not a string in %s transformation" % SplitLabelAndValue.type_str)

        valueKey = json.get("valueKey")
        if not isinstance(valueKey, str):
            return DtlError("valueKey field is not a string in %s transformation" % SplitLabelAndValue.type_str)

        return SplitLabelAndValue(regex, regex_id, labelKey, valueKey)
