'''
# cdk-ecr-deployment

[![Release](https://github.com/wchaws/cdk-ecr-deployment/actions/workflows/release.yml/badge.svg)](https://github.com/wchaws/cdk-ecr-deployment/actions/workflows/release.yml)
[![npm version](https://img.shields.io/npm/v/cdk-ecr-deployment)](https://www.npmjs.com/package/cdk-ecr-deployment)
[![PyPI](https://img.shields.io/pypi/v/cdk-ecr-deployment)](https://pypi.org/project/cdk-ecr-deployment)
[![npm](https://img.shields.io/npm/dw/cdk-ecr-deployment?label=npm%20downloads)](https://www.npmjs.com/package/cdk-ecr-deployment)
[![PyPI - Downloads](https://img.shields.io/pypi/dw/cdk-ecr-deployment?label=pypi%20downloads)](https://pypi.org/project/cdk-ecr-deployment)

CDK construct to deploy docker image to Amazon ECR

⚠️ Please use ^1.0.0 for cdk version 1.x.x, use ^2.0.0 for cdk version 2.x.x

## Features

* Copy an ECR image to another
* Copy docker hub image to ECR
* Copy an archive tarball image from s3 to ECR

## Examples

Run [test/integ.ecr-deployment.ts](./test/integ.ecr-deployment.ts)

```shell
NO_PREBUILT_LAMBDA=1 npx cdk deploy -a "npx ts-node -P tsconfig.dev.json --prefer-ts-exts test/integ.ecr-deployment.ts"
```

## Tech Details & Contribution

The core of this project relies on https://github.com/containers/image which is used by https://github.com/containers/skopeo.
Please take a look at those projects before contribution.

To support a new docker image source(like docker tarball in s3), you need to implement [image transport interface](https://github.com/containers/image/blob/master/types/types.go). You could take a look at [docker-archive](https://github.com/containers/image/blob/ccb87a8d0f45cf28846e307eb0ec2b9d38a458c2/docker/archive/transport.go) transport for a good start.

To test the `lambda` folder, `make test`.
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

import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import constructs


class ECRDeployment(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-ecr-deployment.ECRDeployment",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        dest: "IImageName",
        src: "IImageName",
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param dest: The destination of the docker image.
        :param src: The source of the docker image.
        :param environment: The environment variable to set.
        :param memory_limit: The amount of memory (in MiB) to allocate to the AWS Lambda function which replicates the files from the CDK bucket to the destination bucket. If you are deploying large files, you will need to increase this number accordingly. Default: 512
        :param role: Execution role associated with this function. Default: - A role is automatically created
        :param vpc: The VPC network to place the deployment lambda handler in. Default: None
        :param vpc_subnets: Where in the VPC to place the deployment lambda handler. Only used if 'vpc' is supplied. Default: - the Vpc default strategy if not specified
        '''
        props = ECRDeploymentProps(
            dest=dest,
            src=src,
            environment=environment,
            memory_limit=memory_limit,
            role=role,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-ecr-deployment.ECRDeploymentProps",
    jsii_struct_bases=[],
    name_mapping={
        "dest": "dest",
        "src": "src",
        "environment": "environment",
        "memory_limit": "memoryLimit",
        "role": "role",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class ECRDeploymentProps:
    def __init__(
        self,
        *,
        dest: "IImageName",
        src: "IImageName",
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        memory_limit: typing.Optional[jsii.Number] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param dest: The destination of the docker image.
        :param src: The source of the docker image.
        :param environment: The environment variable to set.
        :param memory_limit: The amount of memory (in MiB) to allocate to the AWS Lambda function which replicates the files from the CDK bucket to the destination bucket. If you are deploying large files, you will need to increase this number accordingly. Default: 512
        :param role: Execution role associated with this function. Default: - A role is automatically created
        :param vpc: The VPC network to place the deployment lambda handler in. Default: None
        :param vpc_subnets: Where in the VPC to place the deployment lambda handler. Only used if 'vpc' is supplied. Default: - the Vpc default strategy if not specified
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "dest": dest,
            "src": src,
        }
        if environment is not None:
            self._values["environment"] = environment
        if memory_limit is not None:
            self._values["memory_limit"] = memory_limit
        if role is not None:
            self._values["role"] = role
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def dest(self) -> "IImageName":
        '''The destination of the docker image.'''
        result = self._values.get("dest")
        assert result is not None, "Required property 'dest' is missing"
        return typing.cast("IImageName", result)

    @builtins.property
    def src(self) -> "IImageName":
        '''The source of the docker image.'''
        result = self._values.get("src")
        assert result is not None, "Required property 'src' is missing"
        return typing.cast("IImageName", result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The environment variable to set.'''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def memory_limit(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory (in MiB) to allocate to the AWS Lambda function which replicates the files from the CDK bucket to the destination bucket.

        If you are deploying large files, you will need to increase this number
        accordingly.

        :default: 512
        '''
        result = self._values.get("memory_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Execution role associated with this function.

        :default: - A role is automatically created
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''The VPC network to place the deployment lambda handler in.

        :default: None
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''Where in the VPC to place the deployment lambda handler.

        Only used if 'vpc' is supplied.

        :default: - the Vpc default strategy if not specified
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ECRDeploymentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cdk-ecr-deployment.IImageName")
class IImageName(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        '''The uri of the docker image.

        The uri spec follows https://github.com/containers/skopeo
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creds")
    def creds(self) -> typing.Optional[builtins.str]:
        '''The credentials of the docker image.

        Format ``user:[password]``
        '''
        ...

    @creds.setter
    def creds(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IImageNameProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-ecr-deployment.IImageName"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        '''The uri of the docker image.

        The uri spec follows https://github.com/containers/skopeo
        '''
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creds")
    def creds(self) -> typing.Optional[builtins.str]:
        '''The credentials of the docker image.

        Format ``user:[password]``
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creds"))

    @creds.setter
    def creds(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "creds", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IImageName).__jsii_proxy_class__ = lambda : _IImageNameProxy


@jsii.implements(IImageName)
class S3ArchiveName(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-ecr-deployment.S3ArchiveName",
):
    def __init__(
        self,
        p: builtins.str,
        ref: typing.Optional[builtins.str] = None,
        creds: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param p: -
        :param ref: -
        :param creds: -
        '''
        jsii.create(self.__class__, self, [p, ref, creds])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        '''The uri of the docker image.

        The uri spec follows https://github.com/containers/skopeo
        '''
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creds")
    def creds(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creds"))

    @creds.setter
    def creds(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "creds", value)


@jsii.implements(IImageName)
class DockerImageName(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-ecr-deployment.DockerImageName",
):
    def __init__(
        self,
        name: builtins.str,
        creds: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: -
        :param creds: -
        '''
        jsii.create(self.__class__, self, [name, creds])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uri")
    def uri(self) -> builtins.str:
        '''The uri of the docker image.

        The uri spec follows https://github.com/containers/skopeo
        '''
        return typing.cast(builtins.str, jsii.get(self, "uri"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="creds")
    def creds(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "creds"))

    @creds.setter
    def creds(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "creds", value)


__all__ = [
    "DockerImageName",
    "ECRDeployment",
    "ECRDeploymentProps",
    "IImageName",
    "S3ArchiveName",
]

publication.publish()
