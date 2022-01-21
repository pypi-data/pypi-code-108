from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, Union, NamedTuple
from uuid import UUID
from datetime import datetime
from dateutil.tz import UTC
from datalogue.errors import _enum_parse_error, DtlError
from datalogue.models.kinesis.shards import ShardAttributes
from datalogue.models.schema import AbstractDataSchema, SchemaNode, Classification
from datalogue.models.pipeline_behavior import (
    PipelineBehavior,
    _pipeline_behavior_from_payload,
    SourceBehavior,
    _source_behavior_from_payload,
)
from datalogue.dtl_utils import (
    _parse_list,
    _parse_string_list,
    SerializableStringEnum,
    _parse_uuid,
)
from datalogue.dtl_utils import map_option, _parse_datetime


class NodeClassification:
    """
    The mapping of a class to a field, as applied using the add, remove, and override commands of the dtl.datastore client.

    :param schema_node_id: the id of a schema field
    :param ontology_node_id: the class of a schema field
    :param score: the Confidence score for the classification, from 0.0 - 1.0 (defaults to 1.0)
    """

    def __init__(
        self, schema_node_id: Union[str, UUID], ontology_node_id: Union[str, UUID], score: float = 1.0,
    ):
        self.schema_node_id = schema_node_id
        self.ontology_node_id = ontology_node_id
        self.score = score

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"schema_node_id= {self.schema_node_id!r}, "
            f"ontology_node_id= {self.ontology_node_id!r},"
            f"score= {self.score!r}, "
        )

    def _as_payload(self) -> Union[DtlError, dict]:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        return {
            "schemaNodeId": str(self.schema_node_id),
            "classId": str(self.ontology_node_id),
            "score": str(self.score),
        }


class CredentialType(SerializableStringEnum):
    S3 = "S3"
    AmazonVendorCentral = "AmazonVendorCentral"
    GCS = "GCS"
    Azure = "Azure"
    JDBC = "Jdbc"
    Mongo = "Mongo"
    Http = "Http"
    Socrata = "Socrata"
    FileSystem = "FileSystem"
    Void = "Void"
    Kinesis = "Kinesis"
    Hadoop = "Hadoop"
    Kafka = "Kafka"
    Minio = "Minio"
    HadoopAzure = "HadoopAzure"
    Webhook = "Webhook"
    SFTP = "SFTP"
    Kerberos = "Kerberos"
    JaasString = "Kerberos"
    Neo4j = "Neo4j"
    ElasticSearch = "ElasticSearch"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("store type", s))

    @staticmethod
    def credential_type_from_str(string: str) -> Union[DtlError, "CredentialType"]:
        return SerializableStringEnum.from_str(CredentialType)(string)


class EncryptionType(SerializableStringEnum):
    AES256 = "AES256"
    KeyId = "KeyId"
    CustomerKey = "CustomerKey"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("encryption type", s))

    @staticmethod
    def encryption_type_from_str(string: str) -> Union[DtlError, "EncryptionType"]:
        return SerializableStringEnum.from_str(EncryptionType)(string)


class FileFormat(SerializableStringEnum):
    Json = "Json"
    Csv = "Csv"
    Text = "Text"
    Xml = "Xml"
    Html = "Html"
    Excel = "Excel"
    Avro = "Avro"
    Parquet = "Parquet"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("file format", s))

    @staticmethod
    def file_format_from_str(string: str) -> Union[DtlError, "FileFormat"]:
        return SerializableStringEnum.from_str(FileFormat)(string)


class HttpMethodType(SerializableStringEnum):
    PUT = "PUT"
    PATCH = "PATCH"
    POST = "POST"
    GET = "GET"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("file format", s))

    @staticmethod
    def method_type_from_str(string: str) -> Union[DtlError, "HttpMethodType"]:
        return SerializableStringEnum.from_str(HttpMethodType)(string)


class ResourceType(SerializableStringEnum):
    EventDirectory = "EventDirectory"
    SnapshotDirectory = "SnapshotDirectory"
    Unknown = "Unknown"
    File = "File"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("resource type", s))

    @staticmethod
    def resource_type_from_str(string: str) -> Union[DtlError, "ResourceType"]:
        return SerializableStringEnum.from_str(ResourceType)(string)


class Decompression(SerializableStringEnum):
    Gzip = "Gzip"
    Infer = "Infer"
    NonGzip = "None"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("decompression type", s))

    @staticmethod
    def decompression_from_str(string: str) -> Union[DtlError, "Decompression"]:
        return SerializableStringEnum.from_str(Decompression)(string)


class SchemaFormat(SerializableStringEnum):
    Avro = "Avro"
    Json = "Json"
    Protobuf = "Protobuf"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("schema format", s))

    @staticmethod
    def schema_format_from_str(string: str) -> Union[DtlError, "SchemaFormat"]:
        return SerializableStringEnum.from_str(SchemaFormat)(string)


class ChangeDataSource(SerializableStringEnum):
    InformaticaFlat = "InformaticaFlat"
    InformaticaNested = "InformaticaNested"
    InformaticaGeneric = "InformaticaGeneric"
    InformaticaWrapped = "InformaticaWrapped"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("Change Data Source", s))

    @staticmethod
    def change_data_source_from_str(string: str) -> Union[DtlError, "ChangeDataSource"]:
        return SerializableStringEnum.from_str(ChangeDataSource)(string)


class DatastoreDef(ABC):
    type_field = "type"
    id_field = "id"

    def __init__(self, credential_type: CredentialType, datastore_id: Optional[UUID] = None):
        self.type = credential_type
        self.datastore_id = datastore_id
        super().__init__()

    def __eq__(self, other: "DatastoreDef"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def _base_payload(self) -> dict:
        base = [(DatastoreDef.type_field, self.type.value)]
        if self.datastore_id is not None:
            base.append((DatastoreDef.id_field, str(self.datastore_id)))
        return dict(base)

    @abstractmethod
    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        pass


class Cell:
    """
        Describes a cell in html table
    """

    def __init__(
        self, label: str, span: int, index: int, total: int, tag: str, tagOverrides: [] = None,
    ):
        """
        Builds a cell

        :param label: text to display
        :param span: the html column span attribute
        :param index: index of this cell in the row
        :param total: total number of cells in the row
        """
        self.label = label
        self.span = span
        self.index = index
        self.total = total
        self.tag = tag
        self.tagOverrides = tagOverrides

    def __repr__(self):
        return f"{self.__class__.__name__}(label= {self.label!r}, span= {self.span!r}, \
                index= {self.index!r}, total= {self.total!r}, tag= {self.tag!r}, tagOverrides= {self.tagOverrides!r})"


def _cell_from_payload(json: dict) -> Union[DtlError, Cell]:
    label = json.get("label")
    if label is None:
        return DtlError("Cell has to have a 'label' key")

    span = json.get("span")
    if span is None:
        return DtlError("Cell has to have a 'span' key")

    index = json.get("index")
    if index is None:
        return DtlError("Cell has to have an 'index' key")

    total = json.get("total")
    if total is None:
        return DtlError("Cell has to have a 'total' key")

    return Cell(label, span, index, total, json.get("tag"), json.get("tagOverrides"))


class Datastore:
    """
    Represents a pointer to a datastore
    """

    def __init__(
        self,
        name: str,
        definition: DatastoreDef,
        credential_id: Optional[UUID] = None,
        alias: Optional[str] = None,
        datastore_id: Optional[UUID] = None,
        schema_paths: Optional[List[List[str]]] = None,
        schema_classes: Optional[List[List[str]]] = None,
        schema_labels: Optional[Set[str]] = None,
        schema_nodes: Optional[List[SchemaNode]] = None,
        ads: Optional[AbstractDataSchema] = None,
        tags: List[str] = [],
    ):
        """
        Builds a pointer to a datastore

        :param name: name of the pointer
        :param alias: unique alias accross the organization for the pointer
        :param definition: definition on how to access the data
        :param credential_id: reference to the Credential to access the data
        :param datastore_id: defined if the object was persisted, otherwise None
        :param schema_paths: Used to replace paths options on the cli
        :param schema_classes: Used to replace classes options on the cli
        :param schema_labels: Set of labels that exists in schema
        :param tags: Set of labels that exists in schema
        """
        self.id = datastore_id
        self.name = name
        self.alias = alias
        self.definition = definition
        self.definition.datastore_id = datastore_id
        self.credential_id = credential_id
        self.schema_paths = schema_paths
        self.schema_classes = schema_classes
        self.schema_labels = schema_labels
        self.schema_nodes = schema_nodes
        self.ads = ads
        self.tags = tags

    def __eq__(self, other: "Datastore"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id= {self.id}, name= {self.name!r}, alias= {self.alias!r}, "
            f"credential_id= {self.credential_id}, definition= {self.definition!r}, "
            f"schema_paths= {self.schema_paths!r}, schema_labels= {self.schema_labels!r}, "
            f"schema_nodes= {self.schema_nodes!r}, tags= {self.tags})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = {
            "name": self.name,
            "gate": self.definition._as_payload(),
        }
        if self.id is not None:
            base["id"] = str(self.id)

        if self.alias is not None:
            base["alias"] = self.alias

        if self.credential_id is not None:
            base["credentialsId"] = str(self.credential_id)

        return base


###############################################################################
#                              Cloud Storage
###############################################################################


class S3DatastoreDef(DatastoreDef):
    type_str = CredentialType.S3

    def __init__(
        self,
        bucket: str,
        key: str,
        file_format: FileFormat,
        params: Optional[Dict[str, str]] = None,
        datastore_id: Optional[UUID] = None,
    ):
        DatastoreDef.__init__(self, S3DatastoreDef.type_str, datastore_id)
        self.bucket = bucket
        self.key = key
        self.file_format = file_format
        self.params = params

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(bucket= {self.bucket!r}, key= {self.key!r}, "
            f"file_format= {self.file_format!r}, params= {self.params})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["bucket"] = self.bucket
        base["key"] = self.key
        base["format"] = self.file_format.value
        if self.params is not None:
            base["params"] = self.params
        return base


def _s3_datastore_def_from_payload(d: dict) -> Union[DtlError, S3DatastoreDef]:
    type_field = d.get(DatastoreDef.type_field)
    if not isinstance(type_field, str):
        return DtlError("string %s is missing from the json" % (DatastoreDef.type_field))

    if type_field != S3DatastoreDef.type_str.value:
        return DtlError("The object %s is not an S3 definition" % (str(d)))

    bucket = d.get("bucket")
    if bucket is None:
        return DtlError("'bucket' needs to be defined in an S3 definition")

    key = d.get("key")
    if key is None:
        return DtlError("'key' needs to be defined in an S3 definition")

    file_format = d.get("format")
    if file_format is None:
        return DtlError("'file_format' needs to be defined in an S3 definition")
    else:
        file_format = FileFormat.file_format_from_str(file_format)
        if isinstance(file_format, DtlError):
            return file_format

    params = d.get("params")
    datastore_id = d.get(DatastoreDef.id_field)

    return S3DatastoreDef(bucket, key, file_format, params, datastore_id)


class AVCOrderItemsDatastore(DatastoreDef):
    type_str = CredentialType.AmazonVendorCentral

    def __init__(
        self,
        marketplace_id: str,
        created_after: datetime,
        created_before: Optional[datetime],
        datastore_id: Optional[UUID] = None,
    ):
        DatastoreDef.__init__(self, AVCOrderItemsDatastore.type_str, datastore_id)
        self.marketplace_id = marketplace_id
        self.created_after = created_after
        self.created_before = created_before

    def __repr__(self):
        created_after_str = self.created_after.strftime("%Y-%m-%dT%H:%M:%SZ")
        created_before_str = None
        if self.created_before is not None:
            created_before_str = self.created_before.strftime("%Y-%m-%dT%H:%M:%SZ")
        return (
            f"AVCOrderItemsDatastore(marketplace_id= {self.marketplace_id!r}, created_after= {created_after_str!r}, "
            f"created_before= {created_before_str!r})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object  with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["marketplaceId"] = self.marketplace_id
        base["createdAfter"] = self.created_after.strftime("%Y-%m-%dT%H:%M:%SZ")
        if self.created_before is not None:
            base["createdBefore"] = self.created_before.strftime("%Y-%m-%dT%H:%M:%SZ")
        return base


def _avc_datastore_def_from_payload(d: dict) -> Union[DtlError, AVCOrderItemsDatastore]:
    type_field = d.get(DatastoreDef.type_field)
    if not isinstance(type_field, str):
        return DtlError("string %s is missing from the json" % (DatastoreDef.type_field))

    if type_field != AVCOrderItemsDatastore.type_str.value:
        return DtlError("The object %s is not a AVCOrderItemsDatastore definition" % (str(d)))

    marketplace_id = d.get("marketplaceId")
    if marketplace_id is None:
        return DtlError("'marketplaceId' needs to be defined in a AVCOrderItemsDatastore definition")

    created_after = map_option(d.get("createdAfter"), _parse_datetime)
    if created_after is None:
        return DtlError("'createdAfter' needs to be defined in a AVCOrderItemsDatastore definition")

    created_before = map_option(d.get("createdBefore"), _parse_datetime)
    store_id = d.get(DatastoreDef.id_field)

    return AVCOrderItemsDatastore(marketplace_id, created_after, created_before, store_id)


class GCSDatastoreDef(DatastoreDef):
    type_str = CredentialType.GCS

    def __init__(
        self,
        bucket: str,
        file_name: str,
        file_format: FileFormat,
        params: Optional[Dict[str, str]] = None,
        datastore_id: Optional[UUID] = None,
    ):
        DatastoreDef.__init__(self, GCSDatastoreDef.type_str, datastore_id)
        self.bucket = bucket
        self.file_name = file_name
        self.file_format = file_format
        self.params = params

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(bucket= {self.bucket!r}, file_name= {self.file_name!r}, "
            f"file_format= {self.file_format!r}, params= {self.params})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object  with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["bucket"] = self.bucket
        base["fileName"] = self.file_name
        base["format"] = self.file_format.value
        if self.params is not None:
            base["params"] = self.params
        return base


def _gcs_datastore_def_from_payload(d: dict) -> Union[DtlError, GCSDatastoreDef]:
    type_field = d.get(DatastoreDef.type_field)
    if not isinstance(type_field, str):
        return DtlError("string %s is missing from the json" % (DatastoreDef.type_field))

    if type_field != GCSDatastoreDef.type_str.value:
        return DtlError("The object %s is not a GCS definition" % (str(d)))

    bucket = d.get("bucket")
    if bucket is None:
        return DtlError("'bucket' needs to be defined in a GCS definition")

    file_name = d.get("fileName")
    if file_name is None:
        return DtlError("'fileName' needs to be defined in a GCS definition")

    file_format = d.get("format")
    if file_format is None:
        return DtlError("'file_format' needs to be defined in a GCS definition")
    else:
        file_format = FileFormat.file_format_from_str(file_format)
        if isinstance(file_format, DtlError):
            return file_format

    params = d.get("params")
    store_id = d.get(DatastoreDef.id_field)

    return GCSDatastoreDef(bucket, file_name, file_format, params, store_id)


class AzureDatastoreDef(DatastoreDef):
    type_str = CredentialType.Azure

    def __init__(
        self,
        container: str,
        file_name: str,
        file_format: FileFormat,
        params: Optional[Dict[str, str]] = None,
        datastore_id: Optional[UUID] = None,
    ):
        DatastoreDef.__init__(self, AzureDatastoreDef.type_str, datastore_id)
        self.container = container
        self.file_name = file_name
        self.file_format = file_format
        self.params = params

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(container= {self.container!r}, file_name= {self.file_name!r}, "
            f"file_format= {self.file_format!r}, params= {self.params})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["container"] = self.container
        base["fileName"] = self.file_name
        base["format"] = self.file_format.value
        if self.params is not None:
            base["params"] = self.params
        return base


def _azure_datastore_def_from_payload(d: dict) -> Union[DtlError, AzureDatastoreDef]:
    type_field = d.get(DatastoreDef.type_field)
    if not isinstance(type_field, str):
        return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

    if type_field != AzureDatastoreDef.type_str.value:
        return DtlError("The object %s is not an Azure Datastore definition" % (str(d)))

    container = d.get("container")
    if container is None:
        return DtlError("'container' needs to be defined in an Azure Datastore definition")

    file_name = d.get("fileName")
    if file_name is None:
        return DtlError("'fileName' needs to be defined in an Azure Datastore definition")

    file_format = d.get("format")
    if file_format is None:
        return DtlError("'file_format' needs to be defined in an Azure Datastore definition")
    else:
        file_format = FileFormat.file_format_from_str(file_format)
        if isinstance(file_format, DtlError):
            return file_format

    params = d.get("params")
    datastore_id = d.get(DatastoreDef.id_field)

    return AzureDatastoreDef(container, file_name, file_format, params, datastore_id)


class DatalogueDatastoreDef(DatastoreDef):
    type_str = CredentialType.Minio

    def __init__(
        self,
        bucket: str,
        key: str,
        file_format: FileFormat,
        params: Optional[Dict[str, str]] = None,
        datastore_id: Optional[UUID] = None,
    ):
        DatastoreDef.__init__(self, DatalogueDatastoreDef.type_str, datastore_id)
        self.bucket = bucket
        self.key = key
        self.file_format = file_format
        self.params = params

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(bucket= {self.bucket!r}, key= {self.key!r}, "
            f"file_format= {self.file_format!r}, params= {self.params})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["bucket"] = self.bucket
        base["key"] = self.key
        base["format"] = self.file_format.value
        if self.params is not None:
            base["params"] = self.params
        return base

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "DatalogueDatastoreDef"]:
        type_field = d.get(DatastoreDef.type_field)
        if not isinstance(type_field, str):
            return DtlError("string %s is missing from the json" % (DatastoreDef.type_field))

        if type_field != DatalogueDatastoreDef.type_str.value:
            return DtlError("The object %s is not an Minio definition" % (str(d)))

        bucket = d.get("bucket")
        if bucket is None:
            return DtlError("'bucket' needs to be defined in an Minio definition")

        key = d.get("key")
        if key is None:
            return DtlError("'key' needs to be defined in an Minio definition")

        file_format = d.get("format")
        if file_format is None:
            return DtlError("'file_format' needs to be defined in an Minio definition")
        else:
            file_format = FileFormat.file_format_from_str(file_format)
            if isinstance(file_format, DtlError):
                return file_format

        params = d.get("params")
        datastore_id = d.get(DatastoreDef.id_field)

        return DatalogueDatastoreDef(bucket, key, file_format, params, datastore_id)


class HadoopDatastoreDef(DatastoreDef):
    type_str = CredentialType.Hadoop

    def __init__(
        self,
        location: str,
        file_format: FileFormat,
        params: Optional[Dict[str, str]] = None,
        datastore_id: Optional[UUID] = None,
    ):
        DatastoreDef.__init__(self, HadoopDatastoreDef.type_str, datastore_id)
        self.location = location
        self.file_format = file_format
        self.params = params

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(location= {self.location!r}, "
            f"file_format= {self.file_format!r}, params= {self.params})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["location"] = self.location
        base["format"] = self.file_format.value
        if self.params is not None:
            base["params"] = self.params
        return base

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "HadoopDatastoreDef"]:
        type_field = d.get(DatastoreDef.type_field)
        if not isinstance(type_field, str):
            return DtlError("string %s is missing from the json" % (DatastoreDef.type_field))

        if type_field != HadoopDatastoreDef.type_str.value:
            return DtlError("The object %s is not a Hadoop definition" % (str(d)))

        location = d.get("location")
        if location is None:
            return DtlError("'location' needs to be defined")

        file_format = d.get("format")
        if file_format is None:
            return DtlError("'format' needs to be defined")
        else:
            file_format = FileFormat.file_format_from_str(file_format)
            if isinstance(file_format, DtlError):
                return file_format
            if file_format != FileFormat.Parquet and file_format != FileFormat.Avro:
                return DtlError("'format' needs to be Avro or Parquet")

        params = d.get("params")
        resource_id = d.get(DatastoreDef.id_field)

        return HadoopDatastoreDef(location, file_format, params, resource_id)


class SchemaRegistry(NamedTuple):
    format: SchemaFormat
    schema_for_write: Optional[str] = None

    @staticmethod
    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = {"format": self.format.value}
        if self.schema_for_write is not None:
            base["schemaForWrite"] = self.schema_for_write
        return base

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "SchemaRegistry"]:
        schema_for_write = d.get("schemaForWrite")

        schema_format = d.get("format")

        if schema_format is None:
            return DtlError("'format' needs to be defined")
        else:
            schema_format = SchemaFormat.schema_format_from_str(schema_format)
            if isinstance(schema_format, DtlError):
                return schema_format

        return SchemaRegistry(schema_format, schema_for_write)


###############################################################################
#
#                              Database Connectors
###############################################################################


class JdbcDatastoreDef(DatastoreDef):
    type_str = CredentialType.JDBC

    def __init__(
        self,
        root_table: Optional[str] = None,
        datastore_id: Optional[UUID] = None,
        view_query: Optional[str] = None,
        post_processing_query: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        schema: Optional[str] = None,
        pipeline_behavior: Optional[PipelineBehavior] = None,
        read_behavior: Optional[SourceBehavior] = None,
    ):
        """
        Defines a JDBC based data source

        :param root_table: the table to capture with this datastore; required for post_processing_query
        :param view_query: can be used to query the database, using the result as the data for that datastore.
            Please use a syntax appropriate for your dB--e.g. SQL for Postgres, CQL for Cassandra, etc.
        :param post_processing_query: can be used to run a query against the root table after a pipeline is run
            targeting that table
        :param params: Passing extra params to the datastore, currently used for Databricks Spark JDBC. Please consult this document on how to use this field : https://docs.google.com/document/d/15odo_ykW_LLiG1RR4g073jZ_QgHiq0Gbnti9TVZS2J4/edit#heading=h.w6jqud4z6wvf
        :raise ValueError: raises value error when both root_table and view_query are not specified. Also when both
            root_table and view_query are specified.
        """
        DatastoreDef.__init__(self, JdbcDatastoreDef.type_str, datastore_id)
        if root_table is None and view_query is None:
            raise ValueError("Either root_table or view_query must be specified for a JDBC datasource")
        if root_table is not None and view_query is not None:
            raise ValueError("Both root_table and view_query cannot be specified together for a JDBC datastore")
        if post_processing_query is not None and root_table is None:
            raise ValueError("root_table has to be defined in order to use post_processing_query")
        self.root_table = root_table
        self.view_query = view_query
        self.post_processing_query = post_processing_query
        self.params = params
        self.schema = schema
        self.pipeline_behavior = pipeline_behavior
        self.read_behavior = read_behavior

    def __repr__(self):
        if self.root_table is None:
            return (
                f"JdbcDatastoreDef(root_table= {self.root_table!r}, "
                f"post_processing_query= {self.post_processing_query!r}, "
                f"pipeline_behavior= {self.pipeline_behavior!r}, "
                f"read_behavior= {self.read_behavior!r})"
            )
        else:
            return (
                f"JdbcDatastoreDef(view_query= {self.view_query!r}, "
                f"post_processing_query= {self.post_processing_query!r}, "
                f"pipeline_behavior= {self.pipeline_behavior!r}, "
                f"read_behavior= {self.read_behavior!r})"
            )

    def _as_payload(self) -> dict:
        """Dictionary representation of the object with camelCase keys"""
        base = self._base_payload()
        if self.schema is not None:
            base["schema"] = self.schema
        if self.root_table is not None:
            base["rootTable"] = self.root_table
        if self.view_query is not None:
            base["viewQuery"] = self.view_query
        if self.post_processing_query is not None:
            base["postProcessingQuery"] = self.post_processing_query
        if self.pipeline_behavior is not None:
            base["pipelineBehavior"] = self.pipeline_behavior._as_payload()
        if self.read_behavior is not None:
            base["readBehavior"] = self.read_behavior._as_payload()
        base["params"] = self.params
        return base


def _jdbc_datastore_def_from_payload(d: dict) -> Union[DtlError, JdbcDatastoreDef]:
    type_field = d.get(DatastoreDef.type_field)
    if not isinstance(type_field, str):
        return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

    if type_field != JdbcDatastoreDef.type_str.value:
        return DtlError("The object %s is not a Jdbc definition" % str(d))

    datastore_id = d.get(DatastoreDef.id_field)

    root_table = d.get("rootTable")
    view_query = d.get("viewQuery")
    if root_table is None and view_query is None:
        return DtlError("'rootTable' or 'viewQuery' needs to be defined in a Jdbc definition")
    if root_table is not None and view_query is not None:
        return DtlError("Either 'rootTable' or 'viewQuery' has to be defined not both in a Jdbc definition")

    post_query = d.get("postProcessingQuery")
    params = d.get("params")
    schema = d.get("schema")

    pipeline_behavior = d.get("pipelineBehavior")
    if pipeline_behavior is not None:
        pipeline_behavior = _pipeline_behavior_from_payload(pipeline_behavior)
    read_behavior = d.get("readBehavior")
    if read_behavior is not None:
        read_behavior = _source_behavior_from_payload(read_behavior)
    return JdbcDatastoreDef(
        root_table, datastore_id, view_query, post_query, params, schema, pipeline_behavior, read_behavior
    )


class MongoDatastoreDef(DatastoreDef):
    type_str = CredentialType.Mongo

    def __init__(self, collection: str, datastore_id: Optional[UUID] = None):
        DatastoreDef.__init__(self, MongoDatastoreDef.type_str, datastore_id)
        self.collection = collection

    def _as_payload(self) -> dict:
        """Dictionary representation of the object with camelCase keys"""
        base = self._base_payload()
        base["collection"] = self.collection
        return base


def _mongo_datastore_def_from_payload(d: dict) -> Union[DtlError, MongoDatastoreDef]:
    type_field = d.get(DatastoreDef.type_field)
    if not isinstance(type_field, str):
        return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

    if type_field != MongoDatastoreDef.type_str.value:
        return DtlError("The object %s is not a Mongo definition" % str(d))

    collection = d.get("collection")
    if collection is None:
        return DtlError("'collection' needs to be defined in a Mongo definition")

    datastore_id = d.get(DatastoreDef.id_field)

    return MongoDatastoreDef(collection, datastore_id)


class KinesisDatastoreDef(DatastoreDef):
    """
    Creates a datastore that references a Kinesis dataset
    """

    type_str = CredentialType.Kinesis

    def __init__(
        self,
        stream_name: str,
        file_format: FileFormat,
        shard_attributes: ShardAttributes = ShardAttributes(),
        params: Optional[Dict[str, str]] = None,
        datastore_id: Optional[UUID] = None,
    ):
        DatastoreDef.__init__(self, KinesisDatastoreDef.type_str, datastore_id)
        self.stream_name = stream_name
        self.file_format = file_format
        self.shard_attributes = shard_attributes
        self.params = params

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(stream_name= {self.stream_name!r}, file_format= {self.file_format!r}, "
            f"shard_attributes= {self.shard_attributes!r}, params= {self.params})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["streamName"] = self.stream_name
        base["format"] = self.file_format.value
        base["shardAttributes"] = self.shard_attributes._as_payload()
        if self.params is not None:
            base["params"] = self.params
        return base

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "KinesisDatastoreDef"]:
        type_field = d.get(DatastoreDef.type_field)
        if not isinstance(type_field, str):
            return DtlError("string %s is missing from the json" % (DatastoreDef.type_field))

        if type_field != KinesisDatastoreDef.type_str.value:
            return DtlError("The object %s is not an Kinesis definition" % (str(d)))

        stream_field = d.get("streamName")
        if stream_field is None:
            return DtlError("'streamName': needs to be defined")

        format_field = d.get("format")
        if format_field is None:
            return DtlError("'format': needs to be defined")
        else:
            format_field = FileFormat.file_format_from_str(format_field)
            if isinstance(format_field, DtlError):
                return format_field

        shard_attributes = d.get("shardAttributes")
        if shard_attributes is None:
            return DtlError("'shardAttributes': needs to be defined")
        else:
            shard_attributes = ShardAttributes._from_payload(shard_attributes)

        params = d.get("params")
        datastore_id = d.get(DatastoreDef.id_field)

        return KinesisDatastoreDef(stream_field, format_field, shard_attributes, params, datastore_id)


class KafkaDatastoreDef(DatastoreDef):
    type_str = CredentialType.Kafka

    """
    :param read_from_timestamp: only read records from the topic that have been published after the specified datetime, in the timezone of the kafka cluster
    """

    def __init__(
        self,
        topic: str,
        format_or_registry: Union[FileFormat, SchemaRegistry],
        params: Optional[Dict[str, str]] = None,
        datastore_id: Optional[UUID] = None,
        read_from_timestamp: Optional[datetime] = None,
    ):
        DatastoreDef.__init__(self, KafkaDatastoreDef.type_str, datastore_id)
        self.topic = topic
        self.format_or_registry = format_or_registry
        self.params = params
        self.read_from_timestamp = read_from_timestamp

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(topic= {self.topic!r}, "
            f"format_or_registry= {self.format_or_registry!r}, params= {self.params}, read_from_timestamp= {self.read_from_timestamp})"
        )

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """
        base = self._base_payload()
        base["topic"] = self.topic
        if isinstance(self.format_or_registry, FileFormat):
            base["format"] = self.format_or_registry.value
        else:
            base["format"] = SchemaRegistry._as_payload(self.format_or_registry)
        if self.params is not None:
            base["params"] = self.params
        if self.read_from_timestamp is not None:
            base["readFromTimestamp"] = int(self.read_from_timestamp.timestamp() * 1000)
        return base

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "KafkaDatastoreDef"]:
        type_field = d.get(KafkaDatastoreDef.type_field)
        if not isinstance(type_field, str):
            return DtlError("string %s is missing from the json" % (DatastoreDef.type_field))

        if type_field != KafkaDatastoreDef.type_str.value:
            return DtlError("The object %s is not a Kafka definition" % (str(d)))

        topic = d.get("topic")
        if topic is None:
            return DtlError("'topic' needs to be defined")

        format_or_registry = d.get("format")
        if format_or_registry is None:
            return DtlError("'format' needs to be defined")
        elif isinstance(format_or_registry, str):
            format_or_registry = FileFormat.file_format_from_str(format_or_registry)
            if isinstance(format_or_registry, DtlError):
                return format_or_registry
            if format_or_registry not in (FileFormat.Csv, FileFormat.Text, FileFormat.Json,):
                return DtlError("'format' needs to be CSV, TEXT, Json")
        else:
            format_or_registry = SchemaRegistry._from_payload(format_or_registry)
            if isinstance(format_or_registry, DtlError):
                return format_or_registry

        params = d.get("params")
        resource_id = d.get(DatastoreDef.id_field)

        read_from_timestamp = d.get("readFromTimestamp")
        if read_from_timestamp is not None:
            read_from_timestamp = datetime.fromtimestamp(read_from_timestamp / 1000)
        return KafkaDatastoreDef(topic, format_or_registry, params, resource_id, read_from_timestamp)


###############################################################################
#                              API Sources
###############################################################################


class SocrataDatastoreDef(DatastoreDef):
    """
    Creates a datastore that references a Socrata dataset
    """

    type_str = CredentialType.Socrata

    def __init__(self, socrata_id: str, datastore_id: Optional[UUID] = None):
        """
        :param socrata_id: id of the dataset on socrata
        :param datastore_id: id of the datastore on the datalogue platform. This will only be set if the object was
         retrieved from the platform
        """
        DatastoreDef.__init__(self, SocrataDatastoreDef.type_str, datastore_id)
        self.socrata_id = socrata_id

    def _as_payload(self) -> dict:
        """Dictionary representation of the object with camelCase keys"""
        base = self._base_payload()
        base["socrataId"] = self.socrata_id
        return base

    @staticmethod
    def _from_payload(d: dict) -> Union[DtlError, "SocrataDatastoreDef"]:
        type_field = d.get(DatastoreDef.type_field)
        if not isinstance(type_field, str):
            return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

        if type_field != SocrataDatastoreDef.type_str.value:
            return DtlError("The object %s is not a Socrata definition" % str(d))

        socrata_id = d.get("socrataId")
        if socrata_id is None:
            return DtlError("'socrata_id' needs to be defined in a Socrata definition")

        datastore_id = d.get(DatastoreDef.id_field)

        return SocrataDatastoreDef(socrata_id, datastore_id)


class HttpDatastoreDef(DatastoreDef):
    """
    Creates a datastore that references a Http dataset
    """

    type_str = CredentialType.Http

    def __init__(
        self,
        endpoint: str,
        file_format: FileFormat,
        method_type: HttpMethodType,
        headers: Optional[dict] = None,
        query_params: Optional[dict] = None,
        body: Optional[dict] = None,
        datastore_id: Optional[UUID] = None,
    ):
        """
        :param endpoint: path to attach to base url in the http credential
        :param file_format: format of the file (json, cvsv, etc.)
        :param method_type: http method selected for the request (GET, PUT, POST)
        :param headers: headers to be added to the request (Accept, X-App-Token, etc.). it's optional
        :param query_params: http request parameters. it's optional
        """
        DatastoreDef.__init__(self, HttpDatastoreDef.type_str, datastore_id)
        self.endpoint = endpoint
        self.file_format = file_format
        self.method_type = method_type
        self.headers = headers
        self.query_params = query_params
        self.body = body

    def _as_payload(self) -> dict:
        """Dictionary representation of the object with camelCase keys"""
        base = self._base_payload()
        base["endpoint"] = self.endpoint
        base["format"] = self.file_format.value
        base["methodType"] = self.method_type.value
        if self.headers is not None:
            base["headers"] = self.headers
        if self.query_params is not None:
            base["queryParams"] = self.query_params
        if self.body is not None:
            base["body"] = self.body

        return base


def _http_datastore_def_from_payload(d: dict) -> Union[DtlError, HttpDatastoreDef]:
    type_field = d.get(DatastoreDef.type_field)
    if not isinstance(type_field, str):
        return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

    if type_field != HttpDatastoreDef.type_str.value:
        return DtlError("The object %s is not an HttpResource definition" % str(d))

    endpoint = d.get("endpoint")
    if endpoint is None:
        return DtlError("'endpoint' needs to be defined in an HttpResource definition")

    file_format = d.get("format")
    if file_format is None:
        return DtlError("'file_format' needs to be defined in an HttpResource definition")
    else:
        file_format = FileFormat.file_format_from_str(file_format)
        if isinstance(file_format, DtlError):
            return file_format

    method_type = d.get("methodType")
    if method_type is None:
        return DtlError("'method_type' needs to be defined in an HttpResource definition")
    else:
        method_type = HttpMethodType.method_type_from_str(method_type)
        if isinstance(method_type, DtlError):
            return method_type

    datastore_id = d.get(DatastoreDef.id_field)
    return HttpDatastoreDef(
        endpoint, file_format, method_type, d.get("headers"), d.get("queryParams"), d.get("body"), datastore_id
    )


###############################################################################
#                              File Sources
###############################################################################


class FileDatastoreDef(DatastoreDef):
    type_str = CredentialType.FileSystem

    def __init__(
        self,
        location: str,
        file_format: FileFormat,
        params: Optional[Dict[str, str]] = None,
        datastore_id: Optional[UUID] = None,
    ):
        DatastoreDef.__init__(self, FileDatastoreDef.type_str, datastore_id)
        self.location = location
        self.file_format = file_format
        self.params = params

    def _as_payload(self) -> dict:
        """Dictionary representation of the object with camelCase keys"""
        base = self._base_payload()
        base["location"] = self.location
        base["format"] = self.file_format.value
        if self.params is not None:
            base["params"] = self.params
        return base


def _file_datastore_def_from_payload(d: dict) -> Union[DtlError, FileDatastoreDef]:
    type_field = d.get(DatastoreDef.type_field)
    if not isinstance(type_field, str):
        return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

    if type_field != FileDatastoreDef.type_str.value:
        return DtlError("The object %s is not a FileSystem definition" % str(d))

    location = d.get("location")
    if location is None:
        return DtlError("'location' needs to be defined in a FileSystem definition")

    file_format = d.get("format")
    if file_format is None:
        return DtlError("'file_format' needs to be defined in a FileSystem definition")
    else:
        file_format = FileFormat.file_format_from_str(file_format)
        if isinstance(file_format, DtlError):
            return file_format

    params = d.get("params")
    datastore_id = d.get(DatastoreDef.id_field)

    return FileDatastoreDef(location, file_format, params, datastore_id)


###############################################################################
#                              The Infinite Abyss
###############################################################################


class VoidDef(DatastoreDef):
    type_str = CredentialType.Void

    def __init__(self, datastore_id: Optional[UUID] = None):
        DatastoreDef.__init__(self, VoidDef.type_str, datastore_id)

    def __repr__(self):
        return "VoidDef()"

    def _as_payload(self) -> dict:
        """Dictionary representation of the object with camelCase keys"""
        return self._base_payload()


def _void_def_from_payload(d: dict) -> Union[DtlError, VoidDef]:
    type_field = d.get(DatastoreDef.type_field)
    if not isinstance(type_field, str):
        return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

    if type_field != VoidDef.type_str.value:
        return DtlError("The object %s is not a Void definition" % str(d))

    datastore_id = d.get(DatastoreDef.id_field)

    return VoidDef(datastore_id)


###############################################################################
#                              Webhook Datastore
###############################################################################


class WebhookDatastoreDef(DatastoreDef):
    type_str = CredentialType.Webhook

    def __init__(
        self,
        message_format: FileFormat,
        identifier: Optional[str] = None,
        url: Optional[str] = None,
        datastore_id: Optional[UUID] = None,
    ):
        """
        Creates a datastore that exposes an url to the Datalogue pipelining engine

        Upon creation, external applications can push data to the url via webhooks. Incoming data will be
        continually fed into any running pipeline using the datastore as a source

        :param message_format: format of the data that will be pushed by the webhook, via the FileFormat enumeration
        :param identifier: can be used to customize the generated url; will default to the UUID of the created
            datastore. Identifiers must be unique within your deployment, and spaces and special characters are not
            supported
        :param url: for backend use; upon creation, the url property will be populated with the API url
            url to which other applications can push data. User input to this param will be ignored.
        :param datastore_id: UUID of the datastore
        """
        DatastoreDef.__init__(self, WebhookDatastoreDef.type_str, datastore_id)
        self.message_format = message_format
        self.identifier = identifier
        self.url = url

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(message_format= {self.message_format}, "
            f"identifier= {self.identifier!r}, url= {self.url!r}, datastore_id= {self.datastore_id!r})"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        # buffer is not needed in SDK, but might be introduced in upcoming versions of Webhooks
        base["buffer"] = 0
        base["fileFormat"] = self.message_format.value

        if self.identifier is not None:
            base["identifier"] = self.identifier

        if self.url is not None:
            base["webhookUrl"] = self.url

        return base

    @staticmethod
    def _webhook_def_from_payload(d: dict) -> Union[DtlError, "WebhookDatastoreDef"]:
        type_field = d.get(DatastoreDef.type_field)
        if not isinstance(type_field, str):
            return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

        if type_field != WebhookDatastoreDef.type_str.value:
            return DtlError("The object %s is not a Webhook definition" % str(d))

        message_format = d.get("fileFormat")
        if not isinstance(message_format, str):
            return DtlError("'message_format' needs to be defined in a Webhook definition")
        else:
            message_format = FileFormat.file_format_from_str(message_format)

        identifier = d.get("identifier")

        url = d.get("webhookUrl")

        datastore_id = d.get(DatastoreDef.id_field)

        return WebhookDatastoreDef(message_format, identifier, url, datastore_id)


###############################################################################
#                              SFTP Datastore
###############################################################################


class SFTPDatastoreDef(DatastoreDef):
    type_str = CredentialType.SFTP

    def __init__(
        self,
        path: str,
        file_format: FileFormat,
        params: Optional[Dict[str, str]] = None,
        decompression: Optional[Decompression] = Decompression.Infer,
        resource_type: Optional[ResourceType] = None,
    ):
        """
        SFTP Datastore definition
        :param path: path within the VM to the filesystem containing data
        :param file_format: format of the file (json, csv, etc.)
        :param params: optional parameters fed to the specified file format
        :param decompression: can be used to decompress files in stream. Default behavior is to infer compression type and decompress. Supported format(s): gzip
        :param resource_type: TBD
        """
        DatastoreDef.__init__(self, SFTPDatastoreDef.type_str)
        self.path = path
        self.file_format = file_format
        self.params = params
        self.decompression = decompression
        self.resource_type = resource_type

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(path= {self.path},"
            f" file_format= {self.file_format},"
            f" params= {self.params},"
            f" decompression= {self.decompression},"
            f" resource_type= {self.resource_type})"
        )

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["fileFormat"] = self.file_format.value
        if self.params is not None:
            base["params"] = self.params
        base["decompression"] = self.decompression.value
        if self.resource_type is not None:
            base["resourceType"] = self.resource_type.value
        return base

    @staticmethod
    def _sftp_def_from_payload(d: dict) -> Union[DtlError, "SFTPDatastoreDef"]:
        type_field = d.get(DatastoreDef.type_field)
        if not isinstance(type_field, str):
            return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

        if type_field != SFTPDatastoreDef.type_str.value:
            return DtlError("The object %s is not a SFTP datastore definition" % str(d))

        path = d.get("path")
        if not isinstance(path, str):
            return DtlError("'path' needs to be specified for SFTP datastore definition")

        file_format = d.get("fileFormat")
        if not isinstance(file_format, str):
            return DtlError("'fileFormat' needs to be specified for SFTP datastore definition")
        else:
            file_format = FileFormat.file_format_from_str(file_format)

        decompression = d.get("decompression")

        if decompression is None:
            return DtlError("'decompression' needs to be defined for SFTP datastore definition")
        else:
            decompression = Decompression.decompression_from_str(decompression)
            if isinstance(decompression, DtlError):
                return decompression

        resource_type = d.get("resourceType")
        if isinstance(resource_type, str):
            resource_type = ResourceType.resource_type_from_str(resource_type)
        if isinstance(resource_type, DtlError):
            return resource_type

        params = d.get("params")

        return SFTPDatastoreDef(path, file_format, params, decompression, resource_type)


###############################################################################
#                             ElasticSearch Datastore
###############################################################################
class ElasticSearchDef(DatastoreDef):
    type_str = CredentialType.ElasticSearch

    def __init__(
        self, index: str, index_id_path: List[str], type_name: str = "_doc", datastore_id: Optional[UUID] = None
    ):
        DatastoreDef.__init__(self, ElasticSearchDef.type_str, datastore_id)
        self.index = index
        self.index_id_path = index_id_path
        self.type_name = type_name

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(index={self.index!r},"
            f"index_id_path={self.index_id_path}"
            f"type_name={self.type_name!r})"
        )

    def _as_payload(self) -> dict:
        """Dictionary representation of the object with camelCase keys"""
        base = self._base_payload()
        base["index"] = self.index
        base["indexIdKey"] = self.index_id_path
        base["docTypeName"] = self.type_name
        return base

    @classmethod
    def _from_payload(cls, json: dict) -> Union[DtlError, "ElasticSearchDef"]:
        type_field = json.get(DatastoreDef.type_field)
        if not isinstance(type_field, str):
            return DtlError("string %s is missing from the json" % DatastoreDef.type_field)

        if type_field != cls.type_str.value:
            return DtlError("The object %s is not an ElasticSearch definition" % str(d))

        index = json.get("index")
        if index is None:
            return DtlError("'index' needs to be defined in an ElasticSearch definition")

        index_id_key = json.get("indexIdKey")
        if index_id_key is None:
            return DtlError("'indexIdKey' needs to be defined in an ElasticSearch definition")
            if not isinstance(index_id_key, list) or not all(isinstance(path, str) for path in lst):
                return DtlError("'indexIdKey' must be defined as a list of strings")

        type_name = json.get("docTypeName")
        if type_name is None:
            return DtlError("'docTypeName' needs to be defined in an ElasticSearch definition")

        datastore_id = json.get(DatastoreDef.id_field)

        return cls(index=index, index_id_path=index_id_key, type_name=type_name, datastore_id=datastore_id)


_data_definitions = dict(
    [
        (S3DatastoreDef.type_str.value, _s3_datastore_def_from_payload),
        (AVCOrderItemsDatastore.type_str.value, _avc_datastore_def_from_payload),
        (GCSDatastoreDef.type_str.value, _gcs_datastore_def_from_payload),
        (AzureDatastoreDef.type_str.value, _azure_datastore_def_from_payload),
        (JdbcDatastoreDef.type_str.value, _jdbc_datastore_def_from_payload),
        (MongoDatastoreDef.type_str.value, _mongo_datastore_def_from_payload),
        (HttpDatastoreDef.type_str.value, _http_datastore_def_from_payload),
        (SocrataDatastoreDef.type_str.value, SocrataDatastoreDef._from_payload),
        (FileDatastoreDef.type_str.value, _file_datastore_def_from_payload),
        (VoidDef.type_str.value, _void_def_from_payload),
        (KinesisDatastoreDef.type_str.value, KinesisDatastoreDef._from_payload),
        (KafkaDatastoreDef.type_str.value, KafkaDatastoreDef._from_payload),
        (HadoopDatastoreDef.type_str.value, HadoopDatastoreDef._from_payload),
        (DatalogueDatastoreDef.type_str.value, DatalogueDatastoreDef._from_payload),
        (WebhookDatastoreDef.type_str.value, WebhookDatastoreDef._webhook_def_from_payload,),
        (SFTPDatastoreDef.type_str.value, SFTPDatastoreDef._sftp_def_from_payload),
        (ElasticSearchDef.type_str.value, ElasticSearchDef._from_payload),
    ]
)


def _datastore_def_from_payload(json: dict) -> Union[DtlError, DatastoreDef]:
    type_field = json.get(DatastoreDef.type_field)
    if type_field is None:
        return DtlError("The datastore definition object doesn't have a '%s' property" % DatastoreDef.type_field)

    parsing_function = _data_definitions.get(type_field)
    if parsing_function is None:
        return DtlError("Looks like '%s' datastore is not handled by the SDK" % type_field)

    return parsing_function(json)


def _datastore_from_payload(json: dict) -> Union[DtlError, Datastore]:
    name = json.get("name")
    if name is None:
        return DtlError("'name' for a datastore should be defined")

    definition = json.get("definition")
    gate = json.get("gate")

    if definition is None and gate is None:
        return DtlError("Neither 'definition' nor 'gate' for a datastore is defined!'")
    elif definition is not None:
        definition = _datastore_def_from_payload(definition)
    else:
        definition = _datastore_def_from_payload(gate)

    alias = json.get("alias")
    credential_id = json.get("credentialsId")
    if credential_id is not None:
        credential_id = UUID(credential_id)
    datastore_id = json.get("id")

    schema_paths = json.get("schemaPaths")
    if schema_paths is not None:
        schema_paths = _parse_list(_parse_string_list)(schema_paths)
        if isinstance(schema_paths, DtlError):
            return schema_paths

    schema_classes = []
    classifications_json = json.get("classifications")
    if classifications_json is not None:
        classifications = _parse_list(Classification._from_payload)(classifications_json)
        if isinstance(classifications, DtlError):
            return classifications
        schema_classes = classifications

    schema_labels = None
    if schema_paths is not None:
        schema_labels = set()
        for row in schema_paths:
            for col in row:
                schema_labels.add(col)
        schema_labels = list(schema_labels)

    ads_json = json.get("ads")
    schema_nodes = None
    ads = None
    if ads_json is not None:
        schema_nodes = ads_json.get("nodes")
        if schema_nodes is not None:
            schema_nodes = _parse_list(SchemaNode._schema_node_from_payload)(schema_nodes)
            if isinstance(schema_nodes, DtlError):
                return schema_nodes
        ads = AbstractDataSchema._from_payload(ads_json, AbstractDataSchema.node_decoder)
    tags = json.get("tags")
    if tags is None:
        tags = []
    return Datastore(
        name,
        definition,
        credential_id,
        alias,
        datastore_id,
        schema_paths,
        schema_classes,
        schema_labels,
        schema_nodes,
        ads,
        tags,
    )


class ReclassificationBehavior(SerializableStringEnum):
    ReplaceAutomatic = "ReplaceAutomatic"
    ReplaceAll = "ReplaceAll"
    AddNew = "AddNew"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("reclassification behavior", s), DtlError(""))

    def __str__(self):
        return str(self.value)

    @staticmethod
    def reclassification_behavior_from_str(string: str,) -> Union[DtlError, "ReclassificationBehavior"]:
        return SerializableStringEnum.from_str("ReclassificationBehavior")(string)


class RollupStrategy(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        pass


class Threshold:
    """
    :param class_ids: List of class Ids. Can be a single class as well.
    :threshold: threshold value for class_ids. It should be between 0 and 1, [0.0, 1.0]

    Takes in a list of class ids with threshold levels to meet for each class_id. User can also enter a list of classes with one threshold to apply to all class_ids
    """

    def __init__(self, classIds: List[UUID], threshold: float):
        self.classIds = classIds
        self.threshold = threshold

    def _as_payload(self) -> dict:
        payload = {
            "classIds": list(map(lambda classId: str(classId), self.classIds)),
            "threshold": str(self.threshold),
        }
        return payload

    def __repr__(self):
        return f'(classIds= [{",".join(map(lambda t: str(t), self.classIds))}], threshold= {self.threshold})'


class ClassThreshold(RollupStrategy):
    """
    Generalizes field classification by setting thresholds for individual classes.
    Top class is selected in instances where multiple thresholds are met. No class is returned if no threshold is met

    :param threshold_pairs: Accepts the class Threshold instance() which contains class_ids and threshold values
    """

    def __init__(self, threshold_pairs: List[Threshold]):
        super().__init__()
        self.threshold_pairs = threshold_pairs

    def _as_payload(self) -> dict:
        payload = {
            "type": "Threshold",
            "thresholds": list(map(lambda threshold: threshold._as_payload(), self.threshold_pairs)),
        }
        return payload

    def __repr__(self):
        return f'Threshold(threshold_pairs= {",".join(map(lambda t: str(t), self.thresholds))})'


class WeightedAverage(RollupStrategy):
    """
    Generalizes field classification by calculating a weighted average of the individual classes
    """

    def __init__(self):
        super().__init__()

    def _as_payload(self) -> dict:
        payload = {"type": "WeightedAverage"}
        return payload

    def __repr__(self):
        return "WeightedAverage()"
