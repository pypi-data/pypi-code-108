'''
# Amazon Kinesis Data Firehose Destinations Library

This library provides constructs for adding destinations to a Amazon Kinesis Data Firehose
delivery stream. Destinations can be added by specifying the `destinations` prop when
defining a delivery stream.

See [Amazon Kinesis Data Firehose module README](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-kinesisfirehose-readme.html) for usage examples.

```python
import monocdk as destinations
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
from .. import Duration as _Duration_070aa057, Size as _Size_7fbd4337
from ..aws_iam import IRole as _IRole_59af6f50
from ..aws_kinesisfirehose import (
    DestinationBindOptions as _DestinationBindOptions_b23afe8e,
    DestinationConfig as _DestinationConfig_9a0983fa,
    IDataProcessor as _IDataProcessor_682cbcf2,
    IDestination as _IDestination_31219c56,
)
from ..aws_kms import IKey as _IKey_36930160
from ..aws_logs import ILogGroup as _ILogGroup_846e17a0
from ..aws_s3 import IBucket as _IBucket_73486e29


@jsii.enum(jsii_type="monocdk.aws_kinesisfirehose_destinations.BackupMode")
class BackupMode(enum.Enum):
    '''(experimental) Options for S3 record backup of a delivery stream.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Enable backup of all source records (to an S3 bucket created by CDK).
        # bucket: s3.Bucket
        # Explicitly provide an S3 bucket to which all source records will be backed up.
        # backup_bucket: s3.Bucket
        
        firehose.DeliveryStream(self, "Delivery Stream Backup All",
            destinations=[
                destinations.S3Bucket(bucket,
                    s3_backup=firehose.aws_kinesisfirehose_destinations.DestinationS3BackupProps(
                        mode=destinations.BackupMode.ALL
                    )
                )
            ]
        )
        firehose.DeliveryStream(self, "Delivery Stream Backup All Explicit Bucket",
            destinations=[
                destinations.S3Bucket(bucket,
                    s3_backup=firehose.aws_kinesisfirehose_destinations.DestinationS3BackupProps(
                        bucket=backup_bucket
                    )
                )
            ]
        )
        # Explicitly provide an S3 prefix under which all source records will be backed up.
        firehose.DeliveryStream(self, "Delivery Stream Backup All Explicit Prefix",
            destinations=[
                destinations.S3Bucket(bucket,
                    s3_backup=firehose.aws_kinesisfirehose_destinations.DestinationS3BackupProps(
                        mode=destinations.BackupMode.ALL,
                        data_output_prefix="mybackup"
                    )
                )
            ]
        )
    '''

    ALL = "ALL"
    '''(experimental) All records are backed up.

    :stability: experimental
    '''
    FAILED = "FAILED"
    '''(experimental) Only records that failed to deliver or transform are backed up.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="monocdk.aws_kinesisfirehose_destinations.CommonDestinationProps",
    jsii_struct_bases=[],
    name_mapping={
        "logging": "logging",
        "log_group": "logGroup",
        "processor": "processor",
        "role": "role",
        "s3_backup": "s3Backup",
    },
)
class CommonDestinationProps:
    def __init__(
        self,
        *,
        logging: typing.Optional[builtins.bool] = None,
        log_group: typing.Optional[_ILogGroup_846e17a0] = None,
        processor: typing.Optional[_IDataProcessor_682cbcf2] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        s3_backup: typing.Optional["DestinationS3BackupProps"] = None,
    ) -> None:
        '''(experimental) Generic properties for defining a delivery stream destination.

        :param logging: (experimental) If true, log errors when data transformation or data delivery fails. If ``logGroup`` is provided, this will be implicitly set to ``true``. Default: true - errors are logged.
        :param log_group: (experimental) The CloudWatch log group where log streams will be created to hold error logs. Default: - if ``logging`` is set to ``true``, a log group will be created for you.
        :param processor: (experimental) The data transformation that should be performed on the data before writing to the destination. Default: - no data transformation will occur.
        :param role: (experimental) The IAM role associated with this destination. Assumed by Kinesis Data Firehose to invoke processors and write to destinations Default: - a role will be created with default permissions.
        :param s3_backup: (experimental) The configuration for backing up source records to S3. Default: - source records will not be backed up to S3.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import monocdk as monocdk
            from monocdk import aws_iam as iam
            from monocdk import aws_kinesisfirehose as kinesisfirehose
            from monocdk import aws_kinesisfirehose_destinations as kinesisfirehose_destinations
            from monocdk import aws_kms as kms
            from monocdk import aws_logs as logs
            from monocdk import aws_s3 as s3
            
            # bucket: s3.Bucket
            # compression: kinesisfirehose_destinations.Compression
            # data_processor: kinesisfirehose.IDataProcessor
            # duration: monocdk.Duration
            # key: kms.Key
            # log_group: logs.LogGroup
            # role: iam.Role
            # size: monocdk.Size
            
            common_destination_props = kinesisfirehose_destinations.CommonDestinationProps(
                logging=False,
                log_group=log_group,
                processor=data_processor,
                role=role,
                s3_backup=kinesisfirehose_destinations.DestinationS3BackupProps(
                    bucket=bucket,
                    buffering_interval=duration,
                    buffering_size=size,
                    compression=compression,
                    data_output_prefix="dataOutputPrefix",
                    encryption_key=key,
                    error_output_prefix="errorOutputPrefix",
                    logging=False,
                    log_group=log_group,
                    mode=kinesisfirehose_destinations.BackupMode.ALL
                )
            )
        '''
        if isinstance(s3_backup, dict):
            s3_backup = DestinationS3BackupProps(**s3_backup)
        self._values: typing.Dict[str, typing.Any] = {}
        if logging is not None:
            self._values["logging"] = logging
        if log_group is not None:
            self._values["log_group"] = log_group
        if processor is not None:
            self._values["processor"] = processor
        if role is not None:
            self._values["role"] = role
        if s3_backup is not None:
            self._values["s3_backup"] = s3_backup

    @builtins.property
    def logging(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If true, log errors when data transformation or data delivery fails.

        If ``logGroup`` is provided, this will be implicitly set to ``true``.

        :default: true - errors are logged.

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_ILogGroup_846e17a0]:
        '''(experimental) The CloudWatch log group where log streams will be created to hold error logs.

        :default: - if ``logging`` is set to ``true``, a log group will be created for you.

        :stability: experimental
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_ILogGroup_846e17a0], result)

    @builtins.property
    def processor(self) -> typing.Optional[_IDataProcessor_682cbcf2]:
        '''(experimental) The data transformation that should be performed on the data before writing to the destination.

        :default: - no data transformation will occur.

        :stability: experimental
        '''
        result = self._values.get("processor")
        return typing.cast(typing.Optional[_IDataProcessor_682cbcf2], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The IAM role associated with this destination.

        Assumed by Kinesis Data Firehose to invoke processors and write to destinations

        :default: - a role will be created with default permissions.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def s3_backup(self) -> typing.Optional["DestinationS3BackupProps"]:
        '''(experimental) The configuration for backing up source records to S3.

        :default: - source records will not be backed up to S3.

        :stability: experimental
        '''
        result = self._values.get("s3_backup")
        return typing.cast(typing.Optional["DestinationS3BackupProps"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonDestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_kinesisfirehose_destinations.CommonDestinationS3Props",
    jsii_struct_bases=[],
    name_mapping={
        "buffering_interval": "bufferingInterval",
        "buffering_size": "bufferingSize",
        "compression": "compression",
        "data_output_prefix": "dataOutputPrefix",
        "encryption_key": "encryptionKey",
        "error_output_prefix": "errorOutputPrefix",
    },
)
class CommonDestinationS3Props:
    def __init__(
        self,
        *,
        buffering_interval: typing.Optional[_Duration_070aa057] = None,
        buffering_size: typing.Optional[_Size_7fbd4337] = None,
        compression: typing.Optional["Compression"] = None,
        data_output_prefix: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        error_output_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Common properties for defining a backup, intermediary, or final S3 destination for a Kinesis Data Firehose delivery stream.

        :param buffering_interval: (experimental) The length of time that Firehose buffers incoming data before delivering it to the S3 bucket. Minimum: Duration.seconds(60) Maximum: Duration.seconds(900) Default: Duration.seconds(300)
        :param buffering_size: (experimental) The size of the buffer that Kinesis Data Firehose uses for incoming data before delivering it to the S3 bucket. Minimum: Size.mebibytes(1) Maximum: Size.mebibytes(128) Default: Size.mebibytes(5)
        :param compression: (experimental) The type of compression that Kinesis Data Firehose uses to compress the data that it delivers to the Amazon S3 bucket. The compression formats SNAPPY or ZIP cannot be specified for Amazon Redshift destinations because they are not supported by the Amazon Redshift COPY operation that reads from the S3 bucket. Default: - UNCOMPRESSED
        :param data_output_prefix: (experimental) A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3. This prefix appears immediately following the bucket name. Default: "YYYY/MM/DD/HH"
        :param encryption_key: (experimental) The AWS KMS key used to encrypt the data that it delivers to your Amazon S3 bucket. Default: - Data is not encrypted.
        :param error_output_prefix: (experimental) A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3. This prefix appears immediately following the bucket name. Default: "YYYY/MM/DD/HH"

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import monocdk as monocdk
            from monocdk import aws_kinesisfirehose_destinations as kinesisfirehose_destinations
            from monocdk import aws_kms as kms
            
            # compression: kinesisfirehose_destinations.Compression
            # duration: monocdk.Duration
            # key: kms.Key
            # size: monocdk.Size
            
            common_destination_s3_props = kinesisfirehose_destinations.CommonDestinationS3Props(
                buffering_interval=duration,
                buffering_size=size,
                compression=compression,
                data_output_prefix="dataOutputPrefix",
                encryption_key=key,
                error_output_prefix="errorOutputPrefix"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if buffering_interval is not None:
            self._values["buffering_interval"] = buffering_interval
        if buffering_size is not None:
            self._values["buffering_size"] = buffering_size
        if compression is not None:
            self._values["compression"] = compression
        if data_output_prefix is not None:
            self._values["data_output_prefix"] = data_output_prefix
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if error_output_prefix is not None:
            self._values["error_output_prefix"] = error_output_prefix

    @builtins.property
    def buffering_interval(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) The length of time that Firehose buffers incoming data before delivering it to the S3 bucket.

        Minimum: Duration.seconds(60)
        Maximum: Duration.seconds(900)

        :default: Duration.seconds(300)

        :stability: experimental
        '''
        result = self._values.get("buffering_interval")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def buffering_size(self) -> typing.Optional[_Size_7fbd4337]:
        '''(experimental) The size of the buffer that Kinesis Data Firehose uses for incoming data before delivering it to the S3 bucket.

        Minimum: Size.mebibytes(1)
        Maximum: Size.mebibytes(128)

        :default: Size.mebibytes(5)

        :stability: experimental
        '''
        result = self._values.get("buffering_size")
        return typing.cast(typing.Optional[_Size_7fbd4337], result)

    @builtins.property
    def compression(self) -> typing.Optional["Compression"]:
        '''(experimental) The type of compression that Kinesis Data Firehose uses to compress the data that it delivers to the Amazon S3 bucket.

        The compression formats SNAPPY or ZIP cannot be specified for Amazon Redshift
        destinations because they are not supported by the Amazon Redshift COPY operation
        that reads from the S3 bucket.

        :default: - UNCOMPRESSED

        :stability: experimental
        '''
        result = self._values.get("compression")
        return typing.cast(typing.Optional["Compression"], result)

    @builtins.property
    def data_output_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3.

        This prefix appears immediately following the bucket name.

        :default: "YYYY/MM/DD/HH"

        :see: https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html
        :stability: experimental
        '''
        result = self._values.get("data_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The AWS KMS key used to encrypt the data that it delivers to your Amazon S3 bucket.

        :default: - Data is not encrypted.

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def error_output_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3.

        This prefix appears immediately following the bucket name.

        :default: "YYYY/MM/DD/HH"

        :see: https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html
        :stability: experimental
        '''
        result = self._values.get("error_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonDestinationS3Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Compression(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_kinesisfirehose_destinations.Compression",
):
    '''(experimental) Possible compression options Kinesis Data Firehose can use to compress data on delivery.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Compress data delivered to S3 using Snappy
        # bucket: s3.Bucket
        
        s3_destination = destinations.S3Bucket(bucket,
            compression=destinations.Compression.SNAPPY
        )
        firehose.DeliveryStream(self, "Delivery Stream",
            destinations=[s3_destination]
        )
    '''

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, value: builtins.str) -> "Compression":
        '''(experimental) Creates a new Compression instance with a custom value.

        :param value: -

        :stability: experimental
        '''
        return typing.cast("Compression", jsii.sinvoke(cls, "of", [value]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GZIP")
    def GZIP(cls) -> "Compression":
        '''(experimental) gzip.

        :stability: experimental
        '''
        return typing.cast("Compression", jsii.sget(cls, "GZIP"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="HADOOP_SNAPPY")
    def HADOOP_SNAPPY(cls) -> "Compression":
        '''(experimental) Hadoop-compatible Snappy.

        :stability: experimental
        '''
        return typing.cast("Compression", jsii.sget(cls, "HADOOP_SNAPPY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SNAPPY")
    def SNAPPY(cls) -> "Compression":
        '''(experimental) Snappy.

        :stability: experimental
        '''
        return typing.cast("Compression", jsii.sget(cls, "SNAPPY"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="ZIP")
    def ZIP(cls) -> "Compression":
        '''(experimental) ZIP.

        :stability: experimental
        '''
        return typing.cast("Compression", jsii.sget(cls, "ZIP"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        '''(experimental) the string value of the Compression.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "value"))


@jsii.data_type(
    jsii_type="monocdk.aws_kinesisfirehose_destinations.DestinationS3BackupProps",
    jsii_struct_bases=[CommonDestinationS3Props],
    name_mapping={
        "buffering_interval": "bufferingInterval",
        "buffering_size": "bufferingSize",
        "compression": "compression",
        "data_output_prefix": "dataOutputPrefix",
        "encryption_key": "encryptionKey",
        "error_output_prefix": "errorOutputPrefix",
        "bucket": "bucket",
        "logging": "logging",
        "log_group": "logGroup",
        "mode": "mode",
    },
)
class DestinationS3BackupProps(CommonDestinationS3Props):
    def __init__(
        self,
        *,
        buffering_interval: typing.Optional[_Duration_070aa057] = None,
        buffering_size: typing.Optional[_Size_7fbd4337] = None,
        compression: typing.Optional[Compression] = None,
        data_output_prefix: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        error_output_prefix: typing.Optional[builtins.str] = None,
        bucket: typing.Optional[_IBucket_73486e29] = None,
        logging: typing.Optional[builtins.bool] = None,
        log_group: typing.Optional[_ILogGroup_846e17a0] = None,
        mode: typing.Optional[BackupMode] = None,
    ) -> None:
        '''(experimental) Properties for defining an S3 backup destination.

        S3 backup is available for all destinations, regardless of whether the final destination is S3 or not.

        :param buffering_interval: (experimental) The length of time that Firehose buffers incoming data before delivering it to the S3 bucket. Minimum: Duration.seconds(60) Maximum: Duration.seconds(900) Default: Duration.seconds(300)
        :param buffering_size: (experimental) The size of the buffer that Kinesis Data Firehose uses for incoming data before delivering it to the S3 bucket. Minimum: Size.mebibytes(1) Maximum: Size.mebibytes(128) Default: Size.mebibytes(5)
        :param compression: (experimental) The type of compression that Kinesis Data Firehose uses to compress the data that it delivers to the Amazon S3 bucket. The compression formats SNAPPY or ZIP cannot be specified for Amazon Redshift destinations because they are not supported by the Amazon Redshift COPY operation that reads from the S3 bucket. Default: - UNCOMPRESSED
        :param data_output_prefix: (experimental) A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3. This prefix appears immediately following the bucket name. Default: "YYYY/MM/DD/HH"
        :param encryption_key: (experimental) The AWS KMS key used to encrypt the data that it delivers to your Amazon S3 bucket. Default: - Data is not encrypted.
        :param error_output_prefix: (experimental) A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3. This prefix appears immediately following the bucket name. Default: "YYYY/MM/DD/HH"
        :param bucket: (experimental) The S3 bucket that will store data and failed records. Default: - If ``mode`` is set to ``BackupMode.ALL`` or ``BackupMode.FAILED``, a bucket will be created for you.
        :param logging: (experimental) If true, log errors when data transformation or data delivery fails. If ``logGroup`` is provided, this will be implicitly set to ``true``. Default: true - errors are logged.
        :param log_group: (experimental) The CloudWatch log group where log streams will be created to hold error logs. Default: - if ``logging`` is set to ``true``, a log group will be created for you.
        :param mode: (experimental) Indicates the mode by which incoming records should be backed up to S3, if any. If ``bucket`` is provided, this will be implicitly set to ``BackupMode.ALL``. Default: - If ``bucket`` is provided, the default will be ``BackupMode.ALL``. Otherwise, source records are not backed up to S3.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Enable backup of all source records (to an S3 bucket created by CDK).
            # bucket: s3.Bucket
            # Explicitly provide an S3 bucket to which all source records will be backed up.
            # backup_bucket: s3.Bucket
            
            firehose.DeliveryStream(self, "Delivery Stream Backup All",
                destinations=[
                    destinations.S3Bucket(bucket,
                        s3_backup=firehose.aws_kinesisfirehose_destinations.DestinationS3BackupProps(
                            mode=destinations.BackupMode.ALL
                        )
                    )
                ]
            )
            firehose.DeliveryStream(self, "Delivery Stream Backup All Explicit Bucket",
                destinations=[
                    destinations.S3Bucket(bucket,
                        s3_backup=firehose.aws_kinesisfirehose_destinations.DestinationS3BackupProps(
                            bucket=backup_bucket
                        )
                    )
                ]
            )
            # Explicitly provide an S3 prefix under which all source records will be backed up.
            firehose.DeliveryStream(self, "Delivery Stream Backup All Explicit Prefix",
                destinations=[
                    destinations.S3Bucket(bucket,
                        s3_backup=firehose.aws_kinesisfirehose_destinations.DestinationS3BackupProps(
                            mode=destinations.BackupMode.ALL,
                            data_output_prefix="mybackup"
                        )
                    )
                ]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if buffering_interval is not None:
            self._values["buffering_interval"] = buffering_interval
        if buffering_size is not None:
            self._values["buffering_size"] = buffering_size
        if compression is not None:
            self._values["compression"] = compression
        if data_output_prefix is not None:
            self._values["data_output_prefix"] = data_output_prefix
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if error_output_prefix is not None:
            self._values["error_output_prefix"] = error_output_prefix
        if bucket is not None:
            self._values["bucket"] = bucket
        if logging is not None:
            self._values["logging"] = logging
        if log_group is not None:
            self._values["log_group"] = log_group
        if mode is not None:
            self._values["mode"] = mode

    @builtins.property
    def buffering_interval(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) The length of time that Firehose buffers incoming data before delivering it to the S3 bucket.

        Minimum: Duration.seconds(60)
        Maximum: Duration.seconds(900)

        :default: Duration.seconds(300)

        :stability: experimental
        '''
        result = self._values.get("buffering_interval")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def buffering_size(self) -> typing.Optional[_Size_7fbd4337]:
        '''(experimental) The size of the buffer that Kinesis Data Firehose uses for incoming data before delivering it to the S3 bucket.

        Minimum: Size.mebibytes(1)
        Maximum: Size.mebibytes(128)

        :default: Size.mebibytes(5)

        :stability: experimental
        '''
        result = self._values.get("buffering_size")
        return typing.cast(typing.Optional[_Size_7fbd4337], result)

    @builtins.property
    def compression(self) -> typing.Optional[Compression]:
        '''(experimental) The type of compression that Kinesis Data Firehose uses to compress the data that it delivers to the Amazon S3 bucket.

        The compression formats SNAPPY or ZIP cannot be specified for Amazon Redshift
        destinations because they are not supported by the Amazon Redshift COPY operation
        that reads from the S3 bucket.

        :default: - UNCOMPRESSED

        :stability: experimental
        '''
        result = self._values.get("compression")
        return typing.cast(typing.Optional[Compression], result)

    @builtins.property
    def data_output_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3.

        This prefix appears immediately following the bucket name.

        :default: "YYYY/MM/DD/HH"

        :see: https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html
        :stability: experimental
        '''
        result = self._values.get("data_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The AWS KMS key used to encrypt the data that it delivers to your Amazon S3 bucket.

        :default: - Data is not encrypted.

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def error_output_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3.

        This prefix appears immediately following the bucket name.

        :default: "YYYY/MM/DD/HH"

        :see: https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html
        :stability: experimental
        '''
        result = self._values.get("error_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket(self) -> typing.Optional[_IBucket_73486e29]:
        '''(experimental) The S3 bucket that will store data and failed records.

        :default: - If ``mode`` is set to ``BackupMode.ALL`` or ``BackupMode.FAILED``, a bucket will be created for you.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[_IBucket_73486e29], result)

    @builtins.property
    def logging(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If true, log errors when data transformation or data delivery fails.

        If ``logGroup`` is provided, this will be implicitly set to ``true``.

        :default: true - errors are logged.

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_ILogGroup_846e17a0]:
        '''(experimental) The CloudWatch log group where log streams will be created to hold error logs.

        :default: - if ``logging`` is set to ``true``, a log group will be created for you.

        :stability: experimental
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_ILogGroup_846e17a0], result)

    @builtins.property
    def mode(self) -> typing.Optional[BackupMode]:
        '''(experimental) Indicates the mode by which incoming records should be backed up to S3, if any.

        If ``bucket`` is provided, this will be implicitly set to ``BackupMode.ALL``.

        :default:

        - If ``bucket`` is provided, the default will be ``BackupMode.ALL``. Otherwise,
        source records are not backed up to S3.

        :stability: experimental
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[BackupMode], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DestinationS3BackupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IDestination_31219c56)
class S3Bucket(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_kinesisfirehose_destinations.S3Bucket",
):
    '''(experimental) An S3 bucket destination for data from a Kinesis Data Firehose delivery stream.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Increase the buffer interval and size to 10 minutes and 8 MiB, respectively
        # bucket: s3.Bucket
        
        destination = destinations.S3Bucket(bucket,
            buffering_interval=Duration.minutes(10),
            buffering_size=Size.mebibytes(8)
        )
        firehose.DeliveryStream(self, "Delivery Stream",
            destinations=[destination]
        )
    '''

    def __init__(
        self,
        bucket: _IBucket_73486e29,
        *,
        buffering_interval: typing.Optional[_Duration_070aa057] = None,
        buffering_size: typing.Optional[_Size_7fbd4337] = None,
        compression: typing.Optional[Compression] = None,
        data_output_prefix: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        error_output_prefix: typing.Optional[builtins.str] = None,
        logging: typing.Optional[builtins.bool] = None,
        log_group: typing.Optional[_ILogGroup_846e17a0] = None,
        processor: typing.Optional[_IDataProcessor_682cbcf2] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        s3_backup: typing.Optional[DestinationS3BackupProps] = None,
    ) -> None:
        '''
        :param bucket: -
        :param buffering_interval: (experimental) The length of time that Firehose buffers incoming data before delivering it to the S3 bucket. Minimum: Duration.seconds(60) Maximum: Duration.seconds(900) Default: Duration.seconds(300)
        :param buffering_size: (experimental) The size of the buffer that Kinesis Data Firehose uses for incoming data before delivering it to the S3 bucket. Minimum: Size.mebibytes(1) Maximum: Size.mebibytes(128) Default: Size.mebibytes(5)
        :param compression: (experimental) The type of compression that Kinesis Data Firehose uses to compress the data that it delivers to the Amazon S3 bucket. The compression formats SNAPPY or ZIP cannot be specified for Amazon Redshift destinations because they are not supported by the Amazon Redshift COPY operation that reads from the S3 bucket. Default: - UNCOMPRESSED
        :param data_output_prefix: (experimental) A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3. This prefix appears immediately following the bucket name. Default: "YYYY/MM/DD/HH"
        :param encryption_key: (experimental) The AWS KMS key used to encrypt the data that it delivers to your Amazon S3 bucket. Default: - Data is not encrypted.
        :param error_output_prefix: (experimental) A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3. This prefix appears immediately following the bucket name. Default: "YYYY/MM/DD/HH"
        :param logging: (experimental) If true, log errors when data transformation or data delivery fails. If ``logGroup`` is provided, this will be implicitly set to ``true``. Default: true - errors are logged.
        :param log_group: (experimental) The CloudWatch log group where log streams will be created to hold error logs. Default: - if ``logging`` is set to ``true``, a log group will be created for you.
        :param processor: (experimental) The data transformation that should be performed on the data before writing to the destination. Default: - no data transformation will occur.
        :param role: (experimental) The IAM role associated with this destination. Assumed by Kinesis Data Firehose to invoke processors and write to destinations Default: - a role will be created with default permissions.
        :param s3_backup: (experimental) The configuration for backing up source records to S3. Default: - source records will not be backed up to S3.

        :stability: experimental
        '''
        props = S3BucketProps(
            buffering_interval=buffering_interval,
            buffering_size=buffering_size,
            compression=compression,
            data_output_prefix=data_output_prefix,
            encryption_key=encryption_key,
            error_output_prefix=error_output_prefix,
            logging=logging,
            log_group=log_group,
            processor=processor,
            role=role,
            s3_backup=s3_backup,
        )

        jsii.create(self.__class__, self, [bucket, props])

    @jsii.member(jsii_name="bind")
    def bind(self, scope: constructs.Construct) -> _DestinationConfig_9a0983fa:
        '''(experimental) Binds this destination to the Kinesis Data Firehose delivery stream.

        Implementers should use this method to bind resources to the stack and initialize values using the provided stream.

        :param scope: -

        :stability: experimental
        '''
        _options = _DestinationBindOptions_b23afe8e()

        return typing.cast(_DestinationConfig_9a0983fa, jsii.invoke(self, "bind", [scope, _options]))


@jsii.data_type(
    jsii_type="monocdk.aws_kinesisfirehose_destinations.S3BucketProps",
    jsii_struct_bases=[CommonDestinationS3Props, CommonDestinationProps],
    name_mapping={
        "buffering_interval": "bufferingInterval",
        "buffering_size": "bufferingSize",
        "compression": "compression",
        "data_output_prefix": "dataOutputPrefix",
        "encryption_key": "encryptionKey",
        "error_output_prefix": "errorOutputPrefix",
        "logging": "logging",
        "log_group": "logGroup",
        "processor": "processor",
        "role": "role",
        "s3_backup": "s3Backup",
    },
)
class S3BucketProps(CommonDestinationS3Props, CommonDestinationProps):
    def __init__(
        self,
        *,
        buffering_interval: typing.Optional[_Duration_070aa057] = None,
        buffering_size: typing.Optional[_Size_7fbd4337] = None,
        compression: typing.Optional[Compression] = None,
        data_output_prefix: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_IKey_36930160] = None,
        error_output_prefix: typing.Optional[builtins.str] = None,
        logging: typing.Optional[builtins.bool] = None,
        log_group: typing.Optional[_ILogGroup_846e17a0] = None,
        processor: typing.Optional[_IDataProcessor_682cbcf2] = None,
        role: typing.Optional[_IRole_59af6f50] = None,
        s3_backup: typing.Optional[DestinationS3BackupProps] = None,
    ) -> None:
        '''(experimental) Props for defining an S3 destination of a Kinesis Data Firehose delivery stream.

        :param buffering_interval: (experimental) The length of time that Firehose buffers incoming data before delivering it to the S3 bucket. Minimum: Duration.seconds(60) Maximum: Duration.seconds(900) Default: Duration.seconds(300)
        :param buffering_size: (experimental) The size of the buffer that Kinesis Data Firehose uses for incoming data before delivering it to the S3 bucket. Minimum: Size.mebibytes(1) Maximum: Size.mebibytes(128) Default: Size.mebibytes(5)
        :param compression: (experimental) The type of compression that Kinesis Data Firehose uses to compress the data that it delivers to the Amazon S3 bucket. The compression formats SNAPPY or ZIP cannot be specified for Amazon Redshift destinations because they are not supported by the Amazon Redshift COPY operation that reads from the S3 bucket. Default: - UNCOMPRESSED
        :param data_output_prefix: (experimental) A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3. This prefix appears immediately following the bucket name. Default: "YYYY/MM/DD/HH"
        :param encryption_key: (experimental) The AWS KMS key used to encrypt the data that it delivers to your Amazon S3 bucket. Default: - Data is not encrypted.
        :param error_output_prefix: (experimental) A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3. This prefix appears immediately following the bucket name. Default: "YYYY/MM/DD/HH"
        :param logging: (experimental) If true, log errors when data transformation or data delivery fails. If ``logGroup`` is provided, this will be implicitly set to ``true``. Default: true - errors are logged.
        :param log_group: (experimental) The CloudWatch log group where log streams will be created to hold error logs. Default: - if ``logging`` is set to ``true``, a log group will be created for you.
        :param processor: (experimental) The data transformation that should be performed on the data before writing to the destination. Default: - no data transformation will occur.
        :param role: (experimental) The IAM role associated with this destination. Assumed by Kinesis Data Firehose to invoke processors and write to destinations Default: - a role will be created with default permissions.
        :param s3_backup: (experimental) The configuration for backing up source records to S3. Default: - source records will not be backed up to S3.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Increase the buffer interval and size to 10 minutes and 8 MiB, respectively
            # bucket: s3.Bucket
            
            destination = destinations.S3Bucket(bucket,
                buffering_interval=Duration.minutes(10),
                buffering_size=Size.mebibytes(8)
            )
            firehose.DeliveryStream(self, "Delivery Stream",
                destinations=[destination]
            )
        '''
        if isinstance(s3_backup, dict):
            s3_backup = DestinationS3BackupProps(**s3_backup)
        self._values: typing.Dict[str, typing.Any] = {}
        if buffering_interval is not None:
            self._values["buffering_interval"] = buffering_interval
        if buffering_size is not None:
            self._values["buffering_size"] = buffering_size
        if compression is not None:
            self._values["compression"] = compression
        if data_output_prefix is not None:
            self._values["data_output_prefix"] = data_output_prefix
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if error_output_prefix is not None:
            self._values["error_output_prefix"] = error_output_prefix
        if logging is not None:
            self._values["logging"] = logging
        if log_group is not None:
            self._values["log_group"] = log_group
        if processor is not None:
            self._values["processor"] = processor
        if role is not None:
            self._values["role"] = role
        if s3_backup is not None:
            self._values["s3_backup"] = s3_backup

    @builtins.property
    def buffering_interval(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) The length of time that Firehose buffers incoming data before delivering it to the S3 bucket.

        Minimum: Duration.seconds(60)
        Maximum: Duration.seconds(900)

        :default: Duration.seconds(300)

        :stability: experimental
        '''
        result = self._values.get("buffering_interval")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def buffering_size(self) -> typing.Optional[_Size_7fbd4337]:
        '''(experimental) The size of the buffer that Kinesis Data Firehose uses for incoming data before delivering it to the S3 bucket.

        Minimum: Size.mebibytes(1)
        Maximum: Size.mebibytes(128)

        :default: Size.mebibytes(5)

        :stability: experimental
        '''
        result = self._values.get("buffering_size")
        return typing.cast(typing.Optional[_Size_7fbd4337], result)

    @builtins.property
    def compression(self) -> typing.Optional[Compression]:
        '''(experimental) The type of compression that Kinesis Data Firehose uses to compress the data that it delivers to the Amazon S3 bucket.

        The compression formats SNAPPY or ZIP cannot be specified for Amazon Redshift
        destinations because they are not supported by the Amazon Redshift COPY operation
        that reads from the S3 bucket.

        :default: - UNCOMPRESSED

        :stability: experimental
        '''
        result = self._values.get("compression")
        return typing.cast(typing.Optional[Compression], result)

    @builtins.property
    def data_output_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) A prefix that Kinesis Data Firehose evaluates and adds to records before writing them to S3.

        This prefix appears immediately following the bucket name.

        :default: "YYYY/MM/DD/HH"

        :see: https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html
        :stability: experimental
        '''
        result = self._values.get("data_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_IKey_36930160]:
        '''(experimental) The AWS KMS key used to encrypt the data that it delivers to your Amazon S3 bucket.

        :default: - Data is not encrypted.

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_IKey_36930160], result)

    @builtins.property
    def error_output_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) A prefix that Kinesis Data Firehose evaluates and adds to failed records before writing them to S3.

        This prefix appears immediately following the bucket name.

        :default: "YYYY/MM/DD/HH"

        :see: https://docs.aws.amazon.com/firehose/latest/dev/s3-prefixes.html
        :stability: experimental
        '''
        result = self._values.get("error_output_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logging(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If true, log errors when data transformation or data delivery fails.

        If ``logGroup`` is provided, this will be implicitly set to ``true``.

        :default: true - errors are logged.

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def log_group(self) -> typing.Optional[_ILogGroup_846e17a0]:
        '''(experimental) The CloudWatch log group where log streams will be created to hold error logs.

        :default: - if ``logging`` is set to ``true``, a log group will be created for you.

        :stability: experimental
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[_ILogGroup_846e17a0], result)

    @builtins.property
    def processor(self) -> typing.Optional[_IDataProcessor_682cbcf2]:
        '''(experimental) The data transformation that should be performed on the data before writing to the destination.

        :default: - no data transformation will occur.

        :stability: experimental
        '''
        result = self._values.get("processor")
        return typing.cast(typing.Optional[_IDataProcessor_682cbcf2], result)

    @builtins.property
    def role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The IAM role associated with this destination.

        Assumed by Kinesis Data Firehose to invoke processors and write to destinations

        :default: - a role will be created with default permissions.

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def s3_backup(self) -> typing.Optional[DestinationS3BackupProps]:
        '''(experimental) The configuration for backing up source records to S3.

        :default: - source records will not be backed up to S3.

        :stability: experimental
        '''
        result = self._values.get("s3_backup")
        return typing.cast(typing.Optional[DestinationS3BackupProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3BucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BackupMode",
    "CommonDestinationProps",
    "CommonDestinationS3Props",
    "Compression",
    "DestinationS3BackupProps",
    "S3Bucket",
    "S3BucketProps",
]

publication.publish()
