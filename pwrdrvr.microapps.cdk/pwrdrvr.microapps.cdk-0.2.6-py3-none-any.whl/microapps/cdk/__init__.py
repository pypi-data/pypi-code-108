'''
![Build/Deploy CI](https://github.com/pwrdrvr/microapps-core/actions/workflows/ci.yml/badge.svg) ![Main Build](https://github.com/pwrdrvr/microapps-core/actions/workflows/main-build.yml/badge.svg) ![Release](https://github.com/pwrdrvr/microapps-core/actions/workflows/release.yml/badge.svg)

# Overview

The MicroApps project enables rapidly deploying many web apps to AWS on a single shared host name, fronted by a CloudFront Distribution, serving static assets from an S3 Bucket, and routing application requests via API Gateway. MicroApps is delivered as a CDK Construct for deployment, although alternative deployment methods can be used if desired and implemented.

MicroApps allows many versions of an application to be deployed either as ephemeral deploys (e.g. for pull request builds) or as semi-permanent deploys. The `microapps-router` Lambda function handled routing requests to apps to the current version targeted for a particular application start request using rules as complex as one is interested in implementing (e.g. A/B testing integration, canary releases, per-user rules for logged in users, per-group, per-deparment, and default rules).

Users start applications via a URL such as `[/{prefix}]/{appname}/`, which hits the `microapps-router` that looks up the version of the application to be run, then renders a transparent `iframe` with a link to that version. The URL seen by the user in the browser (and available for bookmarking) has no version in it, so subsequent launches (e.g. the next day or just in another tab) will lookup the version again. All relative URL API requests (e.g. `some/api/path`) will go to the corresponding API version that matches the version of the loaded static files, eliminating issues of incompatibility between static files and API deployments.

For development / testing purposes only, each version of an applicaton can be accessed directly via a URL of the pattern `[/{prefix}]/{appname}/{semver}/`. These "versioned" URLs are not intended to be advertised to end users as they would cause a user to be stuck on a particular version of the app if the URL was bookmarked. Note that the system does not limit access to particular versions of an application, as of 2022-01-26, but that can be added as a feature.

# Installation / CDK Constructs

* `npm i --save-dev @pwrdrvr/microapps-cdk`
* Add `MicroApps` construct to your stack
* The `MicroApps` construct does a "turn-key" deployment complete with the Release app
* [Construct Hub](https://constructs.dev/packages/@pwrdrvr/microapps-cdk/)

  * CDK API docs
  * Python, DotNet, Java, JS/TS installation instructions

# Why MicroApps

MicroApps are like micro services, but for Web UIs. A MicroApp allows a single functional site to be developed by many independent teams within an organization. Teams must coordinate deployments and agree upon one implementation technology and framework when building a monolithic, or even a monorepo, web application.

Teams using MicroApps can deploy independently of each other with coordination being required only at points of intentional integration (e.g. adding a feature to pass context from one MicroApp to another or coordination of a major feature release to users) and sharing UI styles, if desired (it is possible to build styles that look the same across many different UI frameworks).

MicroApps also allow each team to use a UI framework and backend language that is most appropriate for their solving their business problem. Not every app has to use React or Next.js or even Node on the backend, but instead they can use whatever framework they want and Java, Go, C#, Python, etc. for UI API calls.

For internal sites, or logged-in-customer sites, different tools or products can be hosted in entirely independent MicroApps. A menuing system / toolbar application can be created as a MicroApp and that menu app can open the apps in the system within a transparent iframe. For externally facing sites, such as for an e-commerce site, it is possible to have a MicroApp serving `/product/...`, another serving `/search/...`, another serving `/`, etc.

# Limitations / Future Development

* `iframes`

  * Yeah, yeah: `iframes` are not framesets and most of the hate about iframes is probably better directed at framesets
  * The iframe serves a purpose but it stinks that it is there, primarily because it will cause issues with search bot indexing (SEO)
  * There are other options available to implement that have their own drabacks:

    * Using the `microapps-router` to proxy the "app start" request to a particular version of an app that then renders all of it's API resource requests to versioned URLs

      * Works only with frameworks that support hashing filenams for each deploy to unique names
      * This page would need to be marked as non-cachable
      * This may work well with Next.js which wants to know the explicit path that it will be running at (it writes that path into all resource and API requests)
      * Possible issue: the app would need to work ok being displayed at `[/{prefix}]/{appname}` when it may think that it's being displayed at `[/{prefix}]/{appname}/{semver}`
      * Disadvantage: requires some level of UI framework features (e.g. writing the absolute resource paths) to work correctly - may not work as easily for all UI frameworks
    * HTML5 added features to allow setting the relative path of all subsequent requests to be different than that displayed in the address bar

      * Gotta see if this works in modern browsers
    * Option to ditch the multiple-versions feature

      * Works only with frameworks that support hashing filenams for each deploy to unique names
      * Allows usage of the deploy and routing tooling without advantages and disadvantages of multiple-versions support
* AWS Only

  * For the time being this has only been implemented for AWS technologies and APIs
  * It is possible that Azure and GCP have sufficient support to enable porting the framework
  * CDK would have to be replaced as well (unless it's made available for Azure and GCP in the near future)
* `microapps-publish` only supports Lambda function apps

  * There is no technical reason for the apps to only run as Lambda functions
  * Web apps could just as easily run on EC2, Kubernetes, EKS, ECS, etc
  * Anything that API Gateway can route to can work for serving a MicroApp
  * The publish tool needs to provide additional options for setting up the API Gateway route to the app
* Authentication

  * Authentication requires rolling your own API Gateway and CloudFront deployment at the moment
  * The "turn key" CDK Construct should provide options to show an example of how authentication can be integrated
* Release Rules

  * Currently only a Default rule is supported
  * Need to evaluate if a generic implementation can be made, possibly allowing plugins or webhooks to support arbitrary rules
  * If not possible to make it perfectly generic, consider providing a more complete reference implementation of examples

# Related Projects / Components

* Release App

  * The Release app is an initial, rudimentary, release control console for setting the default version of an application
  * Built with Next.js
  * [](https://github.com/pwrdrvr/microapps-app-release)
* Next.js Demo App

  * The Next.js Tutorial application deployed as a MicroApp
  * [](https://github.com/pwrdrvr/serverless-nextjs-demo)
* Serverless Next.js Router

  * [](https://github.com/pwrdrvr/serverless-nextjs-router)
  * Complementary to [@sls-next/serverless-component](https://github.com/serverless-nextjs/serverless-next.js)
  * Allows Next.js apps to run as Lambda @ Origin for speed and cost improvements vs Lambda@Edge
  * Essentially the router translates CloudFront Lambda events to API Gateway Lambda events and vice versa for responses
  * The `serverless-nextjs` project allows Next.js apps to run as Lambda functions without Express, but there was a design change to make the Lambda functions run at Edge (note: need to recheck if this changed after early 2021)

    * Lambda@Edge is *at least* 3x more expensive than Lambda at the origin:

      * In US East 1, the price per GB-Second is $0.00005001 for Lambda@Edge vs $0.0000166667 for Lambda at the origin
    * Additionally, any DB or services calls from Lambda@Edge back to the origin will pay that 3x higher per GB-Second cost for any time spent waiting to send the request and get a response. Example:

      * Lambda@Edge

        * 0.250s Round Trip Time (RTT) for EU-zone edge request to hit US-East 1 Origin
        * 0.200s DB lookup time
        * 0.050s CPU usage to process the DB response
        * 0.500s total billed time @ $0.00005001 @ 128 MB
        * $0.000003125625 total charge
      * Lambda at Origin

        * RTT does not apply (it's effectively 1-2 ms to hit a DB in the same region)
        * 0.200s DB lookup time
        * 0.050s CPU usage to process the DB response
        * 0.250s total billed time @ $0.0000166667 @ 128 MB
        * Half the billed time of running on Lambda@Edge
        * 1/6th the cost of running on Lambda@Edge:

          * $0.000000520834375 total charge (assuming no CPU time to process the response)
          * $0.000003125625 / $0.000000520834375 = 6x more expensive in Lambda@Edge

# Architecure Diagram

![Architecure Diagram](https://github.com/pwrdrvr/microapps-core/blob/main/assets/images/architecture-diagram.png)

# Project Layout

* [packages/cdk](https://github.com/pwrdrvr/microapps-core/tree/main/packages/cdk)

  * Example CDK Stack
  * Deploys MicroApps CDK stack for the GitHub Workflows
  * Can be used as an example of how to use the MicroApps CDK Construct
* [packages/demo-app](https://github.com/pwrdrvr/microapps-core/tree/main/packages/demo-app)

  * Example app with static resources and a Lambda function
  * Does not use any Web UI framework at all
* [packages/microapps-cdk](https://github.com/pwrdrvr/microapps-core/tree/main/packages/microapps-cdk)

  * MicroApps

    * "Turn key" CDK Construct that creates all assets needed for a working MicroApps deployment
  * MicroAppsAPIGwy

    * Create APIGateway HTTP API
    * Creates domain names to point to the edge (Cloudfront) and origin (API Gateway)
  * MicroAppsCF

    * Creates Cloudfront distribution
  * MicroAppsS3

    * Creates S3 buckets
  * MicroAppsSvcs

    * Create DynamoDB table
    * Create Deployer Lambda function
    * Create Router Lambda function
* [packages/microapps-datalib](https://github.com/pwrdrvr/microapps-core/tree/main/packages/microapps-datalib)

  * Installed from `npm`:

    * `npm i -g @pwrdrvr/microapps-datalib`
  * APIs for access to the DynamoDB Table used by `microapps-publish`, `microapps-deployer`, and `@pwrdrvr/microapps-app-release-cdk`
* [packages/microapps-deployer](https://github.com/pwrdrvr/microapps-core/tree/main/packages/microapps-deployer)

  * Lambda service invoked by `microapps-publish` to record new app/version in the DynamoDB table, create API Gateway integrations, copy S3 assets from staging to prod bucket, etc.
  * Returns a temporary S3 token with restricted access to the staging S3 bucket for upload of the static files for one app/semver
* [packages/microapps-publish](https://github.com/pwrdrvr/microapps-core/tree/main/packages/microapps-publish)

  * Installed from `npm`:

    * `npm i -g @pwrdrvr/microapps-publish`
  * Node executable that updates versions in config files, deploys static assets to the S3 staging bucket, optionally compiles and deploys a new Lambda function version, and invokes `microapps-deployer`
  * AWS IAM permissions required:

    * `lambda:InvokeFunction`
* [packages/microapps-router](https://github.com/pwrdrvr/microapps-core/tree/main/packages/microapps-router)

  * Lambda function that determines which version of an app to point a user to on a particular invocation

# Creating a MicroApp Using Zip Lambda Functions

[TBC]

# Creating a MicroApp Using Docker Lambda Functions

Note: semi-deprecated as of 2022-01-27. Zip Lambda functions are better supported.

## Next.js Apps

Create a Next.js app then follow the steps in this section to set it up for publishing to AWS Lambda @ Origin as a MicroApp. To publish new versions of the app use `npx microapps-publish --new-version x.y.z` when logged in to the target AWS account.

### Modify package.json

Replace the version with `0.0.0` so it can be modified by the `microapps-publish` tool.

### Install Dependencies

```
npm i --save-dev @sls-next/serverless-component@1.19.0 @pwrdrvr/serverless-nextjs-router @pwrdrvr/microapps-publish
```

### Dockerfile

Add this file to the root of the app.

```Dockerfile
FROM node:15-slim as base

WORKDIR /app

# Download the sharp libs once to save time
# Do this before copying anything else in
RUN mkdir -p image-lambda-npms && \
  cd image-lambda-npms && npm i sharp && \
  rm -rf node_modules/sharp/vendor/*/include/

# Copy in the build output from `npx serverless`
COPY .serverless_nextjs .
COPY config.json .

# Move the sharp libs into place
RUN rm -rf image-lambda/node_modules/ && \
  mv image-lambda-npms/node_modules image-labmda/ && \
  rm -rf image-lambda-npms



FROM public.ecr.aws/lambda/nodejs:14 AS final

# Copy in the munged code
COPY --from=base /app .

CMD [ "./index.handler" ]
```

### next.config.js

Add this file to the root of the app.

Replace `appname` with your URL path-compatible application name.

```js
const appRoot = '/appname/0.0.0';

// eslint-disable-next-line no-undef
module.exports = {
  target: 'serverless',
  webpack: (config, _options) => {
    return config;
  },
  basePath: appRoot,
  publicRuntimeConfig: {
    // Will be available on both server and client
    staticFolder: appRoot,
  },
};
```

### deploy.json

Add this file to the root of the app.

Replace `appname` with your URL path-compatible application name.

```json
{
  "AppName": "appname",
  "SemVer": "0.0.0",
  "DefaultFile": "",
  "StaticAssetsPath": "./.serverless_nextjs/assets/appname/0.0.0/",
  "LambdaARN": "arn:aws:lambda:us-east-1:123456789012:function:appname:v0_0_0",
  "AWSAccountID": "123456789012",
  "AWSRegion": "us-east-2",
  "ServerlessNextRouterPath": "./node_modules/@pwrdrvr/serverless-nextjs-router/dist/index.js"
}
```

### serverless.yaml

Add this file to the root of the app.

```yaml
nextApp:
  component: './node_modules/@sls-next/serverless-component'
  inputs:
    deploy: false
    uploadStaticAssetsFromBuild: false
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
        '''(experimental) Options for ``AddRoutes``.

        :param api_gwy_origin: (experimental) API Gateway CloudFront Origin for API calls.
        :param apigwy_origin_request_policy: (experimental) Origin Request policy for API Gateway Origin.
        :param bucket_apps_origin: (experimental) S3 Bucket CloudFront Origin for static assets.
        :param distro: (experimental) CloudFront Distribution to add the Behaviors (Routes) to.
        :param create_api_path_route: (experimental) Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param root_path_prefix: (experimental) Path prefix on the root of the CloudFront distribution.

        :stability: experimental
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
        '''(experimental) API Gateway CloudFront Origin for API calls.

        :stability: experimental
        '''
        result = self._values.get("api_gwy_origin")
        assert result is not None, "Required property 'api_gwy_origin' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.IOrigin, result)

    @builtins.property
    def apigwy_origin_request_policy(
        self,
    ) -> aws_cdk.aws_cloudfront.IOriginRequestPolicy:
        '''(experimental) Origin Request policy for API Gateway Origin.

        :stability: experimental
        '''
        result = self._values.get("apigwy_origin_request_policy")
        assert result is not None, "Required property 'apigwy_origin_request_policy' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.IOriginRequestPolicy, result)

    @builtins.property
    def bucket_apps_origin(self) -> aws_cdk.aws_cloudfront_origins.S3Origin:
        '''(experimental) S3 Bucket CloudFront Origin for static assets.

        :stability: experimental
        '''
        result = self._values.get("bucket_apps_origin")
        assert result is not None, "Required property 'bucket_apps_origin' is missing"
        return typing.cast(aws_cdk.aws_cloudfront_origins.S3Origin, result)

    @builtins.property
    def distro(self) -> aws_cdk.aws_cloudfront.Distribution:
        '''(experimental) CloudFront Distribution to add the Behaviors (Routes) to.

        :stability: experimental
        '''
        result = self._values.get("distro")
        assert result is not None, "Required property 'distro' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.Distribution, result)

    @builtins.property
    def create_api_path_route(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them.

        When false API routes with a period in the path will get routed to S3.

        When true API routes that contain /api/ in the path will get routed to API Gateway
        even if they have a period in the path.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("create_api_path_route")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path prefix on the root of the CloudFront distribution.

        :stability: experimental

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
        '''(experimental) Options for the ``CreateAPIOriginPolicy``.

        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param domain_name_edge: (experimental) Edge domain name used by CloudFront - If set a custom OriginRequestPolicy will be created that prevents the Host header from being passed to the origin.

        :stability: experimental
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
        '''(experimental) Optional asset name root.

        :default: - resource names auto assigned

        :stability: experimental

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional asset name suffix.

        :default: none

        :stability: experimental

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name_edge(self) -> typing.Optional[builtins.str]:
        '''(experimental) Edge domain name used by CloudFront - If set a custom OriginRequestPolicy will be created that prevents the Host header from being passed to the origin.

        :stability: experimental
        '''
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
    '''(experimental) Represents a MicroApps.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apigwy")
    def apigwy(self) -> "IMicroAppsAPIGwy":
        '''(experimental) {@inheritdoc IMicroAppsAPIGwy}.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cf")
    def cf(self) -> "IMicroAppsCF":
        '''(experimental) {@inheritdoc IMicroAppsCF}.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "IMicroAppsS3":
        '''(experimental) {@inheritdoc IMicroAppsS3}.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svcs")
    def svcs(self) -> "IMicroAppsSvcs":
        '''(experimental) {@inheritdoc IMicroAppsSvcs}.

        :stability: experimental
        '''
        ...


class _IMicroAppsProxy:
    '''(experimental) Represents a MicroApps.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroApps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apigwy")
    def apigwy(self) -> "IMicroAppsAPIGwy":
        '''(experimental) {@inheritdoc IMicroAppsAPIGwy}.

        :stability: experimental
        '''
        return typing.cast("IMicroAppsAPIGwy", jsii.get(self, "apigwy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cf")
    def cf(self) -> "IMicroAppsCF":
        '''(experimental) {@inheritdoc IMicroAppsCF}.

        :stability: experimental
        '''
        return typing.cast("IMicroAppsCF", jsii.get(self, "cf"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> "IMicroAppsS3":
        '''(experimental) {@inheritdoc IMicroAppsS3}.

        :stability: experimental
        '''
        return typing.cast("IMicroAppsS3", jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svcs")
    def svcs(self) -> "IMicroAppsSvcs":
        '''(experimental) {@inheritdoc IMicroAppsSvcs}.

        :stability: experimental
        '''
        return typing.cast("IMicroAppsSvcs", jsii.get(self, "svcs"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroApps).__jsii_proxy_class__ = lambda : _IMicroAppsProxy


@jsii.interface(jsii_type="@pwrdrvr/microapps-cdk.IMicroAppsAPIGwy")
class IMicroAppsAPIGwy(typing_extensions.Protocol):
    '''(experimental) Represents a MicroApps API Gateway.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''(experimental) API Gateway.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnAppsOrigin")
    def dn_apps_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IDomainName]:
        '''(experimental) Domain Name applied to API Gateway origin.

        :stability: experimental
        '''
        ...


class _IMicroAppsAPIGwyProxy:
    '''(experimental) Represents a MicroApps API Gateway.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroAppsAPIGwy"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpApi")
    def http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''(experimental) API Gateway.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, jsii.get(self, "httpApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnAppsOrigin")
    def dn_apps_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IDomainName]:
        '''(experimental) Domain Name applied to API Gateway origin.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IDomainName], jsii.get(self, "dnAppsOrigin"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsAPIGwy).__jsii_proxy_class__ = lambda : _IMicroAppsAPIGwyProxy


@jsii.interface(jsii_type="@pwrdrvr/microapps-cdk.IMicroAppsCF")
class IMicroAppsCF(typing_extensions.Protocol):
    '''(experimental) Represents a MicroApps CloudFront.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontDistro")
    def cloud_front_distro(self) -> aws_cdk.aws_cloudfront.Distribution:
        '''
        :stability: experimental
        '''
        ...


class _IMicroAppsCFProxy:
    '''(experimental) Represents a MicroApps CloudFront.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroAppsCF"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudFrontDistro")
    def cloud_front_distro(self) -> aws_cdk.aws_cloudfront.Distribution:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudfront.Distribution, jsii.get(self, "cloudFrontDistro"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsCF).__jsii_proxy_class__ = lambda : _IMicroAppsCFProxy


@jsii.interface(jsii_type="@pwrdrvr/microapps-cdk.IMicroAppsS3")
class IMicroAppsS3(typing_extensions.Protocol):
    '''(experimental) Represents a MicroApps S3.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketApps")
    def bucket_apps(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for deployed applications.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOAI")
    def bucket_apps_oai(self) -> aws_cdk.aws_cloudfront.OriginAccessIdentity:
        '''(experimental) CloudFront Origin Access Identity for the deployed applications bucket.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOrigin")
    def bucket_apps_origin(self) -> aws_cdk.aws_cloudfront_origins.S3Origin:
        '''(experimental) CloudFront Origin for the deployed applications bucket.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsStaging")
    def bucket_apps_staging(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for staged applications (prior to deploy).

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketLogs")
    def bucket_logs(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for CloudFront logs.

        :stability: experimental
        '''
        ...


class _IMicroAppsS3Proxy:
    '''(experimental) Represents a MicroApps S3.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroAppsS3"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketApps")
    def bucket_apps(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for deployed applications.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketApps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOAI")
    def bucket_apps_oai(self) -> aws_cdk.aws_cloudfront.OriginAccessIdentity:
        '''(experimental) CloudFront Origin Access Identity for the deployed applications bucket.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudfront.OriginAccessIdentity, jsii.get(self, "bucketAppsOAI"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOrigin")
    def bucket_apps_origin(self) -> aws_cdk.aws_cloudfront_origins.S3Origin:
        '''(experimental) CloudFront Origin for the deployed applications bucket.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudfront_origins.S3Origin, jsii.get(self, "bucketAppsOrigin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsStaging")
    def bucket_apps_staging(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for staged applications (prior to deploy).

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketAppsStaging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketLogs")
    def bucket_logs(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for CloudFront logs.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketLogs"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsS3).__jsii_proxy_class__ = lambda : _IMicroAppsS3Proxy


@jsii.interface(jsii_type="@pwrdrvr/microapps-cdk.IMicroAppsSvcs")
class IMicroAppsSvcs(typing_extensions.Protocol):
    '''(experimental) Represents a MicroApps Services.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deployerFunc")
    def deployer_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) Lambda function for the Deployer.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routerFunc")
    def router_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) Lambda function for the Router.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''(experimental) DynamoDB table used by Router, Deployer, and Release console app.

        :stability: experimental
        '''
        ...


class _IMicroAppsSvcsProxy:
    '''(experimental) Represents a MicroApps Services.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-cdk.IMicroAppsSvcs"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deployerFunc")
    def deployer_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) Lambda function for the Deployer.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "deployerFunc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routerFunc")
    def router_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) Lambda function for the Router.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "routerFunc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''(experimental) DynamoDB table used by Router, Deployer, and Release console app.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_dynamodb.ITable, jsii.get(self, "table"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsSvcs).__jsii_proxy_class__ = lambda : _IMicroAppsSvcsProxy


@jsii.implements(IMicroApps)
class MicroApps(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pwrdrvr/microapps-cdk.MicroApps",
):
    '''(experimental) Create a new MicroApps "turnkey" construct for simple deployments and for initial evaulation of the MicroApps framework.

    Use this construct to create a working entire stack.

    Do not use this construct when adding MicroApps to an existing
    CloudFront, API Gateway, S3 Bucket, etc. or where access
    to all features of the AWS Resources are needed (e.g. to
    add additional Behaviors to the CloudFront distribution, set authorizors
    on API Gateway, etc.).

    :see: {@link https://github.com/pwrdrvr/microapps-core/blob/main/packages/cdk/lib/MicroApps.ts | example usage in a CDK Stack }
    :stability: experimental
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
        :param app_env: (experimental) Passed to NODE_ENV of Router and Deployer Lambda functions. Default: dev
        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param cert_edge: (experimental) Certificate in US-East-1 for the CloudFront distribution.
        :param cert_origin: (experimental) Certificate in deployed region for the API Gateway.
        :param create_api_path_route: (experimental) Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param domain_name_edge: (experimental) Optional custom domain name for the CloudFront distribution. Default: auto-assigned
        :param domain_name_origin: (experimental) Optional custom domain name for the API Gateway HTTPv2 API. Default: auto-assigned
        :param r53_zone: (experimental) Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: (experimental) Path prefix on the root of the CloudFront distribution.
        :param s3_policy_bypass_aro_as: (experimental) Applies when using s3StrictBucketPolicy = true. AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy. This allows sessions that assume the IAM Role to be excluded from the DENY rules on the S3 Bucket Policy. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list. Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead. Note: This AROA must be specified to prevent this policy from locking out non-root sessions that have assumed the admin role. The notPrincipals will only match the role name exactly and will not match any session that has assumed the role since notPrincipals does not allow wildcard matches and does not do wildcard matches implicitly either. The AROA must be used because there are only 3 Principal variables available: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable aws:username, aws:userid, aws:PrincipalTag For an assumed role, aws:username is blank, aws:userid is: [unique id AKA AROA for Role]:[session name] Table of unique ID prefixes such as AROA: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes The name of the role is simply not available for an assumed role and, if it was, a complicated comparison would be requierd to prevent exclusion of applying the Deny Rule to roles from other accounts. To get the AROA with the AWS CLI: aws iam get-role --role-name ROLE-NAME aws iam get-user -–user-name USER-NAME
        :param s3_policy_bypass_principal_ar_ns: (experimental) Applies when using s3StrictBucketPolicy = true. IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy. Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list.
        :param s3_strict_bucket_policy: (experimental) Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version. This setting should be used when applications are less than fully trusted. Default: false

        :stability: experimental
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
        '''(experimental) {@inheritdoc IMicroAppsAPIGwy}.

        :stability: experimental
        '''
        return typing.cast(IMicroAppsAPIGwy, jsii.get(self, "apigwy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cf")
    def cf(self) -> IMicroAppsCF:
        '''(experimental) {@inheritdoc IMicroAppsCF}.

        :stability: experimental
        '''
        return typing.cast(IMicroAppsCF, jsii.get(self, "cf"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3")
    def s3(self) -> IMicroAppsS3:
        '''(experimental) {@inheritdoc IMicroAppsS3}.

        :stability: experimental
        '''
        return typing.cast(IMicroAppsS3, jsii.get(self, "s3"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="svcs")
    def svcs(self) -> IMicroAppsSvcs:
        '''(experimental) {@inheritdoc IMicroAppsSvcs}.

        :stability: experimental
        '''
        return typing.cast(IMicroAppsSvcs, jsii.get(self, "svcs"))


@jsii.implements(IMicroAppsAPIGwy)
class MicroAppsAPIGwy(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pwrdrvr/microapps-cdk.MicroAppsAPIGwy",
):
    '''(experimental) Create a new MicroApps API Gateway HTTP API endpoint.

    :stability: experimental
    '''

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
        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param cert_origin: (experimental) Optional local region ACM certificate to use for API Gateway Note: required when using a custom domain. Default: none
        :param domain_name_edge: (experimental) CloudFront edge domain name. Default: auto-assigned
        :param domain_name_origin: (experimental) API Gateway origin domain name. Default: auto-assigned
        :param r53_zone: (experimental) Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: (experimental) Path prefix on the root of the API Gateway Stage. Default: none

        :stability: experimental
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
        '''(experimental) API Gateway.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, jsii.get(self, "httpApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnAppsOrigin")
    def dn_apps_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IDomainName]:
        '''(experimental) Domain Name applied to API Gateway origin.

        :stability: experimental
        '''
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
        '''(experimental) Properties to initialize an instance of ``MicroAppsAPIGwy``.

        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param cert_origin: (experimental) Optional local region ACM certificate to use for API Gateway Note: required when using a custom domain. Default: none
        :param domain_name_edge: (experimental) CloudFront edge domain name. Default: auto-assigned
        :param domain_name_origin: (experimental) API Gateway origin domain name. Default: auto-assigned
        :param r53_zone: (experimental) Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: (experimental) Path prefix on the root of the API Gateway Stage. Default: none

        :stability: experimental
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
        '''(experimental) Optional asset name root.

        :default: - resource names auto assigned

        :stability: experimental

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional asset name suffix.

        :default: none

        :stability: experimental

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''(experimental) Optional local region ACM certificate to use for API Gateway Note: required when using a custom domain.

        :default: none

        :stability: experimental
        '''
        result = self._values.get("cert_origin")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def domain_name_edge(self) -> typing.Optional[builtins.str]:
        '''(experimental) CloudFront edge domain name.

        :default: auto-assigned

        :stability: experimental

        Example::

            apps.pwrdrvr.com
        '''
        result = self._values.get("domain_name_edge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name_origin(self) -> typing.Optional[builtins.str]:
        '''(experimental) API Gateway origin domain name.

        :default: auto-assigned

        :stability: experimental

        Example::

            apps-origin.pwrdrvr.com
        '''
        result = self._values.get("domain_name_origin")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def r53_zone(self) -> typing.Optional[aws_cdk.aws_route53.IHostedZone]:
        '''(experimental) Route53 zone in which to create optional ``domainNameEdge`` record.

        :stability: experimental
        '''
        result = self._values.get("r53_zone")
        return typing.cast(typing.Optional[aws_cdk.aws_route53.IHostedZone], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path prefix on the root of the API Gateway Stage.

        :default: none

        :stability: experimental

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
    '''(experimental) Create a new MicroApps CloudFront Distribution.

    :stability: experimental
    '''

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
        :param bucket_apps_origin: (experimental) S3 bucket origin for deployed applications.
        :param http_api: (experimental) API Gateway v2 HTTP API for apps.
        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param bucket_logs: (experimental) S3 bucket for CloudFront logs.
        :param cert_edge: (experimental) ACM Certificate that covers ``domainNameEdge`` name.
        :param create_api_path_route: (experimental) Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param domain_name_edge: (experimental) CloudFront Distribution domain name. Default: auto-assigned
        :param domain_name_origin: (experimental) API Gateway custom origin domain name. Default: - retrieved from httpApi, if possible
        :param r53_zone: (experimental) Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: (experimental) Path prefix on the root of the CloudFront distribution.

        :stability: experimental
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
        '''(experimental) Add API Gateway and S3 routes to an existing CloudFront Distribution.

        :param _scope: -
        :param api_gwy_origin: (experimental) API Gateway CloudFront Origin for API calls.
        :param apigwy_origin_request_policy: (experimental) Origin Request policy for API Gateway Origin.
        :param bucket_apps_origin: (experimental) S3 Bucket CloudFront Origin for static assets.
        :param distro: (experimental) CloudFront Distribution to add the Behaviors (Routes) to.
        :param create_api_path_route: (experimental) Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param root_path_prefix: (experimental) Path prefix on the root of the CloudFront distribution.

        :stability: experimental
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
        '''(experimental) Create or get the origin request policy.

        If a custom domain name is NOT used for the origin then a policy
        will be created.

        If a custom domain name IS used for the origin then the ALL_VIEWER
        policy will be returned.  This policy passes the Host header to the
        origin, which is fine when using a custom domain name on the origin.

        :param scope: -
        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param domain_name_edge: (experimental) Edge domain name used by CloudFront - If set a custom OriginRequestPolicy will be created that prevents the Host header from being passed to the origin.

        :stability: experimental
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
        '''
        :stability: experimental
        '''
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
        '''(experimental) Properties to initialize an instance of ``MicroAppsCF``.

        :param bucket_apps_origin: (experimental) S3 bucket origin for deployed applications.
        :param http_api: (experimental) API Gateway v2 HTTP API for apps.
        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param bucket_logs: (experimental) S3 bucket for CloudFront logs.
        :param cert_edge: (experimental) ACM Certificate that covers ``domainNameEdge`` name.
        :param create_api_path_route: (experimental) Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param domain_name_edge: (experimental) CloudFront Distribution domain name. Default: auto-assigned
        :param domain_name_origin: (experimental) API Gateway custom origin domain name. Default: - retrieved from httpApi, if possible
        :param r53_zone: (experimental) Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: (experimental) Path prefix on the root of the CloudFront distribution.

        :stability: experimental
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
        '''(experimental) S3 bucket origin for deployed applications.

        :stability: experimental
        '''
        result = self._values.get("bucket_apps_origin")
        assert result is not None, "Required property 'bucket_apps_origin' is missing"
        return typing.cast(aws_cdk.aws_cloudfront_origins.S3Origin, result)

    @builtins.property
    def http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''(experimental) API Gateway v2 HTTP API for apps.

        :stability: experimental
        '''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, result)

    @builtins.property
    def asset_name_root(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional asset name root.

        :default: - resource names auto assigned

        :stability: experimental

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional asset name suffix.

        :default: none

        :stability: experimental

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_logs(self) -> typing.Optional[aws_cdk.aws_s3.IBucket]:
        '''(experimental) S3 bucket for CloudFront logs.

        :stability: experimental
        '''
        result = self._values.get("bucket_logs")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.IBucket], result)

    @builtins.property
    def cert_edge(self) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''(experimental) ACM Certificate that covers ``domainNameEdge`` name.

        :stability: experimental
        '''
        result = self._values.get("cert_edge")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def create_api_path_route(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them.

        When false API routes with a period in the path will get routed to S3.

        When true API routes that contain /api/ in the path will get routed to API Gateway
        even if they have a period in the path.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("create_api_path_route")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_name_edge(self) -> typing.Optional[builtins.str]:
        '''(experimental) CloudFront Distribution domain name.

        :default: auto-assigned

        :stability: experimental

        Example::

            apps.pwrdrvr.com
        '''
        result = self._values.get("domain_name_edge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name_origin(self) -> typing.Optional[builtins.str]:
        '''(experimental) API Gateway custom origin domain name.

        :default: - retrieved from httpApi, if possible

        :stability: experimental

        Example::

            apps.pwrdrvr.com
        '''
        result = self._values.get("domain_name_origin")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def r53_zone(self) -> typing.Optional[aws_cdk.aws_route53.IHostedZone]:
        '''(experimental) Route53 zone in which to create optional ``domainNameEdge`` record.

        :stability: experimental
        '''
        result = self._values.get("r53_zone")
        return typing.cast(typing.Optional[aws_cdk.aws_route53.IHostedZone], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path prefix on the root of the CloudFront distribution.

        :stability: experimental

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
        '''(experimental) Properties to initialize an instance of ``MicroApps``.

        :param app_env: (experimental) Passed to NODE_ENV of Router and Deployer Lambda functions. Default: dev
        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param cert_edge: (experimental) Certificate in US-East-1 for the CloudFront distribution.
        :param cert_origin: (experimental) Certificate in deployed region for the API Gateway.
        :param create_api_path_route: (experimental) Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them. When false API routes with a period in the path will get routed to S3. When true API routes that contain /api/ in the path will get routed to API Gateway even if they have a period in the path. Default: true
        :param domain_name_edge: (experimental) Optional custom domain name for the CloudFront distribution. Default: auto-assigned
        :param domain_name_origin: (experimental) Optional custom domain name for the API Gateway HTTPv2 API. Default: auto-assigned
        :param r53_zone: (experimental) Route53 zone in which to create optional ``domainNameEdge`` record.
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: (experimental) Path prefix on the root of the CloudFront distribution.
        :param s3_policy_bypass_aro_as: (experimental) Applies when using s3StrictBucketPolicy = true. AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy. This allows sessions that assume the IAM Role to be excluded from the DENY rules on the S3 Bucket Policy. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list. Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead. Note: This AROA must be specified to prevent this policy from locking out non-root sessions that have assumed the admin role. The notPrincipals will only match the role name exactly and will not match any session that has assumed the role since notPrincipals does not allow wildcard matches and does not do wildcard matches implicitly either. The AROA must be used because there are only 3 Principal variables available: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable aws:username, aws:userid, aws:PrincipalTag For an assumed role, aws:username is blank, aws:userid is: [unique id AKA AROA for Role]:[session name] Table of unique ID prefixes such as AROA: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes The name of the role is simply not available for an assumed role and, if it was, a complicated comparison would be requierd to prevent exclusion of applying the Deny Rule to roles from other accounts. To get the AROA with the AWS CLI: aws iam get-role --role-name ROLE-NAME aws iam get-user -–user-name USER-NAME
        :param s3_policy_bypass_principal_ar_ns: (experimental) Applies when using s3StrictBucketPolicy = true. IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy. Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list.
        :param s3_strict_bucket_policy: (experimental) Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version. This setting should be used when applications are less than fully trusted. Default: false

        :stability: experimental
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
        '''(experimental) Passed to NODE_ENV of Router and Deployer Lambda functions.

        :default: dev

        :stability: experimental
        '''
        result = self._values.get("app_env")
        assert result is not None, "Required property 'app_env' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def asset_name_root(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional asset name root.

        :default: - resource names auto assigned

        :stability: experimental

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional asset name suffix.

        :default: none

        :stability: experimental

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_edge(self) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''(experimental) Certificate in US-East-1 for the CloudFront distribution.

        :stability: experimental
        '''
        result = self._values.get("cert_edge")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def cert_origin(
        self,
    ) -> typing.Optional[aws_cdk.aws_certificatemanager.ICertificate]:
        '''(experimental) Certificate in deployed region for the API Gateway.

        :stability: experimental
        '''
        result = self._values.get("cert_origin")
        return typing.cast(typing.Optional[aws_cdk.aws_certificatemanager.ICertificate], result)

    @builtins.property
    def create_api_path_route(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Create an extra Behavior (Route) for /api/ that allows API routes to have a period in them.

        When false API routes with a period in the path will get routed to S3.

        When true API routes that contain /api/ in the path will get routed to API Gateway
        even if they have a period in the path.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("create_api_path_route")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def domain_name_edge(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional custom domain name for the CloudFront distribution.

        :default: auto-assigned

        :stability: experimental

        Example::

            apps.pwrdrvr.com
        '''
        result = self._values.get("domain_name_edge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def domain_name_origin(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional custom domain name for the API Gateway HTTPv2 API.

        :default: auto-assigned

        :stability: experimental

        Example::

            apps-origin.pwrdrvr.com
        '''
        result = self._values.get("domain_name_origin")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def r53_zone(self) -> typing.Optional[aws_cdk.aws_route53.IHostedZone]:
        '''(experimental) Route53 zone in which to create optional ``domainNameEdge`` record.

        :stability: experimental
        '''
        result = self._values.get("r53_zone")
        return typing.cast(typing.Optional[aws_cdk.aws_route53.IHostedZone], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path prefix on the root of the CloudFront distribution.

        :stability: experimental

        Example::

            dev/
        '''
        result = self._values.get("root_path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_policy_bypass_aro_as(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Applies when using s3StrictBucketPolicy = true.

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
        :stability: experimental

        Example::

            [ 'AROA1234567890123' ]
        '''
        result = self._values.get("s3_policy_bypass_aro_as")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_policy_bypass_principal_ar_ns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Applies when using s3StrictBucketPolicy = true.

        IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy.

        Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``.

        Typically any admin roles / users that need to view or manage the S3 Bucket
        would be added to this list.

        :see: s3PolicyBypassAROAs
        :stability: experimental

        Example::

            ['arn:aws:iam::1234567890123:role/AdminAccess', 'arn:aws:iam::1234567890123:user/MyAdminUser']
        '''
        result = self._values.get("s3_policy_bypass_principal_ar_ns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_strict_bucket_policy(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version.

        This setting should be used when applications are less than
        fully trusted.

        :default: false

        :stability: experimental
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
    '''(experimental) Create a new MicroApps S3 Bucket.

    :stability: experimental
    '''

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
        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param bucket_apps_name: (experimental) S3 deployed apps bucket name. Default: auto-assigned
        :param bucket_apps_staging_name: (experimental) S3 staging apps bucket name. Default: auto-assigned
        :param bucket_logs_name: (experimental) S3 logs bucket name. Default: auto-assigned
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckets will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default

        :stability: experimental
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
        '''(experimental) S3 bucket for deployed applications.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketApps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOAI")
    def bucket_apps_oai(self) -> aws_cdk.aws_cloudfront.OriginAccessIdentity:
        '''(experimental) CloudFront Origin Access Identity for the deployed applications bucket.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudfront.OriginAccessIdentity, jsii.get(self, "bucketAppsOAI"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsOrigin")
    def bucket_apps_origin(self) -> aws_cdk.aws_cloudfront_origins.S3Origin:
        '''(experimental) CloudFront Origin for the deployed applications bucket.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_cloudfront_origins.S3Origin, jsii.get(self, "bucketAppsOrigin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketAppsStaging")
    def bucket_apps_staging(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for staged applications (prior to deploy).

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_s3.IBucket, jsii.get(self, "bucketAppsStaging"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucketLogs")
    def bucket_logs(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for CloudFront logs.

        :stability: experimental
        '''
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
        '''(experimental) Properties to initialize an instance of ``MicroAppsS3``.

        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param bucket_apps_name: (experimental) S3 deployed apps bucket name. Default: auto-assigned
        :param bucket_apps_staging_name: (experimental) S3 staging apps bucket name. Default: auto-assigned
        :param bucket_logs_name: (experimental) S3 logs bucket name. Default: auto-assigned
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckets will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default

        :stability: experimental
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
        '''(experimental) Optional asset name root.

        :default: - resource names auto assigned

        :stability: experimental

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional asset name suffix.

        :default: none

        :stability: experimental

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_apps_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) S3 deployed apps bucket name.

        :default: auto-assigned

        :stability: experimental
        '''
        result = self._values.get("bucket_apps_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_apps_staging_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) S3 staging apps bucket name.

        :default: auto-assigned

        :stability: experimental
        '''
        result = self._values.get("bucket_apps_staging_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bucket_logs_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) S3 logs bucket name.

        :default: auto-assigned

        :stability: experimental
        '''
        result = self._values.get("bucket_logs_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckets will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default

        :stability: experimental
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
    '''(experimental) Create a new MicroApps Services construct, including the Deployer and Router Lambda Functions, and the DynamoDB Table used by both.

    :stability: experimental
    '''

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
        :param app_env: (experimental) Application environment, passed as ``NODE_ENV`` to the Router and Deployer Lambda functions.
        :param bucket_apps: (experimental) S3 bucket for deployed applications.
        :param bucket_apps_oai: (experimental) CloudFront Origin Access Identity for the deployed applications bucket.
        :param bucket_apps_staging: (experimental) S3 bucket for staged applications (prior to deploy).
        :param http_api: (experimental) API Gateway v2 HTTP for Router and app.
        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: (experimental) Path prefix on the root of the deployment. Default: none
        :param s3_policy_bypass_aro_as: (experimental) Applies when using s3StrictBucketPolicy = true. AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy. This allows sessions that assume the IAM Role to be excluded from the DENY rules on the S3 Bucket Policy. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list. Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead. Note: This AROA must be specified to prevent this policy from locking out non-root sessions that have assumed the admin role. The notPrincipals will only match the role name exactly and will not match any session that has assumed the role since notPrincipals does not allow wildcard matches and does not do wildcard matches implicitly either. The AROA must be used because there are only 3 Principal variables available: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable aws:username, aws:userid, aws:PrincipalTag For an assumed role, aws:username is blank, aws:userid is: [unique id AKA AROA for Role]:[session name] Table of unique ID prefixes such as AROA: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes The name of the role is simply not available for an assumed role and, if it was, a complicated comparison would be requierd to prevent exclusion of applying the Deny Rule to roles from other accounts. To get the AROA with the AWS CLI: aws iam get-role --role-name ROLE-NAME aws iam get-user -–user-name USER-NAME
        :param s3_policy_bypass_principal_ar_ns: (experimental) Applies when using s3StrictBucketPolicy = true. IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy. Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list.
        :param s3_strict_bucket_policy: (experimental) Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version. This setting should be used when applications are less than fully trusted. Default: false

        :stability: experimental
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
        '''(experimental) Lambda function for the Deployer.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "deployerFunc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routerFunc")
    def router_func(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) Lambda function for the Router.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "routerFunc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="table")
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''(experimental) DynamoDB table used by Router, Deployer, and Release console app.

        :stability: experimental
        '''
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
        '''(experimental) Properties to initialize an instance of ``MicroAppsSvcs``.

        :param app_env: (experimental) Application environment, passed as ``NODE_ENV`` to the Router and Deployer Lambda functions.
        :param bucket_apps: (experimental) S3 bucket for deployed applications.
        :param bucket_apps_oai: (experimental) CloudFront Origin Access Identity for the deployed applications bucket.
        :param bucket_apps_staging: (experimental) S3 bucket for staged applications (prior to deploy).
        :param http_api: (experimental) API Gateway v2 HTTP for Router and app.
        :param asset_name_root: (experimental) Optional asset name root. Default: - resource names auto assigned
        :param asset_name_suffix: (experimental) Optional asset name suffix. Default: none
        :param removal_policy: (experimental) RemovalPolicy override for child resources. Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true`` Default: - per resource default
        :param root_path_prefix: (experimental) Path prefix on the root of the deployment. Default: none
        :param s3_policy_bypass_aro_as: (experimental) Applies when using s3StrictBucketPolicy = true. AROAs of the IAM Role to exclude from the DENY rules on the S3 Bucket Policy. This allows sessions that assume the IAM Role to be excluded from the DENY rules on the S3 Bucket Policy. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list. Roles / users that are used directly, not assumed, can be added to ``s3PolicyBypassRoleNames`` instead. Note: This AROA must be specified to prevent this policy from locking out non-root sessions that have assumed the admin role. The notPrincipals will only match the role name exactly and will not match any session that has assumed the role since notPrincipals does not allow wildcard matches and does not do wildcard matches implicitly either. The AROA must be used because there are only 3 Principal variables available: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html#principaltable aws:username, aws:userid, aws:PrincipalTag For an assumed role, aws:username is blank, aws:userid is: [unique id AKA AROA for Role]:[session name] Table of unique ID prefixes such as AROA: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html#identifiers-prefixes The name of the role is simply not available for an assumed role and, if it was, a complicated comparison would be requierd to prevent exclusion of applying the Deny Rule to roles from other accounts. To get the AROA with the AWS CLI: aws iam get-role --role-name ROLE-NAME aws iam get-user -–user-name USER-NAME
        :param s3_policy_bypass_principal_ar_ns: (experimental) Applies when using s3StrictBucketPolicy = true. IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy. Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``. Typically any admin roles / users that need to view or manage the S3 Bucket would be added to this list.
        :param s3_strict_bucket_policy: (experimental) Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version. This setting should be used when applications are less than fully trusted. Default: false

        :stability: experimental
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
        '''(experimental) Application environment, passed as ``NODE_ENV`` to the Router and Deployer Lambda functions.

        :stability: experimental
        '''
        result = self._values.get("app_env")
        assert result is not None, "Required property 'app_env' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bucket_apps(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for deployed applications.

        :stability: experimental
        '''
        result = self._values.get("bucket_apps")
        assert result is not None, "Required property 'bucket_apps' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def bucket_apps_oai(self) -> aws_cdk.aws_cloudfront.OriginAccessIdentity:
        '''(experimental) CloudFront Origin Access Identity for the deployed applications bucket.

        :stability: experimental
        '''
        result = self._values.get("bucket_apps_oai")
        assert result is not None, "Required property 'bucket_apps_oai' is missing"
        return typing.cast(aws_cdk.aws_cloudfront.OriginAccessIdentity, result)

    @builtins.property
    def bucket_apps_staging(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) S3 bucket for staged applications (prior to deploy).

        :stability: experimental
        '''
        result = self._values.get("bucket_apps_staging")
        assert result is not None, "Required property 'bucket_apps_staging' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        '''(experimental) API Gateway v2 HTTP for Router and app.

        :stability: experimental
        '''
        result = self._values.get("http_api")
        assert result is not None, "Required property 'http_api' is missing"
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, result)

    @builtins.property
    def asset_name_root(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional asset name root.

        :default: - resource names auto assigned

        :stability: experimental

        Example::

            microapps
        '''
        result = self._values.get("asset_name_root")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def asset_name_suffix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional asset name suffix.

        :default: none

        :stability: experimental

        Example::

            -dev-pr-12
        '''
        result = self._values.get("asset_name_suffix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) RemovalPolicy override for child resources.

        Note: if set to DESTROY the S3 buckes will have ``autoDeleteObjects`` set to ``true``

        :default: - per resource default

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def root_path_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) Path prefix on the root of the deployment.

        :default: none

        :stability: experimental

        Example::

            dev/
        '''
        result = self._values.get("root_path_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_policy_bypass_aro_as(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Applies when using s3StrictBucketPolicy = true.

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
        :stability: experimental

        Example::

            [ 'AROA1234567890123' ]
        '''
        result = self._values.get("s3_policy_bypass_aro_as")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_policy_bypass_principal_ar_ns(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Applies when using s3StrictBucketPolicy = true.

        IAM Role or IAM User names to exclude from the DENY rules on the S3 Bucket Policy.

        Roles that are Assumed must instead have their AROA added to ``s3PolicyBypassAROAs``.

        Typically any admin roles / users that need to view or manage the S3 Bucket
        would be added to this list.

        :see: s3PolicyBypassAROAs
        :stability: experimental

        Example::

            ['arn:aws:iam::1234567890123:role/AdminAccess', 'arn:aws:iam::1234567890123:user/MyAdminUser']
        '''
        result = self._values.get("s3_policy_bypass_principal_ar_ns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_strict_bucket_policy(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Use a strict S3 Bucket Policy that prevents applications from reading/writing/modifying/deleting files in the S3 Bucket outside of the path that is specific to their app/version.

        This setting should be used when applications are less than
        fully trusted.

        :default: false

        :stability: experimental
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
