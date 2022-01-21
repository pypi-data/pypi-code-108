'''
# cdk8s

### Cloud Development Kit for Kubernetes

[![build](https://github.com/cdk8s-team/cdk8s-core/workflows/release/badge.svg)](https://github.com/cdk8s-team/cdk8s-core/actions/workflows/release.yml)
[![npm version](https://badge.fury.io/js/cdk8s.svg)](https://badge.fury.io/js/cdk8s)
[![PyPI version](https://badge.fury.io/py/cdk8s.svg)](https://badge.fury.io/py/cdk8s)
[![Maven Central](https://maven-badges.herokuapp.com/maven-central/org.cdk8s/cdk8s/badge.svg)](https://maven-badges.herokuapp.com/maven-central/org.cdk8s/cdk8s)

**cdk8s** is a software development framework for defining Kubernetes
applications using rich object-oriented APIs. It allows developers to leverage
the full power of software in order to define abstract components called
"constructs" which compose Kubernetes resources or other constructs into
higher-level abstractions.

> **Note:** This repository is the "core library" of cdk8s, with logic for synthesizing Kubernetes manifests using the [constructs framework](https://github.com/aws/constructs). It is published to NPM as [`cdk8s`](https://www.npmjs.com/package/cdk8s) and should not be confused with the cdk8s command-line tool [`cdk8s-cli`](https://www.npmjs.com/package/cdk8s-cli). For more general information about cdk8s, please see [cdk8s.io](https://cdk8s.io), or visit the umbrella repository located at [cdk8s-team/cdk8s](https://github.com/cdk8s-team/cdk8s).

## Documentation

See [cdk8s.io](https://cdk8s.io).

## License

This project is distributed under the [Apache License, Version 2.0](./LICENSE).

This module is part of the [cdk8s project](https://github.com/cdk8s-team/cdk8s).
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


class ApiObject(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s.ApiObject",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_version: builtins.str,
        kind: builtins.str,
        metadata: typing.Optional["ApiObjectMetadata"] = None,
    ) -> None:
        '''Defines an API object.

        :param scope: the construct scope.
        :param id: namespace.
        :param api_version: API version.
        :param kind: Resource kind.
        :param metadata: Object metadata. If ``name`` is not specified, an app-unique name will be allocated by the framework based on the path of the construct within thes construct tree.
        '''
        props = ApiObjectProps(api_version=api_version, kind=kind, metadata=metadata)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, c: constructs.IConstruct) -> "ApiObject":
        '''Returns the ``ApiObject`` named ``Resource`` which is a child of the given construct.

        If ``c`` is an ``ApiObject``, it is returned directly. Throws an
        exception if the construct does not have a child named ``Default`` *or* if
        this child is not an ``ApiObject``.

        :param c: The higher-level construct.
        '''
        return typing.cast("ApiObject", jsii.sinvoke(cls, "of", [c]))

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, *dependencies: constructs.IConstruct) -> None:
        '''Create a dependency between this ApiObject and other constructs.

        These can be other ApiObjects, Charts, or custom.

        :param dependencies: the dependencies to add.
        '''
        return typing.cast(None, jsii.invoke(self, "addDependency", [*dependencies]))

    @jsii.member(jsii_name="addJsonPatch")
    def add_json_patch(self, *ops: "JsonPatch") -> None:
        '''Applies a set of RFC-6902 JSON-Patch operations to the manifest synthesized for this API object.

        :param ops: The JSON-Patch operations to apply.

        Example::

              kubePod.addJsonPatch(JsonPatch.replace('/spec/enableServiceLinks', true));
        '''
        return typing.cast(None, jsii.invoke(self, "addJsonPatch", [*ops]))

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.Any:
        '''Renders the object to Kubernetes JSON.

        To disable sorting of dictionary keys in output object set the
        ``CDK8S_DISABLE_SORT`` environment variable to any non-empty value.
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "toJson", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiGroup")
    def api_group(self) -> builtins.str:
        '''The group portion of the API version (e.g. ``authorization.k8s.io``).'''
        return typing.cast(builtins.str, jsii.get(self, "apiGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiVersion")
    def api_version(self) -> builtins.str:
        '''The object's API version (e.g. ``authorization.k8s.io/v1``).'''
        return typing.cast(builtins.str, jsii.get(self, "apiVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="chart")
    def chart(self) -> "Chart":
        '''The chart in which this object is defined.'''
        return typing.cast("Chart", jsii.get(self, "chart"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kind")
    def kind(self) -> builtins.str:
        '''The object kind.'''
        return typing.cast(builtins.str, jsii.get(self, "kind"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> "ApiObjectMetadataDefinition":
        '''Metadata associated with this API object.'''
        return typing.cast("ApiObjectMetadataDefinition", jsii.get(self, "metadata"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the API object.

        If a name is specified in ``metadata.name`` this will be the name returned.
        Otherwise, a name will be generated by calling
        ``Chart.of(this).generatedObjectName(this)``, which by default uses the
        construct path to generate a DNS-compatible name for the resource.
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))


@jsii.data_type(
    jsii_type="cdk8s.ApiObjectMetadata",
    jsii_struct_bases=[],
    name_mapping={
        "annotations": "annotations",
        "finalizers": "finalizers",
        "labels": "labels",
        "name": "name",
        "namespace": "namespace",
        "owner_references": "ownerReferences",
    },
)
class ApiObjectMetadata:
    def __init__(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        finalizers: typing.Optional[typing.Sequence[builtins.str]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        owner_references: typing.Optional[typing.Sequence["OwnerReference"]] = None,
    ) -> None:
        '''Metadata associated with this object.

        :param annotations: Annotations is an unstructured key value map stored with a resource that may be set by external tools to store and retrieve arbitrary metadata. They are not queryable and should be preserved when modifying objects. Default: - No annotations.
        :param finalizers: Namespaced keys that tell Kubernetes to wait until specific conditions are met before it fully deletes resources marked for deletion. Must be empty before the object is deleted from the registry. Each entry is an identifier for the responsible component that will remove the entry from the list. If the deletionTimestamp of the object is non-nil, entries in this list can only be removed. Finalizers may be processed and removed in any order. Order is NOT enforced because it introduces significant risk of stuck finalizers. finalizers is a shared field, any actor with permission can reorder it. If the finalizer list is processed in order, then this can lead to a situation in which the component responsible for the first finalizer in the list is waiting for a signal (field value, external system, or other) produced by a component responsible for a finalizer later in the list, resulting in a deadlock. Without enforced ordering finalizers are free to order amongst themselves and are not vulnerable to ordering changes in the list. Default: - No finalizers.
        :param labels: Map of string keys and values that can be used to organize and categorize (scope and select) objects. May match selectors of replication controllers and services. Default: - No labels.
        :param name: The unique, namespace-global, name of this object inside the Kubernetes cluster. Normally, you shouldn't specify names for objects and let the CDK generate a name for you that is application-unique. The names CDK generates are composed from the construct path components, separated by dots and a suffix that is based on a hash of the entire path, to ensure uniqueness. You can supply custom name allocation logic by overriding the ``chart.generateObjectName`` method. If you use an explicit name here, bear in mind that this reduces the composability of your construct because it won't be possible to include more than one instance in any app. Therefore it is highly recommended to leave this unspecified. Default: - an app-unique name generated by the chart
        :param namespace: Namespace defines the space within each name must be unique. An empty namespace is equivalent to the "default" namespace, but "default" is the canonical representation. Not all objects are required to be scoped to a namespace - the value of this field for those objects will be empty. Must be a DNS_LABEL. Cannot be updated. More info: http://kubernetes.io/docs/user-guide/namespaces Default: undefined (will be assigned to the 'default' namespace)
        :param owner_references: List of objects depended by this object. If ALL objects in the list have been deleted, this object will be garbage collected. If this object is managed by a controller, then an entry in this list will point to this controller, with the controller field set to true. There cannot be more than one managing controller. Kubernetes sets the value of this field automatically for objects that are dependents of other objects like ReplicaSets, DaemonSets, Deployments, Jobs and CronJobs, and ReplicationControllers. You can also configure these relationships manually by changing the value of this field. However, you usually don't need to and can allow Kubernetes to automatically manage the relationships. Default: - automatically set by Kubernetes
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if annotations is not None:
            self._values["annotations"] = annotations
        if finalizers is not None:
            self._values["finalizers"] = finalizers
        if labels is not None:
            self._values["labels"] = labels
        if name is not None:
            self._values["name"] = name
        if namespace is not None:
            self._values["namespace"] = namespace
        if owner_references is not None:
            self._values["owner_references"] = owner_references

    @builtins.property
    def annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Annotations is an unstructured key value map stored with a resource that may be set by external tools to store and retrieve arbitrary metadata.

        They are not queryable and should be
        preserved when modifying objects.

        :default: - No annotations.

        :see: http://kubernetes.io/docs/user-guide/annotations
        '''
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def finalizers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Namespaced keys that tell Kubernetes to wait until specific conditions are met before it fully deletes resources marked for deletion.

        Must be empty before the object is deleted from the registry. Each entry is
        an identifier for the responsible component that will remove the entry from
        the list. If the deletionTimestamp of the object is non-nil, entries in
        this list can only be removed. Finalizers may be processed and removed in
        any order.  Order is NOT enforced because it introduces significant risk of
        stuck finalizers. finalizers is a shared field, any actor with permission
        can reorder it. If the finalizer list is processed in order, then this can
        lead to a situation in which the component responsible for the first
        finalizer in the list is waiting for a signal (field value, external
        system, or other) produced by a component responsible for a finalizer later
        in the list, resulting in a deadlock. Without enforced ordering finalizers
        are free to order amongst themselves and are not vulnerable to ordering
        changes in the list.

        :default: - No finalizers.

        :see: https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/
        '''
        result = self._values.get("finalizers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Map of string keys and values that can be used to organize and categorize (scope and select) objects.

        May match selectors of replication controllers and services.

        :default: - No labels.

        :see: http://kubernetes.io/docs/user-guide/labels
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The unique, namespace-global, name of this object inside the Kubernetes cluster.

        Normally, you shouldn't specify names for objects and let the CDK generate
        a name for you that is application-unique. The names CDK generates are
        composed from the construct path components, separated by dots and a suffix
        that is based on a hash of the entire path, to ensure uniqueness.

        You can supply custom name allocation logic by overriding the
        ``chart.generateObjectName`` method.

        If you use an explicit name here, bear in mind that this reduces the
        composability of your construct because it won't be possible to include
        more than one instance in any app. Therefore it is highly recommended to
        leave this unspecified.

        :default: - an app-unique name generated by the chart
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Namespace defines the space within each name must be unique.

        An empty namespace is equivalent to the "default" namespace, but "default" is the canonical representation.
        Not all objects are required to be scoped to a namespace - the value of this field for those objects will be empty. Must be a DNS_LABEL. Cannot be updated. More info: http://kubernetes.io/docs/user-guide/namespaces

        :default: undefined (will be assigned to the 'default' namespace)
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner_references(self) -> typing.Optional[typing.List["OwnerReference"]]:
        '''List of objects depended by this object.

        If ALL objects in the list have
        been deleted, this object will be garbage collected. If this object is
        managed by a controller, then an entry in this list will point to this
        controller, with the controller field set to true. There cannot be more
        than one managing controller.

        Kubernetes sets the value of this field automatically for objects that are
        dependents of other objects like ReplicaSets, DaemonSets, Deployments, Jobs
        and CronJobs, and ReplicationControllers. You can also configure these
        relationships manually by changing the value of this field. However, you
        usually don't need to and can allow Kubernetes to automatically manage the
        relationships.

        :default: - automatically set by Kubernetes

        :see: https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/
        '''
        result = self._values.get("owner_references")
        return typing.cast(typing.Optional[typing.List["OwnerReference"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiObjectMetadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApiObjectMetadataDefinition(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s.ApiObjectMetadataDefinition",
):
    '''Object metadata.'''

    def __init__(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        finalizers: typing.Optional[typing.Sequence[builtins.str]] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        owner_references: typing.Optional[typing.Sequence["OwnerReference"]] = None,
    ) -> None:
        '''
        :param annotations: Annotations is an unstructured key value map stored with a resource that may be set by external tools to store and retrieve arbitrary metadata. They are not queryable and should be preserved when modifying objects. Default: - No annotations.
        :param finalizers: Namespaced keys that tell Kubernetes to wait until specific conditions are met before it fully deletes resources marked for deletion. Must be empty before the object is deleted from the registry. Each entry is an identifier for the responsible component that will remove the entry from the list. If the deletionTimestamp of the object is non-nil, entries in this list can only be removed. Finalizers may be processed and removed in any order. Order is NOT enforced because it introduces significant risk of stuck finalizers. finalizers is a shared field, any actor with permission can reorder it. If the finalizer list is processed in order, then this can lead to a situation in which the component responsible for the first finalizer in the list is waiting for a signal (field value, external system, or other) produced by a component responsible for a finalizer later in the list, resulting in a deadlock. Without enforced ordering finalizers are free to order amongst themselves and are not vulnerable to ordering changes in the list. Default: - No finalizers.
        :param labels: Map of string keys and values that can be used to organize and categorize (scope and select) objects. May match selectors of replication controllers and services. Default: - No labels.
        :param name: The unique, namespace-global, name of this object inside the Kubernetes cluster. Normally, you shouldn't specify names for objects and let the CDK generate a name for you that is application-unique. The names CDK generates are composed from the construct path components, separated by dots and a suffix that is based on a hash of the entire path, to ensure uniqueness. You can supply custom name allocation logic by overriding the ``chart.generateObjectName`` method. If you use an explicit name here, bear in mind that this reduces the composability of your construct because it won't be possible to include more than one instance in any app. Therefore it is highly recommended to leave this unspecified. Default: - an app-unique name generated by the chart
        :param namespace: Namespace defines the space within each name must be unique. An empty namespace is equivalent to the "default" namespace, but "default" is the canonical representation. Not all objects are required to be scoped to a namespace - the value of this field for those objects will be empty. Must be a DNS_LABEL. Cannot be updated. More info: http://kubernetes.io/docs/user-guide/namespaces Default: undefined (will be assigned to the 'default' namespace)
        :param owner_references: List of objects depended by this object. If ALL objects in the list have been deleted, this object will be garbage collected. If this object is managed by a controller, then an entry in this list will point to this controller, with the controller field set to true. There cannot be more than one managing controller. Kubernetes sets the value of this field automatically for objects that are dependents of other objects like ReplicaSets, DaemonSets, Deployments, Jobs and CronJobs, and ReplicationControllers. You can also configure these relationships manually by changing the value of this field. However, you usually don't need to and can allow Kubernetes to automatically manage the relationships. Default: - automatically set by Kubernetes
        '''
        options = ApiObjectMetadata(
            annotations=annotations,
            finalizers=finalizers,
            labels=labels,
            name=name,
            namespace=namespace,
            owner_references=owner_references,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="add")
    def add(self, key: builtins.str, value: typing.Any) -> None:
        '''Adds an arbitrary key/value to the object metadata.

        :param key: Metadata key.
        :param value: Metadata value.
        '''
        return typing.cast(None, jsii.invoke(self, "add", [key, value]))

    @jsii.member(jsii_name="addAnnotation")
    def add_annotation(self, key: builtins.str, value: builtins.str) -> None:
        '''Add an annotation.

        :param key: - The key.
        :param value: - The value.
        '''
        return typing.cast(None, jsii.invoke(self, "addAnnotation", [key, value]))

    @jsii.member(jsii_name="addFinalizers")
    def add_finalizers(self, *finalizers: builtins.str) -> None:
        '''Add one or more finalizers.

        :param finalizers: the finalizers.
        '''
        return typing.cast(None, jsii.invoke(self, "addFinalizers", [*finalizers]))

    @jsii.member(jsii_name="addLabel")
    def add_label(self, key: builtins.str, value: builtins.str) -> None:
        '''Add a label.

        :param key: - The key.
        :param value: - The value.
        '''
        return typing.cast(None, jsii.invoke(self, "addLabel", [key, value]))

    @jsii.member(jsii_name="addOwnerReference")
    def add_owner_reference(
        self,
        *,
        api_version: builtins.str,
        kind: builtins.str,
        name: builtins.str,
        uid: builtins.str,
        block_owner_deletion: typing.Optional[builtins.bool] = None,
        controller: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Add an owner.

        :param api_version: API version of the referent.
        :param kind: Kind of the referent.
        :param name: Name of the referent.
        :param uid: UID of the referent.
        :param block_owner_deletion: If true, AND if the owner has the "foregroundDeletion" finalizer, then the owner cannot be deleted from the key-value store until this reference is removed. Defaults to false. To set this field, a user needs "delete" permission of the owner, otherwise 422 (Unprocessable Entity) will be returned. Default: false. To set this field, a user needs "delete" permission of the owner, otherwise 422 (Unprocessable Entity) will be returned.
        :param controller: If true, this reference points to the managing controller.
        '''
        owner = OwnerReference(
            api_version=api_version,
            kind=kind,
            name=name,
            uid=uid,
            block_owner_deletion=block_owner_deletion,
            controller=controller,
        )

        return typing.cast(None, jsii.invoke(self, "addOwnerReference", [owner]))

    @jsii.member(jsii_name="getLabel")
    def get_label(self, key: builtins.str) -> typing.Optional[builtins.str]:
        '''
        :param key: the label.

        :return: a value of a label or undefined
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "getLabel", [key]))

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.Any:
        '''Synthesizes a k8s ObjectMeta for this metadata set.'''
        return typing.cast(typing.Any, jsii.invoke(self, "toJson", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the API object.

        If a name is specified in ``metadata.name`` this will be the name returned.
        Otherwise, a name will be generated by calling
        ``Chart.of(this).generatedObjectName(this)``, which by default uses the
        construct path to generate a DNS-compatible name for the resource.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The object's namespace.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespace"))


@jsii.data_type(
    jsii_type="cdk8s.ApiObjectProps",
    jsii_struct_bases=[],
    name_mapping={"api_version": "apiVersion", "kind": "kind", "metadata": "metadata"},
)
class ApiObjectProps:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        kind: builtins.str,
        metadata: typing.Optional[ApiObjectMetadata] = None,
    ) -> None:
        '''Options for defining API objects.

        :param api_version: API version.
        :param kind: Resource kind.
        :param metadata: Object metadata. If ``name`` is not specified, an app-unique name will be allocated by the framework based on the path of the construct within thes construct tree.
        '''
        if isinstance(metadata, dict):
            metadata = ApiObjectMetadata(**metadata)
        self._values: typing.Dict[str, typing.Any] = {
            "api_version": api_version,
            "kind": kind,
        }
        if metadata is not None:
            self._values["metadata"] = metadata

    @builtins.property
    def api_version(self) -> builtins.str:
        '''API version.'''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kind(self) -> builtins.str:
        '''Resource kind.'''
        result = self._values.get("kind")
        assert result is not None, "Required property 'kind' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def metadata(self) -> typing.Optional[ApiObjectMetadata]:
        '''Object metadata.

        If ``name`` is not specified, an app-unique name will be allocated by the
        framework based on the path of the construct within thes construct tree.
        '''
        result = self._values.get("metadata")
        return typing.cast(typing.Optional[ApiObjectMetadata], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiObjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class App(constructs.Construct, metaclass=jsii.JSIIMeta, jsii_type="cdk8s.App"):
    '''Represents a cdk8s application.'''

    def __init__(
        self,
        *,
        outdir: typing.Optional[builtins.str] = None,
        yaml_output_type: typing.Optional["YamlOutputType"] = None,
    ) -> None:
        '''Defines an app.

        :param outdir: The directory to output Kubernetes manifests. Default: - CDK8S_OUTDIR if defined, otherwise "dist"
        :param yaml_output_type: How to divide the YAML output into files. Default: YamlOutputType.FILE_PER_CHART
        '''
        props = AppProps(outdir=outdir, yaml_output_type=yaml_output_type)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="synth")
    def synth(self) -> None:
        '''Synthesizes all manifests to the output directory.'''
        return typing.cast(None, jsii.invoke(self, "synth", []))

    @jsii.member(jsii_name="synthYaml")
    def synth_yaml(self) -> typing.Any:
        '''Synthesizes the app into a YAML string.

        :return: A string with all YAML objects across all charts in this app.
        '''
        return typing.cast(typing.Any, jsii.invoke(self, "synthYaml", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="charts")
    def charts(self) -> typing.List["Chart"]:
        '''Returns all the charts in this app, sorted topologically.'''
        return typing.cast(typing.List["Chart"], jsii.get(self, "charts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outdir")
    def outdir(self) -> builtins.str:
        '''The output directory into which manifests will be synthesized.'''
        return typing.cast(builtins.str, jsii.get(self, "outdir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="yamlOutputType")
    def yaml_output_type(self) -> "YamlOutputType":
        '''How to divide the YAML output into files.

        :default: YamlOutputType.FILE_PER_CHART
        '''
        return typing.cast("YamlOutputType", jsii.get(self, "yamlOutputType"))


@jsii.data_type(
    jsii_type="cdk8s.AppProps",
    jsii_struct_bases=[],
    name_mapping={"outdir": "outdir", "yaml_output_type": "yamlOutputType"},
)
class AppProps:
    def __init__(
        self,
        *,
        outdir: typing.Optional[builtins.str] = None,
        yaml_output_type: typing.Optional["YamlOutputType"] = None,
    ) -> None:
        '''
        :param outdir: The directory to output Kubernetes manifests. Default: - CDK8S_OUTDIR if defined, otherwise "dist"
        :param yaml_output_type: How to divide the YAML output into files. Default: YamlOutputType.FILE_PER_CHART
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if outdir is not None:
            self._values["outdir"] = outdir
        if yaml_output_type is not None:
            self._values["yaml_output_type"] = yaml_output_type

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''The directory to output Kubernetes manifests.

        :default: - CDK8S_OUTDIR if defined, otherwise "dist"
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def yaml_output_type(self) -> typing.Optional["YamlOutputType"]:
        '''How to divide the YAML output into files.

        :default: YamlOutputType.FILE_PER_CHART
        '''
        result = self._values.get("yaml_output_type")
        return typing.cast(typing.Optional["YamlOutputType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AppProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Chart(constructs.Construct, metaclass=jsii.JSIIMeta, jsii_type="cdk8s.Chart"):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param labels: Labels to apply to all resources in this chart. Default: - no common labels
        :param namespace: The default namespace for all objects defined in this chart (directly or indirectly). This namespace will only apply to objects that don't have a ``namespace`` explicitly defined for them. Default: - no namespace is synthesized (usually this implies "default")
        '''
        props = ChartProps(labels=labels, namespace=namespace)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, c: constructs.IConstruct) -> "Chart":
        '''Finds the chart in which a node is defined.

        :param c: a construct node.
        '''
        return typing.cast("Chart", jsii.sinvoke(cls, "of", [c]))

    @jsii.member(jsii_name="addDependency")
    def add_dependency(self, *dependencies: constructs.IConstruct) -> None:
        '''Create a dependency between this Chart and other constructs.

        These can be other ApiObjects, Charts, or custom.

        :param dependencies: the dependencies to add.
        '''
        return typing.cast(None, jsii.invoke(self, "addDependency", [*dependencies]))

    @jsii.member(jsii_name="generateObjectName")
    def generate_object_name(self, api_object: ApiObject) -> builtins.str:
        '''Generates a app-unique name for an object given it's construct node path.

        Different resource types may have different constraints on names
        (``metadata.name``). The previous version of the name generator was
        compatible with DNS_SUBDOMAIN but not with DNS_LABEL.

        For example, ``Deployment`` names must comply with DNS_SUBDOMAIN while
        ``Service`` names must comply with DNS_LABEL.

        Since there is no formal specification for this, the default name
        generation scheme for kubernetes objects in cdk8s was changed to DNS_LABEL,
        since it’s the common denominator for all kubernetes resources
        (supposedly).

        You can override this method if you wish to customize object names at the
        chart level.

        :param api_object: The API object to generate a name for.
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "generateObjectName", [api_object]))

    @jsii.member(jsii_name="toJson")
    def to_json(self) -> typing.List[typing.Any]:
        '''Renders this chart to a set of Kubernetes JSON resources.

        :return: array of resource manifests
        '''
        return typing.cast(typing.List[typing.Any], jsii.invoke(self, "toJson", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Labels applied to all resources in this chart.

        This is an immutable copy.
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The default namespace for all objects in this chart.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespace"))


@jsii.data_type(
    jsii_type="cdk8s.ChartProps",
    jsii_struct_bases=[],
    name_mapping={"labels": "labels", "namespace": "namespace"},
)
class ChartProps:
    def __init__(
        self,
        *,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param labels: Labels to apply to all resources in this chart. Default: - no common labels
        :param namespace: The default namespace for all objects defined in this chart (directly or indirectly). This namespace will only apply to objects that don't have a ``namespace`` explicitly defined for them. Default: - no namespace is synthesized (usually this implies "default")
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if labels is not None:
            self._values["labels"] = labels
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Labels to apply to all resources in this chart.

        :default: - no common labels
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The default namespace for all objects defined in this chart (directly or indirectly).

        This namespace will only apply to objects that don't have a
        ``namespace`` explicitly defined for them.

        :default: - no namespace is synthesized (usually this implies "default")
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ChartProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DependencyGraph(metaclass=jsii.JSIIMeta, jsii_type="cdk8s.DependencyGraph"):
    '''Represents the dependency graph for a given Node.

    This graph includes the dependency relationships between all nodes in the
    node (construct) sub-tree who's root is this Node.

    Note that this means that lonely nodes (no dependencies and no dependants) are also included in this graph as
    childless children of the root node of the graph.

    The graph does not include cross-scope dependencies. That is, if a child on the current scope depends on a node
    from a different scope, that relationship is not represented in this graph.
    '''

    def __init__(self, node: constructs.Node) -> None:
        '''
        :param node: -
        '''
        jsii.create(self.__class__, self, [node])

    @jsii.member(jsii_name="topology")
    def topology(self) -> typing.List[constructs.IConstruct]:
        '''
        :see: Vertex.topology()
        '''
        return typing.cast(typing.List[constructs.IConstruct], jsii.invoke(self, "topology", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="root")
    def root(self) -> "DependencyVertex":
        '''Returns the root of the graph.

        Note that this vertex will always have ``null`` as its ``.value`` since it is an artifical root
        that binds all the connected spaces of the graph.
        '''
        return typing.cast("DependencyVertex", jsii.get(self, "root"))


class DependencyVertex(metaclass=jsii.JSIIMeta, jsii_type="cdk8s.DependencyVertex"):
    '''Represents a vertex in the graph.

    The value of each vertex is an ``IConstruct`` that is accessible via the ``.value`` getter.
    '''

    def __init__(self, value: typing.Optional[constructs.IConstruct] = None) -> None:
        '''
        :param value: -
        '''
        jsii.create(self.__class__, self, [value])

    @jsii.member(jsii_name="addChild")
    def add_child(self, dep: "DependencyVertex") -> None:
        '''Adds a vertex as a dependency of the current node.

        Also updates the parents of ``dep``, so that it contains this node as a parent.

        This operation will fail in case it creates a cycle in the graph.

        :param dep: The dependency.
        '''
        return typing.cast(None, jsii.invoke(self, "addChild", [dep]))

    @jsii.member(jsii_name="topology")
    def topology(self) -> typing.List[constructs.IConstruct]:
        '''Returns a topologically sorted array of the constructs in the sub-graph.'''
        return typing.cast(typing.List[constructs.IConstruct], jsii.invoke(self, "topology", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inbound")
    def inbound(self) -> typing.List["DependencyVertex"]:
        '''Returns the parents of the vertex (i.e dependants).'''
        return typing.cast(typing.List["DependencyVertex"], jsii.get(self, "inbound"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outbound")
    def outbound(self) -> typing.List["DependencyVertex"]:
        '''Returns the children of the vertex (i.e dependencies).'''
        return typing.cast(typing.List["DependencyVertex"], jsii.get(self, "outbound"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> typing.Optional[constructs.IConstruct]:
        '''Returns the IConstruct this graph vertex represents.

        ``null`` in case this is the root of the graph.
        '''
        return typing.cast(typing.Optional[constructs.IConstruct], jsii.get(self, "value"))


class Duration(metaclass=jsii.JSIIMeta, jsii_type="cdk8s.Duration"):
    '''Represents a length of time.

    The amount can be specified either as a literal value (e.g: ``10``) which
    cannot be negative.
    '''

    @jsii.member(jsii_name="days") # type: ignore[misc]
    @builtins.classmethod
    def days(cls, amount: jsii.Number) -> "Duration":
        '''Create a Duration representing an amount of days.

        :param amount: the amount of Days the ``Duration`` will represent.

        :return: a new ``Duration`` representing ``amount`` Days.
        '''
        return typing.cast("Duration", jsii.sinvoke(cls, "days", [amount]))

    @jsii.member(jsii_name="hours") # type: ignore[misc]
    @builtins.classmethod
    def hours(cls, amount: jsii.Number) -> "Duration":
        '''Create a Duration representing an amount of hours.

        :param amount: the amount of Hours the ``Duration`` will represent.

        :return: a new ``Duration`` representing ``amount`` Hours.
        '''
        return typing.cast("Duration", jsii.sinvoke(cls, "hours", [amount]))

    @jsii.member(jsii_name="millis") # type: ignore[misc]
    @builtins.classmethod
    def millis(cls, amount: jsii.Number) -> "Duration":
        '''Create a Duration representing an amount of milliseconds.

        :param amount: the amount of Milliseconds the ``Duration`` will represent.

        :return: a new ``Duration`` representing ``amount`` ms.
        '''
        return typing.cast("Duration", jsii.sinvoke(cls, "millis", [amount]))

    @jsii.member(jsii_name="minutes") # type: ignore[misc]
    @builtins.classmethod
    def minutes(cls, amount: jsii.Number) -> "Duration":
        '''Create a Duration representing an amount of minutes.

        :param amount: the amount of Minutes the ``Duration`` will represent.

        :return: a new ``Duration`` representing ``amount`` Minutes.
        '''
        return typing.cast("Duration", jsii.sinvoke(cls, "minutes", [amount]))

    @jsii.member(jsii_name="parse") # type: ignore[misc]
    @builtins.classmethod
    def parse(cls, duration: builtins.str) -> "Duration":
        '''Parse a period formatted according to the ISO 8601 standard.

        :param duration: an ISO-formtted duration to be parsed.

        :return: the parsed ``Duration``.

        :see: https://www.iso.org/fr/standard/70907.html
        '''
        return typing.cast("Duration", jsii.sinvoke(cls, "parse", [duration]))

    @jsii.member(jsii_name="seconds") # type: ignore[misc]
    @builtins.classmethod
    def seconds(cls, amount: jsii.Number) -> "Duration":
        '''Create a Duration representing an amount of seconds.

        :param amount: the amount of Seconds the ``Duration`` will represent.

        :return: a new ``Duration`` representing ``amount`` Seconds.
        '''
        return typing.cast("Duration", jsii.sinvoke(cls, "seconds", [amount]))

    @jsii.member(jsii_name="toDays")
    def to_days(
        self,
        *,
        integral: typing.Optional[builtins.bool] = None,
    ) -> jsii.Number:
        '''Return the total number of days in this Duration.

        :param integral: If ``true``, conversions into a larger time unit (e.g. ``Seconds`` to ``Minutes``) will fail if the result is not an integer. Default: true

        :return: the value of this ``Duration`` expressed in Days.
        '''
        opts = TimeConversionOptions(integral=integral)

        return typing.cast(jsii.Number, jsii.invoke(self, "toDays", [opts]))

    @jsii.member(jsii_name="toHours")
    def to_hours(
        self,
        *,
        integral: typing.Optional[builtins.bool] = None,
    ) -> jsii.Number:
        '''Return the total number of hours in this Duration.

        :param integral: If ``true``, conversions into a larger time unit (e.g. ``Seconds`` to ``Minutes``) will fail if the result is not an integer. Default: true

        :return: the value of this ``Duration`` expressed in Hours.
        '''
        opts = TimeConversionOptions(integral=integral)

        return typing.cast(jsii.Number, jsii.invoke(self, "toHours", [opts]))

    @jsii.member(jsii_name="toHumanString")
    def to_human_string(self) -> builtins.str:
        '''Turn this duration into a human-readable string.'''
        return typing.cast(builtins.str, jsii.invoke(self, "toHumanString", []))

    @jsii.member(jsii_name="toIsoString")
    def to_iso_string(self) -> builtins.str:
        '''Return an ISO 8601 representation of this period.

        :return: a string starting with 'PT' describing the period

        :see: https://www.iso.org/fr/standard/70907.html
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "toIsoString", []))

    @jsii.member(jsii_name="toMilliseconds")
    def to_milliseconds(
        self,
        *,
        integral: typing.Optional[builtins.bool] = None,
    ) -> jsii.Number:
        '''Return the total number of milliseconds in this Duration.

        :param integral: If ``true``, conversions into a larger time unit (e.g. ``Seconds`` to ``Minutes``) will fail if the result is not an integer. Default: true

        :return: the value of this ``Duration`` expressed in Milliseconds.
        '''
        opts = TimeConversionOptions(integral=integral)

        return typing.cast(jsii.Number, jsii.invoke(self, "toMilliseconds", [opts]))

    @jsii.member(jsii_name="toMinutes")
    def to_minutes(
        self,
        *,
        integral: typing.Optional[builtins.bool] = None,
    ) -> jsii.Number:
        '''Return the total number of minutes in this Duration.

        :param integral: If ``true``, conversions into a larger time unit (e.g. ``Seconds`` to ``Minutes``) will fail if the result is not an integer. Default: true

        :return: the value of this ``Duration`` expressed in Minutes.
        '''
        opts = TimeConversionOptions(integral=integral)

        return typing.cast(jsii.Number, jsii.invoke(self, "toMinutes", [opts]))

    @jsii.member(jsii_name="toSeconds")
    def to_seconds(
        self,
        *,
        integral: typing.Optional[builtins.bool] = None,
    ) -> jsii.Number:
        '''Return the total number of seconds in this Duration.

        :param integral: If ``true``, conversions into a larger time unit (e.g. ``Seconds`` to ``Minutes``) will fail if the result is not an integer. Default: true

        :return: the value of this ``Duration`` expressed in Seconds.
        '''
        opts = TimeConversionOptions(integral=integral)

        return typing.cast(jsii.Number, jsii.invoke(self, "toSeconds", [opts]))


@jsii.data_type(
    jsii_type="cdk8s.GroupVersionKind",
    jsii_struct_bases=[],
    name_mapping={"api_version": "apiVersion", "kind": "kind"},
)
class GroupVersionKind:
    def __init__(self, *, api_version: builtins.str, kind: builtins.str) -> None:
        '''
        :param api_version: The object's API version (e.g. ``authorization.k8s.io/v1``).
        :param kind: The object kind.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_version": api_version,
            "kind": kind,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''The object's API version (e.g. ``authorization.k8s.io/v1``).'''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kind(self) -> builtins.str:
        '''The object kind.'''
        result = self._values.get("kind")
        assert result is not None, "Required property 'kind' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GroupVersionKind(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s.HelmProps",
    jsii_struct_bases=[],
    name_mapping={
        "chart": "chart",
        "helm_executable": "helmExecutable",
        "helm_flags": "helmFlags",
        "release_name": "releaseName",
        "values": "values",
    },
)
class HelmProps:
    def __init__(
        self,
        *,
        chart: builtins.str,
        helm_executable: typing.Optional[builtins.str] = None,
        helm_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        release_name: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''Options for ``Helm``.

        :param chart: The chart name to use. It can be a chart from a helm repository or a local directory. This name is passed to ``helm template`` and has all the relevant semantics.
        :param helm_executable: The local helm executable to use in order to create the manifest the chart. Default: "helm"
        :param helm_flags: Additional flags to add to the ``helm`` execution. Default: []
        :param release_name: The release name. Default: - if unspecified, a name will be allocated based on the construct path
        :param values: Values to pass to the chart. Default: - If no values are specified, chart will use the defaults.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "chart": chart,
        }
        if helm_executable is not None:
            self._values["helm_executable"] = helm_executable
        if helm_flags is not None:
            self._values["helm_flags"] = helm_flags
        if release_name is not None:
            self._values["release_name"] = release_name
        if values is not None:
            self._values["values"] = values

    @builtins.property
    def chart(self) -> builtins.str:
        '''The chart name to use. It can be a chart from a helm repository or a local directory.

        This name is passed to ``helm template`` and has all the relevant semantics.

        Example::

            "bitnami/redis"
        '''
        result = self._values.get("chart")
        assert result is not None, "Required property 'chart' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def helm_executable(self) -> typing.Optional[builtins.str]:
        '''The local helm executable to use in order to create the manifest the chart.

        :default: "helm"
        '''
        result = self._values.get("helm_executable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def helm_flags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional flags to add to the ``helm`` execution.

        :default: []
        '''
        result = self._values.get("helm_flags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def release_name(self) -> typing.Optional[builtins.str]:
        '''The release name.

        :default: - if unspecified, a name will be allocated based on the construct path

        :see: https://helm.sh/docs/intro/using_helm/#three-big-concepts
        '''
        result = self._values.get("release_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def values(self) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        '''Values to pass to the chart.

        :default: - If no values are specified, chart will use the defaults.
        '''
        result = self._values.get("values")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Any]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HelmProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cdk8s.IAnyProducer")
class IAnyProducer(typing_extensions.Protocol):
    @jsii.member(jsii_name="produce")
    def produce(self) -> typing.Any:
        ...


class _IAnyProducerProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk8s.IAnyProducer"

    @jsii.member(jsii_name="produce")
    def produce(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.invoke(self, "produce", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAnyProducer).__jsii_proxy_class__ = lambda : _IAnyProducerProxy


class Include(constructs.Construct, metaclass=jsii.JSIIMeta, jsii_type="cdk8s.Include"):
    '''Reads a YAML manifest from a file or a URL and defines all resources as API objects within the defined scope.

    The names (``metadata.name``) of imported resources will be preserved as-is
    from the manifest.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        url: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param url: Local file path or URL which includes a Kubernetes YAML manifest.
        '''
        props = IncludeProps(url=url)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiObjects")
    def api_objects(self) -> typing.List[ApiObject]:
        '''Returns all the included API objects.'''
        return typing.cast(typing.List[ApiObject], jsii.get(self, "apiObjects"))


@jsii.data_type(
    jsii_type="cdk8s.IncludeProps",
    jsii_struct_bases=[],
    name_mapping={"url": "url"},
)
class IncludeProps:
    def __init__(self, *, url: builtins.str) -> None:
        '''
        :param url: Local file path or URL which includes a Kubernetes YAML manifest.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }

    @builtins.property
    def url(self) -> builtins.str:
        '''Local file path or URL which includes a Kubernetes YAML manifest.

        Example::

            mymanifest.yaml
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IncludeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class JsonPatch(metaclass=jsii.JSIIMeta, jsii_type="cdk8s.JsonPatch"):
    '''Utility for applying RFC-6902 JSON-Patch to a document.

    Use the the ``JsonPatch.apply(doc, ...ops)`` function to apply a set of
    operations to a JSON document and return the result.

    Operations can be created using the factory methods ``JsonPatch.add()``,
    ``JsonPatch.remove()``, etc.

    Example::

        const output = JsonPatch.apply(input,
         JsonPatch.replace('/world/hi/there', 'goodbye'),
         JsonPatch.add('/world/foo/', 'boom'),
         JsonPatch.remove('/hello'));
    '''

    @jsii.member(jsii_name="add") # type: ignore[misc]
    @builtins.classmethod
    def add(cls, path: builtins.str, value: typing.Any) -> "JsonPatch":
        '''Adds a value to an object or inserts it into an array.

        In the case of an
        array, the value is inserted before the given index. The - character can be
        used instead of an index to insert at the end of an array.

        :param path: -
        :param value: -

        Example::

            JsonPatch.add('/biscuits/1', { "name": "Ginger Nut" })
        '''
        return typing.cast("JsonPatch", jsii.sinvoke(cls, "add", [path, value]))

    @jsii.member(jsii_name="apply") # type: ignore[misc]
    @builtins.classmethod
    def apply(cls, document: typing.Any, *ops: "JsonPatch") -> typing.Any:
        '''Applies a set of JSON-Patch (RFC-6902) operations to ``document`` and returns the result.

        :param document: The document to patch.
        :param ops: The operations to apply.

        :return: The result document
        '''
        return typing.cast(typing.Any, jsii.sinvoke(cls, "apply", [document, *ops]))

    @jsii.member(jsii_name="copy") # type: ignore[misc]
    @builtins.classmethod
    def copy(cls, from_: builtins.str, path: builtins.str) -> "JsonPatch":
        '''Copies a value from one location to another within the JSON document.

        Both
        from and path are JSON Pointers.

        :param from_: -
        :param path: -

        Example::

            JsonPatch.copy('/biscuits/0', '/best_biscuit')
        '''
        return typing.cast("JsonPatch", jsii.sinvoke(cls, "copy", [from_, path]))

    @jsii.member(jsii_name="move") # type: ignore[misc]
    @builtins.classmethod
    def move(cls, from_: builtins.str, path: builtins.str) -> "JsonPatch":
        '''Moves a value from one location to the other.

        Both from and path are JSON Pointers.

        :param from_: -
        :param path: -

        Example::

            JsonPatch.move('/biscuits', '/cookies')
        '''
        return typing.cast("JsonPatch", jsii.sinvoke(cls, "move", [from_, path]))

    @jsii.member(jsii_name="remove") # type: ignore[misc]
    @builtins.classmethod
    def remove(cls, path: builtins.str) -> "JsonPatch":
        '''Removes a value from an object or array.

        :param path: -

        Example::

            JsonPatch.remove('/biscuits/0')
        '''
        return typing.cast("JsonPatch", jsii.sinvoke(cls, "remove", [path]))

    @jsii.member(jsii_name="replace") # type: ignore[misc]
    @builtins.classmethod
    def replace(cls, path: builtins.str, value: typing.Any) -> "JsonPatch":
        '''Replaces a value.

        Equivalent to a “remove” followed by an “add”.

        :param path: -
        :param value: -

        Example::

            JsonPatch.replace('/biscuits/0/name', 'Chocolate Digestive')
        '''
        return typing.cast("JsonPatch", jsii.sinvoke(cls, "replace", [path, value]))

    @jsii.member(jsii_name="test") # type: ignore[misc]
    @builtins.classmethod
    def test(cls, path: builtins.str, value: typing.Any) -> "JsonPatch":
        '''Tests that the specified value is set in the document.

        If the test fails,
        then the patch as a whole should not apply.

        :param path: -
        :param value: -

        Example::

            JsonPatch.test('/best_biscuit/name', 'Choco Leibniz')
        '''
        return typing.cast("JsonPatch", jsii.sinvoke(cls, "test", [path, value]))


class Lazy(metaclass=jsii.JSIIMeta, jsii_type="cdk8s.Lazy"):
    @jsii.member(jsii_name="any") # type: ignore[misc]
    @builtins.classmethod
    def any(cls, producer: IAnyProducer) -> typing.Any:
        '''
        :param producer: -
        '''
        return typing.cast(typing.Any, jsii.sinvoke(cls, "any", [producer]))

    @jsii.member(jsii_name="produce")
    def produce(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.invoke(self, "produce", []))


@jsii.data_type(
    jsii_type="cdk8s.NameOptions",
    jsii_struct_bases=[],
    name_mapping={
        "delimiter": "delimiter",
        "extra": "extra",
        "include_hash": "includeHash",
        "max_len": "maxLen",
    },
)
class NameOptions:
    def __init__(
        self,
        *,
        delimiter: typing.Optional[builtins.str] = None,
        extra: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_hash: typing.Optional[builtins.bool] = None,
        max_len: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''Options for name generation.

        :param delimiter: Delimiter to use between components. Default: "-"
        :param extra: Extra components to include in the name. Default: [] use the construct path components
        :param include_hash: Include a short hash as last part of the name. Default: true
        :param max_len: Maximum allowed length for the name. Default: 63
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delimiter is not None:
            self._values["delimiter"] = delimiter
        if extra is not None:
            self._values["extra"] = extra
        if include_hash is not None:
            self._values["include_hash"] = include_hash
        if max_len is not None:
            self._values["max_len"] = max_len

    @builtins.property
    def delimiter(self) -> typing.Optional[builtins.str]:
        '''Delimiter to use between components.

        :default: "-"
        '''
        result = self._values.get("delimiter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extra(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Extra components to include in the name.

        :default: [] use the construct path components
        '''
        result = self._values.get("extra")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def include_hash(self) -> typing.Optional[builtins.bool]:
        '''Include a short hash as last part of the name.

        :default: true
        '''
        result = self._values.get("include_hash")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_len(self) -> typing.Optional[jsii.Number]:
        '''Maximum allowed length for the name.

        :default: 63
        '''
        result = self._values.get("max_len")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NameOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Names(metaclass=jsii.JSIIMeta, jsii_type="cdk8s.Names"):
    '''Utilities for generating unique and stable names.'''

    @jsii.member(jsii_name="toDnsLabel") # type: ignore[misc]
    @builtins.classmethod
    def to_dns_label(
        cls,
        scope: constructs.Construct,
        *,
        delimiter: typing.Optional[builtins.str] = None,
        extra: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_hash: typing.Optional[builtins.bool] = None,
        max_len: typing.Optional[jsii.Number] = None,
    ) -> builtins.str:
        '''Generates a unique and stable name compatible DNS_LABEL from RFC-1123 from a path.

        The generated name will:

        - contain at most 63 characters
        - contain only lowercase alphanumeric characters or ‘-’
        - start with an alphanumeric character
        - end with an alphanumeric character

        The generated name will have the form:
        --..--

        Where  are the path components (assuming they are is separated by
        "/").

        Note that if the total length is longer than 63 characters, we will trim
        the first components since the last components usually encode more meaning.

        :param scope: The construct for which to render the DNS label.
        :param delimiter: Delimiter to use between components. Default: "-"
        :param extra: Extra components to include in the name. Default: [] use the construct path components
        :param include_hash: Include a short hash as last part of the name. Default: true
        :param max_len: Maximum allowed length for the name. Default: 63

        :link: https://tools.ietf.org/html/rfc1123
        :throws:

        if any of the components do not adhere to naming constraints or
        length.
        '''
        options = NameOptions(
            delimiter=delimiter,
            extra=extra,
            include_hash=include_hash,
            max_len=max_len,
        )

        return typing.cast(builtins.str, jsii.sinvoke(cls, "toDnsLabel", [scope, options]))

    @jsii.member(jsii_name="toLabelValue") # type: ignore[misc]
    @builtins.classmethod
    def to_label_value(
        cls,
        scope: constructs.Construct,
        *,
        delimiter: typing.Optional[builtins.str] = None,
        extra: typing.Optional[typing.Sequence[builtins.str]] = None,
        include_hash: typing.Optional[builtins.bool] = None,
        max_len: typing.Optional[jsii.Number] = None,
    ) -> builtins.str:
        '''Generates a unique and stable name compatible label key name segment and label value from a path.

        The name segment is required and must be 63 characters or less, beginning
        and ending with an alphanumeric character ([a-z0-9A-Z]) with dashes (-),
        underscores (_), dots (.), and alphanumerics between.

        Valid label values must be 63 characters or less and must be empty or
        begin and end with an alphanumeric character ([a-z0-9A-Z]) with dashes
        (-), underscores (_), dots (.), and alphanumerics between.

        The generated name will have the form:
        ..

        Where  are the path components (assuming they are is separated by
        "/").

        Note that if the total length is longer than 63 characters, we will trim
        the first components since the last components usually encode more meaning.

        :param scope: The construct for which to render the DNS label.
        :param delimiter: Delimiter to use between components. Default: "-"
        :param extra: Extra components to include in the name. Default: [] use the construct path components
        :param include_hash: Include a short hash as last part of the name. Default: true
        :param max_len: Maximum allowed length for the name. Default: 63

        :link: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#syntax-and-character-set
        :throws:

        if any of the components do not adhere to naming constraints or
        length.
        '''
        options = NameOptions(
            delimiter=delimiter,
            extra=extra,
            include_hash=include_hash,
            max_len=max_len,
        )

        return typing.cast(builtins.str, jsii.sinvoke(cls, "toLabelValue", [scope, options]))


@jsii.data_type(
    jsii_type="cdk8s.OwnerReference",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "kind": "kind",
        "name": "name",
        "uid": "uid",
        "block_owner_deletion": "blockOwnerDeletion",
        "controller": "controller",
    },
)
class OwnerReference:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        kind: builtins.str,
        name: builtins.str,
        uid: builtins.str,
        block_owner_deletion: typing.Optional[builtins.bool] = None,
        controller: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''OwnerReference contains enough information to let you identify an owning object.

        An owning object must be in the same namespace as the dependent, or
        be cluster-scoped, so there is no namespace field.

        :param api_version: API version of the referent.
        :param kind: Kind of the referent.
        :param name: Name of the referent.
        :param uid: UID of the referent.
        :param block_owner_deletion: If true, AND if the owner has the "foregroundDeletion" finalizer, then the owner cannot be deleted from the key-value store until this reference is removed. Defaults to false. To set this field, a user needs "delete" permission of the owner, otherwise 422 (Unprocessable Entity) will be returned. Default: false. To set this field, a user needs "delete" permission of the owner, otherwise 422 (Unprocessable Entity) will be returned.
        :param controller: If true, this reference points to the managing controller.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api_version": api_version,
            "kind": kind,
            "name": name,
            "uid": uid,
        }
        if block_owner_deletion is not None:
            self._values["block_owner_deletion"] = block_owner_deletion
        if controller is not None:
            self._values["controller"] = controller

    @builtins.property
    def api_version(self) -> builtins.str:
        '''API version of the referent.'''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kind(self) -> builtins.str:
        '''Kind of the referent.

        :see: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        '''
        result = self._values.get("kind")
        assert result is not None, "Required property 'kind' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the referent.

        :see: http://kubernetes.io/docs/user-guide/identifiers#names
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uid(self) -> builtins.str:
        '''UID of the referent.

        :see: http://kubernetes.io/docs/user-guide/identifiers#uids
        '''
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def block_owner_deletion(self) -> typing.Optional[builtins.bool]:
        '''If true, AND if the owner has the "foregroundDeletion" finalizer, then the owner cannot be deleted from the key-value store until this reference is removed.

        Defaults to false. To set this field, a user needs "delete"
        permission of the owner, otherwise 422 (Unprocessable Entity) will be
        returned.

        :default:

        false. To set this field, a user needs "delete" permission of the
        owner, otherwise 422 (Unprocessable Entity) will be returned.
        '''
        result = self._values.get("block_owner_deletion")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def controller(self) -> typing.Optional[builtins.bool]:
        '''If true, this reference points to the managing controller.'''
        result = self._values.get("controller")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OwnerReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Size(metaclass=jsii.JSIIMeta, jsii_type="cdk8s.Size"):
    '''Represents the amount of digital storage.

    The amount can be specified either as a literal value (e.g: ``10``) which
    cannot be negative.

    When the amount is passed as a token, unit conversion is not possible.
    '''

    @jsii.member(jsii_name="gibibytes") # type: ignore[misc]
    @builtins.classmethod
    def gibibytes(cls, amount: jsii.Number) -> "Size":
        '''Create a Storage representing an amount gibibytes.

        1 GiB = 1024 MiB

        :param amount: -
        '''
        return typing.cast("Size", jsii.sinvoke(cls, "gibibytes", [amount]))

    @jsii.member(jsii_name="kibibytes") # type: ignore[misc]
    @builtins.classmethod
    def kibibytes(cls, amount: jsii.Number) -> "Size":
        '''Create a Storage representing an amount kibibytes.

        1 KiB = 1024 bytes

        :param amount: -
        '''
        return typing.cast("Size", jsii.sinvoke(cls, "kibibytes", [amount]))

    @jsii.member(jsii_name="mebibytes") # type: ignore[misc]
    @builtins.classmethod
    def mebibytes(cls, amount: jsii.Number) -> "Size":
        '''Create a Storage representing an amount mebibytes.

        1 MiB = 1024 KiB

        :param amount: -
        '''
        return typing.cast("Size", jsii.sinvoke(cls, "mebibytes", [amount]))

    @jsii.member(jsii_name="pebibyte") # type: ignore[misc]
    @builtins.classmethod
    def pebibyte(cls, amount: jsii.Number) -> "Size":
        '''Create a Storage representing an amount pebibytes.

        1 PiB = 1024 TiB

        :param amount: -
        '''
        return typing.cast("Size", jsii.sinvoke(cls, "pebibyte", [amount]))

    @jsii.member(jsii_name="tebibytes") # type: ignore[misc]
    @builtins.classmethod
    def tebibytes(cls, amount: jsii.Number) -> "Size":
        '''Create a Storage representing an amount tebibytes.

        1 TiB = 1024 GiB

        :param amount: -
        '''
        return typing.cast("Size", jsii.sinvoke(cls, "tebibytes", [amount]))

    @jsii.member(jsii_name="toGibibytes")
    def to_gibibytes(
        self,
        *,
        rounding: typing.Optional["SizeRoundingBehavior"] = None,
    ) -> jsii.Number:
        '''Return this storage as a total number of gibibytes.

        :param rounding: How conversions should behave when it encounters a non-integer result. Default: SizeRoundingBehavior.FAIL
        '''
        opts = SizeConversionOptions(rounding=rounding)

        return typing.cast(jsii.Number, jsii.invoke(self, "toGibibytes", [opts]))

    @jsii.member(jsii_name="toKibibytes")
    def to_kibibytes(
        self,
        *,
        rounding: typing.Optional["SizeRoundingBehavior"] = None,
    ) -> jsii.Number:
        '''Return this storage as a total number of kibibytes.

        :param rounding: How conversions should behave when it encounters a non-integer result. Default: SizeRoundingBehavior.FAIL
        '''
        opts = SizeConversionOptions(rounding=rounding)

        return typing.cast(jsii.Number, jsii.invoke(self, "toKibibytes", [opts]))

    @jsii.member(jsii_name="toMebibytes")
    def to_mebibytes(
        self,
        *,
        rounding: typing.Optional["SizeRoundingBehavior"] = None,
    ) -> jsii.Number:
        '''Return this storage as a total number of mebibytes.

        :param rounding: How conversions should behave when it encounters a non-integer result. Default: SizeRoundingBehavior.FAIL
        '''
        opts = SizeConversionOptions(rounding=rounding)

        return typing.cast(jsii.Number, jsii.invoke(self, "toMebibytes", [opts]))

    @jsii.member(jsii_name="toPebibytes")
    def to_pebibytes(
        self,
        *,
        rounding: typing.Optional["SizeRoundingBehavior"] = None,
    ) -> jsii.Number:
        '''Return this storage as a total number of pebibytes.

        :param rounding: How conversions should behave when it encounters a non-integer result. Default: SizeRoundingBehavior.FAIL
        '''
        opts = SizeConversionOptions(rounding=rounding)

        return typing.cast(jsii.Number, jsii.invoke(self, "toPebibytes", [opts]))

    @jsii.member(jsii_name="toTebibytes")
    def to_tebibytes(
        self,
        *,
        rounding: typing.Optional["SizeRoundingBehavior"] = None,
    ) -> jsii.Number:
        '''Return this storage as a total number of tebibytes.

        :param rounding: How conversions should behave when it encounters a non-integer result. Default: SizeRoundingBehavior.FAIL
        '''
        opts = SizeConversionOptions(rounding=rounding)

        return typing.cast(jsii.Number, jsii.invoke(self, "toTebibytes", [opts]))


@jsii.data_type(
    jsii_type="cdk8s.SizeConversionOptions",
    jsii_struct_bases=[],
    name_mapping={"rounding": "rounding"},
)
class SizeConversionOptions:
    def __init__(
        self,
        *,
        rounding: typing.Optional["SizeRoundingBehavior"] = None,
    ) -> None:
        '''Options for how to convert time to a different unit.

        :param rounding: How conversions should behave when it encounters a non-integer result. Default: SizeRoundingBehavior.FAIL
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if rounding is not None:
            self._values["rounding"] = rounding

    @builtins.property
    def rounding(self) -> typing.Optional["SizeRoundingBehavior"]:
        '''How conversions should behave when it encounters a non-integer result.

        :default: SizeRoundingBehavior.FAIL
        '''
        result = self._values.get("rounding")
        return typing.cast(typing.Optional["SizeRoundingBehavior"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SizeConversionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk8s.SizeRoundingBehavior")
class SizeRoundingBehavior(enum.Enum):
    '''Rounding behaviour when converting between units of ``Size``.'''

    FAIL = "FAIL"
    '''Fail the conversion if the result is not an integer.'''
    FLOOR = "FLOOR"
    '''If the result is not an integer, round it to the closest integer less than the result.'''
    NONE = "NONE"
    '''Don't round.

    Return even if the result is a fraction.
    '''


class Testing(metaclass=jsii.JSIIMeta, jsii_type="cdk8s.Testing"):
    '''Testing utilities for cdk8s applications.'''

    @jsii.member(jsii_name="app") # type: ignore[misc]
    @builtins.classmethod
    def app(
        cls,
        *,
        outdir: typing.Optional[builtins.str] = None,
        yaml_output_type: typing.Optional["YamlOutputType"] = None,
    ) -> App:
        '''Returns an app for testing with the following properties: - Output directory is a temp dir.

        :param outdir: The directory to output Kubernetes manifests. Default: - CDK8S_OUTDIR if defined, otherwise "dist"
        :param yaml_output_type: How to divide the YAML output into files. Default: YamlOutputType.FILE_PER_CHART
        '''
        props = AppProps(outdir=outdir, yaml_output_type=yaml_output_type)

        return typing.cast(App, jsii.sinvoke(cls, "app", [props]))

    @jsii.member(jsii_name="chart") # type: ignore[misc]
    @builtins.classmethod
    def chart(cls) -> Chart:
        '''
        :return: a Chart that can be used for tests
        '''
        return typing.cast(Chart, jsii.sinvoke(cls, "chart", []))

    @jsii.member(jsii_name="synth") # type: ignore[misc]
    @builtins.classmethod
    def synth(cls, chart: Chart) -> typing.List[typing.Any]:
        '''Returns the Kubernetes manifest synthesized from this chart.

        :param chart: -
        '''
        return typing.cast(typing.List[typing.Any], jsii.sinvoke(cls, "synth", [chart]))


@jsii.data_type(
    jsii_type="cdk8s.TimeConversionOptions",
    jsii_struct_bases=[],
    name_mapping={"integral": "integral"},
)
class TimeConversionOptions:
    def __init__(self, *, integral: typing.Optional[builtins.bool] = None) -> None:
        '''Options for how to convert time to a different unit.

        :param integral: If ``true``, conversions into a larger time unit (e.g. ``Seconds`` to ``Minutes``) will fail if the result is not an integer. Default: true
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if integral is not None:
            self._values["integral"] = integral

    @builtins.property
    def integral(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, conversions into a larger time unit (e.g. ``Seconds`` to ``Minutes``) will fail if the result is not an integer.

        :default: true
        '''
        result = self._values.get("integral")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TimeConversionOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Yaml(metaclass=jsii.JSIIMeta, jsii_type="cdk8s.Yaml"):
    '''YAML utilities.'''

    @jsii.member(jsii_name="formatObjects") # type: ignore[misc]
    @builtins.classmethod
    def format_objects(cls, docs: typing.Sequence[typing.Any]) -> builtins.str:
        '''
        :param docs: -

        :deprecated: use ``stringify(doc[, doc, ...])``

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.sinvoke(cls, "formatObjects", [docs]))

    @jsii.member(jsii_name="load") # type: ignore[misc]
    @builtins.classmethod
    def load(cls, url_or_file: builtins.str) -> typing.List[typing.Any]:
        '''Downloads a set of YAML documents (k8s manifest for example) from a URL or a file and returns them as javascript objects.

        Empty documents are filtered out.

        :param url_or_file: a URL of a file path to load from.

        :return: an array of objects, each represents a document inside the YAML
        '''
        return typing.cast(typing.List[typing.Any], jsii.sinvoke(cls, "load", [url_or_file]))

    @jsii.member(jsii_name="save") # type: ignore[misc]
    @builtins.classmethod
    def save(cls, file_path: builtins.str, docs: typing.Sequence[typing.Any]) -> None:
        '''Saves a set of objects as a multi-document YAML file.

        :param file_path: The output path.
        :param docs: The set of objects.
        '''
        return typing.cast(None, jsii.sinvoke(cls, "save", [file_path, docs]))

    @jsii.member(jsii_name="stringify") # type: ignore[misc]
    @builtins.classmethod
    def stringify(cls, *docs: typing.Any) -> builtins.str:
        '''Stringify a document (or multiple documents) into YAML.

        We convert undefined values to null, but ignore any documents that are
        undefined.

        :param docs: A set of objects to convert to YAML.

        :return: a YAML string. Multiple docs are separated by ``---``.
        '''
        return typing.cast(builtins.str, jsii.sinvoke(cls, "stringify", [*docs]))

    @jsii.member(jsii_name="tmp") # type: ignore[misc]
    @builtins.classmethod
    def tmp(cls, docs: typing.Sequence[typing.Any]) -> builtins.str:
        '''Saves a set of YAML documents into a temp file (in /tmp).

        :param docs: the set of documents to save.

        :return: the path to the temporary file
        '''
        return typing.cast(builtins.str, jsii.sinvoke(cls, "tmp", [docs]))


@jsii.enum(jsii_type="cdk8s.YamlOutputType")
class YamlOutputType(enum.Enum):
    '''The method to divide YAML output into files.'''

    FILE_PER_APP = "FILE_PER_APP"
    '''All resources are output into a single YAML file.'''
    FILE_PER_CHART = "FILE_PER_CHART"
    '''Resources are split into seperate files by chart.'''
    FILE_PER_RESOURCE = "FILE_PER_RESOURCE"
    '''Each resource is output to its own file.'''
    FOLDER_PER_CHART_FILE_PER_RESOURCE = "FOLDER_PER_CHART_FILE_PER_RESOURCE"
    '''Each chart in its own folder and each resource in its own file.'''


class Helm(Include, metaclass=jsii.JSIIMeta, jsii_type="cdk8s.Helm"):
    '''Represents a Helm deployment.

    Use this construct to import an existing Helm chart and incorporate it into your constructs.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        chart: builtins.str,
        helm_executable: typing.Optional[builtins.str] = None,
        helm_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
        release_name: typing.Optional[builtins.str] = None,
        values: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param chart: The chart name to use. It can be a chart from a helm repository or a local directory. This name is passed to ``helm template`` and has all the relevant semantics.
        :param helm_executable: The local helm executable to use in order to create the manifest the chart. Default: "helm"
        :param helm_flags: Additional flags to add to the ``helm`` execution. Default: []
        :param release_name: The release name. Default: - if unspecified, a name will be allocated based on the construct path
        :param values: Values to pass to the chart. Default: - If no values are specified, chart will use the defaults.
        '''
        props = HelmProps(
            chart=chart,
            helm_executable=helm_executable,
            helm_flags=helm_flags,
            release_name=release_name,
            values=values,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="releaseName")
    def release_name(self) -> builtins.str:
        '''The helm release name.'''
        return typing.cast(builtins.str, jsii.get(self, "releaseName"))


__all__ = [
    "ApiObject",
    "ApiObjectMetadata",
    "ApiObjectMetadataDefinition",
    "ApiObjectProps",
    "App",
    "AppProps",
    "Chart",
    "ChartProps",
    "DependencyGraph",
    "DependencyVertex",
    "Duration",
    "GroupVersionKind",
    "Helm",
    "HelmProps",
    "IAnyProducer",
    "Include",
    "IncludeProps",
    "JsonPatch",
    "Lazy",
    "NameOptions",
    "Names",
    "OwnerReference",
    "Size",
    "SizeConversionOptions",
    "SizeRoundingBehavior",
    "Testing",
    "TimeConversionOptions",
    "Yaml",
    "YamlOutputType",
]

publication.publish()
