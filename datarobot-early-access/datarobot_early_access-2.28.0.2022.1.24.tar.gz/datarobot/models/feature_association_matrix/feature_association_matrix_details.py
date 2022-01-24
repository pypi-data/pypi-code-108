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
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2


class FeatureAssociationMatrixDetails(APIObject):
    """
    Plotting details for a pair of passed features present in the feature association matrix.

    .. note::
        Projects created prior to v2.17 are not supported by this feature.

    Attributes
    ----------
    project_id : str
        Id of the project that contains the requested associations.
    chart_type : str
        Which type of plotting the pair of features gets in the UI.
        e.g. 'HORIZONTAL_BOX', 'VERTICAL_BOX', 'SCATTER' or 'CONTINGENCY'
    values : list
        The data triplets for pairwise plotting e.g.
        {"values": [[460.0, 428.5, 0.001], [1679.3, 259.0, 0.001], ...]
        The first entry of each list is a value of feature1, the second entry of each list is a
        value of feature2, and the third is the relative frequency of the pair of datapoints in the
        sample.
    features : list
        A list of the requested features, [feature1, feature2]
    types : list
        The type of `feature1` and `feature2`. Possible values: "CATEGORICAL", "NUMERIC"
    featurelist_id : str
        Id of the feature list to lookup FAM details for.
    """

    _path = "projects/{}/featureAssociationMatrixDetails/"
    _converter = t.Dict(
        {
            t.Key("chart_type"): String(),
            t.Key("values"): t.List(t.Tuple(t.Any(), t.Any(), t.Float())),
            t.Key("features"): t.List(String()),
            t.Key("types"): t.List(String()),
        }
    )

    def __init__(
        self,
        project_id=None,
        chart_type=None,
        values=None,
        features=None,
        types=None,
        featurelist_id=None,
    ):
        self.project_id = project_id
        self.chart_type = chart_type
        self.values = values
        self.features = features
        self.types = types
        self.featurelist_id = featurelist_id

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(project_id={}, chart_type={}, values={}, features={}, types={})".format(
                self.__class__.__name__,
                self.project_id,
                self.chart_type,
                self.values,
                self.features,
                self.types,
            )
        )

    @classmethod
    def get(cls, project_id, feature1, feature2, featurelist_id=None):
        """
        Get a sample of the actual values used to measure the association between a pair of features

        .. versionadded:: v2.17

        Parameters
        ----------
        project_id : str
            Id of the project of interest.
        feature1 : str
            Feature name for the first feature of interest.
        feature2 : str
            Feature name for the second feature of interest.
        featurelist_id : str
            Optional, the feature list to lookup FAM data for. By default, depending on the type of
            the project "Informative Features" or "Timeseries Informative Features" list will be
            used.

        Returns
        --------
        FeatureAssociationMatrixDetails
            The feature association plotting for provided pair of features.
        """
        url = cls._path.format(project_id)
        params = {"feature1": feature1, "feature2": feature2}
        if featurelist_id:
            params["featurelistId"] = featurelist_id
        response = cls._client.get(url, params=params)
        fam_details = cls.from_server_data(response.json())
        fam_details.project_id = project_id
        fam_details.featurelist_id = featurelist_id
        return fam_details

    def to_dict(self):
        return {
            "chart_type": self.chart_type,
            "values": self.values,
            "features": self.features,
            "types": self.types,
        }
