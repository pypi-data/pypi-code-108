'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-s3-antivirus

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-s3-antivirus)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-s3-antivirus/)

> Antivirus for Amazon S3

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-s3-antivirus
```

Python:

```bash
pip install cloudcomponents.cdk-s3-antivirus
```

## How to use

```python
import { SnsDestination } from '@aws-cdk/aws-lambda-destinations';
import { Bucket } from '@aws-cdk/aws-s3';
import { Topic } from '@aws-cdk/aws-sns';
import { EmailSubscription } from '@aws-cdk/aws-sns-subscriptions';
import { Construct, RemovalPolicy, Stack, StackProps } from '@aws-cdk/core';

import { Scanner } from '@cloudcomponents/cdk-s3-antivirus';

export class S3AntivirusStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const bucket = new Bucket(this, 'Bucket', {
      autoDeleteObjects: true,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const topic = new Topic(this, 'Topic');
    topic.addSubscription(new EmailSubscription(process.env.DEVSECOPS_TEAM_EMAIL as string));

    const scanner = new Scanner(this, 'Scanner', {
      onResult: new SnsDestination(topic),
      onError: new SnsDestination(topic),
    });

    scanner.addSourceBucket(bucket);
  }
}
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-s3-antivirus/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-s3-antivirus/LICENSE)
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
import aws_cdk.aws_efs
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.core


class ClamavLayer(
    aws_cdk.aws_lambda.LayerVersion,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-s3-antivirus.ClamavLayer",
):
    '''Clamav Lambda layer.'''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(self.__class__, self, [scope, id])


class DefinitionBucket(
    aws_cdk.aws_s3.Bucket,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-s3-antivirus.DefinitionBucket",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        vpc_endpoint: builtins.str,
        bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc_endpoint: -
        :param bucket_name: -
        '''
        props = DefinitionBucketProps(
            vpc_endpoint=vpc_endpoint, bucket_name=bucket_name
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-s3-antivirus.DefinitionBucketProps",
    jsii_struct_bases=[],
    name_mapping={"vpc_endpoint": "vpcEndpoint", "bucket_name": "bucketName"},
)
class DefinitionBucketProps:
    def __init__(
        self,
        *,
        vpc_endpoint: builtins.str,
        bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param vpc_endpoint: -
        :param bucket_name: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "vpc_endpoint": vpc_endpoint,
        }
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name

    @builtins.property
    def vpc_endpoint(self) -> builtins.str:
        result = self._values.get("vpc_endpoint")
        assert result is not None, "Required property 'vpc_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DefinitionBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DefinitionInitializer(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-s3-antivirus.DefinitionInitializer",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        fn: aws_cdk.aws_lambda.IFunction,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param fn: -
        '''
        props = DefinitionInitializerProps(fn=fn)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-s3-antivirus.DefinitionInitializerProps",
    jsii_struct_bases=[],
    name_mapping={"fn": "fn"},
)
class DefinitionInitializerProps:
    def __init__(self, *, fn: aws_cdk.aws_lambda.IFunction) -> None:
        '''
        :param fn: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "fn": fn,
        }

    @builtins.property
    def fn(self) -> aws_cdk.aws_lambda.IFunction:
        result = self._values.get("fn")
        assert result is not None, "Required property 'fn' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DefinitionInitializerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Sandbox(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-s3-antivirus.Sandbox",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        encrypted_file_system: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param encrypted_file_system: -
        '''
        props = SandboxProps(encrypted_file_system=encrypted_file_system)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addToS3EnpointPolicy")
    def add_to_s3_enpoint_policy(
        self,
        statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> None:
        '''
        :param statement: -
        '''
        return typing.cast(None, jsii.invoke(self, "addToS3EnpointPolicy", [statement]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definitionBucket")
    def definition_bucket(self) -> DefinitionBucket:
        return typing.cast(DefinitionBucket, jsii.get(self, "definitionBucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaAccessPoint")
    def lambda_access_point(self) -> aws_cdk.aws_efs.IAccessPoint:
        return typing.cast(aws_cdk.aws_efs.IAccessPoint, jsii.get(self, "lambdaAccessPoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Endpoint")
    def s3_endpoint(self) -> aws_cdk.aws_ec2.GatewayVpcEndpoint:
        return typing.cast(aws_cdk.aws_ec2.GatewayVpcEndpoint, jsii.get(self, "s3Endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-s3-antivirus.SandboxProps",
    jsii_struct_bases=[],
    name_mapping={"encrypted_file_system": "encryptedFileSystem"},
)
class SandboxProps:
    def __init__(
        self,
        *,
        encrypted_file_system: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param encrypted_file_system: -
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if encrypted_file_system is not None:
            self._values["encrypted_file_system"] = encrypted_file_system

    @builtins.property
    def encrypted_file_system(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("encrypted_file_system")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SandboxProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Scanner(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-s3-antivirus.Scanner",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.Bucket]] = None,
        on_error: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_result: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        scan_status_tag_name: typing.Optional[builtins.str] = None,
        update_schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param buckets: -
        :param on_error: -
        :param on_result: -
        :param scan_status_tag_name: Default: cc:scan-status
        :param update_schedule: -
        '''
        props = ScannerProps(
            buckets=buckets,
            on_error=on_error,
            on_result=on_result,
            scan_status_tag_name=scan_status_tag_name,
            update_schedule=update_schedule,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addSourceBucket")
    def add_source_bucket(self, bucket: aws_cdk.aws_s3.Bucket) -> None:
        '''
        :param bucket: -
        '''
        return typing.cast(None, jsii.invoke(self, "addSourceBucket", [bucket]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sandbox")
    def sandbox(self) -> Sandbox:
        return typing.cast(Sandbox, jsii.get(self, "sandbox"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scanFunction")
    def scan_function(self) -> aws_cdk.aws_lambda.IFunction:
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "scanFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scanStatusTagName")
    def scan_status_tag_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scanStatusTagName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateFunction")
    def update_function(self) -> aws_cdk.aws_lambda.IFunction:
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "updateFunction"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-s3-antivirus.ScannerProps",
    jsii_struct_bases=[],
    name_mapping={
        "buckets": "buckets",
        "on_error": "onError",
        "on_result": "onResult",
        "scan_status_tag_name": "scanStatusTagName",
        "update_schedule": "updateSchedule",
    },
)
class ScannerProps:
    def __init__(
        self,
        *,
        buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.Bucket]] = None,
        on_error: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_result: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        scan_status_tag_name: typing.Optional[builtins.str] = None,
        update_schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
    ) -> None:
        '''
        :param buckets: -
        :param on_error: -
        :param on_result: -
        :param scan_status_tag_name: Default: cc:scan-status
        :param update_schedule: -
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if buckets is not None:
            self._values["buckets"] = buckets
        if on_error is not None:
            self._values["on_error"] = on_error
        if on_result is not None:
            self._values["on_result"] = on_result
        if scan_status_tag_name is not None:
            self._values["scan_status_tag_name"] = scan_status_tag_name
        if update_schedule is not None:
            self._values["update_schedule"] = update_schedule

    @builtins.property
    def buckets(self) -> typing.Optional[typing.List[aws_cdk.aws_s3.Bucket]]:
        result = self._values.get("buckets")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.Bucket]], result)

    @builtins.property
    def on_error(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        result = self._values.get("on_error")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    @builtins.property
    def on_result(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        result = self._values.get("on_result")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    @builtins.property
    def scan_status_tag_name(self) -> typing.Optional[builtins.str]:
        '''
        :default: cc:scan-status
        '''
        result = self._values.get("scan_status_tag_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update_schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        result = self._values.get("update_schedule")
        return typing.cast(typing.Optional[aws_cdk.aws_events.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScannerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ClamavLayer",
    "DefinitionBucket",
    "DefinitionBucketProps",
    "DefinitionInitializer",
    "DefinitionInitializerProps",
    "Sandbox",
    "SandboxProps",
    "Scanner",
    "ScannerProps",
]

publication.publish()
