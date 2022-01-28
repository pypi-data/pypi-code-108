import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import (
    Component as _Component_2b0ad27f,
    Project as _Project_57d89203,
    YamlFile as _YamlFile_909731b0,
)


@jsii.enum(jsii_type="projen.gitlab.Action")
class Action(enum.Enum):
    '''(experimental) Specifies what this job will do.

    'start' (default) indicates the job will start the
    deployment. 'prepare' indicates this will not affect the deployment. 'stop' indicates
    this will stop the deployment.

    :stability: experimental
    '''

    PREPARE = "PREPARE"
    '''
    :stability: experimental
    '''
    START = "START"
    '''
    :stability: experimental
    '''
    STOP = "STOP"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="projen.gitlab.AllowFailure",
    jsii_struct_bases=[],
    name_mapping={"exit_codes": "exitCodes"},
)
class AllowFailure:
    def __init__(
        self,
        *,
        exit_codes: typing.Union[jsii.Number, typing.Sequence[jsii.Number]],
    ) -> None:
        '''(experimental) Exit code that are not considered failure.

        The job fails for any other exit code.
        You can list which exit codes are not considered failures. The job fails for any other
        exit code.

        :param exit_codes: 

        :see: https://docs.gitlab.com/ee/ci/yaml/#allow_failure
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "exit_codes": exit_codes,
        }

    @builtins.property
    def exit_codes(self) -> typing.Union[jsii.Number, typing.List[jsii.Number]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("exit_codes")
        assert result is not None, "Required property 'exit_codes' is missing"
        return typing.cast(typing.Union[jsii.Number, typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AllowFailure(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Artifacts",
    jsii_struct_bases=[],
    name_mapping={
        "exclude": "exclude",
        "expire_in": "expireIn",
        "expose_as": "exposeAs",
        "name": "name",
        "paths": "paths",
        "reports": "reports",
        "untracked": "untracked",
        "when": "when",
    },
)
class Artifacts:
    def __init__(
        self,
        *,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        expire_in: typing.Optional[builtins.str] = None,
        expose_as: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        paths: typing.Optional[typing.Sequence[builtins.str]] = None,
        reports: typing.Optional["Reports"] = None,
        untracked: typing.Optional[builtins.bool] = None,
        when: typing.Optional["CacheWhen"] = None,
    ) -> None:
        '''(experimental) Used to specify a list of files and directories that should be attached to the job if it succeeds.

        Artifacts are sent to Gitlab where they can be downloaded.

        :param exclude: (experimental) A list of paths to files/folders that should be excluded in the artifact.
        :param expire_in: (experimental) How long artifacts should be kept. They are saved 30 days by default. Artifacts that have expired are removed periodically via cron job. Supports a wide variety of formats, e.g. '1 week', '3 mins 4 sec', '2 hrs 20 min', '2h20min', '6 mos 1 day', '47 yrs 6 mos and 4d', '3 weeks and 2 days'.
        :param expose_as: (experimental) Can be used to expose job artifacts in the merge request UI. GitLab will add a link <expose_as> to the relevant merge request that points to the artifact.
        :param name: (experimental) Name for the archive created on job success. Can use variables in the name, e.g. '$CI_JOB_NAME'
        :param paths: (experimental) A list of paths to files/folders that should be included in the artifact.
        :param reports: (experimental) Reports will be uploaded as artifacts, and often displayed in the Gitlab UI, such as in Merge Requests.
        :param untracked: (experimental) Whether to add all untracked files (along with 'artifacts.paths') to the artifact.
        :param when: (experimental) Configure when artifacts are uploaded depended on job status.

        :see: https://docs.gitlab.com/ee/ci/yaml/#artifacts
        :stability: experimental
        '''
        if isinstance(reports, dict):
            reports = Reports(**reports)
        self._values: typing.Dict[str, typing.Any] = {}
        if exclude is not None:
            self._values["exclude"] = exclude
        if expire_in is not None:
            self._values["expire_in"] = expire_in
        if expose_as is not None:
            self._values["expose_as"] = expose_as
        if name is not None:
            self._values["name"] = name
        if paths is not None:
            self._values["paths"] = paths
        if reports is not None:
            self._values["reports"] = reports
        if untracked is not None:
            self._values["untracked"] = untracked
        if when is not None:
            self._values["when"] = when

    @builtins.property
    def exclude(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of paths to files/folders that should be excluded in the artifact.

        :stability: experimental
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def expire_in(self) -> typing.Optional[builtins.str]:
        '''(experimental) How long artifacts should be kept.

        They are saved 30 days by default. Artifacts that have expired are removed periodically via cron job. Supports a wide variety of formats, e.g. '1 week', '3 mins 4 sec', '2 hrs 20 min', '2h20min', '6 mos 1 day', '47 yrs 6 mos and 4d', '3 weeks and 2 days'.

        :stability: experimental
        '''
        result = self._values.get("expire_in")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expose_as(self) -> typing.Optional[builtins.str]:
        '''(experimental) Can be used to expose job artifacts in the merge request UI.

        GitLab will add a link <expose_as> to the relevant merge request that points to the artifact.

        :stability: experimental
        '''
        result = self._values.get("expose_as")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name for the archive created on job success.

        Can use variables in the name, e.g. '$CI_JOB_NAME'

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def paths(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of paths to files/folders that should be included in the artifact.

        :stability: experimental
        '''
        result = self._values.get("paths")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def reports(self) -> typing.Optional["Reports"]:
        '''(experimental) Reports will be uploaded as artifacts, and often displayed in the Gitlab UI, such as in Merge Requests.

        :stability: experimental
        '''
        result = self._values.get("reports")
        return typing.cast(typing.Optional["Reports"], result)

    @builtins.property
    def untracked(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to add all untracked files (along with 'artifacts.paths') to the artifact.

        :stability: experimental
        '''
        result = self._values.get("untracked")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def when(self) -> typing.Optional["CacheWhen"]:
        '''(experimental) Configure when artifacts are uploaded depended on job status.

        :stability: experimental
        '''
        result = self._values.get("when")
        return typing.cast(typing.Optional["CacheWhen"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Artifacts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Assets",
    jsii_struct_bases=[],
    name_mapping={"links": "links"},
)
class Assets:
    def __init__(self, *, links: typing.Sequence["Link"]) -> None:
        '''(experimental) Asset configuration for a release.

        :param links: (experimental) Include asset links in the release.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "links": links,
        }

    @builtins.property
    def links(self) -> typing.List["Link"]:
        '''(experimental) Include asset links in the release.

        :stability: experimental
        '''
        result = self._values.get("links")
        assert result is not None, "Required property 'links' is missing"
        return typing.cast(typing.List["Link"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Assets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Cache",
    jsii_struct_bases=[],
    name_mapping={"when": "when"},
)
class Cache:
    def __init__(self, *, when: typing.Optional["CacheWhen"] = None) -> None:
        '''(experimental) Cache Definition.

        :param when: (experimental) Defines when to save the cache, based on the status of the job (Default: Job Success).

        :see: https://docs.gitlab.com/ee/ci/yaml/#cache
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if when is not None:
            self._values["when"] = when

    @builtins.property
    def when(self) -> typing.Optional["CacheWhen"]:
        '''(experimental) Defines when to save the cache, based on the status of the job (Default: Job Success).

        :stability: experimental
        '''
        result = self._values.get("when")
        return typing.cast(typing.Optional["CacheWhen"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Cache(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.gitlab.CacheWhen")
class CacheWhen(enum.Enum):
    '''(experimental) Configure when artifacts are uploaded depended on job status.

    :see: https://docs.gitlab.com/ee/ci/yaml/#cachewhen
    :stability: experimental
    '''

    ALWAYS = "ALWAYS"
    '''(experimental) Upload artifacts regardless of job status.

    :stability: experimental
    '''
    ON_FAILURE = "ON_FAILURE"
    '''(experimental) Upload artifacts only when the job fails.

    :stability: experimental
    '''
    ON_SUCCESS = "ON_SUCCESS"
    '''(experimental) Upload artifacts only when the job succeeds (this is the default).

    :stability: experimental
    '''


class CiConfiguration(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.gitlab.CiConfiguration",
):
    '''(experimental) CI for GitLab.

    A CI is a configurable automated process made up of one or more stages/jobs.

    :see: https://docs.gitlab.com/ee/ci/yaml/
    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        name: builtins.str,
        *,
        default: typing.Optional["Default"] = None,
        jobs: typing.Optional[typing.Mapping[builtins.str, "Job"]] = None,
        pages: typing.Optional["Job"] = None,
        stages: typing.Optional[typing.Sequence[builtins.str]] = None,
        variables: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow: typing.Optional["Workflow"] = None,
    ) -> None:
        '''
        :param project: -
        :param name: -
        :param default: (experimental) Default settings for the CI Configuration. Jobs that do not define one or more of the listed keywords use the value defined in the default section.
        :param jobs: (experimental) An initial set of jobs to add to the configuration.
        :param pages: (experimental) A special job used to upload static sites to Gitlab pages. Requires a ``public/`` directory with ``artifacts.path`` pointing to it.
        :param stages: (experimental) Groups jobs into stages. All jobs in one stage must complete before next stage is executed. If no stages are specified. Defaults to ['build', 'test', 'deploy'].
        :param variables: (experimental) Global variables that are passed to jobs. If the job already has that variable defined, the job-level variable takes precedence.
        :param workflow: (experimental) Used to control pipeline behavior.

        :stability: experimental
        '''
        options = CiConfigurationOptions(
            default=default,
            jobs=jobs,
            pages=pages,
            stages=stages,
            variables=variables,
            workflow=workflow,
        )

        jsii.create(self.__class__, self, [project, name, options])

    @jsii.member(jsii_name="addGlobalVariables")
    def add_global_variables(
        self,
        variables: typing.Mapping[builtins.str, typing.Any],
    ) -> None:
        '''(experimental) Add a globally defined variable to the CI configuration.

        :param variables: The variables to add.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addGlobalVariables", [variables]))

    @jsii.member(jsii_name="addIncludes")
    def add_includes(self, *includes: "Include") -> None:
        '''(experimental) Add additional yml/yaml files to the CI includes.

        :param includes: The includes to add.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addIncludes", [*includes]))

    @jsii.member(jsii_name="addJobs")
    def add_jobs(self, jobs: typing.Mapping[builtins.str, "Job"]) -> None:
        '''(experimental) Add jobs and their stages to the CI configuration.

        :param jobs: Jobs to add.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addJobs", [jobs]))

    @jsii.member(jsii_name="addServices")
    def add_services(self, *services: "Service") -> None:
        '''(experimental) Add additional services.

        :param services: The services to add.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addServices", [*services]))

    @jsii.member(jsii_name="addStages")
    def add_stages(self, *stages: builtins.str) -> None:
        '''(experimental) Add stages to the CI configuration if not already present.

        :param stages: stages to add.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addStages", [*stages]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultAfterScript")
    def default_after_script(self) -> typing.List[builtins.str]:
        '''(experimental) Defines default scripts that should run *after* all jobs.

        Can be overriden by the job level ``afterScript``.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "defaultAfterScript"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultBeforeScript")
    def default_before_script(self) -> typing.List[builtins.str]:
        '''(experimental) Defines default scripts that should run *before* all jobs.

        Can be overriden by the job level ``afterScript``.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "defaultBeforeScript"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTags")
    def default_tags(self) -> typing.List[builtins.str]:
        '''(experimental) Used to select a specific runner from the list of all runners that are available for the project.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "defaultTags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="file")
    def file(self) -> _YamlFile_909731b0:
        '''(experimental) The workflow YAML file.

        :stability: experimental
        '''
        return typing.cast(_YamlFile_909731b0, jsii.get(self, "file"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobs")
    def jobs(self) -> typing.Mapping[builtins.str, "Job"]:
        '''(experimental) The jobs in the CI configuration.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, "Job"], jsii.get(self, "jobs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        '''(experimental) Path to CI file generated by the configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="project")
    def project(self) -> _Project_57d89203:
        '''(experimental) The project the configuration belongs to.

        :stability: experimental
        '''
        return typing.cast(_Project_57d89203, jsii.get(self, "project"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[builtins.str]:
        '''(experimental) Groups jobs into stages.

        All jobs in one stage must complete before next stage is
        executed. Defaults to ['build', 'test', 'deploy'].

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "stages"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variables")
    def variables(
        self,
    ) -> typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number, "VariableConfig"]]:
        '''(experimental) Global variables that are passed to jobs.

        If the job already has that variable defined, the job-level variable takes precedence.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number, "VariableConfig"]], jsii.get(self, "variables"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultArtifacts")
    def default_artifacts(self) -> typing.Optional[Artifacts]:
        '''(experimental) Default list of files and directories that should be attached to the job if it succeeds.

        Artifacts are sent to Gitlab where they can be downloaded.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[Artifacts], jsii.get(self, "defaultArtifacts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultCache")
    def default_cache(self) -> typing.Optional[Cache]:
        '''(experimental) A default list of files and directories to cache between jobs.

        You can only use paths that are in the local working copy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[Cache], jsii.get(self, "defaultCache"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultImage")
    def default_image(self) -> typing.Optional["Image"]:
        '''(experimental) Specifies the default docker image to use globally for all jobs.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["Image"], jsii.get(self, "defaultImage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultInterruptible")
    def default_interruptible(self) -> typing.Optional[builtins.bool]:
        '''(experimental) The default behavior for whether a job should be canceled when a newer pipeline starts before the job completes (Default: false).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "defaultInterruptible"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultRetry")
    def default_retry(self) -> typing.Optional["Retry"]:
        '''(experimental) How many times a job is retried if it fails.

        If not defined, defaults to 0 and jobs do not retry.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["Retry"], jsii.get(self, "defaultRetry"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTimeout")
    def default_timeout(self) -> typing.Optional[builtins.str]:
        '''(experimental) A default timeout job written in natural language (Ex.

        one hour, 3600 seconds, 60 minutes).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultTimeout"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pages")
    def pages(self) -> typing.Optional["Job"]:
        '''(experimental) A special job used to upload static sites to Gitlab pages.

        Requires a ``public/`` directory
        with ``artifacts.path`` pointing to it.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["Job"], jsii.get(self, "pages"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflow")
    def workflow(self) -> typing.Optional["Workflow"]:
        '''(experimental) Used to control pipeline behavior.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["Workflow"], jsii.get(self, "workflow"))


@jsii.data_type(
    jsii_type="projen.gitlab.CiConfigurationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "default": "default",
        "jobs": "jobs",
        "pages": "pages",
        "stages": "stages",
        "variables": "variables",
        "workflow": "workflow",
    },
)
class CiConfigurationOptions:
    def __init__(
        self,
        *,
        default: typing.Optional["Default"] = None,
        jobs: typing.Optional[typing.Mapping[builtins.str, "Job"]] = None,
        pages: typing.Optional["Job"] = None,
        stages: typing.Optional[typing.Sequence[builtins.str]] = None,
        variables: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow: typing.Optional["Workflow"] = None,
    ) -> None:
        '''(experimental) Options for ``CiConfiguration``.

        :param default: (experimental) Default settings for the CI Configuration. Jobs that do not define one or more of the listed keywords use the value defined in the default section.
        :param jobs: (experimental) An initial set of jobs to add to the configuration.
        :param pages: (experimental) A special job used to upload static sites to Gitlab pages. Requires a ``public/`` directory with ``artifacts.path`` pointing to it.
        :param stages: (experimental) Groups jobs into stages. All jobs in one stage must complete before next stage is executed. If no stages are specified. Defaults to ['build', 'test', 'deploy'].
        :param variables: (experimental) Global variables that are passed to jobs. If the job already has that variable defined, the job-level variable takes precedence.
        :param workflow: (experimental) Used to control pipeline behavior.

        :stability: experimental
        '''
        if isinstance(default, dict):
            default = Default(**default)
        if isinstance(pages, dict):
            pages = Job(**pages)
        if isinstance(workflow, dict):
            workflow = Workflow(**workflow)
        self._values: typing.Dict[str, typing.Any] = {}
        if default is not None:
            self._values["default"] = default
        if jobs is not None:
            self._values["jobs"] = jobs
        if pages is not None:
            self._values["pages"] = pages
        if stages is not None:
            self._values["stages"] = stages
        if variables is not None:
            self._values["variables"] = variables
        if workflow is not None:
            self._values["workflow"] = workflow

    @builtins.property
    def default(self) -> typing.Optional["Default"]:
        '''(experimental) Default settings for the CI Configuration.

        Jobs that do not define one or more of the listed keywords use the value defined in the default section.

        :stability: experimental
        '''
        result = self._values.get("default")
        return typing.cast(typing.Optional["Default"], result)

    @builtins.property
    def jobs(self) -> typing.Optional[typing.Mapping[builtins.str, "Job"]]:
        '''(experimental) An initial set of jobs to add to the configuration.

        :stability: experimental
        '''
        result = self._values.get("jobs")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "Job"]], result)

    @builtins.property
    def pages(self) -> typing.Optional["Job"]:
        '''(experimental) A special job used to upload static sites to Gitlab pages.

        Requires a ``public/`` directory
        with ``artifacts.path`` pointing to it.

        :stability: experimental
        '''
        result = self._values.get("pages")
        return typing.cast(typing.Optional["Job"], result)

    @builtins.property
    def stages(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Groups jobs into stages.

        All jobs in one stage must complete before next stage is
        executed. If no stages are specified. Defaults to ['build', 'test', 'deploy'].

        :stability: experimental
        '''
        result = self._values.get("stages")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def variables(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Global variables that are passed to jobs.

        If the job already has that variable defined, the job-level variable takes precedence.

        :stability: experimental
        '''
        result = self._values.get("variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def workflow(self) -> typing.Optional["Workflow"]:
        '''(experimental) Used to control pipeline behavior.

        :stability: experimental
        '''
        result = self._values.get("workflow")
        return typing.cast(typing.Optional["Workflow"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CiConfigurationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Default",
    jsii_struct_bases=[],
    name_mapping={
        "after_script": "afterScript",
        "artifacts": "artifacts",
        "before_script": "beforeScript",
        "cache": "cache",
        "image": "image",
        "interruptible": "interruptible",
        "retry": "retry",
        "services": "services",
        "tags": "tags",
        "timeout": "timeout",
    },
)
class Default:
    def __init__(
        self,
        *,
        after_script: typing.Optional[typing.Sequence[builtins.str]] = None,
        artifacts: typing.Optional[Artifacts] = None,
        before_script: typing.Optional[typing.Sequence[builtins.str]] = None,
        cache: typing.Optional[Cache] = None,
        image: typing.Optional["Image"] = None,
        interruptible: typing.Optional[builtins.bool] = None,
        retry: typing.Optional["Retry"] = None,
        services: typing.Optional[typing.Sequence["Service"]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Default settings for the CI Configuration.

        Jobs that do not define one or more of the listed keywords use the value defined in the default section.

        :param after_script: 
        :param artifacts: 
        :param before_script: 
        :param cache: 
        :param image: 
        :param interruptible: 
        :param retry: 
        :param services: 
        :param tags: 
        :param timeout: 

        :see: https://docs.gitlab.com/ee/ci/yaml/#default
        :stability: experimental
        '''
        if isinstance(artifacts, dict):
            artifacts = Artifacts(**artifacts)
        if isinstance(cache, dict):
            cache = Cache(**cache)
        if isinstance(image, dict):
            image = Image(**image)
        if isinstance(retry, dict):
            retry = Retry(**retry)
        self._values: typing.Dict[str, typing.Any] = {}
        if after_script is not None:
            self._values["after_script"] = after_script
        if artifacts is not None:
            self._values["artifacts"] = artifacts
        if before_script is not None:
            self._values["before_script"] = before_script
        if cache is not None:
            self._values["cache"] = cache
        if image is not None:
            self._values["image"] = image
        if interruptible is not None:
            self._values["interruptible"] = interruptible
        if retry is not None:
            self._values["retry"] = retry
        if services is not None:
            self._values["services"] = services
        if tags is not None:
            self._values["tags"] = tags
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def after_script(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("after_script")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def artifacts(self) -> typing.Optional[Artifacts]:
        '''
        :stability: experimental
        '''
        result = self._values.get("artifacts")
        return typing.cast(typing.Optional[Artifacts], result)

    @builtins.property
    def before_script(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("before_script")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cache(self) -> typing.Optional[Cache]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cache")
        return typing.cast(typing.Optional[Cache], result)

    @builtins.property
    def image(self) -> typing.Optional["Image"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional["Image"], result)

    @builtins.property
    def interruptible(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("interruptible")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def retry(self) -> typing.Optional["Retry"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("retry")
        return typing.cast(typing.Optional["Retry"], result)

    @builtins.property
    def services(self) -> typing.Optional[typing.List["Service"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("services")
        return typing.cast(typing.Optional[typing.List["Service"]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Default(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.gitlab.DefaultElement")
class DefaultElement(enum.Enum):
    '''
    :stability: experimental
    '''

    AFTER_SCRIPT = "AFTER_SCRIPT"
    '''
    :stability: experimental
    '''
    ARTIFACTS = "ARTIFACTS"
    '''
    :stability: experimental
    '''
    BEFORE_SCRIPT = "BEFORE_SCRIPT"
    '''
    :stability: experimental
    '''
    CACHE = "CACHE"
    '''
    :stability: experimental
    '''
    IMAGE = "IMAGE"
    '''
    :stability: experimental
    '''
    INTERRUPTIBLE = "INTERRUPTIBLE"
    '''
    :stability: experimental
    '''
    RETRY = "RETRY"
    '''
    :stability: experimental
    '''
    SERVICES = "SERVICES"
    '''
    :stability: experimental
    '''
    TAGS = "TAGS"
    '''
    :stability: experimental
    '''
    TIMEOUT = "TIMEOUT"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="projen.gitlab.DeploymentTier")
class DeploymentTier(enum.Enum):
    '''(experimental) Explicitly specifies the tier of the deployment environment if non-standard environment name is used.

    :stability: experimental
    '''

    DEVELOPMENT = "DEVELOPMENT"
    '''
    :stability: experimental
    '''
    OTHER = "OTHER"
    '''
    :stability: experimental
    '''
    PRODUCTION = "PRODUCTION"
    '''
    :stability: experimental
    '''
    STAGING = "STAGING"
    '''
    :stability: experimental
    '''
    TESTING = "TESTING"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="projen.gitlab.Engine",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "path": "path"},
)
class Engine:
    def __init__(self, *, name: builtins.str, path: builtins.str) -> None:
        '''(experimental) The engine configuration for a secret.

        :param name: (experimental) Name of the secrets engine.
        :param path: (experimental) Path to the secrets engine.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "path": path,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Name of the secrets engine.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) Path to the secrets engine.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Engine(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Environment",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "action": "action",
        "auto_stop_in": "autoStopIn",
        "deployment_tier": "deploymentTier",
        "kubernetes": "kubernetes",
        "on_stop": "onStop",
        "url": "url",
    },
)
class Environment:
    def __init__(
        self,
        *,
        name: builtins.str,
        action: typing.Optional[Action] = None,
        auto_stop_in: typing.Optional[builtins.str] = None,
        deployment_tier: typing.Optional[DeploymentTier] = None,
        kubernetes: typing.Optional["KubernetesConfig"] = None,
        on_stop: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The environment that a job deploys to.

        :param name: (experimental) The name of the environment, e.g. 'qa', 'staging', 'production'.
        :param action: (experimental) Specifies what this job will do. 'start' (default) indicates the job will start the deployment. 'prepare' indicates this will not affect the deployment. 'stop' indicates this will stop the deployment.
        :param auto_stop_in: (experimental) The amount of time it should take before Gitlab will automatically stop the environment. Supports a wide variety of formats, e.g. '1 week', '3 mins 4 sec', '2 hrs 20 min', '2h20min', '6 mos 1 day', '47 yrs 6 mos and 4d', '3 weeks and 2 days'.
        :param deployment_tier: (experimental) Explicitly specifies the tier of the deployment environment if non-standard environment name is used.
        :param kubernetes: (experimental) Used to configure the kubernetes deployment for this environment. This is currently not supported for kubernetes clusters that are managed by Gitlab.
        :param on_stop: (experimental) The name of a job to execute when the environment is about to be stopped.
        :param url: (experimental) When set, this will expose buttons in various places for the current environment in Gitlab, that will take you to the defined URL.

        :stability: experimental
        '''
        if isinstance(kubernetes, dict):
            kubernetes = KubernetesConfig(**kubernetes)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if action is not None:
            self._values["action"] = action
        if auto_stop_in is not None:
            self._values["auto_stop_in"] = auto_stop_in
        if deployment_tier is not None:
            self._values["deployment_tier"] = deployment_tier
        if kubernetes is not None:
            self._values["kubernetes"] = kubernetes
        if on_stop is not None:
            self._values["on_stop"] = on_stop
        if url is not None:
            self._values["url"] = url

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the environment, e.g. 'qa', 'staging', 'production'.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action(self) -> typing.Optional[Action]:
        '''(experimental) Specifies what this job will do.

        'start' (default) indicates the job will start the deployment. 'prepare' indicates this will not affect the deployment. 'stop' indicates this will stop the deployment.

        :stability: experimental
        '''
        result = self._values.get("action")
        return typing.cast(typing.Optional[Action], result)

    @builtins.property
    def auto_stop_in(self) -> typing.Optional[builtins.str]:
        '''(experimental) The amount of time it should take before Gitlab will automatically stop the environment.

        Supports a wide variety of formats, e.g. '1 week', '3 mins 4 sec', '2 hrs 20 min', '2h20min', '6 mos 1 day', '47 yrs 6 mos and 4d', '3 weeks and 2 days'.

        :stability: experimental
        '''
        result = self._values.get("auto_stop_in")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment_tier(self) -> typing.Optional[DeploymentTier]:
        '''(experimental) Explicitly specifies the tier of the deployment environment if non-standard environment name is used.

        :stability: experimental
        '''
        result = self._values.get("deployment_tier")
        return typing.cast(typing.Optional[DeploymentTier], result)

    @builtins.property
    def kubernetes(self) -> typing.Optional["KubernetesConfig"]:
        '''(experimental) Used to configure the kubernetes deployment for this environment.

        This is currently not supported for kubernetes clusters that are managed by Gitlab.

        :stability: experimental
        '''
        result = self._values.get("kubernetes")
        return typing.cast(typing.Optional["KubernetesConfig"], result)

    @builtins.property
    def on_stop(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of a job to execute when the environment is about to be stopped.

        :stability: experimental
        '''
        result = self._values.get("on_stop")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''(experimental) When set, this will expose buttons in various places for the current environment in Gitlab, that will take you to the defined URL.

        :stability: experimental
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Environment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Filter",
    jsii_struct_bases=[],
    name_mapping={
        "changes": "changes",
        "kubernetes": "kubernetes",
        "refs": "refs",
        "variables": "variables",
    },
)
class Filter:
    def __init__(
        self,
        *,
        changes: typing.Optional[typing.Sequence[builtins.str]] = None,
        kubernetes: typing.Optional["KubernetesEnum"] = None,
        refs: typing.Optional[typing.Sequence[builtins.str]] = None,
        variables: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Filtering options for when a job will run.

        :param changes: (experimental) Filter job creation based on files that were modified in a git push.
        :param kubernetes: (experimental) Filter job based on if Kubernetes integration is active.
        :param refs: (experimental) Control when to add jobs to a pipeline based on branch names or pipeline types.
        :param variables: (experimental) Filter job by checking comparing values of environment variables. Read more about variable expressions: https://docs.gitlab.com/ee/ci/variables/README.html#variables-expressions

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if changes is not None:
            self._values["changes"] = changes
        if kubernetes is not None:
            self._values["kubernetes"] = kubernetes
        if refs is not None:
            self._values["refs"] = refs
        if variables is not None:
            self._values["variables"] = variables

    @builtins.property
    def changes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Filter job creation based on files that were modified in a git push.

        :stability: experimental
        '''
        result = self._values.get("changes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def kubernetes(self) -> typing.Optional["KubernetesEnum"]:
        '''(experimental) Filter job based on if Kubernetes integration is active.

        :stability: experimental
        '''
        result = self._values.get("kubernetes")
        return typing.cast(typing.Optional["KubernetesEnum"], result)

    @builtins.property
    def refs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Control when to add jobs to a pipeline based on branch names or pipeline types.

        :stability: experimental
        '''
        result = self._values.get("refs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def variables(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Filter job by checking comparing values of environment variables.

        Read more about variable expressions: https://docs.gitlab.com/ee/ci/variables/README.html#variables-expressions

        :stability: experimental
        '''
        result = self._values.get("variables")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Filter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GitlabConfiguration(
    CiConfiguration,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.gitlab.GitlabConfiguration",
):
    '''(experimental) A GitLab CI for the main ``.gitlab-ci.yml`` file.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        default: typing.Optional[Default] = None,
        jobs: typing.Optional[typing.Mapping[builtins.str, "Job"]] = None,
        pages: typing.Optional["Job"] = None,
        stages: typing.Optional[typing.Sequence[builtins.str]] = None,
        variables: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow: typing.Optional["Workflow"] = None,
    ) -> None:
        '''
        :param project: -
        :param default: (experimental) Default settings for the CI Configuration. Jobs that do not define one or more of the listed keywords use the value defined in the default section.
        :param jobs: (experimental) An initial set of jobs to add to the configuration.
        :param pages: (experimental) A special job used to upload static sites to Gitlab pages. Requires a ``public/`` directory with ``artifacts.path`` pointing to it.
        :param stages: (experimental) Groups jobs into stages. All jobs in one stage must complete before next stage is executed. If no stages are specified. Defaults to ['build', 'test', 'deploy'].
        :param variables: (experimental) Global variables that are passed to jobs. If the job already has that variable defined, the job-level variable takes precedence.
        :param workflow: (experimental) Used to control pipeline behavior.

        :stability: experimental
        '''
        options = CiConfigurationOptions(
            default=default,
            jobs=jobs,
            pages=pages,
            stages=stages,
            variables=variables,
            workflow=workflow,
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="createNestedTemplates")
    def create_nested_templates(
        self,
        config: typing.Mapping[builtins.str, CiConfigurationOptions],
    ) -> None:
        '''(experimental) Creates and adds nested templates to the includes of the main CI.

        Additionally adds their stages to the main CI if they are not already present.
        You can futher customize nested templates through the ``nestedTemplates`` property.
        E.g. gitlabConfig.nestedTemplates['templateName']?.addStages('stageName')

        :param config: a record the names and configuraitons of the templates.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "createNestedTemplates", [config]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nestedTemplates")
    def nested_templates(self) -> typing.Mapping[builtins.str, "NestedConfiguration"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, "NestedConfiguration"], jsii.get(self, "nestedTemplates"))


@jsii.data_type(
    jsii_type="projen.gitlab.Image",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "entrypoint": "entrypoint"},
)
class Image:
    def __init__(
        self,
        *,
        name: builtins.str,
        entrypoint: typing.Optional[typing.Sequence[typing.Any]] = None,
    ) -> None:
        '''(experimental) Specifies the docker image to use for the job or globally for all jobs.

        Job configuration
        takes precedence over global setting. Requires a certain kind of Gitlab runner executor.

        :param name: (experimental) Full name of the image that should be used. It should contain the Registry part if needed.
        :param entrypoint: (experimental) Command or script that should be executed as the container's entrypoint. It will be translated to Docker's --entrypoint option while creating the container. The syntax is similar to Dockerfile's ENTRYPOINT directive, where each shell token is a separate string in the array.

        :see: https://docs.gitlab.com/ee/ci/yaml/#image
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Full name of the image that should be used.

        It should contain the Registry part if needed.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[typing.List[typing.Any]]:
        '''(experimental) Command or script that should be executed as the container's entrypoint.

        It will be translated to Docker's --entrypoint option while creating the container. The syntax is similar to Dockerfile's ENTRYPOINT directive, where each shell token is a separate string in the array.

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[typing.List[typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Image(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Include",
    jsii_struct_bases=[],
    name_mapping={
        "file": "file",
        "local": "local",
        "project": "project",
        "ref": "ref",
        "remote": "remote",
        "rules": "rules",
        "template": "template",
    },
)
class Include:
    def __init__(
        self,
        *,
        file: typing.Optional[typing.Sequence[builtins.str]] = None,
        local: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        ref: typing.Optional[builtins.str] = None,
        remote: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Sequence["IncludeRule"]] = None,
        template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) An included YAML file.

        :param file: (experimental) Files from another private project on the same GitLab instance. You can use ``file`` in combination with ``project`` only.
        :param local: (experimental) Relative path from local repository root (``/``) to the ``yaml``/``yml`` file template. The file must be on the same branch, and does not work across git submodules.
        :param project: (experimental) Path to the project, e.g. ``group/project``, or ``group/sub-group/project``.
        :param ref: (experimental) Branch/Tag/Commit-hash for the target project.
        :param remote: (experimental) URL to a ``yaml``/``yml`` template file using HTTP/HTTPS.
        :param rules: (experimental) Rules allows for an array of individual rule objects to be evaluated in order, until one matches and dynamically provides attributes to the job.
        :param template: (experimental) Use a ``.gitlab-ci.yml`` template as a base, e.g. ``Nodejs.gitlab-ci.yml``.

        :see: https://docs.gitlab.com/ee/ci/yaml/#include
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if file is not None:
            self._values["file"] = file
        if local is not None:
            self._values["local"] = local
        if project is not None:
            self._values["project"] = project
        if ref is not None:
            self._values["ref"] = ref
        if remote is not None:
            self._values["remote"] = remote
        if rules is not None:
            self._values["rules"] = rules
        if template is not None:
            self._values["template"] = template

    @builtins.property
    def file(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Files from another private project on the same GitLab instance.

        You can use ``file`` in combination with ``project`` only.

        :stability: experimental
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def local(self) -> typing.Optional[builtins.str]:
        '''(experimental) Relative path from local repository root (``/``) to the ``yaml``/``yml`` file template.

        The file must be on the same branch, and does not work across git submodules.

        :stability: experimental
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path to the project, e.g. ``group/project``, or ``group/sub-group/project``.

        :stability: experimental
        '''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ref(self) -> typing.Optional[builtins.str]:
        '''(experimental) Branch/Tag/Commit-hash for the target project.

        :stability: experimental
        '''
        result = self._values.get("ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote(self) -> typing.Optional[builtins.str]:
        '''(experimental) URL to a ``yaml``/``yml`` template file using HTTP/HTTPS.

        :stability: experimental
        '''
        result = self._values.get("remote")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rules(self) -> typing.Optional[typing.List["IncludeRule"]]:
        '''(experimental) Rules allows for an array of individual rule objects to be evaluated in order, until one matches and dynamically provides attributes to the job.

        :stability: experimental
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List["IncludeRule"]], result)

    @builtins.property
    def template(self) -> typing.Optional[builtins.str]:
        '''(experimental) Use a ``.gitlab-ci.yml`` template as a base, e.g. ``Nodejs.gitlab-ci.yml``.

        :stability: experimental
        '''
        result = self._values.get("template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Include(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.IncludeRule",
    jsii_struct_bases=[],
    name_mapping={
        "allow_failure": "allowFailure",
        "changes": "changes",
        "exists": "exists",
        "if_": "if",
        "start_in": "startIn",
        "variables": "variables",
        "when": "when",
    },
)
class IncludeRule:
    def __init__(
        self,
        *,
        allow_failure: typing.Optional[typing.Union[builtins.bool, AllowFailure]] = None,
        changes: typing.Optional[typing.Sequence[builtins.str]] = None,
        exists: typing.Optional[typing.Sequence[builtins.str]] = None,
        if_: typing.Optional[builtins.str] = None,
        start_in: typing.Optional[builtins.str] = None,
        variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number]]] = None,
        when: typing.Optional["JobWhen"] = None,
    ) -> None:
        '''(experimental) Rules allows for an array of individual rule objects to be evaluated in order, until one matches and dynamically provides attributes to the job.

        :param allow_failure: 
        :param changes: 
        :param exists: 
        :param if_: 
        :param start_in: 
        :param variables: 
        :param when: 

        :see: https://docs.gitlab.com/ee/ci/yaml/includes.html#use-rules-with-include
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if allow_failure is not None:
            self._values["allow_failure"] = allow_failure
        if changes is not None:
            self._values["changes"] = changes
        if exists is not None:
            self._values["exists"] = exists
        if if_ is not None:
            self._values["if_"] = if_
        if start_in is not None:
            self._values["start_in"] = start_in
        if variables is not None:
            self._values["variables"] = variables
        if when is not None:
            self._values["when"] = when

    @builtins.property
    def allow_failure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, AllowFailure]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("allow_failure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, AllowFailure]], result)

    @builtins.property
    def changes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("changes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def exists(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("exists")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def if_(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("if_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_in(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("start_in")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number]]], result)

    @builtins.property
    def when(self) -> typing.Optional["JobWhen"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("when")
        return typing.cast(typing.Optional["JobWhen"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IncludeRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Inherit",
    jsii_struct_bases=[],
    name_mapping={"default": "default", "variables": "variables"},
)
class Inherit:
    def __init__(
        self,
        *,
        default: typing.Optional[typing.Union[builtins.bool, typing.Sequence[DefaultElement]]] = None,
        variables: typing.Optional[typing.Union[builtins.bool, typing.Sequence[builtins.str]]] = None,
    ) -> None:
        '''(experimental) Controls inheritance of globally-defined defaults and variables.

        Boolean values control
        inheritance of all default: or variables: keywords. To inherit only a subset of default:
        or variables: keywords, specify what you wish to inherit. Anything not listed is not
        inherited.

        :param default: (experimental) Whether to inherit all globally-defined defaults or not. Or subset of inherited defaults
        :param variables: (experimental) Whether to inherit all globally-defined variables or not. Or subset of inherited variables

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if default is not None:
            self._values["default"] = default
        if variables is not None:
            self._values["variables"] = variables

    @builtins.property
    def default(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, typing.List[DefaultElement]]]:
        '''(experimental) Whether to inherit all globally-defined defaults or not.

        Or subset of inherited defaults

        :stability: experimental
        '''
        result = self._values.get("default")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, typing.List[DefaultElement]]], result)

    @builtins.property
    def variables(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, typing.List[builtins.str]]]:
        '''(experimental) Whether to inherit all globally-defined variables or not.

        Or subset of inherited variables

        :stability: experimental
        '''
        result = self._values.get("variables")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, typing.List[builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Inherit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Job",
    jsii_struct_bases=[],
    name_mapping={
        "after_script": "afterScript",
        "allow_failure": "allowFailure",
        "artifacts": "artifacts",
        "before_script": "beforeScript",
        "cache": "cache",
        "coverage": "coverage",
        "dependencies": "dependencies",
        "environment": "environment",
        "except_": "except",
        "extends": "extends",
        "image": "image",
        "inherit": "inherit",
        "interruptible": "interruptible",
        "needs": "needs",
        "only": "only",
        "parallel": "parallel",
        "release": "release",
        "resource_group": "resourceGroup",
        "retry": "retry",
        "rules": "rules",
        "script": "script",
        "secrets": "secrets",
        "services": "services",
        "stage": "stage",
        "start_in": "startIn",
        "tags": "tags",
        "timeout": "timeout",
        "trigger": "trigger",
        "variables": "variables",
        "when": "when",
    },
)
class Job:
    def __init__(
        self,
        *,
        after_script: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_failure: typing.Optional[typing.Union[builtins.bool, AllowFailure]] = None,
        artifacts: typing.Optional[Artifacts] = None,
        before_script: typing.Optional[typing.Sequence[builtins.str]] = None,
        cache: typing.Optional[Cache] = None,
        coverage: typing.Optional[builtins.str] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        environment: typing.Optional[typing.Union[builtins.str, Environment]] = None,
        except_: typing.Optional[typing.Union[Filter, typing.Sequence[builtins.str]]] = None,
        extends: typing.Optional[typing.Sequence[builtins.str]] = None,
        image: typing.Optional[Image] = None,
        inherit: typing.Optional[Inherit] = None,
        interruptible: typing.Optional[builtins.bool] = None,
        needs: typing.Optional[typing.Sequence[typing.Union[builtins.str, "Need"]]] = None,
        only: typing.Optional[typing.Union[Filter, typing.Sequence[builtins.str]]] = None,
        parallel: typing.Optional[typing.Union[jsii.Number, "Parallel"]] = None,
        release: typing.Optional["Release"] = None,
        resource_group: typing.Optional[builtins.str] = None,
        retry: typing.Optional["Retry"] = None,
        rules: typing.Optional[typing.Sequence[IncludeRule]] = None,
        script: typing.Optional[typing.Sequence[builtins.str]] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, "Secret"]]] = None,
        services: typing.Optional[typing.Sequence["Service"]] = None,
        stage: typing.Optional[builtins.str] = None,
        start_in: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        timeout: typing.Optional[builtins.str] = None,
        trigger: typing.Optional[typing.Union[builtins.str, "Trigger"]] = None,
        variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number]]] = None,
        when: typing.Optional["JobWhen"] = None,
    ) -> None:
        '''(experimental) Jobs are the most fundamental element of a .gitlab-ci.yml file.

        :param after_script: 
        :param allow_failure: (experimental) Whether to allow the pipeline to continue running on job failure (Default: false).
        :param artifacts: 
        :param before_script: 
        :param cache: 
        :param coverage: (experimental) Must be a regular expression, optionally but recommended to be quoted, and must be surrounded with '/'. Example: '/Code coverage: \\d+.\\d+/'
        :param dependencies: (experimental) Specify a list of job names from earlier stages from which artifacts should be loaded. By default, all previous artifacts are passed. Use an empty array to skip downloading artifacts.
        :param environment: (experimental) Used to associate environment metadata with a deploy. Environment can have a name and URL attached to it, and will be displayed under /environments under the project.
        :param except_: (experimental) Job will run *except* for when these filtering options match.
        :param extends: (experimental) The name of one or more jobs to inherit configuration from.
        :param image: 
        :param inherit: (experimental) Controls inheritance of globally-defined defaults and variables. Boolean values control inheritance of all default: or variables: keywords. To inherit only a subset of default: or variables: keywords, specify what you wish to inherit. Anything not listed is not inherited.
        :param interruptible: 
        :param needs: (experimental) The list of jobs in previous stages whose sole completion is needed to start the current job.
        :param only: (experimental) Job will run *only* when these filtering options match.
        :param parallel: (experimental) Parallel will split up a single job into several, and provide ``CI_NODE_INDEX`` and ``CI_NODE_TOTAL`` environment variables for the running jobs.
        :param release: (experimental) Indicates that the job creates a Release.
        :param resource_group: (experimental) Limit job concurrency. Can be used to ensure that the Runner will not run certain jobs simultaneously.
        :param retry: 
        :param rules: (experimental) Rules allows for an array of individual rule objects to be evaluated in order, until one matches and dynamically provides attributes to the job.
        :param script: (experimental) Shell scripts executed by the Runner. The only required property of jobs. Be careful with special characters (e.g. ``:``, ``{``, ``}``, ``&``) and use single or double quotes to avoid issues.
        :param secrets: (experimental) CI/CD secrets.
        :param services: 
        :param stage: (experimental) Define what stage the job will run in.
        :param start_in: 
        :param tags: 
        :param timeout: 
        :param trigger: (experimental) Trigger allows you to define downstream pipeline trigger. When a job created from trigger definition is started by GitLab, a downstream pipeline gets created. Read more: https://docs.gitlab.com/ee/ci/yaml/README.html#trigger
        :param variables: (experimental) Configurable values that are passed to the Job.
        :param when: (experimental) Describes the conditions for when to run the job. Defaults to 'on_success'.

        :see: https://docs.gitlab.com/ee/ci/jobs/
        :stability: experimental
        '''
        if isinstance(artifacts, dict):
            artifacts = Artifacts(**artifacts)
        if isinstance(cache, dict):
            cache = Cache(**cache)
        if isinstance(image, dict):
            image = Image(**image)
        if isinstance(inherit, dict):
            inherit = Inherit(**inherit)
        if isinstance(release, dict):
            release = Release(**release)
        if isinstance(retry, dict):
            retry = Retry(**retry)
        self._values: typing.Dict[str, typing.Any] = {}
        if after_script is not None:
            self._values["after_script"] = after_script
        if allow_failure is not None:
            self._values["allow_failure"] = allow_failure
        if artifacts is not None:
            self._values["artifacts"] = artifacts
        if before_script is not None:
            self._values["before_script"] = before_script
        if cache is not None:
            self._values["cache"] = cache
        if coverage is not None:
            self._values["coverage"] = coverage
        if dependencies is not None:
            self._values["dependencies"] = dependencies
        if environment is not None:
            self._values["environment"] = environment
        if except_ is not None:
            self._values["except_"] = except_
        if extends is not None:
            self._values["extends"] = extends
        if image is not None:
            self._values["image"] = image
        if inherit is not None:
            self._values["inherit"] = inherit
        if interruptible is not None:
            self._values["interruptible"] = interruptible
        if needs is not None:
            self._values["needs"] = needs
        if only is not None:
            self._values["only"] = only
        if parallel is not None:
            self._values["parallel"] = parallel
        if release is not None:
            self._values["release"] = release
        if resource_group is not None:
            self._values["resource_group"] = resource_group
        if retry is not None:
            self._values["retry"] = retry
        if rules is not None:
            self._values["rules"] = rules
        if script is not None:
            self._values["script"] = script
        if secrets is not None:
            self._values["secrets"] = secrets
        if services is not None:
            self._values["services"] = services
        if stage is not None:
            self._values["stage"] = stage
        if start_in is not None:
            self._values["start_in"] = start_in
        if tags is not None:
            self._values["tags"] = tags
        if timeout is not None:
            self._values["timeout"] = timeout
        if trigger is not None:
            self._values["trigger"] = trigger
        if variables is not None:
            self._values["variables"] = variables
        if when is not None:
            self._values["when"] = when

    @builtins.property
    def after_script(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("after_script")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allow_failure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, AllowFailure]]:
        '''(experimental) Whether to allow the pipeline to continue running on job failure (Default: false).

        :stability: experimental
        '''
        result = self._values.get("allow_failure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, AllowFailure]], result)

    @builtins.property
    def artifacts(self) -> typing.Optional[Artifacts]:
        '''
        :stability: experimental
        '''
        result = self._values.get("artifacts")
        return typing.cast(typing.Optional[Artifacts], result)

    @builtins.property
    def before_script(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("before_script")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cache(self) -> typing.Optional[Cache]:
        '''
        :stability: experimental
        '''
        result = self._values.get("cache")
        return typing.cast(typing.Optional[Cache], result)

    @builtins.property
    def coverage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Must be a regular expression, optionally but recommended to be quoted, and must be surrounded with '/'.

        Example: '/Code coverage: \\d+.\\d+/'

        :stability: experimental
        '''
        result = self._values.get("coverage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Specify a list of job names from earlier stages from which artifacts should be loaded.

        By default, all previous artifacts are passed. Use an empty array to skip downloading artifacts.

        :stability: experimental
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def environment(self) -> typing.Optional[typing.Union[builtins.str, Environment]]:
        '''(experimental) Used to associate environment metadata with a deploy.

        Environment can have a name and URL attached to it, and will be displayed under /environments under the project.

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Union[builtins.str, Environment]], result)

    @builtins.property
    def except_(
        self,
    ) -> typing.Optional[typing.Union[Filter, typing.List[builtins.str]]]:
        '''(experimental) Job will run *except* for when these filtering options match.

        :stability: experimental
        '''
        result = self._values.get("except_")
        return typing.cast(typing.Optional[typing.Union[Filter, typing.List[builtins.str]]], result)

    @builtins.property
    def extends(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The name of one or more jobs to inherit configuration from.

        :stability: experimental
        '''
        result = self._values.get("extends")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def image(self) -> typing.Optional[Image]:
        '''
        :stability: experimental
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[Image], result)

    @builtins.property
    def inherit(self) -> typing.Optional[Inherit]:
        '''(experimental) Controls inheritance of globally-defined defaults and variables.

        Boolean values control inheritance of all default: or variables: keywords. To inherit only a subset of default: or variables: keywords, specify what you wish to inherit. Anything not listed is not inherited.

        :stability: experimental
        '''
        result = self._values.get("inherit")
        return typing.cast(typing.Optional[Inherit], result)

    @builtins.property
    def interruptible(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("interruptible")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def needs(self) -> typing.Optional[typing.List[typing.Union[builtins.str, "Need"]]]:
        '''(experimental) The list of jobs in previous stages whose sole completion is needed to start the current job.

        :stability: experimental
        '''
        result = self._values.get("needs")
        return typing.cast(typing.Optional[typing.List[typing.Union[builtins.str, "Need"]]], result)

    @builtins.property
    def only(self) -> typing.Optional[typing.Union[Filter, typing.List[builtins.str]]]:
        '''(experimental) Job will run *only* when these filtering options match.

        :stability: experimental
        '''
        result = self._values.get("only")
        return typing.cast(typing.Optional[typing.Union[Filter, typing.List[builtins.str]]], result)

    @builtins.property
    def parallel(self) -> typing.Optional[typing.Union[jsii.Number, "Parallel"]]:
        '''(experimental) Parallel will split up a single job into several, and provide ``CI_NODE_INDEX`` and ``CI_NODE_TOTAL`` environment variables for the running jobs.

        :stability: experimental
        '''
        result = self._values.get("parallel")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, "Parallel"]], result)

    @builtins.property
    def release(self) -> typing.Optional["Release"]:
        '''(experimental) Indicates that the job creates a Release.

        :stability: experimental
        '''
        result = self._values.get("release")
        return typing.cast(typing.Optional["Release"], result)

    @builtins.property
    def resource_group(self) -> typing.Optional[builtins.str]:
        '''(experimental) Limit job concurrency.

        Can be used to ensure that the Runner will not run certain jobs simultaneously.

        :stability: experimental
        '''
        result = self._values.get("resource_group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retry(self) -> typing.Optional["Retry"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("retry")
        return typing.cast(typing.Optional["Retry"], result)

    @builtins.property
    def rules(self) -> typing.Optional[typing.List[IncludeRule]]:
        '''(experimental) Rules allows for an array of individual rule objects to be evaluated in order, until one matches and dynamically provides attributes to the job.

        :stability: experimental
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List[IncludeRule]], result)

    @builtins.property
    def script(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Shell scripts executed by the Runner.

        The only required property of jobs. Be careful with special characters (e.g. ``:``, ``{``, ``}``, ``&``) and use single or double quotes to avoid issues.

        :stability: experimental
        '''
        result = self._values.get("script")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, "Secret"]]]:
        '''(experimental) CI/CD secrets.

        :stability: experimental
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Mapping[builtins.str, "Secret"]]], result)

    @builtins.property
    def services(self) -> typing.Optional[typing.List["Service"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("services")
        return typing.cast(typing.Optional[typing.List["Service"]], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define what stage the job will run in.

        :stability: experimental
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def start_in(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("start_in")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trigger(self) -> typing.Optional[typing.Union[builtins.str, "Trigger"]]:
        '''(experimental) Trigger allows you to define downstream pipeline trigger.

        When a job created from trigger definition is started by GitLab, a downstream pipeline gets created. Read more: https://docs.gitlab.com/ee/ci/yaml/README.html#trigger

        :stability: experimental
        '''
        result = self._values.get("trigger")
        return typing.cast(typing.Optional[typing.Union[builtins.str, "Trigger"]], result)

    @builtins.property
    def variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number]]]:
        '''(experimental) Configurable values that are passed to the Job.

        :stability: experimental
        '''
        result = self._values.get("variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number]]], result)

    @builtins.property
    def when(self) -> typing.Optional["JobWhen"]:
        '''(experimental) Describes the conditions for when to run the job.

        Defaults to 'on_success'.

        :stability: experimental
        '''
        result = self._values.get("when")
        return typing.cast(typing.Optional["JobWhen"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Job(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.gitlab.JobWhen")
class JobWhen(enum.Enum):
    '''(experimental) Describes the conditions for when to run the job.

    Defaults to 'on_success'.

    :see: https://docs.gitlab.com/ee/ci/yaml/#when
    :stability: experimental
    '''

    ALWAYS = "ALWAYS"
    '''
    :stability: experimental
    '''
    DELAYED = "DELAYED"
    '''
    :stability: experimental
    '''
    MANUAL = "MANUAL"
    '''
    :stability: experimental
    '''
    NEVER = "NEVER"
    '''
    :stability: experimental
    '''
    ON_FAILURE = "ON_FAILURE"
    '''
    :stability: experimental
    '''
    ON_SUCCESS = "ON_SUCCESS"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="projen.gitlab.KubernetesConfig",
    jsii_struct_bases=[],
    name_mapping={"namespace": "namespace"},
)
class KubernetesConfig:
    def __init__(self, *, namespace: typing.Optional[builtins.str] = None) -> None:
        '''(experimental) Used to configure the kubernetes deployment for this environment.

        This is currently not
        supported for kubernetes clusters that are managed by Gitlab.

        :param namespace: (experimental) The kubernetes namespace where this environment should be deployed to.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The kubernetes namespace where this environment should be deployed to.

        :stability: experimental
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubernetesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.gitlab.KubernetesEnum")
class KubernetesEnum(enum.Enum):
    '''(experimental) Filter job based on if Kubernetes integration is active.

    :stability: experimental
    '''

    ACTIVE = "ACTIVE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="projen.gitlab.Link",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "url": "url",
        "filepath": "filepath",
        "link_type": "linkType",
    },
)
class Link:
    def __init__(
        self,
        *,
        name: builtins.str,
        url: builtins.str,
        filepath: typing.Optional[builtins.str] = None,
        link_type: typing.Optional["LinkType"] = None,
    ) -> None:
        '''(experimental) Link configuration for an asset.

        :param name: (experimental) The name of the link.
        :param url: (experimental) The URL to download a file.
        :param filepath: (experimental) The redirect link to the url.
        :param link_type: (experimental) The content kind of what users can download via url.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "url": url,
        }
        if filepath is not None:
            self._values["filepath"] = filepath
        if link_type is not None:
            self._values["link_type"] = link_type

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the link.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''(experimental) The URL to download a file.

        :stability: experimental
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filepath(self) -> typing.Optional[builtins.str]:
        '''(experimental) The redirect link to the url.

        :stability: experimental
        '''
        result = self._values.get("filepath")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def link_type(self) -> typing.Optional["LinkType"]:
        '''(experimental) The content kind of what users can download via url.

        :stability: experimental
        '''
        result = self._values.get("link_type")
        return typing.cast(typing.Optional["LinkType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Link(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.gitlab.LinkType")
class LinkType(enum.Enum):
    '''(experimental) The content kind of what users can download via url.

    :stability: experimental
    '''

    IMAGE = "IMAGE"
    '''
    :stability: experimental
    '''
    OTHER = "OTHER"
    '''
    :stability: experimental
    '''
    PACKAGE = "PACKAGE"
    '''
    :stability: experimental
    '''
    RUNBOOK = "RUNBOOK"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="projen.gitlab.Need",
    jsii_struct_bases=[],
    name_mapping={
        "job": "job",
        "artifacts": "artifacts",
        "optional": "optional",
        "pipeline": "pipeline",
        "project": "project",
        "ref": "ref",
    },
)
class Need:
    def __init__(
        self,
        *,
        job: builtins.str,
        artifacts: typing.Optional[builtins.bool] = None,
        optional: typing.Optional[builtins.bool] = None,
        pipeline: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        ref: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) A jobs in a previous stage whose sole completion is needed to start the current job.

        :param job: 
        :param artifacts: 
        :param optional: 
        :param pipeline: 
        :param project: 
        :param ref: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "job": job,
        }
        if artifacts is not None:
            self._values["artifacts"] = artifacts
        if optional is not None:
            self._values["optional"] = optional
        if pipeline is not None:
            self._values["pipeline"] = pipeline
        if project is not None:
            self._values["project"] = project
        if ref is not None:
            self._values["ref"] = ref

    @builtins.property
    def job(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("job")
        assert result is not None, "Required property 'job' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifacts(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("artifacts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def optional(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("optional")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pipeline(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("pipeline")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ref(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("ref")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Need(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NestedConfiguration(
    CiConfiguration,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.gitlab.NestedConfiguration",
):
    '''(experimental) A GitLab CI for templates that are created and included in the ``.gitlab-ci.yml`` file.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        parent: GitlabConfiguration,
        name: builtins.str,
        *,
        default: typing.Optional[Default] = None,
        jobs: typing.Optional[typing.Mapping[builtins.str, Job]] = None,
        pages: typing.Optional[Job] = None,
        stages: typing.Optional[typing.Sequence[builtins.str]] = None,
        variables: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow: typing.Optional["Workflow"] = None,
    ) -> None:
        '''
        :param project: -
        :param parent: -
        :param name: -
        :param default: (experimental) Default settings for the CI Configuration. Jobs that do not define one or more of the listed keywords use the value defined in the default section.
        :param jobs: (experimental) An initial set of jobs to add to the configuration.
        :param pages: (experimental) A special job used to upload static sites to Gitlab pages. Requires a ``public/`` directory with ``artifacts.path`` pointing to it.
        :param stages: (experimental) Groups jobs into stages. All jobs in one stage must complete before next stage is executed. If no stages are specified. Defaults to ['build', 'test', 'deploy'].
        :param variables: (experimental) Global variables that are passed to jobs. If the job already has that variable defined, the job-level variable takes precedence.
        :param workflow: (experimental) Used to control pipeline behavior.

        :stability: experimental
        '''
        options = CiConfigurationOptions(
            default=default,
            jobs=jobs,
            pages=pages,
            stages=stages,
            variables=variables,
            workflow=workflow,
        )

        jsii.create(self.__class__, self, [project, parent, name, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parent")
    def parent(self) -> GitlabConfiguration:
        '''
        :stability: experimental
        '''
        return typing.cast(GitlabConfiguration, jsii.get(self, "parent"))


@jsii.data_type(
    jsii_type="projen.gitlab.Parallel",
    jsii_struct_bases=[],
    name_mapping={"matrix": "matrix"},
)
class Parallel:
    def __init__(
        self,
        *,
        matrix: typing.Sequence[typing.Mapping[builtins.str, typing.Sequence[typing.Any]]],
    ) -> None:
        '''(experimental) Used to run a job multiple times in parallel in a single pipeline.

        :param matrix: (experimental) Defines different variables for jobs that are running in parallel.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "matrix": matrix,
        }

    @builtins.property
    def matrix(
        self,
    ) -> typing.List[typing.Mapping[builtins.str, typing.List[typing.Any]]]:
        '''(experimental) Defines different variables for jobs that are running in parallel.

        :stability: experimental
        '''
        result = self._values.get("matrix")
        assert result is not None, "Required property 'matrix' is missing"
        return typing.cast(typing.List[typing.Mapping[builtins.str, typing.List[typing.Any]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Parallel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Release",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "tag_name": "tagName",
        "assets": "assets",
        "milestones": "milestones",
        "name": "name",
        "ref": "ref",
        "released_at": "releasedAt",
    },
)
class Release:
    def __init__(
        self,
        *,
        description: builtins.str,
        tag_name: builtins.str,
        assets: typing.Optional[Assets] = None,
        milestones: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        ref: typing.Optional[builtins.str] = None,
        released_at: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Indicates that the job creates a Release.

        :param description: (experimental) Specifies the longer description of the Release.
        :param tag_name: (experimental) The tag_name must be specified. It can refer to an existing Git tag or can be specified by the user.
        :param assets: 
        :param milestones: (experimental) The title of each milestone the release is associated with.
        :param name: (experimental) The Release name. If omitted, it is populated with the value of release: tag_name.
        :param ref: (experimental) If the release: tag_name doesn’t exist yet, the release is created from ref. ref can be a commit SHA, another tag name, or a branch name.
        :param released_at: (experimental) The date and time when the release is ready. Defaults to the current date and time if not defined. Should be enclosed in quotes and expressed in ISO 8601 format.

        :stability: experimental
        '''
        if isinstance(assets, dict):
            assets = Assets(**assets)
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "tag_name": tag_name,
        }
        if assets is not None:
            self._values["assets"] = assets
        if milestones is not None:
            self._values["milestones"] = milestones
        if name is not None:
            self._values["name"] = name
        if ref is not None:
            self._values["ref"] = ref
        if released_at is not None:
            self._values["released_at"] = released_at

    @builtins.property
    def description(self) -> builtins.str:
        '''(experimental) Specifies the longer description of the Release.

        :stability: experimental
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tag_name(self) -> builtins.str:
        '''(experimental) The tag_name must be specified.

        It can refer to an existing Git tag or can be specified by the user.

        :stability: experimental
        '''
        result = self._values.get("tag_name")
        assert result is not None, "Required property 'tag_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assets(self) -> typing.Optional[Assets]:
        '''
        :stability: experimental
        '''
        result = self._values.get("assets")
        return typing.cast(typing.Optional[Assets], result)

    @builtins.property
    def milestones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The title of each milestone the release is associated with.

        :stability: experimental
        '''
        result = self._values.get("milestones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Release name.

        If omitted, it is populated with the value of release: tag_name.

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ref(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the release: tag_name doesn’t exist yet, the release is created from ref.

        ref can be a commit SHA, another tag name, or a branch name.

        :stability: experimental
        '''
        result = self._values.get("ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def released_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The date and time when the release is ready.

        Defaults to the current date and time if not defined. Should be enclosed in quotes and expressed in ISO 8601 format.

        :stability: experimental
        '''
        result = self._values.get("released_at")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Release(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Reports",
    jsii_struct_bases=[],
    name_mapping={
        "cobertura": "cobertura",
        "codequality": "codequality",
        "container_scanning": "containerScanning",
        "dast": "dast",
        "dependency_scanning": "dependencyScanning",
        "dotenv": "dotenv",
        "junit": "junit",
        "license_management": "licenseManagement",
        "license_scanning": "licenseScanning",
        "lsif": "lsif",
        "metrics": "metrics",
        "performance": "performance",
        "requirements": "requirements",
        "sast": "sast",
        "secret_detection": "secretDetection",
        "terraform": "terraform",
    },
)
class Reports:
    def __init__(
        self,
        *,
        cobertura: typing.Optional[typing.Sequence[builtins.str]] = None,
        codequality: typing.Optional[typing.Sequence[builtins.str]] = None,
        container_scanning: typing.Optional[typing.Sequence[builtins.str]] = None,
        dast: typing.Optional[typing.Sequence[builtins.str]] = None,
        dependency_scanning: typing.Optional[typing.Sequence[builtins.str]] = None,
        dotenv: typing.Optional[typing.Sequence[builtins.str]] = None,
        junit: typing.Optional[typing.Sequence[builtins.str]] = None,
        license_management: typing.Optional[typing.Sequence[builtins.str]] = None,
        license_scanning: typing.Optional[typing.Sequence[builtins.str]] = None,
        lsif: typing.Optional[typing.Sequence[builtins.str]] = None,
        metrics: typing.Optional[typing.Sequence[builtins.str]] = None,
        performance: typing.Optional[typing.Sequence[builtins.str]] = None,
        requirements: typing.Optional[typing.Sequence[builtins.str]] = None,
        sast: typing.Optional[typing.Sequence[builtins.str]] = None,
        secret_detection: typing.Optional[typing.Sequence[builtins.str]] = None,
        terraform: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Reports will be uploaded as artifacts, and often displayed in the Gitlab UI, such as in Merge Requests.

        :param cobertura: (experimental) Path for file(s) that should be parsed as Cobertura XML coverage report.
        :param codequality: (experimental) Path to file or list of files with code quality report(s) (such as Code Climate).
        :param container_scanning: (experimental) Path to file or list of files with Container scanning vulnerabilities report(s).
        :param dast: (experimental) Path to file or list of files with DAST vulnerabilities report(s).
        :param dependency_scanning: (experimental) Path to file or list of files with Dependency scanning vulnerabilities report(s).
        :param dotenv: (experimental) Path to file or list of files containing runtime-created variables for this job.
        :param junit: (experimental) Path for file(s) that should be parsed as JUnit XML result.
        :param license_management: (experimental) Deprecated in 12.8: Path to file or list of files with license report(s).
        :param license_scanning: (experimental) Path to file or list of files with license report(s).
        :param lsif: (experimental) Path to file or list of files containing code intelligence (Language Server Index Format).
        :param metrics: (experimental) Path to file or list of files with custom metrics report(s).
        :param performance: (experimental) Path to file or list of files with performance metrics report(s).
        :param requirements: (experimental) Path to file or list of files with requirements report(s).
        :param sast: (experimental) Path to file or list of files with SAST vulnerabilities report(s).
        :param secret_detection: (experimental) Path to file or list of files with secret detection report(s).
        :param terraform: (experimental) Path to file or list of files with terraform plan(s).

        :see: https://docs.gitlab.com/ee/ci/yaml/#artifactsreports
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cobertura is not None:
            self._values["cobertura"] = cobertura
        if codequality is not None:
            self._values["codequality"] = codequality
        if container_scanning is not None:
            self._values["container_scanning"] = container_scanning
        if dast is not None:
            self._values["dast"] = dast
        if dependency_scanning is not None:
            self._values["dependency_scanning"] = dependency_scanning
        if dotenv is not None:
            self._values["dotenv"] = dotenv
        if junit is not None:
            self._values["junit"] = junit
        if license_management is not None:
            self._values["license_management"] = license_management
        if license_scanning is not None:
            self._values["license_scanning"] = license_scanning
        if lsif is not None:
            self._values["lsif"] = lsif
        if metrics is not None:
            self._values["metrics"] = metrics
        if performance is not None:
            self._values["performance"] = performance
        if requirements is not None:
            self._values["requirements"] = requirements
        if sast is not None:
            self._values["sast"] = sast
        if secret_detection is not None:
            self._values["secret_detection"] = secret_detection
        if terraform is not None:
            self._values["terraform"] = terraform

    @builtins.property
    def cobertura(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path for file(s) that should be parsed as Cobertura XML coverage report.

        :stability: experimental
        '''
        result = self._values.get("cobertura")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def codequality(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with code quality report(s) (such as Code Climate).

        :stability: experimental
        '''
        result = self._values.get("codequality")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def container_scanning(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with Container scanning vulnerabilities report(s).

        :stability: experimental
        '''
        result = self._values.get("container_scanning")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dast(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with DAST vulnerabilities report(s).

        :stability: experimental
        '''
        result = self._values.get("dast")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dependency_scanning(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with Dependency scanning vulnerabilities report(s).

        :stability: experimental
        '''
        result = self._values.get("dependency_scanning")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dotenv(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files containing runtime-created variables for this job.

        :stability: experimental
        '''
        result = self._values.get("dotenv")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def junit(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path for file(s) that should be parsed as JUnit XML result.

        :stability: experimental
        '''
        result = self._values.get("junit")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license_management(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Deprecated in 12.8: Path to file or list of files with license report(s).

        :stability: experimental
        '''
        result = self._values.get("license_management")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def license_scanning(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with license report(s).

        :stability: experimental
        '''
        result = self._values.get("license_scanning")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def lsif(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files containing code intelligence (Language Server Index Format).

        :stability: experimental
        '''
        result = self._values.get("lsif")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def metrics(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with custom metrics report(s).

        :stability: experimental
        '''
        result = self._values.get("metrics")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def performance(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with performance metrics report(s).

        :stability: experimental
        '''
        result = self._values.get("performance")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def requirements(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with requirements report(s).

        :stability: experimental
        '''
        result = self._values.get("requirements")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sast(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with SAST vulnerabilities report(s).

        :stability: experimental
        '''
        result = self._values.get("sast")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secret_detection(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with secret detection report(s).

        :stability: experimental
        '''
        result = self._values.get("secret_detection")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def terraform(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Path to file or list of files with terraform plan(s).

        :stability: experimental
        '''
        result = self._values.get("terraform")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Reports(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Retry",
    jsii_struct_bases=[],
    name_mapping={"max": "max", "when": "when"},
)
class Retry:
    def __init__(
        self,
        *,
        max: typing.Optional[jsii.Number] = None,
        when: typing.Any = None,
    ) -> None:
        '''(experimental) How many times a job is retried if it fails.

        If not defined, defaults to 0 and jobs do not retry.

        :param max: (experimental) 0 (default), 1, or 2.
        :param when: (experimental) Either a single or array of error types to trigger job retry.

        :see: https://docs.gitlab.com/ee/ci/yaml/#retry
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if max is not None:
            self._values["max"] = max
        if when is not None:
            self._values["when"] = when

    @builtins.property
    def max(self) -> typing.Optional[jsii.Number]:
        '''(experimental) 0 (default), 1, or 2.

        :stability: experimental
        '''
        result = self._values.get("max")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def when(self) -> typing.Any:
        '''(experimental) Either a single or array of error types to trigger job retry.

        :stability: experimental
        '''
        result = self._values.get("when")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Retry(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Secret",
    jsii_struct_bases=[],
    name_mapping={"vault": "vault"},
)
class Secret:
    def __init__(self, *, vault: "VaultConfig") -> None:
        '''(experimental) A CI/CD secret.

        :param vault: 

        :stability: experimental
        '''
        if isinstance(vault, dict):
            vault = VaultConfig(**vault)
        self._values: typing.Dict[str, typing.Any] = {
            "vault": vault,
        }

    @builtins.property
    def vault(self) -> "VaultConfig":
        '''
        :stability: experimental
        '''
        result = self._values.get("vault")
        assert result is not None, "Required property 'vault' is missing"
        return typing.cast("VaultConfig", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Secret(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Service",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "alias": "alias",
        "command": "command",
        "entrypoint": "entrypoint",
    },
)
class Service:
    def __init__(
        self,
        *,
        name: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        entrypoint: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Used to specify an additional Docker image to run scripts in.

        The service image is linked to the image specified in the @Default image keyword.

        :param name: (experimental) Full name of the image that should be used. It should contain the Registry part if needed.
        :param alias: (experimental) Additional alias that can be used to access the service from the job's container. Read Accessing the services for more information.
        :param command: (experimental) Command or script that should be used as the container's command. It will be translated to arguments passed to Docker after the image's name. The syntax is similar to Dockerfile's CMD directive, where each shell token is a separate string in the array.
        :param entrypoint: (experimental) Command or script that should be executed as the container's entrypoint. It will be translated to Docker's --entrypoint option while creating the container. The syntax is similar to Dockerfile's ENTRYPOINT directive, where each shell token is a separate string in the array.

        :see: https://docs.gitlab.com/ee/ci/yaml/#services
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if alias is not None:
            self._values["alias"] = alias
        if command is not None:
            self._values["command"] = command
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Full name of the image that should be used.

        It should contain the Registry part if needed.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''(experimental) Additional alias that can be used to access the service from the job's container.

        Read Accessing the services for more information.

        :stability: experimental
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Command or script that should be used as the container's command.

        It will be translated to arguments passed to Docker after the image's name. The syntax is similar to Dockerfile's CMD directive, where each shell token is a separate string in the array.

        :stability: experimental
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Command or script that should be executed as the container's entrypoint.

        It will be translated to Docker's --entrypoint option while creating the container. The syntax is similar to Dockerfile's ENTRYPOINT directive, where each shell token is a separate string in the array.

        :stability: experimental
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Service(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.gitlab.Strategy")
class Strategy(enum.Enum):
    '''(experimental) You can mirror the pipeline status from the triggered pipeline to the source bridge job by using strategy: depend.

    :see: https://docs.gitlab.com/ee/ci/yaml/#triggerstrategy
    :stability: experimental
    '''

    DEPEND = "DEPEND"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="projen.gitlab.Trigger",
    jsii_struct_bases=[],
    name_mapping={
        "branch": "branch",
        "include": "include",
        "project": "project",
        "strategy": "strategy",
    },
)
class Trigger:
    def __init__(
        self,
        *,
        branch: typing.Optional[builtins.str] = None,
        include: typing.Optional[typing.Sequence["TriggerInclude"]] = None,
        project: typing.Optional[builtins.str] = None,
        strategy: typing.Optional[Strategy] = None,
    ) -> None:
        '''(experimental) Trigger a multi-project or a child pipeline.

        Read more:

        :param branch: (experimental) The branch name that a downstream pipeline will use.
        :param include: (experimental) A list of local files or artifacts from other jobs to define the pipeline.
        :param project: (experimental) Path to the project, e.g. ``group/project``, or ``group/sub-group/project``.
        :param strategy: (experimental) You can mirror the pipeline status from the triggered pipeline to the source bridge job by using strategy: depend.

        :see: https://docs.gitlab.com/ee/ci/yaml/README.html#trigger-syntax-for-child-pipeline
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if branch is not None:
            self._values["branch"] = branch
        if include is not None:
            self._values["include"] = include
        if project is not None:
            self._values["project"] = project
        if strategy is not None:
            self._values["strategy"] = strategy

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The branch name that a downstream pipeline will use.

        :stability: experimental
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include(self) -> typing.Optional[typing.List["TriggerInclude"]]:
        '''(experimental) A list of local files or artifacts from other jobs to define the pipeline.

        :stability: experimental
        '''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.List["TriggerInclude"]], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path to the project, e.g. ``group/project``, or ``group/sub-group/project``.

        :stability: experimental
        '''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def strategy(self) -> typing.Optional[Strategy]:
        '''(experimental) You can mirror the pipeline status from the triggered pipeline to the source bridge job by using strategy: depend.

        :stability: experimental
        '''
        result = self._values.get("strategy")
        return typing.cast(typing.Optional[Strategy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Trigger(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.TriggerInclude",
    jsii_struct_bases=[],
    name_mapping={
        "artifact": "artifact",
        "file": "file",
        "job": "job",
        "local": "local",
        "project": "project",
        "ref": "ref",
        "template": "template",
    },
)
class TriggerInclude:
    def __init__(
        self,
        *,
        artifact: typing.Optional[builtins.str] = None,
        file: typing.Optional[builtins.str] = None,
        job: typing.Optional[builtins.str] = None,
        local: typing.Optional[builtins.str] = None,
        project: typing.Optional[builtins.str] = None,
        ref: typing.Optional[builtins.str] = None,
        template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) References a local file or an artifact from another job to define the pipeline configuration.

        :param artifact: (experimental) Relative path to the generated YAML file which is extracted from the artifacts and used as the configuration for triggering the child pipeline.
        :param file: (experimental) Relative path from repository root (``/``) to the pipeline configuration YAML file.
        :param job: (experimental) Job name which generates the artifact.
        :param local: (experimental) Relative path from local repository root (``/``) to the local YAML file to define the pipeline configuration.
        :param project: (experimental) Path to another private project under the same GitLab instance, like ``group/project`` or ``group/sub-group/project``.
        :param ref: (experimental) Branch/Tag/Commit hash for the target project.
        :param template: (experimental) Name of the template YAML file to use in the pipeline configuration.

        :see: https://docs.gitlab.com/ee/ci/yaml/#triggerinclude
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if artifact is not None:
            self._values["artifact"] = artifact
        if file is not None:
            self._values["file"] = file
        if job is not None:
            self._values["job"] = job
        if local is not None:
            self._values["local"] = local
        if project is not None:
            self._values["project"] = project
        if ref is not None:
            self._values["ref"] = ref
        if template is not None:
            self._values["template"] = template

    @builtins.property
    def artifact(self) -> typing.Optional[builtins.str]:
        '''(experimental) Relative path to the generated YAML file which is extracted from the artifacts and used as the configuration for triggering the child pipeline.

        :stability: experimental
        '''
        result = self._values.get("artifact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file(self) -> typing.Optional[builtins.str]:
        '''(experimental) Relative path from repository root (``/``) to the pipeline configuration YAML file.

        :stability: experimental
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job(self) -> typing.Optional[builtins.str]:
        '''(experimental) Job name which generates the artifact.

        :stability: experimental
        '''
        result = self._values.get("job")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local(self) -> typing.Optional[builtins.str]:
        '''(experimental) Relative path from local repository root (``/``) to the local YAML file to define the pipeline configuration.

        :stability: experimental
        '''
        result = self._values.get("local")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path to another private project under the same GitLab instance, like ``group/project`` or ``group/sub-group/project``.

        :stability: experimental
        '''
        result = self._values.get("project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ref(self) -> typing.Optional[builtins.str]:
        '''(experimental) Branch/Tag/Commit hash for the target project.

        :stability: experimental
        '''
        result = self._values.get("ref")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the template YAML file to use in the pipeline configuration.

        :stability: experimental
        '''
        result = self._values.get("template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TriggerInclude(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.VariableConfig",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "value": "value"},
)
class VariableConfig:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Explains what the global variable is used for, what the acceptable values are.

        :param description: (experimental) Define a global variable that is prefilled when running a pipeline manually. Must be used with value.
        :param value: (experimental) The variable value.

        :see: https://docs.gitlab.com/ee/ci/yaml/#variables
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Define a global variable that is prefilled when running a pipeline manually.

        Must be used with value.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''(experimental) The variable value.

        :stability: experimental
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VariableConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.VaultConfig",
    jsii_struct_bases=[],
    name_mapping={"engine": "engine", "field": "field", "path": "path"},
)
class VaultConfig:
    def __init__(
        self,
        *,
        engine: Engine,
        field: builtins.str,
        path: builtins.str,
    ) -> None:
        '''(experimental) Specification for a secret provided by a HashiCorp Vault.

        :param engine: 
        :param field: 
        :param path: (experimental) Path to the secret.

        :see: https://www.vaultproject.io/
        :stability: experimental
        '''
        if isinstance(engine, dict):
            engine = Engine(**engine)
        self._values: typing.Dict[str, typing.Any] = {
            "engine": engine,
            "field": field,
            "path": path,
        }

    @builtins.property
    def engine(self) -> Engine:
        '''
        :stability: experimental
        '''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(Engine, result)

    @builtins.property
    def field(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("field")
        assert result is not None, "Required property 'field' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) Path to the secret.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.Workflow",
    jsii_struct_bases=[],
    name_mapping={"rules": "rules"},
)
class Workflow:
    def __init__(
        self,
        *,
        rules: typing.Optional[typing.Sequence["WorkflowRule"]] = None,
    ) -> None:
        '''(experimental) Used to control pipeline behavior.

        :param rules: (experimental) Used to control whether or not a whole pipeline is created.

        :see: https://docs.gitlab.com/ee/ci/yaml/#workflow
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if rules is not None:
            self._values["rules"] = rules

    @builtins.property
    def rules(self) -> typing.Optional[typing.List["WorkflowRule"]]:
        '''(experimental) Used to control whether or not a whole pipeline is created.

        :stability: experimental
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List["WorkflowRule"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Workflow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.gitlab.WorkflowRule",
    jsii_struct_bases=[],
    name_mapping={
        "changes": "changes",
        "exists": "exists",
        "if_": "if",
        "variables": "variables",
        "when": "when",
    },
)
class WorkflowRule:
    def __init__(
        self,
        *,
        changes: typing.Optional[typing.Sequence[builtins.str]] = None,
        exists: typing.Optional[typing.Sequence[builtins.str]] = None,
        if_: typing.Optional[builtins.str] = None,
        variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number]]] = None,
        when: typing.Optional[JobWhen] = None,
    ) -> None:
        '''(experimental) Used to control whether or not a whole pipeline is created.

        :param changes: 
        :param exists: 
        :param if_: 
        :param variables: 
        :param when: 

        :see: https://docs.gitlab.com/ee/ci/yaml/#workflowrules
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if changes is not None:
            self._values["changes"] = changes
        if exists is not None:
            self._values["exists"] = exists
        if if_ is not None:
            self._values["if_"] = if_
        if variables is not None:
            self._values["variables"] = variables
        if when is not None:
            self._values["when"] = when

    @builtins.property
    def changes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("changes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def exists(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("exists")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def if_(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("if_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.str, jsii.Number]]], result)

    @builtins.property
    def when(self) -> typing.Optional[JobWhen]:
        '''
        :stability: experimental
        '''
        result = self._values.get("when")
        return typing.cast(typing.Optional[JobWhen], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.gitlab.WorkflowWhen")
class WorkflowWhen(enum.Enum):
    '''(experimental) Describes the conditions for when to run the job.

    Defaults to 'on_success'.
    The value can only be 'always' or 'never' when used with workflow.

    :see: https://docs.gitlab.com/ee/ci/yaml/#workflowrules
    :stability: experimental
    '''

    ALWAYS = "ALWAYS"
    '''
    :stability: experimental
    '''
    NEVER = "NEVER"
    '''
    :stability: experimental
    '''


__all__ = [
    "Action",
    "AllowFailure",
    "Artifacts",
    "Assets",
    "Cache",
    "CacheWhen",
    "CiConfiguration",
    "CiConfigurationOptions",
    "Default",
    "DefaultElement",
    "DeploymentTier",
    "Engine",
    "Environment",
    "Filter",
    "GitlabConfiguration",
    "Image",
    "Include",
    "IncludeRule",
    "Inherit",
    "Job",
    "JobWhen",
    "KubernetesConfig",
    "KubernetesEnum",
    "Link",
    "LinkType",
    "Need",
    "NestedConfiguration",
    "Parallel",
    "Release",
    "Reports",
    "Retry",
    "Secret",
    "Service",
    "Strategy",
    "Trigger",
    "TriggerInclude",
    "VariableConfig",
    "VaultConfig",
    "Workflow",
    "WorkflowRule",
    "WorkflowWhen",
]

publication.publish()
