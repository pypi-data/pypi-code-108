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

from datarobot.client import get_client, staticproperty
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.models.api_object import APIObject
from datarobot.utils.waiters import wait_for_async_resolution


class FeatureRestorationStatus(APIObject):
    """Status of the feature restoration process.

    .. versionadded:: v2.27

    Attributes
    ----------
    warnings : list of strings
        Warnings generated for those features which failed to restore
    remaining_restore_limit : int
        The remaining available number of the features which can be restored in this project.
    restored_features : list of strings
        Features which were restored

    """

    _converter = t.Dict(
        {t.Key("warnings"): t.List(t.String), t.Key("features_to_restore"): t.List(t.String)}
    ).ignore_extra("*")

    def __init__(self, warnings, features_to_restore):
        self.warnings = warnings
        self.restored_features = features_to_restore


class DiscardedFeaturesInfo(APIObject):
    """An object containing information about time series features which were reduced
    during time series feature generation process. These features can be restored back to the
    project. They will be included into All Time Series Features and can be used to create new
    feature lists.

    .. versionadded:: v2.27

    Attributes
    ----------
    total_restore_limit : int
      The total limit indicating how many features can be restored in this project.
    remaining_restore_limit : int
      The remaining available number of the features which can be restored in this project.
    features : list of strings
      Discarded features which can be restored.
    count : int
      Discarded features count.

    """

    _client = staticproperty(get_client)
    _get_url = "projects/{}/discardedFeatures/"
    _post_url = "projects/{}/modelingFeatures/fromDiscardedFeatures/"

    _converter = t.Dict(
        {
            t.Key("count"): t.Int(gte=0),
            t.Key("total_restore_limit"): t.Int(gte=0),
            t.Key("remaining_restore_limit"): t.Int(gte=0),
            t.Key("features"): t.List(t.String),
        }
    ).ignore_extra("*")

    def __init__(self, total_restore_limit, remaining_restore_limit, count, features):
        self.total_restore_limit = total_restore_limit
        self.remaining_restore_limit = remaining_restore_limit
        self.count = count
        self.features = features

    @classmethod
    def restore(cls, project_id, features_to_restore, max_wait=DEFAULT_MAX_WAIT):
        """Restore discarded during time series feature generation process features back to the
        project. After restoration features will be included into All Time Series Features.

        .. versionadded:: v2.27

        Parameters
        ----------
        project_id: string
        features_to_restore: list of strings
            List of the feature names to restore
        max_wait: int, optional
            max time to wait for features to be restored.
            Defaults to 10 min

        Returns
        -------
        status: FeatureRestorationStatus
            information about features which were restored and which were not.
        """
        payload = {"features_to_restore": features_to_restore}
        response = cls._client.post(cls._post_url.format(project_id), data=payload)
        wait_for_async_resolution(cls._client, response.headers["Location"], max_wait=max_wait)
        return FeatureRestorationStatus.from_server_data(response.json())

    @classmethod
    def retrieve(cls, project_id):
        """Retrieve the discarded features information for a given project.

        .. versionadded:: v2.27

        Parameters
        ----------
        project_id: string

        Returns
        -------
        info: DiscardedFeaturesInfo
            information about features which were discarded during feature generation process and
            limits how many features can be restored.
        """
        return cls.from_location(cls._get_url.format(project_id))
