'''
# cdk-wordpress

[![NPM version](https://badge.fury.io/js/cdk-wordpress.svg)](https://www.npmjs.com/package/cdk-wordpress)
[![PyPI version](https://badge.fury.io/py/cdk-wordpress.svg)](https://pypi.org/project/cdk-wordpress)
![Release](https://github.com/clarencetw/cdk-wordpress/workflows/Release/badge.svg)

![npm](https://img.shields.io/npm/dt/cdk-wordpress?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/cdk-wordpress?label=pypi&color=blue)

A CDK construct library to deploy WordPress

## How do use

Install your package manager:

```sh
yarn add cdk-wordpress
```

### TypeScript Sample

```python
import { WordPress } from "cdk-wordpress";

const wordpress = new WordPress(stack, "WordPressEcs");

// Get WordPress endpoint
new CfnOutput(stack, "Endpoint", { value: wordpress.endpoint });
```

### To deploy

```bash
cdk deploy
```

### To destroy

```bash
cdk destroy
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

import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_rds
import aws_cdk.core


class WordPress(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-wordpress.WordPress",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        cluster: typing.Optional[aws_cdk.aws_ecs.Cluster] = None,
        rds_instance: typing.Optional[aws_cdk.aws_rds.DatabaseInstance] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: The WordPress cluster.
        :param rds_instance: The WordPress RDS.
        :param vpc: The WordPress VPC.
        '''
        props = WordPressProps(cluster=cluster, rds_instance=rds_instance, vpc=vpc)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpoint"))


@jsii.data_type(
    jsii_type="cdk-wordpress.WordPressProps",
    jsii_struct_bases=[],
    name_mapping={"cluster": "cluster", "rds_instance": "rdsInstance", "vpc": "vpc"},
)
class WordPressProps:
    def __init__(
        self,
        *,
        cluster: typing.Optional[aws_cdk.aws_ecs.Cluster] = None,
        rds_instance: typing.Optional[aws_cdk.aws_rds.DatabaseInstance] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''The interface for all wordpress.

        :param cluster: The WordPress cluster.
        :param rds_instance: The WordPress RDS.
        :param vpc: The WordPress VPC.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cluster is not None:
            self._values["cluster"] = cluster
        if rds_instance is not None:
            self._values["rds_instance"] = rds_instance
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def cluster(self) -> typing.Optional[aws_cdk.aws_ecs.Cluster]:
        '''The WordPress cluster.'''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.Cluster], result)

    @builtins.property
    def rds_instance(self) -> typing.Optional[aws_cdk.aws_rds.DatabaseInstance]:
        '''The WordPress RDS.'''
        result = self._values.get("rds_instance")
        return typing.cast(typing.Optional[aws_cdk.aws_rds.DatabaseInstance], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''The WordPress VPC.'''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WordPressProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "WordPress",
    "WordPressProps",
]

publication.publish()
