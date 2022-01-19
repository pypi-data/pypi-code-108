'''
# aws-kinesisstreams-gluejob module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**: | <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span> |
| :--------------------------- | :------------------------------------------------------------------------------------------------ |

<div style="height:8px"></div>

| **Language**                                                                                   | **Package**                                                    |
| :--------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| ![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python             | `aws_solutions_constructs.aws_kinesis_streams_gluejob`         |
| ![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript | `@aws-solutions-constructs/aws-kinesisstreams-gluejob`         |
| ![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java                   | `software.amazon.awsconstructs.services.kinesisstreamsgluejob` |

This AWS Solutions Construct deploys a Kinesis Stream and configures a AWS Glue Job to perform custom ETL transformation with the appropriate resources/properties for interaction and security. It also creates an S3 bucket where the python script for the AWS Glue Job can be uploaded.

Here is a minimal deployable pattern definition in Typescript:

```javascript
import * as glue from '@aws-cdk/aws-glue';
import * as s3assets from '@aws-cdk/aws-s3-assets';
import {KinesisstreamsToGluejob} from '@aws-solutions-constructs/aws-kinesisstreams-gluejob';

const fieldSchema: glue.CfnTable.ColumnProperty[] = [
    {
        name: 'id',
        type: 'int',
        comment: 'Identifier for the record',
    },
    {
        name: 'name',
        type: 'string',
        comment: 'Name for the record',
    },
    {
        name: 'address',
        type: 'string',
        comment: 'Address for the record',
    },
    {
        name: 'value',
        type: 'int',
        comment: 'Value for the record',
    },
];

const customEtlJob = new KinesisstreamsToGluejob(this, 'CustomETL', {
    glueJobProps: {
        command: {
            name: 'gluestreaming',
            pythonVersion: '3',
            scriptLocation: new s3assets.Asset(this, 'ScriptLocation', {
                path: `${__dirname}/../etl/transform.py`,
            }).s3ObjectUrl,
        },
    },
    fieldSchema: fieldSchema,
});
```

## Initializer

```text
new KinesisstreamsToGluejob(scope: Construct, id: string, props: KinesisstreamsToGluejobProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`KinesisstreamsToGluejobProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**            | **Type**                                                                                                                      | **Description**                                                                                                  |
| :------------------ | :---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| existingStreamObj?  | [`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.Stream.html)                          | Existing instance of Kinesis Stream, providing both this and `kinesisStreamProps` will cause an error.                          |
| kinesisStreamProps? | [`kinesis.StreamProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.StreamProps.html)                | Optional user-provided props to override the default props for the Kinesis stream.                               |
| glueJobProps?       | [`cfnJob.CfnJobProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.CfnJobProps.html)                    | User provided props to override the default props for the AWS Glue Job.                                          |
| existingGlueJob?    | [`cfnJob.CfnJob`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.CfnJob.html)                              | Existing instance of AWS Glue Job, providing both this and `glueJobProps` will cause an error.                         |
| fieldSchema?        | [`CfnTable.ColumnProperty[]`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.CfnTable.ColumnProperty.html) | User provided schema structure to create an AWS Glue Table.                                                      |
| existingTable?      | [`CfnTable`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.CfnTable.html)                                 | Existing instance of AWS Glue Table. If this is set, tableProps and fieldSchema are ignored.                     |
| tableProps?         | [`CfnTableProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.TableProps.html)                          | User provided AWS Glue Table props to override default props used to create a Glue Table.                        |
| existingDatabase?   | [`CfnDatabase`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.CfnDatabase.html)                           | Existing instance of AWS Glue Database. If this is set, then databaseProps is ignored.                           |
| databaseProps?      | [`CfnDatabaseProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.CfnDatabaseProps.html)                 | User provided Glue Database Props to override the default props used to create the Glue Database.                |
| outputDataStore?    | [`SinkDataStoreProps`](#sinkdatastoreprops)                                                                                   | User provided properties for S3 bucket that stores Glue Job output. Current datastore types suported is only S3. |
|createCloudWatchAlarms?|`boolean`|Whether to create recommended CloudWatch alarms for Kinesis Data Stream. Default value is set to `true`.|

### SinkDataStoreProps

| **Name**                | **Type**                                                                                          | **Description**                                                                                                |
| :---------------------- | :------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| existingS3OutputBucket? | [`Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)           | Existing instance of S3 bucket where the data should be written. Providing both this and `outputBucketProps` will cause an error. |
| outputBucketProps       | [`BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html) | User provided bucket properties to create the S3 bucket to store the output from the AWS Glue Job.             |
| datastoreType           | [`SinkStoreType`](#sinkstoretype)                                                                 | Sink data store type.                                                                                          |

### SinkStoreType

Enumeration of data store types that could include S3, DynamoDB, DocumentDB, RDS or Redshift. Current construct implementation only supports S3, but potential to add other output types in the future.

| **Name** | **Type** | **Description** |
| :------- | :------- | --------------- |
| S3       | `string` | S3 storage type |

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|kinesisStream|[`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.Stream.html)|Returns an instance of the Kinesis stream created or used by the pattern.|
|glueJob|[`CfnJob`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.CfnJob.html)|Returns an instance of AWS Glue Job created by the construct.|
|glueJobRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the IAM Role created by the construct for the Glue Job.|
|database|[`CfnDatabase`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.CfnDatabase.html)|Returns an instance of AWS Glue Database created by the construct.|
|table|[`CfnTable`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-glue.CfnTable.html)|Returns an instance of the AWS Glue Table created by the construct|
|outputBucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-s3-readme.html)|Returns an instance of the output bucket created by the construct for the AWS Glue Job.|
|cloudwatchAlarms?|[`cloudwatch.Alarm[]`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudwatch.Alarm.html)|Returns an array of recommended CloudWatch Alarms created by the construct for Kinesis Data stream.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon Kinesis Stream

* Configure least privilege access IAM role for Kinesis Stream
* Enable server-side encryption for Kinesis Stream using AWS Managed KMS Key
* Deploy best practices CloudWatch Alarms for the Kinesis Stream

### Glue Job

* Create a Glue Security Config that configures encryption for CloudWatch, Job Bookmarks, and S3. CloudWatch and Job Bookmarks are encrypted using AWS Managed KMS Key created for AWS Glue Service. The S3 bucket is configured with SSE-S3 encryption mode
* Configure service role policies that allow AWS Glue to read from Kinesis Data Streams

### Glue Database

* Create an AWS Glue database. An AWS Glue Table will be added to the database. This table defines the schema for the records buffered in the Amazon Kinesis Data Streams

### Glue Table

* Create an AWS Glue table. The table schema definition is based on the JSON structure of the records buffered in the Amazon Kinesis Data Streams

### IAM Role

* A job execution role that has privileges to 1) read the ETL script from the S3 bucket location, 2) read records from the Kinesis Stream, and 3) execute the Glue Job

### Output S3 Bucket

* An S3 bucket to store the output of the ETL transformation. This bucket will be passed as an argument to the created glue job so that it can be used in the ETL script to write data into it

### Cloudwatch Alarms

* A CloudWatch Alarm to report when consumer application is reading data slower than expected
* A CloudWatch Alarm to report when consumer record processing is falling behind (to avoid risk of data loss due to record expiration)

## Architecture

![Architecture Diagram](architecture.png)

## Reference Implementation

A sample use case which uses this pattern is available under [`use_cases/aws-custom-glue-etl`](https://github.com/awslabs/aws-solutions-constructs/tree/master/source/use_cases/aws-custom-glue-etl).

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

import aws_cdk.aws_cloudwatch
import aws_cdk.aws_glue
import aws_cdk.aws_iam
import aws_cdk.aws_kinesis
import aws_cdk.core
import aws_solutions_constructs.core


class KinesisstreamsToGluejob(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-kinesisstreams-gluejob.KinesisstreamsToGluejob",
):
    '''
    :summary:

    = This construct either creates or uses the existing construct provided that can be deployed
    to perform streaming ETL operations using:

    - AWS Glue Database
    - AWS Glue Table
    - AWS Glue Job
    - Amazon Kinesis Data Streams
    - Amazon S3 Bucket (output datastore).
    The construct also configures the required role policies so that AWS Glue Job can read data from
    the streams, process it, and write to an output store.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        database_props: typing.Optional[aws_cdk.aws_glue.CfnDatabaseProps] = None,
        existing_database: typing.Optional[aws_cdk.aws_glue.CfnDatabase] = None,
        existing_glue_job: typing.Optional[aws_cdk.aws_glue.CfnJob] = None,
        existing_stream_obj: typing.Optional[aws_cdk.aws_kinesis.Stream] = None,
        existing_table: typing.Optional[aws_cdk.aws_glue.CfnTable] = None,
        field_schema: typing.Optional[typing.Sequence[aws_cdk.aws_glue.CfnTable.ColumnProperty]] = None,
        glue_job_props: typing.Any = None,
        kinesis_stream_props: typing.Any = None,
        output_data_store: typing.Optional[aws_solutions_constructs.core.SinkDataStoreProps] = None,
        table_props: typing.Optional[aws_cdk.aws_glue.CfnTableProps] = None,
    ) -> None:
        '''Constructs a new instance of KinesisstreamsToGluejob.Based on the values set in the @props.

        :param scope: -
        :param id: -
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param database_props: The props for the Glue database that the construct should use to create. If @database is set then this property is ignored. If none of @database and @databaseprops is provided, the construct will define a GlueDatabase resoruce.
        :param existing_database: Glue Database for this construct. If not provided the construct will create a new Glue Database. The database is where the schema for the data in Kinesis Data Streams is stored
        :param existing_glue_job: Existing GlueJob configuration. If this property is provided, any properties provided through @glueJobProps is ignored
        :param existing_stream_obj: Existing instance of Kineses Data Stream. If not set, it will create an instance
        :param existing_table: Glue Table for this construct, If not provided the construct will create a new Table in the database. This table should define the schema for the records in the Kinesis Data Streams. One of @tableprops or @table or @fieldSchema is mandatory. If @tableprops is provided then
        :param field_schema: Structure of the records in the Amazon Kinesis Data Streams. An example of such a definition is as below. Either @table or @fieldSchema is mandatory. If @table is provided then @fieldSchema is ignored "FieldSchema": [{ "name": "id", "type": "int", "comment": "Identifier for the record" }, { "name": "name", "type": "string", "comment": "The name of the record" }, { "name": "type", "type": "string", "comment": "The type of the record" }, { "name": "numericvalue", "type": "int", "comment": "Some value associated with the record" }, Default: - None
        :param glue_job_props: User provides props to override the default props for Glue ETL Jobs. Providing both this and existingGlueJob will cause an error. This parameter is defined as ``any`` to not enforce passing the Glue Job role which is a mandatory parameter for CfnJobProps. If a role is not passed, the construct creates one for you and attaches the appropriate role policies The default props will set the Glue Version 2.0, with 2 Workers and WorkerType as G1.X. For details on defining a Glue Job, please refer the following link for documentation - https://docs.aws.amazon.com/glue/latest/webapi/API_Job.html Default: - None
        :param kinesis_stream_props: User provided props to override the default props for the Kinesis Stream. Default: - Default props are used
        :param output_data_store: The output data stores where the transformed data should be written. Current supported data stores include only S3, other potential stores may be added in the future.
        :param table_props: The table properties for the construct to create the table. One of @tableprops or @table or @fieldSchema is mandatory. If @tableprops is provided then @table and @fieldSchema are ignored. If @table is provided, @fieldSchema is ignored
        '''
        props = KinesisstreamsToGluejobProps(
            create_cloud_watch_alarms=create_cloud_watch_alarms,
            database_props=database_props,
            existing_database=existing_database,
            existing_glue_job=existing_glue_job,
            existing_stream_obj=existing_stream_obj,
            existing_table=existing_table,
            field_schema=field_schema,
            glue_job_props=glue_job_props,
            kinesis_stream_props=kinesis_stream_props,
            output_data_store=output_data_store,
            table_props=table_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> aws_cdk.aws_glue.CfnDatabase:
        return typing.cast(aws_cdk.aws_glue.CfnDatabase, jsii.get(self, "database"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="glueJob")
    def glue_job(self) -> aws_cdk.aws_glue.CfnJob:
        return typing.cast(aws_cdk.aws_glue.CfnJob, jsii.get(self, "glueJob"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="glueJobRole")
    def glue_job_role(self) -> aws_cdk.aws_iam.IRole:
        return typing.cast(aws_cdk.aws_iam.IRole, jsii.get(self, "glueJobRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisStream")
    def kinesis_stream(self) -> aws_cdk.aws_kinesis.Stream:
        return typing.cast(aws_cdk.aws_kinesis.Stream, jsii.get(self, "kinesisStream"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_glue.CfnTable:
        return typing.cast(aws_cdk.aws_glue.CfnTable, jsii.get(self, "table"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchAlarms")
    def cloudwatch_alarms(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]]:
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudwatch.Alarm]], jsii.get(self, "cloudwatchAlarms"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputBucket")
    def output_bucket(self) -> typing.Optional[typing.Mapping[typing.Any, typing.Any]]:
        '''This property is only set if the Glue Job is created by the construct.

        If an exisiting Glue Job
        configuraton is supplied, the construct does not create an S3 bucket and hence the @outputBucket
        property is undefined
        '''
        return typing.cast(typing.Optional[typing.Mapping[typing.Any, typing.Any]], jsii.get(self, "outputBucket"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-kinesisstreams-gluejob.KinesisstreamsToGluejobProps",
    jsii_struct_bases=[],
    name_mapping={
        "create_cloud_watch_alarms": "createCloudWatchAlarms",
        "database_props": "databaseProps",
        "existing_database": "existingDatabase",
        "existing_glue_job": "existingGlueJob",
        "existing_stream_obj": "existingStreamObj",
        "existing_table": "existingTable",
        "field_schema": "fieldSchema",
        "glue_job_props": "glueJobProps",
        "kinesis_stream_props": "kinesisStreamProps",
        "output_data_store": "outputDataStore",
        "table_props": "tableProps",
    },
)
class KinesisstreamsToGluejobProps:
    def __init__(
        self,
        *,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        database_props: typing.Optional[aws_cdk.aws_glue.CfnDatabaseProps] = None,
        existing_database: typing.Optional[aws_cdk.aws_glue.CfnDatabase] = None,
        existing_glue_job: typing.Optional[aws_cdk.aws_glue.CfnJob] = None,
        existing_stream_obj: typing.Optional[aws_cdk.aws_kinesis.Stream] = None,
        existing_table: typing.Optional[aws_cdk.aws_glue.CfnTable] = None,
        field_schema: typing.Optional[typing.Sequence[aws_cdk.aws_glue.CfnTable.ColumnProperty]] = None,
        glue_job_props: typing.Any = None,
        kinesis_stream_props: typing.Any = None,
        output_data_store: typing.Optional[aws_solutions_constructs.core.SinkDataStoreProps] = None,
        table_props: typing.Optional[aws_cdk.aws_glue.CfnTableProps] = None,
    ) -> None:
        '''
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param database_props: The props for the Glue database that the construct should use to create. If @database is set then this property is ignored. If none of @database and @databaseprops is provided, the construct will define a GlueDatabase resoruce.
        :param existing_database: Glue Database for this construct. If not provided the construct will create a new Glue Database. The database is where the schema for the data in Kinesis Data Streams is stored
        :param existing_glue_job: Existing GlueJob configuration. If this property is provided, any properties provided through @glueJobProps is ignored
        :param existing_stream_obj: Existing instance of Kineses Data Stream. If not set, it will create an instance
        :param existing_table: Glue Table for this construct, If not provided the construct will create a new Table in the database. This table should define the schema for the records in the Kinesis Data Streams. One of @tableprops or @table or @fieldSchema is mandatory. If @tableprops is provided then
        :param field_schema: Structure of the records in the Amazon Kinesis Data Streams. An example of such a definition is as below. Either @table or @fieldSchema is mandatory. If @table is provided then @fieldSchema is ignored "FieldSchema": [{ "name": "id", "type": "int", "comment": "Identifier for the record" }, { "name": "name", "type": "string", "comment": "The name of the record" }, { "name": "type", "type": "string", "comment": "The type of the record" }, { "name": "numericvalue", "type": "int", "comment": "Some value associated with the record" }, Default: - None
        :param glue_job_props: User provides props to override the default props for Glue ETL Jobs. Providing both this and existingGlueJob will cause an error. This parameter is defined as ``any`` to not enforce passing the Glue Job role which is a mandatory parameter for CfnJobProps. If a role is not passed, the construct creates one for you and attaches the appropriate role policies The default props will set the Glue Version 2.0, with 2 Workers and WorkerType as G1.X. For details on defining a Glue Job, please refer the following link for documentation - https://docs.aws.amazon.com/glue/latest/webapi/API_Job.html Default: - None
        :param kinesis_stream_props: User provided props to override the default props for the Kinesis Stream. Default: - Default props are used
        :param output_data_store: The output data stores where the transformed data should be written. Current supported data stores include only S3, other potential stores may be added in the future.
        :param table_props: The table properties for the construct to create the table. One of @tableprops or @table or @fieldSchema is mandatory. If @tableprops is provided then @table and @fieldSchema are ignored. If @table is provided, @fieldSchema is ignored
        '''
        if isinstance(database_props, dict):
            database_props = aws_cdk.aws_glue.CfnDatabaseProps(**database_props)
        if isinstance(output_data_store, dict):
            output_data_store = aws_solutions_constructs.core.SinkDataStoreProps(**output_data_store)
        if isinstance(table_props, dict):
            table_props = aws_cdk.aws_glue.CfnTableProps(**table_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if create_cloud_watch_alarms is not None:
            self._values["create_cloud_watch_alarms"] = create_cloud_watch_alarms
        if database_props is not None:
            self._values["database_props"] = database_props
        if existing_database is not None:
            self._values["existing_database"] = existing_database
        if existing_glue_job is not None:
            self._values["existing_glue_job"] = existing_glue_job
        if existing_stream_obj is not None:
            self._values["existing_stream_obj"] = existing_stream_obj
        if existing_table is not None:
            self._values["existing_table"] = existing_table
        if field_schema is not None:
            self._values["field_schema"] = field_schema
        if glue_job_props is not None:
            self._values["glue_job_props"] = glue_job_props
        if kinesis_stream_props is not None:
            self._values["kinesis_stream_props"] = kinesis_stream_props
        if output_data_store is not None:
            self._values["output_data_store"] = output_data_store
        if table_props is not None:
            self._values["table_props"] = table_props

    @builtins.property
    def create_cloud_watch_alarms(self) -> typing.Optional[builtins.bool]:
        '''Whether to create recommended CloudWatch alarms.

        :default: - Alarms are created
        '''
        result = self._values.get("create_cloud_watch_alarms")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def database_props(self) -> typing.Optional[aws_cdk.aws_glue.CfnDatabaseProps]:
        '''The props for the Glue database that the construct should use to create.

        If @database is set
        then this property is ignored. If none of @database and @databaseprops is provided, the
        construct will define a GlueDatabase resoruce.
        '''
        result = self._values.get("database_props")
        return typing.cast(typing.Optional[aws_cdk.aws_glue.CfnDatabaseProps], result)

    @builtins.property
    def existing_database(self) -> typing.Optional[aws_cdk.aws_glue.CfnDatabase]:
        '''Glue Database for this construct.

        If not provided the construct will create a new Glue Database.
        The database is where the schema for the data in Kinesis Data Streams is stored
        '''
        result = self._values.get("existing_database")
        return typing.cast(typing.Optional[aws_cdk.aws_glue.CfnDatabase], result)

    @builtins.property
    def existing_glue_job(self) -> typing.Optional[aws_cdk.aws_glue.CfnJob]:
        '''Existing GlueJob configuration.

        If this property is provided, any properties provided through @glueJobProps is ignored
        '''
        result = self._values.get("existing_glue_job")
        return typing.cast(typing.Optional[aws_cdk.aws_glue.CfnJob], result)

    @builtins.property
    def existing_stream_obj(self) -> typing.Optional[aws_cdk.aws_kinesis.Stream]:
        '''Existing instance of Kineses Data Stream.

        If not set, it will create an instance
        '''
        result = self._values.get("existing_stream_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_kinesis.Stream], result)

    @builtins.property
    def existing_table(self) -> typing.Optional[aws_cdk.aws_glue.CfnTable]:
        '''Glue Table for this construct, If not provided the construct will create a new Table in the database.

        This table should define the schema for the records in the Kinesis Data Streams.
        One of @tableprops or @table or @fieldSchema is mandatory. If @tableprops is provided then

        :fieldSchema: is ignored
        :table: is provided,
        '''
        result = self._values.get("existing_table")
        return typing.cast(typing.Optional[aws_cdk.aws_glue.CfnTable], result)

    @builtins.property
    def field_schema(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_glue.CfnTable.ColumnProperty]]:
        '''Structure of the records in the Amazon Kinesis Data Streams.

        An example of such a  definition is as below.
        Either @table or @fieldSchema is mandatory. If @table is provided then @fieldSchema is ignored
        "FieldSchema": [{
        "name": "id",
        "type": "int",
        "comment": "Identifier for the record"
        }, {
        "name": "name",
        "type": "string",
        "comment": "The name of the record"
        }, {
        "name": "type",
        "type": "string",
        "comment": "The type of the record"
        }, {
        "name": "numericvalue",
        "type": "int",
        "comment": "Some value associated with the record"
        },

        :default: - None
        '''
        result = self._values.get("field_schema")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_glue.CfnTable.ColumnProperty]], result)

    @builtins.property
    def glue_job_props(self) -> typing.Any:
        '''User provides props to override the default props for Glue ETL Jobs.

        Providing both this and
        existingGlueJob will cause an error.

        This parameter is defined as ``any`` to not enforce passing the Glue Job role which is a mandatory parameter
        for CfnJobProps. If a role is not passed, the construct creates one for you and attaches the appropriate
        role policies

        The default props will set the Glue Version 2.0, with 2 Workers and WorkerType as G1.X. For details on
        defining a Glue Job, please refer the following link for documentation - https://docs.aws.amazon.com/glue/latest/webapi/API_Job.html

        :default: - None
        '''
        result = self._values.get("glue_job_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def kinesis_stream_props(self) -> typing.Any:
        '''User provided props to override the default props for the Kinesis Stream.

        :default: - Default props are used
        '''
        result = self._values.get("kinesis_stream_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def output_data_store(
        self,
    ) -> typing.Optional[aws_solutions_constructs.core.SinkDataStoreProps]:
        '''The output data stores where the transformed data should be written.

        Current supported data stores
        include only S3, other potential stores may be added in the future.
        '''
        result = self._values.get("output_data_store")
        return typing.cast(typing.Optional[aws_solutions_constructs.core.SinkDataStoreProps], result)

    @builtins.property
    def table_props(self) -> typing.Optional[aws_cdk.aws_glue.CfnTableProps]:
        '''The table properties for the construct to create the table.

        One of @tableprops or @table
        or @fieldSchema is mandatory. If @tableprops is provided then @table and @fieldSchema
        are ignored. If @table is provided, @fieldSchema is ignored
        '''
        result = self._values.get("table_props")
        return typing.cast(typing.Optional[aws_cdk.aws_glue.CfnTableProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KinesisstreamsToGluejobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KinesisstreamsToGluejob",
    "KinesisstreamsToGluejobProps",
]

publication.publish()
