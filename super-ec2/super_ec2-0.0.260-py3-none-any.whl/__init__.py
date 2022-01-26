'''
[![NPM version](https://badge.fury.io/js/%40cdk-constructs-zone%2Fsuper-ec2.svg)](https://badge.fury.io/js/%40cdk-constructs-zone%2Fsuper-ec2)
[![PyPI version](https://badge.fury.io/py/super-ec2.svg)](https://badge.fury.io/py/super-ec2)
![Release](https://github.com/cdk-constructs-zone/super-ec2/workflows/release/badge.svg)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/@cdk-constructs-zone/super-ec2?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/super-ec2?label=pypi&color=blue)

![](https://img.shields.io/badge/jenkins-ec2-green=?style=plastic&logo=appveyor)

# Welcome to `@cdk-constructs-zone/super-ec2`

This repository template helps you create EC2 .

## Sample

### Jenkins

* Simplest deployment: It would creat a VPC and ALB by default.

```python
import * as cdk from '@aws-cdk/core';
import { JenkinsEC2, ELBtype } from '@cdk-constructs-zone/super-ec2';

const app = new cdk.App();

const stack = new cdk.Stack(app, 'demo');

const jks = new JenkinsEC2(stack, 'superJks', {});

new cdk.CfnOutput(stack, 'loadbalancerDNS', {
  value: jks.loadbalancer.loadBalancerDnsName,
});
new cdk.CfnOutput(stack, 'connect-to-instance', {
  value: `aws ssm start-session --target ${jks.instance.instanceId}`,
});
```

* Deploy Jenkins with self-defined VPC and NLB

```python
const jks = new JenkinsEC2(stack, 'superJks', {
  vpc: Vpc.fromLookup(stack, 'defaultVPC', { isDefault: true }),
  loadbalancerType: ELBtype.NLB,
});
```

* Deploy Jenkins with R53 records: If `acm` is not given, it would create a certificate validated from DNS by default.

```python
const jks = new JenkinsEC2(stack, 'superJks', {
  vpc: Vpc.fromLookup(stack, 'defaultVPC', { isDefault: true }),
  loadbalancerType: ELBtype.NLB,
  domain: {
    acm: Certificate.fromCertificateArn(stack, 'cert',
      'arn:aws:xxx',
    ),
    hostedZoneId: 'xxx',
    zoneName: 'bbb.ccc',
    recordName: 'aaa',
  },
});
```

Note: Jenkins initial admin password has been written to `/home/ec2-user/jenkins-data/secrets/initialAdminPassword`. You can access EC2 instance using [ssm tool](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html).

```
aws ssm start-session --target instance-id
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

import aws_cdk.aws_certificatemanager
import aws_cdk.aws_ec2
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_route53
import aws_cdk.core


@jsii.enum(jsii_type="@cdk-constructs-zone/super-ec2.AmiOSType")
class AmiOSType(enum.Enum):
    '''
    :stability: experimental
    '''

    UBUNTU_18_04 = "UBUNTU_18_04"
    '''(experimental) Ubuntu 18.04 ami.

    :stability: experimental
    '''
    UBUNTU_20_04 = "UBUNTU_20_04"
    '''(experimental) Ubuntu 20.04 ami.

    :stability: experimental
    '''
    CENTOS_7 = "CENTOS_7"
    '''(experimental) CentOS 7 ami.

    :stability: experimental
    '''
    CENTOS_8 = "CENTOS_8"
    '''(experimental) CentOS 8 ami.

    :stability: experimental
    '''
    AMAZON_LINUX_2 = "AMAZON_LINUX_2"
    '''(experimental) Amazon Linux 2 ami.

    :stability: experimental
    '''
    AMAZON_LINUX = "AMAZON_LINUX"
    '''(experimental) Amazon Linux  ami.

    :stability: experimental
    '''


@jsii.enum(jsii_type="@cdk-constructs-zone/super-ec2.ELBtype")
class ELBtype(enum.Enum):
    '''
    :stability: experimental
    '''

    ALB = "ALB"
    '''(experimental) Application Load Balancer.

    :stability: experimental
    '''
    NLB = "NLB"
    '''(experimental) Network Load Balancer.

    :stability: experimental
    '''


@jsii.interface(jsii_type="@cdk-constructs-zone/super-ec2.IDomainProps")
class IDomainProps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        '''(experimental) HostZoneID.

        :stability: experimental
        '''
        ...

    @hosted_zone_id.setter
    def hosted_zone_id(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recordName")
    def record_name(self) -> builtins.str:
        '''(experimental) recordname (e.g., superjks).

        :stability: experimental
        '''
        ...

    @record_name.setter
    def record_name(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        '''(experimental) zonename (e.g., ``cdk-construct-zone.com``).

        :stability: experimental
        '''
        ...

    @zone_name.setter
    def zone_name(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acm")
    def acm(self) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''(experimental) Provide a certificate.

        :default: - Create a new certificate (validate from DNS)

        :stability: experimental
        '''
        ...

    @acm.setter
    def acm(
        self,
        value: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''(experimental) record cache time.

        :stability: experimental
        :deafult: - 5 mins.
        '''
        ...

    @ttl.setter
    def ttl(self, value: typing.Optional[aws_cdk.core.Duration]) -> None:
        ...


class _IDomainPropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdk-constructs-zone/super-ec2.IDomainProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostedZoneId")
    def hosted_zone_id(self) -> builtins.str:
        '''(experimental) HostZoneID.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "hostedZoneId"))

    @hosted_zone_id.setter
    def hosted_zone_id(self, value: builtins.str) -> None:
        jsii.set(self, "hostedZoneId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recordName")
    def record_name(self) -> builtins.str:
        '''(experimental) recordname (e.g., superjks).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "recordName"))

    @record_name.setter
    def record_name(self, value: builtins.str) -> None:
        jsii.set(self, "recordName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        '''(experimental) zonename (e.g., ``cdk-construct-zone.com``).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @zone_name.setter
    def zone_name(self, value: builtins.str) -> None:
        jsii.set(self, "zoneName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acm")
    def acm(self) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''(experimental) Provide a certificate.

        :default: - Create a new certificate (validate from DNS)

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], jsii.get(self, "acm"))

    @acm.setter
    def acm(
        self,
        value: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate],
    ) -> None:
        jsii.set(self, "acm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''(experimental) record cache time.

        :stability: experimental
        :deafult: - 5 mins.
        '''
        return typing.cast(typing.Optional[aws_cdk.core.Duration], jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: typing.Optional[aws_cdk.core.Duration]) -> None:
        jsii.set(self, "ttl", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDomainProps).__jsii_proxy_class__ = lambda : _IDomainPropsProxy


@jsii.interface(jsii_type="@cdk-constructs-zone/super-ec2.ISuperDomainProps")
class ISuperDomainProps(IDomainProps, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancer")
    def loadbalancer(
        self,
    ) -> typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]:
        '''
        :stability: experimental
        '''
        ...

    @loadbalancer.setter
    def loadbalancer(
        self,
        value: typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer],
    ) -> None:
        ...


class _ISuperDomainPropsProxy(
    jsii.proxy_for(IDomainProps) # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdk-constructs-zone/super-ec2.ISuperDomainProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancer")
    def loadbalancer(
        self,
    ) -> typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer], jsii.get(self, "loadbalancer"))

    @loadbalancer.setter
    def loadbalancer(
        self,
        value: typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer],
    ) -> None:
        jsii.set(self, "loadbalancer", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISuperDomainProps).__jsii_proxy_class__ = lambda : _ISuperDomainPropsProxy


@jsii.interface(jsii_type="@cdk-constructs-zone/super-ec2.ISuperEC2BaseProps")
class ISuperEC2BaseProps(typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiOSType")
    def ami_os_type(self) -> typing.Optional[AmiOSType]:
        '''(experimental) Super EC2 OS you want.

        :default: - Amzaon Linux 2.

        :stability: experimental
        '''
        ...

    @ami_os_type.setter
    def ami_os_type(self, value: typing.Optional[AmiOSType]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''(experimental) Super EC2 Instance Type.

        :default: - t3.small.

        :stability: experimental
        '''
        ...

    @instance_type.setter
    def instance_type(
        self,
        value: typing.Optional[aws_cdk.aws_ec2.InstanceType],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) Super EC2 Vpc.

        :default: - Create a new Vpc.

        :stability: experimental
        '''
        ...

    @vpc.setter
    def vpc(self, value: typing.Optional[aws_cdk.aws_ec2.IVpc]) -> None:
        ...


class _ISuperEC2BasePropsProxy:
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdk-constructs-zone/super-ec2.ISuperEC2BaseProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiOSType")
    def ami_os_type(self) -> typing.Optional[AmiOSType]:
        '''(experimental) Super EC2 OS you want.

        :default: - Amzaon Linux 2.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[AmiOSType], jsii.get(self, "amiOSType"))

    @ami_os_type.setter
    def ami_os_type(self, value: typing.Optional[AmiOSType]) -> None:
        jsii.set(self, "amiOSType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''(experimental) Super EC2 Instance Type.

        :default: - t3.small.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(
        self,
        value: typing.Optional[aws_cdk.aws_ec2.InstanceType],
    ) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) Super EC2 Vpc.

        :default: - Create a new Vpc.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: typing.Optional[aws_cdk.aws_ec2.IVpc]) -> None:
        jsii.set(self, "vpc", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISuperEC2BaseProps).__jsii_proxy_class__ = lambda : _ISuperEC2BasePropsProxy


class SuperDomain(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-constructs-zone/super-ec2.SuperDomain",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        props: ISuperDomainProps,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="acm")
    def acm(self) -> aws_cdk.aws_certificatemanager.ICertificate:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_certificatemanager.ICertificate, jsii.get(self, "acm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="record")
    def record(self) -> aws_cdk.aws_route53.ARecord:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_route53.ARecord, jsii.get(self, "record"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="zone")
    def zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_route53.IHostedZone, jsii.get(self, "zone"))


class SuperEC2Base(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdk-constructs-zone/super-ec2.SuperEC2Base",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        props: ISuperEC2BaseProps,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultSecurityGroup")
    def default_security_group(self) -> aws_cdk.aws_ec2.SecurityGroup:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.SecurityGroup, jsii.get(self, "defaultSecurityGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instance")
    def instance(self) -> aws_cdk.aws_ec2.Instance:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.Instance, jsii.get(self, "instance"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userData")
    def user_data(self) -> aws_cdk.aws_ec2.UserData:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.UserData, jsii.get(self, "userData"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))


class _SuperEC2BaseProxy(SuperEC2Base):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, SuperEC2Base).__jsii_proxy_class__ = lambda : _SuperEC2BaseProxy


@jsii.interface(jsii_type="@cdk-constructs-zone/super-ec2.IJenkinsEC2Props")
class IJenkinsEC2Props(ISuperEC2BaseProps, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> typing.Optional[IDomainProps]:
        '''(experimental) Provide domain attribute.

        :default: - Not use certificate and route53

        :stability: experimental
        '''
        ...

    @domain.setter
    def domain(self, value: typing.Optional[IDomainProps]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancer")
    def loadbalancer(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]]:
        '''(experimental) Provide a loadbalancer.

        Only support ALB and NLB.

        :default: - Create ApplicationLoadBalancer

        :stability: experimental
        '''
        ...

    @loadbalancer.setter
    def loadbalancer(
        self,
        value: typing.Optional[typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancerType")
    def loadbalancer_type(self) -> typing.Optional[ELBtype]:
        '''(experimental) ELB type.

        :default: - ELBtype.ALB

        :stability: experimental
        '''
        ...

    @loadbalancer_type.setter
    def loadbalancer_type(self, value: typing.Optional[ELBtype]) -> None:
        ...


class _IJenkinsEC2PropsProxy(
    jsii.proxy_for(ISuperEC2BaseProps) # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdk-constructs-zone/super-ec2.IJenkinsEC2Props"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> typing.Optional[IDomainProps]:
        '''(experimental) Provide domain attribute.

        :default: - Not use certificate and route53

        :stability: experimental
        '''
        return typing.cast(typing.Optional[IDomainProps], jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: typing.Optional[IDomainProps]) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancer")
    def loadbalancer(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]]:
        '''(experimental) Provide a loadbalancer.

        Only support ALB and NLB.

        :default: - Create ApplicationLoadBalancer

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]], jsii.get(self, "loadbalancer"))

    @loadbalancer.setter
    def loadbalancer(
        self,
        value: typing.Optional[typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]],
    ) -> None:
        jsii.set(self, "loadbalancer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancerType")
    def loadbalancer_type(self) -> typing.Optional[ELBtype]:
        '''(experimental) ELB type.

        :default: - ELBtype.ALB

        :stability: experimental
        '''
        return typing.cast(typing.Optional[ELBtype], jsii.get(self, "loadbalancerType"))

    @loadbalancer_type.setter
    def loadbalancer_type(self, value: typing.Optional[ELBtype]) -> None:
        jsii.set(self, "loadbalancerType", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IJenkinsEC2Props).__jsii_proxy_class__ = lambda : _IJenkinsEC2PropsProxy


class JenkinsEC2(
    SuperEC2Base,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdk-constructs-zone/super-ec2.JenkinsEC2",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        props: IJenkinsEC2Props,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="jenkinsUserData")
    def jenkins_user_data(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.invoke(self, "jenkinsUserData", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="loadbalancer")
    def loadbalancer(
        self,
    ) -> typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Union[aws_cdk.aws_elasticloadbalancingv2.ApplicationLoadBalancer, aws_cdk.aws_elasticloadbalancingv2.NetworkLoadBalancer], jsii.get(self, "loadbalancer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> typing.Optional[SuperDomain]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[SuperDomain], jsii.get(self, "domain"))


__all__ = [
    "AmiOSType",
    "ELBtype",
    "IDomainProps",
    "IJenkinsEC2Props",
    "ISuperDomainProps",
    "ISuperEC2BaseProps",
    "JenkinsEC2",
    "SuperDomain",
    "SuperEC2Base",
]

publication.publish()
