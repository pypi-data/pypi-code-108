from typing import Union, List, Callable
from uuid import UUID

from datalogue.clients._http import _HttpClient, HttpMethod, MultiPartData, MultiPartFile
from datalogue.dtl_utils import _parse_list, _parse_uuid
from datalogue.errors import DtlError
from datalogue.models.ontology import Ontology, OntologyNode, ClassMapping
from datalogue.models.permission import OntologyPermission
from datalogue.models.scope_level import Scope


class OntologyClient:
    """
    Client to interact with the ontology
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/yggy"
        self.mappings_uri = "/scout/classes/mappings"

    def create(self, ontology: Ontology) -> Union[DtlError, Ontology]:
        """
        Create :class:`Ontology` object given ontology object
        :return: :class:`Ontology` object, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/ontology/import", HttpMethod.POST, body=Ontology._as_payload(ontology),
        )

        if isinstance(res, DtlError):
            return res

        return Ontology._from_payload(res)

    def get(self, ontology_id: UUID) -> Union[DtlError, Ontology]:
        """
        Get :class:`Ontology` object given ontology_id
        :return: :class:`Ontology` object, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(self.service_uri + f"/ontology/{str(ontology_id)}", HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return Ontology._from_payload(res)

    def update(self, ontology_id: UUID, updated_ontology: Ontology) -> Union[DtlError, Ontology]:
        """
        Update :class:`Ontology` method that will replace the existing ontology.
        The structure of this ontology will replace the existing structure. Please make sure you include a full
        ontological structure and not just the changes/modifications
        :param ontology_id: UUID is the id of the ontology that you want to replace/modify/update.
        :param updated_ontology: Ontology object that will replace the existing ontology.
        :return: The updated Ontology if successful, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(
            self.service_uri + f"/ontology/{str(ontology_id)}",
            HttpMethod.PUT,
            body=Ontology._as_payload(updated_ontology),
        )

        if isinstance(res, DtlError):
            return res

        return Ontology._from_payload(res)

    def delete(self, ontology_id: UUID) -> Union[DtlError, bool]:
        """
        Delete :class:`Ontology` based on the given ontology_id
        :return: True if successful, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(
            self.service_uri + f"/ontology/{str(ontology_id)}", HttpMethod.DELETE
        )
        if isinstance(res, DtlError):
            return res
        else:
            return True

    def get_class(self, class_id: UUID) -> Union[DtlError, OntologyNode]:
        """
        Retrieve an ontological class locally/ a class is represented as an OntologyNode object

        :param class_id: id of the ontological class to retrieve
        :return: the OntologyNode object corresponding to the id
        """
        res = self.http_client.make_authed_request(f"/yggy/entity/{class_id}", HttpMethod.GET)
        if isinstance(res, DtlError):
            return res

        return OntologyNode.from_payload(res)

    def share(
        self, ontology_id: UUID, target_id: UUID, target_type: Scope, permission: OntologyPermission,
    ) -> Union[DtlError, bool]:
        """
        Share the given ontology with an specific user or group with the desired permission (Write or Read)

        :param ontology_id: UUID is the id of the ontology that you want to share
        :param target_id: UUID is the id of the User the Group or Organization you want to share with (depending on the target_type param)
        :param target_type: Scope (`Group`, `User` or `Organization`) with whom you want to share the ontology. It can be a User, Group or Organization.
        :param permission: OntologyPermission (`Write` or `Read`) the permission you want to grant
        :return: True if successful, else returns :class:`DtlError`
        """

        body = Ontology._create_body_for_sharing(target_id, target_type, permission)
        if isinstance(body, DtlError):
            return body

        res = self.http_client.make_authed_request(
            self.service_uri + f"/ontology/{str(ontology_id)}/share", HttpMethod.POST, body,
        )
        if isinstance(res, DtlError):
            return res
        else:
            return True

    def unshare(self, ontology_id: UUID, target_id: UUID, target_type: Scope) -> Union[DtlError, bool]:
        """
        Unshare the given ontology from an specific user or group. That User/Group won't be able to access that ontology
        any more.

        :param ontology_id: UUID is the id of the ontology that you want to unshare
        :param target_id: UUID is the id of the User, the Group or Organization you want to unshare from (depending on the target_type param)
        :param target_type: Scope (`Group`, `User` or `Organization`) with whom you want to unshare the ontology. It can be a User, Group or Organization.
        :return: True if successful, else returns :class:`DtlError`
        """
        body = Ontology._create_body_for_unsharing(target_id, target_type, "None")

        if isinstance(body, DtlError):
            return body

        res = self.http_client.make_authed_request(
            self.service_uri + f"/ontology/{str(ontology_id)}/share", HttpMethod.POST, body,
        )
        if isinstance(res, DtlError):
            return res
        else:
            return True

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Ontology]]:
        """
        List the ontologies

        :param page: page to be retrieved
        :param item_per_page: number of ontologies to be put in a page
        :return: Returns a List of all the available Ontologies or an error message as a string

        """
        res = self.http_client.make_authed_request(
            self.service_uri + f"/ontologies?page={page}&size={item_per_page}", HttpMethod.GET,
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(Ontology._from_payload)(res)

    def overwrite(self, ontology_id: UUID, ontology: Ontology) -> Union[DtlError, Ontology]:
        """
        It overwrites all ontology and node information for the given ontology id including training data if there is an ontology for the given id. 
        Otherwise, it creates brand new ontology with the given ontology id
        :return: :class:`Ontology` object, else returns :class:`DtlError`
        """
        res = self.http_client.make_authed_request(
            self.service_uri + f"/ontology/{ontology_id}/import", HttpMethod.PUT, body=Ontology._as_payload(ontology),
        )

        if isinstance(res, DtlError):
            return res

        return Ontology._from_payload(res)

    def get_class_mappings(self, class_ids: List[UUID]) -> Union[DtlError, List[ClassMapping]]:
        """
        Retrieve source and destination mappings of given classes
        :param class_ids:  UUID of classes
        :return: List of ClassMappings
        """
        req_body = []
        for i in class_ids:
            req_body.append(str(i))

        res = self.http_client.make_authed_request(self.mappings_uri, HttpMethod.POST, body=req_body)
        if isinstance(res, DtlError):
            return res

        return _parse_list(ClassMapping.from_payload)(res)

    ####### Internal functions
    def __iterate_over_tree(
        self, current_node: OntologyNode, f: Callable[[OntologyNode], OntologyNode]
    ) -> OntologyNode:
        if not current_node.children:
            updated_node = f(current_node)
            return updated_node
        else:
            updated_children = list(map(lambda c: self.__iterate_over_tree(c, f), current_node.children))
            updated_node = f(current_node)
            updated_node.children = updated_children
            return updated_node

    def __get_node_dataset_ids(self, node_id: UUID) -> List[str]:
        entity_res = self.http_client.make_authed_request(f"/yggy/entity/{node_id}", HttpMethod.GET)
        training_data_list = entity_res.get("trainingDataInfo")
        if training_data_list is None:
            training_data_list = []

        dataset_ids = []
        for trainingData in training_data_list:
            dataset_ids.append(trainingData["datasetId"])

        return dataset_ids

    def __get_node_path(self, node_id: UUID, dataset_id: str) -> List[str]:
        entity_res = self.http_client.make_authed_request(f"/yggy/entity/{node_id}", HttpMethod.GET)
        training_data_list = entity_res.get("trainingDataInfo")
        if training_data_list is None:
            training_data_list = []

        path = []
        for trainingData in training_data_list:
            if dataset_id == trainingData.get("datasetId"):
                path = trainingData.get("nodePath")

        return path
