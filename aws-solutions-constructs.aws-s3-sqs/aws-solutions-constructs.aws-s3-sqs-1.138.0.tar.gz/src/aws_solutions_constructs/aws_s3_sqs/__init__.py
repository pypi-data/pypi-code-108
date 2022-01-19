'''
# aws-s3-sqs module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_s3_sqs`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-s3-sqs`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.s3sqs`|

This AWS Solutions Construct implements an Amazon S3 Bucket that is configured to send notifications to an Amazon SQS queue.

Here is a minimal deployable pattern definition in Typescript:

```python
import {S3ToSqs} from "@aws-solutions-constructs/aws-s3-sqs";

new S3ToSqs(stack, 'S3ToSQSPattern', {});
```

## Initializer

```text
new S3ToSqs(scope: Construct, id: string, props: S3ToSqsProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`S3ToSqsProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingBucketObj?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.IBucket.html)|Existing instance of S3 Bucket object. If this is provided, then also providing bucketProps is an error. |
|bucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html)|Optional user provided props to override the default props for the S3 Bucket.|
|s3EventTypes?|[`s3.EventType[]`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.EventType.html)|The S3 event types that will trigger the notification. Defaults to s3.EventType.OBJECT_CREATED.|
|s3EventFilters?|[`s3.NotificationKeyFilter[]`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.NotificationKeyFilter.html)|S3 object key filter rules to determine which objects trigger this event. If not specified no filter rules will be applied.|
|existingQueueObj?|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Existing SQS queue to be used instead of the default queue. Providing both this and `queueProps` will cause an error. If the SQS queue is encrypted, the KMS key utilized for encryption must be a customer managed CMK.|
|queueProps?|[`sqs.QueueProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.QueueProps.html)|Optional user provided props to override the default props for the SQS queue.|
|deadLetterQueueProps?|[`sqs.QueueProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.QueueProps.html)|Optional user provided props to override the default props for the dead letter SQS queue.|
|deployDeadLetterQueue?|`boolean`|Whether to create a secondary queue to be used as a dead letter queue. Defaults to true.|
|maxReceiveCount?|`number`|The number of times a message can be unsuccessfully dequeued before being moved to the dead letter queue. Defaults to 15.|
|enableEncryptionWithCustomerManagedKey?|`boolean`|Use a KMS Key, either managed by this CDK app, or imported. If importing an encryption key, it must be specified in the encryptionKey property for this construct.|
|encryptionKey?|[`kms.Key`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kms.Key.html)|Optional imported encryption key to encrypt the SQS queue.|
|encryptionKeyProps?|[`kms.KeyProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kms.KeyProps.html)|Optional user provided properties to override the default properties for the KMS encryption key.|
|loggingBucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html)|Optional user provided props to override the default props for the S3 Logging Bucket.|
|logS3AccessLogs?| boolean|Whether to turn on Access Logging for the S3 bucket. Creates an S3 bucket with associated storage costs for the logs. Enabling Access Logging is a best practice. default - true|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|sqsQueue|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Returns an instance of the SQS queue created by the pattern.|
|deadLetterQueue?|[`sqs.Queue`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-sqs.Queue.html)|Returns an instance of the dead-letter SQS queue created by the pattern.|
|encryptionKey|[`kms.IKey`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kms.IKey.html)|Returns an instance of kms.Key used for the SQS queue.|
|s3Bucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)|Returns an instance of the s3.Bucket created by the construct|
|s3LoggingBucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)|Returns an instance of s3.Bucket created by the construct as the logging bucket for the primary bucket.|
|s3BucketInterface|[`s3.IBucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.IBucket.html)|Returns an instance of s3.IBucket created by the construct.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon S3 Bucket

* Configure Access logging for S3 Bucket
* Enable server-side encryption for S3 Bucket using AWS managed KMS Key
* Enforce encryption of data in transit
* Turn on the versioning for S3 Bucket
* Don't allow public access for S3 Bucket
* Retain the S3 Bucket when deleting the CloudFormation stack
* Applies Lifecycle rule to move noncurrent object versions to Glacier storage after 90 days

### Amazon SQS Queue

* Configure least privilege access permissions for SQS Queue
* Deploy SQS dead-letter queue for the source SQS Queue
* Enable server-side encryption for SQS Queue using Customer managed KMS Key
* Enforce encryption of data in transit

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

import aws_cdk.aws_kms
import aws_cdk.aws_s3
import aws_cdk.aws_sqs
import aws_cdk.core


class S3ToSqs(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-s3-sqs.S3ToSqs",
):
    '''
    :summary: The S3ToSqs class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        encryption_key_props: typing.Optional[aws_cdk.aws_kms.KeyProps] = None,
        existing_bucket_obj: typing.Optional[aws_cdk.aws_s3.Bucket] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        s3_event_filters: typing.Optional[typing.Sequence[aws_cdk.aws_s3.NotificationKeyFilter]] = None,
        s3_event_types: typing.Optional[typing.Sequence[aws_cdk.aws_s3.EventType]] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param bucket_props: Optional user provided props to override the default props for the S3 Bucket. Default: - Default props are used
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param enable_encryption_with_customer_managed_key: Use a KMS Key, either managed by this CDK app, or imported. If importing an encryption key, it must be specified in the encryptionKey property for this construct. Default: - true (encryption enabled, managed by this CDK app).
        :param encryption_key: Optional imported encryption key to encrypt the SQS queue. Default: - not specified.
        :param encryption_key_props: Optional user provided props to override the default props for the encryption key. Default: - Default props are used.
        :param existing_bucket_obj: Existing instance of S3 Bucket object, providing both this and ``bucketProps`` will cause an error. Default: - None
        :param existing_queue_obj: Existing instance of SQS queue object, Providing both this and queueProps will cause an error. Default: - Default props are used
        :param logging_bucket_props: Optional user provided props to override the default props for the S3 Logging Bucket. Default: - Default props are used
        :param log_s3_access_logs: Whether to turn on Access Logs for the S3 bucket with the associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param queue_props: Optional user provided properties. Default: - Default props are used
        :param s3_event_filters: S3 object key filter rules to determine which objects trigger this event. Default: - If not specified no filter rules will be applied.
        :param s3_event_types: The S3 event types that will trigger the notification. Default: - If not specified the s3.EventType.OBJECT_CREATED event will trigger the notification.

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the S3ToSqs class.
        '''
        props = S3ToSqsProps(
            bucket_props=bucket_props,
            dead_letter_queue_props=dead_letter_queue_props,
            deploy_dead_letter_queue=deploy_dead_letter_queue,
            enable_encryption_with_customer_managed_key=enable_encryption_with_customer_managed_key,
            encryption_key=encryption_key,
            encryption_key_props=encryption_key_props,
            existing_bucket_obj=existing_bucket_obj,
            existing_queue_obj=existing_queue_obj,
            logging_bucket_props=logging_bucket_props,
            log_s3_access_logs=log_s3_access_logs,
            max_receive_count=max_receive_count,
            queue_props=queue_props,
            s3_event_filters=s3_event_filters,
            s3_event_types=s3_event_types,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3BucketInterface")
    def s3_bucket_interface(self) -> aws_cdk.aws_s3.IBucket:
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "s3BucketInterface"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sqsQueue")
    def sqs_queue(self) -> aws_cdk.aws_sqs.Queue:
        return typing.cast(aws_cdk.aws_sqs.Queue, jsii.get(self, "sqsQueue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deadLetterQueue")
    def dead_letter_queue(self) -> typing.Optional[aws_cdk.aws_sqs.DeadLetterQueue]:
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.DeadLetterQueue], jsii.get(self, "deadLetterQueue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], jsii.get(self, "encryptionKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Bucket")
    def s3_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "s3Bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3LoggingBucket")
    def s3_logging_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "s3LoggingBucket"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-s3-sqs.S3ToSqsProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_props": "bucketProps",
        "dead_letter_queue_props": "deadLetterQueueProps",
        "deploy_dead_letter_queue": "deployDeadLetterQueue",
        "enable_encryption_with_customer_managed_key": "enableEncryptionWithCustomerManagedKey",
        "encryption_key": "encryptionKey",
        "encryption_key_props": "encryptionKeyProps",
        "existing_bucket_obj": "existingBucketObj",
        "existing_queue_obj": "existingQueueObj",
        "logging_bucket_props": "loggingBucketProps",
        "log_s3_access_logs": "logS3AccessLogs",
        "max_receive_count": "maxReceiveCount",
        "queue_props": "queueProps",
        "s3_event_filters": "s3EventFilters",
        "s3_event_types": "s3EventTypes",
    },
)
class S3ToSqsProps:
    def __init__(
        self,
        *,
        bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        dead_letter_queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        deploy_dead_letter_queue: typing.Optional[builtins.bool] = None,
        enable_encryption_with_customer_managed_key: typing.Optional[builtins.bool] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.Key] = None,
        encryption_key_props: typing.Optional[aws_cdk.aws_kms.KeyProps] = None,
        existing_bucket_obj: typing.Optional[aws_cdk.aws_s3.Bucket] = None,
        existing_queue_obj: typing.Optional[aws_cdk.aws_sqs.Queue] = None,
        logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        log_s3_access_logs: typing.Optional[builtins.bool] = None,
        max_receive_count: typing.Optional[jsii.Number] = None,
        queue_props: typing.Optional[aws_cdk.aws_sqs.QueueProps] = None,
        s3_event_filters: typing.Optional[typing.Sequence[aws_cdk.aws_s3.NotificationKeyFilter]] = None,
        s3_event_types: typing.Optional[typing.Sequence[aws_cdk.aws_s3.EventType]] = None,
    ) -> None:
        '''
        :param bucket_props: Optional user provided props to override the default props for the S3 Bucket. Default: - Default props are used
        :param dead_letter_queue_props: Optional user provided properties for the dead letter queue. Default: - Default props are used
        :param deploy_dead_letter_queue: Whether to deploy a secondary queue to be used as a dead letter queue. Default: - true.
        :param enable_encryption_with_customer_managed_key: Use a KMS Key, either managed by this CDK app, or imported. If importing an encryption key, it must be specified in the encryptionKey property for this construct. Default: - true (encryption enabled, managed by this CDK app).
        :param encryption_key: Optional imported encryption key to encrypt the SQS queue. Default: - not specified.
        :param encryption_key_props: Optional user provided props to override the default props for the encryption key. Default: - Default props are used.
        :param existing_bucket_obj: Existing instance of S3 Bucket object, providing both this and ``bucketProps`` will cause an error. Default: - None
        :param existing_queue_obj: Existing instance of SQS queue object, Providing both this and queueProps will cause an error. Default: - Default props are used
        :param logging_bucket_props: Optional user provided props to override the default props for the S3 Logging Bucket. Default: - Default props are used
        :param log_s3_access_logs: Whether to turn on Access Logs for the S3 bucket with the associated storage costs. Enabling Access Logging is a best practice. Default: - true
        :param max_receive_count: The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue. Default: - required field if deployDeadLetterQueue=true.
        :param queue_props: Optional user provided properties. Default: - Default props are used
        :param s3_event_filters: S3 object key filter rules to determine which objects trigger this event. Default: - If not specified no filter rules will be applied.
        :param s3_event_types: The S3 event types that will trigger the notification. Default: - If not specified the s3.EventType.OBJECT_CREATED event will trigger the notification.

        :summary: The properties for the S3ToSqs class.
        '''
        if isinstance(bucket_props, dict):
            bucket_props = aws_cdk.aws_s3.BucketProps(**bucket_props)
        if isinstance(dead_letter_queue_props, dict):
            dead_letter_queue_props = aws_cdk.aws_sqs.QueueProps(**dead_letter_queue_props)
        if isinstance(encryption_key_props, dict):
            encryption_key_props = aws_cdk.aws_kms.KeyProps(**encryption_key_props)
        if isinstance(logging_bucket_props, dict):
            logging_bucket_props = aws_cdk.aws_s3.BucketProps(**logging_bucket_props)
        if isinstance(queue_props, dict):
            queue_props = aws_cdk.aws_sqs.QueueProps(**queue_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket_props is not None:
            self._values["bucket_props"] = bucket_props
        if dead_letter_queue_props is not None:
            self._values["dead_letter_queue_props"] = dead_letter_queue_props
        if deploy_dead_letter_queue is not None:
            self._values["deploy_dead_letter_queue"] = deploy_dead_letter_queue
        if enable_encryption_with_customer_managed_key is not None:
            self._values["enable_encryption_with_customer_managed_key"] = enable_encryption_with_customer_managed_key
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if encryption_key_props is not None:
            self._values["encryption_key_props"] = encryption_key_props
        if existing_bucket_obj is not None:
            self._values["existing_bucket_obj"] = existing_bucket_obj
        if existing_queue_obj is not None:
            self._values["existing_queue_obj"] = existing_queue_obj
        if logging_bucket_props is not None:
            self._values["logging_bucket_props"] = logging_bucket_props
        if log_s3_access_logs is not None:
            self._values["log_s3_access_logs"] = log_s3_access_logs
        if max_receive_count is not None:
            self._values["max_receive_count"] = max_receive_count
        if queue_props is not None:
            self._values["queue_props"] = queue_props
        if s3_event_filters is not None:
            self._values["s3_event_filters"] = s3_event_filters
        if s3_event_types is not None:
            self._values["s3_event_types"] = s3_event_types

    @builtins.property
    def bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Optional user provided props to override the default props for the S3 Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def dead_letter_queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user provided properties for the dead letter queue.

        :default: - Default props are used
        '''
        result = self._values.get("dead_letter_queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def deploy_dead_letter_queue(self) -> typing.Optional[builtins.bool]:
        '''Whether to deploy a secondary queue to be used as a dead letter queue.

        :default: - true.
        '''
        result = self._values.get("deploy_dead_letter_queue")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_encryption_with_customer_managed_key(
        self,
    ) -> typing.Optional[builtins.bool]:
        '''Use a KMS Key, either managed by this CDK app, or imported.

        If importing an encryption key, it must be specified in
        the encryptionKey property for this construct.

        :default: - true (encryption enabled, managed by this CDK app).
        '''
        result = self._values.get("enable_encryption_with_customer_managed_key")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.Key]:
        '''Optional imported encryption key to encrypt the SQS queue.

        :default: - not specified.
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.Key], result)

    @builtins.property
    def encryption_key_props(self) -> typing.Optional[aws_cdk.aws_kms.KeyProps]:
        '''Optional user provided props to override the default props for the encryption key.

        :default: - Default props are used.
        '''
        result = self._values.get("encryption_key_props")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.KeyProps], result)

    @builtins.property
    def existing_bucket_obj(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        '''Existing instance of S3 Bucket object, providing both this and ``bucketProps`` will cause an error.

        :default: - None
        '''
        result = self._values.get("existing_bucket_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], result)

    @builtins.property
    def existing_queue_obj(self) -> typing.Optional[aws_cdk.aws_sqs.Queue]:
        '''Existing instance of SQS queue object, Providing both this and queueProps will cause an error.

        :default: - Default props are used
        '''
        result = self._values.get("existing_queue_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.Queue], result)

    @builtins.property
    def logging_bucket_props(self) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Optional user provided props to override the default props for the S3 Logging Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("logging_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def log_s3_access_logs(self) -> typing.Optional[builtins.bool]:
        '''Whether to turn on Access Logs for the S3 bucket with the associated storage costs.

        Enabling Access Logging is a best practice.

        :default: - true
        '''
        result = self._values.get("log_s3_access_logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_receive_count(self) -> typing.Optional[jsii.Number]:
        '''The number of times a message can be unsuccessfully dequeued before being moved to the dead-letter queue.

        :default: - required field if deployDeadLetterQueue=true.
        '''
        result = self._values.get("max_receive_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def queue_props(self) -> typing.Optional[aws_cdk.aws_sqs.QueueProps]:
        '''Optional user provided properties.

        :default: - Default props are used
        '''
        result = self._values.get("queue_props")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.QueueProps], result)

    @builtins.property
    def s3_event_filters(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_s3.NotificationKeyFilter]]:
        '''S3 object key filter rules to determine which objects trigger this event.

        :default: - If not specified no filter rules will be applied.
        '''
        result = self._values.get("s3_event_filters")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.NotificationKeyFilter]], result)

    @builtins.property
    def s3_event_types(self) -> typing.Optional[typing.List[aws_cdk.aws_s3.EventType]]:
        '''The S3 event types that will trigger the notification.

        :default: - If not specified the s3.EventType.OBJECT_CREATED event will trigger the notification.
        '''
        result = self._values.get("s3_event_types")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_s3.EventType]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3ToSqsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "S3ToSqs",
    "S3ToSqsProps",
]

publication.publish()
