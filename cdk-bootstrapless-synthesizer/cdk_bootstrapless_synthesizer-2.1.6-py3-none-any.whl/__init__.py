'''
# cdk-bootstrapless-synthesizer

[![npm version](https://img.shields.io/npm/v/cdk-bootstrapless-synthesizer)](https://www.npmjs.com/package/cdk-bootstrapless-synthesizer)
[![PyPI](https://img.shields.io/pypi/v/cdk-bootstrapless-synthesizer)](https://pypi.org/project/cdk-bootstrapless-synthesizer)
[![npm](https://img.shields.io/npm/dw/cdk-bootstrapless-synthesizer?label=npm%20downloads)](https://www.npmjs.com/package/cdk-bootstrapless-synthesizer)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/cdk-bootstrapless-synthesizer?label=pypi%20downloads)](https://pypi.org/project/cdk-bootstrapless-synthesizer)

A bootstrapless stack synthesizer that is designated to generate templates that can be directly used by AWS CloudFormation.

Please use ^1.0.0 for cdk version 1.x.x, use ^2.0.0 for cdk version 2.x.x

## Usage

```python
import { BootstraplessStackSynthesizer } from 'cdk-bootstrapless-synthesizer';
```

[main.ts](sample/src/main.ts)

```python
const app = new App();

new MyStack(app, 'my-stack-dev', {
  synthesizer: new BootstraplessStackSynthesizer({
    templateBucketName: 'cfn-template-bucket',

    fileAssetBucketName: 'file-asset-bucket-${AWS::Region}',
    fileAssetRegionSet: ['us-west-1', 'us-west-2'],
    fileAssetPrefix: 'file-asset-prefix/latest/',

    imageAssetRepositoryName: 'your-ecr-repo-name',
    imageAssetAccountId: '1234567890',
    imageAssetTagPrefix: 'latest-',
    imageAssetRegionSet: ['us-west-1', 'us-west-2'],
  }),
});

// Or by environment variables
env.BSS_TEMPLATE_BUCKET_NAME = 'cfn-template-bucket';

env.BSS_FILE_ASSET_BUCKET_NAME = 'file-asset-bucket-\${AWS::Region}';
env.BSS_FILE_ASSET_REGION_SET = 'us-west-1,us-west-2';
env.BSS_FILE_ASSET_PREFIX = 'file-asset-prefix/latest/';

env.BSS_IMAGE_ASSET_REPOSITORY_NAME = 'your-ecr-repo-name';
env.BSS_IMAGE_ASSET_ACCOUNT_ID = '1234567890';
env.BSS_IMAGE_ASSET_TAG_PREFIX = 'latest-';
env.BSS_IMAGE_ASSET_REGION_SET = 'us-west-1,us-west-2';

new MyStack(app, 'my-stack-dev2', {
  synthesizer: new BootstraplessStackSynthesizer(),
});

// use Aspect to grant the role to pull ECR repository from account BSS_IMAGE_ASSET_ACCOUNT_ID
```

[main.ts](sample/src/main.ts)

Synth AWS CloudFormation templates, assets and upload them

```shell
$ cdk synth
$ npx cdk-assets publish -p cdk.out/my-stack-dev.assets.json -v
```

## Limitations

When using `BSS_IMAGE_ASSET_ACCOUNT_ID` to push ECR repository to shared account, you need use `Aspect` to grant the role with policy to pull the repository from cross account. Or using the following `WithCrossAccount`  techniques.

Currently only below scenarios are supported,

* ECS
* SageMaker training job integrated with Step Functions

For other scenarios, the feature request or pull request are welcome.

```python
function OverrideRepositoryAccount(scope: Construct, id: string, repo: IRepository): IRepository {
  class Import extends RepositoryBase {
    public repositoryName = repo.repositoryName;
    public repositoryArn = Repository.arnForLocalRepository(repo.repositoryName, scope, env.BSS_IMAGE_ASSET_ACCOUNT_ID);

    public addToResourcePolicy(_statement: iam.PolicyStatement): iam.AddToResourcePolicyResult {
      // dropped
      return { statementAdded: false };
    }
  }

  return new Import(scope, id);
}

function WithCrossAccount(image: DockerImageAsset): DockerImageAsset {
  image.repository = OverrideRepositoryAccount(image, 'CrossAccountRepo', image.repository);
  return image;
}

export class SampleStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    const image = WithCrossAccount(new DockerImageAsset(this, 'MyBuildImage', {
      directory: path.join(__dirname, '../docker'),
    }));

    new CfnOutput(this, 'output', { value: image.imageUri });

    const taskDefinition = new ecs.FargateTaskDefinition(this, 'TaskDef');
    taskDefinition.addContainer('DefaultContainer', {
      image: ecs.ContainerImage.fromDockerImageAsset(image),
      memoryLimitMiB: 512,
    });

    fromAsset(this, 'stepfunctions', {
      directory: path.join(__dirname, '../docker'),
    });
  }
}
```

[main.ts](sample/src/main.ts)

## Sample Project

See [Sample Project](./sample/README.md)

## API Reference

See [API Reference](./API.md) for API details.
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
import aws_cdk.aws_ecs
import aws_cdk.aws_iam
import constructs


class BootstraplessStackSynthesizer(
    aws_cdk.StackSynthesizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-bootstrapless-synthesizer.BootstraplessStackSynthesizer",
):
    '''A Bootstrapless stack synthesizer that is designated to generate templates that can be directly used by Cloudformation.'''

    def __init__(
        self,
        *,
        file_asset_bucket_name: typing.Optional[builtins.str] = None,
        file_asset_prefix: typing.Optional[builtins.str] = None,
        file_asset_publishing_role_arn: typing.Optional[builtins.str] = None,
        file_asset_region_set: typing.Optional[typing.Sequence[builtins.str]] = None,
        image_asset_account_id: typing.Optional[builtins.str] = None,
        image_asset_publishing_role_arn: typing.Optional[builtins.str] = None,
        image_asset_region_set: typing.Optional[typing.Sequence[builtins.str]] = None,
        image_asset_repository_name: typing.Optional[builtins.str] = None,
        image_asset_tag_prefix: typing.Optional[builtins.str] = None,
        template_bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file_asset_bucket_name: Name of the S3 bucket to hold file assets. You must supply this if you have given a non-standard name to the staging bucket. The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will be replaced with the values of qualifier and the stack's account and region, respectively. Default: - process.env.BSS_FILE_ASSET_BUCKET_NAME
        :param file_asset_prefix: Object key prefix to use while storing S3 Assets. Default: - process.env.BSS_FILE_ASSET_PREFIX
        :param file_asset_publishing_role_arn: The role to use to publish file assets to the S3 bucket in this environment. You must supply this if you have given a non-standard name to the publishing role. The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will be replaced with the values of qualifier and the stack's account and region, respectively. Default: - process.env.BSS_FILE_ASSET_PUBLISHING_ROLE_ARN
        :param file_asset_region_set: The regions set of file assets to be published only when ``fileAssetBucketName`` contains ``${AWS::Region}``. For examples: ``['us-east-1', 'us-west-1']`` Default: - process.env.BSS_FILE_ASSET_REGION_SET // comma delimited list
        :param image_asset_account_id: Override the ECR repository account id of the Docker Image assets. Default: - process.env.BSS_IMAGE_ASSET_ACCOUNT_ID
        :param image_asset_publishing_role_arn: The role to use to publish image assets to the ECR repository in this environment. You must supply this if you have given a non-standard name to the publishing role. The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will be replaced with the values of qualifier and the stack's account and region, respectively. Default: - process.env.BSS_IMAGE_ASSET_PUBLISHING_ROLE_ARN
        :param image_asset_region_set: Override the ECR repository region of the Docker Image assets. For examples: ``['us-east-1', 'us-west-1']`` Default: - process.env.BSS_IMAGE_ASSET_REGION_SET // comma delimited list
        :param image_asset_repository_name: Name of the ECR repository to hold Docker Image assets. You must supply this if you have given a non-standard name to the ECR repository. The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will be replaced with the values of qualifier and the stack's account and region, respectively. Default: - process.env.BSS_IMAGE_ASSET_REPOSITORY_NAME
        :param image_asset_tag_prefix: Override the tag of the Docker Image assets. Default: - process.env.BSS_IMAGE_ASSET_TAG_PREFIX
        :param template_bucket_name: Override the name of the S3 bucket to hold Cloudformation template. Default: - process.env.BSS_TEMPLATE_BUCKET_NAME
        '''
        props = BootstraplessStackSynthesizerProps(
            file_asset_bucket_name=file_asset_bucket_name,
            file_asset_prefix=file_asset_prefix,
            file_asset_publishing_role_arn=file_asset_publishing_role_arn,
            file_asset_region_set=file_asset_region_set,
            image_asset_account_id=image_asset_account_id,
            image_asset_publishing_role_arn=image_asset_publishing_role_arn,
            image_asset_region_set=image_asset_region_set,
            image_asset_repository_name=image_asset_repository_name,
            image_asset_tag_prefix=image_asset_tag_prefix,
            template_bucket_name=template_bucket_name,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addDockerImageAsset")
    def add_docker_image_asset(
        self,
        *,
        source_hash: builtins.str,
        directory_name: typing.Optional[builtins.str] = None,
        docker_build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_target: typing.Optional[builtins.str] = None,
        docker_file: typing.Optional[builtins.str] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> aws_cdk.DockerImageAssetLocation:
        '''Register a Docker Image Asset.

        Returns the parameters that can be used to refer to the asset inside the template.

        :param source_hash: The hash of the contents of the docker build context. This hash is used throughout the system to identify this image and avoid duplicate work in case the source did not change. NOTE: this means that if you wish to update your docker image, you must make a modification to the source (e.g. add some metadata to your Dockerfile).
        :param directory_name: The directory where the Dockerfile is stored, must be relative to the cloud assembly root. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        :param docker_build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Only allowed when ``directoryName`` is specified. Default: - no build args are passed
        :param docker_build_target: Docker target to build to. Only allowed when ``directoryName`` is specified. Default: - no target
        :param docker_file: Path to the Dockerfile (relative to the directory). Only allowed when ``directoryName`` is specified. Default: - no file
        :param executable: An external command that will produce the packaged asset. The command should produce the name of a local Docker image on ``stdout``. Default: - Exactly one of ``directoryName`` and ``executable`` is required
        '''
        asset = aws_cdk.DockerImageAssetSource(
            source_hash=source_hash,
            directory_name=directory_name,
            docker_build_args=docker_build_args,
            docker_build_target=docker_build_target,
            docker_file=docker_file,
            executable=executable,
        )

        return typing.cast(aws_cdk.DockerImageAssetLocation, jsii.invoke(self, "addDockerImageAsset", [asset]))

    @jsii.member(jsii_name="addFileAsset")
    def add_file_asset(
        self,
        *,
        source_hash: builtins.str,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        file_name: typing.Optional[builtins.str] = None,
        packaging: typing.Optional[aws_cdk.FileAssetPackaging] = None,
    ) -> aws_cdk.FileAssetLocation:
        '''Register a File Asset.

        Returns the parameters that can be used to refer to the asset inside the template.

        :param source_hash: A hash on the content source. This hash is used to uniquely identify this asset throughout the system. If this value doesn't change, the asset will not be rebuilt or republished.
        :param executable: An external command that will produce the packaged asset. The command should produce the location of a ZIP file on ``stdout``. Default: - Exactly one of ``directory`` and ``executable`` is required
        :param file_name: The path, relative to the root of the cloud assembly, in which this asset source resides. This can be a path to a file or a directory, depending on the packaging type. Default: - Exactly one of ``directory`` and ``executable`` is required
        :param packaging: Which type of packaging to perform. Default: - Required if ``fileName`` is specified.
        '''
        asset = aws_cdk.FileAssetSource(
            source_hash=source_hash,
            executable=executable,
            file_name=file_name,
            packaging=packaging,
        )

        return typing.cast(aws_cdk.FileAssetLocation, jsii.invoke(self, "addFileAsset", [asset]))

    @jsii.member(jsii_name="bind")
    def bind(self, stack: aws_cdk.Stack) -> None:
        '''Bind to the stack this environment is going to be used on.

        Must be called before any of the other methods are called.

        :param stack: -
        '''
        return typing.cast(None, jsii.invoke(self, "bind", [stack]))

    @jsii.member(jsii_name="dumps")
    def dumps(self) -> builtins.str:
        '''Dumps current manifest into JSON format.'''
        return typing.cast(builtins.str, jsii.invoke(self, "dumps", []))

    @jsii.member(jsii_name="synthesize")
    def synthesize(self, session: aws_cdk.ISynthesisSession) -> None:
        '''Synthesize the associated stack to the session.

        :param session: -
        '''
        return typing.cast(None, jsii.invoke(self, "synthesize", [session]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stack")
    def _stack(self) -> typing.Optional[aws_cdk.Stack]:
        return typing.cast(typing.Optional[aws_cdk.Stack], jsii.get(self, "stack"))


@jsii.data_type(
    jsii_type="cdk-bootstrapless-synthesizer.BootstraplessStackSynthesizerProps",
    jsii_struct_bases=[],
    name_mapping={
        "file_asset_bucket_name": "fileAssetBucketName",
        "file_asset_prefix": "fileAssetPrefix",
        "file_asset_publishing_role_arn": "fileAssetPublishingRoleArn",
        "file_asset_region_set": "fileAssetRegionSet",
        "image_asset_account_id": "imageAssetAccountId",
        "image_asset_publishing_role_arn": "imageAssetPublishingRoleArn",
        "image_asset_region_set": "imageAssetRegionSet",
        "image_asset_repository_name": "imageAssetRepositoryName",
        "image_asset_tag_prefix": "imageAssetTagPrefix",
        "template_bucket_name": "templateBucketName",
    },
)
class BootstraplessStackSynthesizerProps:
    def __init__(
        self,
        *,
        file_asset_bucket_name: typing.Optional[builtins.str] = None,
        file_asset_prefix: typing.Optional[builtins.str] = None,
        file_asset_publishing_role_arn: typing.Optional[builtins.str] = None,
        file_asset_region_set: typing.Optional[typing.Sequence[builtins.str]] = None,
        image_asset_account_id: typing.Optional[builtins.str] = None,
        image_asset_publishing_role_arn: typing.Optional[builtins.str] = None,
        image_asset_region_set: typing.Optional[typing.Sequence[builtins.str]] = None,
        image_asset_repository_name: typing.Optional[builtins.str] = None,
        image_asset_tag_prefix: typing.Optional[builtins.str] = None,
        template_bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configuration properties for BootstraplessStackSynthesizer.

        :param file_asset_bucket_name: Name of the S3 bucket to hold file assets. You must supply this if you have given a non-standard name to the staging bucket. The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will be replaced with the values of qualifier and the stack's account and region, respectively. Default: - process.env.BSS_FILE_ASSET_BUCKET_NAME
        :param file_asset_prefix: Object key prefix to use while storing S3 Assets. Default: - process.env.BSS_FILE_ASSET_PREFIX
        :param file_asset_publishing_role_arn: The role to use to publish file assets to the S3 bucket in this environment. You must supply this if you have given a non-standard name to the publishing role. The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will be replaced with the values of qualifier and the stack's account and region, respectively. Default: - process.env.BSS_FILE_ASSET_PUBLISHING_ROLE_ARN
        :param file_asset_region_set: The regions set of file assets to be published only when ``fileAssetBucketName`` contains ``${AWS::Region}``. For examples: ``['us-east-1', 'us-west-1']`` Default: - process.env.BSS_FILE_ASSET_REGION_SET // comma delimited list
        :param image_asset_account_id: Override the ECR repository account id of the Docker Image assets. Default: - process.env.BSS_IMAGE_ASSET_ACCOUNT_ID
        :param image_asset_publishing_role_arn: The role to use to publish image assets to the ECR repository in this environment. You must supply this if you have given a non-standard name to the publishing role. The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will be replaced with the values of qualifier and the stack's account and region, respectively. Default: - process.env.BSS_IMAGE_ASSET_PUBLISHING_ROLE_ARN
        :param image_asset_region_set: Override the ECR repository region of the Docker Image assets. For examples: ``['us-east-1', 'us-west-1']`` Default: - process.env.BSS_IMAGE_ASSET_REGION_SET // comma delimited list
        :param image_asset_repository_name: Name of the ECR repository to hold Docker Image assets. You must supply this if you have given a non-standard name to the ECR repository. The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will be replaced with the values of qualifier and the stack's account and region, respectively. Default: - process.env.BSS_IMAGE_ASSET_REPOSITORY_NAME
        :param image_asset_tag_prefix: Override the tag of the Docker Image assets. Default: - process.env.BSS_IMAGE_ASSET_TAG_PREFIX
        :param template_bucket_name: Override the name of the S3 bucket to hold Cloudformation template. Default: - process.env.BSS_TEMPLATE_BUCKET_NAME
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if file_asset_bucket_name is not None:
            self._values["file_asset_bucket_name"] = file_asset_bucket_name
        if file_asset_prefix is not None:
            self._values["file_asset_prefix"] = file_asset_prefix
        if file_asset_publishing_role_arn is not None:
            self._values["file_asset_publishing_role_arn"] = file_asset_publishing_role_arn
        if file_asset_region_set is not None:
            self._values["file_asset_region_set"] = file_asset_region_set
        if image_asset_account_id is not None:
            self._values["image_asset_account_id"] = image_asset_account_id
        if image_asset_publishing_role_arn is not None:
            self._values["image_asset_publishing_role_arn"] = image_asset_publishing_role_arn
        if image_asset_region_set is not None:
            self._values["image_asset_region_set"] = image_asset_region_set
        if image_asset_repository_name is not None:
            self._values["image_asset_repository_name"] = image_asset_repository_name
        if image_asset_tag_prefix is not None:
            self._values["image_asset_tag_prefix"] = image_asset_tag_prefix
        if template_bucket_name is not None:
            self._values["template_bucket_name"] = template_bucket_name

    @builtins.property
    def file_asset_bucket_name(self) -> typing.Optional[builtins.str]:
        '''Name of the S3 bucket to hold file assets.

        You must supply this if you have given a non-standard name to the staging bucket.

        The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will
        be replaced with the values of qualifier and the stack's account and region,
        respectively.

        :default: - process.env.BSS_FILE_ASSET_BUCKET_NAME

        :required: if you have file assets
        '''
        result = self._values.get("file_asset_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_asset_prefix(self) -> typing.Optional[builtins.str]:
        '''Object key prefix to use while storing S3 Assets.

        :default: - process.env.BSS_FILE_ASSET_PREFIX
        '''
        result = self._values.get("file_asset_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_asset_publishing_role_arn(self) -> typing.Optional[builtins.str]:
        '''The role to use to publish file assets to the S3 bucket in this environment.

        You must supply this if you have given a non-standard name to the publishing role.

        The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will
        be replaced with the values of qualifier and the stack's account and region,
        respectively.

        :default: - process.env.BSS_FILE_ASSET_PUBLISHING_ROLE_ARN
        '''
        result = self._values.get("file_asset_publishing_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_asset_region_set(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The regions set of file assets to be published only when ``fileAssetBucketName`` contains ``${AWS::Region}``.

        For examples:
        ``['us-east-1', 'us-west-1']``

        :default: - process.env.BSS_FILE_ASSET_REGION_SET // comma delimited list
        '''
        result = self._values.get("file_asset_region_set")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def image_asset_account_id(self) -> typing.Optional[builtins.str]:
        '''Override the ECR repository account id of the Docker Image assets.

        :default: - process.env.BSS_IMAGE_ASSET_ACCOUNT_ID
        '''
        result = self._values.get("image_asset_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_asset_publishing_role_arn(self) -> typing.Optional[builtins.str]:
        '''The role to use to publish image assets to the ECR repository in this environment.

        You must supply this if you have given a non-standard name to the publishing role.

        The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will
        be replaced with the values of qualifier and the stack's account and region,
        respectively.

        :default: - process.env.BSS_IMAGE_ASSET_PUBLISHING_ROLE_ARN
        '''
        result = self._values.get("image_asset_publishing_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_asset_region_set(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Override the ECR repository region of the Docker Image assets.

        For examples:
        ``['us-east-1', 'us-west-1']``

        :default: - process.env.BSS_IMAGE_ASSET_REGION_SET // comma delimited list
        '''
        result = self._values.get("image_asset_region_set")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def image_asset_repository_name(self) -> typing.Optional[builtins.str]:
        '''Name of the ECR repository to hold Docker Image assets.

        You must supply this if you have given a non-standard name to the ECR repository.

        The placeholders ``${AWS::AccountId}`` and ``${AWS::Region}`` will
        be replaced with the values of qualifier and the stack's account and region,
        respectively.

        :default: - process.env.BSS_IMAGE_ASSET_REPOSITORY_NAME

        :required: if you have docker image assets
        '''
        result = self._values.get("image_asset_repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_asset_tag_prefix(self) -> typing.Optional[builtins.str]:
        '''Override the tag of the Docker Image assets.

        :default: - process.env.BSS_IMAGE_ASSET_TAG_PREFIX
        '''
        result = self._values.get("image_asset_tag_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template_bucket_name(self) -> typing.Optional[builtins.str]:
        '''Override the name of the S3 bucket to hold Cloudformation template.

        :default: - process.env.BSS_TEMPLATE_BUCKET_NAME
        '''
        result = self._values.get("template_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BootstraplessStackSynthesizerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.IAspect)
class ECRRepositoryAspect(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdk-bootstrapless-synthesizer.ECRRepositoryAspect",
):
    '''Abtract aspect for ECR repository.

    You must provide the account id in props or set BSS_IMAGE_ASSET_ACCOUNT_ID in env
    '''

    def __init__(
        self,
        *,
        image_asset_account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image_asset_account_id: Override the ECR repository account id of the Docker Image assets. Default: - process.env.BSS_IMAGE_ASSET_ACCOUNT_ID
        '''
        props = ECRRepositoryAspectProps(image_asset_account_id=image_asset_account_id)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="crossAccountECRPolicy")
    def _cross_account_ecr_policy(
        self,
        stack: aws_cdk.Stack,
        repo_name: builtins.str,
    ) -> aws_cdk.aws_iam.Policy:
        '''
        :param stack: -
        :param repo_name: -
        '''
        return typing.cast(aws_cdk.aws_iam.Policy, jsii.invoke(self, "crossAccountECRPolicy", [stack, repo_name]))

    @jsii.member(jsii_name="getRepoName")
    def _get_repo_name(self, image_uri: builtins.str) -> typing.Optional[builtins.str]:
        '''
        :param image_uri: -
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "getRepoName", [image_uri]))

    @jsii.member(jsii_name="visit") # type: ignore[misc]
    @abc.abstractmethod
    def visit(self, construct: constructs.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param construct: -
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="account")
    def account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "account"))


class _ECRRepositoryAspectProxy(ECRRepositoryAspect):
    @jsii.member(jsii_name="visit")
    def visit(self, construct: constructs.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param construct: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [construct]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ECRRepositoryAspect).__jsii_proxy_class__ = lambda : _ECRRepositoryAspectProxy


@jsii.data_type(
    jsii_type="cdk-bootstrapless-synthesizer.ECRRepositoryAspectProps",
    jsii_struct_bases=[],
    name_mapping={"image_asset_account_id": "imageAssetAccountId"},
)
class ECRRepositoryAspectProps:
    def __init__(
        self,
        *,
        image_asset_account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configuration properties for ECRRepositoryAspect.

        :param image_asset_account_id: Override the ECR repository account id of the Docker Image assets. Default: - process.env.BSS_IMAGE_ASSET_ACCOUNT_ID
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if image_asset_account_id is not None:
            self._values["image_asset_account_id"] = image_asset_account_id

    @builtins.property
    def image_asset_account_id(self) -> typing.Optional[builtins.str]:
        '''Override the ECR repository account id of the Docker Image assets.

        :default: - process.env.BSS_IMAGE_ASSET_ACCOUNT_ID
        '''
        result = self._values.get("image_asset_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ECRRepositoryAspectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ECSTaskDefinition(
    ECRRepositoryAspect,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-bootstrapless-synthesizer.ECSTaskDefinition",
):
    '''Process the image assets in ECS task definition.'''

    def __init__(
        self,
        *,
        image_asset_account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image_asset_account_id: Override the ECR repository account id of the Docker Image assets. Default: - process.env.BSS_IMAGE_ASSET_ACCOUNT_ID
        '''
        props = ECRRepositoryAspectProps(image_asset_account_id=image_asset_account_id)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="hasBeReplaced")
    def _has_be_replaced(
        self,
        *,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        cpu: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.ContainerDependencyProperty, aws_cdk.IResolvable]]]] = None,
        disable_networking: typing.Optional[typing.Union[builtins.bool, aws_cdk.IResolvable]] = None,
        dns_search_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_servers: typing.Optional[typing.Sequence[builtins.str]] = None,
        docker_labels: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        docker_security_options: typing.Optional[typing.Sequence[builtins.str]] = None,
        entry_point: typing.Optional[typing.Sequence[builtins.str]] = None,
        environment: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.KeyValuePairProperty, aws_cdk.IResolvable]]]] = None,
        environment_files: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.EnvironmentFileProperty, aws_cdk.IResolvable]]]] = None,
        essential: typing.Optional[typing.Union[builtins.bool, aws_cdk.IResolvable]] = None,
        extra_hosts: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.HostEntryProperty, aws_cdk.IResolvable]]]] = None,
        firelens_configuration: typing.Optional[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.FirelensConfigurationProperty, aws_cdk.IResolvable]] = None,
        health_check: typing.Optional[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.HealthCheckProperty, aws_cdk.IResolvable]] = None,
        hostname: typing.Optional[builtins.str] = None,
        image: typing.Optional[builtins.str] = None,
        interactive: typing.Optional[typing.Union[builtins.bool, aws_cdk.IResolvable]] = None,
        links: typing.Optional[typing.Sequence[builtins.str]] = None,
        linux_parameters: typing.Optional[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.LinuxParametersProperty, aws_cdk.IResolvable]] = None,
        log_configuration: typing.Optional[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.LogConfigurationProperty, aws_cdk.IResolvable]] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_reservation: typing.Optional[jsii.Number] = None,
        mount_points: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.MountPointProperty, aws_cdk.IResolvable]]]] = None,
        name: typing.Optional[builtins.str] = None,
        port_mappings: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.PortMappingProperty, aws_cdk.IResolvable]]]] = None,
        privileged: typing.Optional[typing.Union[builtins.bool, aws_cdk.IResolvable]] = None,
        pseudo_terminal: typing.Optional[typing.Union[builtins.bool, aws_cdk.IResolvable]] = None,
        readonly_root_filesystem: typing.Optional[typing.Union[builtins.bool, aws_cdk.IResolvable]] = None,
        repository_credentials: typing.Optional[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.RepositoryCredentialsProperty, aws_cdk.IResolvable]] = None,
        resource_requirements: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.ResourceRequirementProperty, aws_cdk.IResolvable]]]] = None,
        secrets: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.SecretProperty, aws_cdk.IResolvable]]]] = None,
        start_timeout: typing.Optional[jsii.Number] = None,
        stop_timeout: typing.Optional[jsii.Number] = None,
        system_controls: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.SystemControlProperty, aws_cdk.IResolvable]]]] = None,
        ulimits: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.UlimitProperty, aws_cdk.IResolvable]]]] = None,
        user: typing.Optional[builtins.str] = None,
        volumes_from: typing.Optional[typing.Union[aws_cdk.IResolvable, typing.Sequence[typing.Union[aws_cdk.aws_ecs.CfnTaskDefinition.VolumeFromProperty, aws_cdk.IResolvable]]]] = None,
        working_directory: typing.Optional[builtins.str] = None,
    ) -> typing.Optional[builtins.str]:
        '''
        :param command: The command that's passed to the container. This parameter maps to ``Cmd`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``COMMAND`` parameter to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . For more information, see `https://docs.docker.com/engine/reference/builder/#cmd <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/builder/#cmd>`_ . If there are multiple arguments, each argument is a separated string in the array.
        :param cpu: The number of ``cpu`` units reserved for the container. This parameter maps to ``CpuShares`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--cpu-shares`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . This field is optional for tasks using the Fargate launch type, and the only requirement is that the total amount of CPU reserved for all containers within a task be lower than the task-level ``cpu`` value. .. epigraph:: You can determine the number of CPU units that are available per EC2 instance type by multiplying the vCPUs listed for that instance type on the `Amazon EC2 Instances <https://docs.aws.amazon.com/ec2/instance-types/>`_ detail page by 1,024. Linux containers share unallocated CPU units with other containers on the container instance with the same ratio as their allocated amount. For example, if you run a single-container task on a single-core instance type with 512 CPU units specified for that container, and that's the only task running on the container instance, that container could use the full 1,024 CPU unit share at any given time. However, if you launched another copy of the same task on that container instance, each task is guaranteed a minimum of 512 CPU units when needed. Moreover, each container could float to higher CPU usage if the other container was not using it. If both tasks were 100% active all of the time, they would be limited to 512 CPU units. On Linux container instances, the Docker daemon on the container instance uses the CPU value to calculate the relative CPU share ratios for running containers. For more information, see `CPU share constraint <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#cpu-share-constraint>`_ in the Docker documentation. The minimum valid CPU share value that the Linux kernel allows is 2. However, the CPU parameter isn't required, and you can use CPU values below 2 in your container definitions. For CPU values below 2 (including null), the behavior varies based on your Amazon ECS container agent version: - *Agent versions less than or equal to 1.1.0:* Null and zero CPU values are passed to Docker as 0, which Docker then converts to 1,024 CPU shares. CPU values of 1 are passed to Docker as 1, which the Linux kernel converts to two CPU shares. - *Agent versions greater than or equal to 1.2.0:* Null, zero, and CPU values of 1 are passed to Docker as 2. On Windows container instances, the CPU limit is enforced as an absolute limit, or a quota. Windows containers only have access to the specified amount of CPU that's described in the task definition. A null or zero CPU value is passed to Docker as ``0`` , which Windows interprets as 1% of one CPU.
        :param depends_on: The dependencies defined for container startup and shutdown. A container can contain multiple dependencies. When a dependency is defined for container startup, for container shutdown it is reversed. For tasks using the EC2 launch type, the container instances require at least version 1.26.0 of the container agent to enable container dependencies. However, we recommend using the latest container agent version. For information about checking your agent version and updating to the latest version, see `Updating the Amazon ECS Container Agent <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-update.html>`_ in the *Amazon Elastic Container Service Developer Guide* . If you're using an Amazon ECS-optimized Linux AMI, your instance needs at least version 1.26.0-1 of the ``ecs-init`` package. If your container instances are launched from version ``20190301`` or later, then they contain the required versions of the container agent and ``ecs-init`` . For more information, see `Amazon ECS-optimized Linux AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html>`_ in the *Amazon Elastic Container Service Developer Guide* . For tasks using the Fargate launch type, the task or service requires the following platforms: - Linux platform version ``1.3.0`` or later. - Windows platform version ``1.0.0`` or later.
        :param disable_networking: When this parameter is true, networking is disabled within the container. This parameter maps to ``NetworkDisabled`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ . .. epigraph:: This parameter is not supported for Windows containers.
        :param dns_search_domains: A list of DNS search domains that are presented to the container. This parameter maps to ``DnsSearch`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--dns-search`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: This parameter is not supported for Windows containers.
        :param dns_servers: A list of DNS servers that are presented to the container. This parameter maps to ``Dns`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--dns`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: This parameter is not supported for Windows containers.
        :param docker_labels: A key/value map of labels to add to the container. This parameter maps to ``Labels`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--label`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . This parameter requires version 1.18 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log in to your container instance and run the following command: ``sudo docker version --format '{{.Server.APIVersion}}'``
        :param docker_security_options: A list of strings to provide custom labels for SELinux and AppArmor multi-level security systems. This field isn't valid for containers in tasks using the Fargate launch type. With Windows containers, this parameter can be used to reference a credential spec file when configuring a container for Active Directory authentication. For more information, see `Using gMSAs for Windows Containers <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/windows-gmsa.html>`_ in the *Amazon Elastic Container Service Developer Guide* . This parameter maps to ``SecurityOpt`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--security-opt`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: The Amazon ECS container agent running on a container instance must register with the ``ECS_SELINUX_CAPABLE=true`` or ``ECS_APPARMOR_CAPABLE=true`` environment variables before containers placed on that instance can use these security options. For more information, see `Amazon ECS Container Agent Configuration <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-config.html>`_ in the *Amazon Elastic Container Service Developer Guide* . For more information about valid values, see `Docker Run Security Configuration <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . Valid values: "no-new-privileges" | "apparmor:PROFILE" | "label:value" | "credentialspec:CredentialSpecFilePath"
        :param entry_point: .. epigraph:: Early versions of the Amazon ECS container agent don't properly handle ``entryPoint`` parameters. If you have problems using ``entryPoint`` , update your container agent or enter your commands and arguments as ``command`` array items instead. The entry point that's passed to the container. This parameter maps to ``Entrypoint`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--entrypoint`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . For more information, see `https://docs.docker.com/engine/reference/builder/#entrypoint <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/builder/#entrypoint>`_ .
        :param environment: The environment variables to pass to a container. This parameter maps to ``Env`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--env`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: We don't recommend that you use plaintext environment variables for sensitive information, such as credential data.
        :param environment_files: A list of files containing the environment variables to pass to a container. This parameter maps to the ``--env-file`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . You can specify up to ten environment files. The file must have a ``.env`` file extension. Each line in an environment file contains an environment variable in ``VARIABLE=VALUE`` format. Lines beginning with ``#`` are treated as comments and are ignored. For more information about the environment variable file syntax, see `Declare default environment variables in file <https://docs.aws.amazon.com/https://docs.docker.com/compose/env-file/>`_ . If there are environment variables specified using the ``environment`` parameter in a container definition, they take precedence over the variables contained within an environment file. If multiple environment files are specified that contain the same variable, they're processed from the top down. We recommend that you use unique variable names. For more information, see `Specifying Environment Variables <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/taskdef-envfiles.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
        :param essential: If the ``essential`` parameter of a container is marked as ``true`` , and that container fails or stops for any reason, all other containers that are part of the task are stopped. If the ``essential`` parameter of a container is marked as ``false`` , its failure doesn't affect the rest of the containers in a task. If this parameter is omitted, a container is assumed to be essential. All tasks must have at least one essential container. If you have an application that's composed of multiple containers, group containers that are used for a common purpose into components, and separate the different components into multiple task definitions. For more information, see `Application Architecture <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/application_architecture.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
        :param extra_hosts: A list of hostnames and IP address mappings to append to the ``/etc/hosts`` file on the container. This parameter maps to ``ExtraHosts`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--add-host`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: This parameter isn't supported for Windows containers or tasks that use the ``awsvpc`` network mode.
        :param firelens_configuration: The FireLens configuration for the container. This is used to specify and configure a log router for container logs. For more information, see `Custom Log Routing <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_firelens.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
        :param health_check: The container health check command and associated configuration parameters for the container. This parameter maps to ``HealthCheck`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``HEALTHCHECK`` parameter of `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ .
        :param hostname: The hostname to use for your container. This parameter maps to ``Hostname`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--hostname`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: The ``hostname`` parameter is not supported if you're using the ``awsvpc`` network mode.
        :param image: The image used to start a container. This string is passed directly to the Docker daemon. By default, images in the Docker Hub registry are available. Other repositories are specified with either ``*repository-url* / *image* : *tag*`` or ``*repository-url* / *image* @ *digest*`` . Up to 255 letters (uppercase and lowercase), numbers, hyphens, underscores, colons, periods, forward slashes, and number signs are allowed. This parameter maps to ``Image`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``IMAGE`` parameter of `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . - When a new task starts, the Amazon ECS container agent pulls the latest version of the specified image and tag for the container to use. However, subsequent updates to a repository image aren't propagated to already running tasks. - Images in Amazon ECR repositories can be specified by either using the full ``registry/repository:tag`` or ``registry/repository@digest`` . For example, ``012345678910.dkr.ecr.<region-name>.amazonaws.com/<repository-name>:latest`` or ``012345678910.dkr.ecr.<region-name>.amazonaws.com/<repository-name>@sha256:94afd1f2e64d908bc90dbca0035a5b567EXAMPLE`` . - Images in official repositories on Docker Hub use a single name (for example, ``ubuntu`` or ``mongo`` ). - Images in other repositories on Docker Hub are qualified with an organization name (for example, ``amazon/amazon-ecs-agent`` ). - Images in other online repositories are qualified further by a domain name (for example, ``quay.io/assemblyline/ubuntu`` ).
        :param interactive: When this parameter is ``true`` , you can deploy containerized applications that require ``stdin`` or a ``tty`` to be allocated. This parameter maps to ``OpenStdin`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--interactive`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ .
        :param links: The ``links`` parameter allows containers to communicate with each other without the need for port mappings. This parameter is only supported if the network mode of a task definition is ``bridge`` . The ``name:internalName`` construct is analogous to ``name:alias`` in Docker links. Up to 255 letters (uppercase and lowercase), numbers, underscores, and hyphens are allowed. For more information about linking Docker containers, go to `Legacy container links <https://docs.aws.amazon.com/https://docs.docker.com/network/links/>`_ in the Docker documentation. This parameter maps to ``Links`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--link`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: This parameter is not supported for Windows containers. > Containers that are collocated on a single container instance may be able to communicate with each other without requiring links or host port mappings. Network isolation is achieved on the container instance using security groups and VPC settings.
        :param linux_parameters: Linux-specific modifications that are applied to the container, such as Linux kernel capabilities. For more information see `KernelCapabilities <https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_KernelCapabilities.html>`_ . .. epigraph:: This parameter is not supported for Windows containers.
        :param log_configuration: The log configuration specification for the container. This parameter maps to ``LogConfig`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--log-driver`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . By default, containers use the same logging driver that the Docker daemon uses. However, the container may use a different logging driver than the Docker daemon by specifying a log driver with this parameter in the container definition. To use a different logging driver for a container, the log system must be configured properly on the container instance (or on a different log server for remote logging options). For more information on the options for different supported log drivers, see `Configure logging drivers <https://docs.aws.amazon.com/https://docs.docker.com/engine/admin/logging/overview/>`_ in the Docker documentation. .. epigraph:: Amazon ECS currently supports a subset of the logging drivers available to the Docker daemon (shown in the `LogConfiguration <https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_LogConfiguration.html>`_ data type). Additional log drivers may be available in future releases of the Amazon ECS container agent. This parameter requires version 1.18 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log in to your container instance and run the following command: ``sudo docker version --format '{{.Server.APIVersion}}'`` .. epigraph:: The Amazon ECS container agent running on a container instance must register the logging drivers available on that instance with the ``ECS_AVAILABLE_LOGGING_DRIVERS`` environment variable before containers placed on that instance can use these log configuration options. For more information, see `Amazon ECS Container Agent Configuration <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-config.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
        :param memory: The amount (in MiB) of memory to present to the container. If your container attempts to exceed the memory specified here, the container is killed. The total amount of memory reserved for all containers within a task must be lower than the task ``memory`` value, if one is specified. This parameter maps to ``Memory`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--memory`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . If using the Fargate launch type, this parameter is optional. If using the EC2 launch type, you must specify either a task-level memory value or a container-level memory value. If you specify both a container-level ``memory`` and ``memoryReservation`` value, ``memory`` must be greater than ``memoryReservation`` . If you specify ``memoryReservation`` , then that value is subtracted from the available memory resources for the container instance where the container is placed. Otherwise, the value of ``memory`` is used. The Docker 20.10.0 or later daemon reserves a minimum of 6 MiB of memory for a container, so you should not specify fewer than 6 MiB of memory for your containers. The Docker 19.03.13-ce or earlier daemon reserves a minimum of 4 MiB of memory for a container, so you should not specify fewer than 4 MiB of memory for your containers.
        :param memory_reservation: The soft limit (in MiB) of memory to reserve for the container. When system memory is under heavy contention, Docker attempts to keep the container memory to this soft limit. However, your container can consume more memory when it needs to, up to either the hard limit specified with the ``memory`` parameter (if applicable), or all of the available memory on the container instance, whichever comes first. This parameter maps to ``MemoryReservation`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--memory-reservation`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . If a task-level memory value is not specified, you must specify a non-zero integer for one or both of ``memory`` or ``memoryReservation`` in a container definition. If you specify both, ``memory`` must be greater than ``memoryReservation`` . If you specify ``memoryReservation`` , then that value is subtracted from the available memory resources for the container instance where the container is placed. Otherwise, the value of ``memory`` is used. For example, if your container normally uses 128 MiB of memory, but occasionally bursts to 256 MiB of memory for short periods of time, you can set a ``memoryReservation`` of 128 MiB, and a ``memory`` hard limit of 300 MiB. This configuration would allow the container to only reserve 128 MiB of memory from the remaining resources on the container instance, but also allow the container to consume more memory resources when needed. The Docker daemon reserves a minimum of 4 MiB of memory for a container. Therefore, we recommend that you specify fewer than 4 MiB of memory for your containers.
        :param mount_points: The mount points for data volumes in your container. This parameter maps to ``Volumes`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--volume`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . Windows containers can mount whole directories on the same drive as ``$env:ProgramData`` . Windows containers can't mount directories on a different drive, and mount point can't be across drives.
        :param name: The name of a container. If you're linking multiple containers together in a task definition, the ``name`` of one container can be entered in the ``links`` of another container to connect the containers. Up to 255 letters (uppercase and lowercase), numbers, underscores, and hyphens are allowed. This parameter maps to ``name`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--name`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ .
        :param port_mappings: The list of port mappings for the container. Port mappings allow containers to access ports on the host container instance to send or receive traffic. For task definitions that use the ``awsvpc`` network mode, you should only specify the ``containerPort`` . The ``hostPort`` can be left blank or it must be the same value as the ``containerPort`` . Port mappings on Windows use the ``NetNAT`` gateway address rather than ``localhost`` . There is no loopback for port mappings on Windows, so you cannot access a container's mapped port from the host itself. This parameter maps to ``PortBindings`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--publish`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . If the network mode of a task definition is set to ``none`` , then you can't specify port mappings. If the network mode of a task definition is set to ``host`` , then host ports must either be undefined or they must match the container port in the port mapping. .. epigraph:: After a task reaches the ``RUNNING`` status, manual and automatic host and container port assignments are visible in the *Network Bindings* section of a container description for a selected task in the Amazon ECS console. The assignments are also visible in the ``networkBindings`` section `DescribeTasks <https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_DescribeTasks.html>`_ responses.
        :param privileged: When this parameter is true, the container is given elevated privileges on the host container instance (similar to the ``root`` user). This parameter maps to ``Privileged`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--privileged`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: This parameter is not supported for Windows containers or tasks run on AWS Fargate .
        :param pseudo_terminal: When this parameter is ``true`` , a TTY is allocated. This parameter maps to ``Tty`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--tty`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ .
        :param readonly_root_filesystem: When this parameter is true, the container is given read-only access to its root file system. This parameter maps to ``ReadonlyRootfs`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--read-only`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: This parameter is not supported for Windows containers.
        :param repository_credentials: The private repository authentication credentials to use.
        :param resource_requirements: The type and amount of a resource to assign to a container. The only supported resource is a GPU.
        :param secrets: The secrets to pass to the container. For more information, see `Specifying Sensitive Data <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
        :param start_timeout: Time duration (in seconds) to wait before giving up on resolving dependencies for a container. For example, you specify two containers in a task definition with containerA having a dependency on containerB reaching a ``COMPLETE`` , ``SUCCESS`` , or ``HEALTHY`` status. If a ``startTimeout`` value is specified for containerB and it doesn't reach the desired status within that time then containerA gives up and not start. This results in the task transitioning to a ``STOPPED`` state. .. epigraph:: When the ``ECS_CONTAINER_START_TIMEOUT`` container agent configuration variable is used, it's enforced independently from this start timeout value. For tasks using the Fargate launch type, the task or service requires the following platforms: - Linux platform version ``1.3.0`` or later. - Windows platform version ``1.0.0`` or later. For tasks using the EC2 launch type, your container instances require at least version ``1.26.0`` of the container agent to enable a container start timeout value. However, we recommend using the latest container agent version. For information about checking your agent version and updating to the latest version, see `Updating the Amazon ECS Container Agent <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-update.html>`_ in the *Amazon Elastic Container Service Developer Guide* . If you're using an Amazon ECS-optimized Linux AMI, your instance needs at least version ``1.26.0-1`` of the ``ecs-init`` package. If your container instances are launched from version ``20190301`` or later, then they contain the required versions of the container agent and ``ecs-init`` . For more information, see `Amazon ECS-optimized Linux AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
        :param stop_timeout: Time duration (in seconds) to wait before the container is forcefully killed if it doesn't exit normally on its own. For tasks using the Fargate launch type, the task or service requires the following platforms: - Linux platform version ``1.3.0`` or later. - Windows platform version ``1.0.0`` or later. The max stop timeout value is 120 seconds and if the parameter is not specified, the default value of 30 seconds is used. For tasks that use the EC2 launch type, if the ``stopTimeout`` parameter isn't specified, the value set for the Amazon ECS container agent configuration variable ``ECS_CONTAINER_STOP_TIMEOUT`` is used. If neither the ``stopTimeout`` parameter or the ``ECS_CONTAINER_STOP_TIMEOUT`` agent configuration variable are set, then the default values of 30 seconds for Linux containers and 30 seconds on Windows containers are used. Your container instances require at least version 1.26.0 of the container agent to enable a container stop timeout value. However, we recommend using the latest container agent version. For information about checking your agent version and updating to the latest version, see `Updating the Amazon ECS Container Agent <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-agent-update.html>`_ in the *Amazon Elastic Container Service Developer Guide* . If you're using an Amazon ECS-optimized Linux AMI, your instance needs at least version 1.26.0-1 of the ``ecs-init`` package. If your container instances are launched from version ``20190301`` or later, then they contain the required versions of the container agent and ``ecs-init`` . For more information, see `Amazon ECS-optimized Linux AMI <https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-optimized_AMI.html>`_ in the *Amazon Elastic Container Service Developer Guide* .
        :param system_controls: A list of namespaced kernel parameters to set in the container. This parameter maps to ``Sysctls`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--sysctl`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: We don't recommended that you specify network-related ``systemControls`` parameters for multiple containers in a single task that also uses either the ``awsvpc`` or ``host`` network modes. For tasks that use the ``awsvpc`` network mode, the container that's started last determines which ``systemControls`` parameters take effect. For tasks that use the ``host`` network mode, it changes the container instance's namespaced kernel parameters as well as the containers.
        :param ulimits: A list of ``ulimits`` to set in the container. This parameter maps to ``Ulimits`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--ulimit`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/>`_ . Valid naming values are displayed in the `Ulimit <https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_Ulimit.html>`_ data type. This parameter requires version 1.18 of the Docker Remote API or greater on your container instance. To check the Docker Remote API version on your container instance, log in to your container instance and run the following command: ``sudo docker version --format '{{.Server.APIVersion}}'`` .. epigraph:: This parameter is not supported for Windows containers.
        :param user: The user to use inside the container. This parameter maps to ``User`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--user`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ . .. epigraph:: When running tasks using the ``host`` network mode, don't run containers using the root user (UID 0). We recommend using a non-root user for better security. You can specify the ``user`` using the following formats. If specifying a UID or GID, you must specify it as a positive integer. - ``user`` - ``user:group`` - ``uid`` - ``uid:gid`` - ``user:gid`` - ``uid:group`` .. epigraph:: This parameter is not supported for Windows containers.
        :param volumes_from: Data volumes to mount from another container. This parameter maps to ``VolumesFrom`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--volumes-from`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ .
        :param working_directory: The working directory to run commands inside the container in. This parameter maps to ``WorkingDir`` in the `Create a container <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/#operation/ContainerCreate>`_ section of the `Docker Remote API <https://docs.aws.amazon.com/https://docs.docker.com/engine/api/v1.35/>`_ and the ``--workdir`` option to `docker run <https://docs.aws.amazon.com/https://docs.docker.com/engine/reference/run/#security-configuration>`_ .
        '''
        prop = aws_cdk.aws_ecs.CfnTaskDefinition.ContainerDefinitionProperty(
            command=command,
            cpu=cpu,
            depends_on=depends_on,
            disable_networking=disable_networking,
            dns_search_domains=dns_search_domains,
            dns_servers=dns_servers,
            docker_labels=docker_labels,
            docker_security_options=docker_security_options,
            entry_point=entry_point,
            environment=environment,
            environment_files=environment_files,
            essential=essential,
            extra_hosts=extra_hosts,
            firelens_configuration=firelens_configuration,
            health_check=health_check,
            hostname=hostname,
            image=image,
            interactive=interactive,
            links=links,
            linux_parameters=linux_parameters,
            log_configuration=log_configuration,
            memory=memory,
            memory_reservation=memory_reservation,
            mount_points=mount_points,
            name=name,
            port_mappings=port_mappings,
            privileged=privileged,
            pseudo_terminal=pseudo_terminal,
            readonly_root_filesystem=readonly_root_filesystem,
            repository_credentials=repository_credentials,
            resource_requirements=resource_requirements,
            secrets=secrets,
            start_timeout=start_timeout,
            stop_timeout=stop_timeout,
            system_controls=system_controls,
            ulimits=ulimits,
            user=user,
            volumes_from=volumes_from,
            working_directory=working_directory,
        )

        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "hasBeReplaced", [prop]))

    @jsii.member(jsii_name="visit")
    def visit(self, construct: constructs.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param construct: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [construct]))


class StepFunctionsSageMakerTrainingJob(
    ECRRepositoryAspect,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-bootstrapless-synthesizer.StepFunctionsSageMakerTrainingJob",
):
    '''Process the image assets in SageMaker training job in Step Functions.'''

    def __init__(
        self,
        *,
        image_asset_account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image_asset_account_id: Override the ECR repository account id of the Docker Image assets. Default: - process.env.BSS_IMAGE_ASSET_ACCOUNT_ID
        '''
        props = ECRRepositoryAspectProps(image_asset_account_id=image_asset_account_id)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, construct: constructs.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param construct: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [construct]))


class CompositeECRRepositoryAspect(
    ECRRepositoryAspect,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-bootstrapless-synthesizer.CompositeECRRepositoryAspect",
):
    '''Default ECR asset aspect, support using ECR assets in below services,.

    - ECS task definition
    - SageMaker training job in Step Functions
    '''

    def __init__(
        self,
        *,
        image_asset_account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image_asset_account_id: Override the ECR repository account id of the Docker Image assets. Default: - process.env.BSS_IMAGE_ASSET_ACCOUNT_ID
        '''
        props = ECRRepositoryAspectProps(image_asset_account_id=image_asset_account_id)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="visit")
    def visit(self, construct: constructs.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param construct: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [construct]))


__all__ = [
    "BootstraplessStackSynthesizer",
    "BootstraplessStackSynthesizerProps",
    "CompositeECRRepositoryAspect",
    "ECRRepositoryAspect",
    "ECRRepositoryAspectProps",
    "ECSTaskDefinition",
    "StepFunctionsSageMakerTrainingJob",
]

publication.publish()
