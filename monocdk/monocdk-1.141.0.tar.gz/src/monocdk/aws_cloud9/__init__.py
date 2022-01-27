'''
# AWS Cloud9 Construct Library

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

AWS Cloud9 is a cloud-based integrated development environment (IDE) that lets you write, run, and debug your code with just a
browser. It includes a code editor, debugger, and terminal. Cloud9 comes prepackaged with essential tools for popular
programming languages, including JavaScript, Python, PHP, and more, so you don’t need to install files or configure your
development machine to start new projects. Since your Cloud9 IDE is cloud-based, you can work on your projects from your
office, home, or anywhere using an internet-connected machine. Cloud9 also provides a seamless experience for developing
serverless applications enabling you to easily define resources, debug, and switch between local and remote execution of
serverless applications. With Cloud9, you can quickly share your development environment with your team, enabling you to pair
program and track each other's inputs in real time.

## Creating EC2 Environment

EC2 Environments are defined with `Ec2Environment`. To create an EC2 environment in the private subnet, specify
`subnetSelection` with private `subnetType`.

```python
# create a cloud9 ec2 environment in a new VPC
vpc = ec2.Vpc(self, "VPC", max_azs=3)
cloud9.Ec2Environment(self, "Cloud9Env", vpc=vpc)

# or create the cloud9 environment in the default VPC with specific instanceType
default_vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)
cloud9.Ec2Environment(self, "Cloud9Env2",
    vpc=default_vpc,
    instance_type=ec2.InstanceType("t3.large")
)

# or specify in a different subnetSelection
c9env = cloud9.Ec2Environment(self, "Cloud9Env3",
    vpc=vpc,
    subnet_selection=cloud9.aws_ec2.SubnetSelection(
        subnet_type=ec2.SubnetType.PRIVATE
    )
)

# print the Cloud9 IDE URL in the output
CfnOutput(self, "URL", value=c9env.ide_url)
```

## Cloning Repositories

Use `clonedRepositories` to clone one or multiple AWS Codecommit repositories into the environment:

```python
import monocdk as codecommit

# create a new Cloud9 environment and clone the two repositories
# vpc: ec2.Vpc


# create a codecommit repository to clone into the cloud9 environment
repo_new = codecommit.Repository(self, "RepoNew",
    repository_name="new-repo"
)

# import an existing codecommit repository to clone into the cloud9 environment
repo_existing = codecommit.Repository.from_repository_name(self, "RepoExisting", "existing-repo")
cloud9.Ec2Environment(self, "C9Env",
    vpc=vpc,
    cloned_repositories=[
        cloud9.CloneRepository.from_code_commit(repo_new, "/src/new-repo"),
        cloud9.CloneRepository.from_code_commit(repo_existing, "/src/existing-repo")
    ]
)
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

from .._jsii import *

import constructs
from .. import (
    CfnResource as _CfnResource_e0a482dc,
    CfnTag as _CfnTag_95fbdc29,
    Construct as _Construct_e78e779f,
    IInspectable as _IInspectable_82c04a63,
    IResolvable as _IResolvable_a771d0ef,
    IResource as _IResource_8c1dbbbd,
    Resource as _Resource_abff4495,
    TagManager as _TagManager_0b7ab120,
    TreeInspector as _TreeInspector_1cd1894e,
)
from ..aws_codecommit import IRepository as _IRepository_cdb2a3c0
from ..aws_ec2 import (
    IVpc as _IVpc_6d1f76c4,
    InstanceType as _InstanceType_072ad323,
    SubnetSelection as _SubnetSelection_1284e62c,
)


@jsii.implements(_IInspectable_82c04a63)
class CfnEnvironmentEC2(
    _CfnResource_e0a482dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloud9.CfnEnvironmentEC2",
):
    '''A CloudFormation ``AWS::Cloud9::EnvironmentEC2``.

    The ``AWS::Cloud9::EnvironmentEC2`` resource creates an Amazon EC2 development environment in AWS Cloud9 . For more information, see `Creating an Environment <https://docs.aws.amazon.com/cloud9/latest/user-guide/create-environment.html>`_ in the *AWS Cloud9 User Guide* .

    :cloudformationResource: AWS::Cloud9::EnvironmentEC2
    :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_cloud9 as cloud9
        
        cfn_environment_eC2 = cloud9.CfnEnvironmentEC2(self, "MyCfnEnvironmentEC2",
            instance_type="instanceType",
        
            # the properties below are optional
            automatic_stop_time_minutes=123,
            connection_type="connectionType",
            description="description",
            image_id="imageId",
            name="name",
            owner_arn="ownerArn",
            repositories=[cloud9.CfnEnvironmentEC2.RepositoryProperty(
                path_component="pathComponent",
                repository_url="repositoryUrl"
            )],
            subnet_id="subnetId",
            tags=[CfnTag(
                key="key",
                value="value"
            )]
        )
    '''

    def __init__(
        self,
        scope: _Construct_e78e779f,
        id: builtins.str,
        *,
        instance_type: builtins.str,
        automatic_stop_time_minutes: typing.Optional[jsii.Number] = None,
        connection_type: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner_arn: typing.Optional[builtins.str] = None,
        repositories: typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.Sequence[typing.Union["CfnEnvironmentEC2.RepositoryProperty", _IResolvable_a771d0ef]]]] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Create a new ``AWS::Cloud9::EnvironmentEC2``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param instance_type: The type of instance to connect to the environment (for example, ``t2.micro`` ).
        :param automatic_stop_time_minutes: The number of minutes until the running instance is shut down after the environment was last used.
        :param connection_type: The connection type used for connecting to an Amazon EC2 environment. Valid values are ``CONNECT_SSH`` (default) and ``CONNECT_SSM`` (connected through AWS Systems Manager ).
        :param description: The description of the environment to create.
        :param image_id: The identifier for the Amazon Machine Image (AMI) that's used to create the EC2 instance. To choose an AMI for the instance, you must specify a valid AMI alias or a valid AWS Systems Manager path. The default AMI is used if the parameter isn't explicitly assigned a value in the request. *AMI aliases* - *Amazon Linux (default): ``amazonlinux-1-x86_64``* - Amazon Linux 2: ``amazonlinux-2-x86_64`` - Ubuntu 18.04: ``ubuntu-18.04-x86_64`` *SSM paths* - *Amazon Linux (default): ``resolve:ssm:/aws/service/cloud9/amis/amazonlinux-1-x86_64``* - Amazon Linux 2: ``resolve:ssm:/aws/service/cloud9/amis/amazonlinux-2-x86_64`` - Ubuntu 18.04: ``resolve:ssm:/aws/service/cloud9/amis/ubuntu-18.04-x86_64``
        :param name: The name of the environment.
        :param owner_arn: The Amazon Resource Name (ARN) of the environment owner. This ARN can be the ARN of any AWS Identity and Access Management principal. If this value is not specified, the ARN defaults to this environment's creator.
        :param repositories: Any AWS CodeCommit source code repositories to be cloned into the development environment.
        :param subnet_id: The ID of the subnet in Amazon Virtual Private Cloud (Amazon VPC) that AWS Cloud9 will use to communicate with the Amazon Elastic Compute Cloud (Amazon EC2) instance.
        :param tags: An array of key-value pairs that will be associated with the new AWS Cloud9 development environment.
        '''
        props = CfnEnvironmentEC2Props(
            instance_type=instance_type,
            automatic_stop_time_minutes=automatic_stop_time_minutes,
            connection_type=connection_type,
            description=description,
            image_id=image_id,
            name=name,
            owner_arn=owner_arn,
            repositories=repositories,
            subnet_id=subnet_id,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: _TreeInspector_1cd1894e) -> None:
        '''Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.
        '''
        return typing.cast(None, jsii.invoke(self, "inspect", [inspector]))

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        '''
        :param props: -
        '''
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "renderProperties", [props]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        '''The CloudFormation resource type name for this resource class.'''
        return typing.cast(builtins.str, jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the development environment, such as ``arn:aws:cloud9:us-east-2:123456789012:environment:2bc3642873c342e485f7e0c561234567`` .

        :cloudformationAttribute: Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attrName")
    def attr_name(self) -> builtins.str:
        '''The name of the environment.

        :cloudformationAttribute: Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "attrName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.get(self, "cfnProperties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> _TagManager_0b7ab120:
        '''An array of key-value pairs that will be associated with the new AWS Cloud9 development environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-tags
        '''
        return typing.cast(_TagManager_0b7ab120, jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> builtins.str:
        '''The type of instance to connect to the environment (for example, ``t2.micro`` ).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-instancetype
        '''
        return typing.cast(builtins.str, jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: builtins.str) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="automaticStopTimeMinutes")
    def automatic_stop_time_minutes(self) -> typing.Optional[jsii.Number]:
        '''The number of minutes until the running instance is shut down after the environment was last used.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-automaticstoptimeminutes
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "automaticStopTimeMinutes"))

    @automatic_stop_time_minutes.setter
    def automatic_stop_time_minutes(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "automaticStopTimeMinutes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionType")
    def connection_type(self) -> typing.Optional[builtins.str]:
        '''The connection type used for connecting to an Amazon EC2 environment.

        Valid values are ``CONNECT_SSH`` (default) and ``CONNECT_SSM`` (connected through AWS Systems Manager ).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-connectiontype
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionType"))

    @connection_type.setter
    def connection_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "connectionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the environment to create.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @description.setter
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageId")
    def image_id(self) -> typing.Optional[builtins.str]:
        '''The identifier for the Amazon Machine Image (AMI) that's used to create the EC2 instance.

        To choose an AMI for the instance, you must specify a valid AMI alias or a valid AWS Systems Manager path.

        The default AMI is used if the parameter isn't explicitly assigned a value in the request.

        *AMI aliases*

        - *Amazon Linux (default): ``amazonlinux-1-x86_64``*
        - Amazon Linux 2: ``amazonlinux-2-x86_64``
        - Ubuntu 18.04: ``ubuntu-18.04-x86_64``

        *SSM paths*

        - *Amazon Linux (default): ``resolve:ssm:/aws/service/cloud9/amis/amazonlinux-1-x86_64``*
        - Amazon Linux 2: ``resolve:ssm:/aws/service/cloud9/amis/amazonlinux-2-x86_64``
        - Ubuntu 18.04: ``resolve:ssm:/aws/service/cloud9/amis/ubuntu-18.04-x86_64``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-imageid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageId"))

    @image_id.setter
    def image_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "imageId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-name
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @name.setter
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ownerArn")
    def owner_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the environment owner.

        This ARN can be the ARN of any AWS Identity and Access Management principal. If this value is not specified, the ARN defaults to this environment's creator.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-ownerarn
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ownerArn"))

    @owner_arn.setter
    def owner_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "ownerArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositories")
    def repositories(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union["CfnEnvironmentEC2.RepositoryProperty", _IResolvable_a771d0ef]]]]:
        '''Any AWS CodeCommit source code repositories to be cloned into the development environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-repositories
        '''
        return typing.cast(typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union["CfnEnvironmentEC2.RepositoryProperty", _IResolvable_a771d0ef]]]], jsii.get(self, "repositories"))

    @repositories.setter
    def repositories(
        self,
        value: typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union["CfnEnvironmentEC2.RepositoryProperty", _IResolvable_a771d0ef]]]],
    ) -> None:
        jsii.set(self, "repositories", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the subnet in Amazon Virtual Private Cloud (Amazon VPC) that AWS Cloud9 will use to communicate with the Amazon Elastic Compute Cloud (Amazon EC2) instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-subnetid
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetId"))

    @subnet_id.setter
    def subnet_id(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "subnetId", value)

    @jsii.data_type(
        jsii_type="monocdk.aws_cloud9.CfnEnvironmentEC2.RepositoryProperty",
        jsii_struct_bases=[],
        name_mapping={
            "path_component": "pathComponent",
            "repository_url": "repositoryUrl",
        },
    )
    class RepositoryProperty:
        def __init__(
            self,
            *,
            path_component: builtins.str,
            repository_url: builtins.str,
        ) -> None:
            '''The ``Repository`` property type specifies an AWS CodeCommit source code repository to be cloned into an AWS Cloud9 development environment.

            :param path_component: The path within the development environment's default file system location to clone the AWS CodeCommit repository into. For example, ``/REPOSITORY_NAME`` would clone the repository into the ``/home/USER_NAME/environment/REPOSITORY_NAME`` directory in the environment.
            :param repository_url: The clone URL of the AWS CodeCommit repository to be cloned. For example, for an AWS CodeCommit repository this might be ``https://git-codecommit.us-east-2.amazonaws.com/v1/repos/REPOSITORY_NAME`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloud9-environmentec2-repository.html
            :exampleMetadata: fixture=_generated

            Example::

                # The code below shows an example of how to instantiate this type.
                # The values are placeholders you should change.
                from monocdk import aws_cloud9 as cloud9
                
                repository_property = cloud9.CfnEnvironmentEC2.RepositoryProperty(
                    path_component="pathComponent",
                    repository_url="repositoryUrl"
                )
            '''
            self._values: typing.Dict[str, typing.Any] = {
                "path_component": path_component,
                "repository_url": repository_url,
            }

        @builtins.property
        def path_component(self) -> builtins.str:
            '''The path within the development environment's default file system location to clone the AWS CodeCommit repository into.

            For example, ``/REPOSITORY_NAME`` would clone the repository into the ``/home/USER_NAME/environment/REPOSITORY_NAME`` directory in the environment.

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloud9-environmentec2-repository.html#cfn-cloud9-environmentec2-repository-pathcomponent
            '''
            result = self._values.get("path_component")
            assert result is not None, "Required property 'path_component' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def repository_url(self) -> builtins.str:
            '''The clone URL of the AWS CodeCommit repository to be cloned.

            For example, for an AWS CodeCommit repository this might be ``https://git-codecommit.us-east-2.amazonaws.com/v1/repos/REPOSITORY_NAME`` .

            :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloud9-environmentec2-repository.html#cfn-cloud9-environmentec2-repository-repositoryurl
            '''
            result = self._values.get("repository_url")
            assert result is not None, "Required property 'repository_url' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RepositoryProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="monocdk.aws_cloud9.CfnEnvironmentEC2Props",
    jsii_struct_bases=[],
    name_mapping={
        "instance_type": "instanceType",
        "automatic_stop_time_minutes": "automaticStopTimeMinutes",
        "connection_type": "connectionType",
        "description": "description",
        "image_id": "imageId",
        "name": "name",
        "owner_arn": "ownerArn",
        "repositories": "repositories",
        "subnet_id": "subnetId",
        "tags": "tags",
    },
)
class CfnEnvironmentEC2Props:
    def __init__(
        self,
        *,
        instance_type: builtins.str,
        automatic_stop_time_minutes: typing.Optional[jsii.Number] = None,
        connection_type: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        image_id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        owner_arn: typing.Optional[builtins.str] = None,
        repositories: typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.Sequence[typing.Union[CfnEnvironmentEC2.RepositoryProperty, _IResolvable_a771d0ef]]]] = None,
        subnet_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[_CfnTag_95fbdc29]] = None,
    ) -> None:
        '''Properties for defining a ``CfnEnvironmentEC2``.

        :param instance_type: The type of instance to connect to the environment (for example, ``t2.micro`` ).
        :param automatic_stop_time_minutes: The number of minutes until the running instance is shut down after the environment was last used.
        :param connection_type: The connection type used for connecting to an Amazon EC2 environment. Valid values are ``CONNECT_SSH`` (default) and ``CONNECT_SSM`` (connected through AWS Systems Manager ).
        :param description: The description of the environment to create.
        :param image_id: The identifier for the Amazon Machine Image (AMI) that's used to create the EC2 instance. To choose an AMI for the instance, you must specify a valid AMI alias or a valid AWS Systems Manager path. The default AMI is used if the parameter isn't explicitly assigned a value in the request. *AMI aliases* - *Amazon Linux (default): ``amazonlinux-1-x86_64``* - Amazon Linux 2: ``amazonlinux-2-x86_64`` - Ubuntu 18.04: ``ubuntu-18.04-x86_64`` *SSM paths* - *Amazon Linux (default): ``resolve:ssm:/aws/service/cloud9/amis/amazonlinux-1-x86_64``* - Amazon Linux 2: ``resolve:ssm:/aws/service/cloud9/amis/amazonlinux-2-x86_64`` - Ubuntu 18.04: ``resolve:ssm:/aws/service/cloud9/amis/ubuntu-18.04-x86_64``
        :param name: The name of the environment.
        :param owner_arn: The Amazon Resource Name (ARN) of the environment owner. This ARN can be the ARN of any AWS Identity and Access Management principal. If this value is not specified, the ARN defaults to this environment's creator.
        :param repositories: Any AWS CodeCommit source code repositories to be cloned into the development environment.
        :param subnet_id: The ID of the subnet in Amazon Virtual Private Cloud (Amazon VPC) that AWS Cloud9 will use to communicate with the Amazon Elastic Compute Cloud (Amazon EC2) instance.
        :param tags: An array of key-value pairs that will be associated with the new AWS Cloud9 development environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cloud9 as cloud9
            
            cfn_environment_eC2_props = cloud9.CfnEnvironmentEC2Props(
                instance_type="instanceType",
            
                # the properties below are optional
                automatic_stop_time_minutes=123,
                connection_type="connectionType",
                description="description",
                image_id="imageId",
                name="name",
                owner_arn="ownerArn",
                repositories=[cloud9.CfnEnvironmentEC2.RepositoryProperty(
                    path_component="pathComponent",
                    repository_url="repositoryUrl"
                )],
                subnet_id="subnetId",
                tags=[CfnTag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "instance_type": instance_type,
        }
        if automatic_stop_time_minutes is not None:
            self._values["automatic_stop_time_minutes"] = automatic_stop_time_minutes
        if connection_type is not None:
            self._values["connection_type"] = connection_type
        if description is not None:
            self._values["description"] = description
        if image_id is not None:
            self._values["image_id"] = image_id
        if name is not None:
            self._values["name"] = name
        if owner_arn is not None:
            self._values["owner_arn"] = owner_arn
        if repositories is not None:
            self._values["repositories"] = repositories
        if subnet_id is not None:
            self._values["subnet_id"] = subnet_id
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def instance_type(self) -> builtins.str:
        '''The type of instance to connect to the environment (for example, ``t2.micro`` ).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-instancetype
        '''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def automatic_stop_time_minutes(self) -> typing.Optional[jsii.Number]:
        '''The number of minutes until the running instance is shut down after the environment was last used.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-automaticstoptimeminutes
        '''
        result = self._values.get("automatic_stop_time_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connection_type(self) -> typing.Optional[builtins.str]:
        '''The connection type used for connecting to an Amazon EC2 environment.

        Valid values are ``CONNECT_SSH`` (default) and ``CONNECT_SSM`` (connected through AWS Systems Manager ).

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-connectiontype
        '''
        result = self._values.get("connection_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''The description of the environment to create.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_id(self) -> typing.Optional[builtins.str]:
        '''The identifier for the Amazon Machine Image (AMI) that's used to create the EC2 instance.

        To choose an AMI for the instance, you must specify a valid AMI alias or a valid AWS Systems Manager path.

        The default AMI is used if the parameter isn't explicitly assigned a value in the request.

        *AMI aliases*

        - *Amazon Linux (default): ``amazonlinux-1-x86_64``*
        - Amazon Linux 2: ``amazonlinux-2-x86_64``
        - Ubuntu 18.04: ``ubuntu-18.04-x86_64``

        *SSM paths*

        - *Amazon Linux (default): ``resolve:ssm:/aws/service/cloud9/amis/amazonlinux-1-x86_64``*
        - Amazon Linux 2: ``resolve:ssm:/aws/service/cloud9/amis/amazonlinux-2-x86_64``
        - Ubuntu 18.04: ``resolve:ssm:/aws/service/cloud9/amis/ubuntu-18.04-x86_64``

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-imageid
        '''
        result = self._values.get("image_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-name
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner_arn(self) -> typing.Optional[builtins.str]:
        '''The Amazon Resource Name (ARN) of the environment owner.

        This ARN can be the ARN of any AWS Identity and Access Management principal. If this value is not specified, the ARN defaults to this environment's creator.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-ownerarn
        '''
        result = self._values.get("owner_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repositories(
        self,
    ) -> typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union[CfnEnvironmentEC2.RepositoryProperty, _IResolvable_a771d0ef]]]]:
        '''Any AWS CodeCommit source code repositories to be cloned into the development environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-repositories
        '''
        result = self._values.get("repositories")
        return typing.cast(typing.Optional[typing.Union[_IResolvable_a771d0ef, typing.List[typing.Union[CfnEnvironmentEC2.RepositoryProperty, _IResolvable_a771d0ef]]]], result)

    @builtins.property
    def subnet_id(self) -> typing.Optional[builtins.str]:
        '''The ID of the subnet in Amazon Virtual Private Cloud (Amazon VPC) that AWS Cloud9 will use to communicate with the Amazon Elastic Compute Cloud (Amazon EC2) instance.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-subnetid
        '''
        result = self._values.get("subnet_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[_CfnTag_95fbdc29]]:
        '''An array of key-value pairs that will be associated with the new AWS Cloud9 development environment.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-tags
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[_CfnTag_95fbdc29]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnEnvironmentEC2Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloneRepository(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloud9.CloneRepository",
):
    '''(experimental) The class for different repository providers.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as codecommit
        
        # create a new Cloud9 environment and clone the two repositories
        # vpc: ec2.Vpc
        
        
        # create a codecommit repository to clone into the cloud9 environment
        repo_new = codecommit.Repository(self, "RepoNew",
            repository_name="new-repo"
        )
        
        # import an existing codecommit repository to clone into the cloud9 environment
        repo_existing = codecommit.Repository.from_repository_name(self, "RepoExisting", "existing-repo")
        cloud9.Ec2Environment(self, "C9Env",
            vpc=vpc,
            cloned_repositories=[
                cloud9.CloneRepository.from_code_commit(repo_new, "/src/new-repo"),
                cloud9.CloneRepository.from_code_commit(repo_existing, "/src/existing-repo")
            ]
        )
    '''

    @jsii.member(jsii_name="fromCodeCommit") # type: ignore[misc]
    @builtins.classmethod
    def from_code_commit(
        cls,
        repository: _IRepository_cdb2a3c0,
        path: builtins.str,
    ) -> "CloneRepository":
        '''(experimental) import repository to cloud9 environment from AWS CodeCommit.

        :param repository: the codecommit repository to clone from.
        :param path: the target path in cloud9 environment.

        :stability: experimental
        '''
        return typing.cast("CloneRepository", jsii.sinvoke(cls, "fromCodeCommit", [repository, path]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathComponent")
    def path_component(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "pathComponent"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repositoryUrl")
    def repository_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryUrl"))


@jsii.data_type(
    jsii_type="monocdk.aws_cloud9.Ec2EnvironmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "cloned_repositories": "clonedRepositories",
        "description": "description",
        "ec2_environment_name": "ec2EnvironmentName",
        "instance_type": "instanceType",
        "subnet_selection": "subnetSelection",
    },
)
class Ec2EnvironmentProps:
    def __init__(
        self,
        *,
        vpc: _IVpc_6d1f76c4,
        cloned_repositories: typing.Optional[typing.Sequence[CloneRepository]] = None,
        description: typing.Optional[builtins.str] = None,
        ec2_environment_name: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[_InstanceType_072ad323] = None,
        subnet_selection: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> None:
        '''(experimental) Properties for Ec2Environment.

        :param vpc: (experimental) The VPC that AWS Cloud9 will use to communicate with the Amazon Elastic Compute Cloud (Amazon EC2) instance.
        :param cloned_repositories: (experimental) The AWS CodeCommit repository to be cloned. Default: - do not clone any repository
        :param description: (experimental) Description of the environment. Default: - no description
        :param ec2_environment_name: (experimental) Name of the environment. Default: - automatically generated name
        :param instance_type: (experimental) The type of instance to connect to the environment. Default: - t2.micro
        :param subnet_selection: (experimental) The subnetSelection of the VPC that AWS Cloud9 will use to communicate with the Amazon EC2 instance. Default: - all public subnets of the VPC are selected.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # create a cloud9 ec2 environment in a new VPC
            vpc = ec2.Vpc(self, "VPC", max_azs=3)
            cloud9.Ec2Environment(self, "Cloud9Env", vpc=vpc)
            
            # or create the cloud9 environment in the default VPC with specific instanceType
            default_vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)
            cloud9.Ec2Environment(self, "Cloud9Env2",
                vpc=default_vpc,
                instance_type=ec2.InstanceType("t3.large")
            )
            
            # or specify in a different subnetSelection
            c9env = cloud9.Ec2Environment(self, "Cloud9Env3",
                vpc=vpc,
                subnet_selection=cloud9.aws_ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE
                )
            )
            
            # print the Cloud9 IDE URL in the output
            CfnOutput(self, "URL", value=c9env.ide_url)
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _SubnetSelection_1284e62c(**subnet_selection)
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if cloned_repositories is not None:
            self._values["cloned_repositories"] = cloned_repositories
        if description is not None:
            self._values["description"] = description
        if ec2_environment_name is not None:
            self._values["ec2_environment_name"] = ec2_environment_name
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection

    @builtins.property
    def vpc(self) -> _IVpc_6d1f76c4:
        '''(experimental) The VPC that AWS Cloud9 will use to communicate with the Amazon Elastic Compute Cloud (Amazon EC2) instance.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_IVpc_6d1f76c4, result)

    @builtins.property
    def cloned_repositories(self) -> typing.Optional[typing.List[CloneRepository]]:
        '''(experimental) The AWS CodeCommit repository to be cloned.

        :default: - do not clone any repository

        :stability: experimental
        '''
        result = self._values.get("cloned_repositories")
        return typing.cast(typing.Optional[typing.List[CloneRepository]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of the environment.

        :default: - no description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_environment_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the environment.

        :default: - automatically generated name

        :stability: experimental
        '''
        result = self._values.get("ec2_environment_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[_InstanceType_072ad323]:
        '''(experimental) The type of instance to connect to the environment.

        :default: - t2.micro

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[_InstanceType_072ad323], result)

    @builtins.property
    def subnet_selection(self) -> typing.Optional[_SubnetSelection_1284e62c]:
        '''(experimental) The subnetSelection of the VPC that AWS Cloud9 will use to communicate with the Amazon EC2 instance.

        :default: - all public subnets of the VPC are selected.

        :stability: experimental
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_SubnetSelection_1284e62c], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ec2EnvironmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="monocdk.aws_cloud9.IEc2Environment")
class IEc2Environment(_IResource_8c1dbbbd, typing_extensions.Protocol):
    '''(experimental) A Cloud9 Environment.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2EnvironmentArn")
    def ec2_environment_arn(self) -> builtins.str:
        '''(experimental) The arn of the EnvironmentEc2.

        :stability: experimental
        :attribute: environmentE2Arn
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2EnvironmentName")
    def ec2_environment_name(self) -> builtins.str:
        '''(experimental) The name of the EnvironmentEc2.

        :stability: experimental
        :attribute: environmentEc2Name
        '''
        ...


class _IEc2EnvironmentProxy(
    jsii.proxy_for(_IResource_8c1dbbbd) # type: ignore[misc]
):
    '''(experimental) A Cloud9 Environment.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_cloud9.IEc2Environment"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2EnvironmentArn")
    def ec2_environment_arn(self) -> builtins.str:
        '''(experimental) The arn of the EnvironmentEc2.

        :stability: experimental
        :attribute: environmentE2Arn
        '''
        return typing.cast(builtins.str, jsii.get(self, "ec2EnvironmentArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2EnvironmentName")
    def ec2_environment_name(self) -> builtins.str:
        '''(experimental) The name of the EnvironmentEc2.

        :stability: experimental
        :attribute: environmentEc2Name
        '''
        return typing.cast(builtins.str, jsii.get(self, "ec2EnvironmentName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IEc2Environment).__jsii_proxy_class__ = lambda : _IEc2EnvironmentProxy


@jsii.implements(IEc2Environment)
class Ec2Environment(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloud9.Ec2Environment",
):
    '''(experimental) A Cloud9 Environment with Amazon EC2.

    :stability: experimental
    :exampleMetadata: infused
    :resource: AWS::Cloud9::EnvironmentEC2

    Example::

        # create a cloud9 ec2 environment in a new VPC
        vpc = ec2.Vpc(self, "VPC", max_azs=3)
        cloud9.Ec2Environment(self, "Cloud9Env", vpc=vpc)
        
        # or create the cloud9 environment in the default VPC with specific instanceType
        default_vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)
        cloud9.Ec2Environment(self, "Cloud9Env2",
            vpc=default_vpc,
            instance_type=ec2.InstanceType("t3.large")
        )
        
        # or specify in a different subnetSelection
        c9env = cloud9.Ec2Environment(self, "Cloud9Env3",
            vpc=vpc,
            subnet_selection=cloud9.aws_ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE
            )
        )
        
        # print the Cloud9 IDE URL in the output
        CfnOutput(self, "URL", value=c9env.ide_url)
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        vpc: _IVpc_6d1f76c4,
        cloned_repositories: typing.Optional[typing.Sequence[CloneRepository]] = None,
        description: typing.Optional[builtins.str] = None,
        ec2_environment_name: typing.Optional[builtins.str] = None,
        instance_type: typing.Optional[_InstanceType_072ad323] = None,
        subnet_selection: typing.Optional[_SubnetSelection_1284e62c] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: (experimental) The VPC that AWS Cloud9 will use to communicate with the Amazon Elastic Compute Cloud (Amazon EC2) instance.
        :param cloned_repositories: (experimental) The AWS CodeCommit repository to be cloned. Default: - do not clone any repository
        :param description: (experimental) Description of the environment. Default: - no description
        :param ec2_environment_name: (experimental) Name of the environment. Default: - automatically generated name
        :param instance_type: (experimental) The type of instance to connect to the environment. Default: - t2.micro
        :param subnet_selection: (experimental) The subnetSelection of the VPC that AWS Cloud9 will use to communicate with the Amazon EC2 instance. Default: - all public subnets of the VPC are selected.

        :stability: experimental
        '''
        props = Ec2EnvironmentProps(
            vpc=vpc,
            cloned_repositories=cloned_repositories,
            description=description,
            ec2_environment_name=ec2_environment_name,
            instance_type=instance_type,
            subnet_selection=subnet_selection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromEc2EnvironmentName") # type: ignore[misc]
    @builtins.classmethod
    def from_ec2_environment_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        ec2_environment_name: builtins.str,
    ) -> IEc2Environment:
        '''(experimental) import from EnvironmentEc2Name.

        :param scope: -
        :param id: -
        :param ec2_environment_name: -

        :stability: experimental
        '''
        return typing.cast(IEc2Environment, jsii.sinvoke(cls, "fromEc2EnvironmentName", [scope, id, ec2_environment_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2EnvironmentArn")
    def ec2_environment_arn(self) -> builtins.str:
        '''(experimental) The environment ARN of this Cloud9 environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "ec2EnvironmentArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ec2EnvironmentName")
    def ec2_environment_name(self) -> builtins.str:
        '''(experimental) The environment name of this Cloud9 environment.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "ec2EnvironmentName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentId")
    def environment_id(self) -> builtins.str:
        '''(experimental) The environment ID of this Cloud9 environment.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "environmentId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ideUrl")
    def ide_url(self) -> builtins.str:
        '''(experimental) The complete IDE URL of this Cloud9 environment.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "ideUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> _IVpc_6d1f76c4:
        '''(experimental) VPC ID.

        :stability: experimental
        '''
        return typing.cast(_IVpc_6d1f76c4, jsii.get(self, "vpc"))


__all__ = [
    "CfnEnvironmentEC2",
    "CfnEnvironmentEC2Props",
    "CloneRepository",
    "Ec2Environment",
    "Ec2EnvironmentProps",
    "IEc2Environment",
]

publication.publish()
