'''
# Terraform CDK random Provider ~> 3.1

This repo builds and publishes the Terraform random Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-random](https://www.npmjs.com/package/@cdktf/provider-random).

`npm install @cdktf/provider-random`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-random](https://pypi.org/project/cdktf-cdktf-provider-random).

`pipenv install cdktf-cdktf-provider-random`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Random](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Random).

`dotnet add package HashiCorp.Cdktf.Providers.Random`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-random](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-random).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-random</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform random Provider version 1:1. In fact, it always tracks `latest` of `~> 3.1` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform random Provider](https://github.com/terraform-providers/terraform-provider-random)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform random Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/hashicorp/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [Repository Manager](https://github.com/hashicorp/cdktf-repository-manager/)
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

import cdktf
import constructs


class Id(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-random.Id",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/random/r/id random_id}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        byte_length: jsii.Number,
        keepers: typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]] = None,
        prefix: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/random/r/id random_id} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param byte_length: The number of random bytes to produce. The minimum value is 1, which produces eight bits of randomness. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/id#byte_length Id#byte_length}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/id#keepers Id#keepers}
        :param prefix: Arbitrary string to prefix the output value with. This string is supplied as-is, meaning it is not guaranteed to be URL-safe or base64 encoded. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/id#prefix Id#prefix}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IdConfig(
            byte_length=byte_length,
            keepers=keepers,
            prefix=prefix,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKeepers")
    def reset_keepers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepers", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="b64Std")
    def b64_std(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "b64Std"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="b64Url")
    def b64_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "b64Url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dec")
    def dec(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dec"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hex")
    def hex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hex"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="byteLengthInput")
    def byte_length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "byteLengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepersInput")
    def keepers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "keepersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="byteLength")
    def byte_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "byteLength"))

    @byte_length.setter
    def byte_length(self, value: jsii.Number) -> None:
        jsii.set(self, "byteLength", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepers")
    def keepers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "keepers"))

    @keepers.setter
    def keepers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "keepers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-random.IdConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "byte_length": "byteLength",
        "keepers": "keepers",
        "prefix": "prefix",
    },
)
class IdConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        byte_length: jsii.Number,
        keepers: typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]] = None,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param byte_length: The number of random bytes to produce. The minimum value is 1, which produces eight bits of randomness. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/id#byte_length Id#byte_length}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/id#keepers Id#keepers}
        :param prefix: Arbitrary string to prefix the output value with. This string is supplied as-is, meaning it is not guaranteed to be URL-safe or base64 encoded. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/id#prefix Id#prefix}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "byte_length": byte_length,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if keepers is not None:
            self._values["keepers"] = keepers
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def byte_length(self) -> jsii.Number:
        '''The number of random bytes to produce. The minimum value is 1, which produces eight bits of randomness.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/id#byte_length Id#byte_length}
        '''
        result = self._values.get("byte_length")
        assert result is not None, "Required property 'byte_length' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def keepers(
        self,
    ) -> typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]]:
        '''Arbitrary map of values that, when changed, will trigger recreation of resource.

        See `the main provider documentation <../index.html>`_ for more information.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/id#keepers Id#keepers}
        '''
        result = self._values.get("keepers")
        return typing.cast(typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Arbitrary string to prefix the output value with.

        This string is supplied as-is, meaning it is not guaranteed to be URL-safe or base64 encoded.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/id#prefix Id#prefix}
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Integer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-random.Integer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/random/r/integer random_integer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        max: jsii.Number,
        min: jsii.Number,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        seed: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/random/r/integer random_integer} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param max: The maximum inclusive value of the range. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#max Integer#max}
        :param min: The minimum inclusive value of the range. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#min Integer#min}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#keepers Integer#keepers}
        :param seed: A custom seed to always produce the same value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#seed Integer#seed}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = IntegerConfig(
            max=max,
            min=min,
            keepers=keepers,
            seed=seed,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKeepers")
    def reset_keepers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepers", []))

    @jsii.member(jsii_name="resetSeed")
    def reset_seed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeed", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="result")
    def result(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "result"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepersInput")
    def keepers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "keepersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxInput")
    def max_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minInput")
    def min_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="seedInput")
    def seed_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "seedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepers")
    def keepers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "keepers"))

    @keepers.setter
    def keepers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "keepers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="max")
    def max(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "max"))

    @max.setter
    def max(self, value: jsii.Number) -> None:
        jsii.set(self, "max", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="min")
    def min(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "min"))

    @min.setter
    def min(self, value: jsii.Number) -> None:
        jsii.set(self, "min", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="seed")
    def seed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "seed"))

    @seed.setter
    def seed(self, value: builtins.str) -> None:
        jsii.set(self, "seed", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-random.IntegerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "max": "max",
        "min": "min",
        "keepers": "keepers",
        "seed": "seed",
    },
)
class IntegerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        max: jsii.Number,
        min: jsii.Number,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        seed: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param max: The maximum inclusive value of the range. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#max Integer#max}
        :param min: The minimum inclusive value of the range. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#min Integer#min}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#keepers Integer#keepers}
        :param seed: A custom seed to always produce the same value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#seed Integer#seed}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "max": max,
            "min": min,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if keepers is not None:
            self._values["keepers"] = keepers
        if seed is not None:
            self._values["seed"] = seed

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def max(self) -> jsii.Number:
        '''The maximum inclusive value of the range.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#max Integer#max}
        '''
        result = self._values.get("max")
        assert result is not None, "Required property 'max' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min(self) -> jsii.Number:
        '''The minimum inclusive value of the range.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#min Integer#min}
        '''
        result = self._values.get("min")
        assert result is not None, "Required property 'min' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def keepers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Arbitrary map of values that, when changed, will trigger recreation of resource.

        See `the main provider documentation <../index.html>`_ for more information.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#keepers Integer#keepers}
        '''
        result = self._values.get("keepers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def seed(self) -> typing.Optional[builtins.str]:
        '''A custom seed to always produce the same value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/integer#seed Integer#seed}
        '''
        result = self._values.get("seed")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IntegerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Password(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-random.Password",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/random/r/password random_password}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        length: jsii.Number,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        lower: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        min_lower: typing.Optional[jsii.Number] = None,
        min_numeric: typing.Optional[jsii.Number] = None,
        min_special: typing.Optional[jsii.Number] = None,
        min_upper: typing.Optional[jsii.Number] = None,
        number: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        override_special: typing.Optional[builtins.str] = None,
        special: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        upper: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/random/r/password random_password} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param length: The length of the string desired. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#length Password#length}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#keepers Password#keepers}
        :param lower: Include lowercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#lower Password#lower}
        :param min_lower: Minimum number of lowercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_lower Password#min_lower}
        :param min_numeric: Minimum number of numeric characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_numeric Password#min_numeric}
        :param min_special: Minimum number of special characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_special Password#min_special}
        :param min_upper: Minimum number of uppercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_upper Password#min_upper}
        :param number: Include numeric characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#number Password#number}
        :param override_special: Supply your own list of special characters to use for string generation. This overrides the default character list in the special argument. The ``special`` argument must still be set to true for any overwritten characters to be used in generation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#override_special Password#override_special}
        :param special: Include special characters in the result. These are ``!@#$%&*()-_=+[]{}<>:?``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#special Password#special}
        :param upper: Include uppercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#upper Password#upper}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PasswordConfig(
            length=length,
            keepers=keepers,
            lower=lower,
            min_lower=min_lower,
            min_numeric=min_numeric,
            min_special=min_special,
            min_upper=min_upper,
            number=number,
            override_special=override_special,
            special=special,
            upper=upper,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKeepers")
    def reset_keepers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepers", []))

    @jsii.member(jsii_name="resetLower")
    def reset_lower(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLower", []))

    @jsii.member(jsii_name="resetMinLower")
    def reset_min_lower(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinLower", []))

    @jsii.member(jsii_name="resetMinNumeric")
    def reset_min_numeric(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinNumeric", []))

    @jsii.member(jsii_name="resetMinSpecial")
    def reset_min_special(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinSpecial", []))

    @jsii.member(jsii_name="resetMinUpper")
    def reset_min_upper(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinUpper", []))

    @jsii.member(jsii_name="resetNumber")
    def reset_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumber", []))

    @jsii.member(jsii_name="resetOverrideSpecial")
    def reset_override_special(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideSpecial", []))

    @jsii.member(jsii_name="resetSpecial")
    def reset_special(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpecial", []))

    @jsii.member(jsii_name="resetUpper")
    def reset_upper(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpper", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="result")
    def result(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "result"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepersInput")
    def keepers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "keepersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lengthInput")
    def length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lowerInput")
    def lower_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "lowerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minLowerInput")
    def min_lower_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minLowerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minNumericInput")
    def min_numeric_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minNumericInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minSpecialInput")
    def min_special_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minSpecialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minUpperInput")
    def min_upper_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minUpperInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberInput")
    def number_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "numberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideSpecialInput")
    def override_special_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "overrideSpecialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="specialInput")
    def special_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "specialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="upperInput")
    def upper_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "upperInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepers")
    def keepers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "keepers"))

    @keepers.setter
    def keepers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "keepers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="length")
    def length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "length"))

    @length.setter
    def length(self, value: jsii.Number) -> None:
        jsii.set(self, "length", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lower")
    def lower(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "lower"))

    @lower.setter
    def lower(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "lower", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minLower")
    def min_lower(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minLower"))

    @min_lower.setter
    def min_lower(self, value: jsii.Number) -> None:
        jsii.set(self, "minLower", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minNumeric")
    def min_numeric(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minNumeric"))

    @min_numeric.setter
    def min_numeric(self, value: jsii.Number) -> None:
        jsii.set(self, "minNumeric", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minSpecial")
    def min_special(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minSpecial"))

    @min_special.setter
    def min_special(self, value: jsii.Number) -> None:
        jsii.set(self, "minSpecial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minUpper")
    def min_upper(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minUpper"))

    @min_upper.setter
    def min_upper(self, value: jsii.Number) -> None:
        jsii.set(self, "minUpper", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="number")
    def number(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "number"))

    @number.setter
    def number(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "number", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideSpecial")
    def override_special(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overrideSpecial"))

    @override_special.setter
    def override_special(self, value: builtins.str) -> None:
        jsii.set(self, "overrideSpecial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="special")
    def special(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "special"))

    @special.setter
    def special(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "special", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="upper")
    def upper(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "upper"))

    @upper.setter
    def upper(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "upper", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-random.PasswordConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "length": "length",
        "keepers": "keepers",
        "lower": "lower",
        "min_lower": "minLower",
        "min_numeric": "minNumeric",
        "min_special": "minSpecial",
        "min_upper": "minUpper",
        "number": "number",
        "override_special": "overrideSpecial",
        "special": "special",
        "upper": "upper",
    },
)
class PasswordConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        length: jsii.Number,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        lower: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        min_lower: typing.Optional[jsii.Number] = None,
        min_numeric: typing.Optional[jsii.Number] = None,
        min_special: typing.Optional[jsii.Number] = None,
        min_upper: typing.Optional[jsii.Number] = None,
        number: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        override_special: typing.Optional[builtins.str] = None,
        special: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        upper: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param length: The length of the string desired. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#length Password#length}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#keepers Password#keepers}
        :param lower: Include lowercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#lower Password#lower}
        :param min_lower: Minimum number of lowercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_lower Password#min_lower}
        :param min_numeric: Minimum number of numeric characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_numeric Password#min_numeric}
        :param min_special: Minimum number of special characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_special Password#min_special}
        :param min_upper: Minimum number of uppercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_upper Password#min_upper}
        :param number: Include numeric characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#number Password#number}
        :param override_special: Supply your own list of special characters to use for string generation. This overrides the default character list in the special argument. The ``special`` argument must still be set to true for any overwritten characters to be used in generation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#override_special Password#override_special}
        :param special: Include special characters in the result. These are ``!@#$%&*()-_=+[]{}<>:?``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#special Password#special}
        :param upper: Include uppercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#upper Password#upper}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "length": length,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if keepers is not None:
            self._values["keepers"] = keepers
        if lower is not None:
            self._values["lower"] = lower
        if min_lower is not None:
            self._values["min_lower"] = min_lower
        if min_numeric is not None:
            self._values["min_numeric"] = min_numeric
        if min_special is not None:
            self._values["min_special"] = min_special
        if min_upper is not None:
            self._values["min_upper"] = min_upper
        if number is not None:
            self._values["number"] = number
        if override_special is not None:
            self._values["override_special"] = override_special
        if special is not None:
            self._values["special"] = special
        if upper is not None:
            self._values["upper"] = upper

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def length(self) -> jsii.Number:
        '''The length of the string desired.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#length Password#length}
        '''
        result = self._values.get("length")
        assert result is not None, "Required property 'length' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def keepers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Arbitrary map of values that, when changed, will trigger recreation of resource.

        See `the main provider documentation <../index.html>`_ for more information.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#keepers Password#keepers}
        '''
        result = self._values.get("keepers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def lower(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Include lowercase alphabet characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#lower Password#lower}
        '''
        result = self._values.get("lower")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def min_lower(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of lowercase alphabet characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_lower Password#min_lower}
        '''
        result = self._values.get("min_lower")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_numeric(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of numeric characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_numeric Password#min_numeric}
        '''
        result = self._values.get("min_numeric")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_special(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of special characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_special Password#min_special}
        '''
        result = self._values.get("min_special")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_upper(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of uppercase alphabet characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#min_upper Password#min_upper}
        '''
        result = self._values.get("min_upper")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Include numeric characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#number Password#number}
        '''
        result = self._values.get("number")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def override_special(self) -> typing.Optional[builtins.str]:
        '''Supply your own list of special characters to use for string generation.

        This overrides the default character list in the special argument.  The ``special`` argument must still be set to true for any overwritten characters to be used in generation.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#override_special Password#override_special}
        '''
        result = self._values.get("override_special")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def special(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Include special characters in the result. These are ``!@#$%&*()-_=+[]{}<>:?``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#special Password#special}
        '''
        result = self._values.get("special")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def upper(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Include uppercase alphabet characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/password#upper Password#upper}
        '''
        result = self._values.get("upper")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PasswordConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Pet(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-random.Pet",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/random/r/pet random_pet}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        length: typing.Optional[jsii.Number] = None,
        prefix: typing.Optional[builtins.str] = None,
        separator: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/random/r/pet random_pet} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#keepers Pet#keepers}
        :param length: The length (in words) of the pet name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#length Pet#length}
        :param prefix: A string to prefix the name with. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#prefix Pet#prefix}
        :param separator: The character to separate words in the pet name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#separator Pet#separator}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PetConfig(
            keepers=keepers,
            length=length,
            prefix=prefix,
            separator=separator,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKeepers")
    def reset_keepers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepers", []))

    @jsii.member(jsii_name="resetLength")
    def reset_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLength", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetSeparator")
    def reset_separator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeparator", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepersInput")
    def keepers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "keepersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lengthInput")
    def length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="separatorInput")
    def separator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "separatorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepers")
    def keepers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "keepers"))

    @keepers.setter
    def keepers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "keepers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="length")
    def length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "length"))

    @length.setter
    def length(self, value: jsii.Number) -> None:
        jsii.set(self, "length", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        jsii.set(self, "prefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        jsii.set(self, "separator", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-random.PetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "keepers": "keepers",
        "length": "length",
        "prefix": "prefix",
        "separator": "separator",
    },
)
class PetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        length: typing.Optional[jsii.Number] = None,
        prefix: typing.Optional[builtins.str] = None,
        separator: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#keepers Pet#keepers}
        :param length: The length (in words) of the pet name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#length Pet#length}
        :param prefix: A string to prefix the name with. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#prefix Pet#prefix}
        :param separator: The character to separate words in the pet name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#separator Pet#separator}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if keepers is not None:
            self._values["keepers"] = keepers
        if length is not None:
            self._values["length"] = length
        if prefix is not None:
            self._values["prefix"] = prefix
        if separator is not None:
            self._values["separator"] = separator

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def keepers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Arbitrary map of values that, when changed, will trigger recreation of resource.

        See `the main provider documentation <../index.html>`_ for more information.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#keepers Pet#keepers}
        '''
        result = self._values.get("keepers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def length(self) -> typing.Optional[jsii.Number]:
        '''The length (in words) of the pet name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#length Pet#length}
        '''
        result = self._values.get("length")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''A string to prefix the name with.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#prefix Pet#prefix}
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def separator(self) -> typing.Optional[builtins.str]:
        '''The character to separate words in the pet name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/pet#separator Pet#separator}
        '''
        result = self._values.get("separator")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RandomProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-random.RandomProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/random random}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/random random} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random#alias RandomProvider#alias}
        '''
        config = RandomProviderConfig(alias=alias)

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-random.RandomProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias"},
)
class RandomProviderConfig:
    def __init__(self, *, alias: typing.Optional[builtins.str] = None) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random#alias RandomProvider#alias}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random#alias RandomProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RandomProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Shuffle(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-random.Shuffle",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/random/r/shuffle random_shuffle}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        input: typing.Sequence[builtins.str],
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        result_count: typing.Optional[jsii.Number] = None,
        seed: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/random/r/shuffle random_shuffle} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param input: The list of strings to shuffle. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#input Shuffle#input}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#keepers Shuffle#keepers}
        :param result_count: The number of results to return. Defaults to the number of items in the ``input`` list. If fewer items are requested, some elements will be excluded from the result. If more items are requested, items will be repeated in the result but not more frequently than the number of items in the input list. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#result_count Shuffle#result_count}
        :param seed: Arbitrary string with which to seed the random number generator, in order to produce less-volatile permutations of the list. *Important:** Even with an identical seed, it is not guaranteed that the same permutation will be produced across different versions of Terraform. This argument causes the result to be *less volatile*, but not fixed for all time. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#seed Shuffle#seed}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ShuffleConfig(
            input=input,
            keepers=keepers,
            result_count=result_count,
            seed=seed,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKeepers")
    def reset_keepers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepers", []))

    @jsii.member(jsii_name="resetResultCount")
    def reset_result_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResultCount", []))

    @jsii.member(jsii_name="resetSeed")
    def reset_seed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeed", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="result")
    def result(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "result"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputInput")
    def input_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "inputInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepersInput")
    def keepers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "keepersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resultCountInput")
    def result_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "resultCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="seedInput")
    def seed_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "seedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="input")
    def input(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "input"))

    @input.setter
    def input(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "input", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepers")
    def keepers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "keepers"))

    @keepers.setter
    def keepers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "keepers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resultCount")
    def result_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "resultCount"))

    @result_count.setter
    def result_count(self, value: jsii.Number) -> None:
        jsii.set(self, "resultCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="seed")
    def seed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "seed"))

    @seed.setter
    def seed(self, value: builtins.str) -> None:
        jsii.set(self, "seed", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-random.ShuffleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "input": "input",
        "keepers": "keepers",
        "result_count": "resultCount",
        "seed": "seed",
    },
)
class ShuffleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        input: typing.Sequence[builtins.str],
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        result_count: typing.Optional[jsii.Number] = None,
        seed: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param input: The list of strings to shuffle. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#input Shuffle#input}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#keepers Shuffle#keepers}
        :param result_count: The number of results to return. Defaults to the number of items in the ``input`` list. If fewer items are requested, some elements will be excluded from the result. If more items are requested, items will be repeated in the result but not more frequently than the number of items in the input list. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#result_count Shuffle#result_count}
        :param seed: Arbitrary string with which to seed the random number generator, in order to produce less-volatile permutations of the list. *Important:** Even with an identical seed, it is not guaranteed that the same permutation will be produced across different versions of Terraform. This argument causes the result to be *less volatile*, but not fixed for all time. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#seed Shuffle#seed}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "input": input,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if keepers is not None:
            self._values["keepers"] = keepers
        if result_count is not None:
            self._values["result_count"] = result_count
        if seed is not None:
            self._values["seed"] = seed

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def input(self) -> typing.List[builtins.str]:
        '''The list of strings to shuffle.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#input Shuffle#input}
        '''
        result = self._values.get("input")
        assert result is not None, "Required property 'input' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def keepers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Arbitrary map of values that, when changed, will trigger recreation of resource.

        See `the main provider documentation <../index.html>`_ for more information.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#keepers Shuffle#keepers}
        '''
        result = self._values.get("keepers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def result_count(self) -> typing.Optional[jsii.Number]:
        '''The number of results to return.

        Defaults to the number of items in the ``input`` list. If fewer items are requested, some elements will be excluded from the result. If more items are requested, items will be repeated in the result but not more frequently than the number of items in the input list.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#result_count Shuffle#result_count}
        '''
        result = self._values.get("result_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def seed(self) -> typing.Optional[builtins.str]:
        '''Arbitrary string with which to seed the random number generator, in order to produce less-volatile permutations of the list.

        *Important:** Even with an identical seed, it is not guaranteed that the same permutation will be produced across different versions of Terraform. This argument causes the result to be *less volatile*, but not fixed for all time.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/shuffle#seed Shuffle#seed}
        '''
        result = self._values.get("seed")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ShuffleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StringResource(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-random.StringResource",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/random/r/string random_string}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        length: jsii.Number,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        lower: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        min_lower: typing.Optional[jsii.Number] = None,
        min_numeric: typing.Optional[jsii.Number] = None,
        min_special: typing.Optional[jsii.Number] = None,
        min_upper: typing.Optional[jsii.Number] = None,
        number: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        override_special: typing.Optional[builtins.str] = None,
        special: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        upper: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/random/r/string random_string} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param length: The length of the string desired. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#length StringResource#length}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#keepers StringResource#keepers}
        :param lower: Include lowercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#lower StringResource#lower}
        :param min_lower: Minimum number of lowercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_lower StringResource#min_lower}
        :param min_numeric: Minimum number of numeric characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_numeric StringResource#min_numeric}
        :param min_special: Minimum number of special characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_special StringResource#min_special}
        :param min_upper: Minimum number of uppercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_upper StringResource#min_upper}
        :param number: Include numeric characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#number StringResource#number}
        :param override_special: Supply your own list of special characters to use for string generation. This overrides the default character list in the special argument. The ``special`` argument must still be set to true for any overwritten characters to be used in generation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#override_special StringResource#override_special}
        :param special: Include special characters in the result. These are ``!@#$%&*()-_=+[]{}<>:?``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#special StringResource#special}
        :param upper: Include uppercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#upper StringResource#upper}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = StringResourceConfig(
            length=length,
            keepers=keepers,
            lower=lower,
            min_lower=min_lower,
            min_numeric=min_numeric,
            min_special=min_special,
            min_upper=min_upper,
            number=number,
            override_special=override_special,
            special=special,
            upper=upper,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKeepers")
    def reset_keepers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepers", []))

    @jsii.member(jsii_name="resetLower")
    def reset_lower(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLower", []))

    @jsii.member(jsii_name="resetMinLower")
    def reset_min_lower(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinLower", []))

    @jsii.member(jsii_name="resetMinNumeric")
    def reset_min_numeric(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinNumeric", []))

    @jsii.member(jsii_name="resetMinSpecial")
    def reset_min_special(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinSpecial", []))

    @jsii.member(jsii_name="resetMinUpper")
    def reset_min_upper(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinUpper", []))

    @jsii.member(jsii_name="resetNumber")
    def reset_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumber", []))

    @jsii.member(jsii_name="resetOverrideSpecial")
    def reset_override_special(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideSpecial", []))

    @jsii.member(jsii_name="resetSpecial")
    def reset_special(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpecial", []))

    @jsii.member(jsii_name="resetUpper")
    def reset_upper(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpper", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="result")
    def result(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "result"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepersInput")
    def keepers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "keepersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lengthInput")
    def length_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lengthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lowerInput")
    def lower_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "lowerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minLowerInput")
    def min_lower_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minLowerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minNumericInput")
    def min_numeric_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minNumericInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minSpecialInput")
    def min_special_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minSpecialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minUpperInput")
    def min_upper_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minUpperInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numberInput")
    def number_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "numberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideSpecialInput")
    def override_special_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "overrideSpecialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="specialInput")
    def special_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "specialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="upperInput")
    def upper_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "upperInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepers")
    def keepers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "keepers"))

    @keepers.setter
    def keepers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "keepers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="length")
    def length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "length"))

    @length.setter
    def length(self, value: jsii.Number) -> None:
        jsii.set(self, "length", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lower")
    def lower(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "lower"))

    @lower.setter
    def lower(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "lower", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minLower")
    def min_lower(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minLower"))

    @min_lower.setter
    def min_lower(self, value: jsii.Number) -> None:
        jsii.set(self, "minLower", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minNumeric")
    def min_numeric(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minNumeric"))

    @min_numeric.setter
    def min_numeric(self, value: jsii.Number) -> None:
        jsii.set(self, "minNumeric", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minSpecial")
    def min_special(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minSpecial"))

    @min_special.setter
    def min_special(self, value: jsii.Number) -> None:
        jsii.set(self, "minSpecial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minUpper")
    def min_upper(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minUpper"))

    @min_upper.setter
    def min_upper(self, value: jsii.Number) -> None:
        jsii.set(self, "minUpper", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="number")
    def number(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "number"))

    @number.setter
    def number(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "number", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="overrideSpecial")
    def override_special(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "overrideSpecial"))

    @override_special.setter
    def override_special(self, value: builtins.str) -> None:
        jsii.set(self, "overrideSpecial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="special")
    def special(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "special"))

    @special.setter
    def special(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "special", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="upper")
    def upper(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "upper"))

    @upper.setter
    def upper(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "upper", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-random.StringResourceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "length": "length",
        "keepers": "keepers",
        "lower": "lower",
        "min_lower": "minLower",
        "min_numeric": "minNumeric",
        "min_special": "minSpecial",
        "min_upper": "minUpper",
        "number": "number",
        "override_special": "overrideSpecial",
        "special": "special",
        "upper": "upper",
    },
)
class StringResourceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        length: jsii.Number,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        lower: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        min_lower: typing.Optional[jsii.Number] = None,
        min_numeric: typing.Optional[jsii.Number] = None,
        min_special: typing.Optional[jsii.Number] = None,
        min_upper: typing.Optional[jsii.Number] = None,
        number: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        override_special: typing.Optional[builtins.str] = None,
        special: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        upper: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param length: The length of the string desired. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#length StringResource#length}
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#keepers StringResource#keepers}
        :param lower: Include lowercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#lower StringResource#lower}
        :param min_lower: Minimum number of lowercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_lower StringResource#min_lower}
        :param min_numeric: Minimum number of numeric characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_numeric StringResource#min_numeric}
        :param min_special: Minimum number of special characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_special StringResource#min_special}
        :param min_upper: Minimum number of uppercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_upper StringResource#min_upper}
        :param number: Include numeric characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#number StringResource#number}
        :param override_special: Supply your own list of special characters to use for string generation. This overrides the default character list in the special argument. The ``special`` argument must still be set to true for any overwritten characters to be used in generation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#override_special StringResource#override_special}
        :param special: Include special characters in the result. These are ``!@#$%&*()-_=+[]{}<>:?``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#special StringResource#special}
        :param upper: Include uppercase alphabet characters in the result. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#upper StringResource#upper}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "length": length,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if keepers is not None:
            self._values["keepers"] = keepers
        if lower is not None:
            self._values["lower"] = lower
        if min_lower is not None:
            self._values["min_lower"] = min_lower
        if min_numeric is not None:
            self._values["min_numeric"] = min_numeric
        if min_special is not None:
            self._values["min_special"] = min_special
        if min_upper is not None:
            self._values["min_upper"] = min_upper
        if number is not None:
            self._values["number"] = number
        if override_special is not None:
            self._values["override_special"] = override_special
        if special is not None:
            self._values["special"] = special
        if upper is not None:
            self._values["upper"] = upper

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def length(self) -> jsii.Number:
        '''The length of the string desired.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#length StringResource#length}
        '''
        result = self._values.get("length")
        assert result is not None, "Required property 'length' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def keepers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Arbitrary map of values that, when changed, will trigger recreation of resource.

        See `the main provider documentation <../index.html>`_ for more information.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#keepers StringResource#keepers}
        '''
        result = self._values.get("keepers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def lower(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Include lowercase alphabet characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#lower StringResource#lower}
        '''
        result = self._values.get("lower")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def min_lower(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of lowercase alphabet characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_lower StringResource#min_lower}
        '''
        result = self._values.get("min_lower")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_numeric(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of numeric characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_numeric StringResource#min_numeric}
        '''
        result = self._values.get("min_numeric")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_special(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of special characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_special StringResource#min_special}
        '''
        result = self._values.get("min_special")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_upper(self) -> typing.Optional[jsii.Number]:
        '''Minimum number of uppercase alphabet characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#min_upper StringResource#min_upper}
        '''
        result = self._values.get("min_upper")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def number(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Include numeric characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#number StringResource#number}
        '''
        result = self._values.get("number")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def override_special(self) -> typing.Optional[builtins.str]:
        '''Supply your own list of special characters to use for string generation.

        This overrides the default character list in the special argument.  The ``special`` argument must still be set to true for any overwritten characters to be used in generation.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#override_special StringResource#override_special}
        '''
        result = self._values.get("override_special")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def special(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Include special characters in the result. These are ``!@#$%&*()-_=+[]{}<>:?``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#special StringResource#special}
        '''
        result = self._values.get("special")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def upper(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Include uppercase alphabet characters in the result.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/string#upper StringResource#upper}
        '''
        result = self._values.get("upper")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StringResourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Uuid(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-random.Uuid",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/random/r/uuid random_uuid}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/random/r/uuid random_uuid} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/uuid#keepers Uuid#keepers}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = UuidConfig(
            keepers=keepers,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetKeepers")
    def reset_keepers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="result")
    def result(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "result"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepersInput")
    def keepers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "keepersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepers")
    def keepers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "keepers"))

    @keepers.setter
    def keepers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "keepers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-random.UuidConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "keepers": "keepers",
    },
)
class UuidConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        keepers: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param keepers: Arbitrary map of values that, when changed, will trigger recreation of resource. See `the main provider documentation <../index.html>`_ for more information. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/uuid#keepers Uuid#keepers}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if keepers is not None:
            self._values["keepers"] = keepers

    @builtins.property
    def count(self) -> typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def keepers(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Arbitrary map of values that, when changed, will trigger recreation of resource.

        See `the main provider documentation <../index.html>`_ for more information.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/random/r/uuid#keepers Uuid#keepers}
        '''
        result = self._values.get("keepers")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UuidConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Id",
    "IdConfig",
    "Integer",
    "IntegerConfig",
    "Password",
    "PasswordConfig",
    "Pet",
    "PetConfig",
    "RandomProvider",
    "RandomProviderConfig",
    "Shuffle",
    "ShuffleConfig",
    "StringResource",
    "StringResourceConfig",
    "Uuid",
    "UuidConfig",
]

publication.publish()
