'''
[![cloudcomponents Logo](https://raw.githubusercontent.com/cloudcomponents/cdk-constructs/master/logo.png)](https://github.com/cloudcomponents/cdk-constructs)

# @cloudcomponents/cdk-codepipeline-check-parameter-action

[![Build Status](https://github.com/cloudcomponents/cdk-constructs/workflows/Build/badge.svg)](https://github.com/cloudcomponents/cdk-constructs/actions?query=workflow=Build)
[![cdkdx](https://img.shields.io/badge/buildtool-cdkdx-blue.svg)](https://github.com/hupe1980/cdkdx)
[![typescript](https://img.shields.io/badge/jsii-typescript-blueviolet.svg)](https://www.npmjs.com/package/@cloudcomponents/cdk-codepipeline-check-parameter-action)
[![python](https://img.shields.io/badge/jsii-python-blueviolet.svg)](https://pypi.org/project/cloudcomponents.cdk-codepipeline-check-parameter-action/)

> Cdk component that checks if system parameters are set correctly

## Install

TypeScript/JavaScript:

```bash
npm i @cloudcomponents/cdk-codepipeline-check-parameter-action
```

Python:

```bash
pip install cloudcomponents.cdk-codepipeline-check-parameter-action
```

## How to use

```python
import { Construct, Stack, StackProps } from '@aws-cdk/core';
import { Repository } from '@aws-cdk/aws-codecommit';
import { Pipeline, Artifact } from '@aws-cdk/aws-codepipeline';
import { CodeCommitSourceAction } from '@aws-cdk/aws-codepipeline-actions';
import { CodePipelineCheckParameterAction } from '@cloudcomponents/cdk-codepipeline-check-parameter-action';

export class CodePipelineCheckParameterActionStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const repository = new Repository(this, 'Repository', {
      repositoryName: 'MyRepositoryName',
    });

    const sourceArtifact = new Artifact();

    const sourceAction = new CodeCommitSourceAction({
      actionName: 'CodeCommit',
      repository,
      output: sourceArtifact,
      branch: 'master',
    });

    const checkAction = new CodePipelineCheckParameterAction({
      actionName: 'Check',
      parameterName: '/test',
      regExp: /^The.*Spain$/,
      logParameter: true,
    });

    new Pipeline(this, 'MyPipeline', {
      pipelineName: 'MyPipeline',
      stages: [
        {
          stageName: 'Source',
          actions: [sourceAction],
        },
        {
          stageName: 'Check',
          actions: [checkAction],
        },
      ],
    });
  }
}
```

## API Reference

See [API.md](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-codepipeline-check-parameter-action/API.md).

## Example

See more complete [examples](https://github.com/cloudcomponents/cdk-constructs/tree/master/examples).

## License

[MIT](https://github.com/cloudcomponents/cdk-constructs/tree/master/packages/cdk-codepipeline-check-parameter-action/LICENSE)
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

import aws_cdk.aws_codepipeline
import aws_cdk.aws_codepipeline_actions
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_s3
import aws_cdk.core


class CheckParameterFunction(
    aws_cdk.aws_lambda.Function,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.CheckParameterFunction",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        parameter_name: builtins.str,
        cross_account_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param parameter_name: The name of the parameter.
        :param cross_account_role: Role for crossAccount permission.
        '''
        props = CheckParamterFunctionProps(
            parameter_name=parameter_name, cross_account_role=cross_account_role
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.CheckParamterFunctionProps",
    jsii_struct_bases=[],
    name_mapping={
        "parameter_name": "parameterName",
        "cross_account_role": "crossAccountRole",
    },
)
class CheckParamterFunctionProps:
    def __init__(
        self,
        *,
        parameter_name: builtins.str,
        cross_account_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param parameter_name: The name of the parameter.
        :param cross_account_role: Role for crossAccount permission.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "parameter_name": parameter_name,
        }
        if cross_account_role is not None:
            self._values["cross_account_role"] = cross_account_role

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''The name of the parameter.'''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cross_account_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Role for crossAccount permission.'''
        result = self._values.get("cross_account_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CheckParamterFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodePipelineCheckParameterAction(
    aws_cdk.aws_codepipeline_actions.Action,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.CodePipelineCheckParameterAction",
):
    '''Represents a reference to a CodePipelineCheckParameterAction.'''

    def __init__(
        self,
        *,
        reg_exp: typing.Optional["RegExp"] = None,
        parameter_name: builtins.str,
        cross_account_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        log_parameter: typing.Optional[builtins.bool] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param reg_exp: Regular expression to validate the parameter.
        :param parameter_name: The name of the parameter.
        :param cross_account_role: Role for crossAccount permission.
        :param log_parameter: Parameter is logged after successful check. Default: false The parameter is not logged
        :param role: The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        '''
        props = CodePipelineCheckParameterActionProps(
            reg_exp=reg_exp,
            parameter_name=parameter_name,
            cross_account_role=cross_account_role,
            log_parameter=log_parameter,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bound")
    def _bound(
        self,
        scope: aws_cdk.core.Construct,
        _stage: aws_cdk.aws_codepipeline.IStage,
        *,
        bucket: aws_cdk.aws_s3.IBucket,
        role: aws_cdk.aws_iam.IRole,
    ) -> aws_cdk.aws_codepipeline.ActionConfig:
        '''This is a renamed version of the {@link IAction.bind} method.

        :param scope: -
        :param _stage: -
        :param bucket: 
        :param role: 
        '''
        options = aws_cdk.aws_codepipeline.ActionBindOptions(bucket=bucket, role=role)

        return typing.cast(aws_cdk.aws_codepipeline.ActionConfig, jsii.invoke(self, "bound", [scope, _stage, options]))


class CodePipelineCheckUrlParameterAction(
    CodePipelineCheckParameterAction,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.CodePipelineCheckUrlParameterAction",
):
    def __init__(
        self,
        *,
        exact: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
        parameter_name: builtins.str,
        cross_account_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        log_parameter: typing.Optional[builtins.bool] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param exact: Only match an exact string. Default: true
        :param strict: Force URLs to start with a valid protocol or www.
        :param parameter_name: The name of the parameter.
        :param cross_account_role: Role for crossAccount permission.
        :param log_parameter: Parameter is logged after successful check. Default: false The parameter is not logged
        :param role: The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        '''
        props = CodePipelineCheckUrlParameterActionProps(
            exact=exact,
            strict=strict,
            parameter_name=parameter_name,
            cross_account_role=cross_account_role,
            log_parameter=log_parameter,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.CommonCodePipelineCheckParameterActionProps",
    jsii_struct_bases=[aws_cdk.aws_codepipeline.CommonAwsActionProps],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "parameter_name": "parameterName",
        "cross_account_role": "crossAccountRole",
        "log_parameter": "logParameter",
    },
)
class CommonCodePipelineCheckParameterActionProps(
    aws_cdk.aws_codepipeline.CommonAwsActionProps,
):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        parameter_name: builtins.str,
        cross_account_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        log_parameter: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param parameter_name: The name of the parameter.
        :param cross_account_role: Role for crossAccount permission.
        :param log_parameter: Parameter is logged after successful check. Default: false The parameter is not logged
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "parameter_name": parameter_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if cross_account_role is not None:
            self._values["cross_account_role"] = cross_account_role
        if log_parameter is not None:
            self._values["log_parameter"] = log_parameter

    @builtins.property
    def action_name(self) -> builtins.str:
        '''The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''The name of the parameter.'''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cross_account_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Role for crossAccount permission.'''
        result = self._values.get("cross_account_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def log_parameter(self) -> typing.Optional[builtins.bool]:
        '''Parameter is logged after successful check.

        :default: false The parameter is not logged
        '''
        result = self._values.get("log_parameter")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommonCodePipelineCheckParameterActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.RegExp",
    jsii_struct_bases=[],
    name_mapping={"source": "source"},
)
class RegExp:
    def __init__(self, *, source: builtins.str) -> None:
        '''
        :param source: -
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "source": source,
        }

    @builtins.property
    def source(self) -> builtins.str:
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegExp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodePipelineCheckEmailParameterAction(
    CodePipelineCheckParameterAction,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.CodePipelineCheckEmailParameterAction",
):
    def __init__(
        self,
        *,
        exact: typing.Optional[builtins.bool] = None,
        parameter_name: builtins.str,
        cross_account_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        log_parameter: typing.Optional[builtins.bool] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param exact: Only match an exact string. Default: true
        :param parameter_name: The name of the parameter.
        :param cross_account_role: Role for crossAccount permission.
        :param log_parameter: Parameter is logged after successful check. Default: false The parameter is not logged
        :param role: The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        '''
        props = CodePipelineCheckEmailParameterActionProps(
            exact=exact,
            parameter_name=parameter_name,
            cross_account_role=cross_account_role,
            log_parameter=log_parameter,
            role=role,
            action_name=action_name,
            run_order=run_order,
            variables_namespace=variables_namespace,
        )

        jsii.create(self.__class__, self, [props])


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.CodePipelineCheckEmailParameterActionProps",
    jsii_struct_bases=[CommonCodePipelineCheckParameterActionProps],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "parameter_name": "parameterName",
        "cross_account_role": "crossAccountRole",
        "log_parameter": "logParameter",
        "exact": "exact",
    },
)
class CodePipelineCheckEmailParameterActionProps(
    CommonCodePipelineCheckParameterActionProps,
):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        parameter_name: builtins.str,
        cross_account_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        log_parameter: typing.Optional[builtins.bool] = None,
        exact: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param parameter_name: The name of the parameter.
        :param cross_account_role: Role for crossAccount permission.
        :param log_parameter: Parameter is logged after successful check. Default: false The parameter is not logged
        :param exact: Only match an exact string. Default: true
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "parameter_name": parameter_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if cross_account_role is not None:
            self._values["cross_account_role"] = cross_account_role
        if log_parameter is not None:
            self._values["log_parameter"] = log_parameter
        if exact is not None:
            self._values["exact"] = exact

    @builtins.property
    def action_name(self) -> builtins.str:
        '''The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''The name of the parameter.'''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cross_account_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Role for crossAccount permission.'''
        result = self._values.get("cross_account_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def log_parameter(self) -> typing.Optional[builtins.bool]:
        '''Parameter is logged after successful check.

        :default: false The parameter is not logged
        '''
        result = self._values.get("log_parameter")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.bool]:
        '''Only match an exact string.

        :default: true
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodePipelineCheckEmailParameterActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.CodePipelineCheckParameterActionProps",
    jsii_struct_bases=[CommonCodePipelineCheckParameterActionProps],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "parameter_name": "parameterName",
        "cross_account_role": "crossAccountRole",
        "log_parameter": "logParameter",
        "reg_exp": "regExp",
    },
)
class CodePipelineCheckParameterActionProps(
    CommonCodePipelineCheckParameterActionProps,
):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        parameter_name: builtins.str,
        cross_account_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        log_parameter: typing.Optional[builtins.bool] = None,
        reg_exp: typing.Optional[RegExp] = None,
    ) -> None:
        '''
        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param parameter_name: The name of the parameter.
        :param cross_account_role: Role for crossAccount permission.
        :param log_parameter: Parameter is logged after successful check. Default: false The parameter is not logged
        :param reg_exp: Regular expression to validate the parameter.
        '''
        if isinstance(reg_exp, dict):
            reg_exp = RegExp(**reg_exp)
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "parameter_name": parameter_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if cross_account_role is not None:
            self._values["cross_account_role"] = cross_account_role
        if log_parameter is not None:
            self._values["log_parameter"] = log_parameter
        if reg_exp is not None:
            self._values["reg_exp"] = reg_exp

    @builtins.property
    def action_name(self) -> builtins.str:
        '''The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''The name of the parameter.'''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cross_account_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Role for crossAccount permission.'''
        result = self._values.get("cross_account_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def log_parameter(self) -> typing.Optional[builtins.bool]:
        '''Parameter is logged after successful check.

        :default: false The parameter is not logged
        '''
        result = self._values.get("log_parameter")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def reg_exp(self) -> typing.Optional[RegExp]:
        '''Regular expression to validate the parameter.'''
        result = self._values.get("reg_exp")
        return typing.cast(typing.Optional[RegExp], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodePipelineCheckParameterActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudcomponents/cdk-codepipeline-check-parameter-action.CodePipelineCheckUrlParameterActionProps",
    jsii_struct_bases=[CommonCodePipelineCheckParameterActionProps],
    name_mapping={
        "action_name": "actionName",
        "run_order": "runOrder",
        "variables_namespace": "variablesNamespace",
        "role": "role",
        "parameter_name": "parameterName",
        "cross_account_role": "crossAccountRole",
        "log_parameter": "logParameter",
        "exact": "exact",
        "strict": "strict",
    },
)
class CodePipelineCheckUrlParameterActionProps(
    CommonCodePipelineCheckParameterActionProps,
):
    def __init__(
        self,
        *,
        action_name: builtins.str,
        run_order: typing.Optional[jsii.Number] = None,
        variables_namespace: typing.Optional[builtins.str] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        parameter_name: builtins.str,
        cross_account_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        log_parameter: typing.Optional[builtins.bool] = None,
        exact: typing.Optional[builtins.bool] = None,
        strict: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param action_name: The physical, human-readable name of the Action. Note that Action names must be unique within a single Stage.
        :param run_order: The runOrder property for this Action. RunOrder determines the relative order in which multiple Actions in the same Stage execute. Default: 1
        :param variables_namespace: The name of the namespace to use for variables emitted by this action. Default: - a name will be generated, based on the stage and action names, if any of the action's variables were referenced - otherwise, no namespace will be set
        :param role: The Role in which context's this Action will be executing in. The Pipeline's Role will assume this Role (the required permissions for that will be granted automatically) right before executing this Action. This Action will be passed into your {@link IAction.bind} method in the {@link ActionBindOptions.role} property. Default: a new Role will be generated
        :param parameter_name: The name of the parameter.
        :param cross_account_role: Role for crossAccount permission.
        :param log_parameter: Parameter is logged after successful check. Default: false The parameter is not logged
        :param exact: Only match an exact string. Default: true
        :param strict: Force URLs to start with a valid protocol or www.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_name": action_name,
            "parameter_name": parameter_name,
        }
        if run_order is not None:
            self._values["run_order"] = run_order
        if variables_namespace is not None:
            self._values["variables_namespace"] = variables_namespace
        if role is not None:
            self._values["role"] = role
        if cross_account_role is not None:
            self._values["cross_account_role"] = cross_account_role
        if log_parameter is not None:
            self._values["log_parameter"] = log_parameter
        if exact is not None:
            self._values["exact"] = exact
        if strict is not None:
            self._values["strict"] = strict

    @builtins.property
    def action_name(self) -> builtins.str:
        '''The physical, human-readable name of the Action.

        Note that Action names must be unique within a single Stage.
        '''
        result = self._values.get("action_name")
        assert result is not None, "Required property 'action_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def run_order(self) -> typing.Optional[jsii.Number]:
        '''The runOrder property for this Action.

        RunOrder determines the relative order in which multiple Actions in the same Stage execute.

        :default: 1

        :see: https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html
        '''
        result = self._values.get("run_order")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def variables_namespace(self) -> typing.Optional[builtins.str]:
        '''The name of the namespace to use for variables emitted by this action.

        :default:

        - a name will be generated, based on the stage and action names,
        if any of the action's variables were referenced - otherwise,
        no namespace will be set
        '''
        result = self._values.get("variables_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The Role in which context's this Action will be executing in.

        The Pipeline's Role will assume this Role
        (the required permissions for that will be granted automatically)
        right before executing this Action.
        This Action will be passed into your {@link IAction.bind}
        method in the {@link ActionBindOptions.role} property.

        :default: a new Role will be generated
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def parameter_name(self) -> builtins.str:
        '''The name of the parameter.'''
        result = self._values.get("parameter_name")
        assert result is not None, "Required property 'parameter_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cross_account_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Role for crossAccount permission.'''
        result = self._values.get("cross_account_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def log_parameter(self) -> typing.Optional[builtins.bool]:
        '''Parameter is logged after successful check.

        :default: false The parameter is not logged
        '''
        result = self._values.get("log_parameter")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def exact(self) -> typing.Optional[builtins.bool]:
        '''Only match an exact string.

        :default: true
        '''
        result = self._values.get("exact")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def strict(self) -> typing.Optional[builtins.bool]:
        '''Force URLs to start with a valid protocol or www.'''
        result = self._values.get("strict")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodePipelineCheckUrlParameterActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CheckParameterFunction",
    "CheckParamterFunctionProps",
    "CodePipelineCheckEmailParameterAction",
    "CodePipelineCheckEmailParameterActionProps",
    "CodePipelineCheckParameterAction",
    "CodePipelineCheckParameterActionProps",
    "CodePipelineCheckUrlParameterAction",
    "CodePipelineCheckUrlParameterActionProps",
    "CommonCodePipelineCheckParameterActionProps",
    "RegExp",
]

publication.publish()
