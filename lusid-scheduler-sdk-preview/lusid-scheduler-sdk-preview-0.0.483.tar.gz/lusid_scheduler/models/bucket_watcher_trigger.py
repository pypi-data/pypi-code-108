# coding: utf-8

"""
    FINBOURNE Scheduler API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.0.483
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from lusid_scheduler.configuration import Configuration


class BucketWatcherTrigger(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'file': 'str',
        'poll_period': 'int',
        'bucket': 'str'
    }

    attribute_map = {
        'file': 'file',
        'poll_period': 'pollPeriod',
        'bucket': 'bucket'
    }

    required_map = {
        'file': 'optional',
        'poll_period': 'optional',
        'bucket': 'optional'
    }

    def __init__(self, file=None, poll_period=None, bucket=None, local_vars_configuration=None):  # noqa: E501
        """BucketWatcherTrigger - a model defined in OpenAPI"
        
        :param file:  The file name or partial path of the file that will trigger the job  E.G: `fileName` or `folder1/folder2/someFileName`
        :type file: str
        :param poll_period:  The frequency, in seconds, at which to poll the S3 bucket for the file.  Defaults to 5.
        :type poll_period: int
        :param bucket:  The S3 bucket where to watch for the trigger file
        :type bucket: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._file = None
        self._poll_period = None
        self._bucket = None
        self.discriminator = None

        self.file = file
        if poll_period is not None:
            self.poll_period = poll_period
        self.bucket = bucket

    @property
    def file(self):
        """Gets the file of this BucketWatcherTrigger.  # noqa: E501

        The file name or partial path of the file that will trigger the job  E.G: `fileName` or `folder1/folder2/someFileName`  # noqa: E501

        :return: The file of this BucketWatcherTrigger.  # noqa: E501
        :rtype: str
        """
        return self._file

    @file.setter
    def file(self, file):
        """Sets the file of this BucketWatcherTrigger.

        The file name or partial path of the file that will trigger the job  E.G: `fileName` or `folder1/folder2/someFileName`  # noqa: E501

        :param file: The file of this BucketWatcherTrigger.  # noqa: E501
        :type file: str
        """
        if (self.local_vars_configuration.client_side_validation and
                file is not None and len(file) > 256):
            raise ValueError("Invalid value for `file`, length must be less than or equal to `256`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                file is not None and len(file) < 1):
            raise ValueError("Invalid value for `file`, length must be greater than or equal to `1`")  # noqa: E501

        self._file = file

    @property
    def poll_period(self):
        """Gets the poll_period of this BucketWatcherTrigger.  # noqa: E501

        The frequency, in seconds, at which to poll the S3 bucket for the file.  Defaults to 5.  # noqa: E501

        :return: The poll_period of this BucketWatcherTrigger.  # noqa: E501
        :rtype: int
        """
        return self._poll_period

    @poll_period.setter
    def poll_period(self, poll_period):
        """Sets the poll_period of this BucketWatcherTrigger.

        The frequency, in seconds, at which to poll the S3 bucket for the file.  Defaults to 5.  # noqa: E501

        :param poll_period: The poll_period of this BucketWatcherTrigger.  # noqa: E501
        :type poll_period: int
        """
        if (self.local_vars_configuration.client_side_validation and
                poll_period is not None and poll_period > 86400):  # noqa: E501
            raise ValueError("Invalid value for `poll_period`, must be a value less than or equal to `86400`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                poll_period is not None and poll_period < 1):  # noqa: E501
            raise ValueError("Invalid value for `poll_period`, must be a value greater than or equal to `1`")  # noqa: E501

        self._poll_period = poll_period

    @property
    def bucket(self):
        """Gets the bucket of this BucketWatcherTrigger.  # noqa: E501

        The S3 bucket where to watch for the trigger file  # noqa: E501

        :return: The bucket of this BucketWatcherTrigger.  # noqa: E501
        :rtype: str
        """
        return self._bucket

    @bucket.setter
    def bucket(self, bucket):
        """Sets the bucket of this BucketWatcherTrigger.

        The S3 bucket where to watch for the trigger file  # noqa: E501

        :param bucket: The bucket of this BucketWatcherTrigger.  # noqa: E501
        :type bucket: str
        """

        self._bucket = bucket

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, BucketWatcherTrigger):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, BucketWatcherTrigger):
            return True

        return self.to_dict() != other.to_dict()
