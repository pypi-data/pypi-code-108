'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-organizations?style=flat-square)](https://github.com/pepperize/cdk-organizations/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-organizations?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-organizations)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-organizations?style=flat-square)](https://pypi.org/project/pepperize.cdk-organizations/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.Organizations?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.Organizations/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-organizations/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-organizations/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-organizations?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-organizations/releases)

# AWS Organizations

This project provides a CDK construct creating AWS organizations.

> Currently, there is no `@aws-cdk/aws-organizations` available. See this [Issue on AWS CDK](https://github.com/aws/aws-cdk/issues/2877).

* [AWS Account Management Reference Guide](https://docs.aws.amazon.com/accounts/latest/reference/accounts-welcome.html)
* [AWS Organizations User Guide](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)
* [AWS API Reference](https://docs.aws.amazon.com/organizations/latest/APIReference/Welcome.html)
* [AWS CDK Custom Resources](https://docs.aws.amazon.com/cdk/api/v1/docs/custom-resources-readme.html#custom-resources-for-aws-apis)

## API Reference

See [API.md](https://github.com/pepperize/cdk-organizations/blob/main/API.md)

## Install

### TypeScript

```shell
npm install @pepperize/cdk-organizations
```

or

```shell
yarn add @pepperize/cdk-organizations
```

### Python

```shell
pip install pepperize.cdk-organizations
```

### C# / .Net

```
dotnet add package Pepperize.CDK.Organizations
```

## Restrictions

* The stack can only be deployed in the `us-east-1` region.
* The stack's account must be the management account of an existing organization.
* The stack's account becomes the management account of the new organization.
* An account belongs only to one organization with a single root.

## Organization

To create a new organization or import an existing organization, add the following construct to your stack:

```python
const organization = new Organization(stack, "Organization", {
  featureSet: FeatureSet.ALL,
});
```

* The account which deploys the stack automatically becomes the management account of the new organization.
* If an organization already exists, it will be automatically imported. The account which deploys the stacks must be the management account.
* If the construct gets removed from the stack the organization still remains and must be manually deleted.
* For deletion of an organization you must previously remove all the member accounts, OUs, and policies from the organization.
* Currently, you can have only one root. AWS Organizations automatically creates it for you when you create the new organization.
* It can only be used from within the management account in the us-east-1 region.

## Organizational Unit (OU)

To create a new organizational unit (OU), add the following construct to your stack:

```python
const organizationUnit = new OrganizationalUnit(stack, "Organization", {
  organizationalUnitName: "Project2",
  parent: organisation.root,
});
```

To import an existing organizational unit (OU), add the following to your stack:

```python
const organizationUnit = OrganizationalUnit.fromOrganizationalUnitId(stack, "Organization", {
  organizationalUnitId: "ou-1234",
  organizationalUnitName: "Project2",
  parent: organisation.root,
});
```

* The parent of an organizational unit (OU) can be either the organization's root or another OU within the organization.
* An organizational unit (OU) can't be moved. You have to create a new one and move all the accounts.
* For deletion of an organizational unit (OU) you must first move all accounts out of the OU and any child OUs, and then you can delete the child OUs.
* It can only be used from within the management account in the us-east-1 region.

# Account

To create a new account, add the following construct to your stack:

```python
new Account(stack, "Account", {
  accountName: "MyAccount",
  email: "info@pepperize.com",
  iamUserAccessToBilling: IamUserAccessToBilling.ALLOW,
  parent: organization.root,
});
```

To import an existing organizational unit (OU), add the following to your stack:

```python
Account.fromAccountId(stack, "ImportedAccount", {
  accountId: "123456789012",
  parent: organization.root,
});
```

* The email address must not already be associated with another AWS account. You may suffix the email address, i.e. `info+account-123456789012@pepperize.com`.
* An account will be created and then moved to the parent, if the parent is an organizational unit (OU).
* It can only be used from within the management account in the us-east-1 region.
* An account can't be deleted easily, if the construct gets removed from the stack the account still remains. [Closing an AWS account](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_close.html)

# Contributing

Contributions of all kinds are welcome :rocket: Check out our [contributor's guide](https://github.com/pepperize/cdk-organizations/blob/main/CONTRIBUTING.md).

For a quick start, check out a development environment:

```shell
git clone git@github.com:pepperize/cdk-organizations
cd cdk-organizations
 # install dependencies
yarn
# build with projen
yarn build
```

# Example

See [example.ts](./src/example/example.ts)

```python
import { App, Stack } from "aws-cdk-lib/core";
import {
  Account,
  DelegatedAdministrator,
  EnableAwsServiceAccess,
  EnablePolicyType,
  FeatureSet,
  IamUserAccessToBilling,
  Organization,
  OrganizationalUnit,
  Policy,
  PolicyAttachment,
  PolicyType,
} from "@pepperize/cdk-organizations";

const app = new App();
const stack = new Stack(app);

// Create an organization
const organization = new Organization(stack, "Organization", {
  featureSet: FeatureSet.ALL,
});
// Enable AWS Service Access (requires FeatureSet: ALL)
new EnableAwsServiceAccess(stack, "EnableAwsServiceAccess", {
  servicePrincipal: "service-abbreviation.amazonaws.com",
});

// Create an account
const account = new Account(stack, "SharedAccount", {
  accountName: "SharedAccount",
  email: "info+shared-account@pepperize.com",
  roleName: "OrganizationAccountAccessRole",
  iamUserAccessToBilling: IamUserAccessToBilling.ALLOW,
  parent: organization.root,
});
// Enable a delegated admin account
new DelegatedAdministrator(stack, "DelegatedAdministrator", {
  account: account,
  servicePrincipal: "service-abbreviation.amazonaws.com",
});

// Create an OU in the current organizations root
const projects = new OrganizationalUnit(stack, "ProjectsOU", {
  organizationalUnitName: "Projects",
  parent: organization.root,
});
new Account(stack, "Project1Account", {
  accountName: "SharedAccount",
  email: "info+project1@pepperize.com",
  parent: projects,
});

// Create a nested OU and attach two accounts
const project2 = new OrganizationalUnit(stack, "Project2OU", {
  organizationalUnitName: "Project2",
  parent: projects,
});
new Account(stack, "Project2DevAccount", {
  accountName: "Project 2 Dev",
  email: "info+project2-dev@pepperize.com",
  parent: project2,
});
new Account(stack, "Project2ProdAccount", {
  accountName: "Project 2 Prod",
  email: "info+project2-prod@pepperize.com",
  parent: project2,
});

// Enable the service control policy (SCP) type within the organization
new EnablePolicyType(stack, "EnablePolicyType", {
  root: organization.root,
  policyType: PolicyType.SERVICE_CONTROL_POLICY,
});
// Create and attach and Service Control Policy (SCP)
const policy = new Policy(stack, "Policy", {
  content: '{\\"Version\\":\\"2012-10-17\\",\\"Statement\\":{\\"Effect\\":\\"Allow\\",\\"Action\\":\\"s3:*\\"}}',
  description: "Enables admins of attached accounts to delegate all S3 permissions",
  policyName: "AllowAllS3Actions",
  policyType: PolicyType.SERVICE_CONTROL_POLICY,
});
new PolicyAttachment(stack, "PolicyAttachment", {
  target: organization.root,
  policy: policy,
});
```

# Alternatives

* [AWS Bootstrap Kit](https://github.com/awslabs/aws-bootstrap-kit)
* [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
* [AWS Deployment Framework (ADF)](https://github.com/awslabs/aws-deployment-framework)
* [AWS Organization Formation](https://github.com/org-formation)
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

import aws_cdk
import constructs


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.AccountAttributes",
    jsii_struct_bases=[],
    name_mapping={"account_id": "accountId", "parent": "parent"},
)
class AccountAttributes:
    def __init__(self, *, account_id: builtins.str, parent: "IParent") -> None:
        '''
        :param account_id: 
        :param parent: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_id": account_id,
            "parent": parent,
        }

    @builtins.property
    def account_id(self) -> builtins.str:
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent(self) -> "IParent":
        result = self._values.get("parent")
        assert result is not None, "Required property 'parent' is missing"
        return typing.cast("IParent", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.AccountProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_name": "accountName",
        "email": "email",
        "iam_user_access_to_billing": "iamUserAccessToBilling",
        "parent": "parent",
        "role_name": "roleName",
    },
)
class AccountProps:
    def __init__(
        self,
        *,
        account_name: builtins.str,
        email: builtins.str,
        iam_user_access_to_billing: typing.Optional["IamUserAccessToBilling"] = None,
        parent: typing.Optional["IParent"] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_name: The friendly name of the member account.
        :param email: The email address of the owner to assign to the new member account. This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        :param iam_user_access_to_billing: If set to ALLOW , the new account enables IAM users to access account billing information if they have the required permissions. If set to DENY , only the root user of the new account can access account billing information. Default: ALLOW
        :param parent: The parent root or OU that you want to create the new Account in.
        :param role_name: The name of an IAM role that AWS Organizations automatically preconfigures in the new member account. This role trusts the management account, allowing users in the management account to assume the role, as permitted by the management account administrator. The role has administrator permissions in the new member account. If you don't specify this parameter, the role name defaults to OrganizationAccountAccessRole.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_name": account_name,
            "email": email,
        }
        if iam_user_access_to_billing is not None:
            self._values["iam_user_access_to_billing"] = iam_user_access_to_billing
        if parent is not None:
            self._values["parent"] = parent
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def account_name(self) -> builtins.str:
        '''The friendly name of the member account.'''
        result = self._values.get("account_name")
        assert result is not None, "Required property 'account_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email(self) -> builtins.str:
        '''The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iam_user_access_to_billing(self) -> typing.Optional["IamUserAccessToBilling"]:
        '''If set to ALLOW , the new account enables IAM users to access account billing information if they have the required permissions.

        If set to DENY , only the root user of the new account can access account billing information.

        :default: ALLOW
        '''
        result = self._values.get("iam_user_access_to_billing")
        return typing.cast(typing.Optional["IamUserAccessToBilling"], result)

    @builtins.property
    def parent(self) -> typing.Optional["IParent"]:
        '''The parent root or OU that you want to create the new Account in.'''
        result = self._values.get("parent")
        return typing.cast(typing.Optional["IParent"], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''The name of an IAM role that AWS Organizations automatically preconfigures in the new member account.

        This role trusts the management account, allowing users in the management account to assume the role, as permitted by the management account administrator. The role has administrator permissions in the new member account.

        If you don't specify this parameter, the role name defaults to OrganizationAccountAccessRole.
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DelegatedAdministrator(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.DelegatedAdministrator",
):
    '''Enables the specified member account to administer the Organizations features of the specified AWS service.

    It grants read-only access to AWS Organizations service data. The account still requires IAM permissions to access and administer the AWS service.

    You can run this action only for AWS services that support this feature. For a current list of services that support it, see the column Supports Delegated Administrator in the table at AWS Services that you can use with AWS Organizations in the `AWS Organizations User Guide <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html>`_.

    :see: https://docs.aws.amazon.com/accounts/latest/reference/using-orgs-delegated-admin.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account: "IAccount",
        service_principal: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: The member account in the organization to register as a delegated administrator.
        :param service_principal: The service principal of the AWS service for which you want to make the member account a delegated administrator.
        '''
        props = DelegatedAdministratorProps(
            account=account, service_principal=service_principal
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.DelegatedAdministratorProps",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "service_principal": "servicePrincipal"},
)
class DelegatedAdministratorProps:
    def __init__(self, *, account: "IAccount", service_principal: builtins.str) -> None:
        '''
        :param account: The member account in the organization to register as a delegated administrator.
        :param service_principal: The service principal of the AWS service for which you want to make the member account a delegated administrator.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "service_principal": service_principal,
        }

    @builtins.property
    def account(self) -> "IAccount":
        '''The member account in the organization to register as a delegated administrator.'''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast("IAccount", result)

    @builtins.property
    def service_principal(self) -> builtins.str:
        '''The service principal of the AWS service for which you want to make the member account a delegated administrator.'''
        result = self._values.get("service_principal")
        assert result is not None, "Required property 'service_principal' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DelegatedAdministratorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EnableAwsServiceAccess(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.EnableAwsServiceAccess",
):
    '''Enables the integration of an AWS service (the service that is specified by ServicePrincipal) with AWS Organizations.

    When you enable integration, you allow the specified service to create a service-linked role in all the accounts in your organization. This allows the service to perform operations on your behalf in your organization and its accounts.

    This operation can be called only from the organization's management account and only if the organization has enabled all features.

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services.html#orgs_trusted_access_perms
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        service_principal: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param service_principal: The service principal name of the AWS service for which you want to enable integration with your organization. This is typically in the form of a URL, such as service-abbreviation.amazonaws.com.
        '''
        props = EnableAwsServiceAccessProps(service_principal=service_principal)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.EnableAwsServiceAccessProps",
    jsii_struct_bases=[],
    name_mapping={"service_principal": "servicePrincipal"},
)
class EnableAwsServiceAccessProps:
    def __init__(self, *, service_principal: builtins.str) -> None:
        '''
        :param service_principal: The service principal name of the AWS service for which you want to enable integration with your organization. This is typically in the form of a URL, such as service-abbreviation.amazonaws.com.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "service_principal": service_principal,
        }

    @builtins.property
    def service_principal(self) -> builtins.str:
        '''The service principal name of the AWS service for which you want to enable integration with your organization.

        This is typically in the form of a URL, such as service-abbreviation.amazonaws.com.
        '''
        result = self._values.get("service_principal")
        assert result is not None, "Required property 'service_principal' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnableAwsServiceAccessProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EnablePolicyType(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.EnablePolicyType",
):
    '''Enables and disables Enables a policy type in a root.

    After you enable a policy type in a root, you can attach policies of that type to the root, any organizational unit (OU), or account in that root.

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_enable-disable.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy_type: "PolicyType",
        root: "Root",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param policy_type: 
        :param root: 
        '''
        props = EnablePolicyTypeProps(policy_type=policy_type, root=root)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.EnablePolicyTypeProps",
    jsii_struct_bases=[],
    name_mapping={"policy_type": "policyType", "root": "root"},
)
class EnablePolicyTypeProps:
    def __init__(self, *, policy_type: "PolicyType", root: "Root") -> None:
        '''
        :param policy_type: 
        :param root: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "policy_type": policy_type,
            "root": root,
        }

    @builtins.property
    def policy_type(self) -> "PolicyType":
        result = self._values.get("policy_type")
        assert result is not None, "Required property 'policy_type' is missing"
        return typing.cast("PolicyType", result)

    @builtins.property
    def root(self) -> "Root":
        result = self._values.get("root")
        assert result is not None, "Required property 'root' is missing"
        return typing.cast("Root", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnablePolicyTypeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@pepperize/cdk-organizations.FeatureSet")
class FeatureSet(enum.Enum):
    '''Specifies the feature set supported by the new organization.

    Each feature set supports different levels of functionality.

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html#feature-set
    '''

    CONSOLIDATED_BILLING = "CONSOLIDATED_BILLING"
    '''All member accounts have their bills consolidated to and paid by the management account.

    For more information, see `Consolidated billing <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html#feature-set-cb-only>`_ in the AWS Organizations User Guide. The consolidated billing feature subset isn’t available for organizations in the AWS GovCloud (US) Region.
    '''
    ALL = "ALL"
    '''In addition to all the features supported by the consolidated billing feature set, the management account can also apply any policy type to any member account in the organization.

    For more information, see `All features <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html#feature-set-all>`_ in the AWS Organizations User Guide.
    '''


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IAccount")
class IAccount(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''If the account was created successfully, the unique identifier (ID) of the new account.

        Exactly 12 digits.
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountName")
    def account_name(self) -> builtins.str:
        '''The friendly name of the account.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        '''The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        '''
        ...


class _IAccountProxy:
    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IAccount"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''If the account was created successfully, the unique identifier (ID) of the new account.

        Exactly 12 digits.
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountName")
    def account_name(self) -> builtins.str:
        '''The friendly name of the account.'''
        return typing.cast(builtins.str, jsii.get(self, "accountName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        '''The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        '''
        return typing.cast(builtins.str, jsii.get(self, "email"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAccount).__jsii_proxy_class__ = lambda : _IAccountProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IOrganization")
class IOrganization(typing_extensions.Protocol):
    '''Creates an organization to consolidate your AWS accounts so that you can administer them as a single unit.

    An organization has one management account along with zero or more member accounts. You can organize the accounts in a hierarchical, tree-like structure with a root at the top and organizational units nested under the root. Each account can be directly in the root, or placed in one of the OUs in the hierarchy. An organization has the functionality that is determined by the feature set that you enable.

    The account whose user is calling the CreateOrganization operation automatically becomes the management account of the new organization.

    For deletion of an organization you must previously remove all the member accounts, OUs, and policies from the organization!

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_create.html#create-org
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureSet")
    def feature_set(self) -> FeatureSet:
        '''Specifies the functionality that currently is available to the organization.

        If set to "ALL", then all features are enabled and policies can be applied to accounts in the organization. If set to "CONSOLIDATED_BILLING", then only consolidated billing functionality is available.
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountArn")
    def master_account_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the account that is designated as the management account for the organization.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountEmail")
    def master_account_email(self) -> builtins.str:
        '''The email address that is associated with the AWS account that is designated as the management account for the organization.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountId")
    def master_account_id(self) -> builtins.str:
        '''The unique identifier (ID) of the management account of an organization.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationArn")
    def organization_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of an organization.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''The unique identifier (ID) of an organization.

        The regex pattern for an organization ID string requires "o-" followed by from 10 to 32 lowercase letters or digits.
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="root")
    def root(self) -> "Root":
        '''The root of the current organization, which is automatically created.'''
        ...


class _IOrganizationProxy:
    '''Creates an organization to consolidate your AWS accounts so that you can administer them as a single unit.

    An organization has one management account along with zero or more member accounts. You can organize the accounts in a hierarchical, tree-like structure with a root at the top and organizational units nested under the root. Each account can be directly in the root, or placed in one of the OUs in the hierarchy. An organization has the functionality that is determined by the feature set that you enable.

    The account whose user is calling the CreateOrganization operation automatically becomes the management account of the new organization.

    For deletion of an organization you must previously remove all the member accounts, OUs, and policies from the organization!

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_create.html#create-org
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IOrganization"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureSet")
    def feature_set(self) -> FeatureSet:
        '''Specifies the functionality that currently is available to the organization.

        If set to "ALL", then all features are enabled and policies can be applied to accounts in the organization. If set to "CONSOLIDATED_BILLING", then only consolidated billing functionality is available.
        '''
        return typing.cast(FeatureSet, jsii.get(self, "featureSet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountArn")
    def master_account_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the account that is designated as the management account for the organization.'''
        return typing.cast(builtins.str, jsii.get(self, "masterAccountArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountEmail")
    def master_account_email(self) -> builtins.str:
        '''The email address that is associated with the AWS account that is designated as the management account for the organization.'''
        return typing.cast(builtins.str, jsii.get(self, "masterAccountEmail"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountId")
    def master_account_id(self) -> builtins.str:
        '''The unique identifier (ID) of the management account of an organization.'''
        return typing.cast(builtins.str, jsii.get(self, "masterAccountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationArn")
    def organization_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of an organization.'''
        return typing.cast(builtins.str, jsii.get(self, "organizationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''The unique identifier (ID) of an organization.

        The regex pattern for an organization ID string requires "o-" followed by from 10 to 32 lowercase letters or digits.
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="root")
    def root(self) -> "Root":
        '''The root of the current organization, which is automatically created.'''
        return typing.cast("Root", jsii.get(self, "root"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOrganization).__jsii_proxy_class__ = lambda : _IOrganizationProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IParent")
class IParent(constructs.IDependable, typing_extensions.Protocol):
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''The unique identifier (ID) of the parent root or OU that you want to create the new OU in.'''
        ...


class _IParentProxy(
    jsii.proxy_for(constructs.IDependable) # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IParent"

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''The unique identifier (ID) of the parent root or OU that you want to create the new OU in.'''
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IParent).__jsii_proxy_class__ = lambda : _IParentProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IPolicyAttachmentTarget")
class IPolicyAttachmentTarget(constructs.IDependable, typing_extensions.Protocol):
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        ...


class _IPolicyAttachmentTargetProxy(
    jsii.proxy_for(constructs.IDependable) # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IPolicyAttachmentTarget"

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPolicyAttachmentTarget).__jsii_proxy_class__ = lambda : _IPolicyAttachmentTargetProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.ITaggableResource")
class ITaggableResource(aws_cdk.ITaggable, typing_extensions.Protocol):
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''The unique identifier (ID) of the account, Organizational unit (OU), parent root or Policy (any type) that you want to tag.'''
        ...


class _ITaggableResourceProxy(
    jsii.proxy_for(aws_cdk.ITaggable) # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.ITaggableResource"

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''The unique identifier (ID) of the account, Organizational unit (OU), parent root or Policy (any type) that you want to tag.'''
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITaggableResource).__jsii_proxy_class__ = lambda : _ITaggableResourceProxy


@jsii.enum(jsii_type="@pepperize/cdk-organizations.IamUserAccessToBilling")
class IamUserAccessToBilling(enum.Enum):
    '''
    :see: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/control-access-billing.html#ControllingAccessWebsite-Activate
    '''

    ALLOW = "ALLOW"
    '''If set to ALLOW, the new account enables IAM users to access account billing information if they have the required permissions.'''
    DENY = "DENY"
    '''If set to DENY, only the root user of the new account can access account billing information.'''


@jsii.implements(IOrganization)
class Organization(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Organization",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        feature_set: typing.Optional[FeatureSet] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param feature_set: Enabling features in your organization. Default: ALL
        '''
        props = OrganizationProps(feature_set=feature_set)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureSet")
    def feature_set(self) -> FeatureSet:
        '''Specifies the functionality that currently is available to the organization.

        If set to "ALL", then all features are enabled and policies can be applied to accounts in the organization. If set to "CONSOLIDATED_BILLING", then only consolidated billing functionality is available.
        '''
        return typing.cast(FeatureSet, jsii.get(self, "featureSet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountArn")
    def master_account_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of the account that is designated as the management account for the organization.'''
        return typing.cast(builtins.str, jsii.get(self, "masterAccountArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountEmail")
    def master_account_email(self) -> builtins.str:
        '''The email address that is associated with the AWS account that is designated as the management account for the organization.'''
        return typing.cast(builtins.str, jsii.get(self, "masterAccountEmail"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="masterAccountId")
    def master_account_id(self) -> builtins.str:
        '''The unique identifier (ID) of the management account of an organization.'''
        return typing.cast(builtins.str, jsii.get(self, "masterAccountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationArn")
    def organization_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of an organization.'''
        return typing.cast(builtins.str, jsii.get(self, "organizationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''The unique identifier (ID) of an organization.

        The regex pattern for an organization ID string requires "o-" followed by from 10 to 32 lowercase letters or digits.
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="root")
    def root(self) -> "Root":
        '''The root of the current organization, which is automatically created.'''
        return typing.cast("Root", jsii.get(self, "root"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.OrganizationProps",
    jsii_struct_bases=[],
    name_mapping={"feature_set": "featureSet"},
)
class OrganizationProps:
    def __init__(self, *, feature_set: typing.Optional[FeatureSet] = None) -> None:
        '''
        :param feature_set: Enabling features in your organization. Default: ALL
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if feature_set is not None:
            self._values["feature_set"] = feature_set

    @builtins.property
    def feature_set(self) -> typing.Optional[FeatureSet]:
        '''Enabling features in your organization.

        :default: ALL

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_support-all-features.html
        '''
        result = self._values.get("feature_set")
        return typing.cast(typing.Optional[FeatureSet], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.OrganizationalUnitAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "organizational_unit_id": "organizationalUnitId",
        "organizational_unit_name": "organizationalUnitName",
        "parent": "parent",
    },
)
class OrganizationalUnitAttributes:
    def __init__(
        self,
        *,
        organizational_unit_id: builtins.str,
        organizational_unit_name: builtins.str,
        parent: IParent,
    ) -> None:
        '''
        :param organizational_unit_id: 
        :param organizational_unit_name: 
        :param parent: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "organizational_unit_id": organizational_unit_id,
            "organizational_unit_name": organizational_unit_name,
            "parent": parent,
        }

    @builtins.property
    def organizational_unit_id(self) -> builtins.str:
        result = self._values.get("organizational_unit_id")
        assert result is not None, "Required property 'organizational_unit_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def organizational_unit_name(self) -> builtins.str:
        result = self._values.get("organizational_unit_name")
        assert result is not None, "Required property 'organizational_unit_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent(self) -> IParent:
        result = self._values.get("parent")
        assert result is not None, "Required property 'parent' is missing"
        return typing.cast(IParent, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationalUnitAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.OrganizationalUnitProps",
    jsii_struct_bases=[],
    name_mapping={
        "organizational_unit_name": "organizationalUnitName",
        "parent": "parent",
    },
)
class OrganizationalUnitProps:
    def __init__(
        self,
        *,
        organizational_unit_name: builtins.str,
        parent: IParent,
    ) -> None:
        '''
        :param organizational_unit_name: The friendly name to assign to the new OU.
        :param parent: The parent root or OU that you want to create the new OrganizationalUnit in.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "organizational_unit_name": organizational_unit_name,
            "parent": parent,
        }

    @builtins.property
    def organizational_unit_name(self) -> builtins.str:
        '''The friendly name to assign to the new OU.'''
        result = self._values.get("organizational_unit_name")
        assert result is not None, "Required property 'organizational_unit_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent(self) -> IParent:
        '''The parent root or OU that you want to create the new OrganizationalUnit in.'''
        result = self._values.get("parent")
        assert result is not None, "Required property 'parent' is missing"
        return typing.cast(IParent, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationalUnitProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Policy(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Policy",
):
    '''Policies in AWS Organizations enable you to apply additional types of management to the AWS accounts in your organization.

    You can use policies when all features are enabled in your organization.

    Before you can create and attach a policy to your organization, you must enable that policy type for use.

    :see: FeatureSet
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        content: builtins.str,
        policy_name: builtins.str,
        policy_type: "PolicyType",
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param content: The policy text content to add to the new policy. The text that you supply must adhere to the rules of the policy type you specify in the Type parameter.
        :param policy_name: The friendly name to assign to the policy.
        :param policy_type: The type of policy to create. You can specify one of the following values:
        :param description: An optional description to assign to the policy.
        '''
        props = PolicyProps(
            content=content,
            policy_name=policy_name,
            policy_type=policy_type,
            description=description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        '''The unique identifier (ID) of the policy.

        The regex pattern for a policy ID string requires "p-" followed by from 8 to 128 lowercase or uppercase letters, digits, or the underscore character (_).
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyId"))


class PolicyAttachment(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.PolicyAttachment",
):
    '''Attaches a policy to a root, an organizational unit (OU), or an individual account.

    How the policy affects accounts depends on the type of policy. Refer to the AWS Organizations User Guide for information about each policy type:
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy: Policy,
        target: IPolicyAttachmentTarget,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param policy: The policy that you want to attach to the target.
        :param target: The root, OU, or account that you want to attach the policy to.
        '''
        props = PolicyAttachmentProps(policy=policy, target=target)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.PolicyAttachmentProps",
    jsii_struct_bases=[],
    name_mapping={"policy": "policy", "target": "target"},
)
class PolicyAttachmentProps:
    def __init__(self, *, policy: Policy, target: IPolicyAttachmentTarget) -> None:
        '''
        :param policy: The policy that you want to attach to the target.
        :param target: The root, OU, or account that you want to attach the policy to.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
            "target": target,
        }

    @builtins.property
    def policy(self) -> Policy:
        '''The policy that you want to attach to the target.'''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(Policy, result)

    @builtins.property
    def target(self) -> IPolicyAttachmentTarget:
        '''The root, OU, or account that you want to attach the policy to.'''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(IPolicyAttachmentTarget, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyAttachmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.PolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "policy_name": "policyName",
        "policy_type": "policyType",
        "description": "description",
    },
)
class PolicyProps:
    def __init__(
        self,
        *,
        content: builtins.str,
        policy_name: builtins.str,
        policy_type: "PolicyType",
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param content: The policy text content to add to the new policy. The text that you supply must adhere to the rules of the policy type you specify in the Type parameter.
        :param policy_name: The friendly name to assign to the policy.
        :param policy_type: The type of policy to create. You can specify one of the following values:
        :param description: An optional description to assign to the policy.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "policy_name": policy_name,
            "policy_type": policy_type,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def content(self) -> builtins.str:
        '''The policy text content to add to the new policy.

        The text that you supply must adhere to the rules of the policy type you specify in the Type parameter.
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''The friendly name to assign to the policy.'''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_type(self) -> "PolicyType":
        '''The type of policy to create.

        You can specify one of the following values:
        '''
        result = self._values.get("policy_type")
        assert result is not None, "Required property 'policy_type' is missing"
        return typing.cast("PolicyType", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''An optional description to assign to the policy.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@pepperize/cdk-organizations.PolicyType")
class PolicyType(enum.Enum):
    '''Organizations offers policy types in the following two broad categories:       Authorization policies help you to centrally manage the security of the AWS accounts in your organization.      Management policies enable you to centrally configure and manage AWS services and their features. .

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html#orgs-policy-types
    '''

    SERVICE_CONTROL_POLICY = "SERVICE_CONTROL_POLICY"
    '''Service control policies (SCPs) offer central control over the maximum available permissions for all of the accounts in your organization.'''
    TAG_POLICY = "TAG_POLICY"
    '''Tag policies help you standardize the tags attached to the AWS resources in your organization's accounts.'''
    BACKUP_POLICY = "BACKUP_POLICY"
    '''Backup policies help you centrally manage and apply backup plans to the AWS resources across your organization's accounts.'''
    AISERVICES_OPT_OUT_POLICY = "AISERVICES_OPT_OUT_POLICY"
    '''Artificial Intelligence (AI) services opt-out policies enable you to control data collection for AWS AI services for all of your organization's accounts.'''


@jsii.implements(IParent, IPolicyAttachmentTarget)
class Root(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Root",
):
    '''The parent container for all the accounts for your organization.

    If you apply a policy to the root, it applies to all organizational units (OUs) and accounts in the organization.
    Currently, you can have only one root. AWS Organizations automatically creates it for you when you create an organization.

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        organization: IOrganization,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param organization: 
        '''
        props = RootProps(organization=organization)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''The unique identifier (ID) of the parent root or OU that you want to create the new OU in.'''
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootId")
    def root_id(self) -> builtins.str:
        '''The unique identifier (ID) for the root.

        The regex pattern for a root ID string requires "r-" followed by from 4 to 32 lowercase letters or digits.
        '''
        return typing.cast(builtins.str, jsii.get(self, "rootId"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.RootProps",
    jsii_struct_bases=[],
    name_mapping={"organization": "organization"},
)
class RootProps:
    def __init__(self, *, organization: IOrganization) -> None:
        '''
        :param organization: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "organization": organization,
        }

    @builtins.property
    def organization(self) -> IOrganization:
        result = self._values.get("organization")
        assert result is not None, "Required property 'organization' is missing"
        return typing.cast(IOrganization, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RootProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TagResource(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.TagResource",
):
    '''Add tags to an AWS Organizations resource to make it easier to identify, organize, and search.

    :see: https://docs.aws.amazon.com/ARG/latest/APIReference/API_Tag.html
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        resource: ITaggableResource,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param resource: 
        '''
        props = TagResourceProps(resource=resource)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.TagResourceProps",
    jsii_struct_bases=[],
    name_mapping={"resource": "resource"},
)
class TagResourceProps:
    def __init__(self, *, resource: ITaggableResource) -> None:
        '''
        :param resource: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "resource": resource,
        }

    @builtins.property
    def resource(self) -> ITaggableResource:
        result = self._values.get("resource")
        assert result is not None, "Required property 'resource' is missing"
        return typing.cast(ITaggableResource, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TagResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IAccount, IPolicyAttachmentTarget)
class AccountBase(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@pepperize/cdk-organizations.AccountBase",
):
    '''Creates an AWS account that is automatically a member of the organization whose credentials made the request.

    AWS Organizations automatically copies the information from the management account to the new member account
    '''

    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        '''
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="currentParentId")
    def current_parent_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "currentParentId", []))

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

    @jsii.member(jsii_name="move")
    def move(
        self,
        destination_parent_id: builtins.str,
        source_parent_id: builtins.str,
    ) -> None:
        '''
        :param destination_parent_id: -
        :param source_parent_id: -
        '''
        return typing.cast(None, jsii.invoke(self, "move", [destination_parent_id, source_parent_id]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    @abc.abstractmethod
    def account_id(self) -> builtins.str:
        '''If the account was created successfully, the unique identifier (ID) of the new account.

        Exactly 12 digits.
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountName")
    @abc.abstractmethod
    def account_name(self) -> builtins.str:
        '''The friendly name of the account.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    @abc.abstractmethod
    def email(self) -> builtins.str:
        '''The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        '''
        ...


class _AccountBaseProxy(AccountBase):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''If the account was created successfully, the unique identifier (ID) of the new account.

        Exactly 12 digits.
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountName")
    def account_name(self) -> builtins.str:
        '''The friendly name of the account.'''
        return typing.cast(builtins.str, jsii.get(self, "accountName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        '''The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        '''
        return typing.cast(builtins.str, jsii.get(self, "email"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, AccountBase).__jsii_proxy_class__ = lambda : _AccountBaseProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IOrganizationalUnit")
class IOrganizationalUnit(IPolicyAttachmentTarget, IParent, typing_extensions.Protocol):
    '''A container for accounts within a root.

    An OU also can contain other OUs, enabling you to create a hierarchy that resembles an upside-down tree, with a root at the top and branches of OUs that reach down, ending in accounts that are the leaves of the tree. When you attach a policy to one of the nodes in the hierarchy, it flows down and affects all the branches (OUs) and leaves (accounts) beneath it. An OU can have exactly one parent, and currently each account can be a member of exactly one OU.

    You must first move all accounts out of the OU and any child OUs, and then you can delete the child OUs.
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArn")
    def organizational_unit_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of this OU.

        For more information about ARNs in Organizations, see `ARN Formats Supported by Organizations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsorganizations.html#awsorganizations-resources-for-iam-policies>`_ in the AWS Service Authorization Reference.
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitId")
    def organizational_unit_id(self) -> builtins.str:
        '''The unique identifier (ID) associated with this OU.

        The regex pattern for an organizational unit ID string requires "ou-" followed by from 4 to 32 lowercase letters or digits (the ID of the root that contains the OU). This string is followed by a second "-" dash and from 8 to 32 additional lowercase letters or digits.
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitName")
    def organizational_unit_name(self) -> builtins.str:
        '''The friendly name of this OU.'''
        ...


class _IOrganizationalUnitProxy(
    jsii.proxy_for(IPolicyAttachmentTarget), # type: ignore[misc]
    jsii.proxy_for(IParent), # type: ignore[misc]
):
    '''A container for accounts within a root.

    An OU also can contain other OUs, enabling you to create a hierarchy that resembles an upside-down tree, with a root at the top and branches of OUs that reach down, ending in accounts that are the leaves of the tree. When you attach a policy to one of the nodes in the hierarchy, it flows down and affects all the branches (OUs) and leaves (accounts) beneath it. An OU can have exactly one parent, and currently each account can be a member of exactly one OU.

    You must first move all accounts out of the OU and any child OUs, and then you can delete the child OUs.
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IOrganizationalUnit"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArn")
    def organizational_unit_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of this OU.

        For more information about ARNs in Organizations, see `ARN Formats Supported by Organizations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsorganizations.html#awsorganizations-resources-for-iam-policies>`_ in the AWS Service Authorization Reference.
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitId")
    def organizational_unit_id(self) -> builtins.str:
        '''The unique identifier (ID) associated with this OU.

        The regex pattern for an organizational unit ID string requires "ou-" followed by from 4 to 32 lowercase letters or digits (the ID of the root that contains the OU). This string is followed by a second "-" dash and from 8 to 32 additional lowercase letters or digits.
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitName")
    def organizational_unit_name(self) -> builtins.str:
        '''The friendly name of this OU.'''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOrganizationalUnit).__jsii_proxy_class__ = lambda : _IOrganizationalUnitProxy


@jsii.implements(IOrganizationalUnit)
class OrganizationalUnitBase(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@pepperize/cdk-organizations.OrganizationalUnitBase",
):
    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        '''
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArn")
    @abc.abstractmethod
    def organizational_unit_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of this OU.

        For more information about ARNs in Organizations, see `ARN Formats Supported by Organizations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsorganizations.html#awsorganizations-resources-for-iam-policies>`_ in the AWS Service Authorization Reference.
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitId")
    @abc.abstractmethod
    def organizational_unit_id(self) -> builtins.str:
        '''The unique identifier (ID) associated with this OU.

        The regex pattern for an organizational unit ID string requires "ou-" followed by from 4 to 32 lowercase letters or digits (the ID of the root that contains the OU). This string is followed by a second "-" dash and from 8 to 32 additional lowercase letters or digits.
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitName")
    @abc.abstractmethod
    def organizational_unit_name(self) -> builtins.str:
        '''The friendly name of this OU.'''
        ...


class _OrganizationalUnitBaseProxy(OrganizationalUnitBase):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArn")
    def organizational_unit_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of this OU.

        For more information about ARNs in Organizations, see `ARN Formats Supported by Organizations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsorganizations.html#awsorganizations-resources-for-iam-policies>`_ in the AWS Service Authorization Reference.
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitId")
    def organizational_unit_id(self) -> builtins.str:
        '''The unique identifier (ID) associated with this OU.

        The regex pattern for an organizational unit ID string requires "ou-" followed by from 4 to 32 lowercase letters or digits (the ID of the root that contains the OU). This string is followed by a second "-" dash and from 8 to 32 additional lowercase letters or digits.
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitName")
    def organizational_unit_name(self) -> builtins.str:
        '''The friendly name of this OU.'''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, OrganizationalUnitBase).__jsii_proxy_class__ = lambda : _OrganizationalUnitBaseProxy


class Account(
    AccountBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Account",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_name: builtins.str,
        email: builtins.str,
        iam_user_access_to_billing: typing.Optional[IamUserAccessToBilling] = None,
        parent: typing.Optional[IParent] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account_name: The friendly name of the member account.
        :param email: The email address of the owner to assign to the new member account. This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        :param iam_user_access_to_billing: If set to ALLOW , the new account enables IAM users to access account billing information if they have the required permissions. If set to DENY , only the root user of the new account can access account billing information. Default: ALLOW
        :param parent: The parent root or OU that you want to create the new Account in.
        :param role_name: The name of an IAM role that AWS Organizations automatically preconfigures in the new member account. This role trusts the management account, allowing users in the management account to assume the role, as permitted by the management account administrator. The role has administrator permissions in the new member account. If you don't specify this parameter, the role name defaults to OrganizationAccountAccessRole.
        '''
        props = AccountProps(
            account_name=account_name,
            email=email,
            iam_user_access_to_billing=iam_user_access_to_billing,
            parent=parent,
            role_name=role_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAccountId") # type: ignore[misc]
    @builtins.classmethod
    def from_account_id(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        parent: IParent,
    ) -> IAccount:
        '''Import an existing account from account id.

        :param scope: -
        :param id: -
        :param account_id: 
        :param parent: 
        '''
        attrs = AccountAttributes(account_id=account_id, parent=parent)

        return typing.cast(IAccount, jsii.sinvoke(cls, "fromAccountId", [scope, id, attrs]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''If the account was created successfully, the unique identifier (ID) of the new account.

        Exactly 12 digits.
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountName")
    def account_name(self) -> builtins.str:
        '''The friendly name of the account.'''
        return typing.cast(builtins.str, jsii.get(self, "accountName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        '''The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        '''
        return typing.cast(builtins.str, jsii.get(self, "email"))


class OrganizationalUnit(
    OrganizationalUnitBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.OrganizationalUnit",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        organizational_unit_name: builtins.str,
        parent: IParent,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param organizational_unit_name: The friendly name to assign to the new OU.
        :param parent: The parent root or OU that you want to create the new OrganizationalUnit in.
        '''
        props = OrganizationalUnitProps(
            organizational_unit_name=organizational_unit_name, parent=parent
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromOrganizationalUnitId") # type: ignore[misc]
    @builtins.classmethod
    def from_organizational_unit_id(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        organizational_unit_id: builtins.str,
        organizational_unit_name: builtins.str,
        parent: IParent,
    ) -> IOrganizationalUnit:
        '''
        :param scope: -
        :param id: -
        :param organizational_unit_id: 
        :param organizational_unit_name: 
        :param parent: 
        '''
        attrs = OrganizationalUnitAttributes(
            organizational_unit_id=organizational_unit_id,
            organizational_unit_name=organizational_unit_name,
            parent=parent,
        )

        return typing.cast(IOrganizationalUnit, jsii.sinvoke(cls, "fromOrganizationalUnitId", [scope, id, attrs]))

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArn")
    def organizational_unit_arn(self) -> builtins.str:
        '''The Amazon Resource Name (ARN) of this OU.

        For more information about ARNs in Organizations, see `ARN Formats Supported by Organizations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsorganizations.html#awsorganizations-resources-for-iam-policies>`_ in the AWS Service Authorization Reference.
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitId")
    def organizational_unit_id(self) -> builtins.str:
        '''The unique identifier (ID) associated with this OU.

        The regex pattern for an organizational unit ID string requires "ou-" followed by from 4 to 32 lowercase letters or digits (the ID of the root that contains the OU). This string is followed by a second "-" dash and from 8 to 32 additional lowercase letters or digits.
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitName")
    def organizational_unit_name(self) -> builtins.str:
        '''The friendly name of this OU.'''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitName"))


__all__ = [
    "Account",
    "AccountAttributes",
    "AccountBase",
    "AccountProps",
    "DelegatedAdministrator",
    "DelegatedAdministratorProps",
    "EnableAwsServiceAccess",
    "EnableAwsServiceAccessProps",
    "EnablePolicyType",
    "EnablePolicyTypeProps",
    "FeatureSet",
    "IAccount",
    "IOrganization",
    "IOrganizationalUnit",
    "IParent",
    "IPolicyAttachmentTarget",
    "ITaggableResource",
    "IamUserAccessToBilling",
    "Organization",
    "OrganizationProps",
    "OrganizationalUnit",
    "OrganizationalUnitAttributes",
    "OrganizationalUnitBase",
    "OrganizationalUnitProps",
    "Policy",
    "PolicyAttachment",
    "PolicyAttachmentProps",
    "PolicyProps",
    "PolicyType",
    "Root",
    "RootProps",
    "TagResource",
    "TagResourceProps",
]

publication.publish()
