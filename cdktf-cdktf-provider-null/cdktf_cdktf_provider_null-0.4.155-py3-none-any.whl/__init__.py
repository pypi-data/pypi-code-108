'''
# Terraform CDK null Provider ~> 2.0

This repo builds and publishes the Terraform null Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-null](https://www.npmjs.com/package/@cdktf/provider-null).

`npm install @cdktf/provider-null`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-null](https://pypi.org/project/cdktf-cdktf-provider-null).

`pipenv install cdktf-cdktf-provider-null`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Null](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Null).

`dotnet add package HashiCorp.Cdktf.Providers.Null`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-null](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-null).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-null</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform null Provider version 1:1. In fact, it always tracks `latest` of `~> 2.0` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform null Provider](https://github.com/terraform-providers/terraform-provider-null)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform null Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

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


class DataNullDataSource(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-null.DataNullDataSource",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/null/d/data_source null_data_source}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        has_computed_default: typing.Optional[builtins.str] = None,
        inputs: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/null/d/data_source null_data_source} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param has_computed_default: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null/d/data_source#has_computed_default DataNullDataSource#has_computed_default}.
        :param inputs: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null/d/data_source#inputs DataNullDataSource#inputs}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataNullDataSourceConfig(
            has_computed_default=has_computed_default,
            inputs=inputs,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="outputs")
    def outputs(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "outputs", [key]))

    @jsii.member(jsii_name="resetHasComputedDefault")
    def reset_has_computed_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHasComputedDefault", []))

    @jsii.member(jsii_name="resetInputs")
    def reset_inputs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInputs", []))

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
    @jsii.member(jsii_name="random")
    def random(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "random"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasComputedDefaultInput")
    def has_computed_default_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hasComputedDefaultInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputsInput")
    def inputs_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "inputsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hasComputedDefault")
    def has_computed_default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hasComputedDefault"))

    @has_computed_default.setter
    def has_computed_default(self, value: builtins.str) -> None:
        jsii.set(self, "hasComputedDefault", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputs")
    def inputs(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "inputs"))

    @inputs.setter
    def inputs(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "inputs", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-null.DataNullDataSourceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "has_computed_default": "hasComputedDefault",
        "inputs": "inputs",
    },
)
class DataNullDataSourceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        has_computed_default: typing.Optional[builtins.str] = None,
        inputs: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param has_computed_default: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null/d/data_source#has_computed_default DataNullDataSource#has_computed_default}.
        :param inputs: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null/d/data_source#inputs DataNullDataSource#inputs}.
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
        if has_computed_default is not None:
            self._values["has_computed_default"] = has_computed_default
        if inputs is not None:
            self._values["inputs"] = inputs

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
    def has_computed_default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null/d/data_source#has_computed_default DataNullDataSource#has_computed_default}.'''
        result = self._values.get("has_computed_default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inputs(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null/d/data_source#inputs DataNullDataSource#inputs}.'''
        result = self._values.get("inputs")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataNullDataSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NullProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-null.NullProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/null null}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/null null} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null#alias NullProvider#alias}
        '''
        config = NullProviderConfig(alias=alias)

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
    jsii_type="@cdktf/provider-null.NullProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias"},
)
class NullProviderConfig:
    def __init__(self, *, alias: typing.Optional[builtins.str] = None) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null#alias NullProvider#alias}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null#alias NullProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NullProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Resource(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-null.Resource",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/null/r/resource null_resource}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        triggers: typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/null/r/resource null_resource} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null/r/resource#triggers Resource#triggers}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ResourceConfig(
            triggers=triggers,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetTriggers")
    def reset_triggers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTriggers", []))

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
    @jsii.member(jsii_name="triggersInput")
    def triggers_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "triggersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="triggers")
    def triggers(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "triggers"))

    @triggers.setter
    def triggers(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "triggers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-null.ResourceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "triggers": "triggers",
    },
)
class ResourceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        triggers: typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param triggers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null/r/resource#triggers Resource#triggers}.
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
        if triggers is not None:
            self._values["triggers"] = triggers

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
    def triggers(
        self,
    ) -> typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null/r/resource#triggers Resource#triggers}.'''
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataNullDataSource",
    "DataNullDataSourceConfig",
    "NullProvider",
    "NullProviderConfig",
    "Resource",
    "ResourceConfig",
]

publication.publish()
