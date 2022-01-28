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
from ..github import GitHubProject as _GitHubProject_c48bc7ea
from ..github.workflows import (
    Job as _Job_20ffcf45, JobStep as _JobStep_c3287c05, Tools as _Tools_75b93a2a
)


@jsii.data_type(
    jsii_type="projen.release.BranchOptions",
    jsii_struct_bases=[],
    name_mapping={
        "major_version": "majorVersion",
        "npm_dist_tag": "npmDistTag",
        "prerelease": "prerelease",
        "tag_prefix": "tagPrefix",
        "workflow_name": "workflowName",
    },
)
class BranchOptions:
    def __init__(
        self,
        *,
        major_version: jsii.Number,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        prerelease: typing.Optional[builtins.str] = None,
        tag_prefix: typing.Optional[builtins.str] = None,
        workflow_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for a release branch.

        :param major_version: (experimental) The major versions released from this branch.
        :param npm_dist_tag: (experimental) The npm distribution tag to use for this branch. Default: "latest"
        :param prerelease: (experimental) Bump the version as a pre-release tag. Default: - normal releases
        :param tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param workflow_name: (experimental) The name of the release workflow. Default: "release-BRANCH"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "major_version": major_version,
        }
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if tag_prefix is not None:
            self._values["tag_prefix"] = tag_prefix
        if workflow_name is not None:
            self._values["workflow_name"] = workflow_name

    @builtins.property
    def major_version(self) -> jsii.Number:
        '''(experimental) The major versions released from this branch.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        assert result is not None, "Required property 'major_version' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npm distribution tag to use for this branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump the version as a pre-release tag.

        :default: - normal releases

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers.

        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: - no prefix

        :stability: experimental
        '''
        result = self._values.get("tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the release workflow.

        :default: "release-BRANCH"

        :stability: experimental
        '''
        result = self._values.get("workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.CodeArtifactOptions",
    jsii_struct_bases=[],
    name_mapping={
        "access_key_id_secret": "accessKeyIdSecret",
        "role_to_assume": "roleToAssume",
        "secret_access_key_secret": "secretAccessKeySecret",
    },
)
class CodeArtifactOptions:
    def __init__(
        self,
        *,
        access_key_id_secret: typing.Optional[builtins.str] = None,
        role_to_assume: typing.Optional[builtins.str] = None,
        secret_access_key_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_key_id_secret: (experimental) GitHub secret which contains the AWS access key ID to use when publishing packages to AWS CodeArtifact. This property must be specified only when publishing to AWS CodeArtifact (``registry`` contains AWS CodeArtifact URL). Default: "AWS_ACCESS_KEY_ID"
        :param role_to_assume: (experimental) ARN of AWS role to be assumed prior to get authorization token from AWS CodeArtifact This property must be specified only when publishing to AWS CodeArtifact (``registry`` contains AWS CodeArtifact URL). Default: undefined
        :param secret_access_key_secret: (experimental) GitHub secret which contains the AWS secret access key to use when publishing packages to AWS CodeArtifact. This property must be specified only when publishing to AWS CodeArtifact (``registry`` contains AWS CodeArtifact URL). Default: "AWS_SECRET_ACCESS_KEY"

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if access_key_id_secret is not None:
            self._values["access_key_id_secret"] = access_key_id_secret
        if role_to_assume is not None:
            self._values["role_to_assume"] = role_to_assume
        if secret_access_key_secret is not None:
            self._values["secret_access_key_secret"] = secret_access_key_secret

    @builtins.property
    def access_key_id_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the AWS access key ID to use when publishing packages to AWS CodeArtifact.

        This property must be specified only when publishing to AWS CodeArtifact (``registry`` contains AWS CodeArtifact URL).

        :default: "AWS_ACCESS_KEY_ID"

        :stability: experimental
        '''
        result = self._values.get("access_key_id_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_to_assume(self) -> typing.Optional[builtins.str]:
        '''(experimental) ARN of AWS role to be assumed prior to get authorization token from AWS CodeArtifact This property must be specified only when publishing to AWS CodeArtifact (``registry`` contains AWS CodeArtifact URL).

        :default: undefined

        :stability: experimental
        '''
        result = self._values.get("role_to_assume")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_access_key_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the AWS secret access key to use when publishing packages to AWS CodeArtifact.

        This property must be specified only when publishing to AWS CodeArtifact (``registry`` contains AWS CodeArtifact URL).

        :default: "AWS_SECRET_ACCESS_KEY"

        :stability: experimental
        '''
        result = self._values.get("secret_access_key_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeArtifactOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.CommonPublishOptions",
    jsii_struct_bases=[],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
    },
)
class CommonPublishOptions:
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Common publishing options.

        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed

        :stability: experimental
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.GitHubReleasesPublishOptions",
    jsii_struct_bases=[CommonPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "changelog_file": "changelogFile",
        "release_tag_file": "releaseTagFile",
        "version_file": "versionFile",
    },
)
class GitHubReleasesPublishOptions(CommonPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        changelog_file: builtins.str,
        release_tag_file: builtins.str,
        version_file: builtins.str,
    ) -> None:
        '''(experimental) Publishing options for GitHub releases.

        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param changelog_file: (experimental) The location of an .md file (relative to ``dist/``) that includes the changelog for the release.
        :param release_tag_file: (experimental) The location of a text file (relative to ``dist/``) that contains the release tag.
        :param version_file: (experimental) The location of a text file (relative to ``dist/``) that contains the version number.

        :stability: experimental
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        self._values: typing.Dict[str, typing.Any] = {
            "changelog_file": changelog_file,
            "release_tag_file": release_tag_file,
            "version_file": version_file,
        }
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def changelog_file(self) -> builtins.str:
        '''(experimental) The location of an .md file (relative to ``dist/``) that includes the changelog for the release.

        :stability: experimental

        Example::

            changelog.md
        '''
        result = self._values.get("changelog_file")
        assert result is not None, "Required property 'changelog_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def release_tag_file(self) -> builtins.str:
        '''(experimental) The location of a text file (relative to ``dist/``) that contains the release tag.

        :stability: experimental

        Example::

            releasetag.txt
        '''
        result = self._values.get("release_tag_file")
        assert result is not None, "Required property 'release_tag_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version_file(self) -> builtins.str:
        '''(experimental) The location of a text file (relative to ``dist/``) that contains the version number.

        :stability: experimental

        Example::

            version.txt
        '''
        result = self._values.get("version_file")
        assert result is not None, "Required property 'version_file' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubReleasesPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.GitPublishOptions",
    jsii_struct_bases=[],
    name_mapping={
        "changelog_file": "changelogFile",
        "release_tag_file": "releaseTagFile",
        "version_file": "versionFile",
        "git_branch": "gitBranch",
        "git_push_command": "gitPushCommand",
        "project_changelog_file": "projectChangelogFile",
    },
)
class GitPublishOptions:
    def __init__(
        self,
        *,
        changelog_file: builtins.str,
        release_tag_file: builtins.str,
        version_file: builtins.str,
        git_branch: typing.Optional[builtins.str] = None,
        git_push_command: typing.Optional[builtins.str] = None,
        project_changelog_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Publishing options for Git releases.

        :param changelog_file: (experimental) The location of an .md file (relative to ``dist/``) that includes the changelog for the release.
        :param release_tag_file: (experimental) The location of a text file (relative to ``dist/``) that contains the release tag.
        :param version_file: (experimental) The location of a text file (relative to ``dist/``) that contains the version number.
        :param git_branch: (experimental) Branch to push to. Default: "main"
        :param git_push_command: (experimental) Override git-push command. Set to an empty string to disable pushing.
        :param project_changelog_file: (experimental) The location of an .md file that includes the project-level changelog.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "changelog_file": changelog_file,
            "release_tag_file": release_tag_file,
            "version_file": version_file,
        }
        if git_branch is not None:
            self._values["git_branch"] = git_branch
        if git_push_command is not None:
            self._values["git_push_command"] = git_push_command
        if project_changelog_file is not None:
            self._values["project_changelog_file"] = project_changelog_file

    @builtins.property
    def changelog_file(self) -> builtins.str:
        '''(experimental) The location of an .md file (relative to ``dist/``) that includes the changelog for the release.

        :stability: experimental

        Example::

            changelog.md
        '''
        result = self._values.get("changelog_file")
        assert result is not None, "Required property 'changelog_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def release_tag_file(self) -> builtins.str:
        '''(experimental) The location of a text file (relative to ``dist/``) that contains the release tag.

        :stability: experimental

        Example::

            releasetag.txt
        '''
        result = self._values.get("release_tag_file")
        assert result is not None, "Required property 'release_tag_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version_file(self) -> builtins.str:
        '''(experimental) The location of a text file (relative to ``dist/``) that contains the version number.

        :stability: experimental

        Example::

            version.txt
        '''
        result = self._values.get("version_file")
        assert result is not None, "Required property 'version_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def git_branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) Branch to push to.

        :default: "main"

        :stability: experimental
        '''
        result = self._values.get("git_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_push_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) Override git-push command.

        Set to an empty string to disable pushing.

        :stability: experimental
        '''
        result = self._values.get("git_push_command")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_changelog_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The location of an .md file that includes the project-level changelog.

        :stability: experimental
        '''
        result = self._values.get("project_changelog_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.GoPublishOptions",
    jsii_struct_bases=[CommonPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "git_branch": "gitBranch",
        "git_commit_message": "gitCommitMessage",
        "github_repo": "githubRepo",
        "github_token_secret": "githubTokenSecret",
        "git_user_email": "gitUserEmail",
        "git_user_name": "gitUserName",
    },
)
class GoPublishOptions(CommonPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        git_branch: typing.Optional[builtins.str] = None,
        git_commit_message: typing.Optional[builtins.str] = None,
        github_repo: typing.Optional[builtins.str] = None,
        github_token_secret: typing.Optional[builtins.str] = None,
        git_user_email: typing.Optional[builtins.str] = None,
        git_user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param git_branch: (deprecated) Branch to push to. Default: "main"
        :param git_commit_message: (deprecated) The commit message. Default: "chore(release): $VERSION"
        :param github_repo: (deprecated) GitHub repository to push to. Default: - derived from ``moduleName``
        :param github_token_secret: (deprecated) The name of the secret that includes a personal GitHub access token used to push to the GitHub repository. Default: "GO_GITHUB_TOKEN"
        :param git_user_email: (deprecated) The email to use in the release git commit. Default: "github-actions
        :param git_user_name: (deprecated) The user name to use for the release git commit. Default: "github-actions"

        :deprecated:

        Use ``GoPublishOptions`` instead.
        export interface JsiiReleaseGo extends GoPublishOptions { }
        /**
        Options for Go releases.

        :stability: deprecated
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools
        if git_branch is not None:
            self._values["git_branch"] = git_branch
        if git_commit_message is not None:
            self._values["git_commit_message"] = git_commit_message
        if github_repo is not None:
            self._values["github_repo"] = github_repo
        if github_token_secret is not None:
            self._values["github_token_secret"] = github_token_secret
        if git_user_email is not None:
            self._values["git_user_email"] = git_user_email
        if git_user_name is not None:
            self._values["git_user_name"] = git_user_name

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def git_branch(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Branch to push to.

        :default: "main"

        :stability: deprecated
        '''
        result = self._values.get("git_branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_commit_message(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The commit message.

        :default: "chore(release): $VERSION"

        :stability: deprecated
        '''
        result = self._values.get("git_commit_message")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def github_repo(self) -> typing.Optional[builtins.str]:
        '''(deprecated) GitHub repository to push to.

        :default: - derived from ``moduleName``

        :stability: deprecated
        '''
        result = self._values.get("github_repo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def github_token_secret(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The name of the secret that includes a personal GitHub access token used to push to the GitHub repository.

        :default: "GO_GITHUB_TOKEN"

        :stability: deprecated
        '''
        result = self._values.get("github_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_user_email(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The email to use in the release git commit.

        :default: "github-actions

        :stability: deprecated
        :github: .com"
        '''
        result = self._values.get("git_user_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_user_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) The user name to use for the release git commit.

        :default: "github-actions"

        :stability: deprecated
        '''
        result = self._values.get("git_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.ManualReleaseOptions",
    jsii_struct_bases=[],
    name_mapping={
        "changelog": "changelog",
        "changelog_path": "changelogPath",
        "git_push_command": "gitPushCommand",
    },
)
class ManualReleaseOptions:
    def __init__(
        self,
        *,
        changelog: typing.Optional[builtins.bool] = None,
        changelog_path: typing.Optional[builtins.str] = None,
        git_push_command: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param changelog: (experimental) Maintain a project-level changelog. Default: true
        :param changelog_path: (experimental) Project-level changelog file path. Ignored if ``changelog`` is false. Default: 'CHANGELOG.md'
        :param git_push_command: (experimental) Override git-push command. Set to an empty string to disable pushing.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if changelog is not None:
            self._values["changelog"] = changelog
        if changelog_path is not None:
            self._values["changelog_path"] = changelog_path
        if git_push_command is not None:
            self._values["git_push_command"] = git_push_command

    @builtins.property
    def changelog(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Maintain a project-level changelog.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("changelog")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def changelog_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Project-level changelog file path.

        Ignored if ``changelog`` is false.

        :default: 'CHANGELOG.md'

        :stability: experimental
        '''
        result = self._values.get("changelog_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def git_push_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) Override git-push command.

        Set to an empty string to disable pushing.

        :stability: experimental
        '''
        result = self._values.get("git_push_command")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManualReleaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.MavenPublishOptions",
    jsii_struct_bases=[CommonPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "maven_endpoint": "mavenEndpoint",
        "maven_gpg_private_key_passphrase": "mavenGpgPrivateKeyPassphrase",
        "maven_gpg_private_key_secret": "mavenGpgPrivateKeySecret",
        "maven_password": "mavenPassword",
        "maven_repository_url": "mavenRepositoryUrl",
        "maven_server_id": "mavenServerId",
        "maven_staging_profile_id": "mavenStagingProfileId",
        "maven_username": "mavenUsername",
    },
)
class MavenPublishOptions(CommonPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        maven_endpoint: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_passphrase: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_secret: typing.Optional[builtins.str] = None,
        maven_password: typing.Optional[builtins.str] = None,
        maven_repository_url: typing.Optional[builtins.str] = None,
        maven_server_id: typing.Optional[builtins.str] = None,
        maven_staging_profile_id: typing.Optional[builtins.str] = None,
        maven_username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for Maven releases.

        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param maven_endpoint: (experimental) URL of Nexus repository. if not set, defaults to https://oss.sonatype.org Default: "https://oss.sonatype.org"
        :param maven_gpg_private_key_passphrase: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages
        :param maven_gpg_private_key_secret: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages
        :param maven_password: (experimental) GitHub secret name which contains the Password for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages
        :param maven_repository_url: (experimental) Deployment repository when not deploying to Maven Central. Default: - not set
        :param maven_server_id: (experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub). Default: "ossrh" (Maven Central) or "github" when using GitHub Packages
        :param maven_staging_profile_id: (experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521). Default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages
        :param maven_username: (experimental) GitHub secret name which contains the Username for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages

        :stability: experimental
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools
        if maven_endpoint is not None:
            self._values["maven_endpoint"] = maven_endpoint
        if maven_gpg_private_key_passphrase is not None:
            self._values["maven_gpg_private_key_passphrase"] = maven_gpg_private_key_passphrase
        if maven_gpg_private_key_secret is not None:
            self._values["maven_gpg_private_key_secret"] = maven_gpg_private_key_secret
        if maven_password is not None:
            self._values["maven_password"] = maven_password
        if maven_repository_url is not None:
            self._values["maven_repository_url"] = maven_repository_url
        if maven_server_id is not None:
            self._values["maven_server_id"] = maven_server_id
        if maven_staging_profile_id is not None:
            self._values["maven_staging_profile_id"] = maven_staging_profile_id
        if maven_username is not None:
            self._values["maven_username"] = maven_username

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def maven_endpoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) URL of Nexus repository.

        if not set, defaults to https://oss.sonatype.org

        :default: "https://oss.sonatype.org"

        :stability: experimental
        '''
        result = self._values.get("maven_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_gpg_private_key_passphrase(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the GPG private key or file that includes it.

        This is used to sign your Maven packages. See instructions.

        :default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages

        :see: https://github.com/aws/jsii-release#maven
        :stability: experimental
        '''
        result = self._values.get("maven_gpg_private_key_passphrase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_gpg_private_key_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the GPG private key or file that includes it.

        This is used to sign your Maven
        packages. See instructions.

        :default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages

        :see: https://github.com/aws/jsii-release#maven
        :stability: experimental
        '''
        result = self._values.get("maven_gpg_private_key_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_password(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Password for maven repository.

        For Maven Central, you will need to Create JIRA account and then request a
        new project (see links).

        :default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages

        :see: https://issues.sonatype.org/secure/CreateIssue.jspa?issuetype=21&pid=10134
        :stability: experimental
        '''
        result = self._values.get("maven_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_repository_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Deployment repository when not deploying to Maven Central.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("maven_repository_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_server_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub).

        :default: "ossrh" (Maven Central) or "github" when using GitHub Packages

        :stability: experimental
        '''
        result = self._values.get("maven_server_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_staging_profile_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521).

        :default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages

        :stability: experimental
        '''
        result = self._values.get("maven_staging_profile_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_username(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Username for maven repository.

        For Maven Central, you will need to Create JIRA account and then request a
        new project (see links).

        :default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages

        :see: https://issues.sonatype.org/secure/CreateIssue.jspa?issuetype=21&pid=10134
        :stability: experimental
        '''
        result = self._values.get("maven_username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MavenPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.NpmPublishOptions",
    jsii_struct_bases=[CommonPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "code_artifact_options": "codeArtifactOptions",
        "dist_tag": "distTag",
        "npm_token_secret": "npmTokenSecret",
        "registry": "registry",
    },
)
class NpmPublishOptions(CommonPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        code_artifact_options: typing.Optional[CodeArtifactOptions] = None,
        dist_tag: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for npm release.

        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param code_artifact_options: (experimental) Options for publishing npm package to AWS CodeArtifact. Default: - undefined
        :param dist_tag: (deprecated) Tags can be used to provide an alias instead of version numbers. For example, a project might choose to have multiple streams of development and use a different tag for each stream, e.g., stable, beta, dev, canary. By default, the ``latest`` tag is used by npm to identify the current version of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>`` specifier) installs the latest tag. Typically, projects only use the ``latest`` tag for stable release versions, and use other tags for unstable versions such as prereleases. The ``next`` tag is used by some projects to identify the upcoming version. Default: "latest"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.
        :param registry: (experimental) The domain name of the npm package registry. To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In this if ``npmTokenSecret`` is not specified, it will default to ``GITHUB_TOKEN`` which means that you will be able to publish to the repository's package store. In this case, make sure ``repositoryUrl`` is correctly defined. Default: "registry.npmjs.org"

        :stability: experimental
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        if isinstance(code_artifact_options, dict):
            code_artifact_options = CodeArtifactOptions(**code_artifact_options)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools
        if code_artifact_options is not None:
            self._values["code_artifact_options"] = code_artifact_options
        if dist_tag is not None:
            self._values["dist_tag"] = dist_tag
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if registry is not None:
            self._values["registry"] = registry

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def code_artifact_options(self) -> typing.Optional[CodeArtifactOptions]:
        '''(experimental) Options for publishing npm package to AWS CodeArtifact.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("code_artifact_options")
        return typing.cast(typing.Optional[CodeArtifactOptions], result)

    @builtins.property
    def dist_tag(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Tags can be used to provide an alias instead of version numbers.

        For example, a project might choose to have multiple streams of development
        and use a different tag for each stream, e.g., stable, beta, dev, canary.

        By default, the ``latest`` tag is used by npm to identify the current version
        of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>``
        specifier) installs the latest tag. Typically, projects only use the
        ``latest`` tag for stable release versions, and use other tags for unstable
        versions such as prereleases.

        The ``next`` tag is used by some projects to identify the upcoming version.

        :default: "latest"

        :deprecated: Use ``npmDistTag`` for each release branch instead.

        :stability: deprecated
        '''
        result = self._values.get("dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''(experimental) The domain name of the npm package registry.

        To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In
        this if ``npmTokenSecret`` is not specified, it will default to
        ``GITHUB_TOKEN`` which means that you will be able to publish to the
        repository's package store. In this case, make sure ``repositoryUrl`` is
        correctly defined.

        :default: "registry.npmjs.org"

        :stability: experimental

        Example::

            "npm.pkg.github.com"
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NpmPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.NugetPublishOptions",
    jsii_struct_bases=[CommonPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "nuget_api_key_secret": "nugetApiKeySecret",
    },
)
class NugetPublishOptions(CommonPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        nuget_api_key_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for NuGet releases.

        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param nuget_api_key_secret: (experimental) GitHub secret which contains the API key for NuGet. Default: "NUGET_API_KEY"

        :stability: experimental
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools
        if nuget_api_key_secret is not None:
            self._values["nuget_api_key_secret"] = nuget_api_key_secret

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def nuget_api_key_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the API key for NuGet.

        :default: "NUGET_API_KEY"

        :stability: experimental
        '''
        result = self._values.get("nuget_api_key_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NugetPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Publisher(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.release.Publisher",
):
    '''(experimental) Implements GitHub jobs for publishing modules to package managers.

    Under the hood, it uses https://github.com/aws/jsii-release

    :stability: experimental
    '''

    def __init__(
        self,
        project: _Project_57d89203,
        *,
        artifact_name: builtins.str,
        build_job_id: builtins.str,
        condition: typing.Optional[builtins.str] = None,
        dry_run: typing.Optional[builtins.bool] = None,
        failure_issue: typing.Optional[builtins.bool] = None,
        failure_issue_label: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param project: -
        :param artifact_name: (experimental) The name of the artifact to download (e.g. ``dist``). The artifact is expected to include a subdirectory for each release target: ``go`` (GitHub), ``dotnet`` (NuGet), ``java`` (Maven), ``js`` (npm), ``python`` (PyPI).
        :param build_job_id: (experimental) The job ID that produces the build artifacts. All publish jobs will take a dependency on this job.
        :param condition: (experimental) A GitHub workflow expression used as a condition for publishers. Default: - no condition
        :param dry_run: (experimental) Do not actually publish, only print the commands that would be executed instead. Useful if you wish to block all publishing from a single option.
        :param failure_issue: (experimental) Create an issue when a publish task fails. Default: false
        :param failure_issue_label: (experimental) The label to apply to the issue marking failed publish tasks. Only applies if ``failureIssue`` is true. Default: "failed-release"
        :param jsii_release_version: (experimental) Version requirement for ``jsii-release``. Default: "latest"
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]

        :stability: experimental
        '''
        options = PublisherOptions(
            artifact_name=artifact_name,
            build_job_id=build_job_id,
            condition=condition,
            dry_run=dry_run,
            failure_issue=failure_issue,
            failure_issue_label=failure_issue_label,
            jsii_release_version=jsii_release_version,
            publish_tasks=publish_tasks,
            workflow_runs_on=workflow_runs_on,
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="addGitHubPrePublishingSteps")
    def add_git_hub_pre_publishing_steps(self, *steps: _JobStep_c3287c05) -> None:
        '''(experimental) Adds pre publishing steps for the GitHub release job.

        :param steps: The steps.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addGitHubPrePublishingSteps", [*steps]))

    @jsii.member(jsii_name="publishToGit")
    def publish_to_git(
        self,
        *,
        changelog_file: builtins.str,
        release_tag_file: builtins.str,
        version_file: builtins.str,
        git_branch: typing.Optional[builtins.str] = None,
        git_push_command: typing.Optional[builtins.str] = None,
        project_changelog_file: typing.Optional[builtins.str] = None,
    ) -> _Task_9fa875b6:
        '''(experimental) Publish to git.

        This includes generating a project-level changelog and release tags.

        :param changelog_file: (experimental) The location of an .md file (relative to ``dist/``) that includes the changelog for the release.
        :param release_tag_file: (experimental) The location of a text file (relative to ``dist/``) that contains the release tag.
        :param version_file: (experimental) The location of a text file (relative to ``dist/``) that contains the version number.
        :param git_branch: (experimental) Branch to push to. Default: "main"
        :param git_push_command: (experimental) Override git-push command. Set to an empty string to disable pushing.
        :param project_changelog_file: (experimental) The location of an .md file that includes the project-level changelog.

        :stability: experimental
        '''
        options = GitPublishOptions(
            changelog_file=changelog_file,
            release_tag_file=release_tag_file,
            version_file=version_file,
            git_branch=git_branch,
            git_push_command=git_push_command,
            project_changelog_file=project_changelog_file,
        )

        return typing.cast(_Task_9fa875b6, jsii.invoke(self, "publishToGit", [options]))

    @jsii.member(jsii_name="publishToGitHubReleases")
    def publish_to_git_hub_releases(
        self,
        *,
        changelog_file: builtins.str,
        release_tag_file: builtins.str,
        version_file: builtins.str,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Creates a GitHub Release.

        :param changelog_file: (experimental) The location of an .md file (relative to ``dist/``) that includes the changelog for the release.
        :param release_tag_file: (experimental) The location of a text file (relative to ``dist/``) that contains the release tag.
        :param version_file: (experimental) The location of a text file (relative to ``dist/``) that contains the version number.
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed

        :stability: experimental
        '''
        options = GitHubReleasesPublishOptions(
            changelog_file=changelog_file,
            release_tag_file=release_tag_file,
            version_file=version_file,
            pre_publish_steps=pre_publish_steps,
            publish_tools=publish_tools,
        )

        return typing.cast(None, jsii.invoke(self, "publishToGitHubReleases", [options]))

    @jsii.member(jsii_name="publishToGo")
    def publish_to_go(
        self,
        *,
        git_branch: typing.Optional[builtins.str] = None,
        git_commit_message: typing.Optional[builtins.str] = None,
        github_repo: typing.Optional[builtins.str] = None,
        github_token_secret: typing.Optional[builtins.str] = None,
        git_user_email: typing.Optional[builtins.str] = None,
        git_user_name: typing.Optional[builtins.str] = None,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Adds a go publishing job.

        :param git_branch: (deprecated) Branch to push to. Default: "main"
        :param git_commit_message: (deprecated) The commit message. Default: "chore(release): $VERSION"
        :param github_repo: (deprecated) GitHub repository to push to. Default: - derived from ``moduleName``
        :param github_token_secret: (deprecated) The name of the secret that includes a personal GitHub access token used to push to the GitHub repository. Default: "GO_GITHUB_TOKEN"
        :param git_user_email: (deprecated) The email to use in the release git commit. Default: "github-actions
        :param git_user_name: (deprecated) The user name to use for the release git commit. Default: "github-actions"
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed

        :stability: experimental
        '''
        options = GoPublishOptions(
            git_branch=git_branch,
            git_commit_message=git_commit_message,
            github_repo=github_repo,
            github_token_secret=github_token_secret,
            git_user_email=git_user_email,
            git_user_name=git_user_name,
            pre_publish_steps=pre_publish_steps,
            publish_tools=publish_tools,
        )

        return typing.cast(None, jsii.invoke(self, "publishToGo", [options]))

    @jsii.member(jsii_name="publishToMaven")
    def publish_to_maven(
        self,
        *,
        maven_endpoint: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_passphrase: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_secret: typing.Optional[builtins.str] = None,
        maven_password: typing.Optional[builtins.str] = None,
        maven_repository_url: typing.Optional[builtins.str] = None,
        maven_server_id: typing.Optional[builtins.str] = None,
        maven_staging_profile_id: typing.Optional[builtins.str] = None,
        maven_username: typing.Optional[builtins.str] = None,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Publishes artifacts from ``java/**`` to Maven.

        :param maven_endpoint: (experimental) URL of Nexus repository. if not set, defaults to https://oss.sonatype.org Default: "https://oss.sonatype.org"
        :param maven_gpg_private_key_passphrase: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages
        :param maven_gpg_private_key_secret: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages
        :param maven_password: (experimental) GitHub secret name which contains the Password for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages
        :param maven_repository_url: (experimental) Deployment repository when not deploying to Maven Central. Default: - not set
        :param maven_server_id: (experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub). Default: "ossrh" (Maven Central) or "github" when using GitHub Packages
        :param maven_staging_profile_id: (experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521). Default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages
        :param maven_username: (experimental) GitHub secret name which contains the Username for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed

        :stability: experimental
        '''
        options = MavenPublishOptions(
            maven_endpoint=maven_endpoint,
            maven_gpg_private_key_passphrase=maven_gpg_private_key_passphrase,
            maven_gpg_private_key_secret=maven_gpg_private_key_secret,
            maven_password=maven_password,
            maven_repository_url=maven_repository_url,
            maven_server_id=maven_server_id,
            maven_staging_profile_id=maven_staging_profile_id,
            maven_username=maven_username,
            pre_publish_steps=pre_publish_steps,
            publish_tools=publish_tools,
        )

        return typing.cast(None, jsii.invoke(self, "publishToMaven", [options]))

    @jsii.member(jsii_name="publishToNpm")
    def publish_to_npm(
        self,
        *,
        code_artifact_options: typing.Optional[CodeArtifactOptions] = None,
        dist_tag: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Publishes artifacts from ``js/**`` to npm.

        :param code_artifact_options: (experimental) Options for publishing npm package to AWS CodeArtifact. Default: - undefined
        :param dist_tag: (deprecated) Tags can be used to provide an alias instead of version numbers. For example, a project might choose to have multiple streams of development and use a different tag for each stream, e.g., stable, beta, dev, canary. By default, the ``latest`` tag is used by npm to identify the current version of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>`` specifier) installs the latest tag. Typically, projects only use the ``latest`` tag for stable release versions, and use other tags for unstable versions such as prereleases. The ``next`` tag is used by some projects to identify the upcoming version. Default: "latest"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.
        :param registry: (experimental) The domain name of the npm package registry. To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In this if ``npmTokenSecret`` is not specified, it will default to ``GITHUB_TOKEN`` which means that you will be able to publish to the repository's package store. In this case, make sure ``repositoryUrl`` is correctly defined. Default: "registry.npmjs.org"
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed

        :stability: experimental
        '''
        options = NpmPublishOptions(
            code_artifact_options=code_artifact_options,
            dist_tag=dist_tag,
            npm_token_secret=npm_token_secret,
            registry=registry,
            pre_publish_steps=pre_publish_steps,
            publish_tools=publish_tools,
        )

        return typing.cast(None, jsii.invoke(self, "publishToNpm", [options]))

    @jsii.member(jsii_name="publishToNuget")
    def publish_to_nuget(
        self,
        *,
        nuget_api_key_secret: typing.Optional[builtins.str] = None,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Publishes artifacts from ``dotnet/**`` to NuGet Gallery.

        :param nuget_api_key_secret: (experimental) GitHub secret which contains the API key for NuGet. Default: "NUGET_API_KEY"
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed

        :stability: experimental
        '''
        options = NugetPublishOptions(
            nuget_api_key_secret=nuget_api_key_secret,
            pre_publish_steps=pre_publish_steps,
            publish_tools=publish_tools,
        )

        return typing.cast(None, jsii.invoke(self, "publishToNuget", [options]))

    @jsii.member(jsii_name="publishToPyPi")
    def publish_to_py_pi(
        self,
        *,
        twine_password_secret: typing.Optional[builtins.str] = None,
        twine_registry_url: typing.Optional[builtins.str] = None,
        twine_username_secret: typing.Optional[builtins.str] = None,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
    ) -> None:
        '''(experimental) Publishes wheel artifacts from ``python`` to PyPI.

        :param twine_password_secret: (experimental) The GitHub secret which contains PyPI password. Default: "TWINE_PASSWORD"
        :param twine_registry_url: (experimental) The registry url to use when releasing packages. Default: - twine default
        :param twine_username_secret: (experimental) The GitHub secret which contains PyPI user name. Default: "TWINE_USERNAME"
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed

        :stability: experimental
        '''
        options = PyPiPublishOptions(
            twine_password_secret=twine_password_secret,
            twine_registry_url=twine_registry_url,
            twine_username_secret=twine_username_secret,
            pre_publish_steps=pre_publish_steps,
            publish_tools=publish_tools,
        )

        return typing.cast(None, jsii.invoke(self, "publishToPyPi", [options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactName")
    def artifact_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "artifactName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildJobId")
    def build_job_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "buildJobId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="jsiiReleaseVersion")
    def jsii_release_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "jsiiReleaseVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="condition")
    def condition(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "condition"))


@jsii.data_type(
    jsii_type="projen.release.PublisherOptions",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_name": "artifactName",
        "build_job_id": "buildJobId",
        "condition": "condition",
        "dry_run": "dryRun",
        "failure_issue": "failureIssue",
        "failure_issue_label": "failureIssueLabel",
        "jsii_release_version": "jsiiReleaseVersion",
        "publish_tasks": "publishTasks",
        "workflow_runs_on": "workflowRunsOn",
    },
)
class PublisherOptions:
    def __init__(
        self,
        *,
        artifact_name: builtins.str,
        build_job_id: builtins.str,
        condition: typing.Optional[builtins.str] = None,
        dry_run: typing.Optional[builtins.bool] = None,
        failure_issue: typing.Optional[builtins.bool] = None,
        failure_issue_label: typing.Optional[builtins.str] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Options for ``Publisher``.

        :param artifact_name: (experimental) The name of the artifact to download (e.g. ``dist``). The artifact is expected to include a subdirectory for each release target: ``go`` (GitHub), ``dotnet`` (NuGet), ``java`` (Maven), ``js`` (npm), ``python`` (PyPI).
        :param build_job_id: (experimental) The job ID that produces the build artifacts. All publish jobs will take a dependency on this job.
        :param condition: (experimental) A GitHub workflow expression used as a condition for publishers. Default: - no condition
        :param dry_run: (experimental) Do not actually publish, only print the commands that would be executed instead. Useful if you wish to block all publishing from a single option.
        :param failure_issue: (experimental) Create an issue when a publish task fails. Default: false
        :param failure_issue_label: (experimental) The label to apply to the issue marking failed publish tasks. Only applies if ``failureIssue`` is true. Default: "failed-release"
        :param jsii_release_version: (experimental) Version requirement for ``jsii-release``. Default: "latest"
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "artifact_name": artifact_name,
            "build_job_id": build_job_id,
        }
        if condition is not None:
            self._values["condition"] = condition
        if dry_run is not None:
            self._values["dry_run"] = dry_run
        if failure_issue is not None:
            self._values["failure_issue"] = failure_issue
        if failure_issue_label is not None:
            self._values["failure_issue_label"] = failure_issue_label
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on

    @builtins.property
    def artifact_name(self) -> builtins.str:
        '''(experimental) The name of the artifact to download (e.g. ``dist``).

        The artifact is expected to include a subdirectory for each release target:
        ``go`` (GitHub), ``dotnet`` (NuGet), ``java`` (Maven), ``js`` (npm), ``python``
        (PyPI).

        :see: https://github.com/aws/jsii-release
        :stability: experimental
        '''
        result = self._values.get("artifact_name")
        assert result is not None, "Required property 'artifact_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_job_id(self) -> builtins.str:
        '''(experimental) The job ID that produces the build artifacts.

        All publish jobs will take a dependency on this job.

        :stability: experimental
        '''
        result = self._values.get("build_job_id")
        assert result is not None, "Required property 'build_job_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) A GitHub workflow expression used as a condition for publishers.

        :default: - no condition

        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Do not actually publish, only print the commands that would be executed instead.

        Useful if you wish to block all publishing from a single option.

        :stability: experimental
        '''
        result = self._values.get("dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create an issue when a publish task fails.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to the issue marking failed publish tasks.

        Only applies if ``failureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement for ``jsii-release``.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PublisherOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.PyPiPublishOptions",
    jsii_struct_bases=[CommonPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "twine_password_secret": "twinePasswordSecret",
        "twine_registry_url": "twineRegistryUrl",
        "twine_username_secret": "twineUsernameSecret",
    },
)
class PyPiPublishOptions(CommonPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        twine_password_secret: typing.Optional[builtins.str] = None,
        twine_registry_url: typing.Optional[builtins.str] = None,
        twine_username_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for PyPI release.

        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param twine_password_secret: (experimental) The GitHub secret which contains PyPI password. Default: "TWINE_PASSWORD"
        :param twine_registry_url: (experimental) The registry url to use when releasing packages. Default: - twine default
        :param twine_username_secret: (experimental) The GitHub secret which contains PyPI user name. Default: "TWINE_USERNAME"

        :stability: experimental
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools
        if twine_password_secret is not None:
            self._values["twine_password_secret"] = twine_password_secret
        if twine_registry_url is not None:
            self._values["twine_registry_url"] = twine_registry_url
        if twine_username_secret is not None:
            self._values["twine_username_secret"] = twine_username_secret

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def twine_password_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The GitHub secret which contains PyPI password.

        :default: "TWINE_PASSWORD"

        :stability: experimental
        '''
        result = self._values.get("twine_password_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def twine_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The registry url to use when releasing packages.

        :default: - twine default

        :stability: experimental
        '''
        result = self._values.get("twine_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def twine_username_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The GitHub secret which contains PyPI user name.

        :default: "TWINE_USERNAME"

        :stability: experimental
        '''
        result = self._values.get("twine_username_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PyPiPublishOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Release(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.release.Release",
):
    '''(experimental) Manages releases (currently through GitHub workflows).

    By default, no branches are released. To add branches, call ``addBranch()``.

    :stability: experimental
    '''

    def __init__(
        self,
        project: _GitHubProject_c48bc7ea,
        *,
        artifacts_directory: builtins.str,
        branch: builtins.str,
        task: _Task_9fa875b6,
        version_file: builtins.str,
        github_release: typing.Optional[builtins.bool] = None,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional["ReleaseTrigger"] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param project: -
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param branch: (experimental) The default branch name to release from. Use ``majorVersion`` to restrict this branch to only publish releases with a specific major version. You can add additional branches using ``addBranch()``.
        :param task: (experimental) The task to execute in order to create the release artifacts. Artifacts are expected to reside under ``artifactsDirectory`` (defaults to ``dist/``) once build is complete.
        :param version_file: (experimental) A name of a .json file to set the ``version`` field in after a bump.
        :param github_release: (experimental) Create a GitHub release for each release. Default: true
        :param jsii_release_version: (experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]

        :stability: experimental
        '''
        options = ReleaseOptions(
            artifacts_directory=artifacts_directory,
            branch=branch,
            task=task,
            version_file=version_file,
            github_release=github_release,
            jsii_release_version=jsii_release_version,
            major_version=major_version,
            npm_dist_tag=npm_dist_tag,
            post_build_steps=post_build_steps,
            prerelease=prerelease,
            publish_dry_run=publish_dry_run,
            publish_tasks=publish_tasks,
            release_branches=release_branches,
            release_every_commit=release_every_commit,
            release_failure_issue=release_failure_issue,
            release_failure_issue_label=release_failure_issue_label,
            release_schedule=release_schedule,
            release_tag_prefix=release_tag_prefix,
            release_trigger=release_trigger,
            release_workflow_name=release_workflow_name,
            release_workflow_setup_steps=release_workflow_setup_steps,
            versionrc_options=versionrc_options,
            workflow_container_image=workflow_container_image,
            workflow_runs_on=workflow_runs_on,
        )

        jsii.create(self.__class__, self, [project, options])

    @jsii.member(jsii_name="addBranch")
    def add_branch(
        self,
        branch: builtins.str,
        *,
        major_version: jsii.Number,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        prerelease: typing.Optional[builtins.str] = None,
        tag_prefix: typing.Optional[builtins.str] = None,
        workflow_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Adds a release branch.

        It is a git branch from which releases are published. If a project has more than one release
        branch, we require that ``majorVersion`` is also specified for the primary branch in order to
        ensure branches always release the correct version.

        :param branch: The branch to monitor (e.g. ``main``, ``v2.x``).
        :param major_version: (experimental) The major versions released from this branch.
        :param npm_dist_tag: (experimental) The npm distribution tag to use for this branch. Default: "latest"
        :param prerelease: (experimental) Bump the version as a pre-release tag. Default: - normal releases
        :param tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param workflow_name: (experimental) The name of the release workflow. Default: "release-BRANCH"

        :stability: experimental
        '''
        options = BranchOptions(
            major_version=major_version,
            npm_dist_tag=npm_dist_tag,
            prerelease=prerelease,
            tag_prefix=tag_prefix,
            workflow_name=workflow_name,
        )

        return typing.cast(None, jsii.invoke(self, "addBranch", [branch, options]))

    @jsii.member(jsii_name="addJobs")
    def add_jobs(self, jobs: typing.Mapping[builtins.str, _Job_20ffcf45]) -> None:
        '''(experimental) Adds jobs to all release workflows.

        :param jobs: The jobs to add (name => job).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addJobs", [jobs]))

    @jsii.member(jsii_name="preSynthesize")
    def pre_synthesize(self) -> None:
        '''(experimental) Called before synthesis.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "preSynthesize", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="artifactsDirectory")
    def artifacts_directory(self) -> builtins.str:
        '''(experimental) Location of build artifacts.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "artifactsDirectory"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branches")
    def branches(self) -> typing.List[builtins.str]:
        '''(experimental) Retrieve all release branch names.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "branches"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publisher")
    def publisher(self) -> Publisher:
        '''(experimental) Package publisher.

        :stability: experimental
        '''
        return typing.cast(Publisher, jsii.get(self, "publisher"))


@jsii.data_type(
    jsii_type="projen.release.ReleaseProjectOptions",
    jsii_struct_bases=[],
    name_mapping={
        "jsii_release_version": "jsiiReleaseVersion",
        "major_version": "majorVersion",
        "npm_dist_tag": "npmDistTag",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "publish_dry_run": "publishDryRun",
        "publish_tasks": "publishTasks",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_failure_issue": "releaseFailureIssue",
        "release_failure_issue_label": "releaseFailureIssueLabel",
        "release_schedule": "releaseSchedule",
        "release_tag_prefix": "releaseTagPrefix",
        "release_trigger": "releaseTrigger",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "versionrc_options": "versionrcOptions",
        "workflow_container_image": "workflowContainerImage",
        "workflow_runs_on": "workflowRunsOn",
    },
)
class ReleaseProjectOptions:
    def __init__(
        self,
        *,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional["ReleaseTrigger"] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Project options for release.

        :param jsii_release_version: (experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if major_version is not None:
            self._values["major_version"] = major_version
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if publish_dry_run is not None:
            self._values["publish_dry_run"] = publish_dry_run
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_failure_issue is not None:
            self._values["release_failure_issue"] = release_failure_issue
        if release_failure_issue_label is not None:
            self._values["release_failure_issue_label"] = release_failure_issue_label
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_tag_prefix is not None:
            self._values["release_tag_prefix"] = release_tag_prefix
        if release_trigger is not None:
            self._values["release_trigger"] = release_trigger
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if versionrc_options is not None:
            self._values["versionrc_options"] = versionrc_options
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npmDistTag to use when publishing from the default branch.

        To set the npm dist-tag for release branches, set the ``npmDistTag`` property
        for each branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Instead of actually publishing to package managers, just print the publishing command.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.continuous()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a github issue on every failed publishing task.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to issues indicating publish failures.

        Only applies if ``releaseFailureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(deprecated) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.scheduled()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers.

        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: - no prefix

        :stability: experimental
        '''
        result = self._values.get("release_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_trigger(self) -> typing.Optional["ReleaseTrigger"]:
        '''(experimental) The release trigger to use.

        :default: - Continuous releases (``ReleaseTrigger.continuous()``)

        :stability: experimental
        '''
        result = self._values.get("release_trigger")
        return typing.cast(typing.Optional["ReleaseTrigger"], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "Release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def versionrc_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Custom configuration used when creating changelog with standard-version package.

        Given values either append to default configuration or overwrite values in it.

        :default: - standard configuration applicable for GitHub repositories

        :stability: experimental
        '''
        result = self._values.get("versionrc_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReleaseProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ReleaseTrigger(
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.release.ReleaseTrigger",
):
    '''(experimental) Used to manage release strategies.

    This includes release
    and release artifact automation

    :stability: experimental
    '''

    @jsii.member(jsii_name="continuous") # type: ignore[misc]
    @builtins.classmethod
    def continuous(cls) -> "ReleaseTrigger":
        '''(experimental) Creates a continuous release trigger.

        Automated releases will occur on every commit.

        :stability: experimental
        '''
        return typing.cast("ReleaseTrigger", jsii.sinvoke(cls, "continuous", []))

    @jsii.member(jsii_name="manual") # type: ignore[misc]
    @builtins.classmethod
    def manual(
        cls,
        *,
        changelog: typing.Optional[builtins.bool] = None,
        changelog_path: typing.Optional[builtins.str] = None,
        git_push_command: typing.Optional[builtins.str] = None,
    ) -> "ReleaseTrigger":
        '''(experimental) Creates a manual release trigger.

        Use this option if you want totally manual releases.

        This will give you a release task that, in addition to the normal
        release activities will trigger a ``publish:git`` task. This task will
        handle project-level changelog management, release tagging, and pushing
        these artifacts to origin.

        The command used for pushing can be customised by specifying
        ``gitPushCommand``. Set to an empty string to disable pushing entirely.

        Simply run ``yarn release`` to trigger a manual release.

        :param changelog: (experimental) Maintain a project-level changelog. Default: true
        :param changelog_path: (experimental) Project-level changelog file path. Ignored if ``changelog`` is false. Default: 'CHANGELOG.md'
        :param git_push_command: (experimental) Override git-push command. Set to an empty string to disable pushing.

        :stability: experimental
        '''
        options = ManualReleaseOptions(
            changelog=changelog,
            changelog_path=changelog_path,
            git_push_command=git_push_command,
        )

        return typing.cast("ReleaseTrigger", jsii.sinvoke(cls, "manual", [options]))

    @jsii.member(jsii_name="scheduled") # type: ignore[misc]
    @builtins.classmethod
    def scheduled(cls, *, schedule: builtins.str) -> "ReleaseTrigger":
        '''(experimental) Creates a scheduled release trigger.

        Automated releases will occur based on the provided cron schedule.

        :param schedule: (experimental) Cron schedule for releases. Only defined if this is a scheduled release.

        :stability: experimental
        '''
        options = ScheduledReleaseOptions(schedule=schedule)

        return typing.cast("ReleaseTrigger", jsii.sinvoke(cls, "scheduled", [options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isContinuous")
    def is_continuous(self) -> builtins.bool:
        '''(experimental) Whether or not this is a continuous release.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isContinuous"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isManual")
    def is_manual(self) -> builtins.bool:
        '''(experimental) Whether or not this is a manual release trigger.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isManual"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="changelogPath")
    def changelog_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) Project-level changelog file path.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "changelogPath"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gitPushCommand")
    def git_push_command(self) -> typing.Optional[builtins.str]:
        '''(experimental) Override git-push command used when releasing manually.

        Set to an empty string to disable pushing.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitPushCommand"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> typing.Optional[builtins.str]:
        '''(experimental) Cron schedule for releases.

        Only defined if this is a scheduled release.

        :stability: experimental

        Example::

            '0 17 * * *' - every day at 5 pm
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schedule"))


@jsii.data_type(
    jsii_type="projen.release.ScheduledReleaseOptions",
    jsii_struct_bases=[],
    name_mapping={"schedule": "schedule"},
)
class ScheduledReleaseOptions:
    def __init__(self, *, schedule: builtins.str) -> None:
        '''
        :param schedule: (experimental) Cron schedule for releases. Only defined if this is a scheduled release.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "schedule": schedule,
        }

    @builtins.property
    def schedule(self) -> builtins.str:
        '''(experimental) Cron schedule for releases.

        Only defined if this is a scheduled release.

        :stability: experimental

        Example::

            '0 17 * * *' - every day at 5 pm
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScheduledReleaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.JsiiReleaseMaven",
    jsii_struct_bases=[MavenPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "maven_endpoint": "mavenEndpoint",
        "maven_gpg_private_key_passphrase": "mavenGpgPrivateKeyPassphrase",
        "maven_gpg_private_key_secret": "mavenGpgPrivateKeySecret",
        "maven_password": "mavenPassword",
        "maven_repository_url": "mavenRepositoryUrl",
        "maven_server_id": "mavenServerId",
        "maven_staging_profile_id": "mavenStagingProfileId",
        "maven_username": "mavenUsername",
    },
)
class JsiiReleaseMaven(MavenPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        maven_endpoint: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_passphrase: typing.Optional[builtins.str] = None,
        maven_gpg_private_key_secret: typing.Optional[builtins.str] = None,
        maven_password: typing.Optional[builtins.str] = None,
        maven_repository_url: typing.Optional[builtins.str] = None,
        maven_server_id: typing.Optional[builtins.str] = None,
        maven_staging_profile_id: typing.Optional[builtins.str] = None,
        maven_username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param maven_endpoint: (experimental) URL of Nexus repository. if not set, defaults to https://oss.sonatype.org Default: "https://oss.sonatype.org"
        :param maven_gpg_private_key_passphrase: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages
        :param maven_gpg_private_key_secret: (experimental) GitHub secret name which contains the GPG private key or file that includes it. This is used to sign your Maven packages. See instructions. Default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages
        :param maven_password: (experimental) GitHub secret name which contains the Password for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages
        :param maven_repository_url: (experimental) Deployment repository when not deploying to Maven Central. Default: - not set
        :param maven_server_id: (experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub). Default: "ossrh" (Maven Central) or "github" when using GitHub Packages
        :param maven_staging_profile_id: (experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521). Default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages
        :param maven_username: (experimental) GitHub secret name which contains the Username for maven repository. For Maven Central, you will need to Create JIRA account and then request a new project (see links). Default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages

        :deprecated: Use ``MavenPublishOptions`` instead.

        :stability: deprecated
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools
        if maven_endpoint is not None:
            self._values["maven_endpoint"] = maven_endpoint
        if maven_gpg_private_key_passphrase is not None:
            self._values["maven_gpg_private_key_passphrase"] = maven_gpg_private_key_passphrase
        if maven_gpg_private_key_secret is not None:
            self._values["maven_gpg_private_key_secret"] = maven_gpg_private_key_secret
        if maven_password is not None:
            self._values["maven_password"] = maven_password
        if maven_repository_url is not None:
            self._values["maven_repository_url"] = maven_repository_url
        if maven_server_id is not None:
            self._values["maven_server_id"] = maven_server_id
        if maven_staging_profile_id is not None:
            self._values["maven_staging_profile_id"] = maven_staging_profile_id
        if maven_username is not None:
            self._values["maven_username"] = maven_username

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def maven_endpoint(self) -> typing.Optional[builtins.str]:
        '''(experimental) URL of Nexus repository.

        if not set, defaults to https://oss.sonatype.org

        :default: "https://oss.sonatype.org"

        :stability: experimental
        '''
        result = self._values.get("maven_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_gpg_private_key_passphrase(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the GPG private key or file that includes it.

        This is used to sign your Maven packages. See instructions.

        :default: "MAVEN_GPG_PRIVATE_KEY_PASSPHRASE" or not set when using GitHub Packages

        :see: https://github.com/aws/jsii-release#maven
        :stability: experimental
        '''
        result = self._values.get("maven_gpg_private_key_passphrase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_gpg_private_key_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the GPG private key or file that includes it.

        This is used to sign your Maven
        packages. See instructions.

        :default: "MAVEN_GPG_PRIVATE_KEY" or not set when using GitHub Packages

        :see: https://github.com/aws/jsii-release#maven
        :stability: experimental
        '''
        result = self._values.get("maven_gpg_private_key_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_password(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Password for maven repository.

        For Maven Central, you will need to Create JIRA account and then request a
        new project (see links).

        :default: "MAVEN_PASSWORD" or "GITHUB_TOKEN" when using GitHub Packages

        :see: https://issues.sonatype.org/secure/CreateIssue.jspa?issuetype=21&pid=10134
        :stability: experimental
        '''
        result = self._values.get("maven_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_repository_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) Deployment repository when not deploying to Maven Central.

        :default: - not set

        :stability: experimental
        '''
        result = self._values.get("maven_repository_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_server_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) Used in maven settings for credential lookup (e.g. use github when publishing to GitHub).

        :default: "ossrh" (Maven Central) or "github" when using GitHub Packages

        :stability: experimental
        '''
        result = self._values.get("maven_server_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_staging_profile_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Maven Central (sonatype) staging profile ID (e.g. 68a05363083174). Staging profile ID can be found in the URL of the "Releases" staging profile under "Staging Profiles" in https://oss.sonatype.org (e.g. https://oss.sonatype.org/#stagingProfiles;11a33451234521).

        :default: "MAVEN_STAGING_PROFILE_ID" or not set when using GitHub Packages

        :stability: experimental
        '''
        result = self._values.get("maven_staging_profile_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maven_username(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret name which contains the Username for maven repository.

        For Maven Central, you will need to Create JIRA account and then request a
        new project (see links).

        :default: "MAVEN_USERNAME" or the GitHub Actor when using GitHub Packages

        :see: https://issues.sonatype.org/secure/CreateIssue.jspa?issuetype=21&pid=10134
        :stability: experimental
        '''
        result = self._values.get("maven_username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsiiReleaseMaven(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.JsiiReleaseNpm",
    jsii_struct_bases=[NpmPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "code_artifact_options": "codeArtifactOptions",
        "dist_tag": "distTag",
        "npm_token_secret": "npmTokenSecret",
        "registry": "registry",
    },
)
class JsiiReleaseNpm(NpmPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        code_artifact_options: typing.Optional[CodeArtifactOptions] = None,
        dist_tag: typing.Optional[builtins.str] = None,
        npm_token_secret: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param code_artifact_options: (experimental) Options for publishing npm package to AWS CodeArtifact. Default: - undefined
        :param dist_tag: (deprecated) Tags can be used to provide an alias instead of version numbers. For example, a project might choose to have multiple streams of development and use a different tag for each stream, e.g., stable, beta, dev, canary. By default, the ``latest`` tag is used by npm to identify the current version of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>`` specifier) installs the latest tag. Typically, projects only use the ``latest`` tag for stable release versions, and use other tags for unstable versions such as prereleases. The ``next`` tag is used by some projects to identify the upcoming version. Default: "latest"
        :param npm_token_secret: (experimental) GitHub secret which contains the NPM token to use when publishing packages. Default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.
        :param registry: (experimental) The domain name of the npm package registry. To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In this if ``npmTokenSecret`` is not specified, it will default to ``GITHUB_TOKEN`` which means that you will be able to publish to the repository's package store. In this case, make sure ``repositoryUrl`` is correctly defined. Default: "registry.npmjs.org"

        :deprecated: Use ``NpmPublishOptions`` instead.

        :stability: deprecated
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        if isinstance(code_artifact_options, dict):
            code_artifact_options = CodeArtifactOptions(**code_artifact_options)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools
        if code_artifact_options is not None:
            self._values["code_artifact_options"] = code_artifact_options
        if dist_tag is not None:
            self._values["dist_tag"] = dist_tag
        if npm_token_secret is not None:
            self._values["npm_token_secret"] = npm_token_secret
        if registry is not None:
            self._values["registry"] = registry

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def code_artifact_options(self) -> typing.Optional[CodeArtifactOptions]:
        '''(experimental) Options for publishing npm package to AWS CodeArtifact.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("code_artifact_options")
        return typing.cast(typing.Optional[CodeArtifactOptions], result)

    @builtins.property
    def dist_tag(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Tags can be used to provide an alias instead of version numbers.

        For example, a project might choose to have multiple streams of development
        and use a different tag for each stream, e.g., stable, beta, dev, canary.

        By default, the ``latest`` tag is used by npm to identify the current version
        of a package, and ``npm install <pkg>`` (without any ``@<version>`` or ``@<tag>``
        specifier) installs the latest tag. Typically, projects only use the
        ``latest`` tag for stable release versions, and use other tags for unstable
        versions such as prereleases.

        The ``next`` tag is used by some projects to identify the upcoming version.

        :default: "latest"

        :deprecated: Use ``npmDistTag`` for each release branch instead.

        :stability: deprecated
        '''
        result = self._values.get("dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def npm_token_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the NPM token to use when publishing packages.

        :default: - "NPM_TOKEN" or "GITHUB_TOKEN" if ``registry`` is set to ``npm.pkg.github.com``.

        :stability: experimental
        '''
        result = self._values.get("npm_token_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''(experimental) The domain name of the npm package registry.

        To publish to GitHub Packages, set this value to ``"npm.pkg.github.com"``. In
        this if ``npmTokenSecret`` is not specified, it will default to
        ``GITHUB_TOKEN`` which means that you will be able to publish to the
        repository's package store. In this case, make sure ``repositoryUrl`` is
        correctly defined.

        :default: "registry.npmjs.org"

        :stability: experimental

        Example::

            "npm.pkg.github.com"
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsiiReleaseNpm(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.JsiiReleaseNuget",
    jsii_struct_bases=[NugetPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "nuget_api_key_secret": "nugetApiKeySecret",
    },
)
class JsiiReleaseNuget(NugetPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        nuget_api_key_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param nuget_api_key_secret: (experimental) GitHub secret which contains the API key for NuGet. Default: "NUGET_API_KEY"

        :deprecated: Use ``NugetPublishOptions`` instead.

        :stability: deprecated
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools
        if nuget_api_key_secret is not None:
            self._values["nuget_api_key_secret"] = nuget_api_key_secret

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def nuget_api_key_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub secret which contains the API key for NuGet.

        :default: "NUGET_API_KEY"

        :stability: experimental
        '''
        result = self._values.get("nuget_api_key_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsiiReleaseNuget(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.JsiiReleasePyPi",
    jsii_struct_bases=[PyPiPublishOptions],
    name_mapping={
        "pre_publish_steps": "prePublishSteps",
        "publish_tools": "publishTools",
        "twine_password_secret": "twinePasswordSecret",
        "twine_registry_url": "twineRegistryUrl",
        "twine_username_secret": "twineUsernameSecret",
    },
)
class JsiiReleasePyPi(PyPiPublishOptions):
    def __init__(
        self,
        *,
        pre_publish_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        publish_tools: typing.Optional[_Tools_75b93a2a] = None,
        twine_password_secret: typing.Optional[builtins.str] = None,
        twine_registry_url: typing.Optional[builtins.str] = None,
        twine_username_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param pre_publish_steps: (experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede. These steps are executed after ``dist/`` has been populated with the build output. Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.
        :param publish_tools: (experimental) Additional tools to install in the publishing job. Default: - no additional tools are installed
        :param twine_password_secret: (experimental) The GitHub secret which contains PyPI password. Default: "TWINE_PASSWORD"
        :param twine_registry_url: (experimental) The registry url to use when releasing packages. Default: - twine default
        :param twine_username_secret: (experimental) The GitHub secret which contains PyPI user name. Default: "TWINE_USERNAME"

        :deprecated: Use ``PyPiPublishOptions`` instead.

        :stability: deprecated
        '''
        if isinstance(publish_tools, dict):
            publish_tools = _Tools_75b93a2a(**publish_tools)
        self._values: typing.Dict[str, typing.Any] = {}
        if pre_publish_steps is not None:
            self._values["pre_publish_steps"] = pre_publish_steps
        if publish_tools is not None:
            self._values["publish_tools"] = publish_tools
        if twine_password_secret is not None:
            self._values["twine_password_secret"] = twine_password_secret
        if twine_registry_url is not None:
            self._values["twine_registry_url"] = twine_registry_url
        if twine_username_secret is not None:
            self._values["twine_username_secret"] = twine_username_secret

    @builtins.property
    def pre_publish_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute before executing the publishing command. These can be used to prepare the artifact for publishing if neede.

        These steps are executed after ``dist/`` has been populated with the build
        output.

        Note that when using this in ``publishToGitHubReleases`` this will override steps added via ``addGitHubPrePublishingSteps``.

        :stability: experimental
        '''
        result = self._values.get("pre_publish_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def publish_tools(self) -> typing.Optional[_Tools_75b93a2a]:
        '''(experimental) Additional tools to install in the publishing job.

        :default: - no additional tools are installed

        :stability: experimental
        '''
        result = self._values.get("publish_tools")
        return typing.cast(typing.Optional[_Tools_75b93a2a], result)

    @builtins.property
    def twine_password_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The GitHub secret which contains PyPI password.

        :default: "TWINE_PASSWORD"

        :stability: experimental
        '''
        result = self._values.get("twine_password_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def twine_registry_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) The registry url to use when releasing packages.

        :default: - twine default

        :stability: experimental
        '''
        result = self._values.get("twine_registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def twine_username_secret(self) -> typing.Optional[builtins.str]:
        '''(experimental) The GitHub secret which contains PyPI user name.

        :default: "TWINE_USERNAME"

        :stability: experimental
        '''
        result = self._values.get("twine_username_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JsiiReleasePyPi(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.release.ReleaseOptions",
    jsii_struct_bases=[ReleaseProjectOptions],
    name_mapping={
        "jsii_release_version": "jsiiReleaseVersion",
        "major_version": "majorVersion",
        "npm_dist_tag": "npmDistTag",
        "post_build_steps": "postBuildSteps",
        "prerelease": "prerelease",
        "publish_dry_run": "publishDryRun",
        "publish_tasks": "publishTasks",
        "release_branches": "releaseBranches",
        "release_every_commit": "releaseEveryCommit",
        "release_failure_issue": "releaseFailureIssue",
        "release_failure_issue_label": "releaseFailureIssueLabel",
        "release_schedule": "releaseSchedule",
        "release_tag_prefix": "releaseTagPrefix",
        "release_trigger": "releaseTrigger",
        "release_workflow_name": "releaseWorkflowName",
        "release_workflow_setup_steps": "releaseWorkflowSetupSteps",
        "versionrc_options": "versionrcOptions",
        "workflow_container_image": "workflowContainerImage",
        "workflow_runs_on": "workflowRunsOn",
        "artifacts_directory": "artifactsDirectory",
        "branch": "branch",
        "task": "task",
        "version_file": "versionFile",
        "github_release": "githubRelease",
    },
)
class ReleaseOptions(ReleaseProjectOptions):
    def __init__(
        self,
        *,
        jsii_release_version: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        npm_dist_tag: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        prerelease: typing.Optional[builtins.str] = None,
        publish_dry_run: typing.Optional[builtins.bool] = None,
        publish_tasks: typing.Optional[builtins.bool] = None,
        release_branches: typing.Optional[typing.Mapping[builtins.str, BranchOptions]] = None,
        release_every_commit: typing.Optional[builtins.bool] = None,
        release_failure_issue: typing.Optional[builtins.bool] = None,
        release_failure_issue_label: typing.Optional[builtins.str] = None,
        release_schedule: typing.Optional[builtins.str] = None,
        release_tag_prefix: typing.Optional[builtins.str] = None,
        release_trigger: typing.Optional[ReleaseTrigger] = None,
        release_workflow_name: typing.Optional[builtins.str] = None,
        release_workflow_setup_steps: typing.Optional[typing.Sequence[_JobStep_c3287c05]] = None,
        versionrc_options: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        workflow_container_image: typing.Optional[builtins.str] = None,
        workflow_runs_on: typing.Optional[typing.Sequence[builtins.str]] = None,
        artifacts_directory: builtins.str,
        branch: builtins.str,
        task: _Task_9fa875b6,
        version_file: builtins.str,
        github_release: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Options for ``Release``.

        :param jsii_release_version: (experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm. Default: "latest"
        :param major_version: (experimental) Major version to release from the default branch. If this is specified, we bump the latest version of this major version line. If not specified, we bump the global latest version. Default: - Major version is not enforced.
        :param npm_dist_tag: (experimental) The npmDistTag to use when publishing from the default branch. To set the npm dist-tag for release branches, set the ``npmDistTag`` property for each branch. Default: "latest"
        :param post_build_steps: (experimental) Steps to execute after build as part of the release workflow. Default: []
        :param prerelease: (experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre"). Default: - normal semantic versions
        :param publish_dry_run: (experimental) Instead of actually publishing to package managers, just print the publishing command. Default: false
        :param publish_tasks: (experimental) Define publishing tasks that can be executed manually as well as workflows. Normally, publishing only happens within automated workflows. Enable this in order to create a publishing task for each publishing activity. Default: false
        :param release_branches: (experimental) Defines additional release branches. A workflow will be created for each release branch which will publish releases from commits in this branch. Each release branch *must* be assigned a major version number which is used to enforce that versions published from that branch always use that major version. If multiple branches are used, the ``majorVersion`` field must also be provided for the default branch. Default: - no additional branches are used for release. you can use ``addBranch()`` to add additional branches.
        :param release_every_commit: (deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``. Default: true
        :param release_failure_issue: (experimental) Create a github issue on every failed publishing task. Default: false
        :param release_failure_issue_label: (experimental) The label to apply to issues indicating publish failures. Only applies if ``releaseFailureIssue`` is true. Default: "failed-release"
        :param release_schedule: (deprecated) CRON schedule to trigger new releases. Default: - no scheduled releases
        :param release_tag_prefix: (experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers. Note: this prefix is used to detect the latest tagged version when bumping, so if you change this on a project with an existing version history, you may need to manually tag your latest release with the new prefix. Default: - no prefix
        :param release_trigger: (experimental) The release trigger to use. Default: - Continuous releases (``ReleaseTrigger.continuous()``)
        :param release_workflow_name: (experimental) The name of the default release workflow. Default: "Release"
        :param release_workflow_setup_steps: (experimental) A set of workflow steps to execute in order to setup the workflow container.
        :param versionrc_options: (experimental) Custom configuration used when creating changelog with standard-version package. Given values either append to default configuration or overwrite values in it. Default: - standard configuration applicable for GitHub repositories
        :param workflow_container_image: (experimental) Container image to use for GitHub workflows. Default: - default image
        :param workflow_runs_on: (experimental) Github Runner selection labels. Default: ["ubuntu-latest"]
        :param artifacts_directory: (experimental) A directory which will contain build artifacts. Default: "dist"
        :param branch: (experimental) The default branch name to release from. Use ``majorVersion`` to restrict this branch to only publish releases with a specific major version. You can add additional branches using ``addBranch()``.
        :param task: (experimental) The task to execute in order to create the release artifacts. Artifacts are expected to reside under ``artifactsDirectory`` (defaults to ``dist/``) once build is complete.
        :param version_file: (experimental) A name of a .json file to set the ``version`` field in after a bump.
        :param github_release: (experimental) Create a GitHub release for each release. Default: true

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "artifacts_directory": artifacts_directory,
            "branch": branch,
            "task": task,
            "version_file": version_file,
        }
        if jsii_release_version is not None:
            self._values["jsii_release_version"] = jsii_release_version
        if major_version is not None:
            self._values["major_version"] = major_version
        if npm_dist_tag is not None:
            self._values["npm_dist_tag"] = npm_dist_tag
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if prerelease is not None:
            self._values["prerelease"] = prerelease
        if publish_dry_run is not None:
            self._values["publish_dry_run"] = publish_dry_run
        if publish_tasks is not None:
            self._values["publish_tasks"] = publish_tasks
        if release_branches is not None:
            self._values["release_branches"] = release_branches
        if release_every_commit is not None:
            self._values["release_every_commit"] = release_every_commit
        if release_failure_issue is not None:
            self._values["release_failure_issue"] = release_failure_issue
        if release_failure_issue_label is not None:
            self._values["release_failure_issue_label"] = release_failure_issue_label
        if release_schedule is not None:
            self._values["release_schedule"] = release_schedule
        if release_tag_prefix is not None:
            self._values["release_tag_prefix"] = release_tag_prefix
        if release_trigger is not None:
            self._values["release_trigger"] = release_trigger
        if release_workflow_name is not None:
            self._values["release_workflow_name"] = release_workflow_name
        if release_workflow_setup_steps is not None:
            self._values["release_workflow_setup_steps"] = release_workflow_setup_steps
        if versionrc_options is not None:
            self._values["versionrc_options"] = versionrc_options
        if workflow_container_image is not None:
            self._values["workflow_container_image"] = workflow_container_image
        if workflow_runs_on is not None:
            self._values["workflow_runs_on"] = workflow_runs_on
        if github_release is not None:
            self._values["github_release"] = github_release

    @builtins.property
    def jsii_release_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Version requirement of ``jsii-release`` which is used to publish modules to npm.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("jsii_release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Major version to release from the default branch.

        If this is specified, we bump the latest version of this major version line.
        If not specified, we bump the global latest version.

        :default: - Major version is not enforced.

        :stability: experimental
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def npm_dist_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The npmDistTag to use when publishing from the default branch.

        To set the npm dist-tag for release branches, set the ``npmDistTag`` property
        for each branch.

        :default: "latest"

        :stability: experimental
        '''
        result = self._values.get("npm_dist_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(self) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) Steps to execute after build as part of the release workflow.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def prerelease(self) -> typing.Optional[builtins.str]:
        '''(experimental) Bump versions from the default branch as pre-releases (e.g. "beta", "alpha", "pre").

        :default: - normal semantic versions

        :stability: experimental
        '''
        result = self._values.get("prerelease")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def publish_dry_run(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Instead of actually publishing to package managers, just print the publishing command.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_tasks(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Define publishing tasks that can be executed manually as well as workflows.

        Normally, publishing only happens within automated workflows. Enable this
        in order to create a publishing task for each publishing activity.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("publish_tasks")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_branches(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, BranchOptions]]:
        '''(experimental) Defines additional release branches.

        A workflow will be created for each
        release branch which will publish releases from commits in this branch.
        Each release branch *must* be assigned a major version number which is used
        to enforce that versions published from that branch always use that major
        version. If multiple branches are used, the ``majorVersion`` field must also
        be provided for the default branch.

        :default:

        - no additional branches are used for release. you can use
        ``addBranch()`` to add additional branches.

        :stability: experimental
        '''
        result = self._values.get("release_branches")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, BranchOptions]], result)

    @builtins.property
    def release_every_commit(self) -> typing.Optional[builtins.bool]:
        '''(deprecated) Automatically release new versions every commit to one of branches in ``releaseBranches``.

        :default: true

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.continuous()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_every_commit")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a github issue on every failed publishing task.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def release_failure_issue_label(self) -> typing.Optional[builtins.str]:
        '''(experimental) The label to apply to issues indicating publish failures.

        Only applies if ``releaseFailureIssue`` is true.

        :default: "failed-release"

        :stability: experimental
        '''
        result = self._values.get("release_failure_issue_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_schedule(self) -> typing.Optional[builtins.str]:
        '''(deprecated) CRON schedule to trigger new releases.

        :default: - no scheduled releases

        :deprecated: Use ``releaseTrigger: ReleaseTrigger.scheduled()`` instead

        :stability: deprecated
        '''
        result = self._values.get("release_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Automatically add the given prefix to release tags. Useful if you are releasing on multiple branches with overlapping version numbers.

        Note: this prefix is used to detect the latest tagged version
        when bumping, so if you change this on a project with an existing version
        history, you may need to manually tag your latest release
        with the new prefix.

        :default: - no prefix

        :stability: experimental
        '''
        result = self._values.get("release_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_trigger(self) -> typing.Optional[ReleaseTrigger]:
        '''(experimental) The release trigger to use.

        :default: - Continuous releases (``ReleaseTrigger.continuous()``)

        :stability: experimental
        '''
        result = self._values.get("release_trigger")
        return typing.cast(typing.Optional[ReleaseTrigger], result)

    @builtins.property
    def release_workflow_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the default release workflow.

        :default: "Release"

        :stability: experimental
        '''
        result = self._values.get("release_workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def release_workflow_setup_steps(
        self,
    ) -> typing.Optional[typing.List[_JobStep_c3287c05]]:
        '''(experimental) A set of workflow steps to execute in order to setup the workflow container.

        :stability: experimental
        '''
        result = self._values.get("release_workflow_setup_steps")
        return typing.cast(typing.Optional[typing.List[_JobStep_c3287c05]], result)

    @builtins.property
    def versionrc_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Custom configuration used when creating changelog with standard-version package.

        Given values either append to default configuration or overwrite values in it.

        :default: - standard configuration applicable for GitHub repositories

        :stability: experimental
        '''
        result = self._values.get("versionrc_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def workflow_container_image(self) -> typing.Optional[builtins.str]:
        '''(experimental) Container image to use for GitHub workflows.

        :default: - default image

        :stability: experimental
        '''
        result = self._values.get("workflow_container_image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_runs_on(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Github Runner selection labels.

        :default: ["ubuntu-latest"]

        :stability: experimental
        '''
        result = self._values.get("workflow_runs_on")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def artifacts_directory(self) -> builtins.str:
        '''(experimental) A directory which will contain build artifacts.

        :default: "dist"

        :stability: experimental
        '''
        result = self._values.get("artifacts_directory")
        assert result is not None, "Required property 'artifacts_directory' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch(self) -> builtins.str:
        '''(experimental) The default branch name to release from.

        Use ``majorVersion`` to restrict this branch to only publish releases with a
        specific major version.

        You can add additional branches using ``addBranch()``.

        :stability: experimental
        '''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task(self) -> _Task_9fa875b6:
        '''(experimental) The task to execute in order to create the release artifacts.

        Artifacts are
        expected to reside under ``artifactsDirectory`` (defaults to ``dist/``) once
        build is complete.

        :stability: experimental
        '''
        result = self._values.get("task")
        assert result is not None, "Required property 'task' is missing"
        return typing.cast(_Task_9fa875b6, result)

    @builtins.property
    def version_file(self) -> builtins.str:
        '''(experimental) A name of a .json file to set the ``version`` field in after a bump.

        :stability: experimental

        Example::

            "package.json"
        '''
        result = self._values.get("version_file")
        assert result is not None, "Required property 'version_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def github_release(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create a GitHub release for each release.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("github_release")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReleaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BranchOptions",
    "CodeArtifactOptions",
    "CommonPublishOptions",
    "GitHubReleasesPublishOptions",
    "GitPublishOptions",
    "GoPublishOptions",
    "JsiiReleaseMaven",
    "JsiiReleaseNpm",
    "JsiiReleaseNuget",
    "JsiiReleasePyPi",
    "ManualReleaseOptions",
    "MavenPublishOptions",
    "NpmPublishOptions",
    "NugetPublishOptions",
    "Publisher",
    "PublisherOptions",
    "PyPiPublishOptions",
    "Release",
    "ReleaseOptions",
    "ReleaseProjectOptions",
    "ReleaseTrigger",
    "ScheduledReleaseOptions",
]

publication.publish()
