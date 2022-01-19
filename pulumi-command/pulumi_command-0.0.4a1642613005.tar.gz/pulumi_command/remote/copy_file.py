# coding=utf-8
# *** WARNING: this file was generated by pulumigen. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs
from ._inputs import *

__all__ = ['CopyFileArgs', 'CopyFile']

@pulumi.input_type
class CopyFileArgs:
    def __init__(__self__, *,
                 connection: pulumi.Input['ConnectionArgs'],
                 local_path: pulumi.Input[str],
                 remote_path: pulumi.Input[str],
                 triggers: Optional[pulumi.Input[Sequence[Any]]] = None):
        """
        The set of arguments for constructing a CopyFile resource.
        :param pulumi.Input['ConnectionArgs'] connection: The parameters with which to connect to the remote host.
        :param pulumi.Input[str] local_path: The path of the file to be copied.
        :param pulumi.Input[str] remote_path: The destination path in the remote host.
        :param pulumi.Input[Sequence[Any]] triggers: Trigger replacements on changes to this input.
        """
        pulumi.set(__self__, "connection", connection)
        pulumi.set(__self__, "local_path", local_path)
        pulumi.set(__self__, "remote_path", remote_path)
        if triggers is not None:
            pulumi.set(__self__, "triggers", triggers)

    @property
    @pulumi.getter
    def connection(self) -> pulumi.Input['ConnectionArgs']:
        """
        The parameters with which to connect to the remote host.
        """
        return pulumi.get(self, "connection")

    @connection.setter
    def connection(self, value: pulumi.Input['ConnectionArgs']):
        pulumi.set(self, "connection", value)

    @property
    @pulumi.getter(name="localPath")
    def local_path(self) -> pulumi.Input[str]:
        """
        The path of the file to be copied.
        """
        return pulumi.get(self, "local_path")

    @local_path.setter
    def local_path(self, value: pulumi.Input[str]):
        pulumi.set(self, "local_path", value)

    @property
    @pulumi.getter(name="remotePath")
    def remote_path(self) -> pulumi.Input[str]:
        """
        The destination path in the remote host.
        """
        return pulumi.get(self, "remote_path")

    @remote_path.setter
    def remote_path(self, value: pulumi.Input[str]):
        pulumi.set(self, "remote_path", value)

    @property
    @pulumi.getter
    def triggers(self) -> Optional[pulumi.Input[Sequence[Any]]]:
        """
        Trigger replacements on changes to this input.
        """
        return pulumi.get(self, "triggers")

    @triggers.setter
    def triggers(self, value: Optional[pulumi.Input[Sequence[Any]]]):
        pulumi.set(self, "triggers", value)


class CopyFile(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 connection: Optional[pulumi.Input[pulumi.InputType['ConnectionArgs']]] = None,
                 local_path: Optional[pulumi.Input[str]] = None,
                 remote_path: Optional[pulumi.Input[str]] = None,
                 triggers: Optional[pulumi.Input[Sequence[Any]]] = None,
                 __props__=None):
        """
        Copy a local file to a remote host.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['ConnectionArgs']] connection: The parameters with which to connect to the remote host.
        :param pulumi.Input[str] local_path: The path of the file to be copied.
        :param pulumi.Input[str] remote_path: The destination path in the remote host.
        :param pulumi.Input[Sequence[Any]] triggers: Trigger replacements on changes to this input.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: CopyFileArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Copy a local file to a remote host.

        :param str resource_name: The name of the resource.
        :param CopyFileArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(CopyFileArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 connection: Optional[pulumi.Input[pulumi.InputType['ConnectionArgs']]] = None,
                 local_path: Optional[pulumi.Input[str]] = None,
                 remote_path: Optional[pulumi.Input[str]] = None,
                 triggers: Optional[pulumi.Input[Sequence[Any]]] = None,
                 __props__=None):
        if opts is None:
            opts = pulumi.ResourceOptions()
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.version is None:
            opts.version = _utilities.get_version()
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = CopyFileArgs.__new__(CopyFileArgs)

            if connection is None and not opts.urn:
                raise TypeError("Missing required property 'connection'")
            __props__.__dict__["connection"] = connection
            if local_path is None and not opts.urn:
                raise TypeError("Missing required property 'local_path'")
            __props__.__dict__["local_path"] = local_path
            if remote_path is None and not opts.urn:
                raise TypeError("Missing required property 'remote_path'")
            __props__.__dict__["remote_path"] = remote_path
            __props__.__dict__["triggers"] = triggers
        super(CopyFile, __self__).__init__(
            'command:remote:CopyFile',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'CopyFile':
        """
        Get an existing CopyFile resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = CopyFileArgs.__new__(CopyFileArgs)

        __props__.__dict__["connection"] = None
        __props__.__dict__["local_path"] = None
        __props__.__dict__["remote_path"] = None
        __props__.__dict__["triggers"] = None
        return CopyFile(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def connection(self) -> pulumi.Output['outputs.Connection']:
        """
        The parameters with which to connect to the remote host.
        """
        return pulumi.get(self, "connection")

    @property
    @pulumi.getter(name="localPath")
    def local_path(self) -> pulumi.Output[str]:
        """
        The path of the file to be copied.
        """
        return pulumi.get(self, "local_path")

    @property
    @pulumi.getter(name="remotePath")
    def remote_path(self) -> pulumi.Output[str]:
        """
        The destination path in the remote host.
        """
        return pulumi.get(self, "remote_path")

    @property
    @pulumi.getter
    def triggers(self) -> pulumi.Output[Optional[Sequence[Any]]]:
        """
        Trigger replacements on changes to this input.
        """
        return pulumi.get(self, "triggers")

