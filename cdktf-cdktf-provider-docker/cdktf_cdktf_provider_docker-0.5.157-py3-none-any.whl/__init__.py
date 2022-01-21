'''
# Terraform CDK docker Provider ~> 2.12

This repo builds and publishes the Terraform docker Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-docker](https://www.npmjs.com/package/@cdktf/provider-docker).

`npm install @cdktf/provider-docker`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-docker](https://pypi.org/project/cdktf-cdktf-provider-docker).

`pipenv install cdktf-cdktf-provider-docker`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Docker](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Docker).

`dotnet add package HashiCorp.Cdktf.Providers.Docker`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-docker](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-docker).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-docker</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform docker Provider version 1:1. In fact, it always tracks `latest` of `~> 2.12` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform docker Provider](https://github.com/terraform-providers/terraform-provider-docker)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform docker Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

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


class Config(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Config",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/config docker_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        data: builtins.str,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/config docker_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param data: Base64-url-safe-encoded config data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config#data Config#data}
        :param name: User-defined name of the config. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config#name Config#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ConfigConfig(
            data=data,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="dataInput")
    def data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @data.setter
    def data(self, value: builtins.str) -> None:
        jsii.set(self, "data", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "data": "data",
        "name": "name",
    },
)
class ConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        data: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param data: Base64-url-safe-encoded config data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config#data Config#data}
        :param name: User-defined name of the config. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config#name Config#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "data": data,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

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
    def data(self) -> builtins.str:
        '''Base64-url-safe-encoded config data.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config#data Config#data}
        '''
        result = self._values.get("data")
        assert result is not None, "Required property 'data' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''User-defined name of the config.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config#name Config#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Container(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Container",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/container docker_container}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        image: builtins.str,
        name: builtins.str,
        attach: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        capabilities: typing.Optional["ContainerCapabilities"] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        cpu_set: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        destroy_grace_seconds: typing.Optional[jsii.Number] = None,
        devices: typing.Optional[typing.Sequence["ContainerDevices"]] = None,
        dns: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_opts: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_search: typing.Optional[typing.Sequence[builtins.str]] = None,
        domainname: typing.Optional[builtins.str] = None,
        entrypoint: typing.Optional[typing.Sequence[builtins.str]] = None,
        env: typing.Optional[typing.Sequence[builtins.str]] = None,
        group_add: typing.Optional[typing.Sequence[builtins.str]] = None,
        healthcheck: typing.Optional["ContainerHealthcheck"] = None,
        host: typing.Optional[typing.Sequence["ContainerHost"]] = None,
        hostname: typing.Optional[builtins.str] = None,
        init: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ipc_mode: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Sequence["ContainerLabels"]] = None,
        links: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_driver: typing.Optional[builtins.str] = None,
        log_opts: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        logs: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_retry_count: typing.Optional[jsii.Number] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_swap: typing.Optional[jsii.Number] = None,
        mounts: typing.Optional[typing.Sequence["ContainerMounts"]] = None,
        must_run: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        network_alias: typing.Optional[typing.Sequence[builtins.str]] = None,
        network_mode: typing.Optional[builtins.str] = None,
        networks: typing.Optional[typing.Sequence[builtins.str]] = None,
        networks_advanced: typing.Optional[typing.Sequence["ContainerNetworksAdvanced"]] = None,
        pid_mode: typing.Optional[builtins.str] = None,
        ports: typing.Optional[typing.Sequence["ContainerPorts"]] = None,
        privileged: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        publish_all_ports: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        remove_volumes: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restart: typing.Optional[builtins.str] = None,
        rm: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        security_opts: typing.Optional[typing.Sequence[builtins.str]] = None,
        shm_size: typing.Optional[jsii.Number] = None,
        start: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        stdin_open: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        storage_opts: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        sysctls: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tmpfs: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tty: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ulimit: typing.Optional[typing.Sequence["ContainerUlimit"]] = None,
        upload: typing.Optional[typing.Sequence["ContainerUpload"]] = None,
        user: typing.Optional[builtins.str] = None,
        userns_mode: typing.Optional[builtins.str] = None,
        volumes: typing.Optional[typing.Sequence["ContainerVolumes"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/container docker_container} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param image: The ID of the image to back this container. The easiest way to get this value is to use the ``docker_image`` resource as is shown in the example. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#image Container#image}
        :param name: The name of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#name Container#name}
        :param attach: If ``true`` attach to the container after its creation and waits the end of its execution. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#attach Container#attach}
        :param capabilities: capabilities block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#capabilities Container#capabilities}
        :param command: The command to use to start the container. For example, to run ``/usr/bin/myprogram -f baz.conf`` set the command to be ``["/usr/bin/myprogram","-","baz.con"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#command Container#command}
        :param cpu_set: A comma-separated list or hyphen-separated range of CPUs a container can use, e.g. ``0-1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#cpu_set Container#cpu_set}
        :param cpu_shares: CPU shares (relative weight) for the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#cpu_shares Container#cpu_shares}
        :param destroy_grace_seconds: If defined will attempt to stop the container before destroying. Container will be destroyed after ``n`` seconds or on successful stop. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#destroy_grace_seconds Container#destroy_grace_seconds}
        :param devices: devices block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#devices Container#devices}
        :param dns: DNS servers to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#dns Container#dns}
        :param dns_opts: DNS options used by the DNS provider(s), see ``resolv.conf`` documentation for valid list of options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#dns_opts Container#dns_opts}
        :param dns_search: DNS search domains that are used when bare unqualified hostnames are used inside of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#dns_search Container#dns_search}
        :param domainname: Domain name of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#domainname Container#domainname}
        :param entrypoint: The command to use as the Entrypoint for the container. The Entrypoint allows you to configure a container to run as an executable. For example, to run ``/usr/bin/myprogram`` when starting a container, set the entrypoint to be ``"/usr/bin/myprogra"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#entrypoint Container#entrypoint}
        :param env: Environment variables to set in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#env Container#env}
        :param group_add: Additional groups for the container user. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#group_add Container#group_add}
        :param healthcheck: healthcheck block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#healthcheck Container#healthcheck}
        :param host: host block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#host Container#host}
        :param hostname: Hostname of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#hostname Container#hostname}
        :param init: Configured whether an init process should be injected for this container. If unset this will default to the ``dockerd`` defaults. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#init Container#init}
        :param ipc_mode: IPC sharing mode for the container. Possible values are: ``none``, ``private``, ``shareable``, ``container:<name|id>`` or ``host``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ipc_mode Container#ipc_mode}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#labels Container#labels}
        :param links: Set of links for link based connectivity between containers that are running on the same host. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#links Container#links}
        :param log_driver: The logging driver to use for the container. Defaults to ``json-file``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#log_driver Container#log_driver}
        :param log_opts: Key/value pairs to use as options for the logging driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#log_opts Container#log_opts}
        :param logs: Save the container logs (``attach`` must be enabled). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#logs Container#logs}
        :param max_retry_count: The maximum amount of times to an attempt a restart when ``restart`` is set to 'on-failure'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#max_retry_count Container#max_retry_count}
        :param memory: The memory limit for the container in MBs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#memory Container#memory}
        :param memory_swap: The total memory limit (memory + swap) for the container in MBs. This setting may compute to ``-1`` after ``terraform apply`` if the target host doesn't support memory swap, when that is the case docker will use a soft limitation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#memory_swap Container#memory_swap}
        :param mounts: mounts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#mounts Container#mounts}
        :param must_run: If ``true``, then the Docker container will be kept running. If ``false``, then as long as the container exists, Terraform assumes it is successful. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#must_run Container#must_run}
        :param network_alias: Set an alias for the container in all specified networks. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#network_alias Container#network_alias}
        :param network_mode: Network mode of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#network_mode Container#network_mode}
        :param networks: ID of the networks in which the container is. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#networks Container#networks}
        :param networks_advanced: networks_advanced block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#networks_advanced Container#networks_advanced}
        :param pid_mode: he PID (Process) Namespace mode for the container. Either ``container:<name|id>`` or ``host``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#pid_mode Container#pid_mode}
        :param ports: ports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ports Container#ports}
        :param privileged: If ``true``, the container runs in privileged mode. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#privileged Container#privileged}
        :param publish_all_ports: Publish all ports of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#publish_all_ports Container#publish_all_ports}
        :param read_only: If ``true``, the container will be started as readonly. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#read_only Container#read_only}
        :param remove_volumes: If ``true``, it will remove anonymous volumes associated with the container. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#remove_volumes Container#remove_volumes}
        :param restart: The restart policy for the container. Must be one of 'no', 'on-failure', 'always', 'unless-stopped'. Defaults to ``no``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#restart Container#restart}
        :param rm: If ``true``, then the container will be automatically removed after his execution. Terraform won't check this container after creation. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#rm Container#rm}
        :param security_opts: List of string values to customize labels for MLS systems, such as SELinux. See https://docs.docker.com/engine/reference/run/#security-configuration. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#security_opts Container#security_opts}
        :param shm_size: Size of ``/dev/shm`` in MBs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#shm_size Container#shm_size}
        :param start: If ``true``, then the Docker container will be started after creation. If ``false``, then the container is only created. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#start Container#start}
        :param stdin_open: If ``true``, keep STDIN open even if not attached (``docker run -i``). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#stdin_open Container#stdin_open}
        :param storage_opts: Key/value pairs for the storage driver options, e.g. ``size``: ``120G``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#storage_opts Container#storage_opts}
        :param sysctls: A map of kernel parameters (sysctls) to set in the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#sysctls Container#sysctls}
        :param tmpfs: A map of container directories which should be replaced by ``tmpfs mounts``, and their corresponding mount options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#tmpfs Container#tmpfs}
        :param tty: If ``true``, allocate a pseudo-tty (``docker run -t``). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#tty Container#tty}
        :param ulimit: ulimit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ulimit Container#ulimit}
        :param upload: upload block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#upload Container#upload}
        :param user: User used for run the first process. Format is ``user`` or ``user:group`` which user and group can be passed literraly or by name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#user Container#user}
        :param userns_mode: Sets the usernamespace mode for the container when usernamespace remapping option is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#userns_mode Container#userns_mode}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#volumes Container#volumes}
        :param working_dir: The working directory for commands to run in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#working_dir Container#working_dir}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ContainerConfig(
            image=image,
            name=name,
            attach=attach,
            capabilities=capabilities,
            command=command,
            cpu_set=cpu_set,
            cpu_shares=cpu_shares,
            destroy_grace_seconds=destroy_grace_seconds,
            devices=devices,
            dns=dns,
            dns_opts=dns_opts,
            dns_search=dns_search,
            domainname=domainname,
            entrypoint=entrypoint,
            env=env,
            group_add=group_add,
            healthcheck=healthcheck,
            host=host,
            hostname=hostname,
            init=init,
            ipc_mode=ipc_mode,
            labels=labels,
            links=links,
            log_driver=log_driver,
            log_opts=log_opts,
            logs=logs,
            max_retry_count=max_retry_count,
            memory=memory,
            memory_swap=memory_swap,
            mounts=mounts,
            must_run=must_run,
            network_alias=network_alias,
            network_mode=network_mode,
            networks=networks,
            networks_advanced=networks_advanced,
            pid_mode=pid_mode,
            ports=ports,
            privileged=privileged,
            publish_all_ports=publish_all_ports,
            read_only=read_only,
            remove_volumes=remove_volumes,
            restart=restart,
            rm=rm,
            security_opts=security_opts,
            shm_size=shm_size,
            start=start,
            stdin_open=stdin_open,
            storage_opts=storage_opts,
            sysctls=sysctls,
            tmpfs=tmpfs,
            tty=tty,
            ulimit=ulimit,
            upload=upload,
            user=user,
            userns_mode=userns_mode,
            volumes=volumes,
            working_dir=working_dir,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="networkData")
    def network_data(self, index: builtins.str) -> "ContainerNetworkData":
        '''
        :param index: -
        '''
        return typing.cast("ContainerNetworkData", jsii.invoke(self, "networkData", [index]))

    @jsii.member(jsii_name="putCapabilities")
    def put_capabilities(
        self,
        *,
        add: typing.Optional[typing.Sequence[builtins.str]] = None,
        drop: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param add: List of linux capabilities to add. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#add Container#add}
        :param drop: List of linux capabilities to drop. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#drop Container#drop}
        '''
        value = ContainerCapabilities(add=add, drop=drop)

        return typing.cast(None, jsii.invoke(self, "putCapabilities", [value]))

    @jsii.member(jsii_name="putHealthcheck")
    def put_healthcheck(
        self,
        *,
        test: typing.Sequence[builtins.str],
        interval: typing.Optional[builtins.str] = None,
        retries: typing.Optional[jsii.Number] = None,
        start_period: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param test: Command to run to check health. For example, to run ``curl -f localhost/health`` set the command to be ``["CMD", "curl", "-f", "localhost/health"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#test Container#test}
        :param interval: Time between running the check (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#interval Container#interval}
        :param retries: Consecutive failures needed to report unhealthy. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#retries Container#retries}
        :param start_period: Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#start_period Container#start_period}
        :param timeout: Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#timeout Container#timeout}
        '''
        value = ContainerHealthcheck(
            test=test,
            interval=interval,
            retries=retries,
            start_period=start_period,
            timeout=timeout,
        )

        return typing.cast(None, jsii.invoke(self, "putHealthcheck", [value]))

    @jsii.member(jsii_name="resetAttach")
    def reset_attach(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttach", []))

    @jsii.member(jsii_name="resetCapabilities")
    def reset_capabilities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapabilities", []))

    @jsii.member(jsii_name="resetCommand")
    def reset_command(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommand", []))

    @jsii.member(jsii_name="resetCpuSet")
    def reset_cpu_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuSet", []))

    @jsii.member(jsii_name="resetCpuShares")
    def reset_cpu_shares(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuShares", []))

    @jsii.member(jsii_name="resetDestroyGraceSeconds")
    def reset_destroy_grace_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestroyGraceSeconds", []))

    @jsii.member(jsii_name="resetDevices")
    def reset_devices(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDevices", []))

    @jsii.member(jsii_name="resetDns")
    def reset_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDns", []))

    @jsii.member(jsii_name="resetDnsOpts")
    def reset_dns_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsOpts", []))

    @jsii.member(jsii_name="resetDnsSearch")
    def reset_dns_search(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsSearch", []))

    @jsii.member(jsii_name="resetDomainname")
    def reset_domainname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainname", []))

    @jsii.member(jsii_name="resetEntrypoint")
    def reset_entrypoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntrypoint", []))

    @jsii.member(jsii_name="resetEnv")
    def reset_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnv", []))

    @jsii.member(jsii_name="resetGroupAdd")
    def reset_group_add(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupAdd", []))

    @jsii.member(jsii_name="resetHealthcheck")
    def reset_healthcheck(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthcheck", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetHostname")
    def reset_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostname", []))

    @jsii.member(jsii_name="resetInit")
    def reset_init(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInit", []))

    @jsii.member(jsii_name="resetIpcMode")
    def reset_ipc_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpcMode", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetLinks")
    def reset_links(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinks", []))

    @jsii.member(jsii_name="resetLogDriver")
    def reset_log_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogDriver", []))

    @jsii.member(jsii_name="resetLogOpts")
    def reset_log_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogOpts", []))

    @jsii.member(jsii_name="resetLogs")
    def reset_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogs", []))

    @jsii.member(jsii_name="resetMaxRetryCount")
    def reset_max_retry_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRetryCount", []))

    @jsii.member(jsii_name="resetMemory")
    def reset_memory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemory", []))

    @jsii.member(jsii_name="resetMemorySwap")
    def reset_memory_swap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemorySwap", []))

    @jsii.member(jsii_name="resetMounts")
    def reset_mounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMounts", []))

    @jsii.member(jsii_name="resetMustRun")
    def reset_must_run(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMustRun", []))

    @jsii.member(jsii_name="resetNetworkAlias")
    def reset_network_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkAlias", []))

    @jsii.member(jsii_name="resetNetworkMode")
    def reset_network_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkMode", []))

    @jsii.member(jsii_name="resetNetworks")
    def reset_networks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworks", []))

    @jsii.member(jsii_name="resetNetworksAdvanced")
    def reset_networks_advanced(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworksAdvanced", []))

    @jsii.member(jsii_name="resetPidMode")
    def reset_pid_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPidMode", []))

    @jsii.member(jsii_name="resetPorts")
    def reset_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPorts", []))

    @jsii.member(jsii_name="resetPrivileged")
    def reset_privileged(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivileged", []))

    @jsii.member(jsii_name="resetPublishAllPorts")
    def reset_publish_all_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublishAllPorts", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetRemoveVolumes")
    def reset_remove_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoveVolumes", []))

    @jsii.member(jsii_name="resetRestart")
    def reset_restart(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestart", []))

    @jsii.member(jsii_name="resetRm")
    def reset_rm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRm", []))

    @jsii.member(jsii_name="resetSecurityOpts")
    def reset_security_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityOpts", []))

    @jsii.member(jsii_name="resetShmSize")
    def reset_shm_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShmSize", []))

    @jsii.member(jsii_name="resetStart")
    def reset_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStart", []))

    @jsii.member(jsii_name="resetStdinOpen")
    def reset_stdin_open(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStdinOpen", []))

    @jsii.member(jsii_name="resetStorageOpts")
    def reset_storage_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageOpts", []))

    @jsii.member(jsii_name="resetSysctls")
    def reset_sysctls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSysctls", []))

    @jsii.member(jsii_name="resetTmpfs")
    def reset_tmpfs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTmpfs", []))

    @jsii.member(jsii_name="resetTty")
    def reset_tty(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTty", []))

    @jsii.member(jsii_name="resetUlimit")
    def reset_ulimit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUlimit", []))

    @jsii.member(jsii_name="resetUpload")
    def reset_upload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpload", []))

    @jsii.member(jsii_name="resetUser")
    def reset_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUser", []))

    @jsii.member(jsii_name="resetUsernsMode")
    def reset_userns_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernsMode", []))

    @jsii.member(jsii_name="resetVolumes")
    def reset_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumes", []))

    @jsii.member(jsii_name="resetWorkingDir")
    def reset_working_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkingDir", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bridge")
    def bridge(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bridge"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capabilities")
    def capabilities(self) -> "ContainerCapabilitiesOutputReference":
        return typing.cast("ContainerCapabilitiesOutputReference", jsii.get(self, "capabilities"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerLogs")
    def container_logs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="exitCode")
    def exit_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "exitCode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheck")
    def healthcheck(self) -> "ContainerHealthcheckOutputReference":
        return typing.cast("ContainerHealthcheckOutputReference", jsii.get(self, "healthcheck"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipPrefixLength")
    def ip_prefix_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ipPrefixLength"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attachInput")
    def attach_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "attachInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capabilitiesInput")
    def capabilities_input(self) -> typing.Optional["ContainerCapabilities"]:
        return typing.cast(typing.Optional["ContainerCapabilities"], jsii.get(self, "capabilitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commandInput")
    def command_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "commandInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSetInput")
    def cpu_set_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpuSetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSharesInput")
    def cpu_shares_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuSharesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destroyGraceSecondsInput")
    def destroy_grace_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "destroyGraceSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="devicesInput")
    def devices_input(self) -> typing.Optional[typing.List["ContainerDevices"]]:
        return typing.cast(typing.Optional[typing.List["ContainerDevices"]], jsii.get(self, "devicesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsInput")
    def dns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsOptsInput")
    def dns_opts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsSearchInput")
    def dns_search_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsSearchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainnameInput")
    def domainname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entrypointInput")
    def entrypoint_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "entrypointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="envInput")
    def env_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "envInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupAddInput")
    def group_add_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "groupAddInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheckInput")
    def healthcheck_input(self) -> typing.Optional["ContainerHealthcheck"]:
        return typing.cast(typing.Optional["ContainerHealthcheck"], jsii.get(self, "healthcheckInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[typing.List["ContainerHost"]]:
        return typing.cast(typing.Optional[typing.List["ContainerHost"]], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="initInput")
    def init_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "initInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipcModeInput")
    def ipc_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipcModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["ContainerLabels"]]:
        return typing.cast(typing.Optional[typing.List["ContainerLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="linksInput")
    def links_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "linksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDriverInput")
    def log_driver_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logDriverInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logOptsInput")
    def log_opts_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "logOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logsInput")
    def logs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "logsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetryCountInput")
    def max_retry_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetryCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryInput")
    def memory_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memorySwapInput")
    def memory_swap_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memorySwapInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountsInput")
    def mounts_input(self) -> typing.Optional[typing.List["ContainerMounts"]]:
        return typing.cast(typing.Optional[typing.List["ContainerMounts"]], jsii.get(self, "mountsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mustRunInput")
    def must_run_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "mustRunInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkAliasInput")
    def network_alias_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "networkAliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkModeInput")
    def network_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networksAdvancedInput")
    def networks_advanced_input(
        self,
    ) -> typing.Optional[typing.List["ContainerNetworksAdvanced"]]:
        return typing.cast(typing.Optional[typing.List["ContainerNetworksAdvanced"]], jsii.get(self, "networksAdvancedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networksInput")
    def networks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "networksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pidModeInput")
    def pid_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pidModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portsInput")
    def ports_input(self) -> typing.Optional[typing.List["ContainerPorts"]]:
        return typing.cast(typing.Optional[typing.List["ContainerPorts"]], jsii.get(self, "portsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privilegedInput")
    def privileged_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "privilegedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishAllPortsInput")
    def publish_all_ports_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "publishAllPortsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="removeVolumesInput")
    def remove_volumes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "removeVolumesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartInput")
    def restart_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restartInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rmInput")
    def rm_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "rmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityOptsInput")
    def security_opts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shmSizeInput")
    def shm_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "shmSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startInput")
    def start_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "startInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stdinOpenInput")
    def stdin_open_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "stdinOpenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageOptsInput")
    def storage_opts_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "storageOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sysctlsInput")
    def sysctls_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "sysctlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tmpfsInput")
    def tmpfs_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tmpfsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ttyInput")
    def tty_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ttyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ulimitInput")
    def ulimit_input(self) -> typing.Optional[typing.List["ContainerUlimit"]]:
        return typing.cast(typing.Optional[typing.List["ContainerUlimit"]], jsii.get(self, "ulimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uploadInput")
    def upload_input(self) -> typing.Optional[typing.List["ContainerUpload"]]:
        return typing.cast(typing.Optional[typing.List["ContainerUpload"]], jsii.get(self, "uploadInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernsModeInput")
    def userns_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernsModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumesInput")
    def volumes_input(self) -> typing.Optional[typing.List["ContainerVolumes"]]:
        return typing.cast(typing.Optional[typing.List["ContainerVolumes"]], jsii.get(self, "volumesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirInput")
    def working_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workingDirInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attach")
    def attach(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "attach"))

    @attach.setter
    def attach(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "attach", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "command"))

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "command", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSet")
    def cpu_set(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuSet"))

    @cpu_set.setter
    def cpu_set(self, value: builtins.str) -> None:
        jsii.set(self, "cpuSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuShares")
    def cpu_shares(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuShares"))

    @cpu_shares.setter
    def cpu_shares(self, value: jsii.Number) -> None:
        jsii.set(self, "cpuShares", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destroyGraceSeconds")
    def destroy_grace_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "destroyGraceSeconds"))

    @destroy_grace_seconds.setter
    def destroy_grace_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "destroyGraceSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="devices")
    def devices(self) -> typing.List["ContainerDevices"]:
        return typing.cast(typing.List["ContainerDevices"], jsii.get(self, "devices"))

    @devices.setter
    def devices(self, value: typing.List["ContainerDevices"]) -> None:
        jsii.set(self, "devices", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dns")
    def dns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dns"))

    @dns.setter
    def dns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsOpts")
    def dns_opts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsOpts"))

    @dns_opts.setter
    def dns_opts(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsSearch")
    def dns_search(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsSearch"))

    @dns_search.setter
    def dns_search(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsSearch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainname")
    def domainname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainname"))

    @domainname.setter
    def domainname(self, value: builtins.str) -> None:
        jsii.set(self, "domainname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entrypoint")
    def entrypoint(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "entrypoint"))

    @entrypoint.setter
    def entrypoint(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "entrypoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "env"))

    @env.setter
    def env(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "env", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupAdd")
    def group_add(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "groupAdd"))

    @group_add.setter
    def group_add(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "groupAdd", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> typing.List["ContainerHost"]:
        return typing.cast(typing.List["ContainerHost"], jsii.get(self, "host"))

    @host.setter
    def host(self, value: typing.List["ContainerHost"]) -> None:
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        jsii.set(self, "hostname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @image.setter
    def image(self, value: builtins.str) -> None:
        jsii.set(self, "image", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="init")
    def init(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "init"))

    @init.setter
    def init(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "init", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipcMode")
    def ipc_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipcMode"))

    @ipc_mode.setter
    def ipc_mode(self, value: builtins.str) -> None:
        jsii.set(self, "ipcMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["ContainerLabels"]:
        return typing.cast(typing.List["ContainerLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["ContainerLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="links")
    def links(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "links"))

    @links.setter
    def links(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "links", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDriver")
    def log_driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logDriver"))

    @log_driver.setter
    def log_driver(self, value: builtins.str) -> None:
        jsii.set(self, "logDriver", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logOpts")
    def log_opts(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "logOpts"))

    @log_opts.setter
    def log_opts(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "logOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logs")
    def logs(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "logs"))

    @logs.setter
    def logs(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "logs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetryCount")
    def max_retry_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxRetryCount"))

    @max_retry_count.setter
    def max_retry_count(self, value: jsii.Number) -> None:
        jsii.set(self, "maxRetryCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memory")
    def memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memory"))

    @memory.setter
    def memory(self, value: jsii.Number) -> None:
        jsii.set(self, "memory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memorySwap")
    def memory_swap(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memorySwap"))

    @memory_swap.setter
    def memory_swap(self, value: jsii.Number) -> None:
        jsii.set(self, "memorySwap", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mounts")
    def mounts(self) -> typing.List["ContainerMounts"]:
        return typing.cast(typing.List["ContainerMounts"], jsii.get(self, "mounts"))

    @mounts.setter
    def mounts(self, value: typing.List["ContainerMounts"]) -> None:
        jsii.set(self, "mounts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mustRun")
    def must_run(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "mustRun"))

    @must_run.setter
    def must_run(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "mustRun", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkAlias")
    def network_alias(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networkAlias"))

    @network_alias.setter
    def network_alias(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "networkAlias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkMode")
    def network_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkMode"))

    @network_mode.setter
    def network_mode(self, value: builtins.str) -> None:
        jsii.set(self, "networkMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networks")
    def networks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networks"))

    @networks.setter
    def networks(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "networks", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networksAdvanced")
    def networks_advanced(self) -> typing.List["ContainerNetworksAdvanced"]:
        return typing.cast(typing.List["ContainerNetworksAdvanced"], jsii.get(self, "networksAdvanced"))

    @networks_advanced.setter
    def networks_advanced(
        self,
        value: typing.List["ContainerNetworksAdvanced"],
    ) -> None:
        jsii.set(self, "networksAdvanced", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pidMode")
    def pid_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pidMode"))

    @pid_mode.setter
    def pid_mode(self, value: builtins.str) -> None:
        jsii.set(self, "pidMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.List["ContainerPorts"]:
        return typing.cast(typing.List["ContainerPorts"], jsii.get(self, "ports"))

    @ports.setter
    def ports(self, value: typing.List["ContainerPorts"]) -> None:
        jsii.set(self, "ports", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privileged")
    def privileged(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "privileged"))

    @privileged.setter
    def privileged(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "privileged", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishAllPorts")
    def publish_all_ports(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "publishAllPorts"))

    @publish_all_ports.setter
    def publish_all_ports(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "publishAllPorts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "readOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="removeVolumes")
    def remove_volumes(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "removeVolumes"))

    @remove_volumes.setter
    def remove_volumes(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "removeVolumes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restart")
    def restart(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restart"))

    @restart.setter
    def restart(self, value: builtins.str) -> None:
        jsii.set(self, "restart", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rm")
    def rm(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "rm"))

    @rm.setter
    def rm(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "rm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityOpts")
    def security_opts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityOpts"))

    @security_opts.setter
    def security_opts(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shmSize")
    def shm_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shmSize"))

    @shm_size.setter
    def shm_size(self, value: jsii.Number) -> None:
        jsii.set(self, "shmSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="start")
    def start(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "start"))

    @start.setter
    def start(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "start", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stdinOpen")
    def stdin_open(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "stdinOpen"))

    @stdin_open.setter
    def stdin_open(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "stdinOpen", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageOpts")
    def storage_opts(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "storageOpts"))

    @storage_opts.setter
    def storage_opts(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "storageOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sysctls")
    def sysctls(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "sysctls"))

    @sysctls.setter
    def sysctls(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "sysctls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tmpfs")
    def tmpfs(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tmpfs"))

    @tmpfs.setter
    def tmpfs(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tmpfs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tty")
    def tty(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "tty"))

    @tty.setter
    def tty(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "tty", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ulimit")
    def ulimit(self) -> typing.List["ContainerUlimit"]:
        return typing.cast(typing.List["ContainerUlimit"], jsii.get(self, "ulimit"))

    @ulimit.setter
    def ulimit(self, value: typing.List["ContainerUlimit"]) -> None:
        jsii.set(self, "ulimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="upload")
    def upload(self) -> typing.List["ContainerUpload"]:
        return typing.cast(typing.List["ContainerUpload"], jsii.get(self, "upload"))

    @upload.setter
    def upload(self, value: typing.List["ContainerUpload"]) -> None:
        jsii.set(self, "upload", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernsMode")
    def userns_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernsMode"))

    @userns_mode.setter
    def userns_mode(self, value: builtins.str) -> None:
        jsii.set(self, "usernsMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.List["ContainerVolumes"]:
        return typing.cast(typing.List["ContainerVolumes"], jsii.get(self, "volumes"))

    @volumes.setter
    def volumes(self, value: typing.List["ContainerVolumes"]) -> None:
        jsii.set(self, "volumes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDir")
    def working_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workingDir"))

    @working_dir.setter
    def working_dir(self, value: builtins.str) -> None:
        jsii.set(self, "workingDir", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerCapabilities",
    jsii_struct_bases=[],
    name_mapping={"add": "add", "drop": "drop"},
)
class ContainerCapabilities:
    def __init__(
        self,
        *,
        add: typing.Optional[typing.Sequence[builtins.str]] = None,
        drop: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param add: List of linux capabilities to add. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#add Container#add}
        :param drop: List of linux capabilities to drop. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#drop Container#drop}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if add is not None:
            self._values["add"] = add
        if drop is not None:
            self._values["drop"] = drop

    @builtins.property
    def add(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of linux capabilities to add.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#add Container#add}
        '''
        result = self._values.get("add")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drop(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of linux capabilities to drop.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#drop Container#drop}
        '''
        result = self._values.get("drop")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerCapabilities(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContainerCapabilitiesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ContainerCapabilitiesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAdd")
    def reset_add(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdd", []))

    @jsii.member(jsii_name="resetDrop")
    def reset_drop(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDrop", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addInput")
    def add_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "addInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dropInput")
    def drop_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dropInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="add")
    def add(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "add"))

    @add.setter
    def add(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "add", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="drop")
    def drop(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "drop"))

    @drop.setter
    def drop(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "drop", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ContainerCapabilities]:
        return typing.cast(typing.Optional[ContainerCapabilities], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ContainerCapabilities]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "image": "image",
        "name": "name",
        "attach": "attach",
        "capabilities": "capabilities",
        "command": "command",
        "cpu_set": "cpuSet",
        "cpu_shares": "cpuShares",
        "destroy_grace_seconds": "destroyGraceSeconds",
        "devices": "devices",
        "dns": "dns",
        "dns_opts": "dnsOpts",
        "dns_search": "dnsSearch",
        "domainname": "domainname",
        "entrypoint": "entrypoint",
        "env": "env",
        "group_add": "groupAdd",
        "healthcheck": "healthcheck",
        "host": "host",
        "hostname": "hostname",
        "init": "init",
        "ipc_mode": "ipcMode",
        "labels": "labels",
        "links": "links",
        "log_driver": "logDriver",
        "log_opts": "logOpts",
        "logs": "logs",
        "max_retry_count": "maxRetryCount",
        "memory": "memory",
        "memory_swap": "memorySwap",
        "mounts": "mounts",
        "must_run": "mustRun",
        "network_alias": "networkAlias",
        "network_mode": "networkMode",
        "networks": "networks",
        "networks_advanced": "networksAdvanced",
        "pid_mode": "pidMode",
        "ports": "ports",
        "privileged": "privileged",
        "publish_all_ports": "publishAllPorts",
        "read_only": "readOnly",
        "remove_volumes": "removeVolumes",
        "restart": "restart",
        "rm": "rm",
        "security_opts": "securityOpts",
        "shm_size": "shmSize",
        "start": "start",
        "stdin_open": "stdinOpen",
        "storage_opts": "storageOpts",
        "sysctls": "sysctls",
        "tmpfs": "tmpfs",
        "tty": "tty",
        "ulimit": "ulimit",
        "upload": "upload",
        "user": "user",
        "userns_mode": "usernsMode",
        "volumes": "volumes",
        "working_dir": "workingDir",
    },
)
class ContainerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        image: builtins.str,
        name: builtins.str,
        attach: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        capabilities: typing.Optional[ContainerCapabilities] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        cpu_set: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        destroy_grace_seconds: typing.Optional[jsii.Number] = None,
        devices: typing.Optional[typing.Sequence["ContainerDevices"]] = None,
        dns: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_opts: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_search: typing.Optional[typing.Sequence[builtins.str]] = None,
        domainname: typing.Optional[builtins.str] = None,
        entrypoint: typing.Optional[typing.Sequence[builtins.str]] = None,
        env: typing.Optional[typing.Sequence[builtins.str]] = None,
        group_add: typing.Optional[typing.Sequence[builtins.str]] = None,
        healthcheck: typing.Optional["ContainerHealthcheck"] = None,
        host: typing.Optional[typing.Sequence["ContainerHost"]] = None,
        hostname: typing.Optional[builtins.str] = None,
        init: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ipc_mode: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Sequence["ContainerLabels"]] = None,
        links: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_driver: typing.Optional[builtins.str] = None,
        log_opts: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        logs: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_retry_count: typing.Optional[jsii.Number] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_swap: typing.Optional[jsii.Number] = None,
        mounts: typing.Optional[typing.Sequence["ContainerMounts"]] = None,
        must_run: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        network_alias: typing.Optional[typing.Sequence[builtins.str]] = None,
        network_mode: typing.Optional[builtins.str] = None,
        networks: typing.Optional[typing.Sequence[builtins.str]] = None,
        networks_advanced: typing.Optional[typing.Sequence["ContainerNetworksAdvanced"]] = None,
        pid_mode: typing.Optional[builtins.str] = None,
        ports: typing.Optional[typing.Sequence["ContainerPorts"]] = None,
        privileged: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        publish_all_ports: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        remove_volumes: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        restart: typing.Optional[builtins.str] = None,
        rm: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        security_opts: typing.Optional[typing.Sequence[builtins.str]] = None,
        shm_size: typing.Optional[jsii.Number] = None,
        start: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        stdin_open: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        storage_opts: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        sysctls: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tmpfs: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tty: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ulimit: typing.Optional[typing.Sequence["ContainerUlimit"]] = None,
        upload: typing.Optional[typing.Sequence["ContainerUpload"]] = None,
        user: typing.Optional[builtins.str] = None,
        userns_mode: typing.Optional[builtins.str] = None,
        volumes: typing.Optional[typing.Sequence["ContainerVolumes"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param image: The ID of the image to back this container. The easiest way to get this value is to use the ``docker_image`` resource as is shown in the example. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#image Container#image}
        :param name: The name of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#name Container#name}
        :param attach: If ``true`` attach to the container after its creation and waits the end of its execution. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#attach Container#attach}
        :param capabilities: capabilities block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#capabilities Container#capabilities}
        :param command: The command to use to start the container. For example, to run ``/usr/bin/myprogram -f baz.conf`` set the command to be ``["/usr/bin/myprogram","-","baz.con"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#command Container#command}
        :param cpu_set: A comma-separated list or hyphen-separated range of CPUs a container can use, e.g. ``0-1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#cpu_set Container#cpu_set}
        :param cpu_shares: CPU shares (relative weight) for the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#cpu_shares Container#cpu_shares}
        :param destroy_grace_seconds: If defined will attempt to stop the container before destroying. Container will be destroyed after ``n`` seconds or on successful stop. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#destroy_grace_seconds Container#destroy_grace_seconds}
        :param devices: devices block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#devices Container#devices}
        :param dns: DNS servers to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#dns Container#dns}
        :param dns_opts: DNS options used by the DNS provider(s), see ``resolv.conf`` documentation for valid list of options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#dns_opts Container#dns_opts}
        :param dns_search: DNS search domains that are used when bare unqualified hostnames are used inside of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#dns_search Container#dns_search}
        :param domainname: Domain name of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#domainname Container#domainname}
        :param entrypoint: The command to use as the Entrypoint for the container. The Entrypoint allows you to configure a container to run as an executable. For example, to run ``/usr/bin/myprogram`` when starting a container, set the entrypoint to be ``"/usr/bin/myprogra"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#entrypoint Container#entrypoint}
        :param env: Environment variables to set in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#env Container#env}
        :param group_add: Additional groups for the container user. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#group_add Container#group_add}
        :param healthcheck: healthcheck block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#healthcheck Container#healthcheck}
        :param host: host block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#host Container#host}
        :param hostname: Hostname of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#hostname Container#hostname}
        :param init: Configured whether an init process should be injected for this container. If unset this will default to the ``dockerd`` defaults. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#init Container#init}
        :param ipc_mode: IPC sharing mode for the container. Possible values are: ``none``, ``private``, ``shareable``, ``container:<name|id>`` or ``host``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ipc_mode Container#ipc_mode}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#labels Container#labels}
        :param links: Set of links for link based connectivity between containers that are running on the same host. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#links Container#links}
        :param log_driver: The logging driver to use for the container. Defaults to ``json-file``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#log_driver Container#log_driver}
        :param log_opts: Key/value pairs to use as options for the logging driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#log_opts Container#log_opts}
        :param logs: Save the container logs (``attach`` must be enabled). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#logs Container#logs}
        :param max_retry_count: The maximum amount of times to an attempt a restart when ``restart`` is set to 'on-failure'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#max_retry_count Container#max_retry_count}
        :param memory: The memory limit for the container in MBs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#memory Container#memory}
        :param memory_swap: The total memory limit (memory + swap) for the container in MBs. This setting may compute to ``-1`` after ``terraform apply`` if the target host doesn't support memory swap, when that is the case docker will use a soft limitation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#memory_swap Container#memory_swap}
        :param mounts: mounts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#mounts Container#mounts}
        :param must_run: If ``true``, then the Docker container will be kept running. If ``false``, then as long as the container exists, Terraform assumes it is successful. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#must_run Container#must_run}
        :param network_alias: Set an alias for the container in all specified networks. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#network_alias Container#network_alias}
        :param network_mode: Network mode of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#network_mode Container#network_mode}
        :param networks: ID of the networks in which the container is. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#networks Container#networks}
        :param networks_advanced: networks_advanced block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#networks_advanced Container#networks_advanced}
        :param pid_mode: he PID (Process) Namespace mode for the container. Either ``container:<name|id>`` or ``host``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#pid_mode Container#pid_mode}
        :param ports: ports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ports Container#ports}
        :param privileged: If ``true``, the container runs in privileged mode. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#privileged Container#privileged}
        :param publish_all_ports: Publish all ports of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#publish_all_ports Container#publish_all_ports}
        :param read_only: If ``true``, the container will be started as readonly. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#read_only Container#read_only}
        :param remove_volumes: If ``true``, it will remove anonymous volumes associated with the container. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#remove_volumes Container#remove_volumes}
        :param restart: The restart policy for the container. Must be one of 'no', 'on-failure', 'always', 'unless-stopped'. Defaults to ``no``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#restart Container#restart}
        :param rm: If ``true``, then the container will be automatically removed after his execution. Terraform won't check this container after creation. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#rm Container#rm}
        :param security_opts: List of string values to customize labels for MLS systems, such as SELinux. See https://docs.docker.com/engine/reference/run/#security-configuration. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#security_opts Container#security_opts}
        :param shm_size: Size of ``/dev/shm`` in MBs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#shm_size Container#shm_size}
        :param start: If ``true``, then the Docker container will be started after creation. If ``false``, then the container is only created. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#start Container#start}
        :param stdin_open: If ``true``, keep STDIN open even if not attached (``docker run -i``). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#stdin_open Container#stdin_open}
        :param storage_opts: Key/value pairs for the storage driver options, e.g. ``size``: ``120G``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#storage_opts Container#storage_opts}
        :param sysctls: A map of kernel parameters (sysctls) to set in the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#sysctls Container#sysctls}
        :param tmpfs: A map of container directories which should be replaced by ``tmpfs mounts``, and their corresponding mount options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#tmpfs Container#tmpfs}
        :param tty: If ``true``, allocate a pseudo-tty (``docker run -t``). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#tty Container#tty}
        :param ulimit: ulimit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ulimit Container#ulimit}
        :param upload: upload block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#upload Container#upload}
        :param user: User used for run the first process. Format is ``user`` or ``user:group`` which user and group can be passed literraly or by name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#user Container#user}
        :param userns_mode: Sets the usernamespace mode for the container when usernamespace remapping option is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#userns_mode Container#userns_mode}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#volumes Container#volumes}
        :param working_dir: The working directory for commands to run in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#working_dir Container#working_dir}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(capabilities, dict):
            capabilities = ContainerCapabilities(**capabilities)
        if isinstance(healthcheck, dict):
            healthcheck = ContainerHealthcheck(**healthcheck)
        self._values: typing.Dict[str, typing.Any] = {
            "image": image,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if attach is not None:
            self._values["attach"] = attach
        if capabilities is not None:
            self._values["capabilities"] = capabilities
        if command is not None:
            self._values["command"] = command
        if cpu_set is not None:
            self._values["cpu_set"] = cpu_set
        if cpu_shares is not None:
            self._values["cpu_shares"] = cpu_shares
        if destroy_grace_seconds is not None:
            self._values["destroy_grace_seconds"] = destroy_grace_seconds
        if devices is not None:
            self._values["devices"] = devices
        if dns is not None:
            self._values["dns"] = dns
        if dns_opts is not None:
            self._values["dns_opts"] = dns_opts
        if dns_search is not None:
            self._values["dns_search"] = dns_search
        if domainname is not None:
            self._values["domainname"] = domainname
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if env is not None:
            self._values["env"] = env
        if group_add is not None:
            self._values["group_add"] = group_add
        if healthcheck is not None:
            self._values["healthcheck"] = healthcheck
        if host is not None:
            self._values["host"] = host
        if hostname is not None:
            self._values["hostname"] = hostname
        if init is not None:
            self._values["init"] = init
        if ipc_mode is not None:
            self._values["ipc_mode"] = ipc_mode
        if labels is not None:
            self._values["labels"] = labels
        if links is not None:
            self._values["links"] = links
        if log_driver is not None:
            self._values["log_driver"] = log_driver
        if log_opts is not None:
            self._values["log_opts"] = log_opts
        if logs is not None:
            self._values["logs"] = logs
        if max_retry_count is not None:
            self._values["max_retry_count"] = max_retry_count
        if memory is not None:
            self._values["memory"] = memory
        if memory_swap is not None:
            self._values["memory_swap"] = memory_swap
        if mounts is not None:
            self._values["mounts"] = mounts
        if must_run is not None:
            self._values["must_run"] = must_run
        if network_alias is not None:
            self._values["network_alias"] = network_alias
        if network_mode is not None:
            self._values["network_mode"] = network_mode
        if networks is not None:
            self._values["networks"] = networks
        if networks_advanced is not None:
            self._values["networks_advanced"] = networks_advanced
        if pid_mode is not None:
            self._values["pid_mode"] = pid_mode
        if ports is not None:
            self._values["ports"] = ports
        if privileged is not None:
            self._values["privileged"] = privileged
        if publish_all_ports is not None:
            self._values["publish_all_ports"] = publish_all_ports
        if read_only is not None:
            self._values["read_only"] = read_only
        if remove_volumes is not None:
            self._values["remove_volumes"] = remove_volumes
        if restart is not None:
            self._values["restart"] = restart
        if rm is not None:
            self._values["rm"] = rm
        if security_opts is not None:
            self._values["security_opts"] = security_opts
        if shm_size is not None:
            self._values["shm_size"] = shm_size
        if start is not None:
            self._values["start"] = start
        if stdin_open is not None:
            self._values["stdin_open"] = stdin_open
        if storage_opts is not None:
            self._values["storage_opts"] = storage_opts
        if sysctls is not None:
            self._values["sysctls"] = sysctls
        if tmpfs is not None:
            self._values["tmpfs"] = tmpfs
        if tty is not None:
            self._values["tty"] = tty
        if ulimit is not None:
            self._values["ulimit"] = ulimit
        if upload is not None:
            self._values["upload"] = upload
        if user is not None:
            self._values["user"] = user
        if userns_mode is not None:
            self._values["userns_mode"] = userns_mode
        if volumes is not None:
            self._values["volumes"] = volumes
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
    def image(self) -> builtins.str:
        '''The ID of the image to back this container.

        The easiest way to get this value is to use the ``docker_image`` resource as is shown in the example.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#image Container#image}
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#name Container#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attach(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true`` attach to the container after its creation and waits the end of its execution. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#attach Container#attach}
        '''
        result = self._values.get("attach")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def capabilities(self) -> typing.Optional[ContainerCapabilities]:
        '''capabilities block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#capabilities Container#capabilities}
        '''
        result = self._values.get("capabilities")
        return typing.cast(typing.Optional[ContainerCapabilities], result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The command to use to start the container.

        For example, to run ``/usr/bin/myprogram -f baz.conf`` set the command to be ``["/usr/bin/myprogram","-","baz.con"]``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#command Container#command}
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cpu_set(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list or hyphen-separated range of CPUs a container can use, e.g. ``0-1``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#cpu_set Container#cpu_set}
        '''
        result = self._values.get("cpu_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_shares(self) -> typing.Optional[jsii.Number]:
        '''CPU shares (relative weight) for the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#cpu_shares Container#cpu_shares}
        '''
        result = self._values.get("cpu_shares")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def destroy_grace_seconds(self) -> typing.Optional[jsii.Number]:
        '''If defined will attempt to stop the container before destroying.

        Container will be destroyed after ``n`` seconds or on successful stop.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#destroy_grace_seconds Container#destroy_grace_seconds}
        '''
        result = self._values.get("destroy_grace_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def devices(self) -> typing.Optional[typing.List["ContainerDevices"]]:
        '''devices block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#devices Container#devices}
        '''
        result = self._values.get("devices")
        return typing.cast(typing.Optional[typing.List["ContainerDevices"]], result)

    @builtins.property
    def dns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''DNS servers to use.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#dns Container#dns}
        '''
        result = self._values.get("dns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dns_opts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''DNS options used by the DNS provider(s), see ``resolv.conf`` documentation for valid list of options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#dns_opts Container#dns_opts}
        '''
        result = self._values.get("dns_opts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dns_search(self) -> typing.Optional[typing.List[builtins.str]]:
        '''DNS search domains that are used when bare unqualified hostnames are used inside of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#dns_search Container#dns_search}
        '''
        result = self._values.get("dns_search")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def domainname(self) -> typing.Optional[builtins.str]:
        '''Domain name of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#domainname Container#domainname}
        '''
        result = self._values.get("domainname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The command to use as the Entrypoint for the container.

        The Entrypoint allows you to configure a container to run as an executable. For example, to run ``/usr/bin/myprogram`` when starting a container, set the entrypoint to be ``"/usr/bin/myprogra"]``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#entrypoint Container#entrypoint}
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Environment variables to set in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#env Container#env}
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def group_add(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional groups for the container user.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#group_add Container#group_add}
        '''
        result = self._values.get("group_add")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def healthcheck(self) -> typing.Optional["ContainerHealthcheck"]:
        '''healthcheck block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#healthcheck Container#healthcheck}
        '''
        result = self._values.get("healthcheck")
        return typing.cast(typing.Optional["ContainerHealthcheck"], result)

    @builtins.property
    def host(self) -> typing.Optional[typing.List["ContainerHost"]]:
        '''host block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#host Container#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[typing.List["ContainerHost"]], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''Hostname of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#hostname Container#hostname}
        '''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def init(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Configured whether an init process should be injected for this container.

        If unset this will default to the ``dockerd`` defaults.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#init Container#init}
        '''
        result = self._values.get("init")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ipc_mode(self) -> typing.Optional[builtins.str]:
        '''IPC sharing mode for the container. Possible values are: ``none``, ``private``, ``shareable``, ``container:<name|id>`` or ``host``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ipc_mode Container#ipc_mode}
        '''
        result = self._values.get("ipc_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["ContainerLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#labels Container#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ContainerLabels"]], result)

    @builtins.property
    def links(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of links for link based connectivity between containers that are running on the same host.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#links Container#links}
        '''
        result = self._values.get("links")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def log_driver(self) -> typing.Optional[builtins.str]:
        '''The logging driver to use for the container. Defaults to ``json-file``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#log_driver Container#log_driver}
        '''
        result = self._values.get("log_driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_opts(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Key/value pairs to use as options for the logging driver.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#log_opts Container#log_opts}
        '''
        result = self._values.get("log_opts")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def logs(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Save the container logs (``attach`` must be enabled). Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#logs Container#logs}
        '''
        result = self._values.get("logs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def max_retry_count(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of times to an attempt a restart when ``restart`` is set to 'on-failure'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#max_retry_count Container#max_retry_count}
        '''
        result = self._values.get("max_retry_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory(self) -> typing.Optional[jsii.Number]:
        '''The memory limit for the container in MBs.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#memory Container#memory}
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_swap(self) -> typing.Optional[jsii.Number]:
        '''The total memory limit (memory + swap) for the container in MBs.

        This setting may compute to ``-1`` after ``terraform apply`` if the target host doesn't support memory swap, when that is the case docker will use a soft limitation.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#memory_swap Container#memory_swap}
        '''
        result = self._values.get("memory_swap")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mounts(self) -> typing.Optional[typing.List["ContainerMounts"]]:
        '''mounts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#mounts Container#mounts}
        '''
        result = self._values.get("mounts")
        return typing.cast(typing.Optional[typing.List["ContainerMounts"]], result)

    @builtins.property
    def must_run(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, then the Docker container will be kept running.

        If ``false``, then as long as the container exists, Terraform assumes it is successful. Defaults to ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#must_run Container#must_run}
        '''
        result = self._values.get("must_run")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def network_alias(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set an alias for the container in all specified networks.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#network_alias Container#network_alias}
        '''
        result = self._values.get("network_alias")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def network_mode(self) -> typing.Optional[builtins.str]:
        '''Network mode of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#network_mode Container#network_mode}
        '''
        result = self._values.get("network_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def networks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''ID of the networks in which the container is.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#networks Container#networks}
        '''
        result = self._values.get("networks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def networks_advanced(
        self,
    ) -> typing.Optional[typing.List["ContainerNetworksAdvanced"]]:
        '''networks_advanced block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#networks_advanced Container#networks_advanced}
        '''
        result = self._values.get("networks_advanced")
        return typing.cast(typing.Optional[typing.List["ContainerNetworksAdvanced"]], result)

    @builtins.property
    def pid_mode(self) -> typing.Optional[builtins.str]:
        '''he PID (Process) Namespace mode for the container. Either ``container:<name|id>`` or ``host``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#pid_mode Container#pid_mode}
        '''
        result = self._values.get("pid_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List["ContainerPorts"]]:
        '''ports block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ports Container#ports}
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List["ContainerPorts"]], result)

    @builtins.property
    def privileged(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, the container runs in privileged mode.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#privileged Container#privileged}
        '''
        result = self._values.get("privileged")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def publish_all_ports(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Publish all ports of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#publish_all_ports Container#publish_all_ports}
        '''
        result = self._values.get("publish_all_ports")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, the container will be started as readonly. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#read_only Container#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def remove_volumes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, it will remove anonymous volumes associated with the container. Defaults to ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#remove_volumes Container#remove_volumes}
        '''
        result = self._values.get("remove_volumes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def restart(self) -> typing.Optional[builtins.str]:
        '''The restart policy for the container. Must be one of 'no', 'on-failure', 'always', 'unless-stopped'. Defaults to ``no``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#restart Container#restart}
        '''
        result = self._values.get("restart")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rm(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, then the container will be automatically removed after his execution.

        Terraform won't check this container after creation. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#rm Container#rm}
        '''
        result = self._values.get("rm")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def security_opts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of string values to customize labels for MLS systems, such as SELinux. See https://docs.docker.com/engine/reference/run/#security-configuration.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#security_opts Container#security_opts}
        '''
        result = self._values.get("security_opts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def shm_size(self) -> typing.Optional[jsii.Number]:
        '''Size of ``/dev/shm`` in MBs.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#shm_size Container#shm_size}
        '''
        result = self._values.get("shm_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, then the Docker container will be started after creation.

        If ``false``, then the container is only created. Defaults to ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#start Container#start}
        '''
        result = self._values.get("start")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def stdin_open(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, keep STDIN open even if not attached (``docker run -i``). Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#stdin_open Container#stdin_open}
        '''
        result = self._values.get("stdin_open")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def storage_opts(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Key/value pairs for the storage driver options, e.g. ``size``: ``120G``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#storage_opts Container#storage_opts}
        '''
        result = self._values.get("storage_opts")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def sysctls(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''A map of kernel parameters (sysctls) to set in the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#sysctls Container#sysctls}
        '''
        result = self._values.get("sysctls")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tmpfs(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''A map of container directories which should be replaced by ``tmpfs mounts``, and their corresponding mount options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#tmpfs Container#tmpfs}
        '''
        result = self._values.get("tmpfs")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tty(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, allocate a pseudo-tty (``docker run -t``). Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#tty Container#tty}
        '''
        result = self._values.get("tty")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ulimit(self) -> typing.Optional[typing.List["ContainerUlimit"]]:
        '''ulimit block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ulimit Container#ulimit}
        '''
        result = self._values.get("ulimit")
        return typing.cast(typing.Optional[typing.List["ContainerUlimit"]], result)

    @builtins.property
    def upload(self) -> typing.Optional[typing.List["ContainerUpload"]]:
        '''upload block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#upload Container#upload}
        '''
        result = self._values.get("upload")
        return typing.cast(typing.Optional[typing.List["ContainerUpload"]], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''User used for run the first process.

        Format is ``user`` or ``user:group`` which user and group can be passed literraly or by name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#user Container#user}
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def userns_mode(self) -> typing.Optional[builtins.str]:
        '''Sets the usernamespace mode for the container when usernamespace remapping option is enabled.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#userns_mode Container#userns_mode}
        '''
        result = self._values.get("userns_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List["ContainerVolumes"]]:
        '''volumes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#volumes Container#volumes}
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List["ContainerVolumes"]], result)

    @builtins.property
    def working_dir(self) -> typing.Optional[builtins.str]:
        '''The working directory for commands to run in.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#working_dir Container#working_dir}
        '''
        result = self._values.get("working_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerDevices",
    jsii_struct_bases=[],
    name_mapping={
        "host_path": "hostPath",
        "container_path": "containerPath",
        "permissions": "permissions",
    },
)
class ContainerDevices:
    def __init__(
        self,
        *,
        host_path: builtins.str,
        container_path: typing.Optional[builtins.str] = None,
        permissions: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host_path: The path on the host where the device is located. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#host_path Container#host_path}
        :param container_path: The path in the container where the device will be bound. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#container_path Container#container_path}
        :param permissions: The cgroup permissions given to the container to access the device. Defaults to ``rwm``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#permissions Container#permissions}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "host_path": host_path,
        }
        if container_path is not None:
            self._values["container_path"] = container_path
        if permissions is not None:
            self._values["permissions"] = permissions

    @builtins.property
    def host_path(self) -> builtins.str:
        '''The path on the host where the device is located.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#host_path Container#host_path}
        '''
        result = self._values.get("host_path")
        assert result is not None, "Required property 'host_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_path(self) -> typing.Optional[builtins.str]:
        '''The path in the container where the device will be bound.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#container_path Container#container_path}
        '''
        result = self._values.get("container_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions(self) -> typing.Optional[builtins.str]:
        '''The cgroup permissions given to the container to access the device. Defaults to ``rwm``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#permissions Container#permissions}
        '''
        result = self._values.get("permissions")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerDevices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerHealthcheck",
    jsii_struct_bases=[],
    name_mapping={
        "test": "test",
        "interval": "interval",
        "retries": "retries",
        "start_period": "startPeriod",
        "timeout": "timeout",
    },
)
class ContainerHealthcheck:
    def __init__(
        self,
        *,
        test: typing.Sequence[builtins.str],
        interval: typing.Optional[builtins.str] = None,
        retries: typing.Optional[jsii.Number] = None,
        start_period: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param test: Command to run to check health. For example, to run ``curl -f localhost/health`` set the command to be ``["CMD", "curl", "-f", "localhost/health"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#test Container#test}
        :param interval: Time between running the check (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#interval Container#interval}
        :param retries: Consecutive failures needed to report unhealthy. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#retries Container#retries}
        :param start_period: Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#start_period Container#start_period}
        :param timeout: Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#timeout Container#timeout}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "test": test,
        }
        if interval is not None:
            self._values["interval"] = interval
        if retries is not None:
            self._values["retries"] = retries
        if start_period is not None:
            self._values["start_period"] = start_period
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def test(self) -> typing.List[builtins.str]:
        '''Command to run to check health.

        For example, to run ``curl -f localhost/health`` set the command to be ``["CMD", "curl", "-f", "localhost/health"]``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#test Container#test}
        '''
        result = self._values.get("test")
        assert result is not None, "Required property 'test' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def interval(self) -> typing.Optional[builtins.str]:
        '''Time between running the check (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#interval Container#interval}
        '''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retries(self) -> typing.Optional[jsii.Number]:
        '''Consecutive failures needed to report unhealthy. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#retries Container#retries}
        '''
        result = self._values.get("retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_period(self) -> typing.Optional[builtins.str]:
        '''Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#start_period Container#start_period}
        '''
        result = self._values.get("start_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#timeout Container#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerHealthcheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContainerHealthcheckOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ContainerHealthcheckOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetRetries")
    def reset_retries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetries", []))

    @jsii.member(jsii_name="resetStartPeriod")
    def reset_start_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartPeriod", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retriesInput")
    def retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retriesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startPeriodInput")
    def start_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="testInput")
    def test_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "testInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: builtins.str) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retries")
    def retries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retries"))

    @retries.setter
    def retries(self, value: jsii.Number) -> None:
        jsii.set(self, "retries", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startPeriod")
    def start_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startPeriod"))

    @start_period.setter
    def start_period(self, value: builtins.str) -> None:
        jsii.set(self, "startPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="test")
    def test(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "test"))

    @test.setter
    def test(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "test", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: builtins.str) -> None:
        jsii.set(self, "timeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ContainerHealthcheck]:
        return typing.cast(typing.Optional[ContainerHealthcheck], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ContainerHealthcheck]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerHost",
    jsii_struct_bases=[],
    name_mapping={"host": "host", "ip": "ip"},
)
class ContainerHost:
    def __init__(self, *, host: builtins.str, ip: builtins.str) -> None:
        '''
        :param host: Hostname to add. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#host Container#host}
        :param ip: IP address this hostname should resolve to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ip Container#ip}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "host": host,
            "ip": ip,
        }

    @builtins.property
    def host(self) -> builtins.str:
        '''Hostname to add.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#host Container#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip(self) -> builtins.str:
        '''IP address this hostname should resolve to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ip Container#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerHost(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ContainerLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#label Container#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#value Container#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#label Container#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#value Container#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMounts",
    jsii_struct_bases=[],
    name_mapping={
        "target": "target",
        "type": "type",
        "bind_options": "bindOptions",
        "read_only": "readOnly",
        "source": "source",
        "tmpfs_options": "tmpfsOptions",
        "volume_options": "volumeOptions",
    },
)
class ContainerMounts:
    def __init__(
        self,
        *,
        target: builtins.str,
        type: builtins.str,
        bind_options: typing.Optional["ContainerMountsBindOptions"] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        source: typing.Optional[builtins.str] = None,
        tmpfs_options: typing.Optional["ContainerMountsTmpfsOptions"] = None,
        volume_options: typing.Optional["ContainerMountsVolumeOptions"] = None,
    ) -> None:
        '''
        :param target: Container path. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#target Container#target}
        :param type: The mount type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#type Container#type}
        :param bind_options: bind_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#bind_options Container#bind_options}
        :param read_only: Whether the mount should be read-only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#read_only Container#read_only}
        :param source: Mount source (e.g. a volume name, a host path). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#source Container#source}
        :param tmpfs_options: tmpfs_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#tmpfs_options Container#tmpfs_options}
        :param volume_options: volume_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#volume_options Container#volume_options}
        '''
        if isinstance(bind_options, dict):
            bind_options = ContainerMountsBindOptions(**bind_options)
        if isinstance(tmpfs_options, dict):
            tmpfs_options = ContainerMountsTmpfsOptions(**tmpfs_options)
        if isinstance(volume_options, dict):
            volume_options = ContainerMountsVolumeOptions(**volume_options)
        self._values: typing.Dict[str, typing.Any] = {
            "target": target,
            "type": type,
        }
        if bind_options is not None:
            self._values["bind_options"] = bind_options
        if read_only is not None:
            self._values["read_only"] = read_only
        if source is not None:
            self._values["source"] = source
        if tmpfs_options is not None:
            self._values["tmpfs_options"] = tmpfs_options
        if volume_options is not None:
            self._values["volume_options"] = volume_options

    @builtins.property
    def target(self) -> builtins.str:
        '''Container path.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#target Container#target}
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The mount type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#type Container#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bind_options(self) -> typing.Optional["ContainerMountsBindOptions"]:
        '''bind_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#bind_options Container#bind_options}
        '''
        result = self._values.get("bind_options")
        return typing.cast(typing.Optional["ContainerMountsBindOptions"], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether the mount should be read-only.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#read_only Container#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Mount source (e.g. a volume name, a host path).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#source Container#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tmpfs_options(self) -> typing.Optional["ContainerMountsTmpfsOptions"]:
        '''tmpfs_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#tmpfs_options Container#tmpfs_options}
        '''
        result = self._values.get("tmpfs_options")
        return typing.cast(typing.Optional["ContainerMountsTmpfsOptions"], result)

    @builtins.property
    def volume_options(self) -> typing.Optional["ContainerMountsVolumeOptions"]:
        '''volume_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#volume_options Container#volume_options}
        '''
        result = self._values.get("volume_options")
        return typing.cast(typing.Optional["ContainerMountsVolumeOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMounts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMountsBindOptions",
    jsii_struct_bases=[],
    name_mapping={"propagation": "propagation"},
)
class ContainerMountsBindOptions:
    def __init__(self, *, propagation: typing.Optional[builtins.str] = None) -> None:
        '''
        :param propagation: A propagation mode with the value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#propagation Container#propagation}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if propagation is not None:
            self._values["propagation"] = propagation

    @builtins.property
    def propagation(self) -> typing.Optional[builtins.str]:
        '''A propagation mode with the value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#propagation Container#propagation}
        '''
        result = self._values.get("propagation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMountsBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContainerMountsBindOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ContainerMountsBindOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetPropagation")
    def reset_propagation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPropagation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propagationInput")
    def propagation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "propagationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propagation")
    def propagation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "propagation"))

    @propagation.setter
    def propagation(self, value: builtins.str) -> None:
        jsii.set(self, "propagation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ContainerMountsBindOptions]:
        return typing.cast(typing.Optional[ContainerMountsBindOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ContainerMountsBindOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMountsTmpfsOptions",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "size_bytes": "sizeBytes"},
)
class ContainerMountsTmpfsOptions:
    def __init__(
        self,
        *,
        mode: typing.Optional[jsii.Number] = None,
        size_bytes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mode: The permission mode for the tmpfs mount in an integer. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#mode Container#mode}
        :param size_bytes: The size for the tmpfs mount in bytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#size_bytes Container#size_bytes}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if size_bytes is not None:
            self._values["size_bytes"] = size_bytes

    @builtins.property
    def mode(self) -> typing.Optional[jsii.Number]:
        '''The permission mode for the tmpfs mount in an integer.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#mode Container#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def size_bytes(self) -> typing.Optional[jsii.Number]:
        '''The size for the tmpfs mount in bytes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#size_bytes Container#size_bytes}
        '''
        result = self._values.get("size_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMountsTmpfsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContainerMountsTmpfsOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ContainerMountsTmpfsOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetSizeBytes")
    def reset_size_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSizeBytes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeBytesInput")
    def size_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeBytesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: jsii.Number) -> None:
        jsii.set(self, "mode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeBytes")
    def size_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeBytes"))

    @size_bytes.setter
    def size_bytes(self, value: jsii.Number) -> None:
        jsii.set(self, "sizeBytes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ContainerMountsTmpfsOptions]:
        return typing.cast(typing.Optional[ContainerMountsTmpfsOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ContainerMountsTmpfsOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMountsVolumeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "driver_name": "driverName",
        "driver_options": "driverOptions",
        "labels": "labels",
        "no_copy": "noCopy",
    },
)
class ContainerMountsVolumeOptions:
    def __init__(
        self,
        *,
        driver_name: typing.Optional[builtins.str] = None,
        driver_options: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        labels: typing.Optional[typing.Sequence["ContainerMountsVolumeOptionsLabels"]] = None,
        no_copy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param driver_name: Name of the driver to use to create the volume. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#driver_name Container#driver_name}
        :param driver_options: key/value map of driver specific options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#driver_options Container#driver_options}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#labels Container#labels}
        :param no_copy: Populate volume with data from the target. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#no_copy Container#no_copy}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if driver_name is not None:
            self._values["driver_name"] = driver_name
        if driver_options is not None:
            self._values["driver_options"] = driver_options
        if labels is not None:
            self._values["labels"] = labels
        if no_copy is not None:
            self._values["no_copy"] = no_copy

    @builtins.property
    def driver_name(self) -> typing.Optional[builtins.str]:
        '''Name of the driver to use to create the volume.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#driver_name Container#driver_name}
        '''
        result = self._values.get("driver_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def driver_options(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''key/value map of driver specific options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#driver_options Container#driver_options}
        '''
        result = self._values.get("driver_options")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.List["ContainerMountsVolumeOptionsLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#labels Container#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ContainerMountsVolumeOptionsLabels"]], result)

    @builtins.property
    def no_copy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Populate volume with data from the target.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#no_copy Container#no_copy}
        '''
        result = self._values.get("no_copy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMountsVolumeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMountsVolumeOptionsLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ContainerMountsVolumeOptionsLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#label Container#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#value Container#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#label Container#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#value Container#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMountsVolumeOptionsLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContainerMountsVolumeOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ContainerMountsVolumeOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetDriverName")
    def reset_driver_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverName", []))

    @jsii.member(jsii_name="resetDriverOptions")
    def reset_driver_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverOptions", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetNoCopy")
    def reset_no_copy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoCopy", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverNameInput")
    def driver_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverOptionsInput")
    def driver_options_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "driverOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.List[ContainerMountsVolumeOptionsLabels]]:
        return typing.cast(typing.Optional[typing.List[ContainerMountsVolumeOptionsLabels]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noCopyInput")
    def no_copy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noCopyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverName")
    def driver_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driverName"))

    @driver_name.setter
    def driver_name(self, value: builtins.str) -> None:
        jsii.set(self, "driverName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverOptions")
    def driver_options(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "driverOptions"))

    @driver_options.setter
    def driver_options(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "driverOptions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List[ContainerMountsVolumeOptionsLabels]:
        return typing.cast(typing.List[ContainerMountsVolumeOptionsLabels], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List[ContainerMountsVolumeOptionsLabels]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noCopy")
    def no_copy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noCopy"))

    @no_copy.setter
    def no_copy(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "noCopy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ContainerMountsVolumeOptions]:
        return typing.cast(typing.Optional[ContainerMountsVolumeOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ContainerMountsVolumeOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ContainerNetworkData(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ContainerNetworkData",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalIpv6Address")
    def global_ipv6_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalIpv6Address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalIpv6PrefixLength")
    def global_ipv6_prefix_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "globalIpv6PrefixLength"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipPrefixLength")
    def ip_prefix_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ipPrefixLength"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipv6Gateway")
    def ipv6_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Gateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkName")
    def network_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkName"))


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerNetworksAdvanced",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "aliases": "aliases",
        "ipv4_address": "ipv4Address",
        "ipv6_address": "ipv6Address",
    },
)
class ContainerNetworksAdvanced:
    def __init__(
        self,
        *,
        name: builtins.str,
        aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
        ipv4_address: typing.Optional[builtins.str] = None,
        ipv6_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#name Container#name}
        :param aliases: The network aliases of the container in the specific network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#aliases Container#aliases}
        :param ipv4_address: The IPV4 address of the container in the specific network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ipv4_address Container#ipv4_address}
        :param ipv6_address: The IPV6 address of the container in the specific network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ipv6_address Container#ipv6_address}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if aliases is not None:
            self._values["aliases"] = aliases
        if ipv4_address is not None:
            self._values["ipv4_address"] = ipv4_address
        if ipv6_address is not None:
            self._values["ipv6_address"] = ipv6_address

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#name Container#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aliases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The network aliases of the container in the specific network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#aliases Container#aliases}
        '''
        result = self._values.get("aliases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ipv4_address(self) -> typing.Optional[builtins.str]:
        '''The IPV4 address of the container in the specific network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ipv4_address Container#ipv4_address}
        '''
        result = self._values.get("ipv4_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_address(self) -> typing.Optional[builtins.str]:
        '''The IPV6 address of the container in the specific network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ipv6_address Container#ipv6_address}
        '''
        result = self._values.get("ipv6_address")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerNetworksAdvanced(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerPorts",
    jsii_struct_bases=[],
    name_mapping={
        "internal": "internal",
        "external": "external",
        "ip": "ip",
        "protocol": "protocol",
    },
)
class ContainerPorts:
    def __init__(
        self,
        *,
        internal: jsii.Number,
        external: typing.Optional[jsii.Number] = None,
        ip: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param internal: Port within the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#internal Container#internal}
        :param external: Port exposed out of the container. If not given a free random port ``>= 32768`` will be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#external Container#external}
        :param ip: IP address/mask that can access this port. Defaults to ``0.0.0.0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ip Container#ip}
        :param protocol: Protocol that can be used over this port. Defaults to ``tcp``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#protocol Container#protocol}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "internal": internal,
        }
        if external is not None:
            self._values["external"] = external
        if ip is not None:
            self._values["ip"] = ip
        if protocol is not None:
            self._values["protocol"] = protocol

    @builtins.property
    def internal(self) -> jsii.Number:
        '''Port within the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#internal Container#internal}
        '''
        result = self._values.get("internal")
        assert result is not None, "Required property 'internal' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def external(self) -> typing.Optional[jsii.Number]:
        '''Port exposed out of the container. If not given a free random port ``>= 32768`` will be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#external Container#external}
        '''
        result = self._values.get("external")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ip(self) -> typing.Optional[builtins.str]:
        '''IP address/mask that can access this port. Defaults to ``0.0.0.0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#ip Container#ip}
        '''
        result = self._values.get("ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Protocol that can be used over this port. Defaults to ``tcp``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#protocol Container#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerPorts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerUlimit",
    jsii_struct_bases=[],
    name_mapping={"hard": "hard", "name": "name", "soft": "soft"},
)
class ContainerUlimit:
    def __init__(
        self,
        *,
        hard: jsii.Number,
        name: builtins.str,
        soft: jsii.Number,
    ) -> None:
        '''
        :param hard: The hard limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#hard Container#hard}
        :param name: The name of the ulimit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#name Container#name}
        :param soft: The soft limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#soft Container#soft}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hard": hard,
            "name": name,
            "soft": soft,
        }

    @builtins.property
    def hard(self) -> jsii.Number:
        '''The hard limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#hard Container#hard}
        '''
        result = self._values.get("hard")
        assert result is not None, "Required property 'hard' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the ulimit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#name Container#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def soft(self) -> jsii.Number:
        '''The soft limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#soft Container#soft}
        '''
        result = self._values.get("soft")
        assert result is not None, "Required property 'soft' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerUlimit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerUpload",
    jsii_struct_bases=[],
    name_mapping={
        "file": "file",
        "content": "content",
        "content_base64": "contentBase64",
        "executable": "executable",
        "source": "source",
        "source_hash": "sourceHash",
    },
)
class ContainerUpload:
    def __init__(
        self,
        *,
        file: builtins.str,
        content: typing.Optional[builtins.str] = None,
        content_base64: typing.Optional[builtins.str] = None,
        executable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        source: typing.Optional[builtins.str] = None,
        source_hash: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file: Path to the file in the container where is upload goes to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#file Container#file}
        :param content: Literal string value to use as the object content, which will be uploaded as UTF-8-encoded text. Conflicts with ``content_base64`` & ``source`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#content Container#content}
        :param content_base64: Base64-encoded data that will be decoded and uploaded as raw bytes for the object content. This allows safely uploading non-UTF8 binary data, but is recommended only for larger binary content such as the result of the ``base64encode`` interpolation function. See `here <https://github.com/terraform-providers/terraform-provider-docker/issues/48#issuecomment-374174588>`_ for the reason. Conflicts with ``content`` & ``source`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#content_base64 Container#content_base64}
        :param executable: If ``true``, the file will be uploaded with user executable permission. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#executable Container#executable}
        :param source: A filename that references a file which will be uploaded as the object content. This allows for large file uploads that do not get stored in state. Conflicts with ``content`` & ``content_base64`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#source Container#source}
        :param source_hash: If using ``source``, this will force an update if the file content has updated but the filename has not. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#source_hash Container#source_hash}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "file": file,
        }
        if content is not None:
            self._values["content"] = content
        if content_base64 is not None:
            self._values["content_base64"] = content_base64
        if executable is not None:
            self._values["executable"] = executable
        if source is not None:
            self._values["source"] = source
        if source_hash is not None:
            self._values["source_hash"] = source_hash

    @builtins.property
    def file(self) -> builtins.str:
        '''Path to the file in the container where is upload goes to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#file Container#file}
        '''
        result = self._values.get("file")
        assert result is not None, "Required property 'file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content(self) -> typing.Optional[builtins.str]:
        '''Literal string value to use as the object content, which will be uploaded as UTF-8-encoded text.

        Conflicts with ``content_base64`` & ``source``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#content Container#content}
        '''
        result = self._values.get("content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_base64(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded data that will be decoded and uploaded as raw bytes for the object content.

        This allows safely uploading non-UTF8 binary data, but is recommended only for larger binary content such as the result of the ``base64encode`` interpolation function. See `here <https://github.com/terraform-providers/terraform-provider-docker/issues/48#issuecomment-374174588>`_ for the reason. Conflicts with ``content`` & ``source``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#content_base64 Container#content_base64}
        '''
        result = self._values.get("content_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def executable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, the file will be uploaded with user executable permission. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#executable Container#executable}
        '''
        result = self._values.get("executable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''A filename that references a file which will be uploaded as the object content.

        This allows for large file uploads that do not get stored in state. Conflicts with ``content`` & ``content_base64``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#source Container#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_hash(self) -> typing.Optional[builtins.str]:
        '''If using ``source``, this will force an update if the file content has updated but the filename has not.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#source_hash Container#source_hash}
        '''
        result = self._values.get("source_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerUpload(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerVolumes",
    jsii_struct_bases=[],
    name_mapping={
        "container_path": "containerPath",
        "from_container": "fromContainer",
        "host_path": "hostPath",
        "read_only": "readOnly",
        "volume_name": "volumeName",
    },
)
class ContainerVolumes:
    def __init__(
        self,
        *,
        container_path: typing.Optional[builtins.str] = None,
        from_container: typing.Optional[builtins.str] = None,
        host_path: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        volume_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param container_path: The path in the container where the volume will be mounted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#container_path Container#container_path}
        :param from_container: The container where the volume is coming from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#from_container Container#from_container}
        :param host_path: The path on the host where the volume is coming from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#host_path Container#host_path}
        :param read_only: If ``true``, this volume will be readonly. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#read_only Container#read_only}
        :param volume_name: The name of the docker volume which should be mounted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#volume_name Container#volume_name}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if container_path is not None:
            self._values["container_path"] = container_path
        if from_container is not None:
            self._values["from_container"] = from_container
        if host_path is not None:
            self._values["host_path"] = host_path
        if read_only is not None:
            self._values["read_only"] = read_only
        if volume_name is not None:
            self._values["volume_name"] = volume_name

    @builtins.property
    def container_path(self) -> typing.Optional[builtins.str]:
        '''The path in the container where the volume will be mounted.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#container_path Container#container_path}
        '''
        result = self._values.get("container_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_container(self) -> typing.Optional[builtins.str]:
        '''The container where the volume is coming from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#from_container Container#from_container}
        '''
        result = self._values.get("from_container")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host_path(self) -> typing.Optional[builtins.str]:
        '''The path on the host where the volume is coming from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#host_path Container#host_path}
        '''
        result = self._values.get("host_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, this volume will be readonly. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#read_only Container#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def volume_name(self) -> typing.Optional[builtins.str]:
        '''The name of the docker volume which should be mounted.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container#volume_name Container#volume_name}
        '''
        result = self._values.get("volume_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerVolumes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDockerImage(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerImage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/d/image docker_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/d/image docker_image} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker image, including any tags or SHA256 repo digests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/image#name DataDockerImage#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataDockerImageConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="repoDigest")
    def repo_digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoDigest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DataDockerImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataDockerImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker image, including any tags or SHA256 repo digests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/image#name DataDockerImage#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

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
    def name(self) -> builtins.str:
        '''The name of the Docker image, including any tags or SHA256 repo digests.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/image#name DataDockerImage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDockerImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDockerNetwork(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerNetwork",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/d/network docker_network}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/d/network docker_network} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/network#name DataDockerNetwork#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataDockerNetworkConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="ipamConfig")
    def ipam_config(self, index: builtins.str) -> "DataDockerNetworkIpamConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataDockerNetworkIpamConfig", jsii.invoke(self, "ipamConfig", [index]))

    @jsii.member(jsii_name="options")
    def options(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "options", [key]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driver")
    def driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driver"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internal")
    def internal(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "internal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DataDockerNetworkConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataDockerNetworkConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/network#name DataDockerNetwork#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

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
    def name(self) -> builtins.str:
        '''The name of the Docker network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/network#name DataDockerNetwork#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDockerNetworkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDockerNetworkIpamConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerNetworkIpamConfig",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auxAddress")
    def aux_address(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "auxAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipRange")
    def ip_range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipRange"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnet")
    def subnet(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnet"))


class DataDockerPlugin(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerPlugin",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/d/plugin docker_plugin}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/d/plugin docker_plugin} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: The alias of the Docker plugin. If the tag is omitted, ``:latest`` is complemented to the attribute value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin#alias DataDockerPlugin#alias}
        :param id: The ID of the plugin, which has precedence over the ``alias`` of both are given. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin#id DataDockerPlugin#id}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataDockerPluginConfig(
            alias=alias,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "enabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "env"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantAllPermissions")
    def grant_all_permissions(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "grantAllPermissions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginReference")
    def plugin_reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: builtins.str) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DataDockerPluginConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "alias": "alias",
        "id": "id",
    },
)
class DataDockerPluginConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        alias: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param alias: The alias of the Docker plugin. If the tag is omitted, ``:latest`` is complemented to the attribute value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin#alias DataDockerPlugin#alias}
        :param id: The ID of the plugin, which has precedence over the ``alias`` of both are given. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin#id DataDockerPlugin#id}
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
        if alias is not None:
            self._values["alias"] = alias
        if id is not None:
            self._values["id"] = id

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
    def alias(self) -> typing.Optional[builtins.str]:
        '''The alias of the Docker plugin. If the tag is omitted, ``:latest`` is complemented to the attribute value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin#alias DataDockerPlugin#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''The ID of the plugin, which has precedence over the ``alias`` of both are given.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin#id DataDockerPlugin#id}
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDockerPluginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDockerRegistryImage(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerRegistryImage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/d/registry_image docker_registry_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        insecure_skip_verify: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/d/registry_image docker_registry_image} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker image, including any tags. e.g. ``alpine:latest``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image#name DataDockerRegistryImage#name}
        :param insecure_skip_verify: If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image#insecure_skip_verify DataDockerRegistryImage#insecure_skip_verify}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataDockerRegistryImageConfig(
            name=name,
            insecure_skip_verify=insecure_skip_verify,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetInsecureSkipVerify")
    def reset_insecure_skip_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureSkipVerify", []))

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
    @jsii.member(jsii_name="sha256Digest")
    def sha256_digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha256Digest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerifyInput")
    def insecure_skip_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "insecureSkipVerifyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerify")
    def insecure_skip_verify(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "insecureSkipVerify"))

    @insecure_skip_verify.setter
    def insecure_skip_verify(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "insecureSkipVerify", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DataDockerRegistryImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "insecure_skip_verify": "insecureSkipVerify",
    },
)
class DataDockerRegistryImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        insecure_skip_verify: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker image, including any tags. e.g. ``alpine:latest``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image#name DataDockerRegistryImage#name}
        :param insecure_skip_verify: If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image#insecure_skip_verify DataDockerRegistryImage#insecure_skip_verify}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if insecure_skip_verify is not None:
            self._values["insecure_skip_verify"] = insecure_skip_verify

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
    def name(self) -> builtins.str:
        '''The name of the Docker image, including any tags. e.g. ``alpine:latest``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image#name DataDockerRegistryImage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def insecure_skip_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image#insecure_skip_verify DataDockerRegistryImage#insecure_skip_verify}
        '''
        result = self._values.get("insecure_skip_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDockerRegistryImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DockerProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DockerProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker docker}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        ca_material: typing.Optional[builtins.str] = None,
        cert_material: typing.Optional[builtins.str] = None,
        cert_path: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        key_material: typing.Optional[builtins.str] = None,
        registry_auth: typing.Optional["DockerProviderRegistryAuth"] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker docker} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#alias DockerProvider#alias}
        :param ca_material: PEM-encoded content of Docker host CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#ca_material DockerProvider#ca_material}
        :param cert_material: PEM-encoded content of Docker client certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_material DockerProvider#cert_material}
        :param cert_path: Path to directory with Docker TLS config. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_path DockerProvider#cert_path}
        :param host: The Docker daemon address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#host DockerProvider#host}
        :param key_material: PEM-encoded content of Docker client private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#key_material DockerProvider#key_material}
        :param registry_auth: registry_auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#registry_auth DockerProvider#registry_auth}
        '''
        config = DockerProviderConfig(
            alias=alias,
            ca_material=ca_material,
            cert_material=cert_material,
            cert_path=cert_path,
            host=host,
            key_material=key_material,
            registry_auth=registry_auth,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetCaMaterial")
    def reset_ca_material(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaMaterial", []))

    @jsii.member(jsii_name="resetCertMaterial")
    def reset_cert_material(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertMaterial", []))

    @jsii.member(jsii_name="resetCertPath")
    def reset_cert_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertPath", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetKeyMaterial")
    def reset_key_material(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyMaterial", []))

    @jsii.member(jsii_name="resetRegistryAuth")
    def reset_registry_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegistryAuth", []))

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
    @jsii.member(jsii_name="caMaterialInput")
    def ca_material_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caMaterialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certMaterialInput")
    def cert_material_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certMaterialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certPathInput")
    def cert_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyMaterialInput")
    def key_material_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyMaterialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registryAuthInput")
    def registry_auth_input(self) -> typing.Optional["DockerProviderRegistryAuth"]:
        return typing.cast(typing.Optional["DockerProviderRegistryAuth"], jsii.get(self, "registryAuthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caMaterial")
    def ca_material(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caMaterial"))

    @ca_material.setter
    def ca_material(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "caMaterial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certMaterial")
    def cert_material(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certMaterial"))

    @cert_material.setter
    def cert_material(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certMaterial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certPath")
    def cert_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certPath"))

    @cert_path.setter
    def cert_path(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "host"))

    @host.setter
    def host(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyMaterial")
    def key_material(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyMaterial"))

    @key_material.setter
    def key_material(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "keyMaterial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registryAuth")
    def registry_auth(self) -> typing.Optional["DockerProviderRegistryAuth"]:
        return typing.cast(typing.Optional["DockerProviderRegistryAuth"], jsii.get(self, "registryAuth"))

    @registry_auth.setter
    def registry_auth(
        self,
        value: typing.Optional["DockerProviderRegistryAuth"],
    ) -> None:
        jsii.set(self, "registryAuth", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DockerProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alias": "alias",
        "ca_material": "caMaterial",
        "cert_material": "certMaterial",
        "cert_path": "certPath",
        "host": "host",
        "key_material": "keyMaterial",
        "registry_auth": "registryAuth",
    },
)
class DockerProviderConfig:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        ca_material: typing.Optional[builtins.str] = None,
        cert_material: typing.Optional[builtins.str] = None,
        cert_path: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        key_material: typing.Optional[builtins.str] = None,
        registry_auth: typing.Optional["DockerProviderRegistryAuth"] = None,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#alias DockerProvider#alias}
        :param ca_material: PEM-encoded content of Docker host CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#ca_material DockerProvider#ca_material}
        :param cert_material: PEM-encoded content of Docker client certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_material DockerProvider#cert_material}
        :param cert_path: Path to directory with Docker TLS config. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_path DockerProvider#cert_path}
        :param host: The Docker daemon address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#host DockerProvider#host}
        :param key_material: PEM-encoded content of Docker client private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#key_material DockerProvider#key_material}
        :param registry_auth: registry_auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#registry_auth DockerProvider#registry_auth}
        '''
        if isinstance(registry_auth, dict):
            registry_auth = DockerProviderRegistryAuth(**registry_auth)
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if ca_material is not None:
            self._values["ca_material"] = ca_material
        if cert_material is not None:
            self._values["cert_material"] = cert_material
        if cert_path is not None:
            self._values["cert_path"] = cert_path
        if host is not None:
            self._values["host"] = host
        if key_material is not None:
            self._values["key_material"] = key_material
        if registry_auth is not None:
            self._values["registry_auth"] = registry_auth

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#alias DockerProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_material(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded content of Docker host CA certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#ca_material DockerProvider#ca_material}
        '''
        result = self._values.get("ca_material")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_material(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded content of Docker client certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_material DockerProvider#cert_material}
        '''
        result = self._values.get("cert_material")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_path(self) -> typing.Optional[builtins.str]:
        '''Path to directory with Docker TLS config.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_path DockerProvider#cert_path}
        '''
        result = self._values.get("cert_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''The Docker daemon address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#host DockerProvider#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_material(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded content of Docker client private key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#key_material DockerProvider#key_material}
        '''
        result = self._values.get("key_material")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_auth(self) -> typing.Optional["DockerProviderRegistryAuth"]:
        '''registry_auth block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#registry_auth DockerProvider#registry_auth}
        '''
        result = self._values.get("registry_auth")
        return typing.cast(typing.Optional["DockerProviderRegistryAuth"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DockerProviderRegistryAuth",
    jsii_struct_bases=[],
    name_mapping={
        "address": "address",
        "config_file": "configFile",
        "config_file_content": "configFileContent",
        "password": "password",
        "username": "username",
    },
)
class DockerProviderRegistryAuth:
    def __init__(
        self,
        *,
        address: builtins.str,
        config_file: typing.Optional[builtins.str] = None,
        config_file_content: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: Address of the registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#address DockerProvider#address}
        :param config_file: Path to docker json file for registry auth. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#config_file DockerProvider#config_file}
        :param config_file_content: Plain content of the docker json file for registry auth. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#config_file_content DockerProvider#config_file_content}
        :param password: Password for the registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#password DockerProvider#password}
        :param username: Username for the registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#username DockerProvider#username}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "address": address,
        }
        if config_file is not None:
            self._values["config_file"] = config_file
        if config_file_content is not None:
            self._values["config_file_content"] = config_file_content
        if password is not None:
            self._values["password"] = password
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def address(self) -> builtins.str:
        '''Address of the registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#address DockerProvider#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config_file(self) -> typing.Optional[builtins.str]:
        '''Path to docker json file for registry auth.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#config_file DockerProvider#config_file}
        '''
        result = self._values.get("config_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_file_content(self) -> typing.Optional[builtins.str]:
        '''Plain content of the docker json file for registry auth.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#config_file_content DockerProvider#config_file_content}
        '''
        result = self._values.get("config_file_content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for the registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#password DockerProvider#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Username for the registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#username DockerProvider#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerProviderRegistryAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Image(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Image",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/image docker_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        build_attribute: typing.Optional["ImageBuild"] = None,
        force_remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        keep_locally: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        pull_trigger: typing.Optional[builtins.str] = None,
        pull_triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/image docker_image} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker image, including any tags or SHA256 repo digests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#name Image#name}
        :param build_attribute: build block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#build Image#build}
        :param force_remove: If true, then the image is removed forcibly when the resource is destroyed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#force_remove Image#force_remove}
        :param keep_locally: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#keep_locally Image#keep_locally}
        :param pull_trigger: A value which cause an image pull when changed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#pull_trigger Image#pull_trigger}
        :param pull_triggers: List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the `docker_registry_image <../data-sources/registry_image.md>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#pull_triggers Image#pull_triggers}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ImageConfig(
            name=name,
            build_attribute=build_attribute,
            force_remove=force_remove,
            keep_locally=keep_locally,
            pull_trigger=pull_trigger,
            pull_triggers=pull_triggers,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putBuildAttribute")
    def put_build_attribute(
        self,
        *,
        path: builtins.str,
        build_arg: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        force_remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        label: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        no_cache: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tag: typing.Optional[typing.Sequence[builtins.str]] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Context path. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#path Image#path}
        :param build_arg: Set build-time variables. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#build_arg Image#build_arg}
        :param dockerfile: Name of the Dockerfile. Defaults to ``Dockerfile``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#dockerfile Image#dockerfile}
        :param force_remove: Always remove intermediate containers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#force_remove Image#force_remove}
        :param label: Set metadata for an image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#label Image#label}
        :param no_cache: Do not use cache when building the image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#no_cache Image#no_cache}
        :param remove: Remove intermediate containers after a successful build. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#remove Image#remove}
        :param tag: Name and optionally a tag in the 'name:tag' format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#tag Image#tag}
        :param target: Set the target build stage to build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#target Image#target}
        '''
        value = ImageBuild(
            path=path,
            build_arg=build_arg,
            dockerfile=dockerfile,
            force_remove=force_remove,
            label=label,
            no_cache=no_cache,
            remove=remove,
            tag=tag,
            target=target,
        )

        return typing.cast(None, jsii.invoke(self, "putBuildAttribute", [value]))

    @jsii.member(jsii_name="resetBuildAttribute")
    def reset_build_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildAttribute", []))

    @jsii.member(jsii_name="resetForceRemove")
    def reset_force_remove(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceRemove", []))

    @jsii.member(jsii_name="resetKeepLocally")
    def reset_keep_locally(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepLocally", []))

    @jsii.member(jsii_name="resetPullTrigger")
    def reset_pull_trigger(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullTrigger", []))

    @jsii.member(jsii_name="resetPullTriggers")
    def reset_pull_triggers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullTriggers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildAttribute")
    def build_attribute(self) -> "ImageBuildOutputReference":
        return typing.cast("ImageBuildOutputReference", jsii.get(self, "buildAttribute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latest")
    def latest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="output")
    def output(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "output"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repoDigest")
    def repo_digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoDigest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildAttributeInput")
    def build_attribute_input(self) -> typing.Optional["ImageBuild"]:
        return typing.cast(typing.Optional["ImageBuild"], jsii.get(self, "buildAttributeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceRemoveInput")
    def force_remove_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceRemoveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepLocallyInput")
    def keep_locally_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "keepLocallyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullTriggerInput")
    def pull_trigger_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pullTriggerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullTriggersInput")
    def pull_triggers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pullTriggersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceRemove")
    def force_remove(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceRemove"))

    @force_remove.setter
    def force_remove(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceRemove", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepLocally")
    def keep_locally(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "keepLocally"))

    @keep_locally.setter
    def keep_locally(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "keepLocally", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullTrigger")
    def pull_trigger(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pullTrigger"))

    @pull_trigger.setter
    def pull_trigger(self, value: builtins.str) -> None:
        jsii.set(self, "pullTrigger", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullTriggers")
    def pull_triggers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pullTriggers"))

    @pull_triggers.setter
    def pull_triggers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "pullTriggers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ImageBuild",
    jsii_struct_bases=[],
    name_mapping={
        "path": "path",
        "build_arg": "buildArg",
        "dockerfile": "dockerfile",
        "force_remove": "forceRemove",
        "label": "label",
        "no_cache": "noCache",
        "remove": "remove",
        "tag": "tag",
        "target": "target",
    },
)
class ImageBuild:
    def __init__(
        self,
        *,
        path: builtins.str,
        build_arg: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        force_remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        label: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        no_cache: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        tag: typing.Optional[typing.Sequence[builtins.str]] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Context path. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#path Image#path}
        :param build_arg: Set build-time variables. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#build_arg Image#build_arg}
        :param dockerfile: Name of the Dockerfile. Defaults to ``Dockerfile``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#dockerfile Image#dockerfile}
        :param force_remove: Always remove intermediate containers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#force_remove Image#force_remove}
        :param label: Set metadata for an image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#label Image#label}
        :param no_cache: Do not use cache when building the image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#no_cache Image#no_cache}
        :param remove: Remove intermediate containers after a successful build. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#remove Image#remove}
        :param tag: Name and optionally a tag in the 'name:tag' format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#tag Image#tag}
        :param target: Set the target build stage to build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#target Image#target}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "path": path,
        }
        if build_arg is not None:
            self._values["build_arg"] = build_arg
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if force_remove is not None:
            self._values["force_remove"] = force_remove
        if label is not None:
            self._values["label"] = label
        if no_cache is not None:
            self._values["no_cache"] = no_cache
        if remove is not None:
            self._values["remove"] = remove
        if tag is not None:
            self._values["tag"] = tag
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def path(self) -> builtins.str:
        '''Context path.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#path Image#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_arg(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Set build-time variables.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#build_arg Image#build_arg}
        '''
        result = self._values.get("build_arg")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''Name of the Dockerfile. Defaults to ``Dockerfile``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#dockerfile Image#dockerfile}
        '''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_remove(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Always remove intermediate containers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#force_remove Image#force_remove}
        '''
        result = self._values.get("force_remove")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def label(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Set metadata for an image.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#label Image#label}
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def no_cache(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Do not use cache when building the image.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#no_cache Image#no_cache}
        '''
        result = self._values.get("no_cache")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def remove(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Remove intermediate containers after a successful build. Defaults to  ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#remove Image#remove}
        '''
        result = self._values.get("remove")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def tag(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Name and optionally a tag in the 'name:tag' format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#tag Image#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Set the target build stage to build.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#target Image#target}
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImageBuild(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ImageBuildOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ImageBuildOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetBuildArg")
    def reset_build_arg(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildArg", []))

    @jsii.member(jsii_name="resetDockerfile")
    def reset_dockerfile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDockerfile", []))

    @jsii.member(jsii_name="resetForceRemove")
    def reset_force_remove(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceRemove", []))

    @jsii.member(jsii_name="resetLabel")
    def reset_label(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabel", []))

    @jsii.member(jsii_name="resetNoCache")
    def reset_no_cache(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoCache", []))

    @jsii.member(jsii_name="resetRemove")
    def reset_remove(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemove", []))

    @jsii.member(jsii_name="resetTag")
    def reset_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTag", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildArgInput")
    def build_arg_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "buildArgInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerfileInput")
    def dockerfile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dockerfileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceRemoveInput")
    def force_remove_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceRemoveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelInput")
    def label_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "labelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noCacheInput")
    def no_cache_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noCacheInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="removeInput")
    def remove_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "removeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagInput")
    def tag_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildArg")
    def build_arg(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "buildArg"))

    @build_arg.setter
    def build_arg(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "buildArg", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerfile")
    def dockerfile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dockerfile"))

    @dockerfile.setter
    def dockerfile(self, value: builtins.str) -> None:
        jsii.set(self, "dockerfile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceRemove")
    def force_remove(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceRemove"))

    @force_remove.setter
    def force_remove(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceRemove", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "label"))

    @label.setter
    def label(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "label", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noCache")
    def no_cache(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noCache"))

    @no_cache.setter
    def no_cache(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "noCache", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="remove")
    def remove(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "remove"))

    @remove.setter
    def remove(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "remove", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tag")
    def tag(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "tag", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ImageBuild]:
        return typing.cast(typing.Optional[ImageBuild], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ImageBuild]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "build_attribute": "buildAttribute",
        "force_remove": "forceRemove",
        "keep_locally": "keepLocally",
        "pull_trigger": "pullTrigger",
        "pull_triggers": "pullTriggers",
    },
)
class ImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        build_attribute: typing.Optional[ImageBuild] = None,
        force_remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        keep_locally: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        pull_trigger: typing.Optional[builtins.str] = None,
        pull_triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker image, including any tags or SHA256 repo digests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#name Image#name}
        :param build_attribute: build block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#build Image#build}
        :param force_remove: If true, then the image is removed forcibly when the resource is destroyed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#force_remove Image#force_remove}
        :param keep_locally: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#keep_locally Image#keep_locally}
        :param pull_trigger: A value which cause an image pull when changed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#pull_trigger Image#pull_trigger}
        :param pull_triggers: List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the `docker_registry_image <../data-sources/registry_image.md>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#pull_triggers Image#pull_triggers}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(build_attribute, dict):
            build_attribute = ImageBuild(**build_attribute)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if build_attribute is not None:
            self._values["build_attribute"] = build_attribute
        if force_remove is not None:
            self._values["force_remove"] = force_remove
        if keep_locally is not None:
            self._values["keep_locally"] = keep_locally
        if pull_trigger is not None:
            self._values["pull_trigger"] = pull_trigger
        if pull_triggers is not None:
            self._values["pull_triggers"] = pull_triggers

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
    def name(self) -> builtins.str:
        '''The name of the Docker image, including any tags or SHA256 repo digests.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#name Image#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_attribute(self) -> typing.Optional[ImageBuild]:
        '''build block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#build Image#build}
        '''
        result = self._values.get("build_attribute")
        return typing.cast(typing.Optional[ImageBuild], result)

    @builtins.property
    def force_remove(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If true, then the image is removed forcibly when the resource is destroyed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#force_remove Image#force_remove}
        '''
        result = self._values.get("force_remove")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def keep_locally(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If true, then the Docker image won't be deleted on destroy operation.

        If this is false, it will delete the image from the docker local storage on destroy operation.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#keep_locally Image#keep_locally}
        '''
        result = self._values.get("keep_locally")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def pull_trigger(self) -> typing.Optional[builtins.str]:
        '''A value which cause an image pull when changed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#pull_trigger Image#pull_trigger}
        '''
        result = self._values.get("pull_trigger")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_triggers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of values which cause an image pull when changed.

        This is used to store the image digest from the registry when using the `docker_registry_image <../data-sources/registry_image.md>`_.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image#pull_triggers Image#pull_triggers}
        '''
        result = self._values.get("pull_triggers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Network(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Network",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/network docker_network}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        attachable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        check_duplicate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        driver: typing.Optional[builtins.str] = None,
        ingress: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        internal: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ipam_config: typing.Optional[typing.Sequence["NetworkIpamConfig"]] = None,
        ipam_driver: typing.Optional[builtins.str] = None,
        ipv6: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        labels: typing.Optional[typing.Sequence["NetworkLabels"]] = None,
        options: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/network docker_network} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#name Network#name}
        :param attachable: Enable manual container attachment to the network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#attachable Network#attachable}
        :param check_duplicate: Requests daemon to check for networks with same name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#check_duplicate Network#check_duplicate}
        :param driver: The driver of the Docker network. Possible values are ``bridge``, ``host``, ``overlay``, ``macvlan``. See `network docs <https://docs.docker.com/network/#network-drivers>`_ for more details. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#driver Network#driver}
        :param ingress: Create swarm routing-mesh network. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ingress Network#ingress}
        :param internal: Whether the network is internal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#internal Network#internal}
        :param ipam_config: ipam_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ipam_config Network#ipam_config}
        :param ipam_driver: Driver used by the custom IP scheme of the network. Defaults to ``default``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ipam_driver Network#ipam_driver}
        :param ipv6: Enable IPv6 networking. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ipv6 Network#ipv6}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#labels Network#labels}
        :param options: Only available with bridge networks. See `bridge options docs <https://docs.docker.com/engine/reference/commandline/network_create/#bridge-driver-options>`_ for more details. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#options Network#options}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NetworkConfig(
            name=name,
            attachable=attachable,
            check_duplicate=check_duplicate,
            driver=driver,
            ingress=ingress,
            internal=internal,
            ipam_config=ipam_config,
            ipam_driver=ipam_driver,
            ipv6=ipv6,
            labels=labels,
            options=options,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAttachable")
    def reset_attachable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttachable", []))

    @jsii.member(jsii_name="resetCheckDuplicate")
    def reset_check_duplicate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckDuplicate", []))

    @jsii.member(jsii_name="resetDriver")
    def reset_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriver", []))

    @jsii.member(jsii_name="resetIngress")
    def reset_ingress(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngress", []))

    @jsii.member(jsii_name="resetInternal")
    def reset_internal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternal", []))

    @jsii.member(jsii_name="resetIpamConfig")
    def reset_ipam_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpamConfig", []))

    @jsii.member(jsii_name="resetIpamDriver")
    def reset_ipam_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpamDriver", []))

    @jsii.member(jsii_name="resetIpv6")
    def reset_ipv6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

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
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attachableInput")
    def attachable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "attachableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checkDuplicateInput")
    def check_duplicate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "checkDuplicateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverInput")
    def driver_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingressInput")
    def ingress_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ingressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalInput")
    def internal_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "internalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamConfigInput")
    def ipam_config_input(self) -> typing.Optional[typing.List["NetworkIpamConfig"]]:
        return typing.cast(typing.Optional[typing.List["NetworkIpamConfig"]], jsii.get(self, "ipamConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamDriverInput")
    def ipam_driver_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipamDriverInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipv6Input")
    def ipv6_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "ipv6Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["NetworkLabels"]]:
        return typing.cast(typing.Optional[typing.List["NetworkLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionsInput")
    def options_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "optionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attachable")
    def attachable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "attachable"))

    @attachable.setter
    def attachable(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "attachable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checkDuplicate")
    def check_duplicate(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "checkDuplicate"))

    @check_duplicate.setter
    def check_duplicate(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "checkDuplicate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driver")
    def driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driver"))

    @driver.setter
    def driver(self, value: builtins.str) -> None:
        jsii.set(self, "driver", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingress")
    def ingress(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ingress"))

    @ingress.setter
    def ingress(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "ingress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internal")
    def internal(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "internal"))

    @internal.setter
    def internal(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "internal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamConfig")
    def ipam_config(self) -> typing.List["NetworkIpamConfig"]:
        return typing.cast(typing.List["NetworkIpamConfig"], jsii.get(self, "ipamConfig"))

    @ipam_config.setter
    def ipam_config(self, value: typing.List["NetworkIpamConfig"]) -> None:
        jsii.set(self, "ipamConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamDriver")
    def ipam_driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipamDriver"))

    @ipam_driver.setter
    def ipam_driver(self, value: builtins.str) -> None:
        jsii.set(self, "ipamDriver", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "ipv6"))

    @ipv6.setter
    def ipv6(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "ipv6", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["NetworkLabels"]:
        return typing.cast(typing.List["NetworkLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["NetworkLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="options")
    def options(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "options"))

    @options.setter
    def options(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "options", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.NetworkConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "attachable": "attachable",
        "check_duplicate": "checkDuplicate",
        "driver": "driver",
        "ingress": "ingress",
        "internal": "internal",
        "ipam_config": "ipamConfig",
        "ipam_driver": "ipamDriver",
        "ipv6": "ipv6",
        "labels": "labels",
        "options": "options",
    },
)
class NetworkConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        attachable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        check_duplicate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        driver: typing.Optional[builtins.str] = None,
        ingress: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        internal: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        ipam_config: typing.Optional[typing.Sequence["NetworkIpamConfig"]] = None,
        ipam_driver: typing.Optional[builtins.str] = None,
        ipv6: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        labels: typing.Optional[typing.Sequence["NetworkLabels"]] = None,
        options: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#name Network#name}
        :param attachable: Enable manual container attachment to the network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#attachable Network#attachable}
        :param check_duplicate: Requests daemon to check for networks with same name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#check_duplicate Network#check_duplicate}
        :param driver: The driver of the Docker network. Possible values are ``bridge``, ``host``, ``overlay``, ``macvlan``. See `network docs <https://docs.docker.com/network/#network-drivers>`_ for more details. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#driver Network#driver}
        :param ingress: Create swarm routing-mesh network. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ingress Network#ingress}
        :param internal: Whether the network is internal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#internal Network#internal}
        :param ipam_config: ipam_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ipam_config Network#ipam_config}
        :param ipam_driver: Driver used by the custom IP scheme of the network. Defaults to ``default``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ipam_driver Network#ipam_driver}
        :param ipv6: Enable IPv6 networking. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ipv6 Network#ipv6}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#labels Network#labels}
        :param options: Only available with bridge networks. See `bridge options docs <https://docs.docker.com/engine/reference/commandline/network_create/#bridge-driver-options>`_ for more details. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#options Network#options}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if attachable is not None:
            self._values["attachable"] = attachable
        if check_duplicate is not None:
            self._values["check_duplicate"] = check_duplicate
        if driver is not None:
            self._values["driver"] = driver
        if ingress is not None:
            self._values["ingress"] = ingress
        if internal is not None:
            self._values["internal"] = internal
        if ipam_config is not None:
            self._values["ipam_config"] = ipam_config
        if ipam_driver is not None:
            self._values["ipam_driver"] = ipam_driver
        if ipv6 is not None:
            self._values["ipv6"] = ipv6
        if labels is not None:
            self._values["labels"] = labels
        if options is not None:
            self._values["options"] = options

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
    def name(self) -> builtins.str:
        '''The name of the Docker network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#name Network#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attachable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Enable manual container attachment to the network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#attachable Network#attachable}
        '''
        result = self._values.get("attachable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def check_duplicate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Requests daemon to check for networks with same name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#check_duplicate Network#check_duplicate}
        '''
        result = self._values.get("check_duplicate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def driver(self) -> typing.Optional[builtins.str]:
        '''The driver of the Docker network. Possible values are ``bridge``, ``host``, ``overlay``, ``macvlan``. See `network docs <https://docs.docker.com/network/#network-drivers>`_ for more details.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#driver Network#driver}
        '''
        result = self._values.get("driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ingress(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Create swarm routing-mesh network. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ingress Network#ingress}
        '''
        result = self._values.get("ingress")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def internal(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether the network is internal.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#internal Network#internal}
        '''
        result = self._values.get("internal")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def ipam_config(self) -> typing.Optional[typing.List["NetworkIpamConfig"]]:
        '''ipam_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ipam_config Network#ipam_config}
        '''
        result = self._values.get("ipam_config")
        return typing.cast(typing.Optional[typing.List["NetworkIpamConfig"]], result)

    @builtins.property
    def ipam_driver(self) -> typing.Optional[builtins.str]:
        '''Driver used by the custom IP scheme of the network. Defaults to ``default``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ipam_driver Network#ipam_driver}
        '''
        result = self._values.get("ipam_driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Enable IPv6 networking. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ipv6 Network#ipv6}
        '''
        result = self._values.get("ipv6")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["NetworkLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#labels Network#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["NetworkLabels"]], result)

    @builtins.property
    def options(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Only available with bridge networks. See `bridge options docs <https://docs.docker.com/engine/reference/commandline/network_create/#bridge-driver-options>`_ for more details.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#options Network#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.NetworkIpamConfig",
    jsii_struct_bases=[],
    name_mapping={
        "aux_address": "auxAddress",
        "gateway": "gateway",
        "ip_range": "ipRange",
        "subnet": "subnet",
    },
)
class NetworkIpamConfig:
    def __init__(
        self,
        *,
        aux_address: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        gateway: typing.Optional[builtins.str] = None,
        ip_range: typing.Optional[builtins.str] = None,
        subnet: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aux_address: Auxiliary IPv4 or IPv6 addresses used by Network driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#aux_address Network#aux_address}
        :param gateway: The IP address of the gateway. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#gateway Network#gateway}
        :param ip_range: The ip range in CIDR form. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ip_range Network#ip_range}
        :param subnet: The subnet in CIDR form. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#subnet Network#subnet}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if aux_address is not None:
            self._values["aux_address"] = aux_address
        if gateway is not None:
            self._values["gateway"] = gateway
        if ip_range is not None:
            self._values["ip_range"] = ip_range
        if subnet is not None:
            self._values["subnet"] = subnet

    @builtins.property
    def aux_address(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Auxiliary IPv4 or IPv6 addresses used by Network driver.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#aux_address Network#aux_address}
        '''
        result = self._values.get("aux_address")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def gateway(self) -> typing.Optional[builtins.str]:
        '''The IP address of the gateway.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#gateway Network#gateway}
        '''
        result = self._values.get("gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_range(self) -> typing.Optional[builtins.str]:
        '''The ip range in CIDR form.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#ip_range Network#ip_range}
        '''
        result = self._values.get("ip_range")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet(self) -> typing.Optional[builtins.str]:
        '''The subnet in CIDR form.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#subnet Network#subnet}
        '''
        result = self._values.get("subnet")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkIpamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.NetworkLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class NetworkLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#label Network#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#value Network#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#label Network#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network#value Network#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Plugin(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Plugin",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/plugin docker_plugin}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_timeout: typing.Optional[jsii.Number] = None,
        env: typing.Optional[typing.Sequence[builtins.str]] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        force_disable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        grant_all_permissions: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        grant_permissions: typing.Optional[typing.Sequence["PluginGrantPermissions"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/plugin docker_plugin} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docker Plugin name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#name Plugin#name}
        :param alias: Docker Plugin alias. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#alias Plugin#alias}
        :param enabled: If ``true`` the plugin is enabled. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#enabled Plugin#enabled}
        :param enable_timeout: HTTP client timeout to enable the plugin. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#enable_timeout Plugin#enable_timeout}
        :param env: The environment variables in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#env Plugin#env}
        :param force_destroy: If true, then the plugin is destroyed forcibly. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#force_destroy Plugin#force_destroy}
        :param force_disable: If true, then the plugin is disabled forcibly. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#force_disable Plugin#force_disable}
        :param grant_all_permissions: If true, grant all permissions necessary to run the plugin. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#grant_all_permissions Plugin#grant_all_permissions}
        :param grant_permissions: grant_permissions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#grant_permissions Plugin#grant_permissions}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PluginConfig(
            name=name,
            alias=alias,
            enabled=enabled,
            enable_timeout=enable_timeout,
            env=env,
            force_destroy=force_destroy,
            force_disable=force_disable,
            grant_all_permissions=grant_all_permissions,
            grant_permissions=grant_permissions,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEnableTimeout")
    def reset_enable_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableTimeout", []))

    @jsii.member(jsii_name="resetEnv")
    def reset_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnv", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetForceDisable")
    def reset_force_disable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDisable", []))

    @jsii.member(jsii_name="resetGrantAllPermissions")
    def reset_grant_all_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGrantAllPermissions", []))

    @jsii.member(jsii_name="resetGrantPermissions")
    def reset_grant_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGrantPermissions", []))

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
    @jsii.member(jsii_name="pluginReference")
    def plugin_reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTimeoutInput")
    def enable_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "enableTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="envInput")
    def env_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "envInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDisableInput")
    def force_disable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceDisableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantAllPermissionsInput")
    def grant_all_permissions_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "grantAllPermissionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPermissionsInput")
    def grant_permissions_input(
        self,
    ) -> typing.Optional[typing.List["PluginGrantPermissions"]]:
        return typing.cast(typing.Optional[typing.List["PluginGrantPermissions"]], jsii.get(self, "grantPermissionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: builtins.str) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTimeout")
    def enable_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "enableTimeout"))

    @enable_timeout.setter
    def enable_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "enableTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "env"))

    @env.setter
    def env(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "env", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDisable")
    def force_disable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceDisable"))

    @force_disable.setter
    def force_disable(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceDisable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantAllPermissions")
    def grant_all_permissions(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "grantAllPermissions"))

    @grant_all_permissions.setter
    def grant_all_permissions(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "grantAllPermissions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPermissions")
    def grant_permissions(self) -> typing.List["PluginGrantPermissions"]:
        return typing.cast(typing.List["PluginGrantPermissions"], jsii.get(self, "grantPermissions"))

    @grant_permissions.setter
    def grant_permissions(self, value: typing.List["PluginGrantPermissions"]) -> None:
        jsii.set(self, "grantPermissions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.PluginConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "alias": "alias",
        "enabled": "enabled",
        "enable_timeout": "enableTimeout",
        "env": "env",
        "force_destroy": "forceDestroy",
        "force_disable": "forceDisable",
        "grant_all_permissions": "grantAllPermissions",
        "grant_permissions": "grantPermissions",
    },
)
class PluginConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        enable_timeout: typing.Optional[jsii.Number] = None,
        env: typing.Optional[typing.Sequence[builtins.str]] = None,
        force_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        force_disable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        grant_all_permissions: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        grant_permissions: typing.Optional[typing.Sequence["PluginGrantPermissions"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docker Plugin name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#name Plugin#name}
        :param alias: Docker Plugin alias. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#alias Plugin#alias}
        :param enabled: If ``true`` the plugin is enabled. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#enabled Plugin#enabled}
        :param enable_timeout: HTTP client timeout to enable the plugin. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#enable_timeout Plugin#enable_timeout}
        :param env: The environment variables in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#env Plugin#env}
        :param force_destroy: If true, then the plugin is destroyed forcibly. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#force_destroy Plugin#force_destroy}
        :param force_disable: If true, then the plugin is disabled forcibly. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#force_disable Plugin#force_disable}
        :param grant_all_permissions: If true, grant all permissions necessary to run the plugin. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#grant_all_permissions Plugin#grant_all_permissions}
        :param grant_permissions: grant_permissions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#grant_permissions Plugin#grant_permissions}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if alias is not None:
            self._values["alias"] = alias
        if enabled is not None:
            self._values["enabled"] = enabled
        if enable_timeout is not None:
            self._values["enable_timeout"] = enable_timeout
        if env is not None:
            self._values["env"] = env
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if force_disable is not None:
            self._values["force_disable"] = force_disable
        if grant_all_permissions is not None:
            self._values["grant_all_permissions"] = grant_all_permissions
        if grant_permissions is not None:
            self._values["grant_permissions"] = grant_permissions

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
    def name(self) -> builtins.str:
        '''Docker Plugin name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#name Plugin#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docker Plugin alias.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#alias Plugin#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true`` the plugin is enabled. Defaults to ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#enabled Plugin#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def enable_timeout(self) -> typing.Optional[jsii.Number]:
        '''HTTP client timeout to enable the plugin.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#enable_timeout Plugin#enable_timeout}
        '''
        result = self._values.get("enable_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The environment variables in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#env Plugin#env}
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def force_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If true, then the plugin is destroyed forcibly.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#force_destroy Plugin#force_destroy}
        '''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def force_disable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If true, then the plugin is disabled forcibly.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#force_disable Plugin#force_disable}
        '''
        result = self._values.get("force_disable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def grant_all_permissions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If true, grant all permissions necessary to run the plugin.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#grant_all_permissions Plugin#grant_all_permissions}
        '''
        result = self._values.get("grant_all_permissions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def grant_permissions(
        self,
    ) -> typing.Optional[typing.List["PluginGrantPermissions"]]:
        '''grant_permissions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#grant_permissions Plugin#grant_permissions}
        '''
        result = self._values.get("grant_permissions")
        return typing.cast(typing.Optional[typing.List["PluginGrantPermissions"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PluginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.PluginGrantPermissions",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class PluginGrantPermissions:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: The name of the permission. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#name Plugin#name}
        :param value: The value of the permission. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#value Plugin#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the permission.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#name Plugin#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.List[builtins.str]:
        '''The value of the permission.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin#value Plugin#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PluginGrantPermissions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RegistryImage(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.RegistryImage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/registry_image docker_registry_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        build_attribute: typing.Optional["RegistryImageBuild"] = None,
        insecure_skip_verify: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        keep_remotely: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/registry_image docker_registry_image} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#name RegistryImage#name}
        :param build_attribute: build block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#build RegistryImage#build}
        :param insecure_skip_verify: If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#insecure_skip_verify RegistryImage#insecure_skip_verify}
        :param keep_remotely: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker registry on destroy operation. Defaults to ``false`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#keep_remotely RegistryImage#keep_remotely}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RegistryImageConfig(
            name=name,
            build_attribute=build_attribute,
            insecure_skip_verify=insecure_skip_verify,
            keep_remotely=keep_remotely,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putBuildAttribute")
    def put_build_attribute(
        self,
        *,
        context: builtins.str,
        auth_config: typing.Optional[typing.Sequence["RegistryImageBuildAuthConfig"]] = None,
        build_args: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        build_id: typing.Optional[builtins.str] = None,
        cache_from: typing.Optional[typing.Sequence[builtins.str]] = None,
        cgroup_parent: typing.Optional[builtins.str] = None,
        cpu_period: typing.Optional[jsii.Number] = None,
        cpu_quota: typing.Optional[jsii.Number] = None,
        cpu_set_cpus: typing.Optional[builtins.str] = None,
        cpu_set_mems: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        extra_hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
        force_remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        isolation: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_swap: typing.Optional[jsii.Number] = None,
        network_mode: typing.Optional[builtins.str] = None,
        no_cache: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        platform: typing.Optional[builtins.str] = None,
        pull_parent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        remote_context: typing.Optional[builtins.str] = None,
        remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        security_opt: typing.Optional[typing.Sequence[builtins.str]] = None,
        session_id: typing.Optional[builtins.str] = None,
        shm_size: typing.Optional[jsii.Number] = None,
        squash: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        suppress_output: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        target: typing.Optional[builtins.str] = None,
        ulimit: typing.Optional[typing.Sequence["RegistryImageBuildUlimit"]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param context: The absolute path to the context folder. You can use the helper function '${path.cwd}/context-dir'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#context RegistryImage#context}
        :param auth_config: auth_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#auth_config RegistryImage#auth_config}
        :param build_args: Pairs for build-time variables in the form TODO. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#build_args RegistryImage#build_args}
        :param build_id: BuildID is an optional identifier that can be passed together with the build request. The. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#build_id RegistryImage#build_id}
        :param cache_from: Images to consider as cache sources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cache_from RegistryImage#cache_from}
        :param cgroup_parent: Optional parent cgroup for the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cgroup_parent RegistryImage#cgroup_parent}
        :param cpu_period: The length of a CPU period in microseconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_period RegistryImage#cpu_period}
        :param cpu_quota: Microseconds of CPU time that the container can get in a CPU period. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_quota RegistryImage#cpu_quota}
        :param cpu_set_cpus: CPUs in which to allow execution (e.g., ``0-3``, ``0``, ``1``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_set_cpus RegistryImage#cpu_set_cpus}
        :param cpu_set_mems: MEMs in which to allow execution (``0-3``, ``0``, ``1``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_set_mems RegistryImage#cpu_set_mems}
        :param cpu_shares: CPU shares (relative weight). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_shares RegistryImage#cpu_shares}
        :param dockerfile: Dockerfile file. Defaults to ``Dockerfile``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#dockerfile RegistryImage#dockerfile}
        :param extra_hosts: A list of hostnames/IP mappings to add to the container’s /etc/hosts file. Specified in the form ["hostname:IP"]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#extra_hosts RegistryImage#extra_hosts}
        :param force_remove: Always remove intermediate containers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#force_remove RegistryImage#force_remove}
        :param isolation: Isolation represents the isolation technology of a container. The supported values are. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#isolation RegistryImage#isolation}
        :param labels: User-defined key/value metadata. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#labels RegistryImage#labels}
        :param memory: Set memory limit for build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#memory RegistryImage#memory}
        :param memory_swap: Total memory (memory + swap), -1 to enable unlimited swap. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#memory_swap RegistryImage#memory_swap}
        :param network_mode: Set the networking mode for the RUN instructions during build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#network_mode RegistryImage#network_mode}
        :param no_cache: Do not use the cache when building the image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#no_cache RegistryImage#no_cache}
        :param platform: Set platform if server is multi-platform capable. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#platform RegistryImage#platform}
        :param pull_parent: Attempt to pull the image even if an older image exists locally. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#pull_parent RegistryImage#pull_parent}
        :param remote_context: A Git repository URI or HTTP/HTTPS context URI. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#remote_context RegistryImage#remote_context}
        :param remove: Remove intermediate containers after a successful build (default behavior). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#remove RegistryImage#remove}
        :param security_opt: The security options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#security_opt RegistryImage#security_opt}
        :param session_id: Set an ID for the build session. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#session_id RegistryImage#session_id}
        :param shm_size: Size of /dev/shm in bytes. The size must be greater than 0. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#shm_size RegistryImage#shm_size}
        :param squash: If true the new layers are squashed into a new image with a single new layer. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#squash RegistryImage#squash}
        :param suppress_output: Suppress the build output and print image ID on success. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#suppress_output RegistryImage#suppress_output}
        :param target: Set the target build stage to build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#target RegistryImage#target}
        :param ulimit: ulimit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#ulimit RegistryImage#ulimit}
        :param version: Version of the unerlying builder to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#version RegistryImage#version}
        '''
        value = RegistryImageBuild(
            context=context,
            auth_config=auth_config,
            build_args=build_args,
            build_id=build_id,
            cache_from=cache_from,
            cgroup_parent=cgroup_parent,
            cpu_period=cpu_period,
            cpu_quota=cpu_quota,
            cpu_set_cpus=cpu_set_cpus,
            cpu_set_mems=cpu_set_mems,
            cpu_shares=cpu_shares,
            dockerfile=dockerfile,
            extra_hosts=extra_hosts,
            force_remove=force_remove,
            isolation=isolation,
            labels=labels,
            memory=memory,
            memory_swap=memory_swap,
            network_mode=network_mode,
            no_cache=no_cache,
            platform=platform,
            pull_parent=pull_parent,
            remote_context=remote_context,
            remove=remove,
            security_opt=security_opt,
            session_id=session_id,
            shm_size=shm_size,
            squash=squash,
            suppress_output=suppress_output,
            target=target,
            ulimit=ulimit,
            version=version,
        )

        return typing.cast(None, jsii.invoke(self, "putBuildAttribute", [value]))

    @jsii.member(jsii_name="resetBuildAttribute")
    def reset_build_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildAttribute", []))

    @jsii.member(jsii_name="resetInsecureSkipVerify")
    def reset_insecure_skip_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureSkipVerify", []))

    @jsii.member(jsii_name="resetKeepRemotely")
    def reset_keep_remotely(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepRemotely", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildAttribute")
    def build_attribute(self) -> "RegistryImageBuildOutputReference":
        return typing.cast("RegistryImageBuildOutputReference", jsii.get(self, "buildAttribute"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sha256Digest")
    def sha256_digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha256Digest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildAttributeInput")
    def build_attribute_input(self) -> typing.Optional["RegistryImageBuild"]:
        return typing.cast(typing.Optional["RegistryImageBuild"], jsii.get(self, "buildAttributeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerifyInput")
    def insecure_skip_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "insecureSkipVerifyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepRemotelyInput")
    def keep_remotely_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "keepRemotelyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerify")
    def insecure_skip_verify(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "insecureSkipVerify"))

    @insecure_skip_verify.setter
    def insecure_skip_verify(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "insecureSkipVerify", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepRemotely")
    def keep_remotely(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "keepRemotely"))

    @keep_remotely.setter
    def keep_remotely(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "keepRemotely", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.RegistryImageBuild",
    jsii_struct_bases=[],
    name_mapping={
        "context": "context",
        "auth_config": "authConfig",
        "build_args": "buildArgs",
        "build_id": "buildId",
        "cache_from": "cacheFrom",
        "cgroup_parent": "cgroupParent",
        "cpu_period": "cpuPeriod",
        "cpu_quota": "cpuQuota",
        "cpu_set_cpus": "cpuSetCpus",
        "cpu_set_mems": "cpuSetMems",
        "cpu_shares": "cpuShares",
        "dockerfile": "dockerfile",
        "extra_hosts": "extraHosts",
        "force_remove": "forceRemove",
        "isolation": "isolation",
        "labels": "labels",
        "memory": "memory",
        "memory_swap": "memorySwap",
        "network_mode": "networkMode",
        "no_cache": "noCache",
        "platform": "platform",
        "pull_parent": "pullParent",
        "remote_context": "remoteContext",
        "remove": "remove",
        "security_opt": "securityOpt",
        "session_id": "sessionId",
        "shm_size": "shmSize",
        "squash": "squash",
        "suppress_output": "suppressOutput",
        "target": "target",
        "ulimit": "ulimit",
        "version": "version",
    },
)
class RegistryImageBuild:
    def __init__(
        self,
        *,
        context: builtins.str,
        auth_config: typing.Optional[typing.Sequence["RegistryImageBuildAuthConfig"]] = None,
        build_args: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        build_id: typing.Optional[builtins.str] = None,
        cache_from: typing.Optional[typing.Sequence[builtins.str]] = None,
        cgroup_parent: typing.Optional[builtins.str] = None,
        cpu_period: typing.Optional[jsii.Number] = None,
        cpu_quota: typing.Optional[jsii.Number] = None,
        cpu_set_cpus: typing.Optional[builtins.str] = None,
        cpu_set_mems: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        extra_hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
        force_remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        isolation: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_swap: typing.Optional[jsii.Number] = None,
        network_mode: typing.Optional[builtins.str] = None,
        no_cache: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        platform: typing.Optional[builtins.str] = None,
        pull_parent: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        remote_context: typing.Optional[builtins.str] = None,
        remove: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        security_opt: typing.Optional[typing.Sequence[builtins.str]] = None,
        session_id: typing.Optional[builtins.str] = None,
        shm_size: typing.Optional[jsii.Number] = None,
        squash: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        suppress_output: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        target: typing.Optional[builtins.str] = None,
        ulimit: typing.Optional[typing.Sequence["RegistryImageBuildUlimit"]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param context: The absolute path to the context folder. You can use the helper function '${path.cwd}/context-dir'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#context RegistryImage#context}
        :param auth_config: auth_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#auth_config RegistryImage#auth_config}
        :param build_args: Pairs for build-time variables in the form TODO. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#build_args RegistryImage#build_args}
        :param build_id: BuildID is an optional identifier that can be passed together with the build request. The. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#build_id RegistryImage#build_id}
        :param cache_from: Images to consider as cache sources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cache_from RegistryImage#cache_from}
        :param cgroup_parent: Optional parent cgroup for the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cgroup_parent RegistryImage#cgroup_parent}
        :param cpu_period: The length of a CPU period in microseconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_period RegistryImage#cpu_period}
        :param cpu_quota: Microseconds of CPU time that the container can get in a CPU period. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_quota RegistryImage#cpu_quota}
        :param cpu_set_cpus: CPUs in which to allow execution (e.g., ``0-3``, ``0``, ``1``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_set_cpus RegistryImage#cpu_set_cpus}
        :param cpu_set_mems: MEMs in which to allow execution (``0-3``, ``0``, ``1``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_set_mems RegistryImage#cpu_set_mems}
        :param cpu_shares: CPU shares (relative weight). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_shares RegistryImage#cpu_shares}
        :param dockerfile: Dockerfile file. Defaults to ``Dockerfile``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#dockerfile RegistryImage#dockerfile}
        :param extra_hosts: A list of hostnames/IP mappings to add to the container’s /etc/hosts file. Specified in the form ["hostname:IP"]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#extra_hosts RegistryImage#extra_hosts}
        :param force_remove: Always remove intermediate containers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#force_remove RegistryImage#force_remove}
        :param isolation: Isolation represents the isolation technology of a container. The supported values are. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#isolation RegistryImage#isolation}
        :param labels: User-defined key/value metadata. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#labels RegistryImage#labels}
        :param memory: Set memory limit for build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#memory RegistryImage#memory}
        :param memory_swap: Total memory (memory + swap), -1 to enable unlimited swap. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#memory_swap RegistryImage#memory_swap}
        :param network_mode: Set the networking mode for the RUN instructions during build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#network_mode RegistryImage#network_mode}
        :param no_cache: Do not use the cache when building the image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#no_cache RegistryImage#no_cache}
        :param platform: Set platform if server is multi-platform capable. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#platform RegistryImage#platform}
        :param pull_parent: Attempt to pull the image even if an older image exists locally. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#pull_parent RegistryImage#pull_parent}
        :param remote_context: A Git repository URI or HTTP/HTTPS context URI. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#remote_context RegistryImage#remote_context}
        :param remove: Remove intermediate containers after a successful build (default behavior). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#remove RegistryImage#remove}
        :param security_opt: The security options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#security_opt RegistryImage#security_opt}
        :param session_id: Set an ID for the build session. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#session_id RegistryImage#session_id}
        :param shm_size: Size of /dev/shm in bytes. The size must be greater than 0. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#shm_size RegistryImage#shm_size}
        :param squash: If true the new layers are squashed into a new image with a single new layer. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#squash RegistryImage#squash}
        :param suppress_output: Suppress the build output and print image ID on success. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#suppress_output RegistryImage#suppress_output}
        :param target: Set the target build stage to build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#target RegistryImage#target}
        :param ulimit: ulimit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#ulimit RegistryImage#ulimit}
        :param version: Version of the unerlying builder to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#version RegistryImage#version}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "context": context,
        }
        if auth_config is not None:
            self._values["auth_config"] = auth_config
        if build_args is not None:
            self._values["build_args"] = build_args
        if build_id is not None:
            self._values["build_id"] = build_id
        if cache_from is not None:
            self._values["cache_from"] = cache_from
        if cgroup_parent is not None:
            self._values["cgroup_parent"] = cgroup_parent
        if cpu_period is not None:
            self._values["cpu_period"] = cpu_period
        if cpu_quota is not None:
            self._values["cpu_quota"] = cpu_quota
        if cpu_set_cpus is not None:
            self._values["cpu_set_cpus"] = cpu_set_cpus
        if cpu_set_mems is not None:
            self._values["cpu_set_mems"] = cpu_set_mems
        if cpu_shares is not None:
            self._values["cpu_shares"] = cpu_shares
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if extra_hosts is not None:
            self._values["extra_hosts"] = extra_hosts
        if force_remove is not None:
            self._values["force_remove"] = force_remove
        if isolation is not None:
            self._values["isolation"] = isolation
        if labels is not None:
            self._values["labels"] = labels
        if memory is not None:
            self._values["memory"] = memory
        if memory_swap is not None:
            self._values["memory_swap"] = memory_swap
        if network_mode is not None:
            self._values["network_mode"] = network_mode
        if no_cache is not None:
            self._values["no_cache"] = no_cache
        if platform is not None:
            self._values["platform"] = platform
        if pull_parent is not None:
            self._values["pull_parent"] = pull_parent
        if remote_context is not None:
            self._values["remote_context"] = remote_context
        if remove is not None:
            self._values["remove"] = remove
        if security_opt is not None:
            self._values["security_opt"] = security_opt
        if session_id is not None:
            self._values["session_id"] = session_id
        if shm_size is not None:
            self._values["shm_size"] = shm_size
        if squash is not None:
            self._values["squash"] = squash
        if suppress_output is not None:
            self._values["suppress_output"] = suppress_output
        if target is not None:
            self._values["target"] = target
        if ulimit is not None:
            self._values["ulimit"] = ulimit
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def context(self) -> builtins.str:
        '''The absolute path to the context folder. You can use the helper function '${path.cwd}/context-dir'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#context RegistryImage#context}
        '''
        result = self._values.get("context")
        assert result is not None, "Required property 'context' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_config(
        self,
    ) -> typing.Optional[typing.List["RegistryImageBuildAuthConfig"]]:
        '''auth_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#auth_config RegistryImage#auth_config}
        '''
        result = self._values.get("auth_config")
        return typing.cast(typing.Optional[typing.List["RegistryImageBuildAuthConfig"]], result)

    @builtins.property
    def build_args(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Pairs for build-time variables in the form TODO.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#build_args RegistryImage#build_args}
        '''
        result = self._values.get("build_args")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def build_id(self) -> typing.Optional[builtins.str]:
        '''BuildID is an optional identifier that can be passed together with the build request. The.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#build_id RegistryImage#build_id}
        '''
        result = self._values.get("build_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_from(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Images to consider as cache sources.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cache_from RegistryImage#cache_from}
        '''
        result = self._values.get("cache_from")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cgroup_parent(self) -> typing.Optional[builtins.str]:
        '''Optional parent cgroup for the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cgroup_parent RegistryImage#cgroup_parent}
        '''
        result = self._values.get("cgroup_parent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_period(self) -> typing.Optional[jsii.Number]:
        '''The length of a CPU period in microseconds.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_period RegistryImage#cpu_period}
        '''
        result = self._values.get("cpu_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_quota(self) -> typing.Optional[jsii.Number]:
        '''Microseconds of CPU time that the container can get in a CPU period.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_quota RegistryImage#cpu_quota}
        '''
        result = self._values.get("cpu_quota")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_set_cpus(self) -> typing.Optional[builtins.str]:
        '''CPUs in which to allow execution (e.g., ``0-3``, ``0``, ``1``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_set_cpus RegistryImage#cpu_set_cpus}
        '''
        result = self._values.get("cpu_set_cpus")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_set_mems(self) -> typing.Optional[builtins.str]:
        '''MEMs in which to allow execution (``0-3``, ``0``, ``1``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_set_mems RegistryImage#cpu_set_mems}
        '''
        result = self._values.get("cpu_set_mems")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_shares(self) -> typing.Optional[jsii.Number]:
        '''CPU shares (relative weight).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#cpu_shares RegistryImage#cpu_shares}
        '''
        result = self._values.get("cpu_shares")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''Dockerfile file. Defaults to ``Dockerfile``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#dockerfile RegistryImage#dockerfile}
        '''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extra_hosts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of hostnames/IP mappings to add to the container’s /etc/hosts file. Specified in the form ["hostname:IP"].

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#extra_hosts RegistryImage#extra_hosts}
        '''
        result = self._values.get("extra_hosts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def force_remove(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Always remove intermediate containers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#force_remove RegistryImage#force_remove}
        '''
        result = self._values.get("force_remove")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def isolation(self) -> typing.Optional[builtins.str]:
        '''Isolation represents the isolation technology of a container. The supported values are.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#isolation RegistryImage#isolation}
        '''
        result = self._values.get("isolation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''User-defined key/value metadata.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#labels RegistryImage#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def memory(self) -> typing.Optional[jsii.Number]:
        '''Set memory limit for build.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#memory RegistryImage#memory}
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_swap(self) -> typing.Optional[jsii.Number]:
        '''Total memory (memory + swap), -1 to enable unlimited swap.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#memory_swap RegistryImage#memory_swap}
        '''
        result = self._values.get("memory_swap")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def network_mode(self) -> typing.Optional[builtins.str]:
        '''Set the networking mode for the RUN instructions during build.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#network_mode RegistryImage#network_mode}
        '''
        result = self._values.get("network_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def no_cache(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Do not use the cache when building the image.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#no_cache RegistryImage#no_cache}
        '''
        result = self._values.get("no_cache")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def platform(self) -> typing.Optional[builtins.str]:
        '''Set platform if server is multi-platform capable.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#platform RegistryImage#platform}
        '''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_parent(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Attempt to pull the image even if an older image exists locally.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#pull_parent RegistryImage#pull_parent}
        '''
        result = self._values.get("pull_parent")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def remote_context(self) -> typing.Optional[builtins.str]:
        '''A Git repository URI or HTTP/HTTPS context URI.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#remote_context RegistryImage#remote_context}
        '''
        result = self._values.get("remote_context")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remove(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Remove intermediate containers after a successful build (default behavior).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#remove RegistryImage#remove}
        '''
        result = self._values.get("remove")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def security_opt(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The security options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#security_opt RegistryImage#security_opt}
        '''
        result = self._values.get("security_opt")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def session_id(self) -> typing.Optional[builtins.str]:
        '''Set an ID for the build session.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#session_id RegistryImage#session_id}
        '''
        result = self._values.get("session_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def shm_size(self) -> typing.Optional[jsii.Number]:
        '''Size of /dev/shm in bytes. The size must be greater than 0.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#shm_size RegistryImage#shm_size}
        '''
        result = self._values.get("shm_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def squash(self) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If true the new layers are squashed into a new image with a single new layer.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#squash RegistryImage#squash}
        '''
        result = self._values.get("squash")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def suppress_output(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Suppress the build output and print image ID on success.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#suppress_output RegistryImage#suppress_output}
        '''
        result = self._values.get("suppress_output")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Set the target build stage to build.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#target RegistryImage#target}
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ulimit(self) -> typing.Optional[typing.List["RegistryImageBuildUlimit"]]:
        '''ulimit block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#ulimit RegistryImage#ulimit}
        '''
        result = self._values.get("ulimit")
        return typing.cast(typing.Optional[typing.List["RegistryImageBuildUlimit"]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Version of the unerlying builder to use.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#version RegistryImage#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistryImageBuild(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.RegistryImageBuildAuthConfig",
    jsii_struct_bases=[],
    name_mapping={
        "host_name": "hostName",
        "auth": "auth",
        "email": "email",
        "identity_token": "identityToken",
        "password": "password",
        "registry_token": "registryToken",
        "server_address": "serverAddress",
        "user_name": "userName",
    },
)
class RegistryImageBuildAuthConfig:
    def __init__(
        self,
        *,
        host_name: builtins.str,
        auth: typing.Optional[builtins.str] = None,
        email: typing.Optional[builtins.str] = None,
        identity_token: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        registry_token: typing.Optional[builtins.str] = None,
        server_address: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host_name: hostname of the registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#host_name RegistryImage#host_name}
        :param auth: the auth token. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#auth RegistryImage#auth}
        :param email: the user emal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#email RegistryImage#email}
        :param identity_token: the identity token. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#identity_token RegistryImage#identity_token}
        :param password: the registry password. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#password RegistryImage#password}
        :param registry_token: the registry token. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#registry_token RegistryImage#registry_token}
        :param server_address: the server address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#server_address RegistryImage#server_address}
        :param user_name: the registry user name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#user_name RegistryImage#user_name}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "host_name": host_name,
        }
        if auth is not None:
            self._values["auth"] = auth
        if email is not None:
            self._values["email"] = email
        if identity_token is not None:
            self._values["identity_token"] = identity_token
        if password is not None:
            self._values["password"] = password
        if registry_token is not None:
            self._values["registry_token"] = registry_token
        if server_address is not None:
            self._values["server_address"] = server_address
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def host_name(self) -> builtins.str:
        '''hostname of the registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#host_name RegistryImage#host_name}
        '''
        result = self._values.get("host_name")
        assert result is not None, "Required property 'host_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth(self) -> typing.Optional[builtins.str]:
        '''the auth token.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#auth RegistryImage#auth}
        '''
        result = self._values.get("auth")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''the user emal.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#email RegistryImage#email}
        '''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_token(self) -> typing.Optional[builtins.str]:
        '''the identity token.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#identity_token RegistryImage#identity_token}
        '''
        result = self._values.get("identity_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''the registry password.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#password RegistryImage#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_token(self) -> typing.Optional[builtins.str]:
        '''the registry token.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#registry_token RegistryImage#registry_token}
        '''
        result = self._values.get("registry_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_address(self) -> typing.Optional[builtins.str]:
        '''the server address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#server_address RegistryImage#server_address}
        '''
        result = self._values.get("server_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''the registry user name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#user_name RegistryImage#user_name}
        '''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistryImageBuildAuthConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RegistryImageBuildOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.RegistryImageBuildOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetAuthConfig")
    def reset_auth_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthConfig", []))

    @jsii.member(jsii_name="resetBuildArgs")
    def reset_build_args(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildArgs", []))

    @jsii.member(jsii_name="resetBuildId")
    def reset_build_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildId", []))

    @jsii.member(jsii_name="resetCacheFrom")
    def reset_cache_from(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCacheFrom", []))

    @jsii.member(jsii_name="resetCgroupParent")
    def reset_cgroup_parent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCgroupParent", []))

    @jsii.member(jsii_name="resetCpuPeriod")
    def reset_cpu_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuPeriod", []))

    @jsii.member(jsii_name="resetCpuQuota")
    def reset_cpu_quota(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuQuota", []))

    @jsii.member(jsii_name="resetCpuSetCpus")
    def reset_cpu_set_cpus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuSetCpus", []))

    @jsii.member(jsii_name="resetCpuSetMems")
    def reset_cpu_set_mems(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuSetMems", []))

    @jsii.member(jsii_name="resetCpuShares")
    def reset_cpu_shares(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuShares", []))

    @jsii.member(jsii_name="resetDockerfile")
    def reset_dockerfile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDockerfile", []))

    @jsii.member(jsii_name="resetExtraHosts")
    def reset_extra_hosts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtraHosts", []))

    @jsii.member(jsii_name="resetForceRemove")
    def reset_force_remove(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceRemove", []))

    @jsii.member(jsii_name="resetIsolation")
    def reset_isolation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsolation", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetMemory")
    def reset_memory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemory", []))

    @jsii.member(jsii_name="resetMemorySwap")
    def reset_memory_swap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemorySwap", []))

    @jsii.member(jsii_name="resetNetworkMode")
    def reset_network_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkMode", []))

    @jsii.member(jsii_name="resetNoCache")
    def reset_no_cache(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoCache", []))

    @jsii.member(jsii_name="resetPlatform")
    def reset_platform(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatform", []))

    @jsii.member(jsii_name="resetPullParent")
    def reset_pull_parent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullParent", []))

    @jsii.member(jsii_name="resetRemoteContext")
    def reset_remote_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteContext", []))

    @jsii.member(jsii_name="resetRemove")
    def reset_remove(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemove", []))

    @jsii.member(jsii_name="resetSecurityOpt")
    def reset_security_opt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityOpt", []))

    @jsii.member(jsii_name="resetSessionId")
    def reset_session_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSessionId", []))

    @jsii.member(jsii_name="resetShmSize")
    def reset_shm_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShmSize", []))

    @jsii.member(jsii_name="resetSquash")
    def reset_squash(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSquash", []))

    @jsii.member(jsii_name="resetSuppressOutput")
    def reset_suppress_output(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuppressOutput", []))

    @jsii.member(jsii_name="resetTarget")
    def reset_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTarget", []))

    @jsii.member(jsii_name="resetUlimit")
    def reset_ulimit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUlimit", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authConfigInput")
    def auth_config_input(
        self,
    ) -> typing.Optional[typing.List[RegistryImageBuildAuthConfig]]:
        return typing.cast(typing.Optional[typing.List[RegistryImageBuildAuthConfig]], jsii.get(self, "authConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildArgsInput")
    def build_args_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "buildArgsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildIdInput")
    def build_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buildIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheFromInput")
    def cache_from_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cacheFromInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cgroupParentInput")
    def cgroup_parent_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cgroupParentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contextInput")
    def context_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contextInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuPeriodInput")
    def cpu_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuQuotaInput")
    def cpu_quota_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuQuotaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSetCpusInput")
    def cpu_set_cpus_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpuSetCpusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSetMemsInput")
    def cpu_set_mems_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpuSetMemsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSharesInput")
    def cpu_shares_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuSharesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerfileInput")
    def dockerfile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dockerfileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extraHostsInput")
    def extra_hosts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "extraHostsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceRemoveInput")
    def force_remove_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "forceRemoveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isolationInput")
    def isolation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "isolationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryInput")
    def memory_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memorySwapInput")
    def memory_swap_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memorySwapInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkModeInput")
    def network_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noCacheInput")
    def no_cache_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noCacheInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformInput")
    def platform_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "platformInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullParentInput")
    def pull_parent_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "pullParentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="remoteContextInput")
    def remote_context_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "remoteContextInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="removeInput")
    def remove_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "removeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityOptInput")
    def security_opt_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityOptInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionIdInput")
    def session_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sessionIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shmSizeInput")
    def shm_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "shmSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="squashInput")
    def squash_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "squashInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="suppressOutputInput")
    def suppress_output_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "suppressOutputInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetInput")
    def target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ulimitInput")
    def ulimit_input(self) -> typing.Optional[typing.List["RegistryImageBuildUlimit"]]:
        return typing.cast(typing.Optional[typing.List["RegistryImageBuildUlimit"]], jsii.get(self, "ulimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authConfig")
    def auth_config(self) -> typing.List[RegistryImageBuildAuthConfig]:
        return typing.cast(typing.List[RegistryImageBuildAuthConfig], jsii.get(self, "authConfig"))

    @auth_config.setter
    def auth_config(self, value: typing.List[RegistryImageBuildAuthConfig]) -> None:
        jsii.set(self, "authConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildArgs")
    def build_args(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "buildArgs"))

    @build_args.setter
    def build_args(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "buildArgs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildId")
    def build_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildId"))

    @build_id.setter
    def build_id(self, value: builtins.str) -> None:
        jsii.set(self, "buildId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cacheFrom")
    def cache_from(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cacheFrom"))

    @cache_from.setter
    def cache_from(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "cacheFrom", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cgroupParent")
    def cgroup_parent(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cgroupParent"))

    @cgroup_parent.setter
    def cgroup_parent(self, value: builtins.str) -> None:
        jsii.set(self, "cgroupParent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="context")
    def context(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "context"))

    @context.setter
    def context(self, value: builtins.str) -> None:
        jsii.set(self, "context", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuPeriod")
    def cpu_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuPeriod"))

    @cpu_period.setter
    def cpu_period(self, value: jsii.Number) -> None:
        jsii.set(self, "cpuPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuQuota")
    def cpu_quota(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuQuota"))

    @cpu_quota.setter
    def cpu_quota(self, value: jsii.Number) -> None:
        jsii.set(self, "cpuQuota", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSetCpus")
    def cpu_set_cpus(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuSetCpus"))

    @cpu_set_cpus.setter
    def cpu_set_cpus(self, value: builtins.str) -> None:
        jsii.set(self, "cpuSetCpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSetMems")
    def cpu_set_mems(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuSetMems"))

    @cpu_set_mems.setter
    def cpu_set_mems(self, value: builtins.str) -> None:
        jsii.set(self, "cpuSetMems", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuShares")
    def cpu_shares(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuShares"))

    @cpu_shares.setter
    def cpu_shares(self, value: jsii.Number) -> None:
        jsii.set(self, "cpuShares", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dockerfile")
    def dockerfile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dockerfile"))

    @dockerfile.setter
    def dockerfile(self, value: builtins.str) -> None:
        jsii.set(self, "dockerfile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="extraHosts")
    def extra_hosts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "extraHosts"))

    @extra_hosts.setter
    def extra_hosts(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "extraHosts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceRemove")
    def force_remove(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "forceRemove"))

    @force_remove.setter
    def force_remove(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "forceRemove", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isolation")
    def isolation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "isolation"))

    @isolation.setter
    def isolation(self, value: builtins.str) -> None:
        jsii.set(self, "isolation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labels"))

    @labels.setter
    def labels(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memory")
    def memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memory"))

    @memory.setter
    def memory(self, value: jsii.Number) -> None:
        jsii.set(self, "memory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memorySwap")
    def memory_swap(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memorySwap"))

    @memory_swap.setter
    def memory_swap(self, value: jsii.Number) -> None:
        jsii.set(self, "memorySwap", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkMode")
    def network_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkMode"))

    @network_mode.setter
    def network_mode(self, value: builtins.str) -> None:
        jsii.set(self, "networkMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noCache")
    def no_cache(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noCache"))

    @no_cache.setter
    def no_cache(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "noCache", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platform")
    def platform(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "platform"))

    @platform.setter
    def platform(self, value: builtins.str) -> None:
        jsii.set(self, "platform", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullParent")
    def pull_parent(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "pullParent"))

    @pull_parent.setter
    def pull_parent(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "pullParent", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="remoteContext")
    def remote_context(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "remoteContext"))

    @remote_context.setter
    def remote_context(self, value: builtins.str) -> None:
        jsii.set(self, "remoteContext", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="remove")
    def remove(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "remove"))

    @remove.setter
    def remove(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "remove", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityOpt")
    def security_opt(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityOpt"))

    @security_opt.setter
    def security_opt(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityOpt", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sessionId")
    def session_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sessionId"))

    @session_id.setter
    def session_id(self, value: builtins.str) -> None:
        jsii.set(self, "sessionId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shmSize")
    def shm_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shmSize"))

    @shm_size.setter
    def shm_size(self, value: jsii.Number) -> None:
        jsii.set(self, "shmSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="squash")
    def squash(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "squash"))

    @squash.setter
    def squash(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "squash", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="suppressOutput")
    def suppress_output(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "suppressOutput"))

    @suppress_output.setter
    def suppress_output(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "suppressOutput", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "target"))

    @target.setter
    def target(self, value: builtins.str) -> None:
        jsii.set(self, "target", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ulimit")
    def ulimit(self) -> typing.List["RegistryImageBuildUlimit"]:
        return typing.cast(typing.List["RegistryImageBuildUlimit"], jsii.get(self, "ulimit"))

    @ulimit.setter
    def ulimit(self, value: typing.List["RegistryImageBuildUlimit"]) -> None:
        jsii.set(self, "ulimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        jsii.set(self, "version", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RegistryImageBuild]:
        return typing.cast(typing.Optional[RegistryImageBuild], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[RegistryImageBuild]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.RegistryImageBuildUlimit",
    jsii_struct_bases=[],
    name_mapping={"hard": "hard", "name": "name", "soft": "soft"},
)
class RegistryImageBuildUlimit:
    def __init__(
        self,
        *,
        hard: jsii.Number,
        name: builtins.str,
        soft: jsii.Number,
    ) -> None:
        '''
        :param hard: soft limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#hard RegistryImage#hard}
        :param name: type of ulimit, e.g. ``nofile``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#name RegistryImage#name}
        :param soft: hard limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#soft RegistryImage#soft}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hard": hard,
            "name": name,
            "soft": soft,
        }

    @builtins.property
    def hard(self) -> jsii.Number:
        '''soft limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#hard RegistryImage#hard}
        '''
        result = self._values.get("hard")
        assert result is not None, "Required property 'hard' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''type of ulimit, e.g. ``nofile``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#name RegistryImage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def soft(self) -> jsii.Number:
        '''hard limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#soft RegistryImage#soft}
        '''
        result = self._values.get("soft")
        assert result is not None, "Required property 'soft' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistryImageBuildUlimit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.RegistryImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "build_attribute": "buildAttribute",
        "insecure_skip_verify": "insecureSkipVerify",
        "keep_remotely": "keepRemotely",
    },
)
class RegistryImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        build_attribute: typing.Optional[RegistryImageBuild] = None,
        insecure_skip_verify: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        keep_remotely: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#name RegistryImage#name}
        :param build_attribute: build block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#build RegistryImage#build}
        :param insecure_skip_verify: If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#insecure_skip_verify RegistryImage#insecure_skip_verify}
        :param keep_remotely: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker registry on destroy operation. Defaults to ``false`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#keep_remotely RegistryImage#keep_remotely}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(build_attribute, dict):
            build_attribute = RegistryImageBuild(**build_attribute)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if build_attribute is not None:
            self._values["build_attribute"] = build_attribute
        if insecure_skip_verify is not None:
            self._values["insecure_skip_verify"] = insecure_skip_verify
        if keep_remotely is not None:
            self._values["keep_remotely"] = keep_remotely

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
    def name(self) -> builtins.str:
        '''The name of the Docker image.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#name RegistryImage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_attribute(self) -> typing.Optional[RegistryImageBuild]:
        '''build block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#build RegistryImage#build}
        '''
        result = self._values.get("build_attribute")
        return typing.cast(typing.Optional[RegistryImageBuild], result)

    @builtins.property
    def insecure_skip_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#insecure_skip_verify RegistryImage#insecure_skip_verify}
        '''
        result = self._values.get("insecure_skip_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def keep_remotely(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''If true, then the Docker image won't be deleted on destroy operation.

        If this is false, it will delete the image from the docker registry on destroy operation. Defaults to ``false``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image#keep_remotely RegistryImage#keep_remotely}
        '''
        result = self._values.get("keep_remotely")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistryImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Secret(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Secret",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/secret docker_secret}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        data: builtins.str,
        name: builtins.str,
        labels: typing.Optional[typing.Sequence["SecretLabels"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/secret docker_secret} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param data: Base64-url-safe-encoded secret data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#data Secret#data}
        :param name: User-defined name of the secret. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#name Secret#name}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#labels Secret#labels}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecretConfig(
            data=data,
            name=name,
            labels=labels,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

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
    @jsii.member(jsii_name="dataInput")
    def data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["SecretLabels"]]:
        return typing.cast(typing.Optional[typing.List["SecretLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @data.setter
    def data(self, value: builtins.str) -> None:
        jsii.set(self, "data", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["SecretLabels"]:
        return typing.cast(typing.List["SecretLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["SecretLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.SecretConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "data": "data",
        "name": "name",
        "labels": "labels",
    },
)
class SecretConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        data: builtins.str,
        name: builtins.str,
        labels: typing.Optional[typing.Sequence["SecretLabels"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param data: Base64-url-safe-encoded secret data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#data Secret#data}
        :param name: User-defined name of the secret. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#name Secret#name}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#labels Secret#labels}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "data": data,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if labels is not None:
            self._values["labels"] = labels

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
    def data(self) -> builtins.str:
        '''Base64-url-safe-encoded secret data.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#data Secret#data}
        '''
        result = self._values.get("data")
        assert result is not None, "Required property 'data' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''User-defined name of the secret.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#name Secret#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["SecretLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#labels Secret#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["SecretLabels"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.SecretLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class SecretLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#label Secret#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#value Secret#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#label Secret#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret#value Secret#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Service(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Service",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/service docker_service}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        task_spec: "ServiceTaskSpec",
        auth: typing.Optional["ServiceAuth"] = None,
        converge_config: typing.Optional["ServiceConvergeConfig"] = None,
        endpoint_spec: typing.Optional["ServiceEndpointSpec"] = None,
        labels: typing.Optional[typing.Sequence["ServiceLabels"]] = None,
        mode: typing.Optional["ServiceMode"] = None,
        rollback_config: typing.Optional["ServiceRollbackConfig"] = None,
        update_config: typing.Optional["ServiceUpdateConfig"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/service docker_service} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#name Service#name}
        :param task_spec: task_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#task_spec Service#task_spec}
        :param auth: auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#auth Service#auth}
        :param converge_config: converge_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#converge_config Service#converge_config}
        :param endpoint_spec: endpoint_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#endpoint_spec Service#endpoint_spec}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#labels Service#labels}
        :param mode: mode block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mode Service#mode}
        :param rollback_config: rollback_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#rollback_config Service#rollback_config}
        :param update_config: update_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#update_config Service#update_config}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceConfig(
            name=name,
            task_spec=task_spec,
            auth=auth,
            converge_config=converge_config,
            endpoint_spec=endpoint_spec,
            labels=labels,
            mode=mode,
            rollback_config=rollback_config,
            update_config=update_config,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAuth")
    def put_auth(
        self,
        *,
        server_address: builtins.str,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param server_address: The address of the server for the authentication. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#server_address Service#server_address}
        :param password: The password. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#password Service#password}
        :param username: The username. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#username Service#username}
        '''
        value = ServiceAuth(
            server_address=server_address, password=password, username=username
        )

        return typing.cast(None, jsii.invoke(self, "putAuth", [value]))

    @jsii.member(jsii_name="putConvergeConfig")
    def put_converge_config(
        self,
        *,
        delay: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delay: The interval to check if the desired state is reached (ms|s). Defaults to ``7s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        :param timeout: The timeout of the service to reach the desired state (s|m). Defaults to ``3m``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#timeout Service#timeout}
        '''
        value = ServiceConvergeConfig(delay=delay, timeout=timeout)

        return typing.cast(None, jsii.invoke(self, "putConvergeConfig", [value]))

    @jsii.member(jsii_name="putEndpointSpec")
    def put_endpoint_spec(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        ports: typing.Optional[typing.Sequence["ServiceEndpointSpecPorts"]] = None,
    ) -> None:
        '''
        :param mode: The mode of resolution to use for internal load balancing between tasks. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mode Service#mode}
        :param ports: ports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#ports Service#ports}
        '''
        value = ServiceEndpointSpec(mode=mode, ports=ports)

        return typing.cast(None, jsii.invoke(self, "putEndpointSpec", [value]))

    @jsii.member(jsii_name="putMode")
    def put_mode(
        self,
        *,
        global_: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        replicated: typing.Optional["ServiceModeReplicated"] = None,
    ) -> None:
        '''
        :param global_: The global service mode. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#global Service#global}
        :param replicated: replicated block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#replicated Service#replicated}
        '''
        value = ServiceMode(global_=global_, replicated=replicated)

        return typing.cast(None, jsii.invoke(self, "putMode", [value]))

    @jsii.member(jsii_name="putRollbackConfig")
    def put_rollback_config(
        self,
        *,
        delay: typing.Optional[builtins.str] = None,
        failure_action: typing.Optional[builtins.str] = None,
        max_failure_ratio: typing.Optional[builtins.str] = None,
        monitor: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        parallelism: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param delay: Delay between task rollbacks (ns|us|ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        :param failure_action: Action on rollback failure: pause | continue. Defaults to ``pause``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#failure_action Service#failure_action}
        :param max_failure_ratio: Failure rate to tolerate during a rollback. Defaults to ``0.0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_failure_ratio Service#max_failure_ratio}
        :param monitor: Duration after each task rollback to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#monitor Service#monitor}
        :param order: Rollback order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#order Service#order}
        :param parallelism: Maximum number of tasks to be rollbacked in one iteration. Defaults to ``1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#parallelism Service#parallelism}
        '''
        value = ServiceRollbackConfig(
            delay=delay,
            failure_action=failure_action,
            max_failure_ratio=max_failure_ratio,
            monitor=monitor,
            order=order,
            parallelism=parallelism,
        )

        return typing.cast(None, jsii.invoke(self, "putRollbackConfig", [value]))

    @jsii.member(jsii_name="putTaskSpec")
    def put_task_spec(
        self,
        *,
        container_spec: "ServiceTaskSpecContainerSpec",
        force_update: typing.Optional[jsii.Number] = None,
        log_driver: typing.Optional["ServiceTaskSpecLogDriver"] = None,
        networks: typing.Optional[typing.Sequence[builtins.str]] = None,
        placement: typing.Optional["ServiceTaskSpecPlacement"] = None,
        resources: typing.Optional["ServiceTaskSpecResources"] = None,
        restart_policy: typing.Optional["ServiceTaskSpecRestartPolicy"] = None,
        runtime: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param container_spec: container_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#container_spec Service#container_spec}
        :param force_update: A counter that triggers an update even if no relevant parameters have been changed. See the `spec <https://github.com/docker/swarmkit/blob/master/api/specs.proto#L126>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#force_update Service#force_update}
        :param log_driver: log_driver block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#log_driver Service#log_driver}
        :param networks: Ids of the networks in which the container will be put in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#networks Service#networks}
        :param placement: placement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#placement Service#placement}
        :param resources: resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#resources Service#resources}
        :param restart_policy: restart_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#restart_policy Service#restart_policy}
        :param runtime: Runtime is the type of runtime specified for the task executor. See the `types <https://github.com/moby/moby/blob/master/api/types/swarm/runtime.go>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#runtime Service#runtime}
        '''
        value = ServiceTaskSpec(
            container_spec=container_spec,
            force_update=force_update,
            log_driver=log_driver,
            networks=networks,
            placement=placement,
            resources=resources,
            restart_policy=restart_policy,
            runtime=runtime,
        )

        return typing.cast(None, jsii.invoke(self, "putTaskSpec", [value]))

    @jsii.member(jsii_name="putUpdateConfig")
    def put_update_config(
        self,
        *,
        delay: typing.Optional[builtins.str] = None,
        failure_action: typing.Optional[builtins.str] = None,
        max_failure_ratio: typing.Optional[builtins.str] = None,
        monitor: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        parallelism: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param delay: Delay between task updates (ns|us|ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        :param failure_action: Action on update failure: pause | continue | rollback. Defaults to ``pause``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#failure_action Service#failure_action}
        :param max_failure_ratio: Failure rate to tolerate during an update. Defaults to ``0.0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_failure_ratio Service#max_failure_ratio}
        :param monitor: Duration after each task update to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#monitor Service#monitor}
        :param order: Update order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#order Service#order}
        :param parallelism: Maximum number of tasks to be updated in one iteration. Defaults to ``1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#parallelism Service#parallelism}
        '''
        value = ServiceUpdateConfig(
            delay=delay,
            failure_action=failure_action,
            max_failure_ratio=max_failure_ratio,
            monitor=monitor,
            order=order,
            parallelism=parallelism,
        )

        return typing.cast(None, jsii.invoke(self, "putUpdateConfig", [value]))

    @jsii.member(jsii_name="resetAuth")
    def reset_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuth", []))

    @jsii.member(jsii_name="resetConvergeConfig")
    def reset_converge_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConvergeConfig", []))

    @jsii.member(jsii_name="resetEndpointSpec")
    def reset_endpoint_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointSpec", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetRollbackConfig")
    def reset_rollback_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollbackConfig", []))

    @jsii.member(jsii_name="resetUpdateConfig")
    def reset_update_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdateConfig", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auth")
    def auth(self) -> "ServiceAuthOutputReference":
        return typing.cast("ServiceAuthOutputReference", jsii.get(self, "auth"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="convergeConfig")
    def converge_config(self) -> "ServiceConvergeConfigOutputReference":
        return typing.cast("ServiceConvergeConfigOutputReference", jsii.get(self, "convergeConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointSpec")
    def endpoint_spec(self) -> "ServiceEndpointSpecOutputReference":
        return typing.cast("ServiceEndpointSpecOutputReference", jsii.get(self, "endpointSpec"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> "ServiceModeOutputReference":
        return typing.cast("ServiceModeOutputReference", jsii.get(self, "mode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rollbackConfig")
    def rollback_config(self) -> "ServiceRollbackConfigOutputReference":
        return typing.cast("ServiceRollbackConfigOutputReference", jsii.get(self, "rollbackConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskSpec")
    def task_spec(self) -> "ServiceTaskSpecOutputReference":
        return typing.cast("ServiceTaskSpecOutputReference", jsii.get(self, "taskSpec"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateConfig")
    def update_config(self) -> "ServiceUpdateConfigOutputReference":
        return typing.cast("ServiceUpdateConfigOutputReference", jsii.get(self, "updateConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authInput")
    def auth_input(self) -> typing.Optional["ServiceAuth"]:
        return typing.cast(typing.Optional["ServiceAuth"], jsii.get(self, "authInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="convergeConfigInput")
    def converge_config_input(self) -> typing.Optional["ServiceConvergeConfig"]:
        return typing.cast(typing.Optional["ServiceConvergeConfig"], jsii.get(self, "convergeConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointSpecInput")
    def endpoint_spec_input(self) -> typing.Optional["ServiceEndpointSpec"]:
        return typing.cast(typing.Optional["ServiceEndpointSpec"], jsii.get(self, "endpointSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["ServiceLabels"]]:
        return typing.cast(typing.Optional[typing.List["ServiceLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional["ServiceMode"]:
        return typing.cast(typing.Optional["ServiceMode"], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rollbackConfigInput")
    def rollback_config_input(self) -> typing.Optional["ServiceRollbackConfig"]:
        return typing.cast(typing.Optional["ServiceRollbackConfig"], jsii.get(self, "rollbackConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskSpecInput")
    def task_spec_input(self) -> typing.Optional["ServiceTaskSpec"]:
        return typing.cast(typing.Optional["ServiceTaskSpec"], jsii.get(self, "taskSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateConfigInput")
    def update_config_input(self) -> typing.Optional["ServiceUpdateConfig"]:
        return typing.cast(typing.Optional["ServiceUpdateConfig"], jsii.get(self, "updateConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["ServiceLabels"]:
        return typing.cast(typing.List["ServiceLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["ServiceLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceAuth",
    jsii_struct_bases=[],
    name_mapping={
        "server_address": "serverAddress",
        "password": "password",
        "username": "username",
    },
)
class ServiceAuth:
    def __init__(
        self,
        *,
        server_address: builtins.str,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param server_address: The address of the server for the authentication. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#server_address Service#server_address}
        :param password: The password. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#password Service#password}
        :param username: The username. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#username Service#username}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "server_address": server_address,
        }
        if password is not None:
            self._values["password"] = password
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def server_address(self) -> builtins.str:
        '''The address of the server for the authentication.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#server_address Service#server_address}
        '''
        result = self._values.get("server_address")
        assert result is not None, "Required property 'server_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The password.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#password Service#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The username.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#username Service#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceAuthOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceAuthOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverAddressInput")
    def server_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        jsii.set(self, "password", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serverAddress")
    def server_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serverAddress"))

    @server_address.setter
    def server_address(self, value: builtins.str) -> None:
        jsii.set(self, "serverAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        jsii.set(self, "username", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceAuth]:
        return typing.cast(typing.Optional[ServiceAuth], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceAuth]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "task_spec": "taskSpec",
        "auth": "auth",
        "converge_config": "convergeConfig",
        "endpoint_spec": "endpointSpec",
        "labels": "labels",
        "mode": "mode",
        "rollback_config": "rollbackConfig",
        "update_config": "updateConfig",
    },
)
class ServiceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        task_spec: "ServiceTaskSpec",
        auth: typing.Optional[ServiceAuth] = None,
        converge_config: typing.Optional["ServiceConvergeConfig"] = None,
        endpoint_spec: typing.Optional["ServiceEndpointSpec"] = None,
        labels: typing.Optional[typing.Sequence["ServiceLabels"]] = None,
        mode: typing.Optional["ServiceMode"] = None,
        rollback_config: typing.Optional["ServiceRollbackConfig"] = None,
        update_config: typing.Optional["ServiceUpdateConfig"] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Name of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#name Service#name}
        :param task_spec: task_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#task_spec Service#task_spec}
        :param auth: auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#auth Service#auth}
        :param converge_config: converge_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#converge_config Service#converge_config}
        :param endpoint_spec: endpoint_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#endpoint_spec Service#endpoint_spec}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#labels Service#labels}
        :param mode: mode block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mode Service#mode}
        :param rollback_config: rollback_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#rollback_config Service#rollback_config}
        :param update_config: update_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#update_config Service#update_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(task_spec, dict):
            task_spec = ServiceTaskSpec(**task_spec)
        if isinstance(auth, dict):
            auth = ServiceAuth(**auth)
        if isinstance(converge_config, dict):
            converge_config = ServiceConvergeConfig(**converge_config)
        if isinstance(endpoint_spec, dict):
            endpoint_spec = ServiceEndpointSpec(**endpoint_spec)
        if isinstance(mode, dict):
            mode = ServiceMode(**mode)
        if isinstance(rollback_config, dict):
            rollback_config = ServiceRollbackConfig(**rollback_config)
        if isinstance(update_config, dict):
            update_config = ServiceUpdateConfig(**update_config)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "task_spec": task_spec,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auth is not None:
            self._values["auth"] = auth
        if converge_config is not None:
            self._values["converge_config"] = converge_config
        if endpoint_spec is not None:
            self._values["endpoint_spec"] = endpoint_spec
        if labels is not None:
            self._values["labels"] = labels
        if mode is not None:
            self._values["mode"] = mode
        if rollback_config is not None:
            self._values["rollback_config"] = rollback_config
        if update_config is not None:
            self._values["update_config"] = update_config

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
    def name(self) -> builtins.str:
        '''Name of the service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#name Service#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task_spec(self) -> "ServiceTaskSpec":
        '''task_spec block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#task_spec Service#task_spec}
        '''
        result = self._values.get("task_spec")
        assert result is not None, "Required property 'task_spec' is missing"
        return typing.cast("ServiceTaskSpec", result)

    @builtins.property
    def auth(self) -> typing.Optional[ServiceAuth]:
        '''auth block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#auth Service#auth}
        '''
        result = self._values.get("auth")
        return typing.cast(typing.Optional[ServiceAuth], result)

    @builtins.property
    def converge_config(self) -> typing.Optional["ServiceConvergeConfig"]:
        '''converge_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#converge_config Service#converge_config}
        '''
        result = self._values.get("converge_config")
        return typing.cast(typing.Optional["ServiceConvergeConfig"], result)

    @builtins.property
    def endpoint_spec(self) -> typing.Optional["ServiceEndpointSpec"]:
        '''endpoint_spec block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#endpoint_spec Service#endpoint_spec}
        '''
        result = self._values.get("endpoint_spec")
        return typing.cast(typing.Optional["ServiceEndpointSpec"], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["ServiceLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#labels Service#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ServiceLabels"]], result)

    @builtins.property
    def mode(self) -> typing.Optional["ServiceMode"]:
        '''mode block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mode Service#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional["ServiceMode"], result)

    @builtins.property
    def rollback_config(self) -> typing.Optional["ServiceRollbackConfig"]:
        '''rollback_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#rollback_config Service#rollback_config}
        '''
        result = self._values.get("rollback_config")
        return typing.cast(typing.Optional["ServiceRollbackConfig"], result)

    @builtins.property
    def update_config(self) -> typing.Optional["ServiceUpdateConfig"]:
        '''update_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#update_config Service#update_config}
        '''
        result = self._values.get("update_config")
        return typing.cast(typing.Optional["ServiceUpdateConfig"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceConvergeConfig",
    jsii_struct_bases=[],
    name_mapping={"delay": "delay", "timeout": "timeout"},
)
class ServiceConvergeConfig:
    def __init__(
        self,
        *,
        delay: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delay: The interval to check if the desired state is reached (ms|s). Defaults to ``7s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        :param timeout: The timeout of the service to reach the desired state (s|m). Defaults to ``3m``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#timeout Service#timeout}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delay is not None:
            self._values["delay"] = delay
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def delay(self) -> typing.Optional[builtins.str]:
        '''The interval to check if the desired state is reached (ms|s). Defaults to ``7s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        '''
        result = self._values.get("delay")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''The timeout of the service to reach the desired state (s|m). Defaults to ``3m``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#timeout Service#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceConvergeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceConvergeConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceConvergeConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetDelay")
    def reset_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelay", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delayInput")
    def delay_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "delayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delay")
    def delay(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delay"))

    @delay.setter
    def delay(self, value: builtins.str) -> None:
        jsii.set(self, "delay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: builtins.str) -> None:
        jsii.set(self, "timeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceConvergeConfig]:
        return typing.cast(typing.Optional[ServiceConvergeConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceConvergeConfig]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceEndpointSpec",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "ports": "ports"},
)
class ServiceEndpointSpec:
    def __init__(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        ports: typing.Optional[typing.Sequence["ServiceEndpointSpecPorts"]] = None,
    ) -> None:
        '''
        :param mode: The mode of resolution to use for internal load balancing between tasks. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mode Service#mode}
        :param ports: ports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#ports Service#ports}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if ports is not None:
            self._values["ports"] = ports

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''The mode of resolution to use for internal load balancing between tasks.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mode Service#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List["ServiceEndpointSpecPorts"]]:
        '''ports block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#ports Service#ports}
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List["ServiceEndpointSpecPorts"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEndpointSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceEndpointSpecOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceEndpointSpecOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetPorts")
    def reset_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPorts", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portsInput")
    def ports_input(self) -> typing.Optional[typing.List["ServiceEndpointSpecPorts"]]:
        return typing.cast(typing.Optional[typing.List["ServiceEndpointSpecPorts"]], jsii.get(self, "portsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        jsii.set(self, "mode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.List["ServiceEndpointSpecPorts"]:
        return typing.cast(typing.List["ServiceEndpointSpecPorts"], jsii.get(self, "ports"))

    @ports.setter
    def ports(self, value: typing.List["ServiceEndpointSpecPorts"]) -> None:
        jsii.set(self, "ports", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceEndpointSpec]:
        return typing.cast(typing.Optional[ServiceEndpointSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceEndpointSpec]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceEndpointSpecPorts",
    jsii_struct_bases=[],
    name_mapping={
        "target_port": "targetPort",
        "name": "name",
        "protocol": "protocol",
        "published_port": "publishedPort",
        "publish_mode": "publishMode",
    },
)
class ServiceEndpointSpecPorts:
    def __init__(
        self,
        *,
        target_port: jsii.Number,
        name: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        published_port: typing.Optional[jsii.Number] = None,
        publish_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target_port: The port inside the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#target_port Service#target_port}
        :param name: A random name for the port. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#name Service#name}
        :param protocol: Rrepresents the protocol of a port: 'tcp', 'udp' or 'sctp'. Defaults to ``tcp``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#protocol Service#protocol}
        :param published_port: The port on the swarm hosts. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#published_port Service#published_port}
        :param publish_mode: Represents the mode in which the port is to be published: 'ingress' or 'host'. Defaults to ``ingress``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#publish_mode Service#publish_mode}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_port": target_port,
        }
        if name is not None:
            self._values["name"] = name
        if protocol is not None:
            self._values["protocol"] = protocol
        if published_port is not None:
            self._values["published_port"] = published_port
        if publish_mode is not None:
            self._values["publish_mode"] = publish_mode

    @builtins.property
    def target_port(self) -> jsii.Number:
        '''The port inside the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#target_port Service#target_port}
        '''
        result = self._values.get("target_port")
        assert result is not None, "Required property 'target_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''A random name for the port.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#name Service#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Rrepresents the protocol of a port: 'tcp', 'udp' or 'sctp'. Defaults to ``tcp``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#protocol Service#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def published_port(self) -> typing.Optional[jsii.Number]:
        '''The port on the swarm hosts.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#published_port Service#published_port}
        '''
        result = self._values.get("published_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def publish_mode(self) -> typing.Optional[builtins.str]:
        '''Represents the mode in which the port is to be published: 'ingress' or 'host'. Defaults to ``ingress``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#publish_mode Service#publish_mode}
        '''
        result = self._values.get("publish_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEndpointSpecPorts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ServiceLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#label Service#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#value Service#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#label Service#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#value Service#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceMode",
    jsii_struct_bases=[],
    name_mapping={"global_": "global", "replicated": "replicated"},
)
class ServiceMode:
    def __init__(
        self,
        *,
        global_: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        replicated: typing.Optional["ServiceModeReplicated"] = None,
    ) -> None:
        '''
        :param global_: The global service mode. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#global Service#global}
        :param replicated: replicated block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#replicated Service#replicated}
        '''
        if isinstance(replicated, dict):
            replicated = ServiceModeReplicated(**replicated)
        self._values: typing.Dict[str, typing.Any] = {}
        if global_ is not None:
            self._values["global_"] = global_
        if replicated is not None:
            self._values["replicated"] = replicated

    @builtins.property
    def global_(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''The global service mode. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#global Service#global}
        '''
        result = self._values.get("global_")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def replicated(self) -> typing.Optional["ServiceModeReplicated"]:
        '''replicated block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#replicated Service#replicated}
        '''
        result = self._values.get("replicated")
        return typing.cast(typing.Optional["ServiceModeReplicated"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceModeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceModeOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putReplicated")
    def put_replicated(self, *, replicas: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param replicas: The amount of replicas of the service. Defaults to ``1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#replicas Service#replicas}
        '''
        value = ServiceModeReplicated(replicas=replicas)

        return typing.cast(None, jsii.invoke(self, "putReplicated", [value]))

    @jsii.member(jsii_name="resetGlobal")
    def reset_global(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlobal", []))

    @jsii.member(jsii_name="resetReplicated")
    def reset_replicated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicated", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicated")
    def replicated(self) -> "ServiceModeReplicatedOutputReference":
        return typing.cast("ServiceModeReplicatedOutputReference", jsii.get(self, "replicated"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalInput")
    def global_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "globalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicatedInput")
    def replicated_input(self) -> typing.Optional["ServiceModeReplicated"]:
        return typing.cast(typing.Optional["ServiceModeReplicated"], jsii.get(self, "replicatedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="global")
    def global_(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "global"))

    @global_.setter
    def global_(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "global", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceMode]:
        return typing.cast(typing.Optional[ServiceMode], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceMode]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceModeReplicated",
    jsii_struct_bases=[],
    name_mapping={"replicas": "replicas"},
)
class ServiceModeReplicated:
    def __init__(self, *, replicas: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param replicas: The amount of replicas of the service. Defaults to ``1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#replicas Service#replicas}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if replicas is not None:
            self._values["replicas"] = replicas

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        '''The amount of replicas of the service. Defaults to ``1``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#replicas Service#replicas}
        '''
        result = self._values.get("replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceModeReplicated(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceModeReplicatedOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceModeReplicatedOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetReplicas")
    def reset_replicas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicas", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicasInput")
    def replicas_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "replicasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="replicas")
    def replicas(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "replicas"))

    @replicas.setter
    def replicas(self, value: jsii.Number) -> None:
        jsii.set(self, "replicas", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceModeReplicated]:
        return typing.cast(typing.Optional[ServiceModeReplicated], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceModeReplicated]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceRollbackConfig",
    jsii_struct_bases=[],
    name_mapping={
        "delay": "delay",
        "failure_action": "failureAction",
        "max_failure_ratio": "maxFailureRatio",
        "monitor": "monitor",
        "order": "order",
        "parallelism": "parallelism",
    },
)
class ServiceRollbackConfig:
    def __init__(
        self,
        *,
        delay: typing.Optional[builtins.str] = None,
        failure_action: typing.Optional[builtins.str] = None,
        max_failure_ratio: typing.Optional[builtins.str] = None,
        monitor: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        parallelism: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param delay: Delay between task rollbacks (ns|us|ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        :param failure_action: Action on rollback failure: pause | continue. Defaults to ``pause``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#failure_action Service#failure_action}
        :param max_failure_ratio: Failure rate to tolerate during a rollback. Defaults to ``0.0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_failure_ratio Service#max_failure_ratio}
        :param monitor: Duration after each task rollback to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#monitor Service#monitor}
        :param order: Rollback order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#order Service#order}
        :param parallelism: Maximum number of tasks to be rollbacked in one iteration. Defaults to ``1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#parallelism Service#parallelism}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delay is not None:
            self._values["delay"] = delay
        if failure_action is not None:
            self._values["failure_action"] = failure_action
        if max_failure_ratio is not None:
            self._values["max_failure_ratio"] = max_failure_ratio
        if monitor is not None:
            self._values["monitor"] = monitor
        if order is not None:
            self._values["order"] = order
        if parallelism is not None:
            self._values["parallelism"] = parallelism

    @builtins.property
    def delay(self) -> typing.Optional[builtins.str]:
        '''Delay between task rollbacks (ns|us|ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        '''
        result = self._values.get("delay")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def failure_action(self) -> typing.Optional[builtins.str]:
        '''Action on rollback failure: pause | continue. Defaults to ``pause``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#failure_action Service#failure_action}
        '''
        result = self._values.get("failure_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_failure_ratio(self) -> typing.Optional[builtins.str]:
        '''Failure rate to tolerate during a rollback. Defaults to ``0.0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_failure_ratio Service#max_failure_ratio}
        '''
        result = self._values.get("max_failure_ratio")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monitor(self) -> typing.Optional[builtins.str]:
        '''Duration after each task rollback to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#monitor Service#monitor}
        '''
        result = self._values.get("monitor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''Rollback order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#order Service#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parallelism(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of tasks to be rollbacked in one iteration. Defaults to ``1``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#parallelism Service#parallelism}
        '''
        result = self._values.get("parallelism")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceRollbackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceRollbackConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceRollbackConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetDelay")
    def reset_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelay", []))

    @jsii.member(jsii_name="resetFailureAction")
    def reset_failure_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailureAction", []))

    @jsii.member(jsii_name="resetMaxFailureRatio")
    def reset_max_failure_ratio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxFailureRatio", []))

    @jsii.member(jsii_name="resetMonitor")
    def reset_monitor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMonitor", []))

    @jsii.member(jsii_name="resetOrder")
    def reset_order(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrder", []))

    @jsii.member(jsii_name="resetParallelism")
    def reset_parallelism(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParallelism", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delayInput")
    def delay_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "delayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureActionInput")
    def failure_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "failureActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxFailureRatioInput")
    def max_failure_ratio_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxFailureRatioInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitorInput")
    def monitor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "monitorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="orderInput")
    def order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parallelismInput")
    def parallelism_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "parallelismInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delay")
    def delay(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delay"))

    @delay.setter
    def delay(self, value: builtins.str) -> None:
        jsii.set(self, "delay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureAction")
    def failure_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "failureAction"))

    @failure_action.setter
    def failure_action(self, value: builtins.str) -> None:
        jsii.set(self, "failureAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxFailureRatio")
    def max_failure_ratio(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxFailureRatio"))

    @max_failure_ratio.setter
    def max_failure_ratio(self, value: builtins.str) -> None:
        jsii.set(self, "maxFailureRatio", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitor")
    def monitor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitor"))

    @monitor.setter
    def monitor(self, value: builtins.str) -> None:
        jsii.set(self, "monitor", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="order")
    def order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "order"))

    @order.setter
    def order(self, value: builtins.str) -> None:
        jsii.set(self, "order", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parallelism")
    def parallelism(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "parallelism"))

    @parallelism.setter
    def parallelism(self, value: jsii.Number) -> None:
        jsii.set(self, "parallelism", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceRollbackConfig]:
        return typing.cast(typing.Optional[ServiceRollbackConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceRollbackConfig]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpec",
    jsii_struct_bases=[],
    name_mapping={
        "container_spec": "containerSpec",
        "force_update": "forceUpdate",
        "log_driver": "logDriver",
        "networks": "networks",
        "placement": "placement",
        "resources": "resources",
        "restart_policy": "restartPolicy",
        "runtime": "runtime",
    },
)
class ServiceTaskSpec:
    def __init__(
        self,
        *,
        container_spec: "ServiceTaskSpecContainerSpec",
        force_update: typing.Optional[jsii.Number] = None,
        log_driver: typing.Optional["ServiceTaskSpecLogDriver"] = None,
        networks: typing.Optional[typing.Sequence[builtins.str]] = None,
        placement: typing.Optional["ServiceTaskSpecPlacement"] = None,
        resources: typing.Optional["ServiceTaskSpecResources"] = None,
        restart_policy: typing.Optional["ServiceTaskSpecRestartPolicy"] = None,
        runtime: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param container_spec: container_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#container_spec Service#container_spec}
        :param force_update: A counter that triggers an update even if no relevant parameters have been changed. See the `spec <https://github.com/docker/swarmkit/blob/master/api/specs.proto#L126>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#force_update Service#force_update}
        :param log_driver: log_driver block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#log_driver Service#log_driver}
        :param networks: Ids of the networks in which the container will be put in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#networks Service#networks}
        :param placement: placement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#placement Service#placement}
        :param resources: resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#resources Service#resources}
        :param restart_policy: restart_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#restart_policy Service#restart_policy}
        :param runtime: Runtime is the type of runtime specified for the task executor. See the `types <https://github.com/moby/moby/blob/master/api/types/swarm/runtime.go>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#runtime Service#runtime}
        '''
        if isinstance(container_spec, dict):
            container_spec = ServiceTaskSpecContainerSpec(**container_spec)
        if isinstance(log_driver, dict):
            log_driver = ServiceTaskSpecLogDriver(**log_driver)
        if isinstance(placement, dict):
            placement = ServiceTaskSpecPlacement(**placement)
        if isinstance(resources, dict):
            resources = ServiceTaskSpecResources(**resources)
        if isinstance(restart_policy, dict):
            restart_policy = ServiceTaskSpecRestartPolicy(**restart_policy)
        self._values: typing.Dict[str, typing.Any] = {
            "container_spec": container_spec,
        }
        if force_update is not None:
            self._values["force_update"] = force_update
        if log_driver is not None:
            self._values["log_driver"] = log_driver
        if networks is not None:
            self._values["networks"] = networks
        if placement is not None:
            self._values["placement"] = placement
        if resources is not None:
            self._values["resources"] = resources
        if restart_policy is not None:
            self._values["restart_policy"] = restart_policy
        if runtime is not None:
            self._values["runtime"] = runtime

    @builtins.property
    def container_spec(self) -> "ServiceTaskSpecContainerSpec":
        '''container_spec block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#container_spec Service#container_spec}
        '''
        result = self._values.get("container_spec")
        assert result is not None, "Required property 'container_spec' is missing"
        return typing.cast("ServiceTaskSpecContainerSpec", result)

    @builtins.property
    def force_update(self) -> typing.Optional[jsii.Number]:
        '''A counter that triggers an update even if no relevant parameters have been changed. See the `spec <https://github.com/docker/swarmkit/blob/master/api/specs.proto#L126>`_.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#force_update Service#force_update}
        '''
        result = self._values.get("force_update")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_driver(self) -> typing.Optional["ServiceTaskSpecLogDriver"]:
        '''log_driver block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#log_driver Service#log_driver}
        '''
        result = self._values.get("log_driver")
        return typing.cast(typing.Optional["ServiceTaskSpecLogDriver"], result)

    @builtins.property
    def networks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Ids of the networks in which the  container will be put in.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#networks Service#networks}
        '''
        result = self._values.get("networks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def placement(self) -> typing.Optional["ServiceTaskSpecPlacement"]:
        '''placement block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#placement Service#placement}
        '''
        result = self._values.get("placement")
        return typing.cast(typing.Optional["ServiceTaskSpecPlacement"], result)

    @builtins.property
    def resources(self) -> typing.Optional["ServiceTaskSpecResources"]:
        '''resources block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#resources Service#resources}
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional["ServiceTaskSpecResources"], result)

    @builtins.property
    def restart_policy(self) -> typing.Optional["ServiceTaskSpecRestartPolicy"]:
        '''restart_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#restart_policy Service#restart_policy}
        '''
        result = self._values.get("restart_policy")
        return typing.cast(typing.Optional["ServiceTaskSpecRestartPolicy"], result)

    @builtins.property
    def runtime(self) -> typing.Optional[builtins.str]:
        '''Runtime is the type of runtime specified for the task executor. See the `types <https://github.com/moby/moby/blob/master/api/types/swarm/runtime.go>`_.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#runtime Service#runtime}
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpec",
    jsii_struct_bases=[],
    name_mapping={
        "image": "image",
        "args": "args",
        "command": "command",
        "configs": "configs",
        "dir": "dir",
        "dns_config": "dnsConfig",
        "env": "env",
        "groups": "groups",
        "healthcheck": "healthcheck",
        "hostname": "hostname",
        "hosts": "hosts",
        "isolation": "isolation",
        "labels": "labels",
        "mounts": "mounts",
        "privileges": "privileges",
        "read_only": "readOnly",
        "secrets": "secrets",
        "stop_grace_period": "stopGracePeriod",
        "stop_signal": "stopSignal",
        "user": "user",
    },
)
class ServiceTaskSpecContainerSpec:
    def __init__(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        configs: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecConfigs"]] = None,
        dir: typing.Optional[builtins.str] = None,
        dns_config: typing.Optional["ServiceTaskSpecContainerSpecDnsConfig"] = None,
        env: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        healthcheck: typing.Optional["ServiceTaskSpecContainerSpecHealthcheck"] = None,
        hostname: typing.Optional[builtins.str] = None,
        hosts: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecHosts"]] = None,
        isolation: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecLabels"]] = None,
        mounts: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecMounts"]] = None,
        privileges: typing.Optional["ServiceTaskSpecContainerSpecPrivileges"] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        secrets: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecSecrets"]] = None,
        stop_grace_period: typing.Optional[builtins.str] = None,
        stop_signal: typing.Optional[builtins.str] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image: The image name to use for the containers of the service, like ``nginx:1.17.6``. Also use the data-source or resource of ``docker_image`` with the ``repo_digest`` or ``docker_registry_image`` with the ``name`` attribute for this, as shown in the examples. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#image Service#image}
        :param args: Arguments to the command. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#args Service#args}
        :param command: The command/entrypoint to be run in the image. According to the `docker cli <https://github.com/docker/cli/blob/v20.10.7/cli/command/service/opts.go#L705>`_ the override of the entrypoint is also passed to the ``command`` property and there is no ``entrypoint`` attribute in the ``ContainerSpec`` of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#command Service#command}
        :param configs: configs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#configs Service#configs}
        :param dir: The working directory for commands to run in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#dir Service#dir}
        :param dns_config: dns_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#dns_config Service#dns_config}
        :param env: A list of environment variables in the form VAR="value". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#env Service#env}
        :param groups: A list of additional groups that the container process will run as. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#groups Service#groups}
        :param healthcheck: healthcheck block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#healthcheck Service#healthcheck}
        :param hostname: The hostname to use for the container, as a valid RFC 1123 hostname. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#hostname Service#hostname}
        :param hosts: hosts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#hosts Service#hosts}
        :param isolation: Isolation technology of the containers running the service. (Windows only). Defaults to ``default``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#isolation Service#isolation}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#labels Service#labels}
        :param mounts: mounts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mounts Service#mounts}
        :param privileges: privileges block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#privileges Service#privileges}
        :param read_only: Mount the container's root filesystem as read only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#read_only Service#read_only}
        :param secrets: secrets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#secrets Service#secrets}
        :param stop_grace_period: Amount of time to wait for the container to terminate before forcefully removing it (ms|s|m|h). If not specified or '0s' the destroy will not check if all tasks/containers of the service terminate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#stop_grace_period Service#stop_grace_period}
        :param stop_signal: Signal to stop the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#stop_signal Service#stop_signal}
        :param user: The user inside the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#user Service#user}
        '''
        if isinstance(dns_config, dict):
            dns_config = ServiceTaskSpecContainerSpecDnsConfig(**dns_config)
        if isinstance(healthcheck, dict):
            healthcheck = ServiceTaskSpecContainerSpecHealthcheck(**healthcheck)
        if isinstance(privileges, dict):
            privileges = ServiceTaskSpecContainerSpecPrivileges(**privileges)
        self._values: typing.Dict[str, typing.Any] = {
            "image": image,
        }
        if args is not None:
            self._values["args"] = args
        if command is not None:
            self._values["command"] = command
        if configs is not None:
            self._values["configs"] = configs
        if dir is not None:
            self._values["dir"] = dir
        if dns_config is not None:
            self._values["dns_config"] = dns_config
        if env is not None:
            self._values["env"] = env
        if groups is not None:
            self._values["groups"] = groups
        if healthcheck is not None:
            self._values["healthcheck"] = healthcheck
        if hostname is not None:
            self._values["hostname"] = hostname
        if hosts is not None:
            self._values["hosts"] = hosts
        if isolation is not None:
            self._values["isolation"] = isolation
        if labels is not None:
            self._values["labels"] = labels
        if mounts is not None:
            self._values["mounts"] = mounts
        if privileges is not None:
            self._values["privileges"] = privileges
        if read_only is not None:
            self._values["read_only"] = read_only
        if secrets is not None:
            self._values["secrets"] = secrets
        if stop_grace_period is not None:
            self._values["stop_grace_period"] = stop_grace_period
        if stop_signal is not None:
            self._values["stop_signal"] = stop_signal
        if user is not None:
            self._values["user"] = user

    @builtins.property
    def image(self) -> builtins.str:
        '''The image name to use for the containers of the service, like ``nginx:1.17.6``. Also use the data-source or resource of ``docker_image`` with the ``repo_digest`` or ``docker_registry_image`` with the ``name`` attribute for this, as shown in the examples.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#image Service#image}
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Arguments to the command.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#args Service#args}
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The command/entrypoint to be run in the image.

        According to the `docker cli <https://github.com/docker/cli/blob/v20.10.7/cli/command/service/opts.go#L705>`_ the override of the entrypoint is also passed to the ``command`` property and there is no ``entrypoint`` attribute in the ``ContainerSpec`` of the service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#command Service#command}
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def configs(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecConfigs"]]:
        '''configs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#configs Service#configs}
        '''
        result = self._values.get("configs")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecConfigs"]], result)

    @builtins.property
    def dir(self) -> typing.Optional[builtins.str]:
        '''The working directory for commands to run in.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#dir Service#dir}
        '''
        result = self._values.get("dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns_config(self) -> typing.Optional["ServiceTaskSpecContainerSpecDnsConfig"]:
        '''dns_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#dns_config Service#dns_config}
        '''
        result = self._values.get("dns_config")
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecDnsConfig"], result)

    @builtins.property
    def env(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''A list of environment variables in the form VAR="value".

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#env Service#env}
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of additional groups that the container process will run as.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#groups Service#groups}
        '''
        result = self._values.get("groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def healthcheck(self) -> typing.Optional["ServiceTaskSpecContainerSpecHealthcheck"]:
        '''healthcheck block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#healthcheck Service#healthcheck}
        '''
        result = self._values.get("healthcheck")
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecHealthcheck"], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''The hostname to use for the container, as a valid RFC 1123 hostname.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#hostname Service#hostname}
        '''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hosts(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecHosts"]]:
        '''hosts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#hosts Service#hosts}
        '''
        result = self._values.get("hosts")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecHosts"]], result)

    @builtins.property
    def isolation(self) -> typing.Optional[builtins.str]:
        '''Isolation technology of the containers running the service. (Windows only). Defaults to ``default``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#isolation Service#isolation}
        '''
        result = self._values.get("isolation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#labels Service#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecLabels"]], result)

    @builtins.property
    def mounts(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecMounts"]]:
        '''mounts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mounts Service#mounts}
        '''
        result = self._values.get("mounts")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecMounts"]], result)

    @builtins.property
    def privileges(self) -> typing.Optional["ServiceTaskSpecContainerSpecPrivileges"]:
        '''privileges block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#privileges Service#privileges}
        '''
        result = self._values.get("privileges")
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecPrivileges"], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Mount the container's root filesystem as read only.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#read_only Service#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecSecrets"]]:
        '''secrets block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#secrets Service#secrets}
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecSecrets"]], result)

    @builtins.property
    def stop_grace_period(self) -> typing.Optional[builtins.str]:
        '''Amount of time to wait for the container to terminate before forcefully removing it (ms|s|m|h).

        If not specified or '0s' the destroy will not check if all tasks/containers of the service terminate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#stop_grace_period Service#stop_grace_period}
        '''
        result = self._values.get("stop_grace_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stop_signal(self) -> typing.Optional[builtins.str]:
        '''Signal to stop the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#stop_signal Service#stop_signal}
        '''
        result = self._values.get("stop_signal")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''The user inside the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#user Service#user}
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecConfigs",
    jsii_struct_bases=[],
    name_mapping={
        "config_id": "configId",
        "file_name": "fileName",
        "config_name": "configName",
        "file_gid": "fileGid",
        "file_mode": "fileMode",
        "file_uid": "fileUid",
    },
)
class ServiceTaskSpecContainerSpecConfigs:
    def __init__(
        self,
        *,
        config_id: builtins.str,
        file_name: builtins.str,
        config_name: typing.Optional[builtins.str] = None,
        file_gid: typing.Optional[builtins.str] = None,
        file_mode: typing.Optional[jsii.Number] = None,
        file_uid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_id: ID of the specific config that we're referencing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#config_id Service#config_id}
        :param file_name: Represents the final filename in the filesystem. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_name Service#file_name}
        :param config_name: Name of the config that this references, but this is just provided for lookup/display purposes. The config in the reference will be identified by its ID Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#config_name Service#config_name}
        :param file_gid: Represents the file GID. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_gid Service#file_gid}
        :param file_mode: Represents represents the FileMode of the file. Defaults to ``0o444``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_mode Service#file_mode}
        :param file_uid: Represents the file UID. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_uid Service#file_uid}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "config_id": config_id,
            "file_name": file_name,
        }
        if config_name is not None:
            self._values["config_name"] = config_name
        if file_gid is not None:
            self._values["file_gid"] = file_gid
        if file_mode is not None:
            self._values["file_mode"] = file_mode
        if file_uid is not None:
            self._values["file_uid"] = file_uid

    @builtins.property
    def config_id(self) -> builtins.str:
        '''ID of the specific config that we're referencing.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#config_id Service#config_id}
        '''
        result = self._values.get("config_id")
        assert result is not None, "Required property 'config_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_name(self) -> builtins.str:
        '''Represents the final filename in the filesystem.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_name Service#file_name}
        '''
        result = self._values.get("file_name")
        assert result is not None, "Required property 'file_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config_name(self) -> typing.Optional[builtins.str]:
        '''Name of the config that this references, but this is just provided for lookup/display purposes.

        The config in the reference will be identified by its ID

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#config_name Service#config_name}
        '''
        result = self._values.get("config_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_gid(self) -> typing.Optional[builtins.str]:
        '''Represents the file GID. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_gid Service#file_gid}
        '''
        result = self._values.get("file_gid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_mode(self) -> typing.Optional[jsii.Number]:
        '''Represents represents the FileMode of the file. Defaults to ``0o444``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_mode Service#file_mode}
        '''
        result = self._values.get("file_mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def file_uid(self) -> typing.Optional[builtins.str]:
        '''Represents the file UID. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_uid Service#file_uid}
        '''
        result = self._values.get("file_uid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecDnsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "nameservers": "nameservers",
        "options": "options",
        "search": "search",
    },
)
class ServiceTaskSpecContainerSpecDnsConfig:
    def __init__(
        self,
        *,
        nameservers: typing.Sequence[builtins.str],
        options: typing.Optional[typing.Sequence[builtins.str]] = None,
        search: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param nameservers: The IP addresses of the name servers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#nameservers Service#nameservers}
        :param options: A list of internal resolver variables to be modified (e.g., debug, ndots:3, etc.). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#options Service#options}
        :param search: A search list for host-name lookup. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#search Service#search}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "nameservers": nameservers,
        }
        if options is not None:
            self._values["options"] = options
        if search is not None:
            self._values["search"] = search

    @builtins.property
    def nameservers(self) -> typing.List[builtins.str]:
        '''The IP addresses of the name servers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#nameservers Service#nameservers}
        '''
        result = self._values.get("nameservers")
        assert result is not None, "Required property 'nameservers' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of internal resolver variables to be modified (e.g., debug, ndots:3, etc.).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#options Service#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def search(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A search list for host-name lookup.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#search Service#search}
        '''
        result = self._values.get("search")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecDnsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecContainerSpecDnsConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecDnsConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

    @jsii.member(jsii_name="resetSearch")
    def reset_search(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearch", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameserversInput")
    def nameservers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "nameserversInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionsInput")
    def options_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "optionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="searchInput")
    def search_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "searchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameservers")
    def nameservers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "nameservers"))

    @nameservers.setter
    def nameservers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "nameservers", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="options")
    def options(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "options", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="search")
    def search(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "search"))

    @search.setter
    def search(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "search", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpecContainerSpecDnsConfig]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecDnsConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecContainerSpecDnsConfig],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecHealthcheck",
    jsii_struct_bases=[],
    name_mapping={
        "test": "test",
        "interval": "interval",
        "retries": "retries",
        "start_period": "startPeriod",
        "timeout": "timeout",
    },
)
class ServiceTaskSpecContainerSpecHealthcheck:
    def __init__(
        self,
        *,
        test: typing.Sequence[builtins.str],
        interval: typing.Optional[builtins.str] = None,
        retries: typing.Optional[jsii.Number] = None,
        start_period: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param test: The test to perform as list. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#test Service#test}
        :param interval: Time between running the check (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#interval Service#interval}
        :param retries: Consecutive failures needed to report unhealthy. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#retries Service#retries}
        :param start_period: Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#start_period Service#start_period}
        :param timeout: Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#timeout Service#timeout}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "test": test,
        }
        if interval is not None:
            self._values["interval"] = interval
        if retries is not None:
            self._values["retries"] = retries
        if start_period is not None:
            self._values["start_period"] = start_period
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def test(self) -> typing.List[builtins.str]:
        '''The test to perform as list.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#test Service#test}
        '''
        result = self._values.get("test")
        assert result is not None, "Required property 'test' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def interval(self) -> typing.Optional[builtins.str]:
        '''Time between running the check (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#interval Service#interval}
        '''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retries(self) -> typing.Optional[jsii.Number]:
        '''Consecutive failures needed to report unhealthy. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#retries Service#retries}
        '''
        result = self._values.get("retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_period(self) -> typing.Optional[builtins.str]:
        '''Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#start_period Service#start_period}
        '''
        result = self._values.get("start_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#timeout Service#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecHealthcheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecContainerSpecHealthcheckOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecHealthcheckOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetInterval")
    def reset_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInterval", []))

    @jsii.member(jsii_name="resetRetries")
    def reset_retries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetries", []))

    @jsii.member(jsii_name="resetStartPeriod")
    def reset_start_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartPeriod", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalInput")
    def interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "intervalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retriesInput")
    def retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retriesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startPeriodInput")
    def start_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startPeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="testInput")
    def test_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "testInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="interval")
    def interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interval"))

    @interval.setter
    def interval(self, value: builtins.str) -> None:
        jsii.set(self, "interval", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="retries")
    def retries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retries"))

    @retries.setter
    def retries(self, value: jsii.Number) -> None:
        jsii.set(self, "retries", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startPeriod")
    def start_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startPeriod"))

    @start_period.setter
    def start_period(self, value: builtins.str) -> None:
        jsii.set(self, "startPeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="test")
    def test(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "test"))

    @test.setter
    def test(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "test", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: builtins.str) -> None:
        jsii.set(self, "timeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ServiceTaskSpecContainerSpecHealthcheck]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecHealthcheck], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecContainerSpecHealthcheck],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecHosts",
    jsii_struct_bases=[],
    name_mapping={"host": "host", "ip": "ip"},
)
class ServiceTaskSpecContainerSpecHosts:
    def __init__(self, *, host: builtins.str, ip: builtins.str) -> None:
        '''
        :param host: The name of the host. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#host Service#host}
        :param ip: The ip of the host. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#ip Service#ip}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "host": host,
            "ip": ip,
        }

    @builtins.property
    def host(self) -> builtins.str:
        '''The name of the host.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#host Service#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip(self) -> builtins.str:
        '''The ip of the host.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#ip Service#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecHosts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ServiceTaskSpecContainerSpecLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#label Service#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#value Service#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#label Service#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#value Service#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMounts",
    jsii_struct_bases=[],
    name_mapping={
        "target": "target",
        "type": "type",
        "bind_options": "bindOptions",
        "read_only": "readOnly",
        "source": "source",
        "tmpfs_options": "tmpfsOptions",
        "volume_options": "volumeOptions",
    },
)
class ServiceTaskSpecContainerSpecMounts:
    def __init__(
        self,
        *,
        target: builtins.str,
        type: builtins.str,
        bind_options: typing.Optional["ServiceTaskSpecContainerSpecMountsBindOptions"] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        source: typing.Optional[builtins.str] = None,
        tmpfs_options: typing.Optional["ServiceTaskSpecContainerSpecMountsTmpfsOptions"] = None,
        volume_options: typing.Optional["ServiceTaskSpecContainerSpecMountsVolumeOptions"] = None,
    ) -> None:
        '''
        :param target: Container path. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#target Service#target}
        :param type: The mount type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#type Service#type}
        :param bind_options: bind_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#bind_options Service#bind_options}
        :param read_only: Whether the mount should be read-only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#read_only Service#read_only}
        :param source: Mount source (e.g. a volume name, a host path). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#source Service#source}
        :param tmpfs_options: tmpfs_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#tmpfs_options Service#tmpfs_options}
        :param volume_options: volume_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#volume_options Service#volume_options}
        '''
        if isinstance(bind_options, dict):
            bind_options = ServiceTaskSpecContainerSpecMountsBindOptions(**bind_options)
        if isinstance(tmpfs_options, dict):
            tmpfs_options = ServiceTaskSpecContainerSpecMountsTmpfsOptions(**tmpfs_options)
        if isinstance(volume_options, dict):
            volume_options = ServiceTaskSpecContainerSpecMountsVolumeOptions(**volume_options)
        self._values: typing.Dict[str, typing.Any] = {
            "target": target,
            "type": type,
        }
        if bind_options is not None:
            self._values["bind_options"] = bind_options
        if read_only is not None:
            self._values["read_only"] = read_only
        if source is not None:
            self._values["source"] = source
        if tmpfs_options is not None:
            self._values["tmpfs_options"] = tmpfs_options
        if volume_options is not None:
            self._values["volume_options"] = volume_options

    @builtins.property
    def target(self) -> builtins.str:
        '''Container path.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#target Service#target}
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The mount type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#type Service#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bind_options(
        self,
    ) -> typing.Optional["ServiceTaskSpecContainerSpecMountsBindOptions"]:
        '''bind_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#bind_options Service#bind_options}
        '''
        result = self._values.get("bind_options")
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecMountsBindOptions"], result)

    @builtins.property
    def read_only(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether the mount should be read-only.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#read_only Service#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Mount source (e.g. a volume name, a host path).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#source Service#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tmpfs_options(
        self,
    ) -> typing.Optional["ServiceTaskSpecContainerSpecMountsTmpfsOptions"]:
        '''tmpfs_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#tmpfs_options Service#tmpfs_options}
        '''
        result = self._values.get("tmpfs_options")
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecMountsTmpfsOptions"], result)

    @builtins.property
    def volume_options(
        self,
    ) -> typing.Optional["ServiceTaskSpecContainerSpecMountsVolumeOptions"]:
        '''volume_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#volume_options Service#volume_options}
        '''
        result = self._values.get("volume_options")
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecMountsVolumeOptions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMounts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsBindOptions",
    jsii_struct_bases=[],
    name_mapping={"propagation": "propagation"},
)
class ServiceTaskSpecContainerSpecMountsBindOptions:
    def __init__(self, *, propagation: typing.Optional[builtins.str] = None) -> None:
        '''
        :param propagation: Bind propagation refers to whether or not mounts created within a given bind-mount or named volume can be propagated to replicas of that mount. See the `docs <https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation>`_ for details. Defaults to ``rprivate`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#propagation Service#propagation}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if propagation is not None:
            self._values["propagation"] = propagation

    @builtins.property
    def propagation(self) -> typing.Optional[builtins.str]:
        '''Bind propagation refers to whether or not mounts created within a given bind-mount or named volume can be propagated to replicas of that mount.

        See the `docs <https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation>`_ for details. Defaults to ``rprivate``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#propagation Service#propagation}
        '''
        result = self._values.get("propagation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMountsBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecContainerSpecMountsBindOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsBindOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetPropagation")
    def reset_propagation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPropagation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propagationInput")
    def propagation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "propagationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="propagation")
    def propagation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "propagation"))

    @propagation.setter
    def propagation(self, value: builtins.str) -> None:
        jsii.set(self, "propagation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ServiceTaskSpecContainerSpecMountsBindOptions]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecMountsBindOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecContainerSpecMountsBindOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsTmpfsOptions",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "size_bytes": "sizeBytes"},
)
class ServiceTaskSpecContainerSpecMountsTmpfsOptions:
    def __init__(
        self,
        *,
        mode: typing.Optional[jsii.Number] = None,
        size_bytes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mode: The permission mode for the tmpfs mount in an integer. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mode Service#mode}
        :param size_bytes: The size for the tmpfs mount in bytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#size_bytes Service#size_bytes}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if size_bytes is not None:
            self._values["size_bytes"] = size_bytes

    @builtins.property
    def mode(self) -> typing.Optional[jsii.Number]:
        '''The permission mode for the tmpfs mount in an integer.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mode Service#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def size_bytes(self) -> typing.Optional[jsii.Number]:
        '''The size for the tmpfs mount in bytes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#size_bytes Service#size_bytes}
        '''
        result = self._values.get("size_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMountsTmpfsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecContainerSpecMountsTmpfsOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsTmpfsOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetSizeBytes")
    def reset_size_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSizeBytes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeBytesInput")
    def size_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeBytesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: jsii.Number) -> None:
        jsii.set(self, "mode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sizeBytes")
    def size_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeBytes"))

    @size_bytes.setter
    def size_bytes(self, value: jsii.Number) -> None:
        jsii.set(self, "sizeBytes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ServiceTaskSpecContainerSpecMountsTmpfsOptions]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecMountsTmpfsOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecContainerSpecMountsTmpfsOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsVolumeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "driver_name": "driverName",
        "driver_options": "driverOptions",
        "labels": "labels",
        "no_copy": "noCopy",
    },
)
class ServiceTaskSpecContainerSpecMountsVolumeOptions:
    def __init__(
        self,
        *,
        driver_name: typing.Optional[builtins.str] = None,
        driver_options: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        labels: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels"]] = None,
        no_copy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param driver_name: Name of the driver to use to create the volume. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#driver_name Service#driver_name}
        :param driver_options: key/value map of driver specific options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#driver_options Service#driver_options}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#labels Service#labels}
        :param no_copy: Populate volume with data from the target. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#no_copy Service#no_copy}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if driver_name is not None:
            self._values["driver_name"] = driver_name
        if driver_options is not None:
            self._values["driver_options"] = driver_options
        if labels is not None:
            self._values["labels"] = labels
        if no_copy is not None:
            self._values["no_copy"] = no_copy

    @builtins.property
    def driver_name(self) -> typing.Optional[builtins.str]:
        '''Name of the driver to use to create the volume.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#driver_name Service#driver_name}
        '''
        result = self._values.get("driver_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def driver_options(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''key/value map of driver specific options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#driver_options Service#driver_options}
        '''
        result = self._values.get("driver_options")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#labels Service#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels"]], result)

    @builtins.property
    def no_copy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Populate volume with data from the target.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#no_copy Service#no_copy}
        '''
        result = self._values.get("no_copy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMountsVolumeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#label Service#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#value Service#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#label Service#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#value Service#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecContainerSpecMountsVolumeOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsVolumeOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetDriverName")
    def reset_driver_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverName", []))

    @jsii.member(jsii_name="resetDriverOptions")
    def reset_driver_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverOptions", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetNoCopy")
    def reset_no_copy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoCopy", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverNameInput")
    def driver_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverOptionsInput")
    def driver_options_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "driverOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.List[ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels]]:
        return typing.cast(typing.Optional[typing.List[ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noCopyInput")
    def no_copy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "noCopyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverName")
    def driver_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driverName"))

    @driver_name.setter
    def driver_name(self, value: builtins.str) -> None:
        jsii.set(self, "driverName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverOptions")
    def driver_options(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "driverOptions"))

    @driver_options.setter
    def driver_options(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "driverOptions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(
        self,
    ) -> typing.List[ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels]:
        return typing.cast(typing.List[ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels], jsii.get(self, "labels"))

    @labels.setter
    def labels(
        self,
        value: typing.List[ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels],
    ) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="noCopy")
    def no_copy(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "noCopy"))

    @no_copy.setter
    def no_copy(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "noCopy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ServiceTaskSpecContainerSpecMountsVolumeOptions]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecMountsVolumeOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecContainerSpecMountsVolumeOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ServiceTaskSpecContainerSpecOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putDnsConfig")
    def put_dns_config(
        self,
        *,
        nameservers: typing.Sequence[builtins.str],
        options: typing.Optional[typing.Sequence[builtins.str]] = None,
        search: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param nameservers: The IP addresses of the name servers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#nameservers Service#nameservers}
        :param options: A list of internal resolver variables to be modified (e.g., debug, ndots:3, etc.). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#options Service#options}
        :param search: A search list for host-name lookup. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#search Service#search}
        '''
        value = ServiceTaskSpecContainerSpecDnsConfig(
            nameservers=nameservers, options=options, search=search
        )

        return typing.cast(None, jsii.invoke(self, "putDnsConfig", [value]))

    @jsii.member(jsii_name="putHealthcheck")
    def put_healthcheck(
        self,
        *,
        test: typing.Sequence[builtins.str],
        interval: typing.Optional[builtins.str] = None,
        retries: typing.Optional[jsii.Number] = None,
        start_period: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param test: The test to perform as list. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#test Service#test}
        :param interval: Time between running the check (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#interval Service#interval}
        :param retries: Consecutive failures needed to report unhealthy. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#retries Service#retries}
        :param start_period: Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#start_period Service#start_period}
        :param timeout: Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#timeout Service#timeout}
        '''
        value = ServiceTaskSpecContainerSpecHealthcheck(
            test=test,
            interval=interval,
            retries=retries,
            start_period=start_period,
            timeout=timeout,
        )

        return typing.cast(None, jsii.invoke(self, "putHealthcheck", [value]))

    @jsii.member(jsii_name="putPrivileges")
    def put_privileges(
        self,
        *,
        credential_spec: typing.Optional["ServiceTaskSpecContainerSpecPrivilegesCredentialSpec"] = None,
        se_linux_context: typing.Optional["ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext"] = None,
    ) -> None:
        '''
        :param credential_spec: credential_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#credential_spec Service#credential_spec}
        :param se_linux_context: se_linux_context block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#se_linux_context Service#se_linux_context}
        '''
        value = ServiceTaskSpecContainerSpecPrivileges(
            credential_spec=credential_spec, se_linux_context=se_linux_context
        )

        return typing.cast(None, jsii.invoke(self, "putPrivileges", [value]))

    @jsii.member(jsii_name="resetArgs")
    def reset_args(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArgs", []))

    @jsii.member(jsii_name="resetCommand")
    def reset_command(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommand", []))

    @jsii.member(jsii_name="resetConfigs")
    def reset_configs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigs", []))

    @jsii.member(jsii_name="resetDir")
    def reset_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDir", []))

    @jsii.member(jsii_name="resetDnsConfig")
    def reset_dns_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsConfig", []))

    @jsii.member(jsii_name="resetEnv")
    def reset_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnv", []))

    @jsii.member(jsii_name="resetGroups")
    def reset_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroups", []))

    @jsii.member(jsii_name="resetHealthcheck")
    def reset_healthcheck(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthcheck", []))

    @jsii.member(jsii_name="resetHostname")
    def reset_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostname", []))

    @jsii.member(jsii_name="resetHosts")
    def reset_hosts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHosts", []))

    @jsii.member(jsii_name="resetIsolation")
    def reset_isolation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsolation", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetMounts")
    def reset_mounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMounts", []))

    @jsii.member(jsii_name="resetPrivileges")
    def reset_privileges(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivileges", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetSecrets")
    def reset_secrets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecrets", []))

    @jsii.member(jsii_name="resetStopGracePeriod")
    def reset_stop_grace_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStopGracePeriod", []))

    @jsii.member(jsii_name="resetStopSignal")
    def reset_stop_signal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStopSignal", []))

    @jsii.member(jsii_name="resetUser")
    def reset_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUser", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsConfig")
    def dns_config(self) -> ServiceTaskSpecContainerSpecDnsConfigOutputReference:
        return typing.cast(ServiceTaskSpecContainerSpecDnsConfigOutputReference, jsii.get(self, "dnsConfig"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheck")
    def healthcheck(self) -> ServiceTaskSpecContainerSpecHealthcheckOutputReference:
        return typing.cast(ServiceTaskSpecContainerSpecHealthcheckOutputReference, jsii.get(self, "healthcheck"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privileges")
    def privileges(self) -> "ServiceTaskSpecContainerSpecPrivilegesOutputReference":
        return typing.cast("ServiceTaskSpecContainerSpecPrivilegesOutputReference", jsii.get(self, "privileges"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="argsInput")
    def args_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "argsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commandInput")
    def command_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "commandInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configsInput")
    def configs_input(
        self,
    ) -> typing.Optional[typing.List[ServiceTaskSpecContainerSpecConfigs]]:
        return typing.cast(typing.Optional[typing.List[ServiceTaskSpecContainerSpecConfigs]], jsii.get(self, "configsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dirInput")
    def dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dirInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsConfigInput")
    def dns_config_input(
        self,
    ) -> typing.Optional[ServiceTaskSpecContainerSpecDnsConfig]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecDnsConfig], jsii.get(self, "dnsConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="envInput")
    def env_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "envInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupsInput")
    def groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "groupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheckInput")
    def healthcheck_input(
        self,
    ) -> typing.Optional[ServiceTaskSpecContainerSpecHealthcheck]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecHealthcheck], jsii.get(self, "healthcheckInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostsInput")
    def hosts_input(
        self,
    ) -> typing.Optional[typing.List[ServiceTaskSpecContainerSpecHosts]]:
        return typing.cast(typing.Optional[typing.List[ServiceTaskSpecContainerSpecHosts]], jsii.get(self, "hostsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isolationInput")
    def isolation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "isolationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.List[ServiceTaskSpecContainerSpecLabels]]:
        return typing.cast(typing.Optional[typing.List[ServiceTaskSpecContainerSpecLabels]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountsInput")
    def mounts_input(
        self,
    ) -> typing.Optional[typing.List[ServiceTaskSpecContainerSpecMounts]]:
        return typing.cast(typing.Optional[typing.List[ServiceTaskSpecContainerSpecMounts]], jsii.get(self, "mountsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privilegesInput")
    def privileges_input(
        self,
    ) -> typing.Optional["ServiceTaskSpecContainerSpecPrivileges"]:
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecPrivileges"], jsii.get(self, "privilegesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "readOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretsInput")
    def secrets_input(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecSecrets"]]:
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecSecrets"]], jsii.get(self, "secretsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stopGracePeriodInput")
    def stop_grace_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stopGracePeriodInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stopSignalInput")
    def stop_signal_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stopSignalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="args")
    def args(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "args"))

    @args.setter
    def args(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "args", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "command"))

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "command", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configs")
    def configs(self) -> typing.List[ServiceTaskSpecContainerSpecConfigs]:
        return typing.cast(typing.List[ServiceTaskSpecContainerSpecConfigs], jsii.get(self, "configs"))

    @configs.setter
    def configs(self, value: typing.List[ServiceTaskSpecContainerSpecConfigs]) -> None:
        jsii.set(self, "configs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dir")
    def dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dir"))

    @dir.setter
    def dir(self, value: builtins.str) -> None:
        jsii.set(self, "dir", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "env"))

    @env.setter
    def env(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "env", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groups")
    def groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "groups"))

    @groups.setter
    def groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "groups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        jsii.set(self, "hostname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hosts")
    def hosts(self) -> typing.List[ServiceTaskSpecContainerSpecHosts]:
        return typing.cast(typing.List[ServiceTaskSpecContainerSpecHosts], jsii.get(self, "hosts"))

    @hosts.setter
    def hosts(self, value: typing.List[ServiceTaskSpecContainerSpecHosts]) -> None:
        jsii.set(self, "hosts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @image.setter
    def image(self, value: builtins.str) -> None:
        jsii.set(self, "image", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isolation")
    def isolation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "isolation"))

    @isolation.setter
    def isolation(self, value: builtins.str) -> None:
        jsii.set(self, "isolation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List[ServiceTaskSpecContainerSpecLabels]:
        return typing.cast(typing.List[ServiceTaskSpecContainerSpecLabels], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List[ServiceTaskSpecContainerSpecLabels]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mounts")
    def mounts(self) -> typing.List[ServiceTaskSpecContainerSpecMounts]:
        return typing.cast(typing.List[ServiceTaskSpecContainerSpecMounts], jsii.get(self, "mounts"))

    @mounts.setter
    def mounts(self, value: typing.List[ServiceTaskSpecContainerSpecMounts]) -> None:
        jsii.set(self, "mounts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "readOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secrets")
    def secrets(self) -> typing.List["ServiceTaskSpecContainerSpecSecrets"]:
        return typing.cast(typing.List["ServiceTaskSpecContainerSpecSecrets"], jsii.get(self, "secrets"))

    @secrets.setter
    def secrets(
        self,
        value: typing.List["ServiceTaskSpecContainerSpecSecrets"],
    ) -> None:
        jsii.set(self, "secrets", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stopGracePeriod")
    def stop_grace_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stopGracePeriod"))

    @stop_grace_period.setter
    def stop_grace_period(self, value: builtins.str) -> None:
        jsii.set(self, "stopGracePeriod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stopSignal")
    def stop_signal(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stopSignal"))

    @stop_signal.setter
    def stop_signal(self, value: builtins.str) -> None:
        jsii.set(self, "stopSignal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpecContainerSpec]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecContainerSpec],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecPrivileges",
    jsii_struct_bases=[],
    name_mapping={
        "credential_spec": "credentialSpec",
        "se_linux_context": "seLinuxContext",
    },
)
class ServiceTaskSpecContainerSpecPrivileges:
    def __init__(
        self,
        *,
        credential_spec: typing.Optional["ServiceTaskSpecContainerSpecPrivilegesCredentialSpec"] = None,
        se_linux_context: typing.Optional["ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext"] = None,
    ) -> None:
        '''
        :param credential_spec: credential_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#credential_spec Service#credential_spec}
        :param se_linux_context: se_linux_context block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#se_linux_context Service#se_linux_context}
        '''
        if isinstance(credential_spec, dict):
            credential_spec = ServiceTaskSpecContainerSpecPrivilegesCredentialSpec(**credential_spec)
        if isinstance(se_linux_context, dict):
            se_linux_context = ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext(**se_linux_context)
        self._values: typing.Dict[str, typing.Any] = {}
        if credential_spec is not None:
            self._values["credential_spec"] = credential_spec
        if se_linux_context is not None:
            self._values["se_linux_context"] = se_linux_context

    @builtins.property
    def credential_spec(
        self,
    ) -> typing.Optional["ServiceTaskSpecContainerSpecPrivilegesCredentialSpec"]:
        '''credential_spec block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#credential_spec Service#credential_spec}
        '''
        result = self._values.get("credential_spec")
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecPrivilegesCredentialSpec"], result)

    @builtins.property
    def se_linux_context(
        self,
    ) -> typing.Optional["ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext"]:
        '''se_linux_context block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#se_linux_context Service#se_linux_context}
        '''
        result = self._values.get("se_linux_context")
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecPrivileges(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecPrivilegesCredentialSpec",
    jsii_struct_bases=[],
    name_mapping={"file": "file", "registry": "registry"},
)
class ServiceTaskSpecContainerSpecPrivilegesCredentialSpec:
    def __init__(
        self,
        *,
        file: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file: Load credential spec from this file. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file Service#file}
        :param registry: Load credential spec from this value in the Windows registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#registry Service#registry}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if file is not None:
            self._values["file"] = file
        if registry is not None:
            self._values["registry"] = registry

    @builtins.property
    def file(self) -> typing.Optional[builtins.str]:
        '''Load credential spec from this file.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file Service#file}
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''Load credential spec from this value in the Windows registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#registry Service#registry}
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecPrivilegesCredentialSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecContainerSpecPrivilegesCredentialSpecOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecPrivilegesCredentialSpecOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetFile")
    def reset_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFile", []))

    @jsii.member(jsii_name="resetRegistry")
    def reset_registry(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegistry", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileInput")
    def file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registryInput")
    def registry_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "registryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="file")
    def file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "file"))

    @file.setter
    def file(self, value: builtins.str) -> None:
        jsii.set(self, "file", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registry")
    def registry(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registry"))

    @registry.setter
    def registry(self, value: builtins.str) -> None:
        jsii.set(self, "registry", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ServiceTaskSpecContainerSpecPrivilegesCredentialSpec]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecPrivilegesCredentialSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecContainerSpecPrivilegesCredentialSpec],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ServiceTaskSpecContainerSpecPrivilegesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecPrivilegesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putCredentialSpec")
    def put_credential_spec(
        self,
        *,
        file: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file: Load credential spec from this file. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file Service#file}
        :param registry: Load credential spec from this value in the Windows registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#registry Service#registry}
        '''
        value = ServiceTaskSpecContainerSpecPrivilegesCredentialSpec(
            file=file, registry=registry
        )

        return typing.cast(None, jsii.invoke(self, "putCredentialSpec", [value]))

    @jsii.member(jsii_name="putSeLinuxContext")
    def put_se_linux_context(
        self,
        *,
        disable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        level: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param disable: Disable SELinux. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#disable Service#disable}
        :param level: SELinux level label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#level Service#level}
        :param role: SELinux role label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#role Service#role}
        :param type: SELinux type label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#type Service#type}
        :param user: SELinux user label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#user Service#user}
        '''
        value = ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext(
            disable=disable, level=level, role=role, type=type, user=user
        )

        return typing.cast(None, jsii.invoke(self, "putSeLinuxContext", [value]))

    @jsii.member(jsii_name="resetCredentialSpec")
    def reset_credential_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCredentialSpec", []))

    @jsii.member(jsii_name="resetSeLinuxContext")
    def reset_se_linux_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSeLinuxContext", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialSpec")
    def credential_spec(
        self,
    ) -> ServiceTaskSpecContainerSpecPrivilegesCredentialSpecOutputReference:
        return typing.cast(ServiceTaskSpecContainerSpecPrivilegesCredentialSpecOutputReference, jsii.get(self, "credentialSpec"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="seLinuxContext")
    def se_linux_context(
        self,
    ) -> "ServiceTaskSpecContainerSpecPrivilegesSeLinuxContextOutputReference":
        return typing.cast("ServiceTaskSpecContainerSpecPrivilegesSeLinuxContextOutputReference", jsii.get(self, "seLinuxContext"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentialSpecInput")
    def credential_spec_input(
        self,
    ) -> typing.Optional[ServiceTaskSpecContainerSpecPrivilegesCredentialSpec]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecPrivilegesCredentialSpec], jsii.get(self, "credentialSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="seLinuxContextInput")
    def se_linux_context_input(
        self,
    ) -> typing.Optional["ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext"]:
        return typing.cast(typing.Optional["ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext"], jsii.get(self, "seLinuxContextInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpecContainerSpecPrivileges]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecPrivileges], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecContainerSpecPrivileges],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext",
    jsii_struct_bases=[],
    name_mapping={
        "disable": "disable",
        "level": "level",
        "role": "role",
        "type": "type",
        "user": "user",
    },
)
class ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext:
    def __init__(
        self,
        *,
        disable: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        level: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param disable: Disable SELinux. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#disable Service#disable}
        :param level: SELinux level label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#level Service#level}
        :param role: SELinux role label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#role Service#role}
        :param type: SELinux type label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#type Service#type}
        :param user: SELinux user label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#user Service#user}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if disable is not None:
            self._values["disable"] = disable
        if level is not None:
            self._values["level"] = level
        if role is not None:
            self._values["role"] = role
        if type is not None:
            self._values["type"] = type
        if user is not None:
            self._values["user"] = user

    @builtins.property
    def disable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Disable SELinux.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#disable Service#disable}
        '''
        result = self._values.get("disable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def level(self) -> typing.Optional[builtins.str]:
        '''SELinux level label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#level Service#level}
        '''
        result = self._values.get("level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''SELinux role label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#role Service#role}
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''SELinux type label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#type Service#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''SELinux user label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#user Service#user}
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecContainerSpecPrivilegesSeLinuxContextOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecPrivilegesSeLinuxContextOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetDisable")
    def reset_disable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisable", []))

    @jsii.member(jsii_name="resetLevel")
    def reset_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLevel", []))

    @jsii.member(jsii_name="resetRole")
    def reset_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRole", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetUser")
    def reset_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUser", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disableInput")
    def disable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "disableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="levelInput")
    def level_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "levelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="disable")
    def disable(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "disable"))

    @disable.setter
    def disable(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "disable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="level")
    def level(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "level"))

    @level.setter
    def level(self, value: builtins.str) -> None:
        jsii.set(self, "level", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        jsii.set(self, "role", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecSecrets",
    jsii_struct_bases=[],
    name_mapping={
        "file_name": "fileName",
        "secret_id": "secretId",
        "file_gid": "fileGid",
        "file_mode": "fileMode",
        "file_uid": "fileUid",
        "secret_name": "secretName",
    },
)
class ServiceTaskSpecContainerSpecSecrets:
    def __init__(
        self,
        *,
        file_name: builtins.str,
        secret_id: builtins.str,
        file_gid: typing.Optional[builtins.str] = None,
        file_mode: typing.Optional[jsii.Number] = None,
        file_uid: typing.Optional[builtins.str] = None,
        secret_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file_name: Represents the final filename in the filesystem. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_name Service#file_name}
        :param secret_id: ID of the specific secret that we're referencing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#secret_id Service#secret_id}
        :param file_gid: Represents the file GID. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_gid Service#file_gid}
        :param file_mode: Represents represents the FileMode of the file. Defaults to ``0o444``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_mode Service#file_mode}
        :param file_uid: Represents the file UID. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_uid Service#file_uid}
        :param secret_name: Name of the secret that this references, but this is just provided for lookup/display purposes. The config in the reference will be identified by its ID Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#secret_name Service#secret_name}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "file_name": file_name,
            "secret_id": secret_id,
        }
        if file_gid is not None:
            self._values["file_gid"] = file_gid
        if file_mode is not None:
            self._values["file_mode"] = file_mode
        if file_uid is not None:
            self._values["file_uid"] = file_uid
        if secret_name is not None:
            self._values["secret_name"] = secret_name

    @builtins.property
    def file_name(self) -> builtins.str:
        '''Represents the final filename in the filesystem.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_name Service#file_name}
        '''
        result = self._values.get("file_name")
        assert result is not None, "Required property 'file_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_id(self) -> builtins.str:
        '''ID of the specific secret that we're referencing.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#secret_id Service#secret_id}
        '''
        result = self._values.get("secret_id")
        assert result is not None, "Required property 'secret_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_gid(self) -> typing.Optional[builtins.str]:
        '''Represents the file GID. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_gid Service#file_gid}
        '''
        result = self._values.get("file_gid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_mode(self) -> typing.Optional[jsii.Number]:
        '''Represents represents the FileMode of the file. Defaults to ``0o444``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_mode Service#file_mode}
        '''
        result = self._values.get("file_mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def file_uid(self) -> typing.Optional[builtins.str]:
        '''Represents the file UID. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#file_uid Service#file_uid}
        '''
        result = self._values.get("file_uid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''Name of the secret that this references, but this is just provided for lookup/display purposes.

        The config in the reference will be identified by its ID

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#secret_name Service#secret_name}
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecSecrets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecLogDriver",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "options": "options"},
)
class ServiceTaskSpecLogDriver:
    def __init__(
        self,
        *,
        name: builtins.str,
        options: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param name: The logging driver to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#name Service#name}
        :param options: The options for the logging driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#options Service#options}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if options is not None:
            self._values["options"] = options

    @builtins.property
    def name(self) -> builtins.str:
        '''The logging driver to use.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#name Service#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def options(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''The options for the logging driver.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#options Service#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecLogDriver(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecLogDriverOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecLogDriverOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionsInput")
    def options_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "optionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="options")
    def options(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "options"))

    @options.setter
    def options(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "options", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpecLogDriver]:
        return typing.cast(typing.Optional[ServiceTaskSpecLogDriver], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceTaskSpecLogDriver]) -> None:
        jsii.set(self, "internalValue", value)


class ServiceTaskSpecOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putContainerSpec")
    def put_container_spec(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        configs: typing.Optional[typing.Sequence[ServiceTaskSpecContainerSpecConfigs]] = None,
        dir: typing.Optional[builtins.str] = None,
        dns_config: typing.Optional[ServiceTaskSpecContainerSpecDnsConfig] = None,
        env: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        healthcheck: typing.Optional[ServiceTaskSpecContainerSpecHealthcheck] = None,
        hostname: typing.Optional[builtins.str] = None,
        hosts: typing.Optional[typing.Sequence[ServiceTaskSpecContainerSpecHosts]] = None,
        isolation: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Sequence[ServiceTaskSpecContainerSpecLabels]] = None,
        mounts: typing.Optional[typing.Sequence[ServiceTaskSpecContainerSpecMounts]] = None,
        privileges: typing.Optional[ServiceTaskSpecContainerSpecPrivileges] = None,
        read_only: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        secrets: typing.Optional[typing.Sequence[ServiceTaskSpecContainerSpecSecrets]] = None,
        stop_grace_period: typing.Optional[builtins.str] = None,
        stop_signal: typing.Optional[builtins.str] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image: The image name to use for the containers of the service, like ``nginx:1.17.6``. Also use the data-source or resource of ``docker_image`` with the ``repo_digest`` or ``docker_registry_image`` with the ``name`` attribute for this, as shown in the examples. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#image Service#image}
        :param args: Arguments to the command. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#args Service#args}
        :param command: The command/entrypoint to be run in the image. According to the `docker cli <https://github.com/docker/cli/blob/v20.10.7/cli/command/service/opts.go#L705>`_ the override of the entrypoint is also passed to the ``command`` property and there is no ``entrypoint`` attribute in the ``ContainerSpec`` of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#command Service#command}
        :param configs: configs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#configs Service#configs}
        :param dir: The working directory for commands to run in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#dir Service#dir}
        :param dns_config: dns_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#dns_config Service#dns_config}
        :param env: A list of environment variables in the form VAR="value". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#env Service#env}
        :param groups: A list of additional groups that the container process will run as. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#groups Service#groups}
        :param healthcheck: healthcheck block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#healthcheck Service#healthcheck}
        :param hostname: The hostname to use for the container, as a valid RFC 1123 hostname. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#hostname Service#hostname}
        :param hosts: hosts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#hosts Service#hosts}
        :param isolation: Isolation technology of the containers running the service. (Windows only). Defaults to ``default``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#isolation Service#isolation}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#labels Service#labels}
        :param mounts: mounts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#mounts Service#mounts}
        :param privileges: privileges block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#privileges Service#privileges}
        :param read_only: Mount the container's root filesystem as read only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#read_only Service#read_only}
        :param secrets: secrets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#secrets Service#secrets}
        :param stop_grace_period: Amount of time to wait for the container to terminate before forcefully removing it (ms|s|m|h). If not specified or '0s' the destroy will not check if all tasks/containers of the service terminate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#stop_grace_period Service#stop_grace_period}
        :param stop_signal: Signal to stop the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#stop_signal Service#stop_signal}
        :param user: The user inside the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#user Service#user}
        '''
        value = ServiceTaskSpecContainerSpec(
            image=image,
            args=args,
            command=command,
            configs=configs,
            dir=dir,
            dns_config=dns_config,
            env=env,
            groups=groups,
            healthcheck=healthcheck,
            hostname=hostname,
            hosts=hosts,
            isolation=isolation,
            labels=labels,
            mounts=mounts,
            privileges=privileges,
            read_only=read_only,
            secrets=secrets,
            stop_grace_period=stop_grace_period,
            stop_signal=stop_signal,
            user=user,
        )

        return typing.cast(None, jsii.invoke(self, "putContainerSpec", [value]))

    @jsii.member(jsii_name="putLogDriver")
    def put_log_driver(
        self,
        *,
        name: builtins.str,
        options: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param name: The logging driver to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#name Service#name}
        :param options: The options for the logging driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#options Service#options}
        '''
        value = ServiceTaskSpecLogDriver(name=name, options=options)

        return typing.cast(None, jsii.invoke(self, "putLogDriver", [value]))

    @jsii.member(jsii_name="putPlacement")
    def put_placement(
        self,
        *,
        constraints: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_replicas: typing.Optional[jsii.Number] = None,
        platforms: typing.Optional[typing.Sequence["ServiceTaskSpecPlacementPlatforms"]] = None,
        prefs: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param constraints: An array of constraints. e.g.: ``node.role==manager``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#constraints Service#constraints}
        :param max_replicas: Maximum number of replicas for per node (default value is ``0``, which is unlimited). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_replicas Service#max_replicas}
        :param platforms: platforms block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#platforms Service#platforms}
        :param prefs: Preferences provide a way to make the scheduler aware of factors such as topology. They are provided in order from highest to lowest precedence, e.g.: spread=node.role.manager Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#prefs Service#prefs}
        '''
        value = ServiceTaskSpecPlacement(
            constraints=constraints,
            max_replicas=max_replicas,
            platforms=platforms,
            prefs=prefs,
        )

        return typing.cast(None, jsii.invoke(self, "putPlacement", [value]))

    @jsii.member(jsii_name="putResources")
    def put_resources(
        self,
        *,
        limits: typing.Optional["ServiceTaskSpecResourcesLimits"] = None,
        reservation: typing.Optional["ServiceTaskSpecResourcesReservation"] = None,
    ) -> None:
        '''
        :param limits: limits block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#limits Service#limits}
        :param reservation: reservation block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#reservation Service#reservation}
        '''
        value = ServiceTaskSpecResources(limits=limits, reservation=reservation)

        return typing.cast(None, jsii.invoke(self, "putResources", [value]))

    @jsii.member(jsii_name="putRestartPolicy")
    def put_restart_policy(
        self,
        *,
        condition: typing.Optional[builtins.str] = None,
        delay: typing.Optional[builtins.str] = None,
        max_attempts: typing.Optional[jsii.Number] = None,
        window: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param condition: Condition for restart. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#condition Service#condition}
        :param delay: Delay between restart attempts (ms|s|m|h). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        :param max_attempts: Maximum attempts to restart a given container before giving up (default value is ``0``, which is ignored). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_attempts Service#max_attempts}
        :param window: The time window used to evaluate the restart policy (default value is ``0``, which is unbounded) (ms|s|m|h). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#window Service#window}
        '''
        value = ServiceTaskSpecRestartPolicy(
            condition=condition, delay=delay, max_attempts=max_attempts, window=window
        )

        return typing.cast(None, jsii.invoke(self, "putRestartPolicy", [value]))

    @jsii.member(jsii_name="resetForceUpdate")
    def reset_force_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceUpdate", []))

    @jsii.member(jsii_name="resetLogDriver")
    def reset_log_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogDriver", []))

    @jsii.member(jsii_name="resetNetworks")
    def reset_networks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworks", []))

    @jsii.member(jsii_name="resetPlacement")
    def reset_placement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlacement", []))

    @jsii.member(jsii_name="resetResources")
    def reset_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResources", []))

    @jsii.member(jsii_name="resetRestartPolicy")
    def reset_restart_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestartPolicy", []))

    @jsii.member(jsii_name="resetRuntime")
    def reset_runtime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuntime", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerSpec")
    def container_spec(self) -> ServiceTaskSpecContainerSpecOutputReference:
        return typing.cast(ServiceTaskSpecContainerSpecOutputReference, jsii.get(self, "containerSpec"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDriver")
    def log_driver(self) -> ServiceTaskSpecLogDriverOutputReference:
        return typing.cast(ServiceTaskSpecLogDriverOutputReference, jsii.get(self, "logDriver"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="placement")
    def placement(self) -> "ServiceTaskSpecPlacementOutputReference":
        return typing.cast("ServiceTaskSpecPlacementOutputReference", jsii.get(self, "placement"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resources")
    def resources(self) -> "ServiceTaskSpecResourcesOutputReference":
        return typing.cast("ServiceTaskSpecResourcesOutputReference", jsii.get(self, "resources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartPolicy")
    def restart_policy(self) -> "ServiceTaskSpecRestartPolicyOutputReference":
        return typing.cast("ServiceTaskSpecRestartPolicyOutputReference", jsii.get(self, "restartPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerSpecInput")
    def container_spec_input(self) -> typing.Optional[ServiceTaskSpecContainerSpec]:
        return typing.cast(typing.Optional[ServiceTaskSpecContainerSpec], jsii.get(self, "containerSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceUpdateInput")
    def force_update_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "forceUpdateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDriverInput")
    def log_driver_input(self) -> typing.Optional[ServiceTaskSpecLogDriver]:
        return typing.cast(typing.Optional[ServiceTaskSpecLogDriver], jsii.get(self, "logDriverInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networksInput")
    def networks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "networksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="placementInput")
    def placement_input(self) -> typing.Optional["ServiceTaskSpecPlacement"]:
        return typing.cast(typing.Optional["ServiceTaskSpecPlacement"], jsii.get(self, "placementInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourcesInput")
    def resources_input(self) -> typing.Optional["ServiceTaskSpecResources"]:
        return typing.cast(typing.Optional["ServiceTaskSpecResources"], jsii.get(self, "resourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartPolicyInput")
    def restart_policy_input(self) -> typing.Optional["ServiceTaskSpecRestartPolicy"]:
        return typing.cast(typing.Optional["ServiceTaskSpecRestartPolicy"], jsii.get(self, "restartPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtimeInput")
    def runtime_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runtimeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceUpdate")
    def force_update(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "forceUpdate"))

    @force_update.setter
    def force_update(self, value: jsii.Number) -> None:
        jsii.set(self, "forceUpdate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networks")
    def networks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networks"))

    @networks.setter
    def networks(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "networks", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="runtime")
    def runtime(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runtime"))

    @runtime.setter
    def runtime(self, value: builtins.str) -> None:
        jsii.set(self, "runtime", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpec]:
        return typing.cast(typing.Optional[ServiceTaskSpec], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceTaskSpec]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecPlacement",
    jsii_struct_bases=[],
    name_mapping={
        "constraints": "constraints",
        "max_replicas": "maxReplicas",
        "platforms": "platforms",
        "prefs": "prefs",
    },
)
class ServiceTaskSpecPlacement:
    def __init__(
        self,
        *,
        constraints: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_replicas: typing.Optional[jsii.Number] = None,
        platforms: typing.Optional[typing.Sequence["ServiceTaskSpecPlacementPlatforms"]] = None,
        prefs: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param constraints: An array of constraints. e.g.: ``node.role==manager``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#constraints Service#constraints}
        :param max_replicas: Maximum number of replicas for per node (default value is ``0``, which is unlimited). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_replicas Service#max_replicas}
        :param platforms: platforms block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#platforms Service#platforms}
        :param prefs: Preferences provide a way to make the scheduler aware of factors such as topology. They are provided in order from highest to lowest precedence, e.g.: spread=node.role.manager Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#prefs Service#prefs}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if constraints is not None:
            self._values["constraints"] = constraints
        if max_replicas is not None:
            self._values["max_replicas"] = max_replicas
        if platforms is not None:
            self._values["platforms"] = platforms
        if prefs is not None:
            self._values["prefs"] = prefs

    @builtins.property
    def constraints(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of constraints. e.g.: ``node.role==manager``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#constraints Service#constraints}
        '''
        result = self._values.get("constraints")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_replicas(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of replicas for per node (default value is ``0``, which is unlimited).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_replicas Service#max_replicas}
        '''
        result = self._values.get("max_replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def platforms(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecPlacementPlatforms"]]:
        '''platforms block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#platforms Service#platforms}
        '''
        result = self._values.get("platforms")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecPlacementPlatforms"]], result)

    @builtins.property
    def prefs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Preferences provide a way to make the scheduler aware of factors such as topology.

        They are provided in order from highest to lowest precedence, e.g.: spread=node.role.manager

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#prefs Service#prefs}
        '''
        result = self._values.get("prefs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecPlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecPlacementOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecPlacementOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetConstraints")
    def reset_constraints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConstraints", []))

    @jsii.member(jsii_name="resetMaxReplicas")
    def reset_max_replicas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxReplicas", []))

    @jsii.member(jsii_name="resetPlatforms")
    def reset_platforms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPlatforms", []))

    @jsii.member(jsii_name="resetPrefs")
    def reset_prefs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefs", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="constraintsInput")
    def constraints_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "constraintsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxReplicasInput")
    def max_replicas_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxReplicasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platformsInput")
    def platforms_input(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecPlacementPlatforms"]]:
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecPlacementPlatforms"]], jsii.get(self, "platformsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefsInput")
    def prefs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "prefsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="constraints")
    def constraints(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "constraints"))

    @constraints.setter
    def constraints(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "constraints", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxReplicas")
    def max_replicas(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxReplicas"))

    @max_replicas.setter
    def max_replicas(self, value: jsii.Number) -> None:
        jsii.set(self, "maxReplicas", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="platforms")
    def platforms(self) -> typing.List["ServiceTaskSpecPlacementPlatforms"]:
        return typing.cast(typing.List["ServiceTaskSpecPlacementPlatforms"], jsii.get(self, "platforms"))

    @platforms.setter
    def platforms(
        self,
        value: typing.List["ServiceTaskSpecPlacementPlatforms"],
    ) -> None:
        jsii.set(self, "platforms", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="prefs")
    def prefs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "prefs"))

    @prefs.setter
    def prefs(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "prefs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpecPlacement]:
        return typing.cast(typing.Optional[ServiceTaskSpecPlacement], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceTaskSpecPlacement]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecPlacementPlatforms",
    jsii_struct_bases=[],
    name_mapping={"architecture": "architecture", "os": "os"},
)
class ServiceTaskSpecPlacementPlatforms:
    def __init__(self, *, architecture: builtins.str, os: builtins.str) -> None:
        '''
        :param architecture: The architecture, e.g. ``amd64``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#architecture Service#architecture}
        :param os: The operation system, e.g. ``linux``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#os Service#os}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "architecture": architecture,
            "os": os,
        }

    @builtins.property
    def architecture(self) -> builtins.str:
        '''The architecture, e.g. ``amd64``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#architecture Service#architecture}
        '''
        result = self._values.get("architecture")
        assert result is not None, "Required property 'architecture' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def os(self) -> builtins.str:
        '''The operation system, e.g. ``linux``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#os Service#os}
        '''
        result = self._values.get("os")
        assert result is not None, "Required property 'os' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecPlacementPlatforms(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResources",
    jsii_struct_bases=[],
    name_mapping={"limits": "limits", "reservation": "reservation"},
)
class ServiceTaskSpecResources:
    def __init__(
        self,
        *,
        limits: typing.Optional["ServiceTaskSpecResourcesLimits"] = None,
        reservation: typing.Optional["ServiceTaskSpecResourcesReservation"] = None,
    ) -> None:
        '''
        :param limits: limits block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#limits Service#limits}
        :param reservation: reservation block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#reservation Service#reservation}
        '''
        if isinstance(limits, dict):
            limits = ServiceTaskSpecResourcesLimits(**limits)
        if isinstance(reservation, dict):
            reservation = ServiceTaskSpecResourcesReservation(**reservation)
        self._values: typing.Dict[str, typing.Any] = {}
        if limits is not None:
            self._values["limits"] = limits
        if reservation is not None:
            self._values["reservation"] = reservation

    @builtins.property
    def limits(self) -> typing.Optional["ServiceTaskSpecResourcesLimits"]:
        '''limits block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#limits Service#limits}
        '''
        result = self._values.get("limits")
        return typing.cast(typing.Optional["ServiceTaskSpecResourcesLimits"], result)

    @builtins.property
    def reservation(self) -> typing.Optional["ServiceTaskSpecResourcesReservation"]:
        '''reservation block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#reservation Service#reservation}
        '''
        result = self._values.get("reservation")
        return typing.cast(typing.Optional["ServiceTaskSpecResourcesReservation"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesLimits",
    jsii_struct_bases=[],
    name_mapping={"memory_bytes": "memoryBytes", "nano_cpus": "nanoCpus"},
)
class ServiceTaskSpecResourcesLimits:
    def __init__(
        self,
        *,
        memory_bytes: typing.Optional[jsii.Number] = None,
        nano_cpus: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param memory_bytes: The amounf of memory in bytes the container allocates. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#memory_bytes Service#memory_bytes}
        :param nano_cpus: CPU shares in units of ``1/1e9`` (or ``10^-9``) of the CPU. Should be at least 1000000. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#nano_cpus Service#nano_cpus}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if memory_bytes is not None:
            self._values["memory_bytes"] = memory_bytes
        if nano_cpus is not None:
            self._values["nano_cpus"] = nano_cpus

    @builtins.property
    def memory_bytes(self) -> typing.Optional[jsii.Number]:
        '''The amounf of memory in bytes the container allocates.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#memory_bytes Service#memory_bytes}
        '''
        result = self._values.get("memory_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nano_cpus(self) -> typing.Optional[jsii.Number]:
        '''CPU shares in units of ``1/1e9`` (or ``10^-9``) of the CPU. Should be at least 1000000.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#nano_cpus Service#nano_cpus}
        '''
        result = self._values.get("nano_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecResourcesLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecResourcesLimitsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesLimitsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetMemoryBytes")
    def reset_memory_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryBytes", []))

    @jsii.member(jsii_name="resetNanoCpus")
    def reset_nano_cpus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNanoCpus", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryBytesInput")
    def memory_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryBytesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nanoCpusInput")
    def nano_cpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nanoCpusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryBytes")
    def memory_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryBytes"))

    @memory_bytes.setter
    def memory_bytes(self, value: jsii.Number) -> None:
        jsii.set(self, "memoryBytes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nanoCpus")
    def nano_cpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nanoCpus"))

    @nano_cpus.setter
    def nano_cpus(self, value: jsii.Number) -> None:
        jsii.set(self, "nanoCpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpecResourcesLimits]:
        return typing.cast(typing.Optional[ServiceTaskSpecResourcesLimits], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecResourcesLimits],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ServiceTaskSpecResourcesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putLimits")
    def put_limits(
        self,
        *,
        memory_bytes: typing.Optional[jsii.Number] = None,
        nano_cpus: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param memory_bytes: The amounf of memory in bytes the container allocates. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#memory_bytes Service#memory_bytes}
        :param nano_cpus: CPU shares in units of ``1/1e9`` (or ``10^-9``) of the CPU. Should be at least 1000000. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#nano_cpus Service#nano_cpus}
        '''
        value = ServiceTaskSpecResourcesLimits(
            memory_bytes=memory_bytes, nano_cpus=nano_cpus
        )

        return typing.cast(None, jsii.invoke(self, "putLimits", [value]))

    @jsii.member(jsii_name="putReservation")
    def put_reservation(
        self,
        *,
        generic_resources: typing.Optional["ServiceTaskSpecResourcesReservationGenericResources"] = None,
        memory_bytes: typing.Optional[jsii.Number] = None,
        nano_cpus: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param generic_resources: generic_resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#generic_resources Service#generic_resources}
        :param memory_bytes: The amounf of memory in bytes the container allocates. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#memory_bytes Service#memory_bytes}
        :param nano_cpus: CPU shares in units of 1/1e9 (or 10^-9) of the CPU. Should be at least 1000000. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#nano_cpus Service#nano_cpus}
        '''
        value = ServiceTaskSpecResourcesReservation(
            generic_resources=generic_resources,
            memory_bytes=memory_bytes,
            nano_cpus=nano_cpus,
        )

        return typing.cast(None, jsii.invoke(self, "putReservation", [value]))

    @jsii.member(jsii_name="resetLimits")
    def reset_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLimits", []))

    @jsii.member(jsii_name="resetReservation")
    def reset_reservation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReservation", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="limits")
    def limits(self) -> ServiceTaskSpecResourcesLimitsOutputReference:
        return typing.cast(ServiceTaskSpecResourcesLimitsOutputReference, jsii.get(self, "limits"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reservation")
    def reservation(self) -> "ServiceTaskSpecResourcesReservationOutputReference":
        return typing.cast("ServiceTaskSpecResourcesReservationOutputReference", jsii.get(self, "reservation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="limitsInput")
    def limits_input(self) -> typing.Optional[ServiceTaskSpecResourcesLimits]:
        return typing.cast(typing.Optional[ServiceTaskSpecResourcesLimits], jsii.get(self, "limitsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reservationInput")
    def reservation_input(
        self,
    ) -> typing.Optional["ServiceTaskSpecResourcesReservation"]:
        return typing.cast(typing.Optional["ServiceTaskSpecResourcesReservation"], jsii.get(self, "reservationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpecResources]:
        return typing.cast(typing.Optional[ServiceTaskSpecResources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceTaskSpecResources]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesReservation",
    jsii_struct_bases=[],
    name_mapping={
        "generic_resources": "genericResources",
        "memory_bytes": "memoryBytes",
        "nano_cpus": "nanoCpus",
    },
)
class ServiceTaskSpecResourcesReservation:
    def __init__(
        self,
        *,
        generic_resources: typing.Optional["ServiceTaskSpecResourcesReservationGenericResources"] = None,
        memory_bytes: typing.Optional[jsii.Number] = None,
        nano_cpus: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param generic_resources: generic_resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#generic_resources Service#generic_resources}
        :param memory_bytes: The amounf of memory in bytes the container allocates. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#memory_bytes Service#memory_bytes}
        :param nano_cpus: CPU shares in units of 1/1e9 (or 10^-9) of the CPU. Should be at least 1000000. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#nano_cpus Service#nano_cpus}
        '''
        if isinstance(generic_resources, dict):
            generic_resources = ServiceTaskSpecResourcesReservationGenericResources(**generic_resources)
        self._values: typing.Dict[str, typing.Any] = {}
        if generic_resources is not None:
            self._values["generic_resources"] = generic_resources
        if memory_bytes is not None:
            self._values["memory_bytes"] = memory_bytes
        if nano_cpus is not None:
            self._values["nano_cpus"] = nano_cpus

    @builtins.property
    def generic_resources(
        self,
    ) -> typing.Optional["ServiceTaskSpecResourcesReservationGenericResources"]:
        '''generic_resources block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#generic_resources Service#generic_resources}
        '''
        result = self._values.get("generic_resources")
        return typing.cast(typing.Optional["ServiceTaskSpecResourcesReservationGenericResources"], result)

    @builtins.property
    def memory_bytes(self) -> typing.Optional[jsii.Number]:
        '''The amounf of memory in bytes the container allocates.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#memory_bytes Service#memory_bytes}
        '''
        result = self._values.get("memory_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nano_cpus(self) -> typing.Optional[jsii.Number]:
        '''CPU shares in units of 1/1e9 (or 10^-9) of the CPU. Should be at least 1000000.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#nano_cpus Service#nano_cpus}
        '''
        result = self._values.get("nano_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecResourcesReservation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesReservationGenericResources",
    jsii_struct_bases=[],
    name_mapping={
        "discrete_resources_spec": "discreteResourcesSpec",
        "named_resources_spec": "namedResourcesSpec",
    },
)
class ServiceTaskSpecResourcesReservationGenericResources:
    def __init__(
        self,
        *,
        discrete_resources_spec: typing.Optional[typing.Sequence[builtins.str]] = None,
        named_resources_spec: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param discrete_resources_spec: The Integer resources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#discrete_resources_spec Service#discrete_resources_spec}
        :param named_resources_spec: The String resources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#named_resources_spec Service#named_resources_spec}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if discrete_resources_spec is not None:
            self._values["discrete_resources_spec"] = discrete_resources_spec
        if named_resources_spec is not None:
            self._values["named_resources_spec"] = named_resources_spec

    @builtins.property
    def discrete_resources_spec(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The Integer resources.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#discrete_resources_spec Service#discrete_resources_spec}
        '''
        result = self._values.get("discrete_resources_spec")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def named_resources_spec(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The String resources.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#named_resources_spec Service#named_resources_spec}
        '''
        result = self._values.get("named_resources_spec")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecResourcesReservationGenericResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecResourcesReservationGenericResourcesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesReservationGenericResourcesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetDiscreteResourcesSpec")
    def reset_discrete_resources_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiscreteResourcesSpec", []))

    @jsii.member(jsii_name="resetNamedResourcesSpec")
    def reset_named_resources_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamedResourcesSpec", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="discreteResourcesSpecInput")
    def discrete_resources_spec_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "discreteResourcesSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namedResourcesSpecInput")
    def named_resources_spec_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "namedResourcesSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="discreteResourcesSpec")
    def discrete_resources_spec(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "discreteResourcesSpec"))

    @discrete_resources_spec.setter
    def discrete_resources_spec(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "discreteResourcesSpec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namedResourcesSpec")
    def named_resources_spec(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "namedResourcesSpec"))

    @named_resources_spec.setter
    def named_resources_spec(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "namedResourcesSpec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ServiceTaskSpecResourcesReservationGenericResources]:
        return typing.cast(typing.Optional[ServiceTaskSpecResourcesReservationGenericResources], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecResourcesReservationGenericResources],
    ) -> None:
        jsii.set(self, "internalValue", value)


class ServiceTaskSpecResourcesReservationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesReservationOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="putGenericResources")
    def put_generic_resources(
        self,
        *,
        discrete_resources_spec: typing.Optional[typing.Sequence[builtins.str]] = None,
        named_resources_spec: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param discrete_resources_spec: The Integer resources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#discrete_resources_spec Service#discrete_resources_spec}
        :param named_resources_spec: The String resources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#named_resources_spec Service#named_resources_spec}
        '''
        value = ServiceTaskSpecResourcesReservationGenericResources(
            discrete_resources_spec=discrete_resources_spec,
            named_resources_spec=named_resources_spec,
        )

        return typing.cast(None, jsii.invoke(self, "putGenericResources", [value]))

    @jsii.member(jsii_name="resetGenericResources")
    def reset_generic_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenericResources", []))

    @jsii.member(jsii_name="resetMemoryBytes")
    def reset_memory_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemoryBytes", []))

    @jsii.member(jsii_name="resetNanoCpus")
    def reset_nano_cpus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNanoCpus", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="genericResources")
    def generic_resources(
        self,
    ) -> ServiceTaskSpecResourcesReservationGenericResourcesOutputReference:
        return typing.cast(ServiceTaskSpecResourcesReservationGenericResourcesOutputReference, jsii.get(self, "genericResources"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="genericResourcesInput")
    def generic_resources_input(
        self,
    ) -> typing.Optional[ServiceTaskSpecResourcesReservationGenericResources]:
        return typing.cast(typing.Optional[ServiceTaskSpecResourcesReservationGenericResources], jsii.get(self, "genericResourcesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryBytesInput")
    def memory_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryBytesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nanoCpusInput")
    def nano_cpus_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nanoCpusInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryBytes")
    def memory_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memoryBytes"))

    @memory_bytes.setter
    def memory_bytes(self, value: jsii.Number) -> None:
        jsii.set(self, "memoryBytes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nanoCpus")
    def nano_cpus(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nanoCpus"))

    @nano_cpus.setter
    def nano_cpus(self, value: jsii.Number) -> None:
        jsii.set(self, "nanoCpus", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpecResourcesReservation]:
        return typing.cast(typing.Optional[ServiceTaskSpecResourcesReservation], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecResourcesReservation],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecRestartPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "condition": "condition",
        "delay": "delay",
        "max_attempts": "maxAttempts",
        "window": "window",
    },
)
class ServiceTaskSpecRestartPolicy:
    def __init__(
        self,
        *,
        condition: typing.Optional[builtins.str] = None,
        delay: typing.Optional[builtins.str] = None,
        max_attempts: typing.Optional[jsii.Number] = None,
        window: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param condition: Condition for restart. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#condition Service#condition}
        :param delay: Delay between restart attempts (ms|s|m|h). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        :param max_attempts: Maximum attempts to restart a given container before giving up (default value is ``0``, which is ignored). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_attempts Service#max_attempts}
        :param window: The time window used to evaluate the restart policy (default value is ``0``, which is unbounded) (ms|s|m|h). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#window Service#window}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if condition is not None:
            self._values["condition"] = condition
        if delay is not None:
            self._values["delay"] = delay
        if max_attempts is not None:
            self._values["max_attempts"] = max_attempts
        if window is not None:
            self._values["window"] = window

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''Condition for restart.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#condition Service#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delay(self) -> typing.Optional[builtins.str]:
        '''Delay between restart attempts (ms|s|m|h).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        '''
        result = self._values.get("delay")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_attempts(self) -> typing.Optional[jsii.Number]:
        '''Maximum attempts to restart a given container before giving up (default value is ``0``, which is ignored).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_attempts Service#max_attempts}
        '''
        result = self._values.get("max_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def window(self) -> typing.Optional[builtins.str]:
        '''The time window used to evaluate the restart policy (default value is ``0``, which is unbounded) (ms|s|m|h).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#window Service#window}
        '''
        result = self._values.get("window")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecRestartPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceTaskSpecRestartPolicyOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecRestartPolicyOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetCondition")
    def reset_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCondition", []))

    @jsii.member(jsii_name="resetDelay")
    def reset_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelay", []))

    @jsii.member(jsii_name="resetMaxAttempts")
    def reset_max_attempts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAttempts", []))

    @jsii.member(jsii_name="resetWindow")
    def reset_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWindow", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="conditionInput")
    def condition_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "conditionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delayInput")
    def delay_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "delayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttemptsInput")
    def max_attempts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAttemptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="windowInput")
    def window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "windowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="condition")
    def condition(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "condition"))

    @condition.setter
    def condition(self, value: builtins.str) -> None:
        jsii.set(self, "condition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delay")
    def delay(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delay"))

    @delay.setter
    def delay(self, value: builtins.str) -> None:
        jsii.set(self, "delay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxAttempts")
    def max_attempts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAttempts"))

    @max_attempts.setter
    def max_attempts(self, value: jsii.Number) -> None:
        jsii.set(self, "maxAttempts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="window")
    def window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "window"))

    @window.setter
    def window(self, value: builtins.str) -> None:
        jsii.set(self, "window", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceTaskSpecRestartPolicy]:
        return typing.cast(typing.Optional[ServiceTaskSpecRestartPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ServiceTaskSpecRestartPolicy],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceUpdateConfig",
    jsii_struct_bases=[],
    name_mapping={
        "delay": "delay",
        "failure_action": "failureAction",
        "max_failure_ratio": "maxFailureRatio",
        "monitor": "monitor",
        "order": "order",
        "parallelism": "parallelism",
    },
)
class ServiceUpdateConfig:
    def __init__(
        self,
        *,
        delay: typing.Optional[builtins.str] = None,
        failure_action: typing.Optional[builtins.str] = None,
        max_failure_ratio: typing.Optional[builtins.str] = None,
        monitor: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        parallelism: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param delay: Delay between task updates (ns|us|ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        :param failure_action: Action on update failure: pause | continue | rollback. Defaults to ``pause``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#failure_action Service#failure_action}
        :param max_failure_ratio: Failure rate to tolerate during an update. Defaults to ``0.0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_failure_ratio Service#max_failure_ratio}
        :param monitor: Duration after each task update to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#monitor Service#monitor}
        :param order: Update order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#order Service#order}
        :param parallelism: Maximum number of tasks to be updated in one iteration. Defaults to ``1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#parallelism Service#parallelism}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delay is not None:
            self._values["delay"] = delay
        if failure_action is not None:
            self._values["failure_action"] = failure_action
        if max_failure_ratio is not None:
            self._values["max_failure_ratio"] = max_failure_ratio
        if monitor is not None:
            self._values["monitor"] = monitor
        if order is not None:
            self._values["order"] = order
        if parallelism is not None:
            self._values["parallelism"] = parallelism

    @builtins.property
    def delay(self) -> typing.Optional[builtins.str]:
        '''Delay between task updates (ns|us|ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#delay Service#delay}
        '''
        result = self._values.get("delay")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def failure_action(self) -> typing.Optional[builtins.str]:
        '''Action on update failure: pause | continue | rollback. Defaults to ``pause``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#failure_action Service#failure_action}
        '''
        result = self._values.get("failure_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_failure_ratio(self) -> typing.Optional[builtins.str]:
        '''Failure rate to tolerate during an update. Defaults to ``0.0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#max_failure_ratio Service#max_failure_ratio}
        '''
        result = self._values.get("max_failure_ratio")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monitor(self) -> typing.Optional[builtins.str]:
        '''Duration after each task update to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#monitor Service#monitor}
        '''
        result = self._values.get("monitor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''Update order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#order Service#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parallelism(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of tasks to be updated in one iteration. Defaults to ``1``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service#parallelism Service#parallelism}
        '''
        result = self._values.get("parallelism")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceUpdateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceUpdateConfigOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ServiceUpdateConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        is_single_item: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param is_single_item: True if this is a block, false if it's a list.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, is_single_item])

    @jsii.member(jsii_name="resetDelay")
    def reset_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelay", []))

    @jsii.member(jsii_name="resetFailureAction")
    def reset_failure_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailureAction", []))

    @jsii.member(jsii_name="resetMaxFailureRatio")
    def reset_max_failure_ratio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxFailureRatio", []))

    @jsii.member(jsii_name="resetMonitor")
    def reset_monitor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMonitor", []))

    @jsii.member(jsii_name="resetOrder")
    def reset_order(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrder", []))

    @jsii.member(jsii_name="resetParallelism")
    def reset_parallelism(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParallelism", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delayInput")
    def delay_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "delayInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureActionInput")
    def failure_action_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "failureActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxFailureRatioInput")
    def max_failure_ratio_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxFailureRatioInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitorInput")
    def monitor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "monitorInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="orderInput")
    def order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orderInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parallelismInput")
    def parallelism_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "parallelismInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delay")
    def delay(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delay"))

    @delay.setter
    def delay(self, value: builtins.str) -> None:
        jsii.set(self, "delay", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="failureAction")
    def failure_action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "failureAction"))

    @failure_action.setter
    def failure_action(self, value: builtins.str) -> None:
        jsii.set(self, "failureAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxFailureRatio")
    def max_failure_ratio(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxFailureRatio"))

    @max_failure_ratio.setter
    def max_failure_ratio(self, value: builtins.str) -> None:
        jsii.set(self, "maxFailureRatio", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="monitor")
    def monitor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "monitor"))

    @monitor.setter
    def monitor(self, value: builtins.str) -> None:
        jsii.set(self, "monitor", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="order")
    def order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "order"))

    @order.setter
    def order(self, value: builtins.str) -> None:
        jsii.set(self, "order", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parallelism")
    def parallelism(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "parallelism"))

    @parallelism.setter
    def parallelism(self, value: jsii.Number) -> None:
        jsii.set(self, "parallelism", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ServiceUpdateConfig]:
        return typing.cast(typing.Optional[ServiceUpdateConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ServiceUpdateConfig]) -> None:
        jsii.set(self, "internalValue", value)


class Volume(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Volume",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/volume docker_volume}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        driver: typing.Optional[builtins.str] = None,
        driver_opts: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        labels: typing.Optional[typing.Sequence["VolumeLabels"]] = None,
        name: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/volume docker_volume} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param driver: Driver type for the volume. Defaults to ``local``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#driver Volume#driver}
        :param driver_opts: Options specific to the driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#driver_opts Volume#driver_opts}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#labels Volume#labels}
        :param name: The name of the Docker volume (will be generated if not provided). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#name Volume#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = VolumeConfig(
            driver=driver,
            driver_opts=driver_opts,
            labels=labels,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDriver")
    def reset_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriver", []))

    @jsii.member(jsii_name="resetDriverOpts")
    def reset_driver_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverOpts", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

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
    @jsii.member(jsii_name="mountpoint")
    def mountpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverInput")
    def driver_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverOptsInput")
    def driver_opts_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "driverOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["VolumeLabels"]]:
        return typing.cast(typing.Optional[typing.List["VolumeLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driver")
    def driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driver"))

    @driver.setter
    def driver(self, value: builtins.str) -> None:
        jsii.set(self, "driver", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverOpts")
    def driver_opts(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "driverOpts"))

    @driver_opts.setter
    def driver_opts(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "driverOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["VolumeLabels"]:
        return typing.cast(typing.List["VolumeLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["VolumeLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.VolumeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "driver": "driver",
        "driver_opts": "driverOpts",
        "labels": "labels",
        "name": "name",
    },
)
class VolumeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        driver: typing.Optional[builtins.str] = None,
        driver_opts: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        labels: typing.Optional[typing.Sequence["VolumeLabels"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param driver: Driver type for the volume. Defaults to ``local``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#driver Volume#driver}
        :param driver_opts: Options specific to the driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#driver_opts Volume#driver_opts}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#labels Volume#labels}
        :param name: The name of the Docker volume (will be generated if not provided). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#name Volume#name}
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
        if driver is not None:
            self._values["driver"] = driver
        if driver_opts is not None:
            self._values["driver_opts"] = driver_opts
        if labels is not None:
            self._values["labels"] = labels
        if name is not None:
            self._values["name"] = name

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
    def driver(self) -> typing.Optional[builtins.str]:
        '''Driver type for the volume. Defaults to ``local``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#driver Volume#driver}
        '''
        result = self._values.get("driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def driver_opts(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Options specific to the driver.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#driver_opts Volume#driver_opts}
        '''
        result = self._values.get("driver_opts")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["VolumeLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#labels Volume#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["VolumeLabels"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the Docker volume (will be generated if not provided).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#name Volume#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VolumeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.VolumeLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class VolumeLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#label Volume#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#value Volume#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#label Volume#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume#value Volume#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VolumeLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Config",
    "ConfigConfig",
    "Container",
    "ContainerCapabilities",
    "ContainerCapabilitiesOutputReference",
    "ContainerConfig",
    "ContainerDevices",
    "ContainerHealthcheck",
    "ContainerHealthcheckOutputReference",
    "ContainerHost",
    "ContainerLabels",
    "ContainerMounts",
    "ContainerMountsBindOptions",
    "ContainerMountsBindOptionsOutputReference",
    "ContainerMountsTmpfsOptions",
    "ContainerMountsTmpfsOptionsOutputReference",
    "ContainerMountsVolumeOptions",
    "ContainerMountsVolumeOptionsLabels",
    "ContainerMountsVolumeOptionsOutputReference",
    "ContainerNetworkData",
    "ContainerNetworksAdvanced",
    "ContainerPorts",
    "ContainerUlimit",
    "ContainerUpload",
    "ContainerVolumes",
    "DataDockerImage",
    "DataDockerImageConfig",
    "DataDockerNetwork",
    "DataDockerNetworkConfig",
    "DataDockerNetworkIpamConfig",
    "DataDockerPlugin",
    "DataDockerPluginConfig",
    "DataDockerRegistryImage",
    "DataDockerRegistryImageConfig",
    "DockerProvider",
    "DockerProviderConfig",
    "DockerProviderRegistryAuth",
    "Image",
    "ImageBuild",
    "ImageBuildOutputReference",
    "ImageConfig",
    "Network",
    "NetworkConfig",
    "NetworkIpamConfig",
    "NetworkLabels",
    "Plugin",
    "PluginConfig",
    "PluginGrantPermissions",
    "RegistryImage",
    "RegistryImageBuild",
    "RegistryImageBuildAuthConfig",
    "RegistryImageBuildOutputReference",
    "RegistryImageBuildUlimit",
    "RegistryImageConfig",
    "Secret",
    "SecretConfig",
    "SecretLabels",
    "Service",
    "ServiceAuth",
    "ServiceAuthOutputReference",
    "ServiceConfig",
    "ServiceConvergeConfig",
    "ServiceConvergeConfigOutputReference",
    "ServiceEndpointSpec",
    "ServiceEndpointSpecOutputReference",
    "ServiceEndpointSpecPorts",
    "ServiceLabels",
    "ServiceMode",
    "ServiceModeOutputReference",
    "ServiceModeReplicated",
    "ServiceModeReplicatedOutputReference",
    "ServiceRollbackConfig",
    "ServiceRollbackConfigOutputReference",
    "ServiceTaskSpec",
    "ServiceTaskSpecContainerSpec",
    "ServiceTaskSpecContainerSpecConfigs",
    "ServiceTaskSpecContainerSpecDnsConfig",
    "ServiceTaskSpecContainerSpecDnsConfigOutputReference",
    "ServiceTaskSpecContainerSpecHealthcheck",
    "ServiceTaskSpecContainerSpecHealthcheckOutputReference",
    "ServiceTaskSpecContainerSpecHosts",
    "ServiceTaskSpecContainerSpecLabels",
    "ServiceTaskSpecContainerSpecMounts",
    "ServiceTaskSpecContainerSpecMountsBindOptions",
    "ServiceTaskSpecContainerSpecMountsBindOptionsOutputReference",
    "ServiceTaskSpecContainerSpecMountsTmpfsOptions",
    "ServiceTaskSpecContainerSpecMountsTmpfsOptionsOutputReference",
    "ServiceTaskSpecContainerSpecMountsVolumeOptions",
    "ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels",
    "ServiceTaskSpecContainerSpecMountsVolumeOptionsOutputReference",
    "ServiceTaskSpecContainerSpecOutputReference",
    "ServiceTaskSpecContainerSpecPrivileges",
    "ServiceTaskSpecContainerSpecPrivilegesCredentialSpec",
    "ServiceTaskSpecContainerSpecPrivilegesCredentialSpecOutputReference",
    "ServiceTaskSpecContainerSpecPrivilegesOutputReference",
    "ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext",
    "ServiceTaskSpecContainerSpecPrivilegesSeLinuxContextOutputReference",
    "ServiceTaskSpecContainerSpecSecrets",
    "ServiceTaskSpecLogDriver",
    "ServiceTaskSpecLogDriverOutputReference",
    "ServiceTaskSpecOutputReference",
    "ServiceTaskSpecPlacement",
    "ServiceTaskSpecPlacementOutputReference",
    "ServiceTaskSpecPlacementPlatforms",
    "ServiceTaskSpecResources",
    "ServiceTaskSpecResourcesLimits",
    "ServiceTaskSpecResourcesLimitsOutputReference",
    "ServiceTaskSpecResourcesOutputReference",
    "ServiceTaskSpecResourcesReservation",
    "ServiceTaskSpecResourcesReservationGenericResources",
    "ServiceTaskSpecResourcesReservationGenericResourcesOutputReference",
    "ServiceTaskSpecResourcesReservationOutputReference",
    "ServiceTaskSpecRestartPolicy",
    "ServiceTaskSpecRestartPolicyOutputReference",
    "ServiceUpdateConfig",
    "ServiceUpdateConfigOutputReference",
    "Volume",
    "VolumeConfig",
    "VolumeLabels",
]

publication.publish()
