import sys
from typing import Dict, Optional, Union, List
from uuid import UUID

import pandas as pd

from datalogue.errors import DtlError
from datalogue.models.graph import Graph, Node, NodeDef, Path
from datalogue.dtl_utils import (
    _parse_string_list,
    _parse_list,
    _parse_datetime,
    _parse_uuid,
    map_option,
    SerializableStringEnum,
)
from datetime import datetime
from datalogue.errors import _enum_parse_error


class ClassificationType(SerializableStringEnum):
    Automatic = "Automatic"
    Manual = "Manual"
    Audit = "Audit"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("stream state", s))

    @staticmethod
    def classification_type_from_str(string: str,) -> Union[DtlError, "ClassificationType"]:
        return SerializableStringEnum.from_str(ClassificationType)(string)


class Classification:
    """
    Represents the mapping and application of a class to a field. To edit classifications, please use the add, remove, and override commands of the dtl.datastore client. 
    """

    def __init__(
        self,
        class_id: UUID,
        classification_type: ClassificationType,
        class_name: str,
        class_path: List[str],
        ontology_id: UUID,
        classifier_id: Optional[UUID],
        score: float,
        created_at: datetime,
        created_by: Optional[UUID],
    ):
        self.class_id = class_id
        self.classification_type = classification_type
        self.class_name = class_name
        self.class_path = class_path
        self.ontology_id = ontology_id
        self.classifier_id = classifier_id
        self.score = score
        self.created_at = created_at
        self.created_by = created_by

    def __repr__(self):
        return f"(class_name= {self.class_name}, score= {self.score})"

    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "Classification"]:
        class_id = map_option(payload.get("classId"), _parse_uuid)
        if class_id is None:
            return DtlError("Classification has to have a 'classId' key")

        if class_id is DtlError:
            return class_id

        classification_type = map_option(
            payload.get("classificationType"), ClassificationType.classification_type_from_str,
        )
        if classification_type is None:
            return DtlError("Classification has to have a 'classificationType' key")

        if classification_type is DtlError:
            return classification_type

        ontology_id = map_option(payload.get("ontologyId"), _parse_uuid)
        if ontology_id is None:
            return DtlError("SchemaNode has to have a 'ontologyId' key")

        classifier_id = map_option(payload.get("classifierId"), _parse_uuid)

        score = payload.get("score")
        if score is None:
            return DtlError("Classification has to have a 'score' key")

        created_at = map_option(payload.get("createdAt"), _parse_datetime)
        if isinstance(created_at, DtlError):
            return created_at

        created_by = map_option(payload.get("createdBy"), _parse_uuid)
        if isinstance(created_by, DtlError):
            return created_by

        return Classification(
            class_id, classification_type, None, None, ontology_id, classifier_id, score, created_at, created_by,
        )


class SchemaNode(Node):
    """
    Describes schema node
    """

    def __init__(
        self, id: UUID, label: str, data_type: str, metadata: Dict[str, str], classifications: List[Classification],
    ):
        """
        Builds SchemaNode object

        :param id: schema node id
        :param label: column name
        :param data_type: type of the data
        :param metadata: can be used to enrich the field with mapping of user-defined key:value pairs (via the dtl.datastore.metadata methods)
        """

        self.id = id
        self.label = label
        self.dataType = data_type
        self.metadata = metadata
        self.classifications = classifications
        Node.__init__(self, id, label)

    def __repr__(self):
        classificationStr = ", ".join(list(map(lambda c: str(c), self.classifications)))
        if not bool(self.metadata):
            metadataStr = None
        else:
            metadataStr = self.metadata

        return (
            "SchemaNode("
            f"id= {self.id}, "
            f"label= {self.label}, "
            f"dataType= {self.dataType}, "
            f"metadata= {metadataStr}, "
            f"\n\tclassifications= [{classificationStr}]\n)"
        )

    @staticmethod
    def _as_payload(self) -> Union[DtlError, dict]:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """

        return {"id": self.id, "label": self.label, "dataType": self.dataType}

    def _schema_node_from_payload(json: dict) -> Union[DtlError, "SchemaNode"]:
        node_id = json.get("id")
        if node_id is None:
            return DtlError("SchemaNode has to have a 'id' key")

        label = json.get("label")
        if label is None:
            return DtlError("SchemaNode has to have a 'label' key")

        dataType = json.get("dataType")
        classifications = _parse_list(Classification._from_payload)(json.get("classifications"))
        if isinstance(classifications, DtlError):
            return classifications

        metadata = json.get("metadata")
        if metadata is None or not isinstance(metadata, dict):
            return DtlError("'metadata' is missing or not a dictionary")

        return SchemaNode(node_id, label, dataType, metadata, classifications)


class GraphSampleNode(Node):
    """
    Describes schema node
    """

    def __init__(self, id: UUID, label: str, value: str):
        """
        Builds SchemaNode object

        :param id: schema node id
        :param label: column name
        :param value: value of the data
        """

        self.id = id
        self.label = label
        self.value = value
        Node.__init__(self, id, label)

    def _sample_node_from_payload(json: dict) -> Union[DtlError, "GraphSampleNode"]:
        node_id = json.get("id")
        if node_id is None:
            return DtlError("SampleNode has to have a 'id' key")

        label = json.get("label")
        if label is None:
            return DtlError("SampleNode has to have a 'label' key")

        value = json.get("value")
        if "value" not in json:
            return DtlError("SampleNode has to have a 'value' key")

        return GraphSampleNode(str(node_id), label, value)


class AbstractDataGraph(Graph):
    node_decoder = GraphSampleNode._sample_node_from_payload


class AbstractDataSchema(Graph):
    node_decoder = SchemaNode._schema_node_from_payload


class SchemaOntologyRow:
    """
    Represents printable representation of schema, its associated ontology & samples data.
    """

    def __init__(self, schema_node_def: NodeDef, samples: List[AbstractDataGraph]):
        self.schema_node_def = schema_node_def
        self.samples = samples

    def to_array(self, is_full_path: bool):
        def get_sample_val(index: int, full_path: Path):
            if len(self.samples) > index:
                sample = self.samples[index]
                return sample.path_to_node[full_path].node.value
            else:
                return None

        schema_node = self.schema_node_def.node
        full_path = self.schema_node_def.full_path
        sample_1_val = get_sample_val(0, full_path)
        sample_2_val = get_sample_val(1, full_path)
        sample_3_val = get_sample_val(2, full_path)
        ontology_node_id = schema_node.ontologyNodeId
        if ontology_node_id is None:
            ontology_node_id = '""'
        if not is_full_path:
            if schema_node.ontologyNodePath is not None and len(schema_node.ontologyNodePath) > 0:
                ontology_node_label = schema_node.ontologyNodePath[-1]
            else:
                ontology_node_label = '""'
            return [
                schema_node.id,
                schema_node.label,
                schema_node.dataType,
                ontology_node_label,
                ontology_node_id,
                sample_1_val,
                sample_2_val,
                sample_3_val,
            ]
        else:
            if schema_node.ontologyNodePath is not None:
                ontology_node_label = schema_node.ontologyNodePath
            else:
                ontology_node_label = ['""', '""']
            return [
                schema_node.id,
                self.schema_node_def.full_path,
                schema_node.dataType,
                ontology_node_label,
                ontology_node_id,
                sample_1_val,
                sample_2_val,
                sample_3_val,
            ]


class Schema:
    """
    Represents a schema.
    """

    def __init__(
        self, data_schema: AbstractDataSchema, samples: Optional[List[AbstractDataGraph]],
    ):
        """
        Represents a schema structure

        :param data_schema: Represents data schema
        :param samples: A collection of samples data with the same structure as data_schema
        """

        self.data_schema = data_schema
        self.samples = samples

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Schema"]:
        schema = json.get("schema")
        samples_json = json.get("samples")
        if schema is None:
            return DtlError("Schema has to have a 'schema' key")
        if samples_json is None:
            return DtlError("Schema has to have a 'samples' key")
        ads = AbstractDataSchema._from_payload(schema, AbstractDataSchema.node_decoder)

        if samples_json is None:
            adg = None
        else:
            adg = []
            for obj in samples_json:
                parsed_obj = AbstractDataGraph._from_payload(obj, AbstractDataGraph.node_decoder)

                if isinstance(parsed_obj, DtlError):
                    return parsed_obj
                else:
                    adg.append(parsed_obj)
        return Schema(ads, adg)

    def print(self, full_path: bool):
        pd.set_option("max_colwidth", 29)
        nodes_def = self.data_schema.get_nodes()
        res = []
        if len(nodes_def) > 1000:
            return DtlError("Extremely large schema, please contact Datalogue support to enable larger schemas")
        for node_def in nodes_def:
            res.append(SchemaOntologyRow(node_def, self.samples).to_array(full_path))
        df = pd.DataFrame(
            pd.np.array(res),
            columns=[
                "schema_node_id",
                "schema_node_name",
                "schema_node_type",
                "ontology_node_name",
                "ontology_node_id",
                "sample1",
                "sample2",
                "sample3",
            ],
        )
        sys.stdout.write(df.to_string(index=False))
