'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-container-registry

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-container-registry)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-container-registry/)

> Registry for container images

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-container-registry
```

Python:

```bash
pip install cloudcomponents.cdk-container-registry
```

## How to use

```python
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { Topic } from '@aws-cdk/aws-sns';
import { EmailSubscription } from '@aws-cdk/aws-sns-subscriptions';
import {
  ImageRepository,
  Severity,
} from '@cloudcomponents/cdk-container-registry';

export class ImageRepositoryStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const alarmTopic = new Topic(this, 'Topic');

    alarmTopic.addSubscription(
      new EmailSubscription(process.env.DEVSECOPS_TEAM_EMAIL as string),
    );

    const imageRepository = new ImageRepository(this, 'ImageRepository', {
      forceDelete: true, //Only for tests
      imageScanOnPush: true,
    });

    imageRepository.onFinding('finding', {
      severity: Severity.HIGH,
      alarmTopic,
    });
  }
}
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-container-registry/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-container-registry/LICENSE)
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

import aws_cdk.aws_ecr
import aws_cdk.aws_events
import aws_cdk.aws_sns
import aws_cdk.core


class ImageRepository(
    aws_cdk.aws_ecr.Repository,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-container-registry.ImageRepository",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        force_delete: typing.Optional[builtins.bool] = None,
        image_scan_on_push: typing.Optional[builtins.bool] = None,
        image_tag_mutability: typing.Optional[aws_cdk.aws_ecr.TagMutability] = None,
        lifecycle_registry_id: typing.Optional[builtins.str] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[aws_cdk.aws_ecr.LifecycleRule]] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param force_delete: If a repository contains images, forces the deletion during stack deletion. Default: false
        :param image_scan_on_push: Enable the scan on push when creating the repository. Default: false
        :param image_tag_mutability: The tag mutability setting for the repository. If this parameter is omitted, the default setting of MUTABLE will be used which will allow image tags to be overwritten. Default: TagMutability.MUTABLE
        :param lifecycle_registry_id: The AWS account ID associated with the registry that contains the repository. Default: The default registry is assumed.
        :param lifecycle_rules: Life cycle rules to apply to this registry. Default: No life cycle rules
        :param removal_policy: Determine what happens to the repository when the resource/stack is deleted. Default: RemovalPolicy.Retain
        :param repository_name: Name for this repository. Default: Automatically generated name.
        '''
        props = ImageRepositoryProps(
            force_delete=force_delete,
            image_scan_on_push=image_scan_on_push,
            image_tag_mutability=image_tag_mutability,
            lifecycle_registry_id=lifecycle_registry_id,
            lifecycle_rules=lifecycle_rules,
            removal_policy=removal_policy,
            repository_name=repository_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="onFinding")
    def on_finding(
        self,
        id: builtins.str,
        *,
        alarm_topic: aws_cdk.aws_sns.ITopic,
        severity: "Severity",
        image_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> aws_cdk.aws_events.Rule:
        '''
        :param id: -
        :param alarm_topic: -
        :param severity: -
        :param image_tags: Only watch changes to the image tags specified. Leave it undefined to watch the full repository. Default: - Watch the changes to the repository with all image tags
        '''
        options = OnFindingOptions(
            alarm_topic=alarm_topic, severity=severity, image_tags=image_tags
        )

        return typing.cast(aws_cdk.aws_events.Rule, jsii.invoke(self, "onFinding", [id, options]))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-container-registry.ImageRepositoryProps",
    jsii_struct_bases=[aws_cdk.aws_ecr.RepositoryProps],
    name_mapping={
        "image_scan_on_push": "imageScanOnPush",
        "image_tag_mutability": "imageTagMutability",
        "lifecycle_registry_id": "lifecycleRegistryId",
        "lifecycle_rules": "lifecycleRules",
        "removal_policy": "removalPolicy",
        "repository_name": "repositoryName",
        "force_delete": "forceDelete",
    },
)
class ImageRepositoryProps(aws_cdk.aws_ecr.RepositoryProps):
    def __init__(
        self,
        *,
        image_scan_on_push: typing.Optional[builtins.bool] = None,
        image_tag_mutability: typing.Optional[aws_cdk.aws_ecr.TagMutability] = None,
        lifecycle_registry_id: typing.Optional[builtins.str] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[aws_cdk.aws_ecr.LifecycleRule]] = None,
        removal_policy: typing.Optional[aws_cdk.core.RemovalPolicy] = None,
        repository_name: typing.Optional[builtins.str] = None,
        force_delete: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param image_scan_on_push: Enable the scan on push when creating the repository. Default: false
        :param image_tag_mutability: The tag mutability setting for the repository. If this parameter is omitted, the default setting of MUTABLE will be used which will allow image tags to be overwritten. Default: TagMutability.MUTABLE
        :param lifecycle_registry_id: The AWS account ID associated with the registry that contains the repository. Default: The default registry is assumed.
        :param lifecycle_rules: Life cycle rules to apply to this registry. Default: No life cycle rules
        :param removal_policy: Determine what happens to the repository when the resource/stack is deleted. Default: RemovalPolicy.Retain
        :param repository_name: Name for this repository. Default: Automatically generated name.
        :param force_delete: If a repository contains images, forces the deletion during stack deletion. Default: false
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if image_scan_on_push is not None:
            self._values["image_scan_on_push"] = image_scan_on_push
        if image_tag_mutability is not None:
            self._values["image_tag_mutability"] = image_tag_mutability
        if lifecycle_registry_id is not None:
            self._values["lifecycle_registry_id"] = lifecycle_registry_id
        if lifecycle_rules is not None:
            self._values["lifecycle_rules"] = lifecycle_rules
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if repository_name is not None:
            self._values["repository_name"] = repository_name
        if force_delete is not None:
            self._values["force_delete"] = force_delete

    @builtins.property
    def image_scan_on_push(self) -> typing.Optional[builtins.bool]:
        '''Enable the scan on push when creating the repository.

        :default: false
        '''
        result = self._values.get("image_scan_on_push")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def image_tag_mutability(self) -> typing.Optional[aws_cdk.aws_ecr.TagMutability]:
        '''The tag mutability setting for the repository.

        If this parameter is omitted, the default setting of MUTABLE will be used which will allow image tags to be overwritten.

        :default: TagMutability.MUTABLE
        '''
        result = self._values.get("image_tag_mutability")
        return typing.cast(typing.Optional[aws_cdk.aws_ecr.TagMutability], result)

    @builtins.property
    def lifecycle_registry_id(self) -> typing.Optional[builtins.str]:
        '''The AWS account ID associated with the registry that contains the repository.

        :default: The default registry is assumed.

        :see: https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_PutLifecyclePolicy.html
        '''
        result = self._values.get("lifecycle_registry_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lifecycle_rules(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ecr.LifecycleRule]]:
        '''Life cycle rules to apply to this registry.

        :default: No life cycle rules
        '''
        result = self._values.get("lifecycle_rules")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ecr.LifecycleRule]], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.core.RemovalPolicy]:
        '''Determine what happens to the repository when the resource/stack is deleted.

        :default: RemovalPolicy.Retain
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.core.RemovalPolicy], result)

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''Name for this repository.

        :default: Automatically generated name.
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_delete(self) -> typing.Optional[builtins.bool]:
        '''If a repository contains images, forces the deletion during stack deletion.

        :default: false
        '''
        result = self._values.get("force_delete")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImageRepositoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-container-registry.OnFindingOptions",
    jsii_struct_bases=[],
    name_mapping={
        "alarm_topic": "alarmTopic",
        "severity": "severity",
        "image_tags": "imageTags",
    },
)
class OnFindingOptions:
    def __init__(
        self,
        *,
        alarm_topic: aws_cdk.aws_sns.ITopic,
        severity: "Severity",
        image_tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param alarm_topic: -
        :param severity: -
        :param image_tags: Only watch changes to the image tags specified. Leave it undefined to watch the full repository. Default: - Watch the changes to the repository with all image tags
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "alarm_topic": alarm_topic,
            "severity": severity,
        }
        if image_tags is not None:
            self._values["image_tags"] = image_tags

    @builtins.property
    def alarm_topic(self) -> aws_cdk.aws_sns.ITopic:
        result = self._values.get("alarm_topic")
        assert result is not None, "Required property 'alarm_topic' is missing"
        return typing.cast(aws_cdk.aws_sns.ITopic, result)

    @builtins.property
    def severity(self) -> "Severity":
        result = self._values.get("severity")
        assert result is not None, "Required property 'severity' is missing"
        return typing.cast("Severity", result)

    @builtins.property
    def image_tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Only watch changes to the image tags specified.

        Leave it undefined to watch the full repository.

        :default: - Watch the changes to the repository with all image tags
        '''
        result = self._values.get("image_tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnFindingOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cloudcomponents/cdk-container-registry.Severity")
class Severity(enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"
    UNDEFINED = "UNDEFINED"


__all__ = [
    "ImageRepository",
    "ImageRepositoryProps",
    "OnFindingOptions",
    "Severity",
]

publication.publish()
