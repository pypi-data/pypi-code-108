"""**ALPHA** This module represents the Gitlab CI [Service](https://docs.gitlab.com/ee/ci/yaml/README.html#services) keyword.

The services keyword defines a Docker image that runs during a job linked to the Docker image that the image keyword defines.
This allows you to access the service image during build time.

Currently this module is an unfinished prototype.
"""

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach", "Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


class Service:
    """**ALPHA** This class represents the Gitlab CI [Service](https://docs.gitlab.com/ee/ci/yaml/README.html#services) keyword.

    Currently there is nothing more implemented than providing a service name. In general the `service` functionality
    currently isn't well implemented, as it is only available for `gcip.core.pipeline.Pipeline`s.
    """

    def __init__(self, name: str):
        self._name = name

    def render(self) -> str:
        """Return a representation of this Service object as dictionary with static values.

        The rendered representation is used by the gcip to dump it
        in YAML format as part of the .gitlab-ci.yml pipeline.

        Returns:
            Dict[str, Any]: A dictionary representing the service object in Gitlab CI.
        """
        return self._name
