"""This module represents the Gitlab CI [needs](https://docs.gitlab.com/ee/ci/yaml/#needs) keyword.

Needs are to create relationships between `gcip.core.job.Job`s and `gcip.core.sequence.Sequence`s, which will
then be executed as early as all preceding required jobs finished. This relationship ignores the common ordering by stages.

You do not have to use the `Need` class, when simply linking`gcip.core.job.Job`s as well as `gcip.core.sequence.Sequence`s
together. When putting jobs and sequences into the `add_needs()` methods, they were translated into `Need`s internally:

```
my_job = Job(stage="example", script="do-something.sh")
my_sequence = Sequence()
...
my_next_job = Job(stage="example", script="do-anything.sh")
my_next_job.add_needs(my_job, my_sequence)

my_next_sequence = Sequence()
my_next_sequence.add_needs(my_job, my_sequence)
```

In this example `my_next_job` and `my_next_sequence` start as soon as

* `my_job` has finished
* all jobs within the last stage of `my_sequence` have finished

That also mean that stages are ignored, as the `example` stage for example.

However you have to use the `Need` class directly when depending on other pipelines jobs or for further configuration of the need,
like not [downloading artifacts](https://docs.gitlab.com/ee/ci/yaml/#artifact-downloads-with-needs) from preceding jobs:

```
my_job.add_needs(
    Need("awesome-job", project="master-pipeline"),
    Need(my_job, artifacts=False),
    )
```

You can use `Need` with the `pipeline` parameter, to either download artifacts from a parent pipeline or to
mirror the status from an upstream pipeline. Please refer to the official documentation for examples:

* [Artifact downloads to child pipelines](https://docs.gitlab.com/ee/ci/yaml/README.html#artifact-downloads-to-child-pipelines)
* [Mirror the status from upstream pipelines](https://docs.gitlab.com/ee/ci/yaml/README.html#complex-trigger-syntax-for-multi-project-pipelines)
"""
from __future__ import annotations

from typing import Dict, Union, Optional

from gcip.core.variables import PredefinedVariables


class Need(object):
    def __init__(
        self,
        job: Optional[str] = None,
        *,
        project: Optional[str] = None,
        ref: Optional[str] = None,
        pipeline: Optional[str] = None,
        artifacts: bool = True,
    ):
        """This class represents the Gitlab CI [needs](https://docs.gitlab.com/ee/ci/yaml/#needs) keyword.

        The `needs` key-word adds a possibility to allow out-of-order Gitlab CI jobs.
        A job which needed another job runs directly after the other job as finished successfully.

        Args:
            job (Optional[str]): The name of the job to depend on. Could be left is `pipeline` is set. Defaults to None which requires
                `pipeline` to be set.
            project (Optional[str]): If the `job` resides in another pipeline you have to give its project name here. Defaults to None.
            ref (Optional[str]): Branch of the remote project to depend on. Defaults to None.
            pipeline (Optional[str]): When $CI_PIPELINE_ID of another pipeline is provided, then artifacts from this
                pipeline were downloaded. When the name of an `other/project` is provided, then the status of an
                upstream pipeline is mirrored. Defaults to None, which requires `job` to be set.
            artifacts (bool): Download artifacts from the `job` to depend on. Defaults to True.

        Raises:
            ValueError: If neither `job` nor `pipeline` is set.
            ValueError: If `ref` is set but `project` is missing.
            ValueError: If `pipeline` equals the CI_PIPELINE_ID of the own project.
            ValueError: If both `project` and `pipeline` are set.
        """
        if not job and not pipeline:
            raise ValueError("At least one of `job` or `pipeline` must be set.")

        if ref and not project:
            raise ValueError("'ref' parameter requires the 'project' parameter.")

        if project and pipeline:
            raise ValueError("Needs accepts either `project` or `pipeline` but not both.")

        if pipeline and pipeline == PredefinedVariables.CI_PIPELINE_ID:
            raise ValueError(
                "The pipeline attribute does not accept the current pipeline ($CI_PIPELINE_ID). "
                "To download artifacts from a job in the current pipeline, use the basic form of needs."
            )

        self._job = job
        self._project = project
        self._ref = ref
        self._artifacts = artifacts
        self._pipeline = pipeline

        if self._project and not self._ref:
            self._ref = "main"

    def render(self) -> Dict[str, Union[str, bool]]:
        """Return a representation of this Need object as dictionary with static values.

        The rendered representation is used by the gcip to dump it
        in YAML format as part of the .gitlab-ci.yml pipeline.

        Returns:
            Dict[str, Any]: A dictionary representing the need object in Gitlab CI.
        """

        rendered_need: Dict[str, Union[str, bool]] = {}

        if self._job:
            rendered_need.update(
                {
                    "job": self._job,
                    "artifacts": self._artifacts,
                }
            )

        if self._project and self._ref:
            rendered_need.update({"project": self._project, "ref": self._ref})

        if self._pipeline:
            rendered_need["pipeline"] = self._pipeline

        return rendered_need

    def _equals(self, need: Optional[Need]) -> bool:
        """
        Returns:
            bool: True if self equals to `need`.
        """
        if not need:
            return False

        return self.render() == need.render()
