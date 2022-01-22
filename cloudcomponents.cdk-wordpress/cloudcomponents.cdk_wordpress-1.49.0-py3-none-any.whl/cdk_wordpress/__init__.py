'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-wordpress

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-wordpress)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-wordpress/)

> CDK Construct to deploy wordpress

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-wordpress
```

Python:

```bash
pip install cloudcomponents.cdk-wordpress
```

## How to use

```python
import { PublicHostedZone } from '@aws-cdk/aws-route53';
import { Construct, RemovalPolicy, Stack, StackProps } from '@aws-cdk/core';

import { Wordpress } from '@cloudcomponents/cdk-wordpress';

export class WordpressStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const hostedZone = PublicHostedZone.fromLookup(this, 'HostedZone', {
      domainName: 'cloudcomponents.org',
    });

    new Wordpress(this, 'Wordpress', {
      domainName: 'blog.cloudcomponents.org',
      domainZone: hostedZone,
      removalPolicy: RemovalPolicy.DESTROY,
      offloadStaticContent: true, // Support for plugin e.g. `WP Offload Media for Amazon S3`
    });
  }
}
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-wordpress/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-wordpress/LICENSE)
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

import aws_cdk.aws_backup
import aws_cdk.aws_certificatemanager
import aws_cdk.aws_cloudfront
import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_rds
import aws_cdk.aws_route53
import aws_cdk.core


class Application(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-wordpress.Application",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        certificate: aws_cdk.aws_certificatemanager.ICertificate,
        database: "Database",
        domain_name: builtins.str,
        domain_zone: aws_cdk.aws_route53.IHostedZone,
        volume: "EfsVolume",
        vpc: aws_cdk.aws_ec2.IVpc,
        cloud_front_hash_header: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        image: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        log_driver: typing.Optional[aws_cdk.aws_ecs.LogDriver] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret]] = None,
        service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param certificate: -
        :param database: -
        :param domain_name: -
        :param domain_zone: -
        :param volume: -
        :param vpc: -
        :param cloud_front_hash_header: -
        :param environment: -
        :param image: -
        :param log_driver: -
        :param memory_limit_mib: -
        :param removal_policy: -
        :param secrets: -
        :param service_name: -
        '''
        props = ApplicationProps(
            certificate=certificate,
            database=database,
            domain_name=domain_name,
            domain_zone=domain_zone,
            volume=volume,
            vpc=vpc,
            cloud_front_hash_header=cloud_front_hash_header,
            environment=environment,
            image=image,
            log_driver=log_driver,
            memory_limit_mib=memory_limit_mib,
            removal_policy=removal_policy,
            secrets=secrets,
            service_name=service_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="enableStaticContentOffload")
    def enable_static_content_offload(
        self,
        domain_name: builtins.str,
        certificate: aws_cdk.aws_certificatemanager.ICertificate,
    ) -> "StaticContentOffload":
        '''
        :param domain_name: -
        :param certificate: -
        '''
        return typing.cast("StaticContentOffload", jsii.invoke(self, "enableStaticContentOffload", [domain_name, certificate]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distribution")
    def distribution(self) -> aws_cdk.aws_cloudfront.IDistribution:
        return typing.cast(aws_cdk.aws_cloudfront.IDistribution, jsii.get(self, "distribution"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainZone")
    def domain_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        return typing.cast(aws_cdk.aws_route53.IHostedZone, jsii.get(self, "domainZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="listener")
    def listener(self) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationListener:
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationListener, jsii.get(self, "listener"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="service")
    def service(self) -> aws_cdk.aws_ecs.FargateService:
        return typing.cast(aws_cdk.aws_ecs.FargateService, jsii.get(self, "service"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetGroup")
    def target_group(self) -> aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup:
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup, jsii.get(self, "targetGroup"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-wordpress.ApplicationProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "database": "database",
        "domain_name": "domainName",
        "domain_zone": "domainZone",
        "volume": "volume",
        "vpc": "vpc",
        "cloud_front_hash_header": "cloudFrontHashHeader",
        "environment": "environment",
        "image": "image",
        "log_driver": "logDriver",
        "memory_limit_mib": "memoryLimitMiB",
        "removal_policy": "removalPolicy",
        "secrets": "secrets",
        "service_name": "serviceName",
    },
)
class ApplicationProps:
    def __init__(
        self,
        *,
        certificate: aws_cdk.aws_certificatemanager.ICertificate,
        database: "Database",
        domain_name: builtins.str,
        domain_zone: aws_cdk.aws_route53.IHostedZone,
        volume: "EfsVolume",
        vpc: aws_cdk.aws_ec2.IVpc,
        cloud_front_hash_header: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        image: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        log_driver: typing.Optional[aws_cdk.aws_ecs.LogDriver] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret]] = None,
        service_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param certificate: -
        :param database: -
        :param domain_name: -
        :param domain_zone: -
        :param volume: -
        :param vpc: -
        :param cloud_front_hash_header: -
        :param environment: -
        :param image: -
        :param log_driver: -
        :param memory_limit_mib: -
        :param removal_policy: -
        :param secrets: -
        :param service_name: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "certificate": certificate,
            "database": database,
            "domain_name": domain_name,
            "domain_zone": domain_zone,
            "volume": volume,
            "vpc": vpc,
        }
        if cloud_front_hash_header is not None:
            self._values["cloud_front_hash_header"] = cloud_front_hash_header
        if environment is not None:
            self._values["environment"] = environment
        if image is not None:
            self._values["image"] = image
        if log_driver is not None:
            self._values["log_driver"] = log_driver
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if secrets is not None:
            self._values["secrets"] = secrets
        if service_name is not None:
            self._values["service_name"] = service_name

    @builtins.property
    def certificate(self) -> aws_cdk.aws_certificatemanager.ICertificate:
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(aws_cdk.aws_certificatemanager.ICertificate, result)

    @builtins.property
    def database(self) -> "Database":
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast("Database", result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        result = self._values.get("domain_zone")
        assert result is not None, "Required property 'domain_zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def volume(self) -> "EfsVolume":
        result = self._values.get("volume")
        assert result is not None, "Required property 'volume' is missing"
        return typing.cast("EfsVolume", result)

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def cloud_front_hash_header(self) -> typing.Optional[builtins.str]:
        result = self._values.get("cloud_front_hash_header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def image(self) -> typing.Optional[aws_cdk.aws_ecs.ContainerImage]:
        result = self._values.get("image")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ContainerImage], result)

    @builtins.property
    def log_driver(self) -> typing.Optional[aws_cdk.aws_ecs.LogDriver]:
        result = self._values.get("log_driver")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.LogDriver], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret]]:
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret]], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Database(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-wordpress.Database",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        allocated_storage: typing.Optional[jsii.Number] = None,
        database_name: typing.Optional[builtins.str] = None,
        engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: -
        :param allocated_storage: -
        :param database_name: -
        :param engine: -
        :param instance_type: -
        :param removal_policy: -
        '''
        props = DatabaseProps(
            vpc=vpc,
            allocated_storage=allocated_storage,
            database_name=database_name,
            engine=engine,
            instance_type=instance_type,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="allowDefaultPortFrom")
    def allow_default_port_from(
        self,
        other: aws_cdk.aws_ec2.IConnectable,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param other: -
        :param description: -
        '''
        return typing.cast(None, jsii.invoke(self, "allowDefaultPortFrom", [other, description]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secrets")
    def secrets(self) -> typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret]:
        return typing.cast(typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret], jsii.get(self, "secrets"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-wordpress.DatabaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "allocated_storage": "allocatedStorage",
        "database_name": "databaseName",
        "engine": "engine",
        "instance_type": "instanceType",
        "removal_policy": "removalPolicy",
    },
)
class DatabaseProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        allocated_storage: typing.Optional[jsii.Number] = None,
        database_name: typing.Optional[builtins.str] = None,
        engine: typing.Optional[aws_cdk.aws_rds.IInstanceEngine] = None,
        instance_type: typing.Optional[aws_cdk.aws_ec2.InstanceType] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
    ) -> None:
        '''
        :param vpc: -
        :param allocated_storage: -
        :param database_name: -
        :param engine: -
        :param instance_type: -
        :param removal_policy: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if allocated_storage is not None:
            self._values["allocated_storage"] = allocated_storage
        if database_name is not None:
            self._values["database_name"] = database_name
        if engine is not None:
            self._values["engine"] = engine
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def allocated_storage(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("allocated_storage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def database_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("database_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine(self) -> typing.Optional[aws_cdk.aws_rds.IInstanceEngine]:
        result = self._values.get("engine")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.IInstanceEngine], result)

    @builtins.property
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        result = self._values.get("instance_type")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Dns(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-wordpress.Dns",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        distribution: aws_cdk.aws_cloudfront.IDistribution,
        domain_name: builtins.str,
        domain_zone: aws_cdk.aws_route53.IHostedZone,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param distribution: -
        :param domain_name: -
        :param domain_zone: -
        '''
        props = DnsProps(
            distribution=distribution, domain_name=domain_name, domain_zone=domain_zone
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-wordpress.DnsProps",
    jsii_struct_bases=[],
    name_mapping={
        "distribution": "distribution",
        "domain_name": "domainName",
        "domain_zone": "domainZone",
    },
)
class DnsProps:
    def __init__(
        self,
        *,
        distribution: aws_cdk.aws_cloudfront.IDistribution,
        domain_name: builtins.str,
        domain_zone: aws_cdk.aws_route53.IHostedZone,
    ) -> None:
        '''
        :param distribution: -
        :param domain_name: -
        :param domain_zone: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "distribution": distribution,
            "domain_name": domain_name,
            "domain_zone": domain_zone,
        }

    @builtins.property
    def distribution(self) -> aws_cdk.aws_cloudfront.IDistribution:
        result = self._values.get("distribution")
        assert result is not None, "Required property 'distribution' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.IDistribution, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        result = self._values.get("domain_zone")
        assert result is not None, "Required property 'domain_zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DnsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EfsVolume(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-wordpress.EfsVolume",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param vpc: -
        :param name: -
        :param removal_policy: -
        '''
        props = EfsVolumeProps(vpc=vpc, name=name, removal_policy=removal_policy)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="allowDefaultPortFrom")
    def allow_default_port_from(
        self,
        other: aws_cdk.aws_ec2.IConnectable,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param other: -
        :param description: -
        '''
        return typing.cast(None, jsii.invoke(self, "allowDefaultPortFrom", [other, description]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="efsVolumeConfiguration")
    def efs_volume_configuration(self) -> aws_cdk.aws_ecs.EfsVolumeConfiguration:
        return typing.cast(aws_cdk.aws_ecs.EfsVolumeConfiguration, jsii.get(self, "efsVolumeConfiguration"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-wordpress.EfsVolumeProps",
    jsii_struct_bases=[],
    name_mapping={"vpc": "vpc", "name": "name", "removal_policy": "removalPolicy"},
)
class EfsVolumeProps:
    def __init__(
        self,
        *,
        vpc: aws_cdk.aws_ec2.IVpc,
        name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
    ) -> None:
        '''
        :param vpc: -
        :param name: -
        :param removal_policy: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "vpc": vpc,
        }
        if name is not None:
            self._values["name"] = name
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(aws_cdk.aws_ec2.IVpc, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EfsVolumeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-wordpress.StaticContentOffload",
    jsii_struct_bases=[],
    name_mapping={"distribution": "distribution", "domain_name": "domainName"},
)
class StaticContentOffload:
    def __init__(
        self,
        *,
        distribution: aws_cdk.aws_cloudfront.IDistribution,
        domain_name: builtins.str,
    ) -> None:
        '''
        :param distribution: -
        :param domain_name: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "distribution": distribution,
            "domain_name": domain_name,
        }

    @builtins.property
    def distribution(self) -> aws_cdk.aws_cloudfront.IDistribution:
        result = self._values.get("distribution")
        assert result is not None, "Required property 'distribution' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.IDistribution, result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaticContentOffload(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Wordpress(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-wordpress.Wordpress",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        domain_zone: aws_cdk.aws_route53.IHostedZone,
        backup_plan: typing.Optional[aws_cdk.aws_backup.BackupPlan] = None,
        cloud_front_hash_header: typing.Optional[builtins.str] = None,
        database: typing.Optional[Database] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        image: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        log_driver: typing.Optional[aws_cdk.aws_ecs.LogDriver] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        offload_static_content: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret]] = None,
        service_name: typing.Optional[builtins.str] = None,
        subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        volume: typing.Optional[EfsVolume] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: -
        :param domain_zone: -
        :param backup_plan: -
        :param cloud_front_hash_header: -
        :param database: -
        :param environment: -
        :param image: -
        :param log_driver: -
        :param memory_limit_mib: -
        :param offload_static_content: -
        :param removal_policy: -
        :param secrets: -
        :param service_name: -
        :param subject_alternative_names: -
        :param volume: -
        :param vpc: -
        '''
        props = WordpressProps(
            domain_name=domain_name,
            domain_zone=domain_zone,
            backup_plan=backup_plan,
            cloud_front_hash_header=cloud_front_hash_header,
            database=database,
            environment=environment,
            image=image,
            log_driver=log_driver,
            memory_limit_mib=memory_limit_mib,
            offload_static_content=offload_static_content,
            removal_policy=removal_policy,
            secrets=secrets,
            service_name=service_name,
            subject_alternative_names=subject_alternative_names,
            volume=volume,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="application")
    def application(self) -> Application:
        return typing.cast(Application, jsii.get(self, "application"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="database")
    def database(self) -> Database:
        return typing.cast(Database, jsii.get(self, "database"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volume")
    def volume(self) -> EfsVolume:
        return typing.cast(EfsVolume, jsii.get(self, "volume"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staticContentOffload")
    def static_content_offload(self) -> typing.Optional[StaticContentOffload]:
        return typing.cast(typing.Optional[StaticContentOffload], jsii.get(self, "staticContentOffload"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-wordpress.WordpressProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "domain_zone": "domainZone",
        "backup_plan": "backupPlan",
        "cloud_front_hash_header": "cloudFrontHashHeader",
        "database": "database",
        "environment": "environment",
        "image": "image",
        "log_driver": "logDriver",
        "memory_limit_mib": "memoryLimitMiB",
        "offload_static_content": "offloadStaticContent",
        "removal_policy": "removalPolicy",
        "secrets": "secrets",
        "service_name": "serviceName",
        "subject_alternative_names": "subjectAlternativeNames",
        "volume": "volume",
        "vpc": "vpc",
    },
)
class WordpressProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        domain_zone: aws_cdk.aws_route53.IHostedZone,
        backup_plan: typing.Optional[aws_cdk.aws_backup.BackupPlan] = None,
        cloud_front_hash_header: typing.Optional[builtins.str] = None,
        database: typing.Optional[Database] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        image: typing.Optional[aws_cdk.aws_ecs.ContainerImage] = None,
        log_driver: typing.Optional[aws_cdk.aws_ecs.LogDriver] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        offload_static_content: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret]] = None,
        service_name: typing.Optional[builtins.str] = None,
        subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        volume: typing.Optional[EfsVolume] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param domain_name: -
        :param domain_zone: -
        :param backup_plan: -
        :param cloud_front_hash_header: -
        :param database: -
        :param environment: -
        :param image: -
        :param log_driver: -
        :param memory_limit_mib: -
        :param offload_static_content: -
        :param removal_policy: -
        :param secrets: -
        :param service_name: -
        :param subject_alternative_names: -
        :param volume: -
        :param vpc: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
            "domain_zone": domain_zone,
        }
        if backup_plan is not None:
            self._values["backup_plan"] = backup_plan
        if cloud_front_hash_header is not None:
            self._values["cloud_front_hash_header"] = cloud_front_hash_header
        if database is not None:
            self._values["database"] = database
        if environment is not None:
            self._values["environment"] = environment
        if image is not None:
            self._values["image"] = image
        if log_driver is not None:
            self._values["log_driver"] = log_driver
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if offload_static_content is not None:
            self._values["offload_static_content"] = offload_static_content
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if secrets is not None:
            self._values["secrets"] = secrets
        if service_name is not None:
            self._values["service_name"] = service_name
        if subject_alternative_names is not None:
            self._values["subject_alternative_names"] = subject_alternative_names
        if volume is not None:
            self._values["volume"] = volume
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def domain_name(self) -> builtins.str:
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        result = self._values.get("domain_zone")
        assert result is not None, "Required property 'domain_zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def backup_plan(self) -> typing.Optional[aws_cdk.aws_backup.BackupPlan]:
        result = self._values.get("backup_plan")
        return typing.cast(typing.Optional[aws_cdk.aws_backup.BackupPlan], result)

    @builtins.property
    def cloud_front_hash_header(self) -> typing.Optional[builtins.str]:
        result = self._values.get("cloud_front_hash_header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database(self) -> typing.Optional[Database]:
        result = self._values.get("database")
        return typing.cast(typing.Optional[Database], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def image(self) -> typing.Optional[aws_cdk.aws_ecs.ContainerImage]:
        result = self._values.get("image")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.ContainerImage], result)

    @builtins.property
    def log_driver(self) -> typing.Optional[aws_cdk.aws_ecs.LogDriver]:
        result = self._values.get("log_driver")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.LogDriver], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def offload_static_content(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("offload_static_content")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret]]:
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, aws_cdk.aws_ecs.Secret]], result)

    @builtins.property
    def service_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("service_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subject_alternative_names(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("subject_alternative_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def volume(self) -> typing.Optional[EfsVolume]:
        result = self._values.get("volume")
        return typing.cast(typing.Optional[EfsVolume], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WordpressProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Application",
    "ApplicationProps",
    "Database",
    "DatabaseProps",
    "Dns",
    "DnsProps",
    "EfsVolume",
    "EfsVolumeProps",
    "StaticContentOffload",
    "Wordpress",
    "WordpressProps",
]

publication.publish()
