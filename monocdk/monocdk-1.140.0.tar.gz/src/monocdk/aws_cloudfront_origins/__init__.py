'''
# CloudFront Origins for the CDK CloudFront Library

This library contains convenience methods for defining origins for a CloudFront distribution. You can use this library to create origins from
S3 buckets, Elastic Load Balancing v2 load balancers, or any other domain name.

## S3 Bucket

An S3 bucket can be added as an origin. If the bucket is configured as a website endpoint, the distribution can use S3 redirects and S3 custom error
documents.

```python
my_bucket = s3.Bucket(self, "myBucket")
cloudfront.Distribution(self, "myDist",
    default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(origin=origins.S3Origin(my_bucket))
)
```

The above will treat the bucket differently based on if `IBucket.isWebsite` is set or not. If the bucket is configured as a website, the bucket is
treated as an HTTP origin, and the built-in S3 redirects and error pages can be used. Otherwise, the bucket is handled as a bucket origin and
CloudFront's redirect and error handling will be used. In the latter case, the Origin will create an origin access identity and grant it access to the
underlying bucket. This can be used in conjunction with a bucket that is not public to require that your users access your content using CloudFront
URLs and not S3 URLs directly. Alternatively, a custom origin access identity can be passed to the S3 origin in the properties.

### Adding Custom Headers

You can configure CloudFront to add custom headers to the requests that it sends to your origin. These custom headers enable you to send and gather information from your origin that you don’t get with typical viewer requests. These headers can even be customized for each origin. CloudFront supports custom headers for both for custom and Amazon S3 origins.

```python
my_bucket = s3.Bucket(self, "myBucket")
cloudfront.Distribution(self, "myDist",
    default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(origin=origins.S3Origin(my_bucket,
        custom_headers={
            "Foo": "bar"
        }
    ))
)
```

## ELBv2 Load Balancer

An Elastic Load Balancing (ELB) v2 load balancer may be used as an origin. In order for a load balancer to serve as an origin, it must be publicly
accessible (`internetFacing` is true). Both Application and Network load balancers are supported.

```python
import monocdk as ec2
import monocdk as elbv2

# vpc: ec2.Vpc

# Create an application load balancer in a VPC. 'internetFacing' must be 'true'
# for CloudFront to access the load balancer and use it as an origin.
lb = elbv2.ApplicationLoadBalancer(self, "LB",
    vpc=vpc,
    internet_facing=True
)
cloudfront.Distribution(self, "myDist",
    default_behavior=ec2.aws_cloudfront.BehaviorOptions(origin=origins.LoadBalancerV2Origin(lb))
)
```

The origin can also be customized to respond on different ports, have different connection properties, etc.

```python
import monocdk as elbv2

# load_balancer: elbv2.ApplicationLoadBalancer

origin = origins.LoadBalancerV2Origin(load_balancer,
    connection_attempts=3,
    connection_timeout=Duration.seconds(5),
    protocol_policy=cloudfront.OriginProtocolPolicy.MATCH_VIEWER
)
```

## From an HTTP endpoint

Origins can also be created from any other HTTP endpoint, given the domain name, and optionally, other origin properties.

```python
cloudfront.Distribution(self, "myDist",
    default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(origin=origins.HttpOrigin("www.example.com"))
)
```

See the documentation of `@aws-cdk/aws-cloudfront` for more information.

## Failover Origins (Origin Groups)

You can set up CloudFront with origin failover for scenarios that require high availability.
To get started, you create an origin group with two origins: a primary and a secondary.
If the primary origin is unavailable, or returns specific HTTP response status codes that indicate a failure,
CloudFront automatically switches to the secondary origin.
You achieve that behavior in the CDK using the `OriginGroup` class:

```python
my_bucket = s3.Bucket(self, "myBucket")
cloudfront.Distribution(self, "myDist",
    default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(
        origin=origins.OriginGroup(
            primary_origin=origins.S3Origin(my_bucket),
            fallback_origin=origins.HttpOrigin("www.example.com"),
            # optional, defaults to: 500, 502, 503 and 504
            fallback_status_codes=[404]
        )
    )
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

from .._jsii import *

from .. import Construct as _Construct_e78e779f, Duration as _Duration_070aa057
from ..aws_cloudfront import (
    CfnDistribution as _CfnDistribution_df481f85,
    IOrigin as _IOrigin_a25d8672,
    IOriginAccessIdentity as _IOriginAccessIdentity_7e00f041,
    OriginBase as _OriginBase_41a5d89d,
    OriginBindConfig as _OriginBindConfig_bdbbbd6e,
    OriginBindOptions as _OriginBindOptions_15a2501d,
    OriginProps as _OriginProps_d402b2f3,
    OriginProtocolPolicy as _OriginProtocolPolicy_b165f906,
    OriginSslPolicy as _OriginSslPolicy_36f169b4,
)
from ..aws_elasticloadbalancingv2 import ILoadBalancerV2 as _ILoadBalancerV2_f1c75d72
from ..aws_s3 import IBucket as _IBucket_73486e29


class HttpOrigin(
    _OriginBase_41a5d89d,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloudfront_origins.HttpOrigin",
):
    '''(experimental) An Origin for an HTTP server or S3 bucket configured for website hosting.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        my_bucket = s3.Bucket(self, "myBucket")
        cloudfront.Distribution(self, "myDist",
            default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(
                origin=origins.OriginGroup(
                    primary_origin=origins.S3Origin(my_bucket),
                    fallback_origin=origins.HttpOrigin("www.example.com"),
                    # optional, defaults to: 500, 502, 503 and 504
                    fallback_status_codes=[404]
                )
            )
        )
    '''

    def __init__(
        self,
        domain_name: builtins.str,
        *,
        http_port: typing.Optional[jsii.Number] = None,
        https_port: typing.Optional[jsii.Number] = None,
        keepalive_timeout: typing.Optional[_Duration_070aa057] = None,
        origin_ssl_protocols: typing.Optional[typing.Sequence[_OriginSslPolicy_36f169b4]] = None,
        protocol_policy: typing.Optional[_OriginProtocolPolicy_b165f906] = None,
        read_timeout: typing.Optional[_Duration_070aa057] = None,
        connection_attempts: typing.Optional[jsii.Number] = None,
        connection_timeout: typing.Optional[_Duration_070aa057] = None,
        custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        origin_path: typing.Optional[builtins.str] = None,
        origin_shield_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param domain_name: -
        :param http_port: (experimental) The HTTP port that CloudFront uses to connect to the origin. Default: 80
        :param https_port: (experimental) The HTTPS port that CloudFront uses to connect to the origin. Default: 443
        :param keepalive_timeout: (experimental) Specifies how long, in seconds, CloudFront persists its connection to the origin. The valid range is from 1 to 60 seconds, inclusive. Default: Duration.seconds(5)
        :param origin_ssl_protocols: (experimental) The SSL versions to use when interacting with the origin. Default: OriginSslPolicy.TLS_V1_2
        :param protocol_policy: (experimental) Specifies the protocol (HTTP or HTTPS) that CloudFront uses to connect to the origin. Default: OriginProtocolPolicy.HTTPS_ONLY
        :param read_timeout: (experimental) Specifies how long, in seconds, CloudFront waits for a response from the origin, also known as the origin response timeout. The valid range is from 1 to 60 seconds, inclusive. Default: Duration.seconds(30)
        :param connection_attempts: (experimental) The number of times that CloudFront attempts to connect to the origin; valid values are 1, 2, or 3 attempts. Default: 3
        :param connection_timeout: (experimental) The number of seconds that CloudFront waits when trying to establish a connection to the origin. Valid values are 1-10 seconds, inclusive. Default: Duration.seconds(10)
        :param custom_headers: (experimental) A list of HTTP header names and values that CloudFront adds to requests it sends to the origin. Default: {}
        :param origin_path: (experimental) An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin. Must begin, but not end, with '/' (e.g., '/production/images'). Default: '/'
        :param origin_shield_region: (experimental) When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance. Default: - origin shield not enabled

        :stability: experimental
        '''
        props = HttpOriginProps(
            http_port=http_port,
            https_port=https_port,
            keepalive_timeout=keepalive_timeout,
            origin_ssl_protocols=origin_ssl_protocols,
            protocol_policy=protocol_policy,
            read_timeout=read_timeout,
            connection_attempts=connection_attempts,
            connection_timeout=connection_timeout,
            custom_headers=custom_headers,
            origin_path=origin_path,
            origin_shield_region=origin_shield_region,
        )

        jsii.create(self.__class__, self, [domain_name, props])

    @jsii.member(jsii_name="renderCustomOriginConfig")
    def _render_custom_origin_config(
        self,
    ) -> typing.Optional[_CfnDistribution_df481f85.CustomOriginConfigProperty]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_CfnDistribution_df481f85.CustomOriginConfigProperty], jsii.invoke(self, "renderCustomOriginConfig", []))


@jsii.data_type(
    jsii_type="monocdk.aws_cloudfront_origins.HttpOriginProps",
    jsii_struct_bases=[_OriginProps_d402b2f3],
    name_mapping={
        "connection_attempts": "connectionAttempts",
        "connection_timeout": "connectionTimeout",
        "custom_headers": "customHeaders",
        "origin_path": "originPath",
        "origin_shield_region": "originShieldRegion",
        "http_port": "httpPort",
        "https_port": "httpsPort",
        "keepalive_timeout": "keepaliveTimeout",
        "origin_ssl_protocols": "originSslProtocols",
        "protocol_policy": "protocolPolicy",
        "read_timeout": "readTimeout",
    },
)
class HttpOriginProps(_OriginProps_d402b2f3):
    def __init__(
        self,
        *,
        connection_attempts: typing.Optional[jsii.Number] = None,
        connection_timeout: typing.Optional[_Duration_070aa057] = None,
        custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        origin_path: typing.Optional[builtins.str] = None,
        origin_shield_region: typing.Optional[builtins.str] = None,
        http_port: typing.Optional[jsii.Number] = None,
        https_port: typing.Optional[jsii.Number] = None,
        keepalive_timeout: typing.Optional[_Duration_070aa057] = None,
        origin_ssl_protocols: typing.Optional[typing.Sequence[_OriginSslPolicy_36f169b4]] = None,
        protocol_policy: typing.Optional[_OriginProtocolPolicy_b165f906] = None,
        read_timeout: typing.Optional[_Duration_070aa057] = None,
    ) -> None:
        '''(experimental) Properties for an Origin backed by an S3 website-configured bucket, load balancer, or custom HTTP server.

        :param connection_attempts: (experimental) The number of times that CloudFront attempts to connect to the origin; valid values are 1, 2, or 3 attempts. Default: 3
        :param connection_timeout: (experimental) The number of seconds that CloudFront waits when trying to establish a connection to the origin. Valid values are 1-10 seconds, inclusive. Default: Duration.seconds(10)
        :param custom_headers: (experimental) A list of HTTP header names and values that CloudFront adds to requests it sends to the origin. Default: {}
        :param origin_path: (experimental) An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin. Must begin, but not end, with '/' (e.g., '/production/images'). Default: '/'
        :param origin_shield_region: (experimental) When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance. Default: - origin shield not enabled
        :param http_port: (experimental) The HTTP port that CloudFront uses to connect to the origin. Default: 80
        :param https_port: (experimental) The HTTPS port that CloudFront uses to connect to the origin. Default: 443
        :param keepalive_timeout: (experimental) Specifies how long, in seconds, CloudFront persists its connection to the origin. The valid range is from 1 to 60 seconds, inclusive. Default: Duration.seconds(5)
        :param origin_ssl_protocols: (experimental) The SSL versions to use when interacting with the origin. Default: OriginSslPolicy.TLS_V1_2
        :param protocol_policy: (experimental) Specifies the protocol (HTTP or HTTPS) that CloudFront uses to connect to the origin. Default: OriginProtocolPolicy.HTTPS_ONLY
        :param read_timeout: (experimental) Specifies how long, in seconds, CloudFront waits for a response from the origin, also known as the origin response timeout. The valid range is from 1 to 60 seconds, inclusive. Default: Duration.seconds(30)

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import monocdk as monocdk
            from monocdk import aws_cloudfront as cloudfront
            from monocdk import aws_cloudfront_origins as cloudfront_origins
            
            # duration: monocdk.Duration
            
            http_origin_props = cloudfront_origins.HttpOriginProps(
                connection_attempts=123,
                connection_timeout=duration,
                custom_headers={
                    "custom_headers_key": "customHeaders"
                },
                http_port=123,
                https_port=123,
                keepalive_timeout=duration,
                origin_path="originPath",
                origin_shield_region="originShieldRegion",
                origin_ssl_protocols=[cloudfront.OriginSslPolicy.SSL_V3],
                protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                read_timeout=duration
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if connection_attempts is not None:
            self._values["connection_attempts"] = connection_attempts
        if connection_timeout is not None:
            self._values["connection_timeout"] = connection_timeout
        if custom_headers is not None:
            self._values["custom_headers"] = custom_headers
        if origin_path is not None:
            self._values["origin_path"] = origin_path
        if origin_shield_region is not None:
            self._values["origin_shield_region"] = origin_shield_region
        if http_port is not None:
            self._values["http_port"] = http_port
        if https_port is not None:
            self._values["https_port"] = https_port
        if keepalive_timeout is not None:
            self._values["keepalive_timeout"] = keepalive_timeout
        if origin_ssl_protocols is not None:
            self._values["origin_ssl_protocols"] = origin_ssl_protocols
        if protocol_policy is not None:
            self._values["protocol_policy"] = protocol_policy
        if read_timeout is not None:
            self._values["read_timeout"] = read_timeout

    @builtins.property
    def connection_attempts(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of times that CloudFront attempts to connect to the origin;

        valid values are 1, 2, or 3 attempts.

        :default: 3

        :stability: experimental
        '''
        result = self._values.get("connection_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connection_timeout(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) The number of seconds that CloudFront waits when trying to establish a connection to the origin.

        Valid values are 1-10 seconds, inclusive.

        :default: Duration.seconds(10)

        :stability: experimental
        '''
        result = self._values.get("connection_timeout")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def custom_headers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) A list of HTTP header names and values that CloudFront adds to requests it sends to the origin.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("custom_headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def origin_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin.

        Must begin, but not end, with '/' (e.g., '/production/images').

        :default: '/'

        :stability: experimental
        '''
        result = self._values.get("origin_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_shield_region(self) -> typing.Optional[builtins.str]:
        '''(experimental) When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance.

        :default: - origin shield not enabled

        :see: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html
        :stability: experimental
        '''
        result = self._values.get("origin_shield_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The HTTP port that CloudFront uses to connect to the origin.

        :default: 80

        :stability: experimental
        '''
        result = self._values.get("http_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def https_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The HTTPS port that CloudFront uses to connect to the origin.

        :default: 443

        :stability: experimental
        '''
        result = self._values.get("https_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def keepalive_timeout(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Specifies how long, in seconds, CloudFront persists its connection to the origin.

        The valid range is from 1 to 60 seconds, inclusive.

        :default: Duration.seconds(5)

        :stability: experimental
        '''
        result = self._values.get("keepalive_timeout")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def origin_ssl_protocols(
        self,
    ) -> typing.Optional[typing.List[_OriginSslPolicy_36f169b4]]:
        '''(experimental) The SSL versions to use when interacting with the origin.

        :default: OriginSslPolicy.TLS_V1_2

        :stability: experimental
        '''
        result = self._values.get("origin_ssl_protocols")
        return typing.cast(typing.Optional[typing.List[_OriginSslPolicy_36f169b4]], result)

    @builtins.property
    def protocol_policy(self) -> typing.Optional[_OriginProtocolPolicy_b165f906]:
        '''(experimental) Specifies the protocol (HTTP or HTTPS) that CloudFront uses to connect to the origin.

        :default: OriginProtocolPolicy.HTTPS_ONLY

        :stability: experimental
        '''
        result = self._values.get("protocol_policy")
        return typing.cast(typing.Optional[_OriginProtocolPolicy_b165f906], result)

    @builtins.property
    def read_timeout(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Specifies how long, in seconds, CloudFront waits for a response from the origin, also known as the origin response timeout.

        The valid range is from 1 to 60 seconds, inclusive.

        :default: Duration.seconds(30)

        :stability: experimental
        '''
        result = self._values.get("read_timeout")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpOriginProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadBalancerV2Origin(
    HttpOrigin,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloudfront_origins.LoadBalancerV2Origin",
):
    '''(experimental) An Origin for a v2 load balancer.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Creates a distribution from an ELBv2 load balancer
        # vpc: ec2.Vpc
        
        # Create an application load balancer in a VPC. 'internetFacing' must be 'true'
        # for CloudFront to access the load balancer and use it as an origin.
        lb = elbv2.ApplicationLoadBalancer(self, "LB",
            vpc=vpc,
            internet_facing=True
        )
        cloudfront.Distribution(self, "myDist",
            default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(origin=origins.LoadBalancerV2Origin(lb))
        )
    '''

    def __init__(
        self,
        load_balancer: _ILoadBalancerV2_f1c75d72,
        *,
        http_port: typing.Optional[jsii.Number] = None,
        https_port: typing.Optional[jsii.Number] = None,
        keepalive_timeout: typing.Optional[_Duration_070aa057] = None,
        origin_ssl_protocols: typing.Optional[typing.Sequence[_OriginSslPolicy_36f169b4]] = None,
        protocol_policy: typing.Optional[_OriginProtocolPolicy_b165f906] = None,
        read_timeout: typing.Optional[_Duration_070aa057] = None,
        connection_attempts: typing.Optional[jsii.Number] = None,
        connection_timeout: typing.Optional[_Duration_070aa057] = None,
        custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        origin_path: typing.Optional[builtins.str] = None,
        origin_shield_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param load_balancer: -
        :param http_port: (experimental) The HTTP port that CloudFront uses to connect to the origin. Default: 80
        :param https_port: (experimental) The HTTPS port that CloudFront uses to connect to the origin. Default: 443
        :param keepalive_timeout: (experimental) Specifies how long, in seconds, CloudFront persists its connection to the origin. The valid range is from 1 to 60 seconds, inclusive. Default: Duration.seconds(5)
        :param origin_ssl_protocols: (experimental) The SSL versions to use when interacting with the origin. Default: OriginSslPolicy.TLS_V1_2
        :param protocol_policy: (experimental) Specifies the protocol (HTTP or HTTPS) that CloudFront uses to connect to the origin. Default: OriginProtocolPolicy.HTTPS_ONLY
        :param read_timeout: (experimental) Specifies how long, in seconds, CloudFront waits for a response from the origin, also known as the origin response timeout. The valid range is from 1 to 60 seconds, inclusive. Default: Duration.seconds(30)
        :param connection_attempts: (experimental) The number of times that CloudFront attempts to connect to the origin; valid values are 1, 2, or 3 attempts. Default: 3
        :param connection_timeout: (experimental) The number of seconds that CloudFront waits when trying to establish a connection to the origin. Valid values are 1-10 seconds, inclusive. Default: Duration.seconds(10)
        :param custom_headers: (experimental) A list of HTTP header names and values that CloudFront adds to requests it sends to the origin. Default: {}
        :param origin_path: (experimental) An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin. Must begin, but not end, with '/' (e.g., '/production/images'). Default: '/'
        :param origin_shield_region: (experimental) When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance. Default: - origin shield not enabled

        :stability: experimental
        '''
        props = LoadBalancerV2OriginProps(
            http_port=http_port,
            https_port=https_port,
            keepalive_timeout=keepalive_timeout,
            origin_ssl_protocols=origin_ssl_protocols,
            protocol_policy=protocol_policy,
            read_timeout=read_timeout,
            connection_attempts=connection_attempts,
            connection_timeout=connection_timeout,
            custom_headers=custom_headers,
            origin_path=origin_path,
            origin_shield_region=origin_shield_region,
        )

        jsii.create(self.__class__, self, [load_balancer, props])


@jsii.data_type(
    jsii_type="monocdk.aws_cloudfront_origins.LoadBalancerV2OriginProps",
    jsii_struct_bases=[HttpOriginProps],
    name_mapping={
        "connection_attempts": "connectionAttempts",
        "connection_timeout": "connectionTimeout",
        "custom_headers": "customHeaders",
        "origin_path": "originPath",
        "origin_shield_region": "originShieldRegion",
        "http_port": "httpPort",
        "https_port": "httpsPort",
        "keepalive_timeout": "keepaliveTimeout",
        "origin_ssl_protocols": "originSslProtocols",
        "protocol_policy": "protocolPolicy",
        "read_timeout": "readTimeout",
    },
)
class LoadBalancerV2OriginProps(HttpOriginProps):
    def __init__(
        self,
        *,
        connection_attempts: typing.Optional[jsii.Number] = None,
        connection_timeout: typing.Optional[_Duration_070aa057] = None,
        custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        origin_path: typing.Optional[builtins.str] = None,
        origin_shield_region: typing.Optional[builtins.str] = None,
        http_port: typing.Optional[jsii.Number] = None,
        https_port: typing.Optional[jsii.Number] = None,
        keepalive_timeout: typing.Optional[_Duration_070aa057] = None,
        origin_ssl_protocols: typing.Optional[typing.Sequence[_OriginSslPolicy_36f169b4]] = None,
        protocol_policy: typing.Optional[_OriginProtocolPolicy_b165f906] = None,
        read_timeout: typing.Optional[_Duration_070aa057] = None,
    ) -> None:
        '''(experimental) Properties for an Origin backed by a v2 load balancer.

        :param connection_attempts: (experimental) The number of times that CloudFront attempts to connect to the origin; valid values are 1, 2, or 3 attempts. Default: 3
        :param connection_timeout: (experimental) The number of seconds that CloudFront waits when trying to establish a connection to the origin. Valid values are 1-10 seconds, inclusive. Default: Duration.seconds(10)
        :param custom_headers: (experimental) A list of HTTP header names and values that CloudFront adds to requests it sends to the origin. Default: {}
        :param origin_path: (experimental) An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin. Must begin, but not end, with '/' (e.g., '/production/images'). Default: '/'
        :param origin_shield_region: (experimental) When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance. Default: - origin shield not enabled
        :param http_port: (experimental) The HTTP port that CloudFront uses to connect to the origin. Default: 80
        :param https_port: (experimental) The HTTPS port that CloudFront uses to connect to the origin. Default: 443
        :param keepalive_timeout: (experimental) Specifies how long, in seconds, CloudFront persists its connection to the origin. The valid range is from 1 to 60 seconds, inclusive. Default: Duration.seconds(5)
        :param origin_ssl_protocols: (experimental) The SSL versions to use when interacting with the origin. Default: OriginSslPolicy.TLS_V1_2
        :param protocol_policy: (experimental) Specifies the protocol (HTTP or HTTPS) that CloudFront uses to connect to the origin. Default: OriginProtocolPolicy.HTTPS_ONLY
        :param read_timeout: (experimental) Specifies how long, in seconds, CloudFront waits for a response from the origin, also known as the origin response timeout. The valid range is from 1 to 60 seconds, inclusive. Default: Duration.seconds(30)

        :stability: experimental
        :exampleMetadata: infused

        Example::

            import monocdk as elbv2
            
            # load_balancer: elbv2.ApplicationLoadBalancer
            
            origin = origins.LoadBalancerV2Origin(load_balancer,
                connection_attempts=3,
                connection_timeout=Duration.seconds(5),
                protocol_policy=cloudfront.OriginProtocolPolicy.MATCH_VIEWER
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if connection_attempts is not None:
            self._values["connection_attempts"] = connection_attempts
        if connection_timeout is not None:
            self._values["connection_timeout"] = connection_timeout
        if custom_headers is not None:
            self._values["custom_headers"] = custom_headers
        if origin_path is not None:
            self._values["origin_path"] = origin_path
        if origin_shield_region is not None:
            self._values["origin_shield_region"] = origin_shield_region
        if http_port is not None:
            self._values["http_port"] = http_port
        if https_port is not None:
            self._values["https_port"] = https_port
        if keepalive_timeout is not None:
            self._values["keepalive_timeout"] = keepalive_timeout
        if origin_ssl_protocols is not None:
            self._values["origin_ssl_protocols"] = origin_ssl_protocols
        if protocol_policy is not None:
            self._values["protocol_policy"] = protocol_policy
        if read_timeout is not None:
            self._values["read_timeout"] = read_timeout

    @builtins.property
    def connection_attempts(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of times that CloudFront attempts to connect to the origin;

        valid values are 1, 2, or 3 attempts.

        :default: 3

        :stability: experimental
        '''
        result = self._values.get("connection_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connection_timeout(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) The number of seconds that CloudFront waits when trying to establish a connection to the origin.

        Valid values are 1-10 seconds, inclusive.

        :default: Duration.seconds(10)

        :stability: experimental
        '''
        result = self._values.get("connection_timeout")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def custom_headers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) A list of HTTP header names and values that CloudFront adds to requests it sends to the origin.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("custom_headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def origin_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin.

        Must begin, but not end, with '/' (e.g., '/production/images').

        :default: '/'

        :stability: experimental
        '''
        result = self._values.get("origin_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_shield_region(self) -> typing.Optional[builtins.str]:
        '''(experimental) When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance.

        :default: - origin shield not enabled

        :see: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html
        :stability: experimental
        '''
        result = self._values.get("origin_shield_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The HTTP port that CloudFront uses to connect to the origin.

        :default: 80

        :stability: experimental
        '''
        result = self._values.get("http_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def https_port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The HTTPS port that CloudFront uses to connect to the origin.

        :default: 443

        :stability: experimental
        '''
        result = self._values.get("https_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def keepalive_timeout(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Specifies how long, in seconds, CloudFront persists its connection to the origin.

        The valid range is from 1 to 60 seconds, inclusive.

        :default: Duration.seconds(5)

        :stability: experimental
        '''
        result = self._values.get("keepalive_timeout")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def origin_ssl_protocols(
        self,
    ) -> typing.Optional[typing.List[_OriginSslPolicy_36f169b4]]:
        '''(experimental) The SSL versions to use when interacting with the origin.

        :default: OriginSslPolicy.TLS_V1_2

        :stability: experimental
        '''
        result = self._values.get("origin_ssl_protocols")
        return typing.cast(typing.Optional[typing.List[_OriginSslPolicy_36f169b4]], result)

    @builtins.property
    def protocol_policy(self) -> typing.Optional[_OriginProtocolPolicy_b165f906]:
        '''(experimental) Specifies the protocol (HTTP or HTTPS) that CloudFront uses to connect to the origin.

        :default: OriginProtocolPolicy.HTTPS_ONLY

        :stability: experimental
        '''
        result = self._values.get("protocol_policy")
        return typing.cast(typing.Optional[_OriginProtocolPolicy_b165f906], result)

    @builtins.property
    def read_timeout(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) Specifies how long, in seconds, CloudFront waits for a response from the origin, also known as the origin response timeout.

        The valid range is from 1 to 60 seconds, inclusive.

        :default: Duration.seconds(30)

        :stability: experimental
        '''
        result = self._values.get("read_timeout")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadBalancerV2OriginProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IOrigin_a25d8672)
class OriginGroup(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloudfront_origins.OriginGroup",
):
    '''(experimental) An Origin that represents a group.

    Consists of a primary Origin,
    and a fallback Origin called when the primary returns one of the provided HTTP status codes.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        my_bucket = s3.Bucket(self, "myBucket")
        cloudfront.Distribution(self, "myDist",
            default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(
                origin=origins.OriginGroup(
                    primary_origin=origins.S3Origin(my_bucket),
                    fallback_origin=origins.HttpOrigin("www.example.com"),
                    # optional, defaults to: 500, 502, 503 and 504
                    fallback_status_codes=[404]
                )
            )
        )
    '''

    def __init__(
        self,
        *,
        fallback_origin: _IOrigin_a25d8672,
        primary_origin: _IOrigin_a25d8672,
        fallback_status_codes: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''
        :param fallback_origin: (experimental) The fallback origin that should serve requests when the primary fails.
        :param primary_origin: (experimental) The primary origin that should serve requests for this group.
        :param fallback_status_codes: (experimental) The list of HTTP status codes that, when returned from the primary origin, would cause querying the fallback origin. Default: - 500, 502, 503 and 504

        :stability: experimental
        '''
        props = OriginGroupProps(
            fallback_origin=fallback_origin,
            primary_origin=primary_origin,
            fallback_status_codes=fallback_status_codes,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _Construct_e78e779f,
        *,
        origin_id: builtins.str,
    ) -> _OriginBindConfig_bdbbbd6e:
        '''(experimental) The method called when a given Origin is added (for the first time) to a Distribution.

        :param scope: -
        :param origin_id: (experimental) The identifier of this Origin, as assigned by the Distribution this Origin has been used added to.

        :stability: experimental
        '''
        options = _OriginBindOptions_15a2501d(origin_id=origin_id)

        return typing.cast(_OriginBindConfig_bdbbbd6e, jsii.invoke(self, "bind", [scope, options]))


@jsii.data_type(
    jsii_type="monocdk.aws_cloudfront_origins.OriginGroupProps",
    jsii_struct_bases=[],
    name_mapping={
        "fallback_origin": "fallbackOrigin",
        "primary_origin": "primaryOrigin",
        "fallback_status_codes": "fallbackStatusCodes",
    },
)
class OriginGroupProps:
    def __init__(
        self,
        *,
        fallback_origin: _IOrigin_a25d8672,
        primary_origin: _IOrigin_a25d8672,
        fallback_status_codes: typing.Optional[typing.Sequence[jsii.Number]] = None,
    ) -> None:
        '''(experimental) Construction properties for {@link OriginGroup}.

        :param fallback_origin: (experimental) The fallback origin that should serve requests when the primary fails.
        :param primary_origin: (experimental) The primary origin that should serve requests for this group.
        :param fallback_status_codes: (experimental) The list of HTTP status codes that, when returned from the primary origin, would cause querying the fallback origin. Default: - 500, 502, 503 and 504

        :stability: experimental
        :exampleMetadata: infused

        Example::

            my_bucket = s3.Bucket(self, "myBucket")
            cloudfront.Distribution(self, "myDist",
                default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(
                    origin=origins.OriginGroup(
                        primary_origin=origins.S3Origin(my_bucket),
                        fallback_origin=origins.HttpOrigin("www.example.com"),
                        # optional, defaults to: 500, 502, 503 and 504
                        fallback_status_codes=[404]
                    )
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "fallback_origin": fallback_origin,
            "primary_origin": primary_origin,
        }
        if fallback_status_codes is not None:
            self._values["fallback_status_codes"] = fallback_status_codes

    @builtins.property
    def fallback_origin(self) -> _IOrigin_a25d8672:
        '''(experimental) The fallback origin that should serve requests when the primary fails.

        :stability: experimental
        '''
        result = self._values.get("fallback_origin")
        assert result is not None, "Required property 'fallback_origin' is missing"
        return typing.cast(_IOrigin_a25d8672, result)

    @builtins.property
    def primary_origin(self) -> _IOrigin_a25d8672:
        '''(experimental) The primary origin that should serve requests for this group.

        :stability: experimental
        '''
        result = self._values.get("primary_origin")
        assert result is not None, "Required property 'primary_origin' is missing"
        return typing.cast(_IOrigin_a25d8672, result)

    @builtins.property
    def fallback_status_codes(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''(experimental) The list of HTTP status codes that, when returned from the primary origin, would cause querying the fallback origin.

        :default: - 500, 502, 503 and 504

        :stability: experimental
        '''
        result = self._values.get("fallback_status_codes")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OriginGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(_IOrigin_a25d8672)
class S3Origin(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cloudfront_origins.S3Origin",
):
    '''(experimental) An Origin that is backed by an S3 bucket.

    If the bucket is configured for website hosting, this origin will be configured to use the bucket as an
    HTTP server origin and will use the bucket's configured website redirects and error handling. Otherwise,
    the origin is created as a bucket origin and will use CloudFront's redirect and error handling.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Adding an existing Lambda@Edge function created in a different stack
        # to a CloudFront distribution.
        # s3_bucket: s3.Bucket
        
        function_version = lambda_.Version.from_version_arn(self, "Version", "arn:aws:lambda:us-east-1:123456789012:function:functionName:1")
        
        cloudfront.Distribution(self, "distro",
            default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(
                origin=origins.S3Origin(s3_bucket),
                edge_lambdas=[cloudfront.aws_cloudfront.EdgeLambda(
                    function_version=function_version,
                    event_type=cloudfront.LambdaEdgeEventType.VIEWER_REQUEST
                )
                ]
            )
        )
    '''

    def __init__(
        self,
        bucket: _IBucket_73486e29,
        *,
        origin_access_identity: typing.Optional[_IOriginAccessIdentity_7e00f041] = None,
        connection_attempts: typing.Optional[jsii.Number] = None,
        connection_timeout: typing.Optional[_Duration_070aa057] = None,
        custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        origin_path: typing.Optional[builtins.str] = None,
        origin_shield_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: -
        :param origin_access_identity: (experimental) An optional Origin Access Identity of the origin identity cloudfront will use when calling your s3 bucket. Default: - An Origin Access Identity will be created.
        :param connection_attempts: (experimental) The number of times that CloudFront attempts to connect to the origin; valid values are 1, 2, or 3 attempts. Default: 3
        :param connection_timeout: (experimental) The number of seconds that CloudFront waits when trying to establish a connection to the origin. Valid values are 1-10 seconds, inclusive. Default: Duration.seconds(10)
        :param custom_headers: (experimental) A list of HTTP header names and values that CloudFront adds to requests it sends to the origin. Default: {}
        :param origin_path: (experimental) An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin. Must begin, but not end, with '/' (e.g., '/production/images'). Default: '/'
        :param origin_shield_region: (experimental) When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance. Default: - origin shield not enabled

        :stability: experimental
        '''
        props = S3OriginProps(
            origin_access_identity=origin_access_identity,
            connection_attempts=connection_attempts,
            connection_timeout=connection_timeout,
            custom_headers=custom_headers,
            origin_path=origin_path,
            origin_shield_region=origin_shield_region,
        )

        jsii.create(self.__class__, self, [bucket, props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: _Construct_e78e779f,
        *,
        origin_id: builtins.str,
    ) -> _OriginBindConfig_bdbbbd6e:
        '''(experimental) The method called when a given Origin is added (for the first time) to a Distribution.

        :param scope: -
        :param origin_id: (experimental) The identifier of this Origin, as assigned by the Distribution this Origin has been used added to.

        :stability: experimental
        '''
        options = _OriginBindOptions_15a2501d(origin_id=origin_id)

        return typing.cast(_OriginBindConfig_bdbbbd6e, jsii.invoke(self, "bind", [scope, options]))


@jsii.data_type(
    jsii_type="monocdk.aws_cloudfront_origins.S3OriginProps",
    jsii_struct_bases=[_OriginProps_d402b2f3],
    name_mapping={
        "connection_attempts": "connectionAttempts",
        "connection_timeout": "connectionTimeout",
        "custom_headers": "customHeaders",
        "origin_path": "originPath",
        "origin_shield_region": "originShieldRegion",
        "origin_access_identity": "originAccessIdentity",
    },
)
class S3OriginProps(_OriginProps_d402b2f3):
    def __init__(
        self,
        *,
        connection_attempts: typing.Optional[jsii.Number] = None,
        connection_timeout: typing.Optional[_Duration_070aa057] = None,
        custom_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        origin_path: typing.Optional[builtins.str] = None,
        origin_shield_region: typing.Optional[builtins.str] = None,
        origin_access_identity: typing.Optional[_IOriginAccessIdentity_7e00f041] = None,
    ) -> None:
        '''(experimental) Properties to use to customize an S3 Origin.

        :param connection_attempts: (experimental) The number of times that CloudFront attempts to connect to the origin; valid values are 1, 2, or 3 attempts. Default: 3
        :param connection_timeout: (experimental) The number of seconds that CloudFront waits when trying to establish a connection to the origin. Valid values are 1-10 seconds, inclusive. Default: Duration.seconds(10)
        :param custom_headers: (experimental) A list of HTTP header names and values that CloudFront adds to requests it sends to the origin. Default: {}
        :param origin_path: (experimental) An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin. Must begin, but not end, with '/' (e.g., '/production/images'). Default: '/'
        :param origin_shield_region: (experimental) When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance. Default: - origin shield not enabled
        :param origin_access_identity: (experimental) An optional Origin Access Identity of the origin identity cloudfront will use when calling your s3 bucket. Default: - An Origin Access Identity will be created.

        :stability: experimental
        :exampleMetadata: infused

        Example::

            my_bucket = s3.Bucket(self, "myBucket")
            cloudfront.Distribution(self, "myDist",
                default_behavior=cloudfront.aws_cloudfront.BehaviorOptions(origin=origins.S3Origin(my_bucket,
                    custom_headers={
                        "Foo": "bar"
                    }
                ))
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if connection_attempts is not None:
            self._values["connection_attempts"] = connection_attempts
        if connection_timeout is not None:
            self._values["connection_timeout"] = connection_timeout
        if custom_headers is not None:
            self._values["custom_headers"] = custom_headers
        if origin_path is not None:
            self._values["origin_path"] = origin_path
        if origin_shield_region is not None:
            self._values["origin_shield_region"] = origin_shield_region
        if origin_access_identity is not None:
            self._values["origin_access_identity"] = origin_access_identity

    @builtins.property
    def connection_attempts(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of times that CloudFront attempts to connect to the origin;

        valid values are 1, 2, or 3 attempts.

        :default: 3

        :stability: experimental
        '''
        result = self._values.get("connection_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connection_timeout(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) The number of seconds that CloudFront waits when trying to establish a connection to the origin.

        Valid values are 1-10 seconds, inclusive.

        :default: Duration.seconds(10)

        :stability: experimental
        '''
        result = self._values.get("connection_timeout")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    @builtins.property
    def custom_headers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) A list of HTTP header names and values that CloudFront adds to requests it sends to the origin.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("custom_headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def origin_path(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional path that CloudFront appends to the origin domain name when CloudFront requests content from the origin.

        Must begin, but not end, with '/' (e.g., '/production/images').

        :default: '/'

        :stability: experimental
        '''
        result = self._values.get("origin_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_shield_region(self) -> typing.Optional[builtins.str]:
        '''(experimental) When you enable Origin Shield in the AWS Region that has the lowest latency to your origin, you can get better network performance.

        :default: - origin shield not enabled

        :see: https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html
        :stability: experimental
        '''
        result = self._values.get("origin_shield_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def origin_access_identity(
        self,
    ) -> typing.Optional[_IOriginAccessIdentity_7e00f041]:
        '''(experimental) An optional Origin Access Identity of the origin identity cloudfront will use when calling your s3 bucket.

        :default: - An Origin Access Identity will be created.

        :stability: experimental
        '''
        result = self._values.get("origin_access_identity")
        return typing.cast(typing.Optional[_IOriginAccessIdentity_7e00f041], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3OriginProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HttpOrigin",
    "HttpOriginProps",
    "LoadBalancerV2Origin",
    "LoadBalancerV2OriginProps",
    "OriginGroup",
    "OriginGroupProps",
    "S3Origin",
    "S3OriginProps",
]

publication.publish()
