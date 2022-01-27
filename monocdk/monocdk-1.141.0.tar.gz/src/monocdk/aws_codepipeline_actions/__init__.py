'''
# AWS CodePipeline Actions

This package contains Actions that can be used in a CodePipeline.

```python
import monocdk as codepipeline
import monocdk as codepipeline_actions
```

## Sources

### AWS CodeCommit

To use a CodeCommit Repository in a CodePipeline:

```python
repo = codecommit.Repository(self, "Repo",
    repository_name="MyRepo"
)

pipeline = codepipeline.Pipeline(self, "MyPipeline",
    pipeline_name="MyPipeline"
)
source_output = codepipeline.Artifact()
source_action = codepipeline_actions.CodeCommitSourceAction(
    action_name="CodeCommit",
    repository=repo,
    output=source_output
)
pipeline.add_stage(
    stage_name="Source",
    actions=[source_action]
)
```

If you want to use existing role which can be used by on commit event rule.
You can specify the role object in eventRole property.

```python
# repo: codecommit.Repository
event_role = iam.Role.from_role_arn(self, "Event-role", "roleArn")
source_action = codepipeline_actions.CodeCommitSourceAction(
    action_name="CodeCommit",
    repository=repo,
    output=codepipeline.Artifact(),
    event_role=event_role
)
```

If you want to clone the entire CodeCommit repository (only available for CodeBuild actions),
you can set the `codeBuildCloneOutput` property to `true`:

```python
# project: codebuild.PipelineProject
# repo: codecommit.Repository

source_output = codepipeline.Artifact()
source_action = codepipeline_actions.CodeCommitSourceAction(
    action_name="CodeCommit",
    repository=repo,
    output=source_output,
    code_build_clone_output=True
)

build_action = codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,  # The build action must use the CodeCommitSourceAction output as input.
    outputs=[codepipeline.Artifact()]
)
```

The CodeCommit source action emits variables:

```python
# project: codebuild.PipelineProject
# repo: codecommit.Repository

source_output = codepipeline.Artifact()
source_action = codepipeline_actions.CodeCommitSourceAction(
    action_name="CodeCommit",
    repository=repo,
    output=source_output,
    variables_namespace="MyNamespace"
)

# later:

codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,
    environment_variables={
        "COMMIT_ID": codebuild.aws_codebuild.BuildEnvironmentVariable(
            value=source_action.variables.commit_id
        )
    }
)
```

### GitHub

If you want to use a GitHub repository as the source, you must create:

* A [GitHub Access Token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line),
  with scopes **repo** and **admin:repo_hook**.
* A [Secrets Manager Secret](https://docs.aws.amazon.com/secretsmanager/latest/userguide/manage_create-basic-secret.html)
  with the value of the **GitHub Access Token**. Pick whatever name you want (for example `my-github-token`).
  This token can be stored either as Plaintext or as a Secret key/value.
  If you stored the token as Plaintext,
  set `SecretValue.secretsManager('my-github-token')` as the value of `oauthToken`.
  If you stored it as a Secret key/value,
  you must set `SecretValue.secretsManager('my-github-token', { jsonField : 'my-github-token' })` as the value of `oauthToken`.

To use GitHub as the source of a CodePipeline:

```python
# Read the secret from Secrets Manager
pipeline = codepipeline.Pipeline(self, "MyPipeline")
source_output = codepipeline.Artifact()
source_action = codepipeline_actions.GitHubSourceAction(
    action_name="GitHub_Source",
    owner="awslabs",
    repo="aws-cdk",
    oauth_token=SecretValue.secrets_manager("my-github-token"),
    output=source_output,
    branch="develop"
)
pipeline.add_stage(
    stage_name="Source",
    actions=[source_action]
)
```

The GitHub source action emits variables:

```python
# source_output: codepipeline.Artifact
# project: codebuild.PipelineProject


source_action = codepipeline_actions.GitHubSourceAction(
    action_name="Github_Source",
    output=source_output,
    owner="my-owner",
    repo="my-repo",
    oauth_token=SecretValue.secrets_manager("my-github-token"),
    variables_namespace="MyNamespace"
)

# later:

codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,
    environment_variables={
        "COMMIT_URL": codebuild.aws_codebuild.BuildEnvironmentVariable(
            value=source_action.variables.commit_url
        )
    }
)
```

### BitBucket

CodePipeline can use a BitBucket Git repository as a source:

**Note**: you have to manually connect CodePipeline through the AWS Console with your BitBucket account.
This is a one-time operation for a given AWS account in a given region.
The simplest way to do that is to either start creating a new CodePipeline,
or edit an existing one, while being logged in to BitBucket.
Choose BitBucket as the source,
and grant CodePipeline permissions to your BitBucket account.
Copy & paste the Connection ARN that you get in the console,
or use the [`codestar-connections list-connections` AWS CLI operation](https://docs.aws.amazon.com/cli/latest/reference/codestar-connections/list-connections.html)
to find it.
After that, you can safely abort creating or editing the pipeline -
the connection has already been created.

```python
source_output = codepipeline.Artifact()
source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
    action_name="BitBucket_Source",
    owner="aws",
    repo="aws-cdk",
    output=source_output,
    connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/12345678-abcd-12ab-34cdef5678gh"
)
```

You can also use the `CodeStarConnectionsSourceAction` to connect to GitHub, in the same way
(you just have to select GitHub as the source when creating the connection in the console).

Similarly to `GitHubSourceAction`, `CodeStarConnectionsSourceAction` also emits the variables:

```python
# project: codebuild.Project


source_output = codepipeline.Artifact()
source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
    action_name="BitBucket_Source",
    owner="aws",
    repo="aws-cdk",
    output=source_output,
    connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/12345678-abcd-12ab-34cdef5678gh",
    variables_namespace="SomeSpace"
)

# later:

codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,
    environment_variables={
        "COMMIT_ID": codebuild.aws_codebuild.BuildEnvironmentVariable(
            value=source_action.variables.commit_id
        )
    }
)
```

### AWS S3 Source

To use an S3 Bucket as a source in CodePipeline:

```python
source_bucket = s3.Bucket(self, "MyBucket",
    versioned=True
)

pipeline = codepipeline.Pipeline(self, "MyPipeline")
source_output = codepipeline.Artifact()
source_action = codepipeline_actions.S3SourceAction(
    action_name="S3Source",
    bucket=source_bucket,
    bucket_key="path/to/file.zip",
    output=source_output
)
pipeline.add_stage(
    stage_name="Source",
    actions=[source_action]
)
```

The region of the action will be determined by the region the bucket itself is in.
When using a newly created bucket,
that region will be taken from the stack the bucket belongs to;
for an imported bucket,
you can specify the region explicitly:

```python
source_bucket = s3.Bucket.from_bucket_attributes(self, "SourceBucket",
    bucket_name="my-bucket",
    region="ap-southeast-1"
)
```

By default, the Pipeline will poll the Bucket to detect changes.
You can change that behavior to use CloudWatch Events by setting the `trigger`
property to `S3Trigger.EVENTS` (it's `S3Trigger.POLL` by default).
If you do that, make sure the source Bucket is part of an AWS CloudTrail Trail -
otherwise, the CloudWatch Events will not be emitted,
and your Pipeline will not react to changes in the Bucket.
You can do it through the CDK:

```python
import monocdk as cloudtrail

# source_bucket: s3.Bucket

source_output = codepipeline.Artifact()
key = "some/key.zip"
trail = cloudtrail.Trail(self, "CloudTrail")
trail.add_s3_event_selector([cloudtrail.aws_cloudtrail.S3EventSelector(
    bucket=source_bucket,
    object_prefix=key
)],
    read_write_type=cloudtrail.ReadWriteType.WRITE_ONLY
)
source_action = codepipeline_actions.S3SourceAction(
    action_name="S3Source",
    bucket_key=key,
    bucket=source_bucket,
    output=source_output,
    trigger=codepipeline_actions.S3Trigger.EVENTS
)
```

The S3 source action emits variables:

```python
# source_bucket: s3.Bucket

# later:
# project: codebuild.PipelineProject
key = "some/key.zip"
source_output = codepipeline.Artifact()
source_action = codepipeline_actions.S3SourceAction(
    action_name="S3Source",
    bucket_key=key,
    bucket=source_bucket,
    output=source_output,
    variables_namespace="MyNamespace"
)
codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,
    environment_variables={
        "VERSION_ID": codebuild.aws_codebuild.BuildEnvironmentVariable(
            value=source_action.variables.version_id
        )
    }
)
```

### AWS ECR

To use an ECR Repository as a source in a Pipeline:

```python
import monocdk as ecr

# ecr_repository: ecr.Repository

pipeline = codepipeline.Pipeline(self, "MyPipeline")
source_output = codepipeline.Artifact()
source_action = codepipeline_actions.EcrSourceAction(
    action_name="ECR",
    repository=ecr_repository,
    image_tag="some-tag",  # optional, default: 'latest'
    output=source_output
)
pipeline.add_stage(
    stage_name="Source",
    actions=[source_action]
)
```

The ECR source action emits variables:

```python
import monocdk as ecr
# ecr_repository: ecr.Repository

# later:
# project: codebuild.PipelineProject


source_output = codepipeline.Artifact()
source_action = codepipeline_actions.EcrSourceAction(
    action_name="Source",
    output=source_output,
    repository=ecr_repository,
    variables_namespace="MyNamespace"
)
codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,
    environment_variables={
        "IMAGE_URI": ecr.aws_codebuild.BuildEnvironmentVariable(
            value=source_action.variables.image_uri
        )
    }
)
```

## Build & test

### AWS CodeBuild

Example of a CodeBuild Project used in a Pipeline, alongside CodeCommit:

```python
# project: codebuild.PipelineProject

repository = codecommit.Repository(self, "MyRepository",
    repository_name="MyRepository"
)
project = codebuild.PipelineProject(self, "MyProject")

source_output = codepipeline.Artifact()
source_action = codepipeline_actions.CodeCommitSourceAction(
    action_name="CodeCommit",
    repository=repository,
    output=source_output
)
build_action = codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,
    outputs=[codepipeline.Artifact()],  # optional
    execute_batch_build=True,  # optional, defaults to false
    combine_batch_build_artifacts=True
)

codepipeline.Pipeline(self, "MyPipeline",
    stages=[codebuild.aws_codepipeline.StageProps(
        stage_name="Source",
        actions=[source_action]
    ), codebuild.aws_codepipeline.StageProps(
        stage_name="Build",
        actions=[build_action]
    )
    ]
)
```

The default category of the CodeBuild Action is `Build`;
if you want a `Test` Action instead,
override the `type` property:

```python
# project: codebuild.PipelineProject

source_output = codepipeline.Artifact()
test_action = codepipeline_actions.CodeBuildAction(
    action_name="IntegrationTest",
    project=project,
    input=source_output,
    type=codepipeline_actions.CodeBuildActionType.TEST
)
```

#### Multiple inputs and outputs

When you want to have multiple inputs and/or outputs for a Project used in a
Pipeline, instead of using the `secondarySources` and `secondaryArtifacts`
properties of the `Project` class, you need to use the `extraInputs` and
`outputs` properties of the CodeBuild CodePipeline
Actions. Example:

```python
# repository1: codecommit.Repository
# repository2: codecommit.Repository

# project: codebuild.PipelineProject

source_output1 = codepipeline.Artifact()
source_action1 = codepipeline_actions.CodeCommitSourceAction(
    action_name="Source1",
    repository=repository1,
    output=source_output1
)
source_output2 = codepipeline.Artifact("source2")
source_action2 = codepipeline_actions.CodeCommitSourceAction(
    action_name="Source2",
    repository=repository2,
    output=source_output2
)
build_action = codepipeline_actions.CodeBuildAction(
    action_name="Build",
    project=project,
    input=source_output1,
    extra_inputs=[source_output2
    ],
    outputs=[
        codepipeline.Artifact("artifact1"),  # for better buildspec readability - see below
        codepipeline.Artifact("artifact2")
    ]
)
```

**Note**: when a CodeBuild Action in a Pipeline has more than one output, it
only uses the `secondary-artifacts` field of the buildspec, never the
primary output specification directly under `artifacts`. Because of that, it
pays to explicitly name all output artifacts of that Action, like we did
above, so that you know what name to use in the buildspec.

Example buildspec for the above project:

```python
project = codebuild.PipelineProject(self, "MyProject",
    build_spec=codebuild.BuildSpec.from_object({
        "version": "0.2",
        "phases": {
            "build": {
                "commands": []
            }
        },
        "artifacts": {
            "secondary-artifacts": {
                "artifact1": {},
                "artifact2": {}
            }
        }
    })
)
```

#### Variables

The CodeBuild action emits variables.
Unlike many other actions, the variables are not static,
but dynamic, defined in the buildspec,
in the 'exported-variables' subsection of the 'env' section.
Example:

```python
# later:
# project: codebuild.PipelineProject
source_output = codepipeline.Artifact()
build_action = codepipeline_actions.CodeBuildAction(
    action_name="Build1",
    input=source_output,
    project=codebuild.PipelineProject(self, "Project",
        build_spec=codebuild.BuildSpec.from_object({
            "version": "0.2",
            "env": {
                "exported-variables": ["MY_VAR"
                ]
            },
            "phases": {
                "build": {
                    "commands": "export MY_VAR=\"some value\""
                }
            }
        })
    ),
    variables_namespace="MyNamespace"
)
codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,
    environment_variables={
        "MyVar": codebuild.aws_codebuild.BuildEnvironmentVariable(
            value=build_action.variable("MY_VAR")
        )
    }
)
```

### Jenkins

In order to use Jenkins Actions in the Pipeline,
you first need to create a `JenkinsProvider`:

```python
jenkins_provider = codepipeline_actions.JenkinsProvider(self, "JenkinsProvider",
    provider_name="MyJenkinsProvider",
    server_url="http://my-jenkins.com:8080",
    version="2"
)
```

If you've registered a Jenkins provider in a different CDK app,
or outside the CDK (in the CodePipeline AWS Console, for example),
you can import it:

```python
jenkins_provider = codepipeline_actions.JenkinsProvider.from_jenkins_provider_attributes(self, "JenkinsProvider",
    provider_name="MyJenkinsProvider",
    server_url="http://my-jenkins.com:8080",
    version="2"
)
```

Note that a Jenkins provider
(identified by the provider name-category(build/test)-version tuple)
must always be registered in the given account, in the given AWS region,
before it can be used in CodePipeline.

With a `JenkinsProvider`,
we can create a Jenkins Action:

```python
# jenkins_provider: codepipeline_actions.JenkinsProvider

build_action = codepipeline_actions.JenkinsAction(
    action_name="JenkinsBuild",
    jenkins_provider=jenkins_provider,
    project_name="MyProject",
    type=codepipeline_actions.JenkinsActionType.BUILD
)
```

## Deploy

### AWS CloudFormation

This module contains Actions that allows you to deploy to CloudFormation from AWS CodePipeline.

For example, the following code fragment defines a pipeline that automatically deploys a CloudFormation template
directly from a CodeCommit repository, with a manual approval step in between to confirm the changes:

[example Pipeline to deploy CloudFormation](test/integ.cfn-template-from-repo.lit.ts)

See [the AWS documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline.html)
for more details about using CloudFormation in CodePipeline.

#### Actions defined by this package

This package contains the following CloudFormation actions:

* **CloudFormationCreateUpdateStackAction** - Deploy a CloudFormation template directly from the pipeline. The indicated stack is created,
  or updated if it already exists. If the stack is in a failure state, deployment will fail (unless `replaceOnFailure`
  is set to `true`, in which case it will be destroyed and recreated).
* **CloudFormationDeleteStackAction** - Delete the stack with the given name.
* **CloudFormationCreateReplaceChangeSetAction** - Prepare a change set to be applied later. You will typically use change sets if you want
  to manually verify the changes that are being staged, or if you want to separate the people (or system) preparing the
  changes from the people (or system) applying the changes.
* **CloudFormationExecuteChangeSetAction** - Execute a change set prepared previously.

#### Lambda deployed through CodePipeline

If you want to deploy your Lambda through CodePipeline,
and you don't use assets (for example, because your CDK code and Lambda code are separate),
you can use a special Lambda `Code` class, `CfnParametersCode`.
Note that your Lambda must be in a different Stack than your Pipeline.
The Lambda itself will be deployed, alongside the entire Stack it belongs to,
using a CloudFormation CodePipeline Action. Example:

[Example of deploying a Lambda through CodePipeline](test/integ.lambda-deployed-through-codepipeline.lit.ts)

#### Cross-account actions

If you want to update stacks in a different account,
pass the `account` property when creating the action:

```python
source_output = codepipeline.Artifact()
codepipeline_actions.CloudFormationCreateUpdateStackAction(
    action_name="CloudFormationCreateUpdate",
    stack_name="MyStackName",
    admin_permissions=True,
    template_path=source_output.at_path("template.yaml"),
    account="123456789012"
)
```

This will create a new stack, called `<PipelineStackName>-support-123456789012`, in your `App`,
that will contain the role that the pipeline will assume in account 123456789012 before executing this action.
This support stack will automatically be deployed before the stack containing the pipeline.

You can also pass a role explicitly when creating the action -
in that case, the `account` property is ignored,
and the action will operate in the same account the role belongs to:

```python
from monocdk import PhysicalName

# in stack for account 123456789012...
# other_account_stack: Stack

action_role = iam.Role(other_account_stack, "ActionRole",
    assumed_by=iam.AccountPrincipal("123456789012"),
    # the role has to have a physical name set
    role_name=PhysicalName.GENERATE_IF_NEEDED
)

# in the pipeline stack...
source_output = codepipeline.Artifact()
codepipeline_actions.CloudFormationCreateUpdateStackAction(
    action_name="CloudFormationCreateUpdate",
    stack_name="MyStackName",
    admin_permissions=True,
    template_path=source_output.at_path("template.yaml"),
    role=action_role
)
```

### AWS CodeDeploy

#### Server deployments

To use CodeDeploy for EC2/on-premise deployments in a Pipeline:

```python
# deployment_group: codedeploy.ServerDeploymentGroup
pipeline = codepipeline.Pipeline(self, "MyPipeline",
    pipeline_name="MyPipeline"
)

# add the source and build Stages to the Pipeline...
build_output = codepipeline.Artifact()
deploy_action = codepipeline_actions.CodeDeployServerDeployAction(
    action_name="CodeDeploy",
    input=build_output,
    deployment_group=deployment_group
)
pipeline.add_stage(
    stage_name="Deploy",
    actions=[deploy_action]
)
```

##### Lambda deployments

To use CodeDeploy for blue-green Lambda deployments in a Pipeline:

```python
lambda_code = lambda_.Code.from_cfn_parameters()
func = lambda_.Function(self, "Lambda",
    code=lambda_code,
    handler="index.handler",
    runtime=lambda_.Runtime.NODEJS_12_X
)
# used to make sure each CDK synthesis produces a different Version
version = func.add_version("NewVersion")
alias = lambda_.Alias(self, "LambdaAlias",
    alias_name="Prod",
    version=version
)

codedeploy.LambdaDeploymentGroup(self, "DeploymentGroup",
    alias=alias,
    deployment_config=codedeploy.LambdaDeploymentConfig.LINEAR_10PERCENT_EVERY_1MINUTE
)
```

Then, you need to create your Pipeline Stack,
where you will define your Pipeline,
and deploy the `lambdaStack` using a CloudFormation CodePipeline Action
(see above for a complete example).

### ECS

CodePipeline can deploy an ECS service.
The deploy Action receives one input Artifact which contains the [image definition file](https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-create.html#pipelines-create-image-definitions):

```python
import monocdk as ecs

# service: ecs.FargateService

pipeline = codepipeline.Pipeline(self, "MyPipeline")
build_output = codepipeline.Artifact()
deploy_stage = pipeline.add_stage(
    stage_name="Deploy",
    actions=[
        codepipeline_actions.EcsDeployAction(
            action_name="DeployAction",
            service=service,
            # if your file is called imagedefinitions.json,
            # use the `input` property,
            # and leave out the `imageFile` property
            input=build_output,
            # if your file name is _not_ imagedefinitions.json,
            # use the `imageFile` property,
            # and leave out the `input` property
            image_file=build_output.at_path("imageDef.json"),
            deployment_timeout=Duration.minutes(60)
        )
    ]
)
```

#### Deploying ECS applications to existing services

CodePipeline can deploy to an existing ECS service which uses the
[ECS service ARN format that contains the Cluster name](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-account-settings.html#ecs-resource-ids).
This also works if the service is in a different account and/or region than the pipeline:

```python
import monocdk as ecs


service = ecs.BaseService.from_service_arn_with_cluster(self, "EcsService", "arn:aws:ecs:us-east-1:123456789012:service/myClusterName/myServiceName")
pipeline = codepipeline.Pipeline(self, "MyPipeline")
build_output = codepipeline.Artifact()
# add source and build stages to the pipeline as usual...
deploy_stage = pipeline.add_stage(
    stage_name="Deploy",
    actions=[
        codepipeline_actions.EcsDeployAction(
            action_name="DeployAction",
            service=service,
            input=build_output
        )
    ]
)
```

When deploying across accounts, especially in a CDK Pipelines self-mutating pipeline,
it is recommended to provide the `role` property to the `EcsDeployAction`.
The Role will need to have permissions assigned to it for ECS deployment.
See [the CodePipeline documentation](https://docs.aws.amazon.com/codepipeline/latest/userguide/how-to-custom-role.html#how-to-update-role-new-services)
for the permissions needed.

#### Deploying ECS applications stored in a separate source code repository

The idiomatic CDK way of deploying an ECS application is to have your Dockerfiles and your CDK code in the same source code repository,
leveraging [Docker Assets](https://docs.aws.amazon.com/cdk/latest/guide/assets.html#assets_types_docker),
and use the [CDK Pipelines module](https://docs.aws.amazon.com/cdk/api/latest/docs/pipelines-readme.html).

However, if you want to deploy a Docker application whose source code is kept in a separate version control repository than the CDK code,
you can use the `TagParameterContainerImage` class from the ECS module.
Here's an example:

[example ECS pipeline for an application in a separate source code repository](test/integ.pipeline-ecs-separate-source.lit.ts)

### AWS S3 Deployment

To use an S3 Bucket as a deployment target in CodePipeline:

```python
source_output = codepipeline.Artifact()
target_bucket = s3.Bucket(self, "MyBucket")

pipeline = codepipeline.Pipeline(self, "MyPipeline")
deploy_action = codepipeline_actions.S3DeployAction(
    action_name="S3Deploy",
    bucket=target_bucket,
    input=source_output
)
deploy_stage = pipeline.add_stage(
    stage_name="Deploy",
    actions=[deploy_action]
)
```

#### Invalidating the CloudFront cache when deploying to S3

There is currently no native support in CodePipeline for invalidating a CloudFront cache after deployment.
One workaround is to add another build step after the deploy step,
and use the AWS CLI to invalidate the cache:

```python
# Create a Cloudfront Web Distribution
import monocdk as cloudfront
# distribution: cloudfront.Distribution


# Create the build project that will invalidate the cache
invalidate_build_project = codebuild.PipelineProject(self, "InvalidateProject",
    build_spec=codebuild.BuildSpec.from_object({
        "version": "0.2",
        "phases": {
            "build": {
                "commands": ["aws cloudfront create-invalidation --distribution-id ${CLOUDFRONT_ID} --paths \"/*\""
                ]
            }
        }
    }),
    environment_variables={
        "CLOUDFRONT_ID": cloudfront.aws_codebuild.BuildEnvironmentVariable(value=distribution.distribution_id)
    }
)

# Add Cloudfront invalidation permissions to the project
distribution_arn = f"arn:aws:cloudfront::{this.account}:distribution/{distribution.distributionId}"
invalidate_build_project.add_to_role_policy(iam.PolicyStatement(
    resources=[distribution_arn],
    actions=["cloudfront:CreateInvalidation"
    ]
))

# Create the pipeline (here only the S3 deploy and Invalidate cache build)
deploy_bucket = s3.Bucket(self, "DeployBucket")
deploy_input = codepipeline.Artifact()
codepipeline.Pipeline(self, "Pipeline",
    stages=[cloudfront.aws_codepipeline.StageProps(
        stage_name="Deploy",
        actions=[
            codepipeline_actions.S3DeployAction(
                action_name="S3Deploy",
                bucket=deploy_bucket,
                input=deploy_input,
                run_order=1
            ),
            codepipeline_actions.CodeBuildAction(
                action_name="InvalidateCache",
                project=invalidate_build_project,
                input=deploy_input,
                run_order=2
            )
        ]
    )
    ]
)
```

### Alexa Skill

You can deploy to Alexa using CodePipeline with the following Action:

```python
# Read the secrets from ParameterStore
client_id = SecretValue.secrets_manager("AlexaClientId")
client_secret = SecretValue.secrets_manager("AlexaClientSecret")
refresh_token = SecretValue.secrets_manager("AlexaRefreshToken")

# Add deploy action
source_output = codepipeline.Artifact()
codepipeline_actions.AlexaSkillDeployAction(
    action_name="DeploySkill",
    run_order=1,
    input=source_output,
    client_id=client_id.to_string(),
    client_secret=client_secret,
    refresh_token=refresh_token,
    skill_id="amzn1.ask.skill.12345678-1234-1234-1234-123456789012"
)
```

If you need manifest overrides you can specify them as `parameterOverridesArtifact` in the action:

```python
# Deploy some CFN change set and store output
execute_output = codepipeline.Artifact("CloudFormation")
execute_change_set_action = codepipeline_actions.CloudFormationExecuteChangeSetAction(
    action_name="ExecuteChangesTest",
    run_order=2,
    stack_name="MyStack",
    change_set_name="MyChangeSet",
    output_file_name="overrides.json",
    output=execute_output
)

# Provide CFN output as manifest overrides
client_id = SecretValue.secrets_manager("AlexaClientId")
client_secret = SecretValue.secrets_manager("AlexaClientSecret")
refresh_token = SecretValue.secrets_manager("AlexaRefreshToken")
source_output = codepipeline.Artifact()
codepipeline_actions.AlexaSkillDeployAction(
    action_name="DeploySkill",
    run_order=1,
    input=source_output,
    parameter_overrides_artifact=execute_output,
    client_id=client_id.to_string(),
    client_secret=client_secret,
    refresh_token=refresh_token,
    skill_id="amzn1.ask.skill.12345678-1234-1234-1234-123456789012"
)
```

### AWS Service Catalog

You can deploy a CloudFormation template to an existing Service Catalog product with the following Action:

```python
cdk_build_output = codepipeline.Artifact()
service_catalog_deploy_action = codepipeline_actions.ServiceCatalogDeployActionBeta1(
    action_name="ServiceCatalogDeploy",
    template_path=cdk_build_output.at_path("Sample.template.json"),
    product_version_name="Version - " + Date.now.to_string,
    product_version_description="This is a version from the pipeline with a new description.",
    product_id="prod-XXXXXXXX"
)
```

## Approve & invoke

### Manual approval Action

This package contains an Action that stops the Pipeline until someone manually clicks the approve button:

```python
import monocdk as sns


pipeline = codepipeline.Pipeline(self, "MyPipeline")
approve_stage = pipeline.add_stage(stage_name="Approve")
manual_approval_action = codepipeline_actions.ManualApprovalAction(
    action_name="Approve",
    notification_topic=sns.Topic(self, "Topic"),  # optional
    notify_emails=["some_email@example.com"
    ],  # optional
    additional_information="additional info"
)
approve_stage.add_action(manual_approval_action)
```

If the `notificationTopic` has not been provided,
but `notifyEmails` were,
a new SNS Topic will be created
(and accessible through the `notificationTopic` property of the Action).

If you want to grant a principal permissions to approve the changes,
you can invoke the method `grantManualApproval` passing it a `IGrantable`:

```python
pipeline = codepipeline.Pipeline(self, "MyPipeline")
approve_stage = pipeline.add_stage(stage_name="Approve")
manual_approval_action = codepipeline_actions.ManualApprovalAction(
    action_name="Approve"
)
approve_stage.add_action(manual_approval_action)

role = iam.Role.from_role_arn(self, "Admin", Arn.format(codebuild.ArnComponents(service="iam", resource="role", resource_name="Admin"), self))
manual_approval_action.grant_manual_approval(role)
```

### AWS Lambda

This module contains an Action that allows you to invoke a Lambda function in a Pipeline:

```python
# fn: lambda.Function

pipeline = codepipeline.Pipeline(self, "MyPipeline")
lambda_action = codepipeline_actions.LambdaInvokeAction(
    action_name="Lambda",
    lambda_=fn
)
pipeline.add_stage(
    stage_name="Lambda",
    actions=[lambda_action]
)
```

The Lambda Action can have up to 5 inputs,
and up to 5 outputs:

```python
# fn: lambda.Function

source_output = codepipeline.Artifact()
build_output = codepipeline.Artifact()
lambda_action = codepipeline_actions.LambdaInvokeAction(
    action_name="Lambda",
    inputs=[source_output, build_output
    ],
    outputs=[
        codepipeline.Artifact("Out1"),
        codepipeline.Artifact("Out2")
    ],
    lambda_=fn
)
```

The Lambda Action supports custom user parameters that pipeline
will pass to the Lambda function:

```python
# fn: lambda.Function


pipeline = codepipeline.Pipeline(self, "MyPipeline")
lambda_action = codepipeline_actions.LambdaInvokeAction(
    action_name="Lambda",
    lambda_=fn,
    user_parameters={
        "foo": "bar",
        "baz": "qux"
    },
    # OR
    user_parameters_string="my-parameter-string"
)
```

The Lambda invoke action emits variables.
Unlike many other actions, the variables are not static,
but dynamic, defined by the function calling the `PutJobSuccessResult`
API with the `outputVariables` property filled with the map of variables
Example:

```python
# later:
# project: codebuild.PipelineProject
lambda_invoke_action = codepipeline_actions.LambdaInvokeAction(
    action_name="Lambda",
    lambda_=lambda_.Function(self, "Func",
        runtime=lambda_.Runtime.NODEJS_12_X,
        handler="index.handler",
        code=lambda_.Code.from_inline("""
                    const AWS = require('aws-sdk');

                    exports.handler = async function(event, context) {
                        const codepipeline = new AWS.CodePipeline();
                        await codepipeline.putJobSuccessResult({
                            jobId: event['CodePipeline.job'].id,
                            outputVariables: {
                                MY_VAR: "some value",
                            },
                        }).promise();
                    }
                """)
    ),
    variables_namespace="MyNamespace"
)
source_output = codepipeline.Artifact()
codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,
    environment_variables={
        "MyVar": codebuild.aws_codebuild.BuildEnvironmentVariable(
            value=lambda_invoke_action.variable("MY_VAR")
        )
    }
)
```

See [the AWS documentation](https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-invoke-lambda-function.html)
on how to write a Lambda function invoked from CodePipeline.

### AWS Step Functions

This module contains an Action that allows you to invoke a Step Function in a Pipeline:

```python
import monocdk as stepfunctions

pipeline = codepipeline.Pipeline(self, "MyPipeline")
start_state = stepfunctions.Pass(self, "StartState")
simple_state_machine = stepfunctions.StateMachine(self, "SimpleStateMachine",
    definition=start_state
)
step_function_action = codepipeline_actions.StepFunctionInvokeAction(
    action_name="Invoke",
    state_machine=simple_state_machine,
    state_machine_input=codepipeline_actions.StateMachineInput.literal({"IsHelloWorldExample": True})
)
pipeline.add_stage(
    stage_name="StepFunctions",
    actions=[step_function_action]
)
```

The `StateMachineInput` can be created with one of 2 static factory methods:
`literal`, which takes an arbitrary map as its only argument, or `filePath`:

```python
import monocdk as stepfunctions


pipeline = codepipeline.Pipeline(self, "MyPipeline")
input_artifact = codepipeline.Artifact()
start_state = stepfunctions.Pass(self, "StartState")
simple_state_machine = stepfunctions.StateMachine(self, "SimpleStateMachine",
    definition=start_state
)
step_function_action = codepipeline_actions.StepFunctionInvokeAction(
    action_name="Invoke",
    state_machine=simple_state_machine,
    state_machine_input=codepipeline_actions.StateMachineInput.file_path(input_artifact.at_path("assets/input.json"))
)
pipeline.add_stage(
    stage_name="StepFunctions",
    actions=[step_function_action]
)
```

See [the AWS documentation](https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-StepFunctions.html)
for information on Action structure reference.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from .. import (
    CfnCapabilities as _CfnCapabilities_6e018757,
    Construct as _Construct_e78e779f,
    Duration as _Duration_070aa057,
    IConstruct as _IConstruct_5a0f9c5e,
    IResource as _IResource_8c1dbbbd,
    SecretValue as _SecretValue_c18506ef,
)
from ..aws_cloudformation import (
    CloudFormationCapabilities as _CloudFormationCapabilities_149b400e
)
from ..aws_codebuild import (
    BuildEnvironmentVariable as _BuildEnvironmentVariable_00095c97,
    IProject as _IProject_6da8803e,
)
from ..aws_codecommit import IRepository as _IRepository_cdb2a3c0
from ..aws_codedeploy import (
    IEcsDeploymentGroup as _IEcsDeploymentGroup_538bcae2,
    IServerDeploymentGroup as _IServerDeploymentGroup_9bf302e3,
)
from ..aws_codepipeline import (
    Action as _Action_0220d19f,
    ActionArtifactBounds as _ActionArtifactBounds_77337cd6,
    ActionBindOptions as _ActionBindOptions_20e0a317,
    ActionCategory as _ActionCategory_338d31b4,
    ActionConfig as _ActionConfig_0c698b52,
    ActionProperties as _ActionProperties_c7760ac6,
    Artifact as _Artifact_9905eec2,
    ArtifactPath as _ArtifactPath_a5b79113,
    CommonActionProps as _CommonActionProps_4f0e79c2,
    CommonAwsActionProps as _CommonAwsActionProps_1494edc0,
    IAction as _IAction_ecd54a08,
    IStage as _IStage_5a7e7342,
)
from ..aws_ecr import IRepository as _IRepository_8b4d2894
from ..aws_ecs import IBaseService as _IBaseService_f1507c0b
from ..aws_events import (
    EventPattern as _EventPattern_a23fbf37,
    IEventBus as _IEventBus_2ca38c95,
    IRuleTarget as _IRuleTarget_d45ec729,
    Rule as _Rule_6cfff189,
    RuleProps as _RuleProps_32051f01,
    Schedule as _Schedule_297d3fad,
)
from ..aws_iam import (
    IGrantable as _IGrantable_4c5a91d1,
    IRole as _IRole_59af6f50,
    PolicyStatement as _PolicyStatement_296fe8a3,
)
from ..aws_lambda import IFunction as _IFunction_6e14f09e
from ..aws_s3 import (
    BucketAccessControl as _BucketAccessControl_a8cb5bce, IBucket as _IBucket_73486e29
)
from ..aws_sns import ITopic as _ITopic_465e36b9
from ..aws_stepfunctions import IStateMachine as _IStateMachine_269a89c4


class Action(
    _Action_0220d19f,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="monocdk.aws_codepipeline_actions.Action",
):
    '''(experimental) Low-level class for generic CodePipeline Actions.

    If you're implementing your own IAction,
    prefer to use the Action class from the codepipeline module.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        action_name: builtins.str,
        artifact_bounds: _ActionArtifactBounds_77337cd6,
        category: _ActionCategory_338d31b4,
        provider: builtins.str,
        account: typing.Optional[builtins.str] = None,
        inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        outputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        owner: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        resource: typing.Optional[_IResource_8c1dbbbd] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param action_name: 
        :param artifact_bounds: 
        :param category: (experimental) The category of the action. The category defines which action type the owner (the entity that performs the action) performs.
        :param provider: (experimental) The service provider that the action calls.
        :param account: (experimental) The account the Action is supposed to live in. For Actions backed by resources, this is inferred from the Stack {@link resource} is part of. However, some Actions, like the CloudFormation ones, are not backed by any resource, and they still might want to be cross-account. In general, a concrete Action class should specify either {@link resource}, or {@link account} - but not both.
        :param inputs: 
        :param outputs: 
        :param owner: 
        :param region: (experimental) The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param resource: (experimental) The optional resource that is backing this Action. This is used for automatically handling Actions backed by resources from a different account and/or region.
        :param role: 
        :param run_order: (experimental) The order in which AWS CodePipeline runs this action. For more information, see the AWS CodePipeline User Guide. https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names
        :param version: 

        :stability: experimental
        '''
        action_properties = _ActionProperties_c7760ac6(
            action_name=action_name,
            artifact_bounds=artifact_bounds,
            category=category,
            provider=provider,
            account=account,
            inputs=inputs,
            outputs=outputs,
            owner=owner,
            region=region,
            resource=resource,
            role=role,
            run_order=run_order,
            variables_namespace=variables_namespace,
            version=version,
        )

        jsii.create(self.__class__, self, [action_properties])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providedActionProperties")
    def _provided_action_properties(self) -> _ActionProperties_c7760ac6:
        '''(experimental) This is a renamed version of the {@link IAction.actionProperties} property.

        :stability: experimental
        '''
        return typing.cast(_ActionProperties_c7760ac6, jsii.get(self, "providedActionProperties"))


class _ActionProxy(
    Action, jsii.proxy_for(_Action_0220d19f) # type: ignore[misc]
):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Action).__jsii_proxy_class__ = lambda : _ActionProxy


class AlexaSkillDeployAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.AlexaSkillDeployAction",
):
    '''(experimental) Deploys the skill to Alexa.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Read the secrets from ParameterStore
        client_id = SecretValue.secrets_manager("AlexaClientId")
        client_secret = SecretValue.secrets_manager("AlexaClientSecret")
        refresh_token = SecretValue.secrets_manager("AlexaRefreshToken")
        
        # Add deploy action
        source_output = codepipeline.Artifact()
        codepipeline_actions.AlexaSkillDeployAction(
            action_name="DeploySkill",
            run_order=1,
            input=source_output,
            client_id=client_id.to_string(),
            client_secret=client_secret,
            refresh_token=refresh_token,
            skill_id="amzn1.ask.skill.12345678-1234-1234-1234-123456789012"
        )
    '''

    def __init__(
        self,
        *,
        client_id: builtins.str,
        client_secret: _SecretValue_c18506ef,
        input: _Artifact_9905eec2,
        refresh_token: _SecretValue_c18506ef,
        skill_id: builtins.str,
        parameter_overrides_artifact: typing.Optional[_Artifact_9905eec2] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param client_id: (experimental) The client id of the developer console token.
        :param client_secret: (experimental) The client secret of the developer console token.
        :param input: (experimental) The source artifact containing the voice model and skill manifest.
        :param refresh_token: (experimental) The refresh token of the developer console token.
        :param skill_id: (experimental) The Alexa skill id.
        :param parameter_overrides_artifact: (experimental) An optional artifact containing overrides for the skill manifest.
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = AlexaSkillDeployActionProps(
            client_id=client_id,
            client_secret=client_secret,
            input=input,
            refresh_token=refresh_token,
            skill_id=skill_id,
            parameter_overrides_artifact=parameter_overrides_artifact,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        _options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, _stage, _options]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.AlexaSkillDeployActionProps",
    jsii_struct_bases=[_CommonActionProps_4f0e79c2],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "input": "input",
        "refresh_token": "refreshToken",
        "skill_id": "skillId",
        "parameter_overrides_artifact": "parameterOverridesArtifact",
    },
)
class AlexaSkillDeployActionProps(_CommonActionProps_4f0e79c2):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        client_id: builtins.str,
        client_secret: _SecretValue_c18506ef,
        input: _Artifact_9905eec2,
        refresh_token: _SecretValue_c18506ef,
        skill_id: builtins.str,
        parameter_overrides_artifact: typing.Optional[_Artifact_9905eec2] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link AlexaSkillDeployAction Alexa deploy Action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param client_id: (experimental) The client id of the developer console token.
        :param client_secret: (experimental) The client secret of the developer console token.
        :param input: (experimental) The source artifact containing the voice model and skill manifest.
        :param refresh_token: (experimental) The refresh token of the developer console token.
        :param skill_id: (experimental) The Alexa skill id.
        :param parameter_overrides_artifact: (experimental) An optional artifact containing overrides for the skill manifest.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Read the secrets from ParameterStore
            client_id = SecretValue.secrets_manager("AlexaClientId")
            client_secret = SecretValue.secrets_manager("AlexaClientSecret")
            refresh_token = SecretValue.secrets_manager("AlexaRefreshToken")
            
            # Add deploy action
            source_output = codepipeline.Artifact()
            codepipeline_actions.AlexaSkillDeployAction(
                action_name="DeploySkill",
                run_order=1,
                input=source_output,
                client_id=client_id.to_string(),
                client_secret=client_secret,
                refresh_token=refresh_token,
                skill_id="amzn1.ask.skill.12345678-1234-1234-1234-123456789012"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "client_id": client_id,
            "client_secret": client_secret,
            "input": input,
            "refresh_token": refresh_token,
            "skill_id": skill_id,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if parameter_overrides_artifact is not None:
            self._values["parameter_overrides_artifact"] = parameter_overrides_artifact

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_id(self) -> builtins.str:
        '''(experimental) The client id of the developer console token.

        :stability: experimental
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_secret(self) -> _SecretValue_c18506ef:
        '''(experimental) The client secret of the developer console token.

        :stability: experimental
        '''
        result = self._values.get("client_secret")
        assert result is not None, "Required property 'client_secret' is missing"
        return typing.cast(_SecretValue_c18506ef, result)

    @builtins.property
    def input(self) -> _Artifact_9905eec2:
        '''(experimental) The source artifact containing the voice model and skill manifest.

        :stability: experimental
        '''
        result = self._values.get("input")
        assert result is not None, "Required property 'input' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def refresh_token(self) -> _SecretValue_c18506ef:
        '''(experimental) The refresh token of the developer console token.

        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        assert result is not None, "Required property 'refresh_token' is missing"
        return typing.cast(_SecretValue_c18506ef, result)

    @builtins.property
    def skill_id(self) -> builtins.str:
        '''(experimental) The Alexa skill id.

        :stability: experimental
        '''
        result = self._values.get("skill_id")
        assert result is not None, "Required property 'skill_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_overrides_artifact(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) An optional artifact containing overrides for the skill manifest.

        :stability: experimental
        '''
        result = self._values.get("parameter_overrides_artifact")
        return typing.cast(typing.Optional[_Artifact_9905eec2], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlexaSkillDeployActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IAction_ecd54a08)
class BitBucketSourceAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.BitBucketSourceAction",
):
    '''(deprecated) A CodePipeline source action for BitBucket.

    :deprecated: use CodeStarConnectionsSourceAction instead

    :stability: deprecated
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_codepipeline as codepipeline
        from monocdk import aws_codepipeline_actions as codepipeline_actions
        from monocdk import aws_iam as iam
        
        # artifact: codepipeline.Artifact
        # role: iam.Role
        
        bit_bucket_source_action = codepipeline_actions.BitBucketSourceAction(
            action_name="actionName",
            connection_arn="connectionArn",
            output=artifact,
            owner="owner",
            repo="repo",
        
            # the properties below are optional
            branch="branch",
            code_build_clone_output=False,
            role=role,
            run_order=123,
            trigger_on_push=False,
            variables_namespace="variablesNamespace"
        )
    '''

    def __init__(
        self,
        *,
        connection_arn: builtins.str,
        output: _Artifact_9905eec2,
        owner: builtins.str,
        repo: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        trigger_on_push: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_arn: (experimental) The ARN of the CodeStar Connection created in the AWS console that has permissions to access this GitHub or BitBucket repository.
        :param output: (experimental) The output artifact that this action produces. Can be used as input for further pipeline actions.
        :param owner: (experimental) The owning user or organization of the repository.
        :param repo: (experimental) The name of the repository.
        :param branch: (experimental) The branch to build. Default: 'master'
        :param code_build_clone_output: (experimental) Whether the output should be the contents of the repository (which is the default), or a link that allows CodeBuild to clone the repository before building. **Note**: if this option is true, then only CodeBuild actions can use the resulting {@link output}. Default: false
        :param trigger_on_push: (experimental) Controls automatically starting your pipeline when a new commit is made on the configured repository and branch. If unspecified, the default value is true, and the field does not display by default. Default: true
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: deprecated
        '''
        props = BitBucketSourceActionProps(
            connection_arn=connection_arn,
            output=output,
            owner=owner,
            repo=repo,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            trigger_on_push=trigger_on_push,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(deprecated) The callback invoked when this Action is added to a Pipeline.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: deprecated
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bind", [scope, stage, options]))

    @jsii.member(jsii_name="onStateChange")
    def on_state_change(
        self,
        name: builtins.str,
        target: typing.Optional[_IRuleTarget_d45ec729] = None,
        *,
        description: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        event_bus: typing.Optional[_IEventBus_2ca38c95] = None,
        event_pattern: typing.Optional[_EventPattern_a23fbf37] = None,
        rule_name: typing.Optional[builtins.str] = None,
        schedule: typing.Optional[_Schedule_297d3fad] = None,
        targets: typing.Optional[typing.Sequence[_IRuleTarget_d45ec729]] = None,
    ) -> _Rule_6cfff189:
        '''(deprecated) Creates an Event that will be triggered whenever the state of this Action changes.

        :param name: -
        :param target: -
        :param description: (experimental) A description of the rule's purpose. Default: - No description.
        :param enabled: (experimental) Indicates whether the rule is enabled. Default: true
        :param event_bus: (experimental) The event bus to associate with this rule. Default: - The default event bus.
        :param event_pattern: (experimental) Describes which events EventBridge routes to the specified target. These routed events are matched events. For more information, see Events and Event Patterns in the Amazon EventBridge User Guide. Default: - None.
        :param rule_name: (experimental) A name for the rule. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the rule name. For more information, see Name Type.
        :param schedule: (experimental) The schedule or rate (frequency) that determines when EventBridge runs the rule. For more information, see Schedule Expression Syntax for Rules in the Amazon EventBridge User Guide. Default: - None.
        :param targets: (experimental) Targets to invoke when this rule matches an event. Input will be the full matched event. If you wish to specify custom target input, use ``addTarget(target[, inputOptions])``. Default: - No targets.

        :stability: deprecated
        '''
        options = _RuleProps_32051f01(
            description=description,
            enabled=enabled,
            event_bus=event_bus,
            event_pattern=event_pattern,
            rule_name=rule_name,
            schedule=schedule,
            targets=targets,
        )

        return typing.cast(_Rule_6cfff189, jsii.invoke(self, "onStateChange", [name, target, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionProperties")
    def action_properties(self) -> _ActionProperties_c7760ac6:
        '''(deprecated) The simple properties of the Action, like its Owner, name, etc.

        Note that this accessor will be called before the {@link bind} callback.

        :stability: deprecated
        '''
        return typing.cast(_ActionProperties_c7760ac6, jsii.get(self, "actionProperties"))


class CacheControl(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CacheControl",
):
    '''(experimental) Used for HTTP cache-control header, which influences downstream caches.

    Use the provided static factory methods to construct instances of this class.
    Used in the {@link S3DeployActionProps.cacheControl} property.

    :see: https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.9
    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_codepipeline_actions as codepipeline_actions
        
        cache_control = codepipeline_actions.CacheControl.from_string("s")
    '''

    @jsii.member(jsii_name="fromString") # type: ignore[misc]
    @builtins.classmethod
    def from_string(cls, s: builtins.str) -> "CacheControl":
        '''(experimental) Allows you to create an arbitrary cache control directive, in case our support is missing a method for a particular directive.

        :param s: -

        :stability: experimental
        '''
        return typing.cast("CacheControl", jsii.sinvoke(cls, "fromString", [s]))

    @jsii.member(jsii_name="maxAge") # type: ignore[misc]
    @builtins.classmethod
    def max_age(cls, t: _Duration_070aa057) -> "CacheControl":
        '''(experimental) The 'max-age' cache control directive.

        :param t: -

        :stability: experimental
        '''
        return typing.cast("CacheControl", jsii.sinvoke(cls, "maxAge", [t]))

    @jsii.member(jsii_name="mustRevalidate") # type: ignore[misc]
    @builtins.classmethod
    def must_revalidate(cls) -> "CacheControl":
        '''(experimental) The 'must-revalidate' cache control directive.

        :stability: experimental
        '''
        return typing.cast("CacheControl", jsii.sinvoke(cls, "mustRevalidate", []))

    @jsii.member(jsii_name="noCache") # type: ignore[misc]
    @builtins.classmethod
    def no_cache(cls) -> "CacheControl":
        '''(experimental) The 'no-cache' cache control directive.

        :stability: experimental
        '''
        return typing.cast("CacheControl", jsii.sinvoke(cls, "noCache", []))

    @jsii.member(jsii_name="noTransform") # type: ignore[misc]
    @builtins.classmethod
    def no_transform(cls) -> "CacheControl":
        '''(experimental) The 'no-transform' cache control directive.

        :stability: experimental
        '''
        return typing.cast("CacheControl", jsii.sinvoke(cls, "noTransform", []))

    @jsii.member(jsii_name="proxyRevalidate") # type: ignore[misc]
    @builtins.classmethod
    def proxy_revalidate(cls) -> "CacheControl":
        '''(experimental) The 'proxy-revalidate' cache control directive.

        :stability: experimental
        '''
        return typing.cast("CacheControl", jsii.sinvoke(cls, "proxyRevalidate", []))

    @jsii.member(jsii_name="setPrivate") # type: ignore[misc]
    @builtins.classmethod
    def set_private(cls) -> "CacheControl":
        '''(experimental) The 'private' cache control directive.

        :stability: experimental
        '''
        return typing.cast("CacheControl", jsii.sinvoke(cls, "setPrivate", []))

    @jsii.member(jsii_name="setPublic") # type: ignore[misc]
    @builtins.classmethod
    def set_public(cls) -> "CacheControl":
        '''(experimental) The 'public' cache control directive.

        :stability: experimental
        '''
        return typing.cast("CacheControl", jsii.sinvoke(cls, "setPublic", []))

    @jsii.member(jsii_name="sMaxAge") # type: ignore[misc]
    @builtins.classmethod
    def s_max_age(cls, t: _Duration_070aa057) -> "CacheControl":
        '''(experimental) The 's-max-age' cache control directive.

        :param t: -

        :stability: experimental
        '''
        return typing.cast("CacheControl", jsii.sinvoke(cls, "sMaxAge", [t]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        '''(experimental) the actual text value of the created directive.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        jsii.set(self, "value", value)


class CloudFormationCreateReplaceChangeSetAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CloudFormationCreateReplaceChangeSetAction",
):
    '''(experimental) CodePipeline action to prepare a change set.

    Creates the change set if it doesn't exist based on the stack name and template that you submit.
    If the change set exists, AWS CloudFormation deletes it, and then creates a new one.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import monocdk as monocdk
        from monocdk import aws_cloudformation as cloudformation
        from monocdk import aws_codepipeline as codepipeline
        from monocdk import aws_codepipeline_actions as codepipeline_actions
        from monocdk import aws_iam as iam
        
        # artifact: codepipeline.Artifact
        # artifact_path: codepipeline.ArtifactPath
        # parameter_overrides: Any
        # role: iam.Role
        
        cloud_formation_create_replace_change_set_action = codepipeline_actions.CloudFormationCreateReplaceChangeSetAction(
            action_name="actionName",
            admin_permissions=False,
            change_set_name="changeSetName",
            stack_name="stackName",
            template_path=artifact_path,
        
            # the properties below are optional
            account="account",
            capabilities=[cloudformation.CloudFormationCapabilities.NONE],
            cfn_capabilities=[monocdk.CfnCapabilities.NONE],
            deployment_role=role,
            extra_inputs=[artifact],
            output=artifact,
            output_file_name="outputFileName",
            parameter_overrides={
                "parameter_overrides_key": parameter_overrides
            },
            region="region",
            role=role,
            run_order=123,
            template_configuration=artifact_path,
            variables_namespace="variablesNamespace"
        )
    '''

    def __init__(
        self,
        *,
        admin_permissions: builtins.bool,
        change_set_name: builtins.str,
        stack_name: builtins.str,
        template_path: _ArtifactPath_a5b79113,
        account: typing.Optional[builtins.str] = None,
        capabilities: typing.Optional[typing.Sequence[_CloudFormationCapabilities_149b400e]] = None,
        cfn_capabilities: typing.Optional[typing.Sequence[_CfnCapabilities_6e018757]] = None,
        deployment_role: typing.Optional[_IRole_59af6f50] = None,
        extra_inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        output_file_name: typing.Optional[builtins.str] = None,
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        region: typing.Optional[builtins.str] = None,
        template_configuration: typing.Optional[_ArtifactPath_a5b79113] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param admin_permissions: (experimental) Whether to grant full permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have full (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
        :param change_set_name: (experimental) Name of the change set to create or update.
        :param stack_name: (experimental) The name of the stack to apply this action to.
        :param template_path: (experimental) Input artifact with the ChangeSet's CloudFormation template.
        :param account: (experimental) The AWS account this Action is supposed to operate in. **Note**: if you specify the ``role`` property, this is ignored - the action will operate in the same region the passed role does. Default: - action resides in the same account as the pipeline
        :param capabilities: (deprecated) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify ``AnonymousIAM`` or ``NamedIAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information see the link below. Default: None, unless ``adminPermissions`` is true
        :param cfn_capabilities: (experimental) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement is required that AWS CloudFormation might create or update those resources. For example, you must specify ``ANONYMOUS_IAM`` or ``NAMED_IAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information, see the link below. Default: None, unless ``adminPermissions`` is true
        :param deployment_role: (experimental) IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have full permissions. Default: A fresh role with full or no permissions (depending on the value of ``adminPermissions``).
        :param extra_inputs: (experimental) The list of additional input Artifacts for this Action. This is especially useful when used in conjunction with the ``parameterOverrides`` property. For example, if you have: parameterOverrides: { 'Param1': action1.outputArtifact.bucketName, 'Param2': action2.outputArtifact.objectKey, } , if the output Artifacts of ``action1`` and ``action2`` were not used to set either the ``templateConfiguration`` or the ``templatePath`` properties, you need to make sure to include them in the ``extraInputs`` - otherwise, you'll get an "unrecognized Artifact" error during your Pipeline's execution.
        :param output: (experimental) The name of the output artifact to generate. Only applied if ``outputFileName`` is set as well. Default: Automatically generated artifact name.
        :param output_file_name: (experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result. The file will contain the result of the call to AWS CloudFormation (for example the call to UpdateStack or CreateChangeSet). AWS CodePipeline adds the file to the output artifact after performing the specified action. Default: No output artifact generated
        :param parameter_overrides: (experimental) Additional template parameters. Template parameters specified here take precedence over template parameters found in the artifact specified by the ``templateConfiguration`` property. We recommend that you use the template configuration file to specify most of your parameter values. Use parameter overrides to specify only dynamic parameter values (values that are unknown until you run the pipeline). All parameter names must be present in the stack template. Note: the entire object cannot be more than 1kB. Default: No overrides
        :param region: (experimental) The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param template_configuration: (experimental) Input artifact to use for template parameters values and stack policy. The template configuration file should contain a JSON object that should look like this: ``{ "Parameters": {...}, "Tags": {...}, "StackPolicy": {... }}``. For more information, see `AWS CloudFormation Artifacts <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html>`_. Note that if you include sensitive information, such as passwords, restrict access to this file. Default: No template configuration based on input artifacts
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = CloudFormationCreateReplaceChangeSetActionProps(
            admin_permissions=admin_permissions,
            change_set_name=change_set_name,
            stack_name=stack_name,
            template_path=template_path,
            account=account,
            capabilities=capabilities,
            cfn_capabilities=cfn_capabilities,
            deployment_role=deployment_role,
            extra_inputs=extra_inputs,
            output=output,
            output_file_name=output_file_name,
            parameter_overrides=parameter_overrides,
            region=region,
            template_configuration=template_configuration,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addToDeploymentRolePolicy")
    def add_to_deployment_role_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
    ) -> builtins.bool:
        '''(experimental) Add statement to the service role assumed by CloudFormation while executing this action.

        :param statement: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "addToDeploymentRolePolicy", [statement]))

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [scope, stage, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentRole")
    def deployment_role(self) -> _IRole_59af6f50:
        '''
        :stability: experimental
        '''
        return typing.cast(_IRole_59af6f50, jsii.get(self, "deploymentRole"))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CloudFormationCreateReplaceChangeSetActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "admin_permissions": "adminPermissions",
        "change_set_name": "changeSetName",
        "stack_name": "stackName",
        "template_path": "templatePath",
        "account": "account",
        "capabilities": "capabilities",
        "cfn_capabilities": "cfnCapabilities",
        "deployment_role": "deploymentRole",
        "extra_inputs": "extraInputs",
        "output": "output",
        "output_file_name": "outputFileName",
        "parameter_overrides": "parameterOverrides",
        "region": "region",
        "template_configuration": "templateConfiguration",
    },
)
class CloudFormationCreateReplaceChangeSetActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        admin_permissions: builtins.bool,
        change_set_name: builtins.str,
        stack_name: builtins.str,
        template_path: _ArtifactPath_a5b79113,
        account: typing.Optional[builtins.str] = None,
        capabilities: typing.Optional[typing.Sequence[_CloudFormationCapabilities_149b400e]] = None,
        cfn_capabilities: typing.Optional[typing.Sequence[_CfnCapabilities_6e018757]] = None,
        deployment_role: typing.Optional[_IRole_59af6f50] = None,
        extra_inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        output_file_name: typing.Optional[builtins.str] = None,
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        region: typing.Optional[builtins.str] = None,
        template_configuration: typing.Optional[_ArtifactPath_a5b79113] = None,
    ) -> None:
        '''(experimental) Properties for the CloudFormationCreateReplaceChangeSetAction.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param admin_permissions: (experimental) Whether to grant full permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have full (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
        :param change_set_name: (experimental) Name of the change set to create or update.
        :param stack_name: (experimental) The name of the stack to apply this action to.
        :param template_path: (experimental) Input artifact with the ChangeSet's CloudFormation template.
        :param account: (experimental) The AWS account this Action is supposed to operate in. **Note**: if you specify the ``role`` property, this is ignored - the action will operate in the same region the passed role does. Default: - action resides in the same account as the pipeline
        :param capabilities: (deprecated) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify ``AnonymousIAM`` or ``NamedIAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information see the link below. Default: None, unless ``adminPermissions`` is true
        :param cfn_capabilities: (experimental) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement is required that AWS CloudFormation might create or update those resources. For example, you must specify ``ANONYMOUS_IAM`` or ``NAMED_IAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information, see the link below. Default: None, unless ``adminPermissions`` is true
        :param deployment_role: (experimental) IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have full permissions. Default: A fresh role with full or no permissions (depending on the value of ``adminPermissions``).
        :param extra_inputs: (experimental) The list of additional input Artifacts for this Action. This is especially useful when used in conjunction with the ``parameterOverrides`` property. For example, if you have: parameterOverrides: { 'Param1': action1.outputArtifact.bucketName, 'Param2': action2.outputArtifact.objectKey, } , if the output Artifacts of ``action1`` and ``action2`` were not used to set either the ``templateConfiguration`` or the ``templatePath`` properties, you need to make sure to include them in the ``extraInputs`` - otherwise, you'll get an "unrecognized Artifact" error during your Pipeline's execution.
        :param output: (experimental) The name of the output artifact to generate. Only applied if ``outputFileName`` is set as well. Default: Automatically generated artifact name.
        :param output_file_name: (experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result. The file will contain the result of the call to AWS CloudFormation (for example the call to UpdateStack or CreateChangeSet). AWS CodePipeline adds the file to the output artifact after performing the specified action. Default: No output artifact generated
        :param parameter_overrides: (experimental) Additional template parameters. Template parameters specified here take precedence over template parameters found in the artifact specified by the ``templateConfiguration`` property. We recommend that you use the template configuration file to specify most of your parameter values. Use parameter overrides to specify only dynamic parameter values (values that are unknown until you run the pipeline). All parameter names must be present in the stack template. Note: the entire object cannot be more than 1kB. Default: No overrides
        :param region: (experimental) The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param template_configuration: (experimental) Input artifact to use for template parameters values and stack policy. The template configuration file should contain a JSON object that should look like this: ``{ "Parameters": {...}, "Tags": {...}, "StackPolicy": {... }}``. For more information, see `AWS CloudFormation Artifacts <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html>`_. Note that if you include sensitive information, such as passwords, restrict access to this file. Default: No template configuration based on input artifacts

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import monocdk as monocdk
            from monocdk import aws_cloudformation as cloudformation
            from monocdk import aws_codepipeline as codepipeline
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            from monocdk import aws_iam as iam
            
            # artifact: codepipeline.Artifact
            # artifact_path: codepipeline.ArtifactPath
            # parameter_overrides: Any
            # role: iam.Role
            
            cloud_formation_create_replace_change_set_action_props = codepipeline_actions.CloudFormationCreateReplaceChangeSetActionProps(
                action_name="actionName",
                admin_permissions=False,
                change_set_name="changeSetName",
                stack_name="stackName",
                template_path=artifact_path,
            
                # the properties below are optional
                account="account",
                capabilities=[cloudformation.CloudFormationCapabilities.NONE],
                cfn_capabilities=[monocdk.CfnCapabilities.NONE],
                deployment_role=role,
                extra_inputs=[artifact],
                output=artifact,
                output_file_name="outputFileName",
                parameter_overrides={
                    "parameter_overrides_key": parameter_overrides
                },
                region="region",
                role=role,
                run_order=123,
                template_configuration=artifact_path,
                variables_namespace="variablesNamespace"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "admin_permissions": admin_permissions,
            "change_set_name": change_set_name,
            "stack_name": stack_name,
            "template_path": template_path,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if account is not None:
            self._values["account"] = account
        if capabilities is not None:
            self._values["capabilities"] = capabilities
        if cfn_capabilities is not None:
            self._values["cfn_capabilities"] = cfn_capabilities
        if deployment_role is not None:
            self._values["deployment_role"] = deployment_role
        if extra_inputs is not None:
            self._values["extra_inputs"] = extra_inputs
        if output is not None:
            self._values["output"] = output
        if output_file_name is not None:
            self._values["output_file_name"] = output_file_name
        if parameter_overrides is not None:
            self._values["parameter_overrides"] = parameter_overrides
        if region is not None:
            self._values["region"] = region
        if template_configuration is not None:
            self._values["template_configuration"] = template_configuration

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def admin_permissions(self) -> builtins.bool:
        '''(experimental) Whether to grant full permissions to CloudFormation while deploying this template.

        Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you
        don't specify any alternatives.

        The default role that will be created for you will have full (i.e., ``*``)
        permissions on all resources, and the deployment will have named IAM
        capabilities (i.e., able to create all IAM resources).

        This is a shorthand that you can use if you fully trust the templates that
        are deployed in this pipeline. If you want more fine-grained permissions,
        use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation
        deployment is allowed to do.

        :stability: experimental
        '''
        result = self._values.get("admin_permissions")
        assert result is not None, "Required property 'admin_permissions' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def change_set_name(self) -> builtins.str:
        '''(experimental) Name of the change set to create or update.

        :stability: experimental
        '''
        result = self._values.get("change_set_name")
        assert result is not None, "Required property 'change_set_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stack_name(self) -> builtins.str:
        '''(experimental) The name of the stack to apply this action to.

        :stability: experimental
        '''
        result = self._values.get("stack_name")
        assert result is not None, "Required property 'stack_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template_path(self) -> _ArtifactPath_a5b79113:
        '''(experimental) Input artifact with the ChangeSet's CloudFormation template.

        :stability: experimental
        '''
        result = self._values.get("template_path")
        assert result is not None, "Required property 'template_path' is missing"
        return typing.cast(_ArtifactPath_a5b79113, result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS account this Action is supposed to operate in.

        **Note**: if you specify the ``role`` property,
        this is ignored - the action will operate in the same region the passed role does.

        :default: - action resides in the same account as the pipeline

        :stability: experimental
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def capabilities(
        self,
    ) -> typing.Optional[typing.List[_CloudFormationCapabilities_149b400e]]:
        '''(deprecated) Acknowledge certain changes made as part of deployment.

        For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation
        might create or update those resources. For example, you must specify ``AnonymousIAM`` or ``NamedIAM``
        if your stack template contains AWS Identity and Access Management (IAM) resources. For more
        information see the link below.

        :default: None, unless ``adminPermissions`` is true

        :deprecated: use {@link cfnCapabilities} instead

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
        :stability: deprecated
        '''
        result = self._values.get("capabilities")
        return typing.cast(typing.Optional[typing.List[_CloudFormationCapabilities_149b400e]], result)

    @builtins.property
    def cfn_capabilities(
        self,
    ) -> typing.Optional[typing.List[_CfnCapabilities_6e018757]]:
        '''(experimental) Acknowledge certain changes made as part of deployment.

        For stacks that contain certain resources,
        explicit acknowledgement is required that AWS CloudFormation might create or update those resources.
        For example, you must specify ``ANONYMOUS_IAM`` or ``NAMED_IAM`` if your stack template contains AWS
        Identity and Access Management (IAM) resources.
        For more information, see the link below.

        :default: None, unless ``adminPermissions`` is true

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
        :stability: experimental
        '''
        result = self._values.get("cfn_capabilities")
        return typing.cast(typing.Optional[typing.List[_CfnCapabilities_6e018757]], result)

    @builtins.property
    def deployment_role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) IAM role to assume when deploying changes.

        If not specified, a fresh role is created. The role is created with zero
        permissions unless ``adminPermissions`` is true, in which case the role will have
        full permissions.

        :default: A fresh role with full or no permissions (depending on the value of ``adminPermissions``).

        :stability: experimental
        '''
        result = self._values.get("deployment_role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def extra_inputs(self) -> typing.Optional[typing.List[_Artifact_9905eec2]]:
        '''(experimental) The list of additional input Artifacts for this Action.

        This is especially useful when used in conjunction with the ``parameterOverrides`` property.
        For example, if you have:

        parameterOverrides: {
        'Param1': action1.outputArtifact.bucketName,
        'Param2': action2.outputArtifact.objectKey,
        }

        , if the output Artifacts of ``action1`` and ``action2`` were not used to
        set either the ``templateConfiguration`` or the ``templatePath`` properties,
        you need to make sure to include them in the ``extraInputs`` -
        otherwise, you'll get an "unrecognized Artifact" error during your Pipeline's execution.

        :stability: experimental
        '''
        result = self._values.get("extra_inputs")
        return typing.cast(typing.Optional[typing.List[_Artifact_9905eec2]], result)

    @builtins.property
    def output(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) The name of the output artifact to generate.

        Only applied if ``outputFileName`` is set as well.

        :default: Automatically generated artifact name.

        :stability: experimental
        '''
        result = self._values.get("output")
        return typing.cast(typing.Optional[_Artifact_9905eec2], result)

    @builtins.property
    def output_file_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result.

        The file will contain the result of the call to AWS CloudFormation (for example
        the call to UpdateStack or CreateChangeSet).

        AWS CodePipeline adds the file to the output artifact after performing
        the specified action.

        :default: No output artifact generated

        :stability: experimental
        '''
        result = self._values.get("output_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_overrides(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional template parameters.

        Template parameters specified here take precedence over template parameters
        found in the artifact specified by the ``templateConfiguration`` property.

        We recommend that you use the template configuration file to specify
        most of your parameter values. Use parameter overrides to specify only
        dynamic parameter values (values that are unknown until you run the
        pipeline).

        All parameter names must be present in the stack template.

        Note: the entire object cannot be more than 1kB.

        :default: No overrides

        :stability: experimental
        '''
        result = self._values.get("parameter_overrides")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS region the given Action resides in.

        Note that a cross-region Pipeline requires replication buckets to function correctly.
        You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property.
        If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets,
        that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack.

        :default: the Action resides in the same region as the Pipeline

        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template_configuration(self) -> typing.Optional[_ArtifactPath_a5b79113]:
        '''(experimental) Input artifact to use for template parameters values and stack policy.

        The template configuration file should contain a JSON object that should look like this:
        ``{ "Parameters": {...}, "Tags": {...}, "StackPolicy": {... }}``. For more information,
        see `AWS CloudFormation Artifacts <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html>`_.

        Note that if you include sensitive information, such as passwords, restrict access to this
        file.

        :default: No template configuration based on input artifacts

        :stability: experimental
        '''
        result = self._values.get("template_configuration")
        return typing.cast(typing.Optional[_ArtifactPath_a5b79113], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationCreateReplaceChangeSetActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudFormationCreateUpdateStackAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CloudFormationCreateUpdateStackAction",
):
    '''(experimental) CodePipeline action to deploy a stack.

    Creates the stack if the specified stack doesn't exist. If the stack exists,
    AWS CloudFormation updates the stack. Use this action to update existing
    stacks.

    AWS CodePipeline won't replace the stack, and will fail deployment if the
    stack is in a failed state. Use ``ReplaceOnFailure`` for an action that
    will delete and recreate the stack to try and recover from failed states.

    Use this action to automatically replace failed stacks without recovering or
    troubleshooting them. You would typically choose this mode for testing.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Actions that don't accept a resource objet accept an explicit `account` parameter
        # stage: codepipeline.IStage
        # template_path: codepipeline.ArtifactPath
        
        stage.add_action(codepipeline_actions.CloudFormationCreateUpdateStackAction(
            account="123456789012",
            template_path=template_path,
            admin_permissions=False,
            stack_name=Stack.of(self).stack_name,
            action_name="cloudformation-create-update"
        ))
    '''

    def __init__(
        self,
        *,
        admin_permissions: builtins.bool,
        stack_name: builtins.str,
        template_path: _ArtifactPath_a5b79113,
        account: typing.Optional[builtins.str] = None,
        capabilities: typing.Optional[typing.Sequence[_CloudFormationCapabilities_149b400e]] = None,
        cfn_capabilities: typing.Optional[typing.Sequence[_CfnCapabilities_6e018757]] = None,
        deployment_role: typing.Optional[_IRole_59af6f50] = None,
        extra_inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        output_file_name: typing.Optional[builtins.str] = None,
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        region: typing.Optional[builtins.str] = None,
        replace_on_failure: typing.Optional[builtins.bool] = None,
        template_configuration: typing.Optional[_ArtifactPath_a5b79113] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param admin_permissions: (experimental) Whether to grant full permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have full (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
        :param stack_name: (experimental) The name of the stack to apply this action to.
        :param template_path: (experimental) Input artifact with the CloudFormation template to deploy.
        :param account: (experimental) The AWS account this Action is supposed to operate in. **Note**: if you specify the ``role`` property, this is ignored - the action will operate in the same region the passed role does. Default: - action resides in the same account as the pipeline
        :param capabilities: (deprecated) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify ``AnonymousIAM`` or ``NamedIAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information see the link below. Default: None, unless ``adminPermissions`` is true
        :param cfn_capabilities: (experimental) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement is required that AWS CloudFormation might create or update those resources. For example, you must specify ``ANONYMOUS_IAM`` or ``NAMED_IAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information, see the link below. Default: None, unless ``adminPermissions`` is true
        :param deployment_role: (experimental) IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have full permissions. Default: A fresh role with full or no permissions (depending on the value of ``adminPermissions``).
        :param extra_inputs: (experimental) The list of additional input Artifacts for this Action. This is especially useful when used in conjunction with the ``parameterOverrides`` property. For example, if you have: parameterOverrides: { 'Param1': action1.outputArtifact.bucketName, 'Param2': action2.outputArtifact.objectKey, } , if the output Artifacts of ``action1`` and ``action2`` were not used to set either the ``templateConfiguration`` or the ``templatePath`` properties, you need to make sure to include them in the ``extraInputs`` - otherwise, you'll get an "unrecognized Artifact" error during your Pipeline's execution.
        :param output: (experimental) The name of the output artifact to generate. Only applied if ``outputFileName`` is set as well. Default: Automatically generated artifact name.
        :param output_file_name: (experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result. The file will contain the result of the call to AWS CloudFormation (for example the call to UpdateStack or CreateChangeSet). AWS CodePipeline adds the file to the output artifact after performing the specified action. Default: No output artifact generated
        :param parameter_overrides: (experimental) Additional template parameters. Template parameters specified here take precedence over template parameters found in the artifact specified by the ``templateConfiguration`` property. We recommend that you use the template configuration file to specify most of your parameter values. Use parameter overrides to specify only dynamic parameter values (values that are unknown until you run the pipeline). All parameter names must be present in the stack template. Note: the entire object cannot be more than 1kB. Default: No overrides
        :param region: (experimental) The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param replace_on_failure: (experimental) Replace the stack if it's in a failed state. If this is set to true and the stack is in a failed state (one of ROLLBACK_COMPLETE, ROLLBACK_FAILED, CREATE_FAILED, DELETE_FAILED, or UPDATE_ROLLBACK_FAILED), AWS CloudFormation deletes the stack and then creates a new stack. If this is not set to true and the stack is in a failed state, the deployment fails. Default: false
        :param template_configuration: (experimental) Input artifact to use for template parameters values and stack policy. The template configuration file should contain a JSON object that should look like this: ``{ "Parameters": {...}, "Tags": {...}, "StackPolicy": {... }}``. For more information, see `AWS CloudFormation Artifacts <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html>`_. Note that if you include sensitive information, such as passwords, restrict access to this file. Default: No template configuration based on input artifacts
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = CloudFormationCreateUpdateStackActionProps(
            admin_permissions=admin_permissions,
            stack_name=stack_name,
            template_path=template_path,
            account=account,
            capabilities=capabilities,
            cfn_capabilities=cfn_capabilities,
            deployment_role=deployment_role,
            extra_inputs=extra_inputs,
            output=output,
            output_file_name=output_file_name,
            parameter_overrides=parameter_overrides,
            region=region,
            replace_on_failure=replace_on_failure,
            template_configuration=template_configuration,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addToDeploymentRolePolicy")
    def add_to_deployment_role_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
    ) -> builtins.bool:
        '''(experimental) Add statement to the service role assumed by CloudFormation while executing this action.

        :param statement: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "addToDeploymentRolePolicy", [statement]))

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [scope, stage, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentRole")
    def deployment_role(self) -> _IRole_59af6f50:
        '''
        :stability: experimental
        '''
        return typing.cast(_IRole_59af6f50, jsii.get(self, "deploymentRole"))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CloudFormationCreateUpdateStackActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "admin_permissions": "adminPermissions",
        "stack_name": "stackName",
        "template_path": "templatePath",
        "account": "account",
        "capabilities": "capabilities",
        "cfn_capabilities": "cfnCapabilities",
        "deployment_role": "deploymentRole",
        "extra_inputs": "extraInputs",
        "output": "output",
        "output_file_name": "outputFileName",
        "parameter_overrides": "parameterOverrides",
        "region": "region",
        "replace_on_failure": "replaceOnFailure",
        "template_configuration": "templateConfiguration",
    },
)
class CloudFormationCreateUpdateStackActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        admin_permissions: builtins.bool,
        stack_name: builtins.str,
        template_path: _ArtifactPath_a5b79113,
        account: typing.Optional[builtins.str] = None,
        capabilities: typing.Optional[typing.Sequence[_CloudFormationCapabilities_149b400e]] = None,
        cfn_capabilities: typing.Optional[typing.Sequence[_CfnCapabilities_6e018757]] = None,
        deployment_role: typing.Optional[_IRole_59af6f50] = None,
        extra_inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        output_file_name: typing.Optional[builtins.str] = None,
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        region: typing.Optional[builtins.str] = None,
        replace_on_failure: typing.Optional[builtins.bool] = None,
        template_configuration: typing.Optional[_ArtifactPath_a5b79113] = None,
    ) -> None:
        '''(experimental) Properties for the CloudFormationCreateUpdateStackAction.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param admin_permissions: (experimental) Whether to grant full permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have full (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
        :param stack_name: (experimental) The name of the stack to apply this action to.
        :param template_path: (experimental) Input artifact with the CloudFormation template to deploy.
        :param account: (experimental) The AWS account this Action is supposed to operate in. **Note**: if you specify the ``role`` property, this is ignored - the action will operate in the same region the passed role does. Default: - action resides in the same account as the pipeline
        :param capabilities: (deprecated) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify ``AnonymousIAM`` or ``NamedIAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information see the link below. Default: None, unless ``adminPermissions`` is true
        :param cfn_capabilities: (experimental) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement is required that AWS CloudFormation might create or update those resources. For example, you must specify ``ANONYMOUS_IAM`` or ``NAMED_IAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information, see the link below. Default: None, unless ``adminPermissions`` is true
        :param deployment_role: (experimental) IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have full permissions. Default: A fresh role with full or no permissions (depending on the value of ``adminPermissions``).
        :param extra_inputs: (experimental) The list of additional input Artifacts for this Action. This is especially useful when used in conjunction with the ``parameterOverrides`` property. For example, if you have: parameterOverrides: { 'Param1': action1.outputArtifact.bucketName, 'Param2': action2.outputArtifact.objectKey, } , if the output Artifacts of ``action1`` and ``action2`` were not used to set either the ``templateConfiguration`` or the ``templatePath`` properties, you need to make sure to include them in the ``extraInputs`` - otherwise, you'll get an "unrecognized Artifact" error during your Pipeline's execution.
        :param output: (experimental) The name of the output artifact to generate. Only applied if ``outputFileName`` is set as well. Default: Automatically generated artifact name.
        :param output_file_name: (experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result. The file will contain the result of the call to AWS CloudFormation (for example the call to UpdateStack or CreateChangeSet). AWS CodePipeline adds the file to the output artifact after performing the specified action. Default: No output artifact generated
        :param parameter_overrides: (experimental) Additional template parameters. Template parameters specified here take precedence over template parameters found in the artifact specified by the ``templateConfiguration`` property. We recommend that you use the template configuration file to specify most of your parameter values. Use parameter overrides to specify only dynamic parameter values (values that are unknown until you run the pipeline). All parameter names must be present in the stack template. Note: the entire object cannot be more than 1kB. Default: No overrides
        :param region: (experimental) The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param replace_on_failure: (experimental) Replace the stack if it's in a failed state. If this is set to true and the stack is in a failed state (one of ROLLBACK_COMPLETE, ROLLBACK_FAILED, CREATE_FAILED, DELETE_FAILED, or UPDATE_ROLLBACK_FAILED), AWS CloudFormation deletes the stack and then creates a new stack. If this is not set to true and the stack is in a failed state, the deployment fails. Default: false
        :param template_configuration: (experimental) Input artifact to use for template parameters values and stack policy. The template configuration file should contain a JSON object that should look like this: ``{ "Parameters": {...}, "Tags": {...}, "StackPolicy": {... }}``. For more information, see `AWS CloudFormation Artifacts <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html>`_. Note that if you include sensitive information, such as passwords, restrict access to this file. Default: No template configuration based on input artifacts

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Actions that don't accept a resource objet accept an explicit `account` parameter
            # stage: codepipeline.IStage
            # template_path: codepipeline.ArtifactPath
            
            stage.add_action(codepipeline_actions.CloudFormationCreateUpdateStackAction(
                account="123456789012",
                template_path=template_path,
                admin_permissions=False,
                stack_name=Stack.of(self).stack_name,
                action_name="cloudformation-create-update"
            ))
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "admin_permissions": admin_permissions,
            "stack_name": stack_name,
            "template_path": template_path,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if account is not None:
            self._values["account"] = account
        if capabilities is not None:
            self._values["capabilities"] = capabilities
        if cfn_capabilities is not None:
            self._values["cfn_capabilities"] = cfn_capabilities
        if deployment_role is not None:
            self._values["deployment_role"] = deployment_role
        if extra_inputs is not None:
            self._values["extra_inputs"] = extra_inputs
        if output is not None:
            self._values["output"] = output
        if output_file_name is not None:
            self._values["output_file_name"] = output_file_name
        if parameter_overrides is not None:
            self._values["parameter_overrides"] = parameter_overrides
        if region is not None:
            self._values["region"] = region
        if replace_on_failure is not None:
            self._values["replace_on_failure"] = replace_on_failure
        if template_configuration is not None:
            self._values["template_configuration"] = template_configuration

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def admin_permissions(self) -> builtins.bool:
        '''(experimental) Whether to grant full permissions to CloudFormation while deploying this template.

        Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you
        don't specify any alternatives.

        The default role that will be created for you will have full (i.e., ``*``)
        permissions on all resources, and the deployment will have named IAM
        capabilities (i.e., able to create all IAM resources).

        This is a shorthand that you can use if you fully trust the templates that
        are deployed in this pipeline. If you want more fine-grained permissions,
        use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation
        deployment is allowed to do.

        :stability: experimental
        '''
        result = self._values.get("admin_permissions")
        assert result is not None, "Required property 'admin_permissions' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def stack_name(self) -> builtins.str:
        '''(experimental) The name of the stack to apply this action to.

        :stability: experimental
        '''
        result = self._values.get("stack_name")
        assert result is not None, "Required property 'stack_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template_path(self) -> _ArtifactPath_a5b79113:
        '''(experimental) Input artifact with the CloudFormation template to deploy.

        :stability: experimental
        '''
        result = self._values.get("template_path")
        assert result is not None, "Required property 'template_path' is missing"
        return typing.cast(_ArtifactPath_a5b79113, result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS account this Action is supposed to operate in.

        **Note**: if you specify the ``role`` property,
        this is ignored - the action will operate in the same region the passed role does.

        :default: - action resides in the same account as the pipeline

        :stability: experimental
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def capabilities(
        self,
    ) -> typing.Optional[typing.List[_CloudFormationCapabilities_149b400e]]:
        '''(deprecated) Acknowledge certain changes made as part of deployment.

        For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation
        might create or update those resources. For example, you must specify ``AnonymousIAM`` or ``NamedIAM``
        if your stack template contains AWS Identity and Access Management (IAM) resources. For more
        information see the link below.

        :default: None, unless ``adminPermissions`` is true

        :deprecated: use {@link cfnCapabilities} instead

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
        :stability: deprecated
        '''
        result = self._values.get("capabilities")
        return typing.cast(typing.Optional[typing.List[_CloudFormationCapabilities_149b400e]], result)

    @builtins.property
    def cfn_capabilities(
        self,
    ) -> typing.Optional[typing.List[_CfnCapabilities_6e018757]]:
        '''(experimental) Acknowledge certain changes made as part of deployment.

        For stacks that contain certain resources,
        explicit acknowledgement is required that AWS CloudFormation might create or update those resources.
        For example, you must specify ``ANONYMOUS_IAM`` or ``NAMED_IAM`` if your stack template contains AWS
        Identity and Access Management (IAM) resources.
        For more information, see the link below.

        :default: None, unless ``adminPermissions`` is true

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
        :stability: experimental
        '''
        result = self._values.get("cfn_capabilities")
        return typing.cast(typing.Optional[typing.List[_CfnCapabilities_6e018757]], result)

    @builtins.property
    def deployment_role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) IAM role to assume when deploying changes.

        If not specified, a fresh role is created. The role is created with zero
        permissions unless ``adminPermissions`` is true, in which case the role will have
        full permissions.

        :default: A fresh role with full or no permissions (depending on the value of ``adminPermissions``).

        :stability: experimental
        '''
        result = self._values.get("deployment_role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def extra_inputs(self) -> typing.Optional[typing.List[_Artifact_9905eec2]]:
        '''(experimental) The list of additional input Artifacts for this Action.

        This is especially useful when used in conjunction with the ``parameterOverrides`` property.
        For example, if you have:

        parameterOverrides: {
        'Param1': action1.outputArtifact.bucketName,
        'Param2': action2.outputArtifact.objectKey,
        }

        , if the output Artifacts of ``action1`` and ``action2`` were not used to
        set either the ``templateConfiguration`` or the ``templatePath`` properties,
        you need to make sure to include them in the ``extraInputs`` -
        otherwise, you'll get an "unrecognized Artifact" error during your Pipeline's execution.

        :stability: experimental
        '''
        result = self._values.get("extra_inputs")
        return typing.cast(typing.Optional[typing.List[_Artifact_9905eec2]], result)

    @builtins.property
    def output(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) The name of the output artifact to generate.

        Only applied if ``outputFileName`` is set as well.

        :default: Automatically generated artifact name.

        :stability: experimental
        '''
        result = self._values.get("output")
        return typing.cast(typing.Optional[_Artifact_9905eec2], result)

    @builtins.property
    def output_file_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result.

        The file will contain the result of the call to AWS CloudFormation (for example
        the call to UpdateStack or CreateChangeSet).

        AWS CodePipeline adds the file to the output artifact after performing
        the specified action.

        :default: No output artifact generated

        :stability: experimental
        '''
        result = self._values.get("output_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_overrides(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional template parameters.

        Template parameters specified here take precedence over template parameters
        found in the artifact specified by the ``templateConfiguration`` property.

        We recommend that you use the template configuration file to specify
        most of your parameter values. Use parameter overrides to specify only
        dynamic parameter values (values that are unknown until you run the
        pipeline).

        All parameter names must be present in the stack template.

        Note: the entire object cannot be more than 1kB.

        :default: No overrides

        :stability: experimental
        '''
        result = self._values.get("parameter_overrides")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS region the given Action resides in.

        Note that a cross-region Pipeline requires replication buckets to function correctly.
        You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property.
        If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets,
        that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack.

        :default: the Action resides in the same region as the Pipeline

        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replace_on_failure(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Replace the stack if it's in a failed state.

        If this is set to true and the stack is in a failed state (one of
        ROLLBACK_COMPLETE, ROLLBACK_FAILED, CREATE_FAILED, DELETE_FAILED, or
        UPDATE_ROLLBACK_FAILED), AWS CloudFormation deletes the stack and then
        creates a new stack.

        If this is not set to true and the stack is in a failed state,
        the deployment fails.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("replace_on_failure")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def template_configuration(self) -> typing.Optional[_ArtifactPath_a5b79113]:
        '''(experimental) Input artifact to use for template parameters values and stack policy.

        The template configuration file should contain a JSON object that should look like this:
        ``{ "Parameters": {...}, "Tags": {...}, "StackPolicy": {... }}``. For more information,
        see `AWS CloudFormation Artifacts <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html>`_.

        Note that if you include sensitive information, such as passwords, restrict access to this
        file.

        :default: No template configuration based on input artifacts

        :stability: experimental
        '''
        result = self._values.get("template_configuration")
        return typing.cast(typing.Optional[_ArtifactPath_a5b79113], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationCreateUpdateStackActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudFormationDeleteStackAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CloudFormationDeleteStackAction",
):
    '''(experimental) CodePipeline action to delete a stack.

    Deletes a stack. If you specify a stack that doesn't exist, the action completes successfully
    without deleting a stack.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import monocdk as monocdk
        from monocdk import aws_cloudformation as cloudformation
        from monocdk import aws_codepipeline as codepipeline
        from monocdk import aws_codepipeline_actions as codepipeline_actions
        from monocdk import aws_iam as iam
        
        # artifact: codepipeline.Artifact
        # artifact_path: codepipeline.ArtifactPath
        # parameter_overrides: Any
        # role: iam.Role
        
        cloud_formation_delete_stack_action = codepipeline_actions.CloudFormationDeleteStackAction(
            action_name="actionName",
            admin_permissions=False,
            stack_name="stackName",
        
            # the properties below are optional
            account="account",
            capabilities=[cloudformation.CloudFormationCapabilities.NONE],
            cfn_capabilities=[monocdk.CfnCapabilities.NONE],
            deployment_role=role,
            extra_inputs=[artifact],
            output=artifact,
            output_file_name="outputFileName",
            parameter_overrides={
                "parameter_overrides_key": parameter_overrides
            },
            region="region",
            role=role,
            run_order=123,
            template_configuration=artifact_path,
            variables_namespace="variablesNamespace"
        )
    '''

    def __init__(
        self,
        *,
        admin_permissions: builtins.bool,
        stack_name: builtins.str,
        account: typing.Optional[builtins.str] = None,
        capabilities: typing.Optional[typing.Sequence[_CloudFormationCapabilities_149b400e]] = None,
        cfn_capabilities: typing.Optional[typing.Sequence[_CfnCapabilities_6e018757]] = None,
        deployment_role: typing.Optional[_IRole_59af6f50] = None,
        extra_inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        output_file_name: typing.Optional[builtins.str] = None,
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        region: typing.Optional[builtins.str] = None,
        template_configuration: typing.Optional[_ArtifactPath_a5b79113] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param admin_permissions: (experimental) Whether to grant full permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have full (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
        :param stack_name: (experimental) The name of the stack to apply this action to.
        :param account: (experimental) The AWS account this Action is supposed to operate in. **Note**: if you specify the ``role`` property, this is ignored - the action will operate in the same region the passed role does. Default: - action resides in the same account as the pipeline
        :param capabilities: (deprecated) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify ``AnonymousIAM`` or ``NamedIAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information see the link below. Default: None, unless ``adminPermissions`` is true
        :param cfn_capabilities: (experimental) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement is required that AWS CloudFormation might create or update those resources. For example, you must specify ``ANONYMOUS_IAM`` or ``NAMED_IAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information, see the link below. Default: None, unless ``adminPermissions`` is true
        :param deployment_role: (experimental) IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have full permissions. Default: A fresh role with full or no permissions (depending on the value of ``adminPermissions``).
        :param extra_inputs: (experimental) The list of additional input Artifacts for this Action. This is especially useful when used in conjunction with the ``parameterOverrides`` property. For example, if you have: parameterOverrides: { 'Param1': action1.outputArtifact.bucketName, 'Param2': action2.outputArtifact.objectKey, } , if the output Artifacts of ``action1`` and ``action2`` were not used to set either the ``templateConfiguration`` or the ``templatePath`` properties, you need to make sure to include them in the ``extraInputs`` - otherwise, you'll get an "unrecognized Artifact" error during your Pipeline's execution.
        :param output: (experimental) The name of the output artifact to generate. Only applied if ``outputFileName`` is set as well. Default: Automatically generated artifact name.
        :param output_file_name: (experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result. The file will contain the result of the call to AWS CloudFormation (for example the call to UpdateStack or CreateChangeSet). AWS CodePipeline adds the file to the output artifact after performing the specified action. Default: No output artifact generated
        :param parameter_overrides: (experimental) Additional template parameters. Template parameters specified here take precedence over template parameters found in the artifact specified by the ``templateConfiguration`` property. We recommend that you use the template configuration file to specify most of your parameter values. Use parameter overrides to specify only dynamic parameter values (values that are unknown until you run the pipeline). All parameter names must be present in the stack template. Note: the entire object cannot be more than 1kB. Default: No overrides
        :param region: (experimental) The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param template_configuration: (experimental) Input artifact to use for template parameters values and stack policy. The template configuration file should contain a JSON object that should look like this: ``{ "Parameters": {...}, "Tags": {...}, "StackPolicy": {... }}``. For more information, see `AWS CloudFormation Artifacts <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html>`_. Note that if you include sensitive information, such as passwords, restrict access to this file. Default: No template configuration based on input artifacts
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = CloudFormationDeleteStackActionProps(
            admin_permissions=admin_permissions,
            stack_name=stack_name,
            account=account,
            capabilities=capabilities,
            cfn_capabilities=cfn_capabilities,
            deployment_role=deployment_role,
            extra_inputs=extra_inputs,
            output=output,
            output_file_name=output_file_name,
            parameter_overrides=parameter_overrides,
            region=region,
            template_configuration=template_configuration,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addToDeploymentRolePolicy")
    def add_to_deployment_role_policy(
        self,
        statement: _PolicyStatement_296fe8a3,
    ) -> builtins.bool:
        '''(experimental) Add statement to the service role assumed by CloudFormation while executing this action.

        :param statement: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "addToDeploymentRolePolicy", [statement]))

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [scope, stage, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deploymentRole")
    def deployment_role(self) -> _IRole_59af6f50:
        '''
        :stability: experimental
        '''
        return typing.cast(_IRole_59af6f50, jsii.get(self, "deploymentRole"))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CloudFormationDeleteStackActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "admin_permissions": "adminPermissions",
        "stack_name": "stackName",
        "account": "account",
        "capabilities": "capabilities",
        "cfn_capabilities": "cfnCapabilities",
        "deployment_role": "deploymentRole",
        "extra_inputs": "extraInputs",
        "output": "output",
        "output_file_name": "outputFileName",
        "parameter_overrides": "parameterOverrides",
        "region": "region",
        "template_configuration": "templateConfiguration",
    },
)
class CloudFormationDeleteStackActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        admin_permissions: builtins.bool,
        stack_name: builtins.str,
        account: typing.Optional[builtins.str] = None,
        capabilities: typing.Optional[typing.Sequence[_CloudFormationCapabilities_149b400e]] = None,
        cfn_capabilities: typing.Optional[typing.Sequence[_CfnCapabilities_6e018757]] = None,
        deployment_role: typing.Optional[_IRole_59af6f50] = None,
        extra_inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        output_file_name: typing.Optional[builtins.str] = None,
        parameter_overrides: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        region: typing.Optional[builtins.str] = None,
        template_configuration: typing.Optional[_ArtifactPath_a5b79113] = None,
    ) -> None:
        '''(experimental) Properties for the CloudFormationDeleteStackAction.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param admin_permissions: (experimental) Whether to grant full permissions to CloudFormation while deploying this template. Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you don't specify any alternatives. The default role that will be created for you will have full (i.e., ``*``) permissions on all resources, and the deployment will have named IAM capabilities (i.e., able to create all IAM resources). This is a shorthand that you can use if you fully trust the templates that are deployed in this pipeline. If you want more fine-grained permissions, use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation deployment is allowed to do.
        :param stack_name: (experimental) The name of the stack to apply this action to.
        :param account: (experimental) The AWS account this Action is supposed to operate in. **Note**: if you specify the ``role`` property, this is ignored - the action will operate in the same region the passed role does. Default: - action resides in the same account as the pipeline
        :param capabilities: (deprecated) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation might create or update those resources. For example, you must specify ``AnonymousIAM`` or ``NamedIAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information see the link below. Default: None, unless ``adminPermissions`` is true
        :param cfn_capabilities: (experimental) Acknowledge certain changes made as part of deployment. For stacks that contain certain resources, explicit acknowledgement is required that AWS CloudFormation might create or update those resources. For example, you must specify ``ANONYMOUS_IAM`` or ``NAMED_IAM`` if your stack template contains AWS Identity and Access Management (IAM) resources. For more information, see the link below. Default: None, unless ``adminPermissions`` is true
        :param deployment_role: (experimental) IAM role to assume when deploying changes. If not specified, a fresh role is created. The role is created with zero permissions unless ``adminPermissions`` is true, in which case the role will have full permissions. Default: A fresh role with full or no permissions (depending on the value of ``adminPermissions``).
        :param extra_inputs: (experimental) The list of additional input Artifacts for this Action. This is especially useful when used in conjunction with the ``parameterOverrides`` property. For example, if you have: parameterOverrides: { 'Param1': action1.outputArtifact.bucketName, 'Param2': action2.outputArtifact.objectKey, } , if the output Artifacts of ``action1`` and ``action2`` were not used to set either the ``templateConfiguration`` or the ``templatePath`` properties, you need to make sure to include them in the ``extraInputs`` - otherwise, you'll get an "unrecognized Artifact" error during your Pipeline's execution.
        :param output: (experimental) The name of the output artifact to generate. Only applied if ``outputFileName`` is set as well. Default: Automatically generated artifact name.
        :param output_file_name: (experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result. The file will contain the result of the call to AWS CloudFormation (for example the call to UpdateStack or CreateChangeSet). AWS CodePipeline adds the file to the output artifact after performing the specified action. Default: No output artifact generated
        :param parameter_overrides: (experimental) Additional template parameters. Template parameters specified here take precedence over template parameters found in the artifact specified by the ``templateConfiguration`` property. We recommend that you use the template configuration file to specify most of your parameter values. Use parameter overrides to specify only dynamic parameter values (values that are unknown until you run the pipeline). All parameter names must be present in the stack template. Note: the entire object cannot be more than 1kB. Default: No overrides
        :param region: (experimental) The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param template_configuration: (experimental) Input artifact to use for template parameters values and stack policy. The template configuration file should contain a JSON object that should look like this: ``{ "Parameters": {...}, "Tags": {...}, "StackPolicy": {... }}``. For more information, see `AWS CloudFormation Artifacts <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html>`_. Note that if you include sensitive information, such as passwords, restrict access to this file. Default: No template configuration based on input artifacts

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import monocdk as monocdk
            from monocdk import aws_cloudformation as cloudformation
            from monocdk import aws_codepipeline as codepipeline
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            from monocdk import aws_iam as iam
            
            # artifact: codepipeline.Artifact
            # artifact_path: codepipeline.ArtifactPath
            # parameter_overrides: Any
            # role: iam.Role
            
            cloud_formation_delete_stack_action_props = codepipeline_actions.CloudFormationDeleteStackActionProps(
                action_name="actionName",
                admin_permissions=False,
                stack_name="stackName",
            
                # the properties below are optional
                account="account",
                capabilities=[cloudformation.CloudFormationCapabilities.NONE],
                cfn_capabilities=[monocdk.CfnCapabilities.NONE],
                deployment_role=role,
                extra_inputs=[artifact],
                output=artifact,
                output_file_name="outputFileName",
                parameter_overrides={
                    "parameter_overrides_key": parameter_overrides
                },
                region="region",
                role=role,
                run_order=123,
                template_configuration=artifact_path,
                variables_namespace="variablesNamespace"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "admin_permissions": admin_permissions,
            "stack_name": stack_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if account is not None:
            self._values["account"] = account
        if capabilities is not None:
            self._values["capabilities"] = capabilities
        if cfn_capabilities is not None:
            self._values["cfn_capabilities"] = cfn_capabilities
        if deployment_role is not None:
            self._values["deployment_role"] = deployment_role
        if extra_inputs is not None:
            self._values["extra_inputs"] = extra_inputs
        if output is not None:
            self._values["output"] = output
        if output_file_name is not None:
            self._values["output_file_name"] = output_file_name
        if parameter_overrides is not None:
            self._values["parameter_overrides"] = parameter_overrides
        if region is not None:
            self._values["region"] = region
        if template_configuration is not None:
            self._values["template_configuration"] = template_configuration

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def admin_permissions(self) -> builtins.bool:
        '''(experimental) Whether to grant full permissions to CloudFormation while deploying this template.

        Setting this to ``true`` affects the defaults for ``role`` and ``capabilities``, if you
        don't specify any alternatives.

        The default role that will be created for you will have full (i.e., ``*``)
        permissions on all resources, and the deployment will have named IAM
        capabilities (i.e., able to create all IAM resources).

        This is a shorthand that you can use if you fully trust the templates that
        are deployed in this pipeline. If you want more fine-grained permissions,
        use ``addToRolePolicy`` and ``capabilities`` to control what the CloudFormation
        deployment is allowed to do.

        :stability: experimental
        '''
        result = self._values.get("admin_permissions")
        assert result is not None, "Required property 'admin_permissions' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def stack_name(self) -> builtins.str:
        '''(experimental) The name of the stack to apply this action to.

        :stability: experimental
        '''
        result = self._values.get("stack_name")
        assert result is not None, "Required property 'stack_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS account this Action is supposed to operate in.

        **Note**: if you specify the ``role`` property,
        this is ignored - the action will operate in the same region the passed role does.

        :default: - action resides in the same account as the pipeline

        :stability: experimental
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def capabilities(
        self,
    ) -> typing.Optional[typing.List[_CloudFormationCapabilities_149b400e]]:
        '''(deprecated) Acknowledge certain changes made as part of deployment.

        For stacks that contain certain resources, explicit acknowledgement that AWS CloudFormation
        might create or update those resources. For example, you must specify ``AnonymousIAM`` or ``NamedIAM``
        if your stack template contains AWS Identity and Access Management (IAM) resources. For more
        information see the link below.

        :default: None, unless ``adminPermissions`` is true

        :deprecated: use {@link cfnCapabilities} instead

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
        :stability: deprecated
        '''
        result = self._values.get("capabilities")
        return typing.cast(typing.Optional[typing.List[_CloudFormationCapabilities_149b400e]], result)

    @builtins.property
    def cfn_capabilities(
        self,
    ) -> typing.Optional[typing.List[_CfnCapabilities_6e018757]]:
        '''(experimental) Acknowledge certain changes made as part of deployment.

        For stacks that contain certain resources,
        explicit acknowledgement is required that AWS CloudFormation might create or update those resources.
        For example, you must specify ``ANONYMOUS_IAM`` or ``NAMED_IAM`` if your stack template contains AWS
        Identity and Access Management (IAM) resources.
        For more information, see the link below.

        :default: None, unless ``adminPermissions`` is true

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities
        :stability: experimental
        '''
        result = self._values.get("cfn_capabilities")
        return typing.cast(typing.Optional[typing.List[_CfnCapabilities_6e018757]], result)

    @builtins.property
    def deployment_role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) IAM role to assume when deploying changes.

        If not specified, a fresh role is created. The role is created with zero
        permissions unless ``adminPermissions`` is true, in which case the role will have
        full permissions.

        :default: A fresh role with full or no permissions (depending on the value of ``adminPermissions``).

        :stability: experimental
        '''
        result = self._values.get("deployment_role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def extra_inputs(self) -> typing.Optional[typing.List[_Artifact_9905eec2]]:
        '''(experimental) The list of additional input Artifacts for this Action.

        This is especially useful when used in conjunction with the ``parameterOverrides`` property.
        For example, if you have:

        parameterOverrides: {
        'Param1': action1.outputArtifact.bucketName,
        'Param2': action2.outputArtifact.objectKey,
        }

        , if the output Artifacts of ``action1`` and ``action2`` were not used to
        set either the ``templateConfiguration`` or the ``templatePath`` properties,
        you need to make sure to include them in the ``extraInputs`` -
        otherwise, you'll get an "unrecognized Artifact" error during your Pipeline's execution.

        :stability: experimental
        '''
        result = self._values.get("extra_inputs")
        return typing.cast(typing.Optional[typing.List[_Artifact_9905eec2]], result)

    @builtins.property
    def output(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) The name of the output artifact to generate.

        Only applied if ``outputFileName`` is set as well.

        :default: Automatically generated artifact name.

        :stability: experimental
        '''
        result = self._values.get("output")
        return typing.cast(typing.Optional[_Artifact_9905eec2], result)

    @builtins.property
    def output_file_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result.

        The file will contain the result of the call to AWS CloudFormation (for example
        the call to UpdateStack or CreateChangeSet).

        AWS CodePipeline adds the file to the output artifact after performing
        the specified action.

        :default: No output artifact generated

        :stability: experimental
        '''
        result = self._values.get("output_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter_overrides(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) Additional template parameters.

        Template parameters specified here take precedence over template parameters
        found in the artifact specified by the ``templateConfiguration`` property.

        We recommend that you use the template configuration file to specify
        most of your parameter values. Use parameter overrides to specify only
        dynamic parameter values (values that are unknown until you run the
        pipeline).

        All parameter names must be present in the stack template.

        Note: the entire object cannot be more than 1kB.

        :default: No overrides

        :stability: experimental
        '''
        result = self._values.get("parameter_overrides")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS region the given Action resides in.

        Note that a cross-region Pipeline requires replication buckets to function correctly.
        You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property.
        If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets,
        that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack.

        :default: the Action resides in the same region as the Pipeline

        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def template_configuration(self) -> typing.Optional[_ArtifactPath_a5b79113]:
        '''(experimental) Input artifact to use for template parameters values and stack policy.

        The template configuration file should contain a JSON object that should look like this:
        ``{ "Parameters": {...}, "Tags": {...}, "StackPolicy": {... }}``. For more information,
        see `AWS CloudFormation Artifacts <https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html>`_.

        Note that if you include sensitive information, such as passwords, restrict access to this
        file.

        :default: No template configuration based on input artifacts

        :stability: experimental
        '''
        result = self._values.get("template_configuration")
        return typing.cast(typing.Optional[_ArtifactPath_a5b79113], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationDeleteStackActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudFormationExecuteChangeSetAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CloudFormationExecuteChangeSetAction",
):
    '''(experimental) CodePipeline action to execute a prepared change set.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Deploy some CFN change set and store output
        execute_output = codepipeline.Artifact("CloudFormation")
        execute_change_set_action = codepipeline_actions.CloudFormationExecuteChangeSetAction(
            action_name="ExecuteChangesTest",
            run_order=2,
            stack_name="MyStack",
            change_set_name="MyChangeSet",
            output_file_name="overrides.json",
            output=execute_output
        )
        
        # Provide CFN output as manifest overrides
        client_id = SecretValue.secrets_manager("AlexaClientId")
        client_secret = SecretValue.secrets_manager("AlexaClientSecret")
        refresh_token = SecretValue.secrets_manager("AlexaRefreshToken")
        source_output = codepipeline.Artifact()
        codepipeline_actions.AlexaSkillDeployAction(
            action_name="DeploySkill",
            run_order=1,
            input=source_output,
            parameter_overrides_artifact=execute_output,
            client_id=client_id.to_string(),
            client_secret=client_secret,
            refresh_token=refresh_token,
            skill_id="amzn1.ask.skill.12345678-1234-1234-1234-123456789012"
        )
    '''

    def __init__(
        self,
        *,
        change_set_name: builtins.str,
        stack_name: builtins.str,
        account: typing.Optional[builtins.str] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        output_file_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param change_set_name: (experimental) Name of the change set to execute.
        :param stack_name: (experimental) The name of the stack to apply this action to.
        :param account: (experimental) The AWS account this Action is supposed to operate in. **Note**: if you specify the ``role`` property, this is ignored - the action will operate in the same region the passed role does. Default: - action resides in the same account as the pipeline
        :param output: (experimental) The name of the output artifact to generate. Only applied if ``outputFileName`` is set as well. Default: Automatically generated artifact name.
        :param output_file_name: (experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result. The file will contain the result of the call to AWS CloudFormation (for example the call to UpdateStack or CreateChangeSet). AWS CodePipeline adds the file to the output artifact after performing the specified action. Default: No output artifact generated
        :param region: (experimental) The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = CloudFormationExecuteChangeSetActionProps(
            change_set_name=change_set_name,
            stack_name=stack_name,
            account=account,
            output=output,
            output_file_name=output_file_name,
            region=region,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [scope, stage, options]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CloudFormationExecuteChangeSetActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "change_set_name": "changeSetName",
        "stack_name": "stackName",
        "account": "account",
        "output": "output",
        "output_file_name": "outputFileName",
        "region": "region",
    },
)
class CloudFormationExecuteChangeSetActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        change_set_name: builtins.str,
        stack_name: builtins.str,
        account: typing.Optional[builtins.str] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        output_file_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for the CloudFormationExecuteChangeSetAction.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param change_set_name: (experimental) Name of the change set to execute.
        :param stack_name: (experimental) The name of the stack to apply this action to.
        :param account: (experimental) The AWS account this Action is supposed to operate in. **Note**: if you specify the ``role`` property, this is ignored - the action will operate in the same region the passed role does. Default: - action resides in the same account as the pipeline
        :param output: (experimental) The name of the output artifact to generate. Only applied if ``outputFileName`` is set as well. Default: Automatically generated artifact name.
        :param output_file_name: (experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result. The file will contain the result of the call to AWS CloudFormation (for example the call to UpdateStack or CreateChangeSet). AWS CodePipeline adds the file to the output artifact after performing the specified action. Default: No output artifact generated
        :param region: (experimental) The AWS region the given Action resides in. Note that a cross-region Pipeline requires replication buckets to function correctly. You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property. If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets, that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack. Default: the Action resides in the same region as the Pipeline

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Deploy some CFN change set and store output
            execute_output = codepipeline.Artifact("CloudFormation")
            execute_change_set_action = codepipeline_actions.CloudFormationExecuteChangeSetAction(
                action_name="ExecuteChangesTest",
                run_order=2,
                stack_name="MyStack",
                change_set_name="MyChangeSet",
                output_file_name="overrides.json",
                output=execute_output
            )
            
            # Provide CFN output as manifest overrides
            client_id = SecretValue.secrets_manager("AlexaClientId")
            client_secret = SecretValue.secrets_manager("AlexaClientSecret")
            refresh_token = SecretValue.secrets_manager("AlexaRefreshToken")
            source_output = codepipeline.Artifact()
            codepipeline_actions.AlexaSkillDeployAction(
                action_name="DeploySkill",
                run_order=1,
                input=source_output,
                parameter_overrides_artifact=execute_output,
                client_id=client_id.to_string(),
                client_secret=client_secret,
                refresh_token=refresh_token,
                skill_id="amzn1.ask.skill.12345678-1234-1234-1234-123456789012"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "change_set_name": change_set_name,
            "stack_name": stack_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if account is not None:
            self._values["account"] = account
        if output is not None:
            self._values["output"] = output
        if output_file_name is not None:
            self._values["output_file_name"] = output_file_name
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def change_set_name(self) -> builtins.str:
        '''(experimental) Name of the change set to execute.

        :stability: experimental
        '''
        result = self._values.get("change_set_name")
        assert result is not None, "Required property 'change_set_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stack_name(self) -> builtins.str:
        '''(experimental) The name of the stack to apply this action to.

        :stability: experimental
        '''
        result = self._values.get("stack_name")
        assert result is not None, "Required property 'stack_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS account this Action is supposed to operate in.

        **Note**: if you specify the ``role`` property,
        this is ignored - the action will operate in the same region the passed role does.

        :default: - action resides in the same account as the pipeline

        :stability: experimental
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) The name of the output artifact to generate.

        Only applied if ``outputFileName`` is set as well.

        :default: Automatically generated artifact name.

        :stability: experimental
        '''
        result = self._values.get("output")
        return typing.cast(typing.Optional[_Artifact_9905eec2], result)

    @builtins.property
    def output_file_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the filename in the output artifact to store the AWS CloudFormation call's result.

        The file will contain the result of the call to AWS CloudFormation (for example
        the call to UpdateStack or CreateChangeSet).

        AWS CodePipeline adds the file to the output artifact after performing
        the specified action.

        :default: No output artifact generated

        :stability: experimental
        '''
        result = self._values.get("output_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The AWS region the given Action resides in.

        Note that a cross-region Pipeline requires replication buckets to function correctly.
        You can provide their names with the {@link PipelineProps#crossRegionReplicationBuckets} property.
        If you don't, the CodePipeline Construct will create new Stacks in your CDK app containing those buckets,
        that you will need to ``cdk deploy`` before deploying the main, Pipeline-containing Stack.

        :default: the Action resides in the same region as the Pipeline

        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationExecuteChangeSetActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeBuildAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CodeBuildAction",
):
    '''(experimental) CodePipeline build action that uses AWS CodeBuild.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # project: codebuild.PipelineProject
        
        repository = codecommit.Repository(self, "MyRepository",
            repository_name="MyRepository"
        )
        project = codebuild.PipelineProject(self, "MyProject")
        
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repository,
            output=source_output
        )
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project,
            input=source_output,
            outputs=[codepipeline.Artifact()],  # optional
            execute_batch_build=True,  # optional, defaults to false
            combine_batch_build_artifacts=True
        )
        
        codepipeline.Pipeline(self, "MyPipeline",
            stages=[codebuild.aws_codepipeline.StageProps(
                stage_name="Source",
                actions=[source_action]
            ), codebuild.aws_codepipeline.StageProps(
                stage_name="Build",
                actions=[build_action]
            )
            ]
        )
    '''

    def __init__(
        self,
        *,
        input: _Artifact_9905eec2,
        project: _IProject_6da8803e,
        check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
        combine_batch_build_artifacts: typing.Optional[builtins.bool] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, _BuildEnvironmentVariable_00095c97]] = None,
        execute_batch_build: typing.Optional[builtins.bool] = None,
        extra_inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        outputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        type: typing.Optional["CodeBuildActionType"] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param input: (experimental) The source to use as input for this action.
        :param project: (experimental) The action's Project.
        :param check_secrets_in_plain_text_env_variables: (experimental) Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable. Default: true
        :param combine_batch_build_artifacts: (experimental) Combine the build artifacts for a batch builds. Enabling this will combine the build artifacts into the same location for batch builds. If ``executeBatchBuild`` is not set to ``true``, this property is ignored. Default: false
        :param environment_variables: (experimental) The environment variables to pass to the CodeBuild project when this action executes. If a variable with the same name was set both on the project level, and here, this value will take precedence. Default: - No additional environment variables are specified.
        :param execute_batch_build: (experimental) Trigger a batch build. Enabling this will enable batch builds on the CodeBuild project. Default: false
        :param extra_inputs: (experimental) The list of additional input Artifacts for this action. The directories the additional inputs will be available at are available during the project's build in the CODEBUILD_SRC_DIR_ environment variables. The project's build always starts in the directory with the primary input artifact checked out, the one pointed to by the {@link input} property. For more information, see https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html .
        :param outputs: (experimental) The list of output Artifacts for this action. **Note**: if you specify more than one output Artifact here, you cannot use the primary 'artifacts' section of the buildspec; you have to use the 'secondary-artifacts' section instead. See https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html for details. Default: the action will not have any outputs
        :param type: (experimental) The type of the action that determines its CodePipeline Category - Build, or Test. Default: CodeBuildActionType.BUILD
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = CodeBuildActionProps(
            input=input,
            project=project,
            check_secrets_in_plain_text_env_variables=check_secrets_in_plain_text_env_variables,
            combine_batch_build_artifacts=combine_batch_build_artifacts,
            environment_variables=environment_variables,
            execute_batch_build=execute_batch_build,
            extra_inputs=extra_inputs,
            outputs=outputs,
            type=type,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [scope, _stage, options]))

    @jsii.member(jsii_name="variable")
    def variable(self, variable_name: builtins.str) -> builtins.str:
        '''(experimental) Reference a CodePipeline variable defined by the CodeBuild project this action points to.

        Variables in CodeBuild actions are defined using the 'exported-variables' subsection of the 'env'
        section of the buildspec.

        :param variable_name: the name of the variable to reference. A variable by this name must be present in the 'exported-variables' section of the buildspec

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec-ref-syntax
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "variable", [variable_name]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CodeBuildActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "input": "input",
        "project": "project",
        "check_secrets_in_plain_text_env_variables": "checkSecretsInPlainTextEnvVariables",
        "combine_batch_build_artifacts": "combineBatchBuildArtifacts",
        "environment_variables": "environmentVariables",
        "execute_batch_build": "executeBatchBuild",
        "extra_inputs": "extraInputs",
        "outputs": "outputs",
        "type": "type",
    },
)
class CodeBuildActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        input: _Artifact_9905eec2,
        project: _IProject_6da8803e,
        check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
        combine_batch_build_artifacts: typing.Optional[builtins.bool] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, _BuildEnvironmentVariable_00095c97]] = None,
        execute_batch_build: typing.Optional[builtins.bool] = None,
        extra_inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        outputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        type: typing.Optional["CodeBuildActionType"] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link CodeBuildAction CodeBuild build CodePipeline action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param input: (experimental) The source to use as input for this action.
        :param project: (experimental) The action's Project.
        :param check_secrets_in_plain_text_env_variables: (experimental) Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable. Default: true
        :param combine_batch_build_artifacts: (experimental) Combine the build artifacts for a batch builds. Enabling this will combine the build artifacts into the same location for batch builds. If ``executeBatchBuild`` is not set to ``true``, this property is ignored. Default: false
        :param environment_variables: (experimental) The environment variables to pass to the CodeBuild project when this action executes. If a variable with the same name was set both on the project level, and here, this value will take precedence. Default: - No additional environment variables are specified.
        :param execute_batch_build: (experimental) Trigger a batch build. Enabling this will enable batch builds on the CodeBuild project. Default: false
        :param extra_inputs: (experimental) The list of additional input Artifacts for this action. The directories the additional inputs will be available at are available during the project's build in the CODEBUILD_SRC_DIR_ environment variables. The project's build always starts in the directory with the primary input artifact checked out, the one pointed to by the {@link input} property. For more information, see https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html .
        :param outputs: (experimental) The list of output Artifacts for this action. **Note**: if you specify more than one output Artifact here, you cannot use the primary 'artifacts' section of the buildspec; you have to use the 'secondary-artifacts' section instead. See https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html for details. Default: the action will not have any outputs
        :param type: (experimental) The type of the action that determines its CodePipeline Category - Build, or Test. Default: CodeBuildActionType.BUILD

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # project: codebuild.PipelineProject
            
            repository = codecommit.Repository(self, "MyRepository",
                repository_name="MyRepository"
            )
            project = codebuild.PipelineProject(self, "MyProject")
            
            source_output = codepipeline.Artifact()
            source_action = codepipeline_actions.CodeCommitSourceAction(
                action_name="CodeCommit",
                repository=repository,
                output=source_output
            )
            build_action = codepipeline_actions.CodeBuildAction(
                action_name="CodeBuild",
                project=project,
                input=source_output,
                outputs=[codepipeline.Artifact()],  # optional
                execute_batch_build=True,  # optional, defaults to false
                combine_batch_build_artifacts=True
            )
            
            codepipeline.Pipeline(self, "MyPipeline",
                stages=[codebuild.aws_codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action]
                ), codebuild.aws_codepipeline.StageProps(
                    stage_name="Build",
                    actions=[build_action]
                )
                ]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "input": input,
            "project": project,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if check_secrets_in_plain_text_env_variables is not None:
            self._values["check_secrets_in_plain_text_env_variables"] = check_secrets_in_plain_text_env_variables
        if combine_batch_build_artifacts is not None:
            self._values["combine_batch_build_artifacts"] = combine_batch_build_artifacts
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if execute_batch_build is not None:
            self._values["execute_batch_build"] = execute_batch_build
        if extra_inputs is not None:
            self._values["extra_inputs"] = extra_inputs
        if outputs is not None:
            self._values["outputs"] = outputs
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def input(self) -> _Artifact_9905eec2:
        '''(experimental) The source to use as input for this action.

        :stability: experimental
        '''
        result = self._values.get("input")
        assert result is not None, "Required property 'input' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def project(self) -> _IProject_6da8803e:
        '''(experimental) The action's Project.

        :stability: experimental
        '''
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(_IProject_6da8803e, result)

    @builtins.property
    def check_secrets_in_plain_text_env_variables(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("check_secrets_in_plain_text_env_variables")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def combine_batch_build_artifacts(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Combine the build artifacts for a batch builds.

        Enabling this will combine the build artifacts into the same location for batch builds.
        If ``executeBatchBuild`` is not set to ``true``, this property is ignored.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("combine_batch_build_artifacts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, _BuildEnvironmentVariable_00095c97]]:
        '''(experimental) The environment variables to pass to the CodeBuild project when this action executes.

        If a variable with the same name was set both on the project level, and here,
        this value will take precedence.

        :default: - No additional environment variables are specified.

        :stability: experimental
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, _BuildEnvironmentVariable_00095c97]], result)

    @builtins.property
    def execute_batch_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Trigger a batch build.

        Enabling this will enable batch builds on the CodeBuild project.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("execute_batch_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def extra_inputs(self) -> typing.Optional[typing.List[_Artifact_9905eec2]]:
        '''(experimental) The list of additional input Artifacts for this action.

        The directories the additional inputs will be available at are available
        during the project's build in the CODEBUILD_SRC_DIR_ environment variables.
        The project's build always starts in the directory with the primary input artifact checked out,
        the one pointed to by the {@link input} property.
        For more information,
        see https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html .

        :stability: experimental
        '''
        result = self._values.get("extra_inputs")
        return typing.cast(typing.Optional[typing.List[_Artifact_9905eec2]], result)

    @builtins.property
    def outputs(self) -> typing.Optional[typing.List[_Artifact_9905eec2]]:
        '''(experimental) The list of output Artifacts for this action.

        **Note**: if you specify more than one output Artifact here,
        you cannot use the primary 'artifacts' section of the buildspec;
        you have to use the 'secondary-artifacts' section instead.
        See https://docs.aws.amazon.com/codebuild/latest/userguide/sample-multi-in-out.html
        for details.

        :default: the action will not have any outputs

        :stability: experimental
        '''
        result = self._values.get("outputs")
        return typing.cast(typing.Optional[typing.List[_Artifact_9905eec2]], result)

    @builtins.property
    def type(self) -> typing.Optional["CodeBuildActionType"]:
        '''(experimental) The type of the action that determines its CodePipeline Category - Build, or Test.

        :default: CodeBuildActionType.BUILD

        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["CodeBuildActionType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeBuildActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_codepipeline_actions.CodeBuildActionType")
class CodeBuildActionType(enum.Enum):
    '''(experimental) The type of the CodeBuild action that determines its CodePipeline Category - Build, or Test.

    The default is Build.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # project: codebuild.PipelineProject
        
        source_output = codepipeline.Artifact()
        test_action = codepipeline_actions.CodeBuildAction(
            action_name="IntegrationTest",
            project=project,
            input=source_output,
            type=codepipeline_actions.CodeBuildActionType.TEST
        )
    '''

    BUILD = "BUILD"
    '''(experimental) The action will have the Build Category.

    This is the default.

    :stability: experimental
    '''
    TEST = "TEST"
    '''(experimental) The action will have the Test Category.

    :stability: experimental
    '''


class CodeCommitSourceAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CodeCommitSourceAction",
):
    '''(experimental) CodePipeline Source that is provided by an AWS CodeCommit repository.

    If the CodeCommit repository is in a different account, you must use
    ``CodeCommitTrigger.EVENTS`` to trigger the pipeline.

    (That is because the Pipeline structure normally only has a ``RepositoryName``
    field, and that is not enough for the pipeline to locate the repository's
    source account. However, if the pipeline is triggered via an EventBridge
    event, the event itself has the full repository ARN in there, allowing the
    pipeline to locate the repository).

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # project: codebuild.PipelineProject
        # repo: codecommit.Repository
        
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repo,
            output=source_output,
            code_build_clone_output=True
        )
        
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project,
            input=source_output,  # The build action must use the CodeCommitSourceAction output as input.
            outputs=[codepipeline.Artifact()]
        )
    '''

    def __init__(
        self,
        *,
        output: _Artifact_9905eec2,
        repository: _IRepository_cdb2a3c0,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        event_role: typing.Optional[_IRole_59af6f50] = None,
        trigger: typing.Optional["CodeCommitTrigger"] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param output: 
        :param repository: (experimental) The CodeCommit repository.
        :param branch: Default: 'master'
        :param code_build_clone_output: (experimental) Whether the output should be the contents of the repository (which is the default), or a link that allows CodeBuild to clone the repository before building. **Note**: if this option is true, then only CodeBuild actions can use the resulting {@link output}. Default: false
        :param event_role: (experimental) Role to be used by on commit event rule. Used only when trigger value is CodeCommitTrigger.EVENTS. Default: a new role will be created.
        :param trigger: (experimental) How should CodePipeline detect source changes for this Action. Default: CodeCommitTrigger.EVENTS
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = CodeCommitSourceActionProps(
            output=output,
            repository=repository,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            event_role=event_role,
            trigger=trigger,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, stage, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variables")
    def variables(self) -> "CodeCommitSourceVariables":
        '''(experimental) The variables emitted by this action.

        :stability: experimental
        '''
        return typing.cast("CodeCommitSourceVariables", jsii.get(self, "variables"))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CodeCommitSourceActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "output": "output",
        "repository": "repository",
        "branch": "branch",
        "code_build_clone_output": "codeBuildCloneOutput",
        "event_role": "eventRole",
        "trigger": "trigger",
    },
)
class CodeCommitSourceActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        output: _Artifact_9905eec2,
        repository: _IRepository_cdb2a3c0,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        event_role: typing.Optional[_IRole_59af6f50] = None,
        trigger: typing.Optional["CodeCommitTrigger"] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link CodeCommitSourceAction CodeCommit source CodePipeline Action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param output: 
        :param repository: (experimental) The CodeCommit repository.
        :param branch: Default: 'master'
        :param code_build_clone_output: (experimental) Whether the output should be the contents of the repository (which is the default), or a link that allows CodeBuild to clone the repository before building. **Note**: if this option is true, then only CodeBuild actions can use the resulting {@link output}. Default: false
        :param event_role: (experimental) Role to be used by on commit event rule. Used only when trigger value is CodeCommitTrigger.EVENTS. Default: a new role will be created.
        :param trigger: (experimental) How should CodePipeline detect source changes for this Action. Default: CodeCommitTrigger.EVENTS

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # project: codebuild.PipelineProject
            # repo: codecommit.Repository
            
            source_output = codepipeline.Artifact()
            source_action = codepipeline_actions.CodeCommitSourceAction(
                action_name="CodeCommit",
                repository=repo,
                output=source_output,
                code_build_clone_output=True
            )
            
            build_action = codepipeline_actions.CodeBuildAction(
                action_name="CodeBuild",
                project=project,
                input=source_output,  # The build action must use the CodeCommitSourceAction output as input.
                outputs=[codepipeline.Artifact()]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "output": output,
            "repository": repository,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if branch is not None:
            self._values["branch"] = branch
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if event_role is not None:
            self._values["event_role"] = event_role
        if trigger is not None:
            self._values["trigger"] = trigger

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def output(self) -> _Artifact_9905eec2:
        '''
        :stability: experimental
        '''
        result = self._values.get("output")
        assert result is not None, "Required property 'output' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def repository(self) -> _IRepository_cdb2a3c0:
        '''(experimental) The CodeCommit repository.

        :stability: experimental
        '''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(_IRepository_cdb2a3c0, result)

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''
        :default: 'master'

        :stability: experimental
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the output should be the contents of the repository (which is the default), or a link that allows CodeBuild to clone the repository before building.

        **Note**: if this option is true,
        then only CodeBuild actions can use the resulting {@link output}.

        :default: false

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodeCommit.html
        :stability: experimental
        '''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def event_role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) Role to be used by on commit event rule.

        Used only when trigger value is CodeCommitTrigger.EVENTS.

        :default: a new role will be created.

        :stability: experimental
        '''
        result = self._values.get("event_role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def trigger(self) -> typing.Optional["CodeCommitTrigger"]:
        '''(experimental) How should CodePipeline detect source changes for this Action.

        :default: CodeCommitTrigger.EVENTS

        :stability: experimental
        '''
        result = self._values.get("trigger")
        return typing.cast(typing.Optional["CodeCommitTrigger"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeCommitSourceActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CodeCommitSourceVariables",
    jsii_struct_bases=[],
    name_mapping={
        "author_date": "authorDate",
        "branch_name": "branchName",
        "commit_id": "commitId",
        "commit_message": "commitMessage",
        "committer_date": "committerDate",
        "repository_name": "repositoryName",
    },
)
class CodeCommitSourceVariables:
    def __init__(
        self,
        *,
        author_date: builtins.str,
        branch_name: builtins.str,
        commit_id: builtins.str,
        commit_message: builtins.str,
        committer_date: builtins.str,
        repository_name: builtins.str,
    ) -> None:
        '''(experimental) The CodePipeline variables emitted by the CodeCommit source Action.

        :param author_date: (experimental) The date the currently last commit on the tracked branch was authored, in ISO-8601 format.
        :param branch_name: (experimental) The name of the branch this action tracks.
        :param commit_id: (experimental) The SHA1 hash of the currently last commit on the tracked branch.
        :param commit_message: (experimental) The message of the currently last commit on the tracked branch.
        :param committer_date: (experimental) The date the currently last commit on the tracked branch was committed, in ISO-8601 format.
        :param repository_name: (experimental) The name of the repository this action points to.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            
            code_commit_source_variables = codepipeline_actions.CodeCommitSourceVariables(
                author_date="authorDate",
                branch_name="branchName",
                commit_id="commitId",
                commit_message="commitMessage",
                committer_date="committerDate",
                repository_name="repositoryName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "author_date": author_date,
            "branch_name": branch_name,
            "commit_id": commit_id,
            "commit_message": commit_message,
            "committer_date": committer_date,
            "repository_name": repository_name,
        }

    @builtins.property
    def author_date(self) -> builtins.str:
        '''(experimental) The date the currently last commit on the tracked branch was authored, in ISO-8601 format.

        :stability: experimental
        '''
        result = self._values.get("author_date")
        assert result is not None, "Required property 'author_date' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_name(self) -> builtins.str:
        '''(experimental) The name of the branch this action tracks.

        :stability: experimental
        '''
        result = self._values.get("branch_name")
        assert result is not None, "Required property 'branch_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_id(self) -> builtins.str:
        '''(experimental) The SHA1 hash of the currently last commit on the tracked branch.

        :stability: experimental
        '''
        result = self._values.get("commit_id")
        assert result is not None, "Required property 'commit_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_message(self) -> builtins.str:
        '''(experimental) The message of the currently last commit on the tracked branch.

        :stability: experimental
        '''
        result = self._values.get("commit_message")
        assert result is not None, "Required property 'commit_message' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def committer_date(self) -> builtins.str:
        '''(experimental) The date the currently last commit on the tracked branch was committed, in ISO-8601 format.

        :stability: experimental
        '''
        result = self._values.get("committer_date")
        assert result is not None, "Required property 'committer_date' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''(experimental) The name of the repository this action points to.

        :stability: experimental
        '''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeCommitSourceVariables(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_codepipeline_actions.CodeCommitTrigger")
class CodeCommitTrigger(enum.Enum):
    '''(experimental) How should the CodeCommit Action detect changes.

    This is the type of the {@link CodeCommitSourceAction.trigger} property.

    :stability: experimental
    '''

    NONE = "NONE"
    '''(experimental) The Action will never detect changes - the Pipeline it's part of will only begin a run when explicitly started.

    :stability: experimental
    '''
    POLL = "POLL"
    '''(experimental) CodePipeline will poll the repository to detect changes.

    :stability: experimental
    '''
    EVENTS = "EVENTS"
    '''(experimental) CodePipeline will use CloudWatch Events to be notified of changes.

    This is the default method of detecting changes.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CodeDeployEcsContainerImageInput",
    jsii_struct_bases=[],
    name_mapping={
        "input": "input",
        "task_definition_placeholder": "taskDefinitionPlaceholder",
    },
)
class CodeDeployEcsContainerImageInput:
    def __init__(
        self,
        *,
        input: _Artifact_9905eec2,
        task_definition_placeholder: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Configuration for replacing a placeholder string in the ECS task definition template file with an image URI.

        :param input: (experimental) The artifact that contains an ``imageDetails.json`` file with the image URI. The artifact's ``imageDetails.json`` file must be a JSON file containing an ``ImageURI`` property. For example: ``{ "ImageURI": "ACCOUNTID.dkr.ecr.us-west-2.amazonaws.com/dk-image-repo@sha256:example3" }``
        :param task_definition_placeholder: (experimental) The placeholder string in the ECS task definition template file that will be replaced with the image URI. The placeholder string must be surrounded by angle brackets in the template file. For example, if the task definition template file contains a placeholder like ``"image": "<PLACEHOLDER>"``, then the ``taskDefinitionPlaceholder`` value should be ``PLACEHOLDER``. Default: IMAGE

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_codepipeline as codepipeline
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            
            # artifact: codepipeline.Artifact
            
            code_deploy_ecs_container_image_input = codepipeline_actions.CodeDeployEcsContainerImageInput(
                input=artifact,
            
                # the properties below are optional
                task_definition_placeholder="taskDefinitionPlaceholder"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "input": input,
        }
        if task_definition_placeholder is not None:
            self._values["task_definition_placeholder"] = task_definition_placeholder

    @builtins.property
    def input(self) -> _Artifact_9905eec2:
        '''(experimental) The artifact that contains an ``imageDetails.json`` file with the image URI.

        The artifact's ``imageDetails.json`` file must be a JSON file containing an
        ``ImageURI`` property.  For example:
        ``{ "ImageURI": "ACCOUNTID.dkr.ecr.us-west-2.amazonaws.com/dk-image-repo@sha256:example3" }``

        :stability: experimental
        '''
        result = self._values.get("input")
        assert result is not None, "Required property 'input' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def task_definition_placeholder(self) -> typing.Optional[builtins.str]:
        '''(experimental) The placeholder string in the ECS task definition template file that will be replaced with the image URI.

        The placeholder string must be surrounded by angle brackets in the template file.
        For example, if the task definition template file contains a placeholder like
        ``"image": "<PLACEHOLDER>"``, then the ``taskDefinitionPlaceholder`` value should
        be ``PLACEHOLDER``.

        :default: IMAGE

        :stability: experimental
        '''
        result = self._values.get("task_definition_placeholder")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeDeployEcsContainerImageInput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeDeployEcsDeployAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CodeDeployEcsDeployAction",
):
    '''
    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_codedeploy as codedeploy
        from monocdk import aws_codepipeline as codepipeline
        from monocdk import aws_codepipeline_actions as codepipeline_actions
        from monocdk import aws_iam as iam
        
        # artifact: codepipeline.Artifact
        # artifact_path: codepipeline.ArtifactPath
        # ecs_deployment_group: codedeploy.IEcsDeploymentGroup
        # role: iam.Role
        
        code_deploy_ecs_deploy_action = codepipeline_actions.CodeDeployEcsDeployAction(
            action_name="actionName",
            deployment_group=ecs_deployment_group,
        
            # the properties below are optional
            app_spec_template_file=artifact_path,
            app_spec_template_input=artifact,
            container_image_inputs=[codepipeline_actions.CodeDeployEcsContainerImageInput(
                input=artifact,
        
                # the properties below are optional
                task_definition_placeholder="taskDefinitionPlaceholder"
            )],
            role=role,
            run_order=123,
            task_definition_template_file=artifact_path,
            task_definition_template_input=artifact,
            variables_namespace="variablesNamespace"
        )
    '''

    def __init__(
        self,
        *,
        deployment_group: _IEcsDeploymentGroup_538bcae2,
        app_spec_template_file: typing.Optional[_ArtifactPath_a5b79113] = None,
        app_spec_template_input: typing.Optional[_Artifact_9905eec2] = None,
        container_image_inputs: typing.Optional[typing.Sequence[CodeDeployEcsContainerImageInput]] = None,
        task_definition_template_file: typing.Optional[_ArtifactPath_a5b79113] = None,
        task_definition_template_input: typing.Optional[_Artifact_9905eec2] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployment_group: (experimental) The CodeDeploy ECS Deployment Group to deploy to.
        :param app_spec_template_file: (experimental) The name of the CodeDeploy AppSpec file. During deployment, a new task definition will be registered with ECS, and the new task definition ID will be inserted into the CodeDeploy AppSpec file. The AppSpec file contents will be provided to CodeDeploy for the deployment. Use this property if you want to use a different name for this file than the default 'appspec.yaml'. If you use this property, you don't need to specify the ``appSpecTemplateInput`` property. Default: - one of this property, or ``appSpecTemplateInput``, is required
        :param app_spec_template_input: (experimental) The artifact containing the CodeDeploy AppSpec file. During deployment, a new task definition will be registered with ECS, and the new task definition ID will be inserted into the CodeDeploy AppSpec file. The AppSpec file contents will be provided to CodeDeploy for the deployment. If you use this property, it's assumed the file is called 'appspec.yaml'. If your AppSpec file uses a different filename, leave this property empty, and use the ``appSpecTemplateFile`` property instead. Default: - one of this property, or ``appSpecTemplateFile``, is required
        :param container_image_inputs: (experimental) Configuration for dynamically updated images in the task definition. Provide pairs of an image details input artifact and a placeholder string that will be used to dynamically update the ECS task definition template file prior to deployment. A maximum of 4 images can be given.
        :param task_definition_template_file: (experimental) The name of the ECS task definition template file. During deployment, the task definition template file contents will be registered with ECS. Use this property if you want to use a different name for this file than the default 'taskdef.json'. If you use this property, you don't need to specify the ``taskDefinitionTemplateInput`` property. Default: - one of this property, or ``taskDefinitionTemplateInput``, is required
        :param task_definition_template_input: (experimental) The artifact containing the ECS task definition template file. During deployment, the task definition template file contents will be registered with ECS. If you use this property, it's assumed the file is called 'taskdef.json'. If your task definition template uses a different filename, leave this property empty, and use the ``taskDefinitionTemplateFile`` property instead. Default: - one of this property, or ``taskDefinitionTemplateFile``, is required
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = CodeDeployEcsDeployActionProps(
            deployment_group=deployment_group,
            app_spec_template_file=app_spec_template_file,
            app_spec_template_input=app_spec_template_input,
            container_image_inputs=container_image_inputs,
            task_definition_template_file=task_definition_template_file,
            task_definition_template_input=task_definition_template_input,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, _stage, options]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CodeDeployEcsDeployActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "deployment_group": "deploymentGroup",
        "app_spec_template_file": "appSpecTemplateFile",
        "app_spec_template_input": "appSpecTemplateInput",
        "container_image_inputs": "containerImageInputs",
        "task_definition_template_file": "taskDefinitionTemplateFile",
        "task_definition_template_input": "taskDefinitionTemplateInput",
    },
)
class CodeDeployEcsDeployActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        deployment_group: _IEcsDeploymentGroup_538bcae2,
        app_spec_template_file: typing.Optional[_ArtifactPath_a5b79113] = None,
        app_spec_template_input: typing.Optional[_Artifact_9905eec2] = None,
        container_image_inputs: typing.Optional[typing.Sequence[CodeDeployEcsContainerImageInput]] = None,
        task_definition_template_file: typing.Optional[_ArtifactPath_a5b79113] = None,
        task_definition_template_input: typing.Optional[_Artifact_9905eec2] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link CodeDeployEcsDeployAction CodeDeploy ECS deploy CodePipeline Action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param deployment_group: (experimental) The CodeDeploy ECS Deployment Group to deploy to.
        :param app_spec_template_file: (experimental) The name of the CodeDeploy AppSpec file. During deployment, a new task definition will be registered with ECS, and the new task definition ID will be inserted into the CodeDeploy AppSpec file. The AppSpec file contents will be provided to CodeDeploy for the deployment. Use this property if you want to use a different name for this file than the default 'appspec.yaml'. If you use this property, you don't need to specify the ``appSpecTemplateInput`` property. Default: - one of this property, or ``appSpecTemplateInput``, is required
        :param app_spec_template_input: (experimental) The artifact containing the CodeDeploy AppSpec file. During deployment, a new task definition will be registered with ECS, and the new task definition ID will be inserted into the CodeDeploy AppSpec file. The AppSpec file contents will be provided to CodeDeploy for the deployment. If you use this property, it's assumed the file is called 'appspec.yaml'. If your AppSpec file uses a different filename, leave this property empty, and use the ``appSpecTemplateFile`` property instead. Default: - one of this property, or ``appSpecTemplateFile``, is required
        :param container_image_inputs: (experimental) Configuration for dynamically updated images in the task definition. Provide pairs of an image details input artifact and a placeholder string that will be used to dynamically update the ECS task definition template file prior to deployment. A maximum of 4 images can be given.
        :param task_definition_template_file: (experimental) The name of the ECS task definition template file. During deployment, the task definition template file contents will be registered with ECS. Use this property if you want to use a different name for this file than the default 'taskdef.json'. If you use this property, you don't need to specify the ``taskDefinitionTemplateInput`` property. Default: - one of this property, or ``taskDefinitionTemplateInput``, is required
        :param task_definition_template_input: (experimental) The artifact containing the ECS task definition template file. During deployment, the task definition template file contents will be registered with ECS. If you use this property, it's assumed the file is called 'taskdef.json'. If your task definition template uses a different filename, leave this property empty, and use the ``taskDefinitionTemplateFile`` property instead. Default: - one of this property, or ``taskDefinitionTemplateFile``, is required

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_codedeploy as codedeploy
            from monocdk import aws_codepipeline as codepipeline
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            from monocdk import aws_iam as iam
            
            # artifact: codepipeline.Artifact
            # artifact_path: codepipeline.ArtifactPath
            # ecs_deployment_group: codedeploy.IEcsDeploymentGroup
            # role: iam.Role
            
            code_deploy_ecs_deploy_action_props = codepipeline_actions.CodeDeployEcsDeployActionProps(
                action_name="actionName",
                deployment_group=ecs_deployment_group,
            
                # the properties below are optional
                app_spec_template_file=artifact_path,
                app_spec_template_input=artifact,
                container_image_inputs=[codepipeline_actions.CodeDeployEcsContainerImageInput(
                    input=artifact,
            
                    # the properties below are optional
                    task_definition_placeholder="taskDefinitionPlaceholder"
                )],
                role=role,
                run_order=123,
                task_definition_template_file=artifact_path,
                task_definition_template_input=artifact,
                variables_namespace="variablesNamespace"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "deployment_group": deployment_group,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if app_spec_template_file is not None:
            self._values["app_spec_template_file"] = app_spec_template_file
        if app_spec_template_input is not None:
            self._values["app_spec_template_input"] = app_spec_template_input
        if container_image_inputs is not None:
            self._values["container_image_inputs"] = container_image_inputs
        if task_definition_template_file is not None:
            self._values["task_definition_template_file"] = task_definition_template_file
        if task_definition_template_input is not None:
            self._values["task_definition_template_input"] = task_definition_template_input

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def deployment_group(self) -> _IEcsDeploymentGroup_538bcae2:
        '''(experimental) The CodeDeploy ECS Deployment Group to deploy to.

        :stability: experimental
        '''
        result = self._values.get("deployment_group")
        assert result is not None, "Required property 'deployment_group' is missing"
        return typing.cast(_IEcsDeploymentGroup_538bcae2, result)

    @builtins.property
    def app_spec_template_file(self) -> typing.Optional[_ArtifactPath_a5b79113]:
        '''(experimental) The name of the CodeDeploy AppSpec file.

        During deployment, a new task definition will be registered
        with ECS, and the new task definition ID will be inserted into
        the CodeDeploy AppSpec file.  The AppSpec file contents will be
        provided to CodeDeploy for the deployment.

        Use this property if you want to use a different name for this file than the default 'appspec.yaml'.
        If you use this property, you don't need to specify the ``appSpecTemplateInput`` property.

        :default: - one of this property, or ``appSpecTemplateInput``, is required

        :stability: experimental
        '''
        result = self._values.get("app_spec_template_file")
        return typing.cast(typing.Optional[_ArtifactPath_a5b79113], result)

    @builtins.property
    def app_spec_template_input(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) The artifact containing the CodeDeploy AppSpec file.

        During deployment, a new task definition will be registered
        with ECS, and the new task definition ID will be inserted into
        the CodeDeploy AppSpec file.  The AppSpec file contents will be
        provided to CodeDeploy for the deployment.

        If you use this property, it's assumed the file is called 'appspec.yaml'.
        If your AppSpec file uses a different filename, leave this property empty,
        and use the ``appSpecTemplateFile`` property instead.

        :default: - one of this property, or ``appSpecTemplateFile``, is required

        :stability: experimental
        '''
        result = self._values.get("app_spec_template_input")
        return typing.cast(typing.Optional[_Artifact_9905eec2], result)

    @builtins.property
    def container_image_inputs(
        self,
    ) -> typing.Optional[typing.List[CodeDeployEcsContainerImageInput]]:
        '''(experimental) Configuration for dynamically updated images in the task definition.

        Provide pairs of an image details input artifact and a placeholder string
        that will be used to dynamically update the ECS task definition template
        file prior to deployment. A maximum of 4 images can be given.

        :stability: experimental
        '''
        result = self._values.get("container_image_inputs")
        return typing.cast(typing.Optional[typing.List[CodeDeployEcsContainerImageInput]], result)

    @builtins.property
    def task_definition_template_file(self) -> typing.Optional[_ArtifactPath_a5b79113]:
        '''(experimental) The name of the ECS task definition template file.

        During deployment, the task definition template file contents
        will be registered with ECS.

        Use this property if you want to use a different name for this file than the default 'taskdef.json'.
        If you use this property, you don't need to specify the ``taskDefinitionTemplateInput`` property.

        :default: - one of this property, or ``taskDefinitionTemplateInput``, is required

        :stability: experimental
        '''
        result = self._values.get("task_definition_template_file")
        return typing.cast(typing.Optional[_ArtifactPath_a5b79113], result)

    @builtins.property
    def task_definition_template_input(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) The artifact containing the ECS task definition template file.

        During deployment, the task definition template file contents
        will be registered with ECS.

        If you use this property, it's assumed the file is called 'taskdef.json'.
        If your task definition template uses a different filename, leave this property empty,
        and use the ``taskDefinitionTemplateFile`` property instead.

        :default: - one of this property, or ``taskDefinitionTemplateFile``, is required

        :stability: experimental
        '''
        result = self._values.get("task_definition_template_input")
        return typing.cast(typing.Optional[_Artifact_9905eec2], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeDeployEcsDeployActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeDeployServerDeployAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CodeDeployServerDeployAction",
):
    '''
    :stability: experimental
    :exampleMetadata: infused

    Example::

        # deployment_group: codedeploy.ServerDeploymentGroup
        pipeline = codepipeline.Pipeline(self, "MyPipeline",
            pipeline_name="MyPipeline"
        )
        
        # add the source and build Stages to the Pipeline...
        build_output = codepipeline.Artifact()
        deploy_action = codepipeline_actions.CodeDeployServerDeployAction(
            action_name="CodeDeploy",
            input=build_output,
            deployment_group=deployment_group
        )
        pipeline.add_stage(
            stage_name="Deploy",
            actions=[deploy_action]
        )
    '''

    def __init__(
        self,
        *,
        deployment_group: _IServerDeploymentGroup_9bf302e3,
        input: _Artifact_9905eec2,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param deployment_group: (experimental) The CodeDeploy server Deployment Group to deploy to.
        :param input: (experimental) The source to use as input for deployment.
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = CodeDeployServerDeployActionProps(
            deployment_group=deployment_group,
            input=input,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, _stage, options]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CodeDeployServerDeployActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "deployment_group": "deploymentGroup",
        "input": "input",
    },
)
class CodeDeployServerDeployActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        deployment_group: _IServerDeploymentGroup_9bf302e3,
        input: _Artifact_9905eec2,
    ) -> None:
        '''(experimental) Construction properties of the {@link CodeDeployServerDeployAction CodeDeploy server deploy CodePipeline Action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param deployment_group: (experimental) The CodeDeploy server Deployment Group to deploy to.
        :param input: (experimental) The source to use as input for deployment.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # deployment_group: codedeploy.ServerDeploymentGroup
            pipeline = codepipeline.Pipeline(self, "MyPipeline",
                pipeline_name="MyPipeline"
            )
            
            # add the source and build Stages to the Pipeline...
            build_output = codepipeline.Artifact()
            deploy_action = codepipeline_actions.CodeDeployServerDeployAction(
                action_name="CodeDeploy",
                input=build_output,
                deployment_group=deployment_group
            )
            pipeline.add_stage(
                stage_name="Deploy",
                actions=[deploy_action]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "deployment_group": deployment_group,
            "input": input,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def deployment_group(self) -> _IServerDeploymentGroup_9bf302e3:
        '''(experimental) The CodeDeploy server Deployment Group to deploy to.

        :stability: experimental
        '''
        result = self._values.get("deployment_group")
        assert result is not None, "Required property 'deployment_group' is missing"
        return typing.cast(_IServerDeploymentGroup_9bf302e3, result)

    @builtins.property
    def input(self) -> _Artifact_9905eec2:
        '''(experimental) The source to use as input for deployment.

        :stability: experimental
        '''
        result = self._values.get("input")
        assert result is not None, "Required property 'input' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeDeployServerDeployActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeStarConnectionsSourceAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.CodeStarConnectionsSourceAction",
):
    '''(experimental) A CodePipeline source action for the CodeStar Connections source, which allows connecting to GitHub and BitBucket.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="BitBucket_Source",
            owner="aws",
            repo="aws-cdk",
            output=source_output,
            connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/12345678-abcd-12ab-34cdef5678gh"
        )
    '''

    def __init__(
        self,
        *,
        connection_arn: builtins.str,
        output: _Artifact_9905eec2,
        owner: builtins.str,
        repo: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        trigger_on_push: typing.Optional[builtins.bool] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection_arn: (experimental) The ARN of the CodeStar Connection created in the AWS console that has permissions to access this GitHub or BitBucket repository.
        :param output: (experimental) The output artifact that this action produces. Can be used as input for further pipeline actions.
        :param owner: (experimental) The owning user or organization of the repository.
        :param repo: (experimental) The name of the repository.
        :param branch: (experimental) The branch to build. Default: 'master'
        :param code_build_clone_output: (experimental) Whether the output should be the contents of the repository (which is the default), or a link that allows CodeBuild to clone the repository before building. **Note**: if this option is true, then only CodeBuild actions can use the resulting {@link output}. Default: false
        :param trigger_on_push: (experimental) Controls automatically starting your pipeline when a new commit is made on the configured repository and branch. If unspecified, the default value is true, and the field does not display by default. Default: true
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = CodeStarConnectionsSourceActionProps(
            connection_arn=connection_arn,
            output=output,
            owner=owner,
            repo=repo,
            branch=branch,
            code_build_clone_output=code_build_clone_output,
            trigger_on_push=trigger_on_push,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, _stage, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variables")
    def variables(self) -> "CodeStarSourceVariables":
        '''(experimental) The variables emitted by this action.

        :stability: experimental
        '''
        return typing.cast("CodeStarSourceVariables", jsii.get(self, "variables"))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CodeStarConnectionsSourceActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "connection_arn": "connectionArn",
        "output": "output",
        "owner": "owner",
        "repo": "repo",
        "branch": "branch",
        "code_build_clone_output": "codeBuildCloneOutput",
        "trigger_on_push": "triggerOnPush",
    },
)
class CodeStarConnectionsSourceActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        connection_arn: builtins.str,
        output: _Artifact_9905eec2,
        owner: builtins.str,
        repo: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        trigger_on_push: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Construction properties for {@link CodeStarConnectionsSourceAction}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param connection_arn: (experimental) The ARN of the CodeStar Connection created in the AWS console that has permissions to access this GitHub or BitBucket repository.
        :param output: (experimental) The output artifact that this action produces. Can be used as input for further pipeline actions.
        :param owner: (experimental) The owning user or organization of the repository.
        :param repo: (experimental) The name of the repository.
        :param branch: (experimental) The branch to build. Default: 'master'
        :param code_build_clone_output: (experimental) Whether the output should be the contents of the repository (which is the default), or a link that allows CodeBuild to clone the repository before building. **Note**: if this option is true, then only CodeBuild actions can use the resulting {@link output}. Default: false
        :param trigger_on_push: (experimental) Controls automatically starting your pipeline when a new commit is made on the configured repository and branch. If unspecified, the default value is true, and the field does not display by default. Default: true

        :stability: experimental
        :exampleMetadata: infused

        Example::

            source_output = codepipeline.Artifact()
            source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
                action_name="BitBucket_Source",
                owner="aws",
                repo="aws-cdk",
                output=source_output,
                connection_arn="arn:aws:codestar-connections:us-east-1:123456789012:connection/12345678-abcd-12ab-34cdef5678gh"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "connection_arn": connection_arn,
            "output": output,
            "owner": owner,
            "repo": repo,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if branch is not None:
            self._values["branch"] = branch
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if trigger_on_push is not None:
            self._values["trigger_on_push"] = trigger_on_push

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def connection_arn(self) -> builtins.str:
        '''(experimental) The ARN of the CodeStar Connection created in the AWS console that has permissions to access this GitHub or BitBucket repository.

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/connections-create.html
        :stability: experimental

        Example::

            "arn:aws:codestar-connections:us-east-1:123456789012:connection/12345678-abcd-12ab-34cdef5678gh"
        '''
        result = self._values.get("connection_arn")
        assert result is not None, "Required property 'connection_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output(self) -> _Artifact_9905eec2:
        '''(experimental) The output artifact that this action produces.

        Can be used as input for further pipeline actions.

        :stability: experimental
        '''
        result = self._values.get("output")
        assert result is not None, "Required property 'output' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''(experimental) The owning user or organization of the repository.

        :stability: experimental

        Example::

            "aws"
        '''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo(self) -> builtins.str:
        '''(experimental) The name of the repository.

        :stability: experimental

        Example::

            "aws-cdk"
        '''
        result = self._values.get("repo")
        assert result is not None, "Required property 'repo' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The branch to build.

        :default: 'master'

        :stability: experimental
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the output should be the contents of the repository (which is the default), or a link that allows CodeBuild to clone the repository before building.

        **Note**: if this option is true,
        then only CodeBuild actions can use the resulting {@link output}.

        :default: false

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodestarConnectionSource.html#action-reference-CodestarConnectionSource-config
        :stability: experimental
        '''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def trigger_on_push(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Controls automatically starting your pipeline when a new commit is made on the configured repository and branch.

        If unspecified,
        the default value is true, and the field does not display by default.

        :default: true

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodestarConnectionSource.html
        :stability: experimental
        '''
        result = self._values.get("trigger_on_push")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeStarConnectionsSourceActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.CodeStarSourceVariables",
    jsii_struct_bases=[],
    name_mapping={
        "author_date": "authorDate",
        "branch_name": "branchName",
        "commit_id": "commitId",
        "commit_message": "commitMessage",
        "connection_arn": "connectionArn",
        "full_repository_name": "fullRepositoryName",
    },
)
class CodeStarSourceVariables:
    def __init__(
        self,
        *,
        author_date: builtins.str,
        branch_name: builtins.str,
        commit_id: builtins.str,
        commit_message: builtins.str,
        connection_arn: builtins.str,
        full_repository_name: builtins.str,
    ) -> None:
        '''(experimental) The CodePipeline variables emitted by CodeStar source Action.

        :param author_date: (experimental) The date the currently last commit on the tracked branch was authored, in ISO-8601 format.
        :param branch_name: (experimental) The name of the branch this action tracks.
        :param commit_id: (experimental) The SHA1 hash of the currently last commit on the tracked branch.
        :param commit_message: (experimental) The message of the currently last commit on the tracked branch.
        :param connection_arn: (experimental) The connection ARN this source uses.
        :param full_repository_name: (experimental) The name of the repository this action points to.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            
            code_star_source_variables = codepipeline_actions.CodeStarSourceVariables(
                author_date="authorDate",
                branch_name="branchName",
                commit_id="commitId",
                commit_message="commitMessage",
                connection_arn="connectionArn",
                full_repository_name="fullRepositoryName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "author_date": author_date,
            "branch_name": branch_name,
            "commit_id": commit_id,
            "commit_message": commit_message,
            "connection_arn": connection_arn,
            "full_repository_name": full_repository_name,
        }

    @builtins.property
    def author_date(self) -> builtins.str:
        '''(experimental) The date the currently last commit on the tracked branch was authored, in ISO-8601 format.

        :stability: experimental
        '''
        result = self._values.get("author_date")
        assert result is not None, "Required property 'author_date' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_name(self) -> builtins.str:
        '''(experimental) The name of the branch this action tracks.

        :stability: experimental
        '''
        result = self._values.get("branch_name")
        assert result is not None, "Required property 'branch_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_id(self) -> builtins.str:
        '''(experimental) The SHA1 hash of the currently last commit on the tracked branch.

        :stability: experimental
        '''
        result = self._values.get("commit_id")
        assert result is not None, "Required property 'commit_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_message(self) -> builtins.str:
        '''(experimental) The message of the currently last commit on the tracked branch.

        :stability: experimental
        '''
        result = self._values.get("commit_message")
        assert result is not None, "Required property 'commit_message' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connection_arn(self) -> builtins.str:
        '''(experimental) The connection ARN this source uses.

        :stability: experimental
        '''
        result = self._values.get("connection_arn")
        assert result is not None, "Required property 'connection_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def full_repository_name(self) -> builtins.str:
        '''(experimental) The name of the repository this action points to.

        :stability: experimental
        '''
        result = self._values.get("full_repository_name")
        assert result is not None, "Required property 'full_repository_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeStarSourceVariables(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EcrSourceAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.EcrSourceAction",
):
    '''(experimental) The ECR Repository source CodePipeline Action.

    Will trigger the pipeline as soon as the target tag in the repository
    changes, but only if there is a CloudTrail Trail in the account that
    captures the ECR event.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as ecr
        
        # ecr_repository: ecr.Repository
        
        pipeline = codepipeline.Pipeline(self, "MyPipeline")
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.EcrSourceAction(
            action_name="ECR",
            repository=ecr_repository,
            image_tag="some-tag",  # optional, default: 'latest'
            output=source_output
        )
        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )
    '''

    def __init__(
        self,
        *,
        output: _Artifact_9905eec2,
        repository: _IRepository_8b4d2894,
        image_tag: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param output: 
        :param repository: (experimental) The repository that will be watched for changes.
        :param image_tag: (experimental) The image tag that will be checked for changes. Provide an empty string to trigger on changes to any tag. Default: 'latest'
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = EcrSourceActionProps(
            output=output,
            repository=repository,
            image_tag=image_tag,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, stage, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variables")
    def variables(self) -> "EcrSourceVariables":
        '''(experimental) The variables emitted by this action.

        :stability: experimental
        '''
        return typing.cast("EcrSourceVariables", jsii.get(self, "variables"))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.EcrSourceActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "output": "output",
        "repository": "repository",
        "image_tag": "imageTag",
    },
)
class EcrSourceActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        output: _Artifact_9905eec2,
        repository: _IRepository_8b4d2894,
        image_tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Construction properties of {@link EcrSourceAction}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param output: 
        :param repository: (experimental) The repository that will be watched for changes.
        :param image_tag: (experimental) The image tag that will be checked for changes. Provide an empty string to trigger on changes to any tag. Default: 'latest'

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import monocdk as ecr
            
            # ecr_repository: ecr.Repository
            
            pipeline = codepipeline.Pipeline(self, "MyPipeline")
            source_output = codepipeline.Artifact()
            source_action = codepipeline_actions.EcrSourceAction(
                action_name="ECR",
                repository=ecr_repository,
                image_tag="some-tag",  # optional, default: 'latest'
                output=source_output
            )
            pipeline.add_stage(
                stage_name="Source",
                actions=[source_action]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "output": output,
            "repository": repository,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if image_tag is not None:
            self._values["image_tag"] = image_tag

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def output(self) -> _Artifact_9905eec2:
        '''
        :stability: experimental
        '''
        result = self._values.get("output")
        assert result is not None, "Required property 'output' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def repository(self) -> _IRepository_8b4d2894:
        '''(experimental) The repository that will be watched for changes.

        :stability: experimental
        '''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(_IRepository_8b4d2894, result)

    @builtins.property
    def image_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The image tag that will be checked for changes.

        Provide an empty string to trigger on changes to any tag.

        :default: 'latest'

        :stability: experimental
        '''
        result = self._values.get("image_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcrSourceActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.EcrSourceVariables",
    jsii_struct_bases=[],
    name_mapping={
        "image_digest": "imageDigest",
        "image_tag": "imageTag",
        "image_uri": "imageUri",
        "registry_id": "registryId",
        "repository_name": "repositoryName",
    },
)
class EcrSourceVariables:
    def __init__(
        self,
        *,
        image_digest: builtins.str,
        image_tag: builtins.str,
        image_uri: builtins.str,
        registry_id: builtins.str,
        repository_name: builtins.str,
    ) -> None:
        '''(experimental) The CodePipeline variables emitted by the ECR source Action.

        :param image_digest: (experimental) The digest of the current image, in the form ':'.
        :param image_tag: (experimental) The Docker tag of the current image.
        :param image_uri: (experimental) The full ECR Docker URI of the current image.
        :param registry_id: (experimental) The identifier of the registry. In ECR, this is usually the ID of the AWS account owning it.
        :param repository_name: (experimental) The physical name of the repository that this action tracks.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            
            ecr_source_variables = codepipeline_actions.EcrSourceVariables(
                image_digest="imageDigest",
                image_tag="imageTag",
                image_uri="imageUri",
                registry_id="registryId",
                repository_name="repositoryName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "image_digest": image_digest,
            "image_tag": image_tag,
            "image_uri": image_uri,
            "registry_id": registry_id,
            "repository_name": repository_name,
        }

    @builtins.property
    def image_digest(self) -> builtins.str:
        '''(experimental) The digest of the current image, in the form ':'.

        :stability: experimental
        '''
        result = self._values.get("image_digest")
        assert result is not None, "Required property 'image_digest' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def image_tag(self) -> builtins.str:
        '''(experimental) The Docker tag of the current image.

        :stability: experimental
        '''
        result = self._values.get("image_tag")
        assert result is not None, "Required property 'image_tag' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def image_uri(self) -> builtins.str:
        '''(experimental) The full ECR Docker URI of the current image.

        :stability: experimental
        '''
        result = self._values.get("image_uri")
        assert result is not None, "Required property 'image_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def registry_id(self) -> builtins.str:
        '''(experimental) The identifier of the registry.

        In ECR, this is usually the ID of the AWS account owning it.

        :stability: experimental
        '''
        result = self._values.get("registry_id")
        assert result is not None, "Required property 'registry_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''(experimental) The physical name of the repository that this action tracks.

        :stability: experimental
        '''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcrSourceVariables(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EcsDeployAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.EcsDeployAction",
):
    '''(experimental) CodePipeline Action to deploy an ECS Service.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as ecs
        
        # service: ecs.FargateService
        
        pipeline = codepipeline.Pipeline(self, "MyPipeline")
        build_output = codepipeline.Artifact()
        deploy_stage = pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                codepipeline_actions.EcsDeployAction(
                    action_name="DeployAction",
                    service=service,
                    # if your file is called imagedefinitions.json,
                    # use the `input` property,
                    # and leave out the `imageFile` property
                    input=build_output,
                    # if your file name is _not_ imagedefinitions.json,
                    # use the `imageFile` property,
                    # and leave out the `input` property
                    image_file=build_output.at_path("imageDef.json"),
                    deployment_timeout=Duration.minutes(60)
                )
            ]
        )
    '''

    def __init__(
        self,
        *,
        service: _IBaseService_f1507c0b,
        deployment_timeout: typing.Optional[_Duration_070aa057] = None,
        image_file: typing.Optional[_ArtifactPath_a5b79113] = None,
        input: typing.Optional[_Artifact_9905eec2] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param service: (experimental) The ECS Service to deploy.
        :param deployment_timeout: (experimental) Timeout for the ECS deployment in minutes. Value must be between 1-60. Default: - 60 minutes
        :param image_file: (experimental) The name of the JSON image definitions file to use for deployments. The JSON file is a list of objects, each with 2 keys: ``name`` is the name of the container in the Task Definition, and ``imageUri`` is the Docker image URI you want to update your service with. Use this property if you want to use a different name for this file than the default 'imagedefinitions.json'. If you use this property, you don't need to specify the ``input`` property. Default: - one of this property, or ``input``, is required
        :param input: (experimental) The input artifact that contains the JSON image definitions file to use for deployments. The JSON file is a list of objects, each with 2 keys: ``name`` is the name of the container in the Task Definition, and ``imageUri`` is the Docker image URI you want to update your service with. If you use this property, it's assumed the file is called 'imagedefinitions.json'. If your build uses a different file, leave this property empty, and use the ``imageFile`` property instead. Default: - one of this property, or ``imageFile``, is required
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = EcsDeployActionProps(
            service=service,
            deployment_timeout=deployment_timeout,
            image_file=image_file,
            input=input,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, _stage, options]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.EcsDeployActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "service": "service",
        "deployment_timeout": "deploymentTimeout",
        "image_file": "imageFile",
        "input": "input",
    },
)
class EcsDeployActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        service: _IBaseService_f1507c0b,
        deployment_timeout: typing.Optional[_Duration_070aa057] = None,
        image_file: typing.Optional[_ArtifactPath_a5b79113] = None,
        input: typing.Optional[_Artifact_9905eec2] = None,
    ) -> None:
        '''(experimental) Construction properties of {@link EcsDeployAction}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param service: (experimental) The ECS Service to deploy.
        :param deployment_timeout: (experimental) Timeout for the ECS deployment in minutes. Value must be between 1-60. Default: - 60 minutes
        :param image_file: (experimental) The name of the JSON image definitions file to use for deployments. The JSON file is a list of objects, each with 2 keys: ``name`` is the name of the container in the Task Definition, and ``imageUri`` is the Docker image URI you want to update your service with. Use this property if you want to use a different name for this file than the default 'imagedefinitions.json'. If you use this property, you don't need to specify the ``input`` property. Default: - one of this property, or ``input``, is required
        :param input: (experimental) The input artifact that contains the JSON image definitions file to use for deployments. The JSON file is a list of objects, each with 2 keys: ``name`` is the name of the container in the Task Definition, and ``imageUri`` is the Docker image URI you want to update your service with. If you use this property, it's assumed the file is called 'imagedefinitions.json'. If your build uses a different file, leave this property empty, and use the ``imageFile`` property instead. Default: - one of this property, or ``imageFile``, is required

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import monocdk as ecs
            
            # service: ecs.FargateService
            
            pipeline = codepipeline.Pipeline(self, "MyPipeline")
            build_output = codepipeline.Artifact()
            deploy_stage = pipeline.add_stage(
                stage_name="Deploy",
                actions=[
                    codepipeline_actions.EcsDeployAction(
                        action_name="DeployAction",
                        service=service,
                        # if your file is called imagedefinitions.json,
                        # use the `input` property,
                        # and leave out the `imageFile` property
                        input=build_output,
                        # if your file name is _not_ imagedefinitions.json,
                        # use the `imageFile` property,
                        # and leave out the `input` property
                        image_file=build_output.at_path("imageDef.json"),
                        deployment_timeout=Duration.minutes(60)
                    )
                ]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "service": service,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if deployment_timeout is not None:
            self._values["deployment_timeout"] = deployment_timeout
        if image_file is not None:
            self._values["image_file"] = image_file
        if input is not None:
            self._values["input"] = input

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def service(self) -> _IBaseService_f1507c0b:
        '''(experimental) The ECS Service to deploy.

        :stability: experimental
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(_IBaseService_f1507c0b, result)

    @builtins.property
    def deployment_timeout(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Timeout for the ECS deployment in minutes.

        Value must be between 1-60.

        :default: - 60 minutes

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-ECS.html
        :stability: experimental
        '''
        result = self._values.get("deployment_timeout")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def image_file(self) -> typing.Optional[_ArtifactPath_a5b79113]:
        '''(experimental) The name of the JSON image definitions file to use for deployments.

        The JSON file is a list of objects,
        each with 2 keys: ``name`` is the name of the container in the Task Definition,
        and ``imageUri`` is the Docker image URI you want to update your service with.
        Use this property if you want to use a different name for this file than the default 'imagedefinitions.json'.
        If you use this property, you don't need to specify the ``input`` property.

        :default: - one of this property, or ``input``, is required

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-create.html#pipelines-create-image-definitions
        :stability: experimental
        '''
        result = self._values.get("image_file")
        return typing.cast(typing.Optional[_ArtifactPath_a5b79113], result)

    @builtins.property
    def input(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) The input artifact that contains the JSON image definitions file to use for deployments.

        The JSON file is a list of objects,
        each with 2 keys: ``name`` is the name of the container in the Task Definition,
        and ``imageUri`` is the Docker image URI you want to update your service with.
        If you use this property, it's assumed the file is called 'imagedefinitions.json'.
        If your build uses a different file, leave this property empty,
        and use the ``imageFile`` property instead.

        :default: - one of this property, or ``imageFile``, is required

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-create.html#pipelines-create-image-definitions
        :stability: experimental
        '''
        result = self._values.get("input")
        return typing.cast(typing.Optional[_Artifact_9905eec2], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsDeployActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GitHubSourceAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.GitHubSourceAction",
):
    '''(experimental) Source that is provided by a GitHub repository.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # source_output: codepipeline.Artifact
        # project: codebuild.PipelineProject
        
        
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="Github_Source",
            output=source_output,
            owner="my-owner",
            repo="my-repo",
            oauth_token=SecretValue.secrets_manager("my-github-token"),
            variables_namespace="MyNamespace"
        )
        
        # later:
        
        codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=project,
            input=source_output,
            environment_variables={
                "COMMIT_URL": codebuild.aws_codebuild.BuildEnvironmentVariable(
                    value=source_action.variables.commit_url
                )
            }
        )
    '''

    def __init__(
        self,
        *,
        oauth_token: _SecretValue_c18506ef,
        output: _Artifact_9905eec2,
        owner: builtins.str,
        repo: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        trigger: typing.Optional["GitHubTrigger"] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param oauth_token: (experimental) A GitHub OAuth token to use for authentication. It is recommended to use a Secrets Manager ``Secret`` to obtain the token: const oauth = cdk.SecretValue.secretsManager('my-github-token'); new GitHubSource(this, 'GitHubAction', { oauthToken: oauth, ... }); The GitHub Personal Access Token should have these scopes: - **repo** - to read the repository - **admin:repo_hook** - if you plan to use webhooks (true by default)
        :param output: 
        :param owner: (experimental) The GitHub account/user that owns the repo.
        :param repo: (experimental) The name of the repo, without the username.
        :param branch: (experimental) The branch to use. Default: "master"
        :param trigger: (experimental) How AWS CodePipeline should be triggered. With the default value "WEBHOOK", a webhook is created in GitHub that triggers the action With "POLL", CodePipeline periodically checks the source for changes With "None", the action is not triggered through changes in the source To use ``WEBHOOK``, your GitHub Personal Access Token should have **admin:repo_hook** scope (in addition to the regular **repo** scope). Default: GitHubTrigger.WEBHOOK
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = GitHubSourceActionProps(
            oauth_token=oauth_token,
            output=output,
            owner=owner,
            repo=repo,
            branch=branch,
            trigger=trigger,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        _options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [scope, stage, _options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variables")
    def variables(self) -> "GitHubSourceVariables":
        '''(experimental) The variables emitted by this action.

        :stability: experimental
        '''
        return typing.cast("GitHubSourceVariables", jsii.get(self, "variables"))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.GitHubSourceActionProps",
    jsii_struct_bases=[_CommonActionProps_4f0e79c2],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "oauth_token": "oauthToken",
        "output": "output",
        "owner": "owner",
        "repo": "repo",
        "branch": "branch",
        "trigger": "trigger",
    },
)
class GitHubSourceActionProps(_CommonActionProps_4f0e79c2):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        oauth_token: _SecretValue_c18506ef,
        output: _Artifact_9905eec2,
        owner: builtins.str,
        repo: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        trigger: typing.Optional["GitHubTrigger"] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link GitHubSourceAction GitHub source action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param oauth_token: (experimental) A GitHub OAuth token to use for authentication. It is recommended to use a Secrets Manager ``Secret`` to obtain the token: const oauth = cdk.SecretValue.secretsManager('my-github-token'); new GitHubSource(this, 'GitHubAction', { oauthToken: oauth, ... }); The GitHub Personal Access Token should have these scopes: - **repo** - to read the repository - **admin:repo_hook** - if you plan to use webhooks (true by default)
        :param output: 
        :param owner: (experimental) The GitHub account/user that owns the repo.
        :param repo: (experimental) The name of the repo, without the username.
        :param branch: (experimental) The branch to use. Default: "master"
        :param trigger: (experimental) How AWS CodePipeline should be triggered. With the default value "WEBHOOK", a webhook is created in GitHub that triggers the action With "POLL", CodePipeline periodically checks the source for changes With "None", the action is not triggered through changes in the source To use ``WEBHOOK``, your GitHub Personal Access Token should have **admin:repo_hook** scope (in addition to the regular **repo** scope). Default: GitHubTrigger.WEBHOOK

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # source_output: codepipeline.Artifact
            # project: codebuild.PipelineProject
            
            
            source_action = codepipeline_actions.GitHubSourceAction(
                action_name="Github_Source",
                output=source_output,
                owner="my-owner",
                repo="my-repo",
                oauth_token=SecretValue.secrets_manager("my-github-token"),
                variables_namespace="MyNamespace"
            )
            
            # later:
            
            codepipeline_actions.CodeBuildAction(
                action_name="CodeBuild",
                project=project,
                input=source_output,
                environment_variables={
                    "COMMIT_URL": codebuild.aws_codebuild.BuildEnvironmentVariable(
                        value=source_action.variables.commit_url
                    )
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "oauth_token": oauth_token,
            "output": output,
            "owner": owner,
            "repo": repo,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if branch is not None:
            self._values["branch"] = branch
        if trigger is not None:
            self._values["trigger"] = trigger

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oauth_token(self) -> _SecretValue_c18506ef:
        '''(experimental) A GitHub OAuth token to use for authentication.

        It is recommended to use a Secrets Manager ``Secret`` to obtain the token:

        const oauth = cdk.SecretValue.secretsManager('my-github-token');
        new GitHubSource(this, 'GitHubAction', { oauthToken: oauth, ... });

        The GitHub Personal Access Token should have these scopes:

        - **repo** - to read the repository
        - **admin:repo_hook** - if you plan to use webhooks (true by default)

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/appendix-github-oauth.html#GitHub-create-personal-token-CLI
        :stability: experimental
        '''
        result = self._values.get("oauth_token")
        assert result is not None, "Required property 'oauth_token' is missing"
        return typing.cast(_SecretValue_c18506ef, result)

    @builtins.property
    def output(self) -> _Artifact_9905eec2:
        '''
        :stability: experimental
        '''
        result = self._values.get("output")
        assert result is not None, "Required property 'output' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''(experimental) The GitHub account/user that owns the repo.

        :stability: experimental
        '''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo(self) -> builtins.str:
        '''(experimental) The name of the repo, without the username.

        :stability: experimental
        '''
        result = self._values.get("repo")
        assert result is not None, "Required property 'repo' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The branch to use.

        :default: "master"

        :stability: experimental
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def trigger(self) -> typing.Optional["GitHubTrigger"]:
        '''(experimental) How AWS CodePipeline should be triggered.

        With the default value "WEBHOOK", a webhook is created in GitHub that triggers the action
        With "POLL", CodePipeline periodically checks the source for changes
        With "None", the action is not triggered through changes in the source

        To use ``WEBHOOK``, your GitHub Personal Access Token should have
        **admin:repo_hook** scope (in addition to the regular **repo** scope).

        :default: GitHubTrigger.WEBHOOK

        :stability: experimental
        '''
        result = self._values.get("trigger")
        return typing.cast(typing.Optional["GitHubTrigger"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubSourceActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.GitHubSourceVariables",
    jsii_struct_bases=[],
    name_mapping={
        "author_date": "authorDate",
        "branch_name": "branchName",
        "commit_id": "commitId",
        "commit_message": "commitMessage",
        "committer_date": "committerDate",
        "commit_url": "commitUrl",
        "repository_name": "repositoryName",
    },
)
class GitHubSourceVariables:
    def __init__(
        self,
        *,
        author_date: builtins.str,
        branch_name: builtins.str,
        commit_id: builtins.str,
        commit_message: builtins.str,
        committer_date: builtins.str,
        commit_url: builtins.str,
        repository_name: builtins.str,
    ) -> None:
        '''(experimental) The CodePipeline variables emitted by GitHub source Action.

        :param author_date: (experimental) The date the currently last commit on the tracked branch was authored, in ISO-8601 format.
        :param branch_name: (experimental) The name of the branch this action tracks.
        :param commit_id: (experimental) The SHA1 hash of the currently last commit on the tracked branch.
        :param commit_message: (experimental) The message of the currently last commit on the tracked branch.
        :param committer_date: (experimental) The date the currently last commit on the tracked branch was committed, in ISO-8601 format.
        :param commit_url: (experimental) The GitHub API URL of the currently last commit on the tracked branch.
        :param repository_name: (experimental) The name of the repository this action points to.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            
            git_hub_source_variables = codepipeline_actions.GitHubSourceVariables(
                author_date="authorDate",
                branch_name="branchName",
                commit_id="commitId",
                commit_message="commitMessage",
                committer_date="committerDate",
                commit_url="commitUrl",
                repository_name="repositoryName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "author_date": author_date,
            "branch_name": branch_name,
            "commit_id": commit_id,
            "commit_message": commit_message,
            "committer_date": committer_date,
            "commit_url": commit_url,
            "repository_name": repository_name,
        }

    @builtins.property
    def author_date(self) -> builtins.str:
        '''(experimental) The date the currently last commit on the tracked branch was authored, in ISO-8601 format.

        :stability: experimental
        '''
        result = self._values.get("author_date")
        assert result is not None, "Required property 'author_date' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch_name(self) -> builtins.str:
        '''(experimental) The name of the branch this action tracks.

        :stability: experimental
        '''
        result = self._values.get("branch_name")
        assert result is not None, "Required property 'branch_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_id(self) -> builtins.str:
        '''(experimental) The SHA1 hash of the currently last commit on the tracked branch.

        :stability: experimental
        '''
        result = self._values.get("commit_id")
        assert result is not None, "Required property 'commit_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_message(self) -> builtins.str:
        '''(experimental) The message of the currently last commit on the tracked branch.

        :stability: experimental
        '''
        result = self._values.get("commit_message")
        assert result is not None, "Required property 'commit_message' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def committer_date(self) -> builtins.str:
        '''(experimental) The date the currently last commit on the tracked branch was committed, in ISO-8601 format.

        :stability: experimental
        '''
        result = self._values.get("committer_date")
        assert result is not None, "Required property 'committer_date' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commit_url(self) -> builtins.str:
        '''(experimental) The GitHub API URL of the currently last commit on the tracked branch.

        :stability: experimental
        '''
        result = self._values.get("commit_url")
        assert result is not None, "Required property 'commit_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''(experimental) The name of the repository this action points to.

        :stability: experimental
        '''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubSourceVariables(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_codepipeline_actions.GitHubTrigger")
class GitHubTrigger(enum.Enum):
    '''(experimental) If and how the GitHub source action should be triggered.

    :stability: experimental
    '''

    NONE = "NONE"
    '''
    :stability: experimental
    '''
    POLL = "POLL"
    '''
    :stability: experimental
    '''
    WEBHOOK = "WEBHOOK"
    '''
    :stability: experimental
    '''


@jsii.interface(jsii_type="monocdk.aws_codepipeline_actions.IJenkinsProvider")
class IJenkinsProvider(_IConstruct_5a0f9c5e, typing_extensions.Protocol):
    '''(experimental) A Jenkins provider.

    If you want to create a new Jenkins provider managed alongside your CDK code,
    instantiate the {@link JenkinsProvider} class directly.

    If you want to reference an already registered provider,
    use the {@link JenkinsProvider#fromJenkinsProviderAttributes} method.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverUrl")
    def server_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...


class _IJenkinsProviderProxy(
    jsii.proxy_for(_IConstruct_5a0f9c5e) # type: ignore[misc]
):
    '''(experimental) A Jenkins provider.

    If you want to create a new Jenkins provider managed alongside your CDK code,
    instantiate the {@link JenkinsProvider} class directly.

    If you want to reference an already registered provider,
    use the {@link JenkinsProvider#fromJenkinsProviderAttributes} method.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_codepipeline_actions.IJenkinsProvider"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverUrl")
    def server_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serverUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJenkinsProvider).__jsii_proxy_class__ = lambda : _IJenkinsProviderProxy


class JenkinsAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.JenkinsAction",
):
    '''(experimental) Jenkins build CodePipeline Action.

    :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/tutorials-four-stage-pipeline.html
    :stability: experimental
    :exampleMetadata: infused

    Example::

        # jenkins_provider: codepipeline_actions.JenkinsProvider
        
        build_action = codepipeline_actions.JenkinsAction(
            action_name="JenkinsBuild",
            jenkins_provider=jenkins_provider,
            project_name="MyProject",
            type=codepipeline_actions.JenkinsActionType.BUILD
        )
    '''

    def __init__(
        self,
        *,
        jenkins_provider: IJenkinsProvider,
        project_name: builtins.str,
        type: "JenkinsActionType",
        inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        outputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param jenkins_provider: (experimental) The Jenkins Provider for this Action.
        :param project_name: (experimental) The name of the project (sometimes also called job, or task) on your Jenkins installation that will be invoked by this Action.
        :param type: (experimental) The type of the Action - Build, or Test.
        :param inputs: (experimental) The source to use as input for this build.
        :param outputs: 
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = JenkinsActionProps(
            jenkins_provider=jenkins_provider,
            project_name=project_name,
            type=type,
            inputs=inputs,
            outputs=outputs,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        _options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, _stage, _options]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.JenkinsActionProps",
    jsii_struct_bases=[_CommonActionProps_4f0e79c2],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "jenkins_provider": "jenkinsProvider",
        "project_name": "projectName",
        "type": "type",
        "inputs": "inputs",
        "outputs": "outputs",
    },
)
class JenkinsActionProps(_CommonActionProps_4f0e79c2):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        jenkins_provider: IJenkinsProvider,
        project_name: builtins.str,
        type: "JenkinsActionType",
        inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        outputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
    ) -> None:
        '''(experimental) Construction properties of {@link JenkinsAction}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param jenkins_provider: (experimental) The Jenkins Provider for this Action.
        :param project_name: (experimental) The name of the project (sometimes also called job, or task) on your Jenkins installation that will be invoked by this Action.
        :param type: (experimental) The type of the Action - Build, or Test.
        :param inputs: (experimental) The source to use as input for this build.
        :param outputs: 

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # jenkins_provider: codepipeline_actions.JenkinsProvider
            
            build_action = codepipeline_actions.JenkinsAction(
                action_name="JenkinsBuild",
                jenkins_provider=jenkins_provider,
                project_name="MyProject",
                type=codepipeline_actions.JenkinsActionType.BUILD
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "jenkins_provider": jenkins_provider,
            "project_name": project_name,
            "type": type,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if inputs is not None:
            self._values["inputs"] = inputs
        if outputs is not None:
            self._values["outputs"] = outputs

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jenkins_provider(self) -> IJenkinsProvider:
        '''(experimental) The Jenkins Provider for this Action.

        :stability: experimental
        '''
        result = self._values.get("jenkins_provider")
        assert result is not None, "Required property 'jenkins_provider' is missing"
        return typing.cast(IJenkinsProvider, result)

    @builtins.property
    def project_name(self) -> builtins.str:
        '''(experimental) The name of the project (sometimes also called job, or task) on your Jenkins installation that will be invoked by this Action.

        :stability: experimental

        Example::

            "MyJob"
        '''
        result = self._values.get("project_name")
        assert result is not None, "Required property 'project_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> "JenkinsActionType":
        '''(experimental) The type of the Action - Build, or Test.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("JenkinsActionType", result)

    @builtins.property
    def inputs(self) -> typing.Optional[typing.List[_Artifact_9905eec2]]:
        '''(experimental) The source to use as input for this build.

        :stability: experimental
        '''
        result = self._values.get("inputs")
        return typing.cast(typing.Optional[typing.List[_Artifact_9905eec2]], result)

    @builtins.property
    def outputs(self) -> typing.Optional[typing.List[_Artifact_9905eec2]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("outputs")
        return typing.cast(typing.Optional[typing.List[_Artifact_9905eec2]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JenkinsActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_codepipeline_actions.JenkinsActionType")
class JenkinsActionType(enum.Enum):
    '''(experimental) The type of the Jenkins Action that determines its CodePipeline Category - Build, or Test.

    Note that a Jenkins provider, even if it has the same name,
    must be separately registered for each type.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # jenkins_provider: codepipeline_actions.JenkinsProvider
        
        build_action = codepipeline_actions.JenkinsAction(
            action_name="JenkinsBuild",
            jenkins_provider=jenkins_provider,
            project_name="MyProject",
            type=codepipeline_actions.JenkinsActionType.BUILD
        )
    '''

    BUILD = "BUILD"
    '''(experimental) The Action will have the Build Category.

    :stability: experimental
    '''
    TEST = "TEST"
    '''(experimental) The Action will have the Test Category.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.JenkinsProviderAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "provider_name": "providerName",
        "server_url": "serverUrl",
        "version": "version",
    },
)
class JenkinsProviderAttributes:
    def __init__(
        self,
        *,
        provider_name: builtins.str,
        server_url: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for importing an existing Jenkins provider.

        :param provider_name: (experimental) The name of the Jenkins provider that you set in the AWS CodePipeline plugin configuration of your Jenkins project.
        :param server_url: (experimental) The base URL of your Jenkins server.
        :param version: (experimental) The version of your provider. Default: '1'

        :stability: experimental
        :exampleMetadata: infused

        Example::

            jenkins_provider = codepipeline_actions.JenkinsProvider.from_jenkins_provider_attributes(self, "JenkinsProvider",
                provider_name="MyJenkinsProvider",
                server_url="http://my-jenkins.com:8080",
                version="2"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "provider_name": provider_name,
            "server_url": server_url,
        }
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def provider_name(self) -> builtins.str:
        '''(experimental) The name of the Jenkins provider that you set in the AWS CodePipeline plugin configuration of your Jenkins project.

        :stability: experimental

        Example::

            "MyJenkinsProvider"
        '''
        result = self._values.get("provider_name")
        assert result is not None, "Required property 'provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_url(self) -> builtins.str:
        '''(experimental) The base URL of your Jenkins server.

        :stability: experimental

        Example::

            "http://myjenkins.com:8080"
        '''
        result = self._values.get("server_url")
        assert result is not None, "Required property 'server_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of your provider.

        :default: '1'

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JenkinsProviderAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.JenkinsProviderProps",
    jsii_struct_bases=[],
    name_mapping={
        "provider_name": "providerName",
        "server_url": "serverUrl",
        "for_build": "forBuild",
        "for_test": "forTest",
        "version": "version",
    },
)
class JenkinsProviderProps:
    def __init__(
        self,
        *,
        provider_name: builtins.str,
        server_url: builtins.str,
        for_build: typing.Optional[builtins.bool] = None,
        for_test: typing.Optional[builtins.bool] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param provider_name: (experimental) The name of the Jenkins provider that you set in the AWS CodePipeline plugin configuration of your Jenkins project.
        :param server_url: (experimental) The base URL of your Jenkins server.
        :param for_build: (experimental) Whether to immediately register a Jenkins Provider for the build category. The Provider will always be registered if you create a {@link JenkinsAction}. Default: false
        :param for_test: (experimental) Whether to immediately register a Jenkins Provider for the test category. The Provider will always be registered if you create a {@link JenkinsTestAction}. Default: false
        :param version: (experimental) The version of your provider. Default: '1'

        :stability: experimental
        :exampleMetadata: infused

        Example::

            jenkins_provider = codepipeline_actions.JenkinsProvider(self, "JenkinsProvider",
                provider_name="MyJenkinsProvider",
                server_url="http://my-jenkins.com:8080",
                version="2"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "provider_name": provider_name,
            "server_url": server_url,
        }
        if for_build is not None:
            self._values["for_build"] = for_build
        if for_test is not None:
            self._values["for_test"] = for_test
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def provider_name(self) -> builtins.str:
        '''(experimental) The name of the Jenkins provider that you set in the AWS CodePipeline plugin configuration of your Jenkins project.

        :stability: experimental

        Example::

            "MyJenkinsProvider"
        '''
        result = self._values.get("provider_name")
        assert result is not None, "Required property 'provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_url(self) -> builtins.str:
        '''(experimental) The base URL of your Jenkins server.

        :stability: experimental

        Example::

            "http://myjenkins.com:8080"
        '''
        result = self._values.get("server_url")
        assert result is not None, "Required property 'server_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def for_build(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to immediately register a Jenkins Provider for the build category.

        The Provider will always be registered if you create a {@link JenkinsAction}.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("for_build")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def for_test(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to immediately register a Jenkins Provider for the test category.

        The Provider will always be registered if you create a {@link JenkinsTestAction}.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("for_test")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of your provider.

        :default: '1'

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JenkinsProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LambdaInvokeAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.LambdaInvokeAction",
):
    '''(experimental) CodePipeline invoke Action that is provided by an AWS Lambda function.

    :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-invoke-lambda-function.html
    :stability: experimental
    :exampleMetadata: infused

    Example::

        # fn: lambda.Function
        
        source_output = codepipeline.Artifact()
        build_output = codepipeline.Artifact()
        lambda_action = codepipeline_actions.LambdaInvokeAction(
            action_name="Lambda",
            inputs=[source_output, build_output
            ],
            outputs=[
                codepipeline.Artifact("Out1"),
                codepipeline.Artifact("Out2")
            ],
            lambda_=fn
        )
    '''

    def __init__(
        self,
        *,
        lambda_: _IFunction_6e14f09e,
        inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        outputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        user_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        user_parameters_string: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param lambda_: (experimental) The lambda function to invoke.
        :param inputs: (experimental) The optional input Artifacts of the Action. A Lambda Action can have up to 5 inputs. The inputs will appear in the event passed to the Lambda, under the ``'CodePipeline.job'.data.inputArtifacts`` path. Default: the Action will not have any inputs
        :param outputs: (experimental) The optional names of the output Artifacts of the Action. A Lambda Action can have up to 5 outputs. The outputs will appear in the event passed to the Lambda, under the ``'CodePipeline.job'.data.outputArtifacts`` path. It is the responsibility of the Lambda to upload ZIP files with the Artifact contents to the provided locations. Default: the Action will not have any outputs
        :param user_parameters: (experimental) A set of key-value pairs that will be accessible to the invoked Lambda inside the event that the Pipeline will call it with. Only one of ``userParameters`` or ``userParametersString`` can be specified. Default: - no user parameters will be passed
        :param user_parameters_string: (experimental) The string representation of the user parameters that will be accessible to the invoked Lambda inside the event that the Pipeline will call it with. Only one of ``userParametersString`` or ``userParameters`` can be specified. Default: - no user parameters will be passed
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = LambdaInvokeActionProps(
            lambda_=lambda_,
            inputs=inputs,
            outputs=outputs,
            user_parameters=user_parameters,
            user_parameters_string=user_parameters_string,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [scope, _stage, options]))

    @jsii.member(jsii_name="variable")
    def variable(self, variable_name: builtins.str) -> builtins.str:
        '''(experimental) Reference a CodePipeline variable defined by the Lambda function this action points to.

        Variables in Lambda invoke actions are defined by calling the PutJobSuccessResult CodePipeline API call
        with the 'outputVariables' property filled.

        :param variable_name: the name of the variable to reference. A variable by this name must be present in the 'outputVariables' section of the PutJobSuccessResult request that the Lambda function calls when the action is invoked

        :see: https://docs.aws.amazon.com/codepipeline/latest/APIReference/API_PutJobSuccessResult.html
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "variable", [variable_name]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.LambdaInvokeActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "lambda_": "lambda",
        "inputs": "inputs",
        "outputs": "outputs",
        "user_parameters": "userParameters",
        "user_parameters_string": "userParametersString",
    },
)
class LambdaInvokeActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        lambda_: _IFunction_6e14f09e,
        inputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        outputs: typing.Optional[typing.Sequence[_Artifact_9905eec2]] = None,
        user_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        user_parameters_string: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link LambdaInvokeAction Lambda invoke CodePipeline Action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param lambda_: (experimental) The lambda function to invoke.
        :param inputs: (experimental) The optional input Artifacts of the Action. A Lambda Action can have up to 5 inputs. The inputs will appear in the event passed to the Lambda, under the ``'CodePipeline.job'.data.inputArtifacts`` path. Default: the Action will not have any inputs
        :param outputs: (experimental) The optional names of the output Artifacts of the Action. A Lambda Action can have up to 5 outputs. The outputs will appear in the event passed to the Lambda, under the ``'CodePipeline.job'.data.outputArtifacts`` path. It is the responsibility of the Lambda to upload ZIP files with the Artifact contents to the provided locations. Default: the Action will not have any outputs
        :param user_parameters: (experimental) A set of key-value pairs that will be accessible to the invoked Lambda inside the event that the Pipeline will call it with. Only one of ``userParameters`` or ``userParametersString`` can be specified. Default: - no user parameters will be passed
        :param user_parameters_string: (experimental) The string representation of the user parameters that will be accessible to the invoked Lambda inside the event that the Pipeline will call it with. Only one of ``userParametersString`` or ``userParameters`` can be specified. Default: - no user parameters will be passed

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # fn: lambda.Function
            
            source_output = codepipeline.Artifact()
            build_output = codepipeline.Artifact()
            lambda_action = codepipeline_actions.LambdaInvokeAction(
                action_name="Lambda",
                inputs=[source_output, build_output
                ],
                outputs=[
                    codepipeline.Artifact("Out1"),
                    codepipeline.Artifact("Out2")
                ],
                lambda_=fn
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "lambda_": lambda_,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if inputs is not None:
            self._values["inputs"] = inputs
        if outputs is not None:
            self._values["outputs"] = outputs
        if user_parameters is not None:
            self._values["user_parameters"] = user_parameters
        if user_parameters_string is not None:
            self._values["user_parameters_string"] = user_parameters_string

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def lambda_(self) -> _IFunction_6e14f09e:
        '''(experimental) The lambda function to invoke.

        :stability: experimental
        '''
        result = self._values.get("lambda_")
        assert result is not None, "Required property 'lambda_' is missing"
        return typing.cast(_IFunction_6e14f09e, result)

    @builtins.property
    def inputs(self) -> typing.Optional[typing.List[_Artifact_9905eec2]]:
        '''(experimental) The optional input Artifacts of the Action.

        A Lambda Action can have up to 5 inputs.
        The inputs will appear in the event passed to the Lambda,
        under the ``'CodePipeline.job'.data.inputArtifacts`` path.

        :default: the Action will not have any inputs

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-invoke-lambda-function.html#actions-invoke-lambda-function-json-event-example
        :stability: experimental
        '''
        result = self._values.get("inputs")
        return typing.cast(typing.Optional[typing.List[_Artifact_9905eec2]], result)

    @builtins.property
    def outputs(self) -> typing.Optional[typing.List[_Artifact_9905eec2]]:
        '''(experimental) The optional names of the output Artifacts of the Action.

        A Lambda Action can have up to 5 outputs.
        The outputs will appear in the event passed to the Lambda,
        under the ``'CodePipeline.job'.data.outputArtifacts`` path.
        It is the responsibility of the Lambda to upload ZIP files with the Artifact contents to the provided locations.

        :default: the Action will not have any outputs

        :stability: experimental
        '''
        result = self._values.get("outputs")
        return typing.cast(typing.Optional[typing.List[_Artifact_9905eec2]], result)

    @builtins.property
    def user_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''(experimental) A set of key-value pairs that will be accessible to the invoked Lambda inside the event that the Pipeline will call it with.

        Only one of ``userParameters`` or ``userParametersString`` can be specified.

        :default: - no user parameters will be passed

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-invoke-lambda-function.html#actions-invoke-lambda-function-json-event-example
        :stability: experimental
        '''
        result = self._values.get("user_parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    @builtins.property
    def user_parameters_string(self) -> typing.Optional[builtins.str]:
        '''(experimental) The string representation of the user parameters that will be accessible to the invoked Lambda inside the event that the Pipeline will call it with.

        Only one of ``userParametersString`` or ``userParameters`` can be specified.

        :default: - no user parameters will be passed

        :stability: experimental
        '''
        result = self._values.get("user_parameters_string")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaInvokeActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ManualApprovalAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.ManualApprovalAction",
):
    '''(experimental) Manual approval action.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as sns
        
        
        pipeline = codepipeline.Pipeline(self, "MyPipeline")
        approve_stage = pipeline.add_stage(stage_name="Approve")
        manual_approval_action = codepipeline_actions.ManualApprovalAction(
            action_name="Approve",
            notification_topic=sns.Topic(self, "Topic"),  # optional
            notify_emails=["some_email@example.com"
            ],  # optional
            additional_information="additional info"
        )
        approve_stage.add_action(manual_approval_action)
    '''

    def __init__(
        self,
        *,
        additional_information: typing.Optional[builtins.str] = None,
        external_entity_link: typing.Optional[builtins.str] = None,
        notification_topic: typing.Optional[_ITopic_465e36b9] = None,
        notify_emails: typing.Optional[typing.Sequence[builtins.str]] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param additional_information: (experimental) Any additional information that you want to include in the notification email message.
        :param external_entity_link: (experimental) URL you want to provide to the reviewer as part of the approval request. Default: - the approval request will not have an external link
        :param notification_topic: (experimental) Optional SNS topic to send notifications to when an approval is pending.
        :param notify_emails: (experimental) A list of email addresses to subscribe to notifications when this Action is pending approval. If this has been provided, but not ``notificationTopic``, a new Topic will be created.
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = ManualApprovalActionProps(
            additional_information=additional_information,
            external_entity_link=external_entity_link,
            notification_topic=notification_topic,
            notify_emails=notify_emails,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [scope, stage, options]))

    @jsii.member(jsii_name="grantManualApproval")
    def grant_manual_approval(self, grantable: _IGrantable_4c5a91d1) -> None:
        '''(experimental) grant the provided principal the permissions to approve or reject this manual approval action.

        For more info see:
        https://docs.aws.amazon.com/codepipeline/latest/userguide/approvals-iam-permissions.html

        :param grantable: the grantable to attach the permissions to.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "grantManualApproval", [grantable]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationTopic")
    def notification_topic(self) -> typing.Optional[_ITopic_465e36b9]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_ITopic_465e36b9], jsii.get(self, "notificationTopic"))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.ManualApprovalActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "additional_information": "additionalInformation",
        "external_entity_link": "externalEntityLink",
        "notification_topic": "notificationTopic",
        "notify_emails": "notifyEmails",
    },
)
class ManualApprovalActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        additional_information: typing.Optional[builtins.str] = None,
        external_entity_link: typing.Optional[builtins.str] = None,
        notification_topic: typing.Optional[_ITopic_465e36b9] = None,
        notify_emails: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link ManualApprovalAction}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param additional_information: (experimental) Any additional information that you want to include in the notification email message.
        :param external_entity_link: (experimental) URL you want to provide to the reviewer as part of the approval request. Default: - the approval request will not have an external link
        :param notification_topic: (experimental) Optional SNS topic to send notifications to when an approval is pending.
        :param notify_emails: (experimental) A list of email addresses to subscribe to notifications when this Action is pending approval. If this has been provided, but not ``notificationTopic``, a new Topic will be created.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import monocdk as sns
            
            
            pipeline = codepipeline.Pipeline(self, "MyPipeline")
            approve_stage = pipeline.add_stage(stage_name="Approve")
            manual_approval_action = codepipeline_actions.ManualApprovalAction(
                action_name="Approve",
                notification_topic=sns.Topic(self, "Topic"),  # optional
                notify_emails=["some_email@example.com"
                ],  # optional
                additional_information="additional info"
            )
            approve_stage.add_action(manual_approval_action)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if additional_information is not None:
            self._values["additional_information"] = additional_information
        if external_entity_link is not None:
            self._values["external_entity_link"] = external_entity_link
        if notification_topic is not None:
            self._values["notification_topic"] = notification_topic
        if notify_emails is not None:
            self._values["notify_emails"] = notify_emails

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def additional_information(self) -> typing.Optional[builtins.str]:
        '''(experimental) Any additional information that you want to include in the notification email message.

        :stability: experimental
        '''
        result = self._values.get("additional_information")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_entity_link(self) -> typing.Optional[builtins.str]:
        '''(experimental) URL you want to provide to the reviewer as part of the approval request.

        :default: - the approval request will not have an external link

        :stability: experimental
        '''
        result = self._values.get("external_entity_link")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification_topic(self) -> typing.Optional[_ITopic_465e36b9]:
        '''(experimental) Optional SNS topic to send notifications to when an approval is pending.

        :stability: experimental
        '''
        result = self._values.get("notification_topic")
        return typing.cast(typing.Optional[_ITopic_465e36b9], result)

    @builtins.property
    def notify_emails(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A list of email addresses to subscribe to notifications when this Action is pending approval.

        If this has been provided, but not ``notificationTopic``,
        a new Topic will be created.

        :stability: experimental
        '''
        result = self._values.get("notify_emails")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManualApprovalActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3DeployAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.S3DeployAction",
):
    '''(experimental) Deploys the sourceArtifact to Amazon S3.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        source_output = codepipeline.Artifact()
        target_bucket = s3.Bucket(self, "MyBucket")
        
        pipeline = codepipeline.Pipeline(self, "MyPipeline")
        deploy_action = codepipeline_actions.S3DeployAction(
            action_name="S3Deploy",
            bucket=target_bucket,
            input=source_output
        )
        deploy_stage = pipeline.add_stage(
            stage_name="Deploy",
            actions=[deploy_action]
        )
    '''

    def __init__(
        self,
        *,
        bucket: _IBucket_73486e29,
        input: _Artifact_9905eec2,
        access_control: typing.Optional[_BucketAccessControl_a8cb5bce] = None,
        cache_control: typing.Optional[typing.Sequence[CacheControl]] = None,
        extract: typing.Optional[builtins.bool] = None,
        object_key: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: (experimental) The Amazon S3 bucket that is the deploy target.
        :param input: (experimental) The input Artifact to deploy to Amazon S3.
        :param access_control: (experimental) The specified canned ACL to objects deployed to Amazon S3. This overwrites any existing ACL that was applied to the object. Default: - the original object ACL
        :param cache_control: (experimental) The caching behavior for requests/responses for objects in the bucket. The final cache control property will be the result of joining all of the provided array elements with a comma (plus a space after the comma). Default: - none, decided by the HTTP client
        :param extract: (experimental) Should the deploy action extract the artifact before deploying to Amazon S3. Default: true
        :param object_key: (experimental) The key of the target object. This is required if extract is false.
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = S3DeployActionProps(
            bucket=bucket,
            input=input,
            access_control=access_control,
            cache_control=cache_control,
            extract=extract,
            object_key=object_key,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, _stage, options]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.S3DeployActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "bucket": "bucket",
        "input": "input",
        "access_control": "accessControl",
        "cache_control": "cacheControl",
        "extract": "extract",
        "object_key": "objectKey",
    },
)
class S3DeployActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        bucket: _IBucket_73486e29,
        input: _Artifact_9905eec2,
        access_control: typing.Optional[_BucketAccessControl_a8cb5bce] = None,
        cache_control: typing.Optional[typing.Sequence[CacheControl]] = None,
        extract: typing.Optional[builtins.bool] = None,
        object_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link S3DeployAction S3 deploy Action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param bucket: (experimental) The Amazon S3 bucket that is the deploy target.
        :param input: (experimental) The input Artifact to deploy to Amazon S3.
        :param access_control: (experimental) The specified canned ACL to objects deployed to Amazon S3. This overwrites any existing ACL that was applied to the object. Default: - the original object ACL
        :param cache_control: (experimental) The caching behavior for requests/responses for objects in the bucket. The final cache control property will be the result of joining all of the provided array elements with a comma (plus a space after the comma). Default: - none, decided by the HTTP client
        :param extract: (experimental) Should the deploy action extract the artifact before deploying to Amazon S3. Default: true
        :param object_key: (experimental) The key of the target object. This is required if extract is false.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            source_output = codepipeline.Artifact()
            target_bucket = s3.Bucket(self, "MyBucket")
            
            pipeline = codepipeline.Pipeline(self, "MyPipeline")
            deploy_action = codepipeline_actions.S3DeployAction(
                action_name="S3Deploy",
                bucket=target_bucket,
                input=source_output
            )
            deploy_stage = pipeline.add_stage(
                stage_name="Deploy",
                actions=[deploy_action]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "bucket": bucket,
            "input": input,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if access_control is not None:
            self._values["access_control"] = access_control
        if cache_control is not None:
            self._values["cache_control"] = cache_control
        if extract is not None:
            self._values["extract"] = extract
        if object_key is not None:
            self._values["object_key"] = object_key

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def bucket(self) -> _IBucket_73486e29:
        '''(experimental) The Amazon S3 bucket that is the deploy target.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_IBucket_73486e29, result)

    @builtins.property
    def input(self) -> _Artifact_9905eec2:
        '''(experimental) The input Artifact to deploy to Amazon S3.

        :stability: experimental
        '''
        result = self._values.get("input")
        assert result is not None, "Required property 'input' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def access_control(self) -> typing.Optional[_BucketAccessControl_a8cb5bce]:
        '''(experimental) The specified canned ACL to objects deployed to Amazon S3.

        This overwrites any existing ACL that was applied to the object.

        :default: - the original object ACL

        :stability: experimental
        '''
        result = self._values.get("access_control")
        return typing.cast(typing.Optional[_BucketAccessControl_a8cb5bce], result)

    @builtins.property
    def cache_control(self) -> typing.Optional[typing.List[CacheControl]]:
        '''(experimental) The caching behavior for requests/responses for objects in the bucket.

        The final cache control property will be the result of joining all of the provided array elements with a comma
        (plus a space after the comma).

        :default: - none, decided by the HTTP client

        :stability: experimental
        '''
        result = self._values.get("cache_control")
        return typing.cast(typing.Optional[typing.List[CacheControl]], result)

    @builtins.property
    def extract(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should the deploy action extract the artifact before deploying to Amazon S3.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("extract")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def object_key(self) -> typing.Optional[builtins.str]:
        '''(experimental) The key of the target object.

        This is required if extract is false.

        :stability: experimental
        '''
        result = self._values.get("object_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3DeployActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class S3SourceAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.S3SourceAction",
):
    '''(experimental) Source that is provided by a specific Amazon S3 object.

    Will trigger the pipeline as soon as the S3 object changes, but only if there is
    a CloudTrail Trail in the account that captures the S3 event.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as cloudtrail
        
        # source_bucket: s3.Bucket
        
        source_output = codepipeline.Artifact()
        key = "some/key.zip"
        trail = cloudtrail.Trail(self, "CloudTrail")
        trail.add_s3_event_selector([cloudtrail.aws_cloudtrail.S3EventSelector(
            bucket=source_bucket,
            object_prefix=key
        )],
            read_write_type=cloudtrail.ReadWriteType.WRITE_ONLY
        )
        source_action = codepipeline_actions.S3SourceAction(
            action_name="S3Source",
            bucket_key=key,
            bucket=source_bucket,
            output=source_output,
            trigger=codepipeline_actions.S3Trigger.EVENTS
        )
    '''

    def __init__(
        self,
        *,
        bucket: _IBucket_73486e29,
        bucket_key: builtins.str,
        output: _Artifact_9905eec2,
        trigger: typing.Optional["S3Trigger"] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: (experimental) The Amazon S3 bucket that stores the source code. If you import an encrypted bucket in your stack, please specify the encryption key at import time by using ``Bucket.fromBucketAttributes()`` method.
        :param bucket_key: (experimental) The key within the S3 bucket that stores the source code.
        :param output: 
        :param trigger: (experimental) How should CodePipeline detect source changes for this Action. Note that if this is S3Trigger.EVENTS, you need to make sure to include the source Bucket in a CloudTrail Trail, as otherwise the CloudWatch Events will not be emitted. Default: S3Trigger.POLL
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = S3SourceActionProps(
            bucket=bucket,
            bucket_key=bucket_key,
            output=output,
            trigger=trigger,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, stage, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="variables")
    def variables(self) -> "S3SourceVariables":
        '''(experimental) The variables emitted by this action.

        :stability: experimental
        '''
        return typing.cast("S3SourceVariables", jsii.get(self, "variables"))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.S3SourceActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "bucket": "bucket",
        "bucket_key": "bucketKey",
        "output": "output",
        "trigger": "trigger",
    },
)
class S3SourceActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        bucket: _IBucket_73486e29,
        bucket_key: builtins.str,
        output: _Artifact_9905eec2,
        trigger: typing.Optional["S3Trigger"] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link S3SourceAction S3 source Action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param bucket: (experimental) The Amazon S3 bucket that stores the source code. If you import an encrypted bucket in your stack, please specify the encryption key at import time by using ``Bucket.fromBucketAttributes()`` method.
        :param bucket_key: (experimental) The key within the S3 bucket that stores the source code.
        :param output: 
        :param trigger: (experimental) How should CodePipeline detect source changes for this Action. Note that if this is S3Trigger.EVENTS, you need to make sure to include the source Bucket in a CloudTrail Trail, as otherwise the CloudWatch Events will not be emitted. Default: S3Trigger.POLL

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import monocdk as cloudtrail
            
            # source_bucket: s3.Bucket
            
            source_output = codepipeline.Artifact()
            key = "some/key.zip"
            trail = cloudtrail.Trail(self, "CloudTrail")
            trail.add_s3_event_selector([cloudtrail.aws_cloudtrail.S3EventSelector(
                bucket=source_bucket,
                object_prefix=key
            )],
                read_write_type=cloudtrail.ReadWriteType.WRITE_ONLY
            )
            source_action = codepipeline_actions.S3SourceAction(
                action_name="S3Source",
                bucket_key=key,
                bucket=source_bucket,
                output=source_output,
                trigger=codepipeline_actions.S3Trigger.EVENTS
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "bucket": bucket,
            "bucket_key": bucket_key,
            "output": output,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if trigger is not None:
            self._values["trigger"] = trigger

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def bucket(self) -> _IBucket_73486e29:
        '''(experimental) The Amazon S3 bucket that stores the source code.

        If you import an encrypted bucket in your stack, please specify
        the encryption key at import time by using ``Bucket.fromBucketAttributes()`` method.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_IBucket_73486e29, result)

    @builtins.property
    def bucket_key(self) -> builtins.str:
        '''(experimental) The key within the S3 bucket that stores the source code.

        :stability: experimental

        Example::

            "path/to/file.zip"
        '''
        result = self._values.get("bucket_key")
        assert result is not None, "Required property 'bucket_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output(self) -> _Artifact_9905eec2:
        '''
        :stability: experimental
        '''
        result = self._values.get("output")
        assert result is not None, "Required property 'output' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def trigger(self) -> typing.Optional["S3Trigger"]:
        '''(experimental) How should CodePipeline detect source changes for this Action.

        Note that if this is S3Trigger.EVENTS, you need to make sure to include the source Bucket in a CloudTrail Trail,
        as otherwise the CloudWatch Events will not be emitted.

        :default: S3Trigger.POLL

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/log-s3-data-events.html
        :stability: experimental
        '''
        result = self._values.get("trigger")
        return typing.cast(typing.Optional["S3Trigger"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3SourceActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.S3SourceVariables",
    jsii_struct_bases=[],
    name_mapping={"e_tag": "eTag", "version_id": "versionId"},
)
class S3SourceVariables:
    def __init__(self, *, e_tag: builtins.str, version_id: builtins.str) -> None:
        '''(experimental) The CodePipeline variables emitted by the S3 source Action.

        :param e_tag: (experimental) The e-tag of the S3 version of the object that triggered the build.
        :param version_id: (experimental) The identifier of the S3 version of the object that triggered the build.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            
            s3_source_variables = codepipeline_actions.S3SourceVariables(
                e_tag="eTag",
                version_id="versionId"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "e_tag": e_tag,
            "version_id": version_id,
        }

    @builtins.property
    def e_tag(self) -> builtins.str:
        '''(experimental) The e-tag of the S3 version of the object that triggered the build.

        :stability: experimental
        '''
        result = self._values.get("e_tag")
        assert result is not None, "Required property 'e_tag' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def version_id(self) -> builtins.str:
        '''(experimental) The identifier of the S3 version of the object that triggered the build.

        :stability: experimental
        '''
        result = self._values.get("version_id")
        assert result is not None, "Required property 'version_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3SourceVariables(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_codepipeline_actions.S3Trigger")
class S3Trigger(enum.Enum):
    '''(experimental) How should the S3 Action detect changes.

    This is the type of the {@link S3SourceAction.trigger} property.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as cloudtrail
        
        # source_bucket: s3.Bucket
        
        source_output = codepipeline.Artifact()
        key = "some/key.zip"
        trail = cloudtrail.Trail(self, "CloudTrail")
        trail.add_s3_event_selector([cloudtrail.aws_cloudtrail.S3EventSelector(
            bucket=source_bucket,
            object_prefix=key
        )],
            read_write_type=cloudtrail.ReadWriteType.WRITE_ONLY
        )
        source_action = codepipeline_actions.S3SourceAction(
            action_name="S3Source",
            bucket_key=key,
            bucket=source_bucket,
            output=source_output,
            trigger=codepipeline_actions.S3Trigger.EVENTS
        )
    '''

    NONE = "NONE"
    '''(experimental) The Action will never detect changes - the Pipeline it's part of will only begin a run when explicitly started.

    :stability: experimental
    '''
    POLL = "POLL"
    '''(experimental) CodePipeline will poll S3 to detect changes.

    This is the default method of detecting changes.

    :stability: experimental
    '''
    EVENTS = "EVENTS"
    '''(experimental) CodePipeline will use CloudWatch Events to be notified of changes.

    Note that the Bucket that the Action uses needs to be part of a CloudTrail Trail
    for the events to be delivered.

    :stability: experimental
    '''


class ServiceCatalogDeployActionBeta1(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.ServiceCatalogDeployActionBeta1",
):
    '''(experimental) CodePipeline action to connect to an existing ServiceCatalog product.

    **Note**: this class is still experimental, and may have breaking changes in the future!

    :stability: experimental
    :exampleMetadata: infused

    Example::

        cdk_build_output = codepipeline.Artifact()
        service_catalog_deploy_action = codepipeline_actions.ServiceCatalogDeployActionBeta1(
            action_name="ServiceCatalogDeploy",
            template_path=cdk_build_output.at_path("Sample.template.json"),
            product_version_name="Version - " + Date.now.to_string,
            product_version_description="This is a version from the pipeline with a new description.",
            product_id="prod-XXXXXXXX"
        )
    '''

    def __init__(
        self,
        *,
        product_id: builtins.str,
        product_version_name: builtins.str,
        template_path: _ArtifactPath_a5b79113,
        product_version_description: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param product_id: (experimental) The identifier of the product in the Service Catalog. This product must already exist.
        :param product_version_name: (experimental) The name of the version of the Service Catalog product to be deployed.
        :param template_path: (experimental) The path to the cloudformation artifact.
        :param product_version_description: (experimental) The optional description of this version of the Service Catalog product. Default: ''
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = ServiceCatalogDeployActionBeta1Props(
            product_id=product_id,
            product_version_name=product_version_name,
            template_path=template_path,
            product_version_description=product_version_description,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, _stage, options]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.ServiceCatalogDeployActionBeta1Props",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "product_id": "productId",
        "product_version_name": "productVersionName",
        "template_path": "templatePath",
        "product_version_description": "productVersionDescription",
    },
)
class ServiceCatalogDeployActionBeta1Props(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        product_id: builtins.str,
        product_version_name: builtins.str,
        template_path: _ArtifactPath_a5b79113,
        product_version_description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link ServiceCatalogDeployActionBeta1 ServiceCatalog deploy CodePipeline Action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param product_id: (experimental) The identifier of the product in the Service Catalog. This product must already exist.
        :param product_version_name: (experimental) The name of the version of the Service Catalog product to be deployed.
        :param template_path: (experimental) The path to the cloudformation artifact.
        :param product_version_description: (experimental) The optional description of this version of the Service Catalog product. Default: ''

        :stability: experimental
        :exampleMetadata: infused

        Example::

            cdk_build_output = codepipeline.Artifact()
            service_catalog_deploy_action = codepipeline_actions.ServiceCatalogDeployActionBeta1(
                action_name="ServiceCatalogDeploy",
                template_path=cdk_build_output.at_path("Sample.template.json"),
                product_version_name="Version - " + Date.now.to_string,
                product_version_description="This is a version from the pipeline with a new description.",
                product_id="prod-XXXXXXXX"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "product_id": product_id,
            "product_version_name": product_version_name,
            "template_path": template_path,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if product_version_description is not None:
            self._values["product_version_description"] = product_version_description

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def product_id(self) -> builtins.str:
        '''(experimental) The identifier of the product in the Service Catalog.

        This product must already exist.

        :stability: experimental
        '''
        result = self._values.get("product_id")
        assert result is not None, "Required property 'product_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def product_version_name(self) -> builtins.str:
        '''(experimental) The name of the version of the Service Catalog product to be deployed.

        :stability: experimental
        '''
        result = self._values.get("product_version_name")
        assert result is not None, "Required property 'product_version_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template_path(self) -> _ArtifactPath_a5b79113:
        '''(experimental) The path to the cloudformation artifact.

        :stability: experimental
        '''
        result = self._values.get("template_path")
        assert result is not None, "Required property 'template_path' is missing"
        return typing.cast(_ArtifactPath_a5b79113, result)

    @builtins.property
    def product_version_description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The optional description of this version of the Service Catalog product.

        :default: ''

        :stability: experimental
        '''
        result = self._values.get("product_version_description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceCatalogDeployActionBeta1Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StateMachineInput(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.StateMachineInput",
):
    '''(experimental) Represents the input for the StateMachine.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as stepfunctions
        
        pipeline = codepipeline.Pipeline(self, "MyPipeline")
        start_state = stepfunctions.Pass(self, "StartState")
        simple_state_machine = stepfunctions.StateMachine(self, "SimpleStateMachine",
            definition=start_state
        )
        step_function_action = codepipeline_actions.StepFunctionInvokeAction(
            action_name="Invoke",
            state_machine=simple_state_machine,
            state_machine_input=codepipeline_actions.StateMachineInput.literal({"IsHelloWorldExample": True})
        )
        pipeline.add_stage(
            stage_name="StepFunctions",
            actions=[step_function_action]
        )
    '''

    @jsii.member(jsii_name="filePath") # type: ignore[misc]
    @builtins.classmethod
    def file_path(cls, input_file: _ArtifactPath_a5b79113) -> "StateMachineInput":
        '''(experimental) When the input type is FilePath, input artifact and filepath must be specified.

        :param input_file: -

        :stability: experimental
        '''
        return typing.cast("StateMachineInput", jsii.sinvoke(cls, "filePath", [input_file]))

    @jsii.member(jsii_name="literal") # type: ignore[misc]
    @builtins.classmethod
    def literal(
        cls,
        object: typing.Mapping[typing.Any, typing.Any],
    ) -> "StateMachineInput":
        '''(experimental) When the input type is Literal, input value is passed directly to the state machine input.

        :param object: -

        :stability: experimental
        '''
        return typing.cast("StateMachineInput", jsii.sinvoke(cls, "literal", [object]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="input")
    def input(self) -> typing.Any:
        '''(experimental) When InputType is set to Literal (default), the Input field is used directly as the input for the state machine execution.

        Otherwise, the state machine is invoked with an empty JSON object {}.

        When InputType is set to FilePath, this field is required.
        An input artifact is also required when InputType is set to FilePath.

        :default: - none

        :stability: experimental
        '''
        return typing.cast(typing.Any, jsii.get(self, "input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputArtifact")
    def input_artifact(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) The optional input Artifact of the Action.

        If InputType is set to FilePath, this artifact is required
        and is used to source the input for the state machine execution.

        :default: - the Action will not have any inputs

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-StepFunctions.html#action-reference-StepFunctions-example
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_Artifact_9905eec2], jsii.get(self, "inputArtifact"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputType")
    def input_type(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional StateMachine InputType InputType can be Literal or FilePath.

        :default: - Literal

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inputType"))


class StepFunctionInvokeAction(
    Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.StepFunctionInvokeAction",
):
    '''(experimental) StepFunctionInvokeAction that is provided by an AWS CodePipeline.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as stepfunctions
        
        pipeline = codepipeline.Pipeline(self, "MyPipeline")
        start_state = stepfunctions.Pass(self, "StartState")
        simple_state_machine = stepfunctions.StateMachine(self, "SimpleStateMachine",
            definition=start_state
        )
        step_function_action = codepipeline_actions.StepFunctionInvokeAction(
            action_name="Invoke",
            state_machine=simple_state_machine,
            state_machine_input=codepipeline_actions.StateMachineInput.literal({"IsHelloWorldExample": True})
        )
        pipeline.add_stage(
            stage_name="StepFunctions",
            actions=[step_function_action]
        )
    '''

    def __init__(
        self,
        *,
        state_machine: _IStateMachine_269a89c4,
        execution_name_prefix: typing.Optional[builtins.str] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        state_machine_input: typing.Optional[StateMachineInput] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param state_machine: (experimental) The state machine to invoke.
        :param execution_name_prefix: (experimental) Prefix (optional). By default, the action execution ID is used as the state machine execution name. If a prefix is provided, it is prepended to the action execution ID with a hyphen and together used as the state machine execution name. Default: - action execution ID
        :param output: (experimental) The optional output Artifact of the Action. Default: the Action will not have any outputs
        :param state_machine_input: (experimental) Represents the input to the StateMachine. This includes input artifact, input type and the statemachine input. Default: - none
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set

        :stability: experimental
        '''
        props = StepFunctionsInvokeActionProps(
            state_machine=state_machine,
            execution_name_prefix=execution_name_prefix,
            output=output,
            state_machine_input=state_machine_input,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        _scope: _Construct_e78e779f,
        _stage: _IStage_5a7e7342,
        *,
        bucket: _IBucket_73486e29,
        role: _IRole_59af6f50,
    ) -> _ActionConfig_0c698b52:
        '''(experimental) This is a renamed version of the {@link IAction.bind} method.

        :param _scope: -
        :param _stage: -
        :param bucket: 
        :param role: 

        :stability: experimental
        '''
        options = _ActionBindOptions_20e0a317(bucket=bucket, role=role)

        return typing.cast(_ActionConfig_0c698b52, jsii.invoke(self, "bound", [_scope, _stage, options]))


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.StepFunctionsInvokeActionProps",
    jsii_struct_bases=[_CommonAwsActionProps_1494edc0],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "state_machine": "stateMachine",
        "execution_name_prefix": "executionNamePrefix",
        "output": "output",
        "state_machine_input": "stateMachineInput",
    },
)
class StepFunctionsInvokeActionProps(_CommonAwsActionProps_1494edc0):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        state_machine: _IStateMachine_269a89c4,
        execution_name_prefix: typing.Optional[builtins.str] = None,
        output: typing.Optional[_Artifact_9905eec2] = None,
        state_machine_input: typing.Optional[StateMachineInput] = None,
    ) -> None:
        '''(experimental) Construction properties of the {@link StepFunctionsInvokeAction StepFunction Invoke Action}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param state_machine: (experimental) The state machine to invoke.
        :param execution_name_prefix: (experimental) Prefix (optional). By default, the action execution ID is used as the state machine execution name. If a prefix is provided, it is prepended to the action execution ID with a hyphen and together used as the state machine execution name. Default: - action execution ID
        :param output: (experimental) The optional output Artifact of the Action. Default: the Action will not have any outputs
        :param state_machine_input: (experimental) Represents the input to the StateMachine. This includes input artifact, input type and the statemachine input. Default: - none

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import monocdk as stepfunctions
            
            pipeline = codepipeline.Pipeline(self, "MyPipeline")
            start_state = stepfunctions.Pass(self, "StartState")
            simple_state_machine = stepfunctions.StateMachine(self, "SimpleStateMachine",
                definition=start_state
            )
            step_function_action = codepipeline_actions.StepFunctionInvokeAction(
                action_name="Invoke",
                state_machine=simple_state_machine,
                state_machine_input=codepipeline_actions.StateMachineInput.literal({"IsHelloWorldExample": True})
            )
            pipeline.add_stage(
                stage_name="StepFunctions",
                actions=[step_function_action]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "state_machine": state_machine,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if execution_name_prefix is not None:
            self._values["execution_name_prefix"] = execution_name_prefix
        if output is not None:
            self._values["output"] = output
        if state_machine_input is not None:
            self._values["state_machine_input"] = state_machine_input

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def state_machine(self) -> _IStateMachine_269a89c4:
        '''(experimental) The state machine to invoke.

        :stability: experimental
        '''
        result = self._values.get("state_machine")
        assert result is not None, "Required property 'state_machine' is missing"
        return typing.cast(_IStateMachine_269a89c4, result)

    @builtins.property
    def execution_name_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Prefix (optional).

        By default, the action execution ID is used as the state machine execution name.
        If a prefix is provided, it is prepended to the action execution ID with a hyphen and
        together used as the state machine execution name.

        :default: - action execution ID

        :stability: experimental
        '''
        result = self._values.get("execution_name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def output(self) -> typing.Optional[_Artifact_9905eec2]:
        '''(experimental) The optional output Artifact of the Action.

        :default: the Action will not have any outputs

        :stability: experimental
        '''
        result = self._values.get("output")
        return typing.cast(typing.Optional[_Artifact_9905eec2], result)

    @builtins.property
    def state_machine_input(self) -> typing.Optional[StateMachineInput]:
        '''(experimental) Represents the input to the StateMachine.

        This includes input artifact, input type and the statemachine input.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("state_machine_input")
        return typing.cast(typing.Optional[StateMachineInput], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StepFunctionsInvokeActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IJenkinsProvider)
class BaseJenkinsProvider(
    _Construct_e78e779f,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="monocdk.aws_codepipeline_actions.BaseJenkinsProvider",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param version: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id, version])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerName")
    @abc.abstractmethod
    def provider_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverUrl")
    @abc.abstractmethod
    def server_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))


class _BaseJenkinsProviderProxy(BaseJenkinsProvider):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverUrl")
    def server_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serverUrl"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseJenkinsProvider).__jsii_proxy_class__ = lambda : _BaseJenkinsProviderProxy


@jsii.data_type(
    jsii_type="monocdk.aws_codepipeline_actions.BitBucketSourceActionProps",
    jsii_struct_bases=[CodeStarConnectionsSourceActionProps],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "connection_arn": "connectionArn",
        "output": "output",
        "owner": "owner",
        "repo": "repo",
        "branch": "branch",
        "code_build_clone_output": "codeBuildCloneOutput",
        "trigger_on_push": "triggerOnPush",
    },
)
class BitBucketSourceActionProps(CodeStarConnectionsSourceActionProps):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        connection_arn: builtins.str,
        output: _Artifact_9905eec2,
        owner: builtins.str,
        repo: builtins.str,
        branch: typing.Optional[builtins.str] = None,
        code_build_clone_output: typing.Optional[builtins.bool] = None,
        trigger_on_push: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(deprecated) Construction properties for {@link BitBucketSourceAction}.

        :param action_name: (experimental) The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: (experimental) The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: (experimental) The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: (experimental) The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param connection_arn: (experimental) The ARN of the CodeStar Connection created in the AWS console that has permissions to access this GitHub or BitBucket repository.
        :param output: (experimental) The output artifact that this action produces. Can be used as input for further pipeline actions.
        :param owner: (experimental) The owning user or organization of the repository.
        :param repo: (experimental) The name of the repository.
        :param branch: (experimental) The branch to build. Default: 'master'
        :param code_build_clone_output: (experimental) Whether the output should be the contents of the repository (which is the default), or a link that allows CodeBuild to clone the repository before building. **Note**: if this option is true, then only CodeBuild actions can use the resulting {@link output}. Default: false
        :param trigger_on_push: (experimental) Controls automatically starting your pipeline when a new commit is made on the configured repository and branch. If unspecified, the default value is true, and the field does not display by default. Default: true

        :deprecated: use CodeStarConnectionsSourceActionProps instead

        :stability: deprecated
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_codepipeline as codepipeline
            from monocdk import aws_codepipeline_actions as codepipeline_actions
            from monocdk import aws_iam as iam
            
            # artifact: codepipeline.Artifact
            # role: iam.Role
            
            bit_bucket_source_action_props = codepipeline_actions.BitBucketSourceActionProps(
                action_name="actionName",
                connection_arn="connectionArn",
                output=artifact,
                owner="owner",
                repo="repo",
            
                # the properties below are optional
                branch="branch",
                code_build_clone_output=False,
                role=role,
                run_order=123,
                trigger_on_push=False,
                variables_namespace="variablesNamespace"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "connection_arn": connection_arn,
            "output": output,
            "owner": owner,
            "repo": repo,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if branch is not None:
            self._values["branch"] = branch
        if code_build_clone_output is not None:
            self._values["code_build_clone_output"] = code_build_clone_output
        if trigger_on_push is not None:
            self._values["trigger_on_push"] = trigger_on_push

    @builtins.property
    def action_name(self) -> builtins.str:
        '''(experimental) The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.

        :stability: experimental
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        :stability: experimental
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set

        :stability: experimental
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def connection_arn(self) -> builtins.str:
        '''(experimental) The ARN of the CodeStar Connection created in the AWS console that has permissions to access this GitHub or BitBucket repository.

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/connections-create.html
        :stability: experimental

        Example::

            "arn:aws:codestar-connections:us-east-1:123456789012:connection/12345678-abcd-12ab-34cdef5678gh"
        '''
        result = self._values.get("connection_arn")
        assert result is not None, "Required property 'connection_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def output(self) -> _Artifact_9905eec2:
        '''(experimental) The output artifact that this action produces.

        Can be used as input for further pipeline actions.

        :stability: experimental
        '''
        result = self._values.get("output")
        assert result is not None, "Required property 'output' is missing"
        return typing.cast(_Artifact_9905eec2, result)

    @builtins.property
    def owner(self) -> builtins.str:
        '''(experimental) The owning user or organization of the repository.

        :stability: experimental

        Example::

            "aws"
        '''
        result = self._values.get("owner")
        assert result is not None, "Required property 'owner' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo(self) -> builtins.str:
        '''(experimental) The name of the repository.

        :stability: experimental

        Example::

            "aws-cdk"
        '''
        result = self._values.get("repo")
        assert result is not None, "Required property 'repo' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def branch(self) -> typing.Optional[builtins.str]:
        '''(experimental) The branch to build.

        :default: 'master'

        :stability: experimental
        '''
        result = self._values.get("branch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def code_build_clone_output(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the output should be the contents of the repository (which is the default), or a link that allows CodeBuild to clone the repository before building.

        **Note**: if this option is true,
        then only CodeBuild actions can use the resulting {@link output}.

        :default: false

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodestarConnectionSource.html#action-reference-CodestarConnectionSource-config
        :stability: experimental
        '''
        result = self._values.get("code_build_clone_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def trigger_on_push(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Controls automatically starting your pipeline when a new commit is made on the configured repository and branch.

        If unspecified,
        the default value is true, and the field does not display by default.

        :default: true

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodestarConnectionSource.html
        :stability: experimental
        '''
        result = self._values.get("trigger_on_push")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BitBucketSourceActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class JenkinsProvider(
    BaseJenkinsProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_codepipeline_actions.JenkinsProvider",
):
    '''(experimental) A class representing Jenkins providers.

    :see: #import
    :stability: experimental
    :exampleMetadata: infused

    Example::

        jenkins_provider = codepipeline_actions.JenkinsProvider(self, "JenkinsProvider",
            provider_name="MyJenkinsProvider",
            server_url="http://my-jenkins.com:8080",
            version="2"
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        provider_name: builtins.str,
        server_url: builtins.str,
        for_build: typing.Optional[builtins.bool] = None,
        for_test: typing.Optional[builtins.bool] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param provider_name: (experimental) The name of the Jenkins provider that you set in the AWS CodePipeline plugin configuration of your Jenkins project.
        :param server_url: (experimental) The base URL of your Jenkins server.
        :param for_build: (experimental) Whether to immediately register a Jenkins Provider for the build category. The Provider will always be registered if you create a {@link JenkinsAction}. Default: false
        :param for_test: (experimental) Whether to immediately register a Jenkins Provider for the test category. The Provider will always be registered if you create a {@link JenkinsTestAction}. Default: false
        :param version: (experimental) The version of your provider. Default: '1'

        :stability: experimental
        '''
        props = JenkinsProviderProps(
            provider_name=provider_name,
            server_url=server_url,
            for_build=for_build,
            for_test=for_test,
            version=version,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromJenkinsProviderAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_jenkins_provider_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        provider_name: builtins.str,
        server_url: builtins.str,
        version: typing.Optional[builtins.str] = None,
    ) -> IJenkinsProvider:
        '''(experimental) Import a Jenkins provider registered either outside the CDK, or in a different CDK Stack.

        :param scope: the parent Construct for the new provider.
        :param id: the identifier of the new provider Construct.
        :param provider_name: (experimental) The name of the Jenkins provider that you set in the AWS CodePipeline plugin configuration of your Jenkins project.
        :param server_url: (experimental) The base URL of your Jenkins server.
        :param version: (experimental) The version of your provider. Default: '1'

        :return: a new Construct representing a reference to an existing Jenkins provider

        :stability: experimental
        '''
        attrs = JenkinsProviderAttributes(
            provider_name=provider_name, server_url=server_url, version=version
        )

        return typing.cast(IJenkinsProvider, jsii.sinvoke(cls, "fromJenkinsProviderAttributes", [scope, id, attrs]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverUrl")
    def server_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "serverUrl"))


__all__ = [
    "Action",
    "AlexaSkillDeployAction",
    "AlexaSkillDeployActionProps",
    "BaseJenkinsProvider",
    "BitBucketSourceAction",
    "BitBucketSourceActionProps",
    "CacheControl",
    "CloudFormationCreateReplaceChangeSetAction",
    "CloudFormationCreateReplaceChangeSetActionProps",
    "CloudFormationCreateUpdateStackAction",
    "CloudFormationCreateUpdateStackActionProps",
    "CloudFormationDeleteStackAction",
    "CloudFormationDeleteStackActionProps",
    "CloudFormationExecuteChangeSetAction",
    "CloudFormationExecuteChangeSetActionProps",
    "CodeBuildAction",
    "CodeBuildActionProps",
    "CodeBuildActionType",
    "CodeCommitSourceAction",
    "CodeCommitSourceActionProps",
    "CodeCommitSourceVariables",
    "CodeCommitTrigger",
    "CodeDeployEcsContainerImageInput",
    "CodeDeployEcsDeployAction",
    "CodeDeployEcsDeployActionProps",
    "CodeDeployServerDeployAction",
    "CodeDeployServerDeployActionProps",
    "CodeStarConnectionsSourceAction",
    "CodeStarConnectionsSourceActionProps",
    "CodeStarSourceVariables",
    "EcrSourceAction",
    "EcrSourceActionProps",
    "EcrSourceVariables",
    "EcsDeployAction",
    "EcsDeployActionProps",
    "GitHubSourceAction",
    "GitHubSourceActionProps",
    "GitHubSourceVariables",
    "GitHubTrigger",
    "IJenkinsProvider",
    "JenkinsAction",
    "JenkinsActionProps",
    "JenkinsActionType",
    "JenkinsProvider",
    "JenkinsProviderAttributes",
    "JenkinsProviderProps",
    "LambdaInvokeAction",
    "LambdaInvokeActionProps",
    "ManualApprovalAction",
    "ManualApprovalActionProps",
    "S3DeployAction",
    "S3DeployActionProps",
    "S3SourceAction",
    "S3SourceActionProps",
    "S3SourceVariables",
    "S3Trigger",
    "ServiceCatalogDeployActionBeta1",
    "ServiceCatalogDeployActionBeta1Props",
    "StateMachineInput",
    "StepFunctionInvokeAction",
    "StepFunctionsInvokeActionProps",
]

publication.publish()
