'''
![Build/Deploy CI](https://github.com/pwrdrvr/microapps-app-release/actions/workflows/ci.yml/badge.svg) ![Main Build](https://github.com/pwrdrvr/microapps-app-release/actions/workflows/jsii.yml/badge.svg) ![Deploy](https://github.com/pwrdrvr/microapps-app-release/actions/workflows/deploy.yml/badge.svg) ![Release](https://github.com/pwrdrvr/microapps-app-release/actions/workflows/release.yml/badge.svg)

# Overview

Example / basic Next.js-based Release app for the [MicroApps framework](https://github.com/pwrdrvr/microapps-core).

# Screenshot

![Main View Screenshot of App](https://github.com/pwrdrvr/microapps-app-release/blob/main/assets/images/app-main.png)

# Try the App

[Launch the App](https://dukw9jtyq2dwo.cloudfront.net/prefix/release/)

# Video Preview of the App

![Video Preview of App](https://github.com/pwrdrvr/microapps-app-release/blob/main/assets/videos/app-overview.gif)

# Functionality

* Lists all deployed applications
* Shows all versions and rules per application
* Allows setting the `default` rule (pointer to version) for each application

# Installation

The application is intended to be deployed upon the [MicroApps framework](https://github.com/pwrdrvr/microapps-core) and it operates on a DynamoDB Table created by the MicroApps framework. Thus, it is required that there be a deployment of MicroApps that can receive this application. Deploying the MicroApps framework and general application deployment instructions are covered by the MicroApps documentation.

The application is packaged for deployment via AWS CDK and consists of a single Lambda function that reads/writes the MicroApps DynamoDB Table.

The CDK Construct is available for TypeScript, DotNet, Java, and Python with docs and install instructions available on [@pwrdrvr/microapps-app-release-cdk - Construct Hub](https://constructs.dev/packages/@pwrdrvr/microapps-app-release-cdk).

## Quick Notes for TypeScript / Node.js Installation

```sh
npm i --save-dev @pwrdrvr/microapps-app-release-cdk
```

## Sharp Image Processing Lambda Layer

The Sharp layer is extracted and shared across all Serverless Next.js apps. The Sharp layer can be built with whatever features you are licensed for (or just open source features) following the example in this PR:

https://github.com/zoellner/sharp-heic-lambda-layer/pull/3

## Add the Construct to your CDK Stack

See [cdk-stack](packages/cdk-stack/lib/svcs.ts) for a complete example used to deploy this app for PR builds.

```python
import { MicroAppsAppRelease } from '@pwrdrvr/microapps-app-release-cdk';

const app = new MicroAppsAppRelease(this, 'app', {
  functionName: `microapps-app-${appName}${shared.envSuffix}${shared.prSuffix}`,
  staticAssetsS3Bucket: s3.Bucket.fromBucketName(this, 'apps-bucket', shared.s3BucketName),
  table: dynamodb.Table.fromTableName(this, 'apps-table', shared.tableName),
  nodeEnv: shared.env as Env,
  removalPolicy: shared.isPR ? RemovalPolicy.DESTROY : RemovalPolicy.RETAIN,
  sharpLayer,
});
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
import aws_cdk.aws_dynamodb
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import constructs


@jsii.interface(jsii_type="@pwrdrvr/microapps-app-release-cdk.IMicroAppsAppRelease")
class IMicroAppsAppRelease(typing_extensions.Protocol):
    '''(experimental) Represents a Release app.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The Lambda function created.

        :stability: experimental
        '''
        ...


class _IMicroAppsAppReleaseProxy:
    '''(experimental) Represents a Release app.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-app-release-cdk.IMicroAppsAppRelease"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The Lambda function created.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "lambdaFunction"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsAppRelease).__jsii_proxy_class__ = lambda : _IMicroAppsAppReleaseProxy


@jsii.implements(IMicroAppsAppRelease)
class MicroAppsAppRelease(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pwrdrvr/microapps-app-release-cdk.MicroAppsAppRelease",
):
    '''(experimental) Release app for MicroApps framework.

    :stability: experimental
    :remarks:

    The Release app lists apps, versions, and allows setting the default
    version of an app.  The app is just an example of what can be done, it
    is not feature complete for all use cases.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        static_assets_s3_bucket: aws_cdk.aws_s3.IBucket,
        table: aws_cdk.aws_dynamodb.ITable,
        function_name: typing.Optional[builtins.str] = None,
        node_env: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        sharp_layer: typing.Optional[aws_cdk.aws_lambda.ILayerVersion] = None,
    ) -> None:
        '''(experimental) Lambda function, permissions, and assets used by the MicroApps Release app.

        :param scope: -
        :param id: -
        :param static_assets_s3_bucket: (experimental) Bucket with the static assets of the app. Next.js apps need access to the static assets bucket.
        :param table: (experimental) DynamoDB table for data displayed / edited in the app. This table is used by @pwrdrvr/microapps-datalib.
        :param function_name: (experimental) Name for the Lambda function. While this can be random, it's much easier to make it deterministic so it can be computed for passing to ``microapps-publish``. Default: auto-generated
        :param node_env: (experimental) NODE_ENV to set on Lambda.
        :param removal_policy: (experimental) Removal Policy to pass to assets (e.g. Lambda function).
        :param sharp_layer: (experimental) ``sharp`` node module Lambda Layer for Next.js image adjustments.

        :stability: experimental
        '''
        props = MicroAppsAppReleaseProps(
            static_assets_s3_bucket=static_assets_s3_bucket,
            table=table,
            function_name=function_name,
            node_env=node_env,
            removal_policy=removal_policy,
            sharp_layer=sharp_layer,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The Lambda function created.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "lambdaFunction"))


@jsii.data_type(
    jsii_type="@pwrdrvr/microapps-app-release-cdk.MicroAppsAppReleaseProps",
    jsii_struct_bases=[],
    name_mapping={
        "static_assets_s3_bucket": "staticAssetsS3Bucket",
        "table": "table",
        "function_name": "functionName",
        "node_env": "nodeEnv",
        "removal_policy": "removalPolicy",
        "sharp_layer": "sharpLayer",
    },
)
class MicroAppsAppReleaseProps:
    def __init__(
        self,
        *,
        static_assets_s3_bucket: aws_cdk.aws_s3.IBucket,
        table: aws_cdk.aws_dynamodb.ITable,
        function_name: typing.Optional[builtins.str] = None,
        node_env: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        sharp_layer: typing.Optional[aws_cdk.aws_lambda.ILayerVersion] = None,
    ) -> None:
        '''(experimental) Properties to initialize an instance of ``MicroAppsAppRelease``.

        :param static_assets_s3_bucket: (experimental) Bucket with the static assets of the app. Next.js apps need access to the static assets bucket.
        :param table: (experimental) DynamoDB table for data displayed / edited in the app. This table is used by @pwrdrvr/microapps-datalib.
        :param function_name: (experimental) Name for the Lambda function. While this can be random, it's much easier to make it deterministic so it can be computed for passing to ``microapps-publish``. Default: auto-generated
        :param node_env: (experimental) NODE_ENV to set on Lambda.
        :param removal_policy: (experimental) Removal Policy to pass to assets (e.g. Lambda function).
        :param sharp_layer: (experimental) ``sharp`` node module Lambda Layer for Next.js image adjustments.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "static_assets_s3_bucket": static_assets_s3_bucket,
            "table": table,
        }
        if function_name is not None:
            self._values["function_name"] = function_name
        if node_env is not None:
            self._values["node_env"] = node_env
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if sharp_layer is not None:
            self._values["sharp_layer"] = sharp_layer

    @builtins.property
    def static_assets_s3_bucket(self) -> aws_cdk.aws_s3.IBucket:
        '''(experimental) Bucket with the static assets of the app.

        Next.js apps need access to the static assets bucket.

        :stability: experimental
        '''
        result = self._values.get("static_assets_s3_bucket")
        assert result is not None, "Required property 'static_assets_s3_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''(experimental) DynamoDB table for data displayed / edited in the app.

        This table is used by @pwrdrvr/microapps-datalib.

        :stability: experimental
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(aws_cdk.aws_dynamodb.ITable, result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name for the Lambda function.

        While this can be random, it's much easier to make it deterministic
        so it can be computed for passing to ``microapps-publish``.

        :default: auto-generated

        :stability: experimental
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_env(self) -> typing.Optional[builtins.str]:
        '''(experimental) NODE_ENV to set on Lambda.

        :stability: experimental
        '''
        result = self._values.get("node_env")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) Removal Policy to pass to assets (e.g. Lambda function).

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def sharp_layer(self) -> typing.Optional[aws_cdk.aws_lambda.ILayerVersion]:
        '''(experimental) ``sharp`` node module Lambda Layer for Next.js image adjustments.

        :stability: experimental

        Example::

            https://github.com/zoellner/sharp-heic-lambda-layer/pull/3
        '''
        result = self._values.get("sharp_layer")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.ILayerVersion], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicroAppsAppReleaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IMicroAppsAppRelease",
    "MicroAppsAppRelease",
    "MicroAppsAppReleaseProps",
]

publication.publish()
