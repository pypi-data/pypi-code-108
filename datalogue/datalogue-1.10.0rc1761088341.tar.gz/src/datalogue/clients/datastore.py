from typing import List, Dict, Union, Optional, Set
from uuid import UUID
from pyarrow import csv,json, Table

from datalogue.clients._http import _HttpClient, HttpMethod, MultiPartData, MultiPartFile
from datalogue.models.schema import AbstractDataSchema, Schema, SchemaNode
from datalogue.models.datastore import (
    Datastore,
    _datastore_from_payload,
    FileFormat,
    Cell,
    _cell_from_payload,
    NodeClassification,
    ReclassificationBehavior,
    RollupStrategy,
    WeightedAverage,
)
from datalogue.errors import DtlError
from datalogue.dtl_utils import _parse_list, ResponseStream
from datalogue.clients._processed_sources import _ProcessedSourcesClient


class _MetadataClient:
    """
    Client to interact with metadata
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def add(
        self, datastore_id: Union[str, UUID], field: List[str], metadata: Dict[str, str]
    ) -> Union[DtlError, SchemaNode]:
        """
        Add key:value pairs of metadata to a field

        :param datastore_id: id of the datastore to which to add metadata
        :param field: path to the field to which to add metadata; note: the specified metadata will be added to all fields thus named 
        :param metadata: a dictionary of metadata, in key:value format, to be added to the afore-specified field; e.g. {'description':'family names of customers', 'privacy':'private'} will add two pairs of metadata
        :return: the updated SchemaNode if successful or DtlError if failed 
        """
        payload = {"fieldPath": field, "metadata": metadata}

        rsp = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/metadata", HttpMethod.PUT, payload,
        )

        if isinstance(rsp, DtlError):
            return rsp
        elif rsp.status_code == 200:
            return SchemaNode._schema_node_from_payload(rsp.json())
        else:
            return DtlError(rsp.text)

    def remove(self, datastore_id: Union[str, UUID], field: List[str], key: str) -> Union[DtlError, SchemaNode]:
        """
        Remove a specified metadata key:value pair from a field

        :param datastore_id: id of the datastore from which to remove metadata
        :param field: path to the field from which to remove metadata; note: the specified metadata will be removed from all fields thus named 
        :param key: the key of the metadata pair you wish to remove
        :return: the updated SchemaNode if successful or DtlError if failed
        """
        payload = {"fieldPath": field, "key": key}

        rsp = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/metadata", HttpMethod.DELETE, payload,
        )

        if isinstance(rsp, DtlError):
            return rsp
        elif rsp.status_code == 200:
            return SchemaNode._schema_node_from_payload(rsp.json())
        else:
            return DtlError(rsp.text)

    def replace_value(
        self, datastore_id: Union[str, UUID], field: List[str], key: str, new_value: str
    ) -> Union[DtlError, SchemaNode]:
        """
        Replace the value of a specified metadata key:value pair

        :param datastore_id: id of the datastore of which to replace metadata value
        :param field: path to the field of which to replace metadata value
        :param key: the key of the metadata pair whose value should be replaced
        :new_value: the new value of the afore-specified key
        :return: the updated SchemaNode if successful or DtlError if failed
        """
        metadata = {}
        metadata[key] = new_value
        payload = {"fieldPath": field, "metadata": metadata}

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/metadata/replace", HttpMethod.POST, body=payload,
        )
        if isinstance(res, DtlError):
            return res

        return SchemaNode._schema_node_from_payload(res)

    def clear(self, datastore_id: Union[str, UUID], field: List[str]) -> Union[DtlError, SchemaNode]:
        """
        Clear all metadata from a field

        :param datastore_id: id of the datastore from which to clear metadata
        :param field: path to the field from which to clear metadata
        :return: the updated SchemaNode if successful or DtlError if failed 

        """
        payload = {"fieldPath": field}

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/metadata/clear", HttpMethod.POST, body=payload,
        )
        if isinstance(res, DtlError):
            return res

        return SchemaNode._schema_node_from_payload(res)


class DatastoreClient:
    """
    Client to interact with the Datastores objects
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"
        self.metadata = _MetadataClient(http_client)
        self.processed_sources = _ProcessedSourcesClient(self.http_client)

    def create(self, datastore: Datastore) -> Union[DtlError, Datastore]:
        """
        Creates a data source

        :param datastore: data source to be created
        :return: string with error message if failed, the data source otherwise
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores", HttpMethod.POST, datastore._as_payload()
        )

        if isinstance(res, DtlError):
            return res

        return _datastore_from_payload(res)

    def get(self, datastore_id: UUID) -> Union[DtlError, Datastore]:
        """
        From the provided id, get the corresponding Datastore

        :param datastore_id: id of the datastore to be retrieved
        :return:
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id), HttpMethod.GET
        )

        if isinstance(res, DtlError):
            return res

        datastore_resp = _datastore_from_payload(res)
        if isinstance(datastore_resp, DtlError):
            return datastore_resp

        return self.__load_datastore_with_class_info(datastore_resp)

    def get_by_credential_id(
        self, credential_id: UUID, page: int = 1, item_per_page: int = 25
    ) -> Union[DtlError, List[Datastore]]:
        """
        From the provided credential id, get corresponding Datastores
        :param credential_id: id of the datastore to be retrieved
        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all datastores for given credential_id or an error message as a string
        """
        payload = {"queries": {}, "from": (page - 1) * item_per_page, "size": item_per_page, "type": "datastore"}

        res = self.http_client.make_authed_request(
            self.service_uri + f"/credentials/{str(credential_id)}/datastores/search", HttpMethod.POST, payload
        )

        if isinstance(res, DtlError):
            return res

        datastore_list = _parse_list(_datastore_from_payload)(res["results"])
        if isinstance(datastore_list, DtlError):
            return datastore_list

        datastore_list_with_class_info = []
        for datastore_resp in datastore_list:
            datastore_resp_with_class_info = self.__load_datastore_with_class_info(datastore_resp)
            if isinstance(datastore_resp_with_class_info, DtlError):
                return datastore_resp_with_class_info
            datastore_list_with_class_info.append(datastore_resp_with_class_info)
        return datastore_list_with_class_info

    def update(self, datastore: Datastore) -> Union[DtlError, Datastore]:
        """
        Updates the backend with the new status of the existing datastore

        :param datastore: to be persisted
        :return:
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore.id), HttpMethod.PUT, datastore._as_payload(),
        )

        if isinstance(res, DtlError):
            return res

        return _datastore_from_payload(res)

    def list(
        self, by_tag_name: Optional[str] = None, page: int = 1, item_per_page: int = 25
    ) -> Union[DtlError, List[Datastore]]:
        """
        List all the datastores that are saved

        :param by_tag_name: optionally filter your list by only those datastores tagged by the specified tag
        :param page: page to be retrieved (ignored)
        :param item_per_page: number of items to be put in a page (ignored)
        :return: Returns a List of all the available datastores or an error message as a string
        """
        params = {
            "page": page,
            "size": item_per_page,
        }
        if isinstance(by_tag_name, str):
            params["tag_name"] = by_tag_name

        res = self.http_client.make_authed_request(self.service_uri + "/datastores", HttpMethod.GET, params=params)

        if isinstance(res, DtlError):
            return res

        datastore_list = _parse_list(_datastore_from_payload)(res)
        if isinstance(datastore_list, DtlError):
            return datastore_list

        datastore_list_with_class_info = []
        for datastore_resp in datastore_list:
            datastore_resp_with_class_info = self.__load_datastore_with_class_info(datastore_resp)
            if isinstance(datastore_resp_with_class_info, DtlError):
                return datastore_resp_with_class_info
            datastore_list_with_class_info.append(datastore_resp_with_class_info)
        return datastore_list_with_class_info

    def search(
        self,
        by_tag_name: Optional[str] = None,
        by_name: Optional[List[str]] = None,
        by_field_name: Optional[List[str]] = None,
        by_field_class: Optional[List[str]] = None,
        page: int = 1,
        item_per_page: int = 25,
    ) -> Union[DtlError, List[Datastore]]:
        """
        Search among all backend Datastores, using any numbers of queries as the search criteria
         Multiple items within a query will be applied with OR logic — multiple queries will be applied with AND logic

         The wildcard operators: `?` and `*` can be used as wildcards,
         matching one and any number of additional characters, respectively

        :param by_tag_name: a tag applied to the datastores, specified by the full tag name
        :param by_name: a list of datastore names
        :param by_field_name: a list of column labels
        :param by_field_class: a list of classes that columns are classified
        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available datastores or an error message as a string
        """

        queries = {}

        if isinstance(by_name, list):
            queries["name"] = by_name

        if isinstance(by_field_name, list):
            queries["schema.nodes.label"] = by_field_name

        if isinstance(by_field_class, list):
            queries["classes.name"] = by_field_class

        if len(queries) > 0:
            payload = {
                "queries": queries,
                "from": (page - 1) * item_per_page,
                "size": item_per_page,
                "type": "datastore",
            }
            if isinstance(by_tag_name, str):
                payload["tag"] = by_tag_name

            res = self.http_client.make_authed_request(self.service_uri + "/v2/search", HttpMethod.POST, payload)
            if isinstance(res, DtlError):
                return res

            return _parse_list(_datastore_from_payload)(res["results"])
        else:
            # If there is not query, we will bring everything
            payload = {
                "query": "*",
                "page": page,
                "size": item_per_page,
                "type": "datastore",
            }
            if isinstance(by_tag_name, str):
                payload["tag"] = by_tag_name

            res = self.http_client.make_authed_request(self.service_uri + "/search", HttpMethod.POST, payload)
            return _parse_list(_datastore_from_payload)(res["results"])

    def get_schema(self, datastore_id: UUID) -> Union[DtlError, AbstractDataSchema]:
        """
        From the provided id, get the corresponding Datastore schema

        :param datastore_id: id of the datastore to be retrieved
        :return:
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/schema", HttpMethod.GET,
        )
        if isinstance(res, DtlError):
            return res

        schema = Schema._from_payload(res).data_schema
        if isinstance(schema, DtlError):
            return schema

        schema = self.__load_ads_with_class_info(schema)
        return schema

    def __load_datastore_with_class_info(self, datastore: Datastore) -> Union[DtlError, Datastore]:
        if datastore.ads is None and (datastore.schema_nodes is None or (len(datastore.schema_nodes) == 0)):
            return datastore

        if datastore.ads is not None or datastore.schema_nodes is not None:
            # 1. Get schema nodes from either Datastore or from ADS
            schema_nodes = []
            if datastore.schema_nodes is not None:
                schema_nodes = datastore.schema_nodes
            elif datastore.ads is not None:
                schema_nodes = list(map(lambda node_def: node_def.node, datastore.ads.get_nodes()))

            # 2. Load the dictionary for set of class_id
            class_id_path_dict = self.__load_paths_of_class_ids(schema_nodes)
            if isinstance(class_id_path_dict, DtlError):
                return class_id_path_dict

            # 3. Update ADS and List of SchemaNode respectively
            if datastore.ads is not None:
                datastore.ads = self.__fill_ads(datastore.ads, class_id_path_dict)

            if datastore.schema_nodes is not None:
                datastore.schema_nodes = self.__fill_schema_nodes(datastore.schema_nodes, class_id_path_dict)

            if datastore.schema_classes is not None:
                for schema_class in datastore.schema_classes:
                    class_path = class_id_path_dict.get(schema_class.class_id)
                    if class_path is None:
                        # There is no class or user does not have Read permissions
                        schema_class.class_name = "Permission denied"
                        schema_class.class_path = ["Permission denied"]
                    elif len(class_path) > 0:
                        schema_class.class_name = class_path[-1]
                        schema_class.class_path = class_path
                    else:
                        schema_class.class_path = class_path

        return datastore

    def __load_ads_with_class_info(self, schema: AbstractDataSchema) -> Union[DtlError, AbstractDataSchema]:
        schema_nodes = list(map(lambda node_def: node_def.node, schema.get_nodes()))
        class_id_path_dict = self.__load_paths_of_class_ids(schema_nodes)

        if isinstance(class_id_path_dict, DtlError):
            return class_id_path_dict

        return self.__fill_ads(schema, class_id_path_dict)

    def __fill_ads(
        self, schema: AbstractDataSchema, class_id_path_dict: Dict[UUID, List[str]]
    ) -> Union[DtlError, AbstractDataSchema]:
        schema_nodes = list(map(lambda node_def: node_def.node, schema.get_nodes()))
        for schema_node in schema_nodes:
            classifications = schema_node.classifications
            for classification in classifications:
                class_path = class_id_path_dict.get(classification.class_id)
                if class_path is None:
                    # There is no class or user does not have Read permissions
                    classification.class_name = "Permission denied"
                    classification.class_path = ["Permission denied"]
                elif len(class_path) > 0:
                    classification.class_name = class_path[-1]
                    classification.class_path = class_path
                else:
                    classification.class_path = class_path

        return schema

    def __load_schema_nodes_with_class_info(self, schema_nodes: List[SchemaNode]) -> Union[DtlError, List[SchemaNode]]:
        class_id_path_dict = self.__load_paths_of_class_ids(schema_nodes)
        return self.__fill_schema_nodes(schema_nodes, class_id_path_dict)

    def __fill_schema_nodes(
        self, schema_nodes: List[SchemaNode], class_id_path_dict: Dict[UUID, List[str]]
    ) -> Union[DtlError, List[SchemaNode]]:
        for schema_node in schema_nodes:
            classifications = schema_node.classifications
            for classification in classifications:
                class_path = class_id_path_dict.get(classification.class_id)
                if class_path is None:
                    # There is no class or user does not have Read permissions
                    classification.class_name = "Permission denied"
                    classification.class_path = ["Permission denied"]
                elif len(class_path) > 0:
                    classification.class_name = class_path[-1]
                    classification.class_path = class_path
                else:
                    classification.class_path = class_path
        return schema_nodes

    def __load_paths_of_class_ids(self, schema_nodes: List[SchemaNode]) -> Union[DtlError, Dict[str, List[str]]]:
        class_id_set = set([])
        for schema_node in schema_nodes:
            classifications = schema_node.classifications
            for classification in classifications:
                class_id_set.add(classification.class_id)

        res = []
        if len(class_id_set) > 0:
            res = self.http_client.make_authed_request(
                f"/yggy/entities?page=1&size={len(class_id_set)}",
                HttpMethod.PUT,
                list(map(lambda x: str(x), class_id_set)),
            )

            if isinstance(res, DtlError):
                return res

        class_id_path_dict = {}
        for classInfo in res:
            class_id = UUID(classInfo["id"])
            class_path = classInfo["path"]
            class_id_path_dict[class_id] = class_path

        return class_id_path_dict

    def print(self, datastore_id: UUID, full_path: bool = False) -> Union[DtlError, None]:
        """
        TEMPORARILY DISABLED.
        From the provided id, get the corresponding Datastore schema

        :param datastore_id: id of the datastore to be retrieved
        :return:
        """
        print("Feature currently disabled, please contact Datalogue.")
        # res = self.http_client.make_authed_request(self.service_uri + "/datastores/" + str(datastore_id) + "/schema", HttpMethod.GET)
        # if isinstance(res, DtlError):
        #     if res.message.__contains__("Route not found"):
        #         res.message = "Invalid ID, please verify that your data store exists with dtl.datastore.list()"
        #     return res
        # schema = Schema._from_payload(res)
        # schema.print(full_path)

    def delete(self, datastore_id: UUID) -> Union[DtlError, bool]:
        """
        Deletes the given Datastore

        :param datastore_id: id of the datastore to be deleted
        :return: true if successful, false otherwise
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id), HttpMethod.DELETE
        )

        if isinstance(res, DtlError):
            return res
        else:
            return True

    def download(
        self, datastore_id: UUID, file_format: FileFormat, path: str, limit: Optional[int] = None,
    ) -> Union[DtlError, str]:
        """
        Downloads the resource in a file

        :param datastore_id: id of the resource to download
        :param file_format: File format of the downloaded resource
        :param path: location to save the file
        :param limit: limit the number of elements to be downloaded
        :return: An error or the path to the downloaded file
        """

        params = {
            "fileFormat": file_format.value,
        }

        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                return DtlError("limit should be a positive integer")

            params["limit"] = limit

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/download",
            HttpMethod.GET,
            params=params,
            stream=True,
        )

        if isinstance(res, DtlError):
            return res

        with open(path, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024 * 32):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        return path

    def load_arrow_table(
        self, datastore_id: UUID, file_format: FileFormat = FileFormat.Csv, limit: Optional[int] = None, batch_size: int = 1024
    ) -> Union[DtlError, Table]:
        """
        Loads the resource in an in memory arrow buffer.
        This can be used either with Nvidia RAPIDS or pandas

        pandas:
        df = dtl.client.datastore.load_arrow_table(datastore_id).to_pandas()

        :param datastore_id: if of the resource to load
        :param file_format: can be FileFormat.Csv or FileFormat.Json. Json is useful if the data has commas in it, which will throw an error using csv.
        :param limit: elements to be loaded in the frame
        :param batch_size: size of the batch to be retrieved at a time from the collection
        :return:
        """

        params = {"fileFormat": file_format.value}

        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                return DtlError("limit should be a positive integer")

            params["limit"] = limit

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/download",
            HttpMethod.GET,
            params=params,
            stream=True,
        )

        if isinstance(res, DtlError):
            return res

        stream = ResponseStream(res.iter_content(batch_size))

        if file_format.value == 'Json':
            return json.read_json(stream)
        elif file_format.value == 'Csv':
            return csv.read_csv(stream)
        else:
            return DtlError(f'{file_format.value} is not supported for this method. Please use csv or json instead.')

        
    def upload(
        self, datastore_id: UUID, file_format: FileFormat, path: str, params: dict = {}
    ) -> Union[DtlError, None]:
        """
        Enable to upload a file to the specified resource through the platform

        :param datastore_id: id of the resource to upload the data through
        :param file_format: format of the file to be uploaded
        :param path: location of the file to upload on disk
        :return:
        """

        with open(path, "rb") as f:
            files = [MultiPartFile("content", f)]

            data = [
                MultiPartData("file-format", file_format.value),
                MultiPartData("params", "{}"),
            ]

            res = self.http_client.post_multipart_data(
                self.service_uri + "/datastores/" + str(datastore_id) + "/upload", files, data,
            )

            if isinstance(res, DtlError):
                return res

    def classify_fields(
        self,
        datastore_id: UUID,
        classifier_id: Union[str, UUID],
        target_fields: Optional[List[List[str]]] = None,
        sample_size: int = 100,
        rollup_strategy: RollupStrategy = WeightedAverage(),
        reclassification_behavior: ReclassificationBehavior = ReclassificationBehavior.ReplaceAutomatic,
    ) -> Union[DtlError, UUID]:
        """
        Classify the fields of a datastore. Classifications will be found within the ‘classifications’ property of
         each SchemaNode of the datastore.

        :param datastore_id: the id of the datastore to classify the fields of
        :param classifier_id: the classifier to apply classes to the data points, which will be used to calculate the
         classes of the fields
        :param rollup_strategy: describes the intended behavior for classification of fields. 
            It can be either ClassThreshold or WeightedAverage which is the default value.
        :param reclassification_behavior: describes the intended behavior if this operation reclassifies a
            field--defaults to replacing only automatic classifications from the specified classifier
        :return: the job id of the pipeline classifying the datastore fields
        """

        if isinstance(reclassification_behavior, str):
            return ReclassificationBehavior.parse_error(reclassification_behavior)

        params = {
            "classifier": str(classifier_id),
            "reclassification-behavior": str(reclassification_behavior.value),
        }

        payload = {}
        if target_fields is not None:
            payload["targetFields"] = target_fields
        if sample_size is not None:
            payload["sampleSize"] = sample_size

        payload["rollupStrategy"] = rollup_strategy._as_payload()

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + f"/classify",
            HttpMethod.POST,
            params=params,
            body=payload,
        )

        if isinstance(res, DtlError):
            return res
        elif res.status_code == 200:
            return UUID(res.json()["jobId"])
        else:
            return DtlError(res.text)

    def add_classifications(
        self, datastore_id: UUID, classifications: List[NodeClassification]
    ) -> Union[DtlError, List[SchemaNode]]:
        """
        Apply classes to specified fields (append, not override)

        :param datastore_id: the id of the datastore to add classes to
        :param classifications: a list of NodeClassifications, representing the fields to add classes to, and the classes to add
        :return: a list of altered SchemaNodes if successful, or DtlError if failed
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/classifications/add",
            HttpMethod.PUT,
            list(map(lambda x: x._as_payload(), classifications)),
        )

        if isinstance(res, DtlError):
            return res

        updated_schema_nodes = _parse_list(SchemaNode._schema_node_from_payload)(res)
        if isinstance(updated_schema_nodes, DtlError):
            return updated_schema_nodes

        return self.__load_schema_nodes_with_class_info(updated_schema_nodes)

    def remove_classifications(
        self, datastore_id: UUID, classifications: List[NodeClassification]
    ) -> Union[DtlError, List[SchemaNode]]:
        """
        Remove classes from specified fields.

        :param datastore_id: the id of the datastore to remove classes from
        :param classifications: a list of NodeClassifications, representing the fields from which classes should be removed, and the classes  to remove from those fields
        :return: a list of altered SchemaNodes if successful, or DtlError if failed
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/classifications/remove",
            HttpMethod.PUT,
            list(map(lambda x: x._as_payload(), classifications)),
        )

        if isinstance(res, DtlError):
            return res

        updated_schema_nodes = _parse_list(SchemaNode._schema_node_from_payload)(res)
        if isinstance(updated_schema_nodes, DtlError):
            return updated_schema_nodes

        return self.__load_schema_nodes_with_class_info(updated_schema_nodes)

    def override_classifications(
        self, datastore_id: UUID, classifications: List[NodeClassification]
    ) -> Union[DtlError, List[SchemaNode]]:
        """
        Remove all classes from specified fields, and then apply new classes to those fields.

        :param datastore_id: the id of the datastore whose fields should be overridden
        :param classifications: a list of NodeClassifications, representing the fields that should be cleared and the new classes for  those fields
        :return: a list of altered SchemaNodes if successful, or DtlError if failed
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/" + str(datastore_id) + "/classifications/replace",
            HttpMethod.PUT,
            list(map(lambda x: x._as_payload(), classifications)),
        )

        if isinstance(res, DtlError):
            return res

        updated_schema_nodes = _parse_list(SchemaNode._schema_node_from_payload)(res)
        if isinstance(updated_schema_nodes, DtlError):
            return updated_schema_nodes

        return self.__load_schema_nodes_with_class_info(updated_schema_nodes)

    def resample(self, datastore_ids: List[UUID]) -> Union[DtlError, List[Datastore]]:
        """
        Trigger resampling jobs for a given list of datastore ids.
        
        :param datastore_ids: ids of the datastores to refresh schema and samples
        :return: datastore payloads
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/datastores/schema-sample-jobs", HttpMethod.POST, body={"ids": datastore_ids}
        )
        if isinstance(res, DtlError):
            return res
        datastore_list = _parse_list(_datastore_from_payload)(res)

        return datastore_list
