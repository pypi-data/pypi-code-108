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
    Gitpod as _Gitpod_5d9b9d87,
    LoggerOptions as _LoggerOptions_eb0f6309,
    Project as _Project_57d89203,
    ProjectOptions as _ProjectOptions_0d5b93c6,
    ProjectType as _ProjectType_fd80c725,
    ProjenrcOptions as _ProjenrcOptions_164bd039,
    SampleReadmeProps as _SampleReadmeProps_3518b03b,
    Task as _Task_9fa875b6,
    TextFile as _TextFile_4a74808c,
    YamlFile as _YamlFile_909731b0,
)
from ..vscode import DevContainer as _DevContainer_ae6f3538, VsCode as _VsCode_9f0f4eb5
from .workflows import (
    BranchProtectionRuleOptions as _BranchProtectionRuleOptions_422f7f4e,
    CheckRunOptions as _CheckRunOptions_66af1ceb,
    CheckSuiteOptions as _CheckSuiteOptions_6a122376,
    ContainerOptions as _ContainerOptions_f50907af,
    CreateOptions as _CreateOptions_6247308d,
    CronScheduleOptions as _CronScheduleOptions_7724cd93,
    DeleteOptions as _DeleteOptions_c46578d4,
    DeploymentOptions as _DeploymentOptions_0bea6580,
    DeploymentStatusOptions as _DeploymentStatusOptions_f9cbd32b,
    DiscussionCommentOptions as _DiscussionCommentOptions_e8674c31,
    DiscussionOptions as _DiscussionOptions_6b34c7b6,
    ForkOptions as _ForkOptions_0437229d,
    GollumOptions as _GollumOptions_1acffea2,
    IssueCommentOptions as _IssueCommentOptions_b551b1e5,
    IssuesOptions as _IssuesOptions_dd89885c,
    Job as _Job_20ffcf45,
    JobDefaults as _JobDefaults_965f0d10,
    JobPermissions as _JobPermissions_3b5b53dc,
    JobStep as _JobStep_c3287c05,
    JobStepOutput as _JobStepOutput_acebe827,
    JobStrategy as _JobStrategy_15089712,
    LabelOptions as _LabelOptions_ca474a61,
    MilestoneOptions as _MilestoneOptions_6f9d8b6f,
    PageBuildOptions as _PageBuildOptions_c30eafce,
    ProjectCardOptions as _ProjectCardOptions_c89fc28d,
    ProjectColumnOptions as _ProjectColumnOptions_25a462f6,
    ProjectOptions as _ProjectOptions_50d963ea,
    PublicOptions as _PublicOptions_2c3a3b94,
    PullRequestOptions as _PullRequestOptions_b051b0c9,
    PullRequestReviewCommentOptions as _PullRequestReviewCommentOptions_85235a68,
    PullRequestReviewOptions as _PullRequestReviewOptions_27fd8e95,
    PullRequestTargetOptions as _PullRequestTargetOptions_81011bb1,
    PushOptions as _PushOptions_63e1c4f2,
    RegistryPackageOptions as _RegistryPackageOptions_781d5ac7,
    ReleaseOptions as _ReleaseOptions_d152186d,
    RepositoryDispatchOptions as _RepositoryDispatchOptions_d75e9903,
    StatusOptions as _StatusOptions_aa35df44,
    Tools as _Tools_75b93a2a,
    Triggers as _Triggers_e9ae7617,
    WatchOptions as _WatchOptions_d33f5d00,
    WorkflowCallOptions as _WorkflowCallOptions_bc57a5b4,
    WorkflowDispatchOptions as _WorkflowDispatchOptions_7110ffdc,
    WorkflowRunOptions as _WorkflowRunOptions_5a4262c5,
)


class AutoApprove(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.AutoApprove",
):
    '''(experimental) Auto approve pull requests that meet a criteria.

    :stability: experimental
    '''

    def __init__(
        self,
        github: "GitHub",
        *,
        allowed_usernames: typing.Optional[typing.Sequence[builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param github: -
        :param allowed_usernames: (experimental) Only pull requests authored by these Github usernames will be auto-approved. Default: ['github-bot']
        :param label: (experimental) Only pull requests with this label will be auto-approved. Default: 'auto-approve'
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param secret: (experimental) A GitHub secret name which contains a GitHub Access Token with write permissions for the ``pull_request`` scope. This token is used to approve pull requests. Github forbids an identity to approve its own pull request. If your project produces automated pull requests using the Github default token - {@link https://docs.github.com/en/actions/reference/authentication-in-a-workflow ``GITHUB_TOKEN`` } - that you would like auto approved, such as when using the ``depsUpgrade`` property in ``NodeProjectOptions``, then you must use a different token here. Default: "GITHUB_TOKEN"

        :stability: experimental
        '''
        options = AutoApproveOptions(
            allowed_usernames=allowed_usernames,
            label=label,
            runs_on=runs_on,
            secret=secret,
        )

        jsii.create(self.__class__, self, [github, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "label"))


@jsii.data_type(
    jsii_type="projen.github.AutoApproveOptions",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_usernames": "allowedUsernames",
        "label": "label",
        "runs_on": "runsOn",
        "secret": "secret",
    },
)
class AutoApproveOptions:
    def __init__(
        self,
        *,
        allowed_usernames: typing.Optional[typing.Sequence[builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for 'AutoApprove'.

        :param allowed_usernames: (experimental) Only pull requests authored by these Github usernames will be auto-approved. Default: ['github-bot']
        :param label: (experimental) Only pull requests with this label will be auto-approved. Default: 'auto-approve'
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param secret: (experimental) A GitHub secret name which contains a GitHub Access Token with write permissions for the ``pull_request`` scope. This token is used to approve pull requests. Github forbids an identity to approve its own pull request. If your project produces automated pull requests using the Github default token - {@link https://docs.github.com/en/actions/reference/authentication-in-a-workflow ``GITHUB_TOKEN`` } - that you would like auto approved, such as when using the ``depsUpgrade`` property in ``NodeProjectOptions``, then you must use a different token here. Default: "GITHUB_TOKEN"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if allowed_usernames is not None:
            self._values["allowed_usernames"] = allowed_usernames
        if label is not None:
            self._values["label"] = label
        if runs_on is not None:
            self._values["runs_on"] = runs_on
        if secret is not None:
            self._values["secret"] = secret

    @builtins.property
    def allowed_usernames(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Only pull requests authored by these Github usernames will be auto-approved.

        :default: ['github-bot']

        :stability: experimental
        '''
        result = self._values.get("allowed_usernames")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''(experimental) Only pull requests with this label will be auto-approved.

        :default: 'auto-approve'

        :stability: experimental
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) A GitHub secret name which contains a GitHub Access Token with write permissions for the ``pull_request`` scope.

        This token is used to approve pull requests.

        Github forbids an identity to approve its own pull request.
        If your project produces automated pull requests using the Github default token -
        {@link https://docs.github.com/en/actions/reference/authentication-in-a-workflow ``GITHUB_TOKEN`` }

        - that you would like auto approved, such as when using the ``depsUpgrade`` property in
          ``NodeProjectOptions``, then you must use a different token here.

        :default: "GITHUB_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoApproveOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoMerge(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.AutoMerge",
):
    '''(experimental) Sets up mergify to merging approved pull requests.

    If ``buildJob`` is specified, the specified GitHub workflow job ID is required
    to succeed in order for the PR to be merged.

    ``approvedReviews`` specified the number of code review approvals required for
    the PR to be merged.

    :stability: experimental
    '''

    def __init__(
        self,
        github: "GitHub",
        *,
        approved_reviews: typing.Optional[jsii.Number] = None,
        blocking_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param github: -
        :param approved_reviews: (experimental) Number of approved code reviews. Default: 1
        :param blocking_labels: (experimental) List of labels that will prevent auto-merging. Default: ['do-not-merge']

        :stability: experimental
        '''
        options = AutoMergeOptions(
            approved_reviews=approved_reviews, blocking_labels=blocking_labels
        )

        jsii.create(self.__class__, self, [github, options])

    @jsii.member(jsii_name="addConditions")
    def add_conditions(self, *conditions: builtins.str) -> None:
        '''(experimental) Adds conditions to the auto merge rule.

        :param conditions: The conditions to add (mergify syntax).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addConditions", [*conditions]))

    @jsii.member(jsii_name="addConditionsLater")
    def add_conditions_later(self, later: "IAddConditionsLater") -> None:
        '''(experimental) Adds conditions that will be rendered only during synthesis.

        :param later: The later.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addConditionsLater", [later]))


@jsii.data_type(
    jsii_type="projen.github.AutoMergeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "approved_reviews": "approvedReviews",
        "blocking_labels": "blockingLabels",
    },
)
class AutoMergeOptions:
    def __init__(
        self,
        *,
        approved_reviews: typing.Optional[jsii.Number] = None,
        blocking_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approved_reviews: (experimental) Number of approved code reviews. Default: 1
        :param blocking_labels: (experimental) List of labels that will prevent auto-merging. Default: ['do-not-merge']

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if approved_reviews is not None:
            self._values["approved_reviews"] = approved_reviews
        if blocking_labels is not None:
            self._values["blocking_labels"] = blocking_labels

    @builtins.property
    def approved_reviews(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of approved code reviews.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("approved_reviews")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def blocking_labels(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of labels that will prevent auto-merging.

        :default: ['do-not-merge']

        :stability: experimental
        '''
        result = self._values.get("blocking_labels")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoMergeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Dependabot(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.Dependabot",
):
    '''(experimental) Defines dependabot configuration for node projects.

    Since module versions are managed in projen, the versioning strategy will be
    configured to "lockfile-only" which means that only updates that can be done
    on the lockfile itself will be proposed.

    :stability: experimental
    '''

    def __init__(
        self,
        github: "GitHub",
        *,
        ignore: typing.Optional[typing.Sequence["DependabotIgnore"]] = None,
        ignore_projen: typing.Optional[builtins.bool] = None,
        labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        registries: typing.Optional[typing.Mapping[builtins.str, "DependabotRegistry"]] = None,
        schedule_interval: typing.Optional["DependabotScheduleInterval"] = None,
        versioning_strategy: typing.Optional["VersioningStrategy"] = None,
    ) -> None:
        '''
        :param github: -
        :param ignore: (experimental) You can use the ``ignore`` option to customize which dependencies are updated. The ignore option supports the following options. Default: []
        :param ignore_projen: (experimental) Ignores updates to ``projen``. This is required since projen updates may cause changes in committed files and anti-tamper checks will fail. Projen upgrades are covered through the ``ProjenUpgrade`` class. Default: true
        :param labels: (experimental) List of labels to apply to the created PR's.
        :param registries: (experimental) Map of package registries to use. Default: - use public registries
        :param schedule_interval: (experimental) How often to check for new versions and raise pull requests. Default: ScheduleInterval.DAILY
        :param versioning_strategy: (experimental) The strategy to use when edits manifest and lock files. Default: VersioningStrategy.LOCKFILE_ONLY The default is to only update the lock file because package.json is controlled by projen and any outside updates will fail the build.

        :stability: experimental
        '''
        options = DependabotOptions(
            ignore=ignore,
            ignore_projen=ignore_projen,
            labels=labels,
            registries=registries,
            schedule_interval=schedule_interval,
            versioning_strategy=versioning_strategy,
        )

        jsii.create(self.__class__, self, [github, options])

    @jsii.member(jsii_name="addIgnore")
    def add_ignore(
        self,
        dependency_name: builtins.str,
        *versions: builtins.str,
    ) -> None:
        '''(experimental) Ignores a dependency from automatic updates.

        :param dependency_name: Use to ignore updates for dependencies with matching names, optionally using ``*`` to match zero or more characters.
        :param versions: Use to ignore specific versions or ranges of versions. If you want to define a range, use the standard pattern for the package manager (for example: ``^1.0.0`` for npm, or ``~> 2.0`` for Bundler).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addIgnore", [dependency_name, *versions]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="config")
    def config(self) -> typing.Any:
        '''(experimental) The raw dependabot configuration.

        :see: https://docs.github.com/en/github/administering-a-repository/configuration-options-for-dependency-updates
        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.get(self, "config"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoresProjen")
    def ignores_projen(self) -> builtins.bool:
        '''(experimental) Whether or not projen is also upgraded in this config,.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "ignoresProjen"))


@jsii.data_type(
    jsii_type="projen.github.DependabotIgnore",
    jsii_struct_bases=[],
    name_mapping={"dependency_name": "dependencyName", "versions": "versions"},
)
class DependabotIgnore:
    def __init__(
        self,
        *,
        dependency_name: builtins.str,
        versions: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) You can use the ``ignore`` option to customize which dependencies are updated.

        The ignore option supports the following options.

        :param dependency_name: (experimental) Use to ignore updates for dependencies with matching names, optionally using ``*`` to match zero or more characters. For Java dependencies, the format of the dependency-name attribute is: ``groupId:artifactId``, for example: ``org.kohsuke:github-api``.
        :param versions: (experimental) Use to ignore specific versions or ranges of versions. If you want to define a range, use the standard pattern for the package manager (for example: ``^1.0.0`` for npm, or ``~> 2.0`` for Bundler).

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dependency_name": dependency_name,
        }
        if versions is not None:
            self._values["versions"] = versions

    @builtins.property
    def dependency_name(self) -> builtins.str:
        '''(experimental) Use to ignore updates for dependencies with matching names, optionally using ``*`` to match zero or more characters.

        For Java dependencies, the format of the dependency-name attribute is:
        ``groupId:artifactId``, for example: ``org.kohsuke:github-api``.

        :stability: experimental
        '''
        result = self._values.get("dependency_name")
        assert result is not None, "Required property 'dependency_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def versions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Use to ignore specific versions or ranges of versions.

        If you want to
        define a range, use the standard pattern for the package manager (for
        example: ``^1.0.0`` for npm, or ``~> 2.0`` for Bundler).

        :stability: experimental
        '''
        result = self._values.get("versions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DependabotIgnore(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.DependabotOptions",
    jsii_struct_bases=[],
    name_mapping={
        "ignore": "ignore",
        "ignore_projen": "ignoreProjen",
        "labels": "labels",
        "registries": "registries",
        "schedule_interval": "scheduleInterval",
        "versioning_strategy": "versioningStrategy",
    },
)
class DependabotOptions:
    def __init__(
        self,
        *,
        ignore: typing.Optional[typing.Sequence[DependabotIgnore]] = None,
        ignore_projen: typing.Optional[builtins.bool] = None,
        labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        registries: typing.Optional[typing.Mapping[builtins.str, "DependabotRegistry"]] = None,
        schedule_interval: typing.Optional["DependabotScheduleInterval"] = None,
        versioning_strategy: typing.Optional["VersioningStrategy"] = None,
    ) -> None:
        '''
        :param ignore: (experimental) You can use the ``ignore`` option to customize which dependencies are updated. The ignore option supports the following options. Default: []
        :param ignore_projen: (experimental) Ignores updates to ``projen``. This is required since projen updates may cause changes in committed files and anti-tamper checks will fail. Projen upgrades are covered through the ``ProjenUpgrade`` class. Default: true
        :param labels: (experimental) List of labels to apply to the created PR's.
        :param registries: (experimental) Map of package registries to use. Default: - use public registries
        :param schedule_interval: (experimental) How often to check for new versions and raise pull requests. Default: ScheduleInterval.DAILY
        :param versioning_strategy: (experimental) The strategy to use when edits manifest and lock files. Default: VersioningStrategy.LOCKFILE_ONLY The default is to only update the lock file because package.json is controlled by projen and any outside updates will fail the build.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if ignore is not None:
            self._values["ignore"] = ignore
        if ignore_projen is not None:
            self._values["ignore_projen"] = ignore_projen
        if labels is not None:
            self._values["labels"] = labels
        if registries is not None:
            self._values["registries"] = registries
        if schedule_interval is not None:
            self._values["schedule_interval"] = schedule_interval
        if versioning_strategy is not None:
            self._values["versioning_strategy"] = versioning_strategy

    @builtins.property
    def ignore(self) -> typing.Optional[typing.List[DependabotIgnore]]:
        '''(experimental) You can use the ``ignore`` option to customize which dependencies are updated.

        The ignore option supports the following options.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("ignore")
        return typing.cast(typing.Optional[typing.List[DependabotIgnore]], result)

    @builtins.property
    def ignore_projen(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Ignores updates to ``projen``.

        This is required since projen updates may cause changes in committed files
        and anti-tamper checks will fail.

        Projen upgrades are covered through the ``ProjenUpgrade`` class.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("ignore_projen")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) List of labels to apply to the created PR's.

        :stability: experimental
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def registries(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "DependabotRegistry"]]:
        '''(experimental) Map of package registries to use.

        :default: - use public registries

        :stability: experimental
        '''
        result = self._values.get("registries")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "DependabotRegistry"]], result)

    @builtins.property
    def schedule_interval(self) -> typing.Optional["DependabotScheduleInterval"]:
        '''(experimental) How often to check for new versions and raise pull requests.

        :default: ScheduleInterval.DAILY

        :stability: experimental
        '''
        result = self._values.get("schedule_interval")
        return typing.cast(typing.Optional["DependabotScheduleInterval"], result)

    @builtins.property
    def versioning_strategy(self) -> typing.Optional["VersioningStrategy"]:
        '''(experimental) The strategy to use when edits manifest and lock files.

        :default:

        VersioningStrategy.LOCKFILE_ONLY The default is to only update the
        lock file because package.json is controlled by projen and any outside
        updates will fail the build.

        :stability: experimental
        '''
        result = self._values.get("versioning_strategy")
        return typing.cast(typing.Optional["VersioningStrategy"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DependabotOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.DependabotRegistry",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "url": "url",
        "key": "key",
        "organization": "organization",
        "password": "password",
        "replaces_base": "replacesBase",
        "token": "token",
        "username": "username",
    },
)
class DependabotRegistry:
    def __init__(
        self,
        *,
        type: "DependabotRegistryType",
        url: builtins.str,
        key: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        replaces_base: typing.Optional[builtins.bool] = None,
        token: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Use to add private registry support for dependabot.

        :param type: (experimental) Registry type e.g. 'npm-registry' or 'docker-registry'.
        :param url: (experimental) Url for the registry e.g. 'https://npm.pkg.github.com' or 'registry.hub.docker.com'.
        :param key: (experimental) A reference to a Dependabot secret containing an access key for this registry. Default: undefined
        :param organization: (experimental) Used with the hex-organization registry type. Default: undefined
        :param password: (experimental) A reference to a Dependabot secret containing the password for the specified user. Default: undefined
        :param replaces_base: (experimental) For registries with type: python-index, if the boolean value is true, pip esolves dependencies by using the specified URL rather than the base URL of the Python Package Index (by default https://pypi.org/simple). Default: undefined
        :param token: (experimental) Secret token for dependabot access e.g. '${{ secrets.DEPENDABOT_PACKAGE_TOKEN }}'. Default: undefined
        :param username: (experimental) The username that Dependabot uses to access the registry. Default: - do not authenticate

        :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#configuration-options-for-private-registries
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
            "url": url,
        }
        if key is not None:
            self._values["key"] = key
        if organization is not None:
            self._values["organization"] = organization
        if password is not None:
            self._values["password"] = password
        if replaces_base is not None:
            self._values["replaces_base"] = replaces_base
        if token is not None:
            self._values["token"] = token
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def type(self) -> "DependabotRegistryType":
        '''(experimental) Registry type e.g. 'npm-registry' or 'docker-registry'.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("DependabotRegistryType", result)

    @builtins.property
    def url(self) -> builtins.str:
        '''(experimental) Url for the registry e.g. 'https://npm.pkg.github.com' or 'registry.hub.docker.com'.

        :stability: experimental
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''(experimental) A reference to a Dependabot secret containing an access key for this registry.

        :default: undefined

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''(experimental) Used with the hex-organization registry type.

        :default: undefined

        :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#hex-organization
        :stability: experimental
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''(experimental) A reference to a Dependabot secret containing the password for the specified user.

        :default: undefined

        :stability: experimental
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replaces_base(self) -> typing.Optional[builtins.bool]:
        '''(experimental) For registries with type: python-index, if the boolean value is true, pip esolves dependencies by using the specified URL rather than the base URL of the Python Package Index (by default https://pypi.org/simple).

        :default: undefined

        :stability: experimental
        '''
        result = self._values.get("replaces_base")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''(experimental) Secret token for dependabot access e.g. '${{ secrets.DEPENDABOT_PACKAGE_TOKEN }}'.

        :default: undefined

        :stability: experimental
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''(experimental) The username that Dependabot uses to access the registry.

        :default: - do not authenticate

        :stability: experimental
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DependabotRegistry(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.github.DependabotRegistryType")
class DependabotRegistryType(enum.Enum):
    '''(experimental) Each configuration type requires you to provide particular settings.

    Some types allow more than one way to connect

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#configuration-options-for-private-registries
    :stability: experimental
    '''

    COMPOSER_REGISTRY = "COMPOSER_REGISTRY"
    '''(experimental) The composer-repository type supports username and password.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#composer-repository
    :stability: experimental
    '''
    DOCKER_REGISTRY = "DOCKER_REGISTRY"
    '''(experimental) The docker-registry type supports username and password.

    The docker-registry type can also be used to pull from Amazon ECR using static AWS credentials

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#docker-registry
    :stability: experimental
    '''
    GIT = "GIT"
    '''(experimental) The git type supports username and password.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#git
    :stability: experimental
    '''
    HEX_ORGANIZATION = "HEX_ORGANIZATION"
    '''(experimental) The hex-organization type supports organization and key.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#hex-organization
    :stability: experimental
    '''
    MAVEN_REPOSITORY = "MAVEN_REPOSITORY"
    '''(experimental) The maven-repository type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#maven-repository
    :stability: experimental
    '''
    NPM_REGISTRY = "NPM_REGISTRY"
    '''(experimental) The npm-registry type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#npm-registry
    :stability: experimental
    '''
    NUGET_FEED = "NUGET_FEED"
    '''(experimental) The nuget-feed type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#nuget-feed
    :stability: experimental
    '''
    PYTHON_INDEX = "PYTHON_INDEX"
    '''(experimental) The python-index type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#python-index
    :stability: experimental
    '''
    RUBYGEMS_SERVER = "RUBYGEMS_SERVER"
    '''(experimental) The rubygems-server type supports username and password, or token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#rubygems-server
    :stability: experimental
    '''
    TERRAFORM_REGISTRY = "TERRAFORM_REGISTRY"
    '''(experimental) The terraform-registry type supports a token.

    :see: https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/configuration-options-for-dependency-updates#terraform-registry
    :stability: experimental
    '''


@jsii.enum(jsii_type="projen.github.DependabotScheduleInterval")
class DependabotScheduleInterval(enum.Enum):
    '''(experimental) How often to check for new versions and raise pull requests for version updates.

    :stability: experimental
    '''

    DAILY = "DAILY"
    '''(experimental) Runs on every weekday, Monday to Friday.

    :stability: experimental
    '''
    WEEKLY = "WEEKLY"
    '''(experimental) Runs once each week.

    By default, this is on Monday.

    :stability: experimental
    '''
    MONTHLY = "MONTHLY"
    '''(experimental) Runs once each month.

    This is on the first day of the month.

    :stability: experimental
    '''


class GitHub(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.GitHub",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional["MergifyOptions"] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        pull_request_lint: typing.Optional[builtins.bool] = None,
        pull_request_lint_options: typing.Optional["PullRequestLintOptions"] = None,
        workflows: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param project: -
        :param mergify: (experimental) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (experimental) Options for Mergify. Default: - default options
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param pull_request_lint: (experimental) Add a workflow that performs basic checks for pull requests, like validating that PRs follow Conventional Commits. Default: true
        :param pull_request_lint_options: (experimental) Options for configuring a pull request linter. Default: - see defaults in ``PullRequestLintOptions``
        :param workflows: (experimental) Enables GitHub workflows. If this is set to ``false``, workflows will not be created. Default: true

        :stability: experimental
        '''
        options = GitHubOptions(
            mergify=mergify,
            mergify_options=mergify_options,
            projen_token_secret=projen_token_secret,
            pull_request_lint=pull_request_lint,
            pull_request_lint_options=pull_request_lint_options,
            workflows=workflows,
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, project: _Project_57d89203) -> typing.Optional["GitHub"]:
        '''(experimental) Returns the ``GitHub`` component of a project or ``undefined`` if the project does not have a GitHub component.

        :param project: -

        :stability: experimental
        '''
        return typing.cast(typing.Optional["GitHub"], jsii.sinvoke(cls, "of", [project]))

    @jsii.member(jsii_name="addDependabot")
    def add_dependabot(
        self,
        *,
        ignore: typing.Optional[typing.Sequence[DependabotIgnore]] = None,
        ignore_projen: typing.Optional[builtins.bool] = None,
        labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        registries: typing.Optional[typing.Mapping[builtins.str, DependabotRegistry]] = None,
        schedule_interval: typing.Optional[DependabotScheduleInterval] = None,
        versioning_strategy: typing.Optional["VersioningStrategy"] = None,
    ) -> Dependabot:
        '''
        :param ignore: (experimental) You can use the ``ignore`` option to customize which dependencies are updated. The ignore option supports the following options. Default: []
        :param ignore_projen: (experimental) Ignores updates to ``projen``. This is required since projen updates may cause changes in committed files and anti-tamper checks will fail. Projen upgrades are covered through the ``ProjenUpgrade`` class. Default: true
        :param labels: (experimental) List of labels to apply to the created PR's.
        :param registries: (experimental) Map of package registries to use. Default: - use public registries
        :param schedule_interval: (experimental) How often to check for new versions and raise pull requests. Default: ScheduleInterval.DAILY
        :param versioning_strategy: (experimental) The strategy to use when edits manifest and lock files. Default: VersioningStrategy.LOCKFILE_ONLY The default is to only update the lock file because package.json is controlled by projen and any outside updates will fail the build.

        :stability: experimental
        '''
        options = DependabotOptions(
            ignore=ignore,
            ignore_projen=ignore_projen,
            labels=labels,
            registries=registries,
            schedule_interval=schedule_interval,
            versioning_strategy=versioning_strategy,
        )

        return typing.cast(Dependabot, jsii.invoke(self, "addDependabot", [options]))

    @jsii.member(jsii_name="addPullRequestTemplate")
    def add_pull_request_template(
        self,
        *content: builtins.str,
    ) -> "PullRequestTemplate":
        '''
        :param content: -

        :stability: experimental
        '''
        return typing.cast("PullRequestTemplate", jsii.invoke(self, "addPullRequestTemplate", [*content]))

    @jsii.member(jsii_name="addWorkflow")
    def add_workflow(self, name: builtins.str) -> "GithubWorkflow":
        '''(experimental) Adds a workflow to the project.

        :param name: Name of the workflow.

        :return: a GithubWorkflow instance

        :stability: experimental
        '''
        return typing.cast("GithubWorkflow", jsii.invoke(self, "addWorkflow", [name]))

    @jsii.member(jsii_name="tryFindWorkflow")
    def try_find_workflow(
        self,
        name: builtins.str,
    ) -> typing.Optional["GithubWorkflow"]:
        '''(experimental) Finds a GitHub workflow by name.

        Returns ``undefined`` if the workflow cannot be found.

        :param name: The name of the GitHub workflow.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["GithubWorkflow"], jsii.invoke(self, "tryFindWorkflow", [name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="projenTokenSecret")
    def projen_token_secret(self) -> builtins.str:
        '''(experimental) The name of a secret with a GitHub Personal Access Token to be used by projen workflows.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "projenTokenSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflows")
    def workflows(self) -> typing.List["GithubWorkflow"]:
        '''(experimental) All workflows.

        :stability: experimental
        '''
        return typing.cast(typing.List["GithubWorkflow"], jsii.get(self, "workflows"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowsEnabled")
    def workflows_enabled(self) -> builtins.bool:
        '''(experimental) Are workflows enabled?

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "workflowsEnabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mergify")
    def mergify(self) -> typing.Optional["Mergify"]:
        '''(experimental) The ``Mergify`` configured on this repository.

        This is ``undefined`` if Mergify
        was not enabled when creating the repository.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["Mergify"], jsii.get(self, "mergify"))


@jsii.data_type(
    jsii_type="projen.github.GitHubOptions",
    jsii_struct_bases=[],
    name_mapping={
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "projen_token_secret": "projenTokenSecret",
        "pull_request_lint": "pullRequestLint",
        "pull_request_lint_options": "pullRequestLintOptions",
        "workflows": "workflows",
    },
)
class GitHubOptions:
    def __init__(
        self,
        *,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional["MergifyOptions"] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        pull_request_lint: typing.Optional[builtins.bool] = None,
        pull_request_lint_options: typing.Optional["PullRequestLintOptions"] = None,
        workflows: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param mergify: (experimental) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (experimental) Options for Mergify. Default: - default options
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param pull_request_lint: (experimental) Add a workflow that performs basic checks for pull requests, like validating that PRs follow Conventional Commits. Default: true
        :param pull_request_lint_options: (experimental) Options for configuring a pull request linter. Default: - see defaults in ``PullRequestLintOptions``
        :param workflows: (experimental) Enables GitHub workflows. If this is set to ``false``, workflows will not be created. Default: true

        :stability: experimental
        '''
        if isinstance(mergify_options, dict):
            mergify_options = MergifyOptions(**mergify_options)
        if isinstance(pull_request_lint_options, dict):
            pull_request_lint_options = PullRequestLintOptions(**pull_request_lint_options)
        self._values: typing.Dict[str, typing.Any] = {}
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if pull_request_lint is not None:
            self._values["pull_request_lint"] = pull_request_lint
        if pull_request_lint_options is not None:
            self._values["pull_request_lint_options"] = pull_request_lint_options
        if workflows is not None:
            self._values["workflows"] = workflows

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether mergify should be enabled on this repository or not.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional["MergifyOptions"]:
        '''(experimental) Options for Mergify.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional["MergifyOptions"], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_lint(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a workflow that performs basic checks for pull requests, like validating that PRs follow Conventional Commits.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_lint")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_request_lint_options(self) -> typing.Optional["PullRequestLintOptions"]:
        '''(experimental) Options for configuring a pull request linter.

        :default: - see defaults in ``PullRequestLintOptions``

        :stability: experimental
        '''
        result = self._values.get("pull_request_lint_options")
        return typing.cast(typing.Optional["PullRequestLintOptions"], result)

    @builtins.property
    def workflows(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enables GitHub workflows.

        If this is set to ``false``, workflows will not be created.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("workflows")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GitHubProject(
    _Project_57d89203,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.GitHubProject",
):
    '''(deprecated) GitHub-based project.

    :deprecated:

    This is a *temporary* class. At the moment, our base project
    types such as ``NodeProject`` and ``JavaProject`` are derived from this, but we
    want to be able to use these project types outside of GitHub as well. One of
    the next steps to address this is to abstract workflows so that different
    "engines" can be used to implement our CI/CD solutions.

    :stability: deprecated
    '''

    def __init__(
        self,
        *,
        auto_approve_options: typing.Optional[AutoApproveOptions] = None,
        auto_merge_options: typing.Optional[AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional["MergifyOptions"] = None,
        project_type: typing.Optional[_ProjectType_fd80c725] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[_SampleReadmeProps_3518b03b] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional["StaleOptions"] = None,
        vscode: typing.Optional[builtins.bool] = None,
        name: builtins.str,
        logging: typing.Optional[_LoggerOptions_eb0f6309] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_Project_57d89203] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[_ProjenrcOptions_164bd039] = None,
    ) -> None:
        '''
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options

        :stability: deprecated
        '''
        options = GitHubProjectOptions(
            auto_approve_options=auto_approve_options,
            auto_merge_options=auto_merge_options,
            clobber=clobber,
            dev_container=dev_container,
            github=github,
            github_options=github_options,
            gitpod=gitpod,
            mergify=mergify,
            mergify_options=mergify_options,
            project_type=project_type,
            projen_token_secret=projen_token_secret,
            readme=readme,
            stale=stale,
            stale_options=stale_options,
            vscode=vscode,
            name=name,
            logging=logging,
            outdir=outdir,
            parent=parent,
            projen_command=projen_command,
            projenrc_json=projenrc_json,
            projenrc_json_options=projenrc_json_options,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="annotateGenerated")
    def annotate_generated(self, glob: builtins.str) -> None:
        '''(deprecated) Marks the provided file(s) as being generated.

        This is achieved using the
        github-linguist attributes. Generated files do not count against the
        repository statistics and language breakdown.

        :param glob: the glob pattern to match (could be a file path).

        :see: https://github.com/github/linguist/blob/master/docs/overrides.md
        :stability: deprecated
        '''
        return typing.cast(None, jsii.invoke(self, "annotateGenerated", [glob]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="projectType")
    def project_type(self) -> _ProjectType_fd80c725:
        '''
        :stability: deprecated
        '''
        return typing.cast(_ProjectType_fd80c725, jsii.get(self, "projectType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoApprove")
    def auto_approve(self) -> typing.Optional[AutoApprove]:
        '''(deprecated) Auto approve set up for this project.

        :stability: deprecated
        '''
        return typing.cast(typing.Optional[AutoApprove], jsii.get(self, "autoApprove"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="devContainer")
    def dev_container(self) -> typing.Optional[_DevContainer_ae6f3538]:
        '''(deprecated) Access for .devcontainer.json (used for GitHub Codespaces).

        This will be ``undefined`` if devContainer boolean is false

        :stability: deprecated
        '''
        return typing.cast(typing.Optional[_DevContainer_ae6f3538], jsii.get(self, "devContainer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="github")
    def github(self) -> typing.Optional[GitHub]:
        '''(deprecated) Access all github components.

        This will be ``undefined`` for subprojects.

        :stability: deprecated
        '''
        return typing.cast(typing.Optional[GitHub], jsii.get(self, "github"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gitpod")
    def gitpod(self) -> typing.Optional[_Gitpod_5d9b9d87]:
        '''(deprecated) Access for Gitpod.

        This will be ``undefined`` if gitpod boolean is false

        :stability: deprecated
        '''
        return typing.cast(typing.Optional[_Gitpod_5d9b9d87], jsii.get(self, "gitpod"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vscode")
    def vscode(self) -> typing.Optional[_VsCode_9f0f4eb5]:
        '''(deprecated) Access all VSCode components.

        This will be ``undefined`` for subprojects.

        :stability: deprecated
        '''
        return typing.cast(typing.Optional[_VsCode_9f0f4eb5], jsii.get(self, "vscode"))


@jsii.data_type(
    jsii_type="projen.github.GitHubProjectOptions",
    jsii_struct_bases=[_ProjectOptions_0d5b93c6],
    name_mapping={
        "name": "name",
        "logging": "logging",
        "outdir": "outdir",
        "parent": "parent",
        "projen_command": "projenCommand",
        "projenrc_json": "projenrcJson",
        "projenrc_json_options": "projenrcJsonOptions",
        "auto_approve_options": "autoApproveOptions",
        "auto_merge_options": "autoMergeOptions",
        "clobber": "clobber",
        "dev_container": "devContainer",
        "github": "github",
        "github_options": "githubOptions",
        "gitpod": "gitpod",
        "mergify": "mergify",
        "mergify_options": "mergifyOptions",
        "project_type": "projectType",
        "projen_token_secret": "projenTokenSecret",
        "readme": "readme",
        "stale": "stale",
        "stale_options": "staleOptions",
        "vscode": "vscode",
    },
)
class GitHubProjectOptions(_ProjectOptions_0d5b93c6):
    def __init__(
        self,
        *,
        name: builtins.str,
        logging: typing.Optional[_LoggerOptions_eb0f6309] = None,
        outdir: typing.Optional[builtins.str] = None,
        parent: typing.Optional[_Project_57d89203] = None,
        projen_command: typing.Optional[builtins.str] = None,
        projenrc_json: typing.Optional[builtins.bool] = None,
        projenrc_json_options: typing.Optional[_ProjenrcOptions_164bd039] = None,
        auto_approve_options: typing.Optional[AutoApproveOptions] = None,
        auto_merge_options: typing.Optional[AutoMergeOptions] = None,
        clobber: typing.Optional[builtins.bool] = None,
        dev_container: typing.Optional[builtins.bool] = None,
        github: typing.Optional[builtins.bool] = None,
        github_options: typing.Optional[GitHubOptions] = None,
        gitpod: typing.Optional[builtins.bool] = None,
        mergify: typing.Optional[builtins.bool] = None,
        mergify_options: typing.Optional["MergifyOptions"] = None,
        project_type: typing.Optional[_ProjectType_fd80c725] = None,
        projen_token_secret: typing.Optional[builtins.str] = None,
        readme: typing.Optional[_SampleReadmeProps_3518b03b] = None,
        stale: typing.Optional[builtins.bool] = None,
        stale_options: typing.Optional["StaleOptions"] = None,
        vscode: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for ``GitHubProject``.

        :param name: (experimental) This is the name of your project. Default: $BASEDIR
        :param logging: (experimental) Configure logging options such as verbosity. Default: {}
        :param outdir: (experimental) The root directory of the project. Relative to this directory, all files are synthesized. If this project has a parent, this directory is relative to the parent directory and it cannot be the same as the parent or any of it's other sub-projects. Default: "."
        :param parent: (experimental) The parent project, if this project is part of a bigger project.
        :param projen_command: (experimental) The shell command to use in order to run the projen CLI. Can be used to customize in special environments. Default: "npx projen"
        :param projenrc_json: (experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation. Default: false
        :param projenrc_json_options: (experimental) Options for .projenrc.json. Default: - default options
        :param auto_approve_options: (experimental) Enable and configure the 'auto approve' workflow. Default: - auto approve is disabled
        :param auto_merge_options: (experimental) Configure options for automatic merging on GitHub. Has no effect if ``github.mergify`` is set to false. Default: - see defaults in ``AutoMergeOptions``
        :param clobber: (experimental) Add a ``clobber`` task which resets the repo to origin. Default: true
        :param dev_container: (experimental) Add a VSCode development environment (used for GitHub Codespaces). Default: false
        :param github: (experimental) Enable GitHub integration. Enabled by default for root projects. Disabled for non-root projects. Default: true
        :param github_options: (experimental) Options for GitHub integration. Default: - see GitHubOptions
        :param gitpod: (experimental) Add a Gitpod development environment. Default: false
        :param mergify: (deprecated) Whether mergify should be enabled on this repository or not. Default: true
        :param mergify_options: (deprecated) Options for mergify. Default: - default options
        :param project_type: (deprecated) Which type of project this is (library/app). Default: ProjectType.UNKNOWN
        :param projen_token_secret: (experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows. This token needs to have the ``repo``, ``workflows`` and ``packages`` scope. Default: "PROJEN_GITHUB_TOKEN"
        :param readme: (experimental) The README setup. Default: - { filename: 'README.md', contents: '# replace this' }
        :param stale: (experimental) Auto-close of stale issues and pull request. See ``staleOptions`` for options. Default: true
        :param stale_options: (experimental) Auto-close stale issues and pull requests. To disable set ``stale`` to ``false``. Default: - see defaults in ``StaleOptions``
        :param vscode: (experimental) Enable VSCode integration. Enabled by default for root projects. Disabled for non-root projects. Default: true

        :stability: experimental
        '''
        if isinstance(logging, dict):
            logging = _LoggerOptions_eb0f6309(**logging)
        if isinstance(projenrc_json_options, dict):
            projenrc_json_options = _ProjenrcOptions_164bd039(**projenrc_json_options)
        if isinstance(auto_approve_options, dict):
            auto_approve_options = AutoApproveOptions(**auto_approve_options)
        if isinstance(auto_merge_options, dict):
            auto_merge_options = AutoMergeOptions(**auto_merge_options)
        if isinstance(github_options, dict):
            github_options = GitHubOptions(**github_options)
        if isinstance(mergify_options, dict):
            mergify_options = MergifyOptions(**mergify_options)
        if isinstance(readme, dict):
            readme = _SampleReadmeProps_3518b03b(**readme)
        if isinstance(stale_options, dict):
            stale_options = StaleOptions(**stale_options)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if logging is not None:
            self._values["logging"] = logging
        if outdir is not None:
            self._values["outdir"] = outdir
        if parent is not None:
            self._values["parent"] = parent
        if projen_command is not None:
            self._values["projen_command"] = projen_command
        if projenrc_json is not None:
            self._values["projenrc_json"] = projenrc_json
        if projenrc_json_options is not None:
            self._values["projenrc_json_options"] = projenrc_json_options
        if auto_approve_options is not None:
            self._values["auto_approve_options"] = auto_approve_options
        if auto_merge_options is not None:
            self._values["auto_merge_options"] = auto_merge_options
        if clobber is not None:
            self._values["clobber"] = clobber
        if dev_container is not None:
            self._values["dev_container"] = dev_container
        if github is not None:
            self._values["github"] = github
        if github_options is not None:
            self._values["github_options"] = github_options
        if gitpod is not None:
            self._values["gitpod"] = gitpod
        if mergify is not None:
            self._values["mergify"] = mergify
        if mergify_options is not None:
            self._values["mergify_options"] = mergify_options
        if project_type is not None:
            self._values["project_type"] = project_type
        if projen_token_secret is not None:
            self._values["projen_token_secret"] = projen_token_secret
        if readme is not None:
            self._values["readme"] = readme
        if stale is not None:
            self._values["stale"] = stale
        if stale_options is not None:
            self._values["stale_options"] = stale_options
        if vscode is not None:
            self._values["vscode"] = vscode

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) This is the name of your project.

        :default: $BASEDIR

        :stability: experimental
        :featured: true
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logging(self) -> typing.Optional[_LoggerOptions_eb0f6309]:
        '''(experimental) Configure logging options such as verbosity.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_LoggerOptions_eb0f6309], result)

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''(experimental) The root directory of the project.

        Relative to this directory, all files are synthesized.

        If this project has a parent, this directory is relative to the parent
        directory and it cannot be the same as the parent or any of it's other
        sub-projects.

        :default: "."

        :stability: experimental
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent(self) -> typing.Optional[_Project_57d89203]:
        '''(experimental) The parent project, if this project is part of a bigger project.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional[_Project_57d89203], result)

    @builtins.property
    def projen_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) The shell command to use in order to run the projen CLI.

        Can be used to customize in special environments.

        :default: "npx projen"

        :stability: experimental
        '''
        result = self._values.get("projen_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def projenrc_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Generate (once) .projenrc.json (in JSON). Set to ``false`` in order to disable .projenrc.json generation.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("projenrc_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def projenrc_json_options(self) -> typing.Optional[_ProjenrcOptions_164bd039]:
        '''(experimental) Options for .projenrc.json.

        :default: - default options

        :stability: experimental
        '''
        result = self._values.get("projenrc_json_options")
        return typing.cast(typing.Optional[_ProjenrcOptions_164bd039], result)

    @builtins.property
    def auto_approve_options(self) -> typing.Optional[AutoApproveOptions]:
        '''(experimental) Enable and configure the 'auto approve' workflow.

        :default: - auto approve is disabled

        :stability: experimental
        '''
        result = self._values.get("auto_approve_options")
        return typing.cast(typing.Optional[AutoApproveOptions], result)

    @builtins.property
    def auto_merge_options(self) -> typing.Optional[AutoMergeOptions]:
        '''(experimental) Configure options for automatic merging on GitHub.

        Has no effect if
        ``github.mergify`` is set to false.

        :default: - see defaults in ``AutoMergeOptions``

        :stability: experimental
        '''
        result = self._values.get("auto_merge_options")
        return typing.cast(typing.Optional[AutoMergeOptions], result)

    @builtins.property
    def clobber(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a ``clobber`` task which resets the repo to origin.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("clobber")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def dev_container(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a VSCode development environment (used for GitHub Codespaces).

        :default: false

        :stability: experimental
        '''
        result = self._values.get("dev_container")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable GitHub integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def github_options(self) -> typing.Optional[GitHubOptions]:
        '''(experimental) Options for GitHub integration.

        :default: - see GitHubOptions

        :stability: experimental
        '''
        result = self._values.get("github_options")
        return typing.cast(typing.Optional[GitHubOptions], result)

    @builtins.property
    def gitpod(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Add a Gitpod development environment.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("gitpod")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Whether mergify should be enabled on this repository or not.

        :default: true

        :deprecated: use ``githubOptions.mergify`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def mergify_options(self) -> typing.Optional["MergifyOptions"]:
        '''(deprecated) Options for mergify.

        :default: - default options

        :deprecated: use ``githubOptions.mergifyOptions`` instead

        :stability: deprecated
        '''
        result = self._values.get("mergify_options")
        return typing.cast(typing.Optional["MergifyOptions"], result)

    @builtins.property
    def project_type(self) -> typing.Optional[_ProjectType_fd80c725]:
        '''(deprecated) Which type of project this is (library/app).

        :default: ProjectType.UNKNOWN

        :deprecated: no longer supported at the base project level

        :stability: deprecated
        '''
        result = self._values.get("project_type")
        return typing.cast(typing.Optional[_ProjectType_fd80c725], result)

    @builtins.property
    def projen_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of a secret which includes a GitHub Personal Access Token to be used by projen workflows.

        This token needs to have the ``repo``, ``workflows``
        and ``packages`` scope.

        :default: "PROJEN_GITHUB_TOKEN"

        :stability: experimental
        '''
        result = self._values.get("projen_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def readme(self) -> typing.Optional[_SampleReadmeProps_3518b03b]:
        '''(experimental) The README setup.

        :default: - { filename: 'README.md', contents: '# replace this' }

        :stability: experimental

        Example::

            "{ filename: 'readme.md', contents: '# title' }"
        '''
        result = self._values.get("readme")
        return typing.cast(typing.Optional[_SampleReadmeProps_3518b03b], result)

    @builtins.property
    def stale(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Auto-close of stale issues and pull request.

        See ``staleOptions`` for options.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("stale")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_options(self) -> typing.Optional["StaleOptions"]:
        '''(experimental) Auto-close stale issues and pull requests.

        To disable set ``stale`` to ``false``.

        :default: - see defaults in ``StaleOptions``

        :stability: experimental
        '''
        result = self._values.get("stale_options")
        return typing.cast(typing.Optional["StaleOptions"], result)

    @builtins.property
    def vscode(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable VSCode integration.

        Enabled by default for root projects. Disabled for non-root projects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("vscode")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.GitIdentity",
    jsii_struct_bases=[],
    name_mapping={"email": "email", "name": "name"},
)
class GitIdentity:
    def __init__(self, *, email: builtins.str, name: builtins.str) -> None:
        '''(experimental) Represents the git identity.

        :param email: (experimental) The email address of the git user.
        :param name: (experimental) The name of the user.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
            "name": name,
        }

    @builtins.property
    def email(self) -> builtins.str:
        '''(experimental) The email address of the git user.

        :stability: experimental
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the user.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitIdentity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GithubWorkflow(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.GithubWorkflow",
):
    '''(experimental) Workflow for GitHub.

    A workflow is a configurable automated process made up of one or more jobs.

    :see: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        name: builtins.str,
        *,
        concurrency: typing.Optional[builtins.str] = None,
        force: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param github: -
        :param name: -
        :param concurrency: (experimental) Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time. Currently in beta. Default: - disabled
        :param force: (experimental) Force the creation of the workflow even if ``workflows`` is disabled in ``GitHub``. Default: false

        :stability: experimental
        '''
        options = GithubWorkflowOptions(concurrency=concurrency, force=force)

        jsii.create(self.__class__, self, [github, name, options])

    @jsii.member(jsii_name="addJob")
    def add_job(
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
        '''(experimental) Adds a single job to the workflow.

        :param id: The job name (unique within the workflow).
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

        return typing.cast(None, jsii.invoke(self, "addJob", [id, job]))

    @jsii.member(jsii_name="addJobs")
    def add_jobs(self, jobs: typing.Mapping[builtins.str, _Job_20ffcf45]) -> None:
        '''(experimental) Add jobs to the workflow.

        :param jobs: Jobs to add.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addJobs", [jobs]))

    @jsii.member(jsii_name="on")
    def on(
        self,
        *,
        branch_protection_rule: typing.Optional[_BranchProtectionRuleOptions_422f7f4e] = None,
        check_run: typing.Optional[_CheckRunOptions_66af1ceb] = None,
        check_suite: typing.Optional[_CheckSuiteOptions_6a122376] = None,
        create: typing.Optional[_CreateOptions_6247308d] = None,
        delete: typing.Optional[_DeleteOptions_c46578d4] = None,
        deployment: typing.Optional[_DeploymentOptions_0bea6580] = None,
        deployment_status: typing.Optional[_DeploymentStatusOptions_f9cbd32b] = None,
        discussion: typing.Optional[_DiscussionOptions_6b34c7b6] = None,
        discussion_comment: typing.Optional[_DiscussionCommentOptions_e8674c31] = None,
        fork: typing.Optional[_ForkOptions_0437229d] = None,
        gollum: typing.Optional[_GollumOptions_1acffea2] = None,
        issue_comment: typing.Optional[_IssueCommentOptions_b551b1e5] = None,
        issues: typing.Optional[_IssuesOptions_dd89885c] = None,
        label: typing.Optional[_LabelOptions_ca474a61] = None,
        milestone: typing.Optional[_MilestoneOptions_6f9d8b6f] = None,
        page_build: typing.Optional[_PageBuildOptions_c30eafce] = None,
        project: typing.Optional[_ProjectOptions_50d963ea] = None,
        project_card: typing.Optional[_ProjectCardOptions_c89fc28d] = None,
        project_column: typing.Optional[_ProjectColumnOptions_25a462f6] = None,
        public: typing.Optional[_PublicOptions_2c3a3b94] = None,
        pull_request: typing.Optional[_PullRequestOptions_b051b0c9] = None,
        pull_request_review: typing.Optional[_PullRequestReviewOptions_27fd8e95] = None,
        pull_request_review_comment: typing.Optional[_PullRequestReviewCommentOptions_85235a68] = None,
        pull_request_target: typing.Optional[_PullRequestTargetOptions_81011bb1] = None,
        push: typing.Optional[_PushOptions_63e1c4f2] = None,
        registry_package: typing.Optional[_RegistryPackageOptions_781d5ac7] = None,
        release: typing.Optional[_ReleaseOptions_d152186d] = None,
        repository_dispatch: typing.Optional[_RepositoryDispatchOptions_d75e9903] = None,
        schedule: typing.Optional[typing.Sequence[_CronScheduleOptions_7724cd93]] = None,
        status: typing.Optional[_StatusOptions_aa35df44] = None,
        watch: typing.Optional[_WatchOptions_d33f5d00] = None,
        workflow_call: typing.Optional[_WorkflowCallOptions_bc57a5b4] = None,
        workflow_dispatch: typing.Optional[_WorkflowDispatchOptions_7110ffdc] = None,
        workflow_run: typing.Optional[_WorkflowRunOptions_5a4262c5] = None,
    ) -> None:
        '''(experimental) Add events to triggers the workflow.

        :param branch_protection_rule: (experimental) Runs your workflow anytime the branch_protection_rule event occurs.
        :param check_run: (experimental) Runs your workflow anytime the check_run event occurs.
        :param check_suite: (experimental) Runs your workflow anytime the check_suite event occurs.
        :param create: (experimental) Runs your workflow anytime someone creates a branch or tag, which triggers the create event.
        :param delete: (experimental) Runs your workflow anytime someone deletes a branch or tag, which triggers the delete event.
        :param deployment: (experimental) Runs your workflow anytime someone creates a deployment, which triggers the deployment event. Deployments created with a commit SHA may not have a Git ref.
        :param deployment_status: (experimental) Runs your workflow anytime a third party provides a deployment status, which triggers the deployment_status event. Deployments created with a commit SHA may not have a Git ref.
        :param discussion: (experimental) Runs your workflow anytime the discussion event occurs. More than one activity type triggers this event.
        :param discussion_comment: (experimental) Runs your workflow anytime the discussion_comment event occurs. More than one activity type triggers this event.
        :param fork: (experimental) Runs your workflow anytime when someone forks a repository, which triggers the fork event.
        :param gollum: (experimental) Runs your workflow when someone creates or updates a Wiki page, which triggers the gollum event.
        :param issue_comment: (experimental) Runs your workflow anytime the issue_comment event occurs.
        :param issues: (experimental) Runs your workflow anytime the issues event occurs.
        :param label: (experimental) Runs your workflow anytime the label event occurs.
        :param milestone: (experimental) Runs your workflow anytime the milestone event occurs.
        :param page_build: (experimental) Runs your workflow anytime someone pushes to a GitHub Pages-enabled branch, which triggers the page_build event.
        :param project: (experimental) Runs your workflow anytime the project event occurs.
        :param project_card: (experimental) Runs your workflow anytime the project_card event occurs.
        :param project_column: (experimental) Runs your workflow anytime the project_column event occurs.
        :param public: (experimental) Runs your workflow anytime someone makes a private repository public, which triggers the public event.
        :param pull_request: (experimental) Runs your workflow anytime the pull_request event occurs.
        :param pull_request_review: (experimental) Runs your workflow anytime the pull_request_review event occurs.
        :param pull_request_review_comment: (experimental) Runs your workflow anytime a comment on a pull request's unified diff is modified, which triggers the pull_request_review_comment event.
        :param pull_request_target: (experimental) This event runs in the context of the base of the pull request, rather than in the merge commit as the pull_request event does. This prevents executing unsafe workflow code from the head of the pull request that could alter your repository or steal any secrets you use in your workflow. This event allows you to do things like create workflows that label and comment on pull requests based on the contents of the event payload. WARNING: The ``pull_request_target`` event is granted read/write repository token and can access secrets, even when it is triggered from a fork. Although the workflow runs in the context of the base of the pull request, you should make sure that you do not check out, build, or run untrusted code from the pull request with this event. Additionally, any caches share the same scope as the base branch, and to help prevent cache poisoning, you should not save the cache if there is a possibility that the cache contents were altered.
        :param push: (experimental) Runs your workflow when someone pushes to a repository branch, which triggers the push event.
        :param registry_package: (experimental) Runs your workflow anytime a package is published or updated.
        :param release: (experimental) Runs your workflow anytime the release event occurs.
        :param repository_dispatch: (experimental) You can use the GitHub API to trigger a webhook event called repository_dispatch when you want to trigger a workflow for activity that happens outside of GitHub.
        :param schedule: (experimental) You can schedule a workflow to run at specific UTC times using POSIX cron syntax. Scheduled workflows run on the latest commit on the default or base branch. The shortest interval you can run scheduled workflows is once every 5 minutes.
        :param status: (experimental) Runs your workflow anytime the status of a Git commit changes, which triggers the status event.
        :param watch: (experimental) Runs your workflow anytime the watch event occurs.
        :param workflow_call: (experimental) Can be called from another workflow.
        :param workflow_dispatch: (experimental) You can configure custom-defined input properties, default input values, and required inputs for the event directly in your workflow. When the workflow runs, you can access the input values in the github.event.inputs context.
        :param workflow_run: (experimental) This event occurs when a workflow run is requested or completed, and allows you to execute a workflow based on the finished result of another workflow. A workflow run is triggered regardless of the result of the previous workflow.

        :stability: experimental
        '''
        events = _Triggers_e9ae7617(
            branch_protection_rule=branch_protection_rule,
            check_run=check_run,
            check_suite=check_suite,
            create=create,
            delete=delete,
            deployment=deployment,
            deployment_status=deployment_status,
            discussion=discussion,
            discussion_comment=discussion_comment,
            fork=fork,
            gollum=gollum,
            issue_comment=issue_comment,
            issues=issues,
            label=label,
            milestone=milestone,
            page_build=page_build,
            project=project,
            project_card=project_card,
            project_column=project_column,
            public=public,
            pull_request=pull_request,
            pull_request_review=pull_request_review,
            pull_request_review_comment=pull_request_review_comment,
            pull_request_target=pull_request_target,
            push=push,
            registry_package=registry_package,
            release=release,
            repository_dispatch=repository_dispatch,
            schedule=schedule,
            status=status,
            watch=watch,
            workflow_call=workflow_call,
            workflow_dispatch=workflow_dispatch,
            workflow_run=workflow_run,
        )

        return typing.cast(None, jsii.invoke(self, "on", [events]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the workflow.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="projenTokenSecret")
    def projen_token_secret(self) -> builtins.str:
        '''(experimental) The name of a secret that includes a PAT that can be used by workflows.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "projenTokenSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="concurrency")
    def concurrency(self) -> typing.Optional[builtins.str]:
        '''(experimental) Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time.

        :default: disabled

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "concurrency"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="file")
    def file(self) -> typing.Optional[_YamlFile_909731b0]:
        '''(experimental) The workflow YAML file.

        May not exist if ``workflowsEnabled`` is false on ``GitHub``.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_YamlFile_909731b0], jsii.get(self, "file"))


@jsii.data_type(
    jsii_type="projen.github.GithubWorkflowOptions",
    jsii_struct_bases=[],
    name_mapping={"concurrency": "concurrency", "force": "force"},
)
class GithubWorkflowOptions:
    def __init__(
        self,
        *,
        concurrency: typing.Optional[builtins.str] = None,
        force: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for ``GithubWorkflow``.

        :param concurrency: (experimental) Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time. Currently in beta. Default: - disabled
        :param force: (experimental) Force the creation of the workflow even if ``workflows`` is disabled in ``GitHub``. Default: false

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if concurrency is not None:
            self._values["concurrency"] = concurrency
        if force is not None:
            self._values["force"] = force

    @builtins.property
    def concurrency(self) -> typing.Optional[builtins.str]:
        '''(experimental) Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time.

        Currently in beta.

        :default: - disabled

        :see: https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions#concurrency
        :stability: experimental
        '''
        result = self._values.get("concurrency")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Force the creation of the workflow even if ``workflows`` is disabled in ``GitHub``.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("force")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubWorkflowOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="projen.github.IAddConditionsLater")
class IAddConditionsLater(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @jsii.member(jsii_name="render")
    def render(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        ...


class _IAddConditionsLaterProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "projen.github.IAddConditionsLater"

    @jsii.member(jsii_name="render")
    def render(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "render", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAddConditionsLater).__jsii_proxy_class__ = lambda : _IAddConditionsLaterProxy


@jsii.interface(jsii_type="projen.github.IJobProvider")
class IJobProvider(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @jsii.member(jsii_name="renderJobs")
    def render_jobs(self) -> typing.Mapping[builtins.str, _Job_20ffcf45]:
        '''(experimental) Generates a collection of named GitHub workflow jobs.

        :stability: experimental
        '''
        ...


class _IJobProviderProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "projen.github.IJobProvider"

    @jsii.member(jsii_name="renderJobs")
    def render_jobs(self) -> typing.Mapping[builtins.str, _Job_20ffcf45]:
        '''(experimental) Generates a collection of named GitHub workflow jobs.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, _Job_20ffcf45], jsii.invoke(self, "renderJobs", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJobProvider).__jsii_proxy_class__ = lambda : _IJobProviderProxy


class Mergify(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.Mergify",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        *,
        queues: typing.Optional[typing.Sequence["MergifyQueue"]] = None,
        rules: typing.Optional[typing.Sequence["MergifyRule"]] = None,
    ) -> None:
        '''
        :param github: -
        :param queues: 
        :param rules: 

        :stability: experimental
        '''
        options = MergifyOptions(queues=queues, rules=rules)

        jsii.create(self.__class__, self, [github, options])

    @jsii.member(jsii_name="addQueue")
    def add_queue(
        self,
        *,
        conditions: typing.Sequence[typing.Union[builtins.str, "MergifyConditionalOperator"]],
        name: builtins.str,
    ) -> None:
        '''
        :param conditions: (experimental) A list of Conditions string that must match against the pull request for the pull request to be added to the queue.
        :param name: (experimental) The name of the queue.

        :stability: experimental
        '''
        queue = MergifyQueue(conditions=conditions, name=name)

        return typing.cast(None, jsii.invoke(self, "addQueue", [queue]))

    @jsii.member(jsii_name="addRule")
    def add_rule(
        self,
        *,
        actions: typing.Mapping[builtins.str, typing.Any],
        conditions: typing.Sequence[typing.Union[builtins.str, "MergifyConditionalOperator"]],
        name: builtins.str,
    ) -> None:
        '''
        :param actions: (experimental) A dictionary made of Actions that will be executed on the matching pull requests.
        :param conditions: (experimental) A list of Conditions string that must match against the pull request for the rule to be applied.
        :param name: (experimental) The name of the rule. This is not used by the engine directly, but is used when reporting information about a rule.

        :stability: experimental
        '''
        rule = MergifyRule(actions=actions, conditions=conditions, name=name)

        return typing.cast(None, jsii.invoke(self, "addRule", [rule]))


@jsii.data_type(
    jsii_type="projen.github.MergifyConditionalOperator",
    jsii_struct_bases=[],
    name_mapping={"and_": "and", "or_": "or"},
)
class MergifyConditionalOperator:
    def __init__(
        self,
        *,
        and_: typing.Optional[typing.Sequence[typing.Union[builtins.str, "MergifyConditionalOperator"]]] = None,
        or_: typing.Optional[typing.Sequence[typing.Union[builtins.str, "MergifyConditionalOperator"]]] = None,
    ) -> None:
        '''(experimental) The Mergify conditional operators that can be used are: ``or`` and ``and``.

        Note: The number of nested conditions is limited to 3.

        :param and_: 
        :param or_: 

        :see: https://docs.mergify.io/conditions/#combining-conditions-with-operators
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if and_ is not None:
            self._values["and_"] = and_
        if or_ is not None:
            self._values["or_"] = or_

    @builtins.property
    def and_(
        self,
    ) -> typing.Optional[typing.List[typing.Union[builtins.str, "MergifyConditionalOperator"]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("and_")
        return typing.cast(typing.Optional[typing.List[typing.Union[builtins.str, "MergifyConditionalOperator"]]], result)

    @builtins.property
    def or_(
        self,
    ) -> typing.Optional[typing.List[typing.Union[builtins.str, "MergifyConditionalOperator"]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("or_")
        return typing.cast(typing.Optional[typing.List[typing.Union[builtins.str, "MergifyConditionalOperator"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MergifyConditionalOperator(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.MergifyOptions",
    jsii_struct_bases=[],
    name_mapping={"queues": "queues", "rules": "rules"},
)
class MergifyOptions:
    def __init__(
        self,
        *,
        queues: typing.Optional[typing.Sequence["MergifyQueue"]] = None,
        rules: typing.Optional[typing.Sequence["MergifyRule"]] = None,
    ) -> None:
        '''
        :param queues: 
        :param rules: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if queues is not None:
            self._values["queues"] = queues
        if rules is not None:
            self._values["rules"] = rules

    @builtins.property
    def queues(self) -> typing.Optional[typing.List["MergifyQueue"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("queues")
        return typing.cast(typing.Optional[typing.List["MergifyQueue"]], result)

    @builtins.property
    def rules(self) -> typing.Optional[typing.List["MergifyRule"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List["MergifyRule"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MergifyOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.MergifyQueue",
    jsii_struct_bases=[],
    name_mapping={"conditions": "conditions", "name": "name"},
)
class MergifyQueue:
    def __init__(
        self,
        *,
        conditions: typing.Sequence[typing.Union[builtins.str, MergifyConditionalOperator]],
        name: builtins.str,
    ) -> None:
        '''
        :param conditions: (experimental) A list of Conditions string that must match against the pull request for the pull request to be added to the queue.
        :param name: (experimental) The name of the queue.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "conditions": conditions,
            "name": name,
        }

    @builtins.property
    def conditions(
        self,
    ) -> typing.List[typing.Union[builtins.str, MergifyConditionalOperator]]:
        '''(experimental) A list of Conditions string that must match against the pull request for the pull request to be added to the queue.

        :see: https://docs.mergify.com/conditions/#conditions
        :stability: experimental
        '''
        result = self._values.get("conditions")
        assert result is not None, "Required property 'conditions' is missing"
        return typing.cast(typing.List[typing.Union[builtins.str, MergifyConditionalOperator]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the queue.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MergifyQueue(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.MergifyRule",
    jsii_struct_bases=[],
    name_mapping={"actions": "actions", "conditions": "conditions", "name": "name"},
)
class MergifyRule:
    def __init__(
        self,
        *,
        actions: typing.Mapping[builtins.str, typing.Any],
        conditions: typing.Sequence[typing.Union[builtins.str, MergifyConditionalOperator]],
        name: builtins.str,
    ) -> None:
        '''
        :param actions: (experimental) A dictionary made of Actions that will be executed on the matching pull requests.
        :param conditions: (experimental) A list of Conditions string that must match against the pull request for the rule to be applied.
        :param name: (experimental) The name of the rule. This is not used by the engine directly, but is used when reporting information about a rule.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "actions": actions,
            "conditions": conditions,
            "name": name,
        }

    @builtins.property
    def actions(self) -> typing.Mapping[builtins.str, typing.Any]:
        '''(experimental) A dictionary made of Actions that will be executed on the matching pull requests.

        :see: https://docs.mergify.io/actions/#actions
        :stability: experimental
        '''
        result = self._values.get("actions")
        assert result is not None, "Required property 'actions' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.Any], result)

    @builtins.property
    def conditions(
        self,
    ) -> typing.List[typing.Union[builtins.str, MergifyConditionalOperator]]:
        '''(experimental) A list of Conditions string that must match against the pull request for the rule to be applied.

        :see: https://docs.mergify.io/conditions/#conditions
        :stability: experimental
        '''
        result = self._values.get("conditions")
        assert result is not None, "Required property 'conditions' is missing"
        return typing.cast(typing.List[typing.Union[builtins.str, MergifyConditionalOperator]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name of the rule.

        This is not used by the engine directly,
        but is used when reporting information about a rule.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MergifyRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PullRequestLint(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.PullRequestLint",
):
    '''(experimental) Configure validations to run on GitHub pull requests.

    Only generates a file if at least one linter is configured.

    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        *,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        semantic_title: typing.Optional[builtins.bool] = None,
        semantic_title_options: typing.Optional["SemanticTitleOptions"] = None,
    ) -> None:
        '''
        :param github: -
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param semantic_title: (experimental) Validate that pull request titles follow Conventional Commits. Default: true
        :param semantic_title_options: (experimental) Options for validating the conventional commit title linter. Default: - title must start with "feat", "fix", or "chore"

        :stability: experimental
        '''
        options = PullRequestLintOptions(
            runs_on=runs_on,
            semantic_title=semantic_title,
            semantic_title_options=semantic_title_options,
        )

        jsii.create(self.__class__, self, [github, options])


@jsii.data_type(
    jsii_type="projen.github.PullRequestLintOptions",
    jsii_struct_bases=[],
    name_mapping={
        "runs_on": "runsOn",
        "semantic_title": "semanticTitle",
        "semantic_title_options": "semanticTitleOptions",
    },
)
class PullRequestLintOptions:
    def __init__(
        self,
        *,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        semantic_title: typing.Optional[builtins.bool] = None,
        semantic_title_options: typing.Optional["SemanticTitleOptions"] = None,
    ) -> None:
        '''(experimental) Options for PullRequestLint.

        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param semantic_title: (experimental) Validate that pull request titles follow Conventional Commits. Default: true
        :param semantic_title_options: (experimental) Options for validating the conventional commit title linter. Default: - title must start with "feat", "fix", or "chore"

        :stability: experimental
        '''
        if isinstance(semantic_title_options, dict):
            semantic_title_options = SemanticTitleOptions(**semantic_title_options)
        self._values: typing.Dict[str, typing.Any] = {}
        if runs_on is not None:
            self._values["runs_on"] = runs_on
        if semantic_title is not None:
            self._values["semantic_title"] = semantic_title
        if semantic_title_options is not None:
            self._values["semantic_title_options"] = semantic_title_options

    @builtins.property
    def runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def semantic_title(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Validate that pull request titles follow Conventional Commits.

        :default: true

        :see: https://www.conventionalcommits.org/
        :stability: experimental
        '''
        result = self._values.get("semantic_title")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def semantic_title_options(self) -> typing.Optional["SemanticTitleOptions"]:
        '''(experimental) Options for validating the conventional commit title linter.

        :default: - title must start with "feat", "fix", or "chore"

        :stability: experimental
        '''
        result = self._values.get("semantic_title_options")
        return typing.cast(typing.Optional["SemanticTitleOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PullRequestLintOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PullRequestTemplate(
    _TextFile_4a74808c,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.PullRequestTemplate",
):
    '''(experimental) Template for GitHub pull requests.

    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        *,
        lines: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param github: -
        :param lines: (experimental) The contents of the template. You can use ``addLine()`` to add additional lines. Default: - a standard default template will be created.

        :stability: experimental
        '''
        options = PullRequestTemplateOptions(lines=lines)

        jsii.create(self.__class__, self, [github, options])


@jsii.data_type(
    jsii_type="projen.github.PullRequestTemplateOptions",
    jsii_struct_bases=[],
    name_mapping={"lines": "lines"},
)
class PullRequestTemplateOptions:
    def __init__(
        self,
        *,
        lines: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Options for ``PullRequestTemplate``.

        :param lines: (experimental) The contents of the template. You can use ``addLine()`` to add additional lines. Default: - a standard default template will be created.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if lines is not None:
            self._values["lines"] = lines

    @builtins.property
    def lines(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) The contents of the template.

        You can use ``addLine()`` to add additional lines.

        :default: - a standard default template will be created.

        :stability: experimental
        '''
        result = self._values.get("lines")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PullRequestTemplateOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.SemanticTitleOptions",
    jsii_struct_bases=[],
    name_mapping={"require_scope": "requireScope", "types": "types"},
)
class SemanticTitleOptions:
    def __init__(
        self,
        *,
        require_scope: typing.Optional[builtins.bool] = None,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Options for linting that PR titles follow Conventional Commits.

        :param require_scope: (experimental) Configure that a scope must always be provided. e.g. feat(ui), fix(core) Default: false
        :param types: (experimental) Configure a list of commit types that are allowed. Default: ["feat", "fix", "chore"]

        :see: https://www.conventionalcommits.org/
        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if require_scope is not None:
            self._values["require_scope"] = require_scope
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def require_scope(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Configure that a scope must always be provided.

        e.g. feat(ui), fix(core)

        :default: false

        :stability: experimental
        '''
        result = self._values.get("require_scope")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Configure a list of commit types that are allowed.

        :default: ["feat", "fix", "chore"]

        :stability: experimental
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SemanticTitleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Stale(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.Stale",
):
    '''(experimental) Warns and then closes issues and PRs that have had no activity for a specified amount of time.

    The default configuration will:

    - Add a "Stale" label to pull requests after 14 days and closed after 2 days
    - Add a "Stale" label to issues after 60 days and closed after 7 days
    - If a comment is added, the label will be removed and timer is restarted.

    :see: https://github.com/actions/stale
    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        *,
        issues: typing.Optional["StaleBehavior"] = None,
        pull_request: typing.Optional["StaleBehavior"] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param github: -
        :param issues: (experimental) How to handle stale issues. Default: - By default, stale issues with no activity will be marked as stale after 60 days and closed within 7 days.
        :param pull_request: (experimental) How to handle stale pull requests. Default: - By default, pull requests with no activity will be marked as stale after 14 days and closed within 2 days with relevant comments.
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]

        :stability: experimental
        '''
        options = StaleOptions(
            issues=issues, pull_request=pull_request, runs_on=runs_on
        )

        jsii.create(self.__class__, self, [github, options])


@jsii.data_type(
    jsii_type="projen.github.StaleBehavior",
    jsii_struct_bases=[],
    name_mapping={
        "close_message": "closeMessage",
        "days_before_close": "daysBeforeClose",
        "days_before_stale": "daysBeforeStale",
        "enabled": "enabled",
        "stale_label": "staleLabel",
        "stale_message": "staleMessage",
    },
)
class StaleBehavior:
    def __init__(
        self,
        *,
        close_message: typing.Optional[builtins.str] = None,
        days_before_close: typing.Optional[jsii.Number] = None,
        days_before_stale: typing.Optional[jsii.Number] = None,
        enabled: typing.Optional[builtins.bool] = None,
        stale_label: typing.Optional[builtins.str] = None,
        stale_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Stale behavior.

        :param close_message: (experimental) The comment to add to the issue/PR when it's closed. Default: "Closing this pull request as it hasn't seen activity for a while. Please add a comment
        :param days_before_close: (experimental) Days until the issue/PR is closed after it is marked as "Stale". Set to -1 to disable. Default: -
        :param days_before_stale: (experimental) How many days until the issue or pull request is marked as "Stale". Set to -1 to disable. Default: -
        :param enabled: (experimental) Determines if this behavior is enabled. Same as setting ``daysBeforeStale`` and ``daysBeforeClose`` to ``-1``. Default: true
        :param stale_label: (experimental) The label to apply to the issue/PR when it becomes stale. Default: "Stale"
        :param stale_message: (experimental) The comment to add to the issue/PR when it becomes stale. Default: "This pull request is now marked as stale because hasn't seen activity for a while. Add a comment or it will be closed soon."

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if close_message is not None:
            self._values["close_message"] = close_message
        if days_before_close is not None:
            self._values["days_before_close"] = days_before_close
        if days_before_stale is not None:
            self._values["days_before_stale"] = days_before_stale
        if enabled is not None:
            self._values["enabled"] = enabled
        if stale_label is not None:
            self._values["stale_label"] = stale_label
        if stale_message is not None:
            self._values["stale_message"] = stale_message

    @builtins.property
    def close_message(self) -> typing.Optional[builtins.str]:
        '''(experimental) The comment to add to the issue/PR when it's closed.

        :default: "Closing this pull request as it hasn't seen activity for a while. Please add a comment

        :stability: experimental
        :mentioning: a maintainer when you are ready to continue."
        '''
        result = self._values.get("close_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def days_before_close(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Days until the issue/PR is closed after it is marked as "Stale".

        Set to -1 to disable.

        :default: -

        :stability: experimental
        '''
        result = self._values.get("days_before_close")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def days_before_stale(self) -> typing.Optional[jsii.Number]:
        '''(experimental) How many days until the issue or pull request is marked as "Stale".

        Set to -1 to disable.

        :default: -

        :stability: experimental
        '''
        result = self._values.get("days_before_stale")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Determines if this behavior is enabled.

        Same as setting ``daysBeforeStale`` and ``daysBeforeClose`` to ``-1``.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stale_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to the issue/PR when it becomes stale.

        :default: "Stale"

        :stability: experimental
        '''
        result = self._values.get("stale_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stale_message(self) -> typing.Optional[builtins.str]:
        '''(experimental) The comment to add to the issue/PR when it becomes stale.

        :default: "This pull request is now marked as stale because hasn't seen activity for a while. Add a comment or it will be closed soon."

        :stability: experimental
        '''
        result = self._values.get("stale_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaleBehavior(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.github.StaleOptions",
    jsii_struct_bases=[],
    name_mapping={
        "issues": "issues",
        "pull_request": "pullRequest",
        "runs_on": "runsOn",
    },
)
class StaleOptions:
    def __init__(
        self,
        *,
        issues: typing.Optional[StaleBehavior] = None,
        pull_request: typing.Optional[StaleBehavior] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Options for ``Stale``.

        :param issues: (experimental) How to handle stale issues. Default: - By default, stale issues with no activity will be marked as stale after 60 days and closed within 7 days.
        :param pull_request: (experimental) How to handle stale pull requests. Default: - By default, pull requests with no activity will be marked as stale after 14 days and closed within 2 days with relevant comments.
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]

        :stability: experimental
        '''
        if isinstance(issues, dict):
            issues = StaleBehavior(**issues)
        if isinstance(pull_request, dict):
            pull_request = StaleBehavior(**pull_request)
        self._values: typing.Dict[str, typing.Any] = {}
        if issues is not None:
            self._values["issues"] = issues
        if pull_request is not None:
            self._values["pull_request"] = pull_request
        if runs_on is not None:
            self._values["runs_on"] = runs_on

    @builtins.property
    def issues(self) -> typing.Optional[StaleBehavior]:
        '''(experimental) How to handle stale issues.

        :default:

        - By default, stale issues with no activity will be marked as
        stale after 60 days and closed within 7 days.

        :stability: experimental
        '''
        result = self._values.get("issues")
        return typing.cast(typing.Optional[StaleBehavior], result)

    @builtins.property
    def pull_request(self) -> typing.Optional[StaleBehavior]:
        '''(experimental) How to handle stale pull requests.

        :default:

        - By default, pull requests with no activity will be marked as
        stale after 14 days and closed within 2 days with relevant comments.

        :stability: experimental
        '''
        result = self._values.get("pull_request")
        return typing.cast(typing.Optional[StaleBehavior], result)

    @builtins.property
    def runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TaskWorkflow(
    GithubWorkflow,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.github.TaskWorkflow",
):
    '''(experimental) A GitHub workflow for common build tasks within a project.

    :stability: experimental
    '''

    def __init__(
        self,
        github: GitHub,
        *,
        name: builtins.str,
        permissions: _JobPermissions_3b5b53dc,
        task: _Task_9fa875b6,
        artifacts_directory: typing.Optional[builtins.str] = None,
        checkout_with: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        condition: typing.Optional[builtins.str] = None,
        container: typing.Optional[_ContainerOptions_f50907af] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        git_identity: typing.Optional[GitIdentity] = None,
        job_id: typing.Optional[builtins.str] = None,
        outputs: typing.Optional[typing.Mapping[builtins.str, _JobStepOutput_acebe827]] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_checkout_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        triggers: typing.Optional[_Triggers_e9ae7617] = None,
    ) -> None:
        '''
        :param github: -
        :param name: (experimental) The workflow name.
        :param permissions: (experimental) Permissions for the build job.
        :param task: (experimental) The main task to be executed.
        :param artifacts_directory: (experimental) A directory name which contains artifacts to be uploaded (e.g. ``dist``). If this is set, the contents of this directory will be uploaded as an artifact at the end of the workflow run, even if other steps fail. Default: - not set
        :param checkout_with: (experimental) Override for the ``with`` property of the source code checkout step. Default: - not set
        :param condition: (experimental) Adds an 'if' condition to the workflow.
        :param container: Default: - default image
        :param env: (experimental) Workflow environment variables. Default: {}
        :param git_identity: (experimental) The git identity to use in this workflow.
        :param job_id: (experimental) The primary job id. Default: "build"
        :param outputs: (experimental) Mapping of job output names to values/expressions. Default: {}
        :param post_build_steps: (experimental) Actions to run after the main build step. Default: - not set
        :param pre_build_steps: (experimental) Steps to run before the main build step. Default: - not set
        :param pre_checkout_steps: (experimental) Initial steps to run before the source code checkout. Default: - not set
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param triggers: (experimental) The triggers for the workflow. Default: - by default workflows can only be triggered by manually.

        :stability: experimental
        '''
        options = TaskWorkflowOptions(
            name=name,
            permissions=permissions,
            task=task,
            artifacts_directory=artifacts_directory,
            checkout_with=checkout_with,
            condition=condition,
            container=container,
            env=env,
            git_identity=git_identity,
            job_id=job_id,
            outputs=outputs,
            post_build_steps=post_build_steps,
            pre_build_steps=pre_build_steps,
            pre_checkout_steps=pre_checkout_steps,
            runs_on=runs_on,
            triggers=triggers,
        )

        jsii.create(self.__class__, self, [github, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jobId")
    def job_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jobId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactsDirectory")
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "artifactsDirectory"))


@jsii.data_type(
    jsii_type="projen.github.TaskWorkflowOptions",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "permissions": "permissions",
        "task": "task",
        "artifacts_directory": "artifactsDirectory",
        "checkout_with": "checkoutWith",
        "condition": "condition",
        "container": "container",
        "env": "env",
        "git_identity": "gitIdentity",
        "job_id": "jobId",
        "outputs": "outputs",
        "post_build_steps": "postBuildSteps",
        "pre_build_steps": "preBuildSteps",
        "pre_checkout_steps": "preCheckoutSteps",
        "runs_on": "runsOn",
        "triggers": "triggers",
    },
)
class TaskWorkflowOptions:
    def __init__(
        self,
        *,
        name: builtins.str,
        permissions: _JobPermissions_3b5b53dc,
        task: _Task_9fa875b6,
        artifacts_directory: typing.Optional[builtins.str] = None,
        checkout_with: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        condition: typing.Optional[builtins.str] = None,
        container: typing.Optional[_ContainerOptions_f50907af] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        git_identity: typing.Optional[GitIdentity] = None,
        job_id: typing.Optional[builtins.str] = None,
        outputs: typing.Optional[typing.Mapping[builtins.str, _JobStepOutput_acebe827]] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        pre_checkout_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        triggers: typing.Optional[_Triggers_e9ae7617] = None,
    ) -> None:
        '''
        :param name: (experimental) The workflow name.
        :param permissions: (experimental) Permissions for the build job.
        :param task: (experimental) The main task to be executed.
        :param artifacts_directory: (experimental) A directory name which contains artifacts to be uploaded (e.g. ``dist``). If this is set, the contents of this directory will be uploaded as an artifact at the end of the workflow run, even if other steps fail. Default: - not set
        :param checkout_with: (experimental) Override for the ``with`` property of the source code checkout step. Default: - not set
        :param condition: (experimental) Adds an 'if' condition to the workflow.
        :param container: Default: - default image
        :param env: (experimental) Workflow environment variables. Default: {}
        :param git_identity: (experimental) The git identity to use in this workflow.
        :param job_id: (experimental) The primary job id. Default: "build"
        :param outputs: (experimental) Mapping of job output names to values/expressions. Default: {}
        :param post_build_steps: (experimental) Actions to run after the main build step. Default: - not set
        :param pre_build_steps: (experimental) Steps to run before the main build step. Default: - not set
        :param pre_checkout_steps: (experimental) Initial steps to run before the source code checkout. Default: - not set
        :param runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param triggers: (experimental) The triggers for the workflow. Default: - by default workflows can only be triggered by manually.

        :stability: experimental
        '''
        if isinstance(permissions, dict):
            permissions = _JobPermissions_3b5b53dc(**permissions)
        if isinstance(container, dict):
            container = _ContainerOptions_f50907af(**container)
        if isinstance(git_identity, dict):
            git_identity = GitIdentity(**git_identity)
        if isinstance(triggers, dict):
            triggers = _Triggers_e9ae7617(**triggers)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "permissions": permissions,
            "task": task,
        }
        if artifacts_directory is not None:
            self._values["artifacts_directory"] = artifacts_directory
        if checkout_with is not None:
            self._values["checkout_with"] = checkout_with
        if condition is not None:
            self._values["condition"] = condition
        if container is not None:
            self._values["container"] = container
        if env is not None:
            self._values["env"] = env
        if git_identity is not None:
            self._values["git_identity"] = git_identity
        if job_id is not None:
            self._values["job_id"] = job_id
        if outputs is not None:
            self._values["outputs"] = outputs
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if pre_build_steps is not None:
            self._values["pre_build_steps"] = pre_build_steps
        if pre_checkout_steps is not None:
            self._values["pre_checkout_steps"] = pre_checkout_steps
        if runs_on is not None:
            self._values["runs_on"] = runs_on
        if triggers is not None:
            self._values["triggers"] = triggers

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The workflow name.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def permissions(self) -> _JobPermissions_3b5b53dc:
        '''(experimental) Permissions for the build job.

        :stability: experimental
        '''
        result = self._values.get("permissions")
        assert result is not None, "Required property 'permissions' is missing"
        return typing.cast(_JobPermissions_3b5b53dc, result)

    @builtins.property
    def task(self) -> _Task_9fa875b6:
        '''(experimental) The main task to be executed.

        :stability: experimental
        '''
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(_Task_9fa875b6, result)

    @builtins.property
    def artifacts_directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) A directory name which contains artifacts to be uploaded (e.g. ``dist``). If this is set, the contents of this directory will be uploaded as an artifact at the end of the workflow run, even if other steps fail.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def checkout_with(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Override for the ``with`` property of the source code checkout step.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("checkout_with")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) Adds an 'if' condition to the workflow.

        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def container(self) -> typing.Optional[_ContainerOptions_f50907af]:
        '''
        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("container")
        return typing.cast(typing.Optional[_ContainerOptions_f50907af], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Workflow environment variables.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def git_identity(self) -> typing.Optional[GitIdentity]:
        '''(experimental) The git identity to use in this workflow.

        :stability: experimental
        '''
        result = self._values.get("git_identity")
        return typing.cast(typing.Optional[GitIdentity], result)

    @builtins.property
    def job_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The primary job id.

        :default: "build"

        :stability: experimental
        '''
        result = self._values.get("job_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outputs(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _JobStepOutput_acebe827]]:
        '''(experimental) Mapping of job output names to values/expressions.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("outputs")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _JobStepOutput_acebe827]], result)

    @builtins.property
    def post_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Actions to run after the main build step.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def pre_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to run before the main build step.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("pre_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def pre_checkout_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Initial steps to run before the source code checkout.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("pre_checkout_steps")
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
    def triggers(self) -> typing.Optional[_Triggers_e9ae7617]:
        '''(experimental) The triggers for the workflow.

        :default: - by default workflows can only be triggered by manually.

        :stability: experimental
        '''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[_Triggers_e9ae7617], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskWorkflowOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="projen.github.VersioningStrategy")
class VersioningStrategy(enum.Enum):
    '''(experimental) The strategy to use when edits manifest and lock files.

    :stability: experimental
    '''

    LOCKFILE_ONLY = "LOCKFILE_ONLY"
    '''(experimental) Only create pull requests to update lockfiles updates.

    Ignore any new
    versions that would require package manifest changes.

    :stability: experimental
    '''
    AUTO = "AUTO"
    '''(experimental) - For apps, the version requirements are increased.

    - For libraries, the range of versions is widened.

    :stability: experimental
    '''
    WIDEN = "WIDEN"
    '''(experimental) Relax the version requirement to include both the new and old version, when possible.

    :stability: experimental
    '''
    INCREASE = "INCREASE"
    '''(experimental) Always increase the version requirement to match the new version.

    :stability: experimental
    '''
    INCREASE_IF_NECESSARY = "INCREASE_IF_NECESSARY"
    '''(experimental) Increase the version requirement only when required by the new version.

    :stability: experimental
    '''


__all__ = [
    "AutoApprove",
    "AutoApproveOptions",
    "AutoMerge",
    "AutoMergeOptions",
    "Dependabot",
    "DependabotIgnore",
    "DependabotOptions",
    "DependabotRegistry",
    "DependabotRegistryType",
    "DependabotScheduleInterval",
    "GitHub",
    "GitHubOptions",
    "GitHubProject",
    "GitHubProjectOptions",
    "GitIdentity",
    "GithubWorkflow",
    "GithubWorkflowOptions",
    "IAddConditionsLater",
    "IJobProvider",
    "Mergify",
    "MergifyConditionalOperator",
    "MergifyOptions",
    "MergifyQueue",
    "MergifyRule",
    "PullRequestLint",
    "PullRequestLintOptions",
    "PullRequestTemplate",
    "PullRequestTemplateOptions",
    "SemanticTitleOptions",
    "Stale",
    "StaleBehavior",
    "StaleOptions",
    "TaskWorkflow",
    "TaskWorkflowOptions",
    "VersioningStrategy",
]

publication.publish()
