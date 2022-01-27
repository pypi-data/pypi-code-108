'''
# AWS Lambda Layer with wget

[![NPM version](https://badge.fury.io/js/cdk-lambda-layer-wget.svg)](https://badge.fury.io/js/cdk-lambda-layer-wget)
[![PyPI version](https://badge.fury.io/py/cdk-lambda-layer-wget.svg)](https://badge.fury.io/py/cdk-lambda-layer-wget)
![Release](https://github.com/clarencetw/cdk-lambda-layer-wget/workflows/release/badge.svg)
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/clarencetw/cdk-lambda-layer-wget)

Usage:

```python
// WgetLayer bundles the wget in a lambda layer
import { WgetLayer } from 'cdk-lambda-layer-wget';

declare const fn: lambda.Function;
fn.addLayers(new WgetLayer(this, 'WgetLayer'));
```

```python
import { WgetLayer } from 'cdk-lambda-layer-wget'
import * as lambda from 'aws-cdk-lib/aws-lambda'

new lambda.Function(this, 'MyLambda', {
  code: lambda.Code.fromAsset(path.join(__dirname, 'my-lambda-handler')),
  handler: 'index.main',
  runtime: lambda.Runtime.PYTHON_3_9,
  layers: [new WgetLayer(this, 'WgetLayer')]
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

import aws_cdk.aws_lambda
import constructs


class WgetLayer(
    aws_cdk.aws_lambda.LayerVersion,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-lambda-layer-wget.WgetLayer",
):
    '''An AWS Lambda layer that includes the wget.'''

    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(self.__class__, self, [scope, id])


__all__ = [
    "WgetLayer",
]

publication.publish()
