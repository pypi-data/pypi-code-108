'''
# CDK Triggers

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

## Overview

Allow specifying arbitrary handlers which execute as part of the deployment process and trigger them before/after resources or stacks.

## Usage

You can trigger the execution of arbitrary AWS Lambda functions before or after resources or groups of resources are provisioned using the Triggers API.

The library includes constructs that represent different triggers. The `BeforeCreate` and `AfterCreate` constructs can be used to trigger a handler before/after a set of resources have been created.

```python
new triggers.AfterCreate(this, 'InvokeAfter', {
  resources: [resource1, resource2, stack, ...],
  handler: myLambdaFunction,
});
```

Where `resources` is a list of **construct scopes** which determine when `handler` is invoked. Scopes can be either specific resources or composite constructs (in which case all the resources in the construct will be used as a group). The scope can also be a `Stack`, in which case the trigger will apply to all the resources within the stack (same as any composite construct). All scopes must roll up to the same stack.

Let's look at an example. Say we want to publish a notification to an SNS topic that says "hello, topic!" after the topic is created.

```python
// define a topic
const topic = new sns.Topic(this, 'MyTopic');

// define a lambda function which publishes a message to the topic
const publisher = new NodeJsFunction(this, 'PublishToTopic');
publisher.addEnvironment('TOPIC_ARN', topic.topicArn);
publisher.addEnvironment('MESSAGE', 'Hello, topic!');
topic.grantPublish(publisher);

// trigger the lambda function after the topic is created
new triggers.AfterCreate(this, 'SayHello', {
  scopes: [topic],
  handler: publisher
});
```

## Additional Notes

* If the trigger fails, deployment fails.
* If the handler changes (configuration or code), the trigger gets re-executed (trigger is bound to `lambda.currentVersion` which gets recreated
  when the function changes).

## Roadmap

* Additional periodic execution after deployment (`repeatOnSchedule`).
* Async checks (`retryWithTimeout`)
* Execute shell command inside a Docker image

## Use Cases

Here are some examples of use cases for triggers:

* **Intrinsic validations**: execute a check to verify that a resource or set of resources have been deployed correctly

  * Test connections to external systems (e.g. security tokens are valid)
  * Verify integration between resources is working as expected
  * Execute as one-off and also periodically after deployment
  * Wait for data to start flowing (e.g. wait for a metric) before deployment is successful
* **Data priming**: add data to resources after they are created

  * CodeCommit repo + initial commit
  * Database + test data for development
* Check prerequisites before depoyment

  * Account limits
  * Availability of external services
* Connect to other accounts

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.
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


class AfterCreate(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-triggers.AfterCreate",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        handler: aws_cdk.aws_lambda.Function,
        resources: typing.Optional[typing.Sequence[constructs.Construct]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param handler: The handler to execute once after all the resources are created. The trigger will be executed every time the handler changes (code or configuration).
        :param resources: Resources to trigger on. Resources can come from any stack in the app. Default: [] Run the trigger at any time during stack deployment.
        '''
        props = AfterCreateProps(handler=handler, resources=resources)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-triggers.AfterCreateProps",
    jsii_struct_bases=[],
    name_mapping={"handler": "handler", "resources": "resources"},
)
class AfterCreateProps:
    def __init__(
        self,
        *,
        handler: aws_cdk.aws_lambda.Function,
        resources: typing.Optional[typing.Sequence[constructs.Construct]] = None,
    ) -> None:
        '''
        :param handler: The handler to execute once after all the resources are created. The trigger will be executed every time the handler changes (code or configuration).
        :param resources: Resources to trigger on. Resources can come from any stack in the app. Default: [] Run the trigger at any time during stack deployment.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "handler": handler,
        }
        if resources is not None:
            self._values["resources"] = resources

    @builtins.property
    def handler(self) -> aws_cdk.aws_lambda.Function:
        '''The handler to execute once after all the resources are created.

        The trigger will be executed every time the handler changes (code or
        configuration).
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(aws_cdk.aws_lambda.Function, result)

    @builtins.property
    def resources(self) -> typing.Optional[typing.List[constructs.Construct]]:
        '''Resources to trigger on.

        Resources can come from any stack in the app.

        :default: [] Run the trigger at any time during stack deployment.
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.List[constructs.Construct]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AfterCreateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AfterCreate",
    "AfterCreateProps",
]

publication.publish()
