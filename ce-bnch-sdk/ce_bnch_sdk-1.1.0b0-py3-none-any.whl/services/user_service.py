from typing import Iterable, List, Optional

from benchling_api_client.api.users import get_user, list_users
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import ListUsersSort, User, UsersPaginatedList
from benchling_sdk.services.base_service import BaseService


class UserService(BaseService):
    """
    Users.

    Benchling users.

    See https://benchling.com/api/reference#/Users
    """

    @api_method
    def get_by_id(self, user_id: str) -> User:
        """
        Get a user by ID.

        See https://benchling.com/api/reference#/Users/getUser
        """
        response = get_user.sync_detailed(client=self.client, user_id=user_id)
        return model_from_detailed(response)

    @api_method
    def _users_page(
        self,
        *,
        ids: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        modified_at: Optional[str] = None,
        member_of: Optional[Iterable[str]] = None,
        admin_of: Optional[Iterable[str]] = None,
        handles: Optional[Iterable[str]] = None,
        sort: Optional[ListUsersSort] = None,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
    ) -> Response[UsersPaginatedList]:
        return list_users.sync_detailed(  # type: ignore
            client=self.client,
            ids=none_as_unset(optional_array_query_param(ids)),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            modified_at=none_as_unset(modified_at),
            member_of=none_as_unset(optional_array_query_param(member_of)),
            admin_of=none_as_unset(optional_array_query_param(admin_of)),
            handles=none_as_unset(optional_array_query_param(handles)),
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
        member_of: Optional[Iterable[str]] = None,
        admin_of: Optional[Iterable[str]] = None,
        handles: Optional[Iterable[str]] = None,
        sort: Optional[ListUsersSort] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[User]:
        """
        List users.

        See https://benchling.com/api/reference#/Users/listUsers
        """

        def api_call(next_token: NextToken) -> Response[UsersPaginatedList]:
            return self._users_page(
                ids=ids,
                name=name,
                name_includes=name_includes,
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                modified_at=modified_at,
                member_of=member_of,
                admin_of=admin_of,
                handles=handles,
                sort=sort,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: UsersPaginatedList) -> Optional[List[User]]:
            return body.users

        return PageIterator(api_call, results_extractor)
