#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import trafaret as t

from datarobot._compat import String
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2, pagination
from datarobot.utils.waiters import wait_for_async_resolution

# Numeric features.

numeric_insight = t.Dict({t.Key("statistic"): t.Float(), t.Key("cluster_name"): String()})

numeric_insight_per_cluster = t.Dict(
    {
        t.Key("all_data"): t.Float(),
        t.Key("per_cluster"): t.List(numeric_insight),
        t.Key("insight_name"): String(),
    }
)

# Categorical features.

categorical_per_value_statistic = t.Dict(
    {t.Key("category_level"): String(), t.Key("frequency"): t.Float()}
)

categorical_per_value_statistic_list = t.Dict(
    {
        t.Key("all_other"): t.Float(),
        t.Key("missing_rows_percent"): t.Float(),
        t.Key("per_value_statistics"): t.List(categorical_per_value_statistic),
        t.Key("cluster_name"): String(),
    }
)

categorical_insight_per_cluster = t.Dict(
    {
        t.Key("all_data"): t.Dict(
            {
                t.Key("all_other"): t.Float(),
                t.Key("missing_rows_percent"): t.Float(),
                t.Key("per_value_statistics"): t.List(categorical_per_value_statistic),
            }
        ),
        t.Key("per_cluster"): t.List(categorical_per_value_statistic_list),
        t.Key("insight_name"): String(),
    }
)

# Text feature.

text_per_ngram_statistic = t.Dict(
    {
        t.Key("ngram"): String(),
        t.Key("importance"): t.Float(),
        t.Key("contextual_extracts"): t.List(String()),
    }
)

text_per_ngram_statistic_list = t.Dict(
    {
        t.Key("missing_rows_percent"): t.Or(t.Float(), t.Null),
        t.Key("per_value_statistics"): t.List(text_per_ngram_statistic),
        t.Key("cluster_name"): String(),
    }
)

text_important_ngram_insight_per_cluster = t.Dict(
    {
        t.Key("all_data"): t.Dict(
            {
                t.Key("missing_rows_percent"): t.Or(t.Float(), t.Null),
                t.Key("per_value_statistics"): t.List(text_per_ngram_statistic),
            }
        ),
        t.Key("per_cluster"): t.List(text_per_ngram_statistic_list),
        t.Key("insight_name"): String(),
    }
)

# Image feature.

image_insight_statistic = t.Dict(
    {
        t.Key("images"): t.List(String()),
        t.Key("percentage_of_missing_images"): t.Float(),
        t.Key("cluster_name"): String(),
    }
)

image_insight_per_cluster = t.Dict(
    {
        t.Key("all_data"): t.Dict(
            {
                t.Key("image_entities"): t.List(String()),
                t.Key("percentage_of_missing_images"): t.Float(),
            }
        ),
        t.Key("per_cluster"): t.List(image_insight_statistic),
        t.Key("insight_name"): String(),
    }
)

# Geospatial feature.

geospatial_insight_values = t.Dict(
    {t.Key("representative_locations"): t.List(t.List(t.Float())), t.Key("cluster_name"): String()}
)

geospatial_insight_per_cluster = t.Dict(
    {t.Key("per_cluster"): t.List(geospatial_insight_values), t.Key("insight_name"): String()}
)


class ClusterInsight(APIObject):
    """Holds data on all insights related to feature as well as breakdown per cluster.

    Parameters
    ----------
    feature_name: str
        Name of a feature from the dataset.
    feature_type: str
        Type of feature.
    insights : List of classes (ClusterInsight)
        List provides information regarding the importance of a specific feature in relation
        to each cluster. Results help understand how the model is grouping data and what each
        cluster represents.
    feature_impact: float
        Impact of a feature ranging from 0 to 1.
    """

    _compute_path = "projects/{project_id}/models/{model_id}/clusterInsights/"
    _retrieve_path = "projects/{project_id}/models/{model_id}/clusterInsights/"
    _converter = t.Dict(
        {
            t.Key("feature_name"): String(),
            t.Key("feature_type"): String(),
            t.Key("feature_impact"): t.Float(),
            t.Key("insights"): t.List(
                t.Or(
                    numeric_insight_per_cluster,
                    categorical_insight_per_cluster,
                    text_important_ngram_insight_per_cluster,
                    image_insight_per_cluster,
                    geospatial_insight_per_cluster,
                )
            ),
        }
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self.feature_name = kwargs.get("feature_name")
        self.feature_type = kwargs.get("feature_type")
        self.insights = kwargs.get("insights")
        self.feature_impact = kwargs.get("feature_impact")

    def __repr__(self):
        return encode_utf8_if_py2(
            u"ClusterInsight("
            u"feature_name={0.feature_name}, "
            u"feature_type={0.feature_type}, "
            u"feature_impact={0.feature_impact})"
        ).format(self)

    @classmethod
    def list(cls, project_id, model_id):
        path = cls._retrieve_path.format(project_id=project_id, model_id=model_id)
        return [cls.from_server_data(x) for x in pagination.unpaginate(path, {}, cls._client)]

    @classmethod
    def compute(cls, project_id, model_id, max_wait=DEFAULT_MAX_WAIT):
        """Starts creation of cluster insights for the model and if successful, returns computed
        ClusterInsights. This method allows calculation to continue for a specified time and
        if not complete, cancels the request.

        Parameters
        ----------
        project_id: str
            ID of the project to begin creation of cluster insights for.
        model_id: str
                        ID of the project model to begin creation of cluster insights for.
        max_wait: int
            Maximum number of seconds to wait canceling the request.

        Returns
        -------
        ClusterInsights

        Raises
        ------
        ClientError
            Server rejected creation due to client error.
            Most likely cause is bad ``project_id`` or ``model_id``.
        AsyncFailureError
            Indicates whether any of the responses from the server are unexpected.
        AsyncProcessUnsuccessfulError
            Indicates whether the cluster insights computation failed or was cancelled.
        AsyncTimeoutError
            Indicates whether the cluster insights computation did not resolve within the specified
            time limit (max_wait).
        """
        compute_path = cls._compute_path.format(project_id=project_id, model_id=model_id)
        response = cls._client.post(compute_path)
        wait_for_async_resolution(cls._client, response.headers["Location"], max_wait=max_wait)
        return cls.list(project_id, model_id)
