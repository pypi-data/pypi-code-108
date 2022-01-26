'''
# Amazon Kinesis Data Firehose Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

[Amazon Kinesis Data Firehose](https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html)
is a service for fully-managed delivery of real-time streaming data to storage services
such as Amazon S3, Amazon Redshift, Amazon Elasticsearch, Splunk, or any custom HTTP
endpoint or third-party services such as Datadog, Dynatrace, LogicMonitor, MongoDB, New
Relic, and Sumo Logic.

Kinesis Data Firehose delivery streams are distinguished from Kinesis data streams in
their models of consumtpion. Whereas consumers read from a data stream by actively pulling
data from the stream, a delivery stream pushes data to its destination on a regular
cadence. This means that data streams are intended to have consumers that do on-demand
processing, like AWS Lambda or Amazon EC2. On the other hand, delivery streams are
intended to have destinations that are sources for offline processing and analytics, such
as Amazon S3 and Amazon Redshift.

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk)
project. It allows you to define Kinesis Data Firehose delivery streams.

## Defining a Delivery Stream

In order to define a Delivery Stream, you must specify a destination. An S3 bucket can be
used as a destination. More supported destinations are covered [below](#destinations).

```python
bucket = s3.Bucket(self, "Bucket")
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destinations.S3Bucket(bucket)]
)
```

The above example defines the following resources:

* An S3 bucket
* A Kinesis Data Firehose delivery stream with Direct PUT as the source and CloudWatch
  error logging turned on.
* An IAM role which gives the delivery stream permission to write to the S3 bucket.

## Sources

There are two main methods of sourcing input data: Kinesis Data Streams and via a "direct
put".

See: [Sending Data to a Delivery Stream](https://docs.aws.amazon.com/firehose/latest/dev/basic-write.html)
in the *Kinesis Data Firehose Developer Guide*.

### Kinesis Data Stream

A delivery stream can read directly from a Kinesis data stream as a consumer of the data
stream. Configure this behaviour by providing a data stream in the `sourceStream`
property when constructing a delivery stream:

```python
# destination: firehose.IDestination

source_stream = kinesis.Stream(self, "Source Stream")
firehose.DeliveryStream(self, "Delivery Stream",
    source_stream=source_stream,
    destinations=[destination]
)
```

### Direct Put

Data must be provided via "direct put", ie., by using a `PutRecord` or `PutRecordBatch` API call. There are a number of ways of doing
so, such as:

* Kinesis Agent: a standalone Java application that monitors and delivers files while
  handling file rotation, checkpointing, and retries. See: [Writing to Kinesis Data Firehose Using Kinesis Agent](https://docs.aws.amazon.com/firehose/latest/dev/writing-with-agents.html)
  in the *Kinesis Data Firehose Developer Guide*.
* AWS SDK: a general purpose solution that allows you to deliver data to a delivery stream
  from anywhere using Java, .NET, Node.js, Python, or Ruby. See: [Writing to Kinesis Data Firehose Using the AWS SDK](https://docs.aws.amazon.com/firehose/latest/dev/writing-with-sdk.html)
  in the *Kinesis Data Firehose Developer Guide*.
* CloudWatch Logs: subscribe to a log group and receive filtered log events directly into
  a delivery stream. See: [logs-destinations](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-logs-destinations-readme.html).
* Eventbridge: add an event rule target to send events to a delivery stream based on the
  rule filtering. See: [events-targets](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-events-targets-readme.html).
* SNS: add a subscription to send all notifications from the topic to a delivery
  stream. See: [sns-subscriptions](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-sns-subscriptions-readme.html).
* IoT: add an action to an IoT rule to send various IoT information to a delivery stream

## Destinations

The following destinations are supported. See [kinesisfirehose-destinations](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-kinesisfirehose-destinations-readme.html)
for the implementations of these destinations.

### S3

Defining a delivery stream with an S3 bucket destination:

```python
# bucket: s3.Bucket

s3_destination = destinations.S3Bucket(bucket)

firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[s3_destination]
)
```

The S3 destination also supports custom dynamic prefixes. `prefix` will be used for files
successfully delivered to S3. `errorOutputPrefix` will be added to failed records before
writing them to S3.

```python
# bucket: s3.Bucket

s3_destination = destinations.S3Bucket(bucket,
    data_output_prefix="myFirehose/DeliveredYear=!{timestamp:yyyy}/anyMonth/rand=!{firehose:random-string}",
    error_output_prefix="myFirehoseFailures/!{firehose:error-output-type}/!{timestamp:yyyy}/anyMonth/!{timestamp:dd}"
)
```

See: [Custom S3 Prefixes](https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html) in the *Kinesis Data Firehose Developer Guide*.

## Server-side Encryption

Enabling server-side encryption (SSE) requires Kinesis Data Firehose to encrypt all data
sent to delivery stream when it is stored at rest. This means that data is encrypted
before being written to the service's internal storage layer and decrypted after it is
received from the internal storage layer. The service manages keys and cryptographic
operations so that sources and destinations do not need to, as the data is encrypted and
decrypted at the boundaries of the service (ie., before the data is delivered to a
destination). By default, delivery streams do not have SSE enabled.

The Key Management Service (KMS) Customer Managed Key (CMK) used for SSE can either be
AWS-owned or customer-managed. AWS-owned CMKs are keys that an AWS service (in this case
Kinesis Data Firehose) owns and manages for use in multiple AWS accounts. As a customer,
you cannot view, use, track, or manage these keys, and you are not charged for their
use. On the other hand, customer-managed CMKs are keys that are created and owned within
your account and managed entirely by you. As a customer, you are responsible for managing
access, rotation, aliases, and deletion for these keys, and you are changed for their
use. See: [Customer master keys](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#master_keys)
in the *KMS Developer Guide*.

```python
# destination: firehose.IDestination
# SSE with an customer-managed CMK that is explicitly specified
# key: kms.Key


# SSE with an AWS-owned CMK
firehose.DeliveryStream(self, "Delivery Stream AWS Owned",
    encryption=firehose.StreamEncryption.AWS_OWNED,
    destinations=[destination]
)
# SSE with an customer-managed CMK that is created automatically by the CDK
firehose.DeliveryStream(self, "Delivery Stream Implicit Customer Managed",
    encryption=firehose.StreamEncryption.CUSTOMER_MANAGED,
    destinations=[destination]
)
firehose.DeliveryStream(self, "Delivery Stream Explicit Customer Managed",
    encryption_key=key,
    destinations=[destination]
)
```

See: [Data Protection](https://docs.aws.amazon.com/firehose/latest/dev/encryption.html) in
the *Kinesis Data Firehose Developer Guide*.

## Monitoring

Kinesis Data Firehose is integrated with CloudWatch, so you can monitor the performance of
your delivery streams via logs and metrics.

### Logs

Kinesis Data Firehose will send logs to CloudWatch when data transformation or data
delivery fails. The CDK will enable logging by default and create a CloudWatch LogGroup
and LogStream for your Delivery Stream.

You can provide a specific log group to specify where the CDK will create the log streams
where log events will be sent:

```python
import aws_cdk.aws_logs as logs
# bucket: s3.Bucket

# destination: firehose.IDestination


log_group = logs.LogGroup(self, "Log Group")
destination = destinations.S3Bucket(bucket,
    log_group=log_group
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination]
)
```

Logging can also be disabled:

```python
# bucket: s3.Bucket

destination = destinations.S3Bucket(bucket,
    logging=False
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination]
)
```

See: [Monitoring using CloudWatch Logs](https://docs.aws.amazon.com/firehose/latest/dev/monitoring-with-cloudwatch-logs.html)
in the *Kinesis Data Firehose Developer Guide*.

### Metrics

Kinesis Data Firehose sends metrics to CloudWatch so that you can collect and analyze the
performance of the delivery stream, including data delivery, data ingestion, data
transformation, format conversion, API usage, encryption, and resource usage. You can then
use CloudWatch alarms to alert you, for example, when data freshness (the age of the
oldest record in the delivery stream) exceeds the buffering limit (indicating that data is
not being delivered to your destination), or when the rate of incoming records exceeds the
limit of records per second (indicating data is flowing into your delivery stream faster
than it is configured to process).

CDK provides methods for accessing delivery stream metrics with default configuration,
such as `metricIncomingBytes`, and `metricIncomingRecords` (see [`IDeliveryStream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesisfirehose.IDeliveryStream.html)
for a full list). CDK also provides a generic `metric` method that can be used to produce
metric configurations for any metric provided by Kinesis Data Firehose; the configurations
are pre-populated with the correct dimensions for the delivery stream.

```python
import aws_cdk.aws_cloudwatch as cloudwatch
# delivery_stream: firehose.DeliveryStream


# Alarm that triggers when the per-second average of incoming bytes exceeds 90% of the current service limit
incoming_bytes_percent_of_limit = cloudwatch.MathExpression(
    expression="incomingBytes / 300 / bytePerSecLimit",
    using_metrics={
        "incoming_bytes": delivery_stream.metric_incoming_bytes(statistic=cloudwatch.Statistic.SUM),
        "byte_per_sec_limit": delivery_stream.metric("BytesPerSecondLimit")
    }
)

cloudwatch.Alarm(self, "Alarm",
    metric=incoming_bytes_percent_of_limit,
    threshold=0.9,
    evaluation_periods=3
)
```

See: [Monitoring Using CloudWatch Metrics](https://docs.aws.amazon.com/firehose/latest/dev/monitoring-with-cloudwatch-metrics.html)
in the *Kinesis Data Firehose Developer Guide*.

## Compression

Your data can automatically be compressed when it is delivered to S3 as either a final or
an intermediary/backup destination. Supported compression formats are: gzip, Snappy,
Hadoop-compatible Snappy, and ZIP, except for Redshift destinations, where Snappy
(regardless of Hadoop-compatibility) and ZIP are not supported. By default, data is
delivered to S3 without compression.

```python
# Compress data delivered to S3 using Snappy
# bucket: s3.Bucket

s3_destination = destinations.S3Bucket(bucket,
    compression=destinations.Compression.SNAPPY
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[s3_destination]
)
```

## Buffering

Incoming data is buffered before it is delivered to the specified destination. The
delivery stream will wait until the amount of incoming data has exceeded some threshold
(the "buffer size") or until the time since the last data delivery occurred exceeds some
threshold (the "buffer interval"), whichever happens first. You can configure these
thresholds based on the capabilities of the destination and your use-case. By default, the
buffer size is 5 MiB and the buffer interval is 5 minutes.

```python
# Increase the buffer interval and size to 10 minutes and 8 MiB, respectively
# bucket: s3.Bucket

destination = destinations.S3Bucket(bucket,
    buffering_interval=Duration.minutes(10),
    buffering_size=Size.mebibytes(8)
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination]
)
```

See: [Data Delivery Frequency](https://docs.aws.amazon.com/firehose/latest/dev/basic-deliver.html#frequency)
in the *Kinesis Data Firehose Developer Guide*.

## Destination Encryption

Your data can be automatically encrypted when it is delivered to S3 as a final or
an intermediary/backup destination. Kinesis Data Firehose supports Amazon S3 server-side
encryption with AWS Key Management Service (AWS KMS) for encrypting delivered data
in Amazon S3. You can choose to not encrypt the data or to encrypt with a key from
the list of AWS KMS keys that you own. For more information, see [Protecting Data
Using Server-Side Encryption with AWS KMS–Managed Keys (SSE-KMS)](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html). Data is not encrypted by default.

```python
# bucket: s3.Bucket
# key: kms.Key

destination = destinations.S3Bucket(bucket,
    encryption_key=key
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination]
)
```

## Backup

A delivery stream can be configured to backup data to S3 that it attempted to deliver to
the configured destination. Backed up data can be all the data that the delivery stream
attempted to deliver or just data that it failed to deliver (Redshift and S3 destinations
can only backup all data). CDK can create a new S3 bucket where it will back up data or
you can provide a bucket where data will be backed up. You can also provide a prefix under
which your backed-up data will be placed within the bucket. By default, source data is not
backed up to S3.

```python
# Enable backup of all source records (to an S3 bucket created by CDK).
# bucket: s3.Bucket
# Explicitly provide an S3 bucket to which all source records will be backed up.
# backup_bucket: s3.Bucket

firehose.DeliveryStream(self, "Delivery Stream Backup All",
    destinations=[
        destinations.S3Bucket(bucket,
            s3_backup=destinations.DestinationS3BackupProps(
                mode=destinations.BackupMode.ALL
            )
        )
    ]
)
firehose.DeliveryStream(self, "Delivery Stream Backup All Explicit Bucket",
    destinations=[
        destinations.S3Bucket(bucket,
            s3_backup=destinations.DestinationS3BackupProps(
                bucket=backup_bucket
            )
        )
    ]
)
# Explicitly provide an S3 prefix under which all source records will be backed up.
firehose.DeliveryStream(self, "Delivery Stream Backup All Explicit Prefix",
    destinations=[
        destinations.S3Bucket(bucket,
            s3_backup=destinations.DestinationS3BackupProps(
                mode=destinations.BackupMode.ALL,
                data_output_prefix="mybackup"
            )
        )
    ]
)
```

If any Data Processing or Transformation is configured on your Delivery Stream, the source
records will be backed up in their original format.

## Data Processing/Transformation

Data can be transformed before being delivered to destinations. There are two types of
data processing for delivery streams: record transformation with AWS Lambda, and record
format conversion using a schema stored in an AWS Glue table. If both types of data
processing are configured, then the Lambda transformation is performed first. By default,
no data processing occurs. This construct library currently only supports data
transformation with AWS Lambda. See [#15501](https://github.com/aws/aws-cdk/issues/15501)
to track the status of adding support for record format conversion.

### Data transformation with AWS Lambda

To transform the data, Kinesis Data Firehose will call a Lambda function that you provide
and deliver the data returned in place of the source record. The function must return a
result that contains records in a specific format, including the following fields:

* `recordId` -- the ID of the input record that corresponds the results.
* `result` -- the status of the transformation of the record: "Ok" (success), "Dropped"
  (not processed intentionally), or "ProcessingFailed" (not processed due to an error).
* `data` -- the transformed data, Base64-encoded.

The data is buffered up to 1 minute and up to 3 MiB by default before being sent to the
function, but can be configured using `bufferInterval` and `bufferSize` in the processor
configuration (see: [Buffering](#buffering)). If the function invocation fails due to a
network timeout or because of hitting an invocation limit, the invocation is retried 3
times by default, but can be configured using `retries` in the processor configuration.

```python
# bucket: s3.Bucket
# Provide a Lambda function that will transform records before delivery, with custom
# buffering and retry configuration
lambda_function = lambda_.Function(self, "Processor",
    runtime=lambda_.Runtime.NODEJS_12_X,
    handler="index.handler",
    code=lambda_.Code.from_asset(path.join(__dirname, "process-records"))
)
lambda_processor = firehose.LambdaFunctionProcessor(lambda_function,
    buffer_interval=Duration.minutes(5),
    buffer_size=Size.mebibytes(5),
    retries=5
)
s3_destination = destinations.S3Bucket(bucket,
    processor=lambda_processor
)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[s3_destination]
)
```

```python
import path as path
import aws_cdk.aws_kinesisfirehose_alpha as firehose
import aws_cdk.aws_kms as kms
import aws_cdk.aws_lambda_nodejs as lambdanodejs
import aws_cdk.aws_logs as logs
import aws_cdk.aws_s3 as s3
import aws_cdk as cdk
import aws_cdk.aws_kinesisfirehose_destinations_alpha as destinations

app = cdk.App()

stack = cdk.Stack(app, "aws-cdk-firehose-delivery-stream-s3-all-properties")

bucket = s3.Bucket(stack, "Bucket",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True
)

backup_bucket = s3.Bucket(stack, "BackupBucket",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True
)
log_group = logs.LogGroup(stack, "LogGroup",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

data_processor_function = lambdanodejs.NodejsFunction(stack, "DataProcessorFunction",
    entry=path.join(__dirname, "lambda-data-processor.js"),
    timeout=cdk.Duration.minutes(1)
)

processor = firehose.LambdaFunctionProcessor(data_processor_function,
    buffer_interval=cdk.Duration.seconds(60),
    buffer_size=cdk.Size.mebibytes(1),
    retries=1
)

key = kms.Key(stack, "Key",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

backup_key = kms.Key(stack, "BackupKey",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

firehose.DeliveryStream(stack, "Delivery Stream",
    destinations=[destinations.S3Bucket(bucket,
        logging=True,
        log_group=log_group,
        processor=processor,
        compression=destinations.Compression.GZIP,
        data_output_prefix="regularPrefix",
        error_output_prefix="errorPrefix",
        buffering_interval=cdk.Duration.seconds(60),
        buffering_size=cdk.Size.mebibytes(1),
        encryption_key=key,
        s3_backup=destinations.DestinationS3BackupProps(
            mode=destinations.BackupMode.ALL,
            bucket=backup_bucket,
            compression=destinations.Compression.ZIP,
            data_output_prefix="backupPrefix",
            error_output_prefix="backupErrorPrefix",
            buffering_interval=cdk.Duration.seconds(60),
            buffering_size=cdk.Size.mebibytes(1),
            encryption_key=backup_key
        )
    )]
)

app.synth()
```

!cdk-integ pragma:ignore-assets

```python
import path as path
import aws_cdk.aws_kinesisfirehose_alpha as firehose
import aws_cdk.aws_kms as kms
import aws_cdk.aws_lambda_nodejs as lambdanodejs
import aws_cdk.aws_logs as logs
import aws_cdk.aws_s3 as s3
import aws_cdk as cdk
import aws_cdk.aws_kinesisfirehose_destinations_alpha as destinations

app = cdk.App()

stack = cdk.Stack(app, "aws-cdk-firehose-delivery-stream-s3-all-properties")

bucket = s3.Bucket(stack, "Bucket",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True
)

backup_bucket = s3.Bucket(stack, "BackupBucket",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True
)
log_group = logs.LogGroup(stack, "LogGroup",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

data_processor_function = lambdanodejs.NodejsFunction(stack, "DataProcessorFunction",
    entry=path.join(__dirname, "lambda-data-processor.js"),
    timeout=cdk.Duration.minutes(1)
)

processor = firehose.LambdaFunctionProcessor(data_processor_function,
    buffer_interval=cdk.Duration.seconds(60),
    buffer_size=cdk.Size.mebibytes(1),
    retries=1
)

key = kms.Key(stack, "Key",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

backup_key = kms.Key(stack, "BackupKey",
    removal_policy=cdk.RemovalPolicy.DESTROY
)

firehose.DeliveryStream(stack, "Delivery Stream",
    destinations=[destinations.S3Bucket(bucket,
        logging=True,
        log_group=log_group,
        processor=processor,
        compression=destinations.Compression.GZIP,
        data_output_prefix="regularPrefix",
        error_output_prefix="errorPrefix",
        buffering_interval=cdk.Duration.seconds(60),
        buffering_size=cdk.Size.mebibytes(1),
        encryption_key=key,
        s3_backup=destinations.DestinationS3BackupProps(
            mode=destinations.BackupMode.ALL,
            bucket=backup_bucket,
            compression=destinations.Compression.ZIP,
            data_output_prefix="backupPrefix",
            error_output_prefix="backupErrorPrefix",
            buffering_interval=cdk.Duration.seconds(60),
            buffering_size=cdk.Size.mebibytes(1),
            encryption_key=backup_key
        )
    )]
)

app.synth()
```

See: [Data Transformation](https://docs.aws.amazon.com/firehose/latest/dev/data-transformation.html)
in the *Kinesis Data Firehose Developer Guide*.

## Specifying an IAM role

The DeliveryStream class automatically creates IAM service roles with all the minimum
necessary permissions for Kinesis Data Firehose to access the resources referenced by your
delivery stream. One service role is created for the delivery stream that allows Kinesis
Data Firehose to read from a Kinesis data stream (if one is configured as the delivery
stream source) and for server-side encryption. Another service role is created for each
destination, which gives Kinesis Data Firehose write access to the destination resource,
as well as the ability to invoke data transformers and read schemas for record format
conversion. If you wish, you may specify your own IAM role for either the delivery stream
or the destination service role, or both. It must have the correct trust policy (it must
allow Kinesis Data Firehose to assume it) or delivery stream creation or data delivery
will fail. Other required permissions to destination resources, encryption keys, etc.,
will be provided automatically.

```python
# Specify the roles created above when defining the destination and delivery stream.
# bucket: s3.Bucket
# Create service roles for the delivery stream and destination.
# These can be used for other purposes and granted access to different resources.
# They must include the Kinesis Data Firehose service principal in their trust policies.
# Two separate roles are shown below, but the same role can be used for both purposes.
delivery_stream_role = iam.Role(self, "Delivery Stream Role",
    assumed_by=iam.ServicePrincipal("firehose.amazonaws.com")
)
destination_role = iam.Role(self, "Destination Role",
    assumed_by=iam.ServicePrincipal("firehose.amazonaws.com")
)
destination = destinations.S3Bucket(bucket, role=destination_role)
firehose.DeliveryStream(self, "Delivery Stream",
    destinations=[destination],
    role=delivery_stream_role
)
```

See [Controlling Access](https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html)
in the *Kinesis Data Firehose Developer Guide*.

## Granting application access to a delivery stream

IAM roles, users or groups which need to be able to work with delivery streams should be
granted IAM permissions.

Any object that implements the `IGrantable` interface (ie., has an associated principal)
can be granted permissions to a delivery stream by calling:

* `grantPutRecords(principal)` - grants the principal the ability to put records onto the
  delivery stream
* `grant(principal, ...actions)` - grants the principal permission to a custom set of
  actions

```python
# Give the role permissions to write data to the delivery stream
# delivery_stream: firehose.DeliveryStream
lambda_role = iam.Role(self, "Role",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)
delivery_stream.grant_put_records(lambda_role)
```

The following write permissions are provided to a service principal by the `grantPutRecords()` method:

* `firehose:PutRecord`
* `firehose:PutRecordBatch`

## Granting a delivery stream access to a resource

Conversely to the above, Kinesis Data Firehose requires permissions in order for delivery
streams to interact with resources that you own. For example, if an S3 bucket is specified
as a destination of a delivery stream, the delivery stream must be granted permissions to
put and get objects from the bucket. When using the built-in AWS service destinations
found in the `@aws-cdk/aws-kinesisfirehose-destinations` module, the CDK grants the
permissions automatically. However, custom or third-party destinations may require custom
permissions. In this case, use the delivery stream as an `IGrantable`, as follows:

```python
# delivery_stream: firehose.DeliveryStream
fn = lambda_.Function(self, "Function",
    code=lambda_.Code.from_inline("exports.handler = (event) => {}"),
    runtime=lambda_.Runtime.NODEJS_14_X,
    handler="index.handler"
)
fn.grant_invoke(delivery_stream)
```

## Multiple destinations

Though the delivery stream allows specifying an array of destinations, only one
destination per delivery stream is currently allowed. This limitation is enforced at CDK
synthesis time and will throw an error.
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
import aws_cdk.aws_cloudwatch
import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_kinesis
import aws_cdk.aws_kinesisfirehose
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import constructs


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.DataProcessorBindOptions",
    jsii_struct_bases=[],
    name_mapping={"role": "role"},
)
class DataProcessorBindOptions:
    def __init__(self, *, role: aws_cdk.aws_iam.IRole) -> None:
        '''(experimental) Options when binding a DataProcessor to a delivery stream destination.

        :param role: (experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose_alpha as kinesisfirehose_alpha
            from aws_cdk import aws_iam as iam
            
            # role: iam.Role
            
            data_processor_bind_options = kinesisfirehose_alpha.DataProcessorBindOptions(
                role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role": role,
        }

    @builtins.property
    def role(self) -> aws_cdk.aws_iam.IRole:
        '''(experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        '''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(aws_cdk.aws_iam.IRole, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataProcessorBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.DataProcessorConfig",
    jsii_struct_bases=[],
    name_mapping={
        "processor_identifier": "processorIdentifier",
        "processor_type": "processorType",
    },
)
class DataProcessorConfig:
    def __init__(
        self,
        *,
        processor_identifier: "DataProcessorIdentifier",
        processor_type: builtins.str,
    ) -> None:
        '''(experimental) The full configuration of a data processor.

        :param processor_identifier: (experimental) The key-value pair that identifies the underlying processor resource.
        :param processor_type: (experimental) The type of the underlying processor resource. Must be an accepted value in ``CfnDeliveryStream.ProcessorProperty.Type``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose_alpha as kinesisfirehose_alpha
            
            data_processor_config = kinesisfirehose_alpha.DataProcessorConfig(
                processor_identifier=kinesisfirehose_alpha.DataProcessorIdentifier(
                    parameter_name="parameterName",
                    parameter_value="parameterValue"
                ),
                processor_type="processorType"
            )
        '''
        if isinstance(processor_identifier, dict):
            processor_identifier = DataProcessorIdentifier(**processor_identifier)
        self._values: typing.Dict[str, typing.Any] = {
            "processor_identifier": processor_identifier,
            "processor_type": processor_type,
        }

    @builtins.property
    def processor_identifier(self) -> "DataProcessorIdentifier":
        '''(experimental) The key-value pair that identifies the underlying processor resource.

        :stability: experimental
        '''
        result = self._values.get("processor_identifier")
        assert result is not None, "Required property 'processor_identifier' is missing"
        return typing.cast("DataProcessorIdentifier", result)

    @builtins.property
    def processor_type(self) -> builtins.str:
        '''(experimental) The type of the underlying processor resource.

        Must be an accepted value in ``CfnDeliveryStream.ProcessorProperty.Type``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processor.html#cfn-kinesisfirehose-deliverystream-processor-type
        :stability: experimental

        Example::

            "Lambda"
        '''
        result = self._values.get("processor_type")
        assert result is not None, "Required property 'processor_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataProcessorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.DataProcessorIdentifier",
    jsii_struct_bases=[],
    name_mapping={
        "parameter_name": "parameterName",
        "parameter_value": "parameterValue",
    },
)
class DataProcessorIdentifier:
    def __init__(
        self,
        *,
        parameter_name: builtins.str,
        parameter_value: builtins.str,
    ) -> None:
        '''(experimental) The key-value pair that identifies the underlying processor resource.

        :param parameter_name: (experimental) The parameter name that corresponds to the processor resource's identifier. Must be an accepted value in ``CfnDeliveryStream.ProcessoryParameterProperty.ParameterName``.
        :param parameter_value: (experimental) The identifier of the underlying processor resource.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-kinesisfirehose-deliverystream-processorparameter.html
        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose_alpha as kinesisfirehose_alpha
            
            data_processor_identifier = kinesisfirehose_alpha.DataProcessorIdentifier(
                parameter_name="parameterName",
                parameter_value="parameterValue"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "parameter_name": parameter_name,
            "parameter_value": parameter_value,
        }

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''(experimental) The parameter name that corresponds to the processor resource's identifier.

        Must be an accepted value in ``CfnDeliveryStream.ProcessoryParameterProperty.ParameterName``.

        :stability: experimental
        '''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_value(self) -> builtins.str:
        '''(experimental) The identifier of the underlying processor resource.

        :stability: experimental
        '''
        result = self._values.get("parameter_value")
        assert result is not None, "Required property 'parameter_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataProcessorIdentifier(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.DataProcessorProps",
    jsii_struct_bases=[],
    name_mapping={
        "buffer_interval": "bufferInterval",
        "buffer_size": "bufferSize",
        "retries": "retries",
    },
)
class DataProcessorProps:
    def __init__(
        self,
        *,
        buffer_interval: typing.Optional[aws_cdk.Duration] = None,
        buffer_size: typing.Optional[aws_cdk.Size] = None,
        retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Configure the data processor.

        :param buffer_interval: (experimental) The length of time Kinesis Data Firehose will buffer incoming data before calling the processor. s Default: Duration.minutes(1)
        :param buffer_size: (experimental) The amount of incoming data Kinesis Data Firehose will buffer before calling the processor. Default: Size.mebibytes(3)
        :param retries: (experimental) The number of times Kinesis Data Firehose will retry the processor invocation after a failure due to network timeout or invocation limits. Default: 3

        :stability: experimental
        :exampleMetadata: lit=../aws-kinesisfirehose-destinations/test/integ.s3-bucket.lit.ts infused

        Example::

            import path as path
            import aws_cdk.aws_kinesisfirehose_alpha as firehose
            import aws_cdk.aws_kms as kms
            import aws_cdk.aws_lambda_nodejs as lambdanodejs
            import aws_cdk.aws_logs as logs
            import aws_cdk.aws_s3 as s3
            import aws_cdk as cdk
            import aws_cdk.aws_kinesisfirehose_destinations_alpha as destinations
            
            app = cdk.App()
            
            stack = cdk.Stack(app, "aws-cdk-firehose-delivery-stream-s3-all-properties")
            
            bucket = s3.Bucket(stack, "Bucket",
                removal_policy=cdk.RemovalPolicy.DESTROY,
                auto_delete_objects=True
            )
            
            backup_bucket = s3.Bucket(stack, "BackupBucket",
                removal_policy=cdk.RemovalPolicy.DESTROY,
                auto_delete_objects=True
            )
            log_group = logs.LogGroup(stack, "LogGroup",
                removal_policy=cdk.RemovalPolicy.DESTROY
            )
            
            data_processor_function = lambdanodejs.NodejsFunction(stack, "DataProcessorFunction",
                entry=path.join(__dirname, "lambda-data-processor.js"),
                timeout=cdk.Duration.minutes(1)
            )
            
            processor = firehose.LambdaFunctionProcessor(data_processor_function,
                buffer_interval=cdk.Duration.seconds(60),
                buffer_size=cdk.Size.mebibytes(1),
                retries=1
            )
            
            key = kms.Key(stack, "Key",
                removal_policy=cdk.RemovalPolicy.DESTROY
            )
            
            backup_key = kms.Key(stack, "BackupKey",
                removal_policy=cdk.RemovalPolicy.DESTROY
            )
            
            firehose.DeliveryStream(stack, "Delivery Stream",
                destinations=[destinations.S3Bucket(bucket,
                    logging=True,
                    log_group=log_group,
                    processor=processor,
                    compression=destinations.Compression.GZIP,
                    data_output_prefix="regularPrefix",
                    error_output_prefix="errorPrefix",
                    buffering_interval=cdk.Duration.seconds(60),
                    buffering_size=cdk.Size.mebibytes(1),
                    encryption_key=key,
                    s3_backup=destinations.DestinationS3BackupProps(
                        mode=destinations.BackupMode.ALL,
                        bucket=backup_bucket,
                        compression=destinations.Compression.ZIP,
                        data_output_prefix="backupPrefix",
                        error_output_prefix="backupErrorPrefix",
                        buffering_interval=cdk.Duration.seconds(60),
                        buffering_size=cdk.Size.mebibytes(1),
                        encryption_key=backup_key
                    )
                )]
            )
            
            app.synth()
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if buffer_interval is not None:
            self._values["buffer_interval"] = buffer_interval
        if buffer_size is not None:
            self._values["buffer_size"] = buffer_size
        if retries is not None:
            self._values["retries"] = retries

    @builtins.property
    def buffer_interval(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) The length of time Kinesis Data Firehose will buffer incoming data before calling the processor.

        s

        :default: Duration.minutes(1)

        :stability: experimental
        '''
        result = self._values.get("buffer_interval")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def buffer_size(self) -> typing.Optional[aws_cdk.Size]:
        '''(experimental) The amount of incoming data Kinesis Data Firehose will buffer before calling the processor.

        :default: Size.mebibytes(3)

        :stability: experimental
        '''
        result = self._values.get("buffer_size")
        return typing.cast(typing.Optional[aws_cdk.Size], result)

    @builtins.property
    def retries(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of times Kinesis Data Firehose will retry the processor invocation after a failure due to network timeout or invocation limits.

        :default: 3

        :stability: experimental
        '''
        result = self._values.get("retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataProcessorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.DeliveryStreamAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "delivery_stream_arn": "deliveryStreamArn",
        "delivery_stream_name": "deliveryStreamName",
        "role": "role",
    },
)
class DeliveryStreamAttributes:
    def __init__(
        self,
        *,
        delivery_stream_arn: typing.Optional[builtins.str] = None,
        delivery_stream_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''(experimental) A full specification of a delivery stream that can be used to import it fluently into the CDK application.

        :param delivery_stream_arn: (experimental) The ARN of the delivery stream. At least one of deliveryStreamArn and deliveryStreamName must be provided. Default: - derived from ``deliveryStreamName``.
        :param delivery_stream_name: (experimental) The name of the delivery stream. At least one of deliveryStreamName and deliveryStreamArn must be provided. Default: - derived from ``deliveryStreamArn``.
        :param role: (experimental) The IAM role associated with this delivery stream. Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side. Default: - the imported stream cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose_alpha as kinesisfirehose_alpha
            from aws_cdk import aws_iam as iam
            
            # role: iam.Role
            
            delivery_stream_attributes = kinesisfirehose_alpha.DeliveryStreamAttributes(
                delivery_stream_arn="deliveryStreamArn",
                delivery_stream_name="deliveryStreamName",
                role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delivery_stream_arn is not None:
            self._values["delivery_stream_arn"] = delivery_stream_arn
        if delivery_stream_name is not None:
            self._values["delivery_stream_name"] = delivery_stream_name
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def delivery_stream_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the delivery stream.

        At least one of deliveryStreamArn and deliveryStreamName must be provided.

        :default: - derived from ``deliveryStreamName``.

        :stability: experimental
        '''
        result = self._values.get("delivery_stream_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delivery_stream_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the delivery stream.

        At least one of deliveryStreamName and deliveryStreamArn  must be provided.

        :default: - derived from ``deliveryStreamArn``.

        :stability: experimental
        '''
        result = self._values.get("delivery_stream_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM role associated with this delivery stream.

        Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side.

        :default: - the imported stream cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.DeliveryStreamProps",
    jsii_struct_bases=[],
    name_mapping={
        "destinations": "destinations",
        "delivery_stream_name": "deliveryStreamName",
        "encryption": "encryption",
        "encryption_key": "encryptionKey",
        "role": "role",
        "source_stream": "sourceStream",
    },
)
class DeliveryStreamProps:
    def __init__(
        self,
        *,
        destinations: typing.Sequence["IDestination"],
        delivery_stream_name: typing.Optional[builtins.str] = None,
        encryption: typing.Optional["StreamEncryption"] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        source_stream: typing.Optional[aws_cdk.aws_kinesis.IStream] = None,
    ) -> None:
        '''(experimental) Properties for a new delivery stream.

        :param destinations: (experimental) The destinations that this delivery stream will deliver data to. Only a singleton array is supported at this time.
        :param delivery_stream_name: (experimental) A name for the delivery stream. Default: - a name is generated by CloudFormation.
        :param encryption: (experimental) Indicates the type of customer master key (CMK) to use for server-side encryption, if any. Default: StreamEncryption.UNENCRYPTED - unless ``encryptionKey`` is provided, in which case this will be implicitly set to ``StreamEncryption.CUSTOMER_MANAGED``
        :param encryption_key: (experimental) Customer managed key to server-side encrypt data in the stream. Default: - no KMS key will be used; if ``encryption`` is set to ``CUSTOMER_MANAGED``, a KMS key will be created for you
        :param role: (experimental) The IAM role associated with this delivery stream. Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side. Default: - a role will be created with default permissions.
        :param source_stream: (experimental) The Kinesis data stream to use as a source for this delivery stream. Default: - data must be written to the delivery stream via a direct put.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # bucket: s3.Bucket
            # Provide a Lambda function that will transform records before delivery, with custom
            # buffering and retry configuration
            lambda_function = lambda_.Function(self, "Processor",
                runtime=lambda_.Runtime.NODEJS_12_X,
                handler="index.handler",
                code=lambda_.Code.from_asset(path.join(__dirname, "process-records"))
            )
            lambda_processor = firehose.LambdaFunctionProcessor(lambda_function,
                buffer_interval=Duration.minutes(5),
                buffer_size=Size.mebibytes(5),
                retries=5
            )
            s3_destination = destinations.S3Bucket(bucket,
                processor=lambda_processor
            )
            firehose.DeliveryStream(self, "Delivery Stream",
                destinations=[s3_destination]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "destinations": destinations,
        }
        if delivery_stream_name is not None:
            self._values["delivery_stream_name"] = delivery_stream_name
        if encryption is not None:
            self._values["encryption"] = encryption
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if role is not None:
            self._values["role"] = role
        if source_stream is not None:
            self._values["source_stream"] = source_stream

    @builtins.property
    def destinations(self) -> typing.List["IDestination"]:
        '''(experimental) The destinations that this delivery stream will deliver data to.

        Only a singleton array is supported at this time.

        :stability: experimental
        '''
        result = self._values.get("destinations")
        assert result is not None, "Required property 'destinations' is missing"
        return typing.cast(typing.List["IDestination"], result)

    @builtins.property
    def delivery_stream_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for the delivery stream.

        :default: - a name is generated by CloudFormation.

        :stability: experimental
        '''
        result = self._values.get("delivery_stream_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption(self) -> typing.Optional["StreamEncryption"]:
        '''(experimental) Indicates the type of customer master key (CMK) to use for server-side encryption, if any.

        :default: StreamEncryption.UNENCRYPTED - unless ``encryptionKey`` is provided, in which case this will be implicitly set to ``StreamEncryption.CUSTOMER_MANAGED``

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional["StreamEncryption"], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''(experimental) Customer managed key to server-side encrypt data in the stream.

        :default: - no KMS key will be used; if ``encryption`` is set to ``CUSTOMER_MANAGED``, a KMS key will be created for you

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The IAM role associated with this delivery stream.

        Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side.

        :default: - a role will be created with default permissions.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def source_stream(self) -> typing.Optional[aws_cdk.aws_kinesis.IStream]:
        '''(experimental) The Kinesis data stream to use as a source for this delivery stream.

        :default: - data must be written to the delivery stream via a direct put.

        :stability: experimental
        '''
        result = self._values.get("source_stream")
        return typing.cast(typing.Optional[aws_cdk.aws_kinesis.IStream], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeliveryStreamProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.DestinationBindOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class DestinationBindOptions:
    def __init__(self) -> None:
        '''(experimental) Options when binding a destination to a delivery stream.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose_alpha as kinesisfirehose_alpha
            
            destination_bind_options = kinesisfirehose_alpha.DestinationBindOptions()
        '''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DestinationBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.DestinationConfig",
    jsii_struct_bases=[],
    name_mapping={
        "dependables": "dependables",
        "extended_s3_destination_configuration": "extendedS3DestinationConfiguration",
    },
)
class DestinationConfig:
    def __init__(
        self,
        *,
        dependables: typing.Optional[typing.Sequence[constructs.IDependable]] = None,
        extended_s3_destination_configuration: typing.Optional[aws_cdk.aws_kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty] = None,
    ) -> None:
        '''(experimental) A Kinesis Data Firehose delivery stream destination configuration.

        :param dependables: (experimental) Any resources that were created by the destination when binding it to the stack that must be deployed before the delivery stream is deployed. Default: []
        :param extended_s3_destination_configuration: (experimental) S3 destination configuration properties. Default: - S3 destination is not used.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisfirehose_alpha as kinesisfirehose_alpha
            import constructs as constructs
            
            # dependable: constructs.IDependable
            
            destination_config = kinesisfirehose_alpha.DestinationConfig(
                dependables=[dependable],
                extended_s3_destination_configuration=ExtendedS3DestinationConfigurationProperty(
                    bucket_arn="bucketArn",
                    role_arn="roleArn",
            
                    # the properties below are optional
                    buffering_hints=BufferingHintsProperty(
                        interval_in_seconds=123,
                        size_in_mBs=123
                    ),
                    cloud_watch_logging_options=CloudWatchLoggingOptionsProperty(
                        enabled=False,
                        log_group_name="logGroupName",
                        log_stream_name="logStreamName"
                    ),
                    compression_format="compressionFormat",
                    data_format_conversion_configuration=DataFormatConversionConfigurationProperty(
                        enabled=False,
                        input_format_configuration=InputFormatConfigurationProperty(
                            deserializer=DeserializerProperty(
                                hive_json_ser_de=HiveJsonSerDeProperty(
                                    timestamp_formats=["timestampFormats"]
                                ),
                                open_xJson_ser_de=OpenXJsonSerDeProperty(
                                    case_insensitive=False,
                                    column_to_json_key_mappings={
                                        "column_to_json_key_mappings_key": "columnToJsonKeyMappings"
                                    },
                                    convert_dots_in_json_keys_to_underscores=False
                                )
                            )
                        ),
                        output_format_configuration=OutputFormatConfigurationProperty(
                            serializer=SerializerProperty(
                                orc_ser_de=OrcSerDeProperty(
                                    block_size_bytes=123,
                                    bloom_filter_columns=["bloomFilterColumns"],
                                    bloom_filter_false_positive_probability=123,
                                    compression="compression",
                                    dictionary_key_threshold=123,
                                    enable_padding=False,
                                    format_version="formatVersion",
                                    padding_tolerance=123,
                                    row_index_stride=123,
                                    stripe_size_bytes=123
                                ),
                                parquet_ser_de=ParquetSerDeProperty(
                                    block_size_bytes=123,
                                    compression="compression",
                                    enable_dictionary_compression=False,
                                    max_padding_bytes=123,
                                    page_size_bytes=123,
                                    writer_version="writerVersion"
                                )
                            )
                        ),
                        schema_configuration=SchemaConfigurationProperty(
                            catalog_id="catalogId",
                            database_name="databaseName",
                            region="region",
                            role_arn="roleArn",
                            table_name="tableName",
                            version_id="versionId"
                        )
                    ),
                    dynamic_partitioning_configuration=DynamicPartitioningConfigurationProperty(
                        enabled=False,
                        retry_options=RetryOptionsProperty(
                            duration_in_seconds=123
                        )
                    ),
                    encryption_configuration=EncryptionConfigurationProperty(
                        kms_encryption_config=KMSEncryptionConfigProperty(
                            awskms_key_arn="awskmsKeyArn"
                        ),
                        no_encryption_config="noEncryptionConfig"
                    ),
                    error_output_prefix="errorOutputPrefix",
                    prefix="prefix",
                    processing_configuration=ProcessingConfigurationProperty(
                        enabled=False,
                        processors=[ProcessorProperty(
                            type="type",
            
                            # the properties below are optional
                            parameters=[ProcessorParameterProperty(
                                parameter_name="parameterName",
                                parameter_value="parameterValue"
                            )]
                        )]
                    ),
                    s3_backup_configuration=S3DestinationConfigurationProperty(
                        bucket_arn="bucketArn",
                        role_arn="roleArn",
            
                        # the properties below are optional
                        buffering_hints=BufferingHintsProperty(
                            interval_in_seconds=123,
                            size_in_mBs=123
                        ),
                        cloud_watch_logging_options=CloudWatchLoggingOptionsProperty(
                            enabled=False,
                            log_group_name="logGroupName",
                            log_stream_name="logStreamName"
                        ),
                        compression_format="compressionFormat",
                        encryption_configuration=EncryptionConfigurationProperty(
                            kms_encryption_config=KMSEncryptionConfigProperty(
                                awskms_key_arn="awskmsKeyArn"
                            ),
                            no_encryption_config="noEncryptionConfig"
                        ),
                        error_output_prefix="errorOutputPrefix",
                        prefix="prefix"
                    ),
                    s3_backup_mode="s3BackupMode"
                )
            )
        '''
        if isinstance(extended_s3_destination_configuration, dict):
            extended_s3_destination_configuration = aws_cdk.aws_kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(**extended_s3_destination_configuration)
        self._values: typing.Dict[str, typing.Any] = {}
        if dependables is not None:
            self._values["dependables"] = dependables
        if extended_s3_destination_configuration is not None:
            self._values["extended_s3_destination_configuration"] = extended_s3_destination_configuration

    @builtins.property
    def dependables(self) -> typing.Optional[typing.List[constructs.IDependable]]:
        '''(experimental) Any resources that were created by the destination when binding it to the stack that must be deployed before the delivery stream is deployed.

        :default: []

        :stability: experimental
        '''
        result = self._values.get("dependables")
        return typing.cast(typing.Optional[typing.List[constructs.IDependable]], result)

    @builtins.property
    def extended_s3_destination_configuration(
        self,
    ) -> typing.Optional[aws_cdk.aws_kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty]:
        '''(experimental) S3 destination configuration properties.

        :default: - S3 destination is not used.

        :stability: experimental
        '''
        result = self._values.get("extended_s3_destination_configuration")
        return typing.cast(typing.Optional[aws_cdk.aws_kinesisfirehose.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.IDataProcessor")
class IDataProcessor(typing_extensions.Protocol):
    '''(experimental) A data processor that Kinesis Data Firehose will call to transform records before delivering data.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> DataProcessorProps:
        '''(experimental) The constructor props of the DataProcessor.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        *,
        role: aws_cdk.aws_iam.IRole,
    ) -> DataProcessorConfig:
        '''(experimental) Binds this processor to a destination of a delivery stream.

        Implementers should use this method to grant processor invocation permissions to the provided stream and return the
        necessary configuration to register as a processor.

        :param scope: -
        :param role: (experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        '''
        ...


class _IDataProcessorProxy:
    '''(experimental) A data processor that Kinesis Data Firehose will call to transform records before delivering data.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-kinesisfirehose-alpha.IDataProcessor"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> DataProcessorProps:
        '''(experimental) The constructor props of the DataProcessor.

        :stability: experimental
        '''
        return typing.cast(DataProcessorProps, jsii.get(self, "props"))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        *,
        role: aws_cdk.aws_iam.IRole,
    ) -> DataProcessorConfig:
        '''(experimental) Binds this processor to a destination of a delivery stream.

        Implementers should use this method to grant processor invocation permissions to the provided stream and return the
        necessary configuration to register as a processor.

        :param scope: -
        :param role: (experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        '''
        options = DataProcessorBindOptions(role=role)

        return typing.cast(DataProcessorConfig, jsii.invoke(self, "bind", [scope, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDataProcessor).__jsii_proxy_class__ = lambda : _IDataProcessorProxy


@jsii.interface(jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.IDeliveryStream")
class IDeliveryStream(
    aws_cdk.IResource,
    aws_cdk.aws_iam.IGrantable,
    aws_cdk.aws_ec2.IConnectable,
    typing_extensions.Protocol,
):
    '''(experimental) Represents a Kinesis Data Firehose delivery stream.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        '''(experimental) The ARN of the delivery stream.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        '''(experimental) The name of the delivery stream.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        *actions: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantPutRecords")
    def grant_put_records(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``firehose:PutRecord`` and ``firehose:PutRecordBatch`` actions on this delivery stream.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Return the given named metric for this delivery stream.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of bytes delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the age (from getting into Kinesis Data Firehose to now) of the oldest record in Kinesis Data Firehose.

        Any record older than this age has been delivered to the Amazon S3 bucket for backup.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of records delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of bytes ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of records ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        ...


class _IDeliveryStreamProxy(
    jsii.proxy_for(aws_cdk.IResource), # type: ignore[misc]
    jsii.proxy_for(aws_cdk.aws_iam.IGrantable), # type: ignore[misc]
    jsii.proxy_for(aws_cdk.aws_ec2.IConnectable), # type: ignore[misc]
):
    '''(experimental) Represents a Kinesis Data Firehose delivery stream.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-kinesisfirehose-alpha.IDeliveryStream"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        '''(experimental) The ARN of the delivery stream.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        '''(experimental) The name of the delivery stream.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamName"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        *actions: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantPutRecords")
    def grant_put_records(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``firehose:PutRecord`` and ``firehose:PutRecordBatch`` actions on this delivery stream.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantPutRecords", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Return the given named metric for this delivery stream.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of bytes delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3Bytes", [props]))

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the age (from getting into Kinesis Data Firehose to now) of the oldest record in Kinesis Data Firehose.

        Any record older than this age has been delivered to the Amazon S3 bucket for backup.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3DataFreshness", [props]))

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of records delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3Records", [props]))

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of bytes ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricIncomingBytes", [props]))

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of records ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricIncomingRecords", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDeliveryStream).__jsii_proxy_class__ = lambda : _IDeliveryStreamProxy


@jsii.interface(jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.IDestination")
class IDestination(typing_extensions.Protocol):
    '''(experimental) A Kinesis Data Firehose delivery stream destination.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(self, scope: constructs.Construct) -> DestinationConfig:
        '''(experimental) Binds this destination to the Kinesis Data Firehose delivery stream.

        Implementers should use this method to bind resources to the stack and initialize values using the provided stream.

        :param scope: -

        :stability: experimental
        '''
        ...


class _IDestinationProxy:
    '''(experimental) A Kinesis Data Firehose delivery stream destination.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-kinesisfirehose-alpha.IDestination"

    @jsii.member(jsii_name="bind")
    def bind(self, scope: constructs.Construct) -> DestinationConfig:
        '''(experimental) Binds this destination to the Kinesis Data Firehose delivery stream.

        Implementers should use this method to bind resources to the stack and initialize values using the provided stream.

        :param scope: -

        :stability: experimental
        '''
        options = DestinationBindOptions()

        return typing.cast(DestinationConfig, jsii.invoke(self, "bind", [scope, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDestination).__jsii_proxy_class__ = lambda : _IDestinationProxy


@jsii.implements(IDataProcessor)
class LambdaFunctionProcessor(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.LambdaFunctionProcessor",
):
    '''(experimental) Use an AWS Lambda function to transform records.

    :stability: experimental
    :exampleMetadata: lit=../aws-kinesisfirehose-destinations/test/integ.s3-bucket.lit.ts infused

    Example::

        import path as path
        import aws_cdk.aws_kinesisfirehose_alpha as firehose
        import aws_cdk.aws_kms as kms
        import aws_cdk.aws_lambda_nodejs as lambdanodejs
        import aws_cdk.aws_logs as logs
        import aws_cdk.aws_s3 as s3
        import aws_cdk as cdk
        import aws_cdk.aws_kinesisfirehose_destinations_alpha as destinations
        
        app = cdk.App()
        
        stack = cdk.Stack(app, "aws-cdk-firehose-delivery-stream-s3-all-properties")
        
        bucket = s3.Bucket(stack, "Bucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        backup_bucket = s3.Bucket(stack, "BackupBucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        log_group = logs.LogGroup(stack, "LogGroup",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        data_processor_function = lambdanodejs.NodejsFunction(stack, "DataProcessorFunction",
            entry=path.join(__dirname, "lambda-data-processor.js"),
            timeout=cdk.Duration.minutes(1)
        )
        
        processor = firehose.LambdaFunctionProcessor(data_processor_function,
            buffer_interval=cdk.Duration.seconds(60),
            buffer_size=cdk.Size.mebibytes(1),
            retries=1
        )
        
        key = kms.Key(stack, "Key",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        backup_key = kms.Key(stack, "BackupKey",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        firehose.DeliveryStream(stack, "Delivery Stream",
            destinations=[destinations.S3Bucket(bucket,
                logging=True,
                log_group=log_group,
                processor=processor,
                compression=destinations.Compression.GZIP,
                data_output_prefix="regularPrefix",
                error_output_prefix="errorPrefix",
                buffering_interval=cdk.Duration.seconds(60),
                buffering_size=cdk.Size.mebibytes(1),
                encryption_key=key,
                s3_backup=destinations.DestinationS3BackupProps(
                    mode=destinations.BackupMode.ALL,
                    bucket=backup_bucket,
                    compression=destinations.Compression.ZIP,
                    data_output_prefix="backupPrefix",
                    error_output_prefix="backupErrorPrefix",
                    buffering_interval=cdk.Duration.seconds(60),
                    buffering_size=cdk.Size.mebibytes(1),
                    encryption_key=backup_key
                )
            )]
        )
        
        app.synth()
    '''

    def __init__(
        self,
        lambda_function: aws_cdk.aws_lambda.IFunction,
        *,
        buffer_interval: typing.Optional[aws_cdk.Duration] = None,
        buffer_size: typing.Optional[aws_cdk.Size] = None,
        retries: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param lambda_function: -
        :param buffer_interval: (experimental) The length of time Kinesis Data Firehose will buffer incoming data before calling the processor. s Default: Duration.minutes(1)
        :param buffer_size: (experimental) The amount of incoming data Kinesis Data Firehose will buffer before calling the processor. Default: Size.mebibytes(3)
        :param retries: (experimental) The number of times Kinesis Data Firehose will retry the processor invocation after a failure due to network timeout or invocation limits. Default: 3

        :stability: experimental
        '''
        props = DataProcessorProps(
            buffer_interval=buffer_interval, buffer_size=buffer_size, retries=retries
        )

        jsii.create(self.__class__, self, [lambda_function, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _scope: constructs.Construct,
        *,
        role: aws_cdk.aws_iam.IRole,
    ) -> DataProcessorConfig:
        '''(experimental) Binds this processor to a destination of a delivery stream.

        Implementers should use this method to grant processor invocation permissions to the provided stream and return the
        necessary configuration to register as a processor.

        :param _scope: -
        :param role: (experimental) The IAM role assumed by Kinesis Data Firehose to write to the destination that this DataProcessor will bind to.

        :stability: experimental
        '''
        options = DataProcessorBindOptions(role=role)

        return typing.cast(DataProcessorConfig, jsii.invoke(self, "bind", [_scope, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> DataProcessorProps:
        '''(experimental) The constructor props of the LambdaFunctionProcessor.

        :stability: experimental
        '''
        return typing.cast(DataProcessorProps, jsii.get(self, "props"))


@jsii.enum(jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.StreamEncryption")
class StreamEncryption(enum.Enum):
    '''(experimental) Options for server-side encryption of a delivery stream.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # destination: firehose.IDestination
        # SSE with an customer-managed CMK that is explicitly specified
        # key: kms.Key
        
        
        # SSE with an AWS-owned CMK
        firehose.DeliveryStream(self, "Delivery Stream AWS Owned",
            encryption=firehose.StreamEncryption.AWS_OWNED,
            destinations=[destination]
        )
        # SSE with an customer-managed CMK that is created automatically by the CDK
        firehose.DeliveryStream(self, "Delivery Stream Implicit Customer Managed",
            encryption=firehose.StreamEncryption.CUSTOMER_MANAGED,
            destinations=[destination]
        )
        firehose.DeliveryStream(self, "Delivery Stream Explicit Customer Managed",
            encryption_key=key,
            destinations=[destination]
        )
    '''

    UNENCRYPTED = "UNENCRYPTED"
    '''(experimental) Data in the stream is stored unencrypted.

    :stability: experimental
    '''
    CUSTOMER_MANAGED = "CUSTOMER_MANAGED"
    '''(experimental) Data in the stream is stored encrypted by a KMS key managed by the customer.

    :stability: experimental
    '''
    AWS_OWNED = "AWS_OWNED"
    '''(experimental) Data in the stream is stored encrypted by a KMS key owned by AWS and managed for use in multiple AWS accounts.

    :stability: experimental
    '''


@jsii.implements(IDeliveryStream)
class DeliveryStream(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-kinesisfirehose-alpha.DeliveryStream",
):
    '''(experimental) Create a Kinesis Data Firehose delivery stream.

    :stability: experimental
    :exampleMetadata: infused
    :resource: AWS::KinesisFirehose::DeliveryStream

    Example::

        # bucket: s3.Bucket
        # Provide a Lambda function that will transform records before delivery, with custom
        # buffering and retry configuration
        lambda_function = lambda_.Function(self, "Processor",
            runtime=lambda_.Runtime.NODEJS_12_X,
            handler="index.handler",
            code=lambda_.Code.from_asset(path.join(__dirname, "process-records"))
        )
        lambda_processor = firehose.LambdaFunctionProcessor(lambda_function,
            buffer_interval=Duration.minutes(5),
            buffer_size=Size.mebibytes(5),
            retries=5
        )
        s3_destination = destinations.S3Bucket(bucket,
            processor=lambda_processor
        )
        firehose.DeliveryStream(self, "Delivery Stream",
            destinations=[s3_destination]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        destinations: typing.Sequence[IDestination],
        delivery_stream_name: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[StreamEncryption] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        source_stream: typing.Optional[aws_cdk.aws_kinesis.IStream] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param destinations: (experimental) The destinations that this delivery stream will deliver data to. Only a singleton array is supported at this time.
        :param delivery_stream_name: (experimental) A name for the delivery stream. Default: - a name is generated by CloudFormation.
        :param encryption: (experimental) Indicates the type of customer master key (CMK) to use for server-side encryption, if any. Default: StreamEncryption.UNENCRYPTED - unless ``encryptionKey`` is provided, in which case this will be implicitly set to ``StreamEncryption.CUSTOMER_MANAGED``
        :param encryption_key: (experimental) Customer managed key to server-side encrypt data in the stream. Default: - no KMS key will be used; if ``encryption`` is set to ``CUSTOMER_MANAGED``, a KMS key will be created for you
        :param role: (experimental) The IAM role associated with this delivery stream. Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side. Default: - a role will be created with default permissions.
        :param source_stream: (experimental) The Kinesis data stream to use as a source for this delivery stream. Default: - data must be written to the delivery stream via a direct put.

        :stability: experimental
        '''
        props = DeliveryStreamProps(
            destinations=destinations,
            delivery_stream_name=delivery_stream_name,
            encryption=encryption,
            encryption_key=encryption_key,
            role=role,
            source_stream=source_stream,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromDeliveryStreamArn") # type: ignore[misc]
    @builtins.classmethod
    def from_delivery_stream_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        delivery_stream_arn: builtins.str,
    ) -> IDeliveryStream:
        '''(experimental) Import an existing delivery stream from its ARN.

        :param scope: -
        :param id: -
        :param delivery_stream_arn: -

        :stability: experimental
        '''
        return typing.cast(IDeliveryStream, jsii.sinvoke(cls, "fromDeliveryStreamArn", [scope, id, delivery_stream_arn]))

    @jsii.member(jsii_name="fromDeliveryStreamAttributes") # type: ignore[misc]
    @builtins.classmethod
    def from_delivery_stream_attributes(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        delivery_stream_arn: typing.Optional[builtins.str] = None,
        delivery_stream_name: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> IDeliveryStream:
        '''(experimental) Import an existing delivery stream from its attributes.

        :param scope: -
        :param id: -
        :param delivery_stream_arn: (experimental) The ARN of the delivery stream. At least one of deliveryStreamArn and deliveryStreamName must be provided. Default: - derived from ``deliveryStreamName``.
        :param delivery_stream_name: (experimental) The name of the delivery stream. At least one of deliveryStreamName and deliveryStreamArn must be provided. Default: - derived from ``deliveryStreamArn``.
        :param role: (experimental) The IAM role associated with this delivery stream. Assumed by Kinesis Data Firehose to read from sources and encrypt data server-side. Default: - the imported stream cannot be granted access to other resources as an ``iam.IGrantable``.

        :stability: experimental
        '''
        attrs = DeliveryStreamAttributes(
            delivery_stream_arn=delivery_stream_arn,
            delivery_stream_name=delivery_stream_name,
            role=role,
        )

        return typing.cast(IDeliveryStream, jsii.sinvoke(cls, "fromDeliveryStreamAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="fromDeliveryStreamName") # type: ignore[misc]
    @builtins.classmethod
    def from_delivery_stream_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        delivery_stream_name: builtins.str,
    ) -> IDeliveryStream:
        '''(experimental) Import an existing delivery stream from its name.

        :param scope: -
        :param id: -
        :param delivery_stream_name: -

        :stability: experimental
        '''
        return typing.cast(IDeliveryStream, jsii.sinvoke(cls, "fromDeliveryStreamName", [scope, id, delivery_stream_name]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        *actions: builtins.str,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``actions``.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantPutRecords")
    def grant_put_records(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grant the ``grantee`` identity permissions to perform ``firehose:PutRecord`` and ``firehose:PutRecordBatch`` actions on this delivery stream.

        :param grantee: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantPutRecords", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Return the given named metric for this delivery stream.

        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metric", [metric_name, props]))

    @jsii.member(jsii_name="metricBackupToS3Bytes")
    def metric_backup_to_s3_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of bytes delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3Bytes", [props]))

    @jsii.member(jsii_name="metricBackupToS3DataFreshness")
    def metric_backup_to_s3_data_freshness(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the age (from getting into Kinesis Data Firehose to now) of the oldest record in Kinesis Data Firehose.

        Any record older than this age has been delivered to the Amazon S3 bucket for backup.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3DataFreshness", [props]))

    @jsii.member(jsii_name="metricBackupToS3Records")
    def metric_backup_to_s3_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of records delivered to Amazon S3 for backup over the specified time period.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricBackupToS3Records", [props]))

    @jsii.member(jsii_name="metricIncomingBytes")
    def metric_incoming_bytes(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of bytes ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricIncomingBytes", [props]))

    @jsii.member(jsii_name="metricIncomingRecords")
    def metric_incoming_records(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[aws_cdk.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[aws_cdk.aws_cloudwatch.Unit] = None,
    ) -> aws_cdk.aws_cloudwatch.Metric:
        '''(experimental) Metric for the number of records ingested successfully into the delivery stream over the specified time period after throttling.

        By default, this metric will be calculated as an average over a period of 5 minutes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param label: Label for this metric when added to a Graph in a Dashboard. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream

        :stability: experimental
        '''
        props = aws_cdk.aws_cloudwatch.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            label=label,
            period=period,
            region=region,
            statistic=statistic,
            unit=unit,
        )

        return typing.cast(aws_cdk.aws_cloudwatch.Metric, jsii.invoke(self, "metricIncomingRecords", [props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''(experimental) Network connections between Kinesis Data Firehose and other resources, i.e. Redshift cluster.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamArn")
    def delivery_stream_arn(self) -> builtins.str:
        '''(experimental) The ARN of the delivery stream.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryStreamName")
    def delivery_stream_name(self) -> builtins.str:
        '''(experimental) The name of the delivery stream.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "deliveryStreamName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))


__all__ = [
    "DataProcessorBindOptions",
    "DataProcessorConfig",
    "DataProcessorIdentifier",
    "DataProcessorProps",
    "DeliveryStream",
    "DeliveryStreamAttributes",
    "DeliveryStreamProps",
    "DestinationBindOptions",
    "DestinationConfig",
    "IDataProcessor",
    "IDeliveryStream",
    "IDestination",
    "LambdaFunctionProcessor",
    "StreamEncryption",
]

publication.publish()
