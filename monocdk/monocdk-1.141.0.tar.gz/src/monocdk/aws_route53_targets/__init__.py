'''
# Route53 Alias Record Targets for the CDK Route53 Library

This library contains Route53 Alias Record targets for:

* API Gateway custom domains

  ```python
  import monocdk as apigw

  # zone: route53.HostedZone
  # rest_api: apigw.LambdaRestApi


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.ApiGateway(rest_api))
  )
  ```
* API Gateway V2 custom domains

  ```python
  import monocdk as apigwv2

  # zone: route53.HostedZone
  # domain_name: apigwv2.DomainName


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.ApiGatewayv2DomainProperties(domain_name.regional_domain_name, domain_name.regional_hosted_zone_id))
  )
  ```
* CloudFront distributions

  ```python
  import monocdk as cloudfront

  # zone: route53.HostedZone
  # distribution: cloudfront.CloudFrontWebDistribution


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution))
  )
  ```
* ELBv2 load balancers

  ```python
  import monocdk as elbv2

  # zone: route53.HostedZone
  # lb: elbv2.ApplicationLoadBalancer


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(lb))
  )
  ```
* Classic load balancers

  ```python
  import monocdk as elb

  # zone: route53.HostedZone
  # lb: elb.LoadBalancer


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.ClassicLoadBalancerTarget(lb))
  )
  ```

**Important:** Based on [AWS documentation](https://aws.amazon.com/de/premiumsupport/knowledge-center/alias-resource-record-set-route53-cli/), all alias record in Route 53 that points to a Elastic Load Balancer will always include *dualstack* for the DNSName to resolve IPv4/IPv6 addresses (without *dualstack* IPv6 will not resolve).

For example, if the Amazon-provided DNS for the load balancer is `ALB-xxxxxxx.us-west-2.elb.amazonaws.com`, CDK will create alias target in Route 53 will be `dualstack.ALB-xxxxxxx.us-west-2.elb.amazonaws.com`.

* GlobalAccelerator

  ```python
  import monocdk as globalaccelerator

  # zone: route53.HostedZone
  # accelerator: globalaccelerator.Accelerator


  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.GlobalAcceleratorTarget(accelerator))
  )
  ```

**Important:** If you use GlobalAcceleratorDomainTarget, passing a string rather than an instance of IAccelerator, ensure that the string is a valid domain name of an existing Global Accelerator instance.
See [the documentation on DNS addressing](https://docs.aws.amazon.com/global-accelerator/latest/dg/dns-addressing-custom-domains.dns-addressing.html) with Global Accelerator for more info.

* InterfaceVpcEndpoints

**Important:** Based on the CFN docs for VPCEndpoints - [see here](attrDnsEntries) - the attributes returned for DnsEntries in CloudFormation is a combination of the hosted zone ID and the DNS name. The entries are ordered as follows: regional public DNS, zonal public DNS, private DNS, and wildcard DNS. This order is not enforced for AWS Marketplace services, and therefore this CDK construct is ONLY guaranteed to work with non-marketplace services.

```python
import monocdk as ec2

# zone: route53.HostedZone
# interface_vpc_endpoint: ec2.InterfaceVpcEndpoint


route53.ARecord(self, "AliasRecord",
    zone=zone,
    target=route53.RecordTarget.from_alias(targets.InterfaceVpcEndpointTarget(interface_vpc_endpoint))
)
```

* S3 Bucket Website:

**Important:** The Bucket name must strictly match the full DNS name.
See [the Developer Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/getting-started.html) for more info.

```python
import monocdk as s3


record_name = "www"
domain_name = "example.com"

bucket_website = s3.Bucket(self, "BucketWebsite",
    bucket_name=[record_name, domain_name].join("."),  # www.example.com
    public_read_access=True,
    website_index_document="index.html"
)

zone = route53.HostedZone.from_lookup(self, "Zone", domain_name=domain_name) # example.com

route53.ARecord(self, "AliasRecord",
    zone=zone,
    record_name=record_name,  # www
    target=route53.RecordTarget.from_alias(targets.BucketWebsiteTarget(bucket_website))
)
```

* User pool domain

  ```python
  import monocdk as cognito

  # zone: route53.HostedZone
  # domain: cognito.UserPoolDomain

  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.UserPoolDomainTarget(domain))
  )
  ```
* Route 53 record

  ```python
  # zone: route53.HostedZone
  # record: route53.ARecord

  route53.ARecord(self, "AliasRecord",
      zone=zone,
      target=route53.RecordTarget.from_alias(targets.Route53RecordTarget(record))
  )
  ```
* Elastic Beanstalk environment:

**Important:** Only supports Elastic Beanstalk environments created after 2016 that have a regional endpoint.

```python
# zone: route53.HostedZone
# ebs_environment_url: str


route53.ARecord(self, "AliasRecord",
    zone=zone,
    target=route53.RecordTarget.from_alias(targets.ElasticBeanstalkEnvironmentEndpointTarget(ebs_environment_url))
)
```

See the documentation of `@aws-cdk/aws-route53` for more information.
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

from .. import IConstruct as _IConstruct_5a0f9c5e
from ..aws_apigateway import (
    IDomainName as _IDomainName_2f71106c, RestApiBase as _RestApiBase_8be2daa9
)
from ..aws_cloudfront import IDistribution as _IDistribution_685deca5
from ..aws_cognito import UserPoolDomain as _UserPoolDomain_18478017
from ..aws_ec2 import IInterfaceVpcEndpoint as _IInterfaceVpcEndpoint_6081623d
from ..aws_elasticloadbalancing import LoadBalancer as _LoadBalancer_a7de240f
from ..aws_elasticloadbalancingv2 import ILoadBalancerV2 as _ILoadBalancerV2_f1c75d72
from ..aws_globalaccelerator import IAccelerator as _IAccelerator_8b90cb82
from ..aws_route53 import (
    AliasRecordTargetConfig as _AliasRecordTargetConfig_5788d785,
    IAliasRecordTarget as _IAliasRecordTarget_f7c401c2,
    IHostedZone as _IHostedZone_78d5a9c9,
    IRecordSet as _IRecordSet_133a645a,
)
from ..aws_s3 import IBucket as _IBucket_73486e29


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class ApiGatewayDomain(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.ApiGatewayDomain",
):
    '''(experimental) Defines an API Gateway domain name as the alias target.

    Use the ``ApiGateway`` class if you wish to map the alias to an REST API with a
    domain name defined through the ``RestApiProps.domainName`` prop.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # hosted_zone_for_example_com: Any
        # domain_name: apigateway.DomainName
        
        import monocdk as route53
        import monocdk as targets
        
        
        route53.ARecord(self, "CustomDomainAliasRecord",
            zone=hosted_zone_for_example_com,
            target=route53.RecordTarget.from_alias(targets.ApiGatewayDomain(domain_name))
        )
    '''

    def __init__(self, domain_name: _IDomainName_2f71106c) -> None:
        '''
        :param domain_name: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [domain_name])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class ApiGatewayv2DomainProperties(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.ApiGatewayv2DomainProperties",
):
    '''(experimental) Defines an API Gateway V2 domain name as the alias target.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as apigwv2
        
        # zone: route53.HostedZone
        # domain_name: apigwv2.DomainName
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.ApiGatewayv2DomainProperties(domain_name.regional_domain_name, domain_name.regional_hosted_zone_id))
        )
    '''

    def __init__(
        self,
        regional_domain_name: builtins.str,
        regional_hosted_zone_id: builtins.str,
    ) -> None:
        '''
        :param regional_domain_name: the domain name associated with the regional endpoint for this custom domain name.
        :param regional_hosted_zone_id: the region-specific Amazon Route 53 Hosted Zone ID of the regional endpoint.

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [regional_domain_name, regional_hosted_zone_id])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class BucketWebsiteTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.BucketWebsiteTarget",
):
    '''(experimental) Use a S3 as an alias record target.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as s3
        
        
        record_name = "www"
        domain_name = "example.com"
        
        bucket_website = s3.Bucket(self, "BucketWebsite",
            bucket_name=[record_name, domain_name].join("."),  # www.example.com
            public_read_access=True,
            website_index_document="index.html"
        )
        
        zone = route53.HostedZone.from_lookup(self, "Zone", domain_name=domain_name) # example.com
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            record_name=record_name,  # www
            target=route53.RecordTarget.from_alias(targets.BucketWebsiteTarget(bucket_website))
        )
    '''

    def __init__(self, bucket: _IBucket_73486e29) -> None:
        '''
        :param bucket: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [bucket])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class ClassicLoadBalancerTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.ClassicLoadBalancerTarget",
):
    '''(experimental) Use a classic ELB as an alias record target.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as elb
        
        # zone: route53.HostedZone
        # lb: elb.LoadBalancer
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.ClassicLoadBalancerTarget(lb))
        )
    '''

    def __init__(self, load_balancer: _LoadBalancer_a7de240f) -> None:
        '''
        :param load_balancer: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [load_balancer])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class CloudFrontTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.CloudFrontTarget",
):
    '''(experimental) Use a CloudFront Distribution as an alias record target.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as cloudfront
        
        # my_zone: route53.HostedZone
        # distribution: cloudfront.CloudFrontWebDistribution
        
        route53.AaaaRecord(self, "Alias",
            zone=my_zone,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(distribution))
        )
    '''

    def __init__(self, distribution: _IDistribution_685deca5) -> None:
        '''
        :param distribution: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [distribution])

    @jsii.member(jsii_name="getHostedZoneId") # type: ignore[misc]
    @builtins.classmethod
    def get_hosted_zone_id(cls, scope: _IConstruct_5a0f9c5e) -> builtins.str:
        '''(experimental) Get the hosted zone id for the current scope.

        :param scope: - scope in which this resource is defined.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sinvoke(cls, "getHostedZoneId", [scope]))

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CLOUDFRONT_ZONE_ID")
    def CLOUDFRONT_ZONE_ID(cls) -> builtins.str:
        '''(experimental) The hosted zone Id if using an alias record in Route53.

        This value never changes.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "CLOUDFRONT_ZONE_ID"))


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class ElasticBeanstalkEnvironmentEndpointTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.ElasticBeanstalkEnvironmentEndpointTarget",
):
    '''(experimental) Use an Elastic Beanstalk environment URL as an alias record target. E.g. mysampleenvironment.xyz.us-east-1.elasticbeanstalk.com.

    Only supports Elastic Beanstalk environments created after 2016 that have a regional endpoint.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # zone: route53.HostedZone
        # ebs_environment_url: str
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.ElasticBeanstalkEnvironmentEndpointTarget(ebs_environment_url))
        )
    '''

    def __init__(self, environment_endpoint: builtins.str) -> None:
        '''
        :param environment_endpoint: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [environment_endpoint])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class GlobalAcceleratorDomainTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.GlobalAcceleratorDomainTarget",
):
    '''(experimental) Use a Global Accelerator domain name as an alias record target.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_route53_targets as route53_targets
        
        global_accelerator_domain_target = route53_targets.GlobalAcceleratorDomainTarget("acceleratorDomainName")
    '''

    def __init__(self, accelerator_domain_name: builtins.str) -> None:
        '''(experimental) Create an Alias Target for a Global Accelerator domain name.

        :param accelerator_domain_name: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [accelerator_domain_name])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GLOBAL_ACCELERATOR_ZONE_ID")
    def GLOBAL_ACCELERATOR_ZONE_ID(cls) -> builtins.str:
        '''(experimental) The hosted zone Id if using an alias record in Route53.

        This value never changes.
        Ref: https://docs.aws.amazon.com/general/latest/gr/global_accelerator.html

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "GLOBAL_ACCELERATOR_ZONE_ID"))


class GlobalAcceleratorTarget(
    GlobalAcceleratorDomainTarget,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.GlobalAcceleratorTarget",
):
    '''(experimental) Use a Global Accelerator instance domain name as an alias record target.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as globalaccelerator
        
        # zone: route53.HostedZone
        # accelerator: globalaccelerator.Accelerator
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.GlobalAcceleratorTarget(accelerator))
        )
    '''

    def __init__(self, accelerator: _IAccelerator_8b90cb82) -> None:
        '''(experimental) Create an Alias Target for a Global Accelerator instance.

        :param accelerator: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [accelerator])


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class InterfaceVpcEndpointTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.InterfaceVpcEndpointTarget",
):
    '''(experimental) Set an InterfaceVpcEndpoint as a target for an ARecord.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as ec2
        
        # zone: route53.HostedZone
        # interface_vpc_endpoint: ec2.InterfaceVpcEndpoint
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.InterfaceVpcEndpointTarget(interface_vpc_endpoint))
        )
    '''

    def __init__(self, vpc_endpoint: _IInterfaceVpcEndpoint_6081623d) -> None:
        '''
        :param vpc_endpoint: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [vpc_endpoint])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class LoadBalancerTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.LoadBalancerTarget",
):
    '''(experimental) Use an ELBv2 as an alias record target.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as elbv2
        
        # zone: route53.HostedZone
        # lb: elbv2.ApplicationLoadBalancer
        
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(lb))
        )
    '''

    def __init__(self, load_balancer: _ILoadBalancerV2_f1c75d72) -> None:
        '''
        :param load_balancer: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [load_balancer])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class Route53RecordTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.Route53RecordTarget",
):
    '''(experimental) Use another Route 53 record as an alias record target.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # zone: route53.HostedZone
        # record: route53.ARecord
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.Route53RecordTarget(record))
        )
    '''

    def __init__(self, record: _IRecordSet_133a645a) -> None:
        '''
        :param record: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [record])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, zone]))


@jsii.implements(_IAliasRecordTarget_f7c401c2)
class UserPoolDomainTarget(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.UserPoolDomainTarget",
):
    '''(experimental) Use a user pool domain as an alias record target.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as cognito
        
        # zone: route53.HostedZone
        # domain: cognito.UserPoolDomain
        
        route53.ARecord(self, "AliasRecord",
            zone=zone,
            target=route53.RecordTarget.from_alias(targets.UserPoolDomainTarget(domain))
        )
    '''

    def __init__(self, domain: _UserPoolDomain_18478017) -> None:
        '''
        :param domain: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [domain])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _record: _IRecordSet_133a645a,
        _zone: typing.Optional[_IHostedZone_78d5a9c9] = None,
    ) -> _AliasRecordTargetConfig_5788d785:
        '''(experimental) Return hosted zone ID and DNS name, usable for Route53 alias targets.

        :param _record: -
        :param _zone: -

        :stability: experimental
        '''
        return typing.cast(_AliasRecordTargetConfig_5788d785, jsii.invoke(self, "bind", [_record, _zone]))


class ApiGateway(
    ApiGatewayDomain,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_route53_targets.ApiGateway",
):
    '''(experimental) Defines an API Gateway REST API as the alias target. Requires that the domain name will be defined through ``RestApiProps.domainName``.

    You can direct the alias to any ``apigateway.DomainName`` resource through the
    ``ApiGatewayDomain`` class.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        import monocdk as route53
        import monocdk as targets
        
        # api: apigateway.RestApi
        # hosted_zone_for_example_com: Any
        
        
        route53.ARecord(self, "CustomDomainAliasRecord",
            zone=hosted_zone_for_example_com,
            target=route53.RecordTarget.from_alias(targets.ApiGateway(api))
        )
    '''

    def __init__(self, api: _RestApiBase_8be2daa9) -> None:
        '''
        :param api: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [api])


__all__ = [
    "ApiGateway",
    "ApiGatewayDomain",
    "ApiGatewayv2DomainProperties",
    "BucketWebsiteTarget",
    "ClassicLoadBalancerTarget",
    "CloudFrontTarget",
    "ElasticBeanstalkEnvironmentEndpointTarget",
    "GlobalAcceleratorDomainTarget",
    "GlobalAcceleratorTarget",
    "InterfaceVpcEndpointTarget",
    "LoadBalancerTarget",
    "Route53RecordTarget",
    "UserPoolDomainTarget",
]

publication.publish()
