'''
# aws-cloudfront-mediastore module

<!--BEGIN STABILITY BANNER-->---


![Stability: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_cloudfront_mediastore`|
|![TypeScript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) TypeScript|`@aws-solutions-constructs/aws-cloudfront-mediastore`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.cloudfrontmediastore`|

## Overview

This AWS Solutions Construct implements an Amazon CloudFront distribution to an AWS Elemental MediaStore container.

Here is a minimal deployable pattern definition in TypeScript:

```python
import { CloudFrontToMediaStore } from '@aws-solutions-constructs/aws-cloudfront-mediastore';

new CloudFrontToMediaStore(this, 'test-cloudfront-mediastore-default', {});
```

## Initializer

```text
new CloudFrontToMediaStore(scope: Construct, id: string, props: CloudFrontToMediaStoreProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`CloudFrontToMediaStoreProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingMediaStoreContainerObj?|[`mediastore.CfnContainer`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-mediastore.CfnContainer.html)|Optional user provided MediaStore container to override the default MediaStore container.|
|mediaStoreContainerProps?|[`mediastore.CfnContainerProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-mediastore.CfnContainerProps.html)|Optional user provided props to override the default props for the MediaStore Container.|
|cloudFrontDistributionProps?|[`cloudfront.DistributionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudfront.DistributionProps.html)|`any`|Optional user provided props to override the default props for the CloudFront Distribution.|
|insertHttpSecurityHeaders?|`boolean`|Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from CloudFront|
|cloudFrontLoggingBucketProps?|[`s3.BucketProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.BucketProps.html)|Optional user provided props to override the default props for the CloudFront Logging Bucket.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|cloudFrontWebDistribution|[`cloudfront.CloudFrontWebDistribution`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudfront.CloudFrontWebDistribution.html)|Returns an instance of cloudfront.CloudFrontWebDistribution created by the construct.|
|mediaStoreContainer|[`mediastore.CfnContainer`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-mediastore.CfnContainer.html)|Returns an instance of mediastore.CfnContainer.|
|cloudFrontLoggingBucket|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-s3.Bucket.html)|Returns an instance of s3.Bucket as the logging bucket for the CloudFront Web Distribution.|
|cloudFrontOriginRequestPolicy|[`cloudfront.OriginRequestPolicy`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudfront.OriginRequestPolicy.html)|Returns an instance of cloudfront.OriginRequestPolicy created by the construct for the CloudFront Web Distribution.|
|cloudFrontOriginAccessIdentity?|[`cloudfront.OriginAccessIdentity`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudfront.OriginAccessIdentity.html)|Returns an instance of cloudfront.OriginAccessIdentity created by the construct for the CloudFront Web Distribution origin custom headers and the MediaStore Container policy.|
|cloudFrontFunction?|[`cloudfront.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-cloudfront.Function.html)|Returns an instance of the Cloudfront function created by the pattern.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon CloudFront

* Configure access logging for CloudFront Web Distribution
* Enable CloudFront Origin Request Policy for AWS Elemental MediaStore Container
* Set `User-Agent` custom header with CloudFront Origin Access Identity
* Enable automatic injection of best practice HTTP security headers in all responses from CloudFront WebDistribution

### AWS Elemental MediaStore

* Set the deletion policy to retain the resource
* Set the container name with the CloudFormation stack name
* Set the default [Container Cross-origin resource sharing (CORS) policy](https://docs.aws.amazon.com/mediastore/latest/ug/cors-policy.html)
* Set the default [Object Life Cycle policy](https://docs.aws.amazon.com/mediastore/latest/ug/policies-object-lifecycle.html)
* Set the default [Container Policy](https://docs.aws.amazon.com/mediastore/latest/ug/policies.html) to allow only `aws:UserAgent` with CloudFront Origin Access Identity
* Set the default [Metric Policy](https://docs.aws.amazon.com/mediastore/latest/ug/policies-metric.html)
* Enable the access logging

## Architecture

![Architecture Diagram](architecture.png)

---


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

import aws_cdk.aws_cloudfront
import aws_cdk.aws_mediastore
import aws_cdk.aws_s3
import aws_cdk.core


class CloudFrontToMediaStore(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-cloudfront-mediastore.CloudFrontToMediaStore",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cloud_front_distribution_props: typing.Any = None,
        cloud_front_logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_media_store_container_obj: typing.Optional[aws_cdk.aws_mediastore.CfnContainer] = None,
        insert_http_security_headers: typing.Optional[builtins.bool] = None,
        media_store_container_props: typing.Optional[aws_cdk.aws_mediastore.CfnContainerProps] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a scope-unique id.
        :param cloud_front_distribution_props: Optional user provided props to override the default props for the CloudFront. Default: - Default props are used
        :param cloud_front_logging_bucket_props: Optional user provided props to override the default props for the CloudFront Logging Bucket. Default: - Default props are used
        :param existing_media_store_container_obj: Existing instance of mediastore.CfnContainer obejct. Default: - None
        :param insert_http_security_headers: Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from cloudfront. Default: - true
        :param media_store_container_props: Optional user provided props to override the default props for the MediaStore. Default: - Default props are used

        :access: public
        :since: 1.76.0
        :summary: Constructs a new instance of CloudFrontToMediaStore class.
        '''
        props = CloudFrontToMediaStoreProps(
            cloud_front_distribution_props=cloud_front_distribution_props,
            cloud_front_logging_bucket_props=cloud_front_logging_bucket_props,
            existing_media_store_container_obj=existing_media_store_container_obj,
            insert_http_security_headers=insert_http_security_headers,
            media_store_container_props=media_store_container_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontOriginRequestPolicy")
    def cloud_front_origin_request_policy(
        self,
    ) -> aws_cdk.aws_cloudfront.OriginRequestPolicy:
        return typing.cast(aws_cdk.aws_cloudfront.OriginRequestPolicy, jsii.get(self, "cloudFrontOriginRequestPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontWebDistribution")
    def cloud_front_web_distribution(self) -> aws_cdk.aws_cloudfront.Distribution:
        return typing.cast(aws_cdk.aws_cloudfront.Distribution, jsii.get(self, "cloudFrontWebDistribution"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mediaStoreContainer")
    def media_store_container(self) -> aws_cdk.aws_mediastore.CfnContainer:
        return typing.cast(aws_cdk.aws_mediastore.CfnContainer, jsii.get(self, "mediaStoreContainer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontFunction")
    def cloud_front_function(self) -> typing.Optional[aws_cdk.aws_cloudfront.Function]:
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.Function], jsii.get(self, "cloudFrontFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontLoggingBucket")
    def cloud_front_logging_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], jsii.get(self, "cloudFrontLoggingBucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontOriginAccessIdentity")
    def cloud_front_origin_access_identity(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudfront.OriginAccessIdentity]:
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.OriginAccessIdentity], jsii.get(self, "cloudFrontOriginAccessIdentity"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-cloudfront-mediastore.CloudFrontToMediaStoreProps",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_front_distribution_props": "cloudFrontDistributionProps",
        "cloud_front_logging_bucket_props": "cloudFrontLoggingBucketProps",
        "existing_media_store_container_obj": "existingMediaStoreContainerObj",
        "insert_http_security_headers": "insertHttpSecurityHeaders",
        "media_store_container_props": "mediaStoreContainerProps",
    },
)
class CloudFrontToMediaStoreProps:
    def __init__(
        self,
        *,
        cloud_front_distribution_props: typing.Any = None,
        cloud_front_logging_bucket_props: typing.Optional[aws_cdk.aws_s3.BucketProps] = None,
        existing_media_store_container_obj: typing.Optional[aws_cdk.aws_mediastore.CfnContainer] = None,
        insert_http_security_headers: typing.Optional[builtins.bool] = None,
        media_store_container_props: typing.Optional[aws_cdk.aws_mediastore.CfnContainerProps] = None,
    ) -> None:
        '''
        :param cloud_front_distribution_props: Optional user provided props to override the default props for the CloudFront. Default: - Default props are used
        :param cloud_front_logging_bucket_props: Optional user provided props to override the default props for the CloudFront Logging Bucket. Default: - Default props are used
        :param existing_media_store_container_obj: Existing instance of mediastore.CfnContainer obejct. Default: - None
        :param insert_http_security_headers: Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from cloudfront. Default: - true
        :param media_store_container_props: Optional user provided props to override the default props for the MediaStore. Default: - Default props are used

        :summary: The properties for the CloudFrontToMediaStore Construct
        '''
        if isinstance(cloud_front_logging_bucket_props, dict):
            cloud_front_logging_bucket_props = aws_cdk.aws_s3.BucketProps(**cloud_front_logging_bucket_props)
        if isinstance(media_store_container_props, dict):
            media_store_container_props = aws_cdk.aws_mediastore.CfnContainerProps(**media_store_container_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if cloud_front_distribution_props is not None:
            self._values["cloud_front_distribution_props"] = cloud_front_distribution_props
        if cloud_front_logging_bucket_props is not None:
            self._values["cloud_front_logging_bucket_props"] = cloud_front_logging_bucket_props
        if existing_media_store_container_obj is not None:
            self._values["existing_media_store_container_obj"] = existing_media_store_container_obj
        if insert_http_security_headers is not None:
            self._values["insert_http_security_headers"] = insert_http_security_headers
        if media_store_container_props is not None:
            self._values["media_store_container_props"] = media_store_container_props

    @builtins.property
    def cloud_front_distribution_props(self) -> typing.Any:
        '''Optional user provided props to override the default props for the CloudFront.

        :default: - Default props are used
        '''
        result = self._values.get("cloud_front_distribution_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def cloud_front_logging_bucket_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_s3.BucketProps]:
        '''Optional user provided props to override the default props for the CloudFront Logging Bucket.

        :default: - Default props are used
        '''
        result = self._values.get("cloud_front_logging_bucket_props")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.BucketProps], result)

    @builtins.property
    def existing_media_store_container_obj(
        self,
    ) -> typing.Optional[aws_cdk.aws_mediastore.CfnContainer]:
        '''Existing instance of mediastore.CfnContainer obejct.

        :default: - None
        '''
        result = self._values.get("existing_media_store_container_obj")
        return typing.cast(typing.Optional[aws_cdk.aws_mediastore.CfnContainer], result)

    @builtins.property
    def insert_http_security_headers(self) -> typing.Optional[builtins.bool]:
        '''Optional user provided props to turn on/off the automatic injection of best practice HTTP security headers in all responses from cloudfront.

        :default: - true
        '''
        result = self._values.get("insert_http_security_headers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def media_store_container_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_mediastore.CfnContainerProps]:
        '''Optional user provided props to override the default props for the MediaStore.

        :default: - Default props are used
        '''
        result = self._values.get("media_store_container_props")
        return typing.cast(typing.Optional[aws_cdk.aws_mediastore.CfnContainerProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFrontToMediaStoreProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CloudFrontToMediaStore",
    "CloudFrontToMediaStoreProps",
]

publication.publish()
