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
    Task as _Task_9fa875b6,
)
from ..github import GitIdentity as _GitIdentity_6effc3de
from ..github.workflows import (
    ContainerOptions as _ContainerOptions_f50907af,
    Job as _Job_20ffcf45,
    JobDefaults as _JobDefaults_965f0d10,
    JobPermissions as _JobPermissions_3b5b53dc,
    JobStep as _JobStep_c3287c05,
    JobStepOutput as _JobStepOutput_acebe827,
    JobStrategy as _JobStrategy_15089712,
    Tools as _Tools_75b93a2a,
    Triggers as _Triggers_e9ae7617,
)


@jsii.data_type(
    jsii_type="projen.build.AddPostBuildJobCommandsOptions",
    jsii_struct_bases=[],
    name_mapping={
        "checkout_repo": "checkoutRepo",
        "install_deps": "installDeps",
        "runs_on": "runsOn",
        "tools": "tools",
    },
)
class AddPostBuildJobCommandsOptions:
    def __init__(
        self,
        *,
        checkout_repo: typing.Optional[builtins.bool] = None,
        install_deps: typing.Optional[builtins.bool] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Options for ``BuildWorkflow.addPostBuildJobCommands``.

        :param checkout_repo: (experimental) Check out the repository at the pull request branch before commands are run. Default: false
        :param install_deps: (experimental) Install project dependencies before running commands. ``checkoutRepo`` must also be set to true. Currently only supported for ``NodeProject``. Default: false
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param tools: (experimental) Tools that should be installed before the commands are run.

        :stability: experimental
        '''
        if isinstance(tools, dict):
            tools = _Tools_75b93a2a(**tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if checkout_repo is not None:
            self._values["checkout_repo"] = checkout_repo
        if install_deps is not None:
            self._values["install_deps"] = install_deps
        if runs_on is not None:
            self._values["runs_on"] = runs_on
        if tools is not None:
            self._values["tools"] = tools

    @builtins.property
    def checkout_repo(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Check out the repository at the pull request branch before commands are run.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("checkout_repo")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def install_deps(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Install project dependencies before running commands. ``checkoutRepo`` must also be set to true.

        Currently only supported for ``NodeProject``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("install_deps")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Tools that should be installed before the commands are run.

        :stability: experimental
        '''
        result = self._values.get("tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddPostBuildJobCommandsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.build.AddPostBuildJobTaskOptions",
    jsii_struct_bases=[],
    name_mapping={"runs_on": "runsOn", "tools": "tools"},
)
class AddPostBuildJobTaskOptions:
    def __init__(
        self,
        *,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Options for ``BuildWorkflow.addPostBuildJobTask``.

        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param tools: (experimental) Tools that should be installed before the task is run.

        :stability: experimental
        '''
        if isinstance(tools, dict):
            tools = _Tools_75b93a2a(**tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if runs_on is not None:
            self._values["runs_on"] = runs_on
        if tools is not None:
            self._values["tools"] = tools

    @builtins.property
    def runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Tools that should be installed before the task is run.

        :stability: experimental
        '''
        result = self._values.get("tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddPostBuildJobTaskOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BuildWorkflow(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.build.BuildWorkflow",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        artifacts_directory: builtins.str,
        build_task: _Task_9fa875b6,
        container_image: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        git_identity: typing.Optional[_GitIdentity_6effc3de] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_triggers: typing.Optional[_Triggers_e9ae7617] = None,
    ) -> None:
        '''
        :param project: -
        :param artifacts_directory: (experimental) A name of a directory that includes build artifacts.
        :param build_task: (experimental) The task to execute in order to build the project.
        :param container_image: (experimental) The container image to use for builds. Default: - the default workflow container
        :param env: (experimental) Build environment variables. Default: {}
        :param git_identity: (experimental) Git identity to use for the workflow. Default: - default identity
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. This is enabled by default only if ``githubTokenSecret`` is set. Otherwise it is disabled, which implies that file changes that happen during build will not be pushed back to the branch. Default: true
        :param post_build_steps: (experimental) Steps to execute after build. Default: []
        :param pre_build_steps: (experimental) Steps to execute before the build. Default: []
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"

        :stability: experimental
        '''
        options = BuildWorkflowOptions(
            artifacts_directory=artifacts_directory,
            build_task=build_task,
            container_image=container_image,
            env=env,
            git_identity=git_identity,
            mutable_build=mutable_build,
            post_build_steps=post_build_steps,
            pre_build_steps=pre_build_steps,
            runs_on=runs_on,
            workflow_triggers=workflow_triggers,
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="addPostBuildJob")
    def add_post_build_job(
        self,
        id: builtins.str,
        *,
        permissions: _JobPermissions_3b5b53dc,
        runs_on: typing.Sequence[builtins.str],
        steps: typing.Sequence[_JobStep_c3287c05],
        concurrency: typing.Any = None,
        container: typing.Optional[_ContainerOptions_f50907af] = None,
        continue_on_error: typing.Optional[builtins.bool] = None,
        defaults: typing.Optional[_JobDefaults_965f0d10] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment: typing.Any = None,
        if_: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        needs: typing.Optional[typing.Sequence[builtins.str]] = None,
        outputs: typing.Optional[typing.Mapping[builtins.str, _JobStepOutput_acebe827]] = None,
        services: typing.Optional[typing.Mapping[builtins.str, _ContainerOptions_f50907af]] = None,
        strategy: typing.Optional[_JobStrategy_15089712] = None,
        timeout_minutes: typing.Optional[jsii.Number] = None,
        tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Adds another job to the build workflow which is executed after the build job succeeded.

        Jobs are executed *only* if the build did NOT self mutate. If the build
        self-mutate, the branch will either be updated or the build will fail (in
        forks), so there is no point in executing the post-build job.

        :param id: The id of the new job.
        :param permissions: (experimental) You can modify the default permissions granted to the GITHUB_TOKEN, adding or removing access as required, so that you only allow the minimum required access. Use ``{ contents: READ }`` if your job only needs to clone code. This is intentionally a required field since it is required in order to allow workflows to run in GitHub repositories with restricted default access.
        :param runs_on: (experimental) The type of machine to run the job on. The machine can be either a GitHub-hosted runner or a self-hosted runner.
        :param steps: (experimental) A job contains a sequence of tasks called steps. Steps can run commands, run setup tasks, or run an action in your repository, a public repository, or an action published in a Docker registry. Not all steps run actions, but all actions run as a step. Each step runs in its own process in the runner environment and has access to the workspace and filesystem. Because steps run in their own process, changes to environment variables are not preserved between steps. GitHub provides built-in steps to set up and complete a job.
        :param concurrency: (experimental) Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time. A concurrency group can be any string or expression. The expression can use any context except for the secrets context.
        :param container: (experimental) A container to run any steps in a job that don't already specify a container. If you have steps that use both script and container actions, the container actions will run as sibling containers on the same network with the same volume mounts.
        :param continue_on_error: (experimental) Prevents a workflow run from failing when a job fails. Set to true to allow a workflow run to pass when this job fails.
        :param defaults: (experimental) A map of default settings that will apply to all steps in the job. You can also set default settings for the entire workflow.
        :param env: (experimental) A map of environment variables that are available to all steps in the job. You can also set environment variables for the entire workflow or an individual step.
        :param environment: (experimental) The environment that the job references. All environment protection rules must pass before a job referencing the environment is sent to a runner.
        :param if_: (experimental) You can use the if conditional to prevent a job from running unless a condition is met. You can use any supported context and expression to create a conditional.
        :param name: (experimental) The name of the job displayed on GitHub.
        :param needs: (experimental) Identifies any jobs that must complete successfully before this job will run. It can be a string or array of strings. If a job fails, all jobs that need it are skipped unless the jobs use a conditional expression that causes the job to continue.
        :param outputs: (experimental) A map of outputs for a job. Job outputs are available to all downstream jobs that depend on this job.
        :param services: (experimental) Used to host service containers for a job in a workflow. Service containers are useful for creating databases or cache services like Redis. The runner automatically creates a Docker network and manages the life cycle of the service containers.
        :param strategy: (experimental) A strategy creates a build matrix for your jobs. You can define different variations to run each job in.
        :param timeout_minutes: (experimental) The maximum number of minutes to let a job run before GitHub automatically cancels it. Default: 360
        :param tools: (experimental) Tools required for this job. Traslates into ``actions/setup-xxx`` steps at the beginning of the job.

        :stability: experimental
        '''
        job = _Job_20ffcf45(
            permissions=permissions,
            runs_on=runs_on,
            steps=steps,
            concurrency=concurrency,
            container=container,
            continue_on_error=continue_on_error,
            defaults=defaults,
            env=env,
            environment=environment,
            if_=if_,
            name=name,
            needs=needs,
            outputs=outputs,
            services=services,
            strategy=strategy,
            timeout_minutes=timeout_minutes,
            tools=tools,
        )

        return typing.cast(None, jsii.invoke(self, "addPostBuildJob", [id, job]))

    @jsii.member(jsii_name="addPostBuildJobCommands")
    def add_post_build_job_commands(
        self,
        id: builtins.str,
        commands: typing.Sequence[builtins.str],
        *,
        checkout_repo: typing.Optional[builtins.bool] = None,
        install_deps: typing.Optional[builtins.bool] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Run a sequence of commands as a job within the build workflow which is executed after the build job succeeded.

        Jobs are executed *only* if the build did NOT self mutate. If the build
        self-mutate, the branch will either be updated or the build will fail (in
        forks), so there is no point in executing the post-build job.

        :param id: -
        :param commands: -
        :param checkout_repo: (experimental) Check out the repository at the pull request branch before commands are run. Default: false
        :param install_deps: (experimental) Install project dependencies before running commands. ``checkoutRepo`` must also be set to true. Currently only supported for ``NodeProject``. Default: false
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param tools: (experimental) Tools that should be installed before the commands are run.

        :stability: experimental
        '''
        options = AddPostBuildJobCommandsOptions(
            checkout_repo=checkout_repo,
            install_deps=install_deps,
            runs_on=runs_on,
            tools=tools,
        )

        return typing.cast(None, jsii.invoke(self, "addPostBuildJobCommands", [id, commands, options]))

    @jsii.member(jsii_name="addPostBuildJobTask")
    def add_post_build_job_task(
        self,
        task: _Task_9fa875b6,
        *,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Run a task as a job within the build workflow which is executed after the build job succeeded.

        The job will have access to build artifacts and will install project
        dependencies in order to be able to run any commands used in the tasks.

        Jobs are executed *only* if the build did NOT self mutate. If the build
        self-mutate, the branch will either be updated or the build will fail (in
        forks), so there is no point in executing the post-build job.

        :param task: -
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param tools: (experimental) Tools that should be installed before the task is run.

        :stability: experimental
        '''
        options = AddPostBuildJobTaskOptions(runs_on=runs_on, tools=tools)

        return typing.cast(None, jsii.invoke(self, "addPostBuildJobTask", [task, options]))

    @jsii.member(jsii_name="addPostBuildSteps")
    def add_post_build_steps(self, *steps: _JobStep_c3287c05) -> None:
        '''(experimental) Adds steps that are executed after the build.

        :param steps: The job steps.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addPostBuildSteps", [*steps]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildJobIds")
    def build_job_ids(self) -> typing.List[builtins.str]:
        '''(experimental) Returns a list of job IDs that are part of the build.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "buildJobIds"))


@jsii.data_type(
    jsii_type="projen.build.BuildWorkflowOptions",
    jsii_struct_bases=[],
    name_mapping={
        "artifacts_directory": "artifactsDirectory",
        "build_task": "buildTask",
        "container_image": "containerImage",
        "env": "env",
        "git_identity": "gitIdentity",
        "mutable_build": "mutableBuild",
        "post_build_steps": "postBuildSteps",
        "pre_build_steps": "preBuildSteps",
        "runs_on": "runsOn",
        "workflow_triggers": "workflowTriggers",
    },
)
class BuildWorkflowOptions:
    def __init__(
        self,
        *,
        artifacts_directory: builtins.str,
        build_task: _Task_9fa875b6,
        container_image: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        git_identity: typing.Optional[_GitIdentity_6effc3de] = None,
        mutable_build: typing.Optional[builtins.bool] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_triggers: typing.Optional[_Triggers_e9ae7617] = None,
    ) -> None:
        '''
        :param artifacts_directory: (experimental) A name of a directory that includes build artifacts.
        :param build_task: (experimental) The task to execute in order to build the project.
        :param container_image: (experimental) The container image to use for builds. Default: - the default workflow container
        :param env: (experimental) Build environment variables. Default: {}
        :param git_identity: (experimental) Git identity to use for the workflow. Default: - default identity
        :param mutable_build: (experimental) Automatically update files modified during builds to pull-request branches. This means that any files synthesized by projen or e.g. test snapshots will always be up-to-date before a PR is merged. Implies that PR builds do not have anti-tamper checks. This is enabled by default only if ``githubTokenSecret`` is set. Otherwise it is disabled, which implies that file changes that happen during build will not be pushed back to the branch. Default: true
        :param post_build_steps: (experimental) Steps to execute after build. Default: []
        :param pre_build_steps: (experimental) Steps to execute before the build. Default: []
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param workflow_triggers: (experimental) Build workflow triggers. Default: "{ pullRequest: {}, workflowDispatch: {} }"

        :stability: experimental
        '''
        if isinstance(git_identity, dict):
            git_identity = _GitIdentity_6effc3de(**git_identity)
        if isinstance(workflow_triggers, dict):
            workflow_triggers = _Triggers_e9ae7617(**workflow_triggers)
        self._values: typing.Dict[str, typing.Any] = {
            "artifacts_directory": artifacts_directory,
            "build_task": build_task,
        }
        if container_image is not None:
            self._values["container_image"] = container_image
        if env is not None:
            self._values["env"] = env
        if git_identity is not None:
            self._values["git_identity"] = git_identity
        if mutable_build is not None:
            self._values["mutable_build"] = mutable_build
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if pre_build_steps is not None:
            self._values["pre_build_steps"] = pre_build_steps
        if runs_on is not None:
            self._values["runs_on"] = runs_on
        if workflow_triggers is not None:
            self._values["workflow_triggers"] = workflow_triggers

    @builtins.property
    def artifacts_directory(self) -> builtins.str:
        '''(experimental) A name of a directory that includes build artifacts.

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        assert result is not None, "Required property 'artifacts_directory' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_task(self) -> _Task_9fa875b6:
        '''(experimental) The task to execute in order to build the project.

        :stability: experimental
        '''
        result = self._values.get("build_task")
        assert result is not None, "Required property 'build_task' is missing"
        return typing.cast(_Task_9fa875b6, result)

    @builtins.property
    def container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) The container image to use for builds.

        :default: - the default workflow container

        :stability: experimental
        '''
        result = self._values.get("container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Build environment variables.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def git_identity(self) -> typing.Optional[_GitIdentity_6effc3de]:
        '''(experimental) Git identity to use for the workflow.

        :default: - default identity

        :stability: experimental
        '''
        result = self._values.get("git_identity")
        return typing.cast(typing.Optional[_GitIdentity_6effc3de], result)

    @builtins.property
    def mutable_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically update files modified during builds to pull-request branches.

        This means that any files synthesized by projen or e.g. test snapshots will
        always be up-to-date before a PR is merged.

        Implies that PR builds do not have anti-tamper checks.

        This is enabled by default only if ``githubTokenSecret`` is set. Otherwise it
        is disabled, which implies that file changes that happen during build will
        not be pushed back to the branch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mutable_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def post_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute after build.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def pre_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before the build.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("pre_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_triggers(self) -> typing.Optional[_Triggers_e9ae7617]:
        '''(experimental) Build workflow triggers.

        :default: "{ pullRequest: {}, workflowDispatch: {} }"

        :stability: experimental
        '''
        result = self._values.get("workflow_triggers")
        return typing.cast(typing.Optional[_Triggers_e9ae7617], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildWorkflowOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AddPostBuildJobCommandsOptions",
    "AddPostBuildJobTaskOptions",
    "BuildWorkflow",
    "BuildWorkflowOptions",
]

publication.publish()
