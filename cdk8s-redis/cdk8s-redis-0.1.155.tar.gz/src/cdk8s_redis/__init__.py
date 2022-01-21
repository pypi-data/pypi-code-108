'''
# cdk8s-redis

> Redis constructs for cdk8s

Basic implementation of a Redis construct for cdk8s. Contributions are welcome!

## Usage

The following will define a Redis cluster with a primary and 2 replicas:

```python
import { Redis } from 'cdk8s-redis';

// inside your chart:
const redis = new Redis(this, 'my-redis');
```

DNS names can be obtained from `redis.primaryHost` and `redis.replicaHost`.

You can specify how many replicas to define:

```python
new Redis(this, 'my-redis', {
  replicas: 4
});
```

Or, you can specify no replicas:

```python
new Redis(this, 'my-redis', {
  replicas: 0
});
```

## License

Distributed under the [Apache 2.0](./LICENSE) license.
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

import constructs


class Redis(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-redis.Redis",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        replicas: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param labels: (experimental) Extra labels to associate with resources. Default: - none
        :param replicas: (experimental) Number of replicas. Default: 2

        :stability: experimental
        '''
        options = RedisOptions(labels=labels, replicas=replicas)

        jsii.create(self.__class__, self, [scope, id, options])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="primaryHost")
    def primary_host(self) -> builtins.str:
        '''(experimental) The DNS host for the primary service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "primaryHost"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicaHost")
    def replica_host(self) -> builtins.str:
        '''(experimental) The DNS host for the replica service.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "replicaHost"))


@jsii.data_type(
    jsii_type="cdk8s-redis.RedisOptions",
    jsii_struct_bases=[],
    name_mapping={"labels": "labels", "replicas": "replicas"},
)
class RedisOptions:
    def __init__(
        self,
        *,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        replicas: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param labels: (experimental) Extra labels to associate with resources. Default: - none
        :param replicas: (experimental) Number of replicas. Default: 2

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if labels is not None:
            self._values["labels"] = labels
        if replicas is not None:
            self._values["replicas"] = replicas

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Extra labels to associate with resources.

        :default: - none

        :stability: experimental
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of replicas.

        :default: 2

        :stability: experimental
        '''
        result = self._values.get("replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedisOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Redis",
    "RedisOptions",
]

publication.publish()
