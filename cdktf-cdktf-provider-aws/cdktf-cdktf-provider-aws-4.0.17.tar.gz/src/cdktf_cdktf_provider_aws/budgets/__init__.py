import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import cdktf
import constructs


class BudgetsBudget(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudget",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget aws_budgets_budget}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        budget_type: builtins.str,
        limit_amount: builtins.str,
        limit_unit: builtins.str,
        time_unit: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        cost_filter: typing.Optional[typing.Sequence["BudgetsBudgetCostFilter"]] = None,
        cost_filters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        cost_types: typing.Optional["BudgetsBudgetCostTypes"] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        notification: typing.Optional[typing.Sequence["BudgetsBudgetNotification"]] = None,
        time_period_end: typing.Optional[builtins.str] = None,
        time_period_start: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget aws_budgets_budget} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param budget_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#budget_type BudgetsBudget#budget_type}.
        :param limit_amount: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#limit_amount BudgetsBudget#limit_amount}.
        :param limit_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#limit_unit BudgetsBudget#limit_unit}.
        :param time_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#time_unit BudgetsBudget#time_unit}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#account_id BudgetsBudget#account_id}.
        :param cost_filter: cost_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#cost_filter BudgetsBudget#cost_filter}
        :param cost_filters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#cost_filters BudgetsBudget#cost_filters}.
        :param cost_types: cost_types block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#cost_types BudgetsBudget#cost_types}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#name BudgetsBudget#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#name_prefix BudgetsBudget#name_prefix}.
        :param notification: notification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#notification BudgetsBudget#notification}
        :param time_period_end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#time_period_end BudgetsBudget#time_period_end}.
        :param time_period_start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#time_period_start BudgetsBudget#time_period_start}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BudgetsBudgetConfig(
            budget_type=budget_type,
            limit_amount=limit_amount,
            limit_unit=limit_unit,
            time_unit=time_unit,
            account_id=account_id,
            cost_filter=cost_filter,
            cost_filters=cost_filters,
            cost_types=cost_types,
            name=name,
            name_prefix=name_prefix,
            notification=notification,
            time_period_end=time_period_end,
            time_period_start=time_period_start,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putCostTypes")
    def put_cost_types(
        self,
        *,
        include_credit: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_discount: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_other_subscription: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_recurring: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_refund: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_subscription: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_support: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_tax: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_upfront: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        use_amortized: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        use_blended: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param include_credit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_credit BudgetsBudget#include_credit}.
        :param include_discount: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_discount BudgetsBudget#include_discount}.
        :param include_other_subscription: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_other_subscription BudgetsBudget#include_other_subscription}.
        :param include_recurring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_recurring BudgetsBudget#include_recurring}.
        :param include_refund: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_refund BudgetsBudget#include_refund}.
        :param include_subscription: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_subscription BudgetsBudget#include_subscription}.
        :param include_support: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_support BudgetsBudget#include_support}.
        :param include_tax: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_tax BudgetsBudget#include_tax}.
        :param include_upfront: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_upfront BudgetsBudget#include_upfront}.
        :param use_amortized: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#use_amortized BudgetsBudget#use_amortized}.
        :param use_blended: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#use_blended BudgetsBudget#use_blended}.
        '''
        value = BudgetsBudgetCostTypes(
            include_credit=include_credit,
            include_discount=include_discount,
            include_other_subscription=include_other_subscription,
            include_recurring=include_recurring,
            include_refund=include_refund,
            include_subscription=include_subscription,
            include_support=include_support,
            include_tax=include_tax,
            include_upfront=include_upfront,
            use_amortized=use_amortized,
            use_blended=use_blended,
        )

        return typing.cast(None, jsii.invoke(self, "putCostTypes", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="resetCostFilter")
    def reset_cost_filter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCostFilter", []))

    @jsii.member(jsii_name="resetCostFilters")
    def reset_cost_filters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCostFilters", []))

    @jsii.member(jsii_name="resetCostTypes")
    def reset_cost_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCostTypes", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetNotification")
    def reset_notification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotification", []))

    @jsii.member(jsii_name="resetTimePeriodEnd")
    def reset_time_period_end(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimePeriodEnd", []))

    @jsii.member(jsii_name="resetTimePeriodStart")
    def reset_time_period_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimePeriodStart", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="costTypes")
    def cost_types(self) -> "BudgetsBudgetCostTypesOutputReference":
        return typing.cast("BudgetsBudgetCostTypesOutputReference", jsii.get(self, "costTypes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="budgetTypeInput")
    def budget_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "budgetTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="costFilterInput")
    def cost_filter_input(
        self,
    ) -> typing.Optional[typing.List["BudgetsBudgetCostFilter"]]:
        return typing.cast(typing.Optional[typing.List["BudgetsBudgetCostFilter"]], jsii.get(self, "costFilterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="costFiltersInput")
    def cost_filters_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "costFiltersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="costTypesInput")
    def cost_types_input(self) -> typing.Optional["BudgetsBudgetCostTypes"]:
        return typing.cast(typing.Optional["BudgetsBudgetCostTypes"], jsii.get(self, "costTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="limitAmountInput")
    def limit_amount_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "limitAmountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="limitUnitInput")
    def limit_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "limitUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationInput")
    def notification_input(
        self,
    ) -> typing.Optional[typing.List["BudgetsBudgetNotification"]]:
        return typing.cast(typing.Optional[typing.List["BudgetsBudgetNotification"]], jsii.get(self, "notificationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timePeriodEndInput")
    def time_period_end_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timePeriodEndInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timePeriodStartInput")
    def time_period_start_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timePeriodStartInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeUnitInput")
    def time_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timeUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="budgetType")
    def budget_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "budgetType"))

    @budget_type.setter
    def budget_type(self, value: builtins.str) -> None:
        jsii.set(self, "budgetType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="costFilter")
    def cost_filter(self) -> typing.List["BudgetsBudgetCostFilter"]:
        return typing.cast(typing.List["BudgetsBudgetCostFilter"], jsii.get(self, "costFilter"))

    @cost_filter.setter
    def cost_filter(self, value: typing.List["BudgetsBudgetCostFilter"]) -> None:
        jsii.set(self, "costFilter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="costFilters")
    def cost_filters(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "costFilters"))

    @cost_filters.setter
    def cost_filters(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "costFilters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="limitAmount")
    def limit_amount(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "limitAmount"))

    @limit_amount.setter
    def limit_amount(self, value: builtins.str) -> None:
        jsii.set(self, "limitAmount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="limitUnit")
    def limit_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "limitUnit"))

    @limit_unit.setter
    def limit_unit(self, value: builtins.str) -> None:
        jsii.set(self, "limitUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notification")
    def notification(self) -> typing.List["BudgetsBudgetNotification"]:
        return typing.cast(typing.List["BudgetsBudgetNotification"], jsii.get(self, "notification"))

    @notification.setter
    def notification(self, value: typing.List["BudgetsBudgetNotification"]) -> None:
        jsii.set(self, "notification", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timePeriodEnd")
    def time_period_end(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timePeriodEnd"))

    @time_period_end.setter
    def time_period_end(self, value: builtins.str) -> None:
        jsii.set(self, "timePeriodEnd", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timePeriodStart")
    def time_period_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timePeriodStart"))

    @time_period_start.setter
    def time_period_start(self, value: builtins.str) -> None:
        jsii.set(self, "timePeriodStart", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeUnit")
    def time_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeUnit"))

    @time_unit.setter
    def time_unit(self, value: builtins.str) -> None:
        jsii.set(self, "timeUnit", value)


class BudgetsBudgetAction(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetAction",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action aws_budgets_budget_action}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        action_threshold: "BudgetsBudgetActionActionThreshold",
        action_type: builtins.str,
        approval_model: builtins.str,
        budget_name: builtins.str,
        definition: "BudgetsBudgetActionDefinition",
        execution_role_arn: builtins.str,
        notification_type: builtins.str,
        subscriber: typing.Sequence["BudgetsBudgetActionSubscriber"],
        account_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action aws_budgets_budget_action} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param action_threshold: action_threshold block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_threshold BudgetsBudgetAction#action_threshold}
        :param action_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_type BudgetsBudgetAction#action_type}.
        :param approval_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#approval_model BudgetsBudgetAction#approval_model}.
        :param budget_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#budget_name BudgetsBudgetAction#budget_name}.
        :param definition: definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#definition BudgetsBudgetAction#definition}
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#execution_role_arn BudgetsBudgetAction#execution_role_arn}.
        :param notification_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#notification_type BudgetsBudgetAction#notification_type}.
        :param subscriber: subscriber block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#subscriber BudgetsBudgetAction#subscriber}
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#account_id BudgetsBudgetAction#account_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = BudgetsBudgetActionConfig(
            action_threshold=action_threshold,
            action_type=action_type,
            approval_model=approval_model,
            budget_name=budget_name,
            definition=definition,
            execution_role_arn=execution_role_arn,
            notification_type=notification_type,
            subscriber=subscriber,
            account_id=account_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putActionThreshold")
    def put_action_threshold(
        self,
        *,
        action_threshold_type: builtins.str,
        action_threshold_value: jsii.Number,
    ) -> None:
        '''
        :param action_threshold_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_threshold_type BudgetsBudgetAction#action_threshold_type}.
        :param action_threshold_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_threshold_value BudgetsBudgetAction#action_threshold_value}.
        '''
        value = BudgetsBudgetActionActionThreshold(
            action_threshold_type=action_threshold_type,
            action_threshold_value=action_threshold_value,
        )

        return typing.cast(None, jsii.invoke(self, "putActionThreshold", [value]))

    @jsii.member(jsii_name="putDefinition")
    def put_definition(
        self,
        *,
        iam_action_definition: typing.Optional["BudgetsBudgetActionDefinitionIamActionDefinition"] = None,
        scp_action_definition: typing.Optional["BudgetsBudgetActionDefinitionScpActionDefinition"] = None,
        ssm_action_definition: typing.Optional["BudgetsBudgetActionDefinitionSsmActionDefinition"] = None,
    ) -> None:
        '''
        :param iam_action_definition: iam_action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#iam_action_definition BudgetsBudgetAction#iam_action_definition}
        :param scp_action_definition: scp_action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#scp_action_definition BudgetsBudgetAction#scp_action_definition}
        :param ssm_action_definition: ssm_action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#ssm_action_definition BudgetsBudgetAction#ssm_action_definition}
        '''
        value = BudgetsBudgetActionDefinition(
            iam_action_definition=iam_action_definition,
            scp_action_definition=scp_action_definition,
            ssm_action_definition=ssm_action_definition,
        )

        return typing.cast(None, jsii.invoke(self, "putDefinition", [value]))

    @jsii.member(jsii_name="resetAccountId")
    def reset_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccountId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionId")
    def action_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionThreshold")
    def action_threshold(self) -> "BudgetsBudgetActionActionThresholdOutputReference":
        return typing.cast("BudgetsBudgetActionActionThresholdOutputReference", jsii.get(self, "actionThreshold"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definition")
    def definition(self) -> "BudgetsBudgetActionDefinitionOutputReference":
        return typing.cast("BudgetsBudgetActionDefinitionOutputReference", jsii.get(self, "definition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionThresholdInput")
    def action_threshold_input(
        self,
    ) -> typing.Optional["BudgetsBudgetActionActionThreshold"]:
        return typing.cast(typing.Optional["BudgetsBudgetActionActionThreshold"], jsii.get(self, "actionThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionTypeInput")
    def action_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="approvalModelInput")
    def approval_model_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "approvalModelInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="budgetNameInput")
    def budget_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "budgetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="definitionInput")
    def definition_input(self) -> typing.Optional["BudgetsBudgetActionDefinition"]:
        return typing.cast(typing.Optional["BudgetsBudgetActionDefinition"], jsii.get(self, "definitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArnInput")
    def execution_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionRoleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationTypeInput")
    def notification_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notificationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriberInput")
    def subscriber_input(
        self,
    ) -> typing.Optional[typing.List["BudgetsBudgetActionSubscriber"]]:
        return typing.cast(typing.Optional[typing.List["BudgetsBudgetActionSubscriber"]], jsii.get(self, "subscriberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionType")
    def action_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionType"))

    @action_type.setter
    def action_type(self, value: builtins.str) -> None:
        jsii.set(self, "actionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="approvalModel")
    def approval_model(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "approvalModel"))

    @approval_model.setter
    def approval_model(self, value: builtins.str) -> None:
        jsii.set(self, "approvalModel", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="budgetName")
    def budget_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "budgetName"))

    @budget_name.setter
    def budget_name(self, value: builtins.str) -> None:
        jsii.set(self, "budgetName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="executionRoleArn")
    def execution_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionRoleArn"))

    @execution_role_arn.setter
    def execution_role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "executionRoleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationType")
    def notification_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationType"))

    @notification_type.setter
    def notification_type(self, value: builtins.str) -> None:
        jsii.set(self, "notificationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subscriber")
    def subscriber(self) -> typing.List["BudgetsBudgetActionSubscriber"]:
        return typing.cast(typing.List["BudgetsBudgetActionSubscriber"], jsii.get(self, "subscriber"))

    @subscriber.setter
    def subscriber(self, value: typing.List["BudgetsBudgetActionSubscriber"]) -> None:
        jsii.set(self, "subscriber", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionActionThreshold",
    jsii_struct_bases=[],
    name_mapping={
        "action_threshold_type": "actionThresholdType",
        "action_threshold_value": "actionThresholdValue",
    },
)
class BudgetsBudgetActionActionThreshold:
    def __init__(
        self,
        *,
        action_threshold_type: builtins.str,
        action_threshold_value: jsii.Number,
    ) -> None:
        '''
        :param action_threshold_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_threshold_type BudgetsBudgetAction#action_threshold_type}.
        :param action_threshold_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_threshold_value BudgetsBudgetAction#action_threshold_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_threshold_type": action_threshold_type,
            "action_threshold_value": action_threshold_value,
        }

    @builtins.property
    def action_threshold_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_threshold_type BudgetsBudgetAction#action_threshold_type}.'''
        result = self._values.get("action_threshold_type")
        assert result is not None, "Required property 'action_threshold_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_threshold_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_threshold_value BudgetsBudgetAction#action_threshold_value}.'''
        result = self._values.get("action_threshold_value")
        assert result is not None, "Required property 'action_threshold_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetActionActionThreshold(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetsBudgetActionActionThresholdOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionActionThresholdOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionThresholdTypeInput")
    def action_threshold_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionThresholdTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionThresholdValueInput")
    def action_threshold_value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "actionThresholdValueInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionThresholdType")
    def action_threshold_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionThresholdType"))

    @action_threshold_type.setter
    def action_threshold_type(self, value: builtins.str) -> None:
        jsii.set(self, "actionThresholdType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionThresholdValue")
    def action_threshold_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "actionThresholdValue"))

    @action_threshold_value.setter
    def action_threshold_value(self, value: jsii.Number) -> None:
        jsii.set(self, "actionThresholdValue", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BudgetsBudgetActionActionThreshold]:
        return typing.cast(typing.Optional[BudgetsBudgetActionActionThreshold], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BudgetsBudgetActionActionThreshold],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "action_threshold": "actionThreshold",
        "action_type": "actionType",
        "approval_model": "approvalModel",
        "budget_name": "budgetName",
        "definition": "definition",
        "execution_role_arn": "executionRoleArn",
        "notification_type": "notificationType",
        "subscriber": "subscriber",
        "account_id": "accountId",
    },
)
class BudgetsBudgetActionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        action_threshold: BudgetsBudgetActionActionThreshold,
        action_type: builtins.str,
        approval_model: builtins.str,
        budget_name: builtins.str,
        definition: "BudgetsBudgetActionDefinition",
        execution_role_arn: builtins.str,
        notification_type: builtins.str,
        subscriber: typing.Sequence["BudgetsBudgetActionSubscriber"],
        account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Budgets.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param action_threshold: action_threshold block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_threshold BudgetsBudgetAction#action_threshold}
        :param action_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_type BudgetsBudgetAction#action_type}.
        :param approval_model: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#approval_model BudgetsBudgetAction#approval_model}.
        :param budget_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#budget_name BudgetsBudgetAction#budget_name}.
        :param definition: definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#definition BudgetsBudgetAction#definition}
        :param execution_role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#execution_role_arn BudgetsBudgetAction#execution_role_arn}.
        :param notification_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#notification_type BudgetsBudgetAction#notification_type}.
        :param subscriber: subscriber block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#subscriber BudgetsBudgetAction#subscriber}
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#account_id BudgetsBudgetAction#account_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(action_threshold, dict):
            action_threshold = BudgetsBudgetActionActionThreshold(**action_threshold)
        if isinstance(definition, dict):
            definition = BudgetsBudgetActionDefinition(**definition)
        self._values: typing.Dict[str, typing.Any] = {
            "action_threshold": action_threshold,
            "action_type": action_type,
            "approval_model": approval_model,
            "budget_name": budget_name,
            "definition": definition,
            "execution_role_arn": execution_role_arn,
            "notification_type": notification_type,
            "subscriber": subscriber,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id

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
    def action_threshold(self) -> BudgetsBudgetActionActionThreshold:
        '''action_threshold block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_threshold BudgetsBudgetAction#action_threshold}
        '''
        result = self._values.get("action_threshold")
        assert result is not None, "Required property 'action_threshold' is missing"
        return typing.cast(BudgetsBudgetActionActionThreshold, result)

    @builtins.property
    def action_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_type BudgetsBudgetAction#action_type}.'''
        result = self._values.get("action_type")
        assert result is not None, "Required property 'action_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def approval_model(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#approval_model BudgetsBudgetAction#approval_model}.'''
        result = self._values.get("approval_model")
        assert result is not None, "Required property 'approval_model' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def budget_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#budget_name BudgetsBudgetAction#budget_name}.'''
        result = self._values.get("budget_name")
        assert result is not None, "Required property 'budget_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def definition(self) -> "BudgetsBudgetActionDefinition":
        '''definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#definition BudgetsBudgetAction#definition}
        '''
        result = self._values.get("definition")
        assert result is not None, "Required property 'definition' is missing"
        return typing.cast("BudgetsBudgetActionDefinition", result)

    @builtins.property
    def execution_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#execution_role_arn BudgetsBudgetAction#execution_role_arn}.'''
        result = self._values.get("execution_role_arn")
        assert result is not None, "Required property 'execution_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def notification_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#notification_type BudgetsBudgetAction#notification_type}.'''
        result = self._values.get("notification_type")
        assert result is not None, "Required property 'notification_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subscriber(self) -> typing.List["BudgetsBudgetActionSubscriber"]:
        '''subscriber block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#subscriber BudgetsBudgetAction#subscriber}
        '''
        result = self._values.get("subscriber")
        assert result is not None, "Required property 'subscriber' is missing"
        return typing.cast(typing.List["BudgetsBudgetActionSubscriber"], result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#account_id BudgetsBudgetAction#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetActionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionDefinition",
    jsii_struct_bases=[],
    name_mapping={
        "iam_action_definition": "iamActionDefinition",
        "scp_action_definition": "scpActionDefinition",
        "ssm_action_definition": "ssmActionDefinition",
    },
)
class BudgetsBudgetActionDefinition:
    def __init__(
        self,
        *,
        iam_action_definition: typing.Optional["BudgetsBudgetActionDefinitionIamActionDefinition"] = None,
        scp_action_definition: typing.Optional["BudgetsBudgetActionDefinitionScpActionDefinition"] = None,
        ssm_action_definition: typing.Optional["BudgetsBudgetActionDefinitionSsmActionDefinition"] = None,
    ) -> None:
        '''
        :param iam_action_definition: iam_action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#iam_action_definition BudgetsBudgetAction#iam_action_definition}
        :param scp_action_definition: scp_action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#scp_action_definition BudgetsBudgetAction#scp_action_definition}
        :param ssm_action_definition: ssm_action_definition block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#ssm_action_definition BudgetsBudgetAction#ssm_action_definition}
        '''
        if isinstance(iam_action_definition, dict):
            iam_action_definition = BudgetsBudgetActionDefinitionIamActionDefinition(**iam_action_definition)
        if isinstance(scp_action_definition, dict):
            scp_action_definition = BudgetsBudgetActionDefinitionScpActionDefinition(**scp_action_definition)
        if isinstance(ssm_action_definition, dict):
            ssm_action_definition = BudgetsBudgetActionDefinitionSsmActionDefinition(**ssm_action_definition)
        self._values: typing.Dict[str, typing.Any] = {}
        if iam_action_definition is not None:
            self._values["iam_action_definition"] = iam_action_definition
        if scp_action_definition is not None:
            self._values["scp_action_definition"] = scp_action_definition
        if ssm_action_definition is not None:
            self._values["ssm_action_definition"] = ssm_action_definition

    @builtins.property
    def iam_action_definition(
        self,
    ) -> typing.Optional["BudgetsBudgetActionDefinitionIamActionDefinition"]:
        '''iam_action_definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#iam_action_definition BudgetsBudgetAction#iam_action_definition}
        '''
        result = self._values.get("iam_action_definition")
        return typing.cast(typing.Optional["BudgetsBudgetActionDefinitionIamActionDefinition"], result)

    @builtins.property
    def scp_action_definition(
        self,
    ) -> typing.Optional["BudgetsBudgetActionDefinitionScpActionDefinition"]:
        '''scp_action_definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#scp_action_definition BudgetsBudgetAction#scp_action_definition}
        '''
        result = self._values.get("scp_action_definition")
        return typing.cast(typing.Optional["BudgetsBudgetActionDefinitionScpActionDefinition"], result)

    @builtins.property
    def ssm_action_definition(
        self,
    ) -> typing.Optional["BudgetsBudgetActionDefinitionSsmActionDefinition"]:
        '''ssm_action_definition block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#ssm_action_definition BudgetsBudgetAction#ssm_action_definition}
        '''
        result = self._values.get("ssm_action_definition")
        return typing.cast(typing.Optional["BudgetsBudgetActionDefinitionSsmActionDefinition"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetActionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionDefinitionIamActionDefinition",
    jsii_struct_bases=[],
    name_mapping={
        "policy_arn": "policyArn",
        "groups": "groups",
        "roles": "roles",
        "users": "users",
    },
)
class BudgetsBudgetActionDefinitionIamActionDefinition:
    def __init__(
        self,
        *,
        policy_arn: builtins.str,
        groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        users: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#policy_arn BudgetsBudgetAction#policy_arn}.
        :param groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#groups BudgetsBudgetAction#groups}.
        :param roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#roles BudgetsBudgetAction#roles}.
        :param users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#users BudgetsBudgetAction#users}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "policy_arn": policy_arn,
        }
        if groups is not None:
            self._values["groups"] = groups
        if roles is not None:
            self._values["roles"] = roles
        if users is not None:
            self._values["users"] = users

    @builtins.property
    def policy_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#policy_arn BudgetsBudgetAction#policy_arn}.'''
        result = self._values.get("policy_arn")
        assert result is not None, "Required property 'policy_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#groups BudgetsBudgetAction#groups}.'''
        result = self._values.get("groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#roles BudgetsBudgetAction#roles}.'''
        result = self._values.get("roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def users(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#users BudgetsBudgetAction#users}.'''
        result = self._values.get("users")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetActionDefinitionIamActionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetsBudgetActionDefinitionIamActionDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionDefinitionIamActionDefinitionOutputReference",
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

    @jsii.member(jsii_name="resetGroups")
    def reset_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroups", []))

    @jsii.member(jsii_name="resetRoles")
    def reset_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoles", []))

    @jsii.member(jsii_name="resetUsers")
    def reset_users(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsers", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupsInput")
    def groups_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "groupsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyArnInput")
    def policy_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rolesInput")
    def roles_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "rolesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usersInput")
    def users_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "usersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groups")
    def groups(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "groups"))

    @groups.setter
    def groups(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "groups", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyArn")
    def policy_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyArn"))

    @policy_arn.setter
    def policy_arn(self, value: builtins.str) -> None:
        jsii.set(self, "policyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roles")
    def roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "roles"))

    @roles.setter
    def roles(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "roles", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="users")
    def users(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "users"))

    @users.setter
    def users(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "users", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[BudgetsBudgetActionDefinitionIamActionDefinition]:
        return typing.cast(typing.Optional[BudgetsBudgetActionDefinitionIamActionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BudgetsBudgetActionDefinitionIamActionDefinition],
    ) -> None:
        jsii.set(self, "internalValue", value)


class BudgetsBudgetActionDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionDefinitionOutputReference",
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

    @jsii.member(jsii_name="putIamActionDefinition")
    def put_iam_action_definition(
        self,
        *,
        policy_arn: builtins.str,
        groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        users: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param policy_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#policy_arn BudgetsBudgetAction#policy_arn}.
        :param groups: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#groups BudgetsBudgetAction#groups}.
        :param roles: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#roles BudgetsBudgetAction#roles}.
        :param users: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#users BudgetsBudgetAction#users}.
        '''
        value = BudgetsBudgetActionDefinitionIamActionDefinition(
            policy_arn=policy_arn, groups=groups, roles=roles, users=users
        )

        return typing.cast(None, jsii.invoke(self, "putIamActionDefinition", [value]))

    @jsii.member(jsii_name="putScpActionDefinition")
    def put_scp_action_definition(
        self,
        *,
        policy_id: builtins.str,
        target_ids: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#policy_id BudgetsBudgetAction#policy_id}.
        :param target_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#target_ids BudgetsBudgetAction#target_ids}.
        '''
        value = BudgetsBudgetActionDefinitionScpActionDefinition(
            policy_id=policy_id, target_ids=target_ids
        )

        return typing.cast(None, jsii.invoke(self, "putScpActionDefinition", [value]))

    @jsii.member(jsii_name="putSsmActionDefinition")
    def put_ssm_action_definition(
        self,
        *,
        action_sub_type: builtins.str,
        instance_ids: typing.Sequence[builtins.str],
        region: builtins.str,
    ) -> None:
        '''
        :param action_sub_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_sub_type BudgetsBudgetAction#action_sub_type}.
        :param instance_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#instance_ids BudgetsBudgetAction#instance_ids}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#region BudgetsBudgetAction#region}.
        '''
        value = BudgetsBudgetActionDefinitionSsmActionDefinition(
            action_sub_type=action_sub_type, instance_ids=instance_ids, region=region
        )

        return typing.cast(None, jsii.invoke(self, "putSsmActionDefinition", [value]))

    @jsii.member(jsii_name="resetIamActionDefinition")
    def reset_iam_action_definition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIamActionDefinition", []))

    @jsii.member(jsii_name="resetScpActionDefinition")
    def reset_scp_action_definition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScpActionDefinition", []))

    @jsii.member(jsii_name="resetSsmActionDefinition")
    def reset_ssm_action_definition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsmActionDefinition", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamActionDefinition")
    def iam_action_definition(
        self,
    ) -> BudgetsBudgetActionDefinitionIamActionDefinitionOutputReference:
        return typing.cast(BudgetsBudgetActionDefinitionIamActionDefinitionOutputReference, jsii.get(self, "iamActionDefinition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scpActionDefinition")
    def scp_action_definition(
        self,
    ) -> "BudgetsBudgetActionDefinitionScpActionDefinitionOutputReference":
        return typing.cast("BudgetsBudgetActionDefinitionScpActionDefinitionOutputReference", jsii.get(self, "scpActionDefinition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssmActionDefinition")
    def ssm_action_definition(
        self,
    ) -> "BudgetsBudgetActionDefinitionSsmActionDefinitionOutputReference":
        return typing.cast("BudgetsBudgetActionDefinitionSsmActionDefinitionOutputReference", jsii.get(self, "ssmActionDefinition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamActionDefinitionInput")
    def iam_action_definition_input(
        self,
    ) -> typing.Optional[BudgetsBudgetActionDefinitionIamActionDefinition]:
        return typing.cast(typing.Optional[BudgetsBudgetActionDefinitionIamActionDefinition], jsii.get(self, "iamActionDefinitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scpActionDefinitionInput")
    def scp_action_definition_input(
        self,
    ) -> typing.Optional["BudgetsBudgetActionDefinitionScpActionDefinition"]:
        return typing.cast(typing.Optional["BudgetsBudgetActionDefinitionScpActionDefinition"], jsii.get(self, "scpActionDefinitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssmActionDefinitionInput")
    def ssm_action_definition_input(
        self,
    ) -> typing.Optional["BudgetsBudgetActionDefinitionSsmActionDefinition"]:
        return typing.cast(typing.Optional["BudgetsBudgetActionDefinitionSsmActionDefinition"], jsii.get(self, "ssmActionDefinitionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BudgetsBudgetActionDefinition]:
        return typing.cast(typing.Optional[BudgetsBudgetActionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BudgetsBudgetActionDefinition],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionDefinitionScpActionDefinition",
    jsii_struct_bases=[],
    name_mapping={"policy_id": "policyId", "target_ids": "targetIds"},
)
class BudgetsBudgetActionDefinitionScpActionDefinition:
    def __init__(
        self,
        *,
        policy_id: builtins.str,
        target_ids: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param policy_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#policy_id BudgetsBudgetAction#policy_id}.
        :param target_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#target_ids BudgetsBudgetAction#target_ids}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "policy_id": policy_id,
            "target_ids": target_ids,
        }

    @builtins.property
    def policy_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#policy_id BudgetsBudgetAction#policy_id}.'''
        result = self._values.get("policy_id")
        assert result is not None, "Required property 'policy_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#target_ids BudgetsBudgetAction#target_ids}.'''
        result = self._values.get("target_ids")
        assert result is not None, "Required property 'target_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetActionDefinitionScpActionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetsBudgetActionDefinitionScpActionDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionDefinitionScpActionDefinitionOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyIdInput")
    def policy_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetIdsInput")
    def target_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @policy_id.setter
    def policy_id(self, value: builtins.str) -> None:
        jsii.set(self, "policyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="targetIds")
    def target_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetIds"))

    @target_ids.setter
    def target_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "targetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[BudgetsBudgetActionDefinitionScpActionDefinition]:
        return typing.cast(typing.Optional[BudgetsBudgetActionDefinitionScpActionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BudgetsBudgetActionDefinitionScpActionDefinition],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionDefinitionSsmActionDefinition",
    jsii_struct_bases=[],
    name_mapping={
        "action_sub_type": "actionSubType",
        "instance_ids": "instanceIds",
        "region": "region",
    },
)
class BudgetsBudgetActionDefinitionSsmActionDefinition:
    def __init__(
        self,
        *,
        action_sub_type: builtins.str,
        instance_ids: typing.Sequence[builtins.str],
        region: builtins.str,
    ) -> None:
        '''
        :param action_sub_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_sub_type BudgetsBudgetAction#action_sub_type}.
        :param instance_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#instance_ids BudgetsBudgetAction#instance_ids}.
        :param region: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#region BudgetsBudgetAction#region}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action_sub_type": action_sub_type,
            "instance_ids": instance_ids,
            "region": region,
        }

    @builtins.property
    def action_sub_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#action_sub_type BudgetsBudgetAction#action_sub_type}.'''
        result = self._values.get("action_sub_type")
        assert result is not None, "Required property 'action_sub_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#instance_ids BudgetsBudgetAction#instance_ids}.'''
        result = self._values.get("instance_ids")
        assert result is not None, "Required property 'instance_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#region BudgetsBudgetAction#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetActionDefinitionSsmActionDefinition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetsBudgetActionDefinitionSsmActionDefinitionOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionDefinitionSsmActionDefinitionOutputReference",
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

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionSubTypeInput")
    def action_sub_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "actionSubTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIdsInput")
    def instance_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "instanceIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="actionSubType")
    def action_sub_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "actionSubType"))

    @action_sub_type.setter
    def action_sub_type(self, value: builtins.str) -> None:
        jsii.set(self, "actionSubType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceIds")
    def instance_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "instanceIds"))

    @instance_ids.setter
    def instance_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "instanceIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[BudgetsBudgetActionDefinitionSsmActionDefinition]:
        return typing.cast(typing.Optional[BudgetsBudgetActionDefinitionSsmActionDefinition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BudgetsBudgetActionDefinitionSsmActionDefinition],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetActionSubscriber",
    jsii_struct_bases=[],
    name_mapping={"address": "address", "subscription_type": "subscriptionType"},
)
class BudgetsBudgetActionSubscriber:
    def __init__(
        self,
        *,
        address: builtins.str,
        subscription_type: builtins.str,
    ) -> None:
        '''
        :param address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#address BudgetsBudgetAction#address}.
        :param subscription_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#subscription_type BudgetsBudgetAction#subscription_type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "address": address,
            "subscription_type": subscription_type,
        }

    @builtins.property
    def address(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#address BudgetsBudgetAction#address}.'''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subscription_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget_action#subscription_type BudgetsBudgetAction#subscription_type}.'''
        result = self._values.get("subscription_type")
        assert result is not None, "Required property 'subscription_type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetActionSubscriber(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "budget_type": "budgetType",
        "limit_amount": "limitAmount",
        "limit_unit": "limitUnit",
        "time_unit": "timeUnit",
        "account_id": "accountId",
        "cost_filter": "costFilter",
        "cost_filters": "costFilters",
        "cost_types": "costTypes",
        "name": "name",
        "name_prefix": "namePrefix",
        "notification": "notification",
        "time_period_end": "timePeriodEnd",
        "time_period_start": "timePeriodStart",
    },
)
class BudgetsBudgetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        budget_type: builtins.str,
        limit_amount: builtins.str,
        limit_unit: builtins.str,
        time_unit: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        cost_filter: typing.Optional[typing.Sequence["BudgetsBudgetCostFilter"]] = None,
        cost_filters: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        cost_types: typing.Optional["BudgetsBudgetCostTypes"] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        notification: typing.Optional[typing.Sequence["BudgetsBudgetNotification"]] = None,
        time_period_end: typing.Optional[builtins.str] = None,
        time_period_start: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Budgets.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param budget_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#budget_type BudgetsBudget#budget_type}.
        :param limit_amount: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#limit_amount BudgetsBudget#limit_amount}.
        :param limit_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#limit_unit BudgetsBudget#limit_unit}.
        :param time_unit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#time_unit BudgetsBudget#time_unit}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#account_id BudgetsBudget#account_id}.
        :param cost_filter: cost_filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#cost_filter BudgetsBudget#cost_filter}
        :param cost_filters: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#cost_filters BudgetsBudget#cost_filters}.
        :param cost_types: cost_types block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#cost_types BudgetsBudget#cost_types}
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#name BudgetsBudget#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#name_prefix BudgetsBudget#name_prefix}.
        :param notification: notification block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#notification BudgetsBudget#notification}
        :param time_period_end: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#time_period_end BudgetsBudget#time_period_end}.
        :param time_period_start: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#time_period_start BudgetsBudget#time_period_start}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cost_types, dict):
            cost_types = BudgetsBudgetCostTypes(**cost_types)
        self._values: typing.Dict[str, typing.Any] = {
            "budget_type": budget_type,
            "limit_amount": limit_amount,
            "limit_unit": limit_unit,
            "time_unit": time_unit,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if account_id is not None:
            self._values["account_id"] = account_id
        if cost_filter is not None:
            self._values["cost_filter"] = cost_filter
        if cost_filters is not None:
            self._values["cost_filters"] = cost_filters
        if cost_types is not None:
            self._values["cost_types"] = cost_types
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if notification is not None:
            self._values["notification"] = notification
        if time_period_end is not None:
            self._values["time_period_end"] = time_period_end
        if time_period_start is not None:
            self._values["time_period_start"] = time_period_start

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
    def budget_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#budget_type BudgetsBudget#budget_type}.'''
        result = self._values.get("budget_type")
        assert result is not None, "Required property 'budget_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def limit_amount(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#limit_amount BudgetsBudget#limit_amount}.'''
        result = self._values.get("limit_amount")
        assert result is not None, "Required property 'limit_amount' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def limit_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#limit_unit BudgetsBudget#limit_unit}.'''
        result = self._values.get("limit_unit")
        assert result is not None, "Required property 'limit_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def time_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#time_unit BudgetsBudget#time_unit}.'''
        result = self._values.get("time_unit")
        assert result is not None, "Required property 'time_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#account_id BudgetsBudget#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cost_filter(self) -> typing.Optional[typing.List["BudgetsBudgetCostFilter"]]:
        '''cost_filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#cost_filter BudgetsBudget#cost_filter}
        '''
        result = self._values.get("cost_filter")
        return typing.cast(typing.Optional[typing.List["BudgetsBudgetCostFilter"]], result)

    @builtins.property
    def cost_filters(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#cost_filters BudgetsBudget#cost_filters}.'''
        result = self._values.get("cost_filters")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def cost_types(self) -> typing.Optional["BudgetsBudgetCostTypes"]:
        '''cost_types block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#cost_types BudgetsBudget#cost_types}
        '''
        result = self._values.get("cost_types")
        return typing.cast(typing.Optional["BudgetsBudgetCostTypes"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#name BudgetsBudget#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#name_prefix BudgetsBudget#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notification(self) -> typing.Optional[typing.List["BudgetsBudgetNotification"]]:
        '''notification block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#notification BudgetsBudget#notification}
        '''
        result = self._values.get("notification")
        return typing.cast(typing.Optional[typing.List["BudgetsBudgetNotification"]], result)

    @builtins.property
    def time_period_end(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#time_period_end BudgetsBudget#time_period_end}.'''
        result = self._values.get("time_period_end")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def time_period_start(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#time_period_start BudgetsBudget#time_period_start}.'''
        result = self._values.get("time_period_start")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetCostFilter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "values": "values"},
)
class BudgetsBudgetCostFilter:
    def __init__(
        self,
        *,
        name: builtins.str,
        values: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#name BudgetsBudget#name}.
        :param values: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#values BudgetsBudget#values}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "values": values,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#name BudgetsBudget#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def values(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#values BudgetsBudget#values}.'''
        result = self._values.get("values")
        assert result is not None, "Required property 'values' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetCostFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetCostTypes",
    jsii_struct_bases=[],
    name_mapping={
        "include_credit": "includeCredit",
        "include_discount": "includeDiscount",
        "include_other_subscription": "includeOtherSubscription",
        "include_recurring": "includeRecurring",
        "include_refund": "includeRefund",
        "include_subscription": "includeSubscription",
        "include_support": "includeSupport",
        "include_tax": "includeTax",
        "include_upfront": "includeUpfront",
        "use_amortized": "useAmortized",
        "use_blended": "useBlended",
    },
)
class BudgetsBudgetCostTypes:
    def __init__(
        self,
        *,
        include_credit: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_discount: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_other_subscription: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_recurring: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_refund: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_subscription: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_support: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_tax: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        include_upfront: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        use_amortized: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        use_blended: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param include_credit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_credit BudgetsBudget#include_credit}.
        :param include_discount: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_discount BudgetsBudget#include_discount}.
        :param include_other_subscription: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_other_subscription BudgetsBudget#include_other_subscription}.
        :param include_recurring: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_recurring BudgetsBudget#include_recurring}.
        :param include_refund: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_refund BudgetsBudget#include_refund}.
        :param include_subscription: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_subscription BudgetsBudget#include_subscription}.
        :param include_support: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_support BudgetsBudget#include_support}.
        :param include_tax: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_tax BudgetsBudget#include_tax}.
        :param include_upfront: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_upfront BudgetsBudget#include_upfront}.
        :param use_amortized: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#use_amortized BudgetsBudget#use_amortized}.
        :param use_blended: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#use_blended BudgetsBudget#use_blended}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if include_credit is not None:
            self._values["include_credit"] = include_credit
        if include_discount is not None:
            self._values["include_discount"] = include_discount
        if include_other_subscription is not None:
            self._values["include_other_subscription"] = include_other_subscription
        if include_recurring is not None:
            self._values["include_recurring"] = include_recurring
        if include_refund is not None:
            self._values["include_refund"] = include_refund
        if include_subscription is not None:
            self._values["include_subscription"] = include_subscription
        if include_support is not None:
            self._values["include_support"] = include_support
        if include_tax is not None:
            self._values["include_tax"] = include_tax
        if include_upfront is not None:
            self._values["include_upfront"] = include_upfront
        if use_amortized is not None:
            self._values["use_amortized"] = use_amortized
        if use_blended is not None:
            self._values["use_blended"] = use_blended

    @builtins.property
    def include_credit(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_credit BudgetsBudget#include_credit}.'''
        result = self._values.get("include_credit")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_discount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_discount BudgetsBudget#include_discount}.'''
        result = self._values.get("include_discount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_other_subscription(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_other_subscription BudgetsBudget#include_other_subscription}.'''
        result = self._values.get("include_other_subscription")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_recurring(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_recurring BudgetsBudget#include_recurring}.'''
        result = self._values.get("include_recurring")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_refund(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_refund BudgetsBudget#include_refund}.'''
        result = self._values.get("include_refund")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_subscription(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_subscription BudgetsBudget#include_subscription}.'''
        result = self._values.get("include_subscription")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_support(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_support BudgetsBudget#include_support}.'''
        result = self._values.get("include_support")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_tax(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_tax BudgetsBudget#include_tax}.'''
        result = self._values.get("include_tax")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def include_upfront(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#include_upfront BudgetsBudget#include_upfront}.'''
        result = self._values.get("include_upfront")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def use_amortized(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#use_amortized BudgetsBudget#use_amortized}.'''
        result = self._values.get("use_amortized")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def use_blended(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#use_blended BudgetsBudget#use_blended}.'''
        result = self._values.get("use_blended")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetCostTypes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BudgetsBudgetCostTypesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetCostTypesOutputReference",
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

    @jsii.member(jsii_name="resetIncludeCredit")
    def reset_include_credit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeCredit", []))

    @jsii.member(jsii_name="resetIncludeDiscount")
    def reset_include_discount(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeDiscount", []))

    @jsii.member(jsii_name="resetIncludeOtherSubscription")
    def reset_include_other_subscription(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeOtherSubscription", []))

    @jsii.member(jsii_name="resetIncludeRecurring")
    def reset_include_recurring(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeRecurring", []))

    @jsii.member(jsii_name="resetIncludeRefund")
    def reset_include_refund(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeRefund", []))

    @jsii.member(jsii_name="resetIncludeSubscription")
    def reset_include_subscription(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeSubscription", []))

    @jsii.member(jsii_name="resetIncludeSupport")
    def reset_include_support(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeSupport", []))

    @jsii.member(jsii_name="resetIncludeTax")
    def reset_include_tax(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeTax", []))

    @jsii.member(jsii_name="resetIncludeUpfront")
    def reset_include_upfront(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeUpfront", []))

    @jsii.member(jsii_name="resetUseAmortized")
    def reset_use_amortized(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseAmortized", []))

    @jsii.member(jsii_name="resetUseBlended")
    def reset_use_blended(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseBlended", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeCreditInput")
    def include_credit_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeCreditInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeDiscountInput")
    def include_discount_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeDiscountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeOtherSubscriptionInput")
    def include_other_subscription_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeOtherSubscriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeRecurringInput")
    def include_recurring_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeRecurringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeRefundInput")
    def include_refund_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeRefundInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeSubscriptionInput")
    def include_subscription_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeSubscriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeSupportInput")
    def include_support_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeSupportInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTaxInput")
    def include_tax_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeTaxInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeUpfrontInput")
    def include_upfront_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeUpfrontInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useAmortizedInput")
    def use_amortized_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useAmortizedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useBlendedInput")
    def use_blended_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "useBlendedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeCredit")
    def include_credit(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeCredit"))

    @include_credit.setter
    def include_credit(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeCredit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeDiscount")
    def include_discount(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeDiscount"))

    @include_discount.setter
    def include_discount(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeDiscount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeOtherSubscription")
    def include_other_subscription(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeOtherSubscription"))

    @include_other_subscription.setter
    def include_other_subscription(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeOtherSubscription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeRecurring")
    def include_recurring(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeRecurring"))

    @include_recurring.setter
    def include_recurring(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeRecurring", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeRefund")
    def include_refund(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeRefund"))

    @include_refund.setter
    def include_refund(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeRefund", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeSubscription")
    def include_subscription(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeSubscription"))

    @include_subscription.setter
    def include_subscription(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeSubscription", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeSupport")
    def include_support(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeSupport"))

    @include_support.setter
    def include_support(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeSupport", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeTax")
    def include_tax(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeTax"))

    @include_tax.setter
    def include_tax(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeTax", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeUpfront")
    def include_upfront(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeUpfront"))

    @include_upfront.setter
    def include_upfront(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeUpfront", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useAmortized")
    def use_amortized(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useAmortized"))

    @use_amortized.setter
    def use_amortized(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useAmortized", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="useBlended")
    def use_blended(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "useBlended"))

    @use_blended.setter
    def use_blended(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "useBlended", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BudgetsBudgetCostTypes]:
        return typing.cast(typing.Optional[BudgetsBudgetCostTypes], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[BudgetsBudgetCostTypes]) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.budgets.BudgetsBudgetNotification",
    jsii_struct_bases=[],
    name_mapping={
        "comparison_operator": "comparisonOperator",
        "notification_type": "notificationType",
        "threshold": "threshold",
        "threshold_type": "thresholdType",
        "subscriber_email_addresses": "subscriberEmailAddresses",
        "subscriber_sns_topic_arns": "subscriberSnsTopicArns",
    },
)
class BudgetsBudgetNotification:
    def __init__(
        self,
        *,
        comparison_operator: builtins.str,
        notification_type: builtins.str,
        threshold: jsii.Number,
        threshold_type: builtins.str,
        subscriber_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        subscriber_sns_topic_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param comparison_operator: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#comparison_operator BudgetsBudget#comparison_operator}.
        :param notification_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#notification_type BudgetsBudget#notification_type}.
        :param threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#threshold BudgetsBudget#threshold}.
        :param threshold_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#threshold_type BudgetsBudget#threshold_type}.
        :param subscriber_email_addresses: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#subscriber_email_addresses BudgetsBudget#subscriber_email_addresses}.
        :param subscriber_sns_topic_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#subscriber_sns_topic_arns BudgetsBudget#subscriber_sns_topic_arns}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "comparison_operator": comparison_operator,
            "notification_type": notification_type,
            "threshold": threshold,
            "threshold_type": threshold_type,
        }
        if subscriber_email_addresses is not None:
            self._values["subscriber_email_addresses"] = subscriber_email_addresses
        if subscriber_sns_topic_arns is not None:
            self._values["subscriber_sns_topic_arns"] = subscriber_sns_topic_arns

    @builtins.property
    def comparison_operator(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#comparison_operator BudgetsBudget#comparison_operator}.'''
        result = self._values.get("comparison_operator")
        assert result is not None, "Required property 'comparison_operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def notification_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#notification_type BudgetsBudget#notification_type}.'''
        result = self._values.get("notification_type")
        assert result is not None, "Required property 'notification_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def threshold(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#threshold BudgetsBudget#threshold}.'''
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def threshold_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#threshold_type BudgetsBudget#threshold_type}.'''
        result = self._values.get("threshold_type")
        assert result is not None, "Required property 'threshold_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subscriber_email_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#subscriber_email_addresses BudgetsBudget#subscriber_email_addresses}.'''
        result = self._values.get("subscriber_email_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def subscriber_sns_topic_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/budgets_budget#subscriber_sns_topic_arns BudgetsBudget#subscriber_sns_topic_arns}.'''
        result = self._values.get("subscriber_sns_topic_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetsBudgetNotification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BudgetsBudget",
    "BudgetsBudgetAction",
    "BudgetsBudgetActionActionThreshold",
    "BudgetsBudgetActionActionThresholdOutputReference",
    "BudgetsBudgetActionConfig",
    "BudgetsBudgetActionDefinition",
    "BudgetsBudgetActionDefinitionIamActionDefinition",
    "BudgetsBudgetActionDefinitionIamActionDefinitionOutputReference",
    "BudgetsBudgetActionDefinitionOutputReference",
    "BudgetsBudgetActionDefinitionScpActionDefinition",
    "BudgetsBudgetActionDefinitionScpActionDefinitionOutputReference",
    "BudgetsBudgetActionDefinitionSsmActionDefinition",
    "BudgetsBudgetActionDefinitionSsmActionDefinitionOutputReference",
    "BudgetsBudgetActionSubscriber",
    "BudgetsBudgetConfig",
    "BudgetsBudgetCostFilter",
    "BudgetsBudgetCostTypes",
    "BudgetsBudgetCostTypesOutputReference",
    "BudgetsBudgetNotification",
]

publication.publish()
