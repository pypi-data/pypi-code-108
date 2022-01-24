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

from ...enums import PROJECT_STAGE
from ..api_object import APIObject
from ..project import Project

__all__ = ["Image", "SampleImage", "DuplicateImage"]


class Image(APIObject):
    """An image stored in a project's dataset.

    Attributes
    ----------
    id: str
        Image ID for this image.
    image_type: str
        Image media type. Accessing this may require a server request
        and an associated delay in returning.
    image_bytes: [octet]
        Raw octets of this image. Accessing this may require a server request
        and an associated delay in returning.
    height: int
        Height of the image in pixels (72 pixels per inch).
    width: int
        Width of the image in pixels (72 pixels per inch).
    """

    _get_path = "projects/{project_id}/images/{image_id}/"
    _bytes_path = "projects/{project_id}/images/{image_id}/file/"
    _converter = t.Dict(
        {
            t.Key("image_id", optional=True): String(),
            t.Key("height", optional=True): Int(),
            t.Key("width", optional=True): Int(),
        }
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self.id = kwargs.get("image_id")
        self.project_id = kwargs.get("project_id")
        self.__image_type = None
        self.__image_bytes = None
        self.height = int(kwargs.get("height", 0))
        self.width = int(kwargs.get("width", 0))

    def __repr__(self):
        return (
            "datarobot.models.visualai.Image("
            "project_id={0.project_id}, "
            "image_id={0.id}, "
            "height={0.height}, "
            "width={0.width})"
        ).format(self)

    @property
    def image_type(self):
        if not self.__image_type:
            self.__get_image_bytes()
        return self.__image_type

    @property
    def image_bytes(self):
        if not self.__image_bytes:
            self.__get_image_bytes()
        return self.__image_bytes

    def __get_image_bytes(self):
        path = self._bytes_path.format(project_id=self.project_id, image_id=self.id)
        r_data = self._client.get(path)
        self.__image_type = r_data.headers.get("Content-Type")
        self.__image_bytes = r_data.content

    @classmethod
    def get(cls, project_id, image_id):
        """Get a single image object from project.

        Parameters
        ----------
        project_id: str
            Project that contains the images.
        image_id: str
            ID of image to load from the project.
        """
        path = cls._get_path.format(project_id=project_id, image_id=image_id)
        r_data = cls._client.get(path).json()
        ret = cls.from_server_data(r_data)
        ret.project_id = project_id
        return ret


class SampleImage(APIObject):
    """A sample image in a project's dataset.

    If ``Project.stage`` is ``datarobot.enums.PROJECT_STAGE.EDA2`` then
    the ``target_*`` attributes of this class will have values, otherwise
    the values will all be None.

    Attributes
    ----------
    image: Image
        Image object.
    target_value: str
        Value associated with the ``feature_name``.
    """

    _list_sample_path = "projects/{project_id}/imageSamples/"
    _list_images_path = "projects/{project_id}/images/"
    _converter = t.Dict(
        {
            t.Key("image_id", optional=True): String(),
            t.Key("height", optional=True): Int(),
            t.Key("width", optional=True): Int(),
            t.Key("target_value", optional=True): String | Int | t.Float | t.List(String),
        }
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self.image = Image(**kwargs)
        self.project_id = kwargs.get("project_id")
        self.target_value = kwargs.get("target_value")

    def __repr__(self):
        return (
            "datarobot.models.visualai.SampleImage("
            "project_id={0.project_id}, "
            "image_id={0.image.id}, "
            "target_value={0.target_value})"
        ).format(self)

    @classmethod
    def list(cls, project_id, feature_name, target_value=None, offset=None, limit=None):
        """Get sample images from a project.

        Parameters
        ----------
        project_id: str
            Project that contains the images.
        feature_name: str
            Name of feature column that contains images.
        target_value: str
            Target value to filter images.
        offset: int
            Number of images to be skipped.
        limit: int
            Number of images to be returned.
        """
        project = Project.get(project_id)
        list_params = {}
        if project.stage in [PROJECT_STAGE.EDA2, PROJECT_STAGE.MODELING]:
            path = cls._list_images_path.format(project_id=project_id)
        else:
            path = cls._list_sample_path.format(project_id=project_id)

        if feature_name:
            list_params["featureName"] = feature_name
        if target_value:
            list_params["targetValue"] = target_value
        if offset:
            list_params["offset"] = int(offset)
        if limit:
            list_params["limit"] = int(limit)

        r_data = cls._client.get(path, params=list_params).json()
        ret = []
        for si_data in r_data["data"]:
            si = cls.from_server_data(si_data)
            si.project_id = project_id
            si.image.project_id = project_id
            ret.append(si)
        return ret


class DuplicateImage(APIObject):
    """An image that was duplicated in the project dataset.

    Attributes
    ----------
    image: Image
        Image object.
    count: int
        Number of times the image was duplicated.
    """

    _list_path = "projects/{project_id}/duplicateImages/{feature_name}/"
    _converter = t.Dict(
        {t.Key("image_id", optional=True): String(), t.Key("row_count", optional=True): Int()}
    ).ignore_extra("*")

    def __init__(self, **kwargs):
        self.image = Image(**kwargs)
        self.project_id = kwargs.get("project_id")
        self.count = kwargs.get("row_count")

    def __repr__(self):
        return (
            "datarobot.models.visualai.DuplicateImage("
            "project_id={0.project_id}, "
            "image_id={0.image.id}, "
            "count={0.count})"
        ).format(self)

    @classmethod
    def list(cls, project_id, feature_name, offset=None, limit=None):
        """Get all duplicate images in a project.

        Parameters
        ----------
        project_id: str
            Project that contains the images.
        feature_name: str
            Name of feature column that contains images.
        offset: int
            Number of images to be skipped.
        limit: int
            Number of images to be returned.
        """
        path = cls._list_path.format(project_id=project_id, feature_name=feature_name)
        list_params = {}
        if offset:
            list_params["offset"] = int(offset)
        if limit:
            list_params["limit"] = int(limit)
        r_data = cls._client.get(path, params=list_params).json()
        ret = []
        for si_data in r_data["data"]:
            si = cls.from_server_data(si_data)
            si.project_id = project_id
            si.image.project_id = project_id
            ret.append(si)
        return ret
