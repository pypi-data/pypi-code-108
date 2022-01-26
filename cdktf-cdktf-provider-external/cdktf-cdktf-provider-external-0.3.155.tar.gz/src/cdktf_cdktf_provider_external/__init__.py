'''
# Terraform CDK external Provider ~> 2.1

This repo builds and publishes the Terraform external Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-external](https://www.npmjs.com/package/@cdktf/provider-external).

`npm install @cdktf/provider-external`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-external](https://pypi.org/project/cdktf-cdktf-provider-external).

`pipenv install cdktf-cdktf-provider-external`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.External](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.External).

`dotnet add package HashiCorp.Cdktf.Providers.External`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-external](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-external).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-external</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform external Provider version 1:1. In fact, it always tracks `latest` of `~> 2.1` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform external Provider](https://github.com/terraform-providers/terraform-provider-external)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform external Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

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


class DataExternal(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-external.DataExternal",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/external/d/external external}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        program: typing.Sequence[builtins.str],
        query: typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]] = None,
        working_dir: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/external/d/external external} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param program: A list of strings, whose first element is the program to run and whose subsequent elements are optional command line arguments to the program. Terraform does not execute the program through a shell, so it is not necessary to escape shell metacharacters nor add quotes around arguments containing spaces. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external/d/external#program DataExternal#program}
        :param query: A map of string values to pass to the external program as the query arguments. If not supplied, the program will receive an empty object as its input. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external/d/external#query DataExternal#query}
        :param working_dir: Working directory of the program. If not supplied, the program will run in the current directory. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external/d/external#working_dir DataExternal#working_dir}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataExternalConfig(
            program=program,
            query=query,
            working_dir=working_dir,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetQuery")
    def reset_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuery", []))

    @jsii.member(jsii_name="resetWorkingDir")
    def reset_working_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkingDir", []))

    @jsii.member(jsii_name="result")
    def result(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "result", [key]))

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
    @jsii.member(jsii_name="programInput")
    def program_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "programInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="queryInput")
    def query_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "queryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirInput")
    def working_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workingDirInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="program")
    def program(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "program"))

    @program.setter
    def program(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "program", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="query")
    def query(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "query"))

    @query.setter
    def query(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "query", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDir")
    def working_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workingDir"))

    @working_dir.setter
    def working_dir(self, value: builtins.str) -> None:
        jsii.set(self, "workingDir", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-external.DataExternalConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "program": "program",
        "query": "query",
        "working_dir": "workingDir",
    },
)
class DataExternalConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        program: typing.Sequence[builtins.str],
        query: typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param program: A list of strings, whose first element is the program to run and whose subsequent elements are optional command line arguments to the program. Terraform does not execute the program through a shell, so it is not necessary to escape shell metacharacters nor add quotes around arguments containing spaces. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external/d/external#program DataExternal#program}
        :param query: A map of string values to pass to the external program as the query arguments. If not supplied, the program will receive an empty object as its input. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external/d/external#query DataExternal#query}
        :param working_dir: Working directory of the program. If not supplied, the program will run in the current directory. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external/d/external#working_dir DataExternal#working_dir}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "program": program,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if query is not None:
            self._values["query"] = query
        if working_dir is not None:
            self._values["working_dir"] = working_dir

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
    def program(self) -> typing.List[builtins.str]:
        '''A list of strings, whose first element is the program to run and whose subsequent elements are optional command line arguments to the program.

        Terraform does not execute the program through a shell, so it is not necessary to escape shell metacharacters nor add quotes around arguments containing spaces.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external/d/external#program DataExternal#program}
        '''
        result = self._values.get("program")
        assert result is not None, "Required property 'program' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def query(
        self,
    ) -> typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]]:
        '''A map of string values to pass to the external program as the query arguments.

        If not supplied, the program will receive an empty object as its input.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external/d/external#query DataExternal#query}
        '''
        result = self._values.get("query")
        return typing.cast(typing.Optional[typing.Union[typing.Mapping[builtins.str, builtins.str], cdktf.IResolvable]], result)

    @builtins.property
    def working_dir(self) -> typing.Optional[builtins.str]:
        '''Working directory of the program. If not supplied, the program will run in the current directory.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external/d/external#working_dir DataExternal#working_dir}
        '''
        result = self._values.get("working_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataExternalConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ExternalProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-external.ExternalProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/external external}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/external external} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external#alias ExternalProvider#alias}
        '''
        config = ExternalProviderConfig(alias=alias)

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
    jsii_type="@cdktf/provider-external.ExternalProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias"},
)
class ExternalProviderConfig:
    def __init__(self, *, alias: typing.Optional[builtins.str] = None) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external#alias ExternalProvider#alias}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/external#alias ExternalProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExternalProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataExternal",
    "DataExternalConfig",
    "ExternalProvider",
    "ExternalProviderConfig",
]

publication.publish()
