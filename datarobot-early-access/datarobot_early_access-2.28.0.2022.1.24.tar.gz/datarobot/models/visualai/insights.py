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

from ..api_object import APIObject
from .images import Image

__all__ = ["ImageEmbedding", "ImageActivationMap"]


class ImageEmbedding(APIObject):
    """Vector representation of an image in an embedding space.

    A vector in an embedding space will allow linear computations to
    be carried out between images: for example computing the Euclidean
    distance of the images.

    Attributes
    ----------
    image: Image
        Image object used to create this map.
    feature_name: str
        Name of the feature column this embedding is associated with.
    position_x: int
        X coordinate of the image in the embedding space.
    position_y: int
        Y coordinate of the image in the embedding space.
    actual_target_value: object
        Actual target value of the dataset row.
    """

    _compute_path = "projects/{project_id}/models/{model_id}/imageEmbeddings/"
    _models_path = "projects/{project_id}/imageEmbeddings/"
    _list_path = "projects/{project_id}/models/{model_id}/imageEmbeddings/"
    _converter = t.Dict(
        {
            t.Key("image_id", optional=True): String(),
            t.Key("position_x", optional=True): t.Float(),
            t.Key("position_y", optional=True): t.Float(),
            t.Key("actual_target_value", optional=True): t.Any(),
            t.Key("target_values", optional=True): t.Or(t.List(String()), t.Null),
            t.Key("target_bins", optional=True): t.Or(t.List(t.Any()), t.Null),
        }
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self.project_id = kwargs.get("project_id")
        self.model_id = kwargs.get("model_id")
        self.image = Image(**kwargs)
        self.feature_name = kwargs.get("feature_name")
        self.position_x = kwargs.get("position_x")
        self.position_y = kwargs.get("position_y")
        self.actual_target_value = kwargs.get("actual_target_value")

    def __repr__(self):
        return (
            "datarobot.models.visualai.ImageEmbedding("
            "project_id={0.project_id}, "
            "model_id={0.model_id}, "
            "feature_name={0.feature_name}, "
            "position_x={0.position_x}, "
            "position_y={0.position_y}, "
            "image_id={0.image.id})"
        ).format(self)

    @classmethod
    def compute(cls, project_id, model_id):
        """Start creation of image embeddings for the model.

        Parameters
        ----------
        project_id: str
            Project to start creation in.
        model_id: str
            Project's model to start creation in.

        Returns
        -------
        str
            URL to check for image embeddings progress.

        Raises
        ------
        datarobot.errors.ClientError
            Server rejected creation due to client error. Most likely
            cause is bad ``project_id`` or ``model_id``.
        """
        path = cls._compute_path.format(project_id=project_id, model_id=model_id)
        r_data = cls._client.post(path).json()
        return r_data["url"]

    @classmethod
    def models(cls, project_id):
        """List the models in a project.

        Parameters
        ----------
        project_id: str
            Project that contains the models.

        Returns
        -------
        list( tuple(model_id, feature_name) )
             List of model and feature name pairs.
        """
        path = cls._models_path.format(project_id=project_id)
        r_data = cls._client.get(path).json()
        return [(d["modelId"], d["featureName"]) for d in r_data.get("data", [])]

    @classmethod
    def list(cls, project_id, model_id, feature_name):
        """Return a list of ImageEmbedding objects.

        Parameters
        ----------
        project_id: str
            Project that contains the images.
        model_id: str
            Model that contains the images.
        feature_name: str
            Name of feature column that contains images.
        """
        path = cls._list_path.format(project_id=project_id, model_id=model_id)
        list_params = {}
        list_params["featureName"] = feature_name
        r_data = cls._client.get(path, params=list_params).json()
        ret = []
        for embed_data in r_data.get("embeddings", []):
            embed = cls.from_server_data(embed_data)
            embed.project_id = project_id
            embed.model_id = model_id
            embed.feature_name = feature_name
            embed.image.project_id = project_id
            ret.append(embed)
        return ret


class ImageActivationMap(APIObject):
    """Mark areas of image with weight of impact on training.

    This is a technique to display how various areas of the region were
    used in training, and their effect on predictions. Larger values in
    ``activation_values`` indicates a larger impact.

    Attributes
    ----------
    image: Image
        Image object used to create this map.
    overlay_image: Image
        Image object composited with activation heat map.
    feature_name: str
        Name of the feature column that contains the value this map is
        based on.
    height: int
        Height of the original image in pixels.
    width: int
        Width of the original image in pixels.
    actual_target_value: object
        Actual target value of the dataset row.
    predicted_target_value: object
        Predicted target value of the dataset row that contains this image.
    activation_values: [ [ int ] ]
        A row-column matrix that contains the activation strengths for
        image regions. Values are integers in the range [0, 255].
    """

    _compute_path = "projects/{project_id}/models/{model_id}/imageActivationMaps/"
    _models_path = "projects/{project_id}/imageActivationMaps/"
    _list_path = "projects/{project_id}/models/{model_id}/imageActivationMaps/"
    _converter = t.Dict(
        {
            t.Key("image_id", optional=True): String(),
            t.Key("overlay_image_id", optional=True): String(),
            t.Key("feature_name", optional=True): String(),
            t.Key("image_width", to_name="width", optional=True): Int(),
            t.Key("image_height", to_name="height", optional=True): Int(),
            t.Key("activation_values", optional=True): t.List(t.List(Int())),
            t.Key("actual_target_value", optional=True): t.Any(),
            t.Key("predicted_target_value", optional=True): t.Any(),
            t.Key("target_values", optional=True): t.Or(t.List(String()), t.Null),
            t.Key("target_bins", optional=True): t.Or(t.List(t.Any()), t.Null),
        }
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self.project_id = kwargs.get("project_id")
        self.image = Image(**kwargs)
        self.overlay_image = Image(
            image_id=kwargs.get("overlay_image_id", kwargs.get("image_id")),
            project_id=kwargs.get("project_id"),
            height=kwargs.get("height", 0),
            width=kwargs.get("width", 0),
        )
        self.feature_name = kwargs.get("feature_name")
        self.actual_target_value = kwargs.get("actual_target_value")
        self.predicted_target_value = kwargs.get("predicted_target_value")
        self.activation_values = kwargs.get("activation_values")

    def __repr__(self):
        return (
            "datarobot.models.visualai.ActivationMap("
            "project_id={0.project_id}, "
            "model_id={0.model_id}, "
            "feature_name={0.feature_name}, "
            "image_id={0.image.id}, "
            "overlay_image_id={0.overlay_image.id}, "
            "height={0.image.height}, "
            "width={0.image.width})"
        ).format(self)

    @classmethod
    def compute(cls, project_id, model_id):
        """Start creation of a activation map in the given model.

        Parameters
        ----------
        project_id: str
            Project to start creation in.
        model_id: str
            Project's model to start creation in.

        Returns
        -------
        str
            URL to check for image embeddings progress.

        Raises
        ------
        datarobot.errors.ClientError
            Server rejected creation due to client error. Most likely
            cause is bad ``project_id`` or ``model_id``.
        """
        path = cls._compute_path.format(project_id=project_id, model_id=model_id)
        r_data = cls._client.post(path).json()
        return r_data["url"]

    @classmethod
    def models(cls, project_id):
        """List the models in a project.

        Parameters
        ----------
        project_id: str
            Project that contains the models.

        Returns
        -------
        list( tuple(model_id, feature_name) )
             List of model and feature name pairs.
        """
        path = cls._models_path.format(project_id=project_id)
        r_data = cls._client.get(path).json()
        return [(d["modelId"], d["featureName"]) for d in r_data.get("data", [])]

    @classmethod
    def list(cls, project_id, model_id, feature_name, offset=None, limit=None):
        """Return a list of ImageActivationMap objects.

        Parameters
        ----------
        project_id: str
            Project that contains the images.
        model_id: str
            Model that contains the images.
        feature_name: str
            Name of feature column that contains images.
        offset: int
            Number of images to be skipped.
        limit: int
            Number of images to be returned.
        """
        path = cls._list_path.format(project_id=project_id, model_id=model_id)
        list_params = {}
        list_params["featureName"] = feature_name
        if offset:
            list_params["offset"] = int(offset)
        if limit:
            list_params["limit"] = int(limit)
        r_data = cls._client.get(path, params=list_params).json()
        ret = []
        for amap_data in r_data.get("activationMaps", []):
            amap = cls.from_server_data(amap_data)
            amap.project_id = project_id
            amap.model_id = model_id
            amap.image.project_id = project_id
            amap.overlay_image.project_id = project_id
            ret.append(amap)
        return ret
