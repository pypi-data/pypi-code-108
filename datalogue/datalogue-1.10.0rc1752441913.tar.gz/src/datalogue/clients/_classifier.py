from collections import namedtuple
from datetime import datetime
from typing import Optional, Union, List
from uuid import UUID

from datalogue.errors import DtlError
from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.models.permission import Permission
from datalogue.models.permission import ObjectType, SharePermission
from datalogue.models.classifier import (
    Classifier,
    ClassificationMethod,
    ClassifierDataPoint,
    ClassifiedDataPoint,
)
from datalogue.models.regex import Regex
from datalogue.models.scope_level import Scope
from datalogue.dtl_utils import _parse_list, is_valid_uuid
from datalogue.clients.ontology import OntologyClient
from datalogue.models.ontology import OntologyNode


class _ClassifierClient:
    """
    Client to interact with the Classifiers
    """

    def __init__(self, http_client: _HttpClient, ontology_client: OntologyClient):
        self.http_client = http_client
        self.service_uri = "/scout"
        self.ontology_client = ontology_client

    def _fill_domain(self, classifier: Classifier, class_ids: List[str]):
        classifier.domain = []
        for class_id in class_ids:
            res = self.ontology_client.get_class(UUID(class_id))
            if isinstance(res, DtlError):
                res = OntologyNode(name="Permission denied", description="Permission denied", id=UUID(class_id),)
            classifier.domain.append(res)

    def create(self, classifier: Classifier) -> Union[DtlError, Classifier]:
        """
        Creates the Classifier as specified.

        :param classifier: Classifier definition
        :return: Classifier reference with more information id, owner, description
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/classifiers", HttpMethod.POST, classifier._as_payload()
        )

        if isinstance(res, DtlError):
            return res

        new_classifier = Classifier._from_payload(res)
        self._fill_domain(new_classifier, res.get("classIds"))
        return new_classifier

    def update(
        self,
        id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        classification_methods: Optional[List[ClassificationMethod]] = None,
        default_class_id: Optional[UUID] = None,
    ) -> Union[DtlError, Classifier]:
        """
        Updates the Classifier as specified.

        :param id: id of classifier to update
        :param name: Updated name of the classifier (Optional)
        :param description: Updated description of the classifier (Optional)
        :param classification_methods: Updated classification_methods of the classifier (Optional)
        :param default_class_id: Updated default_class_id of the classifier. If empty string is provided, the default_class_id is set to None. (Optional)
        :return: Regex reference with more information id, owner, regex test sample statuses
        """

        req_body = {}
        if name is not None:
            req_body["name"] = name
        if description is not None:
            req_body["description"] = description
        if classification_methods is not None:
            req_body["classificationMethods"] = list(map(lambda m: m._as_payload(), classification_methods))
        if default_class_id is not None:
            if default_class_id == "" or is_valid_uuid(default_class_id):
                req_body["defaultClassId"] = str(default_class_id)
            else:
                raise DtlError(
                    "default_class_id can either be None, empty string, or in UUID format. Other formats are not allowed."
                )

        res = self.http_client.make_authed_request(
            self.service_uri + "/classifiers/" + str(id), HttpMethod.PUT, req_body
        )

        updated_classifier = Classifier._from_payload(res)
        self._fill_domain(updated_classifier, res.get("classIds"))
        return updated_classifier

    def get(self, id: Union[str, UUID]) -> Union[DtlError, Classifier]:
        """
        Retrieve a classifier by its ID.
        :param id: the id of the classifier to be retrieved locally
        :return: the classifier if successful, or a DtlError if failed
        """
        res = self.http_client.make_authed_request(self.service_uri + "/classifiers/" + str(id), HttpMethod.GET)
        if isinstance(res, DtlError):
            return res

        new_classifier = Classifier._from_payload(res)
        self._fill_domain(new_classifier, res.get("classIds"))
        return new_classifier

    def delete(self, classifier_id: Union[str, UUID]) -> Union[DtlError, bool]:
        """
        Delete a classifier.

        :param classifier_id: id of the classifier to be deleted
        :return: True if successful, or DtlError if failed
        """

        res = self.http_client.make_authed_request(
            self.service_uri + "/classifiers/" + str(classifier_id), HttpMethod.DELETE
        )

        if isinstance(res, DtlError):
            return res

        return True

    def share(
        self, classifier_id: UUID, target_id: UUID, target_type: Scope, permission: Permission,
    ) -> Union[SharePermission, DtlError]:
        """
        Modify the sharing permission for the given classifier. The change can be performed to user, group or organization with the desired permission (Share, Write or Read)
        In order to share, the user needs to have `Share` permission. Classifiers owners always have `Share` permission for that classifier.

        :param classifier_id: UUID is the id of the classifier that you want to share
        :param target_id: UUID is the id of the User, Group or Organization you want to share with (depending on the target_type param)
        :param target_type: Scope (`Organization`, `Group` or `User`) with whom you want to share the classifier. It can be Organization Group or User.
        :param permission: Permission (`Share`, `Write` or `Read`) the permission you want to grant
        :return: If successful returns the permission you granted specifying the `target_id` (UUID),
        the `target_type` (User, Group or Organization) and the `permission` level (Read, Write or Share) you just granted.
        (i.e. {target_id: str, target_type: str, permission: str}),
        else returns :class:`DtlError`.
        """

        url = f"/classifiers/{str(classifier_id)}/shares?targetType={str(target_type.value)}&targetId={str(target_id)}&permission={str(permission.value)}"

        resp = self.http_client.execute_authed_request(self.service_uri + url, HttpMethod.POST)

        if isinstance(resp, DtlError):
            return resp
        elif resp.status_code == 200:
            return SharePermission(object_type=ObjectType.Classifier).from_payload(resp.json())
        else:
            return DtlError(resp.text)

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Regex]]:
        """
        List all classifiers.

        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available classifiers if successful, or DtlError if failed
        """
        req_params = {}
        if isinstance(page, int):
            req_params["page"] = page
        if isinstance(item_per_page, int):
            req_params["size"] = item_per_page
        res = self.http_client.make_authed_request(self.service_uri + "/classifiers", HttpMethod.GET, params=req_params)
        if isinstance(res, DtlError):
            return res

        return _parse_list(Classifier._from_payload)(res)

    def search(
        self,
        by_name: Optional[List[str]] = None,
        by_description: Optional[List[str]] = None,
        by_default_class: Optional[List[str]] = None,
        by_owner: Optional[List[UUID]] = None,
        results_per_page: int = 25,
        page: int = 1,
    ) -> Union[DtlError, List[Classifier]]:
        """
         Search among all backend <object>, using any numbers of queries as
         the search criteria
         Multiple items within a query will be applied with OR logic —
         multiple queries will be applied with AND logic
         The wildcard operators: `?` and `*` can be used as wildcards,
         matching one and any number of additional characters, respectively
         :param by_name: query based on classifier name
         :param by_description: query based on description
         :param by_default_class: query based on default class in domain
         :param by_owner: query based on owner id
         :param results_per_page: number of results to include per page
         :param page: page to display
         :return: a list of classifiers, sorted by query similarity, if
         successful, or DtlError if failed
        """
        req_params = {}
        query = {}
        if isinstance(page, int):
            req_params["page"] = page
        if isinstance(results_per_page, int):
            req_params["size"] = results_per_page

        if isinstance(by_name, list):
            query["name"] = by_name
        if isinstance(by_description, list):
            query["description"] = by_description
        if isinstance(by_default_class, list):
            query["defaultClassId"] = by_default_class
        if isinstance(by_owner, list):
            query["owner"] = by_owner
        req_params["query"] = query

        res = self.http_client.make_authed_request(
            self.service_uri + "/classifiers/search", HttpMethod.POST, body=req_params
        )
        if isinstance(res, DtlError):
            return res

        return _parse_list(Classifier._from_payload)(res)

    def classify_datapoint(
        self,
        classifier_id: Union[str, UUID],
        value: Union[str, float, int, datetime, bool, None],
        field_name: Optional[str] = None,
    ) -> Union[ClassifiedDataPoint, DtlError, None]:
        """
         Test a classifier by classifying a single datapoint with specified value and optional field name.

         :param classifier_id: the classifier to be tested
         :param value: the value of the test datapoint to be classified
         :param field_name: can be used to add a field name to the datapoint.
          In the wild, most datapoints will belong to a field with an associated field name
         :return: the class as an OntologyNode if successful classification and match found,
          None if successful classification but no match found, or DtlError if failed
        """

        datapoint = ClassifierDataPoint(value=value, label=field_name)
        datapoints_list = [datapoint._as_payload()]

        res = self.http_client.make_authed_request(
            self.service_uri + f"/classifiers/{classifier_id}/test", HttpMethod.POST, body=datapoints_list,
        )
        if isinstance(res, DtlError):
            return res
        classified = res[0]
        if classified is None:
            return None

        class_result = self.ontology_client.get_class(UUID(classified["classId"]))
        if isinstance(class_result, DtlError):
            return class_result
        else:
            return ClassifiedDataPoint(
                test_class=class_result, score=classified["score"], value=value, field_name=field_name,
            )
