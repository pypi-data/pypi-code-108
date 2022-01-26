'''
# AWS::IoTEvents Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

AWS IoT Events enables you to monitor your equipment or device fleets for
failures or changes in operation, and to trigger actions when such events
occur.

## Installation

Install the module:

```console
$ npm i @aws-cdk/aws-iotevents
```

Import it into your code:

```python
import aws_cdk.aws_iotevents_alpha as iotevents
```

## `Input`

Add an AWS IoT Events input to your stack:

```python
# Example automatically generated from non-compiling source. May contain errors.
import aws_cdk.aws_iotevents_alpha as iotevents

iotevents.Input(self, "MyInput",
    input_name="my_input",
    attribute_json_paths=["payload.temperature"]
)
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
import constructs


@jsii.interface(jsii_type="@aws-cdk/aws-iotevents-alpha.IInput")
class IInput(aws_cdk.IResource, typing_extensions.Protocol):
    '''(experimental) Represents an AWS IoT Events input.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> builtins.str:
        '''(experimental) The name of the input.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IInputProxy(
    jsii.proxy_for(aws_cdk.IResource) # type: ignore[misc]
):
    '''(experimental) Represents an AWS IoT Events input.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-iotevents-alpha.IInput"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> builtins.str:
        '''(experimental) The name of the input.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "inputName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IInput).__jsii_proxy_class__ = lambda : _IInputProxy


@jsii.implements(IInput)
class Input(
    aws_cdk.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-iotevents-alpha.Input",
):
    '''(experimental) Defines an AWS IoT Events input in this stack.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Example automatically generated from non-compiling source. May contain errors.
        import aws_cdk.aws_iotevents_alpha as iotevents
        
        iotevents.Input(self, "MyInput",
            input_name="my_input",
            attribute_json_paths=["payload.temperature"]
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        attribute_json_paths: typing.Sequence[builtins.str],
        input_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param attribute_json_paths: (experimental) An expression that specifies an attribute-value pair in a JSON structure. Use this to specify an attribute from the JSON payload that is made available by the input. Inputs are derived from messages sent to AWS IoT Events (BatchPutMessage). Each such message contains a JSON payload. The attribute (and its paired value) specified here are available for use in the condition expressions used by detectors.
        :param input_name: (experimental) The name of the input. Default: - CloudFormation will generate a unique name of the input

        :stability: experimental
        '''
        props = InputProps(
            attribute_json_paths=attribute_json_paths, input_name=input_name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromInputName") # type: ignore[misc]
    @builtins.classmethod
    def from_input_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        input_name: builtins.str,
    ) -> IInput:
        '''(experimental) Import an existing input.

        :param scope: -
        :param id: -
        :param input_name: -

        :stability: experimental
        '''
        return typing.cast(IInput, jsii.sinvoke(cls, "fromInputName", [scope, id, input_name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputName")
    def input_name(self) -> builtins.str:
        '''(experimental) The name of the input.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "inputName"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-iotevents-alpha.InputProps",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_json_paths": "attributeJsonPaths",
        "input_name": "inputName",
    },
)
class InputProps:
    def __init__(
        self,
        *,
        attribute_json_paths: typing.Sequence[builtins.str],
        input_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for defining an AWS IoT Events input.

        :param attribute_json_paths: (experimental) An expression that specifies an attribute-value pair in a JSON structure. Use this to specify an attribute from the JSON payload that is made available by the input. Inputs are derived from messages sent to AWS IoT Events (BatchPutMessage). Each such message contains a JSON payload. The attribute (and its paired value) specified here are available for use in the condition expressions used by detectors.
        :param input_name: (experimental) The name of the input. Default: - CloudFormation will generate a unique name of the input

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Example automatically generated from non-compiling source. May contain errors.
            import aws_cdk.aws_iotevents_alpha as iotevents
            
            iotevents.Input(self, "MyInput",
                input_name="my_input",
                attribute_json_paths=["payload.temperature"]
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "attribute_json_paths": attribute_json_paths,
        }
        if input_name is not None:
            self._values["input_name"] = input_name

    @builtins.property
    def attribute_json_paths(self) -> typing.List[builtins.str]:
        '''(experimental) An expression that specifies an attribute-value pair in a JSON structure.

        Use this to specify an attribute from the JSON payload that is made available
        by the input. Inputs are derived from messages sent to AWS IoT Events (BatchPutMessage).
        Each such message contains a JSON payload. The attribute (and its paired value)
        specified here are available for use in the condition expressions used by detectors.

        :stability: experimental
        '''
        result = self._values.get("attribute_json_paths")
        assert result is not None, "Required property 'attribute_json_paths' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def input_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the input.

        :default: - CloudFormation will generate a unique name of the input

        :stability: experimental
        '''
        result = self._values.get("input_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IInput",
    "Input",
    "InputProps",
]

publication.publish()
