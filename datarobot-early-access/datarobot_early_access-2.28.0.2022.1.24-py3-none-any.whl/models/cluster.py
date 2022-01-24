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


class Cluster(APIObject):
    """ Representation of a single cluster.

    Attributes
    ----------
    name: str
        Current cluster name
    percent: float
        Percent of data contained in the cluster. This value is reported after cluster insights
        are computed for the model.

    """

    _cluster_names = "projects/{project_id}/models/{model_id}/clusterNames/"

    _converter = t.Dict(
        {t.Key("name"): String(), t.Key("percent", optional=True): t.Float()}
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.percent = kwargs.get("percent")

    def __repr__(self):
        return encode_utf8_if_py2(u"Cluster(name={0.name}, percent={0.percent})").format(self)

    @classmethod
    def list(cls, project_id, model_id):
        """Retrieve a list of clusters in the model.

        Parameters
        ----------
        project_id: str
            ID of the project that the model is part of.
        model_id: str
            ID of the model.

        Returns
        -------
        List of clusters
        """
        path = cls._cluster_names.format(project_id=project_id, model_id=model_id)
        response = cls._client.get(path).json()
        return [cls.from_server_data(item) for item in response["clusters"]]

    @classmethod
    def update_multiple_names(cls, project_id, model_id, cluster_name_mappings):
        """ Update many clusters at once based on list of name mappings.

        Parameters
        ----------
        project_id: str
            ID of the project that the model is part of.
        model_id: str
            ID of the model.
        cluster_name_mappings: List of tuples
            Cluster name mappings, consisting of current and previous names for each cluster.
            Example:

            .. code-block:: python

                cluster_name_mappings = [
                    ("current cluster name 1", "new cluster name 1"),
                    ("current cluster name 2", "new cluster name 2")]

        Returns
        -------
        List of clusters

        Raises
        ------
        datarobot.errors.ClientError
            Server rejected update of cluster names.
        ValueError
            Invalid cluster name mapping provided.
        """
        path = cls._cluster_names.format(project_id=project_id, model_id=model_id)
        mappings = [
            {"currentName": current_name, "newName": new_name}
            for current_name, new_name in cluster_name_mappings
        ]
        payload = {"clusterNameMappings": mappings}
        response = cls._client.patch(path, data=payload).json()
        return [cls.from_server_data(item) for item in response["clusters"]]

    @classmethod
    def update_name(cls, project_id, model_id, current_name, new_name):
        """Change cluster name from current_name to new_name

        Parameters
        ----------
        project_id: str
           ID of the project that the model is part of.
        model_id: str
            ID of the model.
        current_name: str
            Current cluster name
        new_name: str
            New cluster name

        Returns
        -------
        List of Cluster
        """
        return cls.update_multiple_names(
            project_id=project_id,
            model_id=model_id,
            cluster_name_mappings=[(current_name, new_name)],
        )
