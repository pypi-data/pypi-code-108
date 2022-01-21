from __future__ import annotations
from typing import List, Optional, Tuple
from git import Repo

import pandas as pd
import json

from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from continual.python.sdk.ingestions import Ingestion, IngestionManager
from continual.python.sdk.events import EventManager


class FeatureSetManager(Manager):
    """Manages feature set resources."""

    name_pattern: str = "projects/{project}/featureSets/{feature_set}"

    def get(self, id: str, parent: Optional[str] = None) -> FeatureSet:
        """Get feature set.

        Use @version in id to get a specific feature set id.

        Arguments:
            id: Feature set name or id.

        Returns
            A feature set.
        """
        req = management_pb2.GetFeatureSetRequest(name=self.name(id, parent=parent))
        resp = self.client._management.GetFeatureSet(req)
        return FeatureSet.from_proto(resp, client=self.client)

    def list(
        self,
        page_size: Optional[int] = None,
        filters: List[str] = None,
        all_projects=False,
    ) -> List[FeatureSet]:
        """List feature sets.

        Arguments:
            page_size: Number of items to return.

        Returns:
            A list of feature sets.
        """
        req = management_pb2.ListFeatureSetsRequest(
            parent=self.parent,
            page_size=page_size,
            filters=filters,
            all_projects=all_projects,
        )
        resp = self.client._management.ListFeatureSets(req)
        return [FeatureSet.from_proto(x, client=self.client) for x in resp.feature_sets]

    def list_all(self) -> Pager[FeatureSet]:
        """List all feature sets.

        Pages through all feature sets using an iterator.

        Returns:
            A iterator of all feature sets.
        """

        def next_page(next_page_token):
            req = management_pb2.ListFeatureSetsRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListFeatureSets(req)
            return (
                [
                    FeatureSet.from_proto(x, client=self.client)
                    for x in resp.feature_sets
                ],
                resp.next_page_token,
            )

        return Pager(next_page)

    def delete(self, id: str) -> None:
        """Delete an feature set.

        Arguments:
            id: Feature set name or id.
        """

        req = management_pb2.DeleteFeatureSetRequest(name=self.name(id))
        self.client._management.DeleteFeatureSet(req)

    def get_data(
        self, feature_set: FeatureSet, page_size: int = None, page_token: str = None
    ) -> Tuple[pd.DataFrame, str]:
        """Get data for the featureset

        Arguments:
            page_size: number of rows to fetch.
            page_token: starting token for the next page of data.

        Returns:
            A dictionary of features.
        """
        req = management_pb2.GetDataRequest(
            name=feature_set.name,
            page_size=page_size,
            page_token=page_token,
        )

        resp = self.client._management.GetData(req)
        df = None
        rows = []
        if resp.value is not None:
            for k in resp.value:
                feature_dict = json.loads(k)
                rows.append(feature_dict)

        if len(rows) > 0:
            df = pd.DataFrame(rows)

        return df, resp.next_page_token

    def diff(
        self,
        right_yaml: str,
        right_project: str,
        right_environment: str,
        right_resource: str,
        left_yaml: str,
        left_project: str,
        left_environment: str,
        left_resource: str,
        models: bool = False,
    ):
        """Get data for the featureset

        Arguments:
            right_yaml
            right_project
            right_environment
            right_feature_set
            left_yaml
            left_project
            left_environment
            left_featureset

        Returns:
            Diff Report
        """
        right = None
        left = None
        default_project = self.client.config.project.split("/")[-1]
        default_environment = self.client.config.environment
        if default_environment is None:
            repo = Repo(search_parent_directories=True)
            default_environment = repo.active_branch.name
            if default_environment is None:
                default_environment = "prod"

        if right_yaml is None:
            right = right_resource
            if right_project is None:
                right_project = default_project
            if right_environment is None:
                right_environment = default_environment
            right = "%s in project %s, environment %s" % (
                right,
                right_project,
                right_environment,
            )
            env = self.client.projects.get(right_project).environments.get(
                right_environment
            )
            if models:
                right_text = env.models.get(right_resource).schema_text
            else:
                right_text = env.feature_sets.get(right_resource).schema_text
        else:
            right = right_yaml
            with open(right_yaml, "r") as f:
                right_text = f.read()
        if left_yaml is None:
            left = left_resource
            if left_project is None:
                left_project = default_project
            if left_environment is None:
                left_environment = default_environment
            left = "%s in project %s, environment %s" % (
                left,
                left_project,
                left_environment,
            )
            env = self.client.projects.get(left_project).environments.get(
                left_environment
            )
            if models:
                left_text = env.models.get(left_resource).schema_text
            else:
                left_text = env.feature_sets.get(left_resource).schema_text
        else:
            left = left_yaml
            with open(left_yaml, "r") as f:
                left_text = f.read()

        req = management_pb2.YamlDiffRequest(
            right=right,
            left=left,
            right_text=right_text,
            left_text=left_text,
            parent=self.parent,
        )

        resp = self.client._management.GetYamlDiff(req)

        return (right, left, resp.text)


class FeatureSet(Resource, types.FeatureSet):
    """Feature set resource."""

    name_pattern: str = "projects/{project}/featureSets/{feature_set}"
    manager: FeatureSetManager

    ingestions: IngestionManager
    """Ingestion manager."""

    events: EventManager
    """Event manager."""

    def _init(self):
        self.manager = FeatureSetManager(parent=self.parent, client=self.client)
        self.ingestions = IngestionManager(parent=self.name, client=self.client)
        self.events = EventManager(parent=self.name, client=self.client)

    def delete(self) -> None:
        """Delete feature set."""
        self.manager.delete(self.name)

    def ingest(self) -> Ingestion:
        """Ingest feature set"""
        return self.manager.ingest(self.name)

    def list_versions(self, page_size: Optional[int] = None) -> List[FeatureSet]:
        """List feature set versions

        Arguments:
            page_size: number of elements

        Returns:
            List of feature set versions.
        """
        return self.manager.list_versions(id=self.name, page_size=page_size)

    def list_all_versions(self) -> Pager[FeatureSet]:
        """List all feature set versions

        Returns:
            An interator of feature set versions.
        """
        return self.manager.list_all_versions(id=self.name)

    # def training_data(self, model: str):
    #    return self.manager.training_data(self, self.id, model)

    def get_data(self, page_size=None, page_token=None):
        return self.manager.get_data(self, page_size, page_token)


# TODO: Add these methods back once data access is more clear.
# @authenticated
# @normalize_exceptions
# def get_all_entities(
#     self, name=None, visible_time=None, system_time=None, normalized=False,
# ):
#     """Fetches all entities for the given entity name from featurestore.

#     The version of entities returned is based on the visible_time and system_time.

#     If visible_time and system_time are not provided then latest instances of all
#      entities are returned

#     Args:
#         name: name of the entity to fetch.
#         visibile_time: default - now. Event time of of the entity. This allows for
#          going back to previous versions of entity.
#                For eg. if visible time is a date 3 months back from today, then
#                the data fetched will be of entity state known as of that date.
#         system_time: default - now. System time limits the entity's version to the
#          state of entity in continual at that time.
#         normalized: default - False. If set, then the data from related entities
#          are not returned.

#     Returns:
#         dataframe
#         A dataframe containing all entites in featurestore that match the given
#          time constraint.

#     Raises:

#     """

#     # Folling should be either configurable or server default.
#     page_size = 5000

#     entities = []
#     done = False
#     next_token = None
#     while not done:
#         req = featurestore_pb2.GetBatchRequest(
#             name=name,
#             project=self.name,
#             page_size=page_size,
#             page_token=next_token,
#             system_time_ms=system_time,
#             visible_time_ms=visible_time,
#             normalized=normalized,
#         )
#         batch_data = self._client._featurestore.GetBatch(req)
#         for val in batch_data.value:
#             e_dict = {}
#             for k in val.features:
#                 e_dict[k] = getattr(
#                     val.features[k], val.features[k].WhichOneof("kind")
#                 )
#             entities.append(e_dict)
#             next_token = batch_data.next_page_token
#             if next_token == "":
#                 done = True

#     df = pd.DataFrame.from_dict(entities)
#     return df

# @authenticated
# @normalize_exceptions
# def delete_entities(self, entity=None, name=None):
#     if entity is not None:
#         name = self.name + "/featureSets/" + entity
#     req = featurestore_pb2.DeleteEntitiesRequest(name=name)
#     self._client._featurestore.DeleteEntities(req)
#     return True
