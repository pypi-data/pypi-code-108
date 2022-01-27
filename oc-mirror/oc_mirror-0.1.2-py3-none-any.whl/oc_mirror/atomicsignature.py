#!/usr/bin/env python

"""
Abstraction of an openshift atomic signature, as defined in:

https://github.com/openshift/containers-image/blob/master/docs/atomic-signature.md
"""

import logging


from docker_registry_client_async import FormattedSHA256, ImageName, JsonBytes

LOGGER = logging.getLogger(__name__)


class AtomicSignature(JsonBytes):
    """
    OpenShift atomic signature.
    """

    TYPE = "atomic container signature"

    def get_docker_manifest_digest(self) -> FormattedSHA256:
        """
        Retrieves the docker manifest digest.

        Returns:
            The docker manifest digest.
        """
        return FormattedSHA256.parse(
            self.get_json()["critical"]["image"]["docker-manifest-digest"]
        )

    def get_docker_reference(self) -> ImageName:
        """
        Retrieves the docker reference.

        Returns:
            The docker reference.
        """
        return ImageName.parse(
            self.get_json()["critical"]["identity"]["docker-reference"]
        )

    def get_type(self) -> str:
        """
        Retrieves the signature type.

        Returns:
            The signature type.
        """
        return self.get_json()["critical"]["type"]
