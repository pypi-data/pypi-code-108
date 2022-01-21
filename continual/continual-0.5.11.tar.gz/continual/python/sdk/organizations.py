from __future__ import annotations
from typing import List, Optional
from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from continual.python.sdk.projects import OrganizationProjectManager
from google.protobuf import field_mask_pb2
from continual.python.sdk.events import EventManager


class OrganizationManager(Manager):
    """Manages user resources."""

    name_pattern: str = "organizations/{user}"

    def get(self, id: str) -> Organization:
        """Get organization.

        Arguments:
            id: Organization name or id.

        Returns
            An organization.
        """
        req = management_pb2.GetOrganizationRequest(name=self.name(id))
        resp = self.client._management.GetOrganization(req)
        return Organization.from_proto(resp, client=self.client)

    def list(self, page_size: Optional[int] = None) -> List[Organization]:
        """List organizations.

        Arguments:
            page_size: Number of items to return.

        Returns:
            A list of organizations.
        """
        req = management_pb2.ListOrganizationsRequest(page_size=page_size)
        resp = self.client._management.ListOrganizations(req)
        return [
            Organization.from_proto(u, client=self.client) for u in resp.organizations
        ]

    def list_all(self) -> Pager[Organization]:
        """List all organizations.

        Pages through all organization using an iterator.

        Returns:
            A iterator of all organizations.
        """

        def next_page(next_page_token):
            req = management_pb2.ListOrganizationsRequest(page_token=next_page_token)
            resp = self.client._management.ListOrganizations(req)
            return (
                [
                    Organization.from_proto(u, client=self.client)
                    for u in resp.organizations
                ],
                resp.next_page_token,
            )

        return Pager(next_page)

    def create(self, display_name: str) -> Organization:
        """Create an organization.

        Arguments:
            display_name: Display name.

        Returns:
            A new organization.
        """
        req = management_pb2.CreateOrganizationRequest(
            organization=types.Organization(display_name=display_name).to_proto()
        )
        resp = self.client._management.CreateOrganization(req)
        return Organization.from_proto(resp, client=self.client)

    def delete(self, id: str) -> None:
        """Delete an organization.

        Arguments:
            id: Organization name or id.
        """

        req = management_pb2.DeleteOrganizationRequest(name=self.name(id))
        self.client._management.DeleteOrganization(req)

    def update(
        self,
        id: str,
        display_name: Optional[str] = None,
    ) -> Organization:
        """Update organization.

        Arguments:
            display_name:  Display name.

        Returns:
            Updated organization.
        """
        paths = []
        if display_name is not None:
            paths.append("display_name")
        req = management_pb2.UpdateOrganizationRequest(
            update_mask=field_mask_pb2.FieldMask(paths=paths),
            organization=Organization(
                name=self.name(id),
                display_name=display_name,
            ).to_proto(),
        )
        resp = self.client._management.UpdateOrganization(req)
        return Organization.from_proto(resp, client=self.client)


class Organization(Resource, types.Organization):
    """Organization resource."""

    manager: OrganizationManager
    projects: OrganizationProjectManager
    events: EventManager
    name_pattern = "organizations/{users}"

    def _init(self):
        self.manager = OrganizationManager(parent=self.parent, client=self.client)
        self.projects = OrganizationProjectManager(parent=self.name, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def delete(self) -> None:
        """Delete organization."""
        self.manager.delete(self.name)

    def update(
        self,
        display_name: Optional[str] = None,
    ) -> Organization:
        """Update organization.

        Arguments:
            display_name:  Display name.

        Returns:
            Updated organization.
        """
        return self.manager.update(
            self.name,
            display_name=display_name,
        )
