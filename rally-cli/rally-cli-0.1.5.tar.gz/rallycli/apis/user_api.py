import asyncio
from logging import getLogger
from typing import List, Optional, TypeVar, Tuple

import urllib3

from rallycli import BaseAPI
from rallycli.models import User, type_names

## logger definition
logger = getLogger(__name__)
## Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class UserAPI(BaseAPI):
    """Client class for accessing User model for Rally Software API."""

    def get_this_user(self):
        user: User = self.get_element_by_ref(f"{self._baseurl}user", model_class=User)
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        query: str = f"( UserName = {username} )"
        users: List[User] = self.query(query, "user", model_class=User)
        if not users:
            logger.warning(f"User with UserName: '{username}' NOT found")
            return None
        return users[0]

    def create_user(self, user_model: User) -> Optional[User]:
        """Create user"""
        result_object: dict = self._create_from_model(user_model.copy_for_create(), type_names.USER)
        return self._get_rally_object(result_object, User)

    def update_user(self, user_model: User, body_keys: List[str] = None) -> Optional[User]:
        """Update user"""
        key_set: set = set(body_keys) if body_keys else set()
        result_object: dict = self._update_from_model(user_model.copy_for_update(body_keys=key_set),
                                                      type_names.USER)
        return self._get_rally_object(result_object, User)

    def update_user_list(self,
                         user_lst: List[User],
                         body_keys: List[str] = None) -> Optional[List[User]]:
        """Async IO update of a list of users. User objects new _ref field to be updated"""
        key_set: set = set(body_keys) if body_keys else set()
        # List of Tuple [url, update_data]
        url_data: List[Tuple[str, dict]] = []
        for user in user_lst:
            url: str = f"{user._ref}{BaseAPI._security_key}"
            data: dict = {"user": user.copy_for_update(body_keys=key_set)}
            url_data.append((url, data))

        result_objects: List[dict] = asyncio.run(self._async_post_elements(url_data))
        objs: List[User] = [User(robj) for robj in result_objects]
        return objs

    def add_user_to_project_membership(self, user_ref: str, project_ref: str):
        """TODO"""
        pass

    def add_user_permission_for_project(self, user_ref: str, project_ref: str, perm: str):
        """TODO"""
        pass
