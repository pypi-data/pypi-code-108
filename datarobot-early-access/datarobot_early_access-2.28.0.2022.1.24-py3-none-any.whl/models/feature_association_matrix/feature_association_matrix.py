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

from datarobot._compat import Int, String
from datarobot.enums import FEATURE_ASSOCIATION_METRIC, FEATURE_ASSOCIATION_TYPE
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2


class FeatureAssociationMatrix(APIObject):
    """
    Feature association statistics for a project.

    .. note::
        Projects created prior to v2.17 are not supported by this feature.

    Attributes
    ----------
    project_id : str
        Id of the associated project.
    strengths : list of dict
        Pairwise statistics for the available features as structured below.
    features : list of dict
        Metadata for each feature and where it goes in the matrix.

    Examples
    --------
    .. code-block:: python

        import datarobot as dr

        # retrieve feature association matrix
        feature_association_matrix = dr.FeatureAssociationMatrix.get(project_id)
        feature_association_matrix.strengths
        feature_association_matrix.features

        # retrieve feature association matrix for a metric, association type or a feature list
        feature_association_matrix = dr.FeatureAssociationMatrix.get(
            project_id,
            metric=enums.FEATURE_ASSOCIATION_METRIC.SPEARMAN,
            association_type=enums.FEATURE_ASSOCIATION_TYPE.CORRELATION,
            featurelist_id=featurelist_id,
        )
    """

    _path = "projects/{}/featureAssociationMatrix/"
    _association_strength = t.Dict(
        {
            t.Key("feature1"): String(allow_blank=True),
            t.Key("feature2"): String(allow_blank=True),
            t.Key("statistic"): t.Float(),
        }
    )
    _association_feature = t.Dict(
        {
            t.Key("cluster_sort_index", optional=True): Int(),
            t.Key("cluster_name", optional=True): String(),
            t.Key("cluster_id", optional=True): Int(),
            t.Key("feature"): String(allow_blank=True),
            t.Key("strength_sort_index"): Int(),
            t.Key("alphabetic_sort_index"): Int(),
            t.Key("importance_sort_index"): Int(),
        }
    )
    _converter = t.Dict(
        {
            t.Key("strengths"): t.List(_association_strength),
            t.Key("features"): t.List(_association_feature),
        }
    )
    _query_param_validator = t.Dict(
        {
            t.Key("metric", optional=True): t.Enum(*FEATURE_ASSOCIATION_METRIC.ALL),
            t.Key("type", optional=True): t.Enum(*FEATURE_ASSOCIATION_TYPE.ALL),
            t.Key("featurelistId", optional=True): String() | t.Null(),
        }
    )

    def __init__(self, strengths=None, features=None, project_id=None):
        self.strengths = strengths
        self.features = features
        self.project_id = project_id

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(project_id={}, strengths={}, features={})".format(
                self.__class__.__name__, self.project_id, self.strengths, self.features,
            )
        )

    @classmethod
    def get(cls, project_id, metric=None, association_type=None, featurelist_id=None):
        """
        Get feature association statistics.

        Parameters
        ----------
        project_id : str
            Id of the project that contains the requested associations.
        metric : enums.FEATURE_ASSOCIATION_METRIC
            The name of a metric to get pairwise data for. Since 'v2.19' this is optional and
            defaults to `enums.FEATURE_ASSOCIATION_METRIC.MUTUAL_INFO`.
        association_type : enums.FEATURE_ASSOCIATION_TYPE
            The type of dependence for the data. Since 'v2.19' this is optional and defaults to
            `enums.FEATURE_ASSOCIATION_TYPE.ASSOCIATION`.
        featurelist_id : str or None
            Optional, the feature list to lookup FAM data for. By default, depending on the type of
            the project "Informative Features" or "Timeseries Informative Features" list will be
            used.
            (New in version v2.19)

        Returns
        -------
        FeatureAssociationMatrix
            Feature association pairwise metric strength data, feature clustering data, and
            ordering data for Feature Association Matrix visualization.
        """
        String().check(project_id)
        params = dict()
        if metric:
            params["metric"] = metric
        if association_type:
            params["type"] = association_type
        if featurelist_id:
            params["featurelistId"] = featurelist_id
        cls._query_param_validator.check(params)

        url = cls._path.format(project_id)
        response = cls._client.get(url, params=params)
        feature_association_matrix = cls.from_server_data(response.json())
        # FAM public API doesn't include project_id so lets populate it
        feature_association_matrix.project_id = project_id
        return feature_association_matrix

    def to_dict(self):
        return {"strengths": self.strengths, "features": self.features}
