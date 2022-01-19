'''
# aws-apigateway-sagemakerendpoint module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_apigateway_sagemakerendpoint`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-apigateway-sagemakerendpoint`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.apigatewaysagemakerendpoint`|

## Overview

This AWS Solutions Construct implements an Amazon API Gateway connected to an Amazon SageMaker endpoint pattern.

Here is a minimal deployable pattern definition in Typescript:

```javascript
import { ApiGatewayToSageMakerEndpoint, ApiGatewayToSageMakerEndpointProps } from '@aws-solutions-constructs/aws-apigateway-sagemakerendpoint';

// Below is an example VTL (Velocity Template Language) mapping template for mapping the Api GET request to the Sagemaker POST request
const requestTemplate =
`{
    "instances": [
#set( $user_id = $input.params("user_id") )
#set( $items = $input.params("items") )
#foreach( $item in $items.split(",") )
    {"in0": [$user_id], "in1": [$item]}#if( $foreach.hasNext ),#end
    $esc.newline
#end
    ]
}`;

// Replace 'my-endpoint' with your Sagemaker Inference Endpoint
new ApiGatewayToSageMakerEndpoint(this, 'test-apigw-sagemakerendpoint', {
    endpointName: 'my-endpoint',
    resourcePath: '{user_id}',
    requestMappingTemplate: requestTemplate
});
```

## Initializer

```text
new ApiGatewayToSageMakerEndpoint(scope: Construct, id: string, props: ApiGatewayToSageMakerEndpointProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`ApiGatewayToSageMakerEndpointProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiGatewayProps?|[`api.RestApiProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApiProps.html)|Optional user-provided props to override the default props for the API Gateway.|
|apiGatewayExecutionRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|IAM Role used by API Gateway to invoke the SageMaker endpoint. If not specified, a default role is created with access to `endpointName`.|
|endpointName|`string`|Name of the deployed SageMaker inference endpoint.|
|resourceName?|`string`|Optional resource name where the GET method will be available.|
|resourcePath|`string`|Resource path for the GET method. The variable defined here can be referenced in `requestMappingTemplate`.|
|requestMappingTemplate|`string`|Mapping template to convert GET requests received on the REST API to POST requests expected by the SageMaker endpoint.|
|responseMappingTemplate?|`string`|Optional mapping template to convert responses received from the SageMaker endpoint.|
|logGroupProps?|[`logs.LogGroupProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroupProps.html)|User provided props to override the default props for for the CloudWatchLogs LogGroup.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|apiGateway|[`api.RestApi`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.RestApi.html)|Returns an instance of the API Gateway REST API created by the pattern.|
|apiGatewayRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway.|
|apiGatewayCloudWatchRole?|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for API Gateway for CloudWatch access.|
|apiGatewayLogGroup|[`logs.LogGroup`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-logs.LogGroup.html)|Returns an instance of the LogGroup created by the construct for API Gateway access logging to CloudWatch.|

## Sample API Usage

> **Note**: Each SageMaker endpoint is unique, and the response from the API will depend on the deployed model. The example given below assumes the sample from [this blog post](https://aws.amazon.com/blogs/machine-learning/creating-a-machine-learning-powered-rest-api-with-amazon-api-gateway-mapping-templates-and-amazon-sagemaker/). For a reference on how that'd be implemented, please refer to [integ.apigateway-sagemakerendpoint-overwrite.ts](test/integ.apigateway-sagemakerendpoint-overwrite.ts).

| **Method** | **Request Path** | **Query String** | **SageMaker Action** | **Description** |
|:-------------|:----------------|-----------------|-----------------|-----------------|
|GET|`/321`| `items=101,131,162` |`sagemaker:InvokeEndpoint`|Retrieves the predictions for a specific user and items.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon API Gateway

* Deploy an edge-optimized API endpoint
* Enable CloudWatch logging for API Gateway
* Configure least privilege access IAM role for API Gateway
* Set the default authorizationType for all API methods to IAM
* Enable X-Ray Tracing
* Validate request parameters before passing data to SageMaker

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

import aws_cdk.aws_apigateway
import aws_cdk.aws_iam
import aws_cdk.aws_logs
import aws_cdk.core


class ApiGatewayToSageMakerEndpoint(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-apigateway-sagemakerendpoint.ApiGatewayToSageMakerEndpoint",
):
    '''
    :summary: The ApiGatewayToSageMakerEndpoint class.
    '''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        endpoint_name: builtins.str,
        request_mapping_template: builtins.str,
        resource_path: builtins.str,
        api_gateway_execution_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        api_gateway_props: typing.Optional[aws_cdk.aws_apigateway.RestApiProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        resource_name: typing.Optional[builtins.str] = None,
        response_mapping_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param endpoint_name: Name of the deployed SageMaker inference endpoint. Default: - None.
        :param request_mapping_template: Mapping template to convert GET requests received on the REST API to POST requests expected by the SageMaker endpoint. Default: - None.
        :param resource_path: Resource path for the GET method. The variable defined here can be referenced in ``requestMappingTemplate``. Default: - None.
        :param api_gateway_execution_role: Optional IAM role that is used by API Gateway to invoke the SageMaker endpoint. Default: - An IAM role with sagemaker:InvokeEndpoint access to ``endpointName`` is created.
        :param api_gateway_props: Optional user-provided props to override the default props for the API Gateway. Default: - Default properties are used.
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param resource_name: Optional resource name where the GET method will be available. Default: - None.
        :param response_mapping_template: Optional mapping template to convert responses received from the SageMaker endpoint. Default: - None.

        :access: public
        :since: 1.68.0
        :summary: Constructs a new instance of the ApiGatewayToSageMakerEndpoint class.
        '''
        props = ApiGatewayToSageMakerEndpointProps(
            endpoint_name=endpoint_name,
            request_mapping_template=request_mapping_template,
            resource_path=resource_path,
            api_gateway_execution_role=api_gateway_execution_role,
            api_gateway_props=api_gateway_props,
            log_group_props=log_group_props,
            resource_name=resource_name,
            response_mapping_template=response_mapping_template,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGateway")
    def api_gateway(self) -> aws_cdk.aws_apigateway.RestApi:
        return typing.cast(aws_cdk.aws_apigateway.RestApi, jsii.get(self, "apiGateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayLogGroup")
    def api_gateway_log_group(self) -> aws_cdk.aws_logs.LogGroup:
        return typing.cast(aws_cdk.aws_logs.LogGroup, jsii.get(self, "apiGatewayLogGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayRole")
    def api_gateway_role(self) -> aws_cdk.aws_iam.Role:
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "apiGatewayRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGatewayCloudWatchRole")
    def api_gateway_cloud_watch_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], jsii.get(self, "apiGatewayCloudWatchRole"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-apigateway-sagemakerendpoint.ApiGatewayToSageMakerEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "endpoint_name": "endpointName",
        "request_mapping_template": "requestMappingTemplate",
        "resource_path": "resourcePath",
        "api_gateway_execution_role": "apiGatewayExecutionRole",
        "api_gateway_props": "apiGatewayProps",
        "log_group_props": "logGroupProps",
        "resource_name": "resourceName",
        "response_mapping_template": "responseMappingTemplate",
    },
)
class ApiGatewayToSageMakerEndpointProps:
    def __init__(
        self,
        *,
        endpoint_name: builtins.str,
        request_mapping_template: builtins.str,
        resource_path: builtins.str,
        api_gateway_execution_role: typing.Optional[aws_cdk.aws_iam.Role] = None,
        api_gateway_props: typing.Optional[aws_cdk.aws_apigateway.RestApiProps] = None,
        log_group_props: typing.Optional[aws_cdk.aws_logs.LogGroupProps] = None,
        resource_name: typing.Optional[builtins.str] = None,
        response_mapping_template: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param endpoint_name: Name of the deployed SageMaker inference endpoint. Default: - None.
        :param request_mapping_template: Mapping template to convert GET requests received on the REST API to POST requests expected by the SageMaker endpoint. Default: - None.
        :param resource_path: Resource path for the GET method. The variable defined here can be referenced in ``requestMappingTemplate``. Default: - None.
        :param api_gateway_execution_role: Optional IAM role that is used by API Gateway to invoke the SageMaker endpoint. Default: - An IAM role with sagemaker:InvokeEndpoint access to ``endpointName`` is created.
        :param api_gateway_props: Optional user-provided props to override the default props for the API Gateway. Default: - Default properties are used.
        :param log_group_props: User provided props to override the default props for the CloudWatchLogs LogGroup. Default: - Default props are used
        :param resource_name: Optional resource name where the GET method will be available. Default: - None.
        :param response_mapping_template: Optional mapping template to convert responses received from the SageMaker endpoint. Default: - None.

        :summary: The properties for the ApiGatewayToSageMakerEndpointProps class.
        '''
        if isinstance(api_gateway_props, dict):
            api_gateway_props = aws_cdk.aws_apigateway.RestApiProps(**api_gateway_props)
        if isinstance(log_group_props, dict):
            log_group_props = aws_cdk.aws_logs.LogGroupProps(**log_group_props)
        self._values: typing.Dict[str, typing.Any] = {
            "endpoint_name": endpoint_name,
            "request_mapping_template": request_mapping_template,
            "resource_path": resource_path,
        }
        if api_gateway_execution_role is not None:
            self._values["api_gateway_execution_role"] = api_gateway_execution_role
        if api_gateway_props is not None:
            self._values["api_gateway_props"] = api_gateway_props
        if log_group_props is not None:
            self._values["log_group_props"] = log_group_props
        if resource_name is not None:
            self._values["resource_name"] = resource_name
        if response_mapping_template is not None:
            self._values["response_mapping_template"] = response_mapping_template

    @builtins.property
    def endpoint_name(self) -> builtins.str:
        '''Name of the deployed SageMaker inference endpoint.

        :default: - None.
        '''
        result = self._values.get("endpoint_name")
        assert result is not None, "Required property 'endpoint_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def request_mapping_template(self) -> builtins.str:
        '''Mapping template to convert GET requests received on the REST API to POST requests expected by the SageMaker endpoint.

        :default: - None.
        '''
        result = self._values.get("request_mapping_template")
        assert result is not None, "Required property 'request_mapping_template' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_path(self) -> builtins.str:
        '''Resource path for the GET method.

        The variable defined here can be referenced in ``requestMappingTemplate``.

        :default: - None.
        '''
        result = self._values.get("resource_path")
        assert result is not None, "Required property 'resource_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_gateway_execution_role(self) -> typing.Optional[aws_cdk.aws_iam.Role]:
        '''Optional IAM role that is used by API Gateway to invoke the SageMaker endpoint.

        :default: - An IAM role with sagemaker:InvokeEndpoint access to ``endpointName`` is created.
        '''
        result = self._values.get("api_gateway_execution_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.Role], result)

    @builtins.property
    def api_gateway_props(self) -> typing.Optional[aws_cdk.aws_apigateway.RestApiProps]:
        '''Optional user-provided props to override the default props for the API Gateway.

        :default: - Default properties are used.
        '''
        result = self._values.get("api_gateway_props")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.RestApiProps], result)

    @builtins.property
    def log_group_props(self) -> typing.Optional[aws_cdk.aws_logs.LogGroupProps]:
        '''User provided props to override the default props for the CloudWatchLogs LogGroup.

        :default: - Default props are used
        '''
        result = self._values.get("log_group_props")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.LogGroupProps], result)

    @builtins.property
    def resource_name(self) -> typing.Optional[builtins.str]:
        '''Optional resource name where the GET method will be available.

        :default: - None.
        '''
        result = self._values.get("resource_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_mapping_template(self) -> typing.Optional[builtins.str]:
        '''Optional mapping template to convert responses received from the SageMaker endpoint.

        :default: - None.
        '''
        result = self._values.get("response_mapping_template")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayToSageMakerEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayToSageMakerEndpoint",
    "ApiGatewayToSageMakerEndpointProps",
]

publication.publish()
