'''
# AWS Lambda Layer with curl

[![NPM version](https://badge.fury.io/js/cdk-lambda-layer-curl.svg)](https://badge.fury.io/js/cdk-lambda-layer-curl)
[![PyPI version](https://badge.fury.io/py/cdk-lambda-layer-curl.svg)](https://badge.fury.io/py/cdk-lambda-layer-curl)
![Release](https://github.com/clarencetw/cdk-lambda-layer-curl/workflows/release/badge.svg)
[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/clarencetw/cdk-lambda-layer-curl)

Usage:

```python
// CurlLayer bundles the curl in a lambda layer
import { CurlLayer } from 'cdk-lambda-layer-curl';

declare const fn: lambda.Function;
fn.addLayers(new CurlLayer(this, 'CurlLayer'));
```

```python
import { CurlLayer } from 'cdk-lambda-layer-curl'
import * as lambda from 'aws-cdk-lib/aws-lambda'

new lambda.Function(this, 'MyLambda', {
  code: lambda.Code.fromAsset(path.join(__dirname, 'my-lambda-handler')),
  handler: 'index.main',
  runtime: lambda.Runtime.PYTHON_3_9,
  layers: [new CurlLayer(this, 'CurlLayer')]
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
import aws_cdk.core


class CurlLayer(
    aws_cdk.aws_lambda.LayerVersion,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-lambda-layer-curl.CurlLayer",
):
    '''An AWS Lambda layer that includes the curl.'''

    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(self.__class__, self, [scope, id])


__all__ = [
    "CurlLayer",
]

publication.publish()
