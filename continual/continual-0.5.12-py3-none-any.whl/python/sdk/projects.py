from __future__ import annotations
from typing import List, Optional
from google.protobuf import field_mask_pb2
from continual.python.sdk.environments import ProjectEnvironmentManager
from continual.python.utils.utils import (
    generate_datastore_field_paths,
)
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


class OrganizationProjectManager:
    """Manages organization projects."""

    manager: ProjectManager
    parent: str = ""
    client: client.Client

    def __init__(self, parent: str, client: client.Client):
        self.parent = parent
        self.client = client
        self.manager = ProjectManager(parent=self.parent, client=self.client)

    def list(self, page_size: Optional[int] = None) -> List[Project]:
        """List project.

        Arguments:
            page_size: Number of elements.

        Returns:
            A list of organization projects.
        """
        return self.manager.list(page_size)

    def list_all(self) -> Pager[Project]:
        """List all projects.

        Returns:
            An iterator of all organization projects.
        """
        return self.manager.list_all()

    def create(
        self,
        display_name: str,
        data_store: Optional[types.DataStore] = None,
        project_id: Optional[str] = None,
    ) -> Project:
        """Create a new project.

        Creates a new project within organization.  The project ID by
        default is generated from the display name and must be globally
        unique across all organizations.

        Arguments:
            display_name: Display name.
            data_store: Data store configuration.
            project_id: Optional project id.

        Returns:
            A new project
        """
        return self.manager.create(
            display_name=display_name,
            organization=self.parent,
            data_store=data_store,
            project_id=project_id,
        )


class ProjectManager(Manager):
    """Manages project resources."""

    name_pattern: str = "projects/{project}"

    def get(self, id: str) -> Project:
        """Get project.

        Arguments:
            id: Project name or id.

        Returns
            A project.
        """

        project_id = id.split("@")[0]
        req = management_pb2.GetProjectRequest(name=self.name(project_id))
        resp = self.client._management.GetProject(req)
        project = Project.from_proto(resp, client=self.client)
        if "@" in id:
            environment = self.client.environments.get(id.split("@")[1])
            project._set_environment(environment)
        return project

    def list(
        self, page_size: Optional[int] = None, filters: List[str] = None
    ) -> List[Project]:
        """List projects.

        Arguments:
            page_size: Number of items to return.

        Returns:
            A list of projects.
        """
        req = management_pb2.ListProjectsRequest(
            parent=self.parent, page_size=page_size, filters=filters
        )
        resp = self.client._management.ListProjects(req)
        return [Project.from_proto(x, client=self.client) for x in resp.projects]

    def list_all(self) -> Pager[Project]:
        """List all projects.

        Pages through all projects using an iterator.

        Returns:
            A iterator of all projects.
        """

        def next_page(next_page_token):
            req = management_pb2.ListProjectsRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListProjects(req)
            return (
                [Project.from_proto(x, client=self.client) for x in resp.projects],
                resp.next_page_token,
            )

        return Pager(next_page)

    def create(
        self,
        display_name: str,
        organization: str,
        data_store: Optional[types.DataStore] = None,
        project_id: Optional[str] = None,
    ) -> Project:
        """Create an project.

        New projects are identified by a unique project id that is
        generated from the display name.  To set a project id explicitly,
        you can pass `project_id`.  However project ids are globally unique across
        all organizations.

        Arguments:
            display_name: Display name.
            organization: Organization resource name.
            data_store: Data store configuration.
            project_id: User-defined project id.

        Returns:
            A new project.
        """
        req = management_pb2.CreateProjectRequest(
            project=Project(
                display_name=display_name,
                organization=organization,
            ).to_proto()
        )
        if data_store is not None:
            req.project.data_store.type = data_store.type
            if data_store.type == "postgres":
                req.project.data_store.postgres.host = data_store.postgres.host
                req.project.data_store.postgres.port = data_store.postgres.port
                req.project.data_store.postgres.username = data_store.postgres.username
                req.project.data_store.postgres.password = data_store.postgres.password
                req.project.data_store.postgres.database = data_store.postgres.database
            elif data_store.type == "snowflake":
                req.project.data_store.snowflake.host = data_store.snowflake.host
                req.project.data_store.snowflake.port = data_store.snowflake.port
                req.project.data_store.snowflake.username = (
                    data_store.snowflake.username
                )
                req.project.data_store.snowflake.password = (
                    data_store.snowflake.password
                )
                req.project.data_store.snowflake.database = (
                    data_store.snowflake.database
                )
                req.project.data_store.snowflake.warehouse = (
                    data_store.snowflake.warehouse
                )
                req.project.data_store.snowflake.role = data_store.snowflake.role

            elif data_store.type == "bigquery":
                req.project.data_store.big_query.auth_file = (
                    data_store.big_query.auth_file
                )
                req.project.data_store.big_query.auth_file_name = (
                    data_store.big_query.auth_file_name
                )
            elif data_store.type == "redshift":
                req.project.data_store.redshift.host = data_store.redshift.host
                req.project.data_store.redshift.port = data_store.redshift.port
                req.project.data_store.redshift.username = data_store.redshift.username
                req.project.data_store.redshift.password = data_store.redshift.password
                req.project.data_store.redshift.database = data_store.redshift.database
            elif data_store.type == "databricks":
                req.project.data_store.databricks.host = data_store.databricks.host
                req.project.data_store.databricks.port = data_store.databricks.port
                req.project.data_store.databricks.token = data_store.databricks.token
                req.project.data_store.databricks.http_path = (
                    data_store.databricks.http_path
                )
                req.project.data_store.databricks.database = (
                    data_store.databricks.database
                )

        resp = self.client._management.CreateProject(req)
        return Project.from_proto(resp, client=self.client)

    def delete(self, id: str, delete_schema: bool = False) -> None:
        """Delete an project.

        Arguments:
            id: Project name or id.
        """

        req = management_pb2.DeleteProjectRequest(
            name=self.name(id), delete_schema=delete_schema
        )
        self.client._management.DeleteProject(req)

    def update(
        self,
        id: str,
        display_name: Optional[str] = None,
        data_store: Optional[types.DataStore] = None,
    ) -> Project:
        """Update project.

        Arguments:
            display_name:  Display name.
            data_store: Project data store.
        Returns:
            Updated project.
        """
        paths = []
        if display_name is not None:
            paths.append("display_name")
        if data_store is not None:
            paths.extend(generate_datastore_field_paths(data_store))

        req = management_pb2.UpdateProjectRequest(
            update_mask=field_mask_pb2.FieldMask(paths=paths),
            project=Project(
                name=self.name(id), display_name=display_name, data_store=data_store
            ).to_proto(),
        )
        resp = self.client._management.UpdateProject(req)
        return Project.from_proto(resp, client=self.client)


class Project(Resource, types.Project):
    """Project resource."""

    name_pattern: str = "projects/{project}"
    manager: ProjectManager

    feature_sets: FeatureSetManager
    """Feature set manager."""

    models: ModelManager
    """Model manager."""

    changes: ChangeManager
    """Change manager."""

    events: EventManager
    """Event manager."""

    environments: ProjectEnvironmentManager

    def _init(self):
        self.manager = ProjectManager(parent=self.parent, client=self.client)
        self.feature_sets = FeatureSetManager(parent=self.name, client=self.client)
        self.models = ModelManager(parent=self.name, client=self.client)
        self.changes = ChangeManager(parent=self.name, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)
        self.environments = ProjectEnvironmentManager(
            parent=self.name, client=self.client
        )
        self.environment = None

    def _set_environment(self, environment):
        self.environment = environment
        self.feature_sets = FeatureSetManager(
            parent=self.environment.name, client=self.client
        )
        self.models = ModelManager(parent=self.environment.name, client=self.client)
        self.changes = ChangeManager(parent=self.environment.name, client=self.client)
        self.events = EventManager(parent=self.environment.name, client=self.client)

    def delete(self, delete_schema: bool = False) -> None:
        """Delete project."""
        self.manager.delete(self.name, delete_schema=delete_schema)

    def update(
        self,
        display_name: Optional[str] = None,
        data_store: Optional[types.DataStore] = None,
    ) -> Project:
        """Update project.

        Arguments:
            display_name:  Display name.

        Returns:
            Updated project.
        """
        return self.manager.update(
            self.name, display_name=display_name, data_store=data_store
        )

    def _create_csv_signed_url(self, file_name: str) -> str:
        """Get a temporary google signed url.

        Arguments:
            file_name: name of the file to get a signed url for.
        """
        name = self.name
        if self.environment is not None:
            name = self.environment.name

        req = management_pb2.CreateFeatureSetCSVSignedURLRequest(
            parent=name, file_name=file_name
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
                open(file_name, encoding="ISO-8859-1").read().encode("utf-8"),
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

    def get_schema_graph(self) -> str:
        """The a JSON graph of current schema within the project.

        Arguments:
            None
        """

        req = management_pb2.GetSchemaGraphRequest(name=self.name)
        resp = self.client._management.GetSchemaGraph(req)
        return resp.graph_json
