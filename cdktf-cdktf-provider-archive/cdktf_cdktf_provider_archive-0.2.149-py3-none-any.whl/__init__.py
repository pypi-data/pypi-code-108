'''
# Terraform CDK archive Provider ~> 2.2

This repo builds and publishes the Terraform archive Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-archive](https://www.npmjs.com/package/@cdktf/provider-archive).

`npm install @cdktf/provider-archive`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-archive](https://pypi.org/project/cdktf-cdktf-provider-archive).

`pipenv install cdktf-cdktf-provider-archive`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Archive](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Archive).

`dotnet add package HashiCorp.Cdktf.Providers.Archive`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-archive](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-archive).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-archive</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform archive Provider version 1:1. In fact, it always tracks `latest` of `~> 2.2` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform archive Provider](https://github.com/terraform-providers/terraform-provider-archive)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform archive Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

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


class ArchiveProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.ArchiveProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/archive archive}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/archive archive} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive#alias ArchiveProvider#alias}
        '''
        config = ArchiveProviderConfig(alias=alias)

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
    jsii_type="@cdktf/provider-archive.ArchiveProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias"},
)
class ArchiveProviderConfig:
    def __init__(self, *, alias: typing.Optional[builtins.str] = None) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive#alias ArchiveProvider#alias}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive#alias ArchiveProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ArchiveProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataArchiveFile(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.DataArchiveFile",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/archive/d/file archive_file}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        output_path: builtins.str,
        type: builtins.str,
        excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        output_file_mode: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Sequence["DataArchiveFileSource"]] = None,
        source_content: typing.Optional[builtins.str] = None,
        source_content_filename: typing.Optional[builtins.str] = None,
        source_dir: typing.Optional[builtins.str] = None,
        source_file: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/archive/d/file archive_file} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param output_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_path DataArchiveFile#output_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#type DataArchiveFile#type}.
        :param excludes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#excludes DataArchiveFile#excludes}.
        :param output_file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_file_mode DataArchiveFile#output_file_mode}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source DataArchiveFile#source}
        :param source_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content DataArchiveFile#source_content}.
        :param source_content_filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content_filename DataArchiveFile#source_content_filename}.
        :param source_dir: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_dir DataArchiveFile#source_dir}.
        :param source_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_file DataArchiveFile#source_file}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataArchiveFileConfig(
            output_path=output_path,
            type=type,
            excludes=excludes,
            output_file_mode=output_file_mode,
            source=source,
            source_content=source_content,
            source_content_filename=source_content_filename,
            source_dir=source_dir,
            source_file=source_file,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetExcludes")
    def reset_excludes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludes", []))

    @jsii.member(jsii_name="resetOutputFileMode")
    def reset_output_file_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFileMode", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetSourceContent")
    def reset_source_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceContent", []))

    @jsii.member(jsii_name="resetSourceContentFilename")
    def reset_source_content_filename(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceContentFilename", []))

    @jsii.member(jsii_name="resetSourceDir")
    def reset_source_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceDir", []))

    @jsii.member(jsii_name="resetSourceFile")
    def reset_source_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFile", []))

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
    @jsii.member(jsii_name="outputBase64Sha256")
    def output_base64_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputBase64Sha256"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputMd5")
    def output_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputMd5"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSha")
    def output_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSize")
    def output_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "outputSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludesInput")
    def excludes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFileModeInput")
    def output_file_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputFileModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputPathInput")
    def output_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentFilenameInput")
    def source_content_filename_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceContentFilenameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentInput")
    def source_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceContentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDirInput")
    def source_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceDirInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileInput")
    def source_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[typing.List["DataArchiveFileSource"]]:
        return typing.cast(typing.Optional[typing.List["DataArchiveFileSource"]], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludes")
    def excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludes"))

    @excludes.setter
    def excludes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "excludes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFileMode")
    def output_file_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputFileMode"))

    @output_file_mode.setter
    def output_file_mode(self, value: builtins.str) -> None:
        jsii.set(self, "outputFileMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputPath")
    def output_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputPath"))

    @output_path.setter
    def output_path(self, value: builtins.str) -> None:
        jsii.set(self, "outputPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> typing.List["DataArchiveFileSource"]:
        return typing.cast(typing.List["DataArchiveFileSource"], jsii.get(self, "source"))

    @source.setter
    def source(self, value: typing.List["DataArchiveFileSource"]) -> None:
        jsii.set(self, "source", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContent")
    def source_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceContent"))

    @source_content.setter
    def source_content(self, value: builtins.str) -> None:
        jsii.set(self, "sourceContent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentFilename")
    def source_content_filename(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceContentFilename"))

    @source_content_filename.setter
    def source_content_filename(self, value: builtins.str) -> None:
        jsii.set(self, "sourceContentFilename", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDir")
    def source_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDir"))

    @source_dir.setter
    def source_dir(self, value: builtins.str) -> None:
        jsii.set(self, "sourceDir", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFile")
    def source_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFile"))

    @source_file.setter
    def source_file(self, value: builtins.str) -> None:
        jsii.set(self, "sourceFile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-archive.DataArchiveFileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "output_path": "outputPath",
        "type": "type",
        "excludes": "excludes",
        "output_file_mode": "outputFileMode",
        "source": "source",
        "source_content": "sourceContent",
        "source_content_filename": "sourceContentFilename",
        "source_dir": "sourceDir",
        "source_file": "sourceFile",
    },
)
class DataArchiveFileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        output_path: builtins.str,
        type: builtins.str,
        excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        output_file_mode: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Sequence["DataArchiveFileSource"]] = None,
        source_content: typing.Optional[builtins.str] = None,
        source_content_filename: typing.Optional[builtins.str] = None,
        source_dir: typing.Optional[builtins.str] = None,
        source_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param output_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_path DataArchiveFile#output_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#type DataArchiveFile#type}.
        :param excludes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#excludes DataArchiveFile#excludes}.
        :param output_file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_file_mode DataArchiveFile#output_file_mode}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source DataArchiveFile#source}
        :param source_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content DataArchiveFile#source_content}.
        :param source_content_filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content_filename DataArchiveFile#source_content_filename}.
        :param source_dir: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_dir DataArchiveFile#source_dir}.
        :param source_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_file DataArchiveFile#source_file}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "output_path": output_path,
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if excludes is not None:
            self._values["excludes"] = excludes
        if output_file_mode is not None:
            self._values["output_file_mode"] = output_file_mode
        if source is not None:
            self._values["source"] = source
        if source_content is not None:
            self._values["source_content"] = source_content
        if source_content_filename is not None:
            self._values["source_content_filename"] = source_content_filename
        if source_dir is not None:
            self._values["source_dir"] = source_dir
        if source_file is not None:
            self._values["source_file"] = source_file

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
    def output_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_path DataArchiveFile#output_path}.'''
        result = self._values.get("output_path")
        assert result is not None, "Required property 'output_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#type DataArchiveFile#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def excludes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#excludes DataArchiveFile#excludes}.'''
        result = self._values.get("excludes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def output_file_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#output_file_mode DataArchiveFile#output_file_mode}.'''
        result = self._values.get("output_file_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional[typing.List["DataArchiveFileSource"]]:
        '''source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source DataArchiveFile#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[typing.List["DataArchiveFileSource"]], result)

    @builtins.property
    def source_content(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content DataArchiveFile#source_content}.'''
        result = self._values.get("source_content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_content_filename(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_content_filename DataArchiveFile#source_content_filename}.'''
        result = self._values.get("source_content_filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_dir(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_dir DataArchiveFile#source_dir}.'''
        result = self._values.get("source_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#source_file DataArchiveFile#source_file}.'''
        result = self._values.get("source_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataArchiveFileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-archive.DataArchiveFileSource",
    jsii_struct_bases=[],
    name_mapping={"content": "content", "filename": "filename"},
)
class DataArchiveFileSource:
    def __init__(self, *, content: builtins.str, filename: builtins.str) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#content DataArchiveFile#content}.
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#filename DataArchiveFile#filename}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "filename": filename,
        }

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#content DataArchiveFile#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filename(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/d/file#filename DataArchiveFile#filename}.'''
        result = self._values.get("filename")
        assert result is not None, "Required property 'filename' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataArchiveFileSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class File(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-archive.File",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/archive/r/file archive_file}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        output_path: builtins.str,
        type: builtins.str,
        excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        output_file_mode: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Sequence["FileSource"]] = None,
        source_content: typing.Optional[builtins.str] = None,
        source_content_filename: typing.Optional[builtins.str] = None,
        source_dir: typing.Optional[builtins.str] = None,
        source_file: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/archive/r/file archive_file} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param output_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_path File#output_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#type File#type}.
        :param excludes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#excludes File#excludes}.
        :param output_file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_file_mode File#output_file_mode}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source File#source}
        :param source_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content File#source_content}.
        :param source_content_filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content_filename File#source_content_filename}.
        :param source_dir: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_dir File#source_dir}.
        :param source_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_file File#source_file}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = FileConfig(
            output_path=output_path,
            type=type,
            excludes=excludes,
            output_file_mode=output_file_mode,
            source=source,
            source_content=source_content,
            source_content_filename=source_content_filename,
            source_dir=source_dir,
            source_file=source_file,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetExcludes")
    def reset_excludes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludes", []))

    @jsii.member(jsii_name="resetOutputFileMode")
    def reset_output_file_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOutputFileMode", []))

    @jsii.member(jsii_name="resetSource")
    def reset_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSource", []))

    @jsii.member(jsii_name="resetSourceContent")
    def reset_source_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceContent", []))

    @jsii.member(jsii_name="resetSourceContentFilename")
    def reset_source_content_filename(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceContentFilename", []))

    @jsii.member(jsii_name="resetSourceDir")
    def reset_source_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceDir", []))

    @jsii.member(jsii_name="resetSourceFile")
    def reset_source_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSourceFile", []))

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
    @jsii.member(jsii_name="outputBase64Sha256")
    def output_base64_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputBase64Sha256"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputMd5")
    def output_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputMd5"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSha")
    def output_sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputSha"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputSize")
    def output_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "outputSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludesInput")
    def excludes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "excludesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFileModeInput")
    def output_file_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputFileModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputPathInput")
    def output_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "outputPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentFilenameInput")
    def source_content_filename_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceContentFilenameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentInput")
    def source_content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceContentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDirInput")
    def source_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceDirInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFileInput")
    def source_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceFileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceInput")
    def source_input(self) -> typing.Optional[typing.List["FileSource"]]:
        return typing.cast(typing.Optional[typing.List["FileSource"]], jsii.get(self, "sourceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="excludes")
    def excludes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "excludes"))

    @excludes.setter
    def excludes(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "excludes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputFileMode")
    def output_file_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputFileMode"))

    @output_file_mode.setter
    def output_file_mode(self, value: builtins.str) -> None:
        jsii.set(self, "outputFileMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outputPath")
    def output_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outputPath"))

    @output_path.setter
    def output_path(self, value: builtins.str) -> None:
        jsii.set(self, "outputPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> typing.List["FileSource"]:
        return typing.cast(typing.List["FileSource"], jsii.get(self, "source"))

    @source.setter
    def source(self, value: typing.List["FileSource"]) -> None:
        jsii.set(self, "source", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContent")
    def source_content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceContent"))

    @source_content.setter
    def source_content(self, value: builtins.str) -> None:
        jsii.set(self, "sourceContent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceContentFilename")
    def source_content_filename(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceContentFilename"))

    @source_content_filename.setter
    def source_content_filename(self, value: builtins.str) -> None:
        jsii.set(self, "sourceContentFilename", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceDir")
    def source_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceDir"))

    @source_dir.setter
    def source_dir(self, value: builtins.str) -> None:
        jsii.set(self, "sourceDir", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sourceFile")
    def source_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceFile"))

    @source_file.setter
    def source_file(self, value: builtins.str) -> None:
        jsii.set(self, "sourceFile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-archive.FileConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "output_path": "outputPath",
        "type": "type",
        "excludes": "excludes",
        "output_file_mode": "outputFileMode",
        "source": "source",
        "source_content": "sourceContent",
        "source_content_filename": "sourceContentFilename",
        "source_dir": "sourceDir",
        "source_file": "sourceFile",
    },
)
class FileConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        output_path: builtins.str,
        type: builtins.str,
        excludes: typing.Optional[typing.Sequence[builtins.str]] = None,
        output_file_mode: typing.Optional[builtins.str] = None,
        source: typing.Optional[typing.Sequence["FileSource"]] = None,
        source_content: typing.Optional[builtins.str] = None,
        source_content_filename: typing.Optional[builtins.str] = None,
        source_dir: typing.Optional[builtins.str] = None,
        source_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param output_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_path File#output_path}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#type File#type}.
        :param excludes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#excludes File#excludes}.
        :param output_file_mode: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_file_mode File#output_file_mode}.
        :param source: source block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source File#source}
        :param source_content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content File#source_content}.
        :param source_content_filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content_filename File#source_content_filename}.
        :param source_dir: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_dir File#source_dir}.
        :param source_file: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_file File#source_file}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "output_path": output_path,
            "type": type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if excludes is not None:
            self._values["excludes"] = excludes
        if output_file_mode is not None:
            self._values["output_file_mode"] = output_file_mode
        if source is not None:
            self._values["source"] = source
        if source_content is not None:
            self._values["source_content"] = source_content
        if source_content_filename is not None:
            self._values["source_content_filename"] = source_content_filename
        if source_dir is not None:
            self._values["source_dir"] = source_dir
        if source_file is not None:
            self._values["source_file"] = source_file

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
    def output_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_path File#output_path}.'''
        result = self._values.get("output_path")
        assert result is not None, "Required property 'output_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#type File#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def excludes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#excludes File#excludes}.'''
        result = self._values.get("excludes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def output_file_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#output_file_mode File#output_file_mode}.'''
        result = self._values.get("output_file_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source(self) -> typing.Optional[typing.List["FileSource"]]:
        '''source block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source File#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[typing.List["FileSource"]], result)

    @builtins.property
    def source_content(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content File#source_content}.'''
        result = self._values.get("source_content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_content_filename(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_content_filename File#source_content_filename}.'''
        result = self._values.get("source_content_filename")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_dir(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_dir File#source_dir}.'''
        result = self._values.get("source_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_file(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#source_file File#source_file}.'''
        result = self._values.get("source_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-archive.FileSource",
    jsii_struct_bases=[],
    name_mapping={"content": "content", "filename": "filename"},
)
class FileSource:
    def __init__(self, *, content: builtins.str, filename: builtins.str) -> None:
        '''
        :param content: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#content File#content}.
        :param filename: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#filename File#filename}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "filename": filename,
        }

    @builtins.property
    def content(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#content File#content}.'''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filename(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/archive/r/file#filename File#filename}.'''
        result = self._values.get("filename")
        assert result is not None, "Required property 'filename' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FileSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ArchiveProvider",
    "ArchiveProviderConfig",
    "DataArchiveFile",
    "DataArchiveFileConfig",
    "DataArchiveFileSource",
    "File",
    "FileConfig",
    "FileSource",
]

publication.publish()
