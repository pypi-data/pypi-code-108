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


class DataAwsSesActiveReceiptRuleSet(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.DataAwsSesActiveReceiptRuleSet",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/ses_active_receipt_rule_set aws_ses_active_receipt_rule_set}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/ses_active_receipt_rule_set aws_ses_active_receipt_rule_set} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsSesActiveReceiptRuleSetConfig(
            count=count, depends_on=depends_on, lifecycle=lifecycle, provider=provider
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleSetName")
    def rule_set_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleSetName"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.DataAwsSesActiveReceiptRuleSetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
    },
)
class DataAwsSesActiveReceiptRuleSetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
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

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSesActiveReceiptRuleSetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsSesDomainIdentity(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.DataAwsSesDomainIdentity",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/ses_domain_identity aws_ses_domain_identity}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/ses_domain_identity aws_ses_domain_identity} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/ses_domain_identity#domain DataAwsSesDomainIdentity#domain}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsSesDomainIdentityConfig(
            domain=domain,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verificationToken")
    def verification_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "verificationToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.DataAwsSesDomainIdentityConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
    },
)
class DataAwsSesDomainIdentityConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/ses_domain_identity#domain DataAwsSesDomainIdentity#domain}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
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
    def domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/ses_domain_identity#domain DataAwsSesDomainIdentity#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSesDomainIdentityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsSesEmailIdentity(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.DataAwsSesEmailIdentity",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/ses_email_identity aws_ses_email_identity}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        email: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/ses_email_identity aws_ses_email_identity} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/ses_email_identity#email DataAwsSesEmailIdentity#email}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsSesEmailIdentityConfig(
            email=email,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        jsii.set(self, "email", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.DataAwsSesEmailIdentityConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "email": "email",
    },
)
class DataAwsSesEmailIdentityConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        email: builtins.str,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/ses_email_identity#email DataAwsSesEmailIdentity#email}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
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
    def email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/ses_email_identity#email DataAwsSesEmailIdentity#email}.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsSesEmailIdentityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesActiveReceiptRuleSet(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesActiveReceiptRuleSet",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_active_receipt_rule_set aws_ses_active_receipt_rule_set}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        rule_set_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_active_receipt_rule_set aws_ses_active_receipt_rule_set} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param rule_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_active_receipt_rule_set#rule_set_name SesActiveReceiptRuleSet#rule_set_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesActiveReceiptRuleSetConfig(
            rule_set_name=rule_set_name,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleSetNameInput")
    def rule_set_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleSetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleSetName")
    def rule_set_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleSetName"))

    @rule_set_name.setter
    def rule_set_name(self, value: builtins.str) -> None:
        jsii.set(self, "ruleSetName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesActiveReceiptRuleSetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "rule_set_name": "ruleSetName",
    },
)
class SesActiveReceiptRuleSetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        rule_set_name: builtins.str,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param rule_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_active_receipt_rule_set#rule_set_name SesActiveReceiptRuleSet#rule_set_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "rule_set_name": rule_set_name,
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
    def rule_set_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_active_receipt_rule_set#rule_set_name SesActiveReceiptRuleSet#rule_set_name}.'''
        result = self._values.get("rule_set_name")
        assert result is not None, "Required property 'rule_set_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesActiveReceiptRuleSetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesConfigurationSet(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesConfigurationSet",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set aws_ses_configuration_set}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        delivery_options: typing.Optional["SesConfigurationSetDeliveryOptions"] = None,
        reputation_metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sending_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set aws_ses_configuration_set} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#name SesConfigurationSet#name}.
        :param delivery_options: delivery_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#delivery_options SesConfigurationSet#delivery_options}
        :param reputation_metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#reputation_metrics_enabled SesConfigurationSet#reputation_metrics_enabled}.
        :param sending_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#sending_enabled SesConfigurationSet#sending_enabled}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesConfigurationSetConfig(
            name=name,
            delivery_options=delivery_options,
            reputation_metrics_enabled=reputation_metrics_enabled,
            sending_enabled=sending_enabled,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putDeliveryOptions")
    def put_delivery_options(
        self,
        *,
        tls_policy: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param tls_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#tls_policy SesConfigurationSet#tls_policy}.
        '''
        value = SesConfigurationSetDeliveryOptions(tls_policy=tls_policy)

        return typing.cast(None, jsii.invoke(self, "putDeliveryOptions", [value]))

    @jsii.member(jsii_name="resetDeliveryOptions")
    def reset_delivery_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryOptions", []))

    @jsii.member(jsii_name="resetReputationMetricsEnabled")
    def reset_reputation_metrics_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReputationMetricsEnabled", []))

    @jsii.member(jsii_name="resetSendingEnabled")
    def reset_sending_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSendingEnabled", []))

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
    @jsii.member(jsii_name="deliveryOptions")
    def delivery_options(self) -> "SesConfigurationSetDeliveryOptionsOutputReference":
        return typing.cast("SesConfigurationSetDeliveryOptionsOutputReference", jsii.get(self, "deliveryOptions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lastFreshStart")
    def last_fresh_start(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastFreshStart"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deliveryOptionsInput")
    def delivery_options_input(
        self,
    ) -> typing.Optional["SesConfigurationSetDeliveryOptions"]:
        return typing.cast(typing.Optional["SesConfigurationSetDeliveryOptions"], jsii.get(self, "deliveryOptionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reputationMetricsEnabledInput")
    def reputation_metrics_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "reputationMetricsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sendingEnabledInput")
    def sending_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "sendingEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="reputationMetricsEnabled")
    def reputation_metrics_enabled(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "reputationMetricsEnabled"))

    @reputation_metrics_enabled.setter
    def reputation_metrics_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "reputationMetricsEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sendingEnabled")
    def sending_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "sendingEnabled"))

    @sending_enabled.setter
    def sending_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "sendingEnabled", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesConfigurationSetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "delivery_options": "deliveryOptions",
        "reputation_metrics_enabled": "reputationMetricsEnabled",
        "sending_enabled": "sendingEnabled",
    },
)
class SesConfigurationSetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        delivery_options: typing.Optional["SesConfigurationSetDeliveryOptions"] = None,
        reputation_metrics_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sending_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#name SesConfigurationSet#name}.
        :param delivery_options: delivery_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#delivery_options SesConfigurationSet#delivery_options}
        :param reputation_metrics_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#reputation_metrics_enabled SesConfigurationSet#reputation_metrics_enabled}.
        :param sending_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#sending_enabled SesConfigurationSet#sending_enabled}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(delivery_options, dict):
            delivery_options = SesConfigurationSetDeliveryOptions(**delivery_options)
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
        if delivery_options is not None:
            self._values["delivery_options"] = delivery_options
        if reputation_metrics_enabled is not None:
            self._values["reputation_metrics_enabled"] = reputation_metrics_enabled
        if sending_enabled is not None:
            self._values["sending_enabled"] = sending_enabled

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#name SesConfigurationSet#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delivery_options(self) -> typing.Optional["SesConfigurationSetDeliveryOptions"]:
        '''delivery_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#delivery_options SesConfigurationSet#delivery_options}
        '''
        result = self._values.get("delivery_options")
        return typing.cast(typing.Optional["SesConfigurationSetDeliveryOptions"], result)

    @builtins.property
    def reputation_metrics_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#reputation_metrics_enabled SesConfigurationSet#reputation_metrics_enabled}.'''
        result = self._values.get("reputation_metrics_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def sending_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#sending_enabled SesConfigurationSet#sending_enabled}.'''
        result = self._values.get("sending_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesConfigurationSetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesConfigurationSetDeliveryOptions",
    jsii_struct_bases=[],
    name_mapping={"tls_policy": "tlsPolicy"},
)
class SesConfigurationSetDeliveryOptions:
    def __init__(self, *, tls_policy: typing.Optional[builtins.str] = None) -> None:
        '''
        :param tls_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#tls_policy SesConfigurationSet#tls_policy}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if tls_policy is not None:
            self._values["tls_policy"] = tls_policy

    @builtins.property
    def tls_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_configuration_set#tls_policy SesConfigurationSet#tls_policy}.'''
        result = self._values.get("tls_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesConfigurationSetDeliveryOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesConfigurationSetDeliveryOptionsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesConfigurationSetDeliveryOptionsOutputReference",
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

    @jsii.member(jsii_name="resetTlsPolicy")
    def reset_tls_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsPolicy", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsPolicyInput")
    def tls_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsPolicy")
    def tls_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsPolicy"))

    @tls_policy.setter
    def tls_policy(self, value: builtins.str) -> None:
        jsii.set(self, "tlsPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SesConfigurationSetDeliveryOptions]:
        return typing.cast(typing.Optional[SesConfigurationSetDeliveryOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SesConfigurationSetDeliveryOptions],
    ) -> None:
        jsii.set(self, "internalValue", value)


class SesDomainDkim(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesDomainDkim",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_dkim aws_ses_domain_dkim}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_dkim aws_ses_domain_dkim} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_dkim#domain SesDomainDkim#domain}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesDomainDkimConfig(
            domain=domain,
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
    @jsii.member(jsii_name="dkimTokens")
    def dkim_tokens(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dkimTokens"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesDomainDkimConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
    },
)
class SesDomainDkimConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_dkim#domain SesDomainDkim#domain}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
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
    def domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_dkim#domain SesDomainDkim#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesDomainDkimConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesDomainIdentity(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesDomainIdentity",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity aws_ses_domain_identity}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity aws_ses_domain_identity} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity#domain SesDomainIdentity#domain}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesDomainIdentityConfig(
            domain=domain,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verificationToken")
    def verification_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "verificationToken"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesDomainIdentityConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
    },
)
class SesDomainIdentityConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity#domain SesDomainIdentity#domain}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
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
    def domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity#domain SesDomainIdentity#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesDomainIdentityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesDomainIdentityVerification(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesDomainIdentityVerification",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification aws_ses_domain_identity_verification}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        timeouts: typing.Optional["SesDomainIdentityVerificationTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification aws_ses_domain_identity_verification} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification#domain SesDomainIdentityVerification#domain}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification#timeouts SesDomainIdentityVerification#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesDomainIdentityVerificationConfig(
            domain=domain,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification#create SesDomainIdentityVerification#create}.
        '''
        value = SesDomainIdentityVerificationTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "SesDomainIdentityVerificationTimeoutsOutputReference":
        return typing.cast("SesDomainIdentityVerificationTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional["SesDomainIdentityVerificationTimeouts"]:
        return typing.cast(typing.Optional["SesDomainIdentityVerificationTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesDomainIdentityVerificationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
        "timeouts": "timeouts",
    },
)
class SesDomainIdentityVerificationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
        timeouts: typing.Optional["SesDomainIdentityVerificationTimeouts"] = None,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification#domain SesDomainIdentityVerification#domain}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification#timeouts SesDomainIdentityVerification#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = SesDomainIdentityVerificationTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification#domain SesDomainIdentityVerification#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def timeouts(self) -> typing.Optional["SesDomainIdentityVerificationTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification#timeouts SesDomainIdentityVerification#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["SesDomainIdentityVerificationTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesDomainIdentityVerificationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesDomainIdentityVerificationTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class SesDomainIdentityVerificationTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification#create SesDomainIdentityVerification#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_identity_verification#create SesDomainIdentityVerification#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesDomainIdentityVerificationTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesDomainIdentityVerificationTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesDomainIdentityVerificationTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SesDomainIdentityVerificationTimeouts]:
        return typing.cast(typing.Optional[SesDomainIdentityVerificationTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SesDomainIdentityVerificationTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class SesDomainMailFrom(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesDomainMailFrom",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from aws_ses_domain_mail_from}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain: builtins.str,
        mail_from_domain: builtins.str,
        behavior_on_mx_failure: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from aws_ses_domain_mail_from} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from#domain SesDomainMailFrom#domain}.
        :param mail_from_domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from#mail_from_domain SesDomainMailFrom#mail_from_domain}.
        :param behavior_on_mx_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from#behavior_on_mx_failure SesDomainMailFrom#behavior_on_mx_failure}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesDomainMailFromConfig(
            domain=domain,
            mail_from_domain=mail_from_domain,
            behavior_on_mx_failure=behavior_on_mx_failure,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetBehaviorOnMxFailure")
    def reset_behavior_on_mx_failure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBehaviorOnMxFailure", []))

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
    @jsii.member(jsii_name="behaviorOnMxFailureInput")
    def behavior_on_mx_failure_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "behaviorOnMxFailureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainInput")
    def domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mailFromDomainInput")
    def mail_from_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mailFromDomainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="behaviorOnMxFailure")
    def behavior_on_mx_failure(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "behaviorOnMxFailure"))

    @behavior_on_mx_failure.setter
    def behavior_on_mx_failure(self, value: builtins.str) -> None:
        jsii.set(self, "behaviorOnMxFailure", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domain")
    def domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domain"))

    @domain.setter
    def domain(self, value: builtins.str) -> None:
        jsii.set(self, "domain", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mailFromDomain")
    def mail_from_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mailFromDomain"))

    @mail_from_domain.setter
    def mail_from_domain(self, value: builtins.str) -> None:
        jsii.set(self, "mailFromDomain", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesDomainMailFromConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain": "domain",
        "mail_from_domain": "mailFromDomain",
        "behavior_on_mx_failure": "behaviorOnMxFailure",
    },
)
class SesDomainMailFromConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain: builtins.str,
        mail_from_domain: builtins.str,
        behavior_on_mx_failure: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from#domain SesDomainMailFrom#domain}.
        :param mail_from_domain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from#mail_from_domain SesDomainMailFrom#mail_from_domain}.
        :param behavior_on_mx_failure: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from#behavior_on_mx_failure SesDomainMailFrom#behavior_on_mx_failure}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain": domain,
            "mail_from_domain": mail_from_domain,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if behavior_on_mx_failure is not None:
            self._values["behavior_on_mx_failure"] = behavior_on_mx_failure

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
    def domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from#domain SesDomainMailFrom#domain}.'''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mail_from_domain(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from#mail_from_domain SesDomainMailFrom#mail_from_domain}.'''
        result = self._values.get("mail_from_domain")
        assert result is not None, "Required property 'mail_from_domain' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def behavior_on_mx_failure(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_domain_mail_from#behavior_on_mx_failure SesDomainMailFrom#behavior_on_mx_failure}.'''
        result = self._values.get("behavior_on_mx_failure")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesDomainMailFromConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesEmailIdentity(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesEmailIdentity",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_email_identity aws_ses_email_identity}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        email: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_email_identity aws_ses_email_identity} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_email_identity#email SesEmailIdentity#email}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesEmailIdentityConfig(
            email=email,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailInput")
    def email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @email.setter
    def email(self, value: builtins.str) -> None:
        jsii.set(self, "email", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesEmailIdentityConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "email": "email",
    },
)
class SesEmailIdentityConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        email: builtins.str,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param email: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_email_identity#email SesEmailIdentity#email}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
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
    def email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_email_identity#email SesEmailIdentity#email}.'''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesEmailIdentityConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesEventDestination(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesEventDestination",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination aws_ses_event_destination}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        configuration_set_name: builtins.str,
        matching_types: typing.Sequence[builtins.str],
        name: builtins.str,
        cloudwatch_destination: typing.Optional[typing.Sequence["SesEventDestinationCloudwatchDestination"]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kinesis_destination: typing.Optional["SesEventDestinationKinesisDestination"] = None,
        sns_destination: typing.Optional["SesEventDestinationSnsDestination"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination aws_ses_event_destination} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param configuration_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#configuration_set_name SesEventDestination#configuration_set_name}.
        :param matching_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#matching_types SesEventDestination#matching_types}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#name SesEventDestination#name}.
        :param cloudwatch_destination: cloudwatch_destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#cloudwatch_destination SesEventDestination#cloudwatch_destination}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#enabled SesEventDestination#enabled}.
        :param kinesis_destination: kinesis_destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#kinesis_destination SesEventDestination#kinesis_destination}
        :param sns_destination: sns_destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#sns_destination SesEventDestination#sns_destination}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesEventDestinationConfig(
            configuration_set_name=configuration_set_name,
            matching_types=matching_types,
            name=name,
            cloudwatch_destination=cloudwatch_destination,
            enabled=enabled,
            kinesis_destination=kinesis_destination,
            sns_destination=sns_destination,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putKinesisDestination")
    def put_kinesis_destination(
        self,
        *,
        role_arn: builtins.str,
        stream_arn: builtins.str,
    ) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#role_arn SesEventDestination#role_arn}.
        :param stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#stream_arn SesEventDestination#stream_arn}.
        '''
        value = SesEventDestinationKinesisDestination(
            role_arn=role_arn, stream_arn=stream_arn
        )

        return typing.cast(None, jsii.invoke(self, "putKinesisDestination", [value]))

    @jsii.member(jsii_name="putSnsDestination")
    def put_sns_destination(self, *, topic_arn: builtins.str) -> None:
        '''
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#topic_arn SesEventDestination#topic_arn}.
        '''
        value = SesEventDestinationSnsDestination(topic_arn=topic_arn)

        return typing.cast(None, jsii.invoke(self, "putSnsDestination", [value]))

    @jsii.member(jsii_name="resetCloudwatchDestination")
    def reset_cloudwatch_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudwatchDestination", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetKinesisDestination")
    def reset_kinesis_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKinesisDestination", []))

    @jsii.member(jsii_name="resetSnsDestination")
    def reset_sns_destination(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnsDestination", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisDestination")
    def kinesis_destination(
        self,
    ) -> "SesEventDestinationKinesisDestinationOutputReference":
        return typing.cast("SesEventDestinationKinesisDestinationOutputReference", jsii.get(self, "kinesisDestination"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsDestination")
    def sns_destination(self) -> "SesEventDestinationSnsDestinationOutputReference":
        return typing.cast("SesEventDestinationSnsDestinationOutputReference", jsii.get(self, "snsDestination"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchDestinationInput")
    def cloudwatch_destination_input(
        self,
    ) -> typing.Optional[typing.List["SesEventDestinationCloudwatchDestination"]]:
        return typing.cast(typing.Optional[typing.List["SesEventDestinationCloudwatchDestination"]], jsii.get(self, "cloudwatchDestinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationSetNameInput")
    def configuration_set_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configurationSetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kinesisDestinationInput")
    def kinesis_destination_input(
        self,
    ) -> typing.Optional["SesEventDestinationKinesisDestination"]:
        return typing.cast(typing.Optional["SesEventDestinationKinesisDestination"], jsii.get(self, "kinesisDestinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchingTypesInput")
    def matching_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "matchingTypesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsDestinationInput")
    def sns_destination_input(
        self,
    ) -> typing.Optional["SesEventDestinationSnsDestination"]:
        return typing.cast(typing.Optional["SesEventDestinationSnsDestination"], jsii.get(self, "snsDestinationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cloudwatchDestination")
    def cloudwatch_destination(
        self,
    ) -> typing.List["SesEventDestinationCloudwatchDestination"]:
        return typing.cast(typing.List["SesEventDestinationCloudwatchDestination"], jsii.get(self, "cloudwatchDestination"))

    @cloudwatch_destination.setter
    def cloudwatch_destination(
        self,
        value: typing.List["SesEventDestinationCloudwatchDestination"],
    ) -> None:
        jsii.set(self, "cloudwatchDestination", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationSetName")
    def configuration_set_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configurationSetName"))

    @configuration_set_name.setter
    def configuration_set_name(self, value: builtins.str) -> None:
        jsii.set(self, "configurationSetName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="matchingTypes")
    def matching_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "matchingTypes"))

    @matching_types.setter
    def matching_types(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "matchingTypes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesEventDestinationCloudwatchDestination",
    jsii_struct_bases=[],
    name_mapping={
        "default_value": "defaultValue",
        "dimension_name": "dimensionName",
        "value_source": "valueSource",
    },
)
class SesEventDestinationCloudwatchDestination:
    def __init__(
        self,
        *,
        default_value: builtins.str,
        dimension_name: builtins.str,
        value_source: builtins.str,
    ) -> None:
        '''
        :param default_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#default_value SesEventDestination#default_value}.
        :param dimension_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#dimension_name SesEventDestination#dimension_name}.
        :param value_source: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#value_source SesEventDestination#value_source}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "default_value": default_value,
            "dimension_name": dimension_name,
            "value_source": value_source,
        }

    @builtins.property
    def default_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#default_value SesEventDestination#default_value}.'''
        result = self._values.get("default_value")
        assert result is not None, "Required property 'default_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dimension_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#dimension_name SesEventDestination#dimension_name}.'''
        result = self._values.get("dimension_name")
        assert result is not None, "Required property 'dimension_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value_source(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#value_source SesEventDestination#value_source}.'''
        result = self._values.get("value_source")
        assert result is not None, "Required property 'value_source' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesEventDestinationCloudwatchDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesEventDestinationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "configuration_set_name": "configurationSetName",
        "matching_types": "matchingTypes",
        "name": "name",
        "cloudwatch_destination": "cloudwatchDestination",
        "enabled": "enabled",
        "kinesis_destination": "kinesisDestination",
        "sns_destination": "snsDestination",
    },
)
class SesEventDestinationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        configuration_set_name: builtins.str,
        matching_types: typing.Sequence[builtins.str],
        name: builtins.str,
        cloudwatch_destination: typing.Optional[typing.Sequence[SesEventDestinationCloudwatchDestination]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        kinesis_destination: typing.Optional["SesEventDestinationKinesisDestination"] = None,
        sns_destination: typing.Optional["SesEventDestinationSnsDestination"] = None,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param configuration_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#configuration_set_name SesEventDestination#configuration_set_name}.
        :param matching_types: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#matching_types SesEventDestination#matching_types}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#name SesEventDestination#name}.
        :param cloudwatch_destination: cloudwatch_destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#cloudwatch_destination SesEventDestination#cloudwatch_destination}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#enabled SesEventDestination#enabled}.
        :param kinesis_destination: kinesis_destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#kinesis_destination SesEventDestination#kinesis_destination}
        :param sns_destination: sns_destination block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#sns_destination SesEventDestination#sns_destination}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(kinesis_destination, dict):
            kinesis_destination = SesEventDestinationKinesisDestination(**kinesis_destination)
        if isinstance(sns_destination, dict):
            sns_destination = SesEventDestinationSnsDestination(**sns_destination)
        self._values: typing.Dict[str, typing.Any] = {
            "configuration_set_name": configuration_set_name,
            "matching_types": matching_types,
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
        if cloudwatch_destination is not None:
            self._values["cloudwatch_destination"] = cloudwatch_destination
        if enabled is not None:
            self._values["enabled"] = enabled
        if kinesis_destination is not None:
            self._values["kinesis_destination"] = kinesis_destination
        if sns_destination is not None:
            self._values["sns_destination"] = sns_destination

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
    def configuration_set_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#configuration_set_name SesEventDestination#configuration_set_name}.'''
        result = self._values.get("configuration_set_name")
        assert result is not None, "Required property 'configuration_set_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def matching_types(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#matching_types SesEventDestination#matching_types}.'''
        result = self._values.get("matching_types")
        assert result is not None, "Required property 'matching_types' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#name SesEventDestination#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloudwatch_destination(
        self,
    ) -> typing.Optional[typing.List[SesEventDestinationCloudwatchDestination]]:
        '''cloudwatch_destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#cloudwatch_destination SesEventDestination#cloudwatch_destination}
        '''
        result = self._values.get("cloudwatch_destination")
        return typing.cast(typing.Optional[typing.List[SesEventDestinationCloudwatchDestination]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#enabled SesEventDestination#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def kinesis_destination(
        self,
    ) -> typing.Optional["SesEventDestinationKinesisDestination"]:
        '''kinesis_destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#kinesis_destination SesEventDestination#kinesis_destination}
        '''
        result = self._values.get("kinesis_destination")
        return typing.cast(typing.Optional["SesEventDestinationKinesisDestination"], result)

    @builtins.property
    def sns_destination(self) -> typing.Optional["SesEventDestinationSnsDestination"]:
        '''sns_destination block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#sns_destination SesEventDestination#sns_destination}
        '''
        result = self._values.get("sns_destination")
        return typing.cast(typing.Optional["SesEventDestinationSnsDestination"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesEventDestinationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesEventDestinationKinesisDestination",
    jsii_struct_bases=[],
    name_mapping={"role_arn": "roleArn", "stream_arn": "streamArn"},
)
class SesEventDestinationKinesisDestination:
    def __init__(self, *, role_arn: builtins.str, stream_arn: builtins.str) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#role_arn SesEventDestination#role_arn}.
        :param stream_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#stream_arn SesEventDestination#stream_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
            "stream_arn": stream_arn,
        }

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#role_arn SesEventDestination#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stream_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#stream_arn SesEventDestination#stream_arn}.'''
        result = self._values.get("stream_arn")
        assert result is not None, "Required property 'stream_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesEventDestinationKinesisDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesEventDestinationKinesisDestinationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesEventDestinationKinesisDestinationOutputReference",
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
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamArnInput")
    def stream_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streamArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streamArn")
    def stream_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streamArn"))

    @stream_arn.setter
    def stream_arn(self, value: builtins.str) -> None:
        jsii.set(self, "streamArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SesEventDestinationKinesisDestination]:
        return typing.cast(typing.Optional[SesEventDestinationKinesisDestination], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SesEventDestinationKinesisDestination],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesEventDestinationSnsDestination",
    jsii_struct_bases=[],
    name_mapping={"topic_arn": "topicArn"},
)
class SesEventDestinationSnsDestination:
    def __init__(self, *, topic_arn: builtins.str) -> None:
        '''
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#topic_arn SesEventDestination#topic_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "topic_arn": topic_arn,
        }

    @builtins.property
    def topic_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_event_destination#topic_arn SesEventDestination#topic_arn}.'''
        result = self._values.get("topic_arn")
        assert result is not None, "Required property 'topic_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesEventDestinationSnsDestination(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesEventDestinationSnsDestinationOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesEventDestinationSnsDestinationOutputReference",
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
    @jsii.member(jsii_name="topicArnInput")
    def topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topicArn"))

    @topic_arn.setter
    def topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "topicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SesEventDestinationSnsDestination]:
        return typing.cast(typing.Optional[SesEventDestinationSnsDestination], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[SesEventDestinationSnsDestination],
    ) -> None:
        jsii.set(self, "internalValue", value)


class SesIdentityNotificationTopic(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesIdentityNotificationTopic",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic aws_ses_identity_notification_topic}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identity: builtins.str,
        notification_type: builtins.str,
        include_original_headers: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        topic_arn: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic aws_ses_identity_notification_topic} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#identity SesIdentityNotificationTopic#identity}.
        :param notification_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#notification_type SesIdentityNotificationTopic#notification_type}.
        :param include_original_headers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#include_original_headers SesIdentityNotificationTopic#include_original_headers}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#topic_arn SesIdentityNotificationTopic#topic_arn}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesIdentityNotificationTopicConfig(
            identity=identity,
            notification_type=notification_type,
            include_original_headers=include_original_headers,
            topic_arn=topic_arn,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetIncludeOriginalHeaders")
    def reset_include_original_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeOriginalHeaders", []))

    @jsii.member(jsii_name="resetTopicArn")
    def reset_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopicArn", []))

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
    @jsii.member(jsii_name="identityInput")
    def identity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeOriginalHeadersInput")
    def include_original_headers_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "includeOriginalHeadersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationTypeInput")
    def notification_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notificationTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicArnInput")
    def topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "topicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identity")
    def identity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identity"))

    @identity.setter
    def identity(self, value: builtins.str) -> None:
        jsii.set(self, "identity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="includeOriginalHeaders")
    def include_original_headers(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "includeOriginalHeaders"))

    @include_original_headers.setter
    def include_original_headers(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "includeOriginalHeaders", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notificationType")
    def notification_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notificationType"))

    @notification_type.setter
    def notification_type(self, value: builtins.str) -> None:
        jsii.set(self, "notificationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topicArn"))

    @topic_arn.setter
    def topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "topicArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesIdentityNotificationTopicConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "identity": "identity",
        "notification_type": "notificationType",
        "include_original_headers": "includeOriginalHeaders",
        "topic_arn": "topicArn",
    },
)
class SesIdentityNotificationTopicConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        identity: builtins.str,
        notification_type: builtins.str,
        include_original_headers: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param identity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#identity SesIdentityNotificationTopic#identity}.
        :param notification_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#notification_type SesIdentityNotificationTopic#notification_type}.
        :param include_original_headers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#include_original_headers SesIdentityNotificationTopic#include_original_headers}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#topic_arn SesIdentityNotificationTopic#topic_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "identity": identity,
            "notification_type": notification_type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if include_original_headers is not None:
            self._values["include_original_headers"] = include_original_headers
        if topic_arn is not None:
            self._values["topic_arn"] = topic_arn

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
    def identity(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#identity SesIdentityNotificationTopic#identity}.'''
        result = self._values.get("identity")
        assert result is not None, "Required property 'identity' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def notification_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#notification_type SesIdentityNotificationTopic#notification_type}.'''
        result = self._values.get("notification_type")
        assert result is not None, "Required property 'notification_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def include_original_headers(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#include_original_headers SesIdentityNotificationTopic#include_original_headers}.'''
        result = self._values.get("include_original_headers")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_notification_topic#topic_arn SesIdentityNotificationTopic#topic_arn}.'''
        result = self._values.get("topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesIdentityNotificationTopicConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesIdentityPolicy(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesIdentityPolicy",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy aws_ses_identity_policy}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identity: builtins.str,
        name: builtins.str,
        policy: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy aws_ses_identity_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy#identity SesIdentityPolicy#identity}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy#name SesIdentityPolicy#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy#policy SesIdentityPolicy#policy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesIdentityPolicyConfig(
            identity=identity,
            name=name,
            policy=policy,
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
    @jsii.member(jsii_name="identityInput")
    def identity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identity")
    def identity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identity"))

    @identity.setter
    def identity(self, value: builtins.str) -> None:
        jsii.set(self, "identity", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesIdentityPolicyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "identity": "identity",
        "name": "name",
        "policy": "policy",
    },
)
class SesIdentityPolicyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        identity: builtins.str,
        name: builtins.str,
        policy: builtins.str,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param identity: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy#identity SesIdentityPolicy#identity}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy#name SesIdentityPolicy#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy#policy SesIdentityPolicy#policy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "identity": identity,
            "name": name,
            "policy": policy,
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
    def identity(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy#identity SesIdentityPolicy#identity}.'''
        result = self._values.get("identity")
        assert result is not None, "Required property 'identity' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy#name SesIdentityPolicy#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_identity_policy#policy SesIdentityPolicy#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesIdentityPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesReceiptFilter(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesReceiptFilter",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter aws_ses_receipt_filter}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cidr: builtins.str,
        name: builtins.str,
        policy: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter aws_ses_receipt_filter} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter#cidr SesReceiptFilter#cidr}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter#name SesReceiptFilter#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter#policy SesReceiptFilter#policy}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesReceiptFilterConfig(
            cidr=cidr,
            name=name,
            policy=policy,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cidrInput")
    def cidr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cidrInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cidr")
    def cidr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cidr"))

    @cidr.setter
    def cidr(self, value: builtins.str) -> None:
        jsii.set(self, "cidr", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policy")
    def policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policy"))

    @policy.setter
    def policy(self, value: builtins.str) -> None:
        jsii.set(self, "policy", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptFilterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cidr": "cidr",
        "name": "name",
        "policy": "policy",
    },
)
class SesReceiptFilterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cidr: builtins.str,
        name: builtins.str,
        policy: builtins.str,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cidr: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter#cidr SesReceiptFilter#cidr}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter#name SesReceiptFilter#name}.
        :param policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter#policy SesReceiptFilter#policy}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "cidr": cidr,
            "name": name,
            "policy": policy,
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
    def cidr(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter#cidr SesReceiptFilter#cidr}.'''
        result = self._values.get("cidr")
        assert result is not None, "Required property 'cidr' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter#name SesReceiptFilter#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_filter#policy SesReceiptFilter#policy}.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptFilterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesReceiptRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule aws_ses_receipt_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        rule_set_name: builtins.str,
        add_header_action: typing.Optional[typing.Sequence["SesReceiptRuleAddHeaderAction"]] = None,
        after: typing.Optional[builtins.str] = None,
        bounce_action: typing.Optional[typing.Sequence["SesReceiptRuleBounceAction"]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        lambda_action: typing.Optional[typing.Sequence["SesReceiptRuleLambdaAction"]] = None,
        recipients: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_action: typing.Optional[typing.Sequence["SesReceiptRuleS3Action"]] = None,
        scan_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sns_action: typing.Optional[typing.Sequence["SesReceiptRuleSnsAction"]] = None,
        stop_action: typing.Optional[typing.Sequence["SesReceiptRuleStopAction"]] = None,
        tls_policy: typing.Optional[builtins.str] = None,
        workmail_action: typing.Optional[typing.Sequence["SesReceiptRuleWorkmailAction"]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule aws_ses_receipt_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#name SesReceiptRule#name}.
        :param rule_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#rule_set_name SesReceiptRule#rule_set_name}.
        :param add_header_action: add_header_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#add_header_action SesReceiptRule#add_header_action}
        :param after: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#after SesReceiptRule#after}.
        :param bounce_action: bounce_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#bounce_action SesReceiptRule#bounce_action}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#enabled SesReceiptRule#enabled}.
        :param lambda_action: lambda_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#lambda_action SesReceiptRule#lambda_action}
        :param recipients: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#recipients SesReceiptRule#recipients}.
        :param s3_action: s3_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#s3_action SesReceiptRule#s3_action}
        :param scan_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#scan_enabled SesReceiptRule#scan_enabled}.
        :param sns_action: sns_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#sns_action SesReceiptRule#sns_action}
        :param stop_action: stop_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#stop_action SesReceiptRule#stop_action}
        :param tls_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#tls_policy SesReceiptRule#tls_policy}.
        :param workmail_action: workmail_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#workmail_action SesReceiptRule#workmail_action}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesReceiptRuleConfig(
            name=name,
            rule_set_name=rule_set_name,
            add_header_action=add_header_action,
            after=after,
            bounce_action=bounce_action,
            enabled=enabled,
            lambda_action=lambda_action,
            recipients=recipients,
            s3_action=s3_action,
            scan_enabled=scan_enabled,
            sns_action=sns_action,
            stop_action=stop_action,
            tls_policy=tls_policy,
            workmail_action=workmail_action,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAddHeaderAction")
    def reset_add_header_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddHeaderAction", []))

    @jsii.member(jsii_name="resetAfter")
    def reset_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAfter", []))

    @jsii.member(jsii_name="resetBounceAction")
    def reset_bounce_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBounceAction", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetLambdaAction")
    def reset_lambda_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLambdaAction", []))

    @jsii.member(jsii_name="resetRecipients")
    def reset_recipients(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecipients", []))

    @jsii.member(jsii_name="resetS3Action")
    def reset_s3_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3Action", []))

    @jsii.member(jsii_name="resetScanEnabled")
    def reset_scan_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScanEnabled", []))

    @jsii.member(jsii_name="resetSnsAction")
    def reset_sns_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnsAction", []))

    @jsii.member(jsii_name="resetStopAction")
    def reset_stop_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStopAction", []))

    @jsii.member(jsii_name="resetTlsPolicy")
    def reset_tls_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsPolicy", []))

    @jsii.member(jsii_name="resetWorkmailAction")
    def reset_workmail_action(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkmailAction", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addHeaderActionInput")
    def add_header_action_input(
        self,
    ) -> typing.Optional[typing.List["SesReceiptRuleAddHeaderAction"]]:
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleAddHeaderAction"]], jsii.get(self, "addHeaderActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="afterInput")
    def after_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "afterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bounceActionInput")
    def bounce_action_input(
        self,
    ) -> typing.Optional[typing.List["SesReceiptRuleBounceAction"]]:
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleBounceAction"]], jsii.get(self, "bounceActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaActionInput")
    def lambda_action_input(
        self,
    ) -> typing.Optional[typing.List["SesReceiptRuleLambdaAction"]]:
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleLambdaAction"]], jsii.get(self, "lambdaActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recipientsInput")
    def recipients_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "recipientsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleSetNameInput")
    def rule_set_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleSetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ActionInput")
    def s3_action_input(self) -> typing.Optional[typing.List["SesReceiptRuleS3Action"]]:
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleS3Action"]], jsii.get(self, "s3ActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scanEnabledInput")
    def scan_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "scanEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsActionInput")
    def sns_action_input(
        self,
    ) -> typing.Optional[typing.List["SesReceiptRuleSnsAction"]]:
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleSnsAction"]], jsii.get(self, "snsActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stopActionInput")
    def stop_action_input(
        self,
    ) -> typing.Optional[typing.List["SesReceiptRuleStopAction"]]:
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleStopAction"]], jsii.get(self, "stopActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsPolicyInput")
    def tls_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsPolicyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workmailActionInput")
    def workmail_action_input(
        self,
    ) -> typing.Optional[typing.List["SesReceiptRuleWorkmailAction"]]:
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleWorkmailAction"]], jsii.get(self, "workmailActionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="addHeaderAction")
    def add_header_action(self) -> typing.List["SesReceiptRuleAddHeaderAction"]:
        return typing.cast(typing.List["SesReceiptRuleAddHeaderAction"], jsii.get(self, "addHeaderAction"))

    @add_header_action.setter
    def add_header_action(
        self,
        value: typing.List["SesReceiptRuleAddHeaderAction"],
    ) -> None:
        jsii.set(self, "addHeaderAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="after")
    def after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "after"))

    @after.setter
    def after(self, value: builtins.str) -> None:
        jsii.set(self, "after", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bounceAction")
    def bounce_action(self) -> typing.List["SesReceiptRuleBounceAction"]:
        return typing.cast(typing.List["SesReceiptRuleBounceAction"], jsii.get(self, "bounceAction"))

    @bounce_action.setter
    def bounce_action(self, value: typing.List["SesReceiptRuleBounceAction"]) -> None:
        jsii.set(self, "bounceAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: typing.Union[builtins.bool, cdktf.IResolvable]) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaAction")
    def lambda_action(self) -> typing.List["SesReceiptRuleLambdaAction"]:
        return typing.cast(typing.List["SesReceiptRuleLambdaAction"], jsii.get(self, "lambdaAction"))

    @lambda_action.setter
    def lambda_action(self, value: typing.List["SesReceiptRuleLambdaAction"]) -> None:
        jsii.set(self, "lambdaAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="recipients")
    def recipients(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "recipients"))

    @recipients.setter
    def recipients(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "recipients", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleSetName")
    def rule_set_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleSetName"))

    @rule_set_name.setter
    def rule_set_name(self, value: builtins.str) -> None:
        jsii.set(self, "ruleSetName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3Action")
    def s3_action(self) -> typing.List["SesReceiptRuleS3Action"]:
        return typing.cast(typing.List["SesReceiptRuleS3Action"], jsii.get(self, "s3Action"))

    @s3_action.setter
    def s3_action(self, value: typing.List["SesReceiptRuleS3Action"]) -> None:
        jsii.set(self, "s3Action", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scanEnabled")
    def scan_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "scanEnabled"))

    @scan_enabled.setter
    def scan_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "scanEnabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsAction")
    def sns_action(self) -> typing.List["SesReceiptRuleSnsAction"]:
        return typing.cast(typing.List["SesReceiptRuleSnsAction"], jsii.get(self, "snsAction"))

    @sns_action.setter
    def sns_action(self, value: typing.List["SesReceiptRuleSnsAction"]) -> None:
        jsii.set(self, "snsAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stopAction")
    def stop_action(self) -> typing.List["SesReceiptRuleStopAction"]:
        return typing.cast(typing.List["SesReceiptRuleStopAction"], jsii.get(self, "stopAction"))

    @stop_action.setter
    def stop_action(self, value: typing.List["SesReceiptRuleStopAction"]) -> None:
        jsii.set(self, "stopAction", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsPolicy")
    def tls_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsPolicy"))

    @tls_policy.setter
    def tls_policy(self, value: builtins.str) -> None:
        jsii.set(self, "tlsPolicy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workmailAction")
    def workmail_action(self) -> typing.List["SesReceiptRuleWorkmailAction"]:
        return typing.cast(typing.List["SesReceiptRuleWorkmailAction"], jsii.get(self, "workmailAction"))

    @workmail_action.setter
    def workmail_action(
        self,
        value: typing.List["SesReceiptRuleWorkmailAction"],
    ) -> None:
        jsii.set(self, "workmailAction", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleAddHeaderAction",
    jsii_struct_bases=[],
    name_mapping={
        "header_name": "headerName",
        "header_value": "headerValue",
        "position": "position",
    },
)
class SesReceiptRuleAddHeaderAction:
    def __init__(
        self,
        *,
        header_name: builtins.str,
        header_value: builtins.str,
        position: jsii.Number,
    ) -> None:
        '''
        :param header_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#header_name SesReceiptRule#header_name}.
        :param header_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#header_value SesReceiptRule#header_value}.
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "header_name": header_name,
            "header_value": header_value,
            "position": position,
        }

    @builtins.property
    def header_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#header_name SesReceiptRule#header_name}.'''
        result = self._values.get("header_name")
        assert result is not None, "Required property 'header_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def header_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#header_value SesReceiptRule#header_value}.'''
        result = self._values.get("header_value")
        assert result is not None, "Required property 'header_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def position(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.'''
        result = self._values.get("position")
        assert result is not None, "Required property 'position' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptRuleAddHeaderAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleBounceAction",
    jsii_struct_bases=[],
    name_mapping={
        "message": "message",
        "position": "position",
        "sender": "sender",
        "smtp_reply_code": "smtpReplyCode",
        "status_code": "statusCode",
        "topic_arn": "topicArn",
    },
)
class SesReceiptRuleBounceAction:
    def __init__(
        self,
        *,
        message: builtins.str,
        position: jsii.Number,
        sender: builtins.str,
        smtp_reply_code: builtins.str,
        status_code: typing.Optional[builtins.str] = None,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param message: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#message SesReceiptRule#message}.
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.
        :param sender: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#sender SesReceiptRule#sender}.
        :param smtp_reply_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#smtp_reply_code SesReceiptRule#smtp_reply_code}.
        :param status_code: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#status_code SesReceiptRule#status_code}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "message": message,
            "position": position,
            "sender": sender,
            "smtp_reply_code": smtp_reply_code,
        }
        if status_code is not None:
            self._values["status_code"] = status_code
        if topic_arn is not None:
            self._values["topic_arn"] = topic_arn

    @builtins.property
    def message(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#message SesReceiptRule#message}.'''
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def position(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.'''
        result = self._values.get("position")
        assert result is not None, "Required property 'position' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def sender(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#sender SesReceiptRule#sender}.'''
        result = self._values.get("sender")
        assert result is not None, "Required property 'sender' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def smtp_reply_code(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#smtp_reply_code SesReceiptRule#smtp_reply_code}.'''
        result = self._values.get("smtp_reply_code")
        assert result is not None, "Required property 'smtp_reply_code' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def status_code(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#status_code SesReceiptRule#status_code}.'''
        result = self._values.get("status_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.'''
        result = self._values.get("topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptRuleBounceAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "rule_set_name": "ruleSetName",
        "add_header_action": "addHeaderAction",
        "after": "after",
        "bounce_action": "bounceAction",
        "enabled": "enabled",
        "lambda_action": "lambdaAction",
        "recipients": "recipients",
        "s3_action": "s3Action",
        "scan_enabled": "scanEnabled",
        "sns_action": "snsAction",
        "stop_action": "stopAction",
        "tls_policy": "tlsPolicy",
        "workmail_action": "workmailAction",
    },
)
class SesReceiptRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        rule_set_name: builtins.str,
        add_header_action: typing.Optional[typing.Sequence[SesReceiptRuleAddHeaderAction]] = None,
        after: typing.Optional[builtins.str] = None,
        bounce_action: typing.Optional[typing.Sequence[SesReceiptRuleBounceAction]] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        lambda_action: typing.Optional[typing.Sequence["SesReceiptRuleLambdaAction"]] = None,
        recipients: typing.Optional[typing.Sequence[builtins.str]] = None,
        s3_action: typing.Optional[typing.Sequence["SesReceiptRuleS3Action"]] = None,
        scan_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        sns_action: typing.Optional[typing.Sequence["SesReceiptRuleSnsAction"]] = None,
        stop_action: typing.Optional[typing.Sequence["SesReceiptRuleStopAction"]] = None,
        tls_policy: typing.Optional[builtins.str] = None,
        workmail_action: typing.Optional[typing.Sequence["SesReceiptRuleWorkmailAction"]] = None,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#name SesReceiptRule#name}.
        :param rule_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#rule_set_name SesReceiptRule#rule_set_name}.
        :param add_header_action: add_header_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#add_header_action SesReceiptRule#add_header_action}
        :param after: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#after SesReceiptRule#after}.
        :param bounce_action: bounce_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#bounce_action SesReceiptRule#bounce_action}
        :param enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#enabled SesReceiptRule#enabled}.
        :param lambda_action: lambda_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#lambda_action SesReceiptRule#lambda_action}
        :param recipients: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#recipients SesReceiptRule#recipients}.
        :param s3_action: s3_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#s3_action SesReceiptRule#s3_action}
        :param scan_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#scan_enabled SesReceiptRule#scan_enabled}.
        :param sns_action: sns_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#sns_action SesReceiptRule#sns_action}
        :param stop_action: stop_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#stop_action SesReceiptRule#stop_action}
        :param tls_policy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#tls_policy SesReceiptRule#tls_policy}.
        :param workmail_action: workmail_action block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#workmail_action SesReceiptRule#workmail_action}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "rule_set_name": rule_set_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if add_header_action is not None:
            self._values["add_header_action"] = add_header_action
        if after is not None:
            self._values["after"] = after
        if bounce_action is not None:
            self._values["bounce_action"] = bounce_action
        if enabled is not None:
            self._values["enabled"] = enabled
        if lambda_action is not None:
            self._values["lambda_action"] = lambda_action
        if recipients is not None:
            self._values["recipients"] = recipients
        if s3_action is not None:
            self._values["s3_action"] = s3_action
        if scan_enabled is not None:
            self._values["scan_enabled"] = scan_enabled
        if sns_action is not None:
            self._values["sns_action"] = sns_action
        if stop_action is not None:
            self._values["stop_action"] = stop_action
        if tls_policy is not None:
            self._values["tls_policy"] = tls_policy
        if workmail_action is not None:
            self._values["workmail_action"] = workmail_action

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#name SesReceiptRule#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_set_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#rule_set_name SesReceiptRule#rule_set_name}.'''
        result = self._values.get("rule_set_name")
        assert result is not None, "Required property 'rule_set_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def add_header_action(
        self,
    ) -> typing.Optional[typing.List[SesReceiptRuleAddHeaderAction]]:
        '''add_header_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#add_header_action SesReceiptRule#add_header_action}
        '''
        result = self._values.get("add_header_action")
        return typing.cast(typing.Optional[typing.List[SesReceiptRuleAddHeaderAction]], result)

    @builtins.property
    def after(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#after SesReceiptRule#after}.'''
        result = self._values.get("after")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bounce_action(self) -> typing.Optional[typing.List[SesReceiptRuleBounceAction]]:
        '''bounce_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#bounce_action SesReceiptRule#bounce_action}
        '''
        result = self._values.get("bounce_action")
        return typing.cast(typing.Optional[typing.List[SesReceiptRuleBounceAction]], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#enabled SesReceiptRule#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def lambda_action(
        self,
    ) -> typing.Optional[typing.List["SesReceiptRuleLambdaAction"]]:
        '''lambda_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#lambda_action SesReceiptRule#lambda_action}
        '''
        result = self._values.get("lambda_action")
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleLambdaAction"]], result)

    @builtins.property
    def recipients(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#recipients SesReceiptRule#recipients}.'''
        result = self._values.get("recipients")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def s3_action(self) -> typing.Optional[typing.List["SesReceiptRuleS3Action"]]:
        '''s3_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#s3_action SesReceiptRule#s3_action}
        '''
        result = self._values.get("s3_action")
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleS3Action"]], result)

    @builtins.property
    def scan_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#scan_enabled SesReceiptRule#scan_enabled}.'''
        result = self._values.get("scan_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def sns_action(self) -> typing.Optional[typing.List["SesReceiptRuleSnsAction"]]:
        '''sns_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#sns_action SesReceiptRule#sns_action}
        '''
        result = self._values.get("sns_action")
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleSnsAction"]], result)

    @builtins.property
    def stop_action(self) -> typing.Optional[typing.List["SesReceiptRuleStopAction"]]:
        '''stop_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#stop_action SesReceiptRule#stop_action}
        '''
        result = self._values.get("stop_action")
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleStopAction"]], result)

    @builtins.property
    def tls_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#tls_policy SesReceiptRule#tls_policy}.'''
        result = self._values.get("tls_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workmail_action(
        self,
    ) -> typing.Optional[typing.List["SesReceiptRuleWorkmailAction"]]:
        '''workmail_action block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#workmail_action SesReceiptRule#workmail_action}
        '''
        result = self._values.get("workmail_action")
        return typing.cast(typing.Optional[typing.List["SesReceiptRuleWorkmailAction"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleLambdaAction",
    jsii_struct_bases=[],
    name_mapping={
        "function_arn": "functionArn",
        "position": "position",
        "invocation_type": "invocationType",
        "topic_arn": "topicArn",
    },
)
class SesReceiptRuleLambdaAction:
    def __init__(
        self,
        *,
        function_arn: builtins.str,
        position: jsii.Number,
        invocation_type: typing.Optional[builtins.str] = None,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param function_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#function_arn SesReceiptRule#function_arn}.
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.
        :param invocation_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#invocation_type SesReceiptRule#invocation_type}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function_arn": function_arn,
            "position": position,
        }
        if invocation_type is not None:
            self._values["invocation_type"] = invocation_type
        if topic_arn is not None:
            self._values["topic_arn"] = topic_arn

    @builtins.property
    def function_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#function_arn SesReceiptRule#function_arn}.'''
        result = self._values.get("function_arn")
        assert result is not None, "Required property 'function_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def position(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.'''
        result = self._values.get("position")
        assert result is not None, "Required property 'position' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def invocation_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#invocation_type SesReceiptRule#invocation_type}.'''
        result = self._values.get("invocation_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.'''
        result = self._values.get("topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptRuleLambdaAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleS3Action",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "position": "position",
        "kms_key_arn": "kmsKeyArn",
        "object_key_prefix": "objectKeyPrefix",
        "topic_arn": "topicArn",
    },
)
class SesReceiptRuleS3Action:
    def __init__(
        self,
        *,
        bucket_name: builtins.str,
        position: jsii.Number,
        kms_key_arn: typing.Optional[builtins.str] = None,
        object_key_prefix: typing.Optional[builtins.str] = None,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#bucket_name SesReceiptRule#bucket_name}.
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#kms_key_arn SesReceiptRule#kms_key_arn}.
        :param object_key_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#object_key_prefix SesReceiptRule#object_key_prefix}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "bucket_name": bucket_name,
            "position": position,
        }
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if object_key_prefix is not None:
            self._values["object_key_prefix"] = object_key_prefix
        if topic_arn is not None:
            self._values["topic_arn"] = topic_arn

    @builtins.property
    def bucket_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#bucket_name SesReceiptRule#bucket_name}.'''
        result = self._values.get("bucket_name")
        assert result is not None, "Required property 'bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def position(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.'''
        result = self._values.get("position")
        assert result is not None, "Required property 'position' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#kms_key_arn SesReceiptRule#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def object_key_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#object_key_prefix SesReceiptRule#object_key_prefix}.'''
        result = self._values.get("object_key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.'''
        result = self._values.get("topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptRuleS3Action(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesReceiptRuleSet(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleSet",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule_set aws_ses_receipt_rule_set}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        rule_set_name: builtins.str,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule_set aws_ses_receipt_rule_set} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param rule_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule_set#rule_set_name SesReceiptRuleSet#rule_set_name}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesReceiptRuleSetConfig(
            rule_set_name=rule_set_name,
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
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleSetNameInput")
    def rule_set_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleSetNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleSetName")
    def rule_set_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleSetName"))

    @rule_set_name.setter
    def rule_set_name(self, value: builtins.str) -> None:
        jsii.set(self, "ruleSetName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleSetConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "rule_set_name": "ruleSetName",
    },
)
class SesReceiptRuleSetConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        rule_set_name: builtins.str,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param rule_set_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule_set#rule_set_name SesReceiptRuleSet#rule_set_name}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "rule_set_name": rule_set_name,
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
    def rule_set_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule_set#rule_set_name SesReceiptRuleSet#rule_set_name}.'''
        result = self._values.get("rule_set_name")
        assert result is not None, "Required property 'rule_set_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptRuleSetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleSnsAction",
    jsii_struct_bases=[],
    name_mapping={
        "position": "position",
        "topic_arn": "topicArn",
        "encoding": "encoding",
    },
)
class SesReceiptRuleSnsAction:
    def __init__(
        self,
        *,
        position: jsii.Number,
        topic_arn: builtins.str,
        encoding: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.
        :param encoding: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#encoding SesReceiptRule#encoding}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "position": position,
            "topic_arn": topic_arn,
        }
        if encoding is not None:
            self._values["encoding"] = encoding

    @builtins.property
    def position(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.'''
        result = self._values.get("position")
        assert result is not None, "Required property 'position' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def topic_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.'''
        result = self._values.get("topic_arn")
        assert result is not None, "Required property 'topic_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encoding(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#encoding SesReceiptRule#encoding}.'''
        result = self._values.get("encoding")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptRuleSnsAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleStopAction",
    jsii_struct_bases=[],
    name_mapping={"position": "position", "scope": "scope", "topic_arn": "topicArn"},
)
class SesReceiptRuleStopAction:
    def __init__(
        self,
        *,
        position: jsii.Number,
        scope: builtins.str,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.
        :param scope: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#scope SesReceiptRule#scope}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "position": position,
            "scope": scope,
        }
        if topic_arn is not None:
            self._values["topic_arn"] = topic_arn

    @builtins.property
    def position(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.'''
        result = self._values.get("position")
        assert result is not None, "Required property 'position' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def scope(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#scope SesReceiptRule#scope}.'''
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.'''
        result = self._values.get("topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptRuleStopAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesReceiptRuleWorkmailAction",
    jsii_struct_bases=[],
    name_mapping={
        "organization_arn": "organizationArn",
        "position": "position",
        "topic_arn": "topicArn",
    },
)
class SesReceiptRuleWorkmailAction:
    def __init__(
        self,
        *,
        organization_arn: builtins.str,
        position: jsii.Number,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param organization_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#organization_arn SesReceiptRule#organization_arn}.
        :param position: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.
        :param topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "organization_arn": organization_arn,
            "position": position,
        }
        if topic_arn is not None:
            self._values["topic_arn"] = topic_arn

    @builtins.property
    def organization_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#organization_arn SesReceiptRule#organization_arn}.'''
        result = self._values.get("organization_arn")
        assert result is not None, "Required property 'organization_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def position(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#position SesReceiptRule#position}.'''
        result = self._values.get("position")
        assert result is not None, "Required property 'position' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_receipt_rule#topic_arn SesReceiptRule#topic_arn}.'''
        result = self._values.get("topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesReceiptRuleWorkmailAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SesTemplate(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.ses.SesTemplate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/ses_template aws_ses_template}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        html: typing.Optional[builtins.str] = None,
        subject: typing.Optional[builtins.str] = None,
        text: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/ses_template aws_ses_template} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#name SesTemplate#name}.
        :param html: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#html SesTemplate#html}.
        :param subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#subject SesTemplate#subject}.
        :param text: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#text SesTemplate#text}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SesTemplateConfig(
            name=name,
            html=html,
            subject=subject,
            text=text,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetHtml")
    def reset_html(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHtml", []))

    @jsii.member(jsii_name="resetSubject")
    def reset_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubject", []))

    @jsii.member(jsii_name="resetText")
    def reset_text(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetText", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="htmlInput")
    def html_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "htmlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subjectInput")
    def subject_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="textInput")
    def text_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "textInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="html")
    def html(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "html"))

    @html.setter
    def html(self, value: builtins.str) -> None:
        jsii.set(self, "html", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subject"))

    @subject.setter
    def subject(self, value: builtins.str) -> None:
        jsii.set(self, "subject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="text")
    def text(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "text"))

    @text.setter
    def text(self, value: builtins.str) -> None:
        jsii.set(self, "text", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.ses.SesTemplateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "html": "html",
        "subject": "subject",
        "text": "text",
    },
)
class SesTemplateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        html: typing.Optional[builtins.str] = None,
        subject: typing.Optional[builtins.str] = None,
        text: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Simple Email Service.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#name SesTemplate#name}.
        :param html: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#html SesTemplate#html}.
        :param subject: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#subject SesTemplate#subject}.
        :param text: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#text SesTemplate#text}.
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
        if html is not None:
            self._values["html"] = html
        if subject is not None:
            self._values["subject"] = subject
        if text is not None:
            self._values["text"] = text

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
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#name SesTemplate#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def html(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#html SesTemplate#html}.'''
        result = self._values.get("html")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subject(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#subject SesTemplate#subject}.'''
        result = self._values.get("subject")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def text(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/ses_template#text SesTemplate#text}.'''
        result = self._values.get("text")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesTemplateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAwsSesActiveReceiptRuleSet",
    "DataAwsSesActiveReceiptRuleSetConfig",
    "DataAwsSesDomainIdentity",
    "DataAwsSesDomainIdentityConfig",
    "DataAwsSesEmailIdentity",
    "DataAwsSesEmailIdentityConfig",
    "SesActiveReceiptRuleSet",
    "SesActiveReceiptRuleSetConfig",
    "SesConfigurationSet",
    "SesConfigurationSetConfig",
    "SesConfigurationSetDeliveryOptions",
    "SesConfigurationSetDeliveryOptionsOutputReference",
    "SesDomainDkim",
    "SesDomainDkimConfig",
    "SesDomainIdentity",
    "SesDomainIdentityConfig",
    "SesDomainIdentityVerification",
    "SesDomainIdentityVerificationConfig",
    "SesDomainIdentityVerificationTimeouts",
    "SesDomainIdentityVerificationTimeoutsOutputReference",
    "SesDomainMailFrom",
    "SesDomainMailFromConfig",
    "SesEmailIdentity",
    "SesEmailIdentityConfig",
    "SesEventDestination",
    "SesEventDestinationCloudwatchDestination",
    "SesEventDestinationConfig",
    "SesEventDestinationKinesisDestination",
    "SesEventDestinationKinesisDestinationOutputReference",
    "SesEventDestinationSnsDestination",
    "SesEventDestinationSnsDestinationOutputReference",
    "SesIdentityNotificationTopic",
    "SesIdentityNotificationTopicConfig",
    "SesIdentityPolicy",
    "SesIdentityPolicyConfig",
    "SesReceiptFilter",
    "SesReceiptFilterConfig",
    "SesReceiptRule",
    "SesReceiptRuleAddHeaderAction",
    "SesReceiptRuleBounceAction",
    "SesReceiptRuleConfig",
    "SesReceiptRuleLambdaAction",
    "SesReceiptRuleS3Action",
    "SesReceiptRuleSet",
    "SesReceiptRuleSetConfig",
    "SesReceiptRuleSnsAction",
    "SesReceiptRuleStopAction",
    "SesReceiptRuleWorkmailAction",
    "SesTemplate",
    "SesTemplateConfig",
]

publication.publish()
