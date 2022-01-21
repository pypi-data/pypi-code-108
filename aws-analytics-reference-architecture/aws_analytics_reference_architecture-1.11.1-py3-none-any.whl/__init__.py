'''
# AWS Analytics Reference Architecture

The AWS Analytics Reference Architecture is a set of analytics solutions put together as end-to-end examples.
It regroups AWS best practices for designing, implementing, and operating analytics platforms through different purpose-built patterns, handling common requirements, and solving customers' challenges.

This project is composed of:

* Reusable core components exposed in an AWS CDK (Cloud Development Kit) library currently available in [Typescript](https://www.npmjs.com/package/aws-analytics-reference-architecture) and [Python](https://pypi.org/project/aws-analytics-reference-architecture/). This library contains [AWS CDK constructs](https://constructs.dev/packages/aws-analytics-reference-architecture) that can be used to quickly provision analytics solutions in demos, prototypes, proof of concepts and end-to-end reference architectures.
* Reference architectures consumming the reusable components to demonstrate end-to-end examples in a business context. Currently, the [AWS native reference architecture](https://aws-samples.github.io/aws-analytics-reference-architecture/) is available.

This documentation explains how to get started with the core components of the AWS Analytics Reference Architecture.

## Getting started

* [AWS Analytics Reference Architecture](#aws-analytics-reference-architecture)

  * [Getting started](#getting-started)

    * [Prerequisites](#prerequisites)
    * [Initialization (in Python)](#initialization-in-python)
    * [Development](#development)
    * [Deployment](#deployment)
    * [Cleanup](#cleanup)
  * [API Reference](#api-reference)
  * [Contributing](#contributing)
* [License Summary](#license-summary)

### Prerequisites

1. [Create an AWS account](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)
2. The core components can be deployed in any AWS region
3. Install the following components with the specified version on the machine from which the deployment will be executed:

   1. Python [3.8-3.9.2] or Typescript
   2. AWS CDK: Please refer to the [Getting started](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) guide.

### Initialization (in Python)

1. Initialize a new AWS CDK application in Python and use a virtual environment to install dependencies

```bash
mkdir my_demo
cd my_demo
cdk init app --language python
python3 -m venv .env
source .venv/bin/activate
```

1. Add the AWS Analytics Reference Architecture library in the dependencies of your project. Update **setup.py**

```bash
    install_requires=[
        "aws-cdk.core==1.130.0",
        "aws-analytics-reference-architecture==1.8.4",
    ],
```

1. Install The Packages via **pip**

```bash
python -m pip install -r requirements.txt
```

### Development

1. Import the AWS Analytics Reference Architecture in your code in **my_demo/my_demo_stack.py**

```bash
import aws_analytics_reference_architecture as ara
```

1. Now you can use all the constructs available from the core components library to quickly provision resources in your AWS CDK stack. For example:

* The DataLakeStorage to provision a full set of pre-configured Amazon S3 Bucket for a data lake

```bash
        # Create a new DataLakeStorage with Raw, Clean and Transform buckets configured with data lake best practices
        storage = ara.DataLakeStorage (self,"storage")
```

* The DataLakeCatalog to provision a full set of AWS Glue databases for registring tables in your data lake

```bash
        # Create a new DataLakeCatalog with Raw, Clean and Transform databases
        catalog = ara.DataLakeCatalog (self,"catalog")
```

* The DataGenerator to generate live data in the data lake from a pre-configured retail dataset

```bash
        # Generate the Sales Data
        sales_data = ara.DataGenerator(
            scope = self,
            id = 'sale-data',
            dataset = ara.Dataset.RETAIL_1_GB_STORE_SALE,
            sink_arn = storage.raw_bucket.bucket_arn,
            frequency = 120
        )
```

```bash
        # Generate the Customer Data
        customer_data = ara.DataGenerator(
            scope = self,
            id = 'customer-data',
            dataset = ara.Dataset.RETAIL_1_GB_CUSTOMER,
            sink_arn = storage.raw_bucket.bucket_arn,
            frequency = 120
        )
```

* Additionally, the library provides some helpers to quickly run demos:

```bash
        # Configure defaults for Athena console
        ara.AthenaDefaultSetup(
            scope = self,
            id = 'defaultSetup'
        )
```

```bash
        # Configure a default role for AWS Glue jobs
        ara.SingletonGlueDefaultRole.get_or_create(self)
```

### Deployment

1. Bootstrap AWS CDK in your region (here **eu-west-1**). It will provision resources required to deploy AWS CDK applications

```bash
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=eu-west-1
cdk bootstrap aws://$ACCOUNT_ID/eu-west-1
```

1. Deploy the AWS CDK application

```bash
cdk deploy
```

The time to deploy the application is depending on the constructs you are using

### Cleanup

Delete the AWS CDK application

```bash
cdk destroy
```

## API Reference

More contructs, helpers and datasets are available in the AWS Analytics Reference Architecture. See the full API specification [here](https://constructs.dev/packages/aws-analytics-reference-architecture/v/1.8.4?lang=python)

## Contributing

Please refer to the [contributing guidelines](../CONTRIBUTING.md) and [contributing FAQ](../CONTRIB_FAQ.md) for details.

# License Summary

The documentation is made available under the Creative Commons Attribution-ShareAlike 4.0 International License. See the LICENSE file.

The sample code within this documentation is made available under the MIT-0 license. See the LICENSE-SAMPLECODE file.
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
import aws_cdk.aws_eks
import aws_cdk.aws_emrcontainers
import aws_cdk.aws_glue
import aws_cdk.aws_iam
import aws_cdk.aws_kinesis
import aws_cdk.aws_kinesisfirehose
import aws_cdk.aws_kms
import aws_cdk.aws_logs
import aws_cdk.aws_redshift
import aws_cdk.aws_s3
import aws_cdk.core
import constructs


class AthenaDefaultSetup(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.AthenaDefaultSetup",
):
    '''(experimental) AthenaDefaultSetup Construct to automatically setup a new Amazon Athena Workgroup with proper configuration for out-of-the-box usage.

    :stability: experimental
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Constructs a new instance of the AthenaDefaultSetup class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resultBucket")
    def result_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "resultBucket"))


class BatchReplayer(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.BatchReplayer",
):
    '''(experimental) Replay the data in the given PartitionedDataset.

    It will dump files into the ``sinkBucket`` based on the given ``frequency``.
    The computation is in a Step Function with two Lambda steps.

    1. resources/lambdas/find-file-paths
       Read the manifest file and output a list of S3 file paths within that batch time range
    2. resources/lambdas/write-in-batch
       Take a file path, filter only records within given time range, adjust the the time with offset to
       make it looks like just being generated. Then write the output to the ``sinkBucket``

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        dataset: "PartitionedDataset",
        sink_bucket: aws_cdk.aws_s3.Bucket,
        frequency: typing.Optional[jsii.Number] = None,
        output_file_max_size_in_bytes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param dataset: 
        :param sink_bucket: 
        :param frequency: 
        :param output_file_max_size_in_bytes: 

        :stability: experimental
        '''
        props = BatchReplayerProps(
            dataset=dataset,
            sink_bucket=sink_bucket,
            frequency=frequency,
            output_file_max_size_in_bytes=output_file_max_size_in_bytes,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataset")
    def dataset(self) -> "PartitionedDataset":
        '''(experimental) Dataset used for replay.

        :stability: experimental
        '''
        return typing.cast("PartitionedDataset", jsii.get(self, "dataset"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> jsii.Number:
        '''(experimental) Frequency (in Seconds) of the replaying.

        The batch job will start
        for every given frequency and replay the data in that period

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "frequency"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sinkBucket")
    def sink_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''(experimental) Sink bucket where the batch replayer will put data in.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "sinkBucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFileMaxSizeInBytes")
    def output_file_max_size_in_bytes(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Maximum file size for each output file.

        If the output batch file is,
        larger than that, it will be splitted into multiple files that fit this size.

        Default to 100MB (max value)

        :stability: experimental
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "outputFileMaxSizeInBytes"))


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.BatchReplayerProps",
    jsii_struct_bases=[],
    name_mapping={
        "dataset": "dataset",
        "sink_bucket": "sinkBucket",
        "frequency": "frequency",
        "output_file_max_size_in_bytes": "outputFileMaxSizeInBytes",
    },
)
class BatchReplayerProps:
    def __init__(
        self,
        *,
        dataset: "PartitionedDataset",
        sink_bucket: aws_cdk.aws_s3.Bucket,
        frequency: typing.Optional[jsii.Number] = None,
        output_file_max_size_in_bytes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param dataset: 
        :param sink_bucket: 
        :param frequency: 
        :param output_file_max_size_in_bytes: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dataset": dataset,
            "sink_bucket": sink_bucket,
        }
        if frequency is not None:
            self._values["frequency"] = frequency
        if output_file_max_size_in_bytes is not None:
            self._values["output_file_max_size_in_bytes"] = output_file_max_size_in_bytes

    @builtins.property
    def dataset(self) -> "PartitionedDataset":
        '''
        :stability: experimental
        '''
        result = self._values.get("dataset")
        assert result is not None, "Required property 'dataset' is missing"
        return typing.cast("PartitionedDataset", result)

    @builtins.property
    def sink_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("sink_bucket")
        assert result is not None, "Required property 'sink_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.Bucket, result)

    @builtins.property
    def frequency(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def output_file_max_size_in_bytes(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("output_file_max_size_in_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BatchReplayerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataGenerator(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.DataGenerator",
):
    '''(experimental) DataGenerator Construct to replay data from an existing dataset into a target replacing datetime to current datetime Target can be an Amazon S3 bucket or an Amazon Kinesis Data Stream.

    DataGenerator can use pre-defined or custom datasets available in the [Dataset]{@link Dataset} Class

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        dataset: "Dataset",
        sink_arn: builtins.str,
        frequency: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the DataGenerator class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param dataset: (experimental) Source dataset used to generate the data by replying it. Use a pre-defined [Dataset]{@link Dataset} or create a [custom one]{@link Dataset.constructor}.
        :param sink_arn: (experimental) Sink Arn to receive the generated data. Sink must be an Amazon S3 bucket.
        :param frequency: (experimental) Frequency (in Seconds) of the data generation. Should be > 60s. Default: - 30 min (1800s)

        :stability: experimental
        :access: public
        '''
        props = DataGeneratorProps(
            dataset=dataset, sink_arn=sink_arn, frequency=frequency
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DATA_GENERATOR_DATABASE")
    def DATA_GENERATOR_DATABASE(cls) -> builtins.str:
        '''(experimental) AWS Glue Database name used by the DataGenerator.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DATA_GENERATOR_DATABASE"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataset")
    def dataset(self) -> "Dataset":
        '''(experimental) Dataset used to generate data.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.get(self, "dataset"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="frequency")
    def frequency(self) -> jsii.Number:
        '''(experimental) Frequency (in Seconds) of the data generation.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "frequency"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sinkArn")
    def sink_arn(self) -> builtins.str:
        '''(experimental) Sink Arn to receive the generated data.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "sinkArn"))


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.DataGeneratorProps",
    jsii_struct_bases=[],
    name_mapping={
        "dataset": "dataset",
        "sink_arn": "sinkArn",
        "frequency": "frequency",
    },
)
class DataGeneratorProps:
    def __init__(
        self,
        *,
        dataset: "Dataset",
        sink_arn: builtins.str,
        frequency: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The properties for DataGenerator Construct.

        :param dataset: (experimental) Source dataset used to generate the data by replying it. Use a pre-defined [Dataset]{@link Dataset} or create a [custom one]{@link Dataset.constructor}.
        :param sink_arn: (experimental) Sink Arn to receive the generated data. Sink must be an Amazon S3 bucket.
        :param frequency: (experimental) Frequency (in Seconds) of the data generation. Should be > 60s. Default: - 30 min (1800s)

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "dataset": dataset,
            "sink_arn": sink_arn,
        }
        if frequency is not None:
            self._values["frequency"] = frequency

    @builtins.property
    def dataset(self) -> "Dataset":
        '''(experimental) Source dataset used to generate the data by replying it.

        Use a pre-defined [Dataset]{@link Dataset} or create a [custom one]{@link Dataset.constructor}.

        :stability: experimental
        '''
        result = self._values.get("dataset")
        assert result is not None, "Required property 'dataset' is missing"
        return typing.cast("Dataset", result)

    @builtins.property
    def sink_arn(self) -> builtins.str:
        '''(experimental) Sink Arn to receive the generated data.

        Sink must be an Amazon S3 bucket.

        :stability: experimental
        '''
        result = self._values.get("sink_arn")
        assert result is not None, "Required property 'sink_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def frequency(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Frequency (in Seconds) of the data generation.

        Should be > 60s.

        :default: - 30 min (1800s)

        :stability: experimental
        '''
        result = self._values.get("frequency")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataGeneratorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataLakeCatalog(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.DataLakeCatalog",
):
    '''(experimental) A Data Lake Catalog composed of 3 AWS Glue Database configured with AWS best practices:   Databases for Raw/Cleaned/Transformed data,.

    :stability: experimental
    '''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''(experimental) Construct a new instance of DataLakeCatalog based on S3 buckets with best practices configuration.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.

        :stability: experimental
        :access: public
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cleanDatabase")
    def clean_database(self) -> aws_cdk.aws_glue.Database:
        '''(experimental) AWS Glue Database for Clean data.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_glue.Database, jsii.get(self, "cleanDatabase"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rawDatabase")
    def raw_database(self) -> aws_cdk.aws_glue.Database:
        '''(experimental) AWS Glue Database for Raw data.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_glue.Database, jsii.get(self, "rawDatabase"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transformDatabase")
    def transform_database(self) -> aws_cdk.aws_glue.Database:
        '''(experimental) AWS Glue Database for Transform data.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_glue.Database, jsii.get(self, "transformDatabase"))


class DataLakeExporter(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.DataLakeExporter",
):
    '''(experimental) DataLakeExporter Construct to export data from a stream to the data lake.

    Source can be an Amazon Kinesis Data Stream.
    Target can be an Amazon S3 bucket.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        sink_location: aws_cdk.aws_s3.Location,
        source_glue_database: aws_cdk.aws_glue.Database,
        source_glue_table: aws_cdk.aws_glue.Table,
        source_kinesis_data_stream: aws_cdk.aws_kinesis.Stream,
        delivery_interval: typing.Optional[jsii.Number] = None,
        delivery_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param sink_location: (experimental) Sink must be an Amazon S3 Location composed of a bucket and a key.
        :param source_glue_database: (experimental) Source AWS Glue Database containing the schema of the stream.
        :param source_glue_table: (experimental) Source AWS Glue Table containing the schema of the stream.
        :param source_kinesis_data_stream: (experimental) Source must be an Amazon Kinesis Data Stream.
        :param delivery_interval: (experimental) Delivery interval in seconds. The frequency of the data delivery is defined by this interval. Default: - Set to 900 seconds
        :param delivery_size: (experimental) Maximum delivery size in MB. The frequency of the data delivery is defined by this maximum delivery size. Default: - Set to 128 MB

        :stability: experimental
        '''
        props = DataLakeExporterProps(
            sink_location=sink_location,
            source_glue_database=source_glue_database,
            source_glue_table=source_glue_table,
            source_kinesis_data_stream=source_kinesis_data_stream,
            delivery_interval=delivery_interval,
            delivery_size=delivery_size,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cfnIngestionStream")
    def cfn_ingestion_stream(self) -> aws_cdk.aws_kinesisfirehose.CfnDeliveryStream:
        '''(experimental) Constructs a new instance of the DataLakeExporter class.

        :stability: experimental
        :access: public
        '''
        return typing.cast(aws_cdk.aws_kinesisfirehose.CfnDeliveryStream, jsii.get(self, "cfnIngestionStream"))


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.DataLakeExporterProps",
    jsii_struct_bases=[],
    name_mapping={
        "sink_location": "sinkLocation",
        "source_glue_database": "sourceGlueDatabase",
        "source_glue_table": "sourceGlueTable",
        "source_kinesis_data_stream": "sourceKinesisDataStream",
        "delivery_interval": "deliveryInterval",
        "delivery_size": "deliverySize",
    },
)
class DataLakeExporterProps:
    def __init__(
        self,
        *,
        sink_location: aws_cdk.aws_s3.Location,
        source_glue_database: aws_cdk.aws_glue.Database,
        source_glue_table: aws_cdk.aws_glue.Table,
        source_kinesis_data_stream: aws_cdk.aws_kinesis.Stream,
        delivery_interval: typing.Optional[jsii.Number] = None,
        delivery_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The properties for DataLakeExporter Construct.

        :param sink_location: (experimental) Sink must be an Amazon S3 Location composed of a bucket and a key.
        :param source_glue_database: (experimental) Source AWS Glue Database containing the schema of the stream.
        :param source_glue_table: (experimental) Source AWS Glue Table containing the schema of the stream.
        :param source_kinesis_data_stream: (experimental) Source must be an Amazon Kinesis Data Stream.
        :param delivery_interval: (experimental) Delivery interval in seconds. The frequency of the data delivery is defined by this interval. Default: - Set to 900 seconds
        :param delivery_size: (experimental) Maximum delivery size in MB. The frequency of the data delivery is defined by this maximum delivery size. Default: - Set to 128 MB

        :stability: experimental
        '''
        if isinstance(sink_location, dict):
            sink_location = aws_cdk.aws_s3.Location(**sink_location)
        self._values: typing.Dict[str, typing.Any] = {
            "sink_location": sink_location,
            "source_glue_database": source_glue_database,
            "source_glue_table": source_glue_table,
            "source_kinesis_data_stream": source_kinesis_data_stream,
        }
        if delivery_interval is not None:
            self._values["delivery_interval"] = delivery_interval
        if delivery_size is not None:
            self._values["delivery_size"] = delivery_size

    @builtins.property
    def sink_location(self) -> aws_cdk.aws_s3.Location:
        '''(experimental) Sink must be an Amazon S3 Location composed of a bucket and a key.

        :stability: experimental
        '''
        result = self._values.get("sink_location")
        assert result is not None, "Required property 'sink_location' is missing"
        return typing.cast(aws_cdk.aws_s3.Location, result)

    @builtins.property
    def source_glue_database(self) -> aws_cdk.aws_glue.Database:
        '''(experimental) Source AWS Glue Database containing the schema of the stream.

        :stability: experimental
        '''
        result = self._values.get("source_glue_database")
        assert result is not None, "Required property 'source_glue_database' is missing"
        return typing.cast(aws_cdk.aws_glue.Database, result)

    @builtins.property
    def source_glue_table(self) -> aws_cdk.aws_glue.Table:
        '''(experimental) Source AWS Glue Table containing the schema of the stream.

        :stability: experimental
        '''
        result = self._values.get("source_glue_table")
        assert result is not None, "Required property 'source_glue_table' is missing"
        return typing.cast(aws_cdk.aws_glue.Table, result)

    @builtins.property
    def source_kinesis_data_stream(self) -> aws_cdk.aws_kinesis.Stream:
        '''(experimental) Source must be an Amazon Kinesis Data Stream.

        :stability: experimental
        '''
        result = self._values.get("source_kinesis_data_stream")
        assert result is not None, "Required property 'source_kinesis_data_stream' is missing"
        return typing.cast(aws_cdk.aws_kinesis.Stream, result)

    @builtins.property
    def delivery_interval(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Delivery interval in seconds.

        The frequency of the data delivery is defined by this interval.

        :default: - Set to 900 seconds

        :stability: experimental
        '''
        result = self._values.get("delivery_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def delivery_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Maximum delivery size in MB.

        The frequency of the data delivery is defined by this maximum delivery size.

        :default: - Set to 128 MB

        :stability: experimental
        '''
        result = self._values.get("delivery_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataLakeExporterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataLakeStorage(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.DataLakeStorage",
):
    '''(experimental) A Data Lake Storage composed of 3 Amazon S3 Buckets configured with AWS best practices:   S3 buckets for Raw/Cleaned/Transformed data,   data lifecycle optimization/transitioning to different Amazon S3 storage classes   server side buckets encryption managed by KMS.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        clean_archive_delay: typing.Optional[jsii.Number] = None,
        clean_infrequent_access_delay: typing.Optional[jsii.Number] = None,
        raw_archive_delay: typing.Optional[jsii.Number] = None,
        raw_infrequent_access_delay: typing.Optional[jsii.Number] = None,
        transform_archive_delay: typing.Optional[jsii.Number] = None,
        transform_infrequent_access_delay: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Construct a new instance of DataLakeStorage based on Amazon S3 buckets with best practices configuration.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param clean_archive_delay: (experimental) Delay (in days) before archiving CLEAN data to frozen storage (Glacier storage class). Default: - Objects are not archived to Glacier
        :param clean_infrequent_access_delay: (experimental) Delay (in days) before moving CLEAN data to cold storage (Infrequent Access storage class). Default: - Move objects to Infrequent Access after 90 days
        :param raw_archive_delay: (experimental) Delay (in days) before archiving RAW data to frozen storage (Glacier storage class). Default: - Move objects to Glacier after 90 days
        :param raw_infrequent_access_delay: (experimental) Delay (in days) before moving RAW data to cold storage (Infrequent Access storage class). Default: - Move objects to Infrequent Access after 30 days
        :param transform_archive_delay: (experimental) Delay (in days) before archiving TRANSFORM data to frozen storage (Glacier storage class). Default: - Objects are not archived to Glacier
        :param transform_infrequent_access_delay: (experimental) Delay (in days) before moving TRANSFORM data to cold storage (Infrequent Access storage class). Default: - Move objects to Infrequent Access after 90 days

        :stability: experimental
        :access: public
        '''
        props = DataLakeStorageProps(
            clean_archive_delay=clean_archive_delay,
            clean_infrequent_access_delay=clean_infrequent_access_delay,
            raw_archive_delay=raw_archive_delay,
            raw_infrequent_access_delay=raw_infrequent_access_delay,
            transform_archive_delay=transform_archive_delay,
            transform_infrequent_access_delay=transform_infrequent_access_delay,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cleanBucket")
    def clean_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "cleanBucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rawBucket")
    def raw_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "rawBucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="transformBucket")
    def transform_bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "transformBucket"))


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.DataLakeStorageProps",
    jsii_struct_bases=[],
    name_mapping={
        "clean_archive_delay": "cleanArchiveDelay",
        "clean_infrequent_access_delay": "cleanInfrequentAccessDelay",
        "raw_archive_delay": "rawArchiveDelay",
        "raw_infrequent_access_delay": "rawInfrequentAccessDelay",
        "transform_archive_delay": "transformArchiveDelay",
        "transform_infrequent_access_delay": "transformInfrequentAccessDelay",
    },
)
class DataLakeStorageProps:
    def __init__(
        self,
        *,
        clean_archive_delay: typing.Optional[jsii.Number] = None,
        clean_infrequent_access_delay: typing.Optional[jsii.Number] = None,
        raw_archive_delay: typing.Optional[jsii.Number] = None,
        raw_infrequent_access_delay: typing.Optional[jsii.Number] = None,
        transform_archive_delay: typing.Optional[jsii.Number] = None,
        transform_infrequent_access_delay: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties for the DataLakeStorage Construct.

        :param clean_archive_delay: (experimental) Delay (in days) before archiving CLEAN data to frozen storage (Glacier storage class). Default: - Objects are not archived to Glacier
        :param clean_infrequent_access_delay: (experimental) Delay (in days) before moving CLEAN data to cold storage (Infrequent Access storage class). Default: - Move objects to Infrequent Access after 90 days
        :param raw_archive_delay: (experimental) Delay (in days) before archiving RAW data to frozen storage (Glacier storage class). Default: - Move objects to Glacier after 90 days
        :param raw_infrequent_access_delay: (experimental) Delay (in days) before moving RAW data to cold storage (Infrequent Access storage class). Default: - Move objects to Infrequent Access after 30 days
        :param transform_archive_delay: (experimental) Delay (in days) before archiving TRANSFORM data to frozen storage (Glacier storage class). Default: - Objects are not archived to Glacier
        :param transform_infrequent_access_delay: (experimental) Delay (in days) before moving TRANSFORM data to cold storage (Infrequent Access storage class). Default: - Move objects to Infrequent Access after 90 days

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if clean_archive_delay is not None:
            self._values["clean_archive_delay"] = clean_archive_delay
        if clean_infrequent_access_delay is not None:
            self._values["clean_infrequent_access_delay"] = clean_infrequent_access_delay
        if raw_archive_delay is not None:
            self._values["raw_archive_delay"] = raw_archive_delay
        if raw_infrequent_access_delay is not None:
            self._values["raw_infrequent_access_delay"] = raw_infrequent_access_delay
        if transform_archive_delay is not None:
            self._values["transform_archive_delay"] = transform_archive_delay
        if transform_infrequent_access_delay is not None:
            self._values["transform_infrequent_access_delay"] = transform_infrequent_access_delay

    @builtins.property
    def clean_archive_delay(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Delay (in days) before archiving CLEAN data to frozen storage (Glacier storage class).

        :default: - Objects are not archived to Glacier

        :stability: experimental
        '''
        result = self._values.get("clean_archive_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def clean_infrequent_access_delay(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Delay (in days) before moving CLEAN data to cold storage (Infrequent Access storage class).

        :default: - Move objects to Infrequent Access after 90 days

        :stability: experimental
        '''
        result = self._values.get("clean_infrequent_access_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raw_archive_delay(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Delay (in days) before archiving RAW data to frozen storage (Glacier storage class).

        :default: - Move objects to Glacier after 90 days

        :stability: experimental
        '''
        result = self._values.get("raw_archive_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def raw_infrequent_access_delay(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Delay (in days) before moving RAW data to cold storage (Infrequent Access storage class).

        :default: - Move objects to Infrequent Access after 30 days

        :stability: experimental
        '''
        result = self._values.get("raw_infrequent_access_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def transform_archive_delay(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Delay (in days) before archiving TRANSFORM data to frozen storage (Glacier storage class).

        :default: - Objects are not archived to Glacier

        :stability: experimental
        '''
        result = self._values.get("transform_archive_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def transform_infrequent_access_delay(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Delay (in days) before moving TRANSFORM data to cold storage (Infrequent Access storage class).

        :default: - Move objects to Infrequent Access after 90 days

        :stability: experimental
        '''
        result = self._values.get("transform_infrequent_access_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataLakeStorageProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Dataset(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.Dataset",
):
    '''(experimental) Dataset enum-like class providing pre-defined datasets metadata and custom dataset creation.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        create_source_table: builtins.str,
        generate_data: builtins.str,
        location: aws_cdk.aws_s3.Location,
        start_datetime: builtins.str,
        create_target_table: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the Dataset class.

        :param create_source_table: (experimental) The CREATE TABLE DDL command to create the source AWS Glue Table.
        :param generate_data: (experimental) The SELECT query used to generate new data.
        :param location: (experimental) The Amazon S3 Location of the source dataset. It's composed of an Amazon S3 bucketName and an Amazon S3 objectKey
        :param start_datetime: (experimental) The minimum datetime value in the dataset used to calculate time offset.
        :param create_target_table: (experimental) The CREATE TABLE DDL command to create the target AWS Glue Table. Default: - Use the same DDL as the source table

        :stability: experimental
        :access: public
        '''
        props = DatasetProps(
            create_source_table=create_source_table,
            generate_data=generate_data,
            location=location,
            start_datetime=start_datetime,
            create_target_table=create_target_table,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="parseCreateSourceQuery")
    def parse_create_source_query(
        self,
        database: builtins.str,
        table: builtins.str,
        bucket: builtins.str,
        key: builtins.str,
    ) -> builtins.str:
        '''(experimental) Parse the CREATE TABLE statement template for the source.

        :param database: the database name to parse.
        :param table: the table name to parse.
        :param bucket: the bucket name to parse.
        :param key: the key to parse.

        :stability: experimental
        :access: public
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "parseCreateSourceQuery", [database, table, bucket, key]))

    @jsii.member(jsii_name="parseCreateTargetQuery")
    def parse_create_target_query(
        self,
        database: builtins.str,
        table: builtins.str,
        bucket: builtins.str,
        key: builtins.str,
    ) -> builtins.str:
        '''(experimental) Parse the CREATE TABLE statement template for the source.

        :param database: the database name to parse.
        :param table: the table name to parse.
        :param bucket: the bucket name to parse.
        :param key: the key to parse.

        :stability: experimental
        :access: public
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "parseCreateTargetQuery", [database, table, bucket, key]))

    @jsii.member(jsii_name="parseGenerateQuery")
    def parse_generate_query(
        self,
        database: builtins.str,
        source_table: builtins.str,
        target_table: builtins.str,
    ) -> builtins.str:
        '''(experimental) Parse the CREATE TABLE statement template for the target.

        :param database: the database name to parse.
        :param source_table: the source table name to parse.
        :param target_table: the target table name to parse.

        :stability: experimental
        :access: public
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "parseGenerateQuery", [database, source_table, target_table]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DATASETS_BUCKET")
    def DATASETS_BUCKET(cls) -> builtins.str:
        '''(experimental) The bucket name of the AWS Analytics Reference Architecture datasets.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DATASETS_BUCKET"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_100GB_CUSTOMER")
    def RETAIL_100_GB_CUSTOMER(cls) -> "Dataset":
        '''(experimental) The customer dataset part of 100GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_100GB_CUSTOMER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_100GB_CUSTOMER_ADDRESS")
    def RETAIL_100_GB_CUSTOMER_ADDRESS(cls) -> "Dataset":
        '''(experimental) The customer address dataset part of 100GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_100GB_CUSTOMER_ADDRESS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_100GB_ITEM")
    def RETAIL_100_GB_ITEM(cls) -> "Dataset":
        '''(experimental) The item dataset part of 100GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_100GB_ITEM"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_100GB_PROMO")
    def RETAIL_100_GB_PROMO(cls) -> "Dataset":
        '''(experimental) The promotion dataset part of 100GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_100GB_PROMO"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_100GB_STORE")
    def RETAIL_100_GB_STORE(cls) -> "Dataset":
        '''(experimental) The store dataset part of 100GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_100GB_STORE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_100GB_STORE_SALE")
    def RETAIL_100_GB_STORE_SALE(cls) -> "Dataset":
        '''(experimental) The store sale dataset part of 100GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_100GB_STORE_SALE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_100GB_WAREHOUSE")
    def RETAIL_100_GB_WAREHOUSE(cls) -> "Dataset":
        '''(experimental) The warehouse dataset part 100GB of retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_100GB_WAREHOUSE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_100GB_WEB_SALE")
    def RETAIL_100_GB_WEB_SALE(cls) -> "Dataset":
        '''(experimental) The web sale dataset part of 100GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_100GB_WEB_SALE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_1GB_CUSTOMER")
    def RETAIL_1_GB_CUSTOMER(cls) -> "Dataset":
        '''(experimental) The customer dataset part of 1GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_1GB_CUSTOMER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_1GB_CUSTOMER_ADDRESS")
    def RETAIL_1_GB_CUSTOMER_ADDRESS(cls) -> "Dataset":
        '''(experimental) The customer address dataset part of 1GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_1GB_CUSTOMER_ADDRESS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_1GB_ITEM")
    def RETAIL_1_GB_ITEM(cls) -> "Dataset":
        '''(experimental) The item dataset part of 1GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_1GB_ITEM"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_1GB_PROMO")
    def RETAIL_1_GB_PROMO(cls) -> "Dataset":
        '''(experimental) The promotion dataset part of 1GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_1GB_PROMO"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_1GB_STORE")
    def RETAIL_1_GB_STORE(cls) -> "Dataset":
        '''(experimental) The store dataset part of 1GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_1GB_STORE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_1GB_STORE_SALE")
    def RETAIL_1_GB_STORE_SALE(cls) -> "Dataset":
        '''(experimental) The store sale dataset part of 1GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_1GB_STORE_SALE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_1GB_WAREHOUSE")
    def RETAIL_1_GB_WAREHOUSE(cls) -> "Dataset":
        '''(experimental) The warehouse dataset part of 1GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_1GB_WAREHOUSE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_1GB_WEB_SALE")
    def RETAIL_1_GB_WEB_SALE(cls) -> "Dataset":
        '''(experimental) The web sale dataset part of 1GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("Dataset", jsii.sget(cls, "RETAIL_1GB_WEB_SALE"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createSourceTable")
    def create_source_table(self) -> builtins.str:
        '''(experimental) The CREATE TABLE DDL command to create the source AWS Glue Table.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "createSourceTable"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createTargetTable")
    def create_target_table(self) -> builtins.str:
        '''(experimental) The CREATE TABLE DDL command to create the target AWS Glue Table.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "createTargetTable"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="generateData")
    def generate_data(self) -> builtins.str:
        '''(experimental) The SELECT query used to generate new data.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "generateData"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> aws_cdk.aws_s3.Location:
        '''(experimental) The Amazon S3 Location of the source dataset.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Location, jsii.get(self, "location"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offset")
    def offset(self) -> jsii.Number:
        '''(experimental) The offset of the Dataset (difference between min datetime and now) in Seconds.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "offset"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        '''(experimental) The name of the SQL table extracted from path.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableName"))


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.DatasetProps",
    jsii_struct_bases=[],
    name_mapping={
        "create_source_table": "createSourceTable",
        "generate_data": "generateData",
        "location": "location",
        "start_datetime": "startDatetime",
        "create_target_table": "createTargetTable",
    },
)
class DatasetProps:
    def __init__(
        self,
        *,
        create_source_table: builtins.str,
        generate_data: builtins.str,
        location: aws_cdk.aws_s3.Location,
        start_datetime: builtins.str,
        create_target_table: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create_source_table: (experimental) The CREATE TABLE DDL command to create the source AWS Glue Table.
        :param generate_data: (experimental) The SELECT query used to generate new data.
        :param location: (experimental) The Amazon S3 Location of the source dataset. It's composed of an Amazon S3 bucketName and an Amazon S3 objectKey
        :param start_datetime: (experimental) The minimum datetime value in the dataset used to calculate time offset.
        :param create_target_table: (experimental) The CREATE TABLE DDL command to create the target AWS Glue Table. Default: - Use the same DDL as the source table

        :stability: experimental
        '''
        if isinstance(location, dict):
            location = aws_cdk.aws_s3.Location(**location)
        self._values: typing.Dict[str, typing.Any] = {
            "create_source_table": create_source_table,
            "generate_data": generate_data,
            "location": location,
            "start_datetime": start_datetime,
        }
        if create_target_table is not None:
            self._values["create_target_table"] = create_target_table

    @builtins.property
    def create_source_table(self) -> builtins.str:
        '''(experimental) The CREATE TABLE DDL command to create the source AWS Glue Table.

        :stability: experimental
        '''
        result = self._values.get("create_source_table")
        assert result is not None, "Required property 'create_source_table' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def generate_data(self) -> builtins.str:
        '''(experimental) The SELECT query used to generate new data.

        :stability: experimental
        '''
        result = self._values.get("generate_data")
        assert result is not None, "Required property 'generate_data' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> aws_cdk.aws_s3.Location:
        '''(experimental) The Amazon S3 Location of the source dataset.

        It's composed of an Amazon S3 bucketName and an Amazon S3 objectKey

        :stability: experimental
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(aws_cdk.aws_s3.Location, result)

    @builtins.property
    def start_datetime(self) -> builtins.str:
        '''(experimental) The minimum datetime value in the dataset used to calculate time offset.

        :stability: experimental
        '''
        result = self._values.get("start_datetime")
        assert result is not None, "Required property 'start_datetime' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def create_target_table(self) -> typing.Optional[builtins.str]:
        '''(experimental) The CREATE TABLE DDL command to create the target AWS Glue Table.

        :default: - Use the same DDL as the source table

        :stability: experimental
        '''
        result = self._values.get("create_target_table")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatasetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Ec2SsmRole(
    aws_cdk.aws_iam.Role,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.Ec2SsmRole",
):
    '''(experimental) Construct extending IAM Role with AmazonSSMManagedInstanceCore managed policy.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        assumed_by: aws_cdk.aws_iam.IPrincipal,
        description: typing.Optional[builtins.str] = None,
        external_id: typing.Optional[builtins.str] = None,
        external_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        inline_policies: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_iam.PolicyDocument]] = None,
        managed_policies: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IManagedPolicy]] = None,
        max_session_duration: typing.Optional[aws_cdk.core.Duration] = None,
        path: typing.Optional[builtins.str] = None,
        permissions_boundary: typing.Optional[aws_cdk.aws_iam.IManagedPolicy] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the Ec2SsmRole class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param assumed_by: The IAM principal (i.e. ``new ServicePrincipal('sns.amazonaws.com')``) which can assume this role. You can later modify the assume role policy document by accessing it via the ``assumeRolePolicy`` property.
        :param description: A description of the role. It can be up to 1000 characters long. Default: - No description.
        :param external_id: (deprecated) ID that the role assumer needs to provide when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
        :param external_ids: List of IDs that the role assumer needs to provide one of when assuming this role. If the configured and provided external IDs do not match, the AssumeRole operation will fail. Default: No external ID required
        :param inline_policies: A list of named policies to inline into this role. These policies will be created with the role, whereas those added by ``addToPolicy`` are added using a separate CloudFormation resource (allowing a way around circular dependencies that could otherwise be introduced). Default: - No policy is inlined in the Role resource.
        :param managed_policies: A list of managed policies associated with this role. You can add managed policies later using ``addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName(policyName))``. Default: - No managed policies.
        :param max_session_duration: The maximum session duration that you want to set for the specified role. This setting can have a value from 1 hour (3600sec) to 12 (43200sec) hours. Anyone who assumes the role from the AWS CLI or API can use the DurationSeconds API parameter or the duration-seconds CLI parameter to request a longer session. The MaxSessionDuration setting determines the maximum duration that can be requested using the DurationSeconds parameter. If users don't specify a value for the DurationSeconds parameter, their security credentials are valid for one hour by default. This applies when you use the AssumeRole* API operations or the assume-role* CLI operations but does not apply when you use those operations to create a console URL. Default: Duration.hours(1)
        :param path: The path associated with this role. For information about IAM paths, see Friendly Names and Paths in IAM User Guide. Default: /
        :param permissions_boundary: AWS supports permissions boundaries for IAM entities (users or roles). A permissions boundary is an advanced feature for using a managed policy to set the maximum permissions that an identity-based policy can grant to an IAM entity. An entity's permissions boundary allows it to perform only the actions that are allowed by both its identity-based policies and its permissions boundaries. Default: - No permissions boundary.
        :param role_name: A name for the IAM role. For valid values, see the RoleName parameter for the CreateRole action in the IAM API Reference. IMPORTANT: If you specify a name, you cannot perform updates that require replacement of this resource. You can perform updates that require no or some interruption. If you must replace the resource, specify a new name. If you specify a name, you must specify the CAPABILITY_NAMED_IAM value to acknowledge your template's capabilities. For more information, see Acknowledging IAM Resources in AWS CloudFormation Templates. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the role name.

        :stability: experimental
        :access: public
        '''
        props = aws_cdk.aws_iam.RoleProps(
            assumed_by=assumed_by,
            description=description,
            external_id=external_id,
            external_ids=external_ids,
            inline_policies=inline_policies,
            managed_policies=managed_policies,
            max_session_duration=max_session_duration,
            path=path,
            permissions_boundary=permissions_boundary,
            role_name=role_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class EmrEksCluster(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.EmrEksCluster",
):
    '''(experimental) EmrEksCluster Construct packaging all the ressources required to run Amazon EMR on Amazon EKS.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        eks_admin_role_arn: builtins.str,
        eks_cluster_name: typing.Optional[builtins.str] = None,
        emr_eks_nodegroups: typing.Optional[typing.Sequence["EmrEksNodegroup"]] = None,
        kubernetes_version: typing.Optional[aws_cdk.aws_eks.KubernetesVersion] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the EmrEksCluster class.

        An EmrEksCluster contains everything required to run Amazon EMR on Amazon EKS.
        Amazon EKS Nodegroups and Amazon EKS Admin role can be customized.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param eks_admin_role_arn: (experimental) Amazon IAM Role to be added to Amazon EKS master roles that will give access to kubernetes cluster from AWS console UI.
        :param eks_cluster_name: (experimental) Name of the Amazon EKS cluster to be created. Default: - automatically generated cluster name
        :param emr_eks_nodegroups: (experimental) List of EmrEksNodegroup to create in the cluster in addition to the default [nodegroups] {@link EmrEksNodegroup}. Default: - Don't create additional nodegroups
        :param kubernetes_version: (experimental) Kubernetes version for Amazon EKS cluster that will be created. Default: - v1.20 version is used

        :stability: experimental
        :access: public
        '''
        props = EmrEksClusterProps(
            eks_admin_role_arn=eks_admin_role_arn,
            eks_cluster_name=eks_cluster_name,
            emr_eks_nodegroups=emr_eks_nodegroups,
            kubernetes_version=kubernetes_version,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getOrCreate") # type: ignore[misc]
    @builtins.classmethod
    def get_or_create(
        cls,
        scope: aws_cdk.core.Construct,
        eks_admin_role_arn: builtins.str,
        kubernetes_version: typing.Optional[aws_cdk.aws_eks.KubernetesVersion] = None,
        cluster_name: typing.Optional[builtins.str] = None,
    ) -> "EmrEksCluster":
        '''
        :param scope: -
        :param eks_admin_role_arn: -
        :param kubernetes_version: -
        :param cluster_name: -

        :stability: experimental
        '''
        return typing.cast("EmrEksCluster", jsii.sinvoke(cls, "getOrCreate", [scope, eks_admin_role_arn, kubernetes_version, cluster_name]))

    @jsii.member(jsii_name="addEmrEksNodegroup")
    def add_emr_eks_nodegroup(
        self,
        *,
        id: builtins.str,
        mount_nvme: typing.Optional[builtins.bool] = None,
        subnet: typing.Optional[aws_cdk.aws_ec2.ISubnet] = None,
        ami_type: typing.Optional[aws_cdk.aws_eks.NodegroupAmiType] = None,
        capacity_type: typing.Optional[aws_cdk.aws_eks.CapacityType] = None,
        desired_size: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        force_update: typing.Optional[builtins.bool] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        instance_types: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.InstanceType]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        launch_template_spec: typing.Optional[aws_cdk.aws_eks.LaunchTemplateSpec] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        nodegroup_name: typing.Optional[builtins.str] = None,
        node_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        release_version: typing.Optional[builtins.str] = None,
        remote_access: typing.Optional[aws_cdk.aws_eks.NodegroupRemoteAccess] = None,
        subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Sequence[aws_cdk.aws_eks.TaintSpec]] = None,
    ) -> None:
        '''(experimental) Add new Amazon EMR on EKS nodegroups to the cluster.

        This method overrides Amazon EKS nodegroup options then create the nodegroup.
        If no subnet is provided, it creates one nodegroup per private subnet in the Amazon EKS Cluster.
        If NVME local storage is used, the user_data is modified.

        :param id: (experimental) Nodegroup ID.
        :param mount_nvme: (experimental) Set to true if using instance types with local NVMe drives to mount them automatically at boot time. Default: false
        :param subnet: (experimental) Configure the Amazon EKS NodeGroup in this subnet. Use this setting for resource dependencies like an Amazon RD Default: - One NodeGroup is deployed per cluster AZ
        :param ami_type: The AMI type for your node group. Default: - auto-determined from the instanceTypes property.
        :param capacity_type: The capacity type of the nodegroup. Default: - ON_DEMAND
        :param desired_size: The current number of worker nodes that the managed node group should maintain. If not specified, the nodewgroup will initially create ``minSize`` instances. Default: 2
        :param disk_size: The root device disk size (in GiB) for your node group instances. Default: 20
        :param force_update: Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue. If an update fails because pods could not be drained, you can force the update after it fails to terminate the old node whether or not any pods are running on the node. Default: true
        :param instance_type: (deprecated) The instance type to use for your node group. Currently, you can specify a single instance type for a node group. The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the ``AL2_x86_64_GPU`` with the amiType parameter. Default: t3.medium
        :param instance_types: The instance types to use for your node group. Default: t3.medium will be used according to the cloudformation document.
        :param labels: The Kubernetes labels to be applied to the nodes in the node group when they are created. Default: - None
        :param launch_template_spec: Launch template specification used for the nodegroup. Default: - no launch template
        :param max_size: The maximum number of worker nodes that the managed node group can scale out to. Managed node groups can support up to 100 nodes by default. Default: - desiredSize
        :param min_size: The minimum number of worker nodes that the managed node group can scale in to. This number must be greater than or equal to zero. Default: 1
        :param nodegroup_name: Name of the Nodegroup. Default: - resource ID
        :param node_role: The IAM role to associate with your node group. The Amazon EKS worker node kubelet daemon makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through an IAM instance profile and associated policies. Before you can launch worker nodes and register them into a cluster, you must create an IAM role for those worker nodes to use when they are launched. Default: - None. Auto-generated if not specified.
        :param release_version: The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``). Default: - The latest available AMI version for the node group's current Kubernetes version is used.
        :param remote_access: The remote access (SSH) configuration to use with your node group. Disabled by default, however, if you specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group, then port 22 on the worker nodes is opened to the internet (0.0.0.0/0) Default: - disabled
        :param subnets: The subnets to use for the Auto Scaling group that is created for your node group. By specifying the SubnetSelection, the selected subnets will automatically apply required tags i.e. ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with the name of your cluster. Default: - private subnets
        :param tags: The metadata to apply to the node group to assist with categorization and organization. Each tag consists of a key and an optional value, both of which you define. Node group tags do not propagate to any other resources associated with the node group, such as the Amazon EC2 instances or subnets. Default: - None
        :param taints: The Kubernetes taints to be applied to the nodes in the node group when they are created. Default: - None

        :stability: experimental
        :access: public
        '''
        props = EmrEksNodegroupOptions(
            id=id,
            mount_nvme=mount_nvme,
            subnet=subnet,
            ami_type=ami_type,
            capacity_type=capacity_type,
            desired_size=desired_size,
            disk_size=disk_size,
            force_update=force_update,
            instance_type=instance_type,
            instance_types=instance_types,
            labels=labels,
            launch_template_spec=launch_template_spec,
            max_size=max_size,
            min_size=min_size,
            nodegroup_name=nodegroup_name,
            node_role=node_role,
            release_version=release_version,
            remote_access=remote_access,
            subnets=subnets,
            tags=tags,
            taints=taints,
        )

        return typing.cast(None, jsii.invoke(self, "addEmrEksNodegroup", [props]))

    @jsii.member(jsii_name="addEmrVirtualCluster")
    def add_emr_virtual_cluster(
        self,
        *,
        name: builtins.str,
        create_namespace: typing.Optional[builtins.bool] = None,
        eks_namespace: typing.Optional[builtins.str] = None,
    ) -> aws_cdk.aws_emrcontainers.CfnVirtualCluster:
        '''(experimental) Add a new Amazon EMR Virtual Cluster linked to Amazon EKS Cluster.

        :param name: (experimental) name of the EmrVirtualCluster to be created.
        :param create_namespace: (experimental) creates EKS namespace. Default: - Do not create the namespace
        :param eks_namespace: (experimental) name of the EKS namespace to be linked to the EMR virtual Cluster. Default: - Use the default namespace

        :stability: experimental
        :access: public
        '''
        props = EmrVirtualClusterProps(
            name=name, create_namespace=create_namespace, eks_namespace=eks_namespace
        )

        return typing.cast(aws_cdk.aws_emrcontainers.CfnVirtualCluster, jsii.invoke(self, "addEmrVirtualCluster", [props]))

    @jsii.member(jsii_name="addManagedEndpoint")
    def add_managed_endpoint(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        virtual_cluster_id: builtins.str,
        execution_role: aws_cdk.aws_iam.IRole,
        acm_certificate_arn: typing.Optional[builtins.str] = None,
        emr_on_eks_version: typing.Optional[builtins.str] = None,
        configuration_overrides: typing.Optional[builtins.str] = None,
    ) -> aws_cdk.core.CustomResource:
        '''(experimental) Creates a new Amazon EMR managed endpoint to be used with Amazon EMR Virtual Cluster .

        CfnOutput can be customized.

        :param scope: -
        :param id: unique id for endpoint.
        :param virtual_cluster_id: Amazon Emr Virtual Cluster Id.
        :param execution_role: - IAM execution role to attach.
        :param acm_certificate_arn: - ACM Certificate Arn to be attached to the managed endpoint,.
        :param emr_on_eks_version: - EmrOnEks version to be used.
        :param configuration_overrides: - The JSON configuration override for Amazon EMR Managed Endpoint,.

        :default: - Configuration related to the [default nodegroup for notebook]{@link EmrEksNodegroup.NOTEBOOK_EXECUTOR}

        :stability: experimental
        :access: public
        '''
        return typing.cast(aws_cdk.core.CustomResource, jsii.invoke(self, "addManagedEndpoint", [scope, id, virtual_cluster_id, execution_role, acm_certificate_arn, emr_on_eks_version, configuration_overrides]))

    @jsii.member(jsii_name="addNodegroupCapacity")
    def add_nodegroup_capacity(
        self,
        nodegroup_id: builtins.str,
        *,
        id: builtins.str,
        mount_nvme: typing.Optional[builtins.bool] = None,
        subnet: typing.Optional[aws_cdk.aws_ec2.ISubnet] = None,
        ami_type: typing.Optional[aws_cdk.aws_eks.NodegroupAmiType] = None,
        capacity_type: typing.Optional[aws_cdk.aws_eks.CapacityType] = None,
        desired_size: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        force_update: typing.Optional[builtins.bool] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        instance_types: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.InstanceType]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        launch_template_spec: typing.Optional[aws_cdk.aws_eks.LaunchTemplateSpec] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        nodegroup_name: typing.Optional[builtins.str] = None,
        node_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        release_version: typing.Optional[builtins.str] = None,
        remote_access: typing.Optional[aws_cdk.aws_eks.NodegroupRemoteAccess] = None,
        subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Sequence[aws_cdk.aws_eks.TaintSpec]] = None,
    ) -> aws_cdk.aws_eks.Nodegroup:
        '''(experimental) Add a new Amazon EKS Nodegroup to the cluster.

        This method is be used to add a nodegroup to the Amazon EKS cluster and automatically set tags based on labels and taints
        so it can be used for the cluster autoscaler.

        :param nodegroup_id: the ID of the nodegroup.
        :param id: (experimental) Nodegroup ID.
        :param mount_nvme: (experimental) Set to true if using instance types with local NVMe drives to mount them automatically at boot time. Default: false
        :param subnet: (experimental) Configure the Amazon EKS NodeGroup in this subnet. Use this setting for resource dependencies like an Amazon RD Default: - One NodeGroup is deployed per cluster AZ
        :param ami_type: The AMI type for your node group. Default: - auto-determined from the instanceTypes property.
        :param capacity_type: The capacity type of the nodegroup. Default: - ON_DEMAND
        :param desired_size: The current number of worker nodes that the managed node group should maintain. If not specified, the nodewgroup will initially create ``minSize`` instances. Default: 2
        :param disk_size: The root device disk size (in GiB) for your node group instances. Default: 20
        :param force_update: Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue. If an update fails because pods could not be drained, you can force the update after it fails to terminate the old node whether or not any pods are running on the node. Default: true
        :param instance_type: (deprecated) The instance type to use for your node group. Currently, you can specify a single instance type for a node group. The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the ``AL2_x86_64_GPU`` with the amiType parameter. Default: t3.medium
        :param instance_types: The instance types to use for your node group. Default: t3.medium will be used according to the cloudformation document.
        :param labels: The Kubernetes labels to be applied to the nodes in the node group when they are created. Default: - None
        :param launch_template_spec: Launch template specification used for the nodegroup. Default: - no launch template
        :param max_size: The maximum number of worker nodes that the managed node group can scale out to. Managed node groups can support up to 100 nodes by default. Default: - desiredSize
        :param min_size: The minimum number of worker nodes that the managed node group can scale in to. This number must be greater than or equal to zero. Default: 1
        :param nodegroup_name: Name of the Nodegroup. Default: - resource ID
        :param node_role: The IAM role to associate with your node group. The Amazon EKS worker node kubelet daemon makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through an IAM instance profile and associated policies. Before you can launch worker nodes and register them into a cluster, you must create an IAM role for those worker nodes to use when they are launched. Default: - None. Auto-generated if not specified.
        :param release_version: The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``). Default: - The latest available AMI version for the node group's current Kubernetes version is used.
        :param remote_access: The remote access (SSH) configuration to use with your node group. Disabled by default, however, if you specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group, then port 22 on the worker nodes is opened to the internet (0.0.0.0/0) Default: - disabled
        :param subnets: The subnets to use for the Auto Scaling group that is created for your node group. By specifying the SubnetSelection, the selected subnets will automatically apply required tags i.e. ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with the name of your cluster. Default: - private subnets
        :param tags: The metadata to apply to the node group to assist with categorization and organization. Each tag consists of a key and an optional value, both of which you define. Node group tags do not propagate to any other resources associated with the node group, such as the Amazon EC2 instances or subnets. Default: - None
        :param taints: The Kubernetes taints to be applied to the nodes in the node group when they are created. Default: - None

        :stability: experimental
        :access: public
        '''
        options = EmrEksNodegroupOptions(
            id=id,
            mount_nvme=mount_nvme,
            subnet=subnet,
            ami_type=ami_type,
            capacity_type=capacity_type,
            desired_size=desired_size,
            disk_size=disk_size,
            force_update=force_update,
            instance_type=instance_type,
            instance_types=instance_types,
            labels=labels,
            launch_template_spec=launch_template_spec,
            max_size=max_size,
            min_size=min_size,
            nodegroup_name=nodegroup_name,
            node_role=node_role,
            release_version=release_version,
            remote_access=remote_access,
            subnets=subnets,
            tags=tags,
            taints=taints,
        )

        return typing.cast(aws_cdk.aws_eks.Nodegroup, jsii.invoke(self, "addNodegroupCapacity", [nodegroup_id, options]))

    @jsii.member(jsii_name="createExecutionRole")
    def create_execution_role(
        self,
        policy: aws_cdk.aws_iam.Policy,
    ) -> aws_cdk.aws_iam.Role:
        '''(experimental) Create and configure a new Amazon IAM Role usable as an execution role.

        This method links the makes the created role assumed by the Amazon EKS cluster Open ID Connect provider.

        :param policy: the execution policy to attach to the role.

        :stability: experimental
        :access: public
        '''
        return typing.cast(aws_cdk.aws_iam.Role, jsii.invoke(self, "createExecutionRole", [policy]))

    @jsii.member(jsii_name="uploadPodTemplate")
    def upload_pod_template(self, path: builtins.str) -> None:
        '''(experimental) Upload podTemplates to the Amazon S3 location used by the cluster.

        :param path: The local path of the yaml podTemplate files to upload.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "uploadPodTemplate", [path]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="criticalDefaultConfig")
    def critical_default_config(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "criticalDefaultConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eksCluster")
    def eks_cluster(self) -> aws_cdk.aws_eks.Cluster:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_eks.Cluster, jsii.get(self, "eksCluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notebookDefaultConfig")
    def notebook_default_config(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "notebookDefaultConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="podTemplateLocation")
    def pod_template_location(self) -> aws_cdk.aws_s3.Location:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Location, jsii.get(self, "podTemplateLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sharedDefaultConfig")
    def shared_default_config(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "sharedDefaultConfig"))


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.EmrEksClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "eks_admin_role_arn": "eksAdminRoleArn",
        "eks_cluster_name": "eksClusterName",
        "emr_eks_nodegroups": "emrEksNodegroups",
        "kubernetes_version": "kubernetesVersion",
    },
)
class EmrEksClusterProps:
    def __init__(
        self,
        *,
        eks_admin_role_arn: builtins.str,
        eks_cluster_name: typing.Optional[builtins.str] = None,
        emr_eks_nodegroups: typing.Optional[typing.Sequence["EmrEksNodegroup"]] = None,
        kubernetes_version: typing.Optional[aws_cdk.aws_eks.KubernetesVersion] = None,
    ) -> None:
        '''(experimental) The properties for the EmrEksCluster Construct class.

        :param eks_admin_role_arn: (experimental) Amazon IAM Role to be added to Amazon EKS master roles that will give access to kubernetes cluster from AWS console UI.
        :param eks_cluster_name: (experimental) Name of the Amazon EKS cluster to be created. Default: - automatically generated cluster name
        :param emr_eks_nodegroups: (experimental) List of EmrEksNodegroup to create in the cluster in addition to the default [nodegroups] {@link EmrEksNodegroup}. Default: - Don't create additional nodegroups
        :param kubernetes_version: (experimental) Kubernetes version for Amazon EKS cluster that will be created. Default: - v1.20 version is used

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "eks_admin_role_arn": eks_admin_role_arn,
        }
        if eks_cluster_name is not None:
            self._values["eks_cluster_name"] = eks_cluster_name
        if emr_eks_nodegroups is not None:
            self._values["emr_eks_nodegroups"] = emr_eks_nodegroups
        if kubernetes_version is not None:
            self._values["kubernetes_version"] = kubernetes_version

    @builtins.property
    def eks_admin_role_arn(self) -> builtins.str:
        '''(experimental) Amazon IAM Role to be added to Amazon EKS master roles that will give access to kubernetes cluster from AWS console UI.

        :stability: experimental
        '''
        result = self._values.get("eks_admin_role_arn")
        assert result is not None, "Required property 'eks_admin_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def eks_cluster_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the Amazon EKS cluster to be created.

        :default: - automatically generated cluster name

        :stability: experimental
        '''
        result = self._values.get("eks_cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def emr_eks_nodegroups(self) -> typing.Optional[typing.List["EmrEksNodegroup"]]:
        '''(experimental) List of EmrEksNodegroup to create in the cluster in addition to the default [nodegroups] {@link EmrEksNodegroup}.

        :default: - Don't create additional nodegroups

        :stability: experimental
        '''
        result = self._values.get("emr_eks_nodegroups")
        return typing.cast(typing.Optional[typing.List["EmrEksNodegroup"]], result)

    @builtins.property
    def kubernetes_version(self) -> typing.Optional[aws_cdk.aws_eks.KubernetesVersion]:
        '''(experimental) Kubernetes version for Amazon EKS cluster that will be created.

        :default: - v1.20 version is used

        :stability: experimental
        '''
        result = self._values.get("kubernetes_version")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.KubernetesVersion], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrEksClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmrEksNodegroup(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.EmrEksNodegroup",
):
    '''
    :stability: experimental
    :summary: EmrEksNodegroup containing the default Nodegroups
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CRITICAL_ALL")
    def CRITICAL_ALL(cls) -> "EmrEksNodegroupOptions":
        '''
        :stability: experimental
        '''
        return typing.cast("EmrEksNodegroupOptions", jsii.sget(cls, "CRITICAL_ALL"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NOTEBOOK_DRIVER")
    def NOTEBOOK_DRIVER(cls) -> "EmrEksNodegroupOptions":
        '''
        :stability: experimental
        '''
        return typing.cast("EmrEksNodegroupOptions", jsii.sget(cls, "NOTEBOOK_DRIVER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NOTEBOOK_EXECUTOR")
    def NOTEBOOK_EXECUTOR(cls) -> "EmrEksNodegroupOptions":
        '''(experimental) Default nodegroup configuration for EMR Studio notebooks used with EMR on EKS.

        :stability: experimental
        '''
        return typing.cast("EmrEksNodegroupOptions", jsii.sget(cls, "NOTEBOOK_EXECUTOR"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="NOTEBOOK_WITHOUT_PODTEMPLATE")
    def NOTEBOOK_WITHOUT_PODTEMPLATE(cls) -> "EmrEksNodegroupOptions":
        '''
        :stability: experimental
        '''
        return typing.cast("EmrEksNodegroupOptions", jsii.sget(cls, "NOTEBOOK_WITHOUT_PODTEMPLATE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SHARED_DRIVER")
    def SHARED_DRIVER(cls) -> "EmrEksNodegroupOptions":
        '''
        :stability: experimental
        '''
        return typing.cast("EmrEksNodegroupOptions", jsii.sget(cls, "SHARED_DRIVER"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SHARED_EXECUTOR")
    def SHARED_EXECUTOR(cls) -> "EmrEksNodegroupOptions":
        '''
        :stability: experimental
        '''
        return typing.cast("EmrEksNodegroupOptions", jsii.sget(cls, "SHARED_EXECUTOR"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TOOLING_ALL")
    def TOOLING_ALL(cls) -> "EmrEksNodegroupOptions":
        '''
        :stability: experimental
        '''
        return typing.cast("EmrEksNodegroupOptions", jsii.sget(cls, "TOOLING_ALL"))


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.EmrEksNodegroupOptions",
    jsii_struct_bases=[aws_cdk.aws_eks.NodegroupOptions],
    name_mapping={
        "ami_type": "amiType",
        "capacity_type": "capacityType",
        "desired_size": "desiredSize",
        "disk_size": "diskSize",
        "force_update": "forceUpdate",
        "instance_type": "instanceType",
        "instance_types": "instanceTypes",
        "labels": "labels",
        "launch_template_spec": "launchTemplateSpec",
        "max_size": "maxSize",
        "min_size": "minSize",
        "nodegroup_name": "nodegroupName",
        "node_role": "nodeRole",
        "release_version": "releaseVersion",
        "remote_access": "remoteAccess",
        "subnets": "subnets",
        "tags": "tags",
        "taints": "taints",
        "id": "id",
        "mount_nvme": "mountNvme",
        "subnet": "subnet",
    },
)
class EmrEksNodegroupOptions(aws_cdk.aws_eks.NodegroupOptions):
    def __init__(
        self,
        *,
        ami_type: typing.Optional[aws_cdk.aws_eks.NodegroupAmiType] = None,
        capacity_type: typing.Optional[aws_cdk.aws_eks.CapacityType] = None,
        desired_size: typing.Optional[jsii.Number] = None,
        disk_size: typing.Optional[jsii.Number] = None,
        force_update: typing.Optional[builtins.bool] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        instance_types: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.InstanceType]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        launch_template_spec: typing.Optional[aws_cdk.aws_eks.LaunchTemplateSpec] = None,
        max_size: typing.Optional[jsii.Number] = None,
        min_size: typing.Optional[jsii.Number] = None,
        nodegroup_name: typing.Optional[builtins.str] = None,
        node_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        release_version: typing.Optional[builtins.str] = None,
        remote_access: typing.Optional[aws_cdk.aws_eks.NodegroupRemoteAccess] = None,
        subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        taints: typing.Optional[typing.Sequence[aws_cdk.aws_eks.TaintSpec]] = None,
        id: builtins.str,
        mount_nvme: typing.Optional[builtins.bool] = None,
        subnet: typing.Optional[aws_cdk.aws_ec2.ISubnet] = None,
    ) -> None:
        '''(experimental) The Options for adding EmrEksNodegroup to an EmrEksCluster.

        Some of the Amazon EKS Nodegroup parameters are overriden:

        - NodegroupName by the id and an index per AZ
        - LaunchTemplate spec
        - SubnetList by either the subnet parameter or one subnet per Amazon EKS Cluster AZ.

        :param ami_type: The AMI type for your node group. Default: - auto-determined from the instanceTypes property.
        :param capacity_type: The capacity type of the nodegroup. Default: - ON_DEMAND
        :param desired_size: The current number of worker nodes that the managed node group should maintain. If not specified, the nodewgroup will initially create ``minSize`` instances. Default: 2
        :param disk_size: The root device disk size (in GiB) for your node group instances. Default: 20
        :param force_update: Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue. If an update fails because pods could not be drained, you can force the update after it fails to terminate the old node whether or not any pods are running on the node. Default: true
        :param instance_type: (deprecated) The instance type to use for your node group. Currently, you can specify a single instance type for a node group. The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the ``AL2_x86_64_GPU`` with the amiType parameter. Default: t3.medium
        :param instance_types: The instance types to use for your node group. Default: t3.medium will be used according to the cloudformation document.
        :param labels: The Kubernetes labels to be applied to the nodes in the node group when they are created. Default: - None
        :param launch_template_spec: Launch template specification used for the nodegroup. Default: - no launch template
        :param max_size: The maximum number of worker nodes that the managed node group can scale out to. Managed node groups can support up to 100 nodes by default. Default: - desiredSize
        :param min_size: The minimum number of worker nodes that the managed node group can scale in to. This number must be greater than or equal to zero. Default: 1
        :param nodegroup_name: Name of the Nodegroup. Default: - resource ID
        :param node_role: The IAM role to associate with your node group. The Amazon EKS worker node kubelet daemon makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through an IAM instance profile and associated policies. Before you can launch worker nodes and register them into a cluster, you must create an IAM role for those worker nodes to use when they are launched. Default: - None. Auto-generated if not specified.
        :param release_version: The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``). Default: - The latest available AMI version for the node group's current Kubernetes version is used.
        :param remote_access: The remote access (SSH) configuration to use with your node group. Disabled by default, however, if you specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group, then port 22 on the worker nodes is opened to the internet (0.0.0.0/0) Default: - disabled
        :param subnets: The subnets to use for the Auto Scaling group that is created for your node group. By specifying the SubnetSelection, the selected subnets will automatically apply required tags i.e. ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with the name of your cluster. Default: - private subnets
        :param tags: The metadata to apply to the node group to assist with categorization and organization. Each tag consists of a key and an optional value, both of which you define. Node group tags do not propagate to any other resources associated with the node group, such as the Amazon EC2 instances or subnets. Default: - None
        :param taints: The Kubernetes taints to be applied to the nodes in the node group when they are created. Default: - None
        :param id: (experimental) Nodegroup ID.
        :param mount_nvme: (experimental) Set to true if using instance types with local NVMe drives to mount them automatically at boot time. Default: false
        :param subnet: (experimental) Configure the Amazon EKS NodeGroup in this subnet. Use this setting for resource dependencies like an Amazon RD Default: - One NodeGroup is deployed per cluster AZ

        :stability: experimental
        '''
        if isinstance(launch_template_spec, dict):
            launch_template_spec = aws_cdk.aws_eks.LaunchTemplateSpec(**launch_template_spec)
        if isinstance(remote_access, dict):
            remote_access = aws_cdk.aws_eks.NodegroupRemoteAccess(**remote_access)
        if isinstance(subnets, dict):
            subnets = aws_cdk.aws_ec2.SubnetSelection(**subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
        }
        if ami_type is not None:
            self._values["ami_type"] = ami_type
        if capacity_type is not None:
            self._values["capacity_type"] = capacity_type
        if desired_size is not None:
            self._values["desired_size"] = desired_size
        if disk_size is not None:
            self._values["disk_size"] = disk_size
        if force_update is not None:
            self._values["force_update"] = force_update
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if labels is not None:
            self._values["labels"] = labels
        if launch_template_spec is not None:
            self._values["launch_template_spec"] = launch_template_spec
        if max_size is not None:
            self._values["max_size"] = max_size
        if min_size is not None:
            self._values["min_size"] = min_size
        if nodegroup_name is not None:
            self._values["nodegroup_name"] = nodegroup_name
        if node_role is not None:
            self._values["node_role"] = node_role
        if release_version is not None:
            self._values["release_version"] = release_version
        if remote_access is not None:
            self._values["remote_access"] = remote_access
        if subnets is not None:
            self._values["subnets"] = subnets
        if tags is not None:
            self._values["tags"] = tags
        if taints is not None:
            self._values["taints"] = taints
        if mount_nvme is not None:
            self._values["mount_nvme"] = mount_nvme
        if subnet is not None:
            self._values["subnet"] = subnet

    @builtins.property
    def ami_type(self) -> typing.Optional[aws_cdk.aws_eks.NodegroupAmiType]:
        '''The AMI type for your node group.

        :default: - auto-determined from the instanceTypes property.
        '''
        result = self._values.get("ami_type")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.NodegroupAmiType], result)

    @builtins.property
    def capacity_type(self) -> typing.Optional[aws_cdk.aws_eks.CapacityType]:
        '''The capacity type of the nodegroup.

        :default: - ON_DEMAND
        '''
        result = self._values.get("capacity_type")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.CapacityType], result)

    @builtins.property
    def desired_size(self) -> typing.Optional[jsii.Number]:
        '''The current number of worker nodes that the managed node group should maintain.

        If not specified,
        the nodewgroup will initially create ``minSize`` instances.

        :default: 2
        '''
        result = self._values.get("desired_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def disk_size(self) -> typing.Optional[jsii.Number]:
        '''The root device disk size (in GiB) for your node group instances.

        :default: 20
        '''
        result = self._values.get("disk_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def force_update(self) -> typing.Optional[builtins.bool]:
        '''Force the update if the existing node group's pods are unable to be drained due to a pod disruption budget issue.

        If an update fails because pods could not be drained, you can force the update after it fails to terminate the old
        node whether or not any pods are
        running on the node.

        :default: true
        '''
        result = self._values.get("force_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''(deprecated) The instance type to use for your node group.

        Currently, you can specify a single instance type for a node group.
        The default value for this parameter is ``t3.medium``. If you choose a GPU instance type, be sure to specify the
        ``AL2_x86_64_GPU`` with the amiType parameter.

        :default: t3.medium

        :deprecated: Use ``instanceTypes`` instead.

        :stability: deprecated
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def instance_types(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.InstanceType]]:
        '''The instance types to use for your node group.

        :default: t3.medium will be used according to the cloudformation document.

        :see: - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-eks-nodegroup.html#cfn-eks-nodegroup-instancetypes
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.InstanceType]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The Kubernetes labels to be applied to the nodes in the node group when they are created.

        :default: - None
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def launch_template_spec(
        self,
    ) -> typing.Optional[aws_cdk.aws_eks.LaunchTemplateSpec]:
        '''Launch template specification used for the nodegroup.

        :default: - no launch template

        :see: - https://docs.aws.amazon.com/eks/latest/userguide/launch-templates.html
        '''
        result = self._values.get("launch_template_spec")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.LaunchTemplateSpec], result)

    @builtins.property
    def max_size(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of worker nodes that the managed node group can scale out to.

        Managed node groups can support up to 100 nodes by default.

        :default: - desiredSize
        '''
        result = self._values.get("max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_size(self) -> typing.Optional[jsii.Number]:
        '''The minimum number of worker nodes that the managed node group can scale in to.

        This number must be greater than or equal to zero.

        :default: 1
        '''
        result = self._values.get("min_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nodegroup_name(self) -> typing.Optional[builtins.str]:
        '''Name of the Nodegroup.

        :default: - resource ID
        '''
        result = self._values.get("nodegroup_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The IAM role to associate with your node group.

        The Amazon EKS worker node kubelet daemon
        makes calls to AWS APIs on your behalf. Worker nodes receive permissions for these API calls through
        an IAM instance profile and associated policies. Before you can launch worker nodes and register them
        into a cluster, you must create an IAM role for those worker nodes to use when they are launched.

        :default: - None. Auto-generated if not specified.
        '''
        result = self._values.get("node_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def release_version(self) -> typing.Optional[builtins.str]:
        '''The AMI version of the Amazon EKS-optimized AMI to use with your node group (for example, ``1.14.7-YYYYMMDD``).

        :default: - The latest available AMI version for the node group's current Kubernetes version is used.
        '''
        result = self._values.get("release_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remote_access(self) -> typing.Optional[aws_cdk.aws_eks.NodegroupRemoteAccess]:
        '''The remote access (SSH) configuration to use with your node group.

        Disabled by default, however, if you
        specify an Amazon EC2 SSH key but do not specify a source security group when you create a managed node group,
        then port 22 on the worker nodes is opened to the internet (0.0.0.0/0)

        :default: - disabled
        '''
        result = self._values.get("remote_access")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.NodegroupRemoteAccess], result)

    @builtins.property
    def subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''The subnets to use for the Auto Scaling group that is created for your node group.

        By specifying the
        SubnetSelection, the selected subnets will automatically apply required tags i.e.
        ``kubernetes.io/cluster/CLUSTER_NAME`` with a value of ``shared``, where ``CLUSTER_NAME`` is replaced with
        the name of your cluster.

        :default: - private subnets
        '''
        result = self._values.get("subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The metadata to apply to the node group to assist with categorization and organization.

        Each tag consists of
        a key and an optional value, both of which you define. Node group tags do not propagate to any other resources
        associated with the node group, such as the Amazon EC2 instances or subnets.

        :default: - None
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def taints(self) -> typing.Optional[typing.List[aws_cdk.aws_eks.TaintSpec]]:
        '''The Kubernetes taints to be applied to the nodes in the node group when they are created.

        :default: - None
        '''
        result = self._values.get("taints")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_eks.TaintSpec]], result)

    @builtins.property
    def id(self) -> builtins.str:
        '''(experimental) Nodegroup ID.

        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mount_nvme(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Set to true if using instance types with local NVMe drives to mount them automatically at boot time.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("mount_nvme")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def subnet(self) -> typing.Optional[aws_cdk.aws_ec2.ISubnet]:
        '''(experimental) Configure the Amazon EKS NodeGroup in this subnet.

        Use this setting for resource dependencies like an Amazon RD

        :default: - One NodeGroup is deployed per cluster AZ

        :stability: experimental
        '''
        result = self._values.get("subnet")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISubnet], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrEksNodegroupOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.EmrVirtualClusterProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "create_namespace": "createNamespace",
        "eks_namespace": "eksNamespace",
    },
)
class EmrVirtualClusterProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        create_namespace: typing.Optional[builtins.bool] = None,
        eks_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The properties for the EmrVirtualCluster Construct class.

        :param name: (experimental) name of the EmrVirtualCluster to be created.
        :param create_namespace: (experimental) creates EKS namespace. Default: - Do not create the namespace
        :param eks_namespace: (experimental) name of the EKS namespace to be linked to the EMR virtual Cluster. Default: - Use the default namespace

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if create_namespace is not None:
            self._values["create_namespace"] = create_namespace
        if eks_namespace is not None:
            self._values["eks_namespace"] = eks_namespace

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) name of the  EmrVirtualCluster to be created.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def create_namespace(self) -> typing.Optional[builtins.bool]:
        '''(experimental) creates EKS namespace.

        :default: - Do not create the namespace

        :stability: experimental
        '''
        result = self._values.get("create_namespace")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def eks_namespace(self) -> typing.Optional[builtins.str]:
        '''(experimental) name of the  EKS namespace to be linked to the EMR virtual Cluster.

        :default: - Use the default namespace

        :stability: experimental
        '''
        result = self._values.get("eks_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmrVirtualClusterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Example(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.Example",
):
    '''(experimental) Example Construct to help onboarding contributors.

    This example includes best practices for code comment/documentation generation,
    and for default parameters pattern in CDK using Props with Optional properties

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        name: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the Example class with CfnOutput.

        CfnOutput can be customized.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param name: (experimental) Name used to qualify the CfnOutput in the Stack. Default: - Set to 'defaultMessage' if not provided
        :param value: (experimental) Value used in the CfnOutput in the Stack. Default: - Set to 'defaultValue!' if not provided

        :stability: experimental
        :access: public
        '''
        props = ExampleProps(name=name, value=value)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.ExampleProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ExampleProps:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The properties for the Example Construct class.

        :param name: (experimental) Name used to qualify the CfnOutput in the Stack. Default: - Set to 'defaultMessage' if not provided
        :param value: (experimental) Value used in the CfnOutput in the Stack. Default: - Set to 'defaultValue!' if not provided

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name used to qualify the CfnOutput in the Stack.

        :default: - Set to 'defaultMessage' if not provided

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''(experimental) Value used in the CfnOutput in the Stack.

        :default: - Set to 'defaultValue!' if not provided

        :stability: experimental
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExampleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FlywayRunner(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.FlywayRunner",
):
    '''(experimental) A CDK construct that runs flyway migration scripts against a redshift cluster.

    This construct is based on two main resource, an AWS Lambda hosting a flyway runner
    and one custom resource invoking it when content of migrationScriptsFolderAbsolutePath changes.

    Usage example:

    *This example assume that migration SQL files are located in ``resources/sql`` of the cdk project.::

       import * as path from 'path';
       import * as ec2 from '@aws-cdk/aws-ec2';
       import * as redshift from '@aws-cdk/aws-redshift';
       import * as cdk from '@aws-cdk/core';

       import { FlywayRunner } from 'aws-analytics-reference-architecture';

       const integTestApp = new cdk.App();
       const stack = new cdk.Stack(integTestApp, 'fywayRunnerTest');

       const vpc = new ec2.Vpc(stack, 'Vpc');

       const dbName = 'testdb';
       const cluster = new redshift.Cluster(stack, 'Redshift', {
          removalPolicy: cdk.RemovalPolicy.DESTROY,
          masterUser: {
            masterUsername: 'admin',
          },
          vpc,
          defaultDatabaseName: dbName,
       });

       new FlywayRunner(stack, 'testMigration', {
          migrationScriptsFolderAbsolutePath: path.join(__dirname, './resources/sql'),
          cluster: cluster,
          vpc: vpc,
          databaseName: dbName,
       });

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_redshift.Cluster,
        database_name: builtins.str,
        migration_scripts_folder_absolute_path: builtins.str,
        vpc: aws_cdk.aws_ec2.Vpc,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        replace_dictionary: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: (experimental) The cluster to run migration scripts against.
        :param database_name: (experimental) The database name to run migration scripts against.
        :param migration_scripts_folder_absolute_path: (experimental) The absolute path to the flyway migration scripts. Those scripts needs to follow expected flyway naming convention.
        :param vpc: (experimental) The vpc hosting the cluster.
        :param log_retention: (experimental) Period to keep the logs around. Default: logs.RetentionDays.ONE_DAY (1 day)
        :param replace_dictionary: (experimental) A key-value map of string (encapsulated between ``${`` and ``}``) to replace in the SQL files given. Example: - The SQL file:: SELECT * FROM ${TABLE_NAME}; - The replacement map:: replaceDictionary = { TABLE_NAME: 'my_table' }

        :stability: experimental
        '''
        props = FlywayRunnerProps(
            cluster=cluster,
            database_name=database_name,
            migration_scripts_folder_absolute_path=migration_scripts_folder_absolute_path,
            vpc=vpc,
            log_retention=log_retention,
            replace_dictionary=replace_dictionary,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runner")
    def runner(self) -> aws_cdk.core.CustomResource:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.core.CustomResource, jsii.get(self, "runner"))


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.FlywayRunnerProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "database_name": "databaseName",
        "migration_scripts_folder_absolute_path": "migrationScriptsFolderAbsolutePath",
        "vpc": "vpc",
        "log_retention": "logRetention",
        "replace_dictionary": "replaceDictionary",
    },
)
class FlywayRunnerProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_redshift.Cluster,
        database_name: builtins.str,
        migration_scripts_folder_absolute_path: builtins.str,
        vpc: aws_cdk.aws_ec2.Vpc,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        replace_dictionary: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties needed to run flyway migration scripts.

        :param cluster: (experimental) The cluster to run migration scripts against.
        :param database_name: (experimental) The database name to run migration scripts against.
        :param migration_scripts_folder_absolute_path: (experimental) The absolute path to the flyway migration scripts. Those scripts needs to follow expected flyway naming convention.
        :param vpc: (experimental) The vpc hosting the cluster.
        :param log_retention: (experimental) Period to keep the logs around. Default: logs.RetentionDays.ONE_DAY (1 day)
        :param replace_dictionary: (experimental) A key-value map of string (encapsulated between ``${`` and ``}``) to replace in the SQL files given. Example: - The SQL file:: SELECT * FROM ${TABLE_NAME}; - The replacement map:: replaceDictionary = { TABLE_NAME: 'my_table' }

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "database_name": database_name,
            "migration_scripts_folder_absolute_path": migration_scripts_folder_absolute_path,
            "vpc": vpc,
        }
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if replace_dictionary is not None:
            self._values["replace_dictionary"] = replace_dictionary

    @builtins.property
    def cluster(self) -> aws_cdk.aws_redshift.Cluster:
        '''(experimental) The cluster to run migration scripts against.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_redshift.Cluster, result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''(experimental) The database name to run migration scripts against.

        :stability: experimental
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def migration_scripts_folder_absolute_path(self) -> builtins.str:
        '''(experimental) The absolute path to the flyway migration scripts.

        Those scripts needs to follow expected flyway naming convention.

        :see: https://flywaydb.org/documentation/concepts/migrations.html#sql-based-migrations for more details.
        :stability: experimental
        '''
        result = self._values.get("migration_scripts_folder_absolute_path")
        assert result is not None, "Required property 'migration_scripts_folder_absolute_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.Vpc:
        '''(experimental) The vpc hosting the cluster.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.Vpc, result)

    @builtins.property
    def log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''(experimental) Period to keep the logs around.

        :default: logs.RetentionDays.ONE_DAY (1 day)

        :stability: experimental
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def replace_dictionary(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) A key-value map of string (encapsulated between ``${`` and ``}``) to replace in the SQL files given.

        Example:

        - The SQL file::

             SELECT * FROM ${TABLE_NAME};
        - The replacement map::

             replaceDictionary = {
               TABLE_NAME: 'my_table'
             }

        :stability: experimental
        '''
        result = self._values.get("replace_dictionary")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FlywayRunnerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PartitionedDataset(
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.PartitionedDataset",
):
    '''(experimental) PartitionedDataset enum-like class providing pre-defined datasets metadata and custom dataset creation.

    PartitionDataset has following properties:

    1. Data is partitioned by timestamp (in seconds). Each folder stores data within a given range.
       There is no constraint on how long the timestange range can be. But each file must not be larger tahn 100MB.
       Here is an example:
       |- time_range_start=16000000000
       |- file1.csv 100MB
       |- file2.csv 50MB
       |- time_range_start=16000000300 // 5 minute range (300 sec)
       |- file1.csv 1MB
       |- time_range_start=16000000600
       |- file1.csv 100MB
       |- file2.csv 100MB
       |- whichever-file-name-is-fine-as-we-have-manifest-files.csv 50MB
    2. It has a manefest CSV file with two columns: start and path. Start is the timestamp
       start        , path
       16000000000  , s3://///time_range_start=16000000000/file1.csv
       16000000000  , s3://///time_range_start=16000000000/file2.csv
       16000000300  , s3://///time_range_start=16000000300/file1.csv
       16000000600  , s3://///time_range_start=16000000600/file1.csv
       16000000600  , s3://///time_range_start=16000000600/file2.csv
       16000000600  , s3://///time_range_start=16000000600/whichever-file....csv

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        date_time_column_to_filter: builtins.str,
        location: aws_cdk.aws_s3.Location,
        manifest_location: aws_cdk.aws_s3.Location,
        start_datetime: builtins.str,
        date_time_columns_to_adjust: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the Dataset class.

        :param date_time_column_to_filter: (experimental) Datetime column for filtering data.
        :param location: (experimental) The Amazon S3 Location of the source dataset. It's composed of an Amazon S3 bucketName and an Amazon S3 objectKey
        :param manifest_location: (experimental) Manifest file in csv format with two columns: start, path.
        :param start_datetime: (experimental) The minimum datetime value in the dataset used to calculate time offset.
        :param date_time_columns_to_adjust: (experimental) Array of column names with datetime to adjust. The source data will have date in the past 2021-01-01T00:00:00 while the data replayer will have have the current time. The difference (aka. offset) must be added to all datetime columns

        :stability: experimental
        :access: public
        '''
        props = PartitionedDatasetProps(
            date_time_column_to_filter=date_time_column_to_filter,
            location=location,
            manifest_location=manifest_location,
            start_datetime=start_datetime,
            date_time_columns_to_adjust=date_time_columns_to_adjust,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DATASETS_BUCKET")
    def DATASETS_BUCKET(cls) -> builtins.str:
        '''(experimental) The bucket name of the AWS Analytics Reference Architecture datasets.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "DATASETS_BUCKET"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RETAIL_1GB_WEB_SALE")
    def RETAIL_1_GB_WEB_SALE(cls) -> "PartitionedDataset":
        '''(experimental) The web sale dataset part of 1GB retail datasets.

        :stability: experimental
        '''
        return typing.cast("PartitionedDataset", jsii.sget(cls, "RETAIL_1GB_WEB_SALE"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateTimeColumnToFilter")
    def date_time_column_to_filter(self) -> builtins.str:
        '''(experimental) Datetime column for filtering data.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "dateTimeColumnToFilter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="location")
    def location(self) -> aws_cdk.aws_s3.Location:
        '''(experimental) The Amazon S3 Location of the source dataset.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Location, jsii.get(self, "location"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manifestLocation")
    def manifest_location(self) -> aws_cdk.aws_s3.Location:
        '''(experimental) Manifest file in csv format with two columns: start, path.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Location, jsii.get(self, "manifestLocation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="offset")
    def offset(self) -> jsii.Number:
        '''(experimental) The offset of the Dataset (difference between min datetime and now) in Seconds.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "offset"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startDateTime")
    def start_date_time(self) -> builtins.str:
        '''(experimental) Start datetime replaying this dataset.

        Your data set may start from 1 Jan 2020
        But you can specify this to 1 Feb 2020 to omit the first month data.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "startDateTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tableName")
    def table_name(self) -> builtins.str:
        '''(experimental) The name of the SQL table extracted from path.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dateTimeColumnsToAdjust")
    def date_time_columns_to_adjust(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Array of column names with datetime to adjust.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dateTimeColumnsToAdjust"))


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.PartitionedDatasetProps",
    jsii_struct_bases=[],
    name_mapping={
        "date_time_column_to_filter": "dateTimeColumnToFilter",
        "location": "location",
        "manifest_location": "manifestLocation",
        "start_datetime": "startDatetime",
        "date_time_columns_to_adjust": "dateTimeColumnsToAdjust",
    },
)
class PartitionedDatasetProps:
    def __init__(
        self,
        *,
        date_time_column_to_filter: builtins.str,
        location: aws_cdk.aws_s3.Location,
        manifest_location: aws_cdk.aws_s3.Location,
        start_datetime: builtins.str,
        date_time_columns_to_adjust: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param date_time_column_to_filter: (experimental) Datetime column for filtering data.
        :param location: (experimental) The Amazon S3 Location of the source dataset. It's composed of an Amazon S3 bucketName and an Amazon S3 objectKey
        :param manifest_location: (experimental) Manifest file in csv format with two columns: start, path.
        :param start_datetime: (experimental) The minimum datetime value in the dataset used to calculate time offset.
        :param date_time_columns_to_adjust: (experimental) Array of column names with datetime to adjust. The source data will have date in the past 2021-01-01T00:00:00 while the data replayer will have have the current time. The difference (aka. offset) must be added to all datetime columns

        :stability: experimental
        '''
        if isinstance(location, dict):
            location = aws_cdk.aws_s3.Location(**location)
        if isinstance(manifest_location, dict):
            manifest_location = aws_cdk.aws_s3.Location(**manifest_location)
        self._values: typing.Dict[str, typing.Any] = {
            "date_time_column_to_filter": date_time_column_to_filter,
            "location": location,
            "manifest_location": manifest_location,
            "start_datetime": start_datetime,
        }
        if date_time_columns_to_adjust is not None:
            self._values["date_time_columns_to_adjust"] = date_time_columns_to_adjust

    @builtins.property
    def date_time_column_to_filter(self) -> builtins.str:
        '''(experimental) Datetime column for filtering data.

        :stability: experimental
        '''
        result = self._values.get("date_time_column_to_filter")
        assert result is not None, "Required property 'date_time_column_to_filter' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> aws_cdk.aws_s3.Location:
        '''(experimental) The Amazon S3 Location of the source dataset.

        It's composed of an Amazon S3 bucketName and an Amazon S3 objectKey

        :stability: experimental
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(aws_cdk.aws_s3.Location, result)

    @builtins.property
    def manifest_location(self) -> aws_cdk.aws_s3.Location:
        '''(experimental) Manifest file in csv format with two columns: start, path.

        :stability: experimental
        '''
        result = self._values.get("manifest_location")
        assert result is not None, "Required property 'manifest_location' is missing"
        return typing.cast(aws_cdk.aws_s3.Location, result)

    @builtins.property
    def start_datetime(self) -> builtins.str:
        '''(experimental) The minimum datetime value in the dataset used to calculate time offset.

        :stability: experimental
        '''
        result = self._values.get("start_datetime")
        assert result is not None, "Required property 'start_datetime' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def date_time_columns_to_adjust(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Array of column names with datetime to adjust.

        The source data will have date in the past 2021-01-01T00:00:00 while
        the data replayer will have have the current time. The difference (aka. offset)
        must be added to all datetime columns

        :stability: experimental
        '''
        result = self._values.get("date_time_columns_to_adjust")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PartitionedDatasetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SingletonBucket(
    aws_cdk.aws_s3.Bucket,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.SingletonBucket",
):
    '''(experimental) An Amazon S3 Bucket implementing the singleton pattern.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_control: typing.Optional[aws_cdk.aws_s3.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[aws_cdk.aws_s3.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[aws_cdk.aws_s3.CorsRule]] = None,
        encryption: typing.Optional[aws_cdk.aws_s3.BucketEncryption] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        inventories: typing.Optional[typing.Sequence[aws_cdk.aws_s3.Inventory]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[aws_cdk.aws_s3.LifecycleRule]] = None,
        metrics: typing.Optional[typing.Sequence[aws_cdk.aws_s3.BucketMetrics]] = None,
        object_ownership: typing.Optional[aws_cdk.aws_s3.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        server_access_logs_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[aws_cdk.aws_s3.RedirectTarget] = None,
        website_routing_rules: typing.Optional[typing.Sequence[aws_cdk.aws_s3.RoutingRule]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``, switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to all objects in the bucket being deleted. Be sure to update your bucket resources by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Specifies whether Amazon S3 should use an S3 Bucket Key with server-side encryption using KMS (SSE-KMS) for new objects in the bucket. Only relevant, when Encryption is set to {@link BucketEncryption.KMS} Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``Kms`` if ``encryptionKey`` is specified, or ``Unencrypted`` otherwise.
        :param encryption_key: External KMS key to use for bucket encryption. The 'encryption' property must be either not specified or set to "Kms". An error will be emitted if encryption is set to "Unencrypted" or "Managed". Default: - If encryption is set to "Kms" and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration, uploading account will own the object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.
        '''
        props = aws_cdk.aws_s3.BucketProps(
            access_control=access_control,
            auto_delete_objects=auto_delete_objects,
            block_public_access=block_public_access,
            bucket_key_enabled=bucket_key_enabled,
            bucket_name=bucket_name,
            cors=cors,
            encryption=encryption,
            encryption_key=encryption_key,
            enforce_ssl=enforce_ssl,
            inventories=inventories,
            lifecycle_rules=lifecycle_rules,
            metrics=metrics,
            object_ownership=object_ownership,
            public_read_access=public_read_access,
            removal_policy=removal_policy,
            server_access_logs_bucket=server_access_logs_bucket,
            server_access_logs_prefix=server_access_logs_prefix,
            versioned=versioned,
            website_error_document=website_error_document,
            website_index_document=website_index_document,
            website_redirect=website_redirect,
            website_routing_rules=website_routing_rules,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getOrCreate") # type: ignore[misc]
    @builtins.classmethod
    def get_or_create(
        cls,
        scope: aws_cdk.core.Construct,
        bucket_name: builtins.str,
    ) -> aws_cdk.aws_s3.Bucket:
        '''(experimental) Get the Amazon S3 Bucket from the AWS CDK Stack based on the provided name.

        The method adds a prefix (ara-) and a suffix (-{ACCOUNT_ID}) to the provided name.
        If no bucket exists, it creates a new one.

        :param scope: -
        :param bucket_name: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.sinvoke(cls, "getOrCreate", [scope, bucket_name]))


class SingletonGlueDefaultRole(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.SingletonGlueDefaultRole",
):
    '''(experimental) SingletonGlueDefaultRole Construct to automatically setup a new Amazon IAM role to use with AWS Glue jobs.

    The role is created with AWSGlueServiceRole policy and authorize all actions on S3.
    The Construct provides a getOrCreate method for SingletonInstantiation

    :stability: experimental
    '''

    @jsii.member(jsii_name="getOrCreate") # type: ignore[misc]
    @builtins.classmethod
    def get_or_create(cls, scope: aws_cdk.core.Construct) -> "SingletonGlueDefaultRole":
        '''
        :param scope: -

        :stability: experimental
        '''
        return typing.cast("SingletonGlueDefaultRole", jsii.sinvoke(cls, "getOrCreate", [scope]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamRole")
    def iam_role(self) -> aws_cdk.aws_iam.Role:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "iamRole"))


class SynchronousAthenaQuery(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.SynchronousAthenaQuery",
):
    '''(experimental) SynchronousAthenaQuery Construct to execute an Amazon Athena query synchronously.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        result_path: aws_cdk.aws_s3.Location,
        statement: builtins.str,
        execution_role_statements: typing.Optional[typing.Sequence[aws_cdk.aws_iam.PolicyStatement]] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the SynchronousAthenaQuery class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param result_path: (experimental) The Amazon S3 Location for the query results (without trailing slash).
        :param statement: (experimental) The name of the Athena query to execute.
        :param execution_role_statements: (experimental) The Amazon IAM Policy Statements used to run the query. Default: - No Policy Statements are added to the execution role
        :param timeout: (experimental) The timeout in seconds to wait for query success. Default: - 60 seconds

        :stability: experimental
        :access: public
        '''
        props = SynchronousAthenaQueryProps(
            result_path=result_path,
            statement=statement,
            execution_role_statements=execution_role_statements,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.SynchronousAthenaQueryProps",
    jsii_struct_bases=[],
    name_mapping={
        "result_path": "resultPath",
        "statement": "statement",
        "execution_role_statements": "executionRoleStatements",
        "timeout": "timeout",
    },
)
class SynchronousAthenaQueryProps:
    def __init__(
        self,
        *,
        result_path: aws_cdk.aws_s3.Location,
        statement: builtins.str,
        execution_role_statements: typing.Optional[typing.Sequence[aws_cdk.aws_iam.PolicyStatement]] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The properties for SynchronousAthenaQuery Construct.

        :param result_path: (experimental) The Amazon S3 Location for the query results (without trailing slash).
        :param statement: (experimental) The name of the Athena query to execute.
        :param execution_role_statements: (experimental) The Amazon IAM Policy Statements used to run the query. Default: - No Policy Statements are added to the execution role
        :param timeout: (experimental) The timeout in seconds to wait for query success. Default: - 60 seconds

        :stability: experimental
        '''
        if isinstance(result_path, dict):
            result_path = aws_cdk.aws_s3.Location(**result_path)
        self._values: typing.Dict[str, typing.Any] = {
            "result_path": result_path,
            "statement": statement,
        }
        if execution_role_statements is not None:
            self._values["execution_role_statements"] = execution_role_statements
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def result_path(self) -> aws_cdk.aws_s3.Location:
        '''(experimental) The Amazon S3 Location for the query results (without trailing slash).

        :stability: experimental
        '''
        result = self._values.get("result_path")
        assert result is not None, "Required property 'result_path' is missing"
        return typing.cast(aws_cdk.aws_s3.Location, result)

    @builtins.property
    def statement(self) -> builtins.str:
        '''(experimental) The name of the Athena query to execute.

        :stability: experimental
        '''
        result = self._values.get("statement")
        assert result is not None, "Required property 'statement' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def execution_role_statements(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]]:
        '''(experimental) The Amazon IAM Policy Statements used to run the query.

        :default: - No Policy Statements are added to the execution role

        :stability: experimental
        '''
        result = self._values.get("execution_role_statements")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The timeout in seconds to wait for query success.

        :default: - 60 seconds

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SynchronousAthenaQueryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SynchronousCrawler(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="aws-analytics-reference-architecture.SynchronousCrawler",
):
    '''(experimental) CrawlerStartWait Construct to start an AWS Glue Crawler execution and asynchronously wait for completion.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        crawler_name: builtins.str,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Constructs a new instance of the DataGenerator class.

        :param scope: the Scope of the CDK Construct.
        :param id: the ID of the CDK Construct.
        :param crawler_name: (experimental) The name of the Crawler to use.
        :param timeout: (experimental) The timeout in seconds to wait for the Crawler success. Default: - 300 seconds

        :stability: experimental
        :access: public
        '''
        props = SynchronousCrawlerProps(crawler_name=crawler_name, timeout=timeout)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="aws-analytics-reference-architecture.SynchronousCrawlerProps",
    jsii_struct_bases=[],
    name_mapping={"crawler_name": "crawlerName", "timeout": "timeout"},
)
class SynchronousCrawlerProps:
    def __init__(
        self,
        *,
        crawler_name: builtins.str,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) The properties for SynchronousCrawler Construct.

        :param crawler_name: (experimental) The name of the Crawler to use.
        :param timeout: (experimental) The timeout in seconds to wait for the Crawler success. Default: - 300 seconds

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "crawler_name": crawler_name,
        }
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def crawler_name(self) -> builtins.str:
        '''(experimental) The name of the Crawler to use.

        :stability: experimental
        '''
        result = self._values.get("crawler_name")
        assert result is not None, "Required property 'crawler_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The timeout in seconds to wait for the Crawler success.

        :default: - 300 seconds

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SynchronousCrawlerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AthenaDefaultSetup",
    "BatchReplayer",
    "BatchReplayerProps",
    "DataGenerator",
    "DataGeneratorProps",
    "DataLakeCatalog",
    "DataLakeExporter",
    "DataLakeExporterProps",
    "DataLakeStorage",
    "DataLakeStorageProps",
    "Dataset",
    "DatasetProps",
    "Ec2SsmRole",
    "EmrEksCluster",
    "EmrEksClusterProps",
    "EmrEksNodegroup",
    "EmrEksNodegroupOptions",
    "EmrVirtualClusterProps",
    "Example",
    "ExampleProps",
    "FlywayRunner",
    "FlywayRunnerProps",
    "PartitionedDataset",
    "PartitionedDatasetProps",
    "SingletonBucket",
    "SingletonGlueDefaultRole",
    "SynchronousAthenaQuery",
    "SynchronousAthenaQueryProps",
    "SynchronousCrawler",
    "SynchronousCrawlerProps",
]

publication.publish()
