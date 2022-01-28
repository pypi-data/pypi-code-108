'''
# CDKTF Local Exec Construct

A simple construct that executes a command locally. This is useful to run build steps within your CDKTF Program or to run a post action after a resource is created.

The construct uses the null provider to achieve this so it can be trusted to only run after all dependencies are met.

## Usage

```python
import { Provider, LocalExec } from "cdktf-local-exec";

// LocalExec extends from the null provider,
// so if you already have the provider initialized you can skip this step
new Provider(this, "local-exec");

const frontend = new LocalExec(this, "frontend-build", {
  // Will copy this into an asset directory
  cwd: "/path/to/project/frontend",
  command: "npm install && npm build",
});

const pathToUpload = `${frontend.path}/dist`;

new LocalExec(this, "frontend-upload", {
  cwd: pathToUpload,
  command: `aws s3 cp --recursive ${pathToUpload} s3://${bucket.name}/frontend`,
});

new LocalExec(this, "backend-build", {
  cwd: "/path/to/project/backend",
  copyBeforeRun: false, // can not run remotely since the runner has no docker access
  command: "docker build -t foo . && docker push foo",
});
```

### Options

* `cwd`: The working directory to run the command in. It will be copied before execution to ensure the asset can be used in a remote execution environment.
* `command`: The command to execute.
* `copyBeforeRun`: If true, the command will copy the `cwd` directory into a tmp dir and run there. If false, the command will be executed in the `cwd` directory.
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
import cdktf_cdktf_provider_null
import constructs


class LocalExec(
    cdktf_cdktf_provider_null.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktf-local-exec.LocalExec",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        command: builtins.str,
        cwd: builtins.str,
        copy_before_run: typing.Optional[builtins.bool] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param command: The command to run.
        :param cwd: The working directory to run the command in. Defaults to process.pwd(). If copyBeforeRun is set to true it will copy the working directory to an asset directory and take that as the base to run.
        :param copy_before_run: If set to true, the working directory will be copied to an asset directory. Default: true
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param triggers: 
        '''
        config = LocalExecOptions(
            command=command,
            cwd=cwd,
            copy_before_run=copy_before_run,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
            triggers=triggers,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="command")
    def command(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "command"))

    @command.setter
    def command(self, value: builtins.str) -> None:
        jsii.set(self, "command", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cwd")
    def cwd(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cwd"))

    @cwd.setter
    def cwd(self, value: builtins.str) -> None:
        jsii.set(self, "cwd", value)


@jsii.data_type(
    jsii_type="cdktf-local-exec.LocalExecOptions",
    jsii_struct_bases=[],
    name_mapping={
        "command": "command",
        "cwd": "cwd",
        "copy_before_run": "copyBeforeRun",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "triggers": "triggers",
    },
)
class LocalExecOptions:
    def __init__(
        self,
        *,
        command: builtins.str,
        cwd: builtins.str,
        copy_before_run: typing.Optional[builtins.bool] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        triggers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param command: The command to run.
        :param cwd: The working directory to run the command in. Defaults to process.pwd(). If copyBeforeRun is set to true it will copy the working directory to an asset directory and take that as the base to run.
        :param copy_before_run: If set to true, the working directory will be copied to an asset directory. Default: true
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param triggers: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "command": command,
            "cwd": cwd,
        }
        if copy_before_run is not None:
            self._values["copy_before_run"] = copy_before_run
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if triggers is not None:
            self._values["triggers"] = triggers

    @builtins.property
    def command(self) -> builtins.str:
        '''The command to run.'''
        result = self._values.get("command")
        assert result is not None, "Required property 'command' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cwd(self) -> builtins.str:
        '''The working directory to run the command in.

        Defaults to process.pwd().
        If copyBeforeRun is set to true it will copy the working directory to an asset directory and take that as the base to run.
        '''
        result = self._values.get("cwd")
        assert result is not None, "Required property 'cwd' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def copy_before_run(self) -> typing.Optional[builtins.bool]:
        '''If set to true, the working directory will be copied to an asset directory.

        :default: true
        '''
        result = self._values.get("copy_before_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def triggers(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        result = self._values.get("triggers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LocalExecOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class NullProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktf-local-exec.NullProvider",
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
        :param id: The scoped construct ID.
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/null#alias NullProvider#alias}
        '''
        config = cdktf_cdktf_provider_null.NullProviderConfig(alias=alias)

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def tf_resource_type(cls) -> builtins.str:
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


__all__ = [
    "LocalExec",
    "LocalExecOptions",
    "NullProvider",
]

publication.publish()
