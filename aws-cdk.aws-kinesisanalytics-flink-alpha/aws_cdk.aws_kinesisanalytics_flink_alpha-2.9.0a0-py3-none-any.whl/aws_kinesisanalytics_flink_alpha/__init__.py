'''
# Kinesis Analytics Flink

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This package provides constructs for creating Kinesis Analytics Flink
applications. To learn more about using using managed Flink applications, see
the [AWS developer
guide](https://docs.aws.amazon.com/kinesisanalytics/latest/java/what-is.html).

## Creating Flink Applications

To create a new Flink application, use the `Application` construct:

```python
import path as path
import aws_cdk as core
import aws_cdk.aws_kinesisanalytics_flink_alpha as flink

app = core.App()
stack = core.Stack(app, "FlinkAppTest")

flink.Application(stack, "App",
    code=flink.ApplicationCode.from_asset(path.join(__dirname, "code-asset")),
    runtime=flink.Runtime.FLINK_1_11
)

app.synth()
```

The `code` property can use `fromAsset` as shown above to reference a local jar
file in s3 or `fromBucket` to reference a file in s3.

```python
import path as path
import aws_cdk.aws_s3_assets as assets
import aws_cdk as core
import aws_cdk.aws_kinesisanalytics_flink_alpha as flink

app = core.App()
stack = core.Stack(app, "FlinkAppCodeFromBucketTest")

asset = assets.Asset(stack, "CodeAsset",
    path=path.join(__dirname, "code-asset")
)
bucket = asset.bucket
file_key = asset.s3_object_key

flink.Application(stack, "App",
    code=flink.ApplicationCode.from_bucket(bucket, file_key),
    runtime=flink.Runtime.FLINK_1_11
)

app.synth()
```

The `propertyGroups` property provides a way of passing arbitrary runtime
properties to your Flink application. You can use the
aws-kinesisanalytics-runtime library to [retrieve these
properties](https://docs.aws.amazon.com/kinesisanalytics/latest/java/how-properties.html#how-properties-access).

```python
# bucket: s3.Bucket

flink_app = flink.Application(self, "Application",
    property_groups=flink.PropertyGroups(
        FlinkApplicationProperties={
            "input_stream_name": "my-input-kinesis-stream",
            "output_stream_name": "my-output-kinesis-stream"
        }
    ),
    # ...
    runtime=flink.Runtime.FLINK_1_13,
    code=flink.ApplicationCode.from_bucket(bucket, "my-app.jar")
)
```

Flink applications also have specific configuration for passing parameters
when the Flink job starts. These include parameters for checkpointing,
snapshotting, monitoring, and parallelism.

```python
# bucket: s3.Bucket

flink_app = flink.Application(self, "Application",
    code=flink.ApplicationCode.from_bucket(bucket, "my-app.jar"),
    runtime=flink.Runtime.FLINK_1_13,
    checkpointing_enabled=True,  # default is true
    checkpoint_interval=Duration.seconds(30),  # default is 1 minute
    min_pause_between_checkpoints=Duration.seconds(10),  # default is 5 seconds
    log_level=flink.LogLevel.ERROR,  # default is INFO
    metrics_level=flink.MetricsLevel.PARALLELISM,  # default is APPLICATION
    auto_scaling_enabled=False,  # default is true
    parallelism=32,  # default is 1
    parallelism_per_kpu=2,  # default is 1
    snapshots_enabled=False,  # default is true
    log_group=logs.LogGroup(self, "LogGroup")
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

from ._jsii import *

import aws_cdk
import aws_cdk.aws_iam
import aws_cdk.aws_kinesisanalytics
import aws_cdk.aws_logs
import aws_cdk.aws_s3
import aws_cdk.aws_s3_assets
import constructs


class ApplicationCode(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-kinesisanalytics-flink-alpha.ApplicationCode",
):
    '''(experimental) Code configuration providing the location to a Flink application JAR file.

    :stability: experimental
    :exampleMetadata: lit=test/integ.application.lit.ts ! show infused

    Example::

        import path as path
        import aws_cdk as core
        import aws_cdk.aws_kinesisanalytics_flink_alpha as flink
        
        app = core.App()
        stack = core.Stack(app, "FlinkAppTest")
        
        flink.Application(stack, "App",
            code=flink.ApplicationCode.from_asset(path.join(__dirname, "code-asset")),
            runtime=flink.Runtime.FLINK_1_11
        )
        
        app.synth()
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromAsset") # type: ignore[misc]
    @builtins.classmethod
    def from_asset(
        cls,
        path: builtins.str,
        *,
        readers: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IGrantable]] = None,
        asset_hash: typing.Optional[builtins.str] = None,
        asset_hash_type: typing.Optional[aws_cdk.AssetHashType] = None,
        bundling: typing.Optional[aws_cdk.BundlingOptions] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow_symlinks: typing.Optional[aws_cdk.SymlinkFollowMode] = None,
        ignore_mode: typing.Optional[aws_cdk.IgnoreMode] = None,
    ) -> "ApplicationCode":
        '''(experimental) Reference code from a local directory containing a Flink JAR file.

        :param path: - a local directory path.
        :param readers: A list of principals that should be able to read this asset from S3. You can use ``asset.grantRead(principal)`` to grant read permissions later. Default: - No principals that can read file asset.
        :param asset_hash: Specify a custom hash for this asset. If ``assetHashType`` is set it must be set to ``AssetHashType.CUSTOM``. For consistency, this custom hash will be SHA256 hashed and encoded as hex. The resulting hash will be the asset hash. NOTE: the hash is used in order to identify a specific revision of the asset, and used for optimizing and caching deployment activities related to this asset such as packaging, uploading to Amazon S3, etc. If you chose to customize the hash, you will need to make sure it is updated every time the asset changes, or otherwise it is possible that some deployments will not be invalidated. Default: - based on ``assetHashType``
        :param asset_hash_type: Specifies the type of hash to calculate for this asset. If ``assetHash`` is configured, this option must be ``undefined`` or ``AssetHashType.CUSTOM``. Default: - the default is ``AssetHashType.SOURCE``, but if ``assetHash`` is explicitly specified this value defaults to ``AssetHashType.CUSTOM``.
        :param bundling: Bundle the asset by executing a command in a Docker container or a custom bundling provider. The asset path will be mounted at ``/asset-input``. The Docker container is responsible for putting content at ``/asset-output``. The content at ``/asset-output`` will be zipped and used as the final asset. Default: - uploaded as-is to S3 if the asset is a regular file or a .zip file, archived into a .zip file and uploaded to S3 otherwise
        :param exclude: Glob patterns to exclude from the copy. Default: - nothing is excluded
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param ignore_mode: The ignore behavior to use for exclude patterns. Default: IgnoreMode.GLOB

        :stability: experimental
        :parm: options - standard s3 AssetOptions
        '''
        options = aws_cdk.aws_s3_assets.AssetOptions(
            readers=readers,
            asset_hash=asset_hash,
            asset_hash_type=asset_hash_type,
            bundling=bundling,
            exclude=exclude,
            follow_symlinks=follow_symlinks,
            ignore_mode=ignore_mode,
        )

        return typing.cast("ApplicationCode", jsii.sinvoke(cls, "fromAsset", [path, options]))

    @jsii.member(jsii_name="fromBucket") # type: ignore[misc]
    @builtins.classmethod
    def from_bucket(
        cls,
        bucket: aws_cdk.aws_s3.IBucket,
        file_key: builtins.str,
        object_version: typing.Optional[builtins.str] = None,
    ) -> "ApplicationCode":
        '''(experimental) Reference code from an S3 bucket.

        :param bucket: - an s3 bucket.
        :param file_key: - a key pointing to a Flink JAR file.
        :param object_version: - an optional version string for the provided fileKey.

        :stability: experimental
        '''
        return typing.cast("ApplicationCode", jsii.sinvoke(cls, "fromBucket", [bucket, file_key, object_version]))

    @jsii.member(jsii_name="bind") # type: ignore[misc]
    @abc.abstractmethod
    def bind(self, scope: constructs.Construct) -> "ApplicationCodeConfig":
        '''(experimental) A method to lazily bind asset resources to the parent FlinkApplication.

        :param scope: -

        :stability: experimental
        '''
        ...


class _ApplicationCodeProxy(ApplicationCode):
    @jsii.member(jsii_name="bind")
    def bind(self, scope: constructs.Construct) -> "ApplicationCodeConfig":
        '''(experimental) A method to lazily bind asset resources to the parent FlinkApplication.

        :param scope: -

        :stability: experimental
        '''
        return typing.cast("ApplicationCodeConfig", jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ApplicationCode).__jsii_proxy_class__ = lambda : _ApplicationCodeProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisanalytics-flink-alpha.ApplicationCodeConfig",
    jsii_struct_bases=[],
    name_mapping={
        "application_code_configuration_property": "applicationCodeConfigurationProperty",
        "bucket": "bucket",
    },
)
class ApplicationCodeConfig:
    def __init__(
        self,
        *,
        application_code_configuration_property: aws_cdk.aws_kinesisanalytics.CfnApplicationV2.ApplicationConfigurationProperty,
        bucket: aws_cdk.aws_s3.IBucket,
    ) -> None:
        '''(experimental) The return type of {@link ApplicationCode.bind}. This represents CloudFormation configuration and an s3 bucket holding the Flink application JAR file.

        :param application_code_configuration_property: (experimental) Low-level Cloudformation ApplicationConfigurationProperty.
        :param bucket: (experimental) S3 Bucket that stores the Flink application code.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_kinesisanalytics_flink_alpha as kinesisanalytics_flink_alpha
            from aws_cdk import aws_s3 as s3
            
            # bucket: s3.Bucket
            # property_map: Any
            
            application_code_config = kinesisanalytics_flink_alpha.ApplicationCodeConfig(
                application_code_configuration_property=ApplicationConfigurationProperty(
                    application_code_configuration=ApplicationCodeConfigurationProperty(
                        code_content=CodeContentProperty(
                            s3_content_location=S3ContentLocationProperty(
                                bucket_arn="bucketArn",
                                file_key="fileKey",
                                object_version="objectVersion"
                            ),
                            text_content="textContent",
                            zip_file_content="zipFileContent"
                        ),
                        code_content_type="codeContentType"
                    ),
                    application_snapshot_configuration=ApplicationSnapshotConfigurationProperty(
                        snapshots_enabled=False
                    ),
                    environment_properties=EnvironmentPropertiesProperty(
                        property_groups=[PropertyGroupProperty(
                            property_group_id="propertyGroupId",
                            property_map=property_map
                        )]
                    ),
                    flink_application_configuration=FlinkApplicationConfigurationProperty(
                        checkpoint_configuration=CheckpointConfigurationProperty(
                            configuration_type="configurationType",
            
                            # the properties below are optional
                            checkpointing_enabled=False,
                            checkpoint_interval=123,
                            min_pause_between_checkpoints=123
                        ),
                        monitoring_configuration=MonitoringConfigurationProperty(
                            configuration_type="configurationType",
            
                            # the properties below are optional
                            log_level="logLevel",
                            metrics_level="metricsLevel"
                        ),
                        parallelism_configuration=ParallelismConfigurationProperty(
                            configuration_type="configurationType",
            
                            # the properties below are optional
                            auto_scaling_enabled=False,
                            parallelism=123,
                            parallelism_per_kpu=123
                        )
                    ),
                    sql_application_configuration=SqlApplicationConfigurationProperty(
                        inputs=[InputProperty(
                            input_schema=InputSchemaProperty(
                                record_columns=[RecordColumnProperty(
                                    name="name",
                                    sql_type="sqlType",
            
                                    # the properties below are optional
                                    mapping="mapping"
                                )],
                                record_format=RecordFormatProperty(
                                    record_format_type="recordFormatType",
            
                                    # the properties below are optional
                                    mapping_parameters=MappingParametersProperty(
                                        csv_mapping_parameters=CSVMappingParametersProperty(
                                            record_column_delimiter="recordColumnDelimiter",
                                            record_row_delimiter="recordRowDelimiter"
                                        ),
                                        json_mapping_parameters=JSONMappingParametersProperty(
                                            record_row_path="recordRowPath"
                                        )
                                    )
                                ),
            
                                # the properties below are optional
                                record_encoding="recordEncoding"
                            ),
                            name_prefix="namePrefix",
            
                            # the properties below are optional
                            input_parallelism=InputParallelismProperty(
                                count=123
                            ),
                            input_processing_configuration=InputProcessingConfigurationProperty(
                                input_lambda_processor=InputLambdaProcessorProperty(
                                    resource_arn="resourceArn"
                                )
                            ),
                            kinesis_firehose_input=KinesisFirehoseInputProperty(
                                resource_arn="resourceArn"
                            ),
                            kinesis_streams_input=KinesisStreamsInputProperty(
                                resource_arn="resourceArn"
                            )
                        )]
                    ),
                    zeppelin_application_configuration=ZeppelinApplicationConfigurationProperty(
                        catalog_configuration=CatalogConfigurationProperty(
                            glue_data_catalog_configuration=GlueDataCatalogConfigurationProperty(
                                database_arn="databaseArn"
                            )
                        ),
                        custom_artifacts_configuration=[CustomArtifactConfigurationProperty(
                            artifact_type="artifactType",
            
                            # the properties below are optional
                            maven_reference=MavenReferenceProperty(
                                artifact_id="artifactId",
                                group_id="groupId",
                                version="version"
                            ),
                            s3_content_location=S3ContentLocationProperty(
                                bucket_arn="bucketArn",
                                file_key="fileKey",
                                object_version="objectVersion"
                            )
                        )],
                        deploy_as_application_configuration=DeployAsApplicationConfigurationProperty(
                            s3_content_location=S3ContentBaseLocationProperty(
                                base_path="basePath",
                                bucket_arn="bucketArn"
                            )
                        ),
                        monitoring_configuration=ZeppelinMonitoringConfigurationProperty(
                            log_level="logLevel"
                        )
                    )
                ),
                bucket=bucket
            )
        '''
        if isinstance(application_code_configuration_property, dict):
            application_code_configuration_property = aws_cdk.aws_kinesisanalytics.CfnApplicationV2.ApplicationConfigurationProperty(**application_code_configuration_property)
        self._values: typing.Dict[str, typing.Any] = {
            "application_code_configuration_property": application_code_configuration_property,
            "bucket": bucket,
        }

    @builtins.property
    def application_code_configuration_property(
        self,
    ) -> aws_cdk.aws_kinesisanalytics.CfnApplicationV2.ApplicationConfigurationProperty:
        '''(experimental) Low-level Cloudformation ApplicationConfigurationProperty.

        :stability: experimental
        '''
        result = self._values.get("application_code_configuration_property")
        assert result is not None, "Required property 'application_code_configuration_property' is missing"
        return typing.cast(aws_cdk.aws_kinesisanalytics.CfnApplicationV2.ApplicationConfigurationProperty, result)

    @builtins.property
    def bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 Bucket that stores the Flink application code.

        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationCodeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisanalytics-flink-alpha.ApplicationProps",
    jsii_struct_bases=[],
    name_mapping={
        "code": "code",
        "runtime": "runtime",
        "application_name": "applicationName",
        "auto_scaling_enabled": "autoScalingEnabled",
        "checkpointing_enabled": "checkpointingEnabled",
        "checkpoint_interval": "checkpointInterval",
        "log_group": "logGroup",
        "log_level": "logLevel",
        "metrics_level": "metricsLevel",
        "min_pause_between_checkpoints": "minPauseBetweenCheckpoints",
        "parallelism": "parallelism",
        "parallelism_per_kpu": "parallelismPerKpu",
        "property_groups": "propertyGroups",
        "removal_policy": "removalPolicy",
        "role": "role",
        "snapshots_enabled": "snapshotsEnabled",
    },
)
class ApplicationProps:
    def __init__(
        self,
        *,
        code: ApplicationCode,
        runtime: "Runtime",
        application_name: typing.Optional[builtins.str] = None,
        auto_scaling_enabled: typing.Optional[builtins.bool] = None,
        checkpointing_enabled: typing.Optional[builtins.bool] = None,
        checkpoint_interval: typing.Optional[aws_cdk.Duration] = None,
        log_group: typing.Optional[aws_cdk.aws_logs.ILogGroup] = None,
        log_level: typing.Optional["LogLevel"] = None,
        metrics_level: typing.Optional["MetricsLevel"] = None,
        min_pause_between_checkpoints: typing.Optional[aws_cdk.Duration] = None,
        parallelism: typing.Optional[jsii.Number] = None,
        parallelism_per_kpu: typing.Optional[jsii.Number] = None,
        property_groups: typing.Optional["PropertyGroups"] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        snapshots_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Props for creating an Application construct.

        :param code: (experimental) The Flink code asset to run.
        :param runtime: (experimental) The Flink version to use for this application.
        :param application_name: (experimental) A name for your Application that is unique to an AWS account. Default: - CloudFormation-generated name
        :param auto_scaling_enabled: (experimental) Whether the Kinesis Data Analytics service can increase the parallelism of the application in response to resource usage. Default: true
        :param checkpointing_enabled: (experimental) Whether checkpointing is enabled while your application runs. Default: true
        :param checkpoint_interval: (experimental) The interval between checkpoints. Default: 1 minute
        :param log_group: (experimental) The log group to send log entries to. Default: CDK's default LogGroup
        :param log_level: (experimental) The level of log verbosity from the Flink application. Default: FlinkLogLevel.INFO
        :param metrics_level: (experimental) Describes the granularity of the CloudWatch metrics for an application. Use caution with Parallelism level metrics. Parallelism granularity logs metrics for each parallel thread and can quickly become expensive when parallelism is high (e.g. > 64). Default: MetricsLevel.APPLICATION
        :param min_pause_between_checkpoints: (experimental) The minimum amount of time in to wait after a checkpoint finishes to start a new checkpoint. Default: 5 seconds
        :param parallelism: (experimental) The initial parallelism for the application. Kinesis Data Analytics can stop the app, increase the parallelism, and start the app again if autoScalingEnabled is true (the default value). Default: 1
        :param parallelism_per_kpu: (experimental) The Flink parallelism allowed per Kinesis Processing Unit (KPU). Default: 1
        :param property_groups: (experimental) Configuration PropertyGroups. You can use these property groups to pass arbitrary runtime configuration values to your Flink app. Default: No property group configuration provided to the Flink app
        :param removal_policy: (experimental) Provide a RemovalPolicy to override the default. Default: RemovalPolicy.DESTROY
        :param role: (experimental) A role to use to grant permissions to your application. Prefer omitting this property and using the default role. Default: - a new Role will be created
        :param snapshots_enabled: (experimental) Determines if Flink snapshots are enabled. Default: true

        :stability: experimental
        :exampleMetadata: lit=test/integ.application.lit.ts ! show infused

        Example::

            import path as path
            import aws_cdk as core
            import aws_cdk.aws_kinesisanalytics_flink_alpha as flink
            
            app = core.App()
            stack = core.Stack(app, "FlinkAppTest")
            
            flink.Application(stack, "App",
                code=flink.ApplicationCode.from_asset(path.join(__dirname, "code-asset")),
                runtime=flink.Runtime.FLINK_1_11
            )
            
            app.synth()
        '''
        if isinstance(property_groups, dict):
            property_groups = PropertyGroups(**property_groups)
        self._values: typing.Dict[str, typing.Any] = {
            "code": code,
            "runtime": runtime,
        }
        if application_name is not None:
            self._values["application_name"] = application_name
        if auto_scaling_enabled is not None:
            self._values["auto_scaling_enabled"] = auto_scaling_enabled
        if checkpointing_enabled is not None:
            self._values["checkpointing_enabled"] = checkpointing_enabled
        if checkpoint_interval is not None:
            self._values["checkpoint_interval"] = checkpoint_interval
        if log_group is not None:
            self._values["log_group"] = log_group
        if log_level is not None:
            self._values["log_level"] = log_level
        if metrics_level is not None:
            self._values["metrics_level"] = metrics_level
        if min_pause_between_checkpoints is not None:
            self._values["min_pause_between_checkpoints"] = min_pause_between_checkpoints
        if parallelism is not None:
            self._values["parallelism"] = parallelism
        if parallelism_per_kpu is not None:
            self._values["parallelism_per_kpu"] = parallelism_per_kpu
        if property_groups is not None:
            self._values["property_groups"] = property_groups
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if role is not None:
            self._values["role"] = role
        if snapshots_enabled is not None:
            self._values["snapshots_enabled"] = snapshots_enabled

    @builtins.property
    def code(self) -> ApplicationCode:
        '''(experimental) The Flink code asset to run.

        :stability: experimental
        '''
        result = self._values.get("code")
        assert result is not None, "Required property 'code' is missing"
        return typing.cast(ApplicationCode, result)

    @builtins.property
    def runtime(self) -> "Runtime":
        '''(experimental) The Flink version to use for this application.

        :stability: experimental
        '''
        result = self._values.get("runtime")
        assert result is not None, "Required property 'runtime' is missing"
        return typing.cast("Runtime", result)

    @builtins.property
    def application_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A name for your Application that is unique to an AWS account.

        :default: - CloudFormation-generated name

        :stability: experimental
        '''
        result = self._values.get("application_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auto_scaling_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether the Kinesis Data Analytics service can increase the parallelism of the application in response to resource usage.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("auto_scaling_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def checkpointing_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether checkpointing is enabled while your application runs.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("checkpointing_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def checkpoint_interval(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) The interval between checkpoints.

        :default: 1 minute

        :stability: experimental
        '''
        result = self._values.get("checkpoint_interval")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def log_group(self) -> typing.Optional[aws_cdk.aws_logs.ILogGroup]:
        '''(experimental) The log group to send log entries to.

        :default: CDK's default LogGroup

        :stability: experimental
        '''
        result = self._values.get("log_group")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.ILogGroup], result)

    @builtins.property
    def log_level(self) -> typing.Optional["LogLevel"]:
        '''(experimental) The level of log verbosity from the Flink application.

        :default: FlinkLogLevel.INFO

        :stability: experimental
        '''
        result = self._values.get("log_level")
        return typing.cast(typing.Optional["LogLevel"], result)

    @builtins.property
    def metrics_level(self) -> typing.Optional["MetricsLevel"]:
        '''(experimental) Describes the granularity of the CloudWatch metrics for an application.

        Use caution with Parallelism level metrics. Parallelism granularity logs
        metrics for each parallel thread and can quickly become expensive when
        parallelism is high (e.g. > 64).

        :default: MetricsLevel.APPLICATION

        :stability: experimental
        '''
        result = self._values.get("metrics_level")
        return typing.cast(typing.Optional["MetricsLevel"], result)

    @builtins.property
    def min_pause_between_checkpoints(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) The minimum amount of time in to wait after a checkpoint finishes to start a new checkpoint.

        :default: 5 seconds

        :stability: experimental
        '''
        result = self._values.get("min_pause_between_checkpoints")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def parallelism(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The initial parallelism for the application.

        Kinesis Data Analytics can
        stop the app, increase the parallelism, and start the app again if
        autoScalingEnabled is true (the default value).

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("parallelism")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parallelism_per_kpu(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The Flink parallelism allowed per Kinesis Processing Unit (KPU).

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("parallelism_per_kpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def property_groups(self) -> typing.Optional["PropertyGroups"]:
        '''(experimental) Configuration PropertyGroups.

        You can use these property groups to pass
        arbitrary runtime configuration values to your Flink app.

        :default: No property group configuration provided to the Flink app

        :stability: experimental
        '''
        result = self._values.get("property_groups")
        return typing.cast(typing.Optional["PropertyGroups"], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) Provide a RemovalPolicy to override the default.

        :default: RemovalPolicy.DESTROY

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) A role to use to grant permissions to your application.

        Prefer omitting
        this property and using the default role.

        :default: - a new Role will be created

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def snapshots_enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Determines if Flink snapshots are enabled.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("snapshots_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-kinesisanalytics-flink-alpha.IApplication")
class IApplication(
    aws_cdk.IResource,
    aws_cdk.aws_iam.IGrantable,
    typing_extensions.Protocol,
):
    '''(experimental) An interface expressing the public properties on both an imported and CDK-created Flink application.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The application ARN.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> builtins.str:
        '''(experimental) The name of the Flink application.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The application IAM role.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        policy_statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> builtins.bool:
        '''(experimental) Convenience method for adding a policy statement to the application role.

        :param policy_statement: -

        :stability: experimental
        '''
        ...


class _IApplicationProxy(
    jsii.proxy_for(aws_cdk.IResource), # type: ignore[misc]
    jsii.proxy_for(aws_cdk.aws_iam.IGrantable), # type: ignore[misc]
):
    '''(experimental) An interface expressing the public properties on both an imported and CDK-created Flink application.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-kinesisanalytics-flink-alpha.IApplication"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The application ARN.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> builtins.str:
        '''(experimental) The name of the Flink application.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The application IAM role.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], jsii.get(self, "role"))

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        policy_statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> builtins.bool:
        '''(experimental) Convenience method for adding a policy statement to the application role.

        :param policy_statement: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "addToRolePolicy", [policy_statement]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IApplication).__jsii_proxy_class__ = lambda : _IApplicationProxy


@jsii.enum(jsii_type="@aws-cdk/aws-kinesisanalytics-flink-alpha.LogLevel")
class LogLevel(enum.Enum):
    '''(experimental) Available log levels for Flink applications.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # bucket: s3.Bucket
        
        flink_app = flink.Application(self, "Application",
            code=flink.ApplicationCode.from_bucket(bucket, "my-app.jar"),
            runtime=flink.Runtime.FLINK_1_13,
            checkpointing_enabled=True,  # default is true
            checkpoint_interval=Duration.seconds(30),  # default is 1 minute
            min_pause_between_checkpoints=Duration.seconds(10),  # default is 5 seconds
            log_level=flink.LogLevel.ERROR,  # default is INFO
            metrics_level=flink.MetricsLevel.PARALLELISM,  # default is APPLICATION
            auto_scaling_enabled=False,  # default is true
            parallelism=32,  # default is 1
            parallelism_per_kpu=2,  # default is 1
            snapshots_enabled=False,  # default is true
            log_group=logs.LogGroup(self, "LogGroup")
        )
    '''

    DEBUG = "DEBUG"
    '''(experimental) Debug level logging.

    :stability: experimental
    '''
    INFO = "INFO"
    '''(experimental) Info level logging.

    :stability: experimental
    '''
    WARN = "WARN"
    '''(experimental) Warn level logging.

    :stability: experimental
    '''
    ERROR = "ERROR"
    '''(experimental) Error level logging.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@aws-cdk/aws-kinesisanalytics-flink-alpha.MetricsLevel")
class MetricsLevel(enum.Enum):
    '''(experimental) Granularity of metrics sent to CloudWatch.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # bucket: s3.Bucket
        
        flink_app = flink.Application(self, "Application",
            code=flink.ApplicationCode.from_bucket(bucket, "my-app.jar"),
            runtime=flink.Runtime.FLINK_1_13,
            checkpointing_enabled=True,  # default is true
            checkpoint_interval=Duration.seconds(30),  # default is 1 minute
            min_pause_between_checkpoints=Duration.seconds(10),  # default is 5 seconds
            log_level=flink.LogLevel.ERROR,  # default is INFO
            metrics_level=flink.MetricsLevel.PARALLELISM,  # default is APPLICATION
            auto_scaling_enabled=False,  # default is true
            parallelism=32,  # default is 1
            parallelism_per_kpu=2,  # default is 1
            snapshots_enabled=False,  # default is true
            log_group=logs.LogGroup(self, "LogGroup")
        )
    '''

    APPLICATION = "APPLICATION"
    '''(experimental) Application sends the least metrics to CloudWatch.

    :stability: experimental
    '''
    TASK = "TASK"
    '''(experimental) Task includes task-level metrics sent to CloudWatch.

    :stability: experimental
    '''
    OPERATOR = "OPERATOR"
    '''(experimental) Operator includes task-level and operator-level metrics sent to CloudWatch.

    :stability: experimental
    '''
    PARALLELISM = "PARALLELISM"
    '''(experimental) Send all metrics including metrics per task thread.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-kinesisanalytics-flink-alpha.PropertyGroups",
    jsii_struct_bases=[],
    name_mapping={},
)
class PropertyGroups:
    def __init__(self) -> None:
        '''(experimental) Interface for building AWS::KinesisAnalyticsV2::Application PropertyGroup configuration.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # bucket: s3.Bucket
            
            flink_app = flink.Application(self, "Application",
                property_groups=flink.PropertyGroups(
                    FlinkApplicationProperties={
                        "input_stream_name": "my-input-kinesis-stream",
                        "output_stream_name": "my-output-kinesis-stream"
                    }
                ),
                # ...
                runtime=flink.Runtime.FLINK_1_13,
                code=flink.ApplicationCode.from_bucket(bucket, "my-app.jar")
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PropertyGroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Runtime(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-kinesisanalytics-flink-alpha.Runtime",
):
    '''(experimental) Available Flink runtimes for Kinesis Analytics.

    :stability: experimental
    :exampleMetadata: lit=test/integ.application.lit.ts ! show infused

    Example::

        import path as path
        import aws_cdk as core
        import aws_cdk.aws_kinesisanalytics_flink_alpha as flink
        
        app = core.App()
        stack = core.Stack(app, "FlinkAppTest")
        
        flink.Application(stack, "App",
            code=flink.ApplicationCode.from_asset(path.join(__dirname, "code-asset")),
            runtime=flink.Runtime.FLINK_1_11
        )
        
        app.synth()
    '''

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, value: builtins.str) -> "Runtime":
        '''(experimental) Create a new Runtime with with an arbitrary Flink version string.

        :param value: -

        :stability: experimental
        '''
        return typing.cast("Runtime", jsii.sinvoke(cls, "of", [value]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FLINK_1_11")
    def FLINK_1_11(cls) -> "Runtime":
        '''(experimental) Flink Version 1.11.

        :stability: experimental
        '''
        return typing.cast("Runtime", jsii.sget(cls, "FLINK_1_11"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FLINK_1_13")
    def FLINK_1_13(cls) -> "Runtime":
        '''(experimental) Flink Version 1.13.

        :stability: experimental
        '''
        return typing.cast("Runtime", jsii.sget(cls, "FLINK_1_13"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FLINK_1_6")
    def FLINK_1_6(cls) -> "Runtime":
        '''(experimental) Flink Version 1.6.

        :stability: experimental
        '''
        return typing.cast("Runtime", jsii.sget(cls, "FLINK_1_6"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FLINK_1_8")
    def FLINK_1_8(cls) -> "Runtime":
        '''(experimental) Flink Version 1.8.

        :stability: experimental
        '''
        return typing.cast("Runtime", jsii.sget(cls, "FLINK_1_8"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        '''(experimental) The Cfn string that represents a version of Flink.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "value"))


@jsii.implements(IApplication)
class Application(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-kinesisanalytics-flink-alpha.Application",
):
    '''(experimental) The L2 construct for Flink Kinesis Data Applications.

    :stability: experimental
    :exampleMetadata: lit=test/integ.application.lit.ts ! show infused
    :resource: AWS::KinesisAnalyticsV2::Application

    Example::

        import path as path
        import aws_cdk as core
        import aws_cdk.aws_kinesisanalytics_flink_alpha as flink
        
        app = core.App()
        stack = core.Stack(app, "FlinkAppTest")
        
        flink.Application(stack, "App",
            code=flink.ApplicationCode.from_asset(path.join(__dirname, "code-asset")),
            runtime=flink.Runtime.FLINK_1_11
        )
        
        app.synth()
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        code: ApplicationCode,
        runtime: Runtime,
        application_name: typing.Optional[builtins.str] = None,
        auto_scaling_enabled: typing.Optional[builtins.bool] = None,
        checkpointing_enabled: typing.Optional[builtins.bool] = None,
        checkpoint_interval: typing.Optional[aws_cdk.Duration] = None,
        log_group: typing.Optional[aws_cdk.aws_logs.ILogGroup] = None,
        log_level: typing.Optional[LogLevel] = None,
        metrics_level: typing.Optional[MetricsLevel] = None,
        min_pause_between_checkpoints: typing.Optional[aws_cdk.Duration] = None,
        parallelism: typing.Optional[jsii.Number] = None,
        parallelism_per_kpu: typing.Optional[jsii.Number] = None,
        property_groups: typing.Optional[PropertyGroups] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        snapshots_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code: (experimental) The Flink code asset to run.
        :param runtime: (experimental) The Flink version to use for this application.
        :param application_name: (experimental) A name for your Application that is unique to an AWS account. Default: - CloudFormation-generated name
        :param auto_scaling_enabled: (experimental) Whether the Kinesis Data Analytics service can increase the parallelism of the application in response to resource usage. Default: true
        :param checkpointing_enabled: (experimental) Whether checkpointing is enabled while your application runs. Default: true
        :param checkpoint_interval: (experimental) The interval between checkpoints. Default: 1 minute
        :param log_group: (experimental) The log group to send log entries to. Default: CDK's default LogGroup
        :param log_level: (experimental) The level of log verbosity from the Flink application. Default: FlinkLogLevel.INFO
        :param metrics_level: (experimental) Describes the granularity of the CloudWatch metrics for an application. Use caution with Parallelism level metrics. Parallelism granularity logs metrics for each parallel thread and can quickly become expensive when parallelism is high (e.g. > 64). Default: MetricsLevel.APPLICATION
        :param min_pause_between_checkpoints: (experimental) The minimum amount of time in to wait after a checkpoint finishes to start a new checkpoint. Default: 5 seconds
        :param parallelism: (experimental) The initial parallelism for the application. Kinesis Data Analytics can stop the app, increase the parallelism, and start the app again if autoScalingEnabled is true (the default value). Default: 1
        :param parallelism_per_kpu: (experimental) The Flink parallelism allowed per Kinesis Processing Unit (KPU). Default: 1
        :param property_groups: (experimental) Configuration PropertyGroups. You can use these property groups to pass arbitrary runtime configuration values to your Flink app. Default: No property group configuration provided to the Flink app
        :param removal_policy: (experimental) Provide a RemovalPolicy to override the default. Default: RemovalPolicy.DESTROY
        :param role: (experimental) A role to use to grant permissions to your application. Prefer omitting this property and using the default role. Default: - a new Role will be created
        :param snapshots_enabled: (experimental) Determines if Flink snapshots are enabled. Default: true

        :stability: experimental
        '''
        props = ApplicationProps(
            code=code,
            runtime=runtime,
            application_name=application_name,
            auto_scaling_enabled=auto_scaling_enabled,
            checkpointing_enabled=checkpointing_enabled,
            checkpoint_interval=checkpoint_interval,
            log_group=log_group,
            log_level=log_level,
            metrics_level=metrics_level,
            min_pause_between_checkpoints=min_pause_between_checkpoints,
            parallelism=parallelism,
            parallelism_per_kpu=parallelism_per_kpu,
            property_groups=property_groups,
            removal_policy=removal_policy,
            role=role,
            snapshots_enabled=snapshots_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromApplicationArn") # type: ignore[misc]
    @builtins.classmethod
    def from_application_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        application_arn: builtins.str,
    ) -> IApplication:
        '''(experimental) Import an existing application defined outside of CDK code by applicationArn.

        :param scope: -
        :param id: -
        :param application_arn: -

        :stability: experimental
        '''
        return typing.cast(IApplication, jsii.sinvoke(cls, "fromApplicationArn", [scope, id, application_arn]))

    @jsii.member(jsii_name="fromApplicationName") # type: ignore[misc]
    @builtins.classmethod
    def from_application_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        application_name: builtins.str,
    ) -> IApplication:
        '''(experimental) Import an existing Flink application defined outside of CDK code by applicationName.

        :param scope: -
        :param id: -
        :param application_name: -

        :stability: experimental
        '''
        return typing.cast(IApplication, jsii.sinvoke(cls, "fromApplicationName", [scope, id, application_name]))

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        policy_statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> builtins.bool:
        '''(experimental) Implement the convenience {@link IApplication.addToPrincipalPolicy} method.

        :param policy_statement: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "addToRolePolicy", [policy_statement]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationArn")
    def application_arn(self) -> builtins.str:
        '''(experimental) The application ARN.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="applicationName")
    def application_name(self) -> builtins.str:
        '''(experimental) The name of the Flink application.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "applicationName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''(experimental) The application IAM role.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], jsii.get(self, "role"))


__all__ = [
    "Application",
    "ApplicationCode",
    "ApplicationCodeConfig",
    "ApplicationProps",
    "IApplication",
    "LogLevel",
    "MetricsLevel",
    "PropertyGroups",
    "Runtime",
]

publication.publish()
