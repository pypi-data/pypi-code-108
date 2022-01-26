from typing import Optional, Union, List
from uuid import UUID

from datalogue.errors import DtlError
from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.models.permission import Permission
from datalogue.models.regex import Regex, SearchOrder, RegexTestSample
from datalogue.models.permission import ObjectType, SharePermission
from datalogue.models.scope_level import Scope
from datalogue.dtl_utils import _parse_list


class _RegexClient:
    """
    Client to interact with the Regexes
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def create(self, regex: Regex) -> Union[DtlError, Regex]:
        """
        Creates the Regex as specified.

        :param regex: Regex definition
        :return: Regex reference with more information id, owner, regex test sample statuses
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/regexes", HttpMethod.POST, Regex._as_payload(regex)
        )

        if isinstance(res, DtlError):
            return res

        return Regex._from_payload(res)

    def update(
        self, id: UUID, name: Optional[str] = None, description: Optional[str] = None, pattern: Optional[str] = None,
    ) -> Union[Regex, DtlError]:
        """
        Update the regex as specified.

        :param id: id of regex to update
        :param name: Updated name of the regex (Optional)
        :param description: Updated description of the regex (Optional)
        :param pattern: Updated pattern of the regex (Optional)
        :return: Regex reference with more information id, owner, regex test sample statuses
        """
        req_body = {}
        if name is not None:
            req_body["name"] = name
        if description is not None:
            req_body["description"] = description
        if pattern is not None:
            req_body["pattern"] = pattern

        res = self.http_client.make_authed_request(self.service_uri + "/regexes/" + str(id), HttpMethod.PUT, req_body)

        if isinstance(res, DtlError):
            return res

        return Regex._from_payload(res)

    def share(
        self, regex_id: UUID, target_id: UUID, target_type: Scope, permission: Permission,
    ) -> Union[SharePermission, DtlError]:
        """
        Modify the sharing permission for the given regex. The change can be performed to user, group or organization with the desired permission (Share, Write or Read)
        In order to share, the user needs to have `Share` permission. Regex owners always have `Share` permission for that regex.

        :param regex_id: UUID is the id of the regex that you want to share
        :param target_id: UUID is the id of the User, Group or Organization you want to share with (depending on the target_type param)
        :param target_type: Scope (`Organization`, `Group` or `User`) with whom you want to share the regex. It can be Organization Group or User.
        :param permission: Permission (`Share`, `Write` or `Read`) the permission you want to grant
        :return: If successful returns the permission you granted specifying the `target_id` (UUID),
        the `target_type` (User, Group or Organization) and the `permission` level (Read, Write or Share) you just granted.
        (i.e. {target_id: str, target_type: str, permission: str}),
        else returns :class:`DtlError`.
        """

        url = f"/scout/regexes/{str(regex_id)}/shares?targetType={str(target_type.value)}&targetId={str(target_id)}&permission={str(permission.value)}"

        resp = self.http_client.execute_authed_request(url, HttpMethod.POST)

        if isinstance(resp, DtlError):
            return resp
        elif resp.status_code == 200:
            return SharePermission(object_type=ObjectType.Regex).from_payload(resp.json())
        else:
            return DtlError(resp.text)

    def search(
        self,
        by_name: Optional[List[str]] = None,
        by_description: Optional[List[str]] = None,
        by_test_data: Optional[List[str]] = None,
        by_match: Optional[str] = None,
        by_owner: Optional[List[UUID]] = None,
        page: int = 1,
        results_per_page: int = 25,
    ) -> Union[List[Regex], DtlError]:
        """
        Search for a regex (full-text search), where defined (non-None) parameters/queries are the search criteria
        joint by AND operator and those not defined are ignored as search criteria.

        :param by_name: (Optional) Name of regex to be searched for (Optional)
        :param by_description: (Optional) Description of the regex to be searched for (Optional)
        :param by_test_data: (Optional) The textual test data of a regex to be searched for (Optional)
        :param by_match: (Optional) Text that can be pattern matched by the regex to be searched for (Optional)
        :param by_owner: (Optional) Regexes created by this particular owner
        :param page: The index of the page to get the regexes from. (Optional, defaults to first page index 1)
        :param results_per_page: Size per page. (Optional, defaults to 25)
        :return: List of regex references
        """
        body = {}
        query = {}
        if isinstance(by_name, list):
            query["name"] = by_name
        if isinstance(by_description, list):
            query["description"] = by_description
        if isinstance(by_test_data, list):
            query["testData.text"] = by_test_data
        if isinstance(by_owner, list):
            query["owner"] = str(by_owner)

        if isinstance(by_match, str):
            body["match"] = by_match
        if isinstance(page, int):
            body["page"] = page
        if isinstance(results_per_page, int):
            body["size"] = results_per_page
        if len(query.keys()) == 0:
            body["query"] = "*"
        else:
            body["query"] = query

        res = self.http_client.make_authed_request(self.service_uri + "/regexes/search", HttpMethod.POST, body=body)
        if isinstance(res, DtlError):
            return res

        return _parse_list(Regex._from_payload)(res)

    def test(self, id: UUID, data: List[str]) -> Union[List[RegexTestSample], DtlError]:
        """
        Test data against existing regex with given id

        :param id: id of existing regex
        :param data: List of string to verify against existing regex
        :return: data with corresponding statuses if regex with given id exists
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/regexes/" + str(id) + "/match", HttpMethod.PUT, data
        )
        if isinstance(res, DtlError):
            return res
        return _parse_list(RegexTestSample._from_payload)(res)

    def add_test_data(self, id: UUID, test_data: List[str]) -> Union[Regex, DtlError]:
        """
        Add test data to regex

        :param id: id of regex to update
        :param test_data: list of sentences which will be added as test sample
        :return: Regex reference with more information id, owner, regex test sample statuses
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/regexes/" + str(id) + "/test-data", HttpMethod.PUT, test_data,
        )
        if isinstance(res, DtlError):
            return res

        return Regex._from_payload(res)

    def remove_test_data(self, id: UUID, test_data: List[str]) -> Union[Regex, DtlError]:
        """
        Remove test data from regex

        :param id: id of regex to update
        :param test_data: list of sentences which will be removed from test sample
        :return: Regex reference with more information id, owner, regex test sample statuses
        """
        res = self.http_client.make_authed_request(
            self.service_uri + "/regexes/" + str(id) + "/test-data", HttpMethod.DELETE, test_data,
        )
        if isinstance(res, DtlError):
            return res

        return Regex._from_payload(res)

    def get(self, id: Union[str, UUID]) -> Union[DtlError, Regex]:
        """
        Retrieve a regex by its ID.
        :param regex_id: the id of the regex to be retrieved locally
        :return: the regex if successful, or a DtlError if failed
        """
        res = self.http_client.make_authed_request(self.service_uri + "/regexes/" + str(id), HttpMethod.GET)
        if isinstance(res, DtlError):
            return res

        return Regex._from_payload(res)

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Regex]]:
        """
        List all regexes.

        :param page: page to be retrieved
        :param item_per_page: number of items to be put in a page
        :return: Returns a List of all the available regex if successful, or DtlError if failed
        """
        req_params = {}
        if isinstance(page, int):
            req_params["page"] = page
        if isinstance(item_per_page, int):
            req_params["item_per_page"] = item_per_page
        res = self.http_client.make_authed_request(self.service_uri + "/regexes", HttpMethod.GET, params=req_params)
        if isinstance(res, DtlError):
            return res

        return _parse_list(Regex._from_payload)(res)

    def delete(self, regex_id: Union[str, UUID]) -> Union[DtlError, bool]:
        """
        Delete a regex.

        :param regex_id: id of the regex to be deleted
        :return: True if successful, or DtlError if failed
        """

        resp = self.http_client.execute_authed_request(
            self.service_uri + "/regexes/" + str(regex_id), HttpMethod.DELETE
        )

        if isinstance(resp, DtlError):
            return resp
        elif resp.status_code == 200:
            return True
        else:
            return DtlError(resp.text)
