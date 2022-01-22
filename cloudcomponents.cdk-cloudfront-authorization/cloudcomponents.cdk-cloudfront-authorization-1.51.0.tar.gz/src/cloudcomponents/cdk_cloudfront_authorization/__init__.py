'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-cloudfront-authorization

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-cloudfront-authorization)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-cloudfront-authorization/)
[![Mentioned in Awesome CDK](https://awesome.re/mentioned-badge.svg)](https://github.com/kolomied/awesome-cdk)

> CloudFront with Cognito authentication using Lambda@Edge

This construct is based on https://github.com/aws-samples/cloudfront-authorization-at-edge.

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-cloudfront-authorization
```

Python:

```bash
pip install cloudcomponents.cdk-cloudfront-authorization
```

## How to use SPA

```python
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { UserPool } from '@aws-cdk/aws-cognito';
import {
  SpaAuthorization,
  SpaDistribution,
} from '@cloudcomponents/cdk-cloudfront-authorization';

export class CloudFrontAuthorizationStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const userPool = new UserPool(this, 'UserPool', {
      selfSignUpEnabled: false,
      userPoolName: 'cloudfront-authorization-userpool',
    });

    // UserPool must have a domain!
    userPool.addDomain('Domain', {
      cognitoDomain: {
        domainPrefix: 'cloudcomponents',
      },
    });

    const authorization = new SpaAuthorization(this, 'Authorization', {
      userPool,
    });

    new SpaDistribution(this, 'Distribution', {
      authorization,
    });
  }
}
```

## How to use StaticSite

```python
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { UserPool } from '@aws-cdk/aws-cognito';
import {
  StaticSiteAuthorization,
  StaticSiteDistribution,
} from '@cloudcomponents/cdk-cloudfront-authorization';

export class CloudFrontAuthorizationStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const userPool = new UserPool(this, 'UserPool', {
      selfSignUpEnabled: false,
      userPoolName: 'cloudfront-authorization-userpool',
    });

    // UserPool must have a domain!
    userPool.addDomain('Domain', {
      cognitoDomain: {
        domainPrefix: 'cloudcomponents',
      },
    });

    const authorization = new StaticSiteAuthorization(this, 'Authorization', {
      userPool,
    });

    new StaticSiteDistribution(this, 'Distribution', {
      authorization,
    });
  }
}
```

## Legacy CloudFrontWebDistribution

```python
import { CloudFrontWebDistribution, OriginAccessIdentity } from '@aws-cdk/aws-cloudfront';
import { UserPool } from '@aws-cdk/aws-cognito';
import { Bucket } from '@aws-cdk/aws-s3'
import { Construct, Stack, StackProps, RemovalPolicy } from '@aws-cdk/core';
import { SpaAuthorization } from '@cloudcomponentscdk-cloudfront-authorization';

export class CloudFrontAuthorizationStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const userPool = new UserPool(this, 'UserPool', {
      selfSignUpEnabled: false,
      userPoolName: 'cloudfront-authorization-userpool',
    });

    userPool.addDomain('Domain', {
      cognitoDomain: {
        domainPrefix: 'cloudcomponents',
      },
    });

    const authorization = new SpaAuthorization(this, 'Authorization', {
      userPool,
    });

    const bucket = new Bucket(this, 'Bucket', {
      autoDeleteObjects: true,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const originAccessIdentity = new OriginAccessIdentity(this, 'OriginAccessIdentity', {
      comment: `CloudFront OriginAccessIdentity for ${bucket.bucketName}`,
    });

    new CloudFrontWebDistribution(this, 'Distribution', {
      originConfigs: [
        {
          s3OriginSource: {
            s3BucketSource: bucket,
            originAccessIdentity,
          },
          behaviors: [authorization.createLegacyDefaultBehavior(), ...authorization.createLegacyAdditionalBehaviors()],
        },
      ],
    });
  }
}
```

## Identity Providers

Identity providers can be specified in the authorization object. To make sure that the user pool client is created after the identity provider, please specify a dependency using "addDependency".

```python
const identityProvider = UserPoolIdentityProviderAmazon(this, "IdentityProvider", {
  // ...
})
const authorization = new SpaAuthorization(this, 'Authorization_SPA', {
  // ...
  identityProviders: [cognito.UserPoolClientIdentityProvider.AMAZON],
};
authorization.userPoolClient.node.addDependency(identityProvider);
```

## SPA mode vs. Static Site mode

### SPA

* User Pool client does not use a client secret
* The cookies with JWT's are not "http only", so that they can be read and used by the SPA (e.g. to display the user name, or to refresh tokens)
* 404's (page not found on S3) will return index.html, to enable SPA-routing

### Static Site

* Enforce use of a client secret
* Set cookies to be http only by default (unless you've provided other cookie settings explicitly)
* No special error handling

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-cloudfront-authorization/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-cloudfront-authorization/LICENSE)
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
import aws_cdk.aws_cloudfront
import aws_cdk.aws_cognito
import aws_cdk.aws_s3
import aws_cdk.core
import cloudcomponents.cdk_lambda_at_edge_pattern


class AuthFlow(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.AuthFlow",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cognito_auth_domain: builtins.str,
        cookie_settings: typing.Mapping[builtins.str, builtins.str],
        http_headers: typing.Mapping[builtins.str, builtins.str],
        log_level: cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel,
        nonce_signing_secret: builtins.str,
        oauth_scopes: typing.Sequence[aws_cdk.aws_cognito.OAuthScope],
        redirect_paths: "RedirectPaths",
        user_pool: aws_cdk.aws_cognito.IUserPool,
        user_pool_client: aws_cdk.aws_cognito.IUserPoolClient,
        client_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cognito_auth_domain: -
        :param cookie_settings: -
        :param http_headers: -
        :param log_level: -
        :param nonce_signing_secret: -
        :param oauth_scopes: -
        :param redirect_paths: -
        :param user_pool: -
        :param user_pool_client: -
        :param client_secret: -
        '''
        props = AuthFlowProps(
            cognito_auth_domain=cognito_auth_domain,
            cookie_settings=cookie_settings,
            http_headers=http_headers,
            log_level=log_level,
            nonce_signing_secret=nonce_signing_secret,
            oauth_scopes=oauth_scopes,
            redirect_paths=redirect_paths,
            user_pool=user_pool,
            user_pool_client=user_pool_client,
            client_secret=client_secret,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checkAuth")
    def check_auth(self) -> cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction:
        return typing.cast(cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction, jsii.get(self, "checkAuth"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpHeaders")
    def http_headers(self) -> cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction:
        return typing.cast(cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction, jsii.get(self, "httpHeaders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parseAuth")
    def parse_auth(self) -> cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction:
        return typing.cast(cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction, jsii.get(self, "parseAuth"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="refreshAuth")
    def refresh_auth(self) -> cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction:
        return typing.cast(cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction, jsii.get(self, "refreshAuth"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signOut")
    def sign_out(self) -> cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction:
        return typing.cast(cloudcomponents.cdk_lambda_at_edge_pattern.EdgeFunction, jsii.get(self, "signOut"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.AuthFlowProps",
    jsii_struct_bases=[],
    name_mapping={
        "cognito_auth_domain": "cognitoAuthDomain",
        "cookie_settings": "cookieSettings",
        "http_headers": "httpHeaders",
        "log_level": "logLevel",
        "nonce_signing_secret": "nonceSigningSecret",
        "oauth_scopes": "oauthScopes",
        "redirect_paths": "redirectPaths",
        "user_pool": "userPool",
        "user_pool_client": "userPoolClient",
        "client_secret": "clientSecret",
    },
)
class AuthFlowProps:
    def __init__(
        self,
        *,
        cognito_auth_domain: builtins.str,
        cookie_settings: typing.Mapping[builtins.str, builtins.str],
        http_headers: typing.Mapping[builtins.str, builtins.str],
        log_level: cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel,
        nonce_signing_secret: builtins.str,
        oauth_scopes: typing.Sequence[aws_cdk.aws_cognito.OAuthScope],
        redirect_paths: "RedirectPaths",
        user_pool: aws_cdk.aws_cognito.IUserPool,
        user_pool_client: aws_cdk.aws_cognito.IUserPoolClient,
        client_secret: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cognito_auth_domain: -
        :param cookie_settings: -
        :param http_headers: -
        :param log_level: -
        :param nonce_signing_secret: -
        :param oauth_scopes: -
        :param redirect_paths: -
        :param user_pool: -
        :param user_pool_client: -
        :param client_secret: -
        '''
        if isinstance(redirect_paths, dict):
            redirect_paths = RedirectPaths(**redirect_paths)
        self._values: typing.Dict[str, typing.Any] = {
            "cognito_auth_domain": cognito_auth_domain,
            "cookie_settings": cookie_settings,
            "http_headers": http_headers,
            "log_level": log_level,
            "nonce_signing_secret": nonce_signing_secret,
            "oauth_scopes": oauth_scopes,
            "redirect_paths": redirect_paths,
            "user_pool": user_pool,
            "user_pool_client": user_pool_client,
        }
        if client_secret is not None:
            self._values["client_secret"] = client_secret

    @builtins.property
    def cognito_auth_domain(self) -> builtins.str:
        result = self._values.get("cognito_auth_domain")
        assert result is not None, "Required property 'cognito_auth_domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cookie_settings(self) -> typing.Mapping[builtins.str, builtins.str]:
        result = self._values.get("cookie_settings")
        assert result is not None, "Required property 'cookie_settings' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def http_headers(self) -> typing.Mapping[builtins.str, builtins.str]:
        result = self._values.get("http_headers")
        assert result is not None, "Required property 'http_headers' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    @builtins.property
    def log_level(self) -> cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel:
        result = self._values.get("log_level")
        assert result is not None, "Required property 'log_level' is missing"
        return typing.cast(cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel, result)

    @builtins.property
    def nonce_signing_secret(self) -> builtins.str:
        result = self._values.get("nonce_signing_secret")
        assert result is not None, "Required property 'nonce_signing_secret' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def oauth_scopes(self) -> typing.List[aws_cdk.aws_cognito.OAuthScope]:
        result = self._values.get("oauth_scopes")
        assert result is not None, "Required property 'oauth_scopes' is missing"
        return typing.cast(typing.List[aws_cdk.aws_cognito.OAuthScope], result)

    @builtins.property
    def redirect_paths(self) -> "RedirectPaths":
        result = self._values.get("redirect_paths")
        assert result is not None, "Required property 'redirect_paths' is missing"
        return typing.cast("RedirectPaths", result)

    @builtins.property
    def user_pool(self) -> aws_cdk.aws_cognito.IUserPool:
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(aws_cdk.aws_cognito.IUserPool, result)

    @builtins.property
    def user_pool_client(self) -> aws_cdk.aws_cognito.IUserPoolClient:
        result = self._values.get("user_pool_client")
        assert result is not None, "Required property 'user_pool_client' is missing"
        return typing.cast(aws_cdk.aws_cognito.IUserPoolClient, result)

    @builtins.property
    def client_secret(self) -> typing.Optional[builtins.str]:
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthFlowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Authorization(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.Authorization",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        user_pool: aws_cdk.aws_cognito.IUserPool,
        cookie_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        http_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_providers: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.UserPoolClientIdentityProvider]] = None,
        log_level: typing.Optional[cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel] = None,
        oauth_scopes: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.OAuthScope]] = None,
        redirect_paths: typing.Optional["RedirectPaths"] = None,
        sign_out_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param user_pool: -
        :param cookie_settings: -
        :param http_headers: -
        :param identity_providers: -
        :param log_level: -
        :param oauth_scopes: -
        :param redirect_paths: -
        :param sign_out_url: -
        '''
        props = AuthorizationProps(
            user_pool=user_pool,
            cookie_settings=cookie_settings,
            http_headers=http_headers,
            identity_providers=identity_providers,
            log_level=log_level,
            oauth_scopes=oauth_scopes,
            redirect_paths=redirect_paths,
            sign_out_url=sign_out_url,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createAdditionalBehaviors")
    def create_additional_behaviors(
        self,
        origin: aws_cdk.aws_cloudfront.IOrigin,
        *,
        allowed_methods: typing.Optional[aws_cdk.aws_cloudfront.AllowedMethods] = None,
        cached_methods: typing.Optional[aws_cdk.aws_cloudfront.CachedMethods] = None,
        cache_policy: typing.Optional[aws_cdk.aws_cloudfront.ICachePolicy] = None,
        compress: typing.Optional[builtins.bool] = None,
        edge_lambdas: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.EdgeLambda]] = None,
        function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.FunctionAssociation]] = None,
        origin_request_policy: typing.Optional[aws_cdk.aws_cloudfront.IOriginRequestPolicy] = None,
        response_headers_policy: typing.Optional[aws_cdk.aws_cloudfront.IResponseHeadersPolicy] = None,
        smooth_streaming: typing.Optional[builtins.bool] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.IKeyGroup]] = None,
        viewer_protocol_policy: typing.Optional[aws_cdk.aws_cloudfront.ViewerProtocolPolicy] = None,
    ) -> typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions]:
        '''
        :param origin: -
        :param allowed_methods: HTTP methods to allow for this behavior. Default: AllowedMethods.ALLOW_GET_HEAD
        :param cached_methods: HTTP methods to cache for this behavior. Default: CachedMethods.CACHE_GET_HEAD
        :param cache_policy: The cache policy for this behavior. The cache policy determines what values are included in the cache key, and the time-to-live (TTL) values for the cache. Default: CachePolicy.CACHING_OPTIMIZED
        :param compress: Whether you want CloudFront to automatically compress certain files for this cache behavior. See https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ServingCompressedFiles.html#compressed-content-cloudfront-file-types for file types CloudFront will compress. Default: true
        :param edge_lambdas: The Lambda@Edge functions to invoke before serving the contents. Default: - no Lambda functions will be invoked
        :param function_associations: The CloudFront functions to invoke before serving the contents. Default: - no functions will be invoked
        :param origin_request_policy: The origin request policy for this behavior. The origin request policy determines which values (e.g., headers, cookies) are included in requests that CloudFront sends to the origin. Default: - none
        :param response_headers_policy: The response headers policy for this behavior. The response headers policy determines which headers are included in responses Default: - none
        :param smooth_streaming: Set this to true to indicate you want to distribute media files in the Microsoft Smooth Streaming format using this behavior. Default: false
        :param trusted_key_groups: A list of Key Groups that CloudFront can use to validate signed URLs or signed cookies. Default: - no KeyGroups are associated with cache behavior
        :param viewer_protocol_policy: The protocol that viewers can use to access the files controlled by this behavior. Default: ViewerProtocolPolicy.ALLOW_ALL
        '''
        options = aws_cdk.aws_cloudfront.AddBehaviorOptions(
            allowed_methods=allowed_methods,
            cached_methods=cached_methods,
            cache_policy=cache_policy,
            compress=compress,
            edge_lambdas=edge_lambdas,
            function_associations=function_associations,
            origin_request_policy=origin_request_policy,
            response_headers_policy=response_headers_policy,
            smooth_streaming=smooth_streaming,
            trusted_key_groups=trusted_key_groups,
            viewer_protocol_policy=viewer_protocol_policy,
        )

        return typing.cast(typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions], jsii.invoke(self, "createAdditionalBehaviors", [origin, options]))

    @jsii.member(jsii_name="createAuthFlow") # type: ignore[misc]
    @abc.abstractmethod
    def _create_auth_flow(
        self,
        log_level: cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel,
    ) -> AuthFlow:
        '''
        :param log_level: -
        '''
        ...

    @jsii.member(jsii_name="createDefaultBehavior")
    def create_default_behavior(
        self,
        origin: aws_cdk.aws_cloudfront.IOrigin,
        *,
        allowed_methods: typing.Optional[aws_cdk.aws_cloudfront.AllowedMethods] = None,
        cached_methods: typing.Optional[aws_cdk.aws_cloudfront.CachedMethods] = None,
        cache_policy: typing.Optional[aws_cdk.aws_cloudfront.ICachePolicy] = None,
        compress: typing.Optional[builtins.bool] = None,
        edge_lambdas: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.EdgeLambda]] = None,
        function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.FunctionAssociation]] = None,
        origin_request_policy: typing.Optional[aws_cdk.aws_cloudfront.IOriginRequestPolicy] = None,
        response_headers_policy: typing.Optional[aws_cdk.aws_cloudfront.IResponseHeadersPolicy] = None,
        smooth_streaming: typing.Optional[builtins.bool] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.IKeyGroup]] = None,
        viewer_protocol_policy: typing.Optional[aws_cdk.aws_cloudfront.ViewerProtocolPolicy] = None,
    ) -> aws_cdk.aws_cloudfront.BehaviorOptions:
        '''
        :param origin: -
        :param allowed_methods: HTTP methods to allow for this behavior. Default: AllowedMethods.ALLOW_GET_HEAD
        :param cached_methods: HTTP methods to cache for this behavior. Default: CachedMethods.CACHE_GET_HEAD
        :param cache_policy: The cache policy for this behavior. The cache policy determines what values are included in the cache key, and the time-to-live (TTL) values for the cache. Default: CachePolicy.CACHING_OPTIMIZED
        :param compress: Whether you want CloudFront to automatically compress certain files for this cache behavior. See https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ServingCompressedFiles.html#compressed-content-cloudfront-file-types for file types CloudFront will compress. Default: true
        :param edge_lambdas: The Lambda@Edge functions to invoke before serving the contents. Default: - no Lambda functions will be invoked
        :param function_associations: The CloudFront functions to invoke before serving the contents. Default: - no functions will be invoked
        :param origin_request_policy: The origin request policy for this behavior. The origin request policy determines which values (e.g., headers, cookies) are included in requests that CloudFront sends to the origin. Default: - none
        :param response_headers_policy: The response headers policy for this behavior. The response headers policy determines which headers are included in responses Default: - none
        :param smooth_streaming: Set this to true to indicate you want to distribute media files in the Microsoft Smooth Streaming format using this behavior. Default: false
        :param trusted_key_groups: A list of Key Groups that CloudFront can use to validate signed URLs or signed cookies. Default: - no KeyGroups are associated with cache behavior
        :param viewer_protocol_policy: The protocol that viewers can use to access the files controlled by this behavior. Default: ViewerProtocolPolicy.ALLOW_ALL
        '''
        options = aws_cdk.aws_cloudfront.AddBehaviorOptions(
            allowed_methods=allowed_methods,
            cached_methods=cached_methods,
            cache_policy=cache_policy,
            compress=compress,
            edge_lambdas=edge_lambdas,
            function_associations=function_associations,
            origin_request_policy=origin_request_policy,
            response_headers_policy=response_headers_policy,
            smooth_streaming=smooth_streaming,
            trusted_key_groups=trusted_key_groups,
            viewer_protocol_policy=viewer_protocol_policy,
        )

        return typing.cast(aws_cdk.aws_cloudfront.BehaviorOptions, jsii.invoke(self, "createDefaultBehavior", [origin, options]))

    @jsii.member(jsii_name="createLegacyAdditionalBehaviors")
    def create_legacy_additional_behaviors(
        self,
        *,
        allowed_methods: typing.Optional[aws_cdk.aws_cloudfront.CloudFrontAllowedMethods] = None,
        cached_methods: typing.Optional[aws_cdk.aws_cloudfront.CloudFrontAllowedCachedMethods] = None,
        compress: typing.Optional[builtins.bool] = None,
        default_ttl: typing.Optional[aws_cdk.core.Duration] = None,
        forwarded_values: typing.Optional[aws_cdk.aws_cloudfront.CfnDistribution.ForwardedValuesProperty] = None,
        function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.FunctionAssociation]] = None,
        is_default_behavior: typing.Optional[builtins.bool] = None,
        lambda_function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.LambdaFunctionAssociation]] = None,
        max_ttl: typing.Optional[aws_cdk.core.Duration] = None,
        min_ttl: typing.Optional[aws_cdk.core.Duration] = None,
        path_pattern: typing.Optional[builtins.str] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.IKeyGroup]] = None,
        trusted_signers: typing.Optional[typing.Sequence[builtins.str]] = None,
        viewer_protocol_policy: typing.Optional[aws_cdk.aws_cloudfront.ViewerProtocolPolicy] = None,
    ) -> typing.List[aws_cdk.aws_cloudfront.Behavior]:
        '''
        :param allowed_methods: The method this CloudFront distribution responds do. Default: GET_HEAD
        :param cached_methods: Which methods are cached by CloudFront by default. Default: GET_HEAD
        :param compress: If CloudFront should automatically compress some content types. Default: true
        :param default_ttl: The default amount of time CloudFront will cache an object. This value applies only when your custom origin does not add HTTP headers, such as Cache-Control max-age, Cache-Control s-maxage, and Expires to objects. Default: 86400 (1 day)
        :param forwarded_values: The values CloudFront will forward to the origin when making a request. Default: none (no cookies - no headers)
        :param function_associations: The CloudFront functions to invoke before serving the contents. Default: - no functions will be invoked
        :param is_default_behavior: If this behavior is the default behavior for the distribution. You must specify exactly one default distribution per CloudFront distribution. The default behavior is allowed to omit the "path" property.
        :param lambda_function_associations: Declares associated lambda@edge functions for this distribution behaviour. Default: No lambda function associated
        :param max_ttl: The max amount of time you want objects to stay in the cache before CloudFront queries your origin. Default: Duration.seconds(31536000) (one year)
        :param min_ttl: The minimum amount of time that you want objects to stay in the cache before CloudFront queries your origin.
        :param path_pattern: The path this behavior responds to. Required for all non-default behaviors. (The default behavior implicitly has "*" as the path pattern. )
        :param trusted_key_groups: A list of Key Groups that CloudFront can use to validate signed URLs or signed cookies. Default: - no KeyGroups are associated with cache behavior
        :param trusted_signers: (deprecated) Trusted signers is how CloudFront allows you to serve private content. The signers are the account IDs that are allowed to sign cookies/presigned URLs for this distribution. If you pass a non empty value, all requests for this behavior must be signed (no public access will be allowed)
        :param viewer_protocol_policy: The viewer policy for this behavior. Default: - the distribution wide viewer protocol policy will be used
        '''
        options = aws_cdk.aws_cloudfront.Behavior(
            allowed_methods=allowed_methods,
            cached_methods=cached_methods,
            compress=compress,
            default_ttl=default_ttl,
            forwarded_values=forwarded_values,
            function_associations=function_associations,
            is_default_behavior=is_default_behavior,
            lambda_function_associations=lambda_function_associations,
            max_ttl=max_ttl,
            min_ttl=min_ttl,
            path_pattern=path_pattern,
            trusted_key_groups=trusted_key_groups,
            trusted_signers=trusted_signers,
            viewer_protocol_policy=viewer_protocol_policy,
        )

        return typing.cast(typing.List[aws_cdk.aws_cloudfront.Behavior], jsii.invoke(self, "createLegacyAdditionalBehaviors", [options]))

    @jsii.member(jsii_name="createLegacyDefaultBehavior")
    def create_legacy_default_behavior(
        self,
        *,
        allowed_methods: typing.Optional[aws_cdk.aws_cloudfront.CloudFrontAllowedMethods] = None,
        cached_methods: typing.Optional[aws_cdk.aws_cloudfront.CloudFrontAllowedCachedMethods] = None,
        compress: typing.Optional[builtins.bool] = None,
        default_ttl: typing.Optional[aws_cdk.core.Duration] = None,
        forwarded_values: typing.Optional[aws_cdk.aws_cloudfront.CfnDistribution.ForwardedValuesProperty] = None,
        function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.FunctionAssociation]] = None,
        is_default_behavior: typing.Optional[builtins.bool] = None,
        lambda_function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.LambdaFunctionAssociation]] = None,
        max_ttl: typing.Optional[aws_cdk.core.Duration] = None,
        min_ttl: typing.Optional[aws_cdk.core.Duration] = None,
        path_pattern: typing.Optional[builtins.str] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.IKeyGroup]] = None,
        trusted_signers: typing.Optional[typing.Sequence[builtins.str]] = None,
        viewer_protocol_policy: typing.Optional[aws_cdk.aws_cloudfront.ViewerProtocolPolicy] = None,
    ) -> aws_cdk.aws_cloudfront.Behavior:
        '''
        :param allowed_methods: The method this CloudFront distribution responds do. Default: GET_HEAD
        :param cached_methods: Which methods are cached by CloudFront by default. Default: GET_HEAD
        :param compress: If CloudFront should automatically compress some content types. Default: true
        :param default_ttl: The default amount of time CloudFront will cache an object. This value applies only when your custom origin does not add HTTP headers, such as Cache-Control max-age, Cache-Control s-maxage, and Expires to objects. Default: 86400 (1 day)
        :param forwarded_values: The values CloudFront will forward to the origin when making a request. Default: none (no cookies - no headers)
        :param function_associations: The CloudFront functions to invoke before serving the contents. Default: - no functions will be invoked
        :param is_default_behavior: If this behavior is the default behavior for the distribution. You must specify exactly one default distribution per CloudFront distribution. The default behavior is allowed to omit the "path" property.
        :param lambda_function_associations: Declares associated lambda@edge functions for this distribution behaviour. Default: No lambda function associated
        :param max_ttl: The max amount of time you want objects to stay in the cache before CloudFront queries your origin. Default: Duration.seconds(31536000) (one year)
        :param min_ttl: The minimum amount of time that you want objects to stay in the cache before CloudFront queries your origin.
        :param path_pattern: The path this behavior responds to. Required for all non-default behaviors. (The default behavior implicitly has "*" as the path pattern. )
        :param trusted_key_groups: A list of Key Groups that CloudFront can use to validate signed URLs or signed cookies. Default: - no KeyGroups are associated with cache behavior
        :param trusted_signers: (deprecated) Trusted signers is how CloudFront allows you to serve private content. The signers are the account IDs that are allowed to sign cookies/presigned URLs for this distribution. If you pass a non empty value, all requests for this behavior must be signed (no public access will be allowed)
        :param viewer_protocol_policy: The viewer policy for this behavior. Default: - the distribution wide viewer protocol policy will be used
        '''
        options = aws_cdk.aws_cloudfront.Behavior(
            allowed_methods=allowed_methods,
            cached_methods=cached_methods,
            compress=compress,
            default_ttl=default_ttl,
            forwarded_values=forwarded_values,
            function_associations=function_associations,
            is_default_behavior=is_default_behavior,
            lambda_function_associations=lambda_function_associations,
            max_ttl=max_ttl,
            min_ttl=min_ttl,
            path_pattern=path_pattern,
            trusted_key_groups=trusted_key_groups,
            trusted_signers=trusted_signers,
            viewer_protocol_policy=viewer_protocol_policy,
        )

        return typing.cast(aws_cdk.aws_cloudfront.Behavior, jsii.invoke(self, "createLegacyDefaultBehavior", [options]))

    @jsii.member(jsii_name="createUserPoolClient") # type: ignore[misc]
    @abc.abstractmethod
    def _create_user_pool_client(self) -> aws_cdk.aws_cognito.IUserPoolClient:
        ...

    @jsii.member(jsii_name="updateUserPoolClientCallbacks")
    def update_user_pool_client_callbacks(
        self,
        *,
        callback_urls: typing.Sequence[builtins.str],
        logout_urls: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param callback_urls: A list of allowed redirect (callback) URLs for the identity providers.
        :param logout_urls: A list of allowed logout URLs for the identity providers.
        '''
        redirects = UserPoolClientCallbackUrls(
            callback_urls=callback_urls, logout_urls=logout_urls
        )

        return typing.cast(None, jsii.invoke(self, "updateUserPoolClientCallbacks", [redirects]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authFlow")
    def auth_flow(self) -> AuthFlow:
        return typing.cast(AuthFlow, jsii.get(self, "authFlow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cognitoAuthDomain")
    def _cognito_auth_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cognitoAuthDomain"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpHeaders")
    def _http_headers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "httpHeaders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityProviders")
    def _identity_providers(
        self,
    ) -> typing.List[aws_cdk.aws_cognito.UserPoolClientIdentityProvider]:
        return typing.cast(typing.List[aws_cdk.aws_cognito.UserPoolClientIdentityProvider], jsii.get(self, "identityProviders"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nonceSigningSecret")
    def _nonce_signing_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nonceSigningSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="oauthScopes")
    def _oauth_scopes(self) -> typing.List[aws_cdk.aws_cognito.OAuthScope]:
        return typing.cast(typing.List[aws_cdk.aws_cognito.OAuthScope], jsii.get(self, "oauthScopes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redirectPaths")
    def redirect_paths(self) -> "RedirectPaths":
        return typing.cast("RedirectPaths", jsii.get(self, "redirectPaths"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signOutUrlPath")
    def sign_out_url_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signOutUrlPath"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPool")
    def _user_pool(self) -> aws_cdk.aws_cognito.IUserPool:
        return typing.cast(aws_cdk.aws_cognito.IUserPool, jsii.get(self, "userPool"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userPoolClient")
    def user_pool_client(self) -> aws_cdk.aws_cognito.IUserPoolClient:
        return typing.cast(aws_cdk.aws_cognito.IUserPoolClient, jsii.get(self, "userPoolClient"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cookieSettings")
    def _cookie_settings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "cookieSettings"))


class _AuthorizationProxy(Authorization):
    @jsii.member(jsii_name="createAuthFlow")
    def _create_auth_flow(
        self,
        log_level: cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel,
    ) -> AuthFlow:
        '''
        :param log_level: -
        '''
        return typing.cast(AuthFlow, jsii.invoke(self, "createAuthFlow", [log_level]))

    @jsii.member(jsii_name="createUserPoolClient")
    def _create_user_pool_client(self) -> aws_cdk.aws_cognito.IUserPoolClient:
        return typing.cast(aws_cdk.aws_cognito.IUserPoolClient, jsii.invoke(self, "createUserPoolClient", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Authorization).__jsii_proxy_class__ = lambda : _AuthorizationProxy


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.AuthorizationProps",
    jsii_struct_bases=[],
    name_mapping={
        "user_pool": "userPool",
        "cookie_settings": "cookieSettings",
        "http_headers": "httpHeaders",
        "identity_providers": "identityProviders",
        "log_level": "logLevel",
        "oauth_scopes": "oauthScopes",
        "redirect_paths": "redirectPaths",
        "sign_out_url": "signOutUrl",
    },
)
class AuthorizationProps:
    def __init__(
        self,
        *,
        user_pool: aws_cdk.aws_cognito.IUserPool,
        cookie_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        http_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_providers: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.UserPoolClientIdentityProvider]] = None,
        log_level: typing.Optional[cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel] = None,
        oauth_scopes: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.OAuthScope]] = None,
        redirect_paths: typing.Optional["RedirectPaths"] = None,
        sign_out_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param user_pool: -
        :param cookie_settings: -
        :param http_headers: -
        :param identity_providers: -
        :param log_level: -
        :param oauth_scopes: -
        :param redirect_paths: -
        :param sign_out_url: -
        '''
        if isinstance(redirect_paths, dict):
            redirect_paths = RedirectPaths(**redirect_paths)
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool": user_pool,
        }
        if cookie_settings is not None:
            self._values["cookie_settings"] = cookie_settings
        if http_headers is not None:
            self._values["http_headers"] = http_headers
        if identity_providers is not None:
            self._values["identity_providers"] = identity_providers
        if log_level is not None:
            self._values["log_level"] = log_level
        if oauth_scopes is not None:
            self._values["oauth_scopes"] = oauth_scopes
        if redirect_paths is not None:
            self._values["redirect_paths"] = redirect_paths
        if sign_out_url is not None:
            self._values["sign_out_url"] = sign_out_url

    @builtins.property
    def user_pool(self) -> aws_cdk.aws_cognito.IUserPool:
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(aws_cdk.aws_cognito.IUserPool, result)

    @builtins.property
    def cookie_settings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("cookie_settings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def http_headers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("http_headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def identity_providers(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cognito.UserPoolClientIdentityProvider]]:
        result = self._values.get("identity_providers")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cognito.UserPoolClientIdentityProvider]], result)

    @builtins.property
    def log_level(
        self,
    ) -> typing.Optional[cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel]:
        result = self._values.get("log_level")
        return typing.cast(typing.Optional[cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel], result)

    @builtins.property
    def oauth_scopes(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cognito.OAuthScope]]:
        result = self._values.get("oauth_scopes")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cognito.OAuthScope]], result)

    @builtins.property
    def redirect_paths(self) -> typing.Optional["RedirectPaths"]:
        result = self._values.get("redirect_paths")
        return typing.cast(typing.Optional["RedirectPaths"], result)

    @builtins.property
    def sign_out_url(self) -> typing.Optional[builtins.str]:
        result = self._values.get("sign_out_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthorizationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_cloudfront.IDistribution)
class BaseDistribution(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.BaseDistribution",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        authorization: "IAuthorization",
        error_responses: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.ErrorResponse]] = None,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        comment: typing.Optional[builtins.str] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        geo_restriction: typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction] = None,
        http_version: typing.Optional[aws_cdk.aws_cloudfront.HttpVersion] = None,
        log_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        log_file_prefix: typing.Optional[builtins.str] = None,
        log_includes_cookies: typing.Optional[builtins.bool] = None,
        minimum_protocol_version: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        origin: typing.Optional[aws_cdk.aws_cloudfront.IOrigin] = None,
        price_class: typing.Optional[aws_cdk.aws_cloudfront.PriceClass] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param authorization: -
        :param error_responses: -
        :param certificate: A certificate to associate with the distribution. The certificate must be located in N. Virginia (us-east-1). Default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        :param comment: Any comments you want to include about the distribution. Default: - no comment
        :param default_root_object: The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/). Default: - index.html
        :param domain_names: Alternative domain names for this distribution. If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name, you can add an alternate domain name to your distribution. If you attach a certificate to the distribution, you must add (at least one of) the domain names of the certificate to this list. Default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        :param enabled: Enable or disable the distribution. Default: true
        :param enable_ipv6: Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address. If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses. This allows viewers to submit a second request, for an IPv4 address for your distribution. Default: true
        :param enable_logging: Enable access logging for the distribution. Default: - false, unless ``logBucket`` is specified.
        :param geo_restriction: Controls the countries in which your content is distributed. Default: - No geographic restrictions
        :param http_version: Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront. For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI). Default: HttpVersion.HTTP2
        :param log_bucket: The Amazon S3 bucket to store the access logs in. Default: - A bucket is created if ``enableLogging`` is true
        :param log_file_prefix: An optional string that you want CloudFront to prefix to the access log filenames for this distribution. Default: - no prefix
        :param log_includes_cookies: Specifies whether you want CloudFront to include cookies in access logs. Default: false
        :param minimum_protocol_version: The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: SecurityPolicyProtocol.TLS_V1_2_2019
        :param origin: The origin that you want CloudFront to route requests.
        :param price_class: The price class that corresponds with the maximum price that you want to pay for CloudFront service. If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations. If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location that has the lowest latency among the edge locations in your price class. Default: PriceClass.PRICE_CLASS_100
        :param removal_policy: Default: Destroy
        :param web_acl_id: Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution. To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``. Default: - No AWS Web Application Firewall web access control list (web ACL).
        '''
        props = BaseDistributionProps(
            authorization=authorization,
            error_responses=error_responses,
            certificate=certificate,
            comment=comment,
            default_root_object=default_root_object,
            domain_names=domain_names,
            enabled=enabled,
            enable_ipv6=enable_ipv6,
            enable_logging=enable_logging,
            geo_restriction=geo_restriction,
            http_version=http_version,
            log_bucket=log_bucket,
            log_file_prefix=log_file_prefix,
            log_includes_cookies=log_includes_cookies,
            minimum_protocol_version=minimum_protocol_version,
            origin=origin,
            price_class=price_class,
            removal_policy=removal_policy,
            web_acl_id=web_acl_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="applyRemovalPolicy")
    def apply_removal_policy(self, policy: aws_cdk.core.RemovalPolicy) -> None:
        '''Apply the given removal policy to this resource.

        The Removal Policy controls what happens to this resource when it stops
        being managed by CloudFormation, either because you've removed it from the
        CDK application or because you've made a change that requires the resource
        to be replaced.

        The resource can be deleted (``RemovalPolicy.DESTROY``), or left in your AWS
        account for data recovery and cleanup later (``RemovalPolicy.RETAIN``).

        :param policy: -
        '''
        return typing.cast(None, jsii.invoke(self, "applyRemovalPolicy", [policy]))

    @jsii.member(jsii_name="renderAdditionalBehaviors")
    def _render_additional_behaviors(
        self,
        origin: aws_cdk.aws_cloudfront.IOrigin,
        authorization: "IAuthorization",
    ) -> typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions]:
        '''
        :param origin: -
        :param authorization: -
        '''
        return typing.cast(typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions], jsii.invoke(self, "renderAdditionalBehaviors", [origin, authorization]))

    @jsii.member(jsii_name="renderDefaultBehaviour")
    def _render_default_behaviour(
        self,
        origin: aws_cdk.aws_cloudfront.IOrigin,
        authorization: "IAuthorization",
    ) -> aws_cdk.aws_cloudfront.BehaviorOptions:
        '''
        :param origin: -
        :param authorization: -
        '''
        return typing.cast(aws_cdk.aws_cloudfront.BehaviorOptions, jsii.invoke(self, "renderDefaultBehaviour", [origin, authorization]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionDomainName")
    def distribution_domain_name(self) -> builtins.str:
        '''The domain name of the Distribution, such as d111111abcdef8.cloudfront.net.'''
        return typing.cast(builtins.str, jsii.get(self, "distributionDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distributionId")
    def distribution_id(self) -> builtins.str:
        '''The distribution ID for this distribution.'''
        return typing.cast(builtins.str, jsii.get(self, "distributionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''(deprecated) The domain name of the Distribution, such as d111111abcdef8.cloudfront.net.'''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> aws_cdk.core.ResourceEnvironment:
        '''The environment this resource belongs to.

        For resources that are created and managed by the CDK
        (generally, those created by creating new class instances like Role, Bucket, etc.),
        this is always the same as the environment of the stack they belong to;
        however, for imported resources
        (those obtained from static methods like fromRoleArn, fromBucketName, etc.),
        that might be different than the stack they were imported into.
        '''
        return typing.cast(aws_cdk.core.ResourceEnvironment, jsii.get(self, "env"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stack")
    def stack(self) -> aws_cdk.core.Stack:
        '''The stack in which this resource is defined.'''
        return typing.cast(aws_cdk.core.Stack, jsii.get(self, "stack"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.CommonDistributionProps",
    jsii_struct_bases=[],
    name_mapping={
        "certificate": "certificate",
        "comment": "comment",
        "default_root_object": "defaultRootObject",
        "domain_names": "domainNames",
        "enabled": "enabled",
        "enable_ipv6": "enableIpv6",
        "enable_logging": "enableLogging",
        "geo_restriction": "geoRestriction",
        "http_version": "httpVersion",
        "log_bucket": "logBucket",
        "log_file_prefix": "logFilePrefix",
        "log_includes_cookies": "logIncludesCookies",
        "minimum_protocol_version": "minimumProtocolVersion",
        "origin": "origin",
        "price_class": "priceClass",
        "removal_policy": "removalPolicy",
        "web_acl_id": "webAclId",
    },
)
class CommonDistributionProps:
    def __init__(
        self,
        *,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        comment: typing.Optional[builtins.str] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        geo_restriction: typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction] = None,
        http_version: typing.Optional[aws_cdk.aws_cloudfront.HttpVersion] = None,
        log_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        log_file_prefix: typing.Optional[builtins.str] = None,
        log_includes_cookies: typing.Optional[builtins.bool] = None,
        minimum_protocol_version: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        origin: typing.Optional[aws_cdk.aws_cloudfront.IOrigin] = None,
        price_class: typing.Optional[aws_cdk.aws_cloudfront.PriceClass] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param certificate: A certificate to associate with the distribution. The certificate must be located in N. Virginia (us-east-1). Default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        :param comment: Any comments you want to include about the distribution. Default: - no comment
        :param default_root_object: The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/). Default: - index.html
        :param domain_names: Alternative domain names for this distribution. If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name, you can add an alternate domain name to your distribution. If you attach a certificate to the distribution, you must add (at least one of) the domain names of the certificate to this list. Default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        :param enabled: Enable or disable the distribution. Default: true
        :param enable_ipv6: Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address. If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses. This allows viewers to submit a second request, for an IPv4 address for your distribution. Default: true
        :param enable_logging: Enable access logging for the distribution. Default: - false, unless ``logBucket`` is specified.
        :param geo_restriction: Controls the countries in which your content is distributed. Default: - No geographic restrictions
        :param http_version: Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront. For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI). Default: HttpVersion.HTTP2
        :param log_bucket: The Amazon S3 bucket to store the access logs in. Default: - A bucket is created if ``enableLogging`` is true
        :param log_file_prefix: An optional string that you want CloudFront to prefix to the access log filenames for this distribution. Default: - no prefix
        :param log_includes_cookies: Specifies whether you want CloudFront to include cookies in access logs. Default: false
        :param minimum_protocol_version: The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: SecurityPolicyProtocol.TLS_V1_2_2019
        :param origin: The origin that you want CloudFront to route requests.
        :param price_class: The price class that corresponds with the maximum price that you want to pay for CloudFront service. If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations. If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location that has the lowest latency among the edge locations in your price class. Default: PriceClass.PRICE_CLASS_100
        :param removal_policy: Default: Destroy
        :param web_acl_id: Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution. To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``. Default: - No AWS Web Application Firewall web access control list (web ACL).
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if certificate is not None:
            self._values["certificate"] = certificate
        if comment is not None:
            self._values["comment"] = comment
        if default_root_object is not None:
            self._values["default_root_object"] = default_root_object
        if domain_names is not None:
            self._values["domain_names"] = domain_names
        if enabled is not None:
            self._values["enabled"] = enabled
        if enable_ipv6 is not None:
            self._values["enable_ipv6"] = enable_ipv6
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if geo_restriction is not None:
            self._values["geo_restriction"] = geo_restriction
        if http_version is not None:
            self._values["http_version"] = http_version
        if log_bucket is not None:
            self._values["log_bucket"] = log_bucket
        if log_file_prefix is not None:
            self._values["log_file_prefix"] = log_file_prefix
        if log_includes_cookies is not None:
            self._values["log_includes_cookies"] = log_includes_cookies
        if minimum_protocol_version is not None:
            self._values["minimum_protocol_version"] = minimum_protocol_version
        if origin is not None:
            self._values["origin"] = origin
        if price_class is not None:
            self._values["price_class"] = price_class
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if web_acl_id is not None:
            self._values["web_acl_id"] = web_acl_id

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''A certificate to associate with the distribution.

        The certificate must be located in N. Virginia (us-east-1).

        :default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Any comments you want to include about the distribution.

        :default: - no comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_root_object(self) -> typing.Optional[builtins.str]:
        '''The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/).

        :default: - index.html
        '''
        result = self._values.get("default_root_object")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Alternative domain names for this distribution.

        If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name,
        you can add an alternate domain name to your distribution. If you attach a certificate to the distribution,
        you must add (at least one of) the domain names of the certificate to this list.

        :default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        '''
        result = self._values.get("domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable or disable the distribution.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_ipv6(self) -> typing.Optional[builtins.bool]:
        '''Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address.

        If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses.
        This allows viewers to submit a second request, for an IPv4 address for your distribution.

        :default: true
        '''
        result = self._values.get("enable_ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''Enable access logging for the distribution.

        :default: - false, unless ``logBucket`` is specified.
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def geo_restriction(self) -> typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction]:
        '''Controls the countries in which your content is distributed.

        :default: - No geographic restrictions
        '''
        result = self._values.get("geo_restriction")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction], result)

    @builtins.property
    def http_version(self) -> typing.Optional[aws_cdk.aws_cloudfront.HttpVersion]:
        '''Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront.

        For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI).

        :default: HttpVersion.HTTP2
        '''
        result = self._values.get("http_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.HttpVersion], result)

    @builtins.property
    def log_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''The Amazon S3 bucket to store the access logs in.

        :default: - A bucket is created if ``enableLogging`` is true
        '''
        result = self._values.get("log_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def log_file_prefix(self) -> typing.Optional[builtins.str]:
        '''An optional string that you want CloudFront to prefix to the access log filenames for this distribution.

        :default: - no prefix
        '''
        result = self._values.get("log_file_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_includes_cookies(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether you want CloudFront to include cookies in access logs.

        :default: false
        '''
        result = self._values.get("log_includes_cookies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def minimum_protocol_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol]:
        '''The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections.

        CloudFront serves your objects only to browsers or devices that support at
        least the SSL version that you specify.

        :default: SecurityPolicyProtocol.TLS_V1_2_2019
        '''
        result = self._values.get("minimum_protocol_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol], result)

    @builtins.property
    def origin(self) -> typing.Optional[aws_cdk.aws_cloudfront.IOrigin]:
        '''The origin that you want CloudFront to route requests.'''
        result = self._values.get("origin")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.IOrigin], result)

    @builtins.property
    def price_class(self) -> typing.Optional[aws_cdk.aws_cloudfront.PriceClass]:
        '''The price class that corresponds with the maximum price that you want to pay for CloudFront service.

        If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations.
        If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location
        that has the lowest latency among the edge locations in your price class.

        :default: PriceClass.PRICE_CLASS_100
        '''
        result = self._values.get("price_class")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.PriceClass], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''
        :default: Destroy
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def web_acl_id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution.

        To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example
        ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``.
        To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``.

        :default: - No AWS Web Application Firewall web access control list (web ACL).

        :see: https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CreateDistribution.html#API_CreateDistribution_RequestParameters.
        '''
        result = self._values.get("web_acl_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonDistributionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.IAuthorization"
)
class IAuthorization(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redirectPaths")
    def redirect_paths(self) -> "RedirectPaths":
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signOutUrlPath")
    def sign_out_url_path(self) -> builtins.str:
        ...

    @jsii.member(jsii_name="createAdditionalBehaviors")
    def create_additional_behaviors(
        self,
        origin: aws_cdk.aws_cloudfront.IOrigin,
        *,
        allowed_methods: typing.Optional[aws_cdk.aws_cloudfront.AllowedMethods] = None,
        cached_methods: typing.Optional[aws_cdk.aws_cloudfront.CachedMethods] = None,
        cache_policy: typing.Optional[aws_cdk.aws_cloudfront.ICachePolicy] = None,
        compress: typing.Optional[builtins.bool] = None,
        edge_lambdas: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.EdgeLambda]] = None,
        function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.FunctionAssociation]] = None,
        origin_request_policy: typing.Optional[aws_cdk.aws_cloudfront.IOriginRequestPolicy] = None,
        response_headers_policy: typing.Optional[aws_cdk.aws_cloudfront.IResponseHeadersPolicy] = None,
        smooth_streaming: typing.Optional[builtins.bool] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.IKeyGroup]] = None,
        viewer_protocol_policy: typing.Optional[aws_cdk.aws_cloudfront.ViewerProtocolPolicy] = None,
    ) -> typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions]:
        '''
        :param origin: -
        :param allowed_methods: HTTP methods to allow for this behavior. Default: AllowedMethods.ALLOW_GET_HEAD
        :param cached_methods: HTTP methods to cache for this behavior. Default: CachedMethods.CACHE_GET_HEAD
        :param cache_policy: The cache policy for this behavior. The cache policy determines what values are included in the cache key, and the time-to-live (TTL) values for the cache. Default: CachePolicy.CACHING_OPTIMIZED
        :param compress: Whether you want CloudFront to automatically compress certain files for this cache behavior. See https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ServingCompressedFiles.html#compressed-content-cloudfront-file-types for file types CloudFront will compress. Default: true
        :param edge_lambdas: The Lambda@Edge functions to invoke before serving the contents. Default: - no Lambda functions will be invoked
        :param function_associations: The CloudFront functions to invoke before serving the contents. Default: - no functions will be invoked
        :param origin_request_policy: The origin request policy for this behavior. The origin request policy determines which values (e.g., headers, cookies) are included in requests that CloudFront sends to the origin. Default: - none
        :param response_headers_policy: The response headers policy for this behavior. The response headers policy determines which headers are included in responses Default: - none
        :param smooth_streaming: Set this to true to indicate you want to distribute media files in the Microsoft Smooth Streaming format using this behavior. Default: false
        :param trusted_key_groups: A list of Key Groups that CloudFront can use to validate signed URLs or signed cookies. Default: - no KeyGroups are associated with cache behavior
        :param viewer_protocol_policy: The protocol that viewers can use to access the files controlled by this behavior. Default: ViewerProtocolPolicy.ALLOW_ALL
        '''
        ...

    @jsii.member(jsii_name="createDefaultBehavior")
    def create_default_behavior(
        self,
        origin: aws_cdk.aws_cloudfront.IOrigin,
        *,
        allowed_methods: typing.Optional[aws_cdk.aws_cloudfront.AllowedMethods] = None,
        cached_methods: typing.Optional[aws_cdk.aws_cloudfront.CachedMethods] = None,
        cache_policy: typing.Optional[aws_cdk.aws_cloudfront.ICachePolicy] = None,
        compress: typing.Optional[builtins.bool] = None,
        edge_lambdas: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.EdgeLambda]] = None,
        function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.FunctionAssociation]] = None,
        origin_request_policy: typing.Optional[aws_cdk.aws_cloudfront.IOriginRequestPolicy] = None,
        response_headers_policy: typing.Optional[aws_cdk.aws_cloudfront.IResponseHeadersPolicy] = None,
        smooth_streaming: typing.Optional[builtins.bool] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.IKeyGroup]] = None,
        viewer_protocol_policy: typing.Optional[aws_cdk.aws_cloudfront.ViewerProtocolPolicy] = None,
    ) -> aws_cdk.aws_cloudfront.BehaviorOptions:
        '''
        :param origin: -
        :param allowed_methods: HTTP methods to allow for this behavior. Default: AllowedMethods.ALLOW_GET_HEAD
        :param cached_methods: HTTP methods to cache for this behavior. Default: CachedMethods.CACHE_GET_HEAD
        :param cache_policy: The cache policy for this behavior. The cache policy determines what values are included in the cache key, and the time-to-live (TTL) values for the cache. Default: CachePolicy.CACHING_OPTIMIZED
        :param compress: Whether you want CloudFront to automatically compress certain files for this cache behavior. See https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ServingCompressedFiles.html#compressed-content-cloudfront-file-types for file types CloudFront will compress. Default: true
        :param edge_lambdas: The Lambda@Edge functions to invoke before serving the contents. Default: - no Lambda functions will be invoked
        :param function_associations: The CloudFront functions to invoke before serving the contents. Default: - no functions will be invoked
        :param origin_request_policy: The origin request policy for this behavior. The origin request policy determines which values (e.g., headers, cookies) are included in requests that CloudFront sends to the origin. Default: - none
        :param response_headers_policy: The response headers policy for this behavior. The response headers policy determines which headers are included in responses Default: - none
        :param smooth_streaming: Set this to true to indicate you want to distribute media files in the Microsoft Smooth Streaming format using this behavior. Default: false
        :param trusted_key_groups: A list of Key Groups that CloudFront can use to validate signed URLs or signed cookies. Default: - no KeyGroups are associated with cache behavior
        :param viewer_protocol_policy: The protocol that viewers can use to access the files controlled by this behavior. Default: ViewerProtocolPolicy.ALLOW_ALL
        '''
        ...

    @jsii.member(jsii_name="createLegacyAdditionalBehaviors")
    def create_legacy_additional_behaviors(
        self,
    ) -> typing.List[aws_cdk.aws_cloudfront.Behavior]:
        ...

    @jsii.member(jsii_name="createLegacyDefaultBehavior")
    def create_legacy_default_behavior(self) -> aws_cdk.aws_cloudfront.Behavior:
        ...

    @jsii.member(jsii_name="updateUserPoolClientCallbacks")
    def update_user_pool_client_callbacks(
        self,
        *,
        callback_urls: typing.Sequence[builtins.str],
        logout_urls: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param callback_urls: A list of allowed redirect (callback) URLs for the identity providers.
        :param logout_urls: A list of allowed logout URLs for the identity providers.
        '''
        ...


class _IAuthorizationProxy:
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-cloudfront-authorization.IAuthorization"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redirectPaths")
    def redirect_paths(self) -> "RedirectPaths":
        return typing.cast("RedirectPaths", jsii.get(self, "redirectPaths"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signOutUrlPath")
    def sign_out_url_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signOutUrlPath"))

    @jsii.member(jsii_name="createAdditionalBehaviors")
    def create_additional_behaviors(
        self,
        origin: aws_cdk.aws_cloudfront.IOrigin,
        *,
        allowed_methods: typing.Optional[aws_cdk.aws_cloudfront.AllowedMethods] = None,
        cached_methods: typing.Optional[aws_cdk.aws_cloudfront.CachedMethods] = None,
        cache_policy: typing.Optional[aws_cdk.aws_cloudfront.ICachePolicy] = None,
        compress: typing.Optional[builtins.bool] = None,
        edge_lambdas: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.EdgeLambda]] = None,
        function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.FunctionAssociation]] = None,
        origin_request_policy: typing.Optional[aws_cdk.aws_cloudfront.IOriginRequestPolicy] = None,
        response_headers_policy: typing.Optional[aws_cdk.aws_cloudfront.IResponseHeadersPolicy] = None,
        smooth_streaming: typing.Optional[builtins.bool] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.IKeyGroup]] = None,
        viewer_protocol_policy: typing.Optional[aws_cdk.aws_cloudfront.ViewerProtocolPolicy] = None,
    ) -> typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions]:
        '''
        :param origin: -
        :param allowed_methods: HTTP methods to allow for this behavior. Default: AllowedMethods.ALLOW_GET_HEAD
        :param cached_methods: HTTP methods to cache for this behavior. Default: CachedMethods.CACHE_GET_HEAD
        :param cache_policy: The cache policy for this behavior. The cache policy determines what values are included in the cache key, and the time-to-live (TTL) values for the cache. Default: CachePolicy.CACHING_OPTIMIZED
        :param compress: Whether you want CloudFront to automatically compress certain files for this cache behavior. See https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ServingCompressedFiles.html#compressed-content-cloudfront-file-types for file types CloudFront will compress. Default: true
        :param edge_lambdas: The Lambda@Edge functions to invoke before serving the contents. Default: - no Lambda functions will be invoked
        :param function_associations: The CloudFront functions to invoke before serving the contents. Default: - no functions will be invoked
        :param origin_request_policy: The origin request policy for this behavior. The origin request policy determines which values (e.g., headers, cookies) are included in requests that CloudFront sends to the origin. Default: - none
        :param response_headers_policy: The response headers policy for this behavior. The response headers policy determines which headers are included in responses Default: - none
        :param smooth_streaming: Set this to true to indicate you want to distribute media files in the Microsoft Smooth Streaming format using this behavior. Default: false
        :param trusted_key_groups: A list of Key Groups that CloudFront can use to validate signed URLs or signed cookies. Default: - no KeyGroups are associated with cache behavior
        :param viewer_protocol_policy: The protocol that viewers can use to access the files controlled by this behavior. Default: ViewerProtocolPolicy.ALLOW_ALL
        '''
        options = aws_cdk.aws_cloudfront.AddBehaviorOptions(
            allowed_methods=allowed_methods,
            cached_methods=cached_methods,
            cache_policy=cache_policy,
            compress=compress,
            edge_lambdas=edge_lambdas,
            function_associations=function_associations,
            origin_request_policy=origin_request_policy,
            response_headers_policy=response_headers_policy,
            smooth_streaming=smooth_streaming,
            trusted_key_groups=trusted_key_groups,
            viewer_protocol_policy=viewer_protocol_policy,
        )

        return typing.cast(typing.Mapping[builtins.str, aws_cdk.aws_cloudfront.BehaviorOptions], jsii.invoke(self, "createAdditionalBehaviors", [origin, options]))

    @jsii.member(jsii_name="createDefaultBehavior")
    def create_default_behavior(
        self,
        origin: aws_cdk.aws_cloudfront.IOrigin,
        *,
        allowed_methods: typing.Optional[aws_cdk.aws_cloudfront.AllowedMethods] = None,
        cached_methods: typing.Optional[aws_cdk.aws_cloudfront.CachedMethods] = None,
        cache_policy: typing.Optional[aws_cdk.aws_cloudfront.ICachePolicy] = None,
        compress: typing.Optional[builtins.bool] = None,
        edge_lambdas: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.EdgeLambda]] = None,
        function_associations: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.FunctionAssociation]] = None,
        origin_request_policy: typing.Optional[aws_cdk.aws_cloudfront.IOriginRequestPolicy] = None,
        response_headers_policy: typing.Optional[aws_cdk.aws_cloudfront.IResponseHeadersPolicy] = None,
        smooth_streaming: typing.Optional[builtins.bool] = None,
        trusted_key_groups: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.IKeyGroup]] = None,
        viewer_protocol_policy: typing.Optional[aws_cdk.aws_cloudfront.ViewerProtocolPolicy] = None,
    ) -> aws_cdk.aws_cloudfront.BehaviorOptions:
        '''
        :param origin: -
        :param allowed_methods: HTTP methods to allow for this behavior. Default: AllowedMethods.ALLOW_GET_HEAD
        :param cached_methods: HTTP methods to cache for this behavior. Default: CachedMethods.CACHE_GET_HEAD
        :param cache_policy: The cache policy for this behavior. The cache policy determines what values are included in the cache key, and the time-to-live (TTL) values for the cache. Default: CachePolicy.CACHING_OPTIMIZED
        :param compress: Whether you want CloudFront to automatically compress certain files for this cache behavior. See https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/ServingCompressedFiles.html#compressed-content-cloudfront-file-types for file types CloudFront will compress. Default: true
        :param edge_lambdas: The Lambda@Edge functions to invoke before serving the contents. Default: - no Lambda functions will be invoked
        :param function_associations: The CloudFront functions to invoke before serving the contents. Default: - no functions will be invoked
        :param origin_request_policy: The origin request policy for this behavior. The origin request policy determines which values (e.g., headers, cookies) are included in requests that CloudFront sends to the origin. Default: - none
        :param response_headers_policy: The response headers policy for this behavior. The response headers policy determines which headers are included in responses Default: - none
        :param smooth_streaming: Set this to true to indicate you want to distribute media files in the Microsoft Smooth Streaming format using this behavior. Default: false
        :param trusted_key_groups: A list of Key Groups that CloudFront can use to validate signed URLs or signed cookies. Default: - no KeyGroups are associated with cache behavior
        :param viewer_protocol_policy: The protocol that viewers can use to access the files controlled by this behavior. Default: ViewerProtocolPolicy.ALLOW_ALL
        '''
        options = aws_cdk.aws_cloudfront.AddBehaviorOptions(
            allowed_methods=allowed_methods,
            cached_methods=cached_methods,
            cache_policy=cache_policy,
            compress=compress,
            edge_lambdas=edge_lambdas,
            function_associations=function_associations,
            origin_request_policy=origin_request_policy,
            response_headers_policy=response_headers_policy,
            smooth_streaming=smooth_streaming,
            trusted_key_groups=trusted_key_groups,
            viewer_protocol_policy=viewer_protocol_policy,
        )

        return typing.cast(aws_cdk.aws_cloudfront.BehaviorOptions, jsii.invoke(self, "createDefaultBehavior", [origin, options]))

    @jsii.member(jsii_name="createLegacyAdditionalBehaviors")
    def create_legacy_additional_behaviors(
        self,
    ) -> typing.List[aws_cdk.aws_cloudfront.Behavior]:
        return typing.cast(typing.List[aws_cdk.aws_cloudfront.Behavior], jsii.invoke(self, "createLegacyAdditionalBehaviors", []))

    @jsii.member(jsii_name="createLegacyDefaultBehavior")
    def create_legacy_default_behavior(self) -> aws_cdk.aws_cloudfront.Behavior:
        return typing.cast(aws_cdk.aws_cloudfront.Behavior, jsii.invoke(self, "createLegacyDefaultBehavior", []))

    @jsii.member(jsii_name="updateUserPoolClientCallbacks")
    def update_user_pool_client_callbacks(
        self,
        *,
        callback_urls: typing.Sequence[builtins.str],
        logout_urls: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param callback_urls: A list of allowed redirect (callback) URLs for the identity providers.
        :param logout_urls: A list of allowed logout URLs for the identity providers.
        '''
        redirects = UserPoolClientCallbackUrls(
            callback_urls=callback_urls, logout_urls=logout_urls
        )

        return typing.cast(None, jsii.invoke(self, "updateUserPoolClientCallbacks", [redirects]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAuthorization).__jsii_proxy_class__ = lambda : _IAuthorizationProxy


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.ISpaAuthorization"
)
class ISpaAuthorization(IAuthorization, typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> "Mode":
        ...


class _ISpaAuthorizationProxy(
    jsii.proxy_for(IAuthorization) # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-cloudfront-authorization.ISpaAuthorization"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> "Mode":
        return typing.cast("Mode", jsii.get(self, "mode"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISpaAuthorization).__jsii_proxy_class__ = lambda : _ISpaAuthorizationProxy


@jsii.interface(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.IStaticSiteAuthorization"
)
class IStaticSiteAuthorization(IAuthorization, typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> "Mode":
        ...


class _IStaticSiteAuthorizationProxy(
    jsii.proxy_for(IAuthorization) # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "@cloudcomponents/cdk-cloudfront-authorization.IStaticSiteAuthorization"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> "Mode":
        return typing.cast("Mode", jsii.get(self, "mode"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStaticSiteAuthorization).__jsii_proxy_class__ = lambda : _IStaticSiteAuthorizationProxy


@jsii.enum(jsii_type="@cloudcomponents/cdk-cloudfront-authorization.Mode")
class Mode(enum.Enum):
    SPA = "SPA"
    STATIC_SITE = "STATIC_SITE"


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.RedirectPaths",
    jsii_struct_bases=[],
    name_mapping={
        "auth_refresh": "authRefresh",
        "sign_in": "signIn",
        "sign_out": "signOut",
    },
)
class RedirectPaths:
    def __init__(
        self,
        *,
        auth_refresh: builtins.str,
        sign_in: builtins.str,
        sign_out: builtins.str,
    ) -> None:
        '''
        :param auth_refresh: -
        :param sign_in: -
        :param sign_out: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "auth_refresh": auth_refresh,
            "sign_in": sign_in,
            "sign_out": sign_out,
        }

    @builtins.property
    def auth_refresh(self) -> builtins.str:
        result = self._values.get("auth_refresh")
        assert result is not None, "Required property 'auth_refresh' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sign_in(self) -> builtins.str:
        result = self._values.get("sign_in")
        assert result is not None, "Required property 'sign_in' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sign_out(self) -> builtins.str:
        result = self._values.get("sign_out")
        assert result is not None, "Required property 'sign_out' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedirectPaths(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RetrieveUserPoolClientSecret(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.RetrieveUserPoolClientSecret",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        user_pool: aws_cdk.aws_cognito.IUserPool,
        user_pool_client: aws_cdk.aws_cognito.IUserPoolClient,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param user_pool: -
        :param user_pool_client: -
        '''
        props = RetrieveUserPoolClientSecretProps(
            user_pool=user_pool, user_pool_client=user_pool_client
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        jsii.set(self, "clientSecret", value)


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.RetrieveUserPoolClientSecretProps",
    jsii_struct_bases=[],
    name_mapping={"user_pool": "userPool", "user_pool_client": "userPoolClient"},
)
class RetrieveUserPoolClientSecretProps:
    def __init__(
        self,
        *,
        user_pool: aws_cdk.aws_cognito.IUserPool,
        user_pool_client: aws_cdk.aws_cognito.IUserPoolClient,
    ) -> None:
        '''
        :param user_pool: -
        :param user_pool_client: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool": user_pool,
            "user_pool_client": user_pool_client,
        }

    @builtins.property
    def user_pool(self) -> aws_cdk.aws_cognito.IUserPool:
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(aws_cdk.aws_cognito.IUserPool, result)

    @builtins.property
    def user_pool_client(self) -> aws_cdk.aws_cognito.IUserPoolClient:
        result = self._values.get("user_pool_client")
        assert result is not None, "Required property 'user_pool_client' is missing"
        return typing.cast(aws_cdk.aws_cognito.IUserPoolClient, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RetrieveUserPoolClientSecretProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecretGenerator(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.SecretGenerator",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        allowed_characters: typing.Optional[builtins.str] = None,
        length: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param allowed_characters: -
        :param length: -
        '''
        props = SecretGeneratorProps(
            allowed_characters=allowed_characters, length=length
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secret"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.SecretGeneratorProps",
    jsii_struct_bases=[],
    name_mapping={"allowed_characters": "allowedCharacters", "length": "length"},
)
class SecretGeneratorProps:
    def __init__(
        self,
        *,
        allowed_characters: typing.Optional[builtins.str] = None,
        length: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param allowed_characters: -
        :param length: -
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if allowed_characters is not None:
            self._values["allowed_characters"] = allowed_characters
        if length is not None:
            self._values["length"] = length

    @builtins.property
    def allowed_characters(self) -> typing.Optional[builtins.str]:
        result = self._values.get("allowed_characters")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def length(self) -> typing.Optional[jsii.Number]:
        result = self._values.get("length")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretGeneratorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ISpaAuthorization)
class SpaAuthorization(
    Authorization,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.SpaAuthorization",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        user_pool: aws_cdk.aws_cognito.IUserPool,
        cookie_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        http_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_providers: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.UserPoolClientIdentityProvider]] = None,
        log_level: typing.Optional[cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel] = None,
        oauth_scopes: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.OAuthScope]] = None,
        redirect_paths: typing.Optional[RedirectPaths] = None,
        sign_out_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param user_pool: -
        :param cookie_settings: -
        :param http_headers: -
        :param identity_providers: -
        :param log_level: -
        :param oauth_scopes: -
        :param redirect_paths: -
        :param sign_out_url: -
        '''
        props = AuthorizationProps(
            user_pool=user_pool,
            cookie_settings=cookie_settings,
            http_headers=http_headers,
            identity_providers=identity_providers,
            log_level=log_level,
            oauth_scopes=oauth_scopes,
            redirect_paths=redirect_paths,
            sign_out_url=sign_out_url,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createAuthFlow")
    def _create_auth_flow(
        self,
        log_level: cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel,
    ) -> AuthFlow:
        '''
        :param log_level: -
        '''
        return typing.cast(AuthFlow, jsii.invoke(self, "createAuthFlow", [log_level]))

    @jsii.member(jsii_name="createUserPoolClient")
    def _create_user_pool_client(self) -> aws_cdk.aws_cognito.IUserPoolClient:
        return typing.cast(aws_cdk.aws_cognito.IUserPoolClient, jsii.invoke(self, "createUserPoolClient", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> Mode:
        return typing.cast(Mode, jsii.get(self, "mode"))


class SpaDistribution(
    BaseDistribution,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.SpaDistribution",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        authorization: ISpaAuthorization,
        ttl: typing.Optional[aws_cdk.core.Duration] = None,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        comment: typing.Optional[builtins.str] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        geo_restriction: typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction] = None,
        http_version: typing.Optional[aws_cdk.aws_cloudfront.HttpVersion] = None,
        log_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        log_file_prefix: typing.Optional[builtins.str] = None,
        log_includes_cookies: typing.Optional[builtins.bool] = None,
        minimum_protocol_version: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        origin: typing.Optional[aws_cdk.aws_cloudfront.IOrigin] = None,
        price_class: typing.Optional[aws_cdk.aws_cloudfront.PriceClass] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param authorization: -
        :param ttl: The minimum amount of time, in seconds, that you want CloudFront to cache the HTTP status code specified in ErrorCode. Default: 300 seconds
        :param certificate: A certificate to associate with the distribution. The certificate must be located in N. Virginia (us-east-1). Default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        :param comment: Any comments you want to include about the distribution. Default: - no comment
        :param default_root_object: The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/). Default: - index.html
        :param domain_names: Alternative domain names for this distribution. If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name, you can add an alternate domain name to your distribution. If you attach a certificate to the distribution, you must add (at least one of) the domain names of the certificate to this list. Default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        :param enabled: Enable or disable the distribution. Default: true
        :param enable_ipv6: Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address. If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses. This allows viewers to submit a second request, for an IPv4 address for your distribution. Default: true
        :param enable_logging: Enable access logging for the distribution. Default: - false, unless ``logBucket`` is specified.
        :param geo_restriction: Controls the countries in which your content is distributed. Default: - No geographic restrictions
        :param http_version: Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront. For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI). Default: HttpVersion.HTTP2
        :param log_bucket: The Amazon S3 bucket to store the access logs in. Default: - A bucket is created if ``enableLogging`` is true
        :param log_file_prefix: An optional string that you want CloudFront to prefix to the access log filenames for this distribution. Default: - no prefix
        :param log_includes_cookies: Specifies whether you want CloudFront to include cookies in access logs. Default: false
        :param minimum_protocol_version: The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: SecurityPolicyProtocol.TLS_V1_2_2019
        :param origin: The origin that you want CloudFront to route requests.
        :param price_class: The price class that corresponds with the maximum price that you want to pay for CloudFront service. If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations. If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location that has the lowest latency among the edge locations in your price class. Default: PriceClass.PRICE_CLASS_100
        :param removal_policy: Default: Destroy
        :param web_acl_id: Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution. To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``. Default: - No AWS Web Application Firewall web access control list (web ACL).
        '''
        props = SpaDistributionProps(
            authorization=authorization,
            ttl=ttl,
            certificate=certificate,
            comment=comment,
            default_root_object=default_root_object,
            domain_names=domain_names,
            enabled=enabled,
            enable_ipv6=enable_ipv6,
            enable_logging=enable_logging,
            geo_restriction=geo_restriction,
            http_version=http_version,
            log_bucket=log_bucket,
            log_file_prefix=log_file_prefix,
            log_includes_cookies=log_includes_cookies,
            minimum_protocol_version=minimum_protocol_version,
            origin=origin,
            price_class=price_class,
            removal_policy=removal_policy,
            web_acl_id=web_acl_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.SpaDistributionProps",
    jsii_struct_bases=[CommonDistributionProps],
    name_mapping={
        "certificate": "certificate",
        "comment": "comment",
        "default_root_object": "defaultRootObject",
        "domain_names": "domainNames",
        "enabled": "enabled",
        "enable_ipv6": "enableIpv6",
        "enable_logging": "enableLogging",
        "geo_restriction": "geoRestriction",
        "http_version": "httpVersion",
        "log_bucket": "logBucket",
        "log_file_prefix": "logFilePrefix",
        "log_includes_cookies": "logIncludesCookies",
        "minimum_protocol_version": "minimumProtocolVersion",
        "origin": "origin",
        "price_class": "priceClass",
        "removal_policy": "removalPolicy",
        "web_acl_id": "webAclId",
        "authorization": "authorization",
        "ttl": "ttl",
    },
)
class SpaDistributionProps(CommonDistributionProps):
    def __init__(
        self,
        *,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        comment: typing.Optional[builtins.str] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        geo_restriction: typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction] = None,
        http_version: typing.Optional[aws_cdk.aws_cloudfront.HttpVersion] = None,
        log_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        log_file_prefix: typing.Optional[builtins.str] = None,
        log_includes_cookies: typing.Optional[builtins.bool] = None,
        minimum_protocol_version: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        origin: typing.Optional[aws_cdk.aws_cloudfront.IOrigin] = None,
        price_class: typing.Optional[aws_cdk.aws_cloudfront.PriceClass] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
        authorization: ISpaAuthorization,
        ttl: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        '''
        :param certificate: A certificate to associate with the distribution. The certificate must be located in N. Virginia (us-east-1). Default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        :param comment: Any comments you want to include about the distribution. Default: - no comment
        :param default_root_object: The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/). Default: - index.html
        :param domain_names: Alternative domain names for this distribution. If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name, you can add an alternate domain name to your distribution. If you attach a certificate to the distribution, you must add (at least one of) the domain names of the certificate to this list. Default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        :param enabled: Enable or disable the distribution. Default: true
        :param enable_ipv6: Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address. If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses. This allows viewers to submit a second request, for an IPv4 address for your distribution. Default: true
        :param enable_logging: Enable access logging for the distribution. Default: - false, unless ``logBucket`` is specified.
        :param geo_restriction: Controls the countries in which your content is distributed. Default: - No geographic restrictions
        :param http_version: Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront. For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI). Default: HttpVersion.HTTP2
        :param log_bucket: The Amazon S3 bucket to store the access logs in. Default: - A bucket is created if ``enableLogging`` is true
        :param log_file_prefix: An optional string that you want CloudFront to prefix to the access log filenames for this distribution. Default: - no prefix
        :param log_includes_cookies: Specifies whether you want CloudFront to include cookies in access logs. Default: false
        :param minimum_protocol_version: The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: SecurityPolicyProtocol.TLS_V1_2_2019
        :param origin: The origin that you want CloudFront to route requests.
        :param price_class: The price class that corresponds with the maximum price that you want to pay for CloudFront service. If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations. If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location that has the lowest latency among the edge locations in your price class. Default: PriceClass.PRICE_CLASS_100
        :param removal_policy: Default: Destroy
        :param web_acl_id: Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution. To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``. Default: - No AWS Web Application Firewall web access control list (web ACL).
        :param authorization: -
        :param ttl: The minimum amount of time, in seconds, that you want CloudFront to cache the HTTP status code specified in ErrorCode. Default: 300 seconds
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authorization": authorization,
        }
        if certificate is not None:
            self._values["certificate"] = certificate
        if comment is not None:
            self._values["comment"] = comment
        if default_root_object is not None:
            self._values["default_root_object"] = default_root_object
        if domain_names is not None:
            self._values["domain_names"] = domain_names
        if enabled is not None:
            self._values["enabled"] = enabled
        if enable_ipv6 is not None:
            self._values["enable_ipv6"] = enable_ipv6
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if geo_restriction is not None:
            self._values["geo_restriction"] = geo_restriction
        if http_version is not None:
            self._values["http_version"] = http_version
        if log_bucket is not None:
            self._values["log_bucket"] = log_bucket
        if log_file_prefix is not None:
            self._values["log_file_prefix"] = log_file_prefix
        if log_includes_cookies is not None:
            self._values["log_includes_cookies"] = log_includes_cookies
        if minimum_protocol_version is not None:
            self._values["minimum_protocol_version"] = minimum_protocol_version
        if origin is not None:
            self._values["origin"] = origin
        if price_class is not None:
            self._values["price_class"] = price_class
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if web_acl_id is not None:
            self._values["web_acl_id"] = web_acl_id
        if ttl is not None:
            self._values["ttl"] = ttl

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''A certificate to associate with the distribution.

        The certificate must be located in N. Virginia (us-east-1).

        :default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Any comments you want to include about the distribution.

        :default: - no comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_root_object(self) -> typing.Optional[builtins.str]:
        '''The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/).

        :default: - index.html
        '''
        result = self._values.get("default_root_object")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Alternative domain names for this distribution.

        If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name,
        you can add an alternate domain name to your distribution. If you attach a certificate to the distribution,
        you must add (at least one of) the domain names of the certificate to this list.

        :default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        '''
        result = self._values.get("domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable or disable the distribution.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_ipv6(self) -> typing.Optional[builtins.bool]:
        '''Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address.

        If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses.
        This allows viewers to submit a second request, for an IPv4 address for your distribution.

        :default: true
        '''
        result = self._values.get("enable_ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''Enable access logging for the distribution.

        :default: - false, unless ``logBucket`` is specified.
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def geo_restriction(self) -> typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction]:
        '''Controls the countries in which your content is distributed.

        :default: - No geographic restrictions
        '''
        result = self._values.get("geo_restriction")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction], result)

    @builtins.property
    def http_version(self) -> typing.Optional[aws_cdk.aws_cloudfront.HttpVersion]:
        '''Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront.

        For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI).

        :default: HttpVersion.HTTP2
        '''
        result = self._values.get("http_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.HttpVersion], result)

    @builtins.property
    def log_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''The Amazon S3 bucket to store the access logs in.

        :default: - A bucket is created if ``enableLogging`` is true
        '''
        result = self._values.get("log_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def log_file_prefix(self) -> typing.Optional[builtins.str]:
        '''An optional string that you want CloudFront to prefix to the access log filenames for this distribution.

        :default: - no prefix
        '''
        result = self._values.get("log_file_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_includes_cookies(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether you want CloudFront to include cookies in access logs.

        :default: false
        '''
        result = self._values.get("log_includes_cookies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def minimum_protocol_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol]:
        '''The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections.

        CloudFront serves your objects only to browsers or devices that support at
        least the SSL version that you specify.

        :default: SecurityPolicyProtocol.TLS_V1_2_2019
        '''
        result = self._values.get("minimum_protocol_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol], result)

    @builtins.property
    def origin(self) -> typing.Optional[aws_cdk.aws_cloudfront.IOrigin]:
        '''The origin that you want CloudFront to route requests.'''
        result = self._values.get("origin")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.IOrigin], result)

    @builtins.property
    def price_class(self) -> typing.Optional[aws_cdk.aws_cloudfront.PriceClass]:
        '''The price class that corresponds with the maximum price that you want to pay for CloudFront service.

        If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations.
        If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location
        that has the lowest latency among the edge locations in your price class.

        :default: PriceClass.PRICE_CLASS_100
        '''
        result = self._values.get("price_class")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.PriceClass], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''
        :default: Destroy
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def web_acl_id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution.

        To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example
        ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``.
        To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``.

        :default: - No AWS Web Application Firewall web access control list (web ACL).

        :see: https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CreateDistribution.html#API_CreateDistribution_RequestParameters.
        '''
        result = self._values.get("web_acl_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorization(self) -> ISpaAuthorization:
        result = self._values.get("authorization")
        assert result is not None, "Required property 'authorization' is missing"
        return typing.cast(ISpaAuthorization, result)

    @builtins.property
    def ttl(self) -> typing.Optional[aws_cdk.core.Duration]:
        '''The minimum amount of time, in seconds, that you want CloudFront to cache the HTTP status code specified in ErrorCode.

        :default: 300 seconds
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[aws_cdk.core.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SpaDistributionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IStaticSiteAuthorization)
class StaticSiteAuthorization(
    Authorization,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.StaticSiteAuthorization",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        user_pool: aws_cdk.aws_cognito.IUserPool,
        cookie_settings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        http_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        identity_providers: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.UserPoolClientIdentityProvider]] = None,
        log_level: typing.Optional[cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel] = None,
        oauth_scopes: typing.Optional[typing.Sequence[aws_cdk.aws_cognito.OAuthScope]] = None,
        redirect_paths: typing.Optional[RedirectPaths] = None,
        sign_out_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param user_pool: -
        :param cookie_settings: -
        :param http_headers: -
        :param identity_providers: -
        :param log_level: -
        :param oauth_scopes: -
        :param redirect_paths: -
        :param sign_out_url: -
        '''
        props = AuthorizationProps(
            user_pool=user_pool,
            cookie_settings=cookie_settings,
            http_headers=http_headers,
            identity_providers=identity_providers,
            log_level=log_level,
            oauth_scopes=oauth_scopes,
            redirect_paths=redirect_paths,
            sign_out_url=sign_out_url,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createAuthFlow")
    def _create_auth_flow(
        self,
        log_level: cloudcomponents.cdk_lambda_at_edge_pattern.LogLevel,
    ) -> AuthFlow:
        '''
        :param log_level: -
        '''
        return typing.cast(AuthFlow, jsii.invoke(self, "createAuthFlow", [log_level]))

    @jsii.member(jsii_name="createUserPoolClient")
    def _create_user_pool_client(self) -> aws_cdk.aws_cognito.IUserPoolClient:
        return typing.cast(aws_cdk.aws_cognito.IUserPoolClient, jsii.invoke(self, "createUserPoolClient", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> Mode:
        return typing.cast(Mode, jsii.get(self, "mode"))


class StaticSiteDistribution(
    BaseDistribution,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.StaticSiteDistribution",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        authorization: IStaticSiteAuthorization,
        error_responses: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.ErrorResponse]] = None,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        comment: typing.Optional[builtins.str] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        geo_restriction: typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction] = None,
        http_version: typing.Optional[aws_cdk.aws_cloudfront.HttpVersion] = None,
        log_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        log_file_prefix: typing.Optional[builtins.str] = None,
        log_includes_cookies: typing.Optional[builtins.bool] = None,
        minimum_protocol_version: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        origin: typing.Optional[aws_cdk.aws_cloudfront.IOrigin] = None,
        price_class: typing.Optional[aws_cdk.aws_cloudfront.PriceClass] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param authorization: -
        :param error_responses: -
        :param certificate: A certificate to associate with the distribution. The certificate must be located in N. Virginia (us-east-1). Default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        :param comment: Any comments you want to include about the distribution. Default: - no comment
        :param default_root_object: The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/). Default: - index.html
        :param domain_names: Alternative domain names for this distribution. If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name, you can add an alternate domain name to your distribution. If you attach a certificate to the distribution, you must add (at least one of) the domain names of the certificate to this list. Default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        :param enabled: Enable or disable the distribution. Default: true
        :param enable_ipv6: Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address. If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses. This allows viewers to submit a second request, for an IPv4 address for your distribution. Default: true
        :param enable_logging: Enable access logging for the distribution. Default: - false, unless ``logBucket`` is specified.
        :param geo_restriction: Controls the countries in which your content is distributed. Default: - No geographic restrictions
        :param http_version: Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront. For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI). Default: HttpVersion.HTTP2
        :param log_bucket: The Amazon S3 bucket to store the access logs in. Default: - A bucket is created if ``enableLogging`` is true
        :param log_file_prefix: An optional string that you want CloudFront to prefix to the access log filenames for this distribution. Default: - no prefix
        :param log_includes_cookies: Specifies whether you want CloudFront to include cookies in access logs. Default: false
        :param minimum_protocol_version: The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: SecurityPolicyProtocol.TLS_V1_2_2019
        :param origin: The origin that you want CloudFront to route requests.
        :param price_class: The price class that corresponds with the maximum price that you want to pay for CloudFront service. If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations. If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location that has the lowest latency among the edge locations in your price class. Default: PriceClass.PRICE_CLASS_100
        :param removal_policy: Default: Destroy
        :param web_acl_id: Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution. To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``. Default: - No AWS Web Application Firewall web access control list (web ACL).
        '''
        props = StaticSiteDistributionProps(
            authorization=authorization,
            error_responses=error_responses,
            certificate=certificate,
            comment=comment,
            default_root_object=default_root_object,
            domain_names=domain_names,
            enabled=enabled,
            enable_ipv6=enable_ipv6,
            enable_logging=enable_logging,
            geo_restriction=geo_restriction,
            http_version=http_version,
            log_bucket=log_bucket,
            log_file_prefix=log_file_prefix,
            log_includes_cookies=log_includes_cookies,
            minimum_protocol_version=minimum_protocol_version,
            origin=origin,
            price_class=price_class,
            removal_policy=removal_policy,
            web_acl_id=web_acl_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.StaticSiteDistributionProps",
    jsii_struct_bases=[CommonDistributionProps],
    name_mapping={
        "certificate": "certificate",
        "comment": "comment",
        "default_root_object": "defaultRootObject",
        "domain_names": "domainNames",
        "enabled": "enabled",
        "enable_ipv6": "enableIpv6",
        "enable_logging": "enableLogging",
        "geo_restriction": "geoRestriction",
        "http_version": "httpVersion",
        "log_bucket": "logBucket",
        "log_file_prefix": "logFilePrefix",
        "log_includes_cookies": "logIncludesCookies",
        "minimum_protocol_version": "minimumProtocolVersion",
        "origin": "origin",
        "price_class": "priceClass",
        "removal_policy": "removalPolicy",
        "web_acl_id": "webAclId",
        "authorization": "authorization",
        "error_responses": "errorResponses",
    },
)
class StaticSiteDistributionProps(CommonDistributionProps):
    def __init__(
        self,
        *,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        comment: typing.Optional[builtins.str] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        geo_restriction: typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction] = None,
        http_version: typing.Optional[aws_cdk.aws_cloudfront.HttpVersion] = None,
        log_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        log_file_prefix: typing.Optional[builtins.str] = None,
        log_includes_cookies: typing.Optional[builtins.bool] = None,
        minimum_protocol_version: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        origin: typing.Optional[aws_cdk.aws_cloudfront.IOrigin] = None,
        price_class: typing.Optional[aws_cdk.aws_cloudfront.PriceClass] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
        authorization: IStaticSiteAuthorization,
        error_responses: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.ErrorResponse]] = None,
    ) -> None:
        '''
        :param certificate: A certificate to associate with the distribution. The certificate must be located in N. Virginia (us-east-1). Default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        :param comment: Any comments you want to include about the distribution. Default: - no comment
        :param default_root_object: The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/). Default: - index.html
        :param domain_names: Alternative domain names for this distribution. If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name, you can add an alternate domain name to your distribution. If you attach a certificate to the distribution, you must add (at least one of) the domain names of the certificate to this list. Default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        :param enabled: Enable or disable the distribution. Default: true
        :param enable_ipv6: Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address. If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses. This allows viewers to submit a second request, for an IPv4 address for your distribution. Default: true
        :param enable_logging: Enable access logging for the distribution. Default: - false, unless ``logBucket`` is specified.
        :param geo_restriction: Controls the countries in which your content is distributed. Default: - No geographic restrictions
        :param http_version: Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront. For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI). Default: HttpVersion.HTTP2
        :param log_bucket: The Amazon S3 bucket to store the access logs in. Default: - A bucket is created if ``enableLogging`` is true
        :param log_file_prefix: An optional string that you want CloudFront to prefix to the access log filenames for this distribution. Default: - no prefix
        :param log_includes_cookies: Specifies whether you want CloudFront to include cookies in access logs. Default: false
        :param minimum_protocol_version: The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: SecurityPolicyProtocol.TLS_V1_2_2019
        :param origin: The origin that you want CloudFront to route requests.
        :param price_class: The price class that corresponds with the maximum price that you want to pay for CloudFront service. If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations. If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location that has the lowest latency among the edge locations in your price class. Default: PriceClass.PRICE_CLASS_100
        :param removal_policy: Default: Destroy
        :param web_acl_id: Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution. To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``. Default: - No AWS Web Application Firewall web access control list (web ACL).
        :param authorization: -
        :param error_responses: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authorization": authorization,
        }
        if certificate is not None:
            self._values["certificate"] = certificate
        if comment is not None:
            self._values["comment"] = comment
        if default_root_object is not None:
            self._values["default_root_object"] = default_root_object
        if domain_names is not None:
            self._values["domain_names"] = domain_names
        if enabled is not None:
            self._values["enabled"] = enabled
        if enable_ipv6 is not None:
            self._values["enable_ipv6"] = enable_ipv6
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if geo_restriction is not None:
            self._values["geo_restriction"] = geo_restriction
        if http_version is not None:
            self._values["http_version"] = http_version
        if log_bucket is not None:
            self._values["log_bucket"] = log_bucket
        if log_file_prefix is not None:
            self._values["log_file_prefix"] = log_file_prefix
        if log_includes_cookies is not None:
            self._values["log_includes_cookies"] = log_includes_cookies
        if minimum_protocol_version is not None:
            self._values["minimum_protocol_version"] = minimum_protocol_version
        if origin is not None:
            self._values["origin"] = origin
        if price_class is not None:
            self._values["price_class"] = price_class
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if web_acl_id is not None:
            self._values["web_acl_id"] = web_acl_id
        if error_responses is not None:
            self._values["error_responses"] = error_responses

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''A certificate to associate with the distribution.

        The certificate must be located in N. Virginia (us-east-1).

        :default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Any comments you want to include about the distribution.

        :default: - no comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_root_object(self) -> typing.Optional[builtins.str]:
        '''The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/).

        :default: - index.html
        '''
        result = self._values.get("default_root_object")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Alternative domain names for this distribution.

        If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name,
        you can add an alternate domain name to your distribution. If you attach a certificate to the distribution,
        you must add (at least one of) the domain names of the certificate to this list.

        :default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        '''
        result = self._values.get("domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable or disable the distribution.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_ipv6(self) -> typing.Optional[builtins.bool]:
        '''Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address.

        If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses.
        This allows viewers to submit a second request, for an IPv4 address for your distribution.

        :default: true
        '''
        result = self._values.get("enable_ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''Enable access logging for the distribution.

        :default: - false, unless ``logBucket`` is specified.
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def geo_restriction(self) -> typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction]:
        '''Controls the countries in which your content is distributed.

        :default: - No geographic restrictions
        '''
        result = self._values.get("geo_restriction")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction], result)

    @builtins.property
    def http_version(self) -> typing.Optional[aws_cdk.aws_cloudfront.HttpVersion]:
        '''Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront.

        For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI).

        :default: HttpVersion.HTTP2
        '''
        result = self._values.get("http_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.HttpVersion], result)

    @builtins.property
    def log_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''The Amazon S3 bucket to store the access logs in.

        :default: - A bucket is created if ``enableLogging`` is true
        '''
        result = self._values.get("log_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def log_file_prefix(self) -> typing.Optional[builtins.str]:
        '''An optional string that you want CloudFront to prefix to the access log filenames for this distribution.

        :default: - no prefix
        '''
        result = self._values.get("log_file_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_includes_cookies(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether you want CloudFront to include cookies in access logs.

        :default: false
        '''
        result = self._values.get("log_includes_cookies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def minimum_protocol_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol]:
        '''The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections.

        CloudFront serves your objects only to browsers or devices that support at
        least the SSL version that you specify.

        :default: SecurityPolicyProtocol.TLS_V1_2_2019
        '''
        result = self._values.get("minimum_protocol_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol], result)

    @builtins.property
    def origin(self) -> typing.Optional[aws_cdk.aws_cloudfront.IOrigin]:
        '''The origin that you want CloudFront to route requests.'''
        result = self._values.get("origin")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.IOrigin], result)

    @builtins.property
    def price_class(self) -> typing.Optional[aws_cdk.aws_cloudfront.PriceClass]:
        '''The price class that corresponds with the maximum price that you want to pay for CloudFront service.

        If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations.
        If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location
        that has the lowest latency among the edge locations in your price class.

        :default: PriceClass.PRICE_CLASS_100
        '''
        result = self._values.get("price_class")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.PriceClass], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''
        :default: Destroy
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def web_acl_id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution.

        To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example
        ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``.
        To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``.

        :default: - No AWS Web Application Firewall web access control list (web ACL).

        :see: https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CreateDistribution.html#API_CreateDistribution_RequestParameters.
        '''
        result = self._values.get("web_acl_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorization(self) -> IStaticSiteAuthorization:
        result = self._values.get("authorization")
        assert result is not None, "Required property 'authorization' is missing"
        return typing.cast(IStaticSiteAuthorization, result)

    @builtins.property
    def error_responses(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudfront.ErrorResponse]]:
        result = self._values.get("error_responses")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudfront.ErrorResponse]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaticSiteDistributionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.UserPoolClientCallbackUrls",
    jsii_struct_bases=[],
    name_mapping={"callback_urls": "callbackUrls", "logout_urls": "logoutUrls"},
)
class UserPoolClientCallbackUrls:
    def __init__(
        self,
        *,
        callback_urls: typing.Sequence[builtins.str],
        logout_urls: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param callback_urls: A list of allowed redirect (callback) URLs for the identity providers.
        :param logout_urls: A list of allowed logout URLs for the identity providers.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "callback_urls": callback_urls,
            "logout_urls": logout_urls,
        }

    @builtins.property
    def callback_urls(self) -> typing.List[builtins.str]:
        '''A list of allowed redirect (callback) URLs for the identity providers.'''
        result = self._values.get("callback_urls")
        assert result is not None, "Required property 'callback_urls' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def logout_urls(self) -> typing.List[builtins.str]:
        '''A list of allowed logout URLs for the identity providers.'''
        result = self._values.get("logout_urls")
        assert result is not None, "Required property 'logout_urls' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPoolClientCallbackUrls(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UserPoolClientRedirects(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.UserPoolClientRedirects",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        callback_urls: typing.Sequence[builtins.str],
        identity_providers: typing.Sequence[aws_cdk.aws_cognito.UserPoolClientIdentityProvider],
        logout_urls: typing.Sequence[builtins.str],
        oauth_scopes: typing.Sequence[aws_cdk.aws_cognito.OAuthScope],
        user_pool: aws_cdk.aws_cognito.IUserPool,
        user_pool_client: aws_cdk.aws_cognito.IUserPoolClient,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param callback_urls: -
        :param identity_providers: -
        :param logout_urls: -
        :param oauth_scopes: -
        :param user_pool: -
        :param user_pool_client: -
        '''
        props = UserPoolClientRedirectsProps(
            callback_urls=callback_urls,
            identity_providers=identity_providers,
            logout_urls=logout_urls,
            oauth_scopes=oauth_scopes,
            user_pool=user_pool,
            user_pool_client=user_pool_client,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.UserPoolClientRedirectsProps",
    jsii_struct_bases=[],
    name_mapping={
        "callback_urls": "callbackUrls",
        "identity_providers": "identityProviders",
        "logout_urls": "logoutUrls",
        "oauth_scopes": "oauthScopes",
        "user_pool": "userPool",
        "user_pool_client": "userPoolClient",
    },
)
class UserPoolClientRedirectsProps:
    def __init__(
        self,
        *,
        callback_urls: typing.Sequence[builtins.str],
        identity_providers: typing.Sequence[aws_cdk.aws_cognito.UserPoolClientIdentityProvider],
        logout_urls: typing.Sequence[builtins.str],
        oauth_scopes: typing.Sequence[aws_cdk.aws_cognito.OAuthScope],
        user_pool: aws_cdk.aws_cognito.IUserPool,
        user_pool_client: aws_cdk.aws_cognito.IUserPoolClient,
    ) -> None:
        '''
        :param callback_urls: -
        :param identity_providers: -
        :param logout_urls: -
        :param oauth_scopes: -
        :param user_pool: -
        :param user_pool_client: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "callback_urls": callback_urls,
            "identity_providers": identity_providers,
            "logout_urls": logout_urls,
            "oauth_scopes": oauth_scopes,
            "user_pool": user_pool,
            "user_pool_client": user_pool_client,
        }

    @builtins.property
    def callback_urls(self) -> typing.List[builtins.str]:
        result = self._values.get("callback_urls")
        assert result is not None, "Required property 'callback_urls' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def identity_providers(
        self,
    ) -> typing.List[aws_cdk.aws_cognito.UserPoolClientIdentityProvider]:
        result = self._values.get("identity_providers")
        assert result is not None, "Required property 'identity_providers' is missing"
        return typing.cast(typing.List[aws_cdk.aws_cognito.UserPoolClientIdentityProvider], result)

    @builtins.property
    def logout_urls(self) -> typing.List[builtins.str]:
        result = self._values.get("logout_urls")
        assert result is not None, "Required property 'logout_urls' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def oauth_scopes(self) -> typing.List[aws_cdk.aws_cognito.OAuthScope]:
        result = self._values.get("oauth_scopes")
        assert result is not None, "Required property 'oauth_scopes' is missing"
        return typing.cast(typing.List[aws_cdk.aws_cognito.OAuthScope], result)

    @builtins.property
    def user_pool(self) -> aws_cdk.aws_cognito.IUserPool:
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(aws_cdk.aws_cognito.IUserPool, result)

    @builtins.property
    def user_pool_client(self) -> aws_cdk.aws_cognito.IUserPoolClient:
        result = self._values.get("user_pool_client")
        assert result is not None, "Required property 'user_pool_client' is missing"
        return typing.cast(aws_cdk.aws_cognito.IUserPoolClient, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPoolClientRedirectsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-cloudfront-authorization.BaseDistributionProps",
    jsii_struct_bases=[CommonDistributionProps],
    name_mapping={
        "certificate": "certificate",
        "comment": "comment",
        "default_root_object": "defaultRootObject",
        "domain_names": "domainNames",
        "enabled": "enabled",
        "enable_ipv6": "enableIpv6",
        "enable_logging": "enableLogging",
        "geo_restriction": "geoRestriction",
        "http_version": "httpVersion",
        "log_bucket": "logBucket",
        "log_file_prefix": "logFilePrefix",
        "log_includes_cookies": "logIncludesCookies",
        "minimum_protocol_version": "minimumProtocolVersion",
        "origin": "origin",
        "price_class": "priceClass",
        "removal_policy": "removalPolicy",
        "web_acl_id": "webAclId",
        "authorization": "authorization",
        "error_responses": "errorResponses",
    },
)
class BaseDistributionProps(CommonDistributionProps):
    def __init__(
        self,
        *,
        certificate: typing.Optional[aws_cdk.aws_certificatemanager.ICertificate] = None,
        comment: typing.Optional[builtins.str] = None,
        default_root_object: typing.Optional[builtins.str] = None,
        domain_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        geo_restriction: typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction] = None,
        http_version: typing.Optional[aws_cdk.aws_cloudfront.HttpVersion] = None,
        log_bucket: typing.Optional[aws_cdk.aws_s3.IBucket] = None,
        log_file_prefix: typing.Optional[builtins.str] = None,
        log_includes_cookies: typing.Optional[builtins.bool] = None,
        minimum_protocol_version: typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol] = None,
        origin: typing.Optional[aws_cdk.aws_cloudfront.IOrigin] = None,
        price_class: typing.Optional[aws_cdk.aws_cloudfront.PriceClass] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
        authorization: IAuthorization,
        error_responses: typing.Optional[typing.Sequence[aws_cdk.aws_cloudfront.ErrorResponse]] = None,
    ) -> None:
        '''
        :param certificate: A certificate to associate with the distribution. The certificate must be located in N. Virginia (us-east-1). Default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        :param comment: Any comments you want to include about the distribution. Default: - no comment
        :param default_root_object: The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/). Default: - index.html
        :param domain_names: Alternative domain names for this distribution. If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name, you can add an alternate domain name to your distribution. If you attach a certificate to the distribution, you must add (at least one of) the domain names of the certificate to this list. Default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        :param enabled: Enable or disable the distribution. Default: true
        :param enable_ipv6: Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address. If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses. This allows viewers to submit a second request, for an IPv4 address for your distribution. Default: true
        :param enable_logging: Enable access logging for the distribution. Default: - false, unless ``logBucket`` is specified.
        :param geo_restriction: Controls the countries in which your content is distributed. Default: - No geographic restrictions
        :param http_version: Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront. For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI). Default: HttpVersion.HTTP2
        :param log_bucket: The Amazon S3 bucket to store the access logs in. Default: - A bucket is created if ``enableLogging`` is true
        :param log_file_prefix: An optional string that you want CloudFront to prefix to the access log filenames for this distribution. Default: - no prefix
        :param log_includes_cookies: Specifies whether you want CloudFront to include cookies in access logs. Default: false
        :param minimum_protocol_version: The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections. CloudFront serves your objects only to browsers or devices that support at least the SSL version that you specify. Default: SecurityPolicyProtocol.TLS_V1_2_2019
        :param origin: The origin that you want CloudFront to route requests.
        :param price_class: The price class that corresponds with the maximum price that you want to pay for CloudFront service. If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations. If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location that has the lowest latency among the edge locations in your price class. Default: PriceClass.PRICE_CLASS_100
        :param removal_policy: Default: Destroy
        :param web_acl_id: Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution. To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``. To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``. Default: - No AWS Web Application Firewall web access control list (web ACL).
        :param authorization: -
        :param error_responses: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authorization": authorization,
        }
        if certificate is not None:
            self._values["certificate"] = certificate
        if comment is not None:
            self._values["comment"] = comment
        if default_root_object is not None:
            self._values["default_root_object"] = default_root_object
        if domain_names is not None:
            self._values["domain_names"] = domain_names
        if enabled is not None:
            self._values["enabled"] = enabled
        if enable_ipv6 is not None:
            self._values["enable_ipv6"] = enable_ipv6
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if geo_restriction is not None:
            self._values["geo_restriction"] = geo_restriction
        if http_version is not None:
            self._values["http_version"] = http_version
        if log_bucket is not None:
            self._values["log_bucket"] = log_bucket
        if log_file_prefix is not None:
            self._values["log_file_prefix"] = log_file_prefix
        if log_includes_cookies is not None:
            self._values["log_includes_cookies"] = log_includes_cookies
        if minimum_protocol_version is not None:
            self._values["minimum_protocol_version"] = minimum_protocol_version
        if origin is not None:
            self._values["origin"] = origin
        if price_class is not None:
            self._values["price_class"] = price_class
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if web_acl_id is not None:
            self._values["web_acl_id"] = web_acl_id
        if error_responses is not None:
            self._values["error_responses"] = error_responses

    @builtins.property
    def certificate(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''A certificate to associate with the distribution.

        The certificate must be located in N. Virginia (us-east-1).

        :default: - the CloudFront wildcard certificate (*.cloudfront.net) will be used.
        '''
        result = self._values.get("certificate")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''Any comments you want to include about the distribution.

        :default: - no comment
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_root_object(self) -> typing.Optional[builtins.str]:
        '''The object that you want CloudFront to request from your origin (for example, index.html) when a viewer requests the root URL for your distribution. If no default object is set, the request goes to the origin's root (e.g., example.com/).

        :default: - index.html
        '''
        result = self._values.get("default_root_object")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Alternative domain names for this distribution.

        If you want to use your own domain name, such as www.example.com, instead of the cloudfront.net domain name,
        you can add an alternate domain name to your distribution. If you attach a certificate to the distribution,
        you must add (at least one of) the domain names of the certificate to this list.

        :default: - The distribution will only support the default generated name (e.g., d111111abcdef8.cloudfront.net)
        '''
        result = self._values.get("domain_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Enable or disable the distribution.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_ipv6(self) -> typing.Optional[builtins.bool]:
        '''Whether CloudFront will respond to IPv6 DNS requests with an IPv6 address.

        If you specify false, CloudFront responds to IPv6 DNS requests with the DNS response code NOERROR and with no IP addresses.
        This allows viewers to submit a second request, for an IPv4 address for your distribution.

        :default: true
        '''
        result = self._values.get("enable_ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''Enable access logging for the distribution.

        :default: - false, unless ``logBucket`` is specified.
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def geo_restriction(self) -> typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction]:
        '''Controls the countries in which your content is distributed.

        :default: - No geographic restrictions
        '''
        result = self._values.get("geo_restriction")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.GeoRestriction], result)

    @builtins.property
    def http_version(self) -> typing.Optional[aws_cdk.aws_cloudfront.HttpVersion]:
        '''Specify the maximum HTTP version that you want viewers to use to communicate with CloudFront.

        For viewers and CloudFront to use HTTP/2, viewers must support TLS 1.2 or later, and must support server name identification (SNI).

        :default: HttpVersion.HTTP2
        '''
        result = self._values.get("http_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.HttpVersion], result)

    @builtins.property
    def log_bucket(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''The Amazon S3 bucket to store the access logs in.

        :default: - A bucket is created if ``enableLogging`` is true
        '''
        result = self._values.get("log_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def log_file_prefix(self) -> typing.Optional[builtins.str]:
        '''An optional string that you want CloudFront to prefix to the access log filenames for this distribution.

        :default: - no prefix
        '''
        result = self._values.get("log_file_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_includes_cookies(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether you want CloudFront to include cookies in access logs.

        :default: false
        '''
        result = self._values.get("log_includes_cookies")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def minimum_protocol_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol]:
        '''The minimum version of the SSL protocol that you want CloudFront to use for HTTPS connections.

        CloudFront serves your objects only to browsers or devices that support at
        least the SSL version that you specify.

        :default: SecurityPolicyProtocol.TLS_V1_2_2019
        '''
        result = self._values.get("minimum_protocol_version")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.SecurityPolicyProtocol], result)

    @builtins.property
    def origin(self) -> typing.Optional[aws_cdk.aws_cloudfront.IOrigin]:
        '''The origin that you want CloudFront to route requests.'''
        result = self._values.get("origin")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.IOrigin], result)

    @builtins.property
    def price_class(self) -> typing.Optional[aws_cdk.aws_cloudfront.PriceClass]:
        '''The price class that corresponds with the maximum price that you want to pay for CloudFront service.

        If you specify PriceClass_All, CloudFront responds to requests for your objects from all CloudFront edge locations.
        If you specify a price class other than PriceClass_All, CloudFront serves your objects from the CloudFront edge location
        that has the lowest latency among the edge locations in your price class.

        :default: PriceClass.PRICE_CLASS_100
        '''
        result = self._values.get("price_class")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.PriceClass], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''
        :default: Destroy
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def web_acl_id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier that specifies the AWS WAF web ACL to associate with this CloudFront distribution.

        To specify a web ACL created using the latest version of AWS WAF, use the ACL ARN, for example
        ``arn:aws:wafv2:us-east-1:123456789012:global/webacl/ExampleWebACL/473e64fd-f30b-4765-81a0-62ad96dd167a``.
        To specify a web ACL created using AWS WAF Classic, use the ACL ID, for example ``473e64fd-f30b-4765-81a0-62ad96dd167a``.

        :default: - No AWS Web Application Firewall web access control list (web ACL).

        :see: https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CreateDistribution.html#API_CreateDistribution_RequestParameters.
        '''
        result = self._values.get("web_acl_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorization(self) -> IAuthorization:
        result = self._values.get("authorization")
        assert result is not None, "Required property 'authorization' is missing"
        return typing.cast(IAuthorization, result)

    @builtins.property
    def error_responses(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_cloudfront.ErrorResponse]]:
        result = self._values.get("error_responses")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_cloudfront.ErrorResponse]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseDistributionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthFlow",
    "AuthFlowProps",
    "Authorization",
    "AuthorizationProps",
    "BaseDistribution",
    "BaseDistributionProps",
    "CommonDistributionProps",
    "IAuthorization",
    "ISpaAuthorization",
    "IStaticSiteAuthorization",
    "Mode",
    "RedirectPaths",
    "RetrieveUserPoolClientSecret",
    "RetrieveUserPoolClientSecretProps",
    "SecretGenerator",
    "SecretGeneratorProps",
    "SpaAuthorization",
    "SpaDistribution",
    "SpaDistributionProps",
    "StaticSiteAuthorization",
    "StaticSiteDistribution",
    "StaticSiteDistributionProps",
    "UserPoolClientCallbackUrls",
    "UserPoolClientRedirects",
    "UserPoolClientRedirectsProps",
]

publication.publish()
