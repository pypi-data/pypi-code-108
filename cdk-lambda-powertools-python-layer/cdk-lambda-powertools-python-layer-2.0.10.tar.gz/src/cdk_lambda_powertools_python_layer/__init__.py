'''
# Lambda powertools python layer

## Why this project exists

This is a custom construct that will create AWS Lambda Layer with AWS Powertools for Python library. There are different
ways how to create a layer and when working with CDK you need to install the library, create a zip file and wire it
correctly. With this construct you don't have to care about packaging and dependency management, just create a construct
and add it to your function. The construct is an extension of the
existing [`LayerVersion`](https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-lambda.LayerVersion.html) construct
from the CDK library, so you have access to all fields and methods.

See the [API](API.md) for details.

```python
import { LambdaPowertoolsLayer } from 'cdk-lambda-powertools-python-layer';

const powertoolsLayer = new LambdaPowertoolsLayer(this, 'TestLayer');
```

Python

```python
from cdk_lambda_powertools_python_layer import LambdaPowertoolsLayer

powertoolsLayer = LambdaPowertoolsLayer(self, 'PowertoolsLayer')
```

The layer will be created during the CDK `synth` step and thus requires Docker.

## Install

TypeSript/JavaScript:

```shell
npm i cdk-lambda-powertools-python-layer
```

Python:

```shell
pip install cdk-lambda-powertools-python-layer
```

## Usage

### Python

A single line will create a layer with powertools for python:

```python
from cdk_lambda_powertools_python_layer import LambdaPowertoolsLayer

powertoolsLayer = LambdaPowertoolsLayer(self, 'PowertoolsLayer')
```

You can then add the layer to your funciton:

```python
from aws_cdk import aws_lambda

aws_lambda.Function(self, 'LambdaFunction',
                            code=aws_lambda.Code.from_asset('function'),
                            handler='app.handler',
                            runtime=aws_lambda.Runtime.PYTHON_3_9,
                            layers=[powertoolsLayer])
```

You can specify the powertools version by passing the optional `version` paramter, otherwise the construct will take the
latest version from pypi repository.

```python
LambdaPowertoolsLayer(self, 'PowertoolsLayer', version='1.24.0')
```

Additionally, powertools have extras depenedncies such as
Pydantic, [documented here](https://awslabs.github.io/aws-lambda-powertools-python/latest/#lambda-layer). This is not
included by default, and you have to set this option in the construct definition if you need it:

```python
LambdaPowertoolsLayer(self, 'PowertoolsLayer', include_extras=True)
```

Full example:

```python
from aws_cdk import Stack, aws_lambda
from cdk_lambda_powertools_python_layer import LambdaPowertoolsLayer
from constructs import Construct


class LayerTestStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        powertoolsLayer = LambdaPowertoolsLayer(
            self, 'PowertoolsLayer', include_extras=True, version='1.24.0')

        aws_lambda.Function(self, 'LambdaFunction',
                            code=aws_lambda.Code.from_asset('function'),
                            handler='app.handler',
                            runtime=aws_lambda.Runtime.PYTHON_3_9,
                            layers=[powertoolsLayer])

```

### TypeScript

Full example for TypeScript:

```python
import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { LambdaPowertoolsLayer } from 'cdk-lambda-powertools-python-layer';
import { Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';

export class CdkPowertoolsExampleStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const powertoolsLayer = new LambdaPowertoolsLayer(this, 'TestLayer', {
      version: '1.22.0',
      includeExtras: true
    });

    new Function(this, 'LambdaFunction', {
      code: Code.fromAsset(path.join('./function')),
      handler: 'app.handler',
      runtime: Runtime.PYTHON_3_9,
      layers: [powertoolsLayer],
    });
  }
}
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

import aws_cdk.aws_lambda
import constructs


class LambdaPowertoolsLayer(
    aws_cdk.aws_lambda.LayerVersion,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-lambda-powertools-python-layer.LambdaPowertoolsLayer",
):
    '''Defines a new Lambda Layer with Powertools for python library.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        include_extras: typing.Optional[builtins.bool] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param include_extras: A flag for the pydantic extras dependency, used for parsing. This will increase the size of the layer significantly. If you don't use parsing, ignore it.
        :param version: The powertools package version from pypi repository.
        '''
        props = PowertoolsLayerProps(include_extras=include_extras, version=version)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="constructBuildArgs") # type: ignore[misc]
    @builtins.classmethod
    def construct_build_args(
        cls,
        include_extras: typing.Optional[builtins.bool] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''creates build argument for the Dockerfile.

        There are multiple combinations between version and extras package that results in different suffix for the installation.
        With and without version, with and without extras flag.
        We construct one suffix here because it is easier to do in code than inside the Dockerfile with bash commands.
        For example, if we set extras=true and version=1.22.0 we get '[pydantic]==1.22.0'.

        :param include_extras: -
        :param version: -
        '''
        return typing.cast(builtins.str, jsii.sinvoke(cls, "constructBuildArgs", [include_extras, version]))


@jsii.data_type(
    jsii_type="cdk-lambda-powertools-python-layer.PowertoolsLayerProps",
    jsii_struct_bases=[],
    name_mapping={"include_extras": "includeExtras", "version": "version"},
)
class PowertoolsLayerProps:
    def __init__(
        self,
        *,
        include_extras: typing.Optional[builtins.bool] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for Powertools layer for python.

        :param include_extras: A flag for the pydantic extras dependency, used for parsing. This will increase the size of the layer significantly. If you don't use parsing, ignore it.
        :param version: The powertools package version from pypi repository.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if include_extras is not None:
            self._values["include_extras"] = include_extras
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def include_extras(self) -> typing.Optional[builtins.bool]:
        '''A flag for the pydantic extras dependency, used for parsing.

        This will increase the size of the layer significantly. If you don't use parsing, ignore it.
        '''
        result = self._values.get("include_extras")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''The powertools package version from pypi repository.'''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PowertoolsLayerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LambdaPowertoolsLayer",
    "PowertoolsLayerProps",
]

publication.publish()
