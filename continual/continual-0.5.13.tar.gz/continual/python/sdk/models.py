from __future__ import annotations
from typing import List, Optional, Tuple
import pandas as pd
import json
from continual.python.sdk import featuresets
from continual.rpc.management.v1 import management_pb2
from continual.rpc.management.v1 import types
from continual.python.sdk.resource import Resource
from continual.python.sdk.manager import Manager
from continual.python.sdk.iterators import Pager
from continual.python.sdk.model_versions import ModelVersion, ModelVersionManager
from continual.python.sdk.featuresets import FeatureSet
from continual.python.sdk.promotions import PromotionManager
from continual.python.sdk.events import EventManager

from continual.python.common.query import Query

from continual.python.sdk.batchpredictions import (
    BatchPrediction,
    BatchPredictionManager,
)


class ModelManager(Manager):
    """Manages model resources."""

    name_pattern: str = "projects/{project}/models/{model}"

    def get(self, id: str) -> Model:
        """Get model.

        Arguments:
            id: Model name or id.

        Returns
            An experiment.
        """
        req = management_pb2.GetModelRequest(name=self.name(id))
        resp = self.client._management.GetModel(req)
        return Model.from_proto(resp, client=self.client)

    def list(
        self,
        page_size: Optional[int] = None,
        filters: List[str] = None,
        all_projects: bool = False,
    ) -> List[Model]:
        """List model.

        Arguments:
            page_size: Number of items to return.

        Returns:
            A list of models.
        """
        req = management_pb2.ListModelsRequest(
            parent=self.parent,
            page_size=page_size,
            filters=filters,
            all_projects=all_projects,
        )
        resp = self.client._management.ListModels(req)
        return [Model.from_proto(x, client=self.client) for x in resp.models]

    def list_all(self) -> Pager[Model]:
        """List all model.

        Pages through all model using an iterator.

        Returns:
            A iterator of all model.
        """

        def next_page(next_page_token):
            req = management_pb2.ListModelsRequest(
                parent=self.parent, page_token=next_page_token
            )
            resp = self.client._management.ListModels(req)
            return (
                [Model.from_proto(x, client=self.client) for x in resp.models],
                resp.next_page_token,
            )

        return Pager(next_page)

    def train(self, id: str) -> ModelVersion:
        """Train a model.

        Creates a new model version and starts a training run using
        the lastest data available in the feature store.

        Arguments:
            id: Name or id of model.

        Returns:
            A new model version.
        """
        req = management_pb2.TrainModelRequest(name=self.name(id))
        resp = self.client._management.TrainModel(req)
        return ModelVersion.from_proto(resp, client=self.client)

    def delete(self, id: str):
        """Delete a model.

        Deletes the model from system.

        Arguments:
            id: Name or id of model.

        Returns:
            None
        """
        req = management_pb2.DeleteModelRequest(name=self.name(id))
        self.client._management.DeleteModel(req)
        return

    def get_related_feature_sets(self, project: str, entity: str) -> List[FeatureSet]:
        """Get get all feature sets from same entity as a feature set.

        Arugments:
            id: Name or id of feature set.
        Returns:
            A list of feature sets.
        """
        req = management_pb2.GetEntityFeatureSetsRequest(
            project_name=project, entity_id=entity
        )
        resp = self.client._management.GetEntityFeatureSets(req)
        return [FeatureSet.from_proto(x, client=self.client) for x in resp.feature_sets]

    def _get_featureset_map(self):
        return None

    def get_training_data(
        self,
        model,
        n: Optional[int] = None,
        normalized: bool = False,
        metadata: bool = False,
        latest: bool = False,
        all: bool = False,
    ) -> Tuple[pd.DataFrame, Query]:
        """Get training data for a model.

        Arguments:
            id: Name or id of model.
            n: Number of records.
            normalize: Only return normalized data.
            metadata: Include metadata.
            latest: Only return latest data for each entity.
        Returns:
            Training DataFrame and serving query tuple.
        """
        proj = self.client.projects.get(self.parent)
        all_fs = proj.feature_sets.list_all()
        featureset_map = {}
        for f in all_fs:
            featureset_map[f.name] = f.to_proto()

        query = Query.form_query(
            model=model.to_proto(),
            metadata=metadata,
            all_featuresets=featureset_map,
        )

        if n == 0:
            return pd.DataFrame(), query

        # TODO: add paging and more options around stard/end times

        req = management_pb2.GetTrainingDataRequest(
            query=query.to_proto(),
        )

        resp = self.client._management.GetTrainingData(req)

        e_dict = []
        if resp.value is not None:
            for k in resp.value:
                feature_dict = json.loads(k)
                # Reconcile response to fill missing columns
                self._serving_data_reconcile(query, feature_dict)
                e_dict.append(feature_dict)

        return (pd.DataFrame(e_dict), query)

    def get_serving_data(
        self,
        query: Query,
        overrides: Optional[dict] = None,
    ) -> dict:
        """Get online serving data.

        Arguments:
            query: Serving data query.
            id: Entity id.
            overrides: Local data overrides.

        Returns:
            A dictionary of online features.
        """
        q = query.clone()

        # TODO: this should pass in typed overrides.
        # when we have a grpc predict call we can do this more easily
        overide_str = None
        if overrides is not None:
            overide_str = json.dumps(overrides)
        req = management_pb2.GetServingDataRequest(
            query=q.to_proto(), overrides=overide_str
        )

        serving_data = self.client._management.GetServingData(req)
        # TODO: factor out from training/serving code.
        e_dict = []
        if serving_data.value is not None:
            for k in serving_data.value:
                feature_dict = json.loads(k)
                # Reconcile response to fill missing columns
                self._serving_data_reconcile(q, feature_dict)
                e_dict.append(feature_dict)
        return e_dict

    def _serving_data_reconcile(self, query, e_dict):
        for field in query.fields:
            if field.qualified_name not in e_dict:
                e_dict[field.qualified_name] = None

            if field.relation is not None:
                self._serving_data_reconcile(field.relation, e_dict)

        if query.related is None:
            return

        for rel in query.related:
            self._serving_data_reconcile(rel, e_dict)

        return

    def batch_predict(
        self,
        model_id: str,
        source_type: str,
        source: str,
        dest_type: str,
        incremental: bool = False,
        prediction_model: str = None,
    ) -> BatchPrediction:
        """Deploy model version.

        Arguments:
            model_id: Name or id of model.
            source_type:
            source:
            dest_type:
        Returns:
            A batch prediction job object to track batch prediction status.
        """
        model_name = self.name(model_id)
        req = management_pb2.CreateBatchPredictionRequest(
            model=model_name,
            source_type=source_type,
            source=source,
            dest_type=dest_type,
            incremental=incremental,
            prediction_model=prediction_model,
        )
        resp = self.client._management.BatchPredict(req)
        return BatchPrediction.from_proto(resp, client=self.client)

    def get_data(
        self, model: Model, page_size: int = None, page_token: str = None
    ) -> Tuple[pd.DataFrame, str]:
        """Get data for the featureset

        Arguments:
            page_size: number of rows to fetch.
            page_token: starting token for the next page of data.

        Returns:
            A dictionary of features.
        """
        req = management_pb2.GetDataRequest(
            name=model.name,
            page_size=page_size,
            page_token=page_token,
        )

        resp = self.client._management.GetData(req)
        # print("resp: {}".format(resp))
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
        right_model: str,
        left_yaml: str,
        left_project: str,
        left_environment: str,
        left_model: str,
    ):
        """Get data for the featureset

        Arguments:
            right_yaml
            right_model
            right_feature_set
            left_yaml
            left_project
            left_model

        Returns:
            Diff Report
        """
        return featuresets.diff(
            right_yaml,
            right_project,
            right_environment,
            right_model,
            left_yaml,
            left_project,
            left_environment,
            left_model,
            models=True,
        )

    def get_signature(self, id):
        req = management_pb2.GetModelQueryRequest(name=self.name(id))
        resp = self.client._management.GetModelQuery(req)
        return resp.query_json


class Model(Resource, types.Model):
    """Model resource."""

    name_pattern: str = "projects/{project}/models/{model}"
    manager: ModelManager

    model_versions: ModelVersionManager
    """Model version manager."""

    promotions: PromotionManager
    """Promotion manager."""

    batch_prediction_jobs: BatchPredictionManager
    """Batch Prediction  manager."""

    events: EventManager
    """Event manager."""

    def _init(self):
        self.manager = ModelManager(parent=self.parent, client=self.client)
        self.model_versions = ModelVersionManager(parent=self.name, client=self.client)
        self.promotions = PromotionManager(parent=self.name, client=self.client)
        self.batch_prediction_jobs = BatchPredictionManager(
            parent=self.name, client=self.client
        )
        self.events = EventManager(client=self.client, parent=self.name)

    def get_training_data(
        self,
        n: Optional[int] = None,
        normalized: bool = False,
        metadata: bool = False,
        latest: bool = False,
        all: bool = False,
    ) -> Tuple[pd.DataFrame, Query]:
        """Get training data for model.

        Arguments:
            n: Number of records.
            normalized: Return only base data.
            metadata: Include metadata.
        Returns:
            A training data set.
        """
        return self.manager.get_training_data(
            self,
            n=n,
            normalized=normalized,
            metadata=metadata,
            latest=latest,
            all=all,
        )

    def get_serving_data(self, query: Query, overrides: Optional[dict] = None):
        """Get online serving data.

        Arguments:
            query: Serving query token.
            overrides: Local data overrides
        Returns:
            DataFrame of live data.
        """
        return self.manager.get_serving_data(query, overrides)

    def train(self) -> ModelVersion:
        """Wait for experiment to complete."""
        return self.manager.train(self.id)

    def delete(self):
        """Wait for experiment to complete."""
        return self.manager.delete(self.id)

    def batch_predict(
        self,
        source_type: str = "STORE",
        source: str = "",
        dest_type: str = "STORE",
        incremental: bool = False,
        prediction_model: str = None,
    ) -> BatchPrediction:
        """Start batch prediction

        Arguments:
            source_type:
            source: uri of file with records to be batch predicted
            dest_type: proto enum for destination type type
            dest_type:

        Returns:
            A batch prediction job object to track batch prediction status.
        """
        return self.manager.batch_predict(
            self.id,
            source_type,
            source,
            dest_type,
            incremental=incremental,
            prediction_model=prediction_model,
        )

    @property
    def feature_set(self) -> FeatureSet:
        """Expanded feature set for model."""
        return self.client.feature_sets.get(super().feature_set)

    @feature_set.setter
    def feature_set(self, value: FeatureSet) -> None:
        types.Model.feature_set.fset(self, value)

    def get_data(self, page_size=None, page_token=None):
        return self.manager.get_data(self, page_size, page_token)

    def get_signature(self):
        return self.manager.get_signature(self.id)
