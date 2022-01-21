from __future__ import annotations
from typing import List, Optional
from google.protobuf import field_mask_pb2
from continual.python.utils import utils
from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk import client
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from continual.python.sdk.featuresets import FeatureSetManager
from continual.python.sdk.models import ModelManager
from continual.python.sdk.changes import ChangeManager
from continual.python.sdk.events import EventManager
import requests


class ProjectEnvironmentManager:
    """Manages projects environments."""

    manager: EnvironmentManager
    parent: str = ""
    client: client.Client

    def __init__(self, parent: str, client: client.Client):
        self.parent = parent
        self.client = client
        self.manager = EnvironmentManager(parent=self.parent, client=self.client)

    def get(self, id: str) -> Environment:
        """Get an environment.

        Arguments:
            id: The environment ID.

        Returns:
            The environment with the provided ID.
        """
        return self.manager.get(id)

    def list(self, page_size: Optional[int] = None) -> List[Environment]:
        """List environments.

        Arguments:
            page_size: Number of elements.

        Returns:
            A list of project environments.
        """
        return self.manager.list(page_size)

    def list_all(self) -> Pager[Environment]:
        """List all environments.

        Returns:
            An iterator of all enviroments.
        """
        return self.manager.list_all()

    def create(
        self,
        id: str,
        data_store: Optional[types.DataStore] = None,
        source: str = "",
    ) -> Environment:
        """Create a new Environment.

        Creates a new environment within project.  The environment ID must
        be unique within the project.

        Arguments:
            id: Environment ID.
            data_store: Data store configuration.
        Returns:
            A new Environment
        """
        return self.manager.create(
            id=id,
            source=source,
            data_store=data_store,
        )


class EnvironmentManager(Manager):
    """Manages environment resources."""

    name_pattern: str = "projects/{project}"

    def __init__(self, client: client.Client, parent: str = "") -> None:
        self.client = client
        if "@" in parent:
            self.parent = parent.split("@")[0]
        else:
            self.parent = parent

    def name(self, id: str, parent: Optional[str] = None):
        if "/" in id:
            # Don't allow names to override manager parent config since this is confusing
            # and is typically a bug in the user code.
            if parent is not None and parent != "" and not id.startswith(parent):
                raise ValueError(f"Resource {id} not a child of {parent}.")
            return id

        name_str = self.parent or ""
        name_str += "@" + id
        return name_str

    def get(self, id: str) -> Environment:
        """Get environment.

        Arguments:
            id: environment name or id.

        Returns
            A environment.
        """
        req = management_pb2.GetEnvironmentRequest(name=self.name(id))
        resp = self.client._management.GetEnvironment(req)
        return Environment.from_proto(resp, client=self.client)

    def list(
        self, page_size: Optional[int] = None, filters: List[str] = None
    ) -> List[Environment]:
        """List environments.

        Arguments:
            page_size: Number of items to return.

        Returns:
            A list of environments.
        """
        req = management_pb2.ListEnvironmentsRequest(
            parent=self.parent, page_size=page_size, filters=filters
        )
        resp = self.client._management.ListEnvironments(req)
        return [
            Environment.from_proto(x, client=self.client) for x in resp.environments
        ]

    def list_all(self) -> Pager[Environment]:
        """List all environments.

        Pages through all environments using an iterator.

        Returns:
            A iterator of all environments.
        """

        def next_page(next_page_token):
            req = management_pb2.ListEnvironmentsRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListEnvironments(req)
            return (
                [
                    Environment.from_proto(x, client=self.client)
                    for x in resp.environments
                ],
                resp.next_page_token,
            )

        return Pager(next_page)

    def create(
        self,
        id: str,
        source: str = "",
        data_store: Optional[types.DataStore] = None,
    ) -> Environment:
        """Create an environment.

        New environments are identified by a unique ID within
        their parent project.

        Arguments:
            id: Environment ID.
            data_store: Data store configuration.

        Returns:
            A new environment.
        """
        req = management_pb2.CreateEnvironmentRequest(
            parent=self.parent,
            environment_id=id,
            source=source,
            data_store=data_store,
        )
        resp = self.client._management.CreateEnvironment(req)
        return Environment.from_proto(resp, client=self.client)

    def delete(self, id: str, delete_schema: bool = False) -> None:
        """Delete an Environment.

        Arguments:
            id: Environment name or id.
        """

        req = management_pb2.DeleteEnvironmentRequest(
            name=self.name(id), delete_schema=delete_schema
        )
        self.client._management.DeleteEnvironment(req)

    def update(
        self,
        id: str,
        scheduling_enabled: Optional[bool] = None,
        data_store: Optional[types.DataStore] = None,
    ) -> Environment:
        """Update Environment.

        Arguments:
            id: Environment ID.
            scheduling_enabled: Whether to enabled scheduled jobs in the Environment.
            data_store: Environment's data store.
        Returns:
            Updated Environment.
        """
        paths = []

        env = Environment(
            name=self.name(id),
        )

        if data_store is not None:
            env.data_store = data_store
            paths.extend(utils.generate_datastore_field_paths(data_store))

        if scheduling_enabled is not None:
            env.scheduling_enabled = scheduling_enabled
            paths.append("scheduling_enabled")

        req = management_pb2.UpdateEnvironmentRequest(
            update_mask=field_mask_pb2.FieldMask(paths=paths),
            environment=env.to_proto(),
        )
        resp = self.client._management.UpdateEnvironment(req)
        return Environment.from_proto(resp, client=self.client)


class Environment(Resource, types.Environment):
    """Environment resource."""

    name_pattern: str = "projects/{project}"
    manager: EnvironmentManager

    feature_sets: FeatureSetManager
    """Feature set manager."""

    models: ModelManager
    """Model manager."""

    changes: ChangeManager
    """Change manager."""

    events: EventManager
    """Event manager."""

    def _init(self):
        self.manager = EnvironmentManager(parent=self.parent, client=self.client)
        self.feature_sets = FeatureSetManager(parent=self.name, client=self.client)
        self.models = ModelManager(parent=self.name, client=self.client)
        self.changes = ChangeManager(parent=self.name, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def delete(self, delete_schema: bool = False) -> None:
        """Delete environment."""
        self.manager.delete(self.name, delete_schema=delete_schema)

    def update(
        self,
        scheduling_enabled: Optional[bool] = None,
        data_store: Optional[types.DataStore] = None,
    ) -> Environment:
        """Update environment.

        Arguments:
            scheduling_enabled:  Enable scheduled jobs within the Environment.

        Returns:
            Updated environment.
        """
        return self.manager.update(
            self.name, scheduling_enabled=scheduling_enabled, data_store=data_store
        )

    def _create_csv_signed_url(self, file_name: str) -> str:
        """Get a temporary google signed url.

        Arguments:
            file_name: name of the file to get a signed url for.
        """
        req = management_pb2.CreateFeatureSetCSVSignedURLRequest(
            parent=self.name, file_name=file_name
        )
        resp = self.client._management.CreateFeatureSetCSVSignedURL(req)
        return resp.signed_url, resp.bucket_path

    def upload_csv_file(self, file_name: str) -> str:
        """upload a csv file to a continual bucket.

        Arguments:
            file_name: name of the file to upload.
        """
        signed_url, bucket_path = self._create_csv_signed_url(file_name)
        TYPE = "text/csv"
        # TODO: chunk up the file if needed
        resp = requests.put(
            signed_url,
            open(file_name).read().encode("utf-8"),
            headers={"Content-Type": TYPE},
        )
        if resp.text != "":
            raise Exception("could not upload file {}: {}".format(file_name, resp.text))

        return bucket_path

    def seed(self, file_name: str, table_name: str = None) -> str:
        """upload a csv file to a continual bucket.

        Arguments:
            file_name: name of the file to upload.
        """
        if not file_name.startswith("gs://"):
            signed_url, bucket_path = self._create_csv_signed_url(file_name)
            TYPE = "text/csv"
            # TODO: chunk up the file if needed
            resp = requests.put(
                signed_url,
                open(file_name).read().encode("utf-8"),
                headers={"Content-Type": TYPE},
            )
            if resp.text != "":
                raise Exception(
                    "could not upload file {}: {}".format(file_name, resp.text)
                )
        else:
            bucket_path = file_name

        req = management_pb2.SeedRequest(
            project=self.name, file_path=bucket_path, table_name=table_name
        )
        resp = self.client._management.Seed(req)
        return resp.schema_name, resp.table_name

    """
    def get_schema_graph(self) -> str:
        "" "The a JSON graph of current schema within the project.

        Arguments:
            None
        " ""

        req = management_pb2.GetSchemaGraphRequest(name=self.name)
        resp = self.client._management.GetSchemaGraph(req)
        return resp.graph_json
    """
