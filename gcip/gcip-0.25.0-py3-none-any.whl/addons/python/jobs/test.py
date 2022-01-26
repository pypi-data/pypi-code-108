from typing import Any, Union, Optional

from gcip.lib import rules
from gcip.core.job import Job, ScriptArgumentNotAllowedError
from gcip.core.image import Image
from gcip.addons.python.scripts import (
    pip_install_requirements,
)
from gcip.addons.container.images import PredefinedImages


class Pytest(Job):
    def __init__(
        self,
        *,
        name: str = "pytest",
        stage: str = "test",
        **kwargs: Any,
    ) -> None:
        """
        Runs `pytest` and installs project requirements before (`scripts.pip_install_requirements()`)

        * Requires a `requirements.txt` in your project folder containing at least `pytest`
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        super().__init__(
            name=name,
            stage=stage,
            script=[
                pip_install_requirements(),
                "pytest",
            ],
            **kwargs,
        )


class EvaluateGitTagPepe440Conformity(Job):
    def __init__(
        self,
        *,
        name: str = "tag-pep440-conformity",
        stage: str = "test",
        image: Optional[Union[Image, str]] = PredefinedImages.GCIP,
        **kwargs: Any,
    ) -> None:
        """
        Checks if the current pipelines `$CI_COMMIT_TAG` validates to a valid Python package version according to
        https://www.python.org/dev/peps/pep-0440

        This job already contains a rule to only run when a `$CI_COMMIT_TAG` is present (`rules.only_tags()`).
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        super().__init__(
            name=name,
            stage=stage,
            script="python3 -m gcip.tools.evaluate_git_tag_pep440_conformity",
            image=image,
            **kwargs,
        )
        self.append_rules(rules.on_tags())
