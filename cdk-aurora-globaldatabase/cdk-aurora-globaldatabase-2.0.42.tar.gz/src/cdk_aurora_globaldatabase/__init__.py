'''
[![NPM version](https://badge.fury.io/js/cdk-aurora-globaldatabase.svg)](https://badge.fury.io/js/cdk-aurora-globaldatabase)
[![PyPI version](https://badge.fury.io/py/cdk-aurora-globaldatabase.svg)](https://badge.fury.io/py/cdk-aurora-globaldatabase)
![Release](https://github.com/neilkuan/cdk-aurora-globaldatabase/workflows/release/badge.svg)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/cdk-aurora-globaldatabase?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/cdk-aurora-globaldatabase?label=pypi&color=blue)

# cdk-aurora-globaldatabase

`cdk-aurora-globaldatabase` is an AWS CDK construct library that allows you to create [Amazon Aurora Global Databases](https://aws.amazon.com/rds/aurora/global-database/) with AWS CDK in Typescript or Python.

# Why

**Amazon Aurora Global Databases** is designed for multi-regional Amazon Aurora Database clusters that span across different AWS regions. Due to the lack of native cloudformation support, it has been very challenging to build with cloudformation or AWS CDK with the upstream `aws-rds` construct.

`cdk-aurora-globaldatabase` aims to offload the heavy-lifting and helps you provision and deploy cross-regional **Amazon Aurora Global Databases** simply with just a few CDK statements.

## Install

```bash
Use the npm dist tag to opt in CDKv1 or CDKv2:

// for CDKv2
npm install cdk-aurora-globaldatabase
or
npm install cdk-aurora-globaldatabase@latest

// for CDKv1
npm install cdk-aurora-globaldatabase@cdkv1
```

💡💡💡 please click [here](https://github.com/neilkuan/cdk-aurora-globaldatabase/tree/cdkv1#readme), if you are using aws-cdk v1.x.x version.💡💡💡

## Now Try It !!!

# Sample for Mysql

```python
import { GolbalAuroraRDSMaster, InstanceTypeEnum, GolbalAuroraRDSSlaveInfra } from 'cdk-aurora-globaldatabase';
import { App, Stack, CfnOutput } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
// new app .
const mockApp = new App();

// setting two region env config .
const envSingapro  = { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'ap-southeast-1' };
const envTokyo = { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'ap-northeast-1' };

// create stack main .
const stackM = new Stack(mockApp, 'testing-stackM',{env: envTokyo});
const vpcPublic = new ec2.Vpc(stackM,'defaultVpc',{
  natGateways: 0,
  maxAzs: 3,
  subnetConfiguration: [{
    cidrMask: 26,
    name: 'masterVPC2',
    subnetType: ec2.SubnetType.PUBLIC,
  }],
});
const  globaldbM = new GolbalAuroraRDSMaster(stackM, 'golbalAuroraRDSMaster',{
  instanceType: InstanceTypeEnum.R5_LARGE,
  vpc: vpcPublic,
  rdsPassword: '1qaz2wsx',
});
globaldbM.rdsCluster.connections.allowDefaultPortFrom(ec2.Peer.ipv4(`${process.env.MYIP}/32`))

// create stack slave infra or you can give your subnet group.
const stackS = new Stack(mockApp, 'testing-stackS',{env: envSingapro});
const vpcPublic2 = new ec2.Vpc(stackS,'defaultVpc2',{
  natGateways: 0,
  maxAzs: 3,
  subnetConfiguration: [{
    cidrMask: 26,
    name: 'secondVPC2',
    subnetType: ec2.SubnetType.PUBLIC,
  }],
});
const globaldbS = new GolbalAuroraRDSSlaveInfra(stackS, 'slaveregion',{vpc: vpcPublic2,subnetType:ec2.SubnetType.PUBLIC });

// so we need to wait stack slave created first .
stackM.addDependency(stackS)


new CfnOutput(stackM, 'password', { value: globaldbM.rdsPassword });
// add second region cluster
globaldbM.addRegionalCluster(stackM,'addregionalrds',{
  region: 'ap-southeast-1',
  dbSubnetGroupName: globaldbS.dbSubnetGroup.dbSubnetGroupName,
});
```

![like this ](./image/Mysql-cluster.jpg)

# Sample for Postgres

```python
import { GolbalAuroraRDSMaster, InstanceTypeEnum, GolbalAuroraRDSSlaveInfra } from 'cdk-aurora-globaldatabase';
import { App, Stack, CfnOutput } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as _rds from 'aws-cdk-lib/aws-rds';

const mockApp = new App();
const envSingapro  = { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'ap-southeast-1' };
const envTokyo = { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'ap-northeast-1' };

const stackM = new Stack(mockApp, 'testing-stackM',{env: envTokyo});
const vpcPublic = new ec2.Vpc(stackM,'defaultVpc',{
  natGateways: 0,
  maxAzs: 3,
  subnetConfiguration: [{
    cidrMask: 26,
    name: 'masterVPC2',
    subnetType: ec2.SubnetType.PUBLIC,
  }],
});

// Note if you use postgres , need to give the same value in engineVersion and  dbClusterpPG's engine .
const globaldbM = new GolbalAuroraRDSMaster(stackM, 'golbalAuroraRDSMaster',{
  instanceType: InstanceTypeEnum.R5_LARGE,
  vpc: vpcPublic,
  rdsPassword: '1qaz2wsx',
  engineVersion: _rds.DatabaseClusterEngine.auroraPostgres({
    version: _rds.AuroraPostgresEngineVersion.VER_11_7}),
  dbClusterpPG: new _rds.ParameterGroup(stackM, 'dbClusterparametergroup', {
    engine: _rds.DatabaseClusterEngine.auroraPostgres({
      version: _rds.AuroraPostgresEngineVersion.VER_11_7,
    }),
    parameters: {
      'rds.force_ssl': '1',
      'rds.log_retention_period': '10080',
      'auto_explain.log_min_duration': '5000',
      'auto_explain.log_verbose': '1',
      'timezone': 'UTC+8',
      'shared_preload_libraries': 'auto_explain,pg_stat_statements,pg_hint_plan,pgaudit',
      'log_connections': '1',
      'log_statement': 'ddl',
      'log_disconnections': '1',
      'log_lock_waits': '1',
      'log_min_duration_statement': '5000',
      'log_rotation_age': '1440',
      'log_rotation_size': '102400',
      'random_page_cost': '1',
      'track_activity_query_size': '16384',
      'idle_in_transaction_session_timeout': '7200000',
    },
  }),
});
globaldbM.rdsCluster.connections.allowDefaultPortFrom(ec2.Peer.ipv4(`${process.env.MYIP}/32`))

const stackS = new Stack(mockApp, 'testing-stackS',{env: envSingapro});
const vpcPublic2 = new ec2.Vpc(stackS,'defaultVpc2',{
  natGateways: 0,
  maxAzs: 3,
  subnetConfiguration: [{
    cidrMask: 26,
    name: 'secondVPC2',
    subnetType: ec2.SubnetType.PUBLIC,
  }],
});
const globaldbS = new GolbalAuroraRDSSlaveInfra(stackS, 'slaveregion',{
  vpc: vpcPublic2,subnetType:ec2.SubnetType.PUBLIC,
});

stackM.addDependency(stackS)


new CfnOutput(stackM, 'password', { value: globaldbM.rdsPassword });
// add second region cluster
globaldbM.addRegionalCluster(stackM,'addregionalrds',{
  region: 'ap-southeast-1',
  dbSubnetGroupName: globaldbS.dbSubnetGroup.dbSubnetGroupName,
});
```

### To deploy

```bash
cdk deploy
```

### To destroy

```bash
cdk destroy
```

## :clap:  Supporters

[![Stargazers repo roster for @neilkuan/cdk-aurora-globaldatabase](https://reporoster.com/stars/neilkuan/cdk-aurora-globaldatabase)](https://github.com/neilkuan/cdk-aurora-globaldatabase/stargazers)
[![Forkers repo roster for @neilkuan/cdk-aurora-globaldatabase](https://reporoster.com/forks/neilkuan/cdk-aurora-globaldatabase)](https://github.com/neilkuan/cdk-aurora-globaldatabase/network/members)
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
import aws_cdk.aws_ec2
import aws_cdk.aws_rds
import constructs


class GolbalAuroraRDSMaster(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aurora-globaldatabase.GolbalAuroraRDSMaster",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        db_clusterp_pg: typing.Optional[aws_cdk.aws_rds.IParameterGroup] = None,
        db_user_name: typing.Optional[builtins.str] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        engine_version: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        instance_type: typing.Optional["InstanceTypeEnum"] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        rds_password: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        time_zone: typing.Optional["MySQLtimeZone"] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param db_clusterp_pg: (experimental) RDS ParameterGroup. Default: - Aurora MySQL ParameterGroup
        :param db_user_name: (experimental) RDS default Super User Name. Default: - sysadmin
        :param default_database_name: (experimental) RDS default Database Name. Default: - globaldatabase
        :param deletion_protection: (experimental) Global RDS Database Cluster Engine Deletion Protection Option . Default: - false
        :param engine_version: (experimental) RDS Database Cluster Engine . Default: - rds.DatabaseClusterEngine.auroraMysql({version: rds.AuroraMysqlEngineVersion.VER_2_07_1,})
        :param instance_type: (experimental) RDS Instance Type only can use r4 or r5 type see more https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html#aurora-global-database.limitations. Default: - r5.large
        :param parameters: (experimental) RDS Parameters. Default: - {time_zone: 'UTC'}
        :param rds_password: (experimental) return RDS Cluster password.
        :param storage_encrypted: (experimental) Global RDS Database Cluster Engine Storage Encrypted Option . Default: - true
        :param time_zone: (experimental) RDS time zone. Default: - MySQLtimeZone.UTC
        :param vpc: (experimental) RDS default VPC. Default: - new VPC

        :stability: experimental
        '''
        props = GolbalAuroraRDSMasterProps(
            db_clusterp_pg=db_clusterp_pg,
            db_user_name=db_user_name,
            default_database_name=default_database_name,
            deletion_protection=deletion_protection,
            engine_version=engine_version,
            instance_type=instance_type,
            parameters=parameters,
            rds_password=rds_password,
            storage_encrypted=storage_encrypted,
            time_zone=time_zone,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addRegionalCluster")
    def add_regional_cluster(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        region: builtins.str,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param region: 
        :param db_subnet_group_name: 

        :stability: experimental
        '''
        options = RegionalOptions(
            region=region, db_subnet_group_name=db_subnet_group_name
        )

        return typing.cast(None, jsii.invoke(self, "addRegionalCluster", [scope, id, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterEngineVersion")
    def cluster_engine_version(self) -> builtins.str:
        '''(experimental) return RDS Cluster DB Engine Version.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "clusterEngineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbClusterpPG")
    def db_clusterp_pg(self) -> aws_cdk.aws_rds.IParameterGroup:
        '''(experimental) return RDS Cluster ParameterGroup.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_rds.IParameterGroup, jsii.get(self, "dbClusterpPG"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        '''(experimental) return RDS Cluster DB Engine .

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "engine"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> aws_cdk.aws_rds.IClusterEngine:
        '''(experimental) return RDS Cluster DB Engine Version.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_rds.IClusterEngine, jsii.get(self, "engineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalClusterArn")
    def global_cluster_arn(self) -> builtins.str:
        '''(experimental) return Global RDS Cluster Resource ARN .

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "globalClusterArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalClusterIdentifier")
    def global_cluster_identifier(self) -> builtins.str:
        '''(experimental) return Global RDS Cluster Identifier .

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "globalClusterIdentifier"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsCluster")
    def rds_cluster(self) -> aws_cdk.aws_rds.DatabaseCluster:
        '''(experimental) return RDS Cluster.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_rds.DatabaseCluster, jsii.get(self, "rdsCluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsClusterarn")
    def rds_clusterarn(self) -> builtins.str:
        '''(experimental) return RDS Cluster Resource ARN .

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "rdsClusterarn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsInstanceType")
    def rds_instance_type(self) -> "InstanceTypeEnum":
        '''(experimental) return Global RDS Cluster instance Type .

        :stability: experimental
        '''
        return typing.cast("InstanceTypeEnum", jsii.get(self, "rdsInstanceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsIsPublic")
    def rds_is_public(self) -> aws_cdk.aws_ec2.SubnetType:
        '''(experimental) return RDS Cluster is Public ?

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.SubnetType, jsii.get(self, "rdsIsPublic"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rdsPassword")
    def rds_password(self) -> typing.Optional[builtins.str]:
        '''(experimental) return RDS Cluster password.

        if not define props.rdsPassword , password will stored in Secret Manager
        Please use this command get password back , "aws secretsmanager get-secret-value --secret-id secret name"

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdsPassword"))


@jsii.data_type(
    jsii_type="cdk-aurora-globaldatabase.GolbalAuroraRDSMasterProps",
    jsii_struct_bases=[],
    name_mapping={
        "db_clusterp_pg": "dbClusterpPG",
        "db_user_name": "dbUserName",
        "default_database_name": "defaultDatabaseName",
        "deletion_protection": "deletionProtection",
        "engine_version": "engineVersion",
        "instance_type": "instanceType",
        "parameters": "parameters",
        "rds_password": "rdsPassword",
        "storage_encrypted": "storageEncrypted",
        "time_zone": "timeZone",
        "vpc": "vpc",
    },
)
class GolbalAuroraRDSMasterProps:
    def __init__(
        self,
        *,
        db_clusterp_pg: typing.Optional[aws_cdk.aws_rds.IParameterGroup] = None,
        db_user_name: typing.Optional[builtins.str] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        engine_version: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        instance_type: typing.Optional["InstanceTypeEnum"] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        rds_password: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        time_zone: typing.Optional["MySQLtimeZone"] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param db_clusterp_pg: (experimental) RDS ParameterGroup. Default: - Aurora MySQL ParameterGroup
        :param db_user_name: (experimental) RDS default Super User Name. Default: - sysadmin
        :param default_database_name: (experimental) RDS default Database Name. Default: - globaldatabase
        :param deletion_protection: (experimental) Global RDS Database Cluster Engine Deletion Protection Option . Default: - false
        :param engine_version: (experimental) RDS Database Cluster Engine . Default: - rds.DatabaseClusterEngine.auroraMysql({version: rds.AuroraMysqlEngineVersion.VER_2_07_1,})
        :param instance_type: (experimental) RDS Instance Type only can use r4 or r5 type see more https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html#aurora-global-database.limitations. Default: - r5.large
        :param parameters: (experimental) RDS Parameters. Default: - {time_zone: 'UTC'}
        :param rds_password: (experimental) return RDS Cluster password.
        :param storage_encrypted: (experimental) Global RDS Database Cluster Engine Storage Encrypted Option . Default: - true
        :param time_zone: (experimental) RDS time zone. Default: - MySQLtimeZone.UTC
        :param vpc: (experimental) RDS default VPC. Default: - new VPC

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if db_clusterp_pg is not None:
            self._values["db_clusterp_pg"] = db_clusterp_pg
        if db_user_name is not None:
            self._values["db_user_name"] = db_user_name
        if default_database_name is not None:
            self._values["default_database_name"] = default_database_name
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if parameters is not None:
            self._values["parameters"] = parameters
        if rds_password is not None:
            self._values["rds_password"] = rds_password
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if time_zone is not None:
            self._values["time_zone"] = time_zone
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def db_clusterp_pg(self) -> typing.Optional[aws_cdk.aws_rds.IParameterGroup]:
        '''(experimental) RDS ParameterGroup.

        :default: - Aurora MySQL ParameterGroup

        :stability: experimental
        '''
        result = self._values.get("db_clusterp_pg")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IParameterGroup], result)

    @builtins.property
    def db_user_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) RDS default Super User Name.

        :default: - sysadmin

        :stability: experimental
        '''
        result = self._values.get("db_user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_database_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) RDS default Database Name.

        :default: - globaldatabase

        :stability: experimental
        '''
        result = self._values.get("default_database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deletion_protection(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Global RDS Database Cluster Engine Deletion Protection Option .

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[aws_cdk.aws_rds.IClusterEngine]:
        '''(experimental) RDS Database Cluster Engine .

        :default: - rds.DatabaseClusterEngine.auroraMysql({version: rds.AuroraMysqlEngineVersion.VER_2_07_1,})

        :stability: experimental
        '''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IClusterEngine], result)

    @builtins.property
    def instance_type(self) -> typing.Optional["InstanceTypeEnum"]:
        '''(experimental) RDS Instance Type only can use r4 or r5 type see more https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html#aurora-global-database.limitations.

        :default: - r5.large

        :stability: experimental
        '''
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional["InstanceTypeEnum"], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) RDS Parameters.

        :default: - {time_zone: 'UTC'}

        :stability: experimental
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def rds_password(self) -> typing.Optional[builtins.str]:
        '''(experimental) return RDS Cluster password.

        :stability: experimental
        '''
        result = self._values.get("rds_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_encrypted(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Global RDS Database Cluster Engine Storage Encrypted Option .

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def time_zone(self) -> typing.Optional["MySQLtimeZone"]:
        '''(experimental) RDS time zone.

        :default: - MySQLtimeZone.UTC

        :stability: experimental
        '''
        result = self._values.get("time_zone")
        return typing.cast(typing.Optional["MySQLtimeZone"], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) RDS default VPC.

        :default: - new VPC

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GolbalAuroraRDSMasterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GolbalAuroraRDSSlaveInfra(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aurora-globaldatabase.GolbalAuroraRDSSlaveInfra",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        deletion_protection: typing.Optional[builtins.bool] = None,
        stack: typing.Optional[aws_cdk.Stack] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        subnet_type: typing.Optional[aws_cdk.aws_ec2.SubnetType] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param deletion_protection: (experimental) Global RDS Database Cluster Engine Deletion Protection Option . Default: - false
        :param stack: (experimental) RDS Stack.
        :param storage_encrypted: (experimental) Global RDS Database Cluster Engine Storage Encrypted Option . Default: - true
        :param subnet_type: (experimental) Slave region.
        :param vpc: (experimental) Slave region VPC. Default: - new VPC

        :stability: experimental
        '''
        props = GolbalAuroraRDSSlaveInfraProps(
            deletion_protection=deletion_protection,
            stack=stack,
            storage_encrypted=storage_encrypted,
            subnet_type=subnet_type,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dbSubnetGroup")
    def db_subnet_group(self) -> aws_cdk.aws_rds.CfnDBSubnetGroup:
        '''(experimental) GolbalAuroraRDSSlaveInfra subnet group .

        :default: - true

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_rds.CfnDBSubnetGroup, jsii.get(self, "dbSubnetGroup"))


@jsii.data_type(
    jsii_type="cdk-aurora-globaldatabase.GolbalAuroraRDSSlaveInfraProps",
    jsii_struct_bases=[],
    name_mapping={
        "deletion_protection": "deletionProtection",
        "stack": "stack",
        "storage_encrypted": "storageEncrypted",
        "subnet_type": "subnetType",
        "vpc": "vpc",
    },
)
class GolbalAuroraRDSSlaveInfraProps:
    def __init__(
        self,
        *,
        deletion_protection: typing.Optional[builtins.bool] = None,
        stack: typing.Optional[aws_cdk.Stack] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        subnet_type: typing.Optional[aws_cdk.aws_ec2.SubnetType] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param deletion_protection: (experimental) Global RDS Database Cluster Engine Deletion Protection Option . Default: - false
        :param stack: (experimental) RDS Stack.
        :param storage_encrypted: (experimental) Global RDS Database Cluster Engine Storage Encrypted Option . Default: - true
        :param subnet_type: (experimental) Slave region.
        :param vpc: (experimental) Slave region VPC. Default: - new VPC

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if stack is not None:
            self._values["stack"] = stack
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if subnet_type is not None:
            self._values["subnet_type"] = subnet_type
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def deletion_protection(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Global RDS Database Cluster Engine Deletion Protection Option .

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("deletion_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stack(self) -> typing.Optional[aws_cdk.Stack]:
        '''(experimental) RDS Stack.

        :stability: experimental
        '''
        result = self._values.get("stack")
        return typing.cast(typing.Optional[aws_cdk.Stack], result)

    @builtins.property
    def storage_encrypted(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Global RDS Database Cluster Engine Storage Encrypted Option .

        :default: - true

        :stability: experimental
        '''
        result = self._values.get("storage_encrypted")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def subnet_type(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetType]:
        '''(experimental) Slave region.

        :stability: experimental
        '''
        result = self._values.get("subnet_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetType], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) Slave region VPC.

        :default: - new VPC

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GolbalAuroraRDSSlaveInfraProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-aurora-globaldatabase.InstanceTypeEnum")
class InstanceTypeEnum(enum.Enum):
    '''
    :stability: experimental
    '''

    R4_LARGE = "R4_LARGE"
    '''(experimental) db Instance Type r4.large.

    :stability: experimental
    '''
    R4_XLARGE = "R4_XLARGE"
    '''(experimental) db Instance Type r4.xlarge.

    :stability: experimental
    '''
    R4_2XLARGE = "R4_2XLARGE"
    '''(experimental) db Instance Type r4.2xlarge.

    :stability: experimental
    '''
    R4_4XLARGE = "R4_4XLARGE"
    '''(experimental) db Instance Type r4.4xlarge.

    :stability: experimental
    '''
    R4_8XLARGE = "R4_8XLARGE"
    '''(experimental) db Instance Type r4.8xlarge.

    :stability: experimental
    '''
    R4_16XLARGE = "R4_16XLARGE"
    '''(experimental) db Instance Type r4.16xlarge.

    :stability: experimental
    '''
    R5_LARGE = "R5_LARGE"
    '''(experimental) db Instance Type r5.large.

    :stability: experimental
    '''
    R5_XLARGE = "R5_XLARGE"
    '''(experimental) db Instance Type r5.xlarge.

    :stability: experimental
    '''
    R5_2XLARGE = "R5_2XLARGE"
    '''(experimental) db Instance Type r5.2xlarge.

    :stability: experimental
    '''
    R5_4XLARGE = "R5_4XLARGE"
    '''(experimental) db Instance Type r5.4xlarge.

    :stability: experimental
    '''
    R5_8XLARGE = "R5_8XLARGE"
    '''(experimental) db Instance Type r5.8xlarge.

    :stability: experimental
    '''
    R5_12XLARGE = "R5_12XLARGE"
    '''(experimental) db Instance Type r5.12xlarge.

    :stability: experimental
    '''
    R5_16XLARGE = "R5_16XLARGE"
    '''(experimental) db Instance Type r5.16xlarge.

    :stability: experimental
    '''
    R5_24XLARGE = "R5_24XLARGE"
    '''(experimental) db Instance Type r5.24xlarge.

    :stability: experimental
    '''


@jsii.enum(jsii_type="cdk-aurora-globaldatabase.MySQLtimeZone")
class MySQLtimeZone(enum.Enum):
    '''
    :stability: experimental
    '''

    UTC = "UTC"
    '''(experimental) TIME ZONE UTC.

    :stability: experimental
    '''
    ASIA_TAIPEI = "ASIA_TAIPEI"
    '''(experimental) TIME ZONE Asia/Taipei.

    :stability: experimental
    '''
    AFRICA_CAIRO = "AFRICA_CAIRO"
    '''(experimental) TIME ZONE Africa/Cairo.

    :stability: experimental
    '''
    ASIA_BANGKOK = "ASIA_BANGKOK"
    '''(experimental) TIME ZONE Asia/Bangkok.

    :stability: experimental
    '''
    AUSTRALIA_DARWIN = "AUSTRALIA_DARWIN"
    '''(experimental) TIME ZONE Australia/Darwin.

    :stability: experimental
    '''
    AFRICA_CASABLANCA = "AFRICA_CASABLANCA"
    '''(experimental) TIME ZONE Africa/Casablanca.

    :stability: experimental
    '''
    ASIA_BEIRUT = "ASIA_BEIRUT"
    '''(experimental) TIME ZONE Asia/Beirut.

    :stability: experimental
    '''
    AUSTRALIA_HOBART = "AUSTRALIA_HOBART"
    '''(experimental) TIME ZONE Australia/Hobart.

    :stability: experimental
    '''
    AFRICA_HARARE = "AFRICA_HARARE"
    '''(experimental) TIME ZONE Africa/Harare.

    :stability: experimental
    '''
    ASIA_CALCUTTA = "ASIA_CALCUTTA"
    '''(experimental) TIME ZONE Asia/Calcutta.

    :stability: experimental
    '''
    AUSTRALIA_PERTH = "AUSTRALIA_PERTH"
    '''(experimental) TIME ZONE Australia/Perth.

    :stability: experimental
    '''
    AFRICA_MONROVIA = "AFRICA_MONROVIA"
    '''(experimental) TIME ZONE Africa/Monrovia.

    :stability: experimental
    '''
    ASIA_DAMASCUS = "ASIA_DAMASCUS"
    '''(experimental) TIME ZONE Asia/Damascus.

    :stability: experimental
    '''
    AUSTRALIA_SYDNEY = "AUSTRALIA_SYDNEY"
    '''(experimental) TIME ZONE Australia/Sydney.

    :stability: experimental
    '''
    AFRICA_NAIROBI = "AFRICA_NAIROBI"
    '''(experimental) TIME ZONE Africa/Nairobi.

    :stability: experimental
    '''
    ASIA_DHAKA = "ASIA_DHAKA"
    '''(experimental) TIME ZONE Asia/Dhaka.

    :stability: experimental
    '''
    BRAZIL_EAST = "BRAZIL_EAST"
    '''(experimental) TIME ZONE Brazil/East.

    :stability: experimental
    '''
    AFRICA_TRIPOLI = "AFRICA_TRIPOLI"
    '''(experimental) TIME ZONE Africa/Tripoli.

    :stability: experimental
    '''
    ASIA_IRKUTSK = "ASIA_IRKUTSK"
    '''(experimental) TIME ZONE Asia/Irkutsk.

    :stability: experimental
    '''
    CANADA_NEWFOUNDLAND = "CANADA_NEWFOUNDLAND"
    '''(experimental) TIME ZONE Canada/Newfoundland.

    :stability: experimental
    '''
    AFRICA_WINDHOEK = "AFRICA_WINDHOEK"
    '''(experimental) TIME ZONE Africa/Windhoek.

    :stability: experimental
    '''
    ASIA_JERUSALEM = "ASIA_JERUSALEM"
    '''(experimental) TIME ZONE Asia/Jerusalem.

    :stability: experimental
    '''
    CANADA_SASKATCHEWAN = "CANADA_SASKATCHEWAN"
    '''(experimental) TIME ZONE Canada/Saskatchewan.

    :stability: experimental
    '''
    AMERICA_ARAGUAINA = "AMERICA_ARAGUAINA"
    '''(experimental) TIME ZONE America/Araguaina.

    :stability: experimental
    '''
    ASIA_KABUL = "ASIA_KABUL"
    '''(experimental) TIME ZONE Asia/Kabul.

    :stability: experimental
    '''
    EUROPE_AMSTERDAM = "EUROPE_AMSTERDAM"
    '''(experimental) TIME ZONE Europe/Amsterdam.

    :stability: experimental
    '''
    AMERICA_ASUNCION = "AMERICA_ASUNCION"
    '''(experimental) TIME ZONE America/Asuncion.

    :stability: experimental
    '''
    ASIA_KARACHI = "ASIA_KARACHI"
    '''(experimental) TIME ZONE Asia/Karachi.

    :stability: experimental
    '''
    EUROPE_ATHENS = "EUROPE_ATHENS"
    '''(experimental) TIME ZONE Europe/Athens.

    :stability: experimental
    '''
    AMERICA_BOGOTA = "AMERICA_BOGOTA"
    '''(experimental) TIME ZONE America/Bogota.

    :stability: experimental
    '''
    ASIA_KATHMANDU = "ASIA_KATHMANDU"
    '''(experimental) TIME ZONE Asia/Kathmandu.

    :stability: experimental
    '''
    EUROPE_DUBLIN = "EUROPE_DUBLIN"
    '''(experimental) TIME ZONE Europe/Dublin.

    :stability: experimental
    '''
    AMERICA_CARACAS = "AMERICA_CARACAS"
    '''(experimental) TIME ZONE America/Caracas.

    :stability: experimental
    '''
    ASIA_KRASNOYARSK = "ASIA_KRASNOYARSK"
    '''(experimental) TIME ZONE Asia/Krasnoyarsk.

    :stability: experimental
    '''
    EUROPE_HELSINKI = "EUROPE_HELSINKI"
    '''(experimental) TIME ZONE Europe/Helsinki.

    :stability: experimental
    '''
    AMERICA_CHIHUAHUA = "AMERICA_CHIHUAHUA"
    '''(experimental) TIME ZONE America/Chihuahua.

    :stability: experimental
    '''
    ASIA_MAGADAN = "ASIA_MAGADAN"
    '''(experimental) TIME ZONE Asia/Magadan.

    :stability: experimental
    '''
    EUROPE_ISTANBUL = "EUROPE_ISTANBUL"
    '''(experimental) TIME ZONE Europe/Istanbul.

    :stability: experimental
    '''
    AMERICA_CUIABA = "AMERICA_CUIABA"
    '''(experimental) TIME ZONE America/Cuiaba.

    :stability: experimental
    '''
    ASIA_MUSCAT = "ASIA_MUSCAT"
    '''(experimental) TIME ZONE Asia/Muscat.

    :stability: experimental
    '''
    EUROPE_KALININGRAD = "EUROPE_KALININGRAD"
    '''(experimental) TIME ZONE Europe/Kaliningrad.

    :stability: experimental
    '''
    AMERICA_DENVER = "AMERICA_DENVER"
    '''(experimental) TIME ZONE America/Denver.

    :stability: experimental
    '''
    ASIA_NOVOSIBIRSK = "ASIA_NOVOSIBIRSK"
    '''(experimental) TIME ZONE Asia/Novosibirsk.

    :stability: experimental
    '''
    EUROPE_MOSCOW = "EUROPE_MOSCOW"
    '''(experimental) TIME ZONE Europe/Moscow'.

    :stability: experimental
    '''
    AMERICA_FORTALEZA = "AMERICA_FORTALEZA"
    '''(experimental) TIME ZONE America/Fortaleza.

    :stability: experimental
    '''
    ASIA_RIYADH = "ASIA_RIYADH"
    '''(experimental) TIME ZONE Asia/Riyadh.

    :stability: experimental
    '''
    EUROPE_PARIS = "EUROPE_PARIS"
    '''(experimental) TIME ZONE Europe/Paris.

    :stability: experimental
    '''
    AMERICA_GUATEMALA = "AMERICA_GUATEMALA"
    '''(experimental) TIME ZONE America/Guatemala.

    :stability: experimental
    '''
    ASIA_SEOUL = "ASIA_SEOUL"
    '''(experimental) TIME ZONE Asia/Seoul.

    :stability: experimental
    '''
    EUROPE_PRAGUE = "EUROPE_PRAGUE"
    '''(experimental) TIME ZONE Europe/Prague.

    :stability: experimental
    '''
    AMERICA_HALIFAX = "AMERICA_HALIFAX"
    '''(experimental) TIME ZONE America/Halifax.

    :stability: experimental
    '''
    ASIA_SHANGHAI = "ASIA_SHANGHAI"
    '''(experimental) TIME ZONE Asia/Shanghai.

    :stability: experimental
    '''
    EUROPE_SARAJEVO = "EUROPE_SARAJEVO"
    '''(experimental) TIME ZONE Europe/Sarajevo.

    :stability: experimental
    '''
    AMERICA_MANAUS = "AMERICA_MANAUS"
    '''(experimental) TIME ZONE America/Manaus.

    :stability: experimental
    '''
    ASIA_SINGAPORE = "ASIA_SINGAPORE"
    '''(experimental) TIME ZONE Asia/Singapore.

    :stability: experimental
    '''
    PACIFIC_AUCKLAND = "PACIFIC_AUCKLAND"
    '''(experimental) TIME ZONE Pacific/Auckland.

    :stability: experimental
    '''
    AMERICA_MATAMOROS = "AMERICA_MATAMOROS"
    '''(experimental) TIME ZONE America/Matamoros.

    :stability: experimental
    '''
    PACIFIC_FIJI = "PACIFIC_FIJI"
    '''(experimental) TIME ZONE Pacific/Fiji.

    :stability: experimental
    '''
    AMERICA_MONTERREY = "AMERICA_MONTERREY"
    '''(experimental) TIME ZONE America/Monterrey.

    :stability: experimental
    '''
    ASIA_TEHRAN = "ASIA_TEHRAN"
    '''(experimental) TIME ZONE Asia/Tehran.

    :stability: experimental
    '''
    PACIFIC_GUAM = "PACIFIC_GUAM"
    '''(experimental) TIME ZONE Pacific/Guam.

    :stability: experimental
    '''
    AMERICA_MONTEVIDEO = "AMERICA_MONTEVIDEO"
    '''(experimental) TIME ZONE America/Montevideo.

    :stability: experimental
    '''
    ASIA_TOKYO = "ASIA_TOKYO"
    '''(experimental) TIME ZONE Asia/Tokyo.

    :stability: experimental
    '''
    PACIFIC_HONOLULU = "PACIFIC_HONOLULU"
    '''(experimental) TIME ZONE Pacific/Honolulu.

    :stability: experimental
    '''
    AMERICA_PHOENIX = "AMERICA_PHOENIX"
    '''(experimental) TIME ZONE America/Phoenix.

    :stability: experimental
    '''
    ASIA_ULAANBAATAR = "ASIA_ULAANBAATAR"
    '''(experimental) TIME ZONE Asia/Ulaanbaatar.

    :stability: experimental
    '''
    PACIFIC_SAMOA = "PACIFIC_SAMOA"
    '''(experimental) TIME ZONE Pacific/Samoa.

    :stability: experimental
    '''
    AMERICA_SANTIAGO = "AMERICA_SANTIAGO"
    '''(experimental) TIME ZONE America/Santiago.

    :stability: experimental
    '''
    ASIA_VLADIVOSTOK = "ASIA_VLADIVOSTOK"
    '''(experimental) TIME ZONE Asia/Vladivostok.

    :stability: experimental
    '''
    US_ALASKA = "US_ALASKA"
    '''(experimental) TIME ZONE US/Alaska.

    :stability: experimental
    '''
    AMERICA_TIJUANA = "AMERICA_TIJUANA"
    '''(experimental) TIME ZONE America/Tijuana.

    :stability: experimental
    '''
    ASIA_YAKUTSK = "ASIA_YAKUTSK"
    '''(experimental) TIME ZONE Asia/Yakutsk.

    :stability: experimental
    '''
    US_CENTRAL = "US_CENTRAL"
    '''(experimental) TIME ZONE US/Central.

    :stability: experimental
    '''
    ASIA_AMMAN = "ASIA_AMMAN"
    '''(experimental) TIME ZONE Asia/Amman.

    :stability: experimental
    '''
    ASIA_YEREVAN = "ASIA_YEREVAN"
    '''(experimental) TIME ZONE Asia/Yerevan.

    :stability: experimental
    '''
    US_EASTERN = "US_EASTERN"
    '''(experimental) TIME ZONE US/Eastern.

    :stability: experimental
    '''
    ASIA_ASHGABAT = "ASIA_ASHGABAT"
    '''(experimental) TIME ZONE Asia/Ashgabat.

    :stability: experimental
    '''
    ATLANTIC_AZORES = "ATLANTIC_AZORES"
    '''(experimental) TIME ZONE Atlantic/Azores.

    :stability: experimental
    '''
    US_EAST_INDIANA = "US_EAST_INDIANA"
    '''(experimental) TIME ZONE US/East-Indiana.

    :stability: experimental
    '''
    ASIA_BAGHDAD = "ASIA_BAGHDAD"
    '''(experimental) TIME ZONE Asia/Baghdad.

    :stability: experimental
    '''
    AUSTRALIA_ADELAIDE = "AUSTRALIA_ADELAIDE"
    '''(experimental) TIME ZONE Australia/Adelaide.

    :stability: experimental
    '''
    US_PACIFIC = "US_PACIFIC"
    '''(experimental) TIME ZONE US/Pacific.

    :stability: experimental
    '''
    ASIA_BAKU = "ASIA_BAKU"
    '''(experimental) TIME ZONE Asia/Baku.

    :stability: experimental
    '''
    AUSTRALIA_BRISBANE = "AUSTRALIA_BRISBANE"
    '''(experimental) TIME ZONE Australia/Brisbane.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="cdk-aurora-globaldatabase.RegionalOptions",
    jsii_struct_bases=[],
    name_mapping={"region": "region", "db_subnet_group_name": "dbSubnetGroupName"},
)
class RegionalOptions:
    def __init__(
        self,
        *,
        region: builtins.str,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param region: 
        :param db_subnet_group_name: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "region": region,
        }
        if db_subnet_group_name is not None:
            self._values["db_subnet_group_name"] = db_subnet_group_name

    @builtins.property
    def region(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db_subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("db_subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegionalOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GolbalAuroraRDSMaster",
    "GolbalAuroraRDSMasterProps",
    "GolbalAuroraRDSSlaveInfra",
    "GolbalAuroraRDSSlaveInfraProps",
    "InstanceTypeEnum",
    "MySQLtimeZone",
    "RegionalOptions",
]

publication.publish()
