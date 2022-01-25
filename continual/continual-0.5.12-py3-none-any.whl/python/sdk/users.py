from __future__ import annotations
from typing import List, Optional
from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from google.protobuf import field_mask_pb2
from continual.python.sdk.events import EventManager


class UserManager(Manager):
    """Manages user resources."""

    name_pattern: str = "users/{user}"

    def get(self, id: str) -> User:
        """Get user.

        Arguments:
            id: User name or id.

        Returns
            A user.
        """
        req = management_pb2.GetUserRequest(name=self.name(id))
        resp = self.client._management.GetUser(req)
        return User.from_proto(resp, client=self.client)

    def list(self, page_size: Optional[int] = None) -> List[User]:
        """List users.

        Arguments:
            page_size: Number of itmes to return.

        Returns:
            A list of users.
        """
        req = management_pb2.ListUsersRequest(page_size=page_size)
        resp = self.client._management.ListUsers(req)
        return [User.from_proto(u, client=self.client) for u in resp.users]

    def list_all(self) -> Pager[User]:
        """List all users.

        Pages through all users using an iterator.

        Returns:
            A iterator of all users.
        """

        def next_page(next_page_token):
            req = management_pb2.ListUsersRequest(page_token=next_page_token)
            resp = self.client._management.ListUsers(req)
            return (
                [User.from_proto(u, client=self.client) for u in resp.users],
                resp.next_page_token,
            )

        return Pager(next_page)

    def delete(self, id: str) -> None:
        """Delete a user.

        Arguments:
            id: Name or id.
        """

        req = management_pb2.DeleteUserRequest(name=self.name(id))
        self.client._management.DeleteUser(req)

    def update(
        self,
        id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        bio: Optional[str] = None,
        location: Optional[str] = None,
    ) -> User:
        """Update user.

        Arguments:
            first_name:  First name of display name.
            last_name:  Last name of display name.
            bio: Bio.
            location: Location.

        Returns:
            Updated user.
        """
        paths = []
        if first_name is not None:
            paths.append("first_name")
        if last_name is not None:
            paths.append("last_name")
        if bio is not None:
            paths.append("bio")
        if location is not None:
            paths.append("location")
        req = management_pb2.UpdateUserRequest(
            update_mask=field_mask_pb2.FieldMask(paths=paths),
            user=User(
                name=self.name(id),
                first_name=first_name,
                last_name=last_name,
                bio=bio,
                location=location,
            ).to_proto(),
        )
        resp = self.client._management.UpdateUser(req)
        return User.from_proto(resp, client=self.client)


class User(Resource, types.User):
    """User resource."""

    manager: UserManager
    events: EventManager
    name_pattern = "users/{users}"

    def _init(self):
        self.manager = UserManager(parent=self.parent, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def delete(self) -> None:
        """Delete user."""
        self.manager.delete(self.name)

    def update(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        bio: Optional[str] = None,
        location: Optional[str] = None,
    ) -> User:
        """Update user.

        Arguments:
            first_name:  First name of display name.
            last_name:  Last name of display name.
            bio: Bio.
            location: Location.

        Returns:
            Updated user.
        """
        return self.manager.update(
            self.name,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            location=location,
        )
