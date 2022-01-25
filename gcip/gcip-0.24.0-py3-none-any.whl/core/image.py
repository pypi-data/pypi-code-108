"""This module represents the Gitlab CI [Image](https://docs.gitlab.com/ee/ci/yaml/#image) keyword.

Use `Image` to specify a Docker image to use for the `gcip.core.job.Job`.

```
job1.set_image(Image("python"))
job2.set_image(Image("gcr.io/kaniko-project/executor:debug", entrypoint=[""]))
```
"""
from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Union, Optional

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach", "Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


class Image:
    def __init__(self, name: str, *, tag: Optional[str] = None, entrypoint: Optional[List[str]] = None) -> None:
        """This module represents the Gitlab CI [Image](https://docs.gitlab.com/ee/ci/yaml/#image) keyword.

        Use `Image` to specify a Docker image to use for the `gcip.core.job.Job`.

        Objects of this class are not meant to be altered. This is because Image objects are typically be defined
        at a central place and often re-used. Altering the object at one place may lead to unpredictable changes
        at any reference to that object. That is this class has no setter methods. However you can use  the
        `.with_tag()` and `.with_entrypoint()` methods on an Image object, which will return an altered copy
        of that image. Thus you can re-use a centrally maintained Image object and modify it for just the
        place you are using the altered image (copy).

        Args:
            name (str): The fully qualified image name. Could include repository and tag as usual.
            tag (Optional[str]): Container image tag in registrie to use.
            entrypoint (Optional[List[str]]): Overwrites the containers entrypoint. Defaults to None.
        """
        self._name = name
        self._tag = tag
        self._entrypoint = entrypoint

    @property
    def name(self) -> str:
        """Equals the identical Class argument."""
        return self._name

    @property
    def tag(self) -> Optional[str]:
        """Equals the identical Class argument."""
        return self._tag

    @property
    def entrypoint(self) -> Optional[List[str]]:
        """Equals the identical Class argument."""
        return self._entrypoint

    def with_tag(self, tag: str) -> Image:
        """
        Returns a copy of that image with altered tag.
        You can still use the original Image object with its original tag.
        """
        copy = deepcopy(self)
        copy._tag = tag
        return copy

    def with_entrypoint(self, *entrypoint: str) -> Image:
        """
        Returns a copy of that image with altered entrypoint.
        You can still use the original Image object with its original entrypoint.
        """
        copy = deepcopy(self)
        copy._entrypoint = list(entrypoint)
        return copy

    def render(self) -> Dict[str, Union[str, List[str]]]:
        """Return a representation of this Image object as dictionary with static values.

        The rendered representation is used by the gcip to dump it
        in YAML format as part of the .gitlab-ci.yml pipeline.

        Returns:
            Dict[str, Union[str, List[str]]]: A dictionary prepresenting the image object in Gitlab CI.
        """
        rendered: Dict[str, Union[str, List[str]]] = {}

        rendered["name"] = self.name + (f":{self.tag}" if self.tag else "")

        if self._entrypoint:
            rendered["entrypoint"] = self._entrypoint

        return rendered

    def _equals(self, image: Optional[Image]) -> bool:
        """
        Returns:
            bool: True if self equals to `image`.
        """
        if not image:
            return False

        return self.render() == image.render()
