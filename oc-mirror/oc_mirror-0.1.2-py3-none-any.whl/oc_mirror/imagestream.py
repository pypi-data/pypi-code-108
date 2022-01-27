#!/usr/bin/env python

"""
Abstraction of an openshift image stream, as defined in:

https://docs.openshift.com/container-platform/4.4/rest_api/image_apis/imagestream-image-openshift-io-v1.html
"""

import logging

from typing import Tuple


from docker_registry_client_async import ImageName, JsonBytes

LOGGER = logging.getLogger(__name__)


class ImageStream(JsonBytes):
    """
    OpenShift image stream.
    """

    def get_name(self) -> str:
        """
        Retrieves the unique name within a namespace.

        Returns:
            The unique name within a namespace
        """
        return self.get_json()["metadata"]["name"]

    def get_tags(self) -> Tuple[str, ImageName]:
        """
        Retrieves the mapping of arbitrary string values to specific image locators.

        Yields:
            str: The arbitrary string value.
            ImageName: The specific image locator.
        """
        for tag in self.get_json()["spec"]["tags"]:
            if tag.get("from", []).get("kind", []) == "DockerImage":
                if "name" in tag:
                    name = f"{self.get_name()}-{tag['name']}"
                else:
                    name = self.get_name()
                yield name, ImageName.parse(tag["from"]["name"])
