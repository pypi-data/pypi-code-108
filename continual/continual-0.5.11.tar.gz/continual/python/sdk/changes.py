from __future__ import annotations
import os
from typing import List, Union, Optional, Iterator
from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.waiter import wait
from continual.python.sdk.iterators import Pager
from continual.python.sdk.events import EventManager


class ChangeManager(Manager):
    """Manages change workflows"""

    name_pattern: str = "projects/{project}/changes/{change}"

    def push(
        self,
        paths: Union[List[str], str],
        plan_only=False,
        purge=False,
        train_all=False,
        train_none=False,
        profile_none=False,
        update_all=False,
        message=None,
        trigger="SDK",
        yaml_text=None,
        resource="",
    ) -> Change:
        """Change a directory of schemas to Continual.

        Change recursively walks a directory and uploads all yaml
        schema files found.

        Args:
            paths: Files or directories containing schemas.

        Returns:
            A list of feature sets.
        """
        all_files = []
        if isinstance(paths, str):
            paths = [paths]

        for path in paths:
            if os.path.isdir(path):
                for root, dirs, rfiles in os.walk(path, topdown=False):
                    for name in rfiles:
                        if name.endswith(".yaml") or name.endswith(".yml"):
                            all_files.append(os.path.join(root, name))
            elif (
                os.path.isfile(path) and path.endswith(".yaml") or path.endswith(".yml")
            ):
                all_files.append(path)
            elif not resource:
                raise ValueError("path must be a yaml file or directory.")

        schemas = []
        for f in all_files:
            with open(f, "r") as inp_file:
                schema_text = inp_file.read()
                schemas.append(schema_text)

        if yaml_text is not None:
            schemas.append(yaml_text)

        req = management_pb2.CreateChangeRequest(
            parent=self.parent,
            schemas=schemas,
            plan_only=plan_only,
            purge=purge,
            profile_none=profile_none,
            update_all=update_all,
            train_all=train_all,
            train_none=train_none,
            message=message,
            trigger=trigger,
            resource=resource,
        )
        resp = self.client._management.CreateChange(req)
        return Change.from_proto(resp, client=self.client)

    def rerun(self, id: str):
        req = management_pb2.ReRunRequest(name=self.name(id))
        resp = self.client._management.ReRun(req)
        return Change.from_proto(resp, client=self.client)

    def get(self, id: str):
        req = management_pb2.GetChangeRequest(name=self.name(id))
        resp = self.client._management.GetChange(req)
        return Change.from_proto(resp, client=self.client)

    def list(
        self,
        page_size: Optional[int] = None,
        filters: List[str] = None,
        all_projects: bool = False,
    ) -> List[Change]:
        """List all changes in the project.

        Arguments:
            page_size: Number of items to return.

        Returns:
            A list of changes.
        """
        req = management_pb2.ListChangesRequest(
            parent=self.parent,
            page_size=page_size,
            filters=filters,
            all_projects=all_projects,
        )
        resp = self.client._management.ListChanges(req)
        return [Change.from_proto(x, client=self.client) for x in resp.plans]

    def list_all(self) -> Iterator[Change]:
        """List all changes.

        Pages through all changes using an iterator.

        Returns:
            A iterator of all changes.
        """

        def next_page(next_page_token):
            req = management_pb2.ListChangeRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListChange(req)
            return (
                [Change.from_proto(x, client=self.client) for x in resp.plans],
                resp.next_page_token,
            )

        return Pager(next_page)

    def cancel(self, id: str) -> None:
        """Cancel an change workflow.

        Arugments:
            id: Name or id of change workflow

        """
        req = management_pb2.CancelChangeRequest(name=self.name(id))
        self.client._management.CancelChange(req)


class Change(Resource, types.Change):
    """Change resource."""

    name_pattern: str = "projects/{project}/changes/{change}"
    manager: ChangeManager
    events: EventManager
    """Event manager."""

    def _init(self):
        self.manager = ChangeManager(parent=self.parent, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def cancel(self):
        """Cancel change."""
        self.manager.cancel(self.id)

    def rerun(self):
        """Rerun changes."""
        return self.manager.rerun(self.id)

    def wait(self, echo: bool = True, timeout: int = None) -> Change:
        """Wait for Change operation to complete.

        Arguments:
            echo: Display progress.
            timeout: Timeout in seconds.
        Returns:
            Updated changes.
        """
        # if it has already succeeded, return immediately
        if self.state in ["SUCCEEDED", "CANCELLED", "FAILED"]:
            return self

        return wait(
            getter=lambda: self.manager.get(self.id),
            echo=echo,
            timeout=timeout,
        )
