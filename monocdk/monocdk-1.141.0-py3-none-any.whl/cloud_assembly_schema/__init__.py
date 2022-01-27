'''
# Cloud Assembly Schema

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

## Cloud Assembly

The *Cloud Assembly* is the output of the synthesis operation. It is produced as part of the
[`cdk synth`](https://github.com/aws/aws-cdk/tree/master/packages/aws-cdk#cdk-synthesize)
command, or the [`app.synth()`](https://github.com/aws/aws-cdk/blob/master/packages/@aws-cdk/core/lib/app.ts#L135) method invocation.

Its essentially a set of files and directories, one of which is the `manifest.json` file. It defines the set of instructions that are
needed in order to deploy the assembly directory.

> For example, when `cdk deploy` is executed, the CLI reads this file and performs its instructions:
>
> * Build container images.
> * Upload assets.
> * Deploy CloudFormation templates.

Therefore, the assembly is how the CDK class library and CDK CLI (or any other consumer) communicate. To ensure compatibility
between the assembly and its consumers, we treat the manifest file as a well defined, versioned schema.

## Schema

This module contains the typescript structs that comprise the `manifest.json` file, as well as the
generated [*json-schema*](./schema/cloud-assembly.schema.json).

## Versioning

The schema version is specified in the [`cloud-assembly.version.json`](./schema/cloud-assembly.schema.json) file, under the `version` property.
It follows semantic versioning, but with a small twist.

When we add instructions to the assembly, they are reflected in the manifest file and the *json-schema* accordingly.
Every such instruction, is crucial for ensuring the correct deployment behavior. This means that to properly deploy a cloud assembly,
consumers must be aware of every such instruction modification.

For this reason, every change to the schema, even though it might not strictly break validation of the *json-schema* format,
is considered `major` version bump.

## How to consume

If you'd like to consume the [schema file](./schema/cloud-assembly.schema.json) in order to do validations on `manifest.json` files,
simply download it from this repo and run it against standard *json-schema* validators, such as [jsonschema](https://www.npmjs.com/package/jsonschema).

Consumers must take into account the `major` version of the schema they are consuming. They should reject cloud assemblies
with a `major` version that is higher than what they expect. While schema validation might pass on such assemblies, the deployment integrity
cannot be guaranteed because some instructions will be ignored.

> For example, if your consumer was built when the schema version was 2.0.0, you should reject deploying cloud assemblies with a
> manifest version of 3.0.0.

## Contributing

See [Contribution Guide](./CONTRIBUTING.md)
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


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.AmiContextQuery",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "filters": "filters",
        "region": "region",
        "lookup_role_arn": "lookupRoleArn",
        "owners": "owners",
    },
)
class AmiContextQuery:
    def __init__(
        self,
        *,
        account: builtins.str,
        filters: typing.Mapping[builtins.str, typing.Sequence[builtins.str]],
        region: builtins.str,
        lookup_role_arn: typing.Optional[builtins.str] = None,
        owners: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Query to AMI context provider.

        :param account: (experimental) Account to query.
        :param filters: (experimental) Filters to DescribeImages call.
        :param region: (experimental) Region to query.
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None
        :param owners: (experimental) Owners to DescribeImages call. Default: - All owners

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            ami_context_query = cloud_assembly_schema.AmiContextQuery(
                account="account",
                filters={
                    "filters_key": ["filters"]
                },
                region="region",
            
                # the properties below are optional
                lookup_role_arn="lookupRoleArn",
                owners=["owners"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "filters": filters,
            "region": region,
        }
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn
        if owners is not None:
            self._values["owners"] = owners

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Account to query.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filters(self) -> typing.Mapping[builtins.str, typing.List[builtins.str]]:
        '''(experimental) Filters to DescribeImages call.

        :stability: experimental
        '''
        result = self._values.get("filters")
        assert result is not None, "Required property 'filters' is missing"
        return typing.cast(typing.Mapping[builtins.str, typing.List[builtins.str]], result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Region to query.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owners(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Owners to DescribeImages call.

        :default: - All owners

        :stability: experimental
        '''
        result = self._values.get("owners")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmiContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.ArtifactManifest",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "dependencies": "dependencies",
        "display_name": "displayName",
        "environment": "environment",
        "metadata": "metadata",
        "properties": "properties",
    },
)
class ArtifactManifest:
    def __init__(
        self,
        *,
        type: "ArtifactType",
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        display_name: typing.Optional[builtins.str] = None,
        environment: typing.Optional[builtins.str] = None,
        metadata: typing.Optional[typing.Mapping[builtins.str, typing.Sequence["MetadataEntry"]]] = None,
        properties: typing.Optional[typing.Union["AwsCloudFormationStackProperties", "AssetManifestProperties", "TreeArtifactProperties", "NestedCloudAssemblyProperties"]] = None,
    ) -> None:
        '''(experimental) A manifest for a single artifact within the cloud assembly.

        :param type: (experimental) The type of artifact.
        :param dependencies: (experimental) IDs of artifacts that must be deployed before this artifact. Default: - no dependencies.
        :param display_name: (experimental) A string that represents this artifact. Should only be used in user interfaces. Default: - no display name
        :param environment: (experimental) The environment into which this artifact is deployed. Default: - no envrionment.
        :param metadata: (experimental) Associated metadata. Default: - no metadata.
        :param properties: (experimental) The set of properties for this artifact (depends on type). Default: - no properties.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            artifact_manifest = cloud_assembly_schema.ArtifactManifest(
                type=cloud_assembly_schema.ArtifactType.NONE,
            
                # the properties below are optional
                dependencies=["dependencies"],
                display_name="displayName",
                environment="environment",
                metadata={
                    "metadata_key": [cloud_assembly_schema.MetadataEntry(
                        type="type",
            
                        # the properties below are optional
                        data="data",
                        trace=["trace"]
                    )]
                },
                properties=cloud_assembly_schema.AwsCloudFormationStackProperties(
                    template_file="templateFile",
            
                    # the properties below are optional
                    assume_role_arn="assumeRoleArn",
                    assume_role_external_id="assumeRoleExternalId",
                    bootstrap_stack_version_ssm_parameter="bootstrapStackVersionSsmParameter",
                    cloud_formation_execution_role_arn="cloudFormationExecutionRoleArn",
                    lookup_role=cloud_assembly_schema.BootstrapRole(
                        arn="arn",
            
                        # the properties below are optional
                        assume_role_external_id="assumeRoleExternalId",
                        bootstrap_stack_version_ssm_parameter="bootstrapStackVersionSsmParameter",
                        requires_bootstrap_stack_version=123
                    ),
                    parameters={
                        "parameters_key": "parameters"
                    },
                    requires_bootstrap_stack_version=123,
                    stack_name="stackName",
                    stack_template_asset_object_url="stackTemplateAssetObjectUrl",
                    tags={
                        "tags_key": "tags"
                    },
                    termination_protection=False,
                    validate_on_synth=False
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if dependencies is not None:
            self._values["dependencies"] = dependencies
        if display_name is not None:
            self._values["display_name"] = display_name
        if environment is not None:
            self._values["environment"] = environment
        if metadata is not None:
            self._values["metadata"] = metadata
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def type(self) -> "ArtifactType":
        '''(experimental) The type of artifact.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("ArtifactType", result)

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) IDs of artifacts that must be deployed before this artifact.

        :default: - no dependencies.

        :stability: experimental
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) A string that represents this artifact.

        Should only be used in user interfaces.

        :default: - no display name

        :stability: experimental
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(self) -> typing.Optional[builtins.str]:
        '''(experimental) The environment into which this artifact is deployed.

        :default: - no envrionment.

        :stability: experimental
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def metadata(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.List["MetadataEntry"]]]:
        '''(experimental) Associated metadata.

        :default: - no metadata.

        :stability: experimental
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.List["MetadataEntry"]]], result)

    @builtins.property
    def properties(
        self,
    ) -> typing.Optional[typing.Union["AwsCloudFormationStackProperties", "AssetManifestProperties", "TreeArtifactProperties", "NestedCloudAssemblyProperties"]]:
        '''(experimental) The set of properties for this artifact (depends on type).

        :default: - no properties.

        :stability: experimental
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[typing.Union["AwsCloudFormationStackProperties", "AssetManifestProperties", "TreeArtifactProperties", "NestedCloudAssemblyProperties"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ArtifactManifest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.cloud_assembly_schema.ArtifactMetadataEntryType")
class ArtifactMetadataEntryType(enum.Enum):
    '''(experimental) Type of artifact metadata entry.

    :stability: experimental
    '''

    ASSET = "ASSET"
    '''(experimental) Asset in metadata.

    :stability: experimental
    '''
    INFO = "INFO"
    '''(experimental) Metadata key used to print INFO-level messages by the toolkit when an app is syntheized.

    :stability: experimental
    '''
    WARN = "WARN"
    '''(experimental) Metadata key used to print WARNING-level messages by the toolkit when an app is syntheized.

    :stability: experimental
    '''
    ERROR = "ERROR"
    '''(experimental) Metadata key used to print ERROR-level messages by the toolkit when an app is syntheized.

    :stability: experimental
    '''
    LOGICAL_ID = "LOGICAL_ID"
    '''(experimental) Represents the CloudFormation logical ID of a resource at a certain path.

    :stability: experimental
    '''
    STACK_TAGS = "STACK_TAGS"
    '''(experimental) Represents tags of a stack.

    :stability: experimental
    '''


@jsii.enum(jsii_type="monocdk.cloud_assembly_schema.ArtifactType")
class ArtifactType(enum.Enum):
    '''(experimental) Type of cloud artifact.

    :stability: experimental
    '''

    NONE = "NONE"
    '''(experimental) Stub required because of JSII.

    :stability: experimental
    '''
    AWS_CLOUDFORMATION_STACK = "AWS_CLOUDFORMATION_STACK"
    '''(experimental) The artifact is an AWS CloudFormation stack.

    :stability: experimental
    '''
    CDK_TREE = "CDK_TREE"
    '''(experimental) The artifact contains the CDK application's construct tree.

    :stability: experimental
    '''
    ASSET_MANIFEST = "ASSET_MANIFEST"
    '''(experimental) Manifest for all assets in the Cloud Assembly.

    :stability: experimental
    '''
    NESTED_CLOUD_ASSEMBLY = "NESTED_CLOUD_ASSEMBLY"
    '''(experimental) Nested Cloud Assembly.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.AssemblyManifest",
    jsii_struct_bases=[],
    name_mapping={
        "version": "version",
        "artifacts": "artifacts",
        "missing": "missing",
        "runtime": "runtime",
    },
)
class AssemblyManifest:
    def __init__(
        self,
        *,
        version: builtins.str,
        artifacts: typing.Optional[typing.Mapping[builtins.str, ArtifactManifest]] = None,
        missing: typing.Optional[typing.Sequence["MissingContext"]] = None,
        runtime: typing.Optional["RuntimeInfo"] = None,
    ) -> None:
        '''(experimental) A manifest which describes the cloud assembly.

        :param version: (experimental) Protocol version.
        :param artifacts: (experimental) The set of artifacts in this assembly. Default: - no artifacts.
        :param missing: (experimental) Missing context information. If this field has values, it means that the cloud assembly is not complete and should not be deployed. Default: - no missing context.
        :param runtime: (experimental) Runtime information. Default: - no info.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            assembly_manifest = cloud_assembly_schema.AssemblyManifest(
                version="version",
            
                # the properties below are optional
                artifacts={
                    "artifacts_key": cloud_assembly_schema.ArtifactManifest(
                        type=cloud_assembly_schema.ArtifactType.NONE,
            
                        # the properties below are optional
                        dependencies=["dependencies"],
                        display_name="displayName",
                        environment="environment",
                        metadata={
                            "metadata_key": [cloud_assembly_schema.MetadataEntry(
                                type="type",
            
                                # the properties below are optional
                                data="data",
                                trace=["trace"]
                            )]
                        },
                        properties=cloud_assembly_schema.AwsCloudFormationStackProperties(
                            template_file="templateFile",
            
                            # the properties below are optional
                            assume_role_arn="assumeRoleArn",
                            assume_role_external_id="assumeRoleExternalId",
                            bootstrap_stack_version_ssm_parameter="bootstrapStackVersionSsmParameter",
                            cloud_formation_execution_role_arn="cloudFormationExecutionRoleArn",
                            lookup_role=cloud_assembly_schema.BootstrapRole(
                                arn="arn",
            
                                # the properties below are optional
                                assume_role_external_id="assumeRoleExternalId",
                                bootstrap_stack_version_ssm_parameter="bootstrapStackVersionSsmParameter",
                                requires_bootstrap_stack_version=123
                            ),
                            parameters={
                                "parameters_key": "parameters"
                            },
                            requires_bootstrap_stack_version=123,
                            stack_name="stackName",
                            stack_template_asset_object_url="stackTemplateAssetObjectUrl",
                            tags={
                                "tags_key": "tags"
                            },
                            termination_protection=False,
                            validate_on_synth=False
                        )
                    )
                },
                missing=[cloud_assembly_schema.MissingContext(
                    key="key",
                    props=cloud_assembly_schema.AmiContextQuery(
                        account="account",
                        filters={
                            "filters_key": ["filters"]
                        },
                        region="region",
            
                        # the properties below are optional
                        lookup_role_arn="lookupRoleArn",
                        owners=["owners"]
                    ),
                    provider=cloud_assembly_schema.ContextProvider.AMI_PROVIDER
                )],
                runtime=cloud_assembly_schema.RuntimeInfo(
                    libraries={
                        "libraries_key": "libraries"
                    }
                )
            )
        '''
        if isinstance(runtime, dict):
            runtime = RuntimeInfo(**runtime)
        self._values: typing.Dict[str, typing.Any] = {
            "version": version,
        }
        if artifacts is not None:
            self._values["artifacts"] = artifacts
        if missing is not None:
            self._values["missing"] = missing
        if runtime is not None:
            self._values["runtime"] = runtime

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Protocol version.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifacts(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, ArtifactManifest]]:
        '''(experimental) The set of artifacts in this assembly.

        :default: - no artifacts.

        :stability: experimental
        '''
        result = self._values.get("artifacts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, ArtifactManifest]], result)

    @builtins.property
    def missing(self) -> typing.Optional[typing.List["MissingContext"]]:
        '''(experimental) Missing context information.

        If this field has values, it means that the
        cloud assembly is not complete and should not be deployed.

        :default: - no missing context.

        :stability: experimental
        '''
        result = self._values.get("missing")
        return typing.cast(typing.Optional[typing.List["MissingContext"]], result)

    @builtins.property
    def runtime(self) -> typing.Optional["RuntimeInfo"]:
        '''(experimental) Runtime information.

        :default: - no info.

        :stability: experimental
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional["RuntimeInfo"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AssemblyManifest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.AssetManifest",
    jsii_struct_bases=[],
    name_mapping={
        "version": "version",
        "docker_images": "dockerImages",
        "files": "files",
    },
)
class AssetManifest:
    def __init__(
        self,
        *,
        version: builtins.str,
        docker_images: typing.Optional[typing.Mapping[builtins.str, "DockerImageAsset"]] = None,
        files: typing.Optional[typing.Mapping[builtins.str, "FileAsset"]] = None,
    ) -> None:
        '''(experimental) Definitions for the asset manifest.

        :param version: (experimental) Version of the manifest.
        :param docker_images: (experimental) The Docker image assets in this manifest. Default: - No Docker images
        :param files: (experimental) The file assets in this manifest. Default: - No files

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            asset_manifest = cloud_assembly_schema.AssetManifest(
                version="version",
            
                # the properties below are optional
                docker_images={
                    "docker_images_key": cloud_assembly_schema.DockerImageAsset(
                        destinations={
                            "destinations_key": cloud_assembly_schema.DockerImageDestination(
                                image_tag="imageTag",
                                repository_name="repositoryName",
            
                                # the properties below are optional
                                assume_role_arn="assumeRoleArn",
                                assume_role_external_id="assumeRoleExternalId",
                                region="region"
                            )
                        },
                        source=cloud_assembly_schema.DockerImageSource(
                            directory="directory",
                            docker_build_args={
                                "docker_build_args_key": "dockerBuildArgs"
                            },
                            docker_build_target="dockerBuildTarget",
                            docker_file="dockerFile",
                            executable=["executable"]
                        )
                    )
                },
                files={
                    "files_key": cloud_assembly_schema.FileAsset(
                        destinations={
                            "destinations_key": cloud_assembly_schema.FileDestination(
                                bucket_name="bucketName",
                                object_key="objectKey",
            
                                # the properties below are optional
                                assume_role_arn="assumeRoleArn",
                                assume_role_external_id="assumeRoleExternalId",
                                region="region"
                            )
                        },
                        source=cloud_assembly_schema.FileSource(
                            executable=["executable"],
                            packaging=cloud_assembly_schema.FileAssetPackaging.FILE,
                            path="path"
                        )
                    )
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "version": version,
        }
        if docker_images is not None:
            self._values["docker_images"] = docker_images
        if files is not None:
            self._values["files"] = files

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Version of the manifest.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def docker_images(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "DockerImageAsset"]]:
        '''(experimental) The Docker image assets in this manifest.

        :default: - No Docker images

        :stability: experimental
        '''
        result = self._values.get("docker_images")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "DockerImageAsset"]], result)

    @builtins.property
    def files(self) -> typing.Optional[typing.Mapping[builtins.str, "FileAsset"]]:
        '''(experimental) The file assets in this manifest.

        :default: - No files

        :stability: experimental
        '''
        result = self._values.get("files")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "FileAsset"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AssetManifest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.AssetManifestProperties",
    jsii_struct_bases=[],
    name_mapping={
        "file": "file",
        "bootstrap_stack_version_ssm_parameter": "bootstrapStackVersionSsmParameter",
        "requires_bootstrap_stack_version": "requiresBootstrapStackVersion",
    },
)
class AssetManifestProperties:
    def __init__(
        self,
        *,
        file: builtins.str,
        bootstrap_stack_version_ssm_parameter: typing.Optional[builtins.str] = None,
        requires_bootstrap_stack_version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Artifact properties for the Asset Manifest.

        :param file: (experimental) Filename of the asset manifest.
        :param bootstrap_stack_version_ssm_parameter: (experimental) SSM parameter where the bootstrap stack version number can be found. - If this value is not set, the bootstrap stack name must be known at deployment time so the stack version can be looked up from the stack outputs. - If this value is set, the bootstrap stack can have any name because we won't need to look it up. Default: - Bootstrap stack version number looked up
        :param requires_bootstrap_stack_version: (experimental) Version of bootstrap stack required to deploy this stack. Default: - Version 1 (basic modern bootstrap stack)

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            asset_manifest_properties = cloud_assembly_schema.AssetManifestProperties(
                file="file",
            
                # the properties below are optional
                bootstrap_stack_version_ssm_parameter="bootstrapStackVersionSsmParameter",
                requires_bootstrap_stack_version=123
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "file": file,
        }
        if bootstrap_stack_version_ssm_parameter is not None:
            self._values["bootstrap_stack_version_ssm_parameter"] = bootstrap_stack_version_ssm_parameter
        if requires_bootstrap_stack_version is not None:
            self._values["requires_bootstrap_stack_version"] = requires_bootstrap_stack_version

    @builtins.property
    def file(self) -> builtins.str:
        '''(experimental) Filename of the asset manifest.

        :stability: experimental
        '''
        result = self._values.get("file")
        assert result is not None, "Required property 'file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bootstrap_stack_version_ssm_parameter(self) -> typing.Optional[builtins.str]:
        '''(experimental) SSM parameter where the bootstrap stack version number can be found.

        - If this value is not set, the bootstrap stack name must be known at
          deployment time so the stack version can be looked up from the stack
          outputs.
        - If this value is set, the bootstrap stack can have any name because
          we won't need to look it up.

        :default: - Bootstrap stack version number looked up

        :stability: experimental
        '''
        result = self._values.get("bootstrap_stack_version_ssm_parameter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def requires_bootstrap_stack_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Version of bootstrap stack required to deploy this stack.

        :default: - Version 1 (basic modern bootstrap stack)

        :stability: experimental
        '''
        result = self._values.get("requires_bootstrap_stack_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AssetManifestProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.AvailabilityZonesContextQuery",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "region": "region",
        "lookup_role_arn": "lookupRoleArn",
    },
)
class AvailabilityZonesContextQuery:
    def __init__(
        self,
        *,
        account: builtins.str,
        region: builtins.str,
        lookup_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Query to availability zone context provider.

        :param account: (experimental) Query account.
        :param region: (experimental) Query region.
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            availability_zones_context_query = cloud_assembly_schema.AvailabilityZonesContextQuery(
                account="account",
                region="region",
            
                # the properties below are optional
                lookup_role_arn="lookupRoleArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "region": region,
        }
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Query account.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Query region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AvailabilityZonesContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.AwsCloudFormationStackProperties",
    jsii_struct_bases=[],
    name_mapping={
        "template_file": "templateFile",
        "assume_role_arn": "assumeRoleArn",
        "assume_role_external_id": "assumeRoleExternalId",
        "bootstrap_stack_version_ssm_parameter": "bootstrapStackVersionSsmParameter",
        "cloud_formation_execution_role_arn": "cloudFormationExecutionRoleArn",
        "lookup_role": "lookupRole",
        "parameters": "parameters",
        "requires_bootstrap_stack_version": "requiresBootstrapStackVersion",
        "stack_name": "stackName",
        "stack_template_asset_object_url": "stackTemplateAssetObjectUrl",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "validate_on_synth": "validateOnSynth",
    },
)
class AwsCloudFormationStackProperties:
    def __init__(
        self,
        *,
        template_file: builtins.str,
        assume_role_arn: typing.Optional[builtins.str] = None,
        assume_role_external_id: typing.Optional[builtins.str] = None,
        bootstrap_stack_version_ssm_parameter: typing.Optional[builtins.str] = None,
        cloud_formation_execution_role_arn: typing.Optional[builtins.str] = None,
        lookup_role: typing.Optional["BootstrapRole"] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        requires_bootstrap_stack_version: typing.Optional[jsii.Number] = None,
        stack_name: typing.Optional[builtins.str] = None,
        stack_template_asset_object_url: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        validate_on_synth: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Artifact properties for CloudFormation stacks.

        :param template_file: (experimental) A file relative to the assembly root which contains the CloudFormation template for this stack.
        :param assume_role_arn: (experimental) The role that needs to be assumed to deploy the stack. Default: - No role is assumed (current credentials are used)
        :param assume_role_external_id: (experimental) External ID to use when assuming role for cloudformation deployments. Default: - No external ID
        :param bootstrap_stack_version_ssm_parameter: (experimental) SSM parameter where the bootstrap stack version number can be found. Only used if ``requiresBootstrapStackVersion`` is set. - If this value is not set, the bootstrap stack name must be known at deployment time so the stack version can be looked up from the stack outputs. - If this value is set, the bootstrap stack can have any name because we won't need to look it up. Default: - Bootstrap stack version number looked up
        :param cloud_formation_execution_role_arn: (experimental) The role that is passed to CloudFormation to execute the change set. Default: - No role is passed (currently assumed role/credentials are used)
        :param lookup_role: (experimental) The role to use to look up values from the target AWS account. Default: - No role is assumed (current credentials are used)
        :param parameters: (experimental) Values for CloudFormation stack parameters that should be passed when the stack is deployed. Default: - No parameters
        :param requires_bootstrap_stack_version: (experimental) Version of bootstrap stack required to deploy this stack. Default: - No bootstrap stack required
        :param stack_name: (experimental) The name to use for the CloudFormation stack. Default: - name derived from artifact ID
        :param stack_template_asset_object_url: (experimental) If the stack template has already been included in the asset manifest, its asset URL. Default: - Not uploaded yet, upload just before deploying
        :param tags: (experimental) Values for CloudFormation stack tags that should be passed when the stack is deployed. Default: - No tags
        :param termination_protection: (experimental) Whether to enable termination protection for this stack. Default: false
        :param validate_on_synth: (experimental) Whether this stack should be validated by the CLI after synthesis. Default: - false

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            aws_cloud_formation_stack_properties = cloud_assembly_schema.AwsCloudFormationStackProperties(
                template_file="templateFile",
            
                # the properties below are optional
                assume_role_arn="assumeRoleArn",
                assume_role_external_id="assumeRoleExternalId",
                bootstrap_stack_version_ssm_parameter="bootstrapStackVersionSsmParameter",
                cloud_formation_execution_role_arn="cloudFormationExecutionRoleArn",
                lookup_role=cloud_assembly_schema.BootstrapRole(
                    arn="arn",
            
                    # the properties below are optional
                    assume_role_external_id="assumeRoleExternalId",
                    bootstrap_stack_version_ssm_parameter="bootstrapStackVersionSsmParameter",
                    requires_bootstrap_stack_version=123
                ),
                parameters={
                    "parameters_key": "parameters"
                },
                requires_bootstrap_stack_version=123,
                stack_name="stackName",
                stack_template_asset_object_url="stackTemplateAssetObjectUrl",
                tags={
                    "tags_key": "tags"
                },
                termination_protection=False,
                validate_on_synth=False
            )
        '''
        if isinstance(lookup_role, dict):
            lookup_role = BootstrapRole(**lookup_role)
        self._values: typing.Dict[str, typing.Any] = {
            "template_file": template_file,
        }
        if assume_role_arn is not None:
            self._values["assume_role_arn"] = assume_role_arn
        if assume_role_external_id is not None:
            self._values["assume_role_external_id"] = assume_role_external_id
        if bootstrap_stack_version_ssm_parameter is not None:
            self._values["bootstrap_stack_version_ssm_parameter"] = bootstrap_stack_version_ssm_parameter
        if cloud_formation_execution_role_arn is not None:
            self._values["cloud_formation_execution_role_arn"] = cloud_formation_execution_role_arn
        if lookup_role is not None:
            self._values["lookup_role"] = lookup_role
        if parameters is not None:
            self._values["parameters"] = parameters
        if requires_bootstrap_stack_version is not None:
            self._values["requires_bootstrap_stack_version"] = requires_bootstrap_stack_version
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if stack_template_asset_object_url is not None:
            self._values["stack_template_asset_object_url"] = stack_template_asset_object_url
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if validate_on_synth is not None:
            self._values["validate_on_synth"] = validate_on_synth

    @builtins.property
    def template_file(self) -> builtins.str:
        '''(experimental) A file relative to the assembly root which contains the CloudFormation template for this stack.

        :stability: experimental
        '''
        result = self._values.get("template_file")
        assert result is not None, "Required property 'template_file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assume_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The role that needs to be assumed to deploy the stack.

        :default: - No role is assumed (current credentials are used)

        :stability: experimental
        '''
        result = self._values.get("assume_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assume_role_external_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) External ID to use when assuming role for cloudformation deployments.

        :default: - No external ID

        :stability: experimental
        '''
        result = self._values.get("assume_role_external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bootstrap_stack_version_ssm_parameter(self) -> typing.Optional[builtins.str]:
        '''(experimental) SSM parameter where the bootstrap stack version number can be found.

        Only used if ``requiresBootstrapStackVersion`` is set.

        - If this value is not set, the bootstrap stack name must be known at
          deployment time so the stack version can be looked up from the stack
          outputs.
        - If this value is set, the bootstrap stack can have any name because
          we won't need to look it up.

        :default: - Bootstrap stack version number looked up

        :stability: experimental
        '''
        result = self._values.get("bootstrap_stack_version_ssm_parameter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud_formation_execution_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The role that is passed to CloudFormation to execute the change set.

        :default: - No role is passed (currently assumed role/credentials are used)

        :stability: experimental
        '''
        result = self._values.get("cloud_formation_execution_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lookup_role(self) -> typing.Optional["BootstrapRole"]:
        '''(experimental) The role to use to look up values from the target AWS account.

        :default: - No role is assumed (current credentials are used)

        :stability: experimental
        '''
        result = self._values.get("lookup_role")
        return typing.cast(typing.Optional["BootstrapRole"], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Values for CloudFormation stack parameters that should be passed when the stack is deployed.

        :default: - No parameters

        :stability: experimental
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def requires_bootstrap_stack_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Version of bootstrap stack required to deploy this stack.

        :default: - No bootstrap stack required

        :stability: experimental
        '''
        result = self._values.get("requires_bootstrap_stack_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name to use for the CloudFormation stack.

        :default: - name derived from artifact ID

        :stability: experimental
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stack_template_asset_object_url(self) -> typing.Optional[builtins.str]:
        '''(experimental) If the stack template has already been included in the asset manifest, its asset URL.

        :default: - Not uploaded yet, upload just before deploying

        :stability: experimental
        '''
        result = self._values.get("stack_template_asset_object_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Values for CloudFormation stack tags that should be passed when the stack is deployed.

        :default: - No tags

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to enable termination protection for this stack.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def validate_on_synth(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether this stack should be validated by the CLI after synthesis.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("validate_on_synth")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsCloudFormationStackProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.AwsDestination",
    jsii_struct_bases=[],
    name_mapping={
        "assume_role_arn": "assumeRoleArn",
        "assume_role_external_id": "assumeRoleExternalId",
        "region": "region",
    },
)
class AwsDestination:
    def __init__(
        self,
        *,
        assume_role_arn: typing.Optional[builtins.str] = None,
        assume_role_external_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Destination for assets that need to be uploaded to AWS.

        :param assume_role_arn: (experimental) The role that needs to be assumed while publishing this asset. Default: - No role will be assumed
        :param assume_role_external_id: (experimental) The ExternalId that needs to be supplied while assuming this role. Default: - No ExternalId will be supplied
        :param region: (experimental) The region where this asset will need to be published. Default: - Current region

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            aws_destination = cloud_assembly_schema.AwsDestination(
                assume_role_arn="assumeRoleArn",
                assume_role_external_id="assumeRoleExternalId",
                region="region"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if assume_role_arn is not None:
            self._values["assume_role_arn"] = assume_role_arn
        if assume_role_external_id is not None:
            self._values["assume_role_external_id"] = assume_role_external_id
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def assume_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The role that needs to be assumed while publishing this asset.

        :default: - No role will be assumed

        :stability: experimental
        '''
        result = self._values.get("assume_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assume_role_external_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ExternalId that needs to be supplied while assuming this role.

        :default: - No ExternalId will be supplied

        :stability: experimental
        '''
        result = self._values.get("assume_role_external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region where this asset will need to be published.

        :default: - Current region

        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.BootstrapRole",
    jsii_struct_bases=[],
    name_mapping={
        "arn": "arn",
        "assume_role_external_id": "assumeRoleExternalId",
        "bootstrap_stack_version_ssm_parameter": "bootstrapStackVersionSsmParameter",
        "requires_bootstrap_stack_version": "requiresBootstrapStackVersion",
    },
)
class BootstrapRole:
    def __init__(
        self,
        *,
        arn: builtins.str,
        assume_role_external_id: typing.Optional[builtins.str] = None,
        bootstrap_stack_version_ssm_parameter: typing.Optional[builtins.str] = None,
        requires_bootstrap_stack_version: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Information needed to access an IAM role created as part of the bootstrap process.

        :param arn: (experimental) The ARN of the IAM role created as part of bootrapping e.g. lookupRoleArn.
        :param assume_role_external_id: (experimental) External ID to use when assuming the bootstrap role. Default: - No external ID
        :param bootstrap_stack_version_ssm_parameter: (experimental) Name of SSM parameter with bootstrap stack version. Default: - Discover SSM parameter by reading stack
        :param requires_bootstrap_stack_version: (experimental) Version of bootstrap stack required to use this role. Default: - No bootstrap stack required

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            bootstrap_role = cloud_assembly_schema.BootstrapRole(
                arn="arn",
            
                # the properties below are optional
                assume_role_external_id="assumeRoleExternalId",
                bootstrap_stack_version_ssm_parameter="bootstrapStackVersionSsmParameter",
                requires_bootstrap_stack_version=123
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "arn": arn,
        }
        if assume_role_external_id is not None:
            self._values["assume_role_external_id"] = assume_role_external_id
        if bootstrap_stack_version_ssm_parameter is not None:
            self._values["bootstrap_stack_version_ssm_parameter"] = bootstrap_stack_version_ssm_parameter
        if requires_bootstrap_stack_version is not None:
            self._values["requires_bootstrap_stack_version"] = requires_bootstrap_stack_version

    @builtins.property
    def arn(self) -> builtins.str:
        '''(experimental) The ARN of the IAM role created as part of bootrapping e.g. lookupRoleArn.

        :stability: experimental
        '''
        result = self._values.get("arn")
        assert result is not None, "Required property 'arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assume_role_external_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) External ID to use when assuming the bootstrap role.

        :default: - No external ID

        :stability: experimental
        '''
        result = self._values.get("assume_role_external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bootstrap_stack_version_ssm_parameter(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of SSM parameter with bootstrap stack version.

        :default: - Discover SSM parameter by reading stack

        :stability: experimental
        '''
        result = self._values.get("bootstrap_stack_version_ssm_parameter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def requires_bootstrap_stack_version(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Version of bootstrap stack required to use this role.

        :default: - No bootstrap stack required

        :stability: experimental
        '''
        result = self._values.get("requires_bootstrap_stack_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BootstrapRole(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.ContainerImageAssetMetadataEntry",
    jsii_struct_bases=[],
    name_mapping={
        "id": "id",
        "packaging": "packaging",
        "path": "path",
        "source_hash": "sourceHash",
        "build_args": "buildArgs",
        "file": "file",
        "image_name_parameter": "imageNameParameter",
        "image_tag": "imageTag",
        "repository_name": "repositoryName",
        "target": "target",
    },
)
class ContainerImageAssetMetadataEntry:
    def __init__(
        self,
        *,
        id: builtins.str,
        packaging: builtins.str,
        path: builtins.str,
        source_hash: builtins.str,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        file: typing.Optional[builtins.str] = None,
        image_name_parameter: typing.Optional[builtins.str] = None,
        image_tag: typing.Optional[builtins.str] = None,
        repository_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Metadata Entry spec for container images.

        :param id: (experimental) Logical identifier for the asset.
        :param packaging: (experimental) Type of asset.
        :param path: (experimental) Path on disk to the asset.
        :param source_hash: (experimental) The hash of the asset source.
        :param build_args: (experimental) Build args to pass to the ``docker build`` command. Default: no build args are passed
        :param file: (experimental) Path to the Dockerfile (relative to the directory). Default: - no file is passed
        :param image_name_parameter: (deprecated) ECR Repository name and repo digest (separated by "@sha256:") where this image is stored. Default: undefined If not specified, ``repositoryName`` and ``imageTag`` are required because otherwise how will the stack know where to find the asset, ha?
        :param image_tag: (experimental) The docker image tag to use for tagging pushed images. This field is required if ``imageParameterName`` is ommited (otherwise, the app won't be able to find the image). Default: - this parameter is REQUIRED after 1.21.0
        :param repository_name: (experimental) ECR repository name, if omitted a default name based on the asset's ID is used instead. Specify this property if you need to statically address the image, e.g. from a Kubernetes Pod. Note, this is only the repository name, without the registry and the tag parts. Default: - this parameter is REQUIRED after 1.21.0
        :param target: (experimental) Docker target to build to. Default: no build target

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            container_image_asset_metadata_entry = cloud_assembly_schema.ContainerImageAssetMetadataEntry(
                id="id",
                packaging="packaging",
                path="path",
                source_hash="sourceHash",
            
                # the properties below are optional
                build_args={
                    "build_args_key": "buildArgs"
                },
                file="file",
                image_name_parameter="imageNameParameter",
                image_tag="imageTag",
                repository_name="repositoryName",
                target="target"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "id": id,
            "packaging": packaging,
            "path": path,
            "source_hash": source_hash,
        }
        if build_args is not None:
            self._values["build_args"] = build_args
        if file is not None:
            self._values["file"] = file
        if image_name_parameter is not None:
            self._values["image_name_parameter"] = image_name_parameter
        if image_tag is not None:
            self._values["image_tag"] = image_tag
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def id(self) -> builtins.str:
        '''(experimental) Logical identifier for the asset.

        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def packaging(self) -> builtins.str:
        '''(experimental) Type of asset.

        :stability: experimental
        '''
        result = self._values.get("packaging")
        assert result is not None, "Required property 'packaging' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) Path on disk to the asset.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_hash(self) -> builtins.str:
        '''(experimental) The hash of the asset source.

        :stability: experimental
        '''
        result = self._values.get("source_hash")
        assert result is not None, "Required property 'source_hash' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_args(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Build args to pass to the ``docker build`` command.

        :default: no build args are passed

        :stability: experimental
        '''
        result = self._values.get("build_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def file(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path to the Dockerfile (relative to the directory).

        :default: - no file is passed

        :stability: experimental
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_name_parameter(self) -> typing.Optional[builtins.str]:
        '''(deprecated) ECR Repository name and repo digest (separated by "@sha256:") where this image is stored.

        :default:

        undefined If not specified, ``repositoryName`` and ``imageTag`` are
        required because otherwise how will the stack know where to find the asset,
        ha?

        :deprecated:

        specify ``repositoryName`` and ``imageTag`` instead, and then you
        know where the image will go.

        :stability: deprecated
        '''
        result = self._values.get("image_name_parameter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) The docker image tag to use for tagging pushed images.

        This field is
        required if ``imageParameterName`` is ommited (otherwise, the app won't be
        able to find the image).

        :default: - this parameter is REQUIRED after 1.21.0

        :stability: experimental
        '''
        result = self._values.get("image_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) ECR repository name, if omitted a default name based on the asset's ID is used instead.

        Specify this property if you need to statically address the
        image, e.g. from a Kubernetes Pod. Note, this is only the repository name,
        without the registry and the tag parts.

        :default: - this parameter is REQUIRED after 1.21.0

        :stability: experimental
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''(experimental) Docker target to build to.

        :default: no build target

        :stability: experimental
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerImageAssetMetadataEntry(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.cloud_assembly_schema.ContextProvider")
class ContextProvider(enum.Enum):
    '''(experimental) Identifier for the context provider.

    :stability: experimental
    '''

    AMI_PROVIDER = "AMI_PROVIDER"
    '''(experimental) AMI provider.

    :stability: experimental
    '''
    AVAILABILITY_ZONE_PROVIDER = "AVAILABILITY_ZONE_PROVIDER"
    '''(experimental) AZ provider.

    :stability: experimental
    '''
    HOSTED_ZONE_PROVIDER = "HOSTED_ZONE_PROVIDER"
    '''(experimental) Route53 Hosted Zone provider.

    :stability: experimental
    '''
    SSM_PARAMETER_PROVIDER = "SSM_PARAMETER_PROVIDER"
    '''(experimental) SSM Parameter Provider.

    :stability: experimental
    '''
    VPC_PROVIDER = "VPC_PROVIDER"
    '''(experimental) VPC Provider.

    :stability: experimental
    '''
    ENDPOINT_SERVICE_AVAILABILITY_ZONE_PROVIDER = "ENDPOINT_SERVICE_AVAILABILITY_ZONE_PROVIDER"
    '''(experimental) VPC Endpoint Service AZ Provider.

    :stability: experimental
    '''
    LOAD_BALANCER_PROVIDER = "LOAD_BALANCER_PROVIDER"
    '''(experimental) Load balancer provider.

    :stability: experimental
    '''
    LOAD_BALANCER_LISTENER_PROVIDER = "LOAD_BALANCER_LISTENER_PROVIDER"
    '''(experimental) Load balancer listener provider.

    :stability: experimental
    '''
    SECURITY_GROUP_PROVIDER = "SECURITY_GROUP_PROVIDER"
    '''(experimental) Security group provider.

    :stability: experimental
    '''
    KEY_PROVIDER = "KEY_PROVIDER"
    '''(experimental) KMS Key Provider.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.DockerImageAsset",
    jsii_struct_bases=[],
    name_mapping={"destinations": "destinations", "source": "source"},
)
class DockerImageAsset:
    def __init__(
        self,
        *,
        destinations: typing.Mapping[builtins.str, "DockerImageDestination"],
        source: "DockerImageSource",
    ) -> None:
        '''(experimental) A file asset.

        :param destinations: (experimental) Destinations for this file asset.
        :param source: (experimental) Source description for file assets.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            docker_image_asset = cloud_assembly_schema.DockerImageAsset(
                destinations={
                    "destinations_key": cloud_assembly_schema.DockerImageDestination(
                        image_tag="imageTag",
                        repository_name="repositoryName",
            
                        # the properties below are optional
                        assume_role_arn="assumeRoleArn",
                        assume_role_external_id="assumeRoleExternalId",
                        region="region"
                    )
                },
                source=cloud_assembly_schema.DockerImageSource(
                    directory="directory",
                    docker_build_args={
                        "docker_build_args_key": "dockerBuildArgs"
                    },
                    docker_build_target="dockerBuildTarget",
                    docker_file="dockerFile",
                    executable=["executable"]
                )
            )
        '''
        if isinstance(source, dict):
            source = DockerImageSource(**source)
        self._values: typing.Dict[str, typing.Any] = {
            "destinations": destinations,
            "source": source,
        }

    @builtins.property
    def destinations(self) -> typing.Mapping[builtins.str, "DockerImageDestination"]:
        '''(experimental) Destinations for this file asset.

        :stability: experimental
        '''
        result = self._values.get("destinations")
        assert result is not None, "Required property 'destinations' is missing"
        return typing.cast(typing.Mapping[builtins.str, "DockerImageDestination"], result)

    @builtins.property
    def source(self) -> "DockerImageSource":
        '''(experimental) Source description for file assets.

        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("DockerImageSource", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerImageAsset(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.DockerImageDestination",
    jsii_struct_bases=[AwsDestination],
    name_mapping={
        "assume_role_arn": "assumeRoleArn",
        "assume_role_external_id": "assumeRoleExternalId",
        "region": "region",
        "image_tag": "imageTag",
        "repository_name": "repositoryName",
    },
)
class DockerImageDestination(AwsDestination):
    def __init__(
        self,
        *,
        assume_role_arn: typing.Optional[builtins.str] = None,
        assume_role_external_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        image_tag: builtins.str,
        repository_name: builtins.str,
    ) -> None:
        '''(experimental) Where to publish docker images.

        :param assume_role_arn: (experimental) The role that needs to be assumed while publishing this asset. Default: - No role will be assumed
        :param assume_role_external_id: (experimental) The ExternalId that needs to be supplied while assuming this role. Default: - No ExternalId will be supplied
        :param region: (experimental) The region where this asset will need to be published. Default: - Current region
        :param image_tag: (experimental) Tag of the image to publish.
        :param repository_name: (experimental) Name of the ECR repository to publish to.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            docker_image_destination = cloud_assembly_schema.DockerImageDestination(
                image_tag="imageTag",
                repository_name="repositoryName",
            
                # the properties below are optional
                assume_role_arn="assumeRoleArn",
                assume_role_external_id="assumeRoleExternalId",
                region="region"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "image_tag": image_tag,
            "repository_name": repository_name,
        }
        if assume_role_arn is not None:
            self._values["assume_role_arn"] = assume_role_arn
        if assume_role_external_id is not None:
            self._values["assume_role_external_id"] = assume_role_external_id
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def assume_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The role that needs to be assumed while publishing this asset.

        :default: - No role will be assumed

        :stability: experimental
        '''
        result = self._values.get("assume_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assume_role_external_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ExternalId that needs to be supplied while assuming this role.

        :default: - No ExternalId will be supplied

        :stability: experimental
        '''
        result = self._values.get("assume_role_external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region where this asset will need to be published.

        :default: - Current region

        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_tag(self) -> builtins.str:
        '''(experimental) Tag of the image to publish.

        :stability: experimental
        '''
        result = self._values.get("image_tag")
        assert result is not None, "Required property 'image_tag' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository_name(self) -> builtins.str:
        '''(experimental) Name of the ECR repository to publish to.

        :stability: experimental
        '''
        result = self._values.get("repository_name")
        assert result is not None, "Required property 'repository_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerImageDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.DockerImageSource",
    jsii_struct_bases=[],
    name_mapping={
        "directory": "directory",
        "docker_build_args": "dockerBuildArgs",
        "docker_build_target": "dockerBuildTarget",
        "docker_file": "dockerFile",
        "executable": "executable",
    },
)
class DockerImageSource:
    def __init__(
        self,
        *,
        directory: typing.Optional[builtins.str] = None,
        docker_build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        docker_build_target: typing.Optional[builtins.str] = None,
        docker_file: typing.Optional[builtins.str] = None,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for how to produce a Docker image from a source.

        :param directory: (experimental) The directory containing the Docker image build instructions. This path is relative to the asset manifest location. Default: - Exactly one of ``directory`` and ``executable`` is required
        :param docker_build_args: (experimental) Additional build arguments. Only allowed when ``directory`` is set. Default: - No additional build arguments
        :param docker_build_target: (experimental) Target build stage in a Dockerfile with multiple build stages. Only allowed when ``directory`` is set. Default: - The last stage in the Dockerfile
        :param docker_file: (experimental) The name of the file with build instructions. Only allowed when ``directory`` is set. Default: "Dockerfile"
        :param executable: (experimental) A command-line executable that returns the name of a local Docker image on stdout after being run. Default: - Exactly one of ``directory`` and ``executable`` is required

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            docker_image_source = cloud_assembly_schema.DockerImageSource(
                directory="directory",
                docker_build_args={
                    "docker_build_args_key": "dockerBuildArgs"
                },
                docker_build_target="dockerBuildTarget",
                docker_file="dockerFile",
                executable=["executable"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if directory is not None:
            self._values["directory"] = directory
        if docker_build_args is not None:
            self._values["docker_build_args"] = docker_build_args
        if docker_build_target is not None:
            self._values["docker_build_target"] = docker_build_target
        if docker_file is not None:
            self._values["docker_file"] = docker_file
        if executable is not None:
            self._values["executable"] = executable

    @builtins.property
    def directory(self) -> typing.Optional[builtins.str]:
        '''(experimental) The directory containing the Docker image build instructions.

        This path is relative to the asset manifest location.

        :default: - Exactly one of ``directory`` and ``executable`` is required

        :stability: experimental
        '''
        result = self._values.get("directory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docker_build_args(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Additional build arguments.

        Only allowed when ``directory`` is set.

        :default: - No additional build arguments

        :stability: experimental
        '''
        result = self._values.get("docker_build_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def docker_build_target(self) -> typing.Optional[builtins.str]:
        '''(experimental) Target build stage in a Dockerfile with multiple build stages.

        Only allowed when ``directory`` is set.

        :default: - The last stage in the Dockerfile

        :stability: experimental
        '''
        result = self._values.get("docker_build_target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docker_file(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the file with build instructions.

        Only allowed when ``directory`` is set.

        :default: "Dockerfile"

        :stability: experimental
        '''
        result = self._values.get("docker_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def executable(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A command-line executable that returns the name of a local Docker image on stdout after being run.

        :default: - Exactly one of ``directory`` and ``executable`` is required

        :stability: experimental
        '''
        result = self._values.get("executable")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerImageSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.EndpointServiceAvailabilityZonesContextQuery",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "region": "region",
        "service_name": "serviceName",
        "lookup_role_arn": "lookupRoleArn",
    },
)
class EndpointServiceAvailabilityZonesContextQuery:
    def __init__(
        self,
        *,
        account: builtins.str,
        region: builtins.str,
        service_name: builtins.str,
        lookup_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Query to endpoint service context provider.

        :param account: (experimental) Query account.
        :param region: (experimental) Query region.
        :param service_name: (experimental) Query service name.
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            endpoint_service_availability_zones_context_query = cloud_assembly_schema.EndpointServiceAvailabilityZonesContextQuery(
                account="account",
                region="region",
                service_name="serviceName",
            
                # the properties below are optional
                lookup_role_arn="lookupRoleArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "region": region,
            "service_name": service_name,
        }
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Query account.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Query region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_name(self) -> builtins.str:
        '''(experimental) Query service name.

        :stability: experimental
        '''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EndpointServiceAvailabilityZonesContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.FileAsset",
    jsii_struct_bases=[],
    name_mapping={"destinations": "destinations", "source": "source"},
)
class FileAsset:
    def __init__(
        self,
        *,
        destinations: typing.Mapping[builtins.str, "FileDestination"],
        source: "FileSource",
    ) -> None:
        '''(experimental) A file asset.

        :param destinations: (experimental) Destinations for this file asset.
        :param source: (experimental) Source description for file assets.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            file_asset = cloud_assembly_schema.FileAsset(
                destinations={
                    "destinations_key": cloud_assembly_schema.FileDestination(
                        bucket_name="bucketName",
                        object_key="objectKey",
            
                        # the properties below are optional
                        assume_role_arn="assumeRoleArn",
                        assume_role_external_id="assumeRoleExternalId",
                        region="region"
                    )
                },
                source=cloud_assembly_schema.FileSource(
                    executable=["executable"],
                    packaging=cloud_assembly_schema.FileAssetPackaging.FILE,
                    path="path"
                )
            )
        '''
        if isinstance(source, dict):
            source = FileSource(**source)
        self._values: typing.Dict[str, typing.Any] = {
            "destinations": destinations,
            "source": source,
        }

    @builtins.property
    def destinations(self) -> typing.Mapping[builtins.str, "FileDestination"]:
        '''(experimental) Destinations for this file asset.

        :stability: experimental
        '''
        result = self._values.get("destinations")
        assert result is not None, "Required property 'destinations' is missing"
        return typing.cast(typing.Mapping[builtins.str, "FileDestination"], result)

    @builtins.property
    def source(self) -> "FileSource":
        '''(experimental) Source description for file assets.

        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("FileSource", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileAsset(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.FileAssetMetadataEntry",
    jsii_struct_bases=[],
    name_mapping={
        "artifact_hash_parameter": "artifactHashParameter",
        "id": "id",
        "packaging": "packaging",
        "path": "path",
        "s3_bucket_parameter": "s3BucketParameter",
        "s3_key_parameter": "s3KeyParameter",
        "source_hash": "sourceHash",
    },
)
class FileAssetMetadataEntry:
    def __init__(
        self,
        *,
        artifact_hash_parameter: builtins.str,
        id: builtins.str,
        packaging: builtins.str,
        path: builtins.str,
        s3_bucket_parameter: builtins.str,
        s3_key_parameter: builtins.str,
        source_hash: builtins.str,
    ) -> None:
        '''(experimental) Metadata Entry spec for files.

        :param artifact_hash_parameter: (experimental) The name of the parameter where the hash of the bundled asset should be passed in.
        :param id: (experimental) Logical identifier for the asset.
        :param packaging: (experimental) Requested packaging style.
        :param path: (experimental) Path on disk to the asset.
        :param s3_bucket_parameter: (experimental) Name of parameter where S3 bucket should be passed in.
        :param s3_key_parameter: (experimental) Name of parameter where S3 key should be passed in.
        :param source_hash: (experimental) The hash of the asset source.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            file_asset_metadata_entry = cloud_assembly_schema.FileAssetMetadataEntry(
                artifact_hash_parameter="artifactHashParameter",
                id="id",
                packaging="packaging",
                path="path",
                s3_bucket_parameter="s3BucketParameter",
                s3_key_parameter="s3KeyParameter",
                source_hash="sourceHash"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "artifact_hash_parameter": artifact_hash_parameter,
            "id": id,
            "packaging": packaging,
            "path": path,
            "s3_bucket_parameter": s3_bucket_parameter,
            "s3_key_parameter": s3_key_parameter,
            "source_hash": source_hash,
        }

    @builtins.property
    def artifact_hash_parameter(self) -> builtins.str:
        '''(experimental) The name of the parameter where the hash of the bundled asset should be passed in.

        :stability: experimental
        '''
        result = self._values.get("artifact_hash_parameter")
        assert result is not None, "Required property 'artifact_hash_parameter' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> builtins.str:
        '''(experimental) Logical identifier for the asset.

        :stability: experimental
        '''
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def packaging(self) -> builtins.str:
        '''(experimental) Requested packaging style.

        :stability: experimental
        '''
        result = self._values.get("packaging")
        assert result is not None, "Required property 'packaging' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        '''(experimental) Path on disk to the asset.

        :stability: experimental
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_bucket_parameter(self) -> builtins.str:
        '''(experimental) Name of parameter where S3 bucket should be passed in.

        :stability: experimental
        '''
        result = self._values.get("s3_bucket_parameter")
        assert result is not None, "Required property 's3_bucket_parameter' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def s3_key_parameter(self) -> builtins.str:
        '''(experimental) Name of parameter where S3 key should be passed in.

        :stability: experimental
        '''
        result = self._values.get("s3_key_parameter")
        assert result is not None, "Required property 's3_key_parameter' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_hash(self) -> builtins.str:
        '''(experimental) The hash of the asset source.

        :stability: experimental
        '''
        result = self._values.get("source_hash")
        assert result is not None, "Required property 'source_hash' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileAssetMetadataEntry(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.cloud_assembly_schema.FileAssetPackaging")
class FileAssetPackaging(enum.Enum):
    '''(experimental) Packaging strategy for file assets.

    :stability: experimental
    '''

    FILE = "FILE"
    '''(experimental) Upload the given path as a file.

    :stability: experimental
    '''
    ZIP_DIRECTORY = "ZIP_DIRECTORY"
    '''(experimental) The given path is a directory, zip it and upload.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.FileDestination",
    jsii_struct_bases=[AwsDestination],
    name_mapping={
        "assume_role_arn": "assumeRoleArn",
        "assume_role_external_id": "assumeRoleExternalId",
        "region": "region",
        "bucket_name": "bucketName",
        "object_key": "objectKey",
    },
)
class FileDestination(AwsDestination):
    def __init__(
        self,
        *,
        assume_role_arn: typing.Optional[builtins.str] = None,
        assume_role_external_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        bucket_name: builtins.str,
        object_key: builtins.str,
    ) -> None:
        '''(experimental) Where in S3 a file asset needs to be published.

        :param assume_role_arn: (experimental) The role that needs to be assumed while publishing this asset. Default: - No role will be assumed
        :param assume_role_external_id: (experimental) The ExternalId that needs to be supplied while assuming this role. Default: - No ExternalId will be supplied
        :param region: (experimental) The region where this asset will need to be published. Default: - Current region
        :param bucket_name: (experimental) The name of the bucket.
        :param object_key: (experimental) The destination object key.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            file_destination = cloud_assembly_schema.FileDestination(
                bucket_name="bucketName",
                object_key="objectKey",
            
                # the properties below are optional
                assume_role_arn="assumeRoleArn",
                assume_role_external_id="assumeRoleExternalId",
                region="region"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
            "object_key": object_key,
        }
        if assume_role_arn is not None:
            self._values["assume_role_arn"] = assume_role_arn
        if assume_role_external_id is not None:
            self._values["assume_role_external_id"] = assume_role_external_id
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def assume_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The role that needs to be assumed while publishing this asset.

        :default: - No role will be assumed

        :stability: experimental
        '''
        result = self._values.get("assume_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assume_role_external_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ExternalId that needs to be supplied while assuming this role.

        :default: - No ExternalId will be supplied

        :stability: experimental
        '''
        result = self._values.get("assume_role_external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region where this asset will need to be published.

        :default: - Current region

        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''(experimental) The name of the bucket.

        :stability: experimental
        '''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object_key(self) -> builtins.str:
        '''(experimental) The destination object key.

        :stability: experimental
        '''
        result = self._values.get("object_key")
        assert result is not None, "Required property 'object_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.FileSource",
    jsii_struct_bases=[],
    name_mapping={
        "executable": "executable",
        "packaging": "packaging",
        "path": "path",
    },
)
class FileSource:
    def __init__(
        self,
        *,
        executable: typing.Optional[typing.Sequence[builtins.str]] = None,
        packaging: typing.Optional[FileAssetPackaging] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Describe the source of a file asset.

        :param executable: (experimental) External command which will produce the file asset to upload. Default: - Exactly one of ``executable`` and ``path`` is required.
        :param packaging: (experimental) Packaging method. Only allowed when ``path`` is specified. Default: FILE
        :param path: (experimental) The filesystem object to upload. This path is relative to the asset manifest location. Default: - Exactly one of ``executable`` and ``path`` is required.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            file_source = cloud_assembly_schema.FileSource(
                executable=["executable"],
                packaging=cloud_assembly_schema.FileAssetPackaging.FILE,
                path="path"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if executable is not None:
            self._values["executable"] = executable
        if packaging is not None:
            self._values["packaging"] = packaging
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def executable(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) External command which will produce the file asset to upload.

        :default: - Exactly one of ``executable`` and ``path`` is required.

        :stability: experimental
        '''
        result = self._values.get("executable")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def packaging(self) -> typing.Optional[FileAssetPackaging]:
        '''(experimental) Packaging method.

        Only allowed when ``path`` is specified.

        :default: FILE

        :stability: experimental
        '''
        result = self._values.get("packaging")
        return typing.cast(typing.Optional[FileAssetPackaging], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''(experimental) The filesystem object to upload.

        This path is relative to the asset manifest location.

        :default: - Exactly one of ``executable`` and ``path`` is required.

        :stability: experimental
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.HostedZoneContextQuery",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "domain_name": "domainName",
        "region": "region",
        "lookup_role_arn": "lookupRoleArn",
        "private_zone": "privateZone",
        "vpc_id": "vpcId",
    },
)
class HostedZoneContextQuery:
    def __init__(
        self,
        *,
        account: builtins.str,
        domain_name: builtins.str,
        region: builtins.str,
        lookup_role_arn: typing.Optional[builtins.str] = None,
        private_zone: typing.Optional[builtins.bool] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Query to hosted zone context provider.

        :param account: (experimental) Query account.
        :param domain_name: (experimental) The domain name e.g. example.com to lookup.
        :param region: (experimental) Query region.
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None
        :param private_zone: (experimental) True if the zone you want to find is a private hosted zone. Default: false
        :param vpc_id: (experimental) The VPC ID to that the private zone must be associated with. If you provide VPC ID and privateZone is false, this will return no results and raise an error. Default: - Required if privateZone=true

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            hosted_zone_context_query = cloud_assembly_schema.HostedZoneContextQuery(
                account="account",
                domain_name="domainName",
                region="region",
            
                # the properties below are optional
                lookup_role_arn="lookupRoleArn",
                private_zone=False,
                vpc_id="vpcId"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "domain_name": domain_name,
            "region": region,
        }
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn
        if private_zone is not None:
            self._values["private_zone"] = private_zone
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Query account.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''(experimental) The domain name e.g. example.com to lookup.

        :stability: experimental
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Query region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_zone(self) -> typing.Optional[builtins.bool]:
        '''(experimental) True if the zone you want to find is a private hosted zone.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("private_zone")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The VPC ID to that the private zone must be associated with.

        If you provide VPC ID and privateZone is false, this will return no results
        and raise an error.

        :default: - Required if privateZone=true

        :stability: experimental
        '''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HostedZoneContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.KeyContextQuery",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "alias_name": "aliasName",
        "region": "region",
        "lookup_role_arn": "lookupRoleArn",
    },
)
class KeyContextQuery:
    def __init__(
        self,
        *,
        account: builtins.str,
        alias_name: builtins.str,
        region: builtins.str,
        lookup_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Query input for looking up a KMS Key.

        :param account: (experimental) Query account.
        :param alias_name: (experimental) Alias name used to search the Key.
        :param region: (experimental) Query region.
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            key_context_query = cloud_assembly_schema.KeyContextQuery(
                account="account",
                alias_name="aliasName",
                region="region",
            
                # the properties below are optional
                lookup_role_arn="lookupRoleArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "alias_name": alias_name,
            "region": region,
        }
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Query account.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias_name(self) -> builtins.str:
        '''(experimental) Alias name used to search the Key.

        :stability: experimental
        '''
        result = self._values.get("alias_name")
        assert result is not None, "Required property 'alias_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Query region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KeyContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.LoadBalancerFilter",
    jsii_struct_bases=[],
    name_mapping={
        "load_balancer_type": "loadBalancerType",
        "load_balancer_arn": "loadBalancerArn",
        "load_balancer_tags": "loadBalancerTags",
    },
)
class LoadBalancerFilter:
    def __init__(
        self,
        *,
        load_balancer_type: "LoadBalancerType",
        load_balancer_arn: typing.Optional[builtins.str] = None,
        load_balancer_tags: typing.Optional[typing.Sequence["Tag"]] = None,
    ) -> None:
        '''(experimental) Filters for selecting load balancers.

        :param load_balancer_type: (experimental) Filter load balancers by their type.
        :param load_balancer_arn: (experimental) Find by load balancer's ARN. Default: - does not search by load balancer arn
        :param load_balancer_tags: (experimental) Match load balancer tags. Default: - does not match load balancers by tags

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            load_balancer_filter = cloud_assembly_schema.LoadBalancerFilter(
                load_balancer_type=cloud_assembly_schema.LoadBalancerType.NETWORK,
            
                # the properties below are optional
                load_balancer_arn="loadBalancerArn",
                load_balancer_tags=[cloud_assembly_schema.Tag(
                    key="key",
                    value="value"
                )]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "load_balancer_type": load_balancer_type,
        }
        if load_balancer_arn is not None:
            self._values["load_balancer_arn"] = load_balancer_arn
        if load_balancer_tags is not None:
            self._values["load_balancer_tags"] = load_balancer_tags

    @builtins.property
    def load_balancer_type(self) -> "LoadBalancerType":
        '''(experimental) Filter load balancers by their type.

        :stability: experimental
        '''
        result = self._values.get("load_balancer_type")
        assert result is not None, "Required property 'load_balancer_type' is missing"
        return typing.cast("LoadBalancerType", result)

    @builtins.property
    def load_balancer_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) Find by load balancer's ARN.

        :default: - does not search by load balancer arn

        :stability: experimental
        '''
        result = self._values.get("load_balancer_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def load_balancer_tags(self) -> typing.Optional[typing.List["Tag"]]:
        '''(experimental) Match load balancer tags.

        :default: - does not match load balancers by tags

        :stability: experimental
        '''
        result = self._values.get("load_balancer_tags")
        return typing.cast(typing.Optional[typing.List["Tag"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.LoadBalancerListenerContextQuery",
    jsii_struct_bases=[LoadBalancerFilter],
    name_mapping={
        "load_balancer_type": "loadBalancerType",
        "load_balancer_arn": "loadBalancerArn",
        "load_balancer_tags": "loadBalancerTags",
        "account": "account",
        "region": "region",
        "listener_arn": "listenerArn",
        "listener_port": "listenerPort",
        "listener_protocol": "listenerProtocol",
        "lookup_role_arn": "lookupRoleArn",
    },
)
class LoadBalancerListenerContextQuery(LoadBalancerFilter):
    def __init__(
        self,
        *,
        load_balancer_type: "LoadBalancerType",
        load_balancer_arn: typing.Optional[builtins.str] = None,
        load_balancer_tags: typing.Optional[typing.Sequence["Tag"]] = None,
        account: builtins.str,
        region: builtins.str,
        listener_arn: typing.Optional[builtins.str] = None,
        listener_port: typing.Optional[jsii.Number] = None,
        listener_protocol: typing.Optional["LoadBalancerListenerProtocol"] = None,
        lookup_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Query input for looking up a load balancer listener.

        :param load_balancer_type: (experimental) Filter load balancers by their type.
        :param load_balancer_arn: (experimental) Find by load balancer's ARN. Default: - does not search by load balancer arn
        :param load_balancer_tags: (experimental) Match load balancer tags. Default: - does not match load balancers by tags
        :param account: (experimental) Query account.
        :param region: (experimental) Query region.
        :param listener_arn: (experimental) Find by listener's arn. Default: - does not find by listener arn
        :param listener_port: (experimental) Filter listeners by listener port. Default: - does not filter by a listener port
        :param listener_protocol: (experimental) Filter by listener protocol. Default: - does not filter by listener protocol
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            load_balancer_listener_context_query = cloud_assembly_schema.LoadBalancerListenerContextQuery(
                account="account",
                load_balancer_type=cloud_assembly_schema.LoadBalancerType.NETWORK,
                region="region",
            
                # the properties below are optional
                listener_arn="listenerArn",
                listener_port=123,
                listener_protocol=cloud_assembly_schema.LoadBalancerListenerProtocol.HTTP,
                load_balancer_arn="loadBalancerArn",
                load_balancer_tags=[cloud_assembly_schema.Tag(
                    key="key",
                    value="value"
                )],
                lookup_role_arn="lookupRoleArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "load_balancer_type": load_balancer_type,
            "account": account,
            "region": region,
        }
        if load_balancer_arn is not None:
            self._values["load_balancer_arn"] = load_balancer_arn
        if load_balancer_tags is not None:
            self._values["load_balancer_tags"] = load_balancer_tags
        if listener_arn is not None:
            self._values["listener_arn"] = listener_arn
        if listener_port is not None:
            self._values["listener_port"] = listener_port
        if listener_protocol is not None:
            self._values["listener_protocol"] = listener_protocol
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn

    @builtins.property
    def load_balancer_type(self) -> "LoadBalancerType":
        '''(experimental) Filter load balancers by their type.

        :stability: experimental
        '''
        result = self._values.get("load_balancer_type")
        assert result is not None, "Required property 'load_balancer_type' is missing"
        return typing.cast("LoadBalancerType", result)

    @builtins.property
    def load_balancer_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) Find by load balancer's ARN.

        :default: - does not search by load balancer arn

        :stability: experimental
        '''
        result = self._values.get("load_balancer_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def load_balancer_tags(self) -> typing.Optional[typing.List["Tag"]]:
        '''(experimental) Match load balancer tags.

        :default: - does not match load balancers by tags

        :stability: experimental
        '''
        result = self._values.get("load_balancer_tags")
        return typing.cast(typing.Optional[typing.List["Tag"]], result)

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Query account.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Query region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def listener_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) Find by listener's arn.

        :default: - does not find by listener arn

        :stability: experimental
        '''
        result = self._values.get("listener_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def listener_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Filter listeners by listener port.

        :default: - does not filter by a listener port

        :stability: experimental
        '''
        result = self._values.get("listener_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def listener_protocol(self) -> typing.Optional["LoadBalancerListenerProtocol"]:
        '''(experimental) Filter by listener protocol.

        :default: - does not filter by listener protocol

        :stability: experimental
        '''
        result = self._values.get("listener_protocol")
        return typing.cast(typing.Optional["LoadBalancerListenerProtocol"], result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerListenerContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.cloud_assembly_schema.LoadBalancerListenerProtocol")
class LoadBalancerListenerProtocol(enum.Enum):
    '''(experimental) The protocol for connections from clients to the load balancer.

    :stability: experimental
    '''

    HTTP = "HTTP"
    '''(experimental) HTTP protocol.

    :stability: experimental
    '''
    HTTPS = "HTTPS"
    '''(experimental) HTTPS protocol.

    :stability: experimental
    '''
    TCP = "TCP"
    '''(experimental) TCP protocol.

    :stability: experimental
    '''
    TLS = "TLS"
    '''(experimental) TLS protocol.

    :stability: experimental
    '''
    UDP = "UDP"
    '''(experimental) UDP protocol.

    :stability: experimental
    '''
    TCP_UDP = "TCP_UDP"
    '''(experimental) TCP and UDP protocol.

    :stability: experimental
    '''


@jsii.enum(jsii_type="monocdk.cloud_assembly_schema.LoadBalancerType")
class LoadBalancerType(enum.Enum):
    '''(experimental) Type of load balancer.

    :stability: experimental
    '''

    NETWORK = "NETWORK"
    '''(experimental) Network load balancer.

    :stability: experimental
    '''
    APPLICATION = "APPLICATION"
    '''(experimental) Application load balancer.

    :stability: experimental
    '''


class Manifest(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.cloud_assembly_schema.Manifest",
):
    '''(experimental) Protocol utility class.

    :stability: experimental
    '''

    @jsii.member(jsii_name="load") # type: ignore[misc]
    @builtins.classmethod
    def load(cls, file_path: builtins.str) -> AssemblyManifest:
        '''(deprecated) Deprecated.

        :param file_path: -

        :deprecated: use ``loadAssemblyManifest()``

        :stability: deprecated
        '''
        return typing.cast(AssemblyManifest, jsii.sinvoke(cls, "load", [file_path]))

    @jsii.member(jsii_name="loadAssemblyManifest") # type: ignore[misc]
    @builtins.classmethod
    def load_assembly_manifest(cls, file_path: builtins.str) -> AssemblyManifest:
        '''(experimental) Load and validates the cloud assembly manifest from file.

        :param file_path: - path to the manifest file.

        :stability: experimental
        '''
        return typing.cast(AssemblyManifest, jsii.sinvoke(cls, "loadAssemblyManifest", [file_path]))

    @jsii.member(jsii_name="loadAssetManifest") # type: ignore[misc]
    @builtins.classmethod
    def load_asset_manifest(cls, file_path: builtins.str) -> AssetManifest:
        '''(experimental) Load and validates the asset manifest from file.

        :param file_path: - path to the manifest file.

        :stability: experimental
        '''
        return typing.cast(AssetManifest, jsii.sinvoke(cls, "loadAssetManifest", [file_path]))

    @jsii.member(jsii_name="save") # type: ignore[misc]
    @builtins.classmethod
    def save(cls, manifest: AssemblyManifest, file_path: builtins.str) -> None:
        '''(deprecated) Deprecated.

        :param manifest: -
        :param file_path: -

        :deprecated: use ``saveAssemblyManifest()``

        :stability: deprecated
        '''
        return typing.cast(None, jsii.sinvoke(cls, "save", [manifest, file_path]))

    @jsii.member(jsii_name="saveAssemblyManifest") # type: ignore[misc]
    @builtins.classmethod
    def save_assembly_manifest(
        cls,
        manifest: AssemblyManifest,
        file_path: builtins.str,
    ) -> None:
        '''(experimental) Validates and saves the cloud assembly manifest to file.

        :param manifest: - manifest.
        :param file_path: - output file path.

        :stability: experimental
        '''
        return typing.cast(None, jsii.sinvoke(cls, "saveAssemblyManifest", [manifest, file_path]))

    @jsii.member(jsii_name="saveAssetManifest") # type: ignore[misc]
    @builtins.classmethod
    def save_asset_manifest(
        cls,
        manifest: AssetManifest,
        file_path: builtins.str,
    ) -> None:
        '''(experimental) Validates and saves the asset manifest to file.

        :param manifest: - manifest.
        :param file_path: - output file path.

        :stability: experimental
        '''
        return typing.cast(None, jsii.sinvoke(cls, "saveAssetManifest", [manifest, file_path]))

    @jsii.member(jsii_name="version") # type: ignore[misc]
    @builtins.classmethod
    def version(cls) -> builtins.str:
        '''(experimental) Fetch the current schema version number.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sinvoke(cls, "version", []))


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.MetadataEntry",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "data": "data", "trace": "trace"},
)
class MetadataEntry:
    def __init__(
        self,
        *,
        type: builtins.str,
        data: typing.Optional[typing.Union[builtins.str, FileAssetMetadataEntry, ContainerImageAssetMetadataEntry, typing.Sequence["Tag"]]] = None,
        trace: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) A metadata entry in a cloud assembly artifact.

        :param type: (experimental) The type of the metadata entry.
        :param data: (experimental) The data. Default: - no data.
        :param trace: (experimental) A stack trace for when the entry was created. Default: - no trace.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            metadata_entry = cloud_assembly_schema.MetadataEntry(
                type="type",
            
                # the properties below are optional
                data="data",
                trace=["trace"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if data is not None:
            self._values["data"] = data
        if trace is not None:
            self._values["trace"] = trace

    @builtins.property
    def type(self) -> builtins.str:
        '''(experimental) The type of the metadata entry.

        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data(
        self,
    ) -> typing.Optional[typing.Union[builtins.str, FileAssetMetadataEntry, ContainerImageAssetMetadataEntry, typing.List["Tag"]]]:
        '''(experimental) The data.

        :default: - no data.

        :stability: experimental
        '''
        result = self._values.get("data")
        return typing.cast(typing.Optional[typing.Union[builtins.str, FileAssetMetadataEntry, ContainerImageAssetMetadataEntry, typing.List["Tag"]]], result)

    @builtins.property
    def trace(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A stack trace for when the entry was created.

        :default: - no trace.

        :stability: experimental
        '''
        result = self._values.get("trace")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MetadataEntry(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.MissingContext",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "props": "props", "provider": "provider"},
)
class MissingContext:
    def __init__(
        self,
        *,
        key: builtins.str,
        props: typing.Union[AmiContextQuery, AvailabilityZonesContextQuery, HostedZoneContextQuery, "SSMParameterContextQuery", "VpcContextQuery", EndpointServiceAvailabilityZonesContextQuery, "LoadBalancerContextQuery", LoadBalancerListenerContextQuery, "SecurityGroupContextQuery", KeyContextQuery],
        provider: ContextProvider,
    ) -> None:
        '''(experimental) Represents a missing piece of context.

        :param key: (experimental) The missing context key.
        :param props: (experimental) A set of provider-specific options.
        :param provider: (experimental) The provider from which we expect this context key to be obtained.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            missing_context = cloud_assembly_schema.MissingContext(
                key="key",
                props=cloud_assembly_schema.AmiContextQuery(
                    account="account",
                    filters={
                        "filters_key": ["filters"]
                    },
                    region="region",
            
                    # the properties below are optional
                    lookup_role_arn="lookupRoleArn",
                    owners=["owners"]
                ),
                provider=cloud_assembly_schema.ContextProvider.AMI_PROVIDER
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "props": props,
            "provider": provider,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''(experimental) The missing context key.

        :stability: experimental
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def props(
        self,
    ) -> typing.Union[AmiContextQuery, AvailabilityZonesContextQuery, HostedZoneContextQuery, "SSMParameterContextQuery", "VpcContextQuery", EndpointServiceAvailabilityZonesContextQuery, "LoadBalancerContextQuery", LoadBalancerListenerContextQuery, "SecurityGroupContextQuery", KeyContextQuery]:
        '''(experimental) A set of provider-specific options.

        :stability: experimental
        '''
        result = self._values.get("props")
        assert result is not None, "Required property 'props' is missing"
        return typing.cast(typing.Union[AmiContextQuery, AvailabilityZonesContextQuery, HostedZoneContextQuery, "SSMParameterContextQuery", "VpcContextQuery", EndpointServiceAvailabilityZonesContextQuery, "LoadBalancerContextQuery", LoadBalancerListenerContextQuery, "SecurityGroupContextQuery", KeyContextQuery], result)

    @builtins.property
    def provider(self) -> ContextProvider:
        '''(experimental) The provider from which we expect this context key to be obtained.

        :stability: experimental
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(ContextProvider, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MissingContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.NestedCloudAssemblyProperties",
    jsii_struct_bases=[],
    name_mapping={"directory_name": "directoryName", "display_name": "displayName"},
)
class NestedCloudAssemblyProperties:
    def __init__(
        self,
        *,
        directory_name: builtins.str,
        display_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Artifact properties for nested cloud assemblies.

        :param directory_name: (experimental) Relative path to the nested cloud assembly.
        :param display_name: (experimental) Display name for the cloud assembly. Default: - The artifact ID

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            nested_cloud_assembly_properties = cloud_assembly_schema.NestedCloudAssemblyProperties(
                directory_name="directoryName",
            
                # the properties below are optional
                display_name="displayName"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "directory_name": directory_name,
        }
        if display_name is not None:
            self._values["display_name"] = display_name

    @builtins.property
    def directory_name(self) -> builtins.str:
        '''(experimental) Relative path to the nested cloud assembly.

        :stability: experimental
        '''
        result = self._values.get("directory_name")
        assert result is not None, "Required property 'directory_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def display_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Display name for the cloud assembly.

        :default: - The artifact ID

        :stability: experimental
        '''
        result = self._values.get("display_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NestedCloudAssemblyProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.RuntimeInfo",
    jsii_struct_bases=[],
    name_mapping={"libraries": "libraries"},
)
class RuntimeInfo:
    def __init__(
        self,
        *,
        libraries: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        '''(experimental) Information about the application's runtime components.

        :param libraries: (experimental) The list of libraries loaded in the application, associated with their versions.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            runtime_info = cloud_assembly_schema.RuntimeInfo(
                libraries={
                    "libraries_key": "libraries"
                }
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "libraries": libraries,
        }

    @builtins.property
    def libraries(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) The list of libraries loaded in the application, associated with their versions.

        :stability: experimental
        '''
        result = self._values.get("libraries")
        assert result is not None, "Required property 'libraries' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuntimeInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.SSMParameterContextQuery",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "parameter_name": "parameterName",
        "region": "region",
        "lookup_role_arn": "lookupRoleArn",
    },
)
class SSMParameterContextQuery:
    def __init__(
        self,
        *,
        account: builtins.str,
        parameter_name: builtins.str,
        region: builtins.str,
        lookup_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Query to SSM Parameter Context Provider.

        :param account: (experimental) Query account.
        :param parameter_name: (experimental) Parameter name to query.
        :param region: (experimental) Query region.
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            s_sMParameter_context_query = cloud_assembly_schema.SSMParameterContextQuery(
                account="account",
                parameter_name="parameterName",
                region="region",
            
                # the properties below are optional
                lookup_role_arn="lookupRoleArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "parameter_name": parameter_name,
            "region": region,
        }
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Query account.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''(experimental) Parameter name to query.

        :stability: experimental
        '''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Query region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SSMParameterContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.SecurityGroupContextQuery",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "region": "region",
        "lookup_role_arn": "lookupRoleArn",
        "security_group_id": "securityGroupId",
        "security_group_name": "securityGroupName",
        "vpc_id": "vpcId",
    },
)
class SecurityGroupContextQuery:
    def __init__(
        self,
        *,
        account: builtins.str,
        region: builtins.str,
        lookup_role_arn: typing.Optional[builtins.str] = None,
        security_group_id: typing.Optional[builtins.str] = None,
        security_group_name: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Query input for looking up a security group.

        :param account: (experimental) Query account.
        :param region: (experimental) Query region.
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None
        :param security_group_id: (experimental) Security group id. Default: - None
        :param security_group_name: (experimental) Security group name. Default: - None
        :param vpc_id: (experimental) VPC ID. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            security_group_context_query = cloud_assembly_schema.SecurityGroupContextQuery(
                account="account",
                region="region",
            
                # the properties below are optional
                lookup_role_arn="lookupRoleArn",
                security_group_id="securityGroupId",
                security_group_name="securityGroupName",
                vpc_id="vpcId"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "region": region,
        }
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn
        if security_group_id is not None:
            self._values["security_group_id"] = security_group_id
        if security_group_name is not None:
            self._values["security_group_name"] = security_group_name
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Query account.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Query region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) Security group id.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("security_group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Security group name.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("security_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) VPC ID.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityGroupContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.Tag",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class Tag:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''(experimental) Metadata Entry spec for stack tag.

        :param key: (experimental) Tag key. (In the actual file on disk this will be cased as "Key", and the structure is patched to match this structure upon loading: https://github.com/aws/aws-cdk/blob/4aadaa779b48f35838cccd4e25107b2338f05547/packages/%40aws-cdk/cloud-assembly-schema/lib/manifest.ts#L137)
        :param value: (experimental) Tag value. (In the actual file on disk this will be cased as "Value", and the structure is patched to match this structure upon loading: https://github.com/aws/aws-cdk/blob/4aadaa779b48f35838cccd4e25107b2338f05547/packages/%40aws-cdk/cloud-assembly-schema/lib/manifest.ts#L137)

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            tag = cloud_assembly_schema.Tag(
                key="key",
                value="value"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''(experimental) Tag key.

        (In the actual file on disk this will be cased as "Key", and the structure is
        patched to match this structure upon loading:
        https://github.com/aws/aws-cdk/blob/4aadaa779b48f35838cccd4e25107b2338f05547/packages/%40aws-cdk/cloud-assembly-schema/lib/manifest.ts#L137)

        :stability: experimental
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''(experimental) Tag value.

        (In the actual file on disk this will be cased as "Value", and the structure is
        patched to match this structure upon loading:
        https://github.com/aws/aws-cdk/blob/4aadaa779b48f35838cccd4e25107b2338f05547/packages/%40aws-cdk/cloud-assembly-schema/lib/manifest.ts#L137)

        :stability: experimental
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Tag(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.TreeArtifactProperties",
    jsii_struct_bases=[],
    name_mapping={"file": "file"},
)
class TreeArtifactProperties:
    def __init__(self, *, file: builtins.str) -> None:
        '''(experimental) Artifact properties for the Construct Tree Artifact.

        :param file: (experimental) Filename of the tree artifact.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            tree_artifact_properties = cloud_assembly_schema.TreeArtifactProperties(
                file="file"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "file": file,
        }

    @builtins.property
    def file(self) -> builtins.str:
        '''(experimental) Filename of the tree artifact.

        :stability: experimental
        '''
        result = self._values.get("file")
        assert result is not None, "Required property 'file' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TreeArtifactProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.VpcContextQuery",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "filter": "filter",
        "region": "region",
        "lookup_role_arn": "lookupRoleArn",
        "return_asymmetric_subnets": "returnAsymmetricSubnets",
        "subnet_group_name_tag": "subnetGroupNameTag",
    },
)
class VpcContextQuery:
    def __init__(
        self,
        *,
        account: builtins.str,
        filter: typing.Mapping[builtins.str, builtins.str],
        region: builtins.str,
        lookup_role_arn: typing.Optional[builtins.str] = None,
        return_asymmetric_subnets: typing.Optional[builtins.bool] = None,
        subnet_group_name_tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Query input for looking up a VPC.

        :param account: (experimental) Query account.
        :param filter: (experimental) Filters to apply to the VPC. Filter parameters are the same as passed to DescribeVpcs.
        :param region: (experimental) Query region.
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None
        :param return_asymmetric_subnets: (experimental) Whether to populate the subnetGroups field of the {@link VpcContextResponse}, which contains potentially asymmetric subnet groups. Default: false
        :param subnet_group_name_tag: (experimental) Optional tag for subnet group name. If not provided, we'll look at the aws-cdk:subnet-name tag. If the subnet does not have the specified tag, we'll use its type as the name. Default: 'aws-cdk:subnet-name'

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            vpc_context_query = cloud_assembly_schema.VpcContextQuery(
                account="account",
                filter={
                    "filter_key": "filter"
                },
                region="region",
            
                # the properties below are optional
                lookup_role_arn="lookupRoleArn",
                return_asymmetric_subnets=False,
                subnet_group_name_tag="subnetGroupNameTag"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "filter": filter,
            "region": region,
        }
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn
        if return_asymmetric_subnets is not None:
            self._values["return_asymmetric_subnets"] = return_asymmetric_subnets
        if subnet_group_name_tag is not None:
            self._values["subnet_group_name_tag"] = subnet_group_name_tag

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Query account.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) Filters to apply to the VPC.

        Filter parameters are the same as passed to DescribeVpcs.

        :see: https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeVpcs.html
        :stability: experimental
        '''
        result = self._values.get("filter")
        assert result is not None, "Required property 'filter' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Query region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def return_asymmetric_subnets(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to populate the subnetGroups field of the {@link VpcContextResponse}, which contains potentially asymmetric subnet groups.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("return_asymmetric_subnets")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def subnet_group_name_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional tag for subnet group name.

        If not provided, we'll look at the aws-cdk:subnet-name tag.
        If the subnet does not have the specified tag,
        we'll use its type as the name.

        :default: 'aws-cdk:subnet-name'

        :stability: experimental
        '''
        result = self._values.get("subnet_group_name_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.cloud_assembly_schema.LoadBalancerContextQuery",
    jsii_struct_bases=[LoadBalancerFilter],
    name_mapping={
        "load_balancer_type": "loadBalancerType",
        "load_balancer_arn": "loadBalancerArn",
        "load_balancer_tags": "loadBalancerTags",
        "account": "account",
        "region": "region",
        "lookup_role_arn": "lookupRoleArn",
    },
)
class LoadBalancerContextQuery(LoadBalancerFilter):
    def __init__(
        self,
        *,
        load_balancer_type: LoadBalancerType,
        load_balancer_arn: typing.Optional[builtins.str] = None,
        load_balancer_tags: typing.Optional[typing.Sequence[Tag]] = None,
        account: builtins.str,
        region: builtins.str,
        lookup_role_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Query input for looking up a load balancer.

        :param load_balancer_type: (experimental) Filter load balancers by their type.
        :param load_balancer_arn: (experimental) Find by load balancer's ARN. Default: - does not search by load balancer arn
        :param load_balancer_tags: (experimental) Match load balancer tags. Default: - does not match load balancers by tags
        :param account: (experimental) Query account.
        :param region: (experimental) Query region.
        :param lookup_role_arn: (experimental) The ARN of the role that should be used to look up the missing values. Default: - None

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import cloud_assembly_schema
            
            load_balancer_context_query = cloud_assembly_schema.LoadBalancerContextQuery(
                account="account",
                load_balancer_type=cloud_assembly_schema.LoadBalancerType.NETWORK,
                region="region",
            
                # the properties below are optional
                load_balancer_arn="loadBalancerArn",
                load_balancer_tags=[cloud_assembly_schema.Tag(
                    key="key",
                    value="value"
                )],
                lookup_role_arn="lookupRoleArn"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "load_balancer_type": load_balancer_type,
            "account": account,
            "region": region,
        }
        if load_balancer_arn is not None:
            self._values["load_balancer_arn"] = load_balancer_arn
        if load_balancer_tags is not None:
            self._values["load_balancer_tags"] = load_balancer_tags
        if lookup_role_arn is not None:
            self._values["lookup_role_arn"] = lookup_role_arn

    @builtins.property
    def load_balancer_type(self) -> LoadBalancerType:
        '''(experimental) Filter load balancers by their type.

        :stability: experimental
        '''
        result = self._values.get("load_balancer_type")
        assert result is not None, "Required property 'load_balancer_type' is missing"
        return typing.cast(LoadBalancerType, result)

    @builtins.property
    def load_balancer_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) Find by load balancer's ARN.

        :default: - does not search by load balancer arn

        :stability: experimental
        '''
        result = self._values.get("load_balancer_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def load_balancer_tags(self) -> typing.Optional[typing.List[Tag]]:
        '''(experimental) Match load balancer tags.

        :default: - does not match load balancers by tags

        :stability: experimental
        '''
        result = self._values.get("load_balancer_tags")
        return typing.cast(typing.Optional[typing.List[Tag]], result)

    @builtins.property
    def account(self) -> builtins.str:
        '''(experimental) Query account.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''(experimental) Query region.

        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lookup_role_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the role that should be used to look up the missing values.

        :default: - None

        :stability: experimental
        '''
        result = self._values.get("lookup_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerContextQuery(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AmiContextQuery",
    "ArtifactManifest",
    "ArtifactMetadataEntryType",
    "ArtifactType",
    "AssemblyManifest",
    "AssetManifest",
    "AssetManifestProperties",
    "AvailabilityZonesContextQuery",
    "AwsCloudFormationStackProperties",
    "AwsDestination",
    "BootstrapRole",
    "ContainerImageAssetMetadataEntry",
    "ContextProvider",
    "DockerImageAsset",
    "DockerImageDestination",
    "DockerImageSource",
    "EndpointServiceAvailabilityZonesContextQuery",
    "FileAsset",
    "FileAssetMetadataEntry",
    "FileAssetPackaging",
    "FileDestination",
    "FileSource",
    "HostedZoneContextQuery",
    "KeyContextQuery",
    "LoadBalancerContextQuery",
    "LoadBalancerFilter",
    "LoadBalancerListenerContextQuery",
    "LoadBalancerListenerProtocol",
    "LoadBalancerType",
    "Manifest",
    "MetadataEntry",
    "MissingContext",
    "NestedCloudAssemblyProperties",
    "RuntimeInfo",
    "SSMParameterContextQuery",
    "SecurityGroupContextQuery",
    "Tag",
    "TreeArtifactProperties",
    "VpcContextQuery",
]

publication.publish()
