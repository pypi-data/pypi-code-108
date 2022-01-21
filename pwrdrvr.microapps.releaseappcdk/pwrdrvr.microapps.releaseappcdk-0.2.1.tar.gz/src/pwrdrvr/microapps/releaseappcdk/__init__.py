'''
![Build/Deploy CI](https://github.com/pwrdrvr/microapps-app-release/actions/workflows/ci.yml/badge.svg) ![Main Build](https://github.com/pwrdrvr/microapps-app-release/actions/workflows/main-build.yml/badge.svg) ![Deploy](https://github.com/pwrdrvr/microapps-app-release/actions/workflows/deploy.yml/badge.svg)

# Overview

This is the Release Console for the MicroApps framework.
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
    '''Represents a Release app.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''The Lambda function created.'''
        ...


class _IMicroAppsAppReleaseProxy:
    '''Represents a Release app.'''

    __jsii_type__: typing.ClassVar[str] = "@pwrdrvr/microapps-app-release-cdk.IMicroAppsAppRelease"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.IFunction:
        '''The Lambda function created.'''
        return typing.cast(aws_cdk.aws_lambda.IFunction, jsii.get(self, "lambdaFunction"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMicroAppsAppRelease).__jsii_proxy_class__ = lambda : _IMicroAppsAppReleaseProxy


@jsii.implements(IMicroAppsAppRelease)
class MicroAppsAppRelease(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pwrdrvr/microapps-app-release-cdk.MicroAppsAppRelease",
):
    '''Release app for MicroApps framework.

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
        '''Lambda function, permissions, and assets used by the MicroApps Release app.

        :param scope: -
        :param id: -
        :param static_assets_s3_bucket: Bucket with the static assets of the app. Next.js apps need access to the static assets bucket.
        :param table: DynamoDB table for data displayed / edited in the app. This table is used by @pwrdrvr/microapps-datalib.
        :param function_name: Name for the Lambda function. While this can be random, it's much easier to make it deterministic so it can be computed for passing to ``microapps-publish``. Default: auto-generated
        :param node_env: NODE_ENV to set on Lambda.
        :param removal_policy: Removal Policy to pass to assets (e.g. Lambda function).
        :param sharp_layer: ``sharp`` node module Lambda Layer for Next.js image adjustments.
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
        '''The Lambda function created.'''
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
        '''Properties to initialize an instance of ``MicroAppsAppRelease``.

        :param static_assets_s3_bucket: Bucket with the static assets of the app. Next.js apps need access to the static assets bucket.
        :param table: DynamoDB table for data displayed / edited in the app. This table is used by @pwrdrvr/microapps-datalib.
        :param function_name: Name for the Lambda function. While this can be random, it's much easier to make it deterministic so it can be computed for passing to ``microapps-publish``. Default: auto-generated
        :param node_env: NODE_ENV to set on Lambda.
        :param removal_policy: Removal Policy to pass to assets (e.g. Lambda function).
        :param sharp_layer: ``sharp`` node module Lambda Layer for Next.js image adjustments.
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
        '''Bucket with the static assets of the app.

        Next.js apps need access to the static assets bucket.
        '''
        result = self._values.get("static_assets_s3_bucket")
        assert result is not None, "Required property 'static_assets_s3_bucket' is missing"
        return typing.cast(aws_cdk.aws_s3.IBucket, result)

    @builtins.property
    def table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''DynamoDB table for data displayed / edited in the app.

        This table is used by @pwrdrvr/microapps-datalib.
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(aws_cdk.aws_dynamodb.ITable, result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''Name for the Lambda function.

        While this can be random, it's much easier to make it deterministic
        so it can be computed for passing to ``microapps-publish``.

        :default: auto-generated
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_env(self) -> typing.Optional[builtins.str]:
        '''NODE_ENV to set on Lambda.'''
        result = self._values.get("node_env")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''Removal Policy to pass to assets (e.g. Lambda function).'''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def sharp_layer(self) -> typing.Optional[aws_cdk.aws_lambda.ILayerVersion]:
        '''``sharp`` node module Lambda Layer for Next.js image adjustments.

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
