'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-static-website

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-static-website)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-static-website/)
[![Mentioned in Awesome CDK](https://awesome.re/mentioned-badge.svg)](https://github.com/kolomied/awesome-cdk)

> Cdk component that creates a static website using S3, configures CloudFront (CDN) and maps a custom domain via Route53 (DNS)

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-static-website
```

Python:

```bash
pip install cloudcomponents.cdk-static-website
```

## How to use

### Example 1: With an existing certificate

```python
import { Construct, RemovalPolicy, Stack, StackProps } from '@aws-cdk/core';
import { StringParameter } from '@aws-cdk/aws-ssm';
import { SecurityPolicyProtocol } from '@aws-cdk/aws-cloudfront';
import { StaticWebsite } from '@cloudcomponents/cdk-static-website';
import { HttpHeaders } from '@cloudcomponents/cdk-lambda-at-edge-pattern';

export class StaticWebsiteStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const certificateArn = StringParameter.valueFromLookup(
      this,
      '/certificate/cloudcomponents.org',
    );

    const website = new StaticWebsite(this, 'StaticWebsite', {
      bucketConfiguration: {
        removalPolicy: RemovalPolicy.DESTROY,
      },
      aliasConfiguration: {
        domainName: 'cloudcomponents.org',
        names: ['www.cloudcomponents.org', 'cloudcomponents.org'],
        acmCertRef: certificateArn,
      },
    });

    // A us-east-1 stack is generated under the hood
    const httpHeaders = new HttpHeaders(this, 'HttpHeaders', {
      httpHeaders: {
        'Content-Security-Policy':
          "default-src 'none'; img-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none'; connect-src 'self'",
        'Strict-Transport-Security':
          'max-age=31536000; includeSubdomains; preload',
        'Referrer-Policy': 'same-origin',
        'X-XSS-Protection': '1; mode=block',
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'Cache-Control': 'no-cache',
      },
    });

    website.addLambdaFunctionAssociation(httpHeaders);
  }
}
```

### Example 2: Cloudfront URL with existing sources and up to date Securitypolicy

```python
import { Construct, RemovalPolicy, Stack, StackProps } from '@aws-cdk/core';
import { StringParameter } from '@aws-cdk/aws-ssm';
import { StaticWebsite } from '@cloudcomponents/cdk-static-website';
import { SecurityPolicyProtocol } from '@aws-cdk/aws-cloudfront';

export class StaticWebsiteWithExistingSourcesAndSecurityPolicyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const certificateArn = StringParameter.valueFromLookup(
      this,
      '/certificate/cloudcomponents.org',
    );

    new StaticWebsite(this, 'StaticWebsite', {
      bucketConfiguration: {
        source: '../path/to/your/static/webpage',
        removalPolicy: RemovalPolicy.DESTROY,
      },
      aliasConfiguration: {
        domainName: 'cloudcomponents.org',
        names: ['www.cloudcomponents.org', 'cloudcomponents.org'],
        acmCertRef: certificateArn,
        securityPolicy: SecurityPolicyProtocol.TLS_V1_2_2018
      },
    });
  }
}
```

### Lambda@Edge function

```python
website.addLambdaFunctionAssociation({
  eventType: LambdaEdgeEventType.ORIGIN_REQUEST,
  lambdaFunction: Version.fromVersionArn(
    stack,
    'LambdaEdge',
    'arn:aws:lambda:us-east-1:123456789012:function:my-function:1',
  ),
});
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-static-website/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-static-website/LICENSE)
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

import aws_cdk.aws_cloudfront
import aws_cdk.aws_lambda
import aws_cdk.aws_route53
import aws_cdk.core


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-static-website.AliasProps",
    jsii_struct_bases=[aws_cdk.aws_cloudfront.AliasConfiguration],
    name_mapping={
        "acm_cert_ref": "acmCertRef",
        "names": "names",
        "security_policy": "securityPolicy",
        "ssl_method": "sslMethod",
        "domain_name": "domainName",
        "private_zone": "privateZone",
        "vpc_id": "vpcId",
    },
)
class AliasProps(aws_cdk.aws_cloudfront.AliasConfiguration):
    def __init__(
        self,
        *,
        acm_cert_ref: builtins.str,
        names: typing.Sequence[builtins.str],
        security_policy: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        ssl_method: typing.Optional[aws_cdk.aws_cloudfront.SSLMethod] = None,
        domain_name: builtins.str,
        private_zone: typing.Optional[builtins.bool] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param acm_cert_ref: (deprecated) ARN of an AWS Certificate Manager (ACM) certificate.
        :param names: (deprecated) Domain names on the certificate. Both main domain name and Subject Alternative Names.
        :param security_policy: (deprecated) The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: - SSLv3 if sslMethod VIP, TLSv1 if sslMethod SNI
        :param ssl_method: (deprecated) How CloudFront should serve HTTPS requests. See the notes on SSLMethod if you wish to use other SSL termination types. Default: SSLMethod.SNI
        :param domain_name: The domain name for the site like 'example.com'.
        :param private_zone: Allow searching a private hosted zone. Default: false
        :param vpc_id: Specifies the ID of the VPC associated with a private hosted zone. If a VPC ID is provided and privateZone is false, no results will be returned and an error will be raised Default: - No VPC ID
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "acm_cert_ref": acm_cert_ref,
            "names": names,
            "domain_name": domain_name,
        }
        if security_policy is not None:
            self._values["security_policy"] = security_policy
        if ssl_method is not None:
            self._values["ssl_method"] = ssl_method
        if private_zone is not None:
            self._values["private_zone"] = private_zone
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id

    @builtins.property
    def acm_cert_ref(self) -> builtins.str:
        '''(deprecated) ARN of an AWS Certificate Manager (ACM) certificate.

        :stability: deprecated
        '''
        result = self._values.get("acm_cert_ref")
        assert result is not None, "Required property 'acm_cert_ref' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def names(self) -> typing.List[builtins.str]:
        '''(deprecated) Domain names on the certificate.

        Both main domain name and Subject Alternative Names.

        :stability: deprecated
        '''
        result = self._values.get("names")
        assert result is not None, "Required property 'names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def security_policy(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol]:
        '''(deprecated) The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections.

        CloudFront serves your objects only to browsers or devices that support at
        least the SSL version that you specify.

        :default: - SSLv3 if sslMethod VIP, TLSv1 if sslMethod SNI

        :stability: deprecated
        '''
        result = self._values.get("security_policy")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol], result)

    @builtins.property
    def ssl_method(self) -> typing.Optional[aws_cdk.aws_cloudfront.SSLMethod]:
        '''(deprecated) How CloudFront should serve HTTPS requests.

        See the notes on SSLMethod if you wish to use other SSL termination types.

        :default: SSLMethod.SNI

        :see: https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_ViewerCertificate.html
        :stability: deprecated
        '''
        result = self._values.get("ssl_method")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.SSLMethod], result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''The domain name for the site like 'example.com'.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def private_zone(self) -> typing.Optional[builtins.bool]:
        '''Allow searching a private hosted zone.

        :default: false
        '''
        result = self._values.get("private_zone")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''Specifies the ID of the VPC associated with a private hosted zone.

        If a VPC ID is provided and privateZone is false, no results will be returned
        and an error will be raised

        :default: - No VPC ID
        '''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AliasProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StaticWebsite(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-static-website.StaticWebsite",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        alias_configuration: typing.Optional[AliasProps] = None,
        bucket_configuration: typing.Optional["WebsiteBucketProps"] = None,
        disable_i_pv6: typing.Optional[builtins.bool] = None,
        error_configurations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.CfnDistribution.CustomErrorResponseProperty]] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        disable_upload: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        source: typing.Optional[builtins.str] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param alias_configuration: AliasConfiguration is used to configured CloudFront to respond to requests on custom domain names. Default: - No custom domain names are set up
        :param bucket_configuration: BucketConfiguration is used to configured the S3 website bucket. Default: - The website bucket is provided with default values
        :param disable_i_pv6: An override flag that allows you to turn off support for IPv6 if required. Default: - Cloudfront IPv6 support is enabled and if you've supplied an aliasConfiguration, an AAAA record will be created for your service, set this to true to switch this off.
        :param error_configurations: How CloudFront should handle requests that are not successful (e.g., PageNotFound). Default: - No custom error responses.
        :param web_acl_id: AWS WAF WebACL to associate with this CloudFront distribution. Default: - No AWS Web Application Firewall web access control list (web ACL)
        :param bucket_name: Name of the bucket. Default: - Assigned by CloudFormation (recommended).
        :param disable_upload: Disable website deployment. Default: - false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param source: The source from which to deploy the website. Default: - Dummy placeholder
        :param website_error_document: The error page for the site like 'error.html'. Default: - error.html
        :param website_index_document: The index page for the site like 'index.html'. Default: - index.html
        '''
        props = StaticWebsiteProps(
            alias_configuration=alias_configuration,
            bucket_configuration=bucket_configuration,
            disable_i_pv6=disable_i_pv6,
            error_configurations=error_configurations,
            web_acl_id=web_acl_id,
            bucket_name=bucket_name,
            disable_upload=disable_upload,
            removal_policy=removal_policy,
            source=source,
            website_error_document=website_error_document,
            website_index_document=website_index_document,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addLambdaFunctionAssociation")
    def add_lambda_function_association(
        self,
        *,
        event_type: aws_cdk.aws_cloudfront.LambdaEdgeEventType,
        lambda_function: aws_cdk.aws_lambda.IVersion,
        include_body: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param event_type: The lambda event type defines at which event the lambda is called during the request lifecycle.
        :param lambda_function: A version of the lambda to associate.
        :param include_body: Allows a Lambda function to have read access to the body content. Only valid for "request" event types (``ORIGIN_REQUEST`` or ``VIEWER_REQUEST``). See https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-include-body-access.html Default: false
        '''
        assosiation = aws_cdk.aws_cloudfront.LambdaFunctionAssociation(
            event_type=event_type,
            lambda_function=lambda_function,
            include_body=include_body,
        )

        return typing.cast(None, jsii.invoke(self, "addLambdaFunctionAssociation", [assosiation]))

    @jsii.member(jsii_name="addLambdaFunctionAssociations")
    def add_lambda_function_associations(
        self,
        assosiations: typing.Sequence[aws_cdk.aws_cloudfront.LambdaFunctionAssociation],
    ) -> None:
        '''
        :param assosiations: -
        '''
        return typing.cast(None, jsii.invoke(self, "addLambdaFunctionAssociations", [assosiations]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distribution")
    def distribution(self) -> aws_cdk.aws_cloudfront.CloudFrontWebDistribution:
        return typing.cast(aws_cdk.aws_cloudfront.CloudFrontWebDistribution, jsii.get(self, "distribution"))


class WebsiteAliasRecord(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-static-website.WebsiteAliasRecord",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        record_names: typing.Sequence[builtins.str],
        target: aws_cdk.aws_route53.IAliasRecordTarget,
        disable_i_pv6: typing.Optional[builtins.bool] = None,
        private_zone: typing.Optional[builtins.bool] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: The domain name for the site like 'example.com'.
        :param record_names: Names for the records.
        :param target: Target for the alias record.
        :param disable_i_pv6: We support IPv6 and add an AAAA record by default, but you can turn it off.
        :param private_zone: Allow searching a private hosted zone. Default: false
        :param vpc_id: Specifies the ID of the VPC associated with a private hosted zone. If a VPC ID is provided and privateZone is false, no results will be returned and an error will be raised Default: - No VPC ID
        '''
        props = WebsiteAliasRecordProps(
            domain_name=domain_name,
            record_names=record_names,
            target=target,
            disable_i_pv6=disable_i_pv6,
            private_zone=private_zone,
            vpc_id=vpc_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-static-website.WebsiteAliasRecordProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "record_names": "recordNames",
        "target": "target",
        "disable_i_pv6": "disableIPv6",
        "private_zone": "privateZone",
        "vpc_id": "vpcId",
    },
)
class WebsiteAliasRecordProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        record_names: typing.Sequence[builtins.str],
        target: aws_cdk.aws_route53.IAliasRecordTarget,
        disable_i_pv6: typing.Optional[builtins.bool] = None,
        private_zone: typing.Optional[builtins.bool] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param domain_name: The domain name for the site like 'example.com'.
        :param record_names: Names for the records.
        :param target: Target for the alias record.
        :param disable_i_pv6: We support IPv6 and add an AAAA record by default, but you can turn it off.
        :param private_zone: Allow searching a private hosted zone. Default: false
        :param vpc_id: Specifies the ID of the VPC associated with a private hosted zone. If a VPC ID is provided and privateZone is false, no results will be returned and an error will be raised Default: - No VPC ID
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
            "record_names": record_names,
            "target": target,
        }
        if disable_i_pv6 is not None:
            self._values["disable_i_pv6"] = disable_i_pv6
        if private_zone is not None:
            self._values["private_zone"] = private_zone
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''The domain name for the site like 'example.com'.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def record_names(self) -> typing.List[builtins.str]:
        '''Names for the records.'''
        result = self._values.get("record_names")
        assert result is not None, "Required property 'record_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def target(self) -> aws_cdk.aws_route53.IAliasRecordTarget:
        '''Target for the alias record.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(aws_cdk.aws_route53.IAliasRecordTarget, result)

    @builtins.property
    def disable_i_pv6(self) -> typing.Optional[builtins.bool]:
        '''We support IPv6 and add an AAAA record by default, but you can turn it off.'''
        result = self._values.get("disable_i_pv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def private_zone(self) -> typing.Optional[builtins.bool]:
        '''Allow searching a private hosted zone.

        :default: false
        '''
        result = self._values.get("private_zone")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''Specifies the ID of the VPC associated with a private hosted zone.

        If a VPC ID is provided and privateZone is false, no results will be returned
        and an error will be raised

        :default: - No VPC ID
        '''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebsiteAliasRecordProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WebsiteBucket(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-static-website.WebsiteBucket",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        disable_upload: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        source: typing.Optional[builtins.str] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: Name of the bucket. Default: - Assigned by CloudFormation (recommended).
        :param disable_upload: Disable website deployment. Default: - false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param source: The source from which to deploy the website. Default: - Dummy placeholder
        :param website_error_document: The error page for the site like 'error.html'. Default: - error.html
        :param website_index_document: The index page for the site like 'index.html'. Default: - index.html
        '''
        props = WebsiteBucketProps(
            bucket_name=bucket_name,
            disable_upload=disable_upload,
            removal_policy=removal_policy,
            source=source,
            website_error_document=website_error_document,
            website_index_document=website_index_document,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3OriginConfig")
    def s3_origin_config(self) -> aws_cdk.aws_cloudfront.S3OriginConfig:
        return typing.cast(aws_cdk.aws_cloudfront.S3OriginConfig, jsii.get(self, "s3OriginConfig"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-static-website.WebsiteBucketProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "disable_upload": "disableUpload",
        "removal_policy": "removalPolicy",
        "source": "source",
        "website_error_document": "websiteErrorDocument",
        "website_index_document": "websiteIndexDocument",
    },
)
class WebsiteBucketProps:
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        disable_upload: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        source: typing.Optional[builtins.str] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Name of the bucket. Default: - Assigned by CloudFormation (recommended).
        :param disable_upload: Disable website deployment. Default: - false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param source: The source from which to deploy the website. Default: - Dummy placeholder
        :param website_error_document: The error page for the site like 'error.html'. Default: - error.html
        :param website_index_document: The index page for the site like 'index.html'. Default: - index.html
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if disable_upload is not None:
            self._values["disable_upload"] = disable_upload
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if source is not None:
            self._values["source"] = source
        if website_error_document is not None:
            self._values["website_error_document"] = website_error_document
        if website_index_document is not None:
            self._values["website_index_document"] = website_index_document

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Name of the bucket.

        :default: - Assigned by CloudFormation (recommended).
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_upload(self) -> typing.Optional[builtins.bool]:
        '''Disable website deployment.

        :default: - false
        '''
        result = self._values.get("disable_upload")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''Policy to apply when the bucket is removed from this stack.

        :default: - The bucket will be orphaned.
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''The source from which to deploy the website.

        :default: - Dummy placeholder
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_error_document(self) -> typing.Optional[builtins.str]:
        '''The error page for the site like 'error.html'.

        :default: - error.html
        '''
        result = self._values.get("website_error_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_index_document(self) -> typing.Optional[builtins.str]:
        '''The index page for the site like 'index.html'.

        :default: - index.html
        '''
        result = self._values.get("website_index_document")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WebsiteBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-static-website.StaticWebsiteProps",
    jsii_struct_bases=[WebsiteBucketProps],
    name_mapping={
        "bucket_name": "bucketName",
        "disable_upload": "disableUpload",
        "removal_policy": "removalPolicy",
        "source": "source",
        "website_error_document": "websiteErrorDocument",
        "website_index_document": "websiteIndexDocument",
        "alias_configuration": "aliasConfiguration",
        "bucket_configuration": "bucketConfiguration",
        "disable_i_pv6": "disableIPv6",
        "error_configurations": "errorConfigurations",
        "web_acl_id": "webACLId",
    },
)
class StaticWebsiteProps(WebsiteBucketProps):
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        disable_upload: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        source: typing.Optional[builtins.str] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        alias_configuration: typing.Optional[AliasProps] = None,
        bucket_configuration: typing.Optional[WebsiteBucketProps] = None,
        disable_i_pv6: typing.Optional[builtins.bool] = None,
        error_configurations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.CfnDistribution.CustomErrorResponseProperty]] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Name of the bucket. Default: - Assigned by CloudFormation (recommended).
        :param disable_upload: Disable website deployment. Default: - false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param source: The source from which to deploy the website. Default: - Dummy placeholder
        :param website_error_document: The error page for the site like 'error.html'. Default: - error.html
        :param website_index_document: The index page for the site like 'index.html'. Default: - index.html
        :param alias_configuration: AliasConfiguration is used to configured CloudFront to respond to requests on custom domain names. Default: - No custom domain names are set up
        :param bucket_configuration: BucketConfiguration is used to configured the S3 website bucket. Default: - The website bucket is provided with default values
        :param disable_i_pv6: An override flag that allows you to turn off support for IPv6 if required. Default: - Cloudfront IPv6 support is enabled and if you've supplied an aliasConfiguration, an AAAA record will be created for your service, set this to true to switch this off.
        :param error_configurations: How CloudFront should handle requests that are not successful (e.g., PageNotFound). Default: - No custom error responses.
        :param web_acl_id: AWS WAF WebACL to associate with this CloudFront distribution. Default: - No AWS Web Application Firewall web access control list (web ACL)
        '''
        if isinstance(alias_configuration, dict):
            alias_configuration = AliasProps(**alias_configuration)
        if isinstance(bucket_configuration, dict):
            bucket_configuration = WebsiteBucketProps(**bucket_configuration)
        self._values: typing.Dict[str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if disable_upload is not None:
            self._values["disable_upload"] = disable_upload
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if source is not None:
            self._values["source"] = source
        if website_error_document is not None:
            self._values["website_error_document"] = website_error_document
        if website_index_document is not None:
            self._values["website_index_document"] = website_index_document
        if alias_configuration is not None:
            self._values["alias_configuration"] = alias_configuration
        if bucket_configuration is not None:
            self._values["bucket_configuration"] = bucket_configuration
        if disable_i_pv6 is not None:
            self._values["disable_i_pv6"] = disable_i_pv6
        if error_configurations is not None:
            self._values["error_configurations"] = error_configurations
        if web_acl_id is not None:
            self._values["web_acl_id"] = web_acl_id

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''Name of the bucket.

        :default: - Assigned by CloudFormation (recommended).
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_upload(self) -> typing.Optional[builtins.bool]:
        '''Disable website deployment.

        :default: - false
        '''
        result = self._values.get("disable_upload")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''Policy to apply when the bucket is removed from this stack.

        :default: - The bucket will be orphaned.
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''The source from which to deploy the website.

        :default: - Dummy placeholder
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_error_document(self) -> typing.Optional[builtins.str]:
        '''The error page for the site like 'error.html'.

        :default: - error.html
        '''
        result = self._values.get("website_error_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def website_index_document(self) -> typing.Optional[builtins.str]:
        '''The index page for the site like 'index.html'.

        :default: - index.html
        '''
        result = self._values.get("website_index_document")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias_configuration(self) -> typing.Optional[AliasProps]:
        '''AliasConfiguration is used to configured CloudFront to respond to requests on custom domain names.

        :default: - No custom domain names are set up
        '''
        result = self._values.get("alias_configuration")
        return typing.cast(typing.Optional[AliasProps], result)

    @builtins.property
    def bucket_configuration(self) -> typing.Optional[WebsiteBucketProps]:
        '''BucketConfiguration is used to configured the S3 website bucket.

        :default: - The website bucket is provided with default values
        '''
        result = self._values.get("bucket_configuration")
        return typing.cast(typing.Optional[WebsiteBucketProps], result)

    @builtins.property
    def disable_i_pv6(self) -> typing.Optional[builtins.bool]:
        '''An override flag that allows you to turn off support for IPv6 if required.

        :default:

        - Cloudfront IPv6 support is enabled and if you've supplied an aliasConfiguration, an
        AAAA record will be created for your service, set this to true to switch this off.
        '''
        result = self._values.get("disable_i_pv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def error_configurations(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudfront.CfnDistribution.CustomErrorResponseProperty]]:
        '''How CloudFront should handle requests that are not successful (e.g., PageNotFound).

        :default: - No custom error responses.
        '''
        result = self._values.get("error_configurations")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudfront.CfnDistribution.CustomErrorResponseProperty]], result)

    @builtins.property
    def web_acl_id(self) -> typing.Optional[builtins.str]:
        '''AWS WAF WebACL to associate with this CloudFront distribution.

        :default: - No AWS Web Application Firewall web access control list (web ACL)
        '''
        result = self._values.get("web_acl_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaticWebsiteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AliasProps",
    "StaticWebsite",
    "StaticWebsiteProps",
    "WebsiteAliasRecord",
    "WebsiteAliasRecordProps",
    "WebsiteBucket",
    "WebsiteBucketProps",
]

publication.publish()
