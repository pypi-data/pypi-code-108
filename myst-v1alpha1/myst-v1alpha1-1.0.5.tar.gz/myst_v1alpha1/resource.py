"""This module contains the `Resource` abstract base class for all Myst API resources to inherit from."""
import abc

import six

from myst_v1alpha1 import get_client
from myst_v1alpha1.utils.core_utils import format_repr
from myst_v1alpha1.utils.requests_utils import build_resource_url


@six.add_metaclass(abc.ABCMeta)
class Resource(object):
    """Abstract base resource for all Myst API resources to inherit from.

    This class dynamically adds attributes to itself based on responses to the Myst API.
    """

    RESOURCE_NAME = NotImplemented

    def __init__(self, uuid=None, **kwargs):
        """A `Resource` object is initialized with a `uuid` and any number of dynamic attributes.

        Args:
            **kwargs: keyword arguments to dynamically initialize on resource instance
        """
        self.uuid = uuid
        self.refresh_with(kwargs)

    def __eq__(self, other):
        """Resources are considered equal if all of their attributes are equal."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return format_repr(class_name=self.__class__.__name__, class_properties={"uuid": self.uuid})

    @classmethod
    def class_url(cls):
        """Returns the Myst API URL for this resource class.

        Returns:
            class_url (str): resource class URL
        """
        class_url = build_resource_url(resource_name=cls.RESOURCE_NAME)
        return class_url

    @classmethod
    def get(cls, uuid):
        """Gets the resource by uuid.

        Args:
            uuid (str): uuid of resource to get

        Returns:
            resource (myst_v1alpha1.resources.Resource): resource object
        """
        client = get_client()
        instance_url = build_resource_url(resource_name=cls.RESOURCE_NAME, resource_uuid=uuid)
        json_response = client.get(instance_url)
        resource = cls(**json_response)
        return resource

    @classmethod
    def list(cls):
        """Lists all resources.

        Returns:
            resources (list of myst_v1alpha1.resource.Resource): list of resources
        """
        client = get_client()
        class_url = cls.class_url()
        json_response = client.get(class_url)
        resources = [cls(**resource_json) for resource_json in json_response["data"]]
        return resources

    def instance_url(self):
        """Returns the Myst API URL for this resource instance.

        Returns:
            instance_url (str): resource instance URL
        """
        instance_url = build_resource_url(resource_name=self.RESOURCE_NAME, resource_uuid=self.uuid)
        return instance_url

    def refresh(self):
        """Refreshes the resource from the Myst API."""
        client = get_client()
        json_response = client.get(self.instance_url())
        self.refresh_with(attributes=json_response)

    def refresh_with(self, attributes):
        """Dynamically refreshes the resource instance with the given attributes.

        Args:
            attributes (dict): attributes to dynamically refresh resource instance with
        """
        self.__dict__.update(attributes)
