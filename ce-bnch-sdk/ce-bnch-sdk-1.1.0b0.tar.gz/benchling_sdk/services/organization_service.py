from typing import Iterable, List, Optional

from benchling_api_client.api.organizations import get_organization, list_organizations
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import ListOrganizationsSort, Organization, OrganizationsPaginatedList
from benchling_sdk.services.base_service import BaseService


class OrganizationService(BaseService):
    """
    Organizations.

    View organization objects.

    See https://benchling.com/api/reference#/Organizations
    """

    @api_method
    def get_by_id(self, organization_id: str) -> Organization:
        """
        Get an organization by ID.

        Returns an organization by ID if the caller has permission to view. The following roles have view permission:
        * tenant admins
        * members of the organization

        See https://benchling.com/api/reference#/Organizations/getOrganization
        """
        response = get_organization.sync_detailed(client=self.client, organization_id=organization_id)
        return model_from_detailed(response)

    @api_method
    def _organizations_page(
        self,
        *,
        ids: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        modified_at: Optional[str] = None,
        has_members: Optional[Iterable[str]] = None,
        has_admins: Optional[Iterable[str]] = None,
        sort: Optional[ListOrganizationsSort] = None,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
    ) -> Response[OrganizationsPaginatedList]:
        return list_organizations.sync_detailed(  # type: ignore
            client=self.client,
            ids=none_as_unset(optional_array_query_param(ids)),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            modified_at=none_as_unset(modified_at),
            has_members=none_as_unset(optional_array_query_param(has_members)),
            has_admins=none_as_unset(optional_array_query_param(has_admins)),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
            sort=none_as_unset(sort),
        )

    def list(
        self,
        *,
        ids: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        modified_at: Optional[str] = None,
        has_members: Optional[Iterable[str]] = None,
        has_admins: Optional[Iterable[str]] = None,
        sort: Optional[ListOrganizationsSort] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[Organization]:
        """
        List organizations.

        Returns all organizations that the caller has permission to view. The following roles have view permission:
        * tenant admins
        * members of the organization

        See https://benchling.com/api/reference#/Organizations/listOrganizations
        """

        def api_call(next_token: NextToken) -> Response[OrganizationsPaginatedList]:
            return self._organizations_page(
                ids=ids,
                name=name,
                name_includes=name_includes,
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                modified_at=modified_at,
                has_members=has_members,
                has_admins=has_admins,
                sort=sort,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: OrganizationsPaginatedList) -> Optional[List[Organization]]:
            return body.organizations

        return PageIterator(api_call, results_extractor)
