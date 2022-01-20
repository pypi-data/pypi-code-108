'''
# cdk-library-aws-organization

This CDK library is a WIP and not ready for production use.

## Key challenges with Organizations

* Accounts aren't like AWS resources and the [removal process isn't a simple delete](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_remove.html). Therefore the constructs contained in this library do **not** have the goal to delete accounts.
* CloudFormation doesn't support Organizations directly so the constructs in this library use CloudFormation custom resources that utilize Python and [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/organizations.html)

## Testing the custom provider code with SAM CLI

**Pre-reqs**

* You will either want a previously created test account or allow the tests to create a new account

**Testing**

* Create a test project that utilizes this library (you can use a development version by utilizing `yarn link`, but note you might need to set a static dependency for CDK versions or `constructs` in the local app or you'll get errors about mismatched object types)
* Create a test stack
* Synthesize the test stack with `cdk synth --no-staging > template.yml`
* Get the handler function names from the template
* Run `sam local start-lambda -t template.yml`
* Run the `handler_tests` python files with `pytest` like follows:

```
TEST_ACCOUNT_NAME='<name>' TEST_ACCOUNT_EMAIL='<email>' TEST_ACCOUNT_ORIGINAL_OU='<original ou id>' ACCOUNT_LAMBDA_FUNCTION_NAME='<name you noted earlier>' OU_LAMBDA_FUNCTION_NAME='<name you noted earlier>' pytest ./handler_tests/<test file name>.py -rA --capture=sys
```

* Using the name, email, and original OU env variables here allows the test suite to re-use a single test account. Given deleting accounts is not simple you likely dont want to randomly create a new account every time you run tests.
* The `test.py` also looks up the root org id to run tests so you'll need to have AWS creds set up to accomodate that behavior.
* You can run the provided tests against the real lambda function by getting the deployed function name from AWS and setting the `RUN_LOCALLY` env variable

```
TEST_ACCOUNT_NAME='<name>' TEST_ACCOUNT_EMAIL='<email>' TEST_ACCOUNT_ORIGINAL_OU='<original ou id>' RUN_LOCALLY='false' ACCOUNT_LAMBDA_FUNCTION_NAME='<name you noted earlier>' OU_LAMBDA_FUNCTION_NAME='<name from AWS>' pytest ./handler_tests/<test file name>.py -rA --capture=sys
```

## Why can't I move an OU?

Moving OUs isn't supported by Organizations and would cause significant issues with keeping track of OUs in the CDK. Imagine a scenario like below:

* You have an ou, `OUAdmin`, and it has 2 children, `OUChild1 and Account1`, that are also managed by the CDK stack.
* You change the parent of `OUAdmin` to `OUFoo`. The CDK would need to take the following actions:

  * Create a new `OU` under `OUFoo` with the name `OUAdmin`
  * Move all of the original `OUAdmin` OU's children to the new `OUAdmin`
  * Delete the old `OUAdmin`
  * Update all physical resource IDs

    * It would succeed at moving accounts because physical IDs should not change. Accounting moving between OUs is supported by Organizations
    * It would fail at moving any child OUs because they would also be recreated. Resulting in a change to physical resource ID. Because the custom resource can only managed the resource it's currently acting on, `OUAdmin`, any children OUs would be "lost" in this process and ugly to try and manage.

The best way to move OUs would be to add additional OUs to your org then move any accounts as needed then proceed to delete the OUs, like so:

* Add new OU resources
* Deploy the stack
* Change account parents
* Deploy the stack
* Remove old OU resources
* Deploy the stack
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
import aws_cdk.aws_iam
import aws_cdk.custom_resources
import constructs


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-organization.AccountProps",
    jsii_struct_bases=[],
    name_mapping={
        "email": "email",
        "name": "name",
        "allow_move": "allowMove",
        "disable_delete": "disableDelete",
        "import_on_duplicate": "importOnDuplicate",
    },
)
class AccountProps:
    def __init__(
        self,
        *,
        email: builtins.str,
        name: builtins.str,
        allow_move: typing.Optional[builtins.bool] = None,
        disable_delete: typing.Optional[builtins.bool] = None,
        import_on_duplicate: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''The properties of an Account.

        :param email: The email address of the account. Most be unique.
        :param name: The name of the account.
        :param allow_move: Whether or not to allow this account to be moved between OUs. If importing is enabled this will also allow imported accounts to be moved. Default: false
        :param disable_delete: Whether or not attempting to delete an account should raise an error. Accounts cannot be deleted programmatically, but they can be removed as a managed resource. This property will allow you to control whether or not an error is thrown when the stack wants to delete an account (orphan it) or if it should continue silently. Default: false
        :param import_on_duplicate: Whether or not to import an existing account if the new account is a duplicate. If this is false and the account already exists an error will be thrown. Default: false
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
            "name": name,
        }
        if allow_move is not None:
            self._values["allow_move"] = allow_move
        if disable_delete is not None:
            self._values["disable_delete"] = disable_delete
        if import_on_duplicate is not None:
            self._values["import_on_duplicate"] = import_on_duplicate

    @builtins.property
    def email(self) -> builtins.str:
        '''The email address of the account.

        Most be unique.
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the account.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_move(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to allow this account to be moved between OUs.

        If importing is enabled
        this will also allow imported accounts to be moved.

        :default: false
        '''
        result = self._values.get("allow_move")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_delete(self) -> typing.Optional[builtins.bool]:
        '''Whether or not attempting to delete an account should raise an error.

        Accounts cannot be deleted programmatically, but they can be removed as a managed resource.
        This property will allow you to control whether or not an error is thrown
        when the stack wants to delete an account (orphan it) or if it should continue
        silently.

        :default: false

        :see: https://aws.amazon.com/premiumsupport/knowledge-center/close-aws-account/
        '''
        result = self._values.get("disable_delete")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def import_on_duplicate(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to import an existing account if the new account is a duplicate.

        If this is false and the account already exists an error will be thrown.

        :default: false
        '''
        result = self._values.get("import_on_duplicate")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-organization.AccountResourceProps",
    jsii_struct_bases=[AccountProps],
    name_mapping={
        "email": "email",
        "name": "name",
        "allow_move": "allowMove",
        "disable_delete": "disableDelete",
        "import_on_duplicate": "importOnDuplicate",
        "parent": "parent",
        "provider": "provider",
    },
)
class AccountResourceProps(AccountProps):
    def __init__(
        self,
        *,
        email: builtins.str,
        name: builtins.str,
        allow_move: typing.Optional[builtins.bool] = None,
        disable_delete: typing.Optional[builtins.bool] = None,
        import_on_duplicate: typing.Optional[builtins.bool] = None,
        parent: typing.Union[builtins.str, "OrganizationOU"],
        provider: aws_cdk.custom_resources.Provider,
    ) -> None:
        '''The properties of an OrganizationAccount custom resource.

        :param email: The email address of the account. Most be unique.
        :param name: The name of the account.
        :param allow_move: Whether or not to allow this account to be moved between OUs. If importing is enabled this will also allow imported accounts to be moved. Default: false
        :param disable_delete: Whether or not attempting to delete an account should raise an error. Accounts cannot be deleted programmatically, but they can be removed as a managed resource. This property will allow you to control whether or not an error is thrown when the stack wants to delete an account (orphan it) or if it should continue silently. Default: false
        :param import_on_duplicate: Whether or not to import an existing account if the new account is a duplicate. If this is false and the account already exists an error will be thrown. Default: false
        :param parent: The parent OU id.
        :param provider: The provider to use for the custom resource that will create the OU. You can create a provider with the OrganizationOuProvider class
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "email": email,
            "name": name,
            "parent": parent,
            "provider": provider,
        }
        if allow_move is not None:
            self._values["allow_move"] = allow_move
        if disable_delete is not None:
            self._values["disable_delete"] = disable_delete
        if import_on_duplicate is not None:
            self._values["import_on_duplicate"] = import_on_duplicate

    @builtins.property
    def email(self) -> builtins.str:
        '''The email address of the account.

        Most be unique.
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the account.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_move(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to allow this account to be moved between OUs.

        If importing is enabled
        this will also allow imported accounts to be moved.

        :default: false
        '''
        result = self._values.get("allow_move")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def disable_delete(self) -> typing.Optional[builtins.bool]:
        '''Whether or not attempting to delete an account should raise an error.

        Accounts cannot be deleted programmatically, but they can be removed as a managed resource.
        This property will allow you to control whether or not an error is thrown
        when the stack wants to delete an account (orphan it) or if it should continue
        silently.

        :default: false

        :see: https://aws.amazon.com/premiumsupport/knowledge-center/close-aws-account/
        '''
        result = self._values.get("disable_delete")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def import_on_duplicate(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to import an existing account if the new account is a duplicate.

        If this is false and the account already exists an error will be thrown.

        :default: false
        '''
        result = self._values.get("import_on_duplicate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def parent(self) -> typing.Union[builtins.str, "OrganizationOU"]:
        '''The parent OU id.'''
        result = self._values.get("parent")
        assert result is not None, "Required property 'parent' is missing"
        return typing.cast(typing.Union[builtins.str, "OrganizationOU"], result)

    @builtins.property
    def provider(self) -> aws_cdk.custom_resources.Provider:
        '''The provider to use for the custom resource that will create the OU.

        You can create a provider with the OrganizationOuProvider class
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(aws_cdk.custom_resources.Provider, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(
    jsii_type="@renovosolutions/cdk-library-aws-organization.IPAMAdministratorProps"
)
class IPAMAdministratorProps(typing_extensions.Protocol):
    '''The properties of an OrganizationAccount custom resource.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delegatedAdminAccountId")
    def delegated_admin_account_id(self) -> builtins.str:
        '''The account id of the IPAM administrator.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provider")
    def provider(self) -> aws_cdk.custom_resources.Provider:
        '''The provider to use for the custom resource that will handle IPAM admin delegation.

        You can create a provider with the IPAMAdministratorProvider class
        '''
        ...


class _IPAMAdministratorPropsProxy:
    '''The properties of an OrganizationAccount custom resource.'''

    __jsii_type__: typing.ClassVar[str] = "@renovosolutions/cdk-library-aws-organization.IPAMAdministratorProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delegatedAdminAccountId")
    def delegated_admin_account_id(self) -> builtins.str:
        '''The account id of the IPAM administrator.'''
        return typing.cast(builtins.str, jsii.get(self, "delegatedAdminAccountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provider")
    def provider(self) -> aws_cdk.custom_resources.Provider:
        '''The provider to use for the custom resource that will handle IPAM admin delegation.

        You can create a provider with the IPAMAdministratorProvider class
        '''
        return typing.cast(aws_cdk.custom_resources.Provider, jsii.get(self, "provider"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPAMAdministratorProps).__jsii_proxy_class__ = lambda : _IPAMAdministratorPropsProxy


class IPAMAdministratorProvider(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-organization.IPAMAdministratorProvider",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: "IPAMAdministratorProviderProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provider")
    def provider(self) -> aws_cdk.custom_resources.Provider:
        return typing.cast(aws_cdk.custom_resources.Provider, jsii.get(self, "provider"))


@jsii.interface(
    jsii_type="@renovosolutions/cdk-library-aws-organization.IPAMAdministratorProviderProps"
)
class IPAMAdministratorProviderProps(typing_extensions.Protocol):
    '''The properties of an IPAM administrator custom resource provider.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The role the custom resource should use for working with the IPAM administrator delegation if one is not provided one will be created automatically.'''
        ...


class _IPAMAdministratorProviderPropsProxy:
    '''The properties of an IPAM administrator custom resource provider.'''

    __jsii_type__: typing.ClassVar[str] = "@renovosolutions/cdk-library-aws-organization.IPAMAdministratorProviderProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The role the custom resource should use for working with the IPAM administrator delegation if one is not provided one will be created automatically.'''
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], jsii.get(self, "role"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPAMAdministratorProviderProps).__jsii_proxy_class__ = lambda : _IPAMAdministratorProviderPropsProxy


class IPAMdministrator(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-organization.IPAMdministrator",
):
    '''The construct to create or update the delegated IPAM administrator for an organization.

    This relies on the custom resource provider IPAMAdministratorProvider.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: IPAMAdministratorProps,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> aws_cdk.CustomResource:
        return typing.cast(aws_cdk.CustomResource, jsii.get(self, "resource"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-organization.OUObject",
    jsii_struct_bases=[],
    name_mapping={
        "children": "children",
        "properties": "properties",
        "accounts": "accounts",
        "id": "id",
    },
)
class OUObject:
    def __init__(
        self,
        *,
        children: typing.Sequence["OUObject"],
        properties: "OUProps",
        accounts: typing.Optional[typing.Sequence[AccountProps]] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''The structure of an OrgObject.

        :param children: OUs that are children of this OU.
        :param properties: The OU object properties.
        :param accounts: Accounts that belong to this OU.
        :param id: The unique id of the OUObject. This is used as the unique identifier when instantiating a construct object. This is important for the CDK to be able to maintain a reference for the object when utilizing the processOUObj function rather then using the name property of an object which could change. If the id changes the CDK treats this as a new construct and will create a new construct resource and destroy the old one. Not strictly required but useful when using the processOUObj function. If the id is not provided the name property will be used as the id in processOUObj. You can create a unique id however you like. A bash example is provided.
        '''
        if isinstance(properties, dict):
            properties = OUProps(**properties)
        self._values: typing.Dict[str, typing.Any] = {
            "children": children,
            "properties": properties,
        }
        if accounts is not None:
            self._values["accounts"] = accounts
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def children(self) -> typing.List["OUObject"]:
        '''OUs that are children of this OU.'''
        result = self._values.get("children")
        assert result is not None, "Required property 'children' is missing"
        return typing.cast(typing.List["OUObject"], result)

    @builtins.property
    def properties(self) -> "OUProps":
        '''The OU object properties.'''
        result = self._values.get("properties")
        assert result is not None, "Required property 'properties' is missing"
        return typing.cast("OUProps", result)

    @builtins.property
    def accounts(self) -> typing.Optional[typing.List[AccountProps]]:
        '''Accounts that belong to this OU.'''
        result = self._values.get("accounts")
        return typing.cast(typing.Optional[typing.List[AccountProps]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''The unique id of the OUObject.

        This is used as the unique identifier when instantiating a construct object.
        This is important for the CDK to be able to maintain a reference for the object when utilizing
        the processOUObj function rather then using the name property of an object which could change.
        If the id changes the CDK treats this as a new construct and will create a new construct resource and
        destroy the old one.

        Not strictly required but useful when using the processOUObj function. If the id is not provided
        the name property will be used as the id in processOUObj.

        You can create a unique id however you like. A bash example is provided.

        Example::

            echo "ou-$( echo $RANDOM | md5sum | head -c 8 )"
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OUObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-organization.OUProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "allow_recreate_on_update": "allowRecreateOnUpdate",
        "import_on_duplicate": "importOnDuplicate",
    },
)
class OUProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        allow_recreate_on_update: typing.Optional[builtins.bool] = None,
        import_on_duplicate: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''The properties of an OU.

        :param name: The name of the OU.
        :param allow_recreate_on_update: Whether or not a missing OU should be recreated during an update. If this is false and the OU does not exist an error will be thrown when you try to update it. Default: false
        :param import_on_duplicate: Whether or not to import an existing OU if the new OU is a duplicate. If this is false and the OU already exists an error will be thrown. Default: false
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if allow_recreate_on_update is not None:
            self._values["allow_recreate_on_update"] = allow_recreate_on_update
        if import_on_duplicate is not None:
            self._values["import_on_duplicate"] = import_on_duplicate

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the OU.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_recreate_on_update(self) -> typing.Optional[builtins.bool]:
        '''Whether or not a missing OU should be recreated during an update.

        If this is false and the OU does not exist an error will be thrown when you try to update it.

        :default: false
        '''
        result = self._values.get("allow_recreate_on_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def import_on_duplicate(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to import an existing OU if the new OU is a duplicate.

        If this is false and the OU already exists an error will be thrown.

        :default: false
        '''
        result = self._values.get("import_on_duplicate")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OUProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-organization.OUResourceProps",
    jsii_struct_bases=[OUProps],
    name_mapping={
        "name": "name",
        "allow_recreate_on_update": "allowRecreateOnUpdate",
        "import_on_duplicate": "importOnDuplicate",
        "parent": "parent",
        "provider": "provider",
    },
)
class OUResourceProps(OUProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        allow_recreate_on_update: typing.Optional[builtins.bool] = None,
        import_on_duplicate: typing.Optional[builtins.bool] = None,
        parent: typing.Union[builtins.str, "OrganizationOU"],
        provider: aws_cdk.custom_resources.Provider,
    ) -> None:
        '''The properties of an OrganizationOU custom resource.

        :param name: The name of the OU.
        :param allow_recreate_on_update: Whether or not a missing OU should be recreated during an update. If this is false and the OU does not exist an error will be thrown when you try to update it. Default: false
        :param import_on_duplicate: Whether or not to import an existing OU if the new OU is a duplicate. If this is false and the OU already exists an error will be thrown. Default: false
        :param parent: The parent OU id.
        :param provider: The provider to use for the custom resource that will create the OU. You can create a provider with the OrganizationOuProvider class
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "parent": parent,
            "provider": provider,
        }
        if allow_recreate_on_update is not None:
            self._values["allow_recreate_on_update"] = allow_recreate_on_update
        if import_on_duplicate is not None:
            self._values["import_on_duplicate"] = import_on_duplicate

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the OU.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_recreate_on_update(self) -> typing.Optional[builtins.bool]:
        '''Whether or not a missing OU should be recreated during an update.

        If this is false and the OU does not exist an error will be thrown when you try to update it.

        :default: false
        '''
        result = self._values.get("allow_recreate_on_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def import_on_duplicate(self) -> typing.Optional[builtins.bool]:
        '''Whether or not to import an existing OU if the new OU is a duplicate.

        If this is false and the OU already exists an error will be thrown.

        :default: false
        '''
        result = self._values.get("import_on_duplicate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def parent(self) -> typing.Union[builtins.str, "OrganizationOU"]:
        '''The parent OU id.'''
        result = self._values.get("parent")
        assert result is not None, "Required property 'parent' is missing"
        return typing.cast(typing.Union[builtins.str, "OrganizationOU"], result)

    @builtins.property
    def provider(self) -> aws_cdk.custom_resources.Provider:
        '''The provider to use for the custom resource that will create the OU.

        You can create a provider with the OrganizationOuProvider class
        '''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(aws_cdk.custom_resources.Provider, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OUResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OrganizationAccount(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-organization.OrganizationAccount",
):
    '''The construct to create or update an Organization account.

    This relies on the custom resource provider OrganizationAccountProvider.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        parent: typing.Union[builtins.str, "OrganizationOU"],
        provider: aws_cdk.custom_resources.Provider,
        email: builtins.str,
        name: builtins.str,
        allow_move: typing.Optional[builtins.bool] = None,
        disable_delete: typing.Optional[builtins.bool] = None,
        import_on_duplicate: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param parent: The parent OU id.
        :param provider: The provider to use for the custom resource that will create the OU. You can create a provider with the OrganizationOuProvider class
        :param email: The email address of the account. Most be unique.
        :param name: The name of the account.
        :param allow_move: Whether or not to allow this account to be moved between OUs. If importing is enabled this will also allow imported accounts to be moved. Default: false
        :param disable_delete: Whether or not attempting to delete an account should raise an error. Accounts cannot be deleted programmatically, but they can be removed as a managed resource. This property will allow you to control whether or not an error is thrown when the stack wants to delete an account (orphan it) or if it should continue silently. Default: false
        :param import_on_duplicate: Whether or not to import an existing account if the new account is a duplicate. If this is false and the account already exists an error will be thrown. Default: false
        '''
        props = AccountResourceProps(
            parent=parent,
            provider=provider,
            email=email,
            name=name,
            allow_move=allow_move,
            disable_delete=disable_delete,
            import_on_duplicate=import_on_duplicate,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> aws_cdk.CustomResource:
        return typing.cast(aws_cdk.CustomResource, jsii.get(self, "resource"))


class OrganizationAccountProvider(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-organization.OrganizationAccountProvider",
):
    '''The provider for account custom resources.

    This creates a lambda function that handles custom resource requests for creating/updating accounts.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param role: The role the custom resource should use for taking actions on OUs if one is not provided one will be created automatically.
        '''
        props = OrganizationOUProviderProps(role=role)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provider")
    def provider(self) -> aws_cdk.custom_resources.Provider:
        return typing.cast(aws_cdk.custom_resources.Provider, jsii.get(self, "provider"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-organization.OrganizationAccountProviderProps",
    jsii_struct_bases=[],
    name_mapping={"role": "role"},
)
class OrganizationAccountProviderProps:
    def __init__(self, *, role: typing.Optional[aws_cdk.aws_iam.IRole] = None) -> None:
        '''The properties for the account custom resource provider.

        :param role: The role the custom resource should use for taking actions on OUs if one is not provided one will be created automatically.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The role the custom resource should use for taking actions on OUs if one is not provided one will be created automatically.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationAccountProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OrganizationOU(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-organization.OrganizationOU",
):
    '''The construct to create or update an Organization OU.

    This relies on the custom resource provider OrganizationOUProvider.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        parent: typing.Union[builtins.str, "OrganizationOU"],
        provider: aws_cdk.custom_resources.Provider,
        name: builtins.str,
        allow_recreate_on_update: typing.Optional[builtins.bool] = None,
        import_on_duplicate: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param parent: The parent OU id.
        :param provider: The provider to use for the custom resource that will create the OU. You can create a provider with the OrganizationOuProvider class
        :param name: The name of the OU.
        :param allow_recreate_on_update: Whether or not a missing OU should be recreated during an update. If this is false and the OU does not exist an error will be thrown when you try to update it. Default: false
        :param import_on_duplicate: Whether or not to import an existing OU if the new OU is a duplicate. If this is false and the OU already exists an error will be thrown. Default: false
        '''
        props = OUResourceProps(
            parent=parent,
            provider=provider,
            name=name,
            allow_recreate_on_update=allow_recreate_on_update,
            import_on_duplicate=import_on_duplicate,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def resource(self) -> aws_cdk.CustomResource:
        return typing.cast(aws_cdk.CustomResource, jsii.get(self, "resource"))


class OrganizationOUProvider(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aws-organization.OrganizationOUProvider",
):
    '''The provider for OU custom resources.

    This creates a lambda function that handles custom resource requests for creating/updating/deleting OUs.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param role: The role the custom resource should use for taking actions on OUs if one is not provided one will be created automatically.
        '''
        props = OrganizationOUProviderProps(role=role)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provider")
    def provider(self) -> aws_cdk.custom_resources.Provider:
        return typing.cast(aws_cdk.custom_resources.Provider, jsii.get(self, "provider"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aws-organization.OrganizationOUProviderProps",
    jsii_struct_bases=[],
    name_mapping={"role": "role"},
)
class OrganizationOUProviderProps:
    def __init__(self, *, role: typing.Optional[aws_cdk.aws_iam.IRole] = None) -> None:
        '''The properties for the OU custom resource provider.

        :param role: The role the custom resource should use for taking actions on OUs if one is not provided one will be created automatically.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The role the custom resource should use for taking actions on OUs if one is not provided one will be created automatically.'''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationOUProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccountProps",
    "AccountResourceProps",
    "IPAMAdministratorProps",
    "IPAMAdministratorProvider",
    "IPAMAdministratorProviderProps",
    "IPAMdministrator",
    "OUObject",
    "OUProps",
    "OUResourceProps",
    "OrganizationAccount",
    "OrganizationAccountProvider",
    "OrganizationAccountProviderProps",
    "OrganizationOU",
    "OrganizationOUProvider",
    "OrganizationOUProviderProps",
]

publication.publish()
