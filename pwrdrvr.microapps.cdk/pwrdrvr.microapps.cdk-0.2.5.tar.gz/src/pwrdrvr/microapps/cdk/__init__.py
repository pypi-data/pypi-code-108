'''
![Build/Deploy CI](https://github.com/pwrdrvr/microapps-core/actions/workflows/ci.yml/badge.svg) ![Main Build](https://github.com/pwrdrvr/microapps-core/actions/workflows/main-build.yml/badge.svg) ![Release](https://github.com/pwrdrvr/microapps-core/actions/workflows/release.yml/badge.svg)

# Overview

The MicroApps project....

# Project Layout

* [packages/cdk]() - CDK Stacks

  * MicroAppsS3

    * Creates S3 buckets
  * MicroAppsRepos

    * Creates the ECR repos for components to be published into;

      * Deployer
      * Router
  * MicroAppsSvcs

    * Create DynamoDB table
    * Create Deployer Lambda function
    * Create Router Lambda function
    * Create APIGateway HTTP API
  * MicroAppsCF

    * Creates Cloudfront distribution
  * MicroAppsR53

    * Creates domain names to point to the edge (Cloudfront) and origin (API Gateway)
* [packages/microapps-deployer]()

  * Lambda service invoked by `microapps-publish` to record new app/version in the DynamoDB table, create API Gateway integrations, copy S3 assets from staging to prod bucket, etc.
* [packages/microapps-publish]()

  * Node executable that updates versions in config files, deploys static assets to the S3 staging bucket, optionally compiles and deploys a new Lambda function version, and invokes `microapps-deployer`
  * Permissions required:

    * Lambda invoke
    * S3 publish to the staging bucket
    * ECR write
    * Lambda version publish
* [packages/microapps-router]()

  * Lambda function that determines which version of an app to point a user to on a particular invocation

# Useful Commands

* `npm run build` compiles TypeSript to JavaScript
* `npm run lint` checks TypeScript for compliance with Lint rules
* `cdk list` list the stack names
* `cdk deploy` deploy this stack to your default AWS account/region
* `cdk diff` compare deployed stack with current state
* `cdk synth` emits the synthesized CloudFormation template

# Running CDK

Always run CDK from the root of the git repo, which is the directory containing `cdk.json`.

## Set AWS Profile

`export AWS_PROFILE=pwrdrvr`

## Set NVM Version

`nvm use`

# Deployer Service

Copies static assets from staging to deployed directory, creates record of application / version in DynamoDB Table.

# Notes on Selection of Docker Image Lambdas

The Router and Deployer services are very small (0.5 MB) after tree shaking, minification, and uglification performed by `rollup`. The router has the tightest performance requirement and performed just as well as a docker image vs a zip file. However, docker image start up is up to 2x longer vs the zip file for the router; this should not be a problem for any live system with continuous usage and for demos the router can be initialized or pre-provisioned beforehand. The development benefits of docker images for Lambda outweigh the small init time impact on cold starts.

# Notes on Performance

## Router

For best demo performance (and real user performance), the memory for the Router Lambda should be set to 1024 MB as this gives the fastest cold start at the lowest cost. The cost per warm request is actually lower at 1024 MB than at 128 MB, so 1024 MB is just the ideal size.

For supremely optimum demo performance the Router Lambda should be deployed as a .zip file as that saves about 50% of the cold start time, or about 200 ms, but once it's the cold start has happened they are equally as fast as each other.

* Lambda Memory (which linearly scales CPU) Speeds

  * Docker Image Lambda

    * Note: All times captured with Rollup ~400 KB Docker Layer
    * 128 MB

      * Duration Warm: 118 ms
      * Duration Cold: 763 ms
      * Init Duration: 518 ms
      * Billed Duration Warm: 119 ms
      * Billed Duration Init: 1,282 ms
      * Warm Cost: 0.025 millicents
      * Init Cost: 0.26 millicents
    * 256 MB

      * Duration Warm: 30 ms
      * Duration Cold: 363 ms
      * Init Duration: 488 ms
      * Billed Duration Warm: 30 ms
      * Billed Duration Init: 853 ms
      * Warm Cost: 0.013 millicents
      * Init Cost: 0.36 millicents
    * 512 MB

      * Duration Warm: 10 ms
      * Duration Cold: 176 ms
      * Init Duration: 572 ms
      * Billed Duration Warm: 10 ms
      * Billed Duration Init: 749 ms
      * Warm Cost: 0.0083 millicents
      * Init Cost: 0.62 millicents
    * 1024 MB

      * Duration Warm: 9 ms
      * Duration Cold: 84.5 ms
      * Init Duration: 497 ms
      * Billed Duration Warm: 9 ms
      * Billed Duration Init: 585 ms
      * Warm Cost: 0.015 millicents
      * Init Cost: 0.97 millicents
      * *Init performance scales linearly up to and including 1024 MB*
    * 1769 MB

      * This is the point at which a Lambda has 100% of 1 CPU
      * https://docs.aws.amazon.com/lambda/latest/dg/configuration-memory.html
      * Duration Warm: 8.31 ms
      * Duration Cold: 73 ms
      * Init Duration: 514 ms
      * Billed Duration Warm: 10 ms
      * Billed Duration Cold: 587 ms
      * Warm Cost: 0.029 millicents
      * Init Cost: 1.7 millicents
    * 2048 MB

      * Duration Warm: 10 ms
      * Duration Cold: 67 ms
      * Init Duration: 497 ms
      * Billed Duration Warm: 11 ms
      * Billed Duration Init: 566 ms
      * Warm Cost: 0.037 millicents
      * Init Cost: 1.89 millicents
  * Zip File Lambda

    * 128 MB

      * Duration Warm: 110 ms
      * Duration Cold: 761 ms
      * Init Duration: 210 ms
      * Billed Duration Warm: 120 ms
      * Billed Duration Init: 762 ms
      * Warm Cost: 0.025 millicents
      * Init Cost: 0.16 millicents
    * 512 MB

      * Duration Warm: 10 ms
      * Duration Cold: 179 ms
      * Init Duration: 201 ms
      * Billed Duration Warm: 12 ms
      * Billed Duration Init: 185 ms
      * Warm Cost: 0.01 millicents
      * Init Cost: 0.15 millicents
    * 1024 MB

      * Duration Warm: 10 ms
      * Duration Cold: 85 ms
      * Init Duration: 185 ms
      * Billed Duration Warm: 12 ms
      * Billed Duration Init: 85 ms
      * Warm Cost: 0.02 millicents
      * Init Cost: 0.14 millicents
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
import aws_cdk.aws_apigatewayv2_alpha
import aws_cdk.aws_certificatemanager
import aws_cdk.aws_cloudfront
import aws_cdk.aws_cloudfront_origins
import aws_cdk.aws_dynamodb
import aws_cdk.aws_lambda
import aws_cdk.aws_route53
import aws_cdk.aws_s3
import constructs


@jsii.data_type(
    jsii_type="@pwrdrvr/microapps-cdk.AddRoutesOptions",
    jsii_struct_bases=[],
    name_mapping={
        "api_gwy_origin": "apiGwyOrigin",
        "apigwy_origin_request_policy": "apigwyOriginRequestPolicy",
        "bucket_apps_origin": "bucketAppsOrigin",
        "distro": "distro",
        "create_api_path_route": "createAPIPathRoute",
        "root_path_prefix": "rootPathPrefix",
    },
)
class AddRoutesOptions:
    def __init__(
        self,
        *,
        api_gwy_origin: aws_cdk.aws_cloudfront.IOrigin,
        apigwy_origin_request_policy: aws_cdk.aws_cloudfront.IOriginRequestPolicy,
        bucket_apps_origin: aws_cdk.aws_cloudfront_origins.S3Origin,
        distro: aws_cdk.aws_cloudfront.Distribution,
        create_api_path_route: typing.Optional[builtins.bool] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Options for ``AddRoutes``.

        :param api_gwy_origin: API Gateway CloudFront Origin for API calls.
        :param apigwy_origin_request_policy: Origin Request policy for API Gateway Origin.
        :param bucket_apps_origin: S3 Bucket CloudFront Origin for static assets.
        :param distro: CloudFront Distribution to add the Behaviors (Routes) to.
        :param create_api_path_route: Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param root_path_prefix: Path prefix on the root of the CloudFront distribution.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_gwy_origin": api_gwy_origin,
            "apigwy_origin_request_policy": apigwy_origin_request_policy,
            "bucket_apps_origin": bucket_apps_origin,
            "distro": distro,
        }
        if create_api_path_route is not None:
            self._values["create_api_path_route"] = create_api_path_route
        if root_path_prefix is not None:
            self._values["root_path_prefix"] = root_path_prefix

    @builtins.property
    def api_gwy_origin(self) -> aws_cdk.aws_cloudfront.IOrigin:
        '''API Gateway CloudFront Origin for API calls.'''
        result = self._values.get("api_gwy_origin")
        assert result is not None, "Required property 'api_gwy_origin' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.IOrigin, result)

    @builtins.property
    def apigwy_origin_request_policy(
        self,
    ) -> aws_cdk.aws_cloudfront.IOriginRequestPolicy:
        '''Origin Request policy for API Gateway Origin.'''
        result = self._values.get("apigwy_origin_request_policy")
        assert result is not None, "Required property 'apigwy_origin_request_policy' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.IOriginRequestPolicy, result)

    @builtins.property
    def bucket_apps_origin(self) -> aws_cdk.aws_cloudfront_origins.S3Origin:
        '''S3 Bucket CloudFront Origin for static assets.'''
        result = self._values.get("bucket_apps_origin")
        assert result is not None, "Required property 'bucket_apps_origin' is missing"
        return typing.cast(aws_cdk.aws_cloudfront_origins.S3Origin, result)

    @builtins.property
    def distro(self) -> aws_cdk.aws_cloudfront.Distribution:
        '''CloudFront Distribution to add the Behaviors (Routes) to.'''
        result = self._values.get("distro")
        assert result is not None, "Required property 'distro' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.Distribution, result)

    @builtins.property
    def create_api_path_route(self) -> typing.Optional[builtins.bool]:
        '''Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them.

        When false API routes with a period in the path will get routed to S3.

        When true API routes that contain /api/ in the path will get routed to API Gateway
        even if they have a period in the path.

        :default: true
        '''
        result = self._values.get("create_api_path_route")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''Path prefix on the root of the CloudFront distribution.

        Example::

            dev/
        '''
        result = self._values.get("root_path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddRoutesOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pwrdrvr/microapps-cdk.CreateAPIOriginPolicyOptions",
    jsii_struct_bases=[],
    name_mapping={
        "asset_name_root": "assetNameRoot",
        "asset_name_suffix": "assetNameSuffix",
        "domain_name_edge": "domainNameEdge",
    },
)
class CreateAPIOriginPolicyOptions:
    def __init__(
        self,
        *,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        domain_name_edge: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Options for the ``CreateAPIOriginPolicy``.

        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param domain_name_edge: Edge domain name used by CloudFront - If set a custom OriginRequestPolicy will be created that prevents the Host header from being passed to the origin.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if asset_name_root is not None:
            self._values["asset_name_root"] = asset_name_root
        if asset_name_suffix is not None:
            self._values["asset_name_suffix"] = asset_name_suffix
        if domain_name_edge is not None:
            self._values["domain_name_edge"] = domain_name_edge

    @builtins.property
    def asset_name_root(self) -> typing.Optional[builtins.str]:
        '''Optional asset name root.

        :default: - resource names auto assigned

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''Optional asset name suffix.

        :default: none

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name_edge(self) -> typing.Optional[builtins.str]:
        '''Edge domain name used by CloudFront - If set a custom OriginRequestPolicy will be created that prevents the Host header from being passed to the origin.'''
        result = self._values.get("domain_name_edge")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CreateAPIOriginPolicyOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@pwrdrvr/microapps-cdk.IMicroApps")
class IMicroApps(typing_extensions.Protocol):
    '''Represents a MicroApps.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apigwy")
    def apigwy(self) -> "IMicroAppsAPIGwy":
        '''{@inheritdoc IMicroAppsAPIGwy}.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cf")
    def cf(self) -> "IMicroAppsCF":
        '''{@inheritdoc IMicroAppsCF}.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "IMicroAppsS3":
        '''{@inheritdoc IMicroAppsS3}.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svcs")
    def svcs(self) -> "IMicroAppsSvcs":
        '''{@inheritdoc IMicroAppsSvcs}.'''
        ...


class _IMicroAppsProxy:
    '''Represents a MicroApps.'''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroApps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apigwy")
    def apigwy(self) -> "IMicroAppsAPIGwy":
        '''{@inheritdoc IMicroAppsAPIGwy}.'''
        return typing.cast("IMicroAppsAPIGwy", jsii.get(self, "apigwy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cf")
    def cf(self) -> "IMicroAppsCF":
        '''{@inheritdoc IMicroAppsCF}.'''
        return typing.cast("IMicroAppsCF", jsii.get(self, "cf"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "IMicroAppsS3":
        '''{@inheritdoc IMicroAppsS3}.'''
        return typing.cast("IMicroAppsS3", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svcs")
    def svcs(self) -> "IMicroAppsSvcs":
        '''{@inheritdoc IMicroAppsSvcs}.'''
        return typing.cast("IMicroAppsSvcs", jsii.get(self, "svcs"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroApps).__jsii_proxy_class__ = lambda : _IMicroAppsProxy


@jsii.interface(jsii_type="@pwrdrvr/microapps-cdk.IMicroAppsAPIGwy")
class IMicroAppsAPIGwy(typing_extensions.Protocol):
    '''Represents a MicroApps API Gateway.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''API Gateway.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnAppsOrigin")
    def dn_apps_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IDomainName]:
        '''Domain Name applied to API Gateway origin.'''
        ...


class _IMicroAppsAPIGwyProxy:
    '''Represents a MicroApps API Gateway.'''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroAppsAPIGwy"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''API Gateway.'''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, jsii.get(self, "httpApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnAppsOrigin")
    def dn_apps_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IDomainName]:
        '''Domain Name applied to API Gateway origin.'''
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IDomainName], jsii.get(self, "dnAppsOrigin"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsAPIGwy).__jsii_proxy_class__ = lambda : _IMicroAppsAPIGwyProxy


@jsii.interface(jsii_type="@pwrdrvr/microapps-cdk.IMicroAppsCF")
class IMicroAppsCF(typing_extensions.Protocol):
    '''Represents a MicroApps CloudFront.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontDistro")
    def cloud_front_distro(self) -> aws_cdk.aws_cloudfront.Distribution:
        ...


class _IMicroAppsCFProxy:
    '''Represents a MicroApps CloudFront.'''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroAppsCF"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontDistro")
    def cloud_front_distro(self) -> aws_cdk.aws_cloudfront.Distribution:
        return typing.cast(aws_cdk.aws_cloudfront.Distribution, jsii.get(self, "cloudFrontDistro"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsCF).__jsii_proxy_class__ = lambda : _IMicroAppsCFProxy


@jsii.interface(jsii_type="@pwrdrvr/microapps-cdk.IMicroAppsS3")
class IMicroAppsS3(typing_extensions.Protocol):
    '''Represents a MicroApps S3.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketApps")
    def bucket_apps(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for deployed applications.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOAI")
    def bucket_apps_oai(self) -> aws_cdk.aws_cloudfront.OriginAccessIdentity:
        '''CloudFront Origin Access Identity for the deployed applications bucket.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOrigin")
    def bucket_apps_origin(self) -> aws_cdk.aws_cloudfront_origins.S3Origin:
        '''CloudFront Origin for the deployed applications bucket.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsStaging")
    def bucket_apps_staging(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for staged applications (prior to deploy).'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketLogs")
    def bucket_logs(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for CloudFront logs.'''
        ...


class _IMicroAppsS3Proxy:
    '''Represents a MicroApps S3.'''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroAppsS3"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketApps")
    def bucket_apps(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for deployed applications.'''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketApps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOAI")
    def bucket_apps_oai(self) -> aws_cdk.aws_cloudfront.OriginAccessIdentity:
        '''CloudFront Origin Access Identity for the deployed applications bucket.'''
        return typing.cast(aws_cdk.aws_cloudfront.OriginAccessIdentity, jsii.get(self, "bucketAppsOAI"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOrigin")
    def bucket_apps_origin(self) -> aws_cdk.aws_cloudfront_origins.S3Origin:
        '''CloudFront Origin for the deployed applications bucket.'''
        return typing.cast(aws_cdk.aws_cloudfront_origins.S3Origin, jsii.get(self, "bucketAppsOrigin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsStaging")
    def bucket_apps_staging(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for staged applications (prior to deploy).'''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketAppsStaging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketLogs")
    def bucket_logs(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for CloudFront logs.'''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketLogs"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsS3).__jsii_proxy_class__ = lambda : _IMicroAppsS3Proxy


@jsii.interface(jsii_type="@pwrdrvr/microapps-cdk.IMicroAppsSvcs")
class IMicroAppsSvcs(typing_extensions.Protocol):
    '''Represents a MicroApps Services.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deployerFunc")
    def deployer_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''Lambda function for the Deployer.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routerFunc")
    def router_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''Lambda function for the Router.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''DynamoDB table used by Router, Deployer, and Release console app.'''
        ...


class _IMicroAppsSvcsProxy:
    '''Represents a MicroApps Services.'''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroAppsSvcs"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deployerFunc")
    def deployer_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''Lambda function for the Deployer.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "deployerFunc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routerFunc")
    def router_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''Lambda function for the Router.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "routerFunc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''DynamoDB table used by Router, Deployer, and Release console app.'''
        return typing.cast(aws_cdk.aws_dynamodb.ITable, jsii.get(self, "table"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsSvcs).__jsii_proxy_class__ = lambda : _IMicroAppsSvcsProxy


@jsii.implements(IMicroApps)
class MicroApps(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pwrdrvr/microapps-cdk.MicroApps",
):
    '''Create a new MicroApps "turnkey" construct for simple deployments and for initial evaulation of the MicroApps framework.

    Use this construct to create a working entire stack.

    Do not use this construct when adding MicroApps to an existing
    CloudFront, API Gateway, S3 Bucket, etc. or where access
    to all features of the AWS Resources are needed (e.g. to
    add additional Behaviors to the CloudFront distribution, set authorizors
    on API Gateway, etc.).

    :see: {@link https://github.com/pwrdrvr/microapps-core/blob/main/packages/cdk/lib/MicroApps.ts | example usage in a CDK Stack }
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_env: builtins.str,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        cert_edge: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        cert_origin: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        create_api_path_route: typing.Optional[builtins.bool] = None,
        domain_name_edge: typing.Optional[builtins.str] = None,
        domain_name_origin: typing.Optional[builtins.str] = None,
        r53_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
        s3_policy_bypass_aro_as: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_policy_bypass_principal_ar_ns: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_strict_bucket_policy: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_env: Passed to NODE_ENV of Router and Deployer Lambda functions. Default: dev
        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param cert_edge: Certificate in US-East-1 for the CloudFront distribution.
        :param cert_origin: Certificate in deployed region for the API Gateway.
        :param create_api_path_route: Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param domain_name_edge: Optional custom domain name for the CloudFront distribution. Default: auto-assigned
        :param domain_name_origin: Optional custom domain name for the API Gateway HTTPv2 API. Default: auto-assigned
        :param r53_zone: Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: Path prefix on the root of the CloudFront distribution.
        :param s3_policy_bypass_aro_as: Applies when using s3StrictBucketPolicy = true. AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy. This allows sessions that assume the IAM Role to be excluded from the DENY rules on the S3 Bucket Policy. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list. Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead. Note: This AROA must be specified to prevent this policy from locking out non-root sessions that have assumed the admin role. The notPrincipals will only match the role name exactly and will not match any session that has assumed the role since notPrincipals does not allow wildcard matches and does not do wildcard matches implicitly either. The AROA must be used because there are only 3 Principal variables available: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable aws:username, aws:userid, aws:PrincipalTag For an assumed role, aws:username is blank, aws:userid is: [unique id AKA AROA for Role]:[session name] Table of unique ID prefixes such as AROA: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes The name of the role is simply not available for an assumed role and, if it was, a complicated comparison would be requierd to prevent exclusion of applying the Deny Rule to roles from other accounts. To get the AROA with the AWS CLI: aws iam get-role --role-name ROLE-NAME aws iam get-user -–user-name USER-NAME
        :param s3_policy_bypass_principal_ar_ns: Applies when using s3StrictBucketPolicy = true. IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy. Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list.
        :param s3_strict_bucket_policy: Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version. This setting should be used when applications are less than fully trusted. Default: false
        '''
        props = MicroAppsProps(
            app_env=app_env,
            asset_name_root=asset_name_root,
            asset_name_suffix=asset_name_suffix,
            cert_edge=cert_edge,
            cert_origin=cert_origin,
            create_api_path_route=create_api_path_route,
            domain_name_edge=domain_name_edge,
            domain_name_origin=domain_name_origin,
            r53_zone=r53_zone,
            removal_policy=removal_policy,
            root_path_prefix=root_path_prefix,
            s3_policy_bypass_aro_as=s3_policy_bypass_aro_as,
            s3_policy_bypass_principal_ar_ns=s3_policy_bypass_principal_ar_ns,
            s3_strict_bucket_policy=s3_strict_bucket_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apigwy")
    def apigwy(self) -> IMicroAppsAPIGwy:
        '''{@inheritdoc IMicroAppsAPIGwy}.'''
        return typing.cast(IMicroAppsAPIGwy, jsii.get(self, "apigwy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cf")
    def cf(self) -> IMicroAppsCF:
        '''{@inheritdoc IMicroAppsCF}.'''
        return typing.cast(IMicroAppsCF, jsii.get(self, "cf"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> IMicroAppsS3:
        '''{@inheritdoc IMicroAppsS3}.'''
        return typing.cast(IMicroAppsS3, jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svcs")
    def svcs(self) -> IMicroAppsSvcs:
        '''{@inheritdoc IMicroAppsSvcs}.'''
        return typing.cast(IMicroAppsSvcs, jsii.get(self, "svcs"))


@jsii.implements(IMicroAppsAPIGwy)
class MicroAppsAPIGwy(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsAPIGwy",
):
    '''Create a new MicroApps API Gateway HTTP API endpoint.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        cert_origin: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        domain_name_edge: typing.Optional[builtins.str] = None,
        domain_name_origin: typing.Optional[builtins.str] = None,
        r53_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param cert_origin: Optional local region ACM certificate to use for API Gateway Note: required when using a custom domain. Default: none
        :param domain_name_edge: CloudFront edge domain name. Default: auto-assigned
        :param domain_name_origin: API Gateway origin domain name. Default: auto-assigned
        :param r53_zone: Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: Path prefix on the root of the API Gateway Stage. Default: none
        '''
        props = MicroAppsAPIGwyProps(
            asset_name_root=asset_name_root,
            asset_name_suffix=asset_name_suffix,
            cert_origin=cert_origin,
            domain_name_edge=domain_name_edge,
            domain_name_origin=domain_name_origin,
            r53_zone=r53_zone,
            removal_policy=removal_policy,
            root_path_prefix=root_path_prefix,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''API Gateway.'''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, jsii.get(self, "httpApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnAppsOrigin")
    def dn_apps_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IDomainName]:
        '''Domain Name applied to API Gateway origin.'''
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IDomainName], jsii.get(self, "dnAppsOrigin"))


@jsii.data_type(
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsAPIGwyProps",
    jsii_struct_bases=[],
    name_mapping={
        "asset_name_root": "assetNameRoot",
        "asset_name_suffix": "assetNameSuffix",
        "cert_origin": "certOrigin",
        "domain_name_edge": "domainNameEdge",
        "domain_name_origin": "domainNameOrigin",
        "r53_zone": "r53Zone",
        "removal_policy": "removalPolicy",
        "root_path_prefix": "rootPathPrefix",
    },
)
class MicroAppsAPIGwyProps:
    def __init__(
        self,
        *,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        cert_origin: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        domain_name_edge: typing.Optional[builtins.str] = None,
        domain_name_origin: typing.Optional[builtins.str] = None,
        r53_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties to initialize an instance of ``MicroAppsAPIGwy``.

        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param cert_origin: Optional local region ACM certificate to use for API Gateway Note: required when using a custom domain. Default: none
        :param domain_name_edge: CloudFront edge domain name. Default: auto-assigned
        :param domain_name_origin: API Gateway origin domain name. Default: auto-assigned
        :param r53_zone: Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: Path prefix on the root of the API Gateway Stage. Default: none
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if asset_name_root is not None:
            self._values["asset_name_root"] = asset_name_root
        if asset_name_suffix is not None:
            self._values["asset_name_suffix"] = asset_name_suffix
        if cert_origin is not None:
            self._values["cert_origin"] = cert_origin
        if domain_name_edge is not None:
            self._values["domain_name_edge"] = domain_name_edge
        if domain_name_origin is not None:
            self._values["domain_name_origin"] = domain_name_origin
        if r53_zone is not None:
            self._values["r53_zone"] = r53_zone
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if root_path_prefix is not None:
            self._values["root_path_prefix"] = root_path_prefix

    @builtins.property
    def asset_name_root(self) -> typing.Optional[builtins.str]:
        '''Optional asset name root.

        :default: - resource names auto assigned

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''Optional asset name suffix.

        :default: none

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''Optional local region ACM certificate to use for API Gateway Note: required when using a custom domain.

        :default: none
        '''
        result = self._values.get("cert_origin")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def domain_name_edge(self) -> typing.Optional[builtins.str]:
        '''CloudFront edge domain name.

        :default: auto-assigned

        Example::

            apps.pwrdrvr.com
        '''
        result = self._values.get("domain_name_edge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name_origin(self) -> typing.Optional[builtins.str]:
        '''API Gateway origin domain name.

        :default: auto-assigned

        Example::

            apps-origin.pwrdrvr.com
        '''
        result = self._values.get("domain_name_origin")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def r53_zone(self) -> typing.Optional[aws_cdk.aws_route53.IHostedZone]:
        '''Route53 zone in which to create optional ``domainNameEdge`` record.'''
        result = self._values.get("r53_zone")
        return typing.cast(typing.Optional[aws_cdk.aws_route53.IHostedZone], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''Path prefix on the root of the API Gateway Stage.

        :default: none

        Example::

            dev/
        '''
        result = self._values.get("root_path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicroAppsAPIGwyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IMicroAppsCF)
class MicroAppsCF(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsCF",
):
    '''Create a new MicroApps CloudFront Distribution.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        bucket_apps_origin: aws_cdk.aws_cloudfront_origins.S3Origin,
        http_api: aws_cdk.aws_apigatewayv2_alpha.HttpApi,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        bucket_logs: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        cert_edge: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        create_api_path_route: typing.Optional[builtins.bool] = None,
        domain_name_edge: typing.Optional[builtins.str] = None,
        domain_name_origin: typing.Optional[builtins.str] = None,
        r53_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_apps_origin: S3 bucket origin for deployed applications.
        :param http_api: API Gateway v2 HTTP API for apps.
        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param bucket_logs: S3 bucket for CloudFront logs.
        :param cert_edge: ACM Certificate that covers ``domainNameEdge`` name.
        :param create_api_path_route: Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param domain_name_edge: CloudFront Distribution domain name. Default: auto-assigned
        :param domain_name_origin: API Gateway custom origin domain name. Default: - retrieved from httpApi, if possible
        :param r53_zone: Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: Path prefix on the root of the CloudFront distribution.
        '''
        props = MicroAppsCFProps(
            bucket_apps_origin=bucket_apps_origin,
            http_api=http_api,
            asset_name_root=asset_name_root,
            asset_name_suffix=asset_name_suffix,
            bucket_logs=bucket_logs,
            cert_edge=cert_edge,
            create_api_path_route=create_api_path_route,
            domain_name_edge=domain_name_edge,
            domain_name_origin=domain_name_origin,
            r53_zone=r53_zone,
            removal_policy=removal_policy,
            root_path_prefix=root_path_prefix,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addRoutes") # type: ignore[misc]
    @builtins.classmethod
    def add_routes(
        cls,
        _scope: constructs.Construct,
        *,
        api_gwy_origin: aws_cdk.aws_cloudfront.IOrigin,
        apigwy_origin_request_policy: aws_cdk.aws_cloudfront.IOriginRequestPolicy,
        bucket_apps_origin: aws_cdk.aws_cloudfront_origins.S3Origin,
        distro: aws_cdk.aws_cloudfront.Distribution,
        create_api_path_route: typing.Optional[builtins.bool] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Add API Gateway and S3 routes to an existing CloudFront Distribution.

        :param _scope: -
        :param api_gwy_origin: API Gateway CloudFront Origin for API calls.
        :param apigwy_origin_request_policy: Origin Request policy for API Gateway Origin.
        :param bucket_apps_origin: S3 Bucket CloudFront Origin for static assets.
        :param distro: CloudFront Distribution to add the Behaviors (Routes) to.
        :param create_api_path_route: Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param root_path_prefix: Path prefix on the root of the CloudFront distribution.
        '''
        props = AddRoutesOptions(
            api_gwy_origin=api_gwy_origin,
            apigwy_origin_request_policy=apigwy_origin_request_policy,
            bucket_apps_origin=bucket_apps_origin,
            distro=distro,
            create_api_path_route=create_api_path_route,
            root_path_prefix=root_path_prefix,
        )

        return typing.cast(None, jsii.sinvoke(cls, "addRoutes", [_scope, props]))

    @jsii.member(jsii_name="createAPIOriginPolicy") # type: ignore[misc]
    @builtins.classmethod
    def create_api_origin_policy(
        cls,
        scope: constructs.Construct,
        *,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        domain_name_edge: typing.Optional[builtins.str] = None,
    ) -> aws_cdk.aws_cloudfront.IOriginRequestPolicy:
        '''Create or get the origin request policy.

        If a custom domain name is NOT used for the origin then a policy
        will be created.

        If a custom domain name IS used for the origin then the ALL_VIEWER
        policy will be returned.  This policy passes the Host header to the
        origin, which is fine when using a custom domain name on the origin.

        :param scope: -
        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param domain_name_edge: Edge domain name used by CloudFront - If set a custom OriginRequestPolicy will be created that prevents the Host header from being passed to the origin.
        '''
        props = CreateAPIOriginPolicyOptions(
            asset_name_root=asset_name_root,
            asset_name_suffix=asset_name_suffix,
            domain_name_edge=domain_name_edge,
        )

        return typing.cast(aws_cdk.aws_cloudfront.IOriginRequestPolicy, jsii.sinvoke(cls, "createAPIOriginPolicy", [scope, props]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontDistro")
    def cloud_front_distro(self) -> aws_cdk.aws_cloudfront.Distribution:
        return typing.cast(aws_cdk.aws_cloudfront.Distribution, jsii.get(self, "cloudFrontDistro"))


@jsii.data_type(
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsCFProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_apps_origin": "bucketAppsOrigin",
        "http_api": "httpApi",
        "asset_name_root": "assetNameRoot",
        "asset_name_suffix": "assetNameSuffix",
        "bucket_logs": "bucketLogs",
        "cert_edge": "certEdge",
        "create_api_path_route": "createAPIPathRoute",
        "domain_name_edge": "domainNameEdge",
        "domain_name_origin": "domainNameOrigin",
        "r53_zone": "r53Zone",
        "removal_policy": "removalPolicy",
        "root_path_prefix": "rootPathPrefix",
    },
)
class MicroAppsCFProps:
    def __init__(
        self,
        *,
        bucket_apps_origin: aws_cdk.aws_cloudfront_origins.S3Origin,
        http_api: aws_cdk.aws_apigatewayv2_alpha.HttpApi,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        bucket_logs: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        cert_edge: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        create_api_path_route: typing.Optional[builtins.bool] = None,
        domain_name_edge: typing.Optional[builtins.str] = None,
        domain_name_origin: typing.Optional[builtins.str] = None,
        r53_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties to initialize an instance of ``MicroAppsCF``.

        :param bucket_apps_origin: S3 bucket origin for deployed applications.
        :param http_api: API Gateway v2 HTTP API for apps.
        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param bucket_logs: S3 bucket for CloudFront logs.
        :param cert_edge: ACM Certificate that covers ``domainNameEdge`` name.
        :param create_api_path_route: Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param domain_name_edge: CloudFront Distribution domain name. Default: auto-assigned
        :param domain_name_origin: API Gateway custom origin domain name. Default: - retrieved from httpApi, if possible
        :param r53_zone: Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: Path prefix on the root of the CloudFront distribution.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_apps_origin": bucket_apps_origin,
            "http_api": http_api,
        }
        if asset_name_root is not None:
            self._values["asset_name_root"] = asset_name_root
        if asset_name_suffix is not None:
            self._values["asset_name_suffix"] = asset_name_suffix
        if bucket_logs is not None:
            self._values["bucket_logs"] = bucket_logs
        if cert_edge is not None:
            self._values["cert_edge"] = cert_edge
        if create_api_path_route is not None:
            self._values["create_api_path_route"] = create_api_path_route
        if domain_name_edge is not None:
            self._values["domain_name_edge"] = domain_name_edge
        if domain_name_origin is not None:
            self._values["domain_name_origin"] = domain_name_origin
        if r53_zone is not None:
            self._values["r53_zone"] = r53_zone
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if root_path_prefix is not None:
            self._values["root_path_prefix"] = root_path_prefix

    @builtins.property
    def bucket_apps_origin(self) -> aws_cdk.aws_cloudfront_origins.S3Origin:
        '''S3 bucket origin for deployed applications.'''
        result = self._values.get("bucket_apps_origin")
        assert result is not None, "Required property 'bucket_apps_origin' is missing"
        return typing.cast(aws_cdk.aws_cloudfront_origins.S3Origin, result)

    @builtins.property
    def http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''API Gateway v2 HTTP API for apps.'''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, result)

    @builtins.property
    def asset_name_root(self) -> typing.Optional[builtins.str]:
        '''Optional asset name root.

        :default: - resource names auto assigned

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''Optional asset name suffix.

        :default: none

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_logs(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''S3 bucket for CloudFront logs.'''
        result = self._values.get("bucket_logs")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def cert_edge(self) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''ACM Certificate that covers ``domainNameEdge`` name.'''
        result = self._values.get("cert_edge")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def create_api_path_route(self) -> typing.Optional[builtins.bool]:
        '''Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them.

        When false API routes with a period in the path will get routed to S3.

        When true API routes that contain /api/ in the path will get routed to API Gateway
        even if they have a period in the path.

        :default: true
        '''
        result = self._values.get("create_api_path_route")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_name_edge(self) -> typing.Optional[builtins.str]:
        '''CloudFront Distribution domain name.

        :default: auto-assigned

        Example::

            apps.pwrdrvr.com
        '''
        result = self._values.get("domain_name_edge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name_origin(self) -> typing.Optional[builtins.str]:
        '''API Gateway custom origin domain name.

        :default: - retrieved from httpApi, if possible

        Example::

            apps.pwrdrvr.com
        '''
        result = self._values.get("domain_name_origin")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def r53_zone(self) -> typing.Optional[aws_cdk.aws_route53.IHostedZone]:
        '''Route53 zone in which to create optional ``domainNameEdge`` record.'''
        result = self._values.get("r53_zone")
        return typing.cast(typing.Optional[aws_cdk.aws_route53.IHostedZone], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''Path prefix on the root of the CloudFront distribution.

        Example::

            dev/
        '''
        result = self._values.get("root_path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicroAppsCFProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_env": "appEnv",
        "asset_name_root": "assetNameRoot",
        "asset_name_suffix": "assetNameSuffix",
        "cert_edge": "certEdge",
        "cert_origin": "certOrigin",
        "create_api_path_route": "createAPIPathRoute",
        "domain_name_edge": "domainNameEdge",
        "domain_name_origin": "domainNameOrigin",
        "r53_zone": "r53Zone",
        "removal_policy": "removalPolicy",
        "root_path_prefix": "rootPathPrefix",
        "s3_policy_bypass_aro_as": "s3PolicyBypassAROAs",
        "s3_policy_bypass_principal_ar_ns": "s3PolicyBypassPrincipalARNs",
        "s3_strict_bucket_policy": "s3StrictBucketPolicy",
    },
)
class MicroAppsProps:
    def __init__(
        self,
        *,
        app_env: builtins.str,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        cert_edge: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        cert_origin: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        create_api_path_route: typing.Optional[builtins.bool] = None,
        domain_name_edge: typing.Optional[builtins.str] = None,
        domain_name_origin: typing.Optional[builtins.str] = None,
        r53_zone: typing.Optional[aws_cdk.aws_route53.IHostedZone] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
        s3_policy_bypass_aro_as: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_policy_bypass_principal_ar_ns: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_strict_bucket_policy: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties to initialize an instance of ``MicroApps``.

        :param app_env: Passed to NODE_ENV of Router and Deployer Lambda functions. Default: dev
        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param cert_edge: Certificate in US-East-1 for the CloudFront distribution.
        :param cert_origin: Certificate in deployed region for the API Gateway.
        :param create_api_path_route: Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param domain_name_edge: Optional custom domain name for the CloudFront distribution. Default: auto-assigned
        :param domain_name_origin: Optional custom domain name for the API Gateway HTTPv2 API. Default: auto-assigned
        :param r53_zone: Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: Path prefix on the root of the CloudFront distribution.
        :param s3_policy_bypass_aro_as: Applies when using s3StrictBucketPolicy = true. AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy. This allows sessions that assume the IAM Role to be excluded from the DENY rules on the S3 Bucket Policy. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list. Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead. Note: This AROA must be specified to prevent this policy from locking out non-root sessions that have assumed the admin role. The notPrincipals will only match the role name exactly and will not match any session that has assumed the role since notPrincipals does not allow wildcard matches and does not do wildcard matches implicitly either. The AROA must be used because there are only 3 Principal variables available: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable aws:username, aws:userid, aws:PrincipalTag For an assumed role, aws:username is blank, aws:userid is: [unique id AKA AROA for Role]:[session name] Table of unique ID prefixes such as AROA: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes The name of the role is simply not available for an assumed role and, if it was, a complicated comparison would be requierd to prevent exclusion of applying the Deny Rule to roles from other accounts. To get the AROA with the AWS CLI: aws iam get-role --role-name ROLE-NAME aws iam get-user -–user-name USER-NAME
        :param s3_policy_bypass_principal_ar_ns: Applies when using s3StrictBucketPolicy = true. IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy. Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list.
        :param s3_strict_bucket_policy: Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version. This setting should be used when applications are less than fully trusted. Default: false
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_env": app_env,
        }
        if asset_name_root is not None:
            self._values["asset_name_root"] = asset_name_root
        if asset_name_suffix is not None:
            self._values["asset_name_suffix"] = asset_name_suffix
        if cert_edge is not None:
            self._values["cert_edge"] = cert_edge
        if cert_origin is not None:
            self._values["cert_origin"] = cert_origin
        if create_api_path_route is not None:
            self._values["create_api_path_route"] = create_api_path_route
        if domain_name_edge is not None:
            self._values["domain_name_edge"] = domain_name_edge
        if domain_name_origin is not None:
            self._values["domain_name_origin"] = domain_name_origin
        if r53_zone is not None:
            self._values["r53_zone"] = r53_zone
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if root_path_prefix is not None:
            self._values["root_path_prefix"] = root_path_prefix
        if s3_policy_bypass_aro_as is not None:
            self._values["s3_policy_bypass_aro_as"] = s3_policy_bypass_aro_as
        if s3_policy_bypass_principal_ar_ns is not None:
            self._values["s3_policy_bypass_principal_ar_ns"] = s3_policy_bypass_principal_ar_ns
        if s3_strict_bucket_policy is not None:
            self._values["s3_strict_bucket_policy"] = s3_strict_bucket_policy

    @builtins.property
    def app_env(self) -> builtins.str:
        '''Passed to NODE_ENV of Router and Deployer Lambda functions.

        :default: dev
        '''
        result = self._values.get("app_env")
        assert result is not None, "Required property 'app_env' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def asset_name_root(self) -> typing.Optional[builtins.str]:
        '''Optional asset name root.

        :default: - resource names auto assigned

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''Optional asset name suffix.

        :default: none

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_edge(self) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''Certificate in US-East-1 for the CloudFront distribution.'''
        result = self._values.get("cert_edge")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def cert_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''Certificate in deployed region for the API Gateway.'''
        result = self._values.get("cert_origin")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def create_api_path_route(self) -> typing.Optional[builtins.bool]:
        '''Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them.

        When false API routes with a period in the path will get routed to S3.

        When true API routes that contain /api/ in the path will get routed to API Gateway
        even if they have a period in the path.

        :default: true
        '''
        result = self._values.get("create_api_path_route")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_name_edge(self) -> typing.Optional[builtins.str]:
        '''Optional custom domain name for the CloudFront distribution.

        :default: auto-assigned

        Example::

            apps.pwrdrvr.com
        '''
        result = self._values.get("domain_name_edge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name_origin(self) -> typing.Optional[builtins.str]:
        '''Optional custom domain name for the API Gateway HTTPv2 API.

        :default: auto-assigned

        Example::

            apps-origin.pwrdrvr.com
        '''
        result = self._values.get("domain_name_origin")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def r53_zone(self) -> typing.Optional[aws_cdk.aws_route53.IHostedZone]:
        '''Route53 zone in which to create optional ``domainNameEdge`` record.'''
        result = self._values.get("r53_zone")
        return typing.cast(typing.Optional[aws_cdk.aws_route53.IHostedZone], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''Path prefix on the root of the CloudFront distribution.

        Example::

            dev/
        '''
        result = self._values.get("root_path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_policy_bypass_aro_as(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Applies when using s3StrictBucketPolicy = true.

        AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy.
        This allows sessions that assume the IAM Role to be excluded from the
        DENY rules on the S3 Bucket Policy.

        Typically any admin roles / users that need to view or manage the S3 Bucket
        would be added to this list.

        Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead.

        Note: This AROA must be specified to prevent this policy from locking
        out non-root sessions that have assumed the admin role.

        The notPrincipals will only match the role name exactly and will not match
        any session that has assumed the role since notPrincipals does not allow
        wildcard matches and does not do wildcard matches implicitly either.

        The AROA must be used because there are only 3 Principal variables available:
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable
        aws:username, aws:userid, aws:PrincipalTag

        For an assumed role, aws:username is blank, aws:userid is:
        [unique id AKA AROA for Role]:[session name]

        Table of unique ID prefixes such as AROA:
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes

        The name of the role is simply not available for an assumed role and, if it was,
        a complicated comparison would be requierd to prevent exclusion
        of applying the Deny Rule to roles from other accounts.

        To get the AROA with the AWS CLI:
        aws iam get-role --role-name ROLE-NAME
        aws iam get-user -–user-name USER-NAME

        :see: s3StrictBucketPolicy

        Example::

            [ 'AROA1234567890123' ]
        '''
        result = self._values.get("s3_policy_bypass_aro_as")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_policy_bypass_principal_ar_ns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Applies when using s3StrictBucketPolicy = true.

        IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy.

        Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``.

        Typically any admin roles / users that need to view or manage the S3 Bucket
        would be added to this list.

        :see: s3PolicyBypassAROAs

        Example::

            ['arn:aws:iam::1234567890123:role/AdminAccess', 'arn:aws:iam::1234567890123:user/MyAdminUser']
        '''
        result = self._values.get("s3_policy_bypass_principal_ar_ns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_strict_bucket_policy(self) -> typing.Optional[builtins.bool]:
        '''Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version.

        This setting should be used when applications are less than
        fully trusted.

        :default: false
        '''
        result = self._values.get("s3_strict_bucket_policy")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicroAppsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IMicroAppsS3)
class MicroAppsS3(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsS3",
):
    '''Create a new MicroApps S3 Bucket.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        bucket_apps_name: typing.Optional[builtins.str] = None,
        bucket_apps_staging_name: typing.Optional[builtins.str] = None,
        bucket_logs_name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param bucket_apps_name: S3 deployed apps bucket name. Default: auto-assigned
        :param bucket_apps_staging_name: S3 staging apps bucket name. Default: auto-assigned
        :param bucket_logs_name: S3 logs bucket name. Default: auto-assigned
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckets will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        '''
        props = MicroAppsS3Props(
            asset_name_root=asset_name_root,
            asset_name_suffix=asset_name_suffix,
            bucket_apps_name=bucket_apps_name,
            bucket_apps_staging_name=bucket_apps_staging_name,
            bucket_logs_name=bucket_logs_name,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketApps")
    def bucket_apps(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for deployed applications.'''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketApps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOAI")
    def bucket_apps_oai(self) -> aws_cdk.aws_cloudfront.OriginAccessIdentity:
        '''CloudFront Origin Access Identity for the deployed applications bucket.'''
        return typing.cast(aws_cdk.aws_cloudfront.OriginAccessIdentity, jsii.get(self, "bucketAppsOAI"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOrigin")
    def bucket_apps_origin(self) -> aws_cdk.aws_cloudfront_origins.S3Origin:
        '''CloudFront Origin for the deployed applications bucket.'''
        return typing.cast(aws_cdk.aws_cloudfront_origins.S3Origin, jsii.get(self, "bucketAppsOrigin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsStaging")
    def bucket_apps_staging(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for staged applications (prior to deploy).'''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketAppsStaging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketLogs")
    def bucket_logs(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for CloudFront logs.'''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketLogs"))


@jsii.data_type(
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsS3Props",
    jsii_struct_bases=[],
    name_mapping={
        "asset_name_root": "assetNameRoot",
        "asset_name_suffix": "assetNameSuffix",
        "bucket_apps_name": "bucketAppsName",
        "bucket_apps_staging_name": "bucketAppsStagingName",
        "bucket_logs_name": "bucketLogsName",
        "removal_policy": "removalPolicy",
    },
)
class MicroAppsS3Props:
    def __init__(
        self,
        *,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        bucket_apps_name: typing.Optional[builtins.str] = None,
        bucket_apps_staging_name: typing.Optional[builtins.str] = None,
        bucket_logs_name: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
    ) -> None:
        '''Properties to initialize an instance of ``MicroAppsS3``.

        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param bucket_apps_name: S3 deployed apps bucket name. Default: auto-assigned
        :param bucket_apps_staging_name: S3 staging apps bucket name. Default: auto-assigned
        :param bucket_logs_name: S3 logs bucket name. Default: auto-assigned
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckets will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if asset_name_root is not None:
            self._values["asset_name_root"] = asset_name_root
        if asset_name_suffix is not None:
            self._values["asset_name_suffix"] = asset_name_suffix
        if bucket_apps_name is not None:
            self._values["bucket_apps_name"] = bucket_apps_name
        if bucket_apps_staging_name is not None:
            self._values["bucket_apps_staging_name"] = bucket_apps_staging_name
        if bucket_logs_name is not None:
            self._values["bucket_logs_name"] = bucket_logs_name
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def asset_name_root(self) -> typing.Optional[builtins.str]:
        '''Optional asset name root.

        :default: - resource names auto assigned

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''Optional asset name suffix.

        :default: none

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_apps_name(self) -> typing.Optional[builtins.str]:
        '''S3 deployed apps bucket name.

        :default: auto-assigned
        '''
        result = self._values.get("bucket_apps_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_apps_staging_name(self) -> typing.Optional[builtins.str]:
        '''S3 staging apps bucket name.

        :default: auto-assigned
        '''
        result = self._values.get("bucket_apps_staging_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_logs_name(self) -> typing.Optional[builtins.str]:
        '''S3 logs bucket name.

        :default: auto-assigned
        '''
        result = self._values.get("bucket_logs_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckets will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicroAppsS3Props(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IMicroAppsSvcs)
class MicroAppsSvcs(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsSvcs",
):
    '''Create a new MicroApps Services construct, including the Deployer and Router Lambda Functions, and the DynamoDB Table used by both.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_env: builtins.str,
        bucket_apps: aws_cdk.aws_s3.IBucket,
        bucket_apps_oai: aws_cdk.aws_cloudfront.OriginAccessIdentity,
        bucket_apps_staging: aws_cdk.aws_s3.IBucket,
        http_api: aws_cdk.aws_apigatewayv2_alpha.HttpApi,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
        s3_policy_bypass_aro_as: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_policy_bypass_principal_ar_ns: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_strict_bucket_policy: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_env: Application environment, passed as ``NODE_ENV`` to the Router and Deployer Lambda functions.
        :param bucket_apps: S3 bucket for deployed applications.
        :param bucket_apps_oai: CloudFront Origin Access Identity for the deployed applications bucket.
        :param bucket_apps_staging: S3 bucket for staged applications (prior to deploy).
        :param http_api: API Gateway v2 HTTP for Router and app.
        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: Path prefix on the root of the deployment. Default: none
        :param s3_policy_bypass_aro_as: Applies when using s3StrictBucketPolicy = true. AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy. This allows sessions that assume the IAM Role to be excluded from the DENY rules on the S3 Bucket Policy. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list. Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead. Note: This AROA must be specified to prevent this policy from locking out non-root sessions that have assumed the admin role. The notPrincipals will only match the role name exactly and will not match any session that has assumed the role since notPrincipals does not allow wildcard matches and does not do wildcard matches implicitly either. The AROA must be used because there are only 3 Principal variables available: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable aws:username, aws:userid, aws:PrincipalTag For an assumed role, aws:username is blank, aws:userid is: [unique id AKA AROA for Role]:[session name] Table of unique ID prefixes such as AROA: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes The name of the role is simply not available for an assumed role and, if it was, a complicated comparison would be requierd to prevent exclusion of applying the Deny Rule to roles from other accounts. To get the AROA with the AWS CLI: aws iam get-role --role-name ROLE-NAME aws iam get-user -–user-name USER-NAME
        :param s3_policy_bypass_principal_ar_ns: Applies when using s3StrictBucketPolicy = true. IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy. Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list.
        :param s3_strict_bucket_policy: Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version. This setting should be used when applications are less than fully trusted. Default: false
        '''
        props = MicroAppsSvcsProps(
            app_env=app_env,
            bucket_apps=bucket_apps,
            bucket_apps_oai=bucket_apps_oai,
            bucket_apps_staging=bucket_apps_staging,
            http_api=http_api,
            asset_name_root=asset_name_root,
            asset_name_suffix=asset_name_suffix,
            removal_policy=removal_policy,
            root_path_prefix=root_path_prefix,
            s3_policy_bypass_aro_as=s3_policy_bypass_aro_as,
            s3_policy_bypass_principal_ar_ns=s3_policy_bypass_principal_ar_ns,
            s3_strict_bucket_policy=s3_strict_bucket_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deployerFunc")
    def deployer_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''Lambda function for the Deployer.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "deployerFunc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routerFunc")
    def router_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''Lambda function for the Router.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "routerFunc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''DynamoDB table used by Router, Deployer, and Release console app.'''
        return typing.cast(aws_cdk.aws_dynamodb.ITable, jsii.get(self, "table"))


@jsii.data_type(
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsSvcsProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_env": "appEnv",
        "bucket_apps": "bucketApps",
        "bucket_apps_oai": "bucketAppsOAI",
        "bucket_apps_staging": "bucketAppsStaging",
        "http_api": "httpApi",
        "asset_name_root": "assetNameRoot",
        "asset_name_suffix": "assetNameSuffix",
        "removal_policy": "removalPolicy",
        "root_path_prefix": "rootPathPrefix",
        "s3_policy_bypass_aro_as": "s3PolicyBypassAROAs",
        "s3_policy_bypass_principal_ar_ns": "s3PolicyBypassPrincipalARNs",
        "s3_strict_bucket_policy": "s3StrictBucketPolicy",
    },
)
class MicroAppsSvcsProps:
    def __init__(
        self,
        *,
        app_env: builtins.str,
        bucket_apps: aws_cdk.aws_s3.IBucket,
        bucket_apps_oai: aws_cdk.aws_cloudfront.OriginAccessIdentity,
        bucket_apps_staging: aws_cdk.aws_s3.IBucket,
        http_api: aws_cdk.aws_apigatewayv2_alpha.HttpApi,
        asset_name_root: typing.Optional[builtins.str] = None,
        asset_name_suffix: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        root_path_prefix: typing.Optional[builtins.str] = None,
        s3_policy_bypass_aro_as: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_policy_bypass_principal_ar_ns: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_strict_bucket_policy: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties to initialize an instance of ``MicroAppsSvcs``.

        :param app_env: Application environment, passed as ``NODE_ENV`` to the Router and Deployer Lambda functions.
        :param bucket_apps: S3 bucket for deployed applications.
        :param bucket_apps_oai: CloudFront Origin Access Identity for the deployed applications bucket.
        :param bucket_apps_staging: S3 bucket for staged applications (prior to deploy).
        :param http_api: API Gateway v2 HTTP for Router and app.
        :param asset_name_root: Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: Optional asset name suffix. Default: none
        :param removal_policy: RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: Path prefix on the root of the deployment. Default: none
        :param s3_policy_bypass_aro_as: Applies when using s3StrictBucketPolicy = true. AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy. This allows sessions that assume the IAM Role to be excluded from the DENY rules on the S3 Bucket Policy. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list. Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead. Note: This AROA must be specified to prevent this policy from locking out non-root sessions that have assumed the admin role. The notPrincipals will only match the role name exactly and will not match any session that has assumed the role since notPrincipals does not allow wildcard matches and does not do wildcard matches implicitly either. The AROA must be used because there are only 3 Principal variables available: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable aws:username, aws:userid, aws:PrincipalTag For an assumed role, aws:username is blank, aws:userid is: [unique id AKA AROA for Role]:[session name] Table of unique ID prefixes such as AROA: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes The name of the role is simply not available for an assumed role and, if it was, a complicated comparison would be requierd to prevent exclusion of applying the Deny Rule to roles from other accounts. To get the AROA with the AWS CLI: aws iam get-role --role-name ROLE-NAME aws iam get-user -–user-name USER-NAME
        :param s3_policy_bypass_principal_ar_ns: Applies when using s3StrictBucketPolicy = true. IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy. Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list.
        :param s3_strict_bucket_policy: Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version. This setting should be used when applications are less than fully trusted. Default: false
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_env": app_env,
            "bucket_apps": bucket_apps,
            "bucket_apps_oai": bucket_apps_oai,
            "bucket_apps_staging": bucket_apps_staging,
            "http_api": http_api,
        }
        if asset_name_root is not None:
            self._values["asset_name_root"] = asset_name_root
        if asset_name_suffix is not None:
            self._values["asset_name_suffix"] = asset_name_suffix
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if root_path_prefix is not None:
            self._values["root_path_prefix"] = root_path_prefix
        if s3_policy_bypass_aro_as is not None:
            self._values["s3_policy_bypass_aro_as"] = s3_policy_bypass_aro_as
        if s3_policy_bypass_principal_ar_ns is not None:
            self._values["s3_policy_bypass_principal_ar_ns"] = s3_policy_bypass_principal_ar_ns
        if s3_strict_bucket_policy is not None:
            self._values["s3_strict_bucket_policy"] = s3_strict_bucket_policy

    @builtins.property
    def app_env(self) -> builtins.str:
        '''Application environment, passed as ``NODE_ENV`` to the Router and Deployer Lambda functions.'''
        result = self._values.get("app_env")
        assert result is not None, "Required property 'app_env' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_apps(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for deployed applications.'''
        result = self._values.get("bucket_apps")
        assert result is not None, "Required property 'bucket_apps' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def bucket_apps_oai(self) -> aws_cdk.aws_cloudfront.OriginAccessIdentity:
        '''CloudFront Origin Access Identity for the deployed applications bucket.'''
        result = self._values.get("bucket_apps_oai")
        assert result is not None, "Required property 'bucket_apps_oai' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.OriginAccessIdentity, result)

    @builtins.property
    def bucket_apps_staging(self) -> aws_cdk.aws_s3.IBucket:
        '''S3 bucket for staged applications (prior to deploy).'''
        result = self._values.get("bucket_apps_staging")
        assert result is not None, "Required property 'bucket_apps_staging' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''API Gateway v2 HTTP for Router and app.'''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, result)

    @builtins.property
    def asset_name_root(self) -> typing.Optional[builtins.str]:
        '''Optional asset name root.

        :default: - resource names auto assigned

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''Optional asset name suffix.

        :default: none

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''Path prefix on the root of the deployment.

        :default: none

        Example::

            dev/
        '''
        result = self._values.get("root_path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_policy_bypass_aro_as(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Applies when using s3StrictBucketPolicy = true.

        AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy.
        This allows sessions that assume the IAM Role to be excluded from the
        DENY rules on the S3 Bucket Policy.

        Typically any admin roles / users that need to view or manage the S3 Bucket
        would be added to this list.

        Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead.

        Note: This AROA must be specified to prevent this policy from locking
        out non-root sessions that have assumed the admin role.

        The notPrincipals will only match the role name exactly and will not match
        any session that has assumed the role since notPrincipals does not allow
        wildcard matches and does not do wildcard matches implicitly either.

        The AROA must be used because there are only 3 Principal variables available:
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable
        aws:username, aws:userid, aws:PrincipalTag

        For an assumed role, aws:username is blank, aws:userid is:
        [unique id AKA AROA for Role]:[session name]

        Table of unique ID prefixes such as AROA:
        https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes

        The name of the role is simply not available for an assumed role and, if it was,
        a complicated comparison would be requierd to prevent exclusion
        of applying the Deny Rule to roles from other accounts.

        To get the AROA with the AWS CLI:
        aws iam get-role --role-name ROLE-NAME
        aws iam get-user -–user-name USER-NAME

        :see: s3StrictBucketPolicy

        Example::

            [ 'AROA1234567890123' ]
        '''
        result = self._values.get("s3_policy_bypass_aro_as")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_policy_bypass_principal_ar_ns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Applies when using s3StrictBucketPolicy = true.

        IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy.

        Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``.

        Typically any admin roles / users that need to view or manage the S3 Bucket
        would be added to this list.

        :see: s3PolicyBypassAROAs

        Example::

            ['arn:aws:iam::1234567890123:role/AdminAccess', 'arn:aws:iam::1234567890123:user/MyAdminUser']
        '''
        result = self._values.get("s3_policy_bypass_principal_ar_ns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_strict_bucket_policy(self) -> typing.Optional[builtins.bool]:
        '''Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version.

        This setting should be used when applications are less than
        fully trusted.

        :default: false
        '''
        result = self._values.get("s3_strict_bucket_policy")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicroAppsSvcsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AddRoutesOptions",
    "CreateAPIOriginPolicyOptions",
    "IMicroApps",
    "IMicroAppsAPIGwy",
    "IMicroAppsCF",
    "IMicroAppsS3",
    "IMicroAppsSvcs",
    "MicroApps",
    "MicroAppsAPIGwy",
    "MicroAppsAPIGwyProps",
    "MicroAppsCF",
    "MicroAppsCFProps",
    "MicroAppsProps",
    "MicroAppsS3",
    "MicroAppsS3Props",
    "MicroAppsSvcs",
    "MicroAppsSvcsProps",
]

publication.publish()
