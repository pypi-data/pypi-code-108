'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-pull-request-approval-rule

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-pull-request-approval-rule)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-pull-request-approval-rule/)

> CodeCommit pull request approval rules to enforcing your pull request workflow

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-pull-request-approval-rule
```

Python:

```bash
pip install cloudcomponents.cdk-pull-request-approval-rule
```

## How to use

```python
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { Repository } from '@aws-cdk/aws-codecommit';
import { BuildSpec } from '@aws-cdk/aws-codebuild';
import { PullRequestCheck } from '@cloudcomponents/cdk-pull-request-check';
import {
  ApprovalRuleTemplate,
  ApprovalRuleTemplateRepositoryAssociation,
} from '@cloudcomponents/cdk-pull-request-approval-rule';

export class PullRequestStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const repository = new Repository(this, 'Repository', {
      repositoryName: 'pr-check-repository',
    });

    const { approvalRuleTemplateName } = new ApprovalRuleTemplate(
      this,
      'ApprovalRuleTemplate',
      {
        approvalRuleTemplateName: 'template-name',
        template: {
          approvers: {
            numberOfApprovalsNeeded: 1,
          },
        },
      },
    );

    new ApprovalRuleTemplateRepositoryAssociation(
      this,
      'ApprovalRuleTemplateRepositoryAssociation',
      {
        approvalRuleTemplateName,
        repository,
      },
    );

    new PullRequestCheck(this, 'PullRequestCheck', {
      repository,
      buildSpec: BuildSpec.fromSourceFilename('prcheck.yml'),
    });
  }
}
```

## ApprovalRuleOverridden notification

```python
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { Repository } from '@aws-cdk/aws-codecommit';
import { BuildSpec } from '@aws-cdk/aws-codebuild';
import { PullRequestCheck } from '@cloudcomponents/cdk-pull-request-check';
import {
  ApprovalRuleTemplate,
  ApprovalRuleTemplateRepositoryAssociation,
} from '@cloudcomponents/cdk-pull-request-approval-rule';

export class PullRequestStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const repository = new Repository(this, 'Repository', {
      repositoryName: 'pr-check-repository',
    });

    const { approvalRuleTemplateName } = new ApprovalRuleTemplate(
      this,
      'ApprovalRuleTemplate',
      {
        approvalRuleTemplateName: 'template-name',
        template: {
          approvers: {
            numberOfApprovalsNeeded: 1,
          },
        },
      },
    );

    const ruleAsscociation = new ApprovalRuleTemplateRepositoryAssociation(
      stack,
      'ApprovalRuleTemplateRepositoryAssociation',
      {
          approvalRuleTemplateName,
          repository,
      },
    );

    const topic = new Topic(stack, 'Topic');

    ruleAsscociation.onOverridden('overridden', {
        target: new SnsTopic(topic),
    });

    // Approves the pull request
    new PullRequestCheck(this, 'PullRequestCheck', {
        repository,
        buildSpec: BuildSpec.fromSourceFilename('prcheck.yml'),
    });
  }
}
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-pull-request-approval-rule/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-pull-request-approval-rule/LICENSE)
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

import aws_cdk.aws_codecommit
import aws_cdk.aws_events
import aws_cdk.core


class ApprovalRuleTemplate(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-pull-request-approval-rule.ApprovalRuleTemplate",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        approval_rule_template_name: builtins.str,
        template: "Template",
        approval_rule_template_description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param approval_rule_template_name: The name of the approval rule template.
        :param template: The content of the approval rule that is created on pull requests in associated repositories.
        :param approval_rule_template_description: The description of the approval rule template.
        '''
        props = ApprovalRuleTemplateProps(
            approval_rule_template_name=approval_rule_template_name,
            template=template,
            approval_rule_template_description=approval_rule_template_description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="approvalRuleTemplateName")
    def approval_rule_template_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "approvalRuleTemplateName"))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-pull-request-approval-rule.ApprovalRuleTemplateProps",
    jsii_struct_bases=[],
    name_mapping={
        "approval_rule_template_name": "approvalRuleTemplateName",
        "template": "template",
        "approval_rule_template_description": "approvalRuleTemplateDescription",
    },
)
class ApprovalRuleTemplateProps:
    def __init__(
        self,
        *,
        approval_rule_template_name: builtins.str,
        template: "Template",
        approval_rule_template_description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param approval_rule_template_name: The name of the approval rule template.
        :param template: The content of the approval rule that is created on pull requests in associated repositories.
        :param approval_rule_template_description: The description of the approval rule template.
        '''
        if isinstance(template, dict):
            template = Template(**template)
        self._values: typing.Dict[str, typing.Any] = {
            "approval_rule_template_name": approval_rule_template_name,
            "template": template,
        }
        if approval_rule_template_description is not None:
            self._values["approval_rule_template_description"] = approval_rule_template_description

    @builtins.property
    def approval_rule_template_name(self) -> builtins.str:
        '''The name of the approval rule template.'''
        result = self._values.get("approval_rule_template_name")
        assert result is not None, "Required property 'approval_rule_template_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template(self) -> "Template":
        '''The content of the approval rule that is created on pull requests in associated repositories.'''
        result = self._values.get("template")
        assert result is not None, "Required property 'template' is missing"
        return typing.cast("Template", result)

    @builtins.property
    def approval_rule_template_description(self) -> typing.Optional[builtins.str]:
        '''The description of the approval rule template.'''
        result = self._values.get("approval_rule_template_description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApprovalRuleTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ApprovalRuleTemplateRepositoryAssociation(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-pull-request-approval-rule.ApprovalRuleTemplateRepositoryAssociation",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        approval_rule_template_name: builtins.str,
        repository: aws_cdk.aws_codecommit.IRepository,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param approval_rule_template_name: The name of the template you want to associate with one or more repositories.
        :param repository: The repository you want to associate with the template.
        '''
        props = ApprovalRuleTemplateRepositoryAssociationProps(
            approval_rule_template_name=approval_rule_template_name,
            repository=repository,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="onOverridden")
    def on_overridden(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        '''
        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        '''
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return typing.cast(aws_cdk.aws_events.Rule, jsii.invoke(self, "onOverridden", [id, options]))


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-pull-request-approval-rule.ApprovalRuleTemplateRepositoryAssociationProps",
    jsii_struct_bases=[],
    name_mapping={
        "approval_rule_template_name": "approvalRuleTemplateName",
        "repository": "repository",
    },
)
class ApprovalRuleTemplateRepositoryAssociationProps:
    def __init__(
        self,
        *,
        approval_rule_template_name: builtins.str,
        repository: aws_cdk.aws_codecommit.IRepository,
    ) -> None:
        '''
        :param approval_rule_template_name: The name of the template you want to associate with one or more repositories.
        :param repository: The repository you want to associate with the template.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "approval_rule_template_name": approval_rule_template_name,
            "repository": repository,
        }

    @builtins.property
    def approval_rule_template_name(self) -> builtins.str:
        '''The name of the template you want to associate with one or more repositories.'''
        result = self._values.get("approval_rule_template_name")
        assert result is not None, "Required property 'approval_rule_template_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repository(self) -> aws_cdk.aws_codecommit.IRepository:
        '''The repository you want to associate with the template.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast(aws_cdk.aws_codecommit.IRepository, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApprovalRuleTemplateRepositoryAssociationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-pull-request-approval-rule.Approvers",
    jsii_struct_bases=[],
    name_mapping={
        "number_of_approvals_needed": "numberOfApprovalsNeeded",
        "approval_pool_members": "approvalPoolMembers",
    },
)
class Approvers:
    def __init__(
        self,
        *,
        number_of_approvals_needed: jsii.Number,
        approval_pool_members: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param number_of_approvals_needed: -
        :param approval_pool_members: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "number_of_approvals_needed": number_of_approvals_needed,
        }
        if approval_pool_members is not None:
            self._values["approval_pool_members"] = approval_pool_members

    @builtins.property
    def number_of_approvals_needed(self) -> jsii.Number:
        result = self._values.get("number_of_approvals_needed")
        assert result is not None, "Required property 'number_of_approvals_needed' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def approval_pool_members(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("approval_pool_members")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Approvers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-pull-request-approval-rule.Template",
    jsii_struct_bases=[],
    name_mapping={"approvers": "approvers", "branches": "branches"},
)
class Template:
    def __init__(
        self,
        *,
        approvers: Approvers,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param approvers: -
        :param branches: -
        '''
        if isinstance(approvers, dict):
            approvers = Approvers(**approvers)
        self._values: typing.Dict[str, typing.Any] = {
            "approvers": approvers,
        }
        if branches is not None:
            self._values["branches"] = branches

    @builtins.property
    def approvers(self) -> Approvers:
        result = self._values.get("approvers")
        assert result is not None, "Required property 'approvers' is missing"
        return typing.cast(Approvers, result)

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Template(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApprovalRuleTemplate",
    "ApprovalRuleTemplateProps",
    "ApprovalRuleTemplateRepositoryAssociation",
    "ApprovalRuleTemplateRepositoryAssociationProps",
    "Approvers",
    "Template",
]

publication.publish()
