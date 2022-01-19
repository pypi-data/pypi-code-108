# coding: utf-8

"""
    Tator REST API

    Interface to the Tator backend.  # noqa: E501

    The version of the OpenAPI document: v1
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from ..configuration import Configuration


class MediaSpec(object):
    """
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'attributes': 'object',
        'codec': 'str',
        'fps': 'float',
        'gid': 'str',
        'height': 'int',
        'md5': 'str',
        'name': 'str',
        'num_frames': 'int',
        'section': 'str',
        'thumbnail_gif_url': 'str',
        'thumbnail_url': 'str',
        'type': 'int',
        'uid': 'str',
        'url': 'str',
        'width': 'int'
    }

    attribute_map = {
        'attributes': 'attributes',
        'codec': 'codec',
        'fps': 'fps',
        'gid': 'gid',
        'height': 'height',
        'md5': 'md5',
        'name': 'name',
        'num_frames': 'num_frames',
        'section': 'section',
        'thumbnail_gif_url': 'thumbnail_gif_url',
        'thumbnail_url': 'thumbnail_url',
        'type': 'type',
        'uid': 'uid',
        'url': 'url',
        'width': 'width'
    }

    def __init__(self, attributes=None, codec=None, fps=None, gid=None, height=None, md5=None, name=None, num_frames=None, section=None, thumbnail_gif_url=None, thumbnail_url=None, type=None, uid=None, url=None, width=None, local_vars_configuration=None):  # noqa: E501
        """MediaSpec - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._attributes = None
        self._codec = None
        self._fps = None
        self._gid = None
        self._height = None
        self._md5 = None
        self._name = None
        self._num_frames = None
        self._section = None
        self._thumbnail_gif_url = None
        self._thumbnail_url = None
        self._type = None
        self._uid = None
        self._url = None
        self._width = None
        self.discriminator = None

        self.attributes = attributes
        self.codec = codec
        self.fps = fps
        if gid is not None:
            self.gid = gid
        self.height = height
        self.md5 = md5
        self.name = name
        self.num_frames = num_frames
        self.section = section
        if thumbnail_gif_url is not None:
            self.thumbnail_gif_url = thumbnail_gif_url
        if thumbnail_url is not None:
            self.thumbnail_url = thumbnail_url
        self.type = type
        if uid is not None:
            self.uid = uid
        if url is not None:
            self.url = url
        self.width = width

    @property
    def attributes(self):
        """
        Attributes for the media

        :return: The attributes of this MediaSpec. 
        :rtype: object
        """
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        """
        Attributes for the media

        :param attributes: The attributes of this MediaSpec.
        :type: object
        """

        self._attributes = attributes

    @property
    def codec(self):
        """
        Codec for videos.

        :return: The codec of this MediaSpec. 
        :rtype: str
        """
        return self._codec

    @codec.setter
    def codec(self, codec):
        """
        Codec for videos.

        :param codec: The codec of this MediaSpec.
        :type: str
        """

        self._codec = codec

    @property
    def fps(self):
        """
        Frame rate for videos.

        :return: The fps of this MediaSpec. 
        :rtype: float
        """
        return self._fps

    @fps.setter
    def fps(self, fps):
        """
        Frame rate for videos.

        :param fps: The fps of this MediaSpec.
        :type: float
        """

        self._fps = fps

    @property
    def gid(self):
        """
        Group ID for the upload group of this media.

        :return: The gid of this MediaSpec. 
        :rtype: str
        """
        return self._gid

    @gid.setter
    def gid(self, gid):
        """
        Group ID for the upload group of this media.

        :param gid: The gid of this MediaSpec.
        :type: str
        """

        self._gid = gid

    @property
    def height(self):
        """
        Vertical resolution in pixels.

        :return: The height of this MediaSpec. 
        :rtype: int
        """
        return self._height

    @height.setter
    def height(self, height):
        """
        Vertical resolution in pixels.

        :param height: The height of this MediaSpec.
        :type: int
        """

        self._height = height

    @property
    def md5(self):
        """
        MD5 sum of the media file.

        :return: The md5 of this MediaSpec. 
        :rtype: str
        """
        return self._md5

    @md5.setter
    def md5(self, md5):
        """
        MD5 sum of the media file.

        :param md5: The md5 of this MediaSpec.
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and md5 is None:  # noqa: E501
            raise ValueError("Invalid value for `md5`, must not be `None`")  # noqa: E501

        self._md5 = md5

    @property
    def name(self):
        """
        Name of the file.

        :return: The name of this MediaSpec. 
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Name of the file.

        :param name: The name of this MediaSpec.
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def num_frames(self):
        """
        Number of frames for videos.

        :return: The num_frames of this MediaSpec. 
        :rtype: int
        """
        return self._num_frames

    @num_frames.setter
    def num_frames(self, num_frames):
        """
        Number of frames for videos.

        :param num_frames: The num_frames of this MediaSpec.
        :type: int
        """

        self._num_frames = num_frames

    @property
    def section(self):
        """
        Media section name.

        :return: The section of this MediaSpec. 
        :rtype: str
        """
        return self._section

    @section.setter
    def section(self, section):
        """
        Media section name.

        :param section: The section of this MediaSpec.
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and section is None:  # noqa: E501
            raise ValueError("Invalid value for `section`, must not be `None`")  # noqa: E501

        self._section = section

    @property
    def thumbnail_gif_url(self):
        """
        Upload URL for the video gif thumbnail if already generated.

        :return: The thumbnail_gif_url of this MediaSpec. 
        :rtype: str
        """
        return self._thumbnail_gif_url

    @thumbnail_gif_url.setter
    def thumbnail_gif_url(self, thumbnail_gif_url):
        """
        Upload URL for the video gif thumbnail if already generated.

        :param thumbnail_gif_url: The thumbnail_gif_url of this MediaSpec.
        :type: str
        """

        self._thumbnail_gif_url = thumbnail_gif_url

    @property
    def thumbnail_url(self):
        """
        Upload URL for the media thumbnail if already generated.

        :return: The thumbnail_url of this MediaSpec. 
        :rtype: str
        """
        return self._thumbnail_url

    @thumbnail_url.setter
    def thumbnail_url(self, thumbnail_url):
        """
        Upload URL for the media thumbnail if already generated.

        :param thumbnail_url: The thumbnail_url of this MediaSpec.
        :type: str
        """

        self._thumbnail_url = thumbnail_url

    @property
    def type(self):
        """
        Unique integer identifying a media type. Use -1 to automatically select the media type if only one media type exists in a project.

        :return: The type of this MediaSpec. 
        :rtype: int
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Unique integer identifying a media type. Use -1 to automatically select the media type if only one media type exists in a project.

        :param type: The type of this MediaSpec.
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and type is None:  # noqa: E501
            raise ValueError("Invalid value for `type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                type is not None and type < -1):  # noqa: E501
            raise ValueError("Invalid value for `type`, must be a value greater than or equal to `-1`")  # noqa: E501

        self._type = type

    @property
    def uid(self):
        """
        Unique ID for the upload of this media.

        :return: The uid of this MediaSpec. 
        :rtype: str
        """
        return self._uid

    @uid.setter
    def uid(self, uid):
        """
        Unique ID for the upload of this media.

        :param uid: The uid of this MediaSpec.
        :type: str
        """

        self._uid = uid

    @property
    def url(self):
        """
        Upload URL for the image if this is an image type, URL of hosted original media if this is a video type. For video types this field is just for reference.

        :return: The url of this MediaSpec. 
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """
        Upload URL for the image if this is an image type, URL of hosted original media if this is a video type. For video types this field is just for reference.

        :param url: The url of this MediaSpec.
        :type: str
        """

        self._url = url

    @property
    def width(self):
        """
        Horizontal resolution in pixels.

        :return: The width of this MediaSpec. 
        :rtype: int
        """
        return self._width

    @width.setter
    def width(self, width):
        """
        Horizontal resolution in pixels.

        :param width: The width of this MediaSpec.
        :type: int
        """

        self._width = width

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, MediaSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MediaSpec):
            return True

        return self.to_dict() != other.to_dict()
