from abc import ABC, abstractmethod
from typing import List, Union, Optional
from datalogue.errors import DtlError


class DataExtractionRule(ABC):
    def __init__(self, extraction_type: str):
        self.type = extraction_type

    def _base_payload(self) -> dict:
        return {"type": self.type}

    def __eq__(self, other: "DataExtractionRule"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    @abstractmethod
    def _as_payload(self) -> dict:
        """
        :return: Dictionary representation of the Data Extraction Rule
        """


class IgnorePrefix(DataExtractionRule):
    def __init__(self, prefix: str):
        super().__init__("IgnorePrefix")
        self.prefix = prefix

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["prefix"] = self.prefix
        return base


class PipelineBehavior(ABC):
    def __init__(self, behaviour_type: str):
        self.type = behaviour_type

    def _base_payload(self) -> dict:
        return {"type": self.type}

    def __eq__(self, other: "PipelineBehavior"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    @abstractmethod
    def _as_payload(self) -> dict:
        """
        :return: Dictionary representation of the Pipeline Behaviour
        """


class Write(PipelineBehavior):
    def __init__(self):
        """
        Create the target if nonexistant. Append the output records to the target if existing and if output schema is
        compatible with target schema. If schemas are incompatible, the job will fail.
        """
        PipelineBehavior.__init__(self, "Write")

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def _as_payload(self) -> dict:
        return self._base_payload()

    @staticmethod
    def _from_payload(_: dict) -> Union[DtlError, "Write"]:
        return Write()


class Upsert(PipelineBehavior):
    def __init__(self, key: List[str]):
        """
        Create the target if nonexistant. For existing targets, perform an upsert operation. For every output record,
        search existing records for a match in the specified primary key field. If a match is found, update the
        existing record.  If no match is found, append the new record. If schemas are incompatible, job will fail.
        :param key: List of keys to match on while performing an upsert operation
        """
        PipelineBehavior.__init__(self, "Upsert")
        self.key = key

    def __repr__(self):
        return f"{self.__class__.__name__}(key= {self.key})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["key"] = self.key
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Upsert"]:
        key = json.get("key")
        if key is None:
            return DtlError("A Upsert pipeline behavior needs a  'key' field")

        return Upsert(key)


class ChangeData(PipelineBehavior):
    def __init__(
        self,
        key: List[str],
        op_code_field: str,
        soft_delete_field: str = "DTL_DELETED",
        extraction_rules: List[DataExtractionRule] = [],
    ):
        """

        :param key: Primary key fields
        :param op_code_field:
        """
        PipelineBehavior.__init__(self, "ChangeData")
        self.key = key
        self.op_code_field = op_code_field
        self.soft_delete_field = soft_delete_field
        self.extraction_rules = extraction_rules

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(key= {self.key}, op_code_field= {self.op_code_field}, "
            f"soft_delete_field= {self.soft_delete_field}, extraction_rules= {self.extraction_rules!r})"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["key"] = self.key
        base["opCodeField"] = self.op_code_field
        base["softDeleteField"] = self.soft_delete_field
        base["extractionRules"] = self.extraction_rules
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "ChangeData"]:
        key = json.get("key")
        if key is None:
            return DtlError("A ChangeData pipeline behavior needs a 'key' field")

        op_code_field = json.get("opCodeField")
        if op_code_field is None:
            return DtlError("A ChangeData pipeline behavior needs a 'opCodeField' field")

        soft_delete_field = json.get("softDeleteField")
        if soft_delete_field is None:
            return DtlError("A ChangeData pipeline behavior needs a 'softDeleteField' field")

        extraction_rules = json.get("extractionRules")
        if extraction_rules is None:
            return DtlError("A ChangeData pipeline behavior needs a 'extractionRules' field")

        return ChangeData(key, op_code_field, soft_delete_field, extraction_rules)

    @staticmethod
    def get_change_data_for_informatica_flat(keys: List[str], soft_delete_field: str = "DTL_DELETED") -> "ChangeData":
        return ChangeData(keys, "INFA_OP_TYPE", soft_delete_field, [IgnorePrefix("INFA_"), IgnorePrefix("DTL__")],)

    @staticmethod
    def get_change_data_for_informatica_nested(keys: List[str], soft_delete_field: str = "DTL_DELETED") -> "ChangeData":
        # to be implemented
        pass

    @staticmethod
    def get_change_data_for_informatica_generic(
        keys: List[str], soft_delete_field: str = "DTL_DELETED"
    ) -> "ChangeData":
        # to be implemented
        pass

    @staticmethod
    def get_change_data_for_informatica_wrapped(keys: List[str], soft_delete_field: str = "DTL_DELETE") -> "ChangeData":
        # to be implemented
        pass


_behavior_parsing_map = dict(
    [("Write", Write._from_payload), ("Upsert", Upsert._from_payload), ("ChangeData", ChangeData._from_payload),]
)


def _pipeline_behavior_from_payload(json: dict) -> Union[DtlError, PipelineBehavior]:
    type_field = json.get("type")
    if type_field is None:
        return DtlError("The PipelineBehavior should have a field 'type'")

    parsing_function = _behavior_parsing_map.get(type_field)
    if parsing_function is None:
        return DtlError("Looks like '%s' pipeline behavior is not handled by the SDK" % type_field)

    return parsing_function(json)


class SourceBehavior(ABC):
    def __init__(self, behaviour_type: str):
        self.type = behaviour_type

    def _base_payload(self) -> dict:
        return {"type": self.type}

    def __eq__(self, other: "SourceBehavior"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    @abstractmethod
    def _as_payload(self) -> dict:
        """
        :return: Dictionary representation of the Source Behaviour
        """


class Read(SourceBehavior):
    def __init__(self):
        SourceBehavior.__init__(self, "Read")

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def _as_payload(self) -> dict:
        return self._base_payload()

    @classmethod
    def _from_payload(cls, _: dict) -> Union[DtlError, "Read"]:
        return cls()


class ChangeDataCapture(SourceBehavior):
    def __init__(self, primary_keys: List[str]):
        SourceBehavior.__init__(self, "ChangeData")
        self.primary_keys = primary_keys

    def __repr__(self):
        return f"{self.__class__.__name__}(primary_keys = {self.primary_keys})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["primaryKey"] = self.primary_keys
        return base

    @classmethod
    def _from_payload(cls, json: dict) -> Union[DtlError, "ChangeDataCapture"]:
        primary_keys = json.get("primaryKey")
        if primary_keys is None:
            return DtlError("A ChangeDataCapture source behavior needs a 'primaryKeys' field")
        return cls(primary_keys)


_source_behavior_map = dict([("Read", Read._from_payload), ("ChangeData", ChangeDataCapture._from_payload)])


def _source_behavior_from_payload(json: dict) -> Union[DtlError, SourceBehavior]:
    type_field = json.get("type")
    if type_field is None:
        return DtlError("The SourceBehavior should have a field 'type'")

    parsing_function = _source_behavior_map.get(type_field)
    if parsing_function is None:
        return DtlError("Looks like %s source behavior is not handled by the SDK" % type_field)

    return parsing_function(json)
