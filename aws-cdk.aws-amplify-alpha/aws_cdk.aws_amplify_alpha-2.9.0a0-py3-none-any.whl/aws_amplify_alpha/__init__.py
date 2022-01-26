'''
# AWS Amplify Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

The AWS Amplify Console provides a Git-based workflow for deploying and hosting fullstack serverless web applications. A fullstack serverless app consists of a backend built with cloud resources such as GraphQL or REST APIs, file and data storage, and a frontend built with single page application frameworks such as React, Angular, Vue, or Gatsby.

## Setting up an app with branches, custom rules and a domain

To set up an Amplify Console app, define an `App`:

```python
# Example automatically generated from non-compiling source. May contain errors.
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_amplify_alpha as amplify
import aws_cdk as cdk

amplify_app = amplify.App(self, "MyApp",
    source_code_provider=amplify.GitHubSourceCodeProvider(
        owner="<user>",
        repository="<repo>",
        oauth_token=cdk.SecretValue.secrets_manager("my-github-token")
    ),
    build_spec=codebuild.BuildSpec.from_object_to_yaml({ # Alternatively add a `amplify.yml` to the repo
        "version": "1.0",
        "frontend": {
            "phases": {
                "pre_build": {
                    "commands": ["yarn"
                    ]
                },
                "build": {
                    "commands": ["yarn build"
                    ]
                }
            },
            "artifacts": {
                "base_directory": "public",
                "files": -"**/*"
            }
        }})
)
```

To connect your `App` to GitLab, use the `GitLabSourceCodeProvider`:

```python
# Example automatically generated from non-compiling source. May contain errors.
amplify_app = amplify.App(self, "MyApp",
    source_code_provider=amplify.GitLabSourceCodeProvider(
        owner="<user>",
        repository="<repo>",
        oauth_token=cdk.SecretValue.secrets_manager("my-gitlab-token")
    )
)
```

To connect your `App` to CodeCommit, use the `CodeCommitSourceCodeProvider`:

```python
# Example automatically generated from non-compiling source. May contain errors.
repository = codecommit.Repository(self, "Repo",
    repository_name="my-repo"
)

amplify_app = amplify.App(self, "App",
    source_code_provider=amplify.CodeCommitSourceCodeProvider(repository=repository)
)
```

The IAM role associated with the `App` will automatically be granted the permission
to pull the CodeCommit repository.

Add branches:

```python
# Example automatically generated from non-compiling source. May contain errors.
master = amplify_app.add_branch("master") # `id` will be used as repo branch name
dev = amplify_app.add_branch("dev")
dev.add_environment("STAGE", "dev")
```

Auto build and pull request preview are enabled by default.

Add custom rules for redirection:

```python
# Example automatically generated from non-compiling source. May contain errors.
amplify_app.add_custom_rule(
    source="/docs/specific-filename.html",
    target="/documents/different-filename.html",
    status=amplify.RedirectStatus.TEMPORARY_REDIRECT
)
```

When working with a single page application (SPA), use the
`CustomRule.SINGLE_PAGE_APPLICATION_REDIRECT` to set up a 200
rewrite for all files to `index.html` except for the following
file extensions: css, gif, ico, jpg, js, png, txt, svg, woff,
ttf, map, json, webmanifest.

```python
# Example automatically generated from non-compiling source. May contain errors.
my_single_page_app.add_custom_rule(amplify.CustomRule.SINGLE_PAGE_APPLICATION_REDIRECT)
```

Add a domain and map sub domains to branches:

```python
# Example automatically generated from non-compiling source. May contain errors.
domain = amplify_app.add_domain("example.com",
    enable_auto_subdomain=True,  # in case subdomains should be auto registered for branches
    auto_subdomain_creation_patterns=["*", "pr*"]
)
domain.map_root(master) # map master branch to domain root
domain.map_sub_domain(master, "www")
domain.map_sub_domain(dev)
```

## Restricting access

Password protect the app with basic auth by specifying the `basicAuth` prop.

Use `BasicAuth.fromCredentials` when referencing an existing secret:

```python
# Example automatically generated from non-compiling source. May contain errors.
amplify_app = amplify.App(self, "MyApp",
    repository="https://github.com/<user>/<repo>",
    oauth_token=cdk.SecretValue.secrets_manager("my-github-token"),
    basic_auth=amplify.BasicAuth.from_credentials("username", cdk.SecretValue.secrets_manager("my-github-token"))
)
```

Use `BasicAuth.fromGeneratedPassword` to generate a password in Secrets Manager:

```python
# Example automatically generated from non-compiling source. May contain errors.
amplify_app = amplify.App(self, "MyApp",
    repository="https://github.com/<user>/<repo>",
    oauth_token=cdk.SecretValue.secrets_manager("my-github-token"),
    basic_auth=amplify.BasicAuth.from_generated_password("username")
)
```

Basic auth can be added to specific branches:

```python
# Example automatically generated from non-compiling source. May contain errors.
app.add_branch("feature/next",
    basic_auth=amplify.BasicAuth.from_generated_password("username")
)
```

## Automatically creating and deleting branches

Use the `autoBranchCreation` and `autoBranchDeletion` props to control creation/deletion
of branches:

```python
# Example automatically generated from non-compiling source. May contain errors.
amplify_app = amplify.App(self, "MyApp",
    repository="https://github.com/<user>/<repo>",
    oauth_token=cdk.SecretValue.secrets_manager("my-github-token"),
    auto_branch_creation={ # Automatically connect branches that match a pattern set
        "patterns": ["feature/*", "test/*"]},
    auto_branch_deletion=True
)
```

## Adding custom response headers

Use the `customResponseHeaders` prop to configure custom response headers for an Amplify app:

```python
# Example automatically generated from non-compiling source. May contain errors.
amplify_app = amplify.App(stack, "App",
    source_code_provider=amplify.GitHubSourceCodeProvider(
        owner="<user>",
        repository="<repo>",
        oauth_token=cdk.SecretValue.secrets_manager("my-github-token")
    ),
    custom_response_headers=[{
        "pattern": "*.json",
        "headers": {
            "custom-header-name-1": "custom-header-value-1",
            "custom-header-name-2": "custom-header-value-2"
        }
    }, {
        "pattern": "/path/*",
        "headers": {
            "custom-header-name-1": "custom-header-value-2"
        }
    }
    ]
)
```

## Deploying Assets

`sourceCodeProvider` is optional; when this is not specified the Amplify app can be deployed to using `.zip` packages. The `asset` property can be used to deploy S3 assets to Amplify as part of the CDK:

```python
# Example automatically generated from non-compiling source. May contain errors.
asset = assets.Asset(self, "SampleAsset")
amplify_app = amplify.App(self, "MyApp")
branch = amplify_app.add_branch("dev", asset=asset)
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk
import aws_cdk.aws_codebuild
import aws_cdk.aws_codecommit
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_s3_assets
import constructs


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.AppProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_name": "appName",
        "auto_branch_creation": "autoBranchCreation",
        "auto_branch_deletion": "autoBranchDeletion",
        "basic_auth": "basicAuth",
        "build_spec": "buildSpec",
        "custom_response_headers": "customResponseHeaders",
        "custom_rules": "customRules",
        "description": "description",
        "environment_variables": "environmentVariables",
        "role": "role",
        "source_code_provider": "sourceCodeProvider",
    },
)
class AppProps:
    def __init__(
        self,
        *,
        app_name: typing.Optional[builtins.str] = None,
        auto_branch_creation: typing.Optional["AutoBranchCreation"] = None,
        auto_branch_deletion: typing.Optional[builtins.bool] = None,
        basic_auth: typing.Optional["BasicAuth"] = None,
        build_spec: typing.Optional[aws_cdk.aws_codebuild.BuildSpec] = None,
        custom_response_headers: typing.Optional[typing.Sequence["CustomResponseHeader"]] = None,
        custom_rules: typing.Optional[typing.Sequence["CustomRule"]] = None,
        description: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        source_code_provider: typing.Optional["ISourceCodeProvider"] = None,
    ) -> None:
        '''(experimental) Properties for an App.

        :param app_name: (experimental) The name for the application. Default: - a CDK generated name
        :param auto_branch_creation: (experimental) The auto branch creation configuration. Use this to automatically create branches that match a certain pattern. Default: - no auto branch creation
        :param auto_branch_deletion: (experimental) Automatically disconnect a branch in the Amplify Console when you delete a branch from your Git repository. Default: false
        :param basic_auth: (experimental) The Basic Auth configuration. Use this to set password protection at an app level to all your branches. Default: - no password protection
        :param build_spec: (experimental) BuildSpec for the application. Alternatively, add a ``amplify.yml`` file to the repository. Default: - no build spec
        :param custom_response_headers: (experimental) The custom HTTP response headers for an Amplify app. Default: - no custom response headers
        :param custom_rules: (experimental) Custom rewrite/redirect rules for the application. Default: - no custom rewrite/redirect rules
        :param description: (experimental) A description for the application. Default: - no description
        :param environment_variables: (experimental) Environment variables for the application. All environment variables that you add are encrypted to prevent rogue access so you can use them to store secret information. Default: - no environment variables
        :param role: (experimental) The IAM service role to associate with the application. The App implements IGrantable. Default: - a new role is created
        :param source_code_provider: (experimental) The source code provider for this application. Default: - not connected to a source code provider

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.aws_amplify_alpha as amplify
            import aws_cdk as cdk
            
            amplify_app = amplify.App(self, "MyApp",
                source_code_provider=amplify.GitHubSourceCodeProvider(
                    owner="<user>",
                    repository="<repo>",
                    oauth_token=cdk.SecretValue.secrets_manager("my-github-token")
                ),
                build_spec=codebuild.BuildSpec.from_object_to_yaml({ # Alternatively add a `amplify.yml` to the repo
                    "version": "1.0",
                    "frontend": {
                        "phases": {
                            "pre_build": {
                                "commands": ["yarn"
                                ]
                            },
                            "build": {
                                "commands": ["yarn build"
                                ]
                            }
                        },
                        "artifacts": {
                            "base_directory": "public",
                            "files": -"**/*"
                        }
                    }})
            )
        '''
        if isinstance(auto_branch_creation, dict):
            auto_branch_creation = AutoBranchCreation(**auto_branch_creation)
        self._values: typing.Dict[str, typing.Any] = {}
        if app_name is not None:
            self._values["app_name"] = app_name
        if auto_branch_creation is not None:
            self._values["auto_branch_creation"] = auto_branch_creation
        if auto_branch_deletion is not None:
            self._values["auto_branch_deletion"] = auto_branch_deletion
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if custom_response_headers is not None:
            self._values["custom_response_headers"] = custom_response_headers
        if custom_rules is not None:
            self._values["custom_rules"] = custom_rules
        if description is not None:
            self._values["description"] = description
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if role is not None:
            self._values["role"] = role
        if source_code_provider is not None:
            self._values["source_code_provider"] = source_code_provider

    @builtins.property
    def app_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name for the application.

        :default: - a CDK generated name

        :stability: experimental
        '''
        result = self._values.get("app_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_branch_creation(self) -> typing.Optional["AutoBranchCreation"]:
        '''(experimental) The auto branch creation configuration.

        Use this to automatically create
        branches that match a certain pattern.

        :default: - no auto branch creation

        :stability: experimental
        '''
        result = self._values.get("auto_branch_creation")
        return typing.cast(typing.Optional["AutoBranchCreation"], result)

    @builtins.property
    def auto_branch_deletion(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically disconnect a branch in the Amplify Console when you delete a branch from your Git repository.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("auto_branch_deletion")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def basic_auth(self) -> typing.Optional["BasicAuth"]:
        '''(experimental) The Basic Auth configuration.

        Use this to set password protection at an
        app level to all your branches.

        :default: - no password protection

        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional["BasicAuth"], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[aws_cdk.aws_codebuild.BuildSpec]:
        '''(experimental) BuildSpec for the application.

        Alternatively, add a ``amplify.yml``
        file to the repository.

        :default: - no build spec

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/build-settings.html
        :stability: experimental
        '''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.BuildSpec], result)

    @builtins.property
    def custom_response_headers(
        self,
    ) -> typing.Optional[typing.List["CustomResponseHeader"]]:
        '''(experimental) The custom HTTP response headers for an Amplify app.

        :default: - no custom response headers

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/custom-headers.html
        :stability: experimental
        '''
        result = self._values.get("custom_response_headers")
        return typing.cast(typing.Optional[typing.List["CustomResponseHeader"]], result)

    @builtins.property
    def custom_rules(self) -> typing.Optional[typing.List["CustomRule"]]:
        '''(experimental) Custom rewrite/redirect rules for the application.

        :default: - no custom rewrite/redirect rules

        :stability: experimental
        '''
        result = self._values.get("custom_rules")
        return typing.cast(typing.Optional[typing.List["CustomRule"]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description for the application.

        :default: - no description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables for the application.

        All environment variables that you add are encrypted to prevent rogue
        access so you can use them to store secret information.

        :default: - no environment variables

        :stability: experimental
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM service role to associate with the application.

        The App
        implements IGrantable.

        :default: - a new role is created

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def source_code_provider(self) -> typing.Optional["ISourceCodeProvider"]:
        '''(experimental) The source code provider for this application.

        :default: - not connected to a source code provider

        :stability: experimental
        '''
        result = self._values.get("source_code_provider")
        return typing.cast(typing.Optional["ISourceCodeProvider"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.AutoBranchCreation",
    jsii_struct_bases=[],
    name_mapping={
        "auto_build": "autoBuild",
        "basic_auth": "basicAuth",
        "build_spec": "buildSpec",
        "environment_variables": "environmentVariables",
        "patterns": "patterns",
        "pull_request_environment_name": "pullRequestEnvironmentName",
        "pull_request_preview": "pullRequestPreview",
        "stage": "stage",
    },
)
class AutoBranchCreation:
    def __init__(
        self,
        *,
        auto_build: typing.Optional[builtins.bool] = None,
        basic_auth: typing.Optional["BasicAuth"] = None,
        build_spec: typing.Optional[aws_cdk.aws_codebuild.BuildSpec] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        pull_request_preview: typing.Optional[builtins.bool] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Auto branch creation configuration.

        :param auto_build: (experimental) Whether to enable auto building for the auto created branch. Default: true
        :param basic_auth: (experimental) The Basic Auth configuration. Use this to set password protection for the auto created branch. Default: - no password protection
        :param build_spec: (experimental) Build spec for the auto created branch. Default: - application build spec
        :param environment_variables: (experimental) Environment variables for the auto created branch. All environment variables that you add are encrypted to prevent rogue access so you can use them to store secret information. Default: - application environment variables
        :param patterns: (experimental) Automated branch creation glob patterns. Default: - all repository branches
        :param pull_request_environment_name: (experimental) The dedicated backend environment for the pull request previews of the auto created branch. Default: - automatically provision a temporary backend
        :param pull_request_preview: (experimental) Whether to enable pull request preview for the auto created branch. Default: true
        :param stage: (experimental) Stage for the auto created branch. Default: - no stage

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            from aws_cdk import aws_codebuild as codebuild
            
            # basic_auth: amplify_alpha.BasicAuth
            # build_spec: codebuild.BuildSpec
            
            auto_branch_creation = amplify_alpha.AutoBranchCreation(
                auto_build=False,
                basic_auth=basic_auth,
                build_spec=build_spec,
                environment_variables={
                    "environment_variables_key": "environmentVariables"
                },
                patterns=["patterns"],
                pull_request_environment_name="pullRequestEnvironmentName",
                pull_request_preview=False,
                stage="stage"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if auto_build is not None:
            self._values["auto_build"] = auto_build
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if patterns is not None:
            self._values["patterns"] = patterns
        if pull_request_environment_name is not None:
            self._values["pull_request_environment_name"] = pull_request_environment_name
        if pull_request_preview is not None:
            self._values["pull_request_preview"] = pull_request_preview
        if stage is not None:
            self._values["stage"] = stage

    @builtins.property
    def auto_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable auto building for the auto created branch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def basic_auth(self) -> typing.Optional["BasicAuth"]:
        '''(experimental) The Basic Auth configuration.

        Use this to set password protection for
        the auto created branch.

        :default: - no password protection

        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional["BasicAuth"], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[aws_cdk.aws_codebuild.BuildSpec]:
        '''(experimental) Build spec for the auto created branch.

        :default: - application build spec

        :stability: experimental
        '''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.BuildSpec], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables for the auto created branch.

        All environment variables that you add are encrypted to prevent rogue
        access so you can use them to store secret information.

        :default: - application environment variables

        :stability: experimental
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def patterns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Automated branch creation glob patterns.

        :default: - all repository branches

        :stability: experimental
        '''
        result = self._values.get("patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def pull_request_environment_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The dedicated backend environment for the pull request previews of the auto created branch.

        :default: - automatically provision a temporary backend

        :stability: experimental
        '''
        result = self._values.get("pull_request_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_preview(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable pull request preview for the auto created branch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_preview")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Stage for the auto created branch.

        :default: - no stage

        :stability: experimental
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoBranchCreation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BasicAuth(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-amplify-alpha.BasicAuth",
):
    '''(experimental) Basic Auth configuration.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_amplify_alpha as amplify_alpha
        import aws_cdk as cdk
        from aws_cdk import aws_kms as kms
        
        # key: kms.Key
        # secret_value: cdk.SecretValue
        
        basic_auth = amplify_alpha.BasicAuth(
            username="username",
        
            # the properties below are optional
            encryption_key=key,
            password=secret_value
        )
    '''

    def __init__(
        self,
        *,
        username: builtins.str,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        password: typing.Optional[aws_cdk.SecretValue] = None,
    ) -> None:
        '''
        :param username: (experimental) The username.
        :param encryption_key: (experimental) The encryption key to use to encrypt the password when it's generated in Secrets Manager. Default: - default master key
        :param password: (experimental) The password. Default: - A Secrets Manager generated password

        :stability: experimental
        '''
        props = BasicAuthProps(
            username=username, encryption_key=encryption_key, password=password
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="fromCredentials") # type: ignore[misc]
    @builtins.classmethod
    def from_credentials(
        cls,
        username: builtins.str,
        password: aws_cdk.SecretValue,
    ) -> "BasicAuth":
        '''(experimental) Creates a Basic Auth configuration from a username and a password.

        :param username: The username.
        :param password: The password.

        :stability: experimental
        '''
        return typing.cast("BasicAuth", jsii.sinvoke(cls, "fromCredentials", [username, password]))

    @jsii.member(jsii_name="fromGeneratedPassword") # type: ignore[misc]
    @builtins.classmethod
    def from_generated_password(
        cls,
        username: builtins.str,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
    ) -> "BasicAuth":
        '''(experimental) Creates a Basic Auth configuration with a password generated in Secrets Manager.

        :param username: The username.
        :param encryption_key: The encryption key to use to encrypt the password in Secrets Manager.

        :stability: experimental
        '''
        return typing.cast("BasicAuth", jsii.sinvoke(cls, "fromGeneratedPassword", [username, encryption_key]))

    @jsii.member(jsii_name="bind")
    def bind(self, scope: constructs.Construct, id: builtins.str) -> "BasicAuthConfig":
        '''(experimental) Binds this Basic Auth configuration to an App.

        :param scope: -
        :param id: -

        :stability: experimental
        '''
        return typing.cast("BasicAuthConfig", jsii.invoke(self, "bind", [scope, id]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.BasicAuthConfig",
    jsii_struct_bases=[],
    name_mapping={
        "enable_basic_auth": "enableBasicAuth",
        "password": "password",
        "username": "username",
    },
)
class BasicAuthConfig:
    def __init__(
        self,
        *,
        enable_basic_auth: builtins.bool,
        password: builtins.str,
        username: builtins.str,
    ) -> None:
        '''(experimental) A Basic Auth configuration.

        :param enable_basic_auth: (experimental) Whether to enable Basic Auth.
        :param password: (experimental) The password.
        :param username: (experimental) The username.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            
            basic_auth_config = amplify_alpha.BasicAuthConfig(
                enable_basic_auth=False,
                password="password",
                username="username"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "enable_basic_auth": enable_basic_auth,
            "password": password,
            "username": username,
        }

    @builtins.property
    def enable_basic_auth(self) -> builtins.bool:
        '''(experimental) Whether to enable Basic Auth.

        :stability: experimental
        '''
        result = self._values.get("enable_basic_auth")
        assert result is not None, "Required property 'enable_basic_auth' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def password(self) -> builtins.str:
        '''(experimental) The password.

        :stability: experimental
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''(experimental) The username.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BasicAuthConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.BasicAuthProps",
    jsii_struct_bases=[],
    name_mapping={
        "username": "username",
        "encryption_key": "encryptionKey",
        "password": "password",
    },
)
class BasicAuthProps:
    def __init__(
        self,
        *,
        username: builtins.str,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        password: typing.Optional[aws_cdk.SecretValue] = None,
    ) -> None:
        '''(experimental) Properties for a BasicAuth.

        :param username: (experimental) The username.
        :param encryption_key: (experimental) The encryption key to use to encrypt the password when it's generated in Secrets Manager. Default: - default master key
        :param password: (experimental) The password. Default: - A Secrets Manager generated password

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            import aws_cdk as cdk
            from aws_cdk import aws_kms as kms
            
            # key: kms.Key
            # secret_value: cdk.SecretValue
            
            basic_auth_props = amplify_alpha.BasicAuthProps(
                username="username",
            
                # the properties below are optional
                encryption_key=key,
                password=secret_value
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "username": username,
        }
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if password is not None:
            self._values["password"] = password

    @builtins.property
    def username(self) -> builtins.str:
        '''(experimental) The username.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''(experimental) The encryption key to use to encrypt the password when it's generated in Secrets Manager.

        :default: - default master key

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def password(self) -> typing.Optional[aws_cdk.SecretValue]:
        '''(experimental) The password.

        :default: - A Secrets Manager generated password

        :stability: experimental
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[aws_cdk.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BasicAuthProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.BranchOptions",
    jsii_struct_bases=[],
    name_mapping={
        "asset": "asset",
        "auto_build": "autoBuild",
        "basic_auth": "basicAuth",
        "branch_name": "branchName",
        "build_spec": "buildSpec",
        "description": "description",
        "environment_variables": "environmentVariables",
        "pull_request_environment_name": "pullRequestEnvironmentName",
        "pull_request_preview": "pullRequestPreview",
        "stage": "stage",
    },
)
class BranchOptions:
    def __init__(
        self,
        *,
        asset: typing.Optional[aws_cdk.aws_s3_assets.Asset] = None,
        auto_build: typing.Optional[builtins.bool] = None,
        basic_auth: typing.Optional[BasicAuth] = None,
        branch_name: typing.Optional[builtins.str] = None,
        build_spec: typing.Optional[aws_cdk.aws_codebuild.BuildSpec] = None,
        description: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        pull_request_preview: typing.Optional[builtins.bool] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options to add a branch to an application.

        :param asset: (experimental) Asset for deployment. The Amplify app must not have a sourceCodeProvider configured as this resource uses Amplify's startDeployment API to initiate and deploy a S3 asset onto the App. Default: - no asset
        :param auto_build: (experimental) Whether to enable auto building for the branch. Default: true
        :param basic_auth: (experimental) The Basic Auth configuration. Use this to set password protection for the branch Default: - no password protection
        :param branch_name: (experimental) The name of the branch. Default: - the construct's id
        :param build_spec: (experimental) BuildSpec for the branch. Default: - no build spec
        :param description: (experimental) A description for the branch. Default: - no description
        :param environment_variables: (experimental) Environment variables for the branch. All environment variables that you add are encrypted to prevent rogue access so you can use them to store secret information. Default: - application environment variables
        :param pull_request_environment_name: (experimental) The dedicated backend environment for the pull request previews. Default: - automatically provision a temporary backend
        :param pull_request_preview: (experimental) Whether to enable pull request preview for the branch. Default: true
        :param stage: (experimental) Stage for the branch. Default: - no stage

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            from aws_cdk import aws_codebuild as codebuild
            from aws_cdk import aws_s3_assets as s3_assets
            
            # asset: s3_assets.Asset
            # basic_auth: amplify_alpha.BasicAuth
            # build_spec: codebuild.BuildSpec
            
            branch_options = amplify_alpha.BranchOptions(
                asset=asset,
                auto_build=False,
                basic_auth=basic_auth,
                branch_name="branchName",
                build_spec=build_spec,
                description="description",
                environment_variables={
                    "environment_variables_key": "environmentVariables"
                },
                pull_request_environment_name="pullRequestEnvironmentName",
                pull_request_preview=False,
                stage="stage"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if asset is not None:
            self._values["asset"] = asset
        if auto_build is not None:
            self._values["auto_build"] = auto_build
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth
        if branch_name is not None:
            self._values["branch_name"] = branch_name
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if description is not None:
            self._values["description"] = description
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if pull_request_environment_name is not None:
            self._values["pull_request_environment_name"] = pull_request_environment_name
        if pull_request_preview is not None:
            self._values["pull_request_preview"] = pull_request_preview
        if stage is not None:
            self._values["stage"] = stage

    @builtins.property
    def asset(self) -> typing.Optional[aws_cdk.aws_s3_assets.Asset]:
        '''(experimental) Asset for deployment.

        The Amplify app must not have a sourceCodeProvider configured as this resource uses Amplify's
        startDeployment API to initiate and deploy a S3 asset onto the App.

        :default: - no asset

        :stability: experimental
        '''
        result = self._values.get("asset")
        return typing.cast(typing.Optional[aws_cdk.aws_s3_assets.Asset], result)

    @builtins.property
    def auto_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable auto building for the branch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def basic_auth(self) -> typing.Optional[BasicAuth]:
        '''(experimental) The Basic Auth configuration.

        Use this to set password protection for
        the branch

        :default: - no password protection

        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional[BasicAuth], result)

    @builtins.property
    def branch_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the branch.

        :default: - the construct's id

        :stability: experimental
        '''
        result = self._values.get("branch_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[aws_cdk.aws_codebuild.BuildSpec]:
        '''(experimental) BuildSpec for the branch.

        :default: - no build spec

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/build-settings.html
        :stability: experimental
        '''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.BuildSpec], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description for the branch.

        :default: - no description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables for the branch.

        All environment variables that you add are encrypted to prevent rogue
        access so you can use them to store secret information.

        :default: - application environment variables

        :stability: experimental
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def pull_request_environment_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The dedicated backend environment for the pull request previews.

        :default: - automatically provision a temporary backend

        :stability: experimental
        '''
        result = self._values.get("pull_request_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_preview(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable pull request preview for the branch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_preview")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Stage for the branch.

        :default: - no stage

        :stability: experimental
        '''
        result = self._values.get("stage")
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
    jsii_type="@aws-cdk/aws-amplify-alpha.BranchProps",
    jsii_struct_bases=[BranchOptions],
    name_mapping={
        "asset": "asset",
        "auto_build": "autoBuild",
        "basic_auth": "basicAuth",
        "branch_name": "branchName",
        "build_spec": "buildSpec",
        "description": "description",
        "environment_variables": "environmentVariables",
        "pull_request_environment_name": "pullRequestEnvironmentName",
        "pull_request_preview": "pullRequestPreview",
        "stage": "stage",
        "app": "app",
    },
)
class BranchProps(BranchOptions):
    def __init__(
        self,
        *,
        asset: typing.Optional[aws_cdk.aws_s3_assets.Asset] = None,
        auto_build: typing.Optional[builtins.bool] = None,
        basic_auth: typing.Optional[BasicAuth] = None,
        branch_name: typing.Optional[builtins.str] = None,
        build_spec: typing.Optional[aws_cdk.aws_codebuild.BuildSpec] = None,
        description: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        pull_request_preview: typing.Optional[builtins.bool] = None,
        stage: typing.Optional[builtins.str] = None,
        app: "IApp",
    ) -> None:
        '''(experimental) Properties for a Branch.

        :param asset: (experimental) Asset for deployment. The Amplify app must not have a sourceCodeProvider configured as this resource uses Amplify's startDeployment API to initiate and deploy a S3 asset onto the App. Default: - no asset
        :param auto_build: (experimental) Whether to enable auto building for the branch. Default: true
        :param basic_auth: (experimental) The Basic Auth configuration. Use this to set password protection for the branch Default: - no password protection
        :param branch_name: (experimental) The name of the branch. Default: - the construct's id
        :param build_spec: (experimental) BuildSpec for the branch. Default: - no build spec
        :param description: (experimental) A description for the branch. Default: - no description
        :param environment_variables: (experimental) Environment variables for the branch. All environment variables that you add are encrypted to prevent rogue access so you can use them to store secret information. Default: - application environment variables
        :param pull_request_environment_name: (experimental) The dedicated backend environment for the pull request previews. Default: - automatically provision a temporary backend
        :param pull_request_preview: (experimental) Whether to enable pull request preview for the branch. Default: true
        :param stage: (experimental) Stage for the branch. Default: - no stage
        :param app: (experimental) The application within which the branch must be created.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            from aws_cdk import aws_codebuild as codebuild
            from aws_cdk import aws_s3_assets as s3_assets
            
            # app: amplify_alpha.App
            # asset: s3_assets.Asset
            # basic_auth: amplify_alpha.BasicAuth
            # build_spec: codebuild.BuildSpec
            
            branch_props = amplify_alpha.BranchProps(
                app=app,
            
                # the properties below are optional
                asset=asset,
                auto_build=False,
                basic_auth=basic_auth,
                branch_name="branchName",
                build_spec=build_spec,
                description="description",
                environment_variables={
                    "environment_variables_key": "environmentVariables"
                },
                pull_request_environment_name="pullRequestEnvironmentName",
                pull_request_preview=False,
                stage="stage"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app": app,
        }
        if asset is not None:
            self._values["asset"] = asset
        if auto_build is not None:
            self._values["auto_build"] = auto_build
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth
        if branch_name is not None:
            self._values["branch_name"] = branch_name
        if build_spec is not None:
            self._values["build_spec"] = build_spec
        if description is not None:
            self._values["description"] = description
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if pull_request_environment_name is not None:
            self._values["pull_request_environment_name"] = pull_request_environment_name
        if pull_request_preview is not None:
            self._values["pull_request_preview"] = pull_request_preview
        if stage is not None:
            self._values["stage"] = stage

    @builtins.property
    def asset(self) -> typing.Optional[aws_cdk.aws_s3_assets.Asset]:
        '''(experimental) Asset for deployment.

        The Amplify app must not have a sourceCodeProvider configured as this resource uses Amplify's
        startDeployment API to initiate and deploy a S3 asset onto the App.

        :default: - no asset

        :stability: experimental
        '''
        result = self._values.get("asset")
        return typing.cast(typing.Optional[aws_cdk.aws_s3_assets.Asset], result)

    @builtins.property
    def auto_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable auto building for the branch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def basic_auth(self) -> typing.Optional[BasicAuth]:
        '''(experimental) The Basic Auth configuration.

        Use this to set password protection for
        the branch

        :default: - no password protection

        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional[BasicAuth], result)

    @builtins.property
    def branch_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the branch.

        :default: - the construct's id

        :stability: experimental
        '''
        result = self._values.get("branch_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_spec(self) -> typing.Optional[aws_cdk.aws_codebuild.BuildSpec]:
        '''(experimental) BuildSpec for the branch.

        :default: - no build spec

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/build-settings.html
        :stability: experimental
        '''
        result = self._values.get("build_spec")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.BuildSpec], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) A description for the branch.

        :default: - no description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables for the branch.

        All environment variables that you add are encrypted to prevent rogue
        access so you can use them to store secret information.

        :default: - application environment variables

        :stability: experimental
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def pull_request_environment_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The dedicated backend environment for the pull request previews.

        :default: - automatically provision a temporary backend

        :stability: experimental
        '''
        result = self._values.get("pull_request_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_request_preview(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable pull request preview for the branch.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("pull_request_preview")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stage(self) -> typing.Optional[builtins.str]:
        '''(experimental) Stage for the branch.

        :default: - no stage

        :stability: experimental
        '''
        result = self._values.get("stage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def app(self) -> "IApp":
        '''(experimental) The application within which the branch must be created.

        :stability: experimental
        '''
        result = self._values.get("app")
        assert result is not None, "Required property 'app' is missing"
        return typing.cast("IApp", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BranchProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.CodeCommitSourceCodeProviderProps",
    jsii_struct_bases=[],
    name_mapping={"repository": "repository"},
)
class CodeCommitSourceCodeProviderProps:
    def __init__(self, *, repository: aws_cdk.aws_codecommit.IRepository) -> None:
        '''(experimental) Properties for a CodeCommit source code provider.

        :param repository: (experimental) The CodeCommit repository.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            from aws_cdk import aws_codecommit as codecommit
            
            # repository: codecommit.Repository
            
            code_commit_source_code_provider_props = amplify_alpha.CodeCommitSourceCodeProviderProps(
                repository=repository
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "repository": repository,
        }

    @builtins.property
    def repository(self) -> aws_cdk.aws_codecommit.IRepository:
        '''(experimental) The CodeCommit repository.

        :stability: experimental
        '''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(aws_cdk.aws_codecommit.IRepository, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeCommitSourceCodeProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.CustomResponseHeader",
    jsii_struct_bases=[],
    name_mapping={"headers": "headers", "pattern": "pattern"},
)
class CustomResponseHeader:
    def __init__(
        self,
        *,
        headers: typing.Mapping[builtins.str, builtins.str],
        pattern: builtins.str,
    ) -> None:
        '''(experimental) Custom response header of an Amplify App.

        :param headers: (experimental) The map of custom headers to be applied.
        :param pattern: (experimental) These custom headers will be applied to all URL file paths that match this pattern.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            
            custom_response_header = amplify_alpha.CustomResponseHeader(
                headers={
                    "headers_key": "headers"
                },
                pattern="pattern"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "headers": headers,
            "pattern": pattern,
        }

    @builtins.property
    def headers(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) The map of custom headers to be applied.

        :stability: experimental
        '''
        result = self._values.get("headers")
        assert result is not None, "Required property 'headers' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def pattern(self) -> builtins.str:
        '''(experimental) These custom headers will be applied to all URL file paths that match this pattern.

        :stability: experimental
        '''
        result = self._values.get("pattern")
        assert result is not None, "Required property 'pattern' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomResponseHeader(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CustomRule(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-amplify-alpha.CustomRule",
):
    '''(experimental) Custom rewrite/redirect rule for an Amplify App.

    :see: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html
    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_amplify_alpha as amplify_alpha
        
        custom_rule = amplify_alpha.CustomRule(
            source="source",
            target="target",
        
            # the properties below are optional
            condition="condition",
            status=amplify_alpha.RedirectStatus.REWRITE
        )
    '''

    def __init__(
        self,
        *,
        source: builtins.str,
        target: builtins.str,
        condition: typing.Optional[builtins.str] = None,
        status: typing.Optional["RedirectStatus"] = None,
    ) -> None:
        '''
        :param source: (experimental) The source pattern for a URL rewrite or redirect rule.
        :param target: (experimental) The target pattern for a URL rewrite or redirect rule.
        :param condition: (experimental) The condition for a URL rewrite or redirect rule, e.g. country code. Default: - no condition
        :param status: (experimental) The status code for a URL rewrite or redirect rule. Default: PERMANENT_REDIRECT

        :stability: experimental
        '''
        options = CustomRuleOptions(
            source=source, target=target, condition=condition, status=status
        )

        jsii.create(self.__class__, self, [options])

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SINGLE_PAGE_APPLICATION_REDIRECT")
    def SINGLE_PAGE_APPLICATION_REDIRECT(cls) -> "CustomRule":
        '''(experimental) Sets up a 200 rewrite for all paths to ``index.html`` except for path containing a file extension.

        :stability: experimental
        '''
        return typing.cast("CustomRule", jsii.sget(cls, "SINGLE_PAGE_APPLICATION_REDIRECT"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        '''(experimental) The source pattern for a URL rewrite or redirect rule.

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        '''(experimental) The target pattern for a URL rewrite or redirect rule.

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="condition")
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) The condition for a URL rewrite or redirect rule, e.g. country code.

        :default: - no condition

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "condition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional["RedirectStatus"]:
        '''(experimental) The status code for a URL rewrite or redirect rule.

        :default: PERMANENT_REDIRECT

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html
        :stability: experimental
        '''
        return typing.cast(typing.Optional["RedirectStatus"], jsii.get(self, "status"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.CustomRuleOptions",
    jsii_struct_bases=[],
    name_mapping={
        "source": "source",
        "target": "target",
        "condition": "condition",
        "status": "status",
    },
)
class CustomRuleOptions:
    def __init__(
        self,
        *,
        source: builtins.str,
        target: builtins.str,
        condition: typing.Optional[builtins.str] = None,
        status: typing.Optional["RedirectStatus"] = None,
    ) -> None:
        '''(experimental) Options for a custom rewrite/redirect rule for an Amplify App.

        :param source: (experimental) The source pattern for a URL rewrite or redirect rule.
        :param target: (experimental) The target pattern for a URL rewrite or redirect rule.
        :param condition: (experimental) The condition for a URL rewrite or redirect rule, e.g. country code. Default: - no condition
        :param status: (experimental) The status code for a URL rewrite or redirect rule. Default: PERMANENT_REDIRECT

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            
            custom_rule_options = amplify_alpha.CustomRuleOptions(
                source="source",
                target="target",
            
                # the properties below are optional
                condition="condition",
                status=amplify_alpha.RedirectStatus.REWRITE
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "source": source,
            "target": target,
        }
        if condition is not None:
            self._values["condition"] = condition
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def source(self) -> builtins.str:
        '''(experimental) The source pattern for a URL rewrite or redirect rule.

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html
        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target(self) -> builtins.str:
        '''(experimental) The target pattern for a URL rewrite or redirect rule.

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html
        :stability: experimental
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) The condition for a URL rewrite or redirect rule, e.g. country code.

        :default: - no condition

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html
        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional["RedirectStatus"]:
        '''(experimental) The status code for a URL rewrite or redirect rule.

        :default: PERMANENT_REDIRECT

        :see: https://docs.aws.amazon.com/amplify/latest/userguide/redirects.html
        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["RedirectStatus"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomRuleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Domain(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-amplify-alpha.Domain",
):
    '''(experimental) An Amplify Console domain.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_amplify_alpha as amplify_alpha
        from aws_cdk import aws_iam as iam
        
        # app: amplify_alpha.App
        # branch: amplify_alpha.Branch
        # role: iam.Role
        
        domain = amplify_alpha.Domain(self, "MyDomain",
            app=app,
        
            # the properties below are optional
            auto_subdomain_creation_patterns=["autoSubdomainCreationPatterns"],
            auto_sub_domain_iam_role=role,
            domain_name="domainName",
            enable_auto_subdomain=False,
            sub_domains=[amplify_alpha.SubDomain(
                branch=branch,
        
                # the properties below are optional
                prefix="prefix"
            )]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app: "IApp",
        auto_sub_domain_iam_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        auto_subdomain_creation_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        domain_name: typing.Optional[builtins.str] = None,
        enable_auto_subdomain: typing.Optional[builtins.bool] = None,
        sub_domains: typing.Optional[typing.Sequence["SubDomain"]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app: (experimental) The application to which the domain must be connected.
        :param auto_sub_domain_iam_role: (experimental) The IAM role with access to Route53 when using enableAutoSubdomain. Default: the IAM role from App.grantPrincipal
        :param auto_subdomain_creation_patterns: (experimental) Branches which should automatically create subdomains. Default: - all repository branches ['*', 'pr*']
        :param domain_name: (experimental) The name of the domain. Default: - the construct's id
        :param enable_auto_subdomain: (experimental) Automatically create subdomains for connected branches. Default: false
        :param sub_domains: (experimental) Subdomains. Default: - use ``addSubDomain()`` to add subdomains

        :stability: experimental
        '''
        props = DomainProps(
            app=app,
            auto_sub_domain_iam_role=auto_sub_domain_iam_role,
            auto_subdomain_creation_patterns=auto_subdomain_creation_patterns,
            domain_name=domain_name,
            enable_auto_subdomain=enable_auto_subdomain,
            sub_domains=sub_domains,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="mapRoot")
    def map_root(self, branch: "IBranch") -> "Domain":
        '''(experimental) Maps a branch to the domain root.

        :param branch: -

        :stability: experimental
        '''
        return typing.cast("Domain", jsii.invoke(self, "mapRoot", [branch]))

    @jsii.member(jsii_name="mapSubDomain")
    def map_sub_domain(
        self,
        branch: "IBranch",
        prefix: typing.Optional[builtins.str] = None,
    ) -> "Domain":
        '''(experimental) Maps a branch to a sub domain.

        :param branch: The branch.
        :param prefix: The prefix. Use '' to map to the root of the domain. Defaults to branch name.

        :stability: experimental
        '''
        return typing.cast("Domain", jsii.invoke(self, "mapSubDomain", [branch, prefix]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) The ARN of the domain.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateRecord")
    def certificate_record(self) -> builtins.str:
        '''(experimental) The DNS Record for certificate verification.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "certificateRecord"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainAutoSubDomainCreationPatterns")
    def domain_auto_sub_domain_creation_patterns(self) -> typing.List[builtins.str]:
        '''(experimental) Branch patterns for the automatically created subdomain.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domainAutoSubDomainCreationPatterns"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainAutoSubDomainIamRole")
    def domain_auto_sub_domain_iam_role(self) -> builtins.str:
        '''(experimental) The IAM service role for the subdomain.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainAutoSubDomainIamRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainEnableAutoSubDomain")
    def domain_enable_auto_sub_domain(self) -> aws_cdk.IResolvable:
        '''(experimental) Specifies whether the automated creation of subdomains for branches is enabled.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(aws_cdk.IResolvable, jsii.get(self, "domainEnableAutoSubDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(experimental) The name of the domain.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainStatus")
    def domain_status(self) -> builtins.str:
        '''(experimental) The status of the domain association.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainStatus"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="statusReason")
    def status_reason(self) -> builtins.str:
        '''(experimental) The reason for the current status of the domain.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "statusReason"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.DomainOptions",
    jsii_struct_bases=[],
    name_mapping={
        "auto_subdomain_creation_patterns": "autoSubdomainCreationPatterns",
        "domain_name": "domainName",
        "enable_auto_subdomain": "enableAutoSubdomain",
        "sub_domains": "subDomains",
    },
)
class DomainOptions:
    def __init__(
        self,
        *,
        auto_subdomain_creation_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        domain_name: typing.Optional[builtins.str] = None,
        enable_auto_subdomain: typing.Optional[builtins.bool] = None,
        sub_domains: typing.Optional[typing.Sequence["SubDomain"]] = None,
    ) -> None:
        '''(experimental) Options to add a domain to an application.

        :param auto_subdomain_creation_patterns: (experimental) Branches which should automatically create subdomains. Default: - all repository branches ['*', 'pr*']
        :param domain_name: (experimental) The name of the domain. Default: - the construct's id
        :param enable_auto_subdomain: (experimental) Automatically create subdomains for connected branches. Default: false
        :param sub_domains: (experimental) Subdomains. Default: - use ``addSubDomain()`` to add subdomains

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            
            # branch: amplify_alpha.Branch
            
            domain_options = amplify_alpha.DomainOptions(
                auto_subdomain_creation_patterns=["autoSubdomainCreationPatterns"],
                domain_name="domainName",
                enable_auto_subdomain=False,
                sub_domains=[amplify_alpha.SubDomain(
                    branch=branch,
            
                    # the properties below are optional
                    prefix="prefix"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if auto_subdomain_creation_patterns is not None:
            self._values["auto_subdomain_creation_patterns"] = auto_subdomain_creation_patterns
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if enable_auto_subdomain is not None:
            self._values["enable_auto_subdomain"] = enable_auto_subdomain
        if sub_domains is not None:
            self._values["sub_domains"] = sub_domains

    @builtins.property
    def auto_subdomain_creation_patterns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Branches which should automatically create subdomains.

        :default: - all repository branches ['*', 'pr*']

        :stability: experimental
        '''
        result = self._values.get("auto_subdomain_creation_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the domain.

        :default: - the construct's id

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_auto_subdomain(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically create subdomains for connected branches.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_auto_subdomain")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sub_domains(self) -> typing.Optional[typing.List["SubDomain"]]:
        '''(experimental) Subdomains.

        :default: - use ``addSubDomain()`` to add subdomains

        :stability: experimental
        '''
        result = self._values.get("sub_domains")
        return typing.cast(typing.Optional[typing.List["SubDomain"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.DomainProps",
    jsii_struct_bases=[DomainOptions],
    name_mapping={
        "auto_subdomain_creation_patterns": "autoSubdomainCreationPatterns",
        "domain_name": "domainName",
        "enable_auto_subdomain": "enableAutoSubdomain",
        "sub_domains": "subDomains",
        "app": "app",
        "auto_sub_domain_iam_role": "autoSubDomainIamRole",
    },
)
class DomainProps(DomainOptions):
    def __init__(
        self,
        *,
        auto_subdomain_creation_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        domain_name: typing.Optional[builtins.str] = None,
        enable_auto_subdomain: typing.Optional[builtins.bool] = None,
        sub_domains: typing.Optional[typing.Sequence["SubDomain"]] = None,
        app: "IApp",
        auto_sub_domain_iam_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''(experimental) Properties for a Domain.

        :param auto_subdomain_creation_patterns: (experimental) Branches which should automatically create subdomains. Default: - all repository branches ['*', 'pr*']
        :param domain_name: (experimental) The name of the domain. Default: - the construct's id
        :param enable_auto_subdomain: (experimental) Automatically create subdomains for connected branches. Default: false
        :param sub_domains: (experimental) Subdomains. Default: - use ``addSubDomain()`` to add subdomains
        :param app: (experimental) The application to which the domain must be connected.
        :param auto_sub_domain_iam_role: (experimental) The IAM role with access to Route53 when using enableAutoSubdomain. Default: the IAM role from App.grantPrincipal

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            from aws_cdk import aws_iam as iam
            
            # app: amplify_alpha.App
            # branch: amplify_alpha.Branch
            # role: iam.Role
            
            domain_props = amplify_alpha.DomainProps(
                app=app,
            
                # the properties below are optional
                auto_subdomain_creation_patterns=["autoSubdomainCreationPatterns"],
                auto_sub_domain_iam_role=role,
                domain_name="domainName",
                enable_auto_subdomain=False,
                sub_domains=[amplify_alpha.SubDomain(
                    branch=branch,
            
                    # the properties below are optional
                    prefix="prefix"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app": app,
        }
        if auto_subdomain_creation_patterns is not None:
            self._values["auto_subdomain_creation_patterns"] = auto_subdomain_creation_patterns
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if enable_auto_subdomain is not None:
            self._values["enable_auto_subdomain"] = enable_auto_subdomain
        if sub_domains is not None:
            self._values["sub_domains"] = sub_domains
        if auto_sub_domain_iam_role is not None:
            self._values["auto_sub_domain_iam_role"] = auto_sub_domain_iam_role

    @builtins.property
    def auto_subdomain_creation_patterns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Branches which should automatically create subdomains.

        :default: - all repository branches ['*', 'pr*']

        :stability: experimental
        '''
        result = self._values.get("auto_subdomain_creation_patterns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the domain.

        :default: - the construct's id

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_auto_subdomain(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Automatically create subdomains for connected branches.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("enable_auto_subdomain")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sub_domains(self) -> typing.Optional[typing.List["SubDomain"]]:
        '''(experimental) Subdomains.

        :default: - use ``addSubDomain()`` to add subdomains

        :stability: experimental
        '''
        result = self._values.get("sub_domains")
        return typing.cast(typing.Optional[typing.List["SubDomain"]], result)

    @builtins.property
    def app(self) -> "IApp":
        '''(experimental) The application to which the domain must be connected.

        :stability: experimental
        '''
        result = self._values.get("app")
        assert result is not None, "Required property 'app' is missing"
        return typing.cast("IApp", result)

    @builtins.property
    def auto_sub_domain_iam_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM role with access to Route53 when using enableAutoSubdomain.

        :default: the IAM role from App.grantPrincipal

        :stability: experimental
        '''
        result = self._values.get("auto_sub_domain_iam_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DomainProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.GitHubSourceCodeProviderProps",
    jsii_struct_bases=[],
    name_mapping={
        "oauth_token": "oauthToken",
        "owner": "owner",
        "repository": "repository",
    },
)
class GitHubSourceCodeProviderProps:
    def __init__(
        self,
        *,
        oauth_token: aws_cdk.SecretValue,
        owner: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''(experimental) Properties for a GitHub source code provider.

        :param oauth_token: (experimental) A personal access token with the ``repo`` scope.
        :param owner: (experimental) The user or organization owning the repository.
        :param repository: (experimental) The name of the repository.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            import aws_cdk.aws_codebuild as codebuild
            import aws_cdk.aws_amplify_alpha as amplify
            import aws_cdk as cdk
            
            amplify_app = amplify.App(self, "MyApp",
                source_code_provider=amplify.GitHubSourceCodeProvider(
                    owner="<user>",
                    repository="<repo>",
                    oauth_token=cdk.SecretValue.secrets_manager("my-github-token")
                ),
                build_spec=codebuild.BuildSpec.from_object_to_yaml({ # Alternatively add a `amplify.yml` to the repo
                    "version": "1.0",
                    "frontend": {
                        "phases": {
                            "pre_build": {
                                "commands": ["yarn"
                                ]
                            },
                            "build": {
                                "commands": ["yarn build"
                                ]
                            }
                        },
                        "artifacts": {
                            "base_directory": "public",
                            "files": -"**/*"
                        }
                    }})
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "oauth_token": oauth_token,
            "owner": owner,
            "repository": repository,
        }

    @builtins.property
    def oauth_token(self) -> aws_cdk.SecretValue:
        '''(experimental) A personal access token with the ``repo`` scope.

        :stability: experimental
        '''
        result = self._values.get("oauth_token")
        assert result is not None, "Required property 'oauth_token' is missing"
        return typing.cast(aws_cdk.SecretValue, result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''(experimental) The user or organization owning the repository.

        :stability: experimental
        '''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''(experimental) The name of the repository.

        :stability: experimental
        '''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubSourceCodeProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.GitLabSourceCodeProviderProps",
    jsii_struct_bases=[],
    name_mapping={
        "oauth_token": "oauthToken",
        "owner": "owner",
        "repository": "repository",
    },
)
class GitLabSourceCodeProviderProps:
    def __init__(
        self,
        *,
        oauth_token: aws_cdk.SecretValue,
        owner: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''(experimental) Properties for a GitLab source code provider.

        :param oauth_token: (experimental) A personal access token with the ``repo`` scope.
        :param owner: (experimental) The user or organization owning the repository.
        :param repository: (experimental) The name of the repository.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            import aws_cdk as cdk
            
            # secret_value: cdk.SecretValue
            
            git_lab_source_code_provider_props = amplify_alpha.GitLabSourceCodeProviderProps(
                oauth_token=secret_value,
                owner="owner",
                repository="repository"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "oauth_token": oauth_token,
            "owner": owner,
            "repository": repository,
        }

    @builtins.property
    def oauth_token(self) -> aws_cdk.SecretValue:
        '''(experimental) A personal access token with the ``repo`` scope.

        :stability: experimental
        '''
        result = self._values.get("oauth_token")
        assert result is not None, "Required property 'oauth_token' is missing"
        return typing.cast(aws_cdk.SecretValue, result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''(experimental) The user or organization owning the repository.

        :stability: experimental
        '''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> builtins.str:
        '''(experimental) The name of the repository.

        :stability: experimental
        '''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitLabSourceCodeProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-amplify-alpha.IApp")
class IApp(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) An Amplify Console application.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        '''(experimental) The application id.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IAppProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) An Amplify Console application.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-amplify-alpha.IApp"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        '''(experimental) The application id.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "appId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApp).__jsii_proxy_class__ = lambda : _IAppProxy


@jsii.interface(jsii_type="@aws-cdk/aws-amplify-alpha.IBranch")
class IBranch(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) A branch.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchName")
    def branch_name(self) -> builtins.str:
        '''(experimental) The name of the branch.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IBranchProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) A branch.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-amplify-alpha.IBranch"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchName")
    def branch_name(self) -> builtins.str:
        '''(experimental) The name of the branch.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "branchName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBranch).__jsii_proxy_class__ = lambda : _IBranchProxy


@jsii.interface(jsii_type="@aws-cdk/aws-amplify-alpha.ISourceCodeProvider")
class ISourceCodeProvider(typing_extensions.Protocol):
    '''(experimental) A source code provider.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(self, app: "App") -> "SourceCodeProviderConfig":
        '''(experimental) Binds the source code provider to an app.

        :param app: The app [disable-awslint:ref-via-interface].

        :stability: experimental
        '''
        ...


class _ISourceCodeProviderProxy:
    '''(experimental) A source code provider.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-amplify-alpha.ISourceCodeProvider"

    @jsii.member(jsii_name="bind")
    def bind(self, app: "App") -> "SourceCodeProviderConfig":
        '''(experimental) Binds the source code provider to an app.

        :param app: The app [disable-awslint:ref-via-interface].

        :stability: experimental
        '''
        return typing.cast("SourceCodeProviderConfig", jsii.invoke(self, "bind", [app]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISourceCodeProvider).__jsii_proxy_class__ = lambda : _ISourceCodeProviderProxy


@jsii.enum(jsii_type="@aws-cdk/aws-amplify-alpha.RedirectStatus")
class RedirectStatus(enum.Enum):
    '''(experimental) The status code for a URL rewrite or redirect rule.

    :stability: experimental
    '''

    REWRITE = "REWRITE"
    '''(experimental) Rewrite (200).

    :stability: experimental
    '''
    PERMANENT_REDIRECT = "PERMANENT_REDIRECT"
    '''(experimental) Permanent redirect (301).

    :stability: experimental
    '''
    TEMPORARY_REDIRECT = "TEMPORARY_REDIRECT"
    '''(experimental) Temporary redirect (302).

    :stability: experimental
    '''
    NOT_FOUND = "NOT_FOUND"
    '''(experimental) Not found (404).

    :stability: experimental
    '''
    NOT_FOUND_REWRITE = "NOT_FOUND_REWRITE"
    '''(experimental) Not found rewrite (404).

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.SourceCodeProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "repository": "repository",
        "access_token": "accessToken",
        "oauth_token": "oauthToken",
    },
)
class SourceCodeProviderConfig:
    def __init__(
        self,
        *,
        repository: builtins.str,
        access_token: typing.Optional[aws_cdk.SecretValue] = None,
        oauth_token: typing.Optional[aws_cdk.SecretValue] = None,
    ) -> None:
        '''(experimental) Configuration for the source code provider.

        :param repository: (experimental) The repository for the application. Must use the ``HTTPS`` protocol.
        :param access_token: (experimental) Personal Access token for 3rd party source control system for an Amplify App, used to create webhook and read-only deploy key. Token is not stored. Either ``accessToken`` or ``oauthToken`` must be specified if ``repository`` is sepcified. Default: - do not use a token
        :param oauth_token: (experimental) OAuth token for 3rd party source control system for an Amplify App, used to create webhook and read-only deploy key. OAuth token is not stored. Either ``accessToken`` or ``oauthToken`` must be specified if ``repository`` is sepcified. Default: - do not use a token

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            import aws_cdk as cdk
            
            # secret_value: cdk.SecretValue
            
            source_code_provider_config = amplify_alpha.SourceCodeProviderConfig(
                repository="repository",
            
                # the properties below are optional
                access_token=secret_value,
                oauth_token=secret_value
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "repository": repository,
        }
        if access_token is not None:
            self._values["access_token"] = access_token
        if oauth_token is not None:
            self._values["oauth_token"] = oauth_token

    @builtins.property
    def repository(self) -> builtins.str:
        '''(experimental) The repository for the application.

        Must use the ``HTTPS`` protocol.

        :stability: experimental

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            https:
        '''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_token(self) -> typing.Optional[aws_cdk.SecretValue]:
        '''(experimental) Personal Access token for 3rd party source control system for an Amplify App, used to create webhook and read-only deploy key.

        Token is not stored.

        Either ``accessToken`` or ``oauthToken`` must be specified if ``repository``
        is sepcified.

        :default: - do not use a token

        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[aws_cdk.SecretValue], result)

    @builtins.property
    def oauth_token(self) -> typing.Optional[aws_cdk.SecretValue]:
        '''(experimental) OAuth token for 3rd party source control system for an Amplify App, used to create webhook and read-only deploy key.

        OAuth token is not stored.

        Either ``accessToken`` or ``oauthToken`` must be specified if ``repository``
        is sepcified.

        :default: - do not use a token

        :stability: experimental
        '''
        result = self._values.get("oauth_token")
        return typing.cast(typing.Optional[aws_cdk.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SourceCodeProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-amplify-alpha.SubDomain",
    jsii_struct_bases=[],
    name_mapping={"branch": "branch", "prefix": "prefix"},
)
class SubDomain:
    def __init__(
        self,
        *,
        branch: IBranch,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Sub domain settings.

        :param branch: (experimental) The branch.
        :param prefix: (experimental) The prefix. Use '' to map to the root of the domain Default: - the branch name

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_amplify_alpha as amplify_alpha
            
            # branch: amplify_alpha.Branch
            
            sub_domain = amplify_alpha.SubDomain(
                branch=branch,
            
                # the properties below are optional
                prefix="prefix"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "branch": branch,
        }
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def branch(self) -> IBranch:
        '''(experimental) The branch.

        :stability: experimental
        '''
        result = self._values.get("branch")
        assert result is not None, "Required property 'branch' is missing"
        return typing.cast(IBranch, result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The prefix.

        Use '' to map to the root of the domain

        :default: - the branch name

        :stability: experimental
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SubDomain(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IApp, aws_cdk.aws_iam.IGrantable)
class App(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-amplify-alpha.App",
):
    '''(experimental) An Amplify Console application.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import aws_cdk.aws_codebuild as codebuild
        import aws_cdk.aws_amplify_alpha as amplify
        import aws_cdk as cdk
        
        amplify_app = amplify.App(self, "MyApp",
            source_code_provider=amplify.GitHubSourceCodeProvider(
                owner="<user>",
                repository="<repo>",
                oauth_token=cdk.SecretValue.secrets_manager("my-github-token")
            ),
            build_spec=codebuild.BuildSpec.from_object_to_yaml({ # Alternatively add a `amplify.yml` to the repo
                "version": "1.0",
                "frontend": {
                    "phases": {
                        "pre_build": {
                            "commands": ["yarn"
                            ]
                        },
                        "build": {
                            "commands": ["yarn build"
                            ]
                        }
                    },
                    "artifacts": {
                        "base_directory": "public",
                        "files": -"**/*"
                    }
                }})
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_name: typing.Optional[builtins.str] = None,
        auto_branch_creation: typing.Optional[AutoBranchCreation] = None,
        auto_branch_deletion: typing.Optional[builtins.bool] = None,
        basic_auth: typing.Optional[BasicAuth] = None,
        build_spec: typing.Optional[aws_cdk.aws_codebuild.BuildSpec] = None,
        custom_response_headers: typing.Optional[typing.Sequence[CustomResponseHeader]] = None,
        custom_rules: typing.Optional[typing.Sequence[CustomRule]] = None,
        description: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        source_code_provider: typing.Optional[ISourceCodeProvider] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_name: (experimental) The name for the application. Default: - a CDK generated name
        :param auto_branch_creation: (experimental) The auto branch creation configuration. Use this to automatically create branches that match a certain pattern. Default: - no auto branch creation
        :param auto_branch_deletion: (experimental) Automatically disconnect a branch in the Amplify Console when you delete a branch from your Git repository. Default: false
        :param basic_auth: (experimental) The Basic Auth configuration. Use this to set password protection at an app level to all your branches. Default: - no password protection
        :param build_spec: (experimental) BuildSpec for the application. Alternatively, add a ``amplify.yml`` file to the repository. Default: - no build spec
        :param custom_response_headers: (experimental) The custom HTTP response headers for an Amplify app. Default: - no custom response headers
        :param custom_rules: (experimental) Custom rewrite/redirect rules for the application. Default: - no custom rewrite/redirect rules
        :param description: (experimental) A description for the application. Default: - no description
        :param environment_variables: (experimental) Environment variables for the application. All environment variables that you add are encrypted to prevent rogue access so you can use them to store secret information. Default: - no environment variables
        :param role: (experimental) The IAM service role to associate with the application. The App implements IGrantable. Default: - a new role is created
        :param source_code_provider: (experimental) The source code provider for this application. Default: - not connected to a source code provider

        :stability: experimental
        '''
        props = AppProps(
            app_name=app_name,
            auto_branch_creation=auto_branch_creation,
            auto_branch_deletion=auto_branch_deletion,
            basic_auth=basic_auth,
            build_spec=build_spec,
            custom_response_headers=custom_response_headers,
            custom_rules=custom_rules,
            description=description,
            environment_variables=environment_variables,
            role=role,
            source_code_provider=source_code_provider,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAppId") # type: ignore[misc]
    @builtins.classmethod
    def from_app_id(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        app_id: builtins.str,
    ) -> IApp:
        '''(experimental) Import an existing application.

        :param scope: -
        :param id: -
        :param app_id: -

        :stability: experimental
        '''
        return typing.cast(IApp, jsii.sinvoke(cls, "fromAppId", [scope, id, app_id]))

    @jsii.member(jsii_name="addAutoBranchEnvironment")
    def add_auto_branch_environment(
        self,
        name: builtins.str,
        value: builtins.str,
    ) -> "App":
        '''(experimental) Adds an environment variable to the auto created branch.

        All environment variables that you add are encrypted to prevent rogue
        access so you can use them to store secret information.

        :param name: -
        :param value: -

        :stability: experimental
        '''
        return typing.cast("App", jsii.invoke(self, "addAutoBranchEnvironment", [name, value]))

    @jsii.member(jsii_name="addBranch")
    def add_branch(
        self,
        id: builtins.str,
        *,
        asset: typing.Optional[aws_cdk.aws_s3_assets.Asset] = None,
        auto_build: typing.Optional[builtins.bool] = None,
        basic_auth: typing.Optional[BasicAuth] = None,
        branch_name: typing.Optional[builtins.str] = None,
        build_spec: typing.Optional[aws_cdk.aws_codebuild.BuildSpec] = None,
        description: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        pull_request_preview: typing.Optional[builtins.bool] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> "Branch":
        '''(experimental) Adds a branch to this application.

        :param id: -
        :param asset: (experimental) Asset for deployment. The Amplify app must not have a sourceCodeProvider configured as this resource uses Amplify's startDeployment API to initiate and deploy a S3 asset onto the App. Default: - no asset
        :param auto_build: (experimental) Whether to enable auto building for the branch. Default: true
        :param basic_auth: (experimental) The Basic Auth configuration. Use this to set password protection for the branch Default: - no password protection
        :param branch_name: (experimental) The name of the branch. Default: - the construct's id
        :param build_spec: (experimental) BuildSpec for the branch. Default: - no build spec
        :param description: (experimental) A description for the branch. Default: - no description
        :param environment_variables: (experimental) Environment variables for the branch. All environment variables that you add are encrypted to prevent rogue access so you can use them to store secret information. Default: - application environment variables
        :param pull_request_environment_name: (experimental) The dedicated backend environment for the pull request previews. Default: - automatically provision a temporary backend
        :param pull_request_preview: (experimental) Whether to enable pull request preview for the branch. Default: true
        :param stage: (experimental) Stage for the branch. Default: - no stage

        :stability: experimental
        '''
        options = BranchOptions(
            asset=asset,
            auto_build=auto_build,
            basic_auth=basic_auth,
            branch_name=branch_name,
            build_spec=build_spec,
            description=description,
            environment_variables=environment_variables,
            pull_request_environment_name=pull_request_environment_name,
            pull_request_preview=pull_request_preview,
            stage=stage,
        )

        return typing.cast("Branch", jsii.invoke(self, "addBranch", [id, options]))

    @jsii.member(jsii_name="addCustomRule")
    def add_custom_rule(self, rule: CustomRule) -> "App":
        '''(experimental) Adds a custom rewrite/redirect rule to this application.

        :param rule: -

        :stability: experimental
        '''
        return typing.cast("App", jsii.invoke(self, "addCustomRule", [rule]))

    @jsii.member(jsii_name="addDomain")
    def add_domain(
        self,
        id: builtins.str,
        *,
        auto_subdomain_creation_patterns: typing.Optional[typing.Sequence[builtins.str]] = None,
        domain_name: typing.Optional[builtins.str] = None,
        enable_auto_subdomain: typing.Optional[builtins.bool] = None,
        sub_domains: typing.Optional[typing.Sequence[SubDomain]] = None,
    ) -> Domain:
        '''(experimental) Adds a domain to this application.

        :param id: -
        :param auto_subdomain_creation_patterns: (experimental) Branches which should automatically create subdomains. Default: - all repository branches ['*', 'pr*']
        :param domain_name: (experimental) The name of the domain. Default: - the construct's id
        :param enable_auto_subdomain: (experimental) Automatically create subdomains for connected branches. Default: false
        :param sub_domains: (experimental) Subdomains. Default: - use ``addSubDomain()`` to add subdomains

        :stability: experimental
        '''
        options = DomainOptions(
            auto_subdomain_creation_patterns=auto_subdomain_creation_patterns,
            domain_name=domain_name,
            enable_auto_subdomain=enable_auto_subdomain,
            sub_domains=sub_domains,
        )

        return typing.cast(Domain, jsii.invoke(self, "addDomain", [id, options]))

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(self, name: builtins.str, value: builtins.str) -> "App":
        '''(experimental) Adds an environment variable to this application.

        All environment variables that you add are encrypted to prevent rogue
        access so you can use them to store secret information.

        :param name: -
        :param value: -

        :stability: experimental
        '''
        return typing.cast("App", jsii.invoke(self, "addEnvironment", [name, value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        '''(experimental) The application id.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appName")
    def app_name(self) -> builtins.str:
        '''(experimental) The name of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "appName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) The ARN of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultDomain")
    def default_domain(self) -> builtins.str:
        '''(experimental) The default domain of the application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "defaultDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))


@jsii.implements(IBranch)
class Branch(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-amplify-alpha.Branch",
):
    '''(experimental) An Amplify Console branch.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_amplify_alpha as amplify_alpha
        from aws_cdk import aws_codebuild as codebuild
        from aws_cdk import aws_s3_assets as s3_assets
        
        # app: amplify_alpha.App
        # asset: s3_assets.Asset
        # basic_auth: amplify_alpha.BasicAuth
        # build_spec: codebuild.BuildSpec
        
        branch = amplify_alpha.Branch(self, "MyBranch",
            app=app,
        
            # the properties below are optional
            asset=asset,
            auto_build=False,
            basic_auth=basic_auth,
            branch_name="branchName",
            build_spec=build_spec,
            description="description",
            environment_variables={
                "environment_variables_key": "environmentVariables"
            },
            pull_request_environment_name="pullRequestEnvironmentName",
            pull_request_preview=False,
            stage="stage"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app: IApp,
        asset: typing.Optional[aws_cdk.aws_s3_assets.Asset] = None,
        auto_build: typing.Optional[builtins.bool] = None,
        basic_auth: typing.Optional[BasicAuth] = None,
        branch_name: typing.Optional[builtins.str] = None,
        build_spec: typing.Optional[aws_cdk.aws_codebuild.BuildSpec] = None,
        description: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        pull_request_environment_name: typing.Optional[builtins.str] = None,
        pull_request_preview: typing.Optional[builtins.bool] = None,
        stage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app: (experimental) The application within which the branch must be created.
        :param asset: (experimental) Asset for deployment. The Amplify app must not have a sourceCodeProvider configured as this resource uses Amplify's startDeployment API to initiate and deploy a S3 asset onto the App. Default: - no asset
        :param auto_build: (experimental) Whether to enable auto building for the branch. Default: true
        :param basic_auth: (experimental) The Basic Auth configuration. Use this to set password protection for the branch Default: - no password protection
        :param branch_name: (experimental) The name of the branch. Default: - the construct's id
        :param build_spec: (experimental) BuildSpec for the branch. Default: - no build spec
        :param description: (experimental) A description for the branch. Default: - no description
        :param environment_variables: (experimental) Environment variables for the branch. All environment variables that you add are encrypted to prevent rogue access so you can use them to store secret information. Default: - application environment variables
        :param pull_request_environment_name: (experimental) The dedicated backend environment for the pull request previews. Default: - automatically provision a temporary backend
        :param pull_request_preview: (experimental) Whether to enable pull request preview for the branch. Default: true
        :param stage: (experimental) Stage for the branch. Default: - no stage

        :stability: experimental
        '''
        props = BranchProps(
            app=app,
            asset=asset,
            auto_build=auto_build,
            basic_auth=basic_auth,
            branch_name=branch_name,
            build_spec=build_spec,
            description=description,
            environment_variables=environment_variables,
            pull_request_environment_name=pull_request_environment_name,
            pull_request_preview=pull_request_preview,
            stage=stage,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromBranchName") # type: ignore[misc]
    @builtins.classmethod
    def from_branch_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        branch_name: builtins.str,
    ) -> IBranch:
        '''(experimental) Import an existing branch.

        :param scope: -
        :param id: -
        :param branch_name: -

        :stability: experimental
        '''
        return typing.cast(IBranch, jsii.sinvoke(cls, "fromBranchName", [scope, id, branch_name]))

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(self, name: builtins.str, value: builtins.str) -> "Branch":
        '''(experimental) Adds an environment variable to this branch.

        All environment variables that you add are encrypted to prevent rogue
        access so you can use them to store secret information.

        :param name: -
        :param value: -

        :stability: experimental
        '''
        return typing.cast("Branch", jsii.invoke(self, "addEnvironment", [name, value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) The ARN of the branch.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="branchName")
    def branch_name(self) -> builtins.str:
        '''(experimental) The name of the branch.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "branchName"))


@jsii.implements(ISourceCodeProvider)
class CodeCommitSourceCodeProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-amplify-alpha.CodeCommitSourceCodeProvider",
):
    '''(experimental) CodeCommit source code provider.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_amplify_alpha as amplify_alpha
        from aws_cdk import aws_codecommit as codecommit
        
        # repository: codecommit.Repository
        
        code_commit_source_code_provider = amplify_alpha.CodeCommitSourceCodeProvider(
            repository=repository
        )
    '''

    def __init__(self, *, repository: aws_cdk.aws_codecommit.IRepository) -> None:
        '''
        :param repository: (experimental) The CodeCommit repository.

        :stability: experimental
        '''
        props = CodeCommitSourceCodeProviderProps(repository=repository)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(self, app: App) -> SourceCodeProviderConfig:
        '''(experimental) Binds the source code provider to an app.

        :param app: -

        :stability: experimental
        '''
        return typing.cast(SourceCodeProviderConfig, jsii.invoke(self, "bind", [app]))


@jsii.implements(ISourceCodeProvider)
class GitHubSourceCodeProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-amplify-alpha.GitHubSourceCodeProvider",
):
    '''(experimental) GitHub source code provider.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import aws_cdk.aws_codebuild as codebuild
        import aws_cdk.aws_amplify_alpha as amplify
        import aws_cdk as cdk
        
        amplify_app = amplify.App(self, "MyApp",
            source_code_provider=amplify.GitHubSourceCodeProvider(
                owner="<user>",
                repository="<repo>",
                oauth_token=cdk.SecretValue.secrets_manager("my-github-token")
            ),
            build_spec=codebuild.BuildSpec.from_object_to_yaml({ # Alternatively add a `amplify.yml` to the repo
                "version": "1.0",
                "frontend": {
                    "phases": {
                        "pre_build": {
                            "commands": ["yarn"
                            ]
                        },
                        "build": {
                            "commands": ["yarn build"
                            ]
                        }
                    },
                    "artifacts": {
                        "base_directory": "public",
                        "files": -"**/*"
                    }
                }})
        )
    '''

    def __init__(
        self,
        *,
        oauth_token: aws_cdk.SecretValue,
        owner: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param oauth_token: (experimental) A personal access token with the ``repo`` scope.
        :param owner: (experimental) The user or organization owning the repository.
        :param repository: (experimental) The name of the repository.

        :stability: experimental
        '''
        props = GitHubSourceCodeProviderProps(
            oauth_token=oauth_token, owner=owner, repository=repository
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(self, _app: App) -> SourceCodeProviderConfig:
        '''(experimental) Binds the source code provider to an app.

        :param _app: -

        :stability: experimental
        '''
        return typing.cast(SourceCodeProviderConfig, jsii.invoke(self, "bind", [_app]))


@jsii.implements(ISourceCodeProvider)
class GitLabSourceCodeProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-amplify-alpha.GitLabSourceCodeProvider",
):
    '''(experimental) GitLab source code provider.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_amplify_alpha as amplify_alpha
        import aws_cdk as cdk
        
        # secret_value: cdk.SecretValue
        
        git_lab_source_code_provider = amplify_alpha.GitLabSourceCodeProvider(
            oauth_token=secret_value,
            owner="owner",
            repository="repository"
        )
    '''

    def __init__(
        self,
        *,
        oauth_token: aws_cdk.SecretValue,
        owner: builtins.str,
        repository: builtins.str,
    ) -> None:
        '''
        :param oauth_token: (experimental) A personal access token with the ``repo`` scope.
        :param owner: (experimental) The user or organization owning the repository.
        :param repository: (experimental) The name of the repository.

        :stability: experimental
        '''
        props = GitLabSourceCodeProviderProps(
            oauth_token=oauth_token, owner=owner, repository=repository
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(self, _app: App) -> SourceCodeProviderConfig:
        '''(experimental) Binds the source code provider to an app.

        :param _app: -

        :stability: experimental
        '''
        return typing.cast(SourceCodeProviderConfig, jsii.invoke(self, "bind", [_app]))


__all__ = [
    "App",
    "AppProps",
    "AutoBranchCreation",
    "BasicAuth",
    "BasicAuthConfig",
    "BasicAuthProps",
    "Branch",
    "BranchOptions",
    "BranchProps",
    "CodeCommitSourceCodeProvider",
    "CodeCommitSourceCodeProviderProps",
    "CustomResponseHeader",
    "CustomRule",
    "CustomRuleOptions",
    "Domain",
    "DomainOptions",
    "DomainProps",
    "GitHubSourceCodeProvider",
    "GitHubSourceCodeProviderProps",
    "GitLabSourceCodeProvider",
    "GitLabSourceCodeProviderProps",
    "IApp",
    "IBranch",
    "ISourceCodeProvider",
    "RedirectStatus",
    "SourceCodeProviderConfig",
    "SubDomain",
]

publication.publish()
