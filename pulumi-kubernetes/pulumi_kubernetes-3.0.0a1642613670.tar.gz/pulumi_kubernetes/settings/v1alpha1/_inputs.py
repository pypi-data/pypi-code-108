# coding=utf-8
# *** WARNING: this file was generated by pulumigen. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from ... import _utilities
from ... import core as _core
from ... import meta as _meta

__all__ = [
    'PodPresetSpecArgs',
    'PodPresetArgs',
]

@pulumi.input_type
class PodPresetSpecArgs:
    def __init__(__self__, *,
                 env: Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.EnvVarArgs']]]] = None,
                 env_from: Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.EnvFromSourceArgs']]]] = None,
                 selector: Optional[pulumi.Input['_meta.v1.LabelSelectorArgs']] = None,
                 volume_mounts: Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.VolumeMountArgs']]]] = None,
                 volumes: Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.VolumeArgs']]]] = None):
        """
        PodPresetSpec is a description of a pod preset.
        :param pulumi.Input[Sequence[pulumi.Input['_core.v1.EnvVarArgs']]] env: Env defines the collection of EnvVar to inject into containers.
        :param pulumi.Input[Sequence[pulumi.Input['_core.v1.EnvFromSourceArgs']]] env_from: EnvFrom defines the collection of EnvFromSource to inject into containers.
        :param pulumi.Input['_meta.v1.LabelSelectorArgs'] selector: Selector is a label query over a set of resources, in this case pods. Required.
        :param pulumi.Input[Sequence[pulumi.Input['_core.v1.VolumeMountArgs']]] volume_mounts: VolumeMounts defines the collection of VolumeMount to inject into containers.
        :param pulumi.Input[Sequence[pulumi.Input['_core.v1.VolumeArgs']]] volumes: Volumes defines the collection of Volume to inject into the pod.
        """
        if env is not None:
            pulumi.set(__self__, "env", env)
        if env_from is not None:
            pulumi.set(__self__, "env_from", env_from)
        if selector is not None:
            pulumi.set(__self__, "selector", selector)
        if volume_mounts is not None:
            pulumi.set(__self__, "volume_mounts", volume_mounts)
        if volumes is not None:
            pulumi.set(__self__, "volumes", volumes)

    @property
    @pulumi.getter
    def env(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.EnvVarArgs']]]]:
        """
        Env defines the collection of EnvVar to inject into containers.
        """
        return pulumi.get(self, "env")

    @env.setter
    def env(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.EnvVarArgs']]]]):
        pulumi.set(self, "env", value)

    @property
    @pulumi.getter(name="envFrom")
    def env_from(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.EnvFromSourceArgs']]]]:
        """
        EnvFrom defines the collection of EnvFromSource to inject into containers.
        """
        return pulumi.get(self, "env_from")

    @env_from.setter
    def env_from(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.EnvFromSourceArgs']]]]):
        pulumi.set(self, "env_from", value)

    @property
    @pulumi.getter
    def selector(self) -> Optional[pulumi.Input['_meta.v1.LabelSelectorArgs']]:
        """
        Selector is a label query over a set of resources, in this case pods. Required.
        """
        return pulumi.get(self, "selector")

    @selector.setter
    def selector(self, value: Optional[pulumi.Input['_meta.v1.LabelSelectorArgs']]):
        pulumi.set(self, "selector", value)

    @property
    @pulumi.getter(name="volumeMounts")
    def volume_mounts(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.VolumeMountArgs']]]]:
        """
        VolumeMounts defines the collection of VolumeMount to inject into containers.
        """
        return pulumi.get(self, "volume_mounts")

    @volume_mounts.setter
    def volume_mounts(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.VolumeMountArgs']]]]):
        pulumi.set(self, "volume_mounts", value)

    @property
    @pulumi.getter
    def volumes(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.VolumeArgs']]]]:
        """
        Volumes defines the collection of Volume to inject into the pod.
        """
        return pulumi.get(self, "volumes")

    @volumes.setter
    def volumes(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['_core.v1.VolumeArgs']]]]):
        pulumi.set(self, "volumes", value)


@pulumi.input_type
class PodPresetArgs:
    def __init__(__self__, *,
                 api_version: Optional[pulumi.Input[str]] = None,
                 kind: Optional[pulumi.Input[str]] = None,
                 metadata: Optional[pulumi.Input['_meta.v1.ObjectMetaArgs']] = None,
                 spec: Optional[pulumi.Input['PodPresetSpecArgs']] = None):
        """
        PodPreset is a policy resource that defines additional runtime requirements for a Pod.
        :param pulumi.Input[str] api_version: APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        :param pulumi.Input[str] kind: Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        """
        if api_version is not None:
            pulumi.set(__self__, "api_version", 'settings.k8s.io/v1alpha1')
        if kind is not None:
            pulumi.set(__self__, "kind", 'PodPreset')
        if metadata is not None:
            pulumi.set(__self__, "metadata", metadata)
        if spec is not None:
            pulumi.set(__self__, "spec", spec)

    @property
    @pulumi.getter(name="apiVersion")
    def api_version(self) -> Optional[pulumi.Input[str]]:
        """
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        """
        return pulumi.get(self, "api_version")

    @api_version.setter
    def api_version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "api_version", value)

    @property
    @pulumi.getter
    def kind(self) -> Optional[pulumi.Input[str]]:
        """
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        """
        return pulumi.get(self, "kind")

    @kind.setter
    def kind(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kind", value)

    @property
    @pulumi.getter
    def metadata(self) -> Optional[pulumi.Input['_meta.v1.ObjectMetaArgs']]:
        return pulumi.get(self, "metadata")

    @metadata.setter
    def metadata(self, value: Optional[pulumi.Input['_meta.v1.ObjectMetaArgs']]):
        pulumi.set(self, "metadata", value)

    @property
    @pulumi.getter
    def spec(self) -> Optional[pulumi.Input['PodPresetSpecArgs']]:
        return pulumi.get(self, "spec")

    @spec.setter
    def spec(self, value: Optional[pulumi.Input['PodPresetSpecArgs']]):
        pulumi.set(self, "spec", value)


