'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-serverless-cluster-from-snapshot?style=flat-square)](https://github.com/pepperize/cdk-serverless-cluster-from-snapshot/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-serverless-cluster-from-snapshot?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-serverless-cluster-from-snapshot)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-serverless-cluster-from-snapshot?style=flat-square)](https://pypi.org/project/pepperize.cdk-serverless-cluster-from-snapshot/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.ServerlessClusterFromSnapshot?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.ServerlessClusterFromSnapshot/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-serverless-cluster-from-snapshot/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-serverless-cluster-from-snapshot/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-serverless-cluster-from-snapshot?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-serverless-cluster-from-snapshot/releases)

# AWS RDS Aurora serverless cluster from snapshot

This project provides a CDK construct creating a serverless database cluster from a snapshot with AWS RDS Aurora engine.

See [API.md](https://github.com/pepperize/cdk-serverless-cluster-from-snapshot/blob/main/API.md)

## Install

### TypeScript

```shell
npm install @pepperize/cdk-serverless-cluster-from-snapshot
```

or

```shell
yarn add @pepperize/cdk-serverless-cluster-from-snapshot
```

### Python

```shell
pip install pepperize.cdk-serverless-cluster-from-snapshot
```

### C# / .Net

```
dotnet add package Pepperize.CDK.ServerlessClusterFromSnapshot
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

import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_rds
import aws_cdk.aws_secretsmanager
import aws_cdk.core


@jsii.implements(aws_cdk.aws_rds.IServerlessCluster)
class ServerlessClusterFromSnapshot(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-serverless-cluster-from-snapshot.ServerlessClusterFromSnapshot",
):
    '''A Serverless Cluster restored from a snapshot.

    :resource: AWS::RDS::DBInstance
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        engine: aws_cdk.aws_rds.IClusterEngine,
        snapshot_identifier: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[aws_cdk.aws_rds.Credentials] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        enable_data_api: typing.Optional[builtins.bool] = None,
        parameter_group: typing.Optional[aws_cdk.aws_rds.IParameterGroup] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        scaling: typing.Optional[aws_cdk.aws_rds.ServerlessScalingOptions] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        storage_encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        subnet_group: typing.Optional[aws_cdk.aws_rds.ISubnetGroup] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param engine: What kind of database to start.
        :param snapshot_identifier: The identifier for the DB snapshot or DB cluster snapshot to restore from. You can use either the name or the Amazon Resource Name (ARN) to specify a DB cluster snapshot. However, you can use only the ARN to specify a DB snapshot. After you restore a DB cluster with a SnapshotIdentifier property, you must specify the same SnapshotIdentifier property for any future updates to the DB cluster. When you specify this property for an update, the DB cluster is not restored from the snapshot again, and the data in the database is not changed. However, if you don't specify the SnapshotIdentifier property, an empty DB cluster is created, and the original DB cluster is deleted. If you specify a property that is different from the previous snapshot restore property, a new DB cluster is restored from the specified SnapshotIdentifier property, and the original DB cluster is deleted.
        :param vpc: The VPC that this Aurora Serverless cluster has been created in.
        :param backup_retention: The number of days during which automatic DB snapshots are retained. Automatic backup retention cannot be disabled on serverless clusters. Must be a value from 1 day to 35 days. Default: Duration.days(1)
        :param cluster_identifier: An optional identifier for the cluster. Default: - A name is automatically generated.
        :param credentials: Credentials for the administrative user. Default: - A username of 'admin' and SecretsManager-generated password
        :param default_database_name: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
        :param deletion_protection: Indicates whether the DB cluster should have deletion protection enabled. Default: - true if removalPolicy is RETAIN, false otherwise
        :param enable_data_api: Whether to enable the Data API. Default: false
        :param parameter_group: Additional parameters to pass to the database engine. Default: - no parameter group.
        :param removal_policy: The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        :param scaling: Scaling configuration of an Aurora Serverless database cluster. Default: - Serverless cluster is automatically paused after 5 minutes of being idle. minimum capacity: 2 ACU maximum capacity: 16 ACU
        :param security_groups: Security group. Default: - a new security group is created.
        :param storage_encryption_key: The KMS key for storage encryption. If you specify the SnapshotIdentifier property, the StorageEncrypted property value is inherited from the snapshot, and if the DB cluster is encrypted, the specified KmsKeyId property is used. Default: - the default master key will be used for storage encryption
        :param subnet_group: Existing subnet group for the cluster. Default: - a new subnet group will be created.
        :param vpc_subnets: Where to place the instances within the VPC. Default: - the VPC default strategy if not specified.
        '''
        props = ServerlessClusterFromSnapshotProps(
            engine=engine,
            snapshot_identifier=snapshot_identifier,
            vpc=vpc,
            backup_retention=backup_retention,
            cluster_identifier=cluster_identifier,
            credentials=credentials,
            default_database_name=default_database_name,
            deletion_protection=deletion_protection,
            enable_data_api=enable_data_api,
            parameter_group=parameter_group,
            removal_policy=removal_policy,
            scaling=scaling,
            security_groups=security_groups,
            storage_encryption_key=storage_encryption_key,
            subnet_group=subnet_group,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addRotationMultiUser")
    def add_rotation_multi_user(
        self,
        id: builtins.str,
        *,
        secret: aws_cdk.aws_secretsmanager.ISecret,
        automatically_after: typing.Optional[aws_cdk.core.Duration] = None,
        endpoint: typing.Optional[aws_cdk.aws_ec2.IInterfaceVpcEndpoint] = None,
        exclude_characters: typing.Optional[builtins.str] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> aws_cdk.aws_secretsmanager.SecretRotation:
        '''Adds the multi user rotation to this cluster.

        :param id: -
        :param secret: The secret to rotate. It must be a JSON string with the following format:: { "engine": <required: database engine>, "host": <required: instance host name>, "username": <required: username>, "password": <required: password>, "dbname": <optional: database name>, "port": <optional: if not specified, default port will be used>, "masterarn": <required: the arn of the master secret which will be used to create users/change passwords> }
        :param automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: - 30 days
        :param endpoint: The VPC interface endpoint to use for the Secrets Manager API. If you enable private DNS hostnames for your VPC private endpoint (the default), you don't need to specify an endpoint. The standard Secrets Manager DNS hostname the Secrets Manager CLI and SDKs use by default (https://secretsmanager..amazonaws.com) automatically resolves to your VPC endpoint. Default: https://secretsmanager..amazonaws.com
        :param exclude_characters: Specifies characters to not include in generated passwords. Default: " %+~`#$&*()|[]{}:;<>?!'/
        :param vpc_subnets: Where to place the rotation Lambda function. Default: - same placement as instance or cluster
        '''
        options = aws_cdk.aws_rds.RotationMultiUserOptions(
            secret=secret,
            automatically_after=automatically_after,
            endpoint=endpoint,
            exclude_characters=exclude_characters,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast(aws_cdk.aws_secretsmanager.SecretRotation, jsii.invoke(self, "addRotationMultiUser", [id, options]))

    @jsii.member(jsii_name="addRotationSingleUser")
    def add_rotation_single_user(
        self,
        *,
        automatically_after: typing.Optional[aws_cdk.core.Duration] = None,
        endpoint: typing.Optional[aws_cdk.aws_ec2.IInterfaceVpcEndpoint] = None,
        exclude_characters: typing.Optional[builtins.str] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> aws_cdk.aws_secretsmanager.SecretRotation:
        '''Adds the single user rotation of the master password to this cluster.

        :param automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: - 30 days
        :param endpoint: The VPC interface endpoint to use for the Secrets Manager API. If you enable private DNS hostnames for your VPC private endpoint (the default), you don't need to specify an endpoint. The standard Secrets Manager DNS hostname the Secrets Manager CLI and SDKs use by default (https://secretsmanager..amazonaws.com) automatically resolves to your VPC endpoint. Default: https://secretsmanager..amazonaws.com
        :param exclude_characters: Specifies characters to not include in generated passwords. Default: " %+~`#$&*()|[]{}:;<>?!'/
        :param vpc_subnets: Where to place the rotation Lambda function. Default: - same placement as instance or cluster
        '''
        options = aws_cdk.aws_rds.RotationSingleUserOptions(
            automatically_after=automatically_after,
            endpoint=endpoint,
            exclude_characters=exclude_characters,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast(aws_cdk.aws_secretsmanager.SecretRotation, jsii.invoke(self, "addRotationSingleUser", [options]))

    @jsii.member(jsii_name="asSecretAttachmentTarget")
    def as_secret_attachment_target(
        self,
    ) -> aws_cdk.aws_secretsmanager.SecretAttachmentTargetProps:
        '''Renders the secret attachment target specifications.'''
        return typing.cast(aws_cdk.aws_secretsmanager.SecretAttachmentTargetProps, jsii.invoke(self, "asSecretAttachmentTarget", []))

    @jsii.member(jsii_name="grantDataApiAccess")
    def grant_data_api_access(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
    ) -> aws_cdk.aws_iam.Grant:
        '''Grant the given identity to access to the Data API, including read access to the secret attached to the cluster if present.

        :param grantee: The principal to grant access to.
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantDataApiAccess", [grantee]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterArn")
    def cluster_arn(self) -> builtins.str:
        '''The ARN of the cluster.'''
        return typing.cast(builtins.str, jsii.get(self, "clusterArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self) -> aws_cdk.aws_rds.Endpoint:
        '''The endpoint to use for read/write operations.'''
        return typing.cast(aws_cdk.aws_rds.Endpoint, jsii.get(self, "clusterEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterIdentifier")
    def cluster_identifier(self) -> builtins.str:
        '''Identifier of the cluster.'''
        return typing.cast(builtins.str, jsii.get(self, "clusterIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterReadEndpoint")
    def cluster_read_endpoint(self) -> aws_cdk.aws_rds.Endpoint:
        '''The endpoint to use for read/write operations.'''
        return typing.cast(aws_cdk.aws_rds.Endpoint, jsii.get(self, "clusterReadEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''Access to the network connections.'''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        '''The secret attached to this cluster.'''
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.ISecret], jsii.get(self, "secret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableDataApi")
    def _enable_data_api(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enableDataApi"))

    @_enable_data_api.setter
    def _enable_data_api(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "enableDataApi", value)


@jsii.data_type(
    jsii_type="@pepperize/cdk-serverless-cluster-from-snapshot.ServerlessClusterFromSnapshotProps",
    jsii_struct_bases=[],
    name_mapping={
        "engine": "engine",
        "snapshot_identifier": "snapshotIdentifier",
        "vpc": "vpc",
        "backup_retention": "backupRetention",
        "cluster_identifier": "clusterIdentifier",
        "credentials": "credentials",
        "default_database_name": "defaultDatabaseName",
        "deletion_protection": "deletionProtection",
        "enable_data_api": "enableDataApi",
        "parameter_group": "parameterGroup",
        "removal_policy": "removalPolicy",
        "scaling": "scaling",
        "security_groups": "securityGroups",
        "storage_encryption_key": "storageEncryptionKey",
        "subnet_group": "subnetGroup",
        "vpc_subnets": "vpcSubnets",
    },
)
class ServerlessClusterFromSnapshotProps:
    def __init__(
        self,
        *,
        engine: aws_cdk.aws_rds.IClusterEngine,
        snapshot_identifier: builtins.str,
        vpc: aws_cdk.aws_ec2.IVpc,
        backup_retention: typing.Optional[aws_cdk.core.Duration] = None,
        cluster_identifier: typing.Optional[builtins.str] = None,
        credentials: typing.Optional[aws_cdk.aws_rds.Credentials] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        enable_data_api: typing.Optional[builtins.bool] = None,
        parameter_group: typing.Optional[aws_cdk.aws_rds.IParameterGroup] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        scaling: typing.Optional[aws_cdk.aws_rds.ServerlessScalingOptions] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        storage_encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        subnet_group: typing.Optional[aws_cdk.aws_rds.ISubnetGroup] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''Properties to configure an Aurora Serverless Cluster.

        :param engine: What kind of database to start.
        :param snapshot_identifier: The identifier for the DB snapshot or DB cluster snapshot to restore from. You can use either the name or the Amazon Resource Name (ARN) to specify a DB cluster snapshot. However, you can use only the ARN to specify a DB snapshot. After you restore a DB cluster with a SnapshotIdentifier property, you must specify the same SnapshotIdentifier property for any future updates to the DB cluster. When you specify this property for an update, the DB cluster is not restored from the snapshot again, and the data in the database is not changed. However, if you don't specify the SnapshotIdentifier property, an empty DB cluster is created, and the original DB cluster is deleted. If you specify a property that is different from the previous snapshot restore property, a new DB cluster is restored from the specified SnapshotIdentifier property, and the original DB cluster is deleted.
        :param vpc: The VPC that this Aurora Serverless cluster has been created in.
        :param backup_retention: The number of days during which automatic DB snapshots are retained. Automatic backup retention cannot be disabled on serverless clusters. Must be a value from 1 day to 35 days. Default: Duration.days(1)
        :param cluster_identifier: An optional identifier for the cluster. Default: - A name is automatically generated.
        :param credentials: Credentials for the administrative user. Default: - A username of 'admin' and SecretsManager-generated password
        :param default_database_name: Name of a database which is automatically created inside the cluster. Default: - Database is not created in cluster.
        :param deletion_protection: Indicates whether the DB cluster should have deletion protection enabled. Default: - true if removalPolicy is RETAIN, false otherwise
        :param enable_data_api: Whether to enable the Data API. Default: false
        :param parameter_group: Additional parameters to pass to the database engine. Default: - no parameter group.
        :param removal_policy: The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update. Default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        :param scaling: Scaling configuration of an Aurora Serverless database cluster. Default: - Serverless cluster is automatically paused after 5 minutes of being idle. minimum capacity: 2 ACU maximum capacity: 16 ACU
        :param security_groups: Security group. Default: - a new security group is created.
        :param storage_encryption_key: The KMS key for storage encryption. If you specify the SnapshotIdentifier property, the StorageEncrypted property value is inherited from the snapshot, and if the DB cluster is encrypted, the specified KmsKeyId property is used. Default: - the default master key will be used for storage encryption
        :param subnet_group: Existing subnet group for the cluster. Default: - a new subnet group will be created.
        :param vpc_subnets: Where to place the instances within the VPC. Default: - the VPC default strategy if not specified.
        '''
        if isinstance(scaling, dict):
            scaling = aws_cdk.aws_rds.ServerlessScalingOptions(**scaling)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {
            "engine": engine,
            "snapshot_identifier": snapshot_identifier,
            "vpc": vpc,
        }
        if backup_retention is not None:
            self._values["backup_retention"] = backup_retention
        if cluster_identifier is not None:
            self._values["cluster_identifier"] = cluster_identifier
        if credentials is not None:
            self._values["credentials"] = credentials
        if default_database_name is not None:
            self._values["default_database_name"] = default_database_name
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if enable_data_api is not None:
            self._values["enable_data_api"] = enable_data_api
        if parameter_group is not None:
            self._values["parameter_group"] = parameter_group
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if scaling is not None:
            self._values["scaling"] = scaling
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if storage_encryption_key is not None:
            self._values["storage_encryption_key"] = storage_encryption_key
        if subnet_group is not None:
            self._values["subnet_group"] = subnet_group
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def engine(self) -> aws_cdk.aws_rds.IClusterEngine:
        '''What kind of database to start.'''
        result = self._values.get("engine")
        assert result is not None, "Required property 'engine' is missing"
        return typing.cast(aws_cdk.aws_rds.IClusterEngine, result)

    @builtins.property
    def snapshot_identifier(self) -> builtins.str:
        '''The identifier for the DB snapshot or DB cluster snapshot to restore from.

        You can use either the name or the Amazon Resource Name (ARN) to specify a DB cluster snapshot. However, you can use only the ARN to specify a DB snapshot.

        After you restore a DB cluster with a SnapshotIdentifier property, you must specify the same SnapshotIdentifier property for any future updates to the DB cluster. When you specify this property for an update, the DB cluster is not restored from the snapshot again, and the data in the database is not changed. However, if you don't specify the SnapshotIdentifier property, an empty DB cluster is created, and the original DB cluster is deleted. If you specify a property that is different from the previous snapshot restore property, a new DB cluster is restored from the specified SnapshotIdentifier property, and the original DB cluster is deleted.
        '''
        result = self._values.get("snapshot_identifier")
        assert result is not None, "Required property 'snapshot_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC that this Aurora Serverless cluster has been created in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def backup_retention(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The number of days during which automatic DB snapshots are retained.

        Automatic backup retention cannot be disabled on serverless clusters.
        Must be a value from 1 day to 35 days.

        :default: Duration.days(1)
        '''
        result = self._values.get("backup_retention")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    @builtins.property
    def cluster_identifier(self) -> typing.Optional[builtins.str]:
        '''An optional identifier for the cluster.

        :default: - A name is automatically generated.
        '''
        result = self._values.get("cluster_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def credentials(self) -> typing.Optional[aws_cdk.aws_rds.Credentials]:
        '''Credentials for the administrative user.

        :default: - A username of 'admin' and SecretsManager-generated password
        '''
        result = self._values.get("credentials")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.Credentials], result)

    @builtins.property
    def default_database_name(self) -> typing.Optional[builtins.str]:
        '''Name of a database which is automatically created inside the cluster.

        :default: - Database is not created in cluster.
        '''
        result = self._values.get("default_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deletion_protection(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the DB cluster should have deletion protection enabled.

        :default: - true if removalPolicy is RETAIN, false otherwise
        '''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_data_api(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable the Data API.

        :default: false

        :see: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html
        '''
        result = self._values.get("enable_data_api")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def parameter_group(self) -> typing.Optional[aws_cdk.aws_rds.IParameterGroup]:
        '''Additional parameters to pass to the database engine.

        :default: - no parameter group.
        '''
        result = self._values.get("parameter_group")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IParameterGroup], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''The removal policy to apply when the cluster and its instances are removed from the stack or replaced during an update.

        :default: - RemovalPolicy.SNAPSHOT (remove the cluster and instances, but retain a snapshot of the data)
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def scaling(self) -> typing.Optional[aws_cdk.aws_rds.ServerlessScalingOptions]:
        '''Scaling configuration of an Aurora Serverless database cluster.

        :default:

        - Serverless cluster is automatically paused after 5 minutes of being idle.
        minimum capacity: 2 ACU
        maximum capacity: 16 ACU
        '''
        result = self._values.get("scaling")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.ServerlessScalingOptions], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        '''Security group.

        :default: - a new security group is created.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def storage_encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''The KMS key for storage encryption.

        If you specify the SnapshotIdentifier property, the StorageEncrypted property value is inherited from the snapshot, and if the DB cluster is encrypted, the specified KmsKeyId property is used.

        :default: - the default master key will be used for storage encryption
        '''
        result = self._values.get("storage_encryption_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def subnet_group(self) -> typing.Optional[aws_cdk.aws_rds.ISubnetGroup]:
        '''Existing subnet group for the cluster.

        :default: - a new subnet group will be created.
        '''
        result = self._values.get("subnet_group")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.ISubnetGroup], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''Where to place the instances within the VPC.

        :default: - the VPC default strategy if not specified.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerlessClusterFromSnapshotProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ServerlessClusterFromSnapshot",
    "ServerlessClusterFromSnapshotProps",
]

publication.publish()
