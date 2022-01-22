'''
# CDK Pipelines for GitHub Workflows

![Experimental](https://img.shields.io/badge/experimental-important.svg?style=for-the-badge)

NOTICE: this library is still not published to package managers. Stay tuned.

Deploy CDK applications through GitHub workflows.

## Usage

Assuming you have a
[`Stage`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.Stage.html)
called `MyStage` that includes CDK stacks for your app and you want to deploy it
to two AWS environments (`BETA_ENV` and `PROD_ENV`):

```python
import { ShellStep } from 'aws-cdk-lib/pipelines';
import { GithubWorkflow } from 'cdk-pipelines-github';

const app = new App();

const pipeline = new GithubWorkflow(app, 'Pipeline', {
  synth: new ShellStep('Build', {
    commands: [
      'yarn install',
      'yarn build',
    ],
  }),
  workflowPath: '.github/workflows/deploy.yml',
});

pipeline.addStage(new MyStage(this, 'Beta', { env: BETA_ENV }));
pipeline.addStage(new MyStage(this, 'Prod', { env: PROD_ENV }));

app.synth();
```

When you run `cdk synth`, a `deploy.yml` workflow will be created under
`.github/workflows` in your repo. This workflow will deploy your application
based on the definition of the pipeline. In this case, it will the two stages in
sequence, and within each stage, it will deploy all the stacks according to
their dependency order and maximum parallelism. If you app uses assets, assets
will be published to the relevant destination environment.

The `Pipeline` class from `cdk-pipelines-github` is derived from the base CDK
Pipelines class, so most features should be supported out of the box. See the
[CDK Pipelines](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.pipelines-readme.html)
documentation for more details.

**NOTES:**

* Environments must be bootstrapped separately using `cdk bootstrap`. See [CDK
  Environment
  Bootstrapping](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.pipelines-readme.html#cdk-environment-bootstrapping)
  for details.
* The workflow expects the GitHub repository to include secrets with AWS
  credentials (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`).

## Example

You can find an example usage in [test/example-app.ts](./test/example-app.ts)
which includes a simple CDK app and a pipeline.

You can find a repository that uses this example here: [eladb/test-app-cdkpipeline](https://github.com/eladb/test-app-cdkpipeline).

To run the example, clone this repository and install dependencies:

```shell
cd ~/projects # or some other playground space
git clone https://github.com/cdklabs/cdk-pipelines-github
cd cdk-pipelines-github
yarn
```

Now, create a new GitHub repository and clone it as well:

```shell
cd ~/projects
git clone https://github.com/myaccount/my-test-repository
```

You'll need to set up AWS credentials in your environment:

```shell
export AWS_ACCESS_KEY_ID=xxxx
export AWS_SECRET_ACCESS_KEY=xxxxx
```

Bootstrap your environments:

```shell
export CDK_NEW_BOOTSTRAP=1
npx cdk bootstrap aws://ACCOUNTID/us-east-1
npx cdk bootstrap aws://ACCOUNTID/eu-west-2
```

Now, run the `manual-test.sh` script when your working directory is the new repository:

```shell
cd ~/projects/my-test-repository
~/projects/cdk-piplines/github/test/manual-test.sh
```

This will produce a `cdk.out` directory and a `.github/workflows/deploy.yml` file.

Commit and push these files to your repo and you should see the deployment
workflow in action. Make sure your GitHub repository has `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` secrets that can access the same account that you
synthesized against.

## Not supported yet

This is work in progress. The following features are still not supported:

* [ ] Credentials and roles (document permissions required, etc)
* [ ] Support Docker image assets
* [ ] Anti-tamper check for CI runs (`synth` should fail if `CI=1` and the workflow has changed)
* [ ] Revise Documentation

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md) for more information.

## License

This project is licensed under the Apache-2.0 License.
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

import aws_cdk.pipelines
import constructs


@jsii.data_type(
    jsii_type="cdk-pipelines-github.AwsCredentialsSecrets",
    jsii_struct_bases=[],
    name_mapping={
        "access_key_id": "accessKeyId",
        "secret_access_key": "secretAccessKey",
        "session_token": "sessionToken",
    },
)
class AwsCredentialsSecrets:
    def __init__(
        self,
        *,
        access_key_id: typing.Optional[builtins.str] = None,
        secret_access_key: typing.Optional[builtins.str] = None,
        session_token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Names of secrets for AWS credentials.

        :param access_key_id: Default: "AWS_ACCESS_KEY_ID"
        :param secret_access_key: Default: "AWS_SECRET_ACCESS_KEY"
        :param session_token: Default: - no session token is used
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if access_key_id is not None:
            self._values["access_key_id"] = access_key_id
        if secret_access_key is not None:
            self._values["secret_access_key"] = secret_access_key
        if session_token is not None:
            self._values["session_token"] = session_token

    @builtins.property
    def access_key_id(self) -> typing.Optional[builtins.str]:
        '''
        :default: "AWS_ACCESS_KEY_ID"
        '''
        result = self._values.get("access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_access_key(self) -> typing.Optional[builtins.str]:
        '''
        :default: "AWS_SECRET_ACCESS_KEY"
        '''
        result = self._values.get("secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_token(self) -> typing.Optional[builtins.str]:
        '''
        :default: - no session token is used
        '''
        result = self._values.get("session_token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsCredentialsSecrets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.CheckRunOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class CheckRunOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Check run options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CheckRunOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.CheckSuiteOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class CheckSuiteOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Check suite options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CheckSuiteOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.ContainerCredentials",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class ContainerCredentials:
    def __init__(self, *, password: builtins.str, username: builtins.str) -> None:
        '''Credentials to use to authenticate to Docker registries.

        :param password: The password.
        :param username: The username.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> builtins.str:
        '''The password.'''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''The username.'''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerCredentials(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.ContainerOptions",
    jsii_struct_bases=[],
    name_mapping={
        "image": "image",
        "credentials": "credentials",
        "env": "env",
        "options": "options",
        "ports": "ports",
        "volumes": "volumes",
    },
)
class ContainerOptions:
    def __init__(
        self,
        *,
        image: builtins.str,
        credentials: typing.Optional[ContainerCredentials] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        options: typing.Optional[typing.Sequence[builtins.str]] = None,
        ports: typing.Optional[typing.Sequence[jsii.Number]] = None,
        volumes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Options petaining to container environments.

        :param image: The Docker image to use as the container to run the action. The value can be the Docker Hub image name or a registry name.
        :param credentials: f the image's container registry requires authentication to pull the image, you can use credentials to set a map of the username and password. The credentials are the same values that you would provide to the docker login command.
        :param env: Sets a map of environment variables in the container.
        :param options: Additional Docker container resource options.
        :param ports: Sets an array of ports to expose on the container.
        :param volumes: Sets an array of volumes for the container to use. You can use volumes to share data between services or other steps in a job. You can specify named Docker volumes, anonymous Docker volumes, or bind mounts on the host. To specify a volume, you specify the source and destination path: ``<source>:<destinationPath>``.
        '''
        if isinstance(credentials, dict):
            credentials = ContainerCredentials(**credentials)
        self._values: typing.Dict[str, typing.Any] = {
            "image": image,
        }
        if credentials is not None:
            self._values["credentials"] = credentials
        if env is not None:
            self._values["env"] = env
        if options is not None:
            self._values["options"] = options
        if ports is not None:
            self._values["ports"] = ports
        if volumes is not None:
            self._values["volumes"] = volumes

    @builtins.property
    def image(self) -> builtins.str:
        '''The Docker image to use as the container to run the action.

        The value can
        be the Docker Hub image name or a registry name.
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def credentials(self) -> typing.Optional[ContainerCredentials]:
        '''f the image's container registry requires authentication to pull the image, you can use credentials to set a map of the username and password.

        The credentials are the same values that you would provide to the docker
        login command.
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[ContainerCredentials], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Sets a map of environment variables in the container.'''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional Docker container resource options.

        :see: https://docs.docker.com/engine/reference/commandline/create/#options
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Sets an array of ports to expose on the container.'''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Sets an array of volumes for the container to use.

        You can use volumes to
        share data between services or other steps in a job. You can specify
        named Docker volumes, anonymous Docker volumes, or bind mounts on the
        host.

        To specify a volume, you specify the source and destination path:
        ``<source>:<destinationPath>``.
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.CreateOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class CreateOptions:
    def __init__(self) -> None:
        '''The Create event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.CronScheduleOptions",
    jsii_struct_bases=[],
    name_mapping={"cron": "cron"},
)
class CronScheduleOptions:
    def __init__(self, *, cron: builtins.str) -> None:
        '''CRON schedule options.

        :param cron: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cron": cron,
        }

    @builtins.property
    def cron(self) -> builtins.str:
        '''
        :see: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html#tag_20_25_07
        '''
        result = self._values.get("cron")
        assert result is not None, "Required property 'cron' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CronScheduleOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.DeleteOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DeleteOptions:
    def __init__(self) -> None:
        '''The Delete event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeleteOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.DeploymentOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DeploymentOptions:
    def __init__(self) -> None:
        '''The Deployment event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeploymentOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.DeploymentStatusOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DeploymentStatusOptions:
    def __init__(self) -> None:
        '''The Deployment status event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeploymentStatusOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.ForkOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class ForkOptions:
    def __init__(self) -> None:
        '''The Fork event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ForkOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GitHubWorkflow(
    aws_cdk.pipelines.PipelineBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-pipelines-github.GitHubWorkflow",
):
    '''CDK Pipelines for GitHub workflows.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        aws_credentials: typing.Optional[AwsCredentialsSecrets] = None,
        build_container: typing.Optional[ContainerOptions] = None,
        cdk_cli_version: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence["JobStep"]] = None,
        pre_build_steps: typing.Optional[typing.Sequence["JobStep"]] = None,
        pre_synthed: typing.Optional[builtins.bool] = None,
        workflow_name: typing.Optional[builtins.str] = None,
        workflow_path: typing.Optional[builtins.str] = None,
        workflow_triggers: typing.Optional["Triggers"] = None,
        synth: aws_cdk.pipelines.IFileSetProducer,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param aws_credentials: Names of GitHub repository secrets that include AWS credentials for deployment. Default: - ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``.
        :param build_container: Build container options. Default: - GitHub defaults
        :param cdk_cli_version: Version of the CDK CLI to use. Default: - automatic
        :param post_build_steps: GitHub workflow steps to execute after build. Default: []
        :param pre_build_steps: GitHub workflow steps to execute before build. Default: []
        :param pre_synthed: Indicates if the repository already contains a synthesized ``cdk.out`` directory, in which case we will simply checkout the repo in jobs that require ``cdk.out``. Default: false
        :param workflow_name: Name of the workflow. Default: "deploy"
        :param workflow_path: File path for the GitHub workflow. Default: ".github/workflows/deploy.yml"
        :param workflow_triggers: GitHub workflow triggers. Default: - By default, workflow is triggered on push to the ``main`` branch and can also be triggered manually (``workflow_dispatch``).
        :param synth: The build step that produces the CDK Cloud Assembly. The primary output of this step needs to be the ``cdk.out`` directory generated by the ``cdk synth`` command. If you use a ``ShellStep`` here and you don't configure an output directory, the output directory will automatically be assumed to be ``cdk.out``.
        '''
        props = GitHubWorkflowProps(
            aws_credentials=aws_credentials,
            build_container=build_container,
            cdk_cli_version=cdk_cli_version,
            post_build_steps=post_build_steps,
            pre_build_steps=pre_build_steps,
            pre_synthed=pre_synthed,
            workflow_name=workflow_name,
            workflow_path=workflow_path,
            workflow_triggers=workflow_triggers,
            synth=synth,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="doBuildPipeline")
    def _do_build_pipeline(self) -> None:
        '''Implemented by subclasses to do the actual pipeline construction.'''
        return typing.cast(None, jsii.invoke(self, "doBuildPipeline", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowName")
    def workflow_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workflowName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workflowPath")
    def workflow_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workflowPath"))


@jsii.data_type(
    jsii_type="cdk-pipelines-github.GitHubWorkflowProps",
    jsii_struct_bases=[aws_cdk.pipelines.PipelineBaseProps],
    name_mapping={
        "synth": "synth",
        "aws_credentials": "awsCredentials",
        "build_container": "buildContainer",
        "cdk_cli_version": "cdkCliVersion",
        "post_build_steps": "postBuildSteps",
        "pre_build_steps": "preBuildSteps",
        "pre_synthed": "preSynthed",
        "workflow_name": "workflowName",
        "workflow_path": "workflowPath",
        "workflow_triggers": "workflowTriggers",
    },
)
class GitHubWorkflowProps(aws_cdk.pipelines.PipelineBaseProps):
    def __init__(
        self,
        *,
        synth: aws_cdk.pipelines.IFileSetProducer,
        aws_credentials: typing.Optional[AwsCredentialsSecrets] = None,
        build_container: typing.Optional[ContainerOptions] = None,
        cdk_cli_version: typing.Optional[builtins.str] = None,
        post_build_steps: typing.Optional[typing.Sequence["JobStep"]] = None,
        pre_build_steps: typing.Optional[typing.Sequence["JobStep"]] = None,
        pre_synthed: typing.Optional[builtins.bool] = None,
        workflow_name: typing.Optional[builtins.str] = None,
        workflow_path: typing.Optional[builtins.str] = None,
        workflow_triggers: typing.Optional["Triggers"] = None,
    ) -> None:
        '''Props for ``GitHubWorkflow``.

        :param synth: The build step that produces the CDK Cloud Assembly. The primary output of this step needs to be the ``cdk.out`` directory generated by the ``cdk synth`` command. If you use a ``ShellStep`` here and you don't configure an output directory, the output directory will automatically be assumed to be ``cdk.out``.
        :param aws_credentials: Names of GitHub repository secrets that include AWS credentials for deployment. Default: - ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``.
        :param build_container: Build container options. Default: - GitHub defaults
        :param cdk_cli_version: Version of the CDK CLI to use. Default: - automatic
        :param post_build_steps: GitHub workflow steps to execute after build. Default: []
        :param pre_build_steps: GitHub workflow steps to execute before build. Default: []
        :param pre_synthed: Indicates if the repository already contains a synthesized ``cdk.out`` directory, in which case we will simply checkout the repo in jobs that require ``cdk.out``. Default: false
        :param workflow_name: Name of the workflow. Default: "deploy"
        :param workflow_path: File path for the GitHub workflow. Default: ".github/workflows/deploy.yml"
        :param workflow_triggers: GitHub workflow triggers. Default: - By default, workflow is triggered on push to the ``main`` branch and can also be triggered manually (``workflow_dispatch``).
        '''
        if isinstance(aws_credentials, dict):
            aws_credentials = AwsCredentialsSecrets(**aws_credentials)
        if isinstance(build_container, dict):
            build_container = ContainerOptions(**build_container)
        if isinstance(workflow_triggers, dict):
            workflow_triggers = Triggers(**workflow_triggers)
        self._values: typing.Dict[str, typing.Any] = {
            "synth": synth,
        }
        if aws_credentials is not None:
            self._values["aws_credentials"] = aws_credentials
        if build_container is not None:
            self._values["build_container"] = build_container
        if cdk_cli_version is not None:
            self._values["cdk_cli_version"] = cdk_cli_version
        if post_build_steps is not None:
            self._values["post_build_steps"] = post_build_steps
        if pre_build_steps is not None:
            self._values["pre_build_steps"] = pre_build_steps
        if pre_synthed is not None:
            self._values["pre_synthed"] = pre_synthed
        if workflow_name is not None:
            self._values["workflow_name"] = workflow_name
        if workflow_path is not None:
            self._values["workflow_path"] = workflow_path
        if workflow_triggers is not None:
            self._values["workflow_triggers"] = workflow_triggers

    @builtins.property
    def synth(self) -> aws_cdk.pipelines.IFileSetProducer:
        '''The build step that produces the CDK Cloud Assembly.

        The primary output of this step needs to be the ``cdk.out`` directory
        generated by the ``cdk synth`` command.

        If you use a ``ShellStep`` here and you don't configure an output directory,
        the output directory will automatically be assumed to be ``cdk.out``.
        '''
        result = self._values.get("synth")
        assert result is not None, "Required property 'synth' is missing"
        return typing.cast(aws_cdk.pipelines.IFileSetProducer, result)

    @builtins.property
    def aws_credentials(self) -> typing.Optional[AwsCredentialsSecrets]:
        '''Names of GitHub repository secrets that include AWS credentials for deployment.

        :default: - ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``.
        '''
        result = self._values.get("aws_credentials")
        return typing.cast(typing.Optional[AwsCredentialsSecrets], result)

    @builtins.property
    def build_container(self) -> typing.Optional[ContainerOptions]:
        '''Build container options.

        :default: - GitHub defaults
        '''
        result = self._values.get("build_container")
        return typing.cast(typing.Optional[ContainerOptions], result)

    @builtins.property
    def cdk_cli_version(self) -> typing.Optional[builtins.str]:
        '''Version of the CDK CLI to use.

        :default: - automatic
        '''
        result = self._values.get("cdk_cli_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_build_steps(self) -> typing.Optional[typing.List["JobStep"]]:
        '''GitHub workflow steps to execute after build.

        :default: []
        '''
        result = self._values.get("post_build_steps")
        return typing.cast(typing.Optional[typing.List["JobStep"]], result)

    @builtins.property
    def pre_build_steps(self) -> typing.Optional[typing.List["JobStep"]]:
        '''GitHub workflow steps to execute before build.

        :default: []
        '''
        result = self._values.get("pre_build_steps")
        return typing.cast(typing.Optional[typing.List["JobStep"]], result)

    @builtins.property
    def pre_synthed(self) -> typing.Optional[builtins.bool]:
        '''Indicates if the repository already contains a synthesized ``cdk.out`` directory, in which case we will simply checkout the repo in jobs that require ``cdk.out``.

        :default: false
        '''
        result = self._values.get("pre_synthed")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def workflow_name(self) -> typing.Optional[builtins.str]:
        '''Name of the workflow.

        :default: "deploy"
        '''
        result = self._values.get("workflow_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_path(self) -> typing.Optional[builtins.str]:
        '''File path for the GitHub workflow.

        :default: ".github/workflows/deploy.yml"
        '''
        result = self._values.get("workflow_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workflow_triggers(self) -> typing.Optional["Triggers"]:
        '''GitHub workflow triggers.

        :default:

        - By default, workflow is triggered on push to the ``main`` branch
        and can also be triggered manually (``workflow_dispatch``).
        '''
        result = self._values.get("workflow_triggers")
        return typing.cast(typing.Optional["Triggers"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubWorkflowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.GollumOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class GollumOptions:
    def __init__(self) -> None:
        '''The Gollum event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GollumOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.IssueCommentOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class IssueCommentOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Issue comment options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IssueCommentOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.IssuesOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class IssuesOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Issues options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IssuesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.Job",
    jsii_struct_bases=[],
    name_mapping={
        "permissions": "permissions",
        "runs_on": "runsOn",
        "steps": "steps",
        "concurrency": "concurrency",
        "container": "container",
        "continue_on_error": "continueOnError",
        "defaults": "defaults",
        "env": "env",
        "environment": "environment",
        "if_": "if",
        "name": "name",
        "needs": "needs",
        "outputs": "outputs",
        "services": "services",
        "strategy": "strategy",
        "timeout_minutes": "timeoutMinutes",
    },
)
class Job:
    def __init__(
        self,
        *,
        permissions: "JobPermissions",
        runs_on: builtins.str,
        steps: typing.Sequence["JobStep"],
        concurrency: typing.Any = None,
        container: typing.Optional[ContainerOptions] = None,
        continue_on_error: typing.Optional[builtins.bool] = None,
        defaults: typing.Optional["JobDefaults"] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment: typing.Any = None,
        if_: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        needs: typing.Optional[typing.Sequence[builtins.str]] = None,
        outputs: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        services: typing.Optional[typing.Mapping[builtins.str, ContainerOptions]] = None,
        strategy: typing.Optional["JobStrategy"] = None,
        timeout_minutes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''A GitHub Workflow job definition.

        :param permissions: You can modify the default permissions granted to the GITHUB_TOKEN, adding or removing access as required, so that you only allow the minimum required access. Use ``{ contents: READ }`` if your job only needs to clone code. This is intentionally a required field since it is required in order to allow workflows to run in GitHub repositories with restricted default access.
        :param runs_on: The type of machine to run the job on. The machine can be either a GitHub-hosted runner or a self-hosted runner.
        :param steps: A job contains a sequence of tasks called steps. Steps can run commands, run setup tasks, or run an action in your repository, a public repository, or an action published in a Docker registry. Not all steps run actions, but all actions run as a step. Each step runs in its own process in the runner environment and has access to the workspace and filesystem. Because steps run in their own process, changes to environment variables are not preserved between steps. GitHub provides built-in steps to set up and complete a job.
        :param concurrency: (experimental) Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time. A concurrency group can be any string or expression. The expression can use any context except for the secrets context.
        :param container: A container to run any steps in a job that don't already specify a container. If you have steps that use both script and container actions, the container actions will run as sibling containers on the same network with the same volume mounts.
        :param continue_on_error: Prevents a workflow run from failing when a job fails. Set to true to allow a workflow run to pass when this job fails.
        :param defaults: A map of default settings that will apply to all steps in the job. You can also set default settings for the entire workflow.
        :param env: A map of environment variables that are available to all steps in the job. You can also set environment variables for the entire workflow or an individual step.
        :param environment: The environment that the job references. All environment protection rules must pass before a job referencing the environment is sent to a runner.
        :param if_: You can use the if conditional to prevent a job from running unless a condition is met. You can use any supported context and expression to create a conditional.
        :param name: The name of the job displayed on GitHub.
        :param needs: Identifies any jobs that must complete successfully before this job will run. It can be a string or array of strings. If a job fails, all jobs that need it are skipped unless the jobs use a conditional expression that causes the job to continue.
        :param outputs: A map of outputs for a job. Job outputs are available to all downstream jobs that depend on this job.
        :param services: Used to host service containers for a job in a workflow. Service containers are useful for creating databases or cache services like Redis. The runner automatically creates a Docker network and manages the life cycle of the service containers.
        :param strategy: A strategy creates a build matrix for your jobs. You can define different variations to run each job in.
        :param timeout_minutes: The maximum number of minutes to let a job run before GitHub automatically cancels it. Default: 360
        '''
        if isinstance(permissions, dict):
            permissions = JobPermissions(**permissions)
        if isinstance(container, dict):
            container = ContainerOptions(**container)
        if isinstance(defaults, dict):
            defaults = JobDefaults(**defaults)
        if isinstance(strategy, dict):
            strategy = JobStrategy(**strategy)
        self._values: typing.Dict[str, typing.Any] = {
            "permissions": permissions,
            "runs_on": runs_on,
            "steps": steps,
        }
        if concurrency is not None:
            self._values["concurrency"] = concurrency
        if container is not None:
            self._values["container"] = container
        if continue_on_error is not None:
            self._values["continue_on_error"] = continue_on_error
        if defaults is not None:
            self._values["defaults"] = defaults
        if env is not None:
            self._values["env"] = env
        if environment is not None:
            self._values["environment"] = environment
        if if_ is not None:
            self._values["if_"] = if_
        if name is not None:
            self._values["name"] = name
        if needs is not None:
            self._values["needs"] = needs
        if outputs is not None:
            self._values["outputs"] = outputs
        if services is not None:
            self._values["services"] = services
        if strategy is not None:
            self._values["strategy"] = strategy
        if timeout_minutes is not None:
            self._values["timeout_minutes"] = timeout_minutes

    @builtins.property
    def permissions(self) -> "JobPermissions":
        '''You can modify the default permissions granted to the GITHUB_TOKEN, adding or removing access as required, so that you only allow the minimum required access.

        Use ``{ contents: READ }`` if your job only needs to clone code.

        This is intentionally a required field since it is required in order to
        allow workflows to run in GitHub repositories with restricted default
        access.

        :see: https://docs.github.com/en/actions/reference/authentication-in-a-workflow#permissions-for-the-github_token
        '''
        result = self._values.get("permissions")
        assert result is not None, "Required property 'permissions' is missing"
        return typing.cast("JobPermissions", result)

    @builtins.property
    def runs_on(self) -> builtins.str:
        '''The type of machine to run the job on.

        The machine can be either a
        GitHub-hosted runner or a self-hosted runner.

        Example::

            "ubuntu-latest"
        '''
        result = self._values.get("runs_on")
        assert result is not None, "Required property 'runs_on' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def steps(self) -> typing.List["JobStep"]:
        '''A job contains a sequence of tasks called steps.

        Steps can run commands,
        run setup tasks, or run an action in your repository, a public repository,
        or an action published in a Docker registry. Not all steps run actions,
        but all actions run as a step. Each step runs in its own process in the
        runner environment and has access to the workspace and filesystem.
        Because steps run in their own process, changes to environment variables
        are not preserved between steps. GitHub provides built-in steps to set up
        and complete a job.
        '''
        result = self._values.get("steps")
        assert result is not None, "Required property 'steps' is missing"
        return typing.cast(typing.List["JobStep"], result)

    @builtins.property
    def concurrency(self) -> typing.Any:
        '''(experimental) Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time.

        A concurrency group can be any
        string or expression. The expression can use any context except for the
        secrets context.

        :stability: experimental
        '''
        result = self._values.get("concurrency")
        return typing.cast(typing.Any, result)

    @builtins.property
    def container(self) -> typing.Optional[ContainerOptions]:
        '''A container to run any steps in a job that don't already specify a container.

        If you have steps that use both script and container actions,
        the container actions will run as sibling containers on the same network
        with the same volume mounts.
        '''
        result = self._values.get("container")
        return typing.cast(typing.Optional[ContainerOptions], result)

    @builtins.property
    def continue_on_error(self) -> typing.Optional[builtins.bool]:
        '''Prevents a workflow run from failing when a job fails.

        Set to true to
        allow a workflow run to pass when this job fails.
        '''
        result = self._values.get("continue_on_error")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def defaults(self) -> typing.Optional["JobDefaults"]:
        '''A map of default settings that will apply to all steps in the job.

        You
        can also set default settings for the entire workflow.
        '''
        result = self._values.get("defaults")
        return typing.cast(typing.Optional["JobDefaults"], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of environment variables that are available to all steps in the job.

        You can also set environment variables for the entire workflow or an
        individual step.
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def environment(self) -> typing.Any:
        '''The environment that the job references.

        All environment protection rules
        must pass before a job referencing the environment is sent to a runner.

        :see: https://docs.github.com/en/actions/reference/environments
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Any, result)

    @builtins.property
    def if_(self) -> typing.Optional[builtins.str]:
        '''You can use the if conditional to prevent a job from running unless a condition is met.

        You can use any supported context and expression to
        create a conditional.
        '''
        result = self._values.get("if_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the job displayed on GitHub.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def needs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Identifies any jobs that must complete successfully before this job will run.

        It can be a string or array of strings. If a job fails, all jobs
        that need it are skipped unless the jobs use a conditional expression
        that causes the job to continue.
        '''
        result = self._values.get("needs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def outputs(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of outputs for a job.

        Job outputs are available to all downstream
        jobs that depend on this job.
        '''
        result = self._values.get("outputs")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def services(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, ContainerOptions]]:
        '''Used to host service containers for a job in a workflow.

        Service
        containers are useful for creating databases or cache services like Redis.
        The runner automatically creates a Docker network and manages the life
        cycle of the service containers.
        '''
        result = self._values.get("services")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, ContainerOptions]], result)

    @builtins.property
    def strategy(self) -> typing.Optional["JobStrategy"]:
        '''A strategy creates a build matrix for your jobs.

        You can define different
        variations to run each job in.
        '''
        result = self._values.get("strategy")
        return typing.cast(typing.Optional["JobStrategy"], result)

    @builtins.property
    def timeout_minutes(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of minutes to let a job run before GitHub automatically cancels it.

        :default: 360
        '''
        result = self._values.get("timeout_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Job(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.JobDefaults",
    jsii_struct_bases=[],
    name_mapping={"run": "run"},
)
class JobDefaults:
    def __init__(self, *, run: typing.Optional["RunSettings"] = None) -> None:
        '''Default settings for all steps in the job.

        :param run: Default run settings.
        '''
        if isinstance(run, dict):
            run = RunSettings(**run)
        self._values: typing.Dict[str, typing.Any] = {}
        if run is not None:
            self._values["run"] = run

    @builtins.property
    def run(self) -> typing.Optional["RunSettings"]:
        '''Default run settings.'''
        result = self._values.get("run")
        return typing.cast(typing.Optional["RunSettings"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobDefaults(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.JobMatrix",
    jsii_struct_bases=[],
    name_mapping={"domain": "domain", "exclude": "exclude", "include": "include"},
)
class JobMatrix:
    def __init__(
        self,
        *,
        domain: typing.Optional[typing.Mapping[builtins.str, typing.Sequence[builtins.str]]] = None,
        exclude: typing.Optional[typing.Sequence[typing.Mapping[builtins.str, builtins.str]]] = None,
        include: typing.Optional[typing.Sequence[typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''A job matrix.

        :param domain: Each option you define in the matrix has a key and value. The keys you define become properties in the matrix context and you can reference the property in other areas of your workflow file. For example, if you define the key os that contains an array of operating systems, you can use the matrix.os property as the value of the runs-on keyword to create a job for each operating system.
        :param exclude: You can remove a specific configurations defined in the build matrix using the exclude option. Using exclude removes a job defined by the build matrix.
        :param include: You can add additional configuration options to a build matrix job that already exists. For example, if you want to use a specific version of npm when the job that uses windows-latest and version 8 of node runs, you can use include to specify that additional option.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if domain is not None:
            self._values["domain"] = domain
        if exclude is not None:
            self._values["exclude"] = exclude
        if include is not None:
            self._values["include"] = include

    @builtins.property
    def domain(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]]:
        '''Each option you define in the matrix has a key and value.

        The keys you
        define become properties in the matrix context and you can reference the
        property in other areas of your workflow file. For example, if you define
        the key os that contains an array of operating systems, you can use the
        matrix.os property as the value of the runs-on keyword to create a job
        for each operating system.
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List[builtins.str]]], result)

    @builtins.property
    def exclude(
        self,
    ) -> typing.Optional[typing.List[typing.Mapping[builtins.str, builtins.str]]]:
        '''You can remove a specific configurations defined in the build matrix using the exclude option.

        Using exclude removes a job defined by the
        build matrix.
        '''
        result = self._values.get("exclude")
        return typing.cast(typing.Optional[typing.List[typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def include(
        self,
    ) -> typing.Optional[typing.List[typing.Mapping[builtins.str, builtins.str]]]:
        '''You can add additional configuration options to a build matrix job that already exists.

        For example, if you want to use a specific version of npm
        when the job that uses windows-latest and version 8 of node runs, you can
        use include to specify that additional option.
        '''
        result = self._values.get("include")
        return typing.cast(typing.Optional[typing.List[typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobMatrix(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-pipelines-github.JobPermission")
class JobPermission(enum.Enum):
    '''Access level for workflow permission scopes.'''

    READ = "READ"
    '''Read-only access.'''
    WRITE = "WRITE"
    '''Read-write access.'''
    NONE = "NONE"
    '''No access at all.'''


@jsii.data_type(
    jsii_type="cdk-pipelines-github.JobPermissions",
    jsii_struct_bases=[],
    name_mapping={
        "actions": "actions",
        "checks": "checks",
        "contents": "contents",
        "deployments": "deployments",
        "issues": "issues",
        "packages": "packages",
        "pull_requests": "pullRequests",
        "repository_projects": "repositoryProjects",
        "security_events": "securityEvents",
        "statuses": "statuses",
    },
)
class JobPermissions:
    def __init__(
        self,
        *,
        actions: typing.Optional[JobPermission] = None,
        checks: typing.Optional[JobPermission] = None,
        contents: typing.Optional[JobPermission] = None,
        deployments: typing.Optional[JobPermission] = None,
        issues: typing.Optional[JobPermission] = None,
        packages: typing.Optional[JobPermission] = None,
        pull_requests: typing.Optional[JobPermission] = None,
        repository_projects: typing.Optional[JobPermission] = None,
        security_events: typing.Optional[JobPermission] = None,
        statuses: typing.Optional[JobPermission] = None,
    ) -> None:
        '''The available scopes and access values for workflow permissions.

        If you
        specify the access for any of these scopes, all those that are not
        specified are set to ``JobPermission.NONE``, instead of the default behavior
        when none is specified.

        :param actions: 
        :param checks: 
        :param contents: 
        :param deployments: 
        :param issues: 
        :param packages: 
        :param pull_requests: 
        :param repository_projects: 
        :param security_events: 
        :param statuses: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if actions is not None:
            self._values["actions"] = actions
        if checks is not None:
            self._values["checks"] = checks
        if contents is not None:
            self._values["contents"] = contents
        if deployments is not None:
            self._values["deployments"] = deployments
        if issues is not None:
            self._values["issues"] = issues
        if packages is not None:
            self._values["packages"] = packages
        if pull_requests is not None:
            self._values["pull_requests"] = pull_requests
        if repository_projects is not None:
            self._values["repository_projects"] = repository_projects
        if security_events is not None:
            self._values["security_events"] = security_events
        if statuses is not None:
            self._values["statuses"] = statuses

    @builtins.property
    def actions(self) -> typing.Optional[JobPermission]:
        result = self._values.get("actions")
        return typing.cast(typing.Optional[JobPermission], result)

    @builtins.property
    def checks(self) -> typing.Optional[JobPermission]:
        result = self._values.get("checks")
        return typing.cast(typing.Optional[JobPermission], result)

    @builtins.property
    def contents(self) -> typing.Optional[JobPermission]:
        result = self._values.get("contents")
        return typing.cast(typing.Optional[JobPermission], result)

    @builtins.property
    def deployments(self) -> typing.Optional[JobPermission]:
        result = self._values.get("deployments")
        return typing.cast(typing.Optional[JobPermission], result)

    @builtins.property
    def issues(self) -> typing.Optional[JobPermission]:
        result = self._values.get("issues")
        return typing.cast(typing.Optional[JobPermission], result)

    @builtins.property
    def packages(self) -> typing.Optional[JobPermission]:
        result = self._values.get("packages")
        return typing.cast(typing.Optional[JobPermission], result)

    @builtins.property
    def pull_requests(self) -> typing.Optional[JobPermission]:
        result = self._values.get("pull_requests")
        return typing.cast(typing.Optional[JobPermission], result)

    @builtins.property
    def repository_projects(self) -> typing.Optional[JobPermission]:
        result = self._values.get("repository_projects")
        return typing.cast(typing.Optional[JobPermission], result)

    @builtins.property
    def security_events(self) -> typing.Optional[JobPermission]:
        result = self._values.get("security_events")
        return typing.cast(typing.Optional[JobPermission], result)

    @builtins.property
    def statuses(self) -> typing.Optional[JobPermission]:
        result = self._values.get("statuses")
        return typing.cast(typing.Optional[JobPermission], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobPermissions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.JobStep",
    jsii_struct_bases=[],
    name_mapping={
        "continue_on_error": "continueOnError",
        "env": "env",
        "id": "id",
        "if_": "if",
        "name": "name",
        "run": "run",
        "timeout_minutes": "timeoutMinutes",
        "uses": "uses",
        "with_": "with",
    },
)
class JobStep:
    def __init__(
        self,
        *,
        continue_on_error: typing.Optional[builtins.bool] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        if_: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        run: typing.Optional[builtins.str] = None,
        timeout_minutes: typing.Optional[jsii.Number] = None,
        uses: typing.Optional[builtins.str] = None,
        with_: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''A job step.

        :param continue_on_error: Prevents a job from failing when a step fails. Set to true to allow a job to pass when this step fails.
        :param env: Sets environment variables for steps to use in the runner environment. You can also set environment variables for the entire workflow or a job.
        :param id: A unique identifier for the step. You can use the id to reference the step in contexts.
        :param if_: You can use the if conditional to prevent a job from running unless a condition is met. You can use any supported context and expression to create a conditional.
        :param name: A name for your step to display on GitHub.
        :param run: Runs command-line programs using the operating system's shell. If you do not provide a name, the step name will default to the text specified in the run command.
        :param timeout_minutes: The maximum number of minutes to run the step before killing the process.
        :param uses: Selects an action to run as part of a step in your job. An action is a reusable unit of code. You can use an action defined in the same repository as the workflow, a public repository, or in a published Docker container image.
        :param with_: A map of the input parameters defined by the action. Each input parameter is a key/value pair. Input parameters are set as environment variables. The variable is prefixed with INPUT_ and converted to upper case.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if continue_on_error is not None:
            self._values["continue_on_error"] = continue_on_error
        if env is not None:
            self._values["env"] = env
        if id is not None:
            self._values["id"] = id
        if if_ is not None:
            self._values["if_"] = if_
        if name is not None:
            self._values["name"] = name
        if run is not None:
            self._values["run"] = run
        if timeout_minutes is not None:
            self._values["timeout_minutes"] = timeout_minutes
        if uses is not None:
            self._values["uses"] = uses
        if with_ is not None:
            self._values["with_"] = with_

    @builtins.property
    def continue_on_error(self) -> typing.Optional[builtins.bool]:
        '''Prevents a job from failing when a step fails.

        Set to true to allow a job
        to pass when this step fails.
        '''
        result = self._values.get("continue_on_error")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Sets environment variables for steps to use in the runner environment.

        You can also set environment variables for the entire workflow or a job.
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''A unique identifier for the step.

        You can use the id to reference the
        step in contexts.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def if_(self) -> typing.Optional[builtins.str]:
        '''You can use the if conditional to prevent a job from running unless a condition is met.

        You can use any supported context and expression to
        create a conditional.
        '''
        result = self._values.get("if_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''A name for your step to display on GitHub.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run(self) -> typing.Optional[builtins.str]:
        '''Runs command-line programs using the operating system's shell.

        If you do
        not provide a name, the step name will default to the text specified in
        the run command.
        '''
        result = self._values.get("run")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout_minutes(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of minutes to run the step before killing the process.'''
        result = self._values.get("timeout_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uses(self) -> typing.Optional[builtins.str]:
        '''Selects an action to run as part of a step in your job.

        An action is a
        reusable unit of code. You can use an action defined in the same
        repository as the workflow, a public repository, or in a published Docker
        container image.
        '''
        result = self._values.get("uses")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def with_(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''A map of the input parameters defined by the action.

        Each input parameter
        is a key/value pair. Input parameters are set as environment variables.
        The variable is prefixed with INPUT_ and converted to upper case.
        '''
        result = self._values.get("with_")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobStep(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.JobStepOutput",
    jsii_struct_bases=[],
    name_mapping={"output_name": "outputName", "step_id": "stepId"},
)
class JobStepOutput:
    def __init__(self, *, output_name: builtins.str, step_id: builtins.str) -> None:
        '''An output binding for a job.

        :param output_name: The name of the job output that is being bound.
        :param step_id: The ID of the step that exposes the output.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "output_name": output_name,
            "step_id": step_id,
        }

    @builtins.property
    def output_name(self) -> builtins.str:
        '''The name of the job output that is being bound.'''
        result = self._values.get("output_name")
        assert result is not None, "Required property 'output_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def step_id(self) -> builtins.str:
        '''The ID of the step that exposes the output.'''
        result = self._values.get("step_id")
        assert result is not None, "Required property 'step_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobStepOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.JobStrategy",
    jsii_struct_bases=[],
    name_mapping={
        "fail_fast": "failFast",
        "matrix": "matrix",
        "max_parallel": "maxParallel",
    },
)
class JobStrategy:
    def __init__(
        self,
        *,
        fail_fast: typing.Optional[builtins.bool] = None,
        matrix: typing.Optional[JobMatrix] = None,
        max_parallel: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''A strategy creates a build matrix for your jobs.

        You can define different
        variations to run each job in.

        :param fail_fast: When set to true, GitHub cancels all in-progress jobs if any matrix job fails. Default: true
        :param matrix: You can define a matrix of different job configurations. A matrix allows you to create multiple jobs by performing variable substitution in a single job definition. For example, you can use a matrix to create jobs for more than one supported version of a programming language, operating system, or tool. A matrix reuses the job's configuration and creates a job for each matrix you configure. A job matrix can generate a maximum of 256 jobs per workflow run. This limit also applies to self-hosted runners.
        :param max_parallel: The maximum number of jobs that can run simultaneously when using a matrix job strategy. By default, GitHub will maximize the number of jobs run in parallel depending on the available runners on GitHub-hosted virtual machines.
        '''
        if isinstance(matrix, dict):
            matrix = JobMatrix(**matrix)
        self._values: typing.Dict[str, typing.Any] = {}
        if fail_fast is not None:
            self._values["fail_fast"] = fail_fast
        if matrix is not None:
            self._values["matrix"] = matrix
        if max_parallel is not None:
            self._values["max_parallel"] = max_parallel

    @builtins.property
    def fail_fast(self) -> typing.Optional[builtins.bool]:
        '''When set to true, GitHub cancels all in-progress jobs if any matrix job fails.

        Default: true
        '''
        result = self._values.get("fail_fast")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def matrix(self) -> typing.Optional[JobMatrix]:
        '''You can define a matrix of different job configurations.

        A matrix allows
        you to create multiple jobs by performing variable substitution in a
        single job definition. For example, you can use a matrix to create jobs
        for more than one supported version of a programming language, operating
        system, or tool. A matrix reuses the job's configuration and creates a
        job for each matrix you configure.

        A job matrix can generate a maximum of 256 jobs per workflow run. This
        limit also applies to self-hosted runners.
        '''
        result = self._values.get("matrix")
        return typing.cast(typing.Optional[JobMatrix], result)

    @builtins.property
    def max_parallel(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of jobs that can run simultaneously when using a matrix job strategy.

        By default, GitHub will maximize the number of jobs
        run in parallel depending on the available runners on GitHub-hosted
        virtual machines.
        '''
        result = self._values.get("max_parallel")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JobStrategy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.LabelOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class LabelOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''label options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LabelOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.MilestoneOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class MilestoneOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Milestone options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MilestoneOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.PageBuildOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class PageBuildOptions:
    def __init__(self) -> None:
        '''The Page build event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PageBuildOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.ProjectCardOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class ProjectCardOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Project card options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectCardOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.ProjectColumnOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class ProjectColumnOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Probject column options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectColumnOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.ProjectOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class ProjectOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Project options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.PublicOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class PublicOptions:
    def __init__(self) -> None:
        '''The Public event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PublicOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.PullRequestOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class PullRequestOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Pull request options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PullRequestOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.PullRequestReviewCommentOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class PullRequestReviewCommentOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Pull request review comment options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PullRequestReviewCommentOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.PullRequestReviewOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class PullRequestReviewOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Pull request review options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PullRequestReviewOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.PushOptions",
    jsii_struct_bases=[],
    name_mapping={"branches": "branches", "paths": "paths", "tags": "tags"},
)
class PushOptions:
    def __init__(
        self,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        paths: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Options for push-like events.

        :param branches: When using the push and pull_request events, you can configure a workflow to run on specific branches or tags. For a pull_request event, only branches and tags on the base are evaluated. If you define only tags or only branches, the workflow won't run for events affecting the undefined Git ref.
        :param paths: When using the push and pull_request events, you can configure a workflow to run when at least one file does not match paths-ignore or at least one modified file matches the configured paths. Path filters are not evaluated for pushes to tags.
        :param tags: When using the push and pull_request events, you can configure a workflow to run on specific branches or tags. For a pull_request event, only branches and tags on the base are evaluated. If you define only tags or only branches, the workflow won't run for events affecting the undefined Git ref.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if branches is not None:
            self._values["branches"] = branches
        if paths is not None:
            self._values["paths"] = paths
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        '''When using the push and pull_request events, you can configure a workflow to run on specific branches or tags.

        For a pull_request event, only
        branches and tags on the base are evaluated. If you define only tags or
        only branches, the workflow won't run for events affecting the undefined
        Git ref.

        :see: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet
        '''
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def paths(self) -> typing.Optional[typing.List[builtins.str]]:
        '''When using the push and pull_request events, you can configure a workflow to run when at least one file does not match paths-ignore or at least one modified file matches the configured paths.

        Path filters are not
        evaluated for pushes to tags.

        :see: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet
        '''
        result = self._values.get("paths")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''When using the push and pull_request events, you can configure a workflow to run on specific branches or tags.

        For a pull_request event, only
        branches and tags on the base are evaluated. If you define only tags or
        only branches, the workflow won't run for events affecting the undefined
        Git ref.

        :see: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PushOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.RegistryPackageOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class RegistryPackageOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Registry package options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistryPackageOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.ReleaseOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class ReleaseOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Release options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ReleaseOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.RepositoryDispatchOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class RepositoryDispatchOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Repository dispatch options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RepositoryDispatchOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.RunSettings",
    jsii_struct_bases=[],
    name_mapping={"shell": "shell", "working_directory": "workingDirectory"},
)
class RunSettings:
    def __init__(
        self,
        *,
        shell: typing.Optional[builtins.str] = None,
        working_directory: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Run settings for a job.

        :param shell: Which shell to use for running the step.
        :param working_directory: Working directory to use when running the step.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if shell is not None:
            self._values["shell"] = shell
        if working_directory is not None:
            self._values["working_directory"] = working_directory

    @builtins.property
    def shell(self) -> typing.Optional[builtins.str]:
        '''Which shell to use for running the step.

        Example::

            "bash"
        '''
        result = self._values.get("shell")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def working_directory(self) -> typing.Optional[builtins.str]:
        '''Working directory to use when running the step.'''
        result = self._values.get("working_directory")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RunSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.StatusOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class StatusOptions:
    def __init__(self) -> None:
        '''The Status event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StatusOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.Triggers",
    jsii_struct_bases=[],
    name_mapping={
        "check_run": "checkRun",
        "check_suite": "checkSuite",
        "create": "create",
        "delete": "delete",
        "deployment": "deployment",
        "deployment_status": "deploymentStatus",
        "fork": "fork",
        "gollum": "gollum",
        "issue_comment": "issueComment",
        "issues": "issues",
        "label": "label",
        "milestone": "milestone",
        "page_build": "pageBuild",
        "project": "project",
        "project_card": "projectCard",
        "project_column": "projectColumn",
        "public": "public",
        "pull_request": "pullRequest",
        "pull_request_review": "pullRequestReview",
        "pull_request_review_comment": "pullRequestReviewComment",
        "pull_request_target": "pullRequestTarget",
        "push": "push",
        "registry_package": "registryPackage",
        "release": "release",
        "repository_dispatch": "repositoryDispatch",
        "schedule": "schedule",
        "status": "status",
        "watch": "watch",
        "workflow_dispatch": "workflowDispatch",
        "workflow_run": "workflowRun",
    },
)
class Triggers:
    def __init__(
        self,
        *,
        check_run: typing.Optional[CheckRunOptions] = None,
        check_suite: typing.Optional[CheckSuiteOptions] = None,
        create: typing.Optional[CreateOptions] = None,
        delete: typing.Optional[DeleteOptions] = None,
        deployment: typing.Optional[DeploymentOptions] = None,
        deployment_status: typing.Optional[DeploymentStatusOptions] = None,
        fork: typing.Optional[ForkOptions] = None,
        gollum: typing.Optional[GollumOptions] = None,
        issue_comment: typing.Optional[IssueCommentOptions] = None,
        issues: typing.Optional[IssuesOptions] = None,
        label: typing.Optional[LabelOptions] = None,
        milestone: typing.Optional[MilestoneOptions] = None,
        page_build: typing.Optional[PageBuildOptions] = None,
        project: typing.Optional[ProjectOptions] = None,
        project_card: typing.Optional[ProjectCardOptions] = None,
        project_column: typing.Optional[ProjectColumnOptions] = None,
        public: typing.Optional[PublicOptions] = None,
        pull_request: typing.Optional[PullRequestOptions] = None,
        pull_request_review: typing.Optional[PullRequestReviewOptions] = None,
        pull_request_review_comment: typing.Optional[PullRequestReviewCommentOptions] = None,
        pull_request_target: typing.Optional["PullRequestTargetOptions"] = None,
        push: typing.Optional[PushOptions] = None,
        registry_package: typing.Optional[RegistryPackageOptions] = None,
        release: typing.Optional[ReleaseOptions] = None,
        repository_dispatch: typing.Optional[RepositoryDispatchOptions] = None,
        schedule: typing.Optional[typing.Sequence[CronScheduleOptions]] = None,
        status: typing.Optional[StatusOptions] = None,
        watch: typing.Optional["WatchOptions"] = None,
        workflow_dispatch: typing.Optional["WorkflowDispatchOptions"] = None,
        workflow_run: typing.Optional["WorkflowRunOptions"] = None,
    ) -> None:
        '''The set of available triggers for GitHub Workflows.

        :param check_run: Runs your workflow anytime the check_run event occurs.
        :param check_suite: Runs your workflow anytime the check_suite event occurs.
        :param create: Runs your workflow anytime someone creates a branch or tag, which triggers the create event.
        :param delete: Runs your workflow anytime someone deletes a branch or tag, which triggers the delete event.
        :param deployment: Runs your workflow anytime someone creates a deployment, which triggers the deployment event. Deployments created with a commit SHA may not have a Git ref.
        :param deployment_status: Runs your workflow anytime a third party provides a deployment status, which triggers the deployment_status event. Deployments created with a commit SHA may not have a Git ref.
        :param fork: Runs your workflow anytime when someone forks a repository, which triggers the fork event.
        :param gollum: Runs your workflow when someone creates or updates a Wiki page, which triggers the gollum event.
        :param issue_comment: Runs your workflow anytime the issue_comment event occurs.
        :param issues: Runs your workflow anytime the issues event occurs.
        :param label: Runs your workflow anytime the label event occurs.
        :param milestone: Runs your workflow anytime the milestone event occurs.
        :param page_build: Runs your workflow anytime someone pushes to a GitHub Pages-enabled branch, which triggers the page_build event.
        :param project: Runs your workflow anytime the project event occurs.
        :param project_card: Runs your workflow anytime the project_card event occurs.
        :param project_column: Runs your workflow anytime the project_column event occurs.
        :param public: Runs your workflow anytime someone makes a private repository public, which triggers the public event.
        :param pull_request: Runs your workflow anytime the pull_request event occurs.
        :param pull_request_review: Runs your workflow anytime the pull_request_review event occurs.
        :param pull_request_review_comment: Runs your workflow anytime a comment on a pull request's unified diff is modified, which triggers the pull_request_review_comment event.
        :param pull_request_target: This event runs in the context of the base of the pull request, rather than in the merge commit as the pull_request event does. This prevents executing unsafe workflow code from the head of the pull request that could alter your repository or steal any secrets you use in your workflow. This event allows you to do things like create workflows that label and comment on pull requests based on the contents of the event payload. WARNING: The ``pull_request_target`` event is granted read/write repository token and can access secrets, even when it is triggered from a fork. Although the workflow runs in the context of the base of the pull request, you should make sure that you do not check out, build, or run untrusted code from the pull request with this event. Additionally, any caches share the same scope as the base branch, and to help prevent cache poisoning, you should not save the cache if there is a possibility that the cache contents were altered.
        :param push: Runs your workflow when someone pushes to a repository branch, which triggers the push event.
        :param registry_package: Runs your workflow anytime a package is published or updated.
        :param release: Runs your workflow anytime the release event occurs.
        :param repository_dispatch: You can use the GitHub API to trigger a webhook event called repository_dispatch when you want to trigger a workflow for activity that happens outside of GitHub.
        :param schedule: You can schedule a workflow to run at specific UTC times using POSIX cron syntax. Scheduled workflows run on the latest commit on the default or base branch. The shortest interval you can run scheduled workflows is once every 5 minutes.
        :param status: Runs your workflow anytime the status of a Git commit changes, which triggers the status event.
        :param watch: Runs your workflow anytime the watch event occurs.
        :param workflow_dispatch: You can configure custom-defined input properties, default input values, and required inputs for the event directly in your workflow. When the workflow runs, you can access the input values in the github.event.inputs context.
        :param workflow_run: This event occurs when a workflow run is requested or completed, and allows you to execute a workflow based on the finished result of another workflow. A workflow run is triggered regardless of the result of the previous workflow.

        :see: https://docs.github.com/en/actions/reference/events-that-trigger-workflows
        '''
        if isinstance(check_run, dict):
            check_run = CheckRunOptions(**check_run)
        if isinstance(check_suite, dict):
            check_suite = CheckSuiteOptions(**check_suite)
        if isinstance(create, dict):
            create = CreateOptions(**create)
        if isinstance(delete, dict):
            delete = DeleteOptions(**delete)
        if isinstance(deployment, dict):
            deployment = DeploymentOptions(**deployment)
        if isinstance(deployment_status, dict):
            deployment_status = DeploymentStatusOptions(**deployment_status)
        if isinstance(fork, dict):
            fork = ForkOptions(**fork)
        if isinstance(gollum, dict):
            gollum = GollumOptions(**gollum)
        if isinstance(issue_comment, dict):
            issue_comment = IssueCommentOptions(**issue_comment)
        if isinstance(issues, dict):
            issues = IssuesOptions(**issues)
        if isinstance(label, dict):
            label = LabelOptions(**label)
        if isinstance(milestone, dict):
            milestone = MilestoneOptions(**milestone)
        if isinstance(page_build, dict):
            page_build = PageBuildOptions(**page_build)
        if isinstance(project, dict):
            project = ProjectOptions(**project)
        if isinstance(project_card, dict):
            project_card = ProjectCardOptions(**project_card)
        if isinstance(project_column, dict):
            project_column = ProjectColumnOptions(**project_column)
        if isinstance(public, dict):
            public = PublicOptions(**public)
        if isinstance(pull_request, dict):
            pull_request = PullRequestOptions(**pull_request)
        if isinstance(pull_request_review, dict):
            pull_request_review = PullRequestReviewOptions(**pull_request_review)
        if isinstance(pull_request_review_comment, dict):
            pull_request_review_comment = PullRequestReviewCommentOptions(**pull_request_review_comment)
        if isinstance(pull_request_target, dict):
            pull_request_target = PullRequestTargetOptions(**pull_request_target)
        if isinstance(push, dict):
            push = PushOptions(**push)
        if isinstance(registry_package, dict):
            registry_package = RegistryPackageOptions(**registry_package)
        if isinstance(release, dict):
            release = ReleaseOptions(**release)
        if isinstance(repository_dispatch, dict):
            repository_dispatch = RepositoryDispatchOptions(**repository_dispatch)
        if isinstance(status, dict):
            status = StatusOptions(**status)
        if isinstance(watch, dict):
            watch = WatchOptions(**watch)
        if isinstance(workflow_dispatch, dict):
            workflow_dispatch = WorkflowDispatchOptions(**workflow_dispatch)
        if isinstance(workflow_run, dict):
            workflow_run = WorkflowRunOptions(**workflow_run)
        self._values: typing.Dict[str, typing.Any] = {}
        if check_run is not None:
            self._values["check_run"] = check_run
        if check_suite is not None:
            self._values["check_suite"] = check_suite
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if deployment is not None:
            self._values["deployment"] = deployment
        if deployment_status is not None:
            self._values["deployment_status"] = deployment_status
        if fork is not None:
            self._values["fork"] = fork
        if gollum is not None:
            self._values["gollum"] = gollum
        if issue_comment is not None:
            self._values["issue_comment"] = issue_comment
        if issues is not None:
            self._values["issues"] = issues
        if label is not None:
            self._values["label"] = label
        if milestone is not None:
            self._values["milestone"] = milestone
        if page_build is not None:
            self._values["page_build"] = page_build
        if project is not None:
            self._values["project"] = project
        if project_card is not None:
            self._values["project_card"] = project_card
        if project_column is not None:
            self._values["project_column"] = project_column
        if public is not None:
            self._values["public"] = public
        if pull_request is not None:
            self._values["pull_request"] = pull_request
        if pull_request_review is not None:
            self._values["pull_request_review"] = pull_request_review
        if pull_request_review_comment is not None:
            self._values["pull_request_review_comment"] = pull_request_review_comment
        if pull_request_target is not None:
            self._values["pull_request_target"] = pull_request_target
        if push is not None:
            self._values["push"] = push
        if registry_package is not None:
            self._values["registry_package"] = registry_package
        if release is not None:
            self._values["release"] = release
        if repository_dispatch is not None:
            self._values["repository_dispatch"] = repository_dispatch
        if schedule is not None:
            self._values["schedule"] = schedule
        if status is not None:
            self._values["status"] = status
        if watch is not None:
            self._values["watch"] = watch
        if workflow_dispatch is not None:
            self._values["workflow_dispatch"] = workflow_dispatch
        if workflow_run is not None:
            self._values["workflow_run"] = workflow_run

    @builtins.property
    def check_run(self) -> typing.Optional[CheckRunOptions]:
        '''Runs your workflow anytime the check_run event occurs.'''
        result = self._values.get("check_run")
        return typing.cast(typing.Optional[CheckRunOptions], result)

    @builtins.property
    def check_suite(self) -> typing.Optional[CheckSuiteOptions]:
        '''Runs your workflow anytime the check_suite event occurs.'''
        result = self._values.get("check_suite")
        return typing.cast(typing.Optional[CheckSuiteOptions], result)

    @builtins.property
    def create(self) -> typing.Optional[CreateOptions]:
        '''Runs your workflow anytime someone creates a branch or tag, which triggers the create event.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[CreateOptions], result)

    @builtins.property
    def delete(self) -> typing.Optional[DeleteOptions]:
        '''Runs your workflow anytime someone deletes a branch or tag, which triggers the delete event.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[DeleteOptions], result)

    @builtins.property
    def deployment(self) -> typing.Optional[DeploymentOptions]:
        '''Runs your workflow anytime someone creates a deployment, which triggers the deployment event.

        Deployments created with a commit SHA may not have
        a Git ref.
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional[DeploymentOptions], result)

    @builtins.property
    def deployment_status(self) -> typing.Optional[DeploymentStatusOptions]:
        '''Runs your workflow anytime a third party provides a deployment status, which triggers the deployment_status event.

        Deployments created with a
        commit SHA may not have a Git ref.
        '''
        result = self._values.get("deployment_status")
        return typing.cast(typing.Optional[DeploymentStatusOptions], result)

    @builtins.property
    def fork(self) -> typing.Optional[ForkOptions]:
        '''Runs your workflow anytime when someone forks a repository, which triggers the fork event.'''
        result = self._values.get("fork")
        return typing.cast(typing.Optional[ForkOptions], result)

    @builtins.property
    def gollum(self) -> typing.Optional[GollumOptions]:
        '''Runs your workflow when someone creates or updates a Wiki page, which triggers the gollum event.'''
        result = self._values.get("gollum")
        return typing.cast(typing.Optional[GollumOptions], result)

    @builtins.property
    def issue_comment(self) -> typing.Optional[IssueCommentOptions]:
        '''Runs your workflow anytime the issue_comment event occurs.'''
        result = self._values.get("issue_comment")
        return typing.cast(typing.Optional[IssueCommentOptions], result)

    @builtins.property
    def issues(self) -> typing.Optional[IssuesOptions]:
        '''Runs your workflow anytime the issues event occurs.'''
        result = self._values.get("issues")
        return typing.cast(typing.Optional[IssuesOptions], result)

    @builtins.property
    def label(self) -> typing.Optional[LabelOptions]:
        '''Runs your workflow anytime the label event occurs.'''
        result = self._values.get("label")
        return typing.cast(typing.Optional[LabelOptions], result)

    @builtins.property
    def milestone(self) -> typing.Optional[MilestoneOptions]:
        '''Runs your workflow anytime the milestone event occurs.'''
        result = self._values.get("milestone")
        return typing.cast(typing.Optional[MilestoneOptions], result)

    @builtins.property
    def page_build(self) -> typing.Optional[PageBuildOptions]:
        '''Runs your workflow anytime someone pushes to a GitHub Pages-enabled branch, which triggers the page_build event.'''
        result = self._values.get("page_build")
        return typing.cast(typing.Optional[PageBuildOptions], result)

    @builtins.property
    def project(self) -> typing.Optional[ProjectOptions]:
        '''Runs your workflow anytime the project event occurs.'''
        result = self._values.get("project")
        return typing.cast(typing.Optional[ProjectOptions], result)

    @builtins.property
    def project_card(self) -> typing.Optional[ProjectCardOptions]:
        '''Runs your workflow anytime the project_card event occurs.'''
        result = self._values.get("project_card")
        return typing.cast(typing.Optional[ProjectCardOptions], result)

    @builtins.property
    def project_column(self) -> typing.Optional[ProjectColumnOptions]:
        '''Runs your workflow anytime the project_column event occurs.'''
        result = self._values.get("project_column")
        return typing.cast(typing.Optional[ProjectColumnOptions], result)

    @builtins.property
    def public(self) -> typing.Optional[PublicOptions]:
        '''Runs your workflow anytime someone makes a private repository public, which triggers the public event.'''
        result = self._values.get("public")
        return typing.cast(typing.Optional[PublicOptions], result)

    @builtins.property
    def pull_request(self) -> typing.Optional[PullRequestOptions]:
        '''Runs your workflow anytime the pull_request event occurs.'''
        result = self._values.get("pull_request")
        return typing.cast(typing.Optional[PullRequestOptions], result)

    @builtins.property
    def pull_request_review(self) -> typing.Optional[PullRequestReviewOptions]:
        '''Runs your workflow anytime the pull_request_review event occurs.'''
        result = self._values.get("pull_request_review")
        return typing.cast(typing.Optional[PullRequestReviewOptions], result)

    @builtins.property
    def pull_request_review_comment(
        self,
    ) -> typing.Optional[PullRequestReviewCommentOptions]:
        '''Runs your workflow anytime a comment on a pull request's unified diff is modified, which triggers the pull_request_review_comment event.'''
        result = self._values.get("pull_request_review_comment")
        return typing.cast(typing.Optional[PullRequestReviewCommentOptions], result)

    @builtins.property
    def pull_request_target(self) -> typing.Optional["PullRequestTargetOptions"]:
        '''This event runs in the context of the base of the pull request, rather than in the merge commit as the pull_request event does.

        This prevents
        executing unsafe workflow code from the head of the pull request that
        could alter your repository or steal any secrets you use in your workflow.
        This event allows you to do things like create workflows that label and
        comment on pull requests based on the contents of the event payload.

        WARNING: The ``pull_request_target`` event is granted read/write repository
        token and can access secrets, even when it is triggered from a fork.
        Although the workflow runs in the context of the base of the pull request,
        you should make sure that you do not check out, build, or run untrusted
        code from the pull request with this event. Additionally, any caches
        share the same scope as the base branch, and to help prevent cache
        poisoning, you should not save the cache if there is a possibility that
        the cache contents were altered.

        :see: https://securitylab.github.com/research/github-actions-preventing-pwn-requests
        '''
        result = self._values.get("pull_request_target")
        return typing.cast(typing.Optional["PullRequestTargetOptions"], result)

    @builtins.property
    def push(self) -> typing.Optional[PushOptions]:
        '''Runs your workflow when someone pushes to a repository branch, which triggers the push event.'''
        result = self._values.get("push")
        return typing.cast(typing.Optional[PushOptions], result)

    @builtins.property
    def registry_package(self) -> typing.Optional[RegistryPackageOptions]:
        '''Runs your workflow anytime a package is published or updated.'''
        result = self._values.get("registry_package")
        return typing.cast(typing.Optional[RegistryPackageOptions], result)

    @builtins.property
    def release(self) -> typing.Optional[ReleaseOptions]:
        '''Runs your workflow anytime the release event occurs.'''
        result = self._values.get("release")
        return typing.cast(typing.Optional[ReleaseOptions], result)

    @builtins.property
    def repository_dispatch(self) -> typing.Optional[RepositoryDispatchOptions]:
        '''You can use the GitHub API to trigger a webhook event called repository_dispatch when you want to trigger a workflow for activity that happens outside of GitHub.'''
        result = self._values.get("repository_dispatch")
        return typing.cast(typing.Optional[RepositoryDispatchOptions], result)

    @builtins.property
    def schedule(self) -> typing.Optional[typing.List[CronScheduleOptions]]:
        '''You can schedule a workflow to run at specific UTC times using POSIX cron syntax.

        Scheduled workflows run on the latest commit on the default or
        base branch. The shortest interval you can run scheduled workflows is
        once every 5 minutes.

        :see: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html#tag_20_25_07
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[typing.List[CronScheduleOptions]], result)

    @builtins.property
    def status(self) -> typing.Optional[StatusOptions]:
        '''Runs your workflow anytime the status of a Git commit changes, which triggers the status event.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[StatusOptions], result)

    @builtins.property
    def watch(self) -> typing.Optional["WatchOptions"]:
        '''Runs your workflow anytime the watch event occurs.'''
        result = self._values.get("watch")
        return typing.cast(typing.Optional["WatchOptions"], result)

    @builtins.property
    def workflow_dispatch(self) -> typing.Optional["WorkflowDispatchOptions"]:
        '''You can configure custom-defined input properties, default input values, and required inputs for the event directly in your workflow.

        When the
        workflow runs, you can access the input values in the github.event.inputs
        context.
        '''
        result = self._values.get("workflow_dispatch")
        return typing.cast(typing.Optional["WorkflowDispatchOptions"], result)

    @builtins.property
    def workflow_run(self) -> typing.Optional["WorkflowRunOptions"]:
        '''This event occurs when a workflow run is requested or completed, and allows you to execute a workflow based on the finished result of another workflow.

        A workflow run is triggered regardless of the result of the
        previous workflow.
        '''
        result = self._values.get("workflow_run")
        return typing.cast(typing.Optional["WorkflowRunOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Triggers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.WatchOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class WatchOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Watch options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WatchOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.WorkflowDispatchOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class WorkflowDispatchOptions:
    def __init__(self) -> None:
        '''The Workflow dispatch event accepts no options.'''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowDispatchOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.WorkflowRunOptions",
    jsii_struct_bases=[],
    name_mapping={"types": "types"},
)
class WorkflowRunOptions:
    def __init__(
        self,
        *,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Workflow run options.

        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowRunOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-pipelines-github.PullRequestTargetOptions",
    jsii_struct_bases=[PushOptions],
    name_mapping={
        "branches": "branches",
        "paths": "paths",
        "tags": "tags",
        "types": "types",
    },
)
class PullRequestTargetOptions(PushOptions):
    def __init__(
        self,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
        paths: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Pull request target options.

        :param branches: When using the push and pull_request events, you can configure a workflow to run on specific branches or tags. For a pull_request event, only branches and tags on the base are evaluated. If you define only tags or only branches, the workflow won't run for events affecting the undefined Git ref.
        :param paths: When using the push and pull_request events, you can configure a workflow to run when at least one file does not match paths-ignore or at least one modified file matches the configured paths. Path filters are not evaluated for pushes to tags.
        :param tags: When using the push and pull_request events, you can configure a workflow to run on specific branches or tags. For a pull_request event, only branches and tags on the base are evaluated. If you define only tags or only branches, the workflow won't run for events affecting the undefined Git ref.
        :param types: Which activity types to trigger on.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if branches is not None:
            self._values["branches"] = branches
        if paths is not None:
            self._values["paths"] = paths
        if tags is not None:
            self._values["tags"] = tags
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        '''When using the push and pull_request events, you can configure a workflow to run on specific branches or tags.

        For a pull_request event, only
        branches and tags on the base are evaluated. If you define only tags or
        only branches, the workflow won't run for events affecting the undefined
        Git ref.

        :see: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet
        '''
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def paths(self) -> typing.Optional[typing.List[builtins.str]]:
        '''When using the push and pull_request events, you can configure a workflow to run when at least one file does not match paths-ignore or at least one modified file matches the configured paths.

        Path filters are not
        evaluated for pushes to tags.

        :see: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet
        '''
        result = self._values.get("paths")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''When using the push and pull_request events, you can configure a workflow to run on specific branches or tags.

        For a pull_request event, only
        branches and tags on the base are evaluated. If you define only tags or
        only branches, the workflow won't run for events affecting the undefined
        Git ref.

        :see: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Which activity types to trigger on.

        :defaults: - all activity types
        '''
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PullRequestTargetOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AwsCredentialsSecrets",
    "CheckRunOptions",
    "CheckSuiteOptions",
    "ContainerCredentials",
    "ContainerOptions",
    "CreateOptions",
    "CronScheduleOptions",
    "DeleteOptions",
    "DeploymentOptions",
    "DeploymentStatusOptions",
    "ForkOptions",
    "GitHubWorkflow",
    "GitHubWorkflowProps",
    "GollumOptions",
    "IssueCommentOptions",
    "IssuesOptions",
    "Job",
    "JobDefaults",
    "JobMatrix",
    "JobPermission",
    "JobPermissions",
    "JobStep",
    "JobStepOutput",
    "JobStrategy",
    "LabelOptions",
    "MilestoneOptions",
    "PageBuildOptions",
    "ProjectCardOptions",
    "ProjectColumnOptions",
    "ProjectOptions",
    "PublicOptions",
    "PullRequestOptions",
    "PullRequestReviewCommentOptions",
    "PullRequestReviewOptions",
    "PullRequestTargetOptions",
    "PushOptions",
    "RegistryPackageOptions",
    "ReleaseOptions",
    "RepositoryDispatchOptions",
    "RunSettings",
    "StatusOptions",
    "Triggers",
    "WatchOptions",
    "WorkflowDispatchOptions",
    "WorkflowRunOptions",
]

publication.publish()
