'''
# aws-kinesisfirehose-s3-and-kinesisanalytics module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_kinesisfirehose_s3_and_kinesisanalytics`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-kinesisfirehose-s3-and-kinesisanalytics`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.kinesisfirehoses3kinesisanalytics`|

This AWS Solutions Construct implements an Amazon Kinesis Firehose delivery stream connected to an Amazon S3 bucket, and an Amazon Kinesis Analytics application.

Here is a minimal deployable pattern definition in Typescript:

```javascript
const { KinesisFirehoseToAnalyticsAndS3 } from '@aws-solutions-constructs/aws-kinesisfirehose-s3-and-kinesisanalytics';

new KinesisFirehoseToAnalyticsAndS3(this, 'FirehoseToS3AndAnalyticsPattern', {
    kinesisAnalyticsProps: {
        inputs: [{
            inputSchema: {
                recordColumns: [{
                    name: 'ticker_symbol',
                    sqlType: 'VARCHAR(4)',
                    mapping: '$.ticker_symbol'
                }, {
                    name: 'sector',
                    sqlType: 'VARCHAR(16)',
                    mapping: '$.sector'
                }, {
                    name: 'change',
                    sqlType: 'REAL',
                    mapping: '$.change'
                }, {
                    name: 'price',
                    sqlType: 'REAL',
                    mapping: '$.price'
                }],
                recordFormat: {
                    recordFormatType: 'JSON'
                },
                recordEncoding: 'UTF-8'
            },
            namePrefix: 'SOURCE_SQL_STREAM'
        }]
    }
});

```

## Initializer

```text
new KinesisFirehoseToAnalyticsAndS3(scope: Construct, id: string, props: KinesisFirehoseToAnalyticsAndS3Props);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`KinesisFirehoseToAnalyticsAndS3Props`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|kinesisFirehoseProps?|[`kinesisFirehose.CfnDeliveryStreamProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesisfirehose.CfnDeliveryStreamProps.html)|Optional user-provided props to override the default props for the Kinesis Firehose delivery stream.|
|kinesisAnalyticsProps?|[`kinesisAnalytics.CfnApplicationProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesisanalytics.CfnApplicationProps.html)|Optional user-provided props to override the default props for the Kinesis Analytics application.|
|existingBucketObj?|[`s3.IBucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.IBucket.html)|Existing instance of S3 Bucket object. If this is provided, then also providing bucketProps is an error. |
|bucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html)|User provided props to override the default props for the S3 Bucket.|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|
|loggingBucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html)|Optional user provided props to override the default props for the S3 Logging Bucket.|
|logS3AccessLogs?| boolean|Whether to turn on Access Logging for the S3 bucket. Creates an S3 bucket with associated storage costs for the logs. Enabling Access Logging is a best practice. default - true|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|kinesisAnalytics|[`kinesisAnalytics.CfnApplication`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesisanalytics.CfnApplication.html)|Returns an instance of the Kinesis Analytics application created by the pattern.|
|kinesisFirehose|[`kinesisFirehose.CfnDeliveryStream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesisfirehose.CfnDeliveryStream.html)|Returns an instance of the Kinesis Firehose delivery stream created by the pattern.|
|kinesisFirehoseRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for Kinesis Data Firehose delivery stream.|
|kinesisFirehoseLogGroup|[`logs.LogGroup`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroup.html)|Returns an instance of the LogGroup created by the construct for Kinesis Data Firehose delivery stream|
|s3Bucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)|Returns an instance of the S3 bucket created by the pattern.|
|s3LoggingBucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)|Returns an instance of s3.Bucket created by the construct as the logging bucket for the primary bucket.|
|s3BucketInterface|[`s3.IBucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.IBucket.html)|Returns an instance of s3.IBucket created by the construct.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon Kinesis Firehose

* Enable CloudWatch logging for Kinesis Firehose
* Configure least privilege access IAM role for Amazon Kinesis Firehose

### Amazon S3 Bucket

* Configure Access logging for S3 Bucket
* Enable server-side encryption for S3 Bucket using AWS managed KMS Key
* Enforce encryption of data in transit
* Turn on the versioning for S3 Bucket
* Don't allow public access for S3 Bucket
* Retain the S3 Bucket when deleting the CloudFormation stack
* Applies Lifecycle rule to move noncurrent object versions to Glacier storage after 90 days

### Amazon Kinesis Data Analytics

* Configure least privilege access IAM role for Amazon Kinesis Analytics

## Architecture

![Architecture Diagram](architecture.png)

---


© Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import aws_cdk.aws_iam
import aws_cdk.aws_kinesisanalytics
import aws_cdk.aws_kinesisfirehose
import aws_cdk.aws_logs
import aws_cdk.aws_s3
import aws_cdk.core


class KinesisFirehoseToAnalyticsAndS3(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-kinesisfirehose-s3-and-kinesisanalytics.KinesisFirehoseToAnalyticsAndS3",
):
    '''
    :summary: The KinesisFirehoseToAnalyticsAndS3 class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_bucket_obj: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        kinesis_analytics_props: typing.Optional[aws_cdk.aws_kinesisanalytics.CfnApplicationProps] = None,
        kinesis_firehose_props: typing.Any = None,
        logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param bucket_props: User provided props to override the default props for the S3 Bucket. Default: - Default props are used
        :param existing_bucket_obj: Existing instance of S3 Bucket object, providing both this and ``bucketProps`` will cause an error. Default: - None
        :param kinesis_analytics_props: Optional user-provided props to override the default props for the Kinesis Analytics application. Default: - Default props are used.
        :param kinesis_firehose_props: Optional user-provided props to override the default props for the Kinesis Firehose delivery stream. Default: - Default props are used.
        :param logging_bucket_props: Optional user provided props to override the default props for the S3 Logging Bucket. Default: - Default props are used
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param log_s3_access_logs: Whether to turn on Access Logs for the S3 bucket with the associated storage costs. Enabling Access Logging is a best practice. Default: - true

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the KinesisFirehoseToAnalyticsAndS3 class.
        '''
        props = KinesisFirehoseToAnalyticsAndS3Props(
            bucket_props=bucket_props,
            existing_bucket_obj=existing_bucket_obj,
            kinesis_analytics_props=kinesis_analytics_props,
            kinesis_firehose_props=kinesis_firehose_props,
            logging_bucket_props=logging_bucket_props,
            log_group_props=log_group_props,
            log_s3_access_logs=log_s3_access_logs,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisAnalytics")
    def kinesis_analytics(self) -> aws_cdk.aws_kinesisanalytics.CfnApplication:
        return typing.cast(aws_cdk.aws_kinesisanalytics.CfnApplication, jsii.get(self, "kinesisAnalytics"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisFirehose")
    def kinesis_firehose(self) -> aws_cdk.aws_kinesisfirehose.CfnDeliveryStream:
        return typing.cast(aws_cdk.aws_kinesisfirehose.CfnDeliveryStream, jsii.get(self, "kinesisFirehose"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisFirehoseLogGroup")
    def kinesis_firehose_log_group(self) -> aws_cdk.aws_logs.LogGroup:
        return typing.cast(aws_cdk.aws_logs.LogGroup, jsii.get(self, "kinesisFirehoseLogGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisFirehoseRole")
    def kinesis_firehose_role(self) -> aws_cdk.aws_iam.Role:
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "kinesisFirehoseRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketInterface")
    def s3_bucket_interface(self) -> aws_cdk.aws_s3.IBucket:
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "s3BucketInterface"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "s3Bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3LoggingBucket")
    def s3_logging_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "s3LoggingBucket"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-kinesisfirehose-s3-and-kinesisanalytics.KinesisFirehoseToAnalyticsAndS3Props",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_props": "bucketProps",
        "existing_bucket_obj": "existingBucketObj",
        "kinesis_analytics_props": "kinesisAnalyticsProps",
        "kinesis_firehose_props": "kinesisFirehoseProps",
        "logging_bucket_props": "loggingBucketProps",
        "log_group_props": "logGroupProps",
        "log_s3_access_logs": "logS3AccessLogs",
    },
)
class KinesisFirehoseToAnalyticsAndS3Props:
    def __init__(
        self,
        *,
        bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_bucket_obj: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        kinesis_analytics_props: typing.Optional[aws_cdk.aws_kinesisanalytics.CfnApplicationProps] = None,
        kinesis_firehose_props: typing.Any = None,
        logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''The properties for the KinesisFirehoseToAnalyticsAndS3 class.

        :param bucket_props: User provided props to override the default props for the S3 Bucket. Default: - Default props are used
        :param existing_bucket_obj: Existing instance of S3 Bucket object, providing both this and ``bucketProps`` will cause an error. Default: - None
        :param kinesis_analytics_props: Optional user-provided props to override the default props for the Kinesis Analytics application. Default: - Default props are used.
        :param kinesis_firehose_props: Optional user-provided props to override the default props for the Kinesis Firehose delivery stream. Default: - Default props are used.
        :param logging_bucket_props: Optional user provided props to override the default props for the S3 Logging Bucket. Default: - Default props are used
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param log_s3_access_logs: Whether to turn on Access Logs for the S3 bucket with the associated storage costs. Enabling Access Logging is a best practice. Default: - true
        '''
        if isinstance(bucket_props, dict):
            bucket_props = aws_cdk.aws_s3.BucketProps(**bucket_props)
        if isinstance(kinesis_analytics_props, dict):
            kinesis_analytics_props = aws_cdk.aws_kinesisanalytics.CfnApplicationProps(**kinesis_analytics_props)
        if isinstance(logging_bucket_props, dict):
            logging_bucket_props = aws_cdk.aws_s3.BucketProps(**logging_bucket_props)
        if isinstance(log_group_props, dict):
            log_group_props = aws_cdk.aws_logs.LogGroupProps(**log_group_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket_props is not None:
            self._values["bucket_props"] = bucket_props
        if existing_bucket_obj is not None:
            self._values["existing_bucket_obj"] = existing_bucket_obj
        if kinesis_analytics_props is not None:
            self._values["kinesis_analytics_props"] = kinesis_analytics_props
        if kinesis_firehose_props is not None:
            self._values["kinesis_firehose_props"] = kinesis_firehose_props
        if logging_bucket_props is not None:
            self._values["logging_bucket_props"] = logging_bucket_props
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props
        if log_s3_access_logs is not None:
            self._values["log_s3_access_logs"] = log_s3_access_logs

    @builtins.property
    def bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''User provided props to override the default props for the S3 Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def existing_bucket_obj(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''Existing instance of S3 Bucket object, providing both this and ``bucketProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_bucket_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def kinesis_analytics_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_kinesisanalytics.CfnApplicationProps]:
        '''Optional user-provided props to override the default props for the Kinesis Analytics application.

        :default: - Default props are used.
        '''
        result = self._values.get("kinesis_analytics_props")
        return typing.cast(typing.Optional[aws_cdk.aws_kinesisanalytics.CfnApplicationProps], result)

    @builtins.property
    def kinesis_firehose_props(self) -> typing.Any:
        '''Optional user-provided props to override the default props for the Kinesis Firehose delivery stream.

        :default: - Default props are used.
        '''
        result = self._values.get("kinesis_firehose_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def logging_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Optional user provided props to override the default props for the S3 Logging Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("logging_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def log_group_props(self) -> typing.Optional[aws_cdk.aws_logs.LogGroupProps]:
        '''User provided props to override the default props for the CloudWatchLogs LogGroup.

        :default: - Default props are used
        '''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.LogGroupProps], result)

    @builtins.property
    def log_s3_access_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether to turn on Access Logs for the S3 bucket with the associated storage costs.

        Enabling Access Logging is a best practice.

        :default: - true
        '''
        result = self._values.get("log_s3_access_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KinesisFirehoseToAnalyticsAndS3Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KinesisFirehoseToAnalyticsAndS3",
    "KinesisFirehoseToAnalyticsAndS3Props",
]

publication.publish()
