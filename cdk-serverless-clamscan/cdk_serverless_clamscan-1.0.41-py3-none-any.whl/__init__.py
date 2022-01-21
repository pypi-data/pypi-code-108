'''
# cdk-serverless-clamscan

| Language   | cdk-serverless-clamscan                                                                                   | monocdk-serverless-clamscan                                                                                       |
| ---------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Python     | [![PyPI version](https://badge.fury.io/py/cdk-serverless-clamscan.svg)](https://badge.fury.io/py/cdk-serverless-clamscan) | [![PyPI version](https://badge.fury.io/py/monocdk-serverless-clamscan.svg)](https://badge.fury.io/py/monocdk-serverless-clamscan) |
| TypeScript | [![npm version](https://badge.fury.io/js/cdk-serverless-clamscan.svg)](https://badge.fury.io/js/cdk-serverless-clamscan)  | [![npm version](https://badge.fury.io/js/monocdk-serverless-clamscan.svg)](https://badge.fury.io/js/monocdk-serverless-clamscan)  |

* If your project uses cdk version **1.x.x** use `cdk-serverless-clamscan` **^1.0.0**
* If your project uses cdk version **2.x.x** use `cdk-serverless-clamscan` **^2.0.0**
* If your project uses monocdk use `monocdk-serverless-clamscan` **^1.0.0**

An [aws-cdk](https://github.com/aws/aws-cdk) construct that uses [ClamAV®](https://www.clamav.net/) to scan objects in Amazon S3 for viruses. The construct provides a flexible interface for a system to act based on the results of a ClamAV virus scan.

![Overview](serverless-clamscan.png)

## Pre-Requisites

**Docker:** The ClamAV Lambda functions utilizes a [container image](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/) that is built locally using [docker bundling](https://aws.amazon.com/blogs/devops/building-apps-with-aws-cdk/)

## Examples

This project uses [projen](https://github.com/projen/projen) and thus all the constructs follow language specific standards and naming patterns. For more information on how to translate the following examples into your desired language read the CDK guide on [Translating TypeScript AWS CDK code to other languages](https://docs.aws.amazon.com/cdk/latest/guide/multiple_languages.html)

### Example 1. (Default destinations with rule target)

<details><summary>typescript</summary>
<p>

```python
import { RuleTargetInput } from '@aws-cdk/aws-events';
import { SnsTopic } from '@aws-cdk/aws-events-targets';
import { Bucket } from '@aws-cdk/aws-s3';
import { Topic } from '@aws-cdk/aws-sns';
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { ServerlessClamscan } from 'cdk-serverless-clamscan';

export class CdkTestStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const bucket_1 = new Bucket(this, 'rBucket1');
    const bucket_2 = new Bucket(this, 'rBucket2');
    const bucketList = [bucket_1, bucket_2];
    const sc = new ServerlessClamscan(this, 'rClamscan', {
      buckets: bucketList,
    });
    const bucket_3 = new Bucket(this, 'rBucket3');
    sc.addSourceBucket(bucket_3);
    const infectedTopic = new Topic(this, 'rInfectedTopic');
    sc.infectedRule?.addTarget(
      new SnsTopic(infectedTopic, {
        message: RuleTargetInput.fromEventPath(
          '$.detail.responsePayload.message',
        ),
      }),
    );
  }
}
```

</p>
</details><details><summary>python</summary>
<p>

```python
from aws_cdk import (
  core as core,
  aws_events as events,
  aws_events_targets as events_targets,
  aws_s3 as s3,
  aws_sns as sns
)
from cdk_serverless_clamscan import ServerlessClamscan

class CdkTestStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    bucket_1 = s3.Bucket(self, "rBucket1")
    bucket_2 = s3.Bucket(self, "rBucket2")
    bucketList = [ bucket_1, bucket_2 ]
    sc = ServerlessClamscan(self, "rClamScan",
      buckets=bucketList,
    )
    bucket_3 = s3.Bucket(self, "rBucket3")
    sc.add_source_bucket(bucket_3)
    infected_topic = sns.Topic(self, "rInfectedTopic")
    if sc.infected_rule != None:
      sc.infected_rule.add_target(
        events_targets.SnsTopic(
          infected_topic,
          message=events.RuleTargetInput.from_event_path('$.detail.responsePayload.message'),
        )
      )
```

</p>
</details>

### Example 2. (Bring your own destinations)

<details><summary>typescript</summary>
<p>

```python
import {
  SqsDestination,
  EventBridgeDestination,
} from '@aws-cdk/aws-lambda-destinations';
import { Bucket } from '@aws-cdk/aws-s3';
import { Queue } from '@aws-cdk/aws-sqs';
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { ServerlessClamscan } from 'cdk-serverless-clamscan';

export class CdkTestStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const bucket_1 = new Bucket(this, 'rBucket1');
    const bucket_2 = new Bucket(this, 'rBucket2');
    const bucketList = [bucket_1, bucket_2];
    const queue = new Queue(this, 'rQueue');
    const sc = new ServerlessClamscan(this, 'default', {
      buckets: bucketList,
      onResult: new EventBridgeDestination(),
      onError: new SqsDestination(queue),
    });
    const bucket_3 = new Bucket(this, 'rBucket3');
    sc.addSourceBucket(bucket_3);
  }
}
```

</p>
</details><details><summary>python</summary>
<p>

```python
from aws_cdk import (
  core as core,
  aws_lambda_destinations as lambda_destinations,
  aws_s3 as s3,
  aws_sqs as sqs
)
from cdk_serverless_clamscan import ServerlessClamscan

class CdkTestStack(core.Stack):

  def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    bucket_1 = s3.Bucket(self, "rBucket1")
    bucket_2 = s3.Bucket(self, "rBucket2")
    bucketList = [ bucket_1, bucket_2 ]
    queue = sqs.Queue(self, "rQueue")
    sc = ServerlessClamscan(self, "rClamScan",
      buckets=bucketList,
      on_result=lambda_destinations.EventBridgeDestination(),
      on_error=lambda_destinations.SqsDestination(queue),
    )
    bucket_3 = s3.Bucket(self, "rBucket3")
    sc.add_source_bucket(bucket_3)
```

</p>
</details>

## Operation and Maintenance

When ClamAV publishes updates to the scanner you will see “Your ClamAV installation is OUTDATED” in your scan results. While the construct creates a system to keep the database definitions up to date, you must update the scanner to detect all the latest Viruses.

Update the docker images of the Lambda functions with the latest version of ClamAV by re-running `cdk deploy`.

## API Reference

See [API.md](./API.md).

## Contributing

See [CONTRIBUTING](./CONTRIBUTING.md) for more information.

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

import aws_cdk.aws_events
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.aws_sqs
import aws_cdk.core


class ServerlessClamscan(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-serverless-clamscan.ServerlessClamscan",
):
    '''An `aws-cdk <https://github.com/aws/aws-cdk>`_ construct that uses `ClamAV® <https://www.clamav.net/>`_. to scan objects in Amazon S3 for viruses. The construct provides a flexible interface for a system to act based on the results of a ClamAV virus scan.

    The construct creates a Lambda function with EFS integration to support larger files.
    A VPC with isolated subnets, a S3 Gateway endpoint will also be created.

    Additionally creates an twice-daily job to download the latest ClamAV definition files to the
    Virus Definitions S3 Bucket by utilizing an EventBridge rule and a Lambda function and
    publishes CloudWatch Metrics to the 'serverless-clamscan' namespace.

    **Important O&M**:
    When ClamAV publishes updates to the scanner you will see “Your ClamAV installation is OUTDATED” in your scan results.
    While the construct creates a system to keep the database definitions up to date, you must update the scanner to
    detect all the latest Viruses.

    Update the docker images of the Lambda functions with the latest version of ClamAV by re-running ``cdk deploy``.

    Successful Scan Event format Example::

       {
           "source": "serverless-clamscan",
           "input_bucket": <input_bucket_name>,
           "input_key": <object_key>,
           "status": <"CLEAN"|"INFECTED"|"N/A">,
           "message": <scan_summary>,
         }

    Note: The Virus Definitions bucket policy will likely cause a deletion error if you choose to delete
    the stack associated in the construct. However since the bucket itself gets deleted, you can delete
    the stack again to resolve the error.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.Bucket]] = None,
        defs_bucket_access_logs_config: typing.Optional["ServerlessClamscanLoggingProps"] = None,
        efs_encryption: typing.Optional[builtins.bool] = None,
        on_error: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_result: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
    ) -> None:
        '''Creates a ServerlessClamscan construct.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param buckets: An optional list of S3 buckets to configure for ClamAV Virus Scanning; buckets can be added later by calling addSourceBucket.
        :param defs_bucket_access_logs_config: Whether or not to enable Access Logging for the Virus Definitions bucket, you can specify an existing bucket and prefix (Default: Creates a new S3 Bucket for access logs ).
        :param efs_encryption: Whether or not to enable encryption on EFS filesystem (Default: enabled).
        :param on_error: The Lambda Destination for files that fail to scan and are marked 'ERROR' or stuck 'IN PROGRESS' due to a Lambda timeout (Default: Creates and publishes to a new SQS queue if unspecified).
        :param on_result: The Lambda Destination for files marked 'CLEAN' or 'INFECTED' based on the ClamAV Virus scan or 'N/A' for scans triggered by S3 folder creation events marked (Default: Creates and publishes to a new Event Bridge Bus if unspecified).
        '''
        props = ServerlessClamscanProps(
            buckets=buckets,
            defs_bucket_access_logs_config=defs_bucket_access_logs_config,
            efs_encryption=efs_encryption,
            on_error=on_error,
            on_result=on_result,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addSourceBucket")
    def add_source_bucket(self, bucket: aws_cdk.aws_s3.Bucket) -> None:
        '''Sets the specified S3 Bucket as a s3:ObjectCreate* for the ClamAV function.

        Grants the ClamAV function permissions to get and tag objects.
        Adds a bucket policy to disallow GetObject operations on files that are tagged 'IN PROGRESS', 'INFECTED', or 'ERROR'.

        :param bucket: The bucket to add the scanning bucket policy and s3:ObjectCreate* trigger to.
        '''
        return typing.cast(None, jsii.invoke(self, "addSourceBucket", [bucket]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorDest")
    def error_dest(self) -> aws_cdk.aws_lambda.IDestination:
        '''The Lambda Destination for failed on erred scans [ERROR, IN PROGRESS (If error is due to Lambda timeout)].'''
        return typing.cast(aws_cdk.aws_lambda.IDestination, jsii.get(self, "errorDest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resultDest")
    def result_dest(self) -> aws_cdk.aws_lambda.IDestination:
        '''The Lambda Destination for completed ClamAV scans [CLEAN, INFECTED].'''
        return typing.cast(aws_cdk.aws_lambda.IDestination, jsii.get(self, "resultDest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cleanRule")
    def clean_rule(self) -> typing.Optional[aws_cdk.aws_events.Rule]:
        '''Conditional: An Event Bridge Rule for files that are marked 'CLEAN' by ClamAV if a success destination was not specified.'''
        return typing.cast(typing.Optional[aws_cdk.aws_events.Rule], jsii.get(self, "cleanRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defsAccessLogsBucket")
    def defs_access_logs_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        '''Conditional: The Bucket for access logs for the virus definitions bucket if logging is enabled (defsBucketAccessLogsConfig).'''
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "defsAccessLogsBucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorDeadLetterQueue")
    def error_dead_letter_queue(self) -> typing.Optional[aws_cdk.aws_sqs.Queue]:
        '''Conditional: The SQS Dead Letter Queue for the errorQueue if a failure (onError) destination was not specified.'''
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.Queue], jsii.get(self, "errorDeadLetterQueue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="errorQueue")
    def error_queue(self) -> typing.Optional[aws_cdk.aws_sqs.Queue]:
        '''Conditional: The SQS Queue for erred scans if a failure (onError) destination was not specified.'''
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.Queue], jsii.get(self, "errorQueue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="infectedRule")
    def infected_rule(self) -> typing.Optional[aws_cdk.aws_events.Rule]:
        '''Conditional: An Event Bridge Rule for files that are marked 'INFECTED' by ClamAV if a success destination was not specified.'''
        return typing.cast(typing.Optional[aws_cdk.aws_events.Rule], jsii.get(self, "infectedRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resultBus")
    def result_bus(self) -> typing.Optional[aws_cdk.aws_events.EventBus]:
        '''Conditional: The Event Bridge Bus for completed ClamAV scans if a success (onResult) destination was not specified.'''
        return typing.cast(typing.Optional[aws_cdk.aws_events.EventBus], jsii.get(self, "resultBus"))


@jsii.data_type(
    jsii_type="cdk-serverless-clamscan.ServerlessClamscanLoggingProps",
    jsii_struct_bases=[],
    name_mapping={"logs_bucket": "logsBucket", "logs_prefix": "logsPrefix"},
)
class ServerlessClamscanLoggingProps:
    def __init__(
        self,
        *,
        logs_bucket: typing.Optional[typing.Union[builtins.bool, aws_cdk.aws_s3.Bucket]] = None,
        logs_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Interface for ServerlessClamscan Virus Definitions S3 Bucket Logging.

        :param logs_bucket: Destination bucket for the server access logs (Default: Creates a new S3 Bucket for access logs ).
        :param logs_prefix: Optional log file prefix to use for the bucket's access logs, option is ignored if logs_bucket is set to false.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if logs_bucket is not None:
            self._values["logs_bucket"] = logs_bucket
        if logs_prefix is not None:
            self._values["logs_prefix"] = logs_prefix

    @builtins.property
    def logs_bucket(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.aws_s3.Bucket]]:
        '''Destination bucket for the server access logs (Default: Creates a new S3 Bucket for access logs ).'''
        result = self._values.get("logs_bucket")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, aws_cdk.aws_s3.Bucket]], result)

    @builtins.property
    def logs_prefix(self) -> typing.Optional[builtins.str]:
        '''Optional log file prefix to use for the bucket's access logs, option is ignored if logs_bucket is set to false.'''
        result = self._values.get("logs_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerlessClamscanLoggingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-serverless-clamscan.ServerlessClamscanProps",
    jsii_struct_bases=[],
    name_mapping={
        "buckets": "buckets",
        "defs_bucket_access_logs_config": "defsBucketAccessLogsConfig",
        "efs_encryption": "efsEncryption",
        "on_error": "onError",
        "on_result": "onResult",
    },
)
class ServerlessClamscanProps:
    def __init__(
        self,
        *,
        buckets: typing.Optional[typing.Sequence[aws_cdk.aws_s3.Bucket]] = None,
        defs_bucket_access_logs_config: typing.Optional[ServerlessClamscanLoggingProps] = None,
        efs_encryption: typing.Optional[builtins.bool] = None,
        on_error: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_result: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
    ) -> None:
        '''Interface for creating a ServerlessClamscan.

        :param buckets: An optional list of S3 buckets to configure for ClamAV Virus Scanning; buckets can be added later by calling addSourceBucket.
        :param defs_bucket_access_logs_config: Whether or not to enable Access Logging for the Virus Definitions bucket, you can specify an existing bucket and prefix (Default: Creates a new S3 Bucket for access logs ).
        :param efs_encryption: Whether or not to enable encryption on EFS filesystem (Default: enabled).
        :param on_error: The Lambda Destination for files that fail to scan and are marked 'ERROR' or stuck 'IN PROGRESS' due to a Lambda timeout (Default: Creates and publishes to a new SQS queue if unspecified).
        :param on_result: The Lambda Destination for files marked 'CLEAN' or 'INFECTED' based on the ClamAV Virus scan or 'N/A' for scans triggered by S3 folder creation events marked (Default: Creates and publishes to a new Event Bridge Bus if unspecified).
        '''
        if isinstance(defs_bucket_access_logs_config, dict):
            defs_bucket_access_logs_config = ServerlessClamscanLoggingProps(**defs_bucket_access_logs_config)
        self._values: typing.Dict[str, typing.Any] = {}
        if buckets is not None:
            self._values["buckets"] = buckets
        if defs_bucket_access_logs_config is not None:
            self._values["defs_bucket_access_logs_config"] = defs_bucket_access_logs_config
        if efs_encryption is not None:
            self._values["efs_encryption"] = efs_encryption
        if on_error is not None:
            self._values["on_error"] = on_error
        if on_result is not None:
            self._values["on_result"] = on_result

    @builtins.property
    def buckets(self) -> typing.Optional[typing.List[aws_cdk.aws_s3.Bucket]]:
        '''An optional list of S3 buckets to configure for ClamAV Virus Scanning;

        buckets can be added later by calling addSourceBucket.
        '''
        result = self._values.get("buckets")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.Bucket]], result)

    @builtins.property
    def defs_bucket_access_logs_config(
        self,
    ) -> typing.Optional[ServerlessClamscanLoggingProps]:
        '''Whether or not to enable Access Logging for the Virus Definitions bucket, you can specify an existing bucket and prefix (Default: Creates a new S3 Bucket for access logs ).'''
        result = self._values.get("defs_bucket_access_logs_config")
        return typing.cast(typing.Optional[ServerlessClamscanLoggingProps], result)

    @builtins.property
    def efs_encryption(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to enable encryption on EFS filesystem (Default: enabled).'''
        result = self._values.get("efs_encryption")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def on_error(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        '''The Lambda Destination for files that fail to scan and are marked 'ERROR' or stuck 'IN PROGRESS' due to a Lambda timeout (Default: Creates and publishes to a new SQS queue if unspecified).'''
        result = self._values.get("on_error")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    @builtins.property
    def on_result(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        '''The Lambda Destination for files marked 'CLEAN' or 'INFECTED' based on the ClamAV Virus scan or 'N/A' for scans triggered by S3 folder creation events marked (Default: Creates and publishes to a new Event Bridge Bus if unspecified).'''
        result = self._values.get("on_result")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerlessClamscanProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ServerlessClamscan",
    "ServerlessClamscanLoggingProps",
    "ServerlessClamscanProps",
]

publication.publish()
