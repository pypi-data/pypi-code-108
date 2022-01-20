'''
# AWS Lambda Layer with AWS CLI

This module exports a single class called `AwsCliLayer` which is a `lambda.Layer` that bundles the AWS CLI.

Usage:

```python
# AwsCliLayer bundles the AWS CLI in a lambda layer
from monocdk.lambda_layer_awscli import AwsCliLayer

# fn: lambda.Function

fn.add_layers(AwsCliLayer(self, "AwsCliLayer"))
```

The CLI will be installed under `/opt/awscli/aws`.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from ..aws_lambda import LayerVersion as _LayerVersion_34d6006f


class AwsCliLayer(
    _LayerVersion_34d6006f,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.lambda_layer_awscli.AwsCliLayer",
):
    '''(experimental) An AWS Lambda layer that includes the AWS CLI.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # AwsCliLayer bundles the AWS CLI in a lambda layer
        from monocdk.lambda_layer_awscli import AwsCliLayer
        
        # fn: lambda.Function
        
        fn.add_layers(AwsCliLayer(self, "AwsCliLayer"))
    '''

    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id])


__all__ = [
    "AwsCliLayer",
]

publication.publish()
