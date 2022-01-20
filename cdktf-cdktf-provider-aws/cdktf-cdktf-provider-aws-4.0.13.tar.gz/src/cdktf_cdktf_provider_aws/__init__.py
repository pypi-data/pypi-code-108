'''
# Terraform CDK aws Provider ~> 3.0

This repo builds and publishes the Terraform aws Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-aws](https://www.npmjs.com/package/@cdktf/provider-aws).

`npm install @cdktf/provider-aws`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-aws](https://pypi.org/project/cdktf-cdktf-provider-aws).

`pipenv install cdktf-cdktf-provider-aws`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Aws](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Aws).

`dotnet add package HashiCorp.Cdktf.Providers.Aws`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-aws](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-aws).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-aws</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform aws Provider version 1:1. In fact, it always tracks `latest` of `~> 3.0` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform aws Provider](https://github.com/terraform-providers/terraform-provider-aws)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform aws Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/hashicorp/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [Repository Manager](https://github.com/hashicorp/cdktf-repository-manager/)
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

import cdktf
import constructs


class AccountAlternateContact(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.AccountAlternateContact",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact aws_account_alternate_contact}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alternate_contact_type: builtins.str,
        email_address: builtins.str,
        name: builtins.str,
        phone_number: builtins.str,
        title: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact aws_account_alternate_contact} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alternate_contact_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#alternate_contact_type AccountAlternateContact#alternate_contact_type}.
        :param email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#email_address AccountAlternateContact#email_address}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#name AccountAlternateContact#name}.
        :param phone_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#phone_number AccountAlternateContact#phone_number}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#title AccountAlternateContact#title}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#account_id AccountAlternateContact#account_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AccountAlternateContactConfig(
            alternate_contact_type=alternate_contact_type,
            email_address=email_address,
            name=name,
            phone_number=phone_number,
            title=title,
            account_id=account_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alternateContactTypeInput")
    def alternate_contact_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alternateContactTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailAddressInput")
    def email_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="phoneNumberInput")
    def phone_number_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "phoneNumberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="titleInput")
    def title_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "titleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        jsii.set(self, "accountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alternateContactType")
    def alternate_contact_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alternateContactType"))

    @alternate_contact_type.setter
    def alternate_contact_type(self, value: builtins.str) -> None:
        jsii.set(self, "alternateContactType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="emailAddress")
    def email_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailAddress"))

    @email_address.setter
    def email_address(self, value: builtins.str) -> None:
        jsii.set(self, "emailAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="phoneNumber")
    def phone_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "phoneNumber"))

    @phone_number.setter
    def phone_number(self, value: builtins.str) -> None:
        jsii.set(self, "phoneNumber", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @title.setter
    def title(self, value: builtins.str) -> None:
        jsii.set(self, "title", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.AccountAlternateContactConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "alternate_contact_type": "alternateContactType",
        "email_address": "emailAddress",
        "name": "name",
        "phone_number": "phoneNumber",
        "title": "title",
        "account_id": "accountId",
    },
)
class AccountAlternateContactConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        alternate_contact_type: builtins.str,
        email_address: builtins.str,
        name: builtins.str,
        phone_number: builtins.str,
        title: builtins.str,
        account_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param alternate_contact_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#alternate_contact_type AccountAlternateContact#alternate_contact_type}.
        :param email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#email_address AccountAlternateContact#email_address}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#name AccountAlternateContact#name}.
        :param phone_number: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#phone_number AccountAlternateContact#phone_number}.
        :param title: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#title AccountAlternateContact#title}.
        :param account_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#account_id AccountAlternateContact#account_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "alternate_contact_type": alternate_contact_type,
            "email_address": email_address,
            "name": name,
            "phone_number": phone_number,
            "title": title,
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
    def alternate_contact_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#alternate_contact_type AccountAlternateContact#alternate_contact_type}.'''
        result = self._values.get("alternate_contact_type")
        assert result is not None, "Required property 'alternate_contact_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email_address(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#email_address AccountAlternateContact#email_address}.'''
        result = self._values.get("email_address")
        assert result is not None, "Required property 'email_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#name AccountAlternateContact#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def phone_number(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#phone_number AccountAlternateContact#phone_number}.'''
        result = self._values.get("phone_number")
        assert result is not None, "Required property 'phone_number' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def title(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#title AccountAlternateContact#title}.'''
        result = self._values.get("title")
        assert result is not None, "Required property 'title' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/account_alternate_contact#account_id AccountAlternateContact#account_id}.'''
        result = self._values.get("account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountAlternateContactConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AwsProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.AwsProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws aws}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        region: builtins.str,
        access_key: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        allowed_account_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        assume_role: typing.Optional["AwsProviderAssumeRole"] = None,
        default_tags: typing.Optional["AwsProviderDefaultTags"] = None,
        endpoints: typing.Optional[typing.Sequence["AwsProviderEndpoints"]] = None,
        forbidden_account_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        http_proxy: typing.Optional[builtins.str] = None,
        ignore_tags: typing.Optional["AwsProviderIgnoreTags"] = None,
        insecure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        profile: typing.Optional[builtins.str] = None,
        s3_force_path_style: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        secret_key: typing.Optional[builtins.str] = None,
        shared_credentials_file: typing.Optional[builtins.str] = None,
        skip_credentials_validation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_get_ec2_platforms: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_metadata_api_check: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_region_validation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_requesting_account_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws aws} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param region: The region where AWS operations will take place. Examples are us-east-1, us-west-2, etc. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#region AwsProvider#region}
        :param access_key: The access key for API operations. You can retrieve this from the 'Security & Credentials' section of the AWS console. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#access_key AwsProvider#access_key}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#alias AwsProvider#alias}
        :param allowed_account_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#allowed_account_ids AwsProvider#allowed_account_ids}.
        :param assume_role: assume_role block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#assume_role AwsProvider#assume_role}
        :param default_tags: default_tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#default_tags AwsProvider#default_tags}
        :param endpoints: endpoints block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#endpoints AwsProvider#endpoints}
        :param forbidden_account_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forbidden_account_ids AwsProvider#forbidden_account_ids}.
        :param http_proxy: The address of an HTTP proxy to use when accessing the AWS API. Can also be configured using the ``HTTP_PROXY`` or ``HTTPS_PROXY`` environment variables. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#http_proxy AwsProvider#http_proxy}
        :param ignore_tags: ignore_tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ignore_tags AwsProvider#ignore_tags}
        :param insecure: Explicitly allow the provider to perform "insecure" SSL requests. If omitted, default value is ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#insecure AwsProvider#insecure}
        :param max_retries: The maximum number of times an AWS API request is being executed. If the API request still fails, an error is thrown. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#max_retries AwsProvider#max_retries}
        :param profile: The profile for API operations. If not set, the default profile created with ``aws configure`` will be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#profile AwsProvider#profile}
        :param s3_force_path_style: Set this to true to force the request to use path-style addressing, i.e., http://s3.amazonaws.com/BUCKET/KEY. By default, the S3 client will use virtual hosted bucket addressing when possible (http://BUCKET.s3.amazonaws.com/KEY). Specific to the Amazon S3 service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#s3_force_path_style AwsProvider#s3_force_path_style}
        :param secret_key: The secret key for API operations. You can retrieve this from the 'Security & Credentials' section of the AWS console. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#secret_key AwsProvider#secret_key}
        :param shared_credentials_file: The path to the shared credentials file. If not set this defaults to ~/.aws/credentials. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#shared_credentials_file AwsProvider#shared_credentials_file}
        :param skip_credentials_validation: Skip the credentials validation via STS API. Used for AWS API implementations that do not have STS available/implemented. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_credentials_validation AwsProvider#skip_credentials_validation}
        :param skip_get_ec2_platforms: Skip getting the supported EC2 platforms. Used by users that don't have ec2:DescribeAccountAttributes permissions. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_get_ec2_platforms AwsProvider#skip_get_ec2_platforms}
        :param skip_metadata_api_check: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_metadata_api_check AwsProvider#skip_metadata_api_check}.
        :param skip_region_validation: Skip static validation of region name. Used by users of alternative AWS-like APIs or users w/ access to regions that are not public (yet). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_region_validation AwsProvider#skip_region_validation}
        :param skip_requesting_account_id: Skip requesting the account ID. Used for AWS API implementations that do not have IAM/STS API and/or metadata API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_requesting_account_id AwsProvider#skip_requesting_account_id}
        :param token: session token. A session token is only required if you are using temporary security credentials. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#token AwsProvider#token}
        '''
        config = AwsProviderConfig(
            region=region,
            access_key=access_key,
            alias=alias,
            allowed_account_ids=allowed_account_ids,
            assume_role=assume_role,
            default_tags=default_tags,
            endpoints=endpoints,
            forbidden_account_ids=forbidden_account_ids,
            http_proxy=http_proxy,
            ignore_tags=ignore_tags,
            insecure=insecure,
            max_retries=max_retries,
            profile=profile,
            s3_force_path_style=s3_force_path_style,
            secret_key=secret_key,
            shared_credentials_file=shared_credentials_file,
            skip_credentials_validation=skip_credentials_validation,
            skip_get_ec2_platforms=skip_get_ec2_platforms,
            skip_metadata_api_check=skip_metadata_api_check,
            skip_region_validation=skip_region_validation,
            skip_requesting_account_id=skip_requesting_account_id,
            token=token,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAccessKey")
    def reset_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessKey", []))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetAllowedAccountIds")
    def reset_allowed_account_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedAccountIds", []))

    @jsii.member(jsii_name="resetAssumeRole")
    def reset_assume_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssumeRole", []))

    @jsii.member(jsii_name="resetDefaultTags")
    def reset_default_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTags", []))

    @jsii.member(jsii_name="resetEndpoints")
    def reset_endpoints(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoints", []))

    @jsii.member(jsii_name="resetForbiddenAccountIds")
    def reset_forbidden_account_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForbiddenAccountIds", []))

    @jsii.member(jsii_name="resetHttpProxy")
    def reset_http_proxy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpProxy", []))

    @jsii.member(jsii_name="resetIgnoreTags")
    def reset_ignore_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreTags", []))

    @jsii.member(jsii_name="resetInsecure")
    def reset_insecure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecure", []))

    @jsii.member(jsii_name="resetMaxRetries")
    def reset_max_retries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRetries", []))

    @jsii.member(jsii_name="resetProfile")
    def reset_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfile", []))

    @jsii.member(jsii_name="resetS3ForcePathStyle")
    def reset_s3_force_path_style(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetS3ForcePathStyle", []))

    @jsii.member(jsii_name="resetSecretKey")
    def reset_secret_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretKey", []))

    @jsii.member(jsii_name="resetSharedCredentialsFile")
    def reset_shared_credentials_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSharedCredentialsFile", []))

    @jsii.member(jsii_name="resetSkipCredentialsValidation")
    def reset_skip_credentials_validation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipCredentialsValidation", []))

    @jsii.member(jsii_name="resetSkipGetEc2Platforms")
    def reset_skip_get_ec2_platforms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipGetEc2Platforms", []))

    @jsii.member(jsii_name="resetSkipMetadataApiCheck")
    def reset_skip_metadata_api_check(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipMetadataApiCheck", []))

    @jsii.member(jsii_name="resetSkipRegionValidation")
    def reset_skip_region_validation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipRegionValidation", []))

    @jsii.member(jsii_name="resetSkipRequestingAccountId")
    def reset_skip_requesting_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipRequestingAccountId", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessKeyInput")
    def access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedAccountIdsInput")
    def allowed_account_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedAccountIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="assumeRoleInput")
    def assume_role_input(self) -> typing.Optional["AwsProviderAssumeRole"]:
        return typing.cast(typing.Optional["AwsProviderAssumeRole"], jsii.get(self, "assumeRoleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTagsInput")
    def default_tags_input(self) -> typing.Optional["AwsProviderDefaultTags"]:
        return typing.cast(typing.Optional["AwsProviderDefaultTags"], jsii.get(self, "defaultTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointsInput")
    def endpoints_input(self) -> typing.Optional[typing.List["AwsProviderEndpoints"]]:
        return typing.cast(typing.Optional[typing.List["AwsProviderEndpoints"]], jsii.get(self, "endpointsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forbiddenAccountIdsInput")
    def forbidden_account_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "forbiddenAccountIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpProxyInput")
    def http_proxy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpProxyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreTagsInput")
    def ignore_tags_input(self) -> typing.Optional["AwsProviderIgnoreTags"]:
        return typing.cast(typing.Optional["AwsProviderIgnoreTags"], jsii.get(self, "ignoreTagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureInput")
    def insecure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "insecureInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetriesInput")
    def max_retries_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetriesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profileInput")
    def profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ForcePathStyleInput")
    def s3_force_path_style_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "s3ForcePathStyleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretKeyInput")
    def secret_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sharedCredentialsFileInput")
    def shared_credentials_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sharedCredentialsFileInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipCredentialsValidationInput")
    def skip_credentials_validation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipCredentialsValidationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipGetEc2PlatformsInput")
    def skip_get_ec2_platforms_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipGetEc2PlatformsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipMetadataApiCheckInput")
    def skip_metadata_api_check_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipMetadataApiCheckInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipRegionValidationInput")
    def skip_region_validation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipRegionValidationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipRequestingAccountIdInput")
    def skip_requesting_account_id_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipRequestingAccountIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessKey")
    def access_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessKey"))

    @access_key.setter
    def access_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "accessKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedAccountIds")
    def allowed_account_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedAccountIds"))

    @allowed_account_ids.setter
    def allowed_account_ids(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "allowedAccountIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="assumeRole")
    def assume_role(self) -> typing.Optional["AwsProviderAssumeRole"]:
        return typing.cast(typing.Optional["AwsProviderAssumeRole"], jsii.get(self, "assumeRole"))

    @assume_role.setter
    def assume_role(self, value: typing.Optional["AwsProviderAssumeRole"]) -> None:
        jsii.set(self, "assumeRole", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultTags")
    def default_tags(self) -> typing.Optional["AwsProviderDefaultTags"]:
        return typing.cast(typing.Optional["AwsProviderDefaultTags"], jsii.get(self, "defaultTags"))

    @default_tags.setter
    def default_tags(self, value: typing.Optional["AwsProviderDefaultTags"]) -> None:
        jsii.set(self, "defaultTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoints")
    def endpoints(self) -> typing.Optional[typing.List["AwsProviderEndpoints"]]:
        return typing.cast(typing.Optional[typing.List["AwsProviderEndpoints"]], jsii.get(self, "endpoints"))

    @endpoints.setter
    def endpoints(
        self,
        value: typing.Optional[typing.List["AwsProviderEndpoints"]],
    ) -> None:
        jsii.set(self, "endpoints", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forbiddenAccountIds")
    def forbidden_account_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "forbiddenAccountIds"))

    @forbidden_account_ids.setter
    def forbidden_account_ids(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "forbiddenAccountIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpProxy")
    def http_proxy(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpProxy"))

    @http_proxy.setter
    def http_proxy(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "httpProxy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ignoreTags")
    def ignore_tags(self) -> typing.Optional["AwsProviderIgnoreTags"]:
        return typing.cast(typing.Optional["AwsProviderIgnoreTags"], jsii.get(self, "ignoreTags"))

    @ignore_tags.setter
    def ignore_tags(self, value: typing.Optional["AwsProviderIgnoreTags"]) -> None:
        jsii.set(self, "ignoreTags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecure")
    def insecure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "insecure"))

    @insecure.setter
    def insecure(
        self,
        value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "insecure", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetries")
    def max_retries(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetries"))

    @max_retries.setter
    def max_retries(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "maxRetries", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="profile")
    def profile(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profile"))

    @profile.setter
    def profile(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "profile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))

    @region.setter
    def region(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "region", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="s3ForcePathStyle")
    def s3_force_path_style(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "s3ForcePathStyle"))

    @s3_force_path_style.setter
    def s3_force_path_style(
        self,
        value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "s3ForcePathStyle", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretKey"))

    @secret_key.setter
    def secret_key(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "secretKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sharedCredentialsFile")
    def shared_credentials_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sharedCredentialsFile"))

    @shared_credentials_file.setter
    def shared_credentials_file(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "sharedCredentialsFile", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipCredentialsValidation")
    def skip_credentials_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipCredentialsValidation"))

    @skip_credentials_validation.setter
    def skip_credentials_validation(
        self,
        value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "skipCredentialsValidation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipGetEc2Platforms")
    def skip_get_ec2_platforms(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipGetEc2Platforms"))

    @skip_get_ec2_platforms.setter
    def skip_get_ec2_platforms(
        self,
        value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "skipGetEc2Platforms", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipMetadataApiCheck")
    def skip_metadata_api_check(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipMetadataApiCheck"))

    @skip_metadata_api_check.setter
    def skip_metadata_api_check(
        self,
        value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "skipMetadataApiCheck", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipRegionValidation")
    def skip_region_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipRegionValidation"))

    @skip_region_validation.setter
    def skip_region_validation(
        self,
        value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "skipRegionValidation", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipRequestingAccountId")
    def skip_requesting_account_id(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "skipRequestingAccountId"))

    @skip_requesting_account_id.setter
    def skip_requesting_account_id(
        self,
        value: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "skipRequestingAccountId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="token")
    def token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "token"))

    @token.setter
    def token(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "token", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.AwsProviderAssumeRole",
    jsii_struct_bases=[],
    name_mapping={
        "duration_seconds": "durationSeconds",
        "external_id": "externalId",
        "policy": "policy",
        "policy_arns": "policyArns",
        "role_arn": "roleArn",
        "session_name": "sessionName",
        "tags": "tags",
        "transitive_tag_keys": "transitiveTagKeys",
    },
)
class AwsProviderAssumeRole:
    def __init__(
        self,
        *,
        duration_seconds: typing.Optional[jsii.Number] = None,
        external_id: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        policy_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        role_arn: typing.Optional[builtins.str] = None,
        session_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        transitive_tag_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param duration_seconds: The duration, in seconds, of the role session. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#duration_seconds AwsProvider#duration_seconds}
        :param external_id: A unique identifier that might be required when you assume a role in another account. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#external_id AwsProvider#external_id}
        :param policy: IAM Policy JSON describing further restricting permissions for the IAM Role being assumed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#policy AwsProvider#policy}
        :param policy_arns: Amazon Resource Names (ARNs) of IAM Policies describing further restricting permissions for the IAM Role being assumed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#policy_arns AwsProvider#policy_arns}
        :param role_arn: Amazon Resource Name of an IAM Role to assume prior to making API calls. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#role_arn AwsProvider#role_arn}
        :param session_name: An identifier for the assumed role session. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#session_name AwsProvider#session_name}
        :param tags: Assume role session tags. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#tags AwsProvider#tags}
        :param transitive_tag_keys: Assume role session tag keys to pass to any subsequent sessions. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transitive_tag_keys AwsProvider#transitive_tag_keys}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if duration_seconds is not None:
            self._values["duration_seconds"] = duration_seconds
        if external_id is not None:
            self._values["external_id"] = external_id
        if policy is not None:
            self._values["policy"] = policy
        if policy_arns is not None:
            self._values["policy_arns"] = policy_arns
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if session_name is not None:
            self._values["session_name"] = session_name
        if tags is not None:
            self._values["tags"] = tags
        if transitive_tag_keys is not None:
            self._values["transitive_tag_keys"] = transitive_tag_keys

    @builtins.property
    def duration_seconds(self) -> typing.Optional[jsii.Number]:
        '''The duration, in seconds, of the role session.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#duration_seconds AwsProvider#duration_seconds}
        '''
        result = self._values.get("duration_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def external_id(self) -> typing.Optional[builtins.str]:
        '''A unique identifier that might be required when you assume a role in another account.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#external_id AwsProvider#external_id}
        '''
        result = self._values.get("external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''IAM Policy JSON describing further restricting permissions for the IAM Role being assumed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#policy AwsProvider#policy}
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Amazon Resource Names (ARNs) of IAM Policies describing further restricting permissions for the IAM Role being assumed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#policy_arns AwsProvider#policy_arns}
        '''
        result = self._values.get("policy_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Amazon Resource Name of an IAM Role to assume prior to making API calls.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#role_arn AwsProvider#role_arn}
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_name(self) -> typing.Optional[builtins.str]:
        '''An identifier for the assumed role session.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#session_name AwsProvider#session_name}
        '''
        result = self._values.get("session_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Assume role session tags.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#tags AwsProvider#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def transitive_tag_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Assume role session tag keys to pass to any subsequent sessions.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transitive_tag_keys AwsProvider#transitive_tag_keys}
        '''
        result = self._values.get("transitive_tag_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsProviderAssumeRole(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.AwsProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "region": "region",
        "access_key": "accessKey",
        "alias": "alias",
        "allowed_account_ids": "allowedAccountIds",
        "assume_role": "assumeRole",
        "default_tags": "defaultTags",
        "endpoints": "endpoints",
        "forbidden_account_ids": "forbiddenAccountIds",
        "http_proxy": "httpProxy",
        "ignore_tags": "ignoreTags",
        "insecure": "insecure",
        "max_retries": "maxRetries",
        "profile": "profile",
        "s3_force_path_style": "s3ForcePathStyle",
        "secret_key": "secretKey",
        "shared_credentials_file": "sharedCredentialsFile",
        "skip_credentials_validation": "skipCredentialsValidation",
        "skip_get_ec2_platforms": "skipGetEc2Platforms",
        "skip_metadata_api_check": "skipMetadataApiCheck",
        "skip_region_validation": "skipRegionValidation",
        "skip_requesting_account_id": "skipRequestingAccountId",
        "token": "token",
    },
)
class AwsProviderConfig:
    def __init__(
        self,
        *,
        region: builtins.str,
        access_key: typing.Optional[builtins.str] = None,
        alias: typing.Optional[builtins.str] = None,
        allowed_account_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        assume_role: typing.Optional[AwsProviderAssumeRole] = None,
        default_tags: typing.Optional["AwsProviderDefaultTags"] = None,
        endpoints: typing.Optional[typing.Sequence["AwsProviderEndpoints"]] = None,
        forbidden_account_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        http_proxy: typing.Optional[builtins.str] = None,
        ignore_tags: typing.Optional["AwsProviderIgnoreTags"] = None,
        insecure: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        max_retries: typing.Optional[jsii.Number] = None,
        profile: typing.Optional[builtins.str] = None,
        s3_force_path_style: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        secret_key: typing.Optional[builtins.str] = None,
        shared_credentials_file: typing.Optional[builtins.str] = None,
        skip_credentials_validation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_get_ec2_platforms: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_metadata_api_check: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_region_validation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        skip_requesting_account_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param region: The region where AWS operations will take place. Examples are us-east-1, us-west-2, etc. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#region AwsProvider#region}
        :param access_key: The access key for API operations. You can retrieve this from the 'Security & Credentials' section of the AWS console. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#access_key AwsProvider#access_key}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#alias AwsProvider#alias}
        :param allowed_account_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#allowed_account_ids AwsProvider#allowed_account_ids}.
        :param assume_role: assume_role block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#assume_role AwsProvider#assume_role}
        :param default_tags: default_tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#default_tags AwsProvider#default_tags}
        :param endpoints: endpoints block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#endpoints AwsProvider#endpoints}
        :param forbidden_account_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forbidden_account_ids AwsProvider#forbidden_account_ids}.
        :param http_proxy: The address of an HTTP proxy to use when accessing the AWS API. Can also be configured using the ``HTTP_PROXY`` or ``HTTPS_PROXY`` environment variables. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#http_proxy AwsProvider#http_proxy}
        :param ignore_tags: ignore_tags block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ignore_tags AwsProvider#ignore_tags}
        :param insecure: Explicitly allow the provider to perform "insecure" SSL requests. If omitted, default value is ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#insecure AwsProvider#insecure}
        :param max_retries: The maximum number of times an AWS API request is being executed. If the API request still fails, an error is thrown. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#max_retries AwsProvider#max_retries}
        :param profile: The profile for API operations. If not set, the default profile created with ``aws configure`` will be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#profile AwsProvider#profile}
        :param s3_force_path_style: Set this to true to force the request to use path-style addressing, i.e., http://s3.amazonaws.com/BUCKET/KEY. By default, the S3 client will use virtual hosted bucket addressing when possible (http://BUCKET.s3.amazonaws.com/KEY). Specific to the Amazon S3 service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#s3_force_path_style AwsProvider#s3_force_path_style}
        :param secret_key: The secret key for API operations. You can retrieve this from the 'Security & Credentials' section of the AWS console. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#secret_key AwsProvider#secret_key}
        :param shared_credentials_file: The path to the shared credentials file. If not set this defaults to ~/.aws/credentials. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#shared_credentials_file AwsProvider#shared_credentials_file}
        :param skip_credentials_validation: Skip the credentials validation via STS API. Used for AWS API implementations that do not have STS available/implemented. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_credentials_validation AwsProvider#skip_credentials_validation}
        :param skip_get_ec2_platforms: Skip getting the supported EC2 platforms. Used by users that don't have ec2:DescribeAccountAttributes permissions. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_get_ec2_platforms AwsProvider#skip_get_ec2_platforms}
        :param skip_metadata_api_check: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_metadata_api_check AwsProvider#skip_metadata_api_check}.
        :param skip_region_validation: Skip static validation of region name. Used by users of alternative AWS-like APIs or users w/ access to regions that are not public (yet). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_region_validation AwsProvider#skip_region_validation}
        :param skip_requesting_account_id: Skip requesting the account ID. Used for AWS API implementations that do not have IAM/STS API and/or metadata API. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_requesting_account_id AwsProvider#skip_requesting_account_id}
        :param token: session token. A session token is only required if you are using temporary security credentials. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#token AwsProvider#token}
        '''
        if isinstance(assume_role, dict):
            assume_role = AwsProviderAssumeRole(**assume_role)
        if isinstance(default_tags, dict):
            default_tags = AwsProviderDefaultTags(**default_tags)
        if isinstance(ignore_tags, dict):
            ignore_tags = AwsProviderIgnoreTags(**ignore_tags)
        self._values: typing.Dict[str, typing.Any] = {
            "region": region,
        }
        if access_key is not None:
            self._values["access_key"] = access_key
        if alias is not None:
            self._values["alias"] = alias
        if allowed_account_ids is not None:
            self._values["allowed_account_ids"] = allowed_account_ids
        if assume_role is not None:
            self._values["assume_role"] = assume_role
        if default_tags is not None:
            self._values["default_tags"] = default_tags
        if endpoints is not None:
            self._values["endpoints"] = endpoints
        if forbidden_account_ids is not None:
            self._values["forbidden_account_ids"] = forbidden_account_ids
        if http_proxy is not None:
            self._values["http_proxy"] = http_proxy
        if ignore_tags is not None:
            self._values["ignore_tags"] = ignore_tags
        if insecure is not None:
            self._values["insecure"] = insecure
        if max_retries is not None:
            self._values["max_retries"] = max_retries
        if profile is not None:
            self._values["profile"] = profile
        if s3_force_path_style is not None:
            self._values["s3_force_path_style"] = s3_force_path_style
        if secret_key is not None:
            self._values["secret_key"] = secret_key
        if shared_credentials_file is not None:
            self._values["shared_credentials_file"] = shared_credentials_file
        if skip_credentials_validation is not None:
            self._values["skip_credentials_validation"] = skip_credentials_validation
        if skip_get_ec2_platforms is not None:
            self._values["skip_get_ec2_platforms"] = skip_get_ec2_platforms
        if skip_metadata_api_check is not None:
            self._values["skip_metadata_api_check"] = skip_metadata_api_check
        if skip_region_validation is not None:
            self._values["skip_region_validation"] = skip_region_validation
        if skip_requesting_account_id is not None:
            self._values["skip_requesting_account_id"] = skip_requesting_account_id
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def region(self) -> builtins.str:
        '''The region where AWS operations will take place. Examples are us-east-1, us-west-2, etc.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#region AwsProvider#region}
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_key(self) -> typing.Optional[builtins.str]:
        '''The access key for API operations. You can retrieve this from the 'Security & Credentials' section of the AWS console.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#access_key AwsProvider#access_key}
        '''
        result = self._values.get("access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#alias AwsProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowed_account_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#allowed_account_ids AwsProvider#allowed_account_ids}.'''
        result = self._values.get("allowed_account_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def assume_role(self) -> typing.Optional[AwsProviderAssumeRole]:
        '''assume_role block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#assume_role AwsProvider#assume_role}
        '''
        result = self._values.get("assume_role")
        return typing.cast(typing.Optional[AwsProviderAssumeRole], result)

    @builtins.property
    def default_tags(self) -> typing.Optional["AwsProviderDefaultTags"]:
        '''default_tags block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#default_tags AwsProvider#default_tags}
        '''
        result = self._values.get("default_tags")
        return typing.cast(typing.Optional["AwsProviderDefaultTags"], result)

    @builtins.property
    def endpoints(self) -> typing.Optional[typing.List["AwsProviderEndpoints"]]:
        '''endpoints block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#endpoints AwsProvider#endpoints}
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[typing.List["AwsProviderEndpoints"]], result)

    @builtins.property
    def forbidden_account_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forbidden_account_ids AwsProvider#forbidden_account_ids}.'''
        result = self._values.get("forbidden_account_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def http_proxy(self) -> typing.Optional[builtins.str]:
        '''The address of an HTTP proxy to use when accessing the AWS API.

        Can also be configured using the ``HTTP_PROXY`` or ``HTTPS_PROXY`` environment variables.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#http_proxy AwsProvider#http_proxy}
        '''
        result = self._values.get("http_proxy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_tags(self) -> typing.Optional["AwsProviderIgnoreTags"]:
        '''ignore_tags block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ignore_tags AwsProvider#ignore_tags}
        '''
        result = self._values.get("ignore_tags")
        return typing.cast(typing.Optional["AwsProviderIgnoreTags"], result)

    @builtins.property
    def insecure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Explicitly allow the provider to perform "insecure" SSL requests. If omitted, default value is ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#insecure AwsProvider#insecure}
        '''
        result = self._values.get("insecure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def max_retries(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times an AWS API request is being executed.

        If the API request still fails, an error is
        thrown.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#max_retries AwsProvider#max_retries}
        '''
        result = self._values.get("max_retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''The profile for API operations. If not set, the default profile created with ``aws configure`` will be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#profile AwsProvider#profile}
        '''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_force_path_style(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Set this to true to force the request to use path-style addressing, i.e., http://s3.amazonaws.com/BUCKET/KEY. By default, the S3 client will use virtual hosted bucket addressing when possible (http://BUCKET.s3.amazonaws.com/KEY). Specific to the Amazon S3 service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#s3_force_path_style AwsProvider#s3_force_path_style}
        '''
        result = self._values.get("s3_force_path_style")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[builtins.str]:
        '''The secret key for API operations. You can retrieve this from the 'Security & Credentials' section of the AWS console.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#secret_key AwsProvider#secret_key}
        '''
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def shared_credentials_file(self) -> typing.Optional[builtins.str]:
        '''The path to the shared credentials file. If not set this defaults to ~/.aws/credentials.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#shared_credentials_file AwsProvider#shared_credentials_file}
        '''
        result = self._values.get("shared_credentials_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_credentials_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Skip the credentials validation via STS API. Used for AWS API implementations that do not have STS available/implemented.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_credentials_validation AwsProvider#skip_credentials_validation}
        '''
        result = self._values.get("skip_credentials_validation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def skip_get_ec2_platforms(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Skip getting the supported EC2 platforms. Used by users that don't have ec2:DescribeAccountAttributes permissions.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_get_ec2_platforms AwsProvider#skip_get_ec2_platforms}
        '''
        result = self._values.get("skip_get_ec2_platforms")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def skip_metadata_api_check(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_metadata_api_check AwsProvider#skip_metadata_api_check}.'''
        result = self._values.get("skip_metadata_api_check")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def skip_region_validation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Skip static validation of region name.

        Used by users of alternative AWS-like APIs or users w/ access to regions that are not public (yet).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_region_validation AwsProvider#skip_region_validation}
        '''
        result = self._values.get("skip_region_validation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def skip_requesting_account_id(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Skip requesting the account ID. Used for AWS API implementations that do not have IAM/STS API and/or metadata API.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#skip_requesting_account_id AwsProvider#skip_requesting_account_id}
        '''
        result = self._values.get("skip_requesting_account_id")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''session token. A session token is only required if you are using temporary security credentials.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#token AwsProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.AwsProviderDefaultTags",
    jsii_struct_bases=[],
    name_mapping={"tags": "tags"},
)
class AwsProviderDefaultTags:
    def __init__(
        self,
        *,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param tags: Resource tags to default across all resources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#tags AwsProvider#tags}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Resource tags to default across all resources.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#tags AwsProvider#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsProviderDefaultTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.AwsProviderEndpoints",
    jsii_struct_bases=[],
    name_mapping={
        "accessanalyzer": "accessanalyzer",
        "account": "account",
        "acm": "acm",
        "acmpca": "acmpca",
        "alexaforbusiness": "alexaforbusiness",
        "amp": "amp",
        "amplify": "amplify",
        "amplifybackend": "amplifybackend",
        "apigateway": "apigateway",
        "apigatewayv2": "apigatewayv2",
        "appautoscaling": "appautoscaling",
        "appconfig": "appconfig",
        "appflow": "appflow",
        "appintegrations": "appintegrations",
        "appintegrationsservice": "appintegrationsservice",
        "applicationautoscaling": "applicationautoscaling",
        "applicationcostprofiler": "applicationcostprofiler",
        "applicationdiscovery": "applicationdiscovery",
        "applicationdiscoveryservice": "applicationdiscoveryservice",
        "applicationinsights": "applicationinsights",
        "appmesh": "appmesh",
        "appregistry": "appregistry",
        "apprunner": "apprunner",
        "appstream": "appstream",
        "appsync": "appsync",
        "athena": "athena",
        "auditmanager": "auditmanager",
        "augmentedairuntime": "augmentedairuntime",
        "autoscaling": "autoscaling",
        "autoscalingplans": "autoscalingplans",
        "backup": "backup",
        "batch": "batch",
        "braket": "braket",
        "budgets": "budgets",
        "chime": "chime",
        "cloud9": "cloud9",
        "cloudcontrol": "cloudcontrol",
        "cloudcontrolapi": "cloudcontrolapi",
        "clouddirectory": "clouddirectory",
        "cloudformation": "cloudformation",
        "cloudfront": "cloudfront",
        "cloudhsm": "cloudhsm",
        "cloudhsmv2": "cloudhsmv2",
        "cloudsearch": "cloudsearch",
        "cloudsearchdomain": "cloudsearchdomain",
        "cloudtrail": "cloudtrail",
        "cloudwatch": "cloudwatch",
        "cloudwatchevents": "cloudwatchevents",
        "cloudwatchlogs": "cloudwatchlogs",
        "codeartifact": "codeartifact",
        "codebuild": "codebuild",
        "codecommit": "codecommit",
        "codedeploy": "codedeploy",
        "codeguruprofiler": "codeguruprofiler",
        "codegurureviewer": "codegurureviewer",
        "codepipeline": "codepipeline",
        "codestar": "codestar",
        "codestarconnections": "codestarconnections",
        "codestarnotifications": "codestarnotifications",
        "cognitoidentity": "cognitoidentity",
        "cognitoidentityprovider": "cognitoidentityprovider",
        "cognitoidp": "cognitoidp",
        "cognitosync": "cognitosync",
        "comprehend": "comprehend",
        "comprehendmedical": "comprehendmedical",
        "config": "config",
        "configservice": "configservice",
        "connect": "connect",
        "connectcontactlens": "connectcontactlens",
        "connectparticipant": "connectparticipant",
        "costandusagereportservice": "costandusagereportservice",
        "costexplorer": "costexplorer",
        "cur": "cur",
        "databasemigration": "databasemigration",
        "databasemigrationservice": "databasemigrationservice",
        "dataexchange": "dataexchange",
        "datapipeline": "datapipeline",
        "datasync": "datasync",
        "dax": "dax",
        "detective": "detective",
        "devicefarm": "devicefarm",
        "devopsguru": "devopsguru",
        "directconnect": "directconnect",
        "dlm": "dlm",
        "dms": "dms",
        "docdb": "docdb",
        "ds": "ds",
        "dynamodb": "dynamodb",
        "dynamodbstreams": "dynamodbstreams",
        "ec2": "ec2",
        "ec2_instanceconnect": "ec2Instanceconnect",
        "ecr": "ecr",
        "ecrpublic": "ecrpublic",
        "ecs": "ecs",
        "efs": "efs",
        "eks": "eks",
        "elasticache": "elasticache",
        "elasticbeanstalk": "elasticbeanstalk",
        "elasticinference": "elasticinference",
        "elasticsearch": "elasticsearch",
        "elasticsearchservice": "elasticsearchservice",
        "elastictranscoder": "elastictranscoder",
        "elb": "elb",
        "elbv2": "elbv2",
        "emr": "emr",
        "emrcontainers": "emrcontainers",
        "es": "es",
        "eventbridge": "eventbridge",
        "events": "events",
        "finspace": "finspace",
        "finspacedata": "finspacedata",
        "firehose": "firehose",
        "fis": "fis",
        "fms": "fms",
        "forecast": "forecast",
        "forecastquery": "forecastquery",
        "forecastqueryservice": "forecastqueryservice",
        "forecastservice": "forecastservice",
        "frauddetector": "frauddetector",
        "fsx": "fsx",
        "gamelift": "gamelift",
        "glacier": "glacier",
        "globalaccelerator": "globalaccelerator",
        "glue": "glue",
        "gluedatabrew": "gluedatabrew",
        "greengrass": "greengrass",
        "greengrassv2": "greengrassv2",
        "groundstation": "groundstation",
        "guardduty": "guardduty",
        "health": "health",
        "healthlake": "healthlake",
        "honeycode": "honeycode",
        "iam": "iam",
        "identitystore": "identitystore",
        "imagebuilder": "imagebuilder",
        "inspector": "inspector",
        "iot": "iot",
        "iot1_clickdevices": "iot1Clickdevices",
        "iot1_clickdevicesservice": "iot1Clickdevicesservice",
        "iot1_clickprojects": "iot1Clickprojects",
        "iotanalytics": "iotanalytics",
        "iotdataplane": "iotdataplane",
        "iotdeviceadvisor": "iotdeviceadvisor",
        "iotevents": "iotevents",
        "ioteventsdata": "ioteventsdata",
        "iotfleethub": "iotfleethub",
        "iotjobsdataplane": "iotjobsdataplane",
        "iotsecuretunneling": "iotsecuretunneling",
        "iotsitewise": "iotsitewise",
        "iotthingsgraph": "iotthingsgraph",
        "iotwireless": "iotwireless",
        "kafka": "kafka",
        "kafkaconnect": "kafkaconnect",
        "kendra": "kendra",
        "kinesis": "kinesis",
        "kinesisanalytics": "kinesisanalytics",
        "kinesisanalyticsv2": "kinesisanalyticsv2",
        "kinesisvideo": "kinesisvideo",
        "kinesisvideoarchivedmedia": "kinesisvideoarchivedmedia",
        "kinesisvideomedia": "kinesisvideomedia",
        "kinesisvideosignalingchannels": "kinesisvideosignalingchannels",
        "kms": "kms",
        "lakeformation": "lakeformation",
        "lambda_": "lambda",
        "lexmodelbuilding": "lexmodelbuilding",
        "lexmodelbuildingservice": "lexmodelbuildingservice",
        "lexmodels": "lexmodels",
        "lexmodelsv2": "lexmodelsv2",
        "lexruntime": "lexruntime",
        "lexruntimeservice": "lexruntimeservice",
        "lexruntimev2": "lexruntimev2",
        "licensemanager": "licensemanager",
        "lightsail": "lightsail",
        "location": "location",
        "lookoutequipment": "lookoutequipment",
        "lookoutforvision": "lookoutforvision",
        "lookoutmetrics": "lookoutmetrics",
        "machinelearning": "machinelearning",
        "macie": "macie",
        "macie2": "macie2",
        "managedblockchain": "managedblockchain",
        "marketplacecatalog": "marketplacecatalog",
        "marketplacecommerceanalytics": "marketplacecommerceanalytics",
        "marketplaceentitlement": "marketplaceentitlement",
        "marketplaceentitlementservice": "marketplaceentitlementservice",
        "marketplacemetering": "marketplacemetering",
        "mediaconnect": "mediaconnect",
        "mediaconvert": "mediaconvert",
        "medialive": "medialive",
        "mediapackage": "mediapackage",
        "mediapackagevod": "mediapackagevod",
        "mediastore": "mediastore",
        "mediastoredata": "mediastoredata",
        "mediatailor": "mediatailor",
        "memorydb": "memorydb",
        "mgn": "mgn",
        "migrationhub": "migrationhub",
        "migrationhubconfig": "migrationhubconfig",
        "mobile": "mobile",
        "mobileanalytics": "mobileanalytics",
        "mq": "mq",
        "mturk": "mturk",
        "mwaa": "mwaa",
        "neptune": "neptune",
        "networkfirewall": "networkfirewall",
        "networkmanager": "networkmanager",
        "nimblestudio": "nimblestudio",
        "opsworks": "opsworks",
        "opsworkscm": "opsworkscm",
        "organizations": "organizations",
        "outposts": "outposts",
        "personalize": "personalize",
        "personalizeevents": "personalizeevents",
        "personalizeruntime": "personalizeruntime",
        "pi": "pi",
        "pinpoint": "pinpoint",
        "pinpointemail": "pinpointemail",
        "pinpointsmsvoice": "pinpointsmsvoice",
        "polly": "polly",
        "pricing": "pricing",
        "prometheus": "prometheus",
        "prometheusservice": "prometheusservice",
        "proton": "proton",
        "qldb": "qldb",
        "qldbsession": "qldbsession",
        "quicksight": "quicksight",
        "ram": "ram",
        "rds": "rds",
        "rdsdata": "rdsdata",
        "rdsdataservice": "rdsdataservice",
        "redshift": "redshift",
        "redshiftdata": "redshiftdata",
        "rekognition": "rekognition",
        "resourcegroups": "resourcegroups",
        "resourcegroupstagging": "resourcegroupstagging",
        "resourcegroupstaggingapi": "resourcegroupstaggingapi",
        "robomaker": "robomaker",
        "route53": "route53",
        "route53_domains": "route53Domains",
        "route53_recoverycontrolconfig": "route53Recoverycontrolconfig",
        "route53_recoveryreadiness": "route53Recoveryreadiness",
        "route53_resolver": "route53Resolver",
        "s3": "s3",
        "s3_control": "s3Control",
        "s3_outposts": "s3Outposts",
        "sagemaker": "sagemaker",
        "sagemakeredgemanager": "sagemakeredgemanager",
        "sagemakerfeaturestoreruntime": "sagemakerfeaturestoreruntime",
        "sagemakerruntime": "sagemakerruntime",
        "savingsplans": "savingsplans",
        "schemas": "schemas",
        "sdb": "sdb",
        "secretsmanager": "secretsmanager",
        "securityhub": "securityhub",
        "serverlessapplicationrepository": "serverlessapplicationrepository",
        "serverlessapprepo": "serverlessapprepo",
        "serverlessrepo": "serverlessrepo",
        "servicecatalog": "servicecatalog",
        "servicediscovery": "servicediscovery",
        "servicequotas": "servicequotas",
        "ses": "ses",
        "sesv2": "sesv2",
        "sfn": "sfn",
        "shield": "shield",
        "signer": "signer",
        "simpledb": "simpledb",
        "sms": "sms",
        "snowball": "snowball",
        "sns": "sns",
        "sqs": "sqs",
        "ssm": "ssm",
        "ssmcontacts": "ssmcontacts",
        "ssmincidents": "ssmincidents",
        "sso": "sso",
        "ssoadmin": "ssoadmin",
        "ssooidc": "ssooidc",
        "stepfunctions": "stepfunctions",
        "storagegateway": "storagegateway",
        "sts": "sts",
        "support": "support",
        "swf": "swf",
        "synthetics": "synthetics",
        "textract": "textract",
        "timestreamquery": "timestreamquery",
        "timestreamwrite": "timestreamwrite",
        "transcribe": "transcribe",
        "transcribeservice": "transcribeservice",
        "transcribestreaming": "transcribestreaming",
        "transcribestreamingservice": "transcribestreamingservice",
        "transfer": "transfer",
        "translate": "translate",
        "waf": "waf",
        "wafregional": "wafregional",
        "wafv2": "wafv2",
        "wellarchitected": "wellarchitected",
        "workdocs": "workdocs",
        "worklink": "worklink",
        "workmail": "workmail",
        "workmailmessageflow": "workmailmessageflow",
        "workspaces": "workspaces",
        "xray": "xray",
    },
)
class AwsProviderEndpoints:
    def __init__(
        self,
        *,
        accessanalyzer: typing.Optional[builtins.str] = None,
        account: typing.Optional[builtins.str] = None,
        acm: typing.Optional[builtins.str] = None,
        acmpca: typing.Optional[builtins.str] = None,
        alexaforbusiness: typing.Optional[builtins.str] = None,
        amp: typing.Optional[builtins.str] = None,
        amplify: typing.Optional[builtins.str] = None,
        amplifybackend: typing.Optional[builtins.str] = None,
        apigateway: typing.Optional[builtins.str] = None,
        apigatewayv2: typing.Optional[builtins.str] = None,
        appautoscaling: typing.Optional[builtins.str] = None,
        appconfig: typing.Optional[builtins.str] = None,
        appflow: typing.Optional[builtins.str] = None,
        appintegrations: typing.Optional[builtins.str] = None,
        appintegrationsservice: typing.Optional[builtins.str] = None,
        applicationautoscaling: typing.Optional[builtins.str] = None,
        applicationcostprofiler: typing.Optional[builtins.str] = None,
        applicationdiscovery: typing.Optional[builtins.str] = None,
        applicationdiscoveryservice: typing.Optional[builtins.str] = None,
        applicationinsights: typing.Optional[builtins.str] = None,
        appmesh: typing.Optional[builtins.str] = None,
        appregistry: typing.Optional[builtins.str] = None,
        apprunner: typing.Optional[builtins.str] = None,
        appstream: typing.Optional[builtins.str] = None,
        appsync: typing.Optional[builtins.str] = None,
        athena: typing.Optional[builtins.str] = None,
        auditmanager: typing.Optional[builtins.str] = None,
        augmentedairuntime: typing.Optional[builtins.str] = None,
        autoscaling: typing.Optional[builtins.str] = None,
        autoscalingplans: typing.Optional[builtins.str] = None,
        backup: typing.Optional[builtins.str] = None,
        batch: typing.Optional[builtins.str] = None,
        braket: typing.Optional[builtins.str] = None,
        budgets: typing.Optional[builtins.str] = None,
        chime: typing.Optional[builtins.str] = None,
        cloud9: typing.Optional[builtins.str] = None,
        cloudcontrol: typing.Optional[builtins.str] = None,
        cloudcontrolapi: typing.Optional[builtins.str] = None,
        clouddirectory: typing.Optional[builtins.str] = None,
        cloudformation: typing.Optional[builtins.str] = None,
        cloudfront: typing.Optional[builtins.str] = None,
        cloudhsm: typing.Optional[builtins.str] = None,
        cloudhsmv2: typing.Optional[builtins.str] = None,
        cloudsearch: typing.Optional[builtins.str] = None,
        cloudsearchdomain: typing.Optional[builtins.str] = None,
        cloudtrail: typing.Optional[builtins.str] = None,
        cloudwatch: typing.Optional[builtins.str] = None,
        cloudwatchevents: typing.Optional[builtins.str] = None,
        cloudwatchlogs: typing.Optional[builtins.str] = None,
        codeartifact: typing.Optional[builtins.str] = None,
        codebuild: typing.Optional[builtins.str] = None,
        codecommit: typing.Optional[builtins.str] = None,
        codedeploy: typing.Optional[builtins.str] = None,
        codeguruprofiler: typing.Optional[builtins.str] = None,
        codegurureviewer: typing.Optional[builtins.str] = None,
        codepipeline: typing.Optional[builtins.str] = None,
        codestar: typing.Optional[builtins.str] = None,
        codestarconnections: typing.Optional[builtins.str] = None,
        codestarnotifications: typing.Optional[builtins.str] = None,
        cognitoidentity: typing.Optional[builtins.str] = None,
        cognitoidentityprovider: typing.Optional[builtins.str] = None,
        cognitoidp: typing.Optional[builtins.str] = None,
        cognitosync: typing.Optional[builtins.str] = None,
        comprehend: typing.Optional[builtins.str] = None,
        comprehendmedical: typing.Optional[builtins.str] = None,
        config: typing.Optional[builtins.str] = None,
        configservice: typing.Optional[builtins.str] = None,
        connect: typing.Optional[builtins.str] = None,
        connectcontactlens: typing.Optional[builtins.str] = None,
        connectparticipant: typing.Optional[builtins.str] = None,
        costandusagereportservice: typing.Optional[builtins.str] = None,
        costexplorer: typing.Optional[builtins.str] = None,
        cur: typing.Optional[builtins.str] = None,
        databasemigration: typing.Optional[builtins.str] = None,
        databasemigrationservice: typing.Optional[builtins.str] = None,
        dataexchange: typing.Optional[builtins.str] = None,
        datapipeline: typing.Optional[builtins.str] = None,
        datasync: typing.Optional[builtins.str] = None,
        dax: typing.Optional[builtins.str] = None,
        detective: typing.Optional[builtins.str] = None,
        devicefarm: typing.Optional[builtins.str] = None,
        devopsguru: typing.Optional[builtins.str] = None,
        directconnect: typing.Optional[builtins.str] = None,
        dlm: typing.Optional[builtins.str] = None,
        dms: typing.Optional[builtins.str] = None,
        docdb: typing.Optional[builtins.str] = None,
        ds: typing.Optional[builtins.str] = None,
        dynamodb: typing.Optional[builtins.str] = None,
        dynamodbstreams: typing.Optional[builtins.str] = None,
        ec2: typing.Optional[builtins.str] = None,
        ec2_instanceconnect: typing.Optional[builtins.str] = None,
        ecr: typing.Optional[builtins.str] = None,
        ecrpublic: typing.Optional[builtins.str] = None,
        ecs: typing.Optional[builtins.str] = None,
        efs: typing.Optional[builtins.str] = None,
        eks: typing.Optional[builtins.str] = None,
        elasticache: typing.Optional[builtins.str] = None,
        elasticbeanstalk: typing.Optional[builtins.str] = None,
        elasticinference: typing.Optional[builtins.str] = None,
        elasticsearch: typing.Optional[builtins.str] = None,
        elasticsearchservice: typing.Optional[builtins.str] = None,
        elastictranscoder: typing.Optional[builtins.str] = None,
        elb: typing.Optional[builtins.str] = None,
        elbv2: typing.Optional[builtins.str] = None,
        emr: typing.Optional[builtins.str] = None,
        emrcontainers: typing.Optional[builtins.str] = None,
        es: typing.Optional[builtins.str] = None,
        eventbridge: typing.Optional[builtins.str] = None,
        events: typing.Optional[builtins.str] = None,
        finspace: typing.Optional[builtins.str] = None,
        finspacedata: typing.Optional[builtins.str] = None,
        firehose: typing.Optional[builtins.str] = None,
        fis: typing.Optional[builtins.str] = None,
        fms: typing.Optional[builtins.str] = None,
        forecast: typing.Optional[builtins.str] = None,
        forecastquery: typing.Optional[builtins.str] = None,
        forecastqueryservice: typing.Optional[builtins.str] = None,
        forecastservice: typing.Optional[builtins.str] = None,
        frauddetector: typing.Optional[builtins.str] = None,
        fsx: typing.Optional[builtins.str] = None,
        gamelift: typing.Optional[builtins.str] = None,
        glacier: typing.Optional[builtins.str] = None,
        globalaccelerator: typing.Optional[builtins.str] = None,
        glue: typing.Optional[builtins.str] = None,
        gluedatabrew: typing.Optional[builtins.str] = None,
        greengrass: typing.Optional[builtins.str] = None,
        greengrassv2: typing.Optional[builtins.str] = None,
        groundstation: typing.Optional[builtins.str] = None,
        guardduty: typing.Optional[builtins.str] = None,
        health: typing.Optional[builtins.str] = None,
        healthlake: typing.Optional[builtins.str] = None,
        honeycode: typing.Optional[builtins.str] = None,
        iam: typing.Optional[builtins.str] = None,
        identitystore: typing.Optional[builtins.str] = None,
        imagebuilder: typing.Optional[builtins.str] = None,
        inspector: typing.Optional[builtins.str] = None,
        iot: typing.Optional[builtins.str] = None,
        iot1_clickdevices: typing.Optional[builtins.str] = None,
        iot1_clickdevicesservice: typing.Optional[builtins.str] = None,
        iot1_clickprojects: typing.Optional[builtins.str] = None,
        iotanalytics: typing.Optional[builtins.str] = None,
        iotdataplane: typing.Optional[builtins.str] = None,
        iotdeviceadvisor: typing.Optional[builtins.str] = None,
        iotevents: typing.Optional[builtins.str] = None,
        ioteventsdata: typing.Optional[builtins.str] = None,
        iotfleethub: typing.Optional[builtins.str] = None,
        iotjobsdataplane: typing.Optional[builtins.str] = None,
        iotsecuretunneling: typing.Optional[builtins.str] = None,
        iotsitewise: typing.Optional[builtins.str] = None,
        iotthingsgraph: typing.Optional[builtins.str] = None,
        iotwireless: typing.Optional[builtins.str] = None,
        kafka: typing.Optional[builtins.str] = None,
        kafkaconnect: typing.Optional[builtins.str] = None,
        kendra: typing.Optional[builtins.str] = None,
        kinesis: typing.Optional[builtins.str] = None,
        kinesisanalytics: typing.Optional[builtins.str] = None,
        kinesisanalyticsv2: typing.Optional[builtins.str] = None,
        kinesisvideo: typing.Optional[builtins.str] = None,
        kinesisvideoarchivedmedia: typing.Optional[builtins.str] = None,
        kinesisvideomedia: typing.Optional[builtins.str] = None,
        kinesisvideosignalingchannels: typing.Optional[builtins.str] = None,
        kms: typing.Optional[builtins.str] = None,
        lakeformation: typing.Optional[builtins.str] = None,
        lambda_: typing.Optional[builtins.str] = None,
        lexmodelbuilding: typing.Optional[builtins.str] = None,
        lexmodelbuildingservice: typing.Optional[builtins.str] = None,
        lexmodels: typing.Optional[builtins.str] = None,
        lexmodelsv2: typing.Optional[builtins.str] = None,
        lexruntime: typing.Optional[builtins.str] = None,
        lexruntimeservice: typing.Optional[builtins.str] = None,
        lexruntimev2: typing.Optional[builtins.str] = None,
        licensemanager: typing.Optional[builtins.str] = None,
        lightsail: typing.Optional[builtins.str] = None,
        location: typing.Optional[builtins.str] = None,
        lookoutequipment: typing.Optional[builtins.str] = None,
        lookoutforvision: typing.Optional[builtins.str] = None,
        lookoutmetrics: typing.Optional[builtins.str] = None,
        machinelearning: typing.Optional[builtins.str] = None,
        macie: typing.Optional[builtins.str] = None,
        macie2: typing.Optional[builtins.str] = None,
        managedblockchain: typing.Optional[builtins.str] = None,
        marketplacecatalog: typing.Optional[builtins.str] = None,
        marketplacecommerceanalytics: typing.Optional[builtins.str] = None,
        marketplaceentitlement: typing.Optional[builtins.str] = None,
        marketplaceentitlementservice: typing.Optional[builtins.str] = None,
        marketplacemetering: typing.Optional[builtins.str] = None,
        mediaconnect: typing.Optional[builtins.str] = None,
        mediaconvert: typing.Optional[builtins.str] = None,
        medialive: typing.Optional[builtins.str] = None,
        mediapackage: typing.Optional[builtins.str] = None,
        mediapackagevod: typing.Optional[builtins.str] = None,
        mediastore: typing.Optional[builtins.str] = None,
        mediastoredata: typing.Optional[builtins.str] = None,
        mediatailor: typing.Optional[builtins.str] = None,
        memorydb: typing.Optional[builtins.str] = None,
        mgn: typing.Optional[builtins.str] = None,
        migrationhub: typing.Optional[builtins.str] = None,
        migrationhubconfig: typing.Optional[builtins.str] = None,
        mobile: typing.Optional[builtins.str] = None,
        mobileanalytics: typing.Optional[builtins.str] = None,
        mq: typing.Optional[builtins.str] = None,
        mturk: typing.Optional[builtins.str] = None,
        mwaa: typing.Optional[builtins.str] = None,
        neptune: typing.Optional[builtins.str] = None,
        networkfirewall: typing.Optional[builtins.str] = None,
        networkmanager: typing.Optional[builtins.str] = None,
        nimblestudio: typing.Optional[builtins.str] = None,
        opsworks: typing.Optional[builtins.str] = None,
        opsworkscm: typing.Optional[builtins.str] = None,
        organizations: typing.Optional[builtins.str] = None,
        outposts: typing.Optional[builtins.str] = None,
        personalize: typing.Optional[builtins.str] = None,
        personalizeevents: typing.Optional[builtins.str] = None,
        personalizeruntime: typing.Optional[builtins.str] = None,
        pi: typing.Optional[builtins.str] = None,
        pinpoint: typing.Optional[builtins.str] = None,
        pinpointemail: typing.Optional[builtins.str] = None,
        pinpointsmsvoice: typing.Optional[builtins.str] = None,
        polly: typing.Optional[builtins.str] = None,
        pricing: typing.Optional[builtins.str] = None,
        prometheus: typing.Optional[builtins.str] = None,
        prometheusservice: typing.Optional[builtins.str] = None,
        proton: typing.Optional[builtins.str] = None,
        qldb: typing.Optional[builtins.str] = None,
        qldbsession: typing.Optional[builtins.str] = None,
        quicksight: typing.Optional[builtins.str] = None,
        ram: typing.Optional[builtins.str] = None,
        rds: typing.Optional[builtins.str] = None,
        rdsdata: typing.Optional[builtins.str] = None,
        rdsdataservice: typing.Optional[builtins.str] = None,
        redshift: typing.Optional[builtins.str] = None,
        redshiftdata: typing.Optional[builtins.str] = None,
        rekognition: typing.Optional[builtins.str] = None,
        resourcegroups: typing.Optional[builtins.str] = None,
        resourcegroupstagging: typing.Optional[builtins.str] = None,
        resourcegroupstaggingapi: typing.Optional[builtins.str] = None,
        robomaker: typing.Optional[builtins.str] = None,
        route53: typing.Optional[builtins.str] = None,
        route53_domains: typing.Optional[builtins.str] = None,
        route53_recoverycontrolconfig: typing.Optional[builtins.str] = None,
        route53_recoveryreadiness: typing.Optional[builtins.str] = None,
        route53_resolver: typing.Optional[builtins.str] = None,
        s3: typing.Optional[builtins.str] = None,
        s3_control: typing.Optional[builtins.str] = None,
        s3_outposts: typing.Optional[builtins.str] = None,
        sagemaker: typing.Optional[builtins.str] = None,
        sagemakeredgemanager: typing.Optional[builtins.str] = None,
        sagemakerfeaturestoreruntime: typing.Optional[builtins.str] = None,
        sagemakerruntime: typing.Optional[builtins.str] = None,
        savingsplans: typing.Optional[builtins.str] = None,
        schemas: typing.Optional[builtins.str] = None,
        sdb: typing.Optional[builtins.str] = None,
        secretsmanager: typing.Optional[builtins.str] = None,
        securityhub: typing.Optional[builtins.str] = None,
        serverlessapplicationrepository: typing.Optional[builtins.str] = None,
        serverlessapprepo: typing.Optional[builtins.str] = None,
        serverlessrepo: typing.Optional[builtins.str] = None,
        servicecatalog: typing.Optional[builtins.str] = None,
        servicediscovery: typing.Optional[builtins.str] = None,
        servicequotas: typing.Optional[builtins.str] = None,
        ses: typing.Optional[builtins.str] = None,
        sesv2: typing.Optional[builtins.str] = None,
        sfn: typing.Optional[builtins.str] = None,
        shield: typing.Optional[builtins.str] = None,
        signer: typing.Optional[builtins.str] = None,
        simpledb: typing.Optional[builtins.str] = None,
        sms: typing.Optional[builtins.str] = None,
        snowball: typing.Optional[builtins.str] = None,
        sns: typing.Optional[builtins.str] = None,
        sqs: typing.Optional[builtins.str] = None,
        ssm: typing.Optional[builtins.str] = None,
        ssmcontacts: typing.Optional[builtins.str] = None,
        ssmincidents: typing.Optional[builtins.str] = None,
        sso: typing.Optional[builtins.str] = None,
        ssoadmin: typing.Optional[builtins.str] = None,
        ssooidc: typing.Optional[builtins.str] = None,
        stepfunctions: typing.Optional[builtins.str] = None,
        storagegateway: typing.Optional[builtins.str] = None,
        sts: typing.Optional[builtins.str] = None,
        support: typing.Optional[builtins.str] = None,
        swf: typing.Optional[builtins.str] = None,
        synthetics: typing.Optional[builtins.str] = None,
        textract: typing.Optional[builtins.str] = None,
        timestreamquery: typing.Optional[builtins.str] = None,
        timestreamwrite: typing.Optional[builtins.str] = None,
        transcribe: typing.Optional[builtins.str] = None,
        transcribeservice: typing.Optional[builtins.str] = None,
        transcribestreaming: typing.Optional[builtins.str] = None,
        transcribestreamingservice: typing.Optional[builtins.str] = None,
        transfer: typing.Optional[builtins.str] = None,
        translate: typing.Optional[builtins.str] = None,
        waf: typing.Optional[builtins.str] = None,
        wafregional: typing.Optional[builtins.str] = None,
        wafv2: typing.Optional[builtins.str] = None,
        wellarchitected: typing.Optional[builtins.str] = None,
        workdocs: typing.Optional[builtins.str] = None,
        worklink: typing.Optional[builtins.str] = None,
        workmail: typing.Optional[builtins.str] = None,
        workmailmessageflow: typing.Optional[builtins.str] = None,
        workspaces: typing.Optional[builtins.str] = None,
        xray: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param accessanalyzer: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#accessanalyzer AwsProvider#accessanalyzer}
        :param account: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#account AwsProvider#account}
        :param acm: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#acm AwsProvider#acm}
        :param acmpca: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#acmpca AwsProvider#acmpca}
        :param alexaforbusiness: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#alexaforbusiness AwsProvider#alexaforbusiness}
        :param amp: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#amp AwsProvider#amp}
        :param amplify: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#amplify AwsProvider#amplify}
        :param amplifybackend: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#amplifybackend AwsProvider#amplifybackend}
        :param apigateway: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#apigateway AwsProvider#apigateway}
        :param apigatewayv2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#apigatewayv2 AwsProvider#apigatewayv2}
        :param appautoscaling: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appautoscaling AwsProvider#appautoscaling}
        :param appconfig: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appconfig AwsProvider#appconfig}
        :param appflow: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appflow AwsProvider#appflow}
        :param appintegrations: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appintegrations AwsProvider#appintegrations}
        :param appintegrationsservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appintegrationsservice AwsProvider#appintegrationsservice}
        :param applicationautoscaling: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationautoscaling AwsProvider#applicationautoscaling}
        :param applicationcostprofiler: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationcostprofiler AwsProvider#applicationcostprofiler}
        :param applicationdiscovery: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationdiscovery AwsProvider#applicationdiscovery}
        :param applicationdiscoveryservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationdiscoveryservice AwsProvider#applicationdiscoveryservice}
        :param applicationinsights: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationinsights AwsProvider#applicationinsights}
        :param appmesh: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appmesh AwsProvider#appmesh}
        :param appregistry: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appregistry AwsProvider#appregistry}
        :param apprunner: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#apprunner AwsProvider#apprunner}
        :param appstream: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appstream AwsProvider#appstream}
        :param appsync: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appsync AwsProvider#appsync}
        :param athena: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#athena AwsProvider#athena}
        :param auditmanager: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#auditmanager AwsProvider#auditmanager}
        :param augmentedairuntime: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#augmentedairuntime AwsProvider#augmentedairuntime}
        :param autoscaling: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#autoscaling AwsProvider#autoscaling}
        :param autoscalingplans: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#autoscalingplans AwsProvider#autoscalingplans}
        :param backup: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#backup AwsProvider#backup}
        :param batch: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#batch AwsProvider#batch}
        :param braket: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#braket AwsProvider#braket}
        :param budgets: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#budgets AwsProvider#budgets}
        :param chime: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#chime AwsProvider#chime}
        :param cloud9: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloud9 AwsProvider#cloud9}
        :param cloudcontrol: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudcontrol AwsProvider#cloudcontrol}
        :param cloudcontrolapi: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudcontrolapi AwsProvider#cloudcontrolapi}
        :param clouddirectory: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#clouddirectory AwsProvider#clouddirectory}
        :param cloudformation: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudformation AwsProvider#cloudformation}
        :param cloudfront: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudfront AwsProvider#cloudfront}
        :param cloudhsm: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudhsm AwsProvider#cloudhsm}
        :param cloudhsmv2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudhsmv2 AwsProvider#cloudhsmv2}
        :param cloudsearch: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudsearch AwsProvider#cloudsearch}
        :param cloudsearchdomain: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudsearchdomain AwsProvider#cloudsearchdomain}
        :param cloudtrail: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudtrail AwsProvider#cloudtrail}
        :param cloudwatch: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudwatch AwsProvider#cloudwatch}
        :param cloudwatchevents: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudwatchevents AwsProvider#cloudwatchevents}
        :param cloudwatchlogs: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudwatchlogs AwsProvider#cloudwatchlogs}
        :param codeartifact: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codeartifact AwsProvider#codeartifact}
        :param codebuild: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codebuild AwsProvider#codebuild}
        :param codecommit: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codecommit AwsProvider#codecommit}
        :param codedeploy: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codedeploy AwsProvider#codedeploy}
        :param codeguruprofiler: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codeguruprofiler AwsProvider#codeguruprofiler}
        :param codegurureviewer: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codegurureviewer AwsProvider#codegurureviewer}
        :param codepipeline: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codepipeline AwsProvider#codepipeline}
        :param codestar: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codestar AwsProvider#codestar}
        :param codestarconnections: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codestarconnections AwsProvider#codestarconnections}
        :param codestarnotifications: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codestarnotifications AwsProvider#codestarnotifications}
        :param cognitoidentity: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cognitoidentity AwsProvider#cognitoidentity}
        :param cognitoidentityprovider: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cognitoidentityprovider AwsProvider#cognitoidentityprovider}
        :param cognitoidp: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cognitoidp AwsProvider#cognitoidp}
        :param cognitosync: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cognitosync AwsProvider#cognitosync}
        :param comprehend: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#comprehend AwsProvider#comprehend}
        :param comprehendmedical: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#comprehendmedical AwsProvider#comprehendmedical}
        :param config: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#config AwsProvider#config}
        :param configservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#configservice AwsProvider#configservice}
        :param connect: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#connect AwsProvider#connect}
        :param connectcontactlens: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#connectcontactlens AwsProvider#connectcontactlens}
        :param connectparticipant: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#connectparticipant AwsProvider#connectparticipant}
        :param costandusagereportservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#costandusagereportservice AwsProvider#costandusagereportservice}
        :param costexplorer: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#costexplorer AwsProvider#costexplorer}
        :param cur: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cur AwsProvider#cur}
        :param databasemigration: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#databasemigration AwsProvider#databasemigration}
        :param databasemigrationservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#databasemigrationservice AwsProvider#databasemigrationservice}
        :param dataexchange: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dataexchange AwsProvider#dataexchange}
        :param datapipeline: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#datapipeline AwsProvider#datapipeline}
        :param datasync: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#datasync AwsProvider#datasync}
        :param dax: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dax AwsProvider#dax}
        :param detective: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#detective AwsProvider#detective}
        :param devicefarm: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#devicefarm AwsProvider#devicefarm}
        :param devopsguru: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#devopsguru AwsProvider#devopsguru}
        :param directconnect: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#directconnect AwsProvider#directconnect}
        :param dlm: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dlm AwsProvider#dlm}
        :param dms: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dms AwsProvider#dms}
        :param docdb: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#docdb AwsProvider#docdb}
        :param ds: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ds AwsProvider#ds}
        :param dynamodb: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dynamodb AwsProvider#dynamodb}
        :param dynamodbstreams: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dynamodbstreams AwsProvider#dynamodbstreams}
        :param ec2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ec2 AwsProvider#ec2}
        :param ec2_instanceconnect: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ec2instanceconnect AwsProvider#ec2instanceconnect}
        :param ecr: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ecr AwsProvider#ecr}
        :param ecrpublic: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ecrpublic AwsProvider#ecrpublic}
        :param ecs: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ecs AwsProvider#ecs}
        :param efs: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#efs AwsProvider#efs}
        :param eks: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#eks AwsProvider#eks}
        :param elasticache: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticache AwsProvider#elasticache}
        :param elasticbeanstalk: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticbeanstalk AwsProvider#elasticbeanstalk}
        :param elasticinference: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticinference AwsProvider#elasticinference}
        :param elasticsearch: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticsearch AwsProvider#elasticsearch}
        :param elasticsearchservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticsearchservice AwsProvider#elasticsearchservice}
        :param elastictranscoder: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elastictranscoder AwsProvider#elastictranscoder}
        :param elb: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elb AwsProvider#elb}
        :param elbv2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elbv2 AwsProvider#elbv2}
        :param emr: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#emr AwsProvider#emr}
        :param emrcontainers: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#emrcontainers AwsProvider#emrcontainers}
        :param es: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#es AwsProvider#es}
        :param eventbridge: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#eventbridge AwsProvider#eventbridge}
        :param events: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#events AwsProvider#events}
        :param finspace: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#finspace AwsProvider#finspace}
        :param finspacedata: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#finspacedata AwsProvider#finspacedata}
        :param firehose: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#firehose AwsProvider#firehose}
        :param fis: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#fis AwsProvider#fis}
        :param fms: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#fms AwsProvider#fms}
        :param forecast: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forecast AwsProvider#forecast}
        :param forecastquery: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forecastquery AwsProvider#forecastquery}
        :param forecastqueryservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forecastqueryservice AwsProvider#forecastqueryservice}
        :param forecastservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forecastservice AwsProvider#forecastservice}
        :param frauddetector: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#frauddetector AwsProvider#frauddetector}
        :param fsx: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#fsx AwsProvider#fsx}
        :param gamelift: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#gamelift AwsProvider#gamelift}
        :param glacier: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#glacier AwsProvider#glacier}
        :param globalaccelerator: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#globalaccelerator AwsProvider#globalaccelerator}
        :param glue: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#glue AwsProvider#glue}
        :param gluedatabrew: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#gluedatabrew AwsProvider#gluedatabrew}
        :param greengrass: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#greengrass AwsProvider#greengrass}
        :param greengrassv2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#greengrassv2 AwsProvider#greengrassv2}
        :param groundstation: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#groundstation AwsProvider#groundstation}
        :param guardduty: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#guardduty AwsProvider#guardduty}
        :param health: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#health AwsProvider#health}
        :param healthlake: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#healthlake AwsProvider#healthlake}
        :param honeycode: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#honeycode AwsProvider#honeycode}
        :param iam: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iam AwsProvider#iam}
        :param identitystore: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#identitystore AwsProvider#identitystore}
        :param imagebuilder: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#imagebuilder AwsProvider#imagebuilder}
        :param inspector: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#inspector AwsProvider#inspector}
        :param iot: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iot AwsProvider#iot}
        :param iot1_clickdevices: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iot1clickdevices AwsProvider#iot1clickdevices}
        :param iot1_clickdevicesservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iot1clickdevicesservice AwsProvider#iot1clickdevicesservice}
        :param iot1_clickprojects: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iot1clickprojects AwsProvider#iot1clickprojects}
        :param iotanalytics: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotanalytics AwsProvider#iotanalytics}
        :param iotdataplane: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotdataplane AwsProvider#iotdataplane}
        :param iotdeviceadvisor: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotdeviceadvisor AwsProvider#iotdeviceadvisor}
        :param iotevents: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotevents AwsProvider#iotevents}
        :param ioteventsdata: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ioteventsdata AwsProvider#ioteventsdata}
        :param iotfleethub: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotfleethub AwsProvider#iotfleethub}
        :param iotjobsdataplane: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotjobsdataplane AwsProvider#iotjobsdataplane}
        :param iotsecuretunneling: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotsecuretunneling AwsProvider#iotsecuretunneling}
        :param iotsitewise: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotsitewise AwsProvider#iotsitewise}
        :param iotthingsgraph: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotthingsgraph AwsProvider#iotthingsgraph}
        :param iotwireless: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotwireless AwsProvider#iotwireless}
        :param kafka: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kafka AwsProvider#kafka}
        :param kafkaconnect: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kafkaconnect AwsProvider#kafkaconnect}
        :param kendra: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kendra AwsProvider#kendra}
        :param kinesis: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesis AwsProvider#kinesis}
        :param kinesisanalytics: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisanalytics AwsProvider#kinesisanalytics}
        :param kinesisanalyticsv2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisanalyticsv2 AwsProvider#kinesisanalyticsv2}
        :param kinesisvideo: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisvideo AwsProvider#kinesisvideo}
        :param kinesisvideoarchivedmedia: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisvideoarchivedmedia AwsProvider#kinesisvideoarchivedmedia}
        :param kinesisvideomedia: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisvideomedia AwsProvider#kinesisvideomedia}
        :param kinesisvideosignalingchannels: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisvideosignalingchannels AwsProvider#kinesisvideosignalingchannels}
        :param kms: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kms AwsProvider#kms}
        :param lakeformation: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lakeformation AwsProvider#lakeformation}
        :param lambda_: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lambda AwsProvider#lambda}
        :param lexmodelbuilding: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexmodelbuilding AwsProvider#lexmodelbuilding}
        :param lexmodelbuildingservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexmodelbuildingservice AwsProvider#lexmodelbuildingservice}
        :param lexmodels: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexmodels AwsProvider#lexmodels}
        :param lexmodelsv2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexmodelsv2 AwsProvider#lexmodelsv2}
        :param lexruntime: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexruntime AwsProvider#lexruntime}
        :param lexruntimeservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexruntimeservice AwsProvider#lexruntimeservice}
        :param lexruntimev2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexruntimev2 AwsProvider#lexruntimev2}
        :param licensemanager: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#licensemanager AwsProvider#licensemanager}
        :param lightsail: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lightsail AwsProvider#lightsail}
        :param location: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#location AwsProvider#location}
        :param lookoutequipment: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lookoutequipment AwsProvider#lookoutequipment}
        :param lookoutforvision: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lookoutforvision AwsProvider#lookoutforvision}
        :param lookoutmetrics: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lookoutmetrics AwsProvider#lookoutmetrics}
        :param machinelearning: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#machinelearning AwsProvider#machinelearning}
        :param macie: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#macie AwsProvider#macie}
        :param macie2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#macie2 AwsProvider#macie2}
        :param managedblockchain: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#managedblockchain AwsProvider#managedblockchain}
        :param marketplacecatalog: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplacecatalog AwsProvider#marketplacecatalog}
        :param marketplacecommerceanalytics: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplacecommerceanalytics AwsProvider#marketplacecommerceanalytics}
        :param marketplaceentitlement: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplaceentitlement AwsProvider#marketplaceentitlement}
        :param marketplaceentitlementservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplaceentitlementservice AwsProvider#marketplaceentitlementservice}
        :param marketplacemetering: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplacemetering AwsProvider#marketplacemetering}
        :param mediaconnect: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediaconnect AwsProvider#mediaconnect}
        :param mediaconvert: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediaconvert AwsProvider#mediaconvert}
        :param medialive: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#medialive AwsProvider#medialive}
        :param mediapackage: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediapackage AwsProvider#mediapackage}
        :param mediapackagevod: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediapackagevod AwsProvider#mediapackagevod}
        :param mediastore: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediastore AwsProvider#mediastore}
        :param mediastoredata: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediastoredata AwsProvider#mediastoredata}
        :param mediatailor: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediatailor AwsProvider#mediatailor}
        :param memorydb: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#memorydb AwsProvider#memorydb}
        :param mgn: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mgn AwsProvider#mgn}
        :param migrationhub: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#migrationhub AwsProvider#migrationhub}
        :param migrationhubconfig: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#migrationhubconfig AwsProvider#migrationhubconfig}
        :param mobile: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mobile AwsProvider#mobile}
        :param mobileanalytics: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mobileanalytics AwsProvider#mobileanalytics}
        :param mq: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mq AwsProvider#mq}
        :param mturk: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mturk AwsProvider#mturk}
        :param mwaa: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mwaa AwsProvider#mwaa}
        :param neptune: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#neptune AwsProvider#neptune}
        :param networkfirewall: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#networkfirewall AwsProvider#networkfirewall}
        :param networkmanager: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#networkmanager AwsProvider#networkmanager}
        :param nimblestudio: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#nimblestudio AwsProvider#nimblestudio}
        :param opsworks: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#opsworks AwsProvider#opsworks}
        :param opsworkscm: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#opsworkscm AwsProvider#opsworkscm}
        :param organizations: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#organizations AwsProvider#organizations}
        :param outposts: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#outposts AwsProvider#outposts}
        :param personalize: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#personalize AwsProvider#personalize}
        :param personalizeevents: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#personalizeevents AwsProvider#personalizeevents}
        :param personalizeruntime: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#personalizeruntime AwsProvider#personalizeruntime}
        :param pi: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pi AwsProvider#pi}
        :param pinpoint: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pinpoint AwsProvider#pinpoint}
        :param pinpointemail: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pinpointemail AwsProvider#pinpointemail}
        :param pinpointsmsvoice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pinpointsmsvoice AwsProvider#pinpointsmsvoice}
        :param polly: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#polly AwsProvider#polly}
        :param pricing: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pricing AwsProvider#pricing}
        :param prometheus: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#prometheus AwsProvider#prometheus}
        :param prometheusservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#prometheusservice AwsProvider#prometheusservice}
        :param proton: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#proton AwsProvider#proton}
        :param qldb: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#qldb AwsProvider#qldb}
        :param qldbsession: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#qldbsession AwsProvider#qldbsession}
        :param quicksight: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#quicksight AwsProvider#quicksight}
        :param ram: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ram AwsProvider#ram}
        :param rds: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#rds AwsProvider#rds}
        :param rdsdata: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#rdsdata AwsProvider#rdsdata}
        :param rdsdataservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#rdsdataservice AwsProvider#rdsdataservice}
        :param redshift: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#redshift AwsProvider#redshift}
        :param redshiftdata: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#redshiftdata AwsProvider#redshiftdata}
        :param rekognition: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#rekognition AwsProvider#rekognition}
        :param resourcegroups: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#resourcegroups AwsProvider#resourcegroups}
        :param resourcegroupstagging: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#resourcegroupstagging AwsProvider#resourcegroupstagging}
        :param resourcegroupstaggingapi: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#resourcegroupstaggingapi AwsProvider#resourcegroupstaggingapi}
        :param robomaker: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#robomaker AwsProvider#robomaker}
        :param route53: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53 AwsProvider#route53}
        :param route53_domains: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53domains AwsProvider#route53domains}
        :param route53_recoverycontrolconfig: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53recoverycontrolconfig AwsProvider#route53recoverycontrolconfig}
        :param route53_recoveryreadiness: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53recoveryreadiness AwsProvider#route53recoveryreadiness}
        :param route53_resolver: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53resolver AwsProvider#route53resolver}
        :param s3: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#s3 AwsProvider#s3}
        :param s3_control: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#s3control AwsProvider#s3control}
        :param s3_outposts: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#s3outposts AwsProvider#s3outposts}
        :param sagemaker: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sagemaker AwsProvider#sagemaker}
        :param sagemakeredgemanager: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sagemakeredgemanager AwsProvider#sagemakeredgemanager}
        :param sagemakerfeaturestoreruntime: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sagemakerfeaturestoreruntime AwsProvider#sagemakerfeaturestoreruntime}
        :param sagemakerruntime: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sagemakerruntime AwsProvider#sagemakerruntime}
        :param savingsplans: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#savingsplans AwsProvider#savingsplans}
        :param schemas: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#schemas AwsProvider#schemas}
        :param sdb: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sdb AwsProvider#sdb}
        :param secretsmanager: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#secretsmanager AwsProvider#secretsmanager}
        :param securityhub: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#securityhub AwsProvider#securityhub}
        :param serverlessapplicationrepository: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#serverlessapplicationrepository AwsProvider#serverlessapplicationrepository}
        :param serverlessapprepo: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#serverlessapprepo AwsProvider#serverlessapprepo}
        :param serverlessrepo: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#serverlessrepo AwsProvider#serverlessrepo}
        :param servicecatalog: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#servicecatalog AwsProvider#servicecatalog}
        :param servicediscovery: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#servicediscovery AwsProvider#servicediscovery}
        :param servicequotas: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#servicequotas AwsProvider#servicequotas}
        :param ses: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ses AwsProvider#ses}
        :param sesv2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sesv2 AwsProvider#sesv2}
        :param sfn: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sfn AwsProvider#sfn}
        :param shield: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#shield AwsProvider#shield}
        :param signer: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#signer AwsProvider#signer}
        :param simpledb: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#simpledb AwsProvider#simpledb}
        :param sms: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sms AwsProvider#sms}
        :param snowball: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#snowball AwsProvider#snowball}
        :param sns: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sns AwsProvider#sns}
        :param sqs: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sqs AwsProvider#sqs}
        :param ssm: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssm AwsProvider#ssm}
        :param ssmcontacts: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssmcontacts AwsProvider#ssmcontacts}
        :param ssmincidents: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssmincidents AwsProvider#ssmincidents}
        :param sso: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sso AwsProvider#sso}
        :param ssoadmin: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssoadmin AwsProvider#ssoadmin}
        :param ssooidc: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssooidc AwsProvider#ssooidc}
        :param stepfunctions: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#stepfunctions AwsProvider#stepfunctions}
        :param storagegateway: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#storagegateway AwsProvider#storagegateway}
        :param sts: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sts AwsProvider#sts}
        :param support: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#support AwsProvider#support}
        :param swf: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#swf AwsProvider#swf}
        :param synthetics: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#synthetics AwsProvider#synthetics}
        :param textract: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#textract AwsProvider#textract}
        :param timestreamquery: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#timestreamquery AwsProvider#timestreamquery}
        :param timestreamwrite: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#timestreamwrite AwsProvider#timestreamwrite}
        :param transcribe: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transcribe AwsProvider#transcribe}
        :param transcribeservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transcribeservice AwsProvider#transcribeservice}
        :param transcribestreaming: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transcribestreaming AwsProvider#transcribestreaming}
        :param transcribestreamingservice: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transcribestreamingservice AwsProvider#transcribestreamingservice}
        :param transfer: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transfer AwsProvider#transfer}
        :param translate: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#translate AwsProvider#translate}
        :param waf: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#waf AwsProvider#waf}
        :param wafregional: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#wafregional AwsProvider#wafregional}
        :param wafv2: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#wafv2 AwsProvider#wafv2}
        :param wellarchitected: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#wellarchitected AwsProvider#wellarchitected}
        :param workdocs: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#workdocs AwsProvider#workdocs}
        :param worklink: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#worklink AwsProvider#worklink}
        :param workmail: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#workmail AwsProvider#workmail}
        :param workmailmessageflow: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#workmailmessageflow AwsProvider#workmailmessageflow}
        :param workspaces: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#workspaces AwsProvider#workspaces}
        :param xray: Use this to override the default service endpoint URL. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#xray AwsProvider#xray}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if accessanalyzer is not None:
            self._values["accessanalyzer"] = accessanalyzer
        if account is not None:
            self._values["account"] = account
        if acm is not None:
            self._values["acm"] = acm
        if acmpca is not None:
            self._values["acmpca"] = acmpca
        if alexaforbusiness is not None:
            self._values["alexaforbusiness"] = alexaforbusiness
        if amp is not None:
            self._values["amp"] = amp
        if amplify is not None:
            self._values["amplify"] = amplify
        if amplifybackend is not None:
            self._values["amplifybackend"] = amplifybackend
        if apigateway is not None:
            self._values["apigateway"] = apigateway
        if apigatewayv2 is not None:
            self._values["apigatewayv2"] = apigatewayv2
        if appautoscaling is not None:
            self._values["appautoscaling"] = appautoscaling
        if appconfig is not None:
            self._values["appconfig"] = appconfig
        if appflow is not None:
            self._values["appflow"] = appflow
        if appintegrations is not None:
            self._values["appintegrations"] = appintegrations
        if appintegrationsservice is not None:
            self._values["appintegrationsservice"] = appintegrationsservice
        if applicationautoscaling is not None:
            self._values["applicationautoscaling"] = applicationautoscaling
        if applicationcostprofiler is not None:
            self._values["applicationcostprofiler"] = applicationcostprofiler
        if applicationdiscovery is not None:
            self._values["applicationdiscovery"] = applicationdiscovery
        if applicationdiscoveryservice is not None:
            self._values["applicationdiscoveryservice"] = applicationdiscoveryservice
        if applicationinsights is not None:
            self._values["applicationinsights"] = applicationinsights
        if appmesh is not None:
            self._values["appmesh"] = appmesh
        if appregistry is not None:
            self._values["appregistry"] = appregistry
        if apprunner is not None:
            self._values["apprunner"] = apprunner
        if appstream is not None:
            self._values["appstream"] = appstream
        if appsync is not None:
            self._values["appsync"] = appsync
        if athena is not None:
            self._values["athena"] = athena
        if auditmanager is not None:
            self._values["auditmanager"] = auditmanager
        if augmentedairuntime is not None:
            self._values["augmentedairuntime"] = augmentedairuntime
        if autoscaling is not None:
            self._values["autoscaling"] = autoscaling
        if autoscalingplans is not None:
            self._values["autoscalingplans"] = autoscalingplans
        if backup is not None:
            self._values["backup"] = backup
        if batch is not None:
            self._values["batch"] = batch
        if braket is not None:
            self._values["braket"] = braket
        if budgets is not None:
            self._values["budgets"] = budgets
        if chime is not None:
            self._values["chime"] = chime
        if cloud9 is not None:
            self._values["cloud9"] = cloud9
        if cloudcontrol is not None:
            self._values["cloudcontrol"] = cloudcontrol
        if cloudcontrolapi is not None:
            self._values["cloudcontrolapi"] = cloudcontrolapi
        if clouddirectory is not None:
            self._values["clouddirectory"] = clouddirectory
        if cloudformation is not None:
            self._values["cloudformation"] = cloudformation
        if cloudfront is not None:
            self._values["cloudfront"] = cloudfront
        if cloudhsm is not None:
            self._values["cloudhsm"] = cloudhsm
        if cloudhsmv2 is not None:
            self._values["cloudhsmv2"] = cloudhsmv2
        if cloudsearch is not None:
            self._values["cloudsearch"] = cloudsearch
        if cloudsearchdomain is not None:
            self._values["cloudsearchdomain"] = cloudsearchdomain
        if cloudtrail is not None:
            self._values["cloudtrail"] = cloudtrail
        if cloudwatch is not None:
            self._values["cloudwatch"] = cloudwatch
        if cloudwatchevents is not None:
            self._values["cloudwatchevents"] = cloudwatchevents
        if cloudwatchlogs is not None:
            self._values["cloudwatchlogs"] = cloudwatchlogs
        if codeartifact is not None:
            self._values["codeartifact"] = codeartifact
        if codebuild is not None:
            self._values["codebuild"] = codebuild
        if codecommit is not None:
            self._values["codecommit"] = codecommit
        if codedeploy is not None:
            self._values["codedeploy"] = codedeploy
        if codeguruprofiler is not None:
            self._values["codeguruprofiler"] = codeguruprofiler
        if codegurureviewer is not None:
            self._values["codegurureviewer"] = codegurureviewer
        if codepipeline is not None:
            self._values["codepipeline"] = codepipeline
        if codestar is not None:
            self._values["codestar"] = codestar
        if codestarconnections is not None:
            self._values["codestarconnections"] = codestarconnections
        if codestarnotifications is not None:
            self._values["codestarnotifications"] = codestarnotifications
        if cognitoidentity is not None:
            self._values["cognitoidentity"] = cognitoidentity
        if cognitoidentityprovider is not None:
            self._values["cognitoidentityprovider"] = cognitoidentityprovider
        if cognitoidp is not None:
            self._values["cognitoidp"] = cognitoidp
        if cognitosync is not None:
            self._values["cognitosync"] = cognitosync
        if comprehend is not None:
            self._values["comprehend"] = comprehend
        if comprehendmedical is not None:
            self._values["comprehendmedical"] = comprehendmedical
        if config is not None:
            self._values["config"] = config
        if configservice is not None:
            self._values["configservice"] = configservice
        if connect is not None:
            self._values["connect"] = connect
        if connectcontactlens is not None:
            self._values["connectcontactlens"] = connectcontactlens
        if connectparticipant is not None:
            self._values["connectparticipant"] = connectparticipant
        if costandusagereportservice is not None:
            self._values["costandusagereportservice"] = costandusagereportservice
        if costexplorer is not None:
            self._values["costexplorer"] = costexplorer
        if cur is not None:
            self._values["cur"] = cur
        if databasemigration is not None:
            self._values["databasemigration"] = databasemigration
        if databasemigrationservice is not None:
            self._values["databasemigrationservice"] = databasemigrationservice
        if dataexchange is not None:
            self._values["dataexchange"] = dataexchange
        if datapipeline is not None:
            self._values["datapipeline"] = datapipeline
        if datasync is not None:
            self._values["datasync"] = datasync
        if dax is not None:
            self._values["dax"] = dax
        if detective is not None:
            self._values["detective"] = detective
        if devicefarm is not None:
            self._values["devicefarm"] = devicefarm
        if devopsguru is not None:
            self._values["devopsguru"] = devopsguru
        if directconnect is not None:
            self._values["directconnect"] = directconnect
        if dlm is not None:
            self._values["dlm"] = dlm
        if dms is not None:
            self._values["dms"] = dms
        if docdb is not None:
            self._values["docdb"] = docdb
        if ds is not None:
            self._values["ds"] = ds
        if dynamodb is not None:
            self._values["dynamodb"] = dynamodb
        if dynamodbstreams is not None:
            self._values["dynamodbstreams"] = dynamodbstreams
        if ec2 is not None:
            self._values["ec2"] = ec2
        if ec2_instanceconnect is not None:
            self._values["ec2_instanceconnect"] = ec2_instanceconnect
        if ecr is not None:
            self._values["ecr"] = ecr
        if ecrpublic is not None:
            self._values["ecrpublic"] = ecrpublic
        if ecs is not None:
            self._values["ecs"] = ecs
        if efs is not None:
            self._values["efs"] = efs
        if eks is not None:
            self._values["eks"] = eks
        if elasticache is not None:
            self._values["elasticache"] = elasticache
        if elasticbeanstalk is not None:
            self._values["elasticbeanstalk"] = elasticbeanstalk
        if elasticinference is not None:
            self._values["elasticinference"] = elasticinference
        if elasticsearch is not None:
            self._values["elasticsearch"] = elasticsearch
        if elasticsearchservice is not None:
            self._values["elasticsearchservice"] = elasticsearchservice
        if elastictranscoder is not None:
            self._values["elastictranscoder"] = elastictranscoder
        if elb is not None:
            self._values["elb"] = elb
        if elbv2 is not None:
            self._values["elbv2"] = elbv2
        if emr is not None:
            self._values["emr"] = emr
        if emrcontainers is not None:
            self._values["emrcontainers"] = emrcontainers
        if es is not None:
            self._values["es"] = es
        if eventbridge is not None:
            self._values["eventbridge"] = eventbridge
        if events is not None:
            self._values["events"] = events
        if finspace is not None:
            self._values["finspace"] = finspace
        if finspacedata is not None:
            self._values["finspacedata"] = finspacedata
        if firehose is not None:
            self._values["firehose"] = firehose
        if fis is not None:
            self._values["fis"] = fis
        if fms is not None:
            self._values["fms"] = fms
        if forecast is not None:
            self._values["forecast"] = forecast
        if forecastquery is not None:
            self._values["forecastquery"] = forecastquery
        if forecastqueryservice is not None:
            self._values["forecastqueryservice"] = forecastqueryservice
        if forecastservice is not None:
            self._values["forecastservice"] = forecastservice
        if frauddetector is not None:
            self._values["frauddetector"] = frauddetector
        if fsx is not None:
            self._values["fsx"] = fsx
        if gamelift is not None:
            self._values["gamelift"] = gamelift
        if glacier is not None:
            self._values["glacier"] = glacier
        if globalaccelerator is not None:
            self._values["globalaccelerator"] = globalaccelerator
        if glue is not None:
            self._values["glue"] = glue
        if gluedatabrew is not None:
            self._values["gluedatabrew"] = gluedatabrew
        if greengrass is not None:
            self._values["greengrass"] = greengrass
        if greengrassv2 is not None:
            self._values["greengrassv2"] = greengrassv2
        if groundstation is not None:
            self._values["groundstation"] = groundstation
        if guardduty is not None:
            self._values["guardduty"] = guardduty
        if health is not None:
            self._values["health"] = health
        if healthlake is not None:
            self._values["healthlake"] = healthlake
        if honeycode is not None:
            self._values["honeycode"] = honeycode
        if iam is not None:
            self._values["iam"] = iam
        if identitystore is not None:
            self._values["identitystore"] = identitystore
        if imagebuilder is not None:
            self._values["imagebuilder"] = imagebuilder
        if inspector is not None:
            self._values["inspector"] = inspector
        if iot is not None:
            self._values["iot"] = iot
        if iot1_clickdevices is not None:
            self._values["iot1_clickdevices"] = iot1_clickdevices
        if iot1_clickdevicesservice is not None:
            self._values["iot1_clickdevicesservice"] = iot1_clickdevicesservice
        if iot1_clickprojects is not None:
            self._values["iot1_clickprojects"] = iot1_clickprojects
        if iotanalytics is not None:
            self._values["iotanalytics"] = iotanalytics
        if iotdataplane is not None:
            self._values["iotdataplane"] = iotdataplane
        if iotdeviceadvisor is not None:
            self._values["iotdeviceadvisor"] = iotdeviceadvisor
        if iotevents is not None:
            self._values["iotevents"] = iotevents
        if ioteventsdata is not None:
            self._values["ioteventsdata"] = ioteventsdata
        if iotfleethub is not None:
            self._values["iotfleethub"] = iotfleethub
        if iotjobsdataplane is not None:
            self._values["iotjobsdataplane"] = iotjobsdataplane
        if iotsecuretunneling is not None:
            self._values["iotsecuretunneling"] = iotsecuretunneling
        if iotsitewise is not None:
            self._values["iotsitewise"] = iotsitewise
        if iotthingsgraph is not None:
            self._values["iotthingsgraph"] = iotthingsgraph
        if iotwireless is not None:
            self._values["iotwireless"] = iotwireless
        if kafka is not None:
            self._values["kafka"] = kafka
        if kafkaconnect is not None:
            self._values["kafkaconnect"] = kafkaconnect
        if kendra is not None:
            self._values["kendra"] = kendra
        if kinesis is not None:
            self._values["kinesis"] = kinesis
        if kinesisanalytics is not None:
            self._values["kinesisanalytics"] = kinesisanalytics
        if kinesisanalyticsv2 is not None:
            self._values["kinesisanalyticsv2"] = kinesisanalyticsv2
        if kinesisvideo is not None:
            self._values["kinesisvideo"] = kinesisvideo
        if kinesisvideoarchivedmedia is not None:
            self._values["kinesisvideoarchivedmedia"] = kinesisvideoarchivedmedia
        if kinesisvideomedia is not None:
            self._values["kinesisvideomedia"] = kinesisvideomedia
        if kinesisvideosignalingchannels is not None:
            self._values["kinesisvideosignalingchannels"] = kinesisvideosignalingchannels
        if kms is not None:
            self._values["kms"] = kms
        if lakeformation is not None:
            self._values["lakeformation"] = lakeformation
        if lambda_ is not None:
            self._values["lambda_"] = lambda_
        if lexmodelbuilding is not None:
            self._values["lexmodelbuilding"] = lexmodelbuilding
        if lexmodelbuildingservice is not None:
            self._values["lexmodelbuildingservice"] = lexmodelbuildingservice
        if lexmodels is not None:
            self._values["lexmodels"] = lexmodels
        if lexmodelsv2 is not None:
            self._values["lexmodelsv2"] = lexmodelsv2
        if lexruntime is not None:
            self._values["lexruntime"] = lexruntime
        if lexruntimeservice is not None:
            self._values["lexruntimeservice"] = lexruntimeservice
        if lexruntimev2 is not None:
            self._values["lexruntimev2"] = lexruntimev2
        if licensemanager is not None:
            self._values["licensemanager"] = licensemanager
        if lightsail is not None:
            self._values["lightsail"] = lightsail
        if location is not None:
            self._values["location"] = location
        if lookoutequipment is not None:
            self._values["lookoutequipment"] = lookoutequipment
        if lookoutforvision is not None:
            self._values["lookoutforvision"] = lookoutforvision
        if lookoutmetrics is not None:
            self._values["lookoutmetrics"] = lookoutmetrics
        if machinelearning is not None:
            self._values["machinelearning"] = machinelearning
        if macie is not None:
            self._values["macie"] = macie
        if macie2 is not None:
            self._values["macie2"] = macie2
        if managedblockchain is not None:
            self._values["managedblockchain"] = managedblockchain
        if marketplacecatalog is not None:
            self._values["marketplacecatalog"] = marketplacecatalog
        if marketplacecommerceanalytics is not None:
            self._values["marketplacecommerceanalytics"] = marketplacecommerceanalytics
        if marketplaceentitlement is not None:
            self._values["marketplaceentitlement"] = marketplaceentitlement
        if marketplaceentitlementservice is not None:
            self._values["marketplaceentitlementservice"] = marketplaceentitlementservice
        if marketplacemetering is not None:
            self._values["marketplacemetering"] = marketplacemetering
        if mediaconnect is not None:
            self._values["mediaconnect"] = mediaconnect
        if mediaconvert is not None:
            self._values["mediaconvert"] = mediaconvert
        if medialive is not None:
            self._values["medialive"] = medialive
        if mediapackage is not None:
            self._values["mediapackage"] = mediapackage
        if mediapackagevod is not None:
            self._values["mediapackagevod"] = mediapackagevod
        if mediastore is not None:
            self._values["mediastore"] = mediastore
        if mediastoredata is not None:
            self._values["mediastoredata"] = mediastoredata
        if mediatailor is not None:
            self._values["mediatailor"] = mediatailor
        if memorydb is not None:
            self._values["memorydb"] = memorydb
        if mgn is not None:
            self._values["mgn"] = mgn
        if migrationhub is not None:
            self._values["migrationhub"] = migrationhub
        if migrationhubconfig is not None:
            self._values["migrationhubconfig"] = migrationhubconfig
        if mobile is not None:
            self._values["mobile"] = mobile
        if mobileanalytics is not None:
            self._values["mobileanalytics"] = mobileanalytics
        if mq is not None:
            self._values["mq"] = mq
        if mturk is not None:
            self._values["mturk"] = mturk
        if mwaa is not None:
            self._values["mwaa"] = mwaa
        if neptune is not None:
            self._values["neptune"] = neptune
        if networkfirewall is not None:
            self._values["networkfirewall"] = networkfirewall
        if networkmanager is not None:
            self._values["networkmanager"] = networkmanager
        if nimblestudio is not None:
            self._values["nimblestudio"] = nimblestudio
        if opsworks is not None:
            self._values["opsworks"] = opsworks
        if opsworkscm is not None:
            self._values["opsworkscm"] = opsworkscm
        if organizations is not None:
            self._values["organizations"] = organizations
        if outposts is not None:
            self._values["outposts"] = outposts
        if personalize is not None:
            self._values["personalize"] = personalize
        if personalizeevents is not None:
            self._values["personalizeevents"] = personalizeevents
        if personalizeruntime is not None:
            self._values["personalizeruntime"] = personalizeruntime
        if pi is not None:
            self._values["pi"] = pi
        if pinpoint is not None:
            self._values["pinpoint"] = pinpoint
        if pinpointemail is not None:
            self._values["pinpointemail"] = pinpointemail
        if pinpointsmsvoice is not None:
            self._values["pinpointsmsvoice"] = pinpointsmsvoice
        if polly is not None:
            self._values["polly"] = polly
        if pricing is not None:
            self._values["pricing"] = pricing
        if prometheus is not None:
            self._values["prometheus"] = prometheus
        if prometheusservice is not None:
            self._values["prometheusservice"] = prometheusservice
        if proton is not None:
            self._values["proton"] = proton
        if qldb is not None:
            self._values["qldb"] = qldb
        if qldbsession is not None:
            self._values["qldbsession"] = qldbsession
        if quicksight is not None:
            self._values["quicksight"] = quicksight
        if ram is not None:
            self._values["ram"] = ram
        if rds is not None:
            self._values["rds"] = rds
        if rdsdata is not None:
            self._values["rdsdata"] = rdsdata
        if rdsdataservice is not None:
            self._values["rdsdataservice"] = rdsdataservice
        if redshift is not None:
            self._values["redshift"] = redshift
        if redshiftdata is not None:
            self._values["redshiftdata"] = redshiftdata
        if rekognition is not None:
            self._values["rekognition"] = rekognition
        if resourcegroups is not None:
            self._values["resourcegroups"] = resourcegroups
        if resourcegroupstagging is not None:
            self._values["resourcegroupstagging"] = resourcegroupstagging
        if resourcegroupstaggingapi is not None:
            self._values["resourcegroupstaggingapi"] = resourcegroupstaggingapi
        if robomaker is not None:
            self._values["robomaker"] = robomaker
        if route53 is not None:
            self._values["route53"] = route53
        if route53_domains is not None:
            self._values["route53_domains"] = route53_domains
        if route53_recoverycontrolconfig is not None:
            self._values["route53_recoverycontrolconfig"] = route53_recoverycontrolconfig
        if route53_recoveryreadiness is not None:
            self._values["route53_recoveryreadiness"] = route53_recoveryreadiness
        if route53_resolver is not None:
            self._values["route53_resolver"] = route53_resolver
        if s3 is not None:
            self._values["s3"] = s3
        if s3_control is not None:
            self._values["s3_control"] = s3_control
        if s3_outposts is not None:
            self._values["s3_outposts"] = s3_outposts
        if sagemaker is not None:
            self._values["sagemaker"] = sagemaker
        if sagemakeredgemanager is not None:
            self._values["sagemakeredgemanager"] = sagemakeredgemanager
        if sagemakerfeaturestoreruntime is not None:
            self._values["sagemakerfeaturestoreruntime"] = sagemakerfeaturestoreruntime
        if sagemakerruntime is not None:
            self._values["sagemakerruntime"] = sagemakerruntime
        if savingsplans is not None:
            self._values["savingsplans"] = savingsplans
        if schemas is not None:
            self._values["schemas"] = schemas
        if sdb is not None:
            self._values["sdb"] = sdb
        if secretsmanager is not None:
            self._values["secretsmanager"] = secretsmanager
        if securityhub is not None:
            self._values["securityhub"] = securityhub
        if serverlessapplicationrepository is not None:
            self._values["serverlessapplicationrepository"] = serverlessapplicationrepository
        if serverlessapprepo is not None:
            self._values["serverlessapprepo"] = serverlessapprepo
        if serverlessrepo is not None:
            self._values["serverlessrepo"] = serverlessrepo
        if servicecatalog is not None:
            self._values["servicecatalog"] = servicecatalog
        if servicediscovery is not None:
            self._values["servicediscovery"] = servicediscovery
        if servicequotas is not None:
            self._values["servicequotas"] = servicequotas
        if ses is not None:
            self._values["ses"] = ses
        if sesv2 is not None:
            self._values["sesv2"] = sesv2
        if sfn is not None:
            self._values["sfn"] = sfn
        if shield is not None:
            self._values["shield"] = shield
        if signer is not None:
            self._values["signer"] = signer
        if simpledb is not None:
            self._values["simpledb"] = simpledb
        if sms is not None:
            self._values["sms"] = sms
        if snowball is not None:
            self._values["snowball"] = snowball
        if sns is not None:
            self._values["sns"] = sns
        if sqs is not None:
            self._values["sqs"] = sqs
        if ssm is not None:
            self._values["ssm"] = ssm
        if ssmcontacts is not None:
            self._values["ssmcontacts"] = ssmcontacts
        if ssmincidents is not None:
            self._values["ssmincidents"] = ssmincidents
        if sso is not None:
            self._values["sso"] = sso
        if ssoadmin is not None:
            self._values["ssoadmin"] = ssoadmin
        if ssooidc is not None:
            self._values["ssooidc"] = ssooidc
        if stepfunctions is not None:
            self._values["stepfunctions"] = stepfunctions
        if storagegateway is not None:
            self._values["storagegateway"] = storagegateway
        if sts is not None:
            self._values["sts"] = sts
        if support is not None:
            self._values["support"] = support
        if swf is not None:
            self._values["swf"] = swf
        if synthetics is not None:
            self._values["synthetics"] = synthetics
        if textract is not None:
            self._values["textract"] = textract
        if timestreamquery is not None:
            self._values["timestreamquery"] = timestreamquery
        if timestreamwrite is not None:
            self._values["timestreamwrite"] = timestreamwrite
        if transcribe is not None:
            self._values["transcribe"] = transcribe
        if transcribeservice is not None:
            self._values["transcribeservice"] = transcribeservice
        if transcribestreaming is not None:
            self._values["transcribestreaming"] = transcribestreaming
        if transcribestreamingservice is not None:
            self._values["transcribestreamingservice"] = transcribestreamingservice
        if transfer is not None:
            self._values["transfer"] = transfer
        if translate is not None:
            self._values["translate"] = translate
        if waf is not None:
            self._values["waf"] = waf
        if wafregional is not None:
            self._values["wafregional"] = wafregional
        if wafv2 is not None:
            self._values["wafv2"] = wafv2
        if wellarchitected is not None:
            self._values["wellarchitected"] = wellarchitected
        if workdocs is not None:
            self._values["workdocs"] = workdocs
        if worklink is not None:
            self._values["worklink"] = worklink
        if workmail is not None:
            self._values["workmail"] = workmail
        if workmailmessageflow is not None:
            self._values["workmailmessageflow"] = workmailmessageflow
        if workspaces is not None:
            self._values["workspaces"] = workspaces
        if xray is not None:
            self._values["xray"] = xray

    @builtins.property
    def accessanalyzer(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#accessanalyzer AwsProvider#accessanalyzer}
        '''
        result = self._values.get("accessanalyzer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#account AwsProvider#account}
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def acm(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#acm AwsProvider#acm}
        '''
        result = self._values.get("acm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def acmpca(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#acmpca AwsProvider#acmpca}
        '''
        result = self._values.get("acmpca")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alexaforbusiness(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#alexaforbusiness AwsProvider#alexaforbusiness}
        '''
        result = self._values.get("alexaforbusiness")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def amp(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#amp AwsProvider#amp}
        '''
        result = self._values.get("amp")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def amplify(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#amplify AwsProvider#amplify}
        '''
        result = self._values.get("amplify")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def amplifybackend(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#amplifybackend AwsProvider#amplifybackend}
        '''
        result = self._values.get("amplifybackend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def apigateway(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#apigateway AwsProvider#apigateway}
        '''
        result = self._values.get("apigateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def apigatewayv2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#apigatewayv2 AwsProvider#apigatewayv2}
        '''
        result = self._values.get("apigatewayv2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def appautoscaling(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appautoscaling AwsProvider#appautoscaling}
        '''
        result = self._values.get("appautoscaling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def appconfig(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appconfig AwsProvider#appconfig}
        '''
        result = self._values.get("appconfig")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def appflow(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appflow AwsProvider#appflow}
        '''
        result = self._values.get("appflow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def appintegrations(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appintegrations AwsProvider#appintegrations}
        '''
        result = self._values.get("appintegrations")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def appintegrationsservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appintegrationsservice AwsProvider#appintegrationsservice}
        '''
        result = self._values.get("appintegrationsservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def applicationautoscaling(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationautoscaling AwsProvider#applicationautoscaling}
        '''
        result = self._values.get("applicationautoscaling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def applicationcostprofiler(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationcostprofiler AwsProvider#applicationcostprofiler}
        '''
        result = self._values.get("applicationcostprofiler")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def applicationdiscovery(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationdiscovery AwsProvider#applicationdiscovery}
        '''
        result = self._values.get("applicationdiscovery")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def applicationdiscoveryservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationdiscoveryservice AwsProvider#applicationdiscoveryservice}
        '''
        result = self._values.get("applicationdiscoveryservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def applicationinsights(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#applicationinsights AwsProvider#applicationinsights}
        '''
        result = self._values.get("applicationinsights")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def appmesh(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appmesh AwsProvider#appmesh}
        '''
        result = self._values.get("appmesh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def appregistry(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appregistry AwsProvider#appregistry}
        '''
        result = self._values.get("appregistry")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def apprunner(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#apprunner AwsProvider#apprunner}
        '''
        result = self._values.get("apprunner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def appstream(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appstream AwsProvider#appstream}
        '''
        result = self._values.get("appstream")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def appsync(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#appsync AwsProvider#appsync}
        '''
        result = self._values.get("appsync")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def athena(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#athena AwsProvider#athena}
        '''
        result = self._values.get("athena")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auditmanager(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#auditmanager AwsProvider#auditmanager}
        '''
        result = self._values.get("auditmanager")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def augmentedairuntime(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#augmentedairuntime AwsProvider#augmentedairuntime}
        '''
        result = self._values.get("augmentedairuntime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def autoscaling(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#autoscaling AwsProvider#autoscaling}
        '''
        result = self._values.get("autoscaling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def autoscalingplans(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#autoscalingplans AwsProvider#autoscalingplans}
        '''
        result = self._values.get("autoscalingplans")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def backup(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#backup AwsProvider#backup}
        '''
        result = self._values.get("backup")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def batch(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#batch AwsProvider#batch}
        '''
        result = self._values.get("batch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def braket(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#braket AwsProvider#braket}
        '''
        result = self._values.get("braket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def budgets(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#budgets AwsProvider#budgets}
        '''
        result = self._values.get("budgets")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def chime(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#chime AwsProvider#chime}
        '''
        result = self._values.get("chime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloud9(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloud9 AwsProvider#cloud9}
        '''
        result = self._values.get("cloud9")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudcontrol(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudcontrol AwsProvider#cloudcontrol}
        '''
        result = self._values.get("cloudcontrol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudcontrolapi(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudcontrolapi AwsProvider#cloudcontrolapi}
        '''
        result = self._values.get("cloudcontrolapi")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def clouddirectory(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#clouddirectory AwsProvider#clouddirectory}
        '''
        result = self._values.get("clouddirectory")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudformation(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudformation AwsProvider#cloudformation}
        '''
        result = self._values.get("cloudformation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudfront(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudfront AwsProvider#cloudfront}
        '''
        result = self._values.get("cloudfront")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudhsm(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudhsm AwsProvider#cloudhsm}
        '''
        result = self._values.get("cloudhsm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudhsmv2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudhsmv2 AwsProvider#cloudhsmv2}
        '''
        result = self._values.get("cloudhsmv2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudsearch(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudsearch AwsProvider#cloudsearch}
        '''
        result = self._values.get("cloudsearch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudsearchdomain(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudsearchdomain AwsProvider#cloudsearchdomain}
        '''
        result = self._values.get("cloudsearchdomain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudtrail(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudtrail AwsProvider#cloudtrail}
        '''
        result = self._values.get("cloudtrail")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudwatch(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudwatch AwsProvider#cloudwatch}
        '''
        result = self._values.get("cloudwatch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudwatchevents(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudwatchevents AwsProvider#cloudwatchevents}
        '''
        result = self._values.get("cloudwatchevents")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cloudwatchlogs(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cloudwatchlogs AwsProvider#cloudwatchlogs}
        '''
        result = self._values.get("cloudwatchlogs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codeartifact(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codeartifact AwsProvider#codeartifact}
        '''
        result = self._values.get("codeartifact")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codebuild(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codebuild AwsProvider#codebuild}
        '''
        result = self._values.get("codebuild")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codecommit(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codecommit AwsProvider#codecommit}
        '''
        result = self._values.get("codecommit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codedeploy(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codedeploy AwsProvider#codedeploy}
        '''
        result = self._values.get("codedeploy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codeguruprofiler(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codeguruprofiler AwsProvider#codeguruprofiler}
        '''
        result = self._values.get("codeguruprofiler")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codegurureviewer(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codegurureviewer AwsProvider#codegurureviewer}
        '''
        result = self._values.get("codegurureviewer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codepipeline(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codepipeline AwsProvider#codepipeline}
        '''
        result = self._values.get("codepipeline")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codestar(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codestar AwsProvider#codestar}
        '''
        result = self._values.get("codestar")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codestarconnections(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codestarconnections AwsProvider#codestarconnections}
        '''
        result = self._values.get("codestarconnections")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def codestarnotifications(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#codestarnotifications AwsProvider#codestarnotifications}
        '''
        result = self._values.get("codestarnotifications")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cognitoidentity(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cognitoidentity AwsProvider#cognitoidentity}
        '''
        result = self._values.get("cognitoidentity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cognitoidentityprovider(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cognitoidentityprovider AwsProvider#cognitoidentityprovider}
        '''
        result = self._values.get("cognitoidentityprovider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cognitoidp(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cognitoidp AwsProvider#cognitoidp}
        '''
        result = self._values.get("cognitoidp")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cognitosync(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cognitosync AwsProvider#cognitosync}
        '''
        result = self._values.get("cognitosync")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def comprehend(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#comprehend AwsProvider#comprehend}
        '''
        result = self._values.get("comprehend")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def comprehendmedical(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#comprehendmedical AwsProvider#comprehendmedical}
        '''
        result = self._values.get("comprehendmedical")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#config AwsProvider#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def configservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#configservice AwsProvider#configservice}
        '''
        result = self._values.get("configservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connect(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#connect AwsProvider#connect}
        '''
        result = self._values.get("connect")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connectcontactlens(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#connectcontactlens AwsProvider#connectcontactlens}
        '''
        result = self._values.get("connectcontactlens")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def connectparticipant(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#connectparticipant AwsProvider#connectparticipant}
        '''
        result = self._values.get("connectparticipant")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def costandusagereportservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#costandusagereportservice AwsProvider#costandusagereportservice}
        '''
        result = self._values.get("costandusagereportservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def costexplorer(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#costexplorer AwsProvider#costexplorer}
        '''
        result = self._values.get("costexplorer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cur(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#cur AwsProvider#cur}
        '''
        result = self._values.get("cur")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def databasemigration(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#databasemigration AwsProvider#databasemigration}
        '''
        result = self._values.get("databasemigration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def databasemigrationservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#databasemigrationservice AwsProvider#databasemigrationservice}
        '''
        result = self._values.get("databasemigrationservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dataexchange(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dataexchange AwsProvider#dataexchange}
        '''
        result = self._values.get("dataexchange")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datapipeline(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#datapipeline AwsProvider#datapipeline}
        '''
        result = self._values.get("datapipeline")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datasync(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#datasync AwsProvider#datasync}
        '''
        result = self._values.get("datasync")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dax(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dax AwsProvider#dax}
        '''
        result = self._values.get("dax")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def detective(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#detective AwsProvider#detective}
        '''
        result = self._values.get("detective")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def devicefarm(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#devicefarm AwsProvider#devicefarm}
        '''
        result = self._values.get("devicefarm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def devopsguru(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#devopsguru AwsProvider#devopsguru}
        '''
        result = self._values.get("devopsguru")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def directconnect(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#directconnect AwsProvider#directconnect}
        '''
        result = self._values.get("directconnect")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dlm(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dlm AwsProvider#dlm}
        '''
        result = self._values.get("dlm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dms(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dms AwsProvider#dms}
        '''
        result = self._values.get("dms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def docdb(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#docdb AwsProvider#docdb}
        '''
        result = self._values.get("docdb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ds(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ds AwsProvider#ds}
        '''
        result = self._values.get("ds")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dynamodb(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dynamodb AwsProvider#dynamodb}
        '''
        result = self._values.get("dynamodb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dynamodbstreams(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#dynamodbstreams AwsProvider#dynamodbstreams}
        '''
        result = self._values.get("dynamodbstreams")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ec2 AwsProvider#ec2}
        '''
        result = self._values.get("ec2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_instanceconnect(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ec2instanceconnect AwsProvider#ec2instanceconnect}
        '''
        result = self._values.get("ec2_instanceconnect")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecr(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ecr AwsProvider#ecr}
        '''
        result = self._values.get("ecr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecrpublic(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ecrpublic AwsProvider#ecrpublic}
        '''
        result = self._values.get("ecrpublic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecs(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ecs AwsProvider#ecs}
        '''
        result = self._values.get("ecs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def efs(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#efs AwsProvider#efs}
        '''
        result = self._values.get("efs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#eks AwsProvider#eks}
        '''
        result = self._values.get("eks")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elasticache(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticache AwsProvider#elasticache}
        '''
        result = self._values.get("elasticache")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elasticbeanstalk(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticbeanstalk AwsProvider#elasticbeanstalk}
        '''
        result = self._values.get("elasticbeanstalk")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elasticinference(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticinference AwsProvider#elasticinference}
        '''
        result = self._values.get("elasticinference")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elasticsearch(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticsearch AwsProvider#elasticsearch}
        '''
        result = self._values.get("elasticsearch")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elasticsearchservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elasticsearchservice AwsProvider#elasticsearchservice}
        '''
        result = self._values.get("elasticsearchservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elastictranscoder(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elastictranscoder AwsProvider#elastictranscoder}
        '''
        result = self._values.get("elastictranscoder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elb(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elb AwsProvider#elb}
        '''
        result = self._values.get("elb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def elbv2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#elbv2 AwsProvider#elbv2}
        '''
        result = self._values.get("elbv2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def emr(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#emr AwsProvider#emr}
        '''
        result = self._values.get("emr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def emrcontainers(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#emrcontainers AwsProvider#emrcontainers}
        '''
        result = self._values.get("emrcontainers")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def es(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#es AwsProvider#es}
        '''
        result = self._values.get("es")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eventbridge(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#eventbridge AwsProvider#eventbridge}
        '''
        result = self._values.get("eventbridge")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def events(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#events AwsProvider#events}
        '''
        result = self._values.get("events")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def finspace(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#finspace AwsProvider#finspace}
        '''
        result = self._values.get("finspace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def finspacedata(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#finspacedata AwsProvider#finspacedata}
        '''
        result = self._values.get("finspacedata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def firehose(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#firehose AwsProvider#firehose}
        '''
        result = self._values.get("firehose")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fis(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#fis AwsProvider#fis}
        '''
        result = self._values.get("fis")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fms(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#fms AwsProvider#fms}
        '''
        result = self._values.get("fms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forecast(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forecast AwsProvider#forecast}
        '''
        result = self._values.get("forecast")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forecastquery(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forecastquery AwsProvider#forecastquery}
        '''
        result = self._values.get("forecastquery")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forecastqueryservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forecastqueryservice AwsProvider#forecastqueryservice}
        '''
        result = self._values.get("forecastqueryservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def forecastservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#forecastservice AwsProvider#forecastservice}
        '''
        result = self._values.get("forecastservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frauddetector(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#frauddetector AwsProvider#frauddetector}
        '''
        result = self._values.get("frauddetector")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fsx(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#fsx AwsProvider#fsx}
        '''
        result = self._values.get("fsx")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gamelift(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#gamelift AwsProvider#gamelift}
        '''
        result = self._values.get("gamelift")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def glacier(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#glacier AwsProvider#glacier}
        '''
        result = self._values.get("glacier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def globalaccelerator(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#globalaccelerator AwsProvider#globalaccelerator}
        '''
        result = self._values.get("globalaccelerator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def glue(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#glue AwsProvider#glue}
        '''
        result = self._values.get("glue")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gluedatabrew(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#gluedatabrew AwsProvider#gluedatabrew}
        '''
        result = self._values.get("gluedatabrew")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def greengrass(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#greengrass AwsProvider#greengrass}
        '''
        result = self._values.get("greengrass")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def greengrassv2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#greengrassv2 AwsProvider#greengrassv2}
        '''
        result = self._values.get("greengrassv2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def groundstation(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#groundstation AwsProvider#groundstation}
        '''
        result = self._values.get("groundstation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def guardduty(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#guardduty AwsProvider#guardduty}
        '''
        result = self._values.get("guardduty")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def health(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#health AwsProvider#health}
        '''
        result = self._values.get("health")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def healthlake(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#healthlake AwsProvider#healthlake}
        '''
        result = self._values.get("healthlake")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def honeycode(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#honeycode AwsProvider#honeycode}
        '''
        result = self._values.get("honeycode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iam(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iam AwsProvider#iam}
        '''
        result = self._values.get("iam")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identitystore(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#identitystore AwsProvider#identitystore}
        '''
        result = self._values.get("identitystore")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def imagebuilder(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#imagebuilder AwsProvider#imagebuilder}
        '''
        result = self._values.get("imagebuilder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inspector(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#inspector AwsProvider#inspector}
        '''
        result = self._values.get("inspector")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iot(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iot AwsProvider#iot}
        '''
        result = self._values.get("iot")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iot1_clickdevices(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iot1clickdevices AwsProvider#iot1clickdevices}
        '''
        result = self._values.get("iot1_clickdevices")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iot1_clickdevicesservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iot1clickdevicesservice AwsProvider#iot1clickdevicesservice}
        '''
        result = self._values.get("iot1_clickdevicesservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iot1_clickprojects(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iot1clickprojects AwsProvider#iot1clickprojects}
        '''
        result = self._values.get("iot1_clickprojects")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotanalytics(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotanalytics AwsProvider#iotanalytics}
        '''
        result = self._values.get("iotanalytics")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotdataplane(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotdataplane AwsProvider#iotdataplane}
        '''
        result = self._values.get("iotdataplane")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotdeviceadvisor(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotdeviceadvisor AwsProvider#iotdeviceadvisor}
        '''
        result = self._values.get("iotdeviceadvisor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotevents(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotevents AwsProvider#iotevents}
        '''
        result = self._values.get("iotevents")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ioteventsdata(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ioteventsdata AwsProvider#ioteventsdata}
        '''
        result = self._values.get("ioteventsdata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotfleethub(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotfleethub AwsProvider#iotfleethub}
        '''
        result = self._values.get("iotfleethub")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotjobsdataplane(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotjobsdataplane AwsProvider#iotjobsdataplane}
        '''
        result = self._values.get("iotjobsdataplane")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotsecuretunneling(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotsecuretunneling AwsProvider#iotsecuretunneling}
        '''
        result = self._values.get("iotsecuretunneling")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotsitewise(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotsitewise AwsProvider#iotsitewise}
        '''
        result = self._values.get("iotsitewise")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotthingsgraph(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotthingsgraph AwsProvider#iotthingsgraph}
        '''
        result = self._values.get("iotthingsgraph")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def iotwireless(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#iotwireless AwsProvider#iotwireless}
        '''
        result = self._values.get("iotwireless")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kafka(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kafka AwsProvider#kafka}
        '''
        result = self._values.get("kafka")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kafkaconnect(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kafkaconnect AwsProvider#kafkaconnect}
        '''
        result = self._values.get("kafkaconnect")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kendra(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kendra AwsProvider#kendra}
        '''
        result = self._values.get("kendra")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kinesis(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesis AwsProvider#kinesis}
        '''
        result = self._values.get("kinesis")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kinesisanalytics(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisanalytics AwsProvider#kinesisanalytics}
        '''
        result = self._values.get("kinesisanalytics")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kinesisanalyticsv2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisanalyticsv2 AwsProvider#kinesisanalyticsv2}
        '''
        result = self._values.get("kinesisanalyticsv2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kinesisvideo(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisvideo AwsProvider#kinesisvideo}
        '''
        result = self._values.get("kinesisvideo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kinesisvideoarchivedmedia(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisvideoarchivedmedia AwsProvider#kinesisvideoarchivedmedia}
        '''
        result = self._values.get("kinesisvideoarchivedmedia")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kinesisvideomedia(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisvideomedia AwsProvider#kinesisvideomedia}
        '''
        result = self._values.get("kinesisvideomedia")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kinesisvideosignalingchannels(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kinesisvideosignalingchannels AwsProvider#kinesisvideosignalingchannels}
        '''
        result = self._values.get("kinesisvideosignalingchannels")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#kms AwsProvider#kms}
        '''
        result = self._values.get("kms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lakeformation(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lakeformation AwsProvider#lakeformation}
        '''
        result = self._values.get("lakeformation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lambda_(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lambda AwsProvider#lambda}
        '''
        result = self._values.get("lambda_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lexmodelbuilding(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexmodelbuilding AwsProvider#lexmodelbuilding}
        '''
        result = self._values.get("lexmodelbuilding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lexmodelbuildingservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexmodelbuildingservice AwsProvider#lexmodelbuildingservice}
        '''
        result = self._values.get("lexmodelbuildingservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lexmodels(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexmodels AwsProvider#lexmodels}
        '''
        result = self._values.get("lexmodels")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lexmodelsv2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexmodelsv2 AwsProvider#lexmodelsv2}
        '''
        result = self._values.get("lexmodelsv2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lexruntime(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexruntime AwsProvider#lexruntime}
        '''
        result = self._values.get("lexruntime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lexruntimeservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexruntimeservice AwsProvider#lexruntimeservice}
        '''
        result = self._values.get("lexruntimeservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lexruntimev2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lexruntimev2 AwsProvider#lexruntimev2}
        '''
        result = self._values.get("lexruntimev2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def licensemanager(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#licensemanager AwsProvider#licensemanager}
        '''
        result = self._values.get("licensemanager")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lightsail(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lightsail AwsProvider#lightsail}
        '''
        result = self._values.get("lightsail")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def location(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#location AwsProvider#location}
        '''
        result = self._values.get("location")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lookoutequipment(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lookoutequipment AwsProvider#lookoutequipment}
        '''
        result = self._values.get("lookoutequipment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lookoutforvision(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lookoutforvision AwsProvider#lookoutforvision}
        '''
        result = self._values.get("lookoutforvision")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lookoutmetrics(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#lookoutmetrics AwsProvider#lookoutmetrics}
        '''
        result = self._values.get("lookoutmetrics")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def machinelearning(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#machinelearning AwsProvider#machinelearning}
        '''
        result = self._values.get("machinelearning")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def macie(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#macie AwsProvider#macie}
        '''
        result = self._values.get("macie")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def macie2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#macie2 AwsProvider#macie2}
        '''
        result = self._values.get("macie2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def managedblockchain(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#managedblockchain AwsProvider#managedblockchain}
        '''
        result = self._values.get("managedblockchain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def marketplacecatalog(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplacecatalog AwsProvider#marketplacecatalog}
        '''
        result = self._values.get("marketplacecatalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def marketplacecommerceanalytics(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplacecommerceanalytics AwsProvider#marketplacecommerceanalytics}
        '''
        result = self._values.get("marketplacecommerceanalytics")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def marketplaceentitlement(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplaceentitlement AwsProvider#marketplaceentitlement}
        '''
        result = self._values.get("marketplaceentitlement")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def marketplaceentitlementservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplaceentitlementservice AwsProvider#marketplaceentitlementservice}
        '''
        result = self._values.get("marketplaceentitlementservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def marketplacemetering(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#marketplacemetering AwsProvider#marketplacemetering}
        '''
        result = self._values.get("marketplacemetering")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mediaconnect(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediaconnect AwsProvider#mediaconnect}
        '''
        result = self._values.get("mediaconnect")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mediaconvert(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediaconvert AwsProvider#mediaconvert}
        '''
        result = self._values.get("mediaconvert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def medialive(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#medialive AwsProvider#medialive}
        '''
        result = self._values.get("medialive")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mediapackage(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediapackage AwsProvider#mediapackage}
        '''
        result = self._values.get("mediapackage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mediapackagevod(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediapackagevod AwsProvider#mediapackagevod}
        '''
        result = self._values.get("mediapackagevod")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mediastore(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediastore AwsProvider#mediastore}
        '''
        result = self._values.get("mediastore")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mediastoredata(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediastoredata AwsProvider#mediastoredata}
        '''
        result = self._values.get("mediastoredata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mediatailor(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mediatailor AwsProvider#mediatailor}
        '''
        result = self._values.get("mediatailor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memorydb(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#memorydb AwsProvider#memorydb}
        '''
        result = self._values.get("memorydb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mgn(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mgn AwsProvider#mgn}
        '''
        result = self._values.get("mgn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def migrationhub(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#migrationhub AwsProvider#migrationhub}
        '''
        result = self._values.get("migrationhub")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def migrationhubconfig(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#migrationhubconfig AwsProvider#migrationhubconfig}
        '''
        result = self._values.get("migrationhubconfig")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mobile(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mobile AwsProvider#mobile}
        '''
        result = self._values.get("mobile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mobileanalytics(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mobileanalytics AwsProvider#mobileanalytics}
        '''
        result = self._values.get("mobileanalytics")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mq(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mq AwsProvider#mq}
        '''
        result = self._values.get("mq")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mturk(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mturk AwsProvider#mturk}
        '''
        result = self._values.get("mturk")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mwaa(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#mwaa AwsProvider#mwaa}
        '''
        result = self._values.get("mwaa")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def neptune(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#neptune AwsProvider#neptune}
        '''
        result = self._values.get("neptune")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def networkfirewall(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#networkfirewall AwsProvider#networkfirewall}
        '''
        result = self._values.get("networkfirewall")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def networkmanager(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#networkmanager AwsProvider#networkmanager}
        '''
        result = self._values.get("networkmanager")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nimblestudio(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#nimblestudio AwsProvider#nimblestudio}
        '''
        result = self._values.get("nimblestudio")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def opsworks(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#opsworks AwsProvider#opsworks}
        '''
        result = self._values.get("opsworks")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def opsworkscm(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#opsworkscm AwsProvider#opsworkscm}
        '''
        result = self._values.get("opsworkscm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organizations(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#organizations AwsProvider#organizations}
        '''
        result = self._values.get("organizations")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def outposts(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#outposts AwsProvider#outposts}
        '''
        result = self._values.get("outposts")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def personalize(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#personalize AwsProvider#personalize}
        '''
        result = self._values.get("personalize")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def personalizeevents(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#personalizeevents AwsProvider#personalizeevents}
        '''
        result = self._values.get("personalizeevents")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def personalizeruntime(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#personalizeruntime AwsProvider#personalizeruntime}
        '''
        result = self._values.get("personalizeruntime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pi(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pi AwsProvider#pi}
        '''
        result = self._values.get("pi")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pinpoint(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pinpoint AwsProvider#pinpoint}
        '''
        result = self._values.get("pinpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pinpointemail(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pinpointemail AwsProvider#pinpointemail}
        '''
        result = self._values.get("pinpointemail")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pinpointsmsvoice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pinpointsmsvoice AwsProvider#pinpointsmsvoice}
        '''
        result = self._values.get("pinpointsmsvoice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def polly(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#polly AwsProvider#polly}
        '''
        result = self._values.get("polly")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pricing(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#pricing AwsProvider#pricing}
        '''
        result = self._values.get("pricing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prometheus(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#prometheus AwsProvider#prometheus}
        '''
        result = self._values.get("prometheus")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prometheusservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#prometheusservice AwsProvider#prometheusservice}
        '''
        result = self._values.get("prometheusservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proton(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#proton AwsProvider#proton}
        '''
        result = self._values.get("proton")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def qldb(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#qldb AwsProvider#qldb}
        '''
        result = self._values.get("qldb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def qldbsession(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#qldbsession AwsProvider#qldbsession}
        '''
        result = self._values.get("qldbsession")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def quicksight(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#quicksight AwsProvider#quicksight}
        '''
        result = self._values.get("quicksight")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ram(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ram AwsProvider#ram}
        '''
        result = self._values.get("ram")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rds(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#rds AwsProvider#rds}
        '''
        result = self._values.get("rds")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdsdata(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#rdsdata AwsProvider#rdsdata}
        '''
        result = self._values.get("rdsdata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdsdataservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#rdsdataservice AwsProvider#rdsdataservice}
        '''
        result = self._values.get("rdsdataservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redshift(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#redshift AwsProvider#redshift}
        '''
        result = self._values.get("redshift")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redshiftdata(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#redshiftdata AwsProvider#redshiftdata}
        '''
        result = self._values.get("redshiftdata")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rekognition(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#rekognition AwsProvider#rekognition}
        '''
        result = self._values.get("rekognition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resourcegroups(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#resourcegroups AwsProvider#resourcegroups}
        '''
        result = self._values.get("resourcegroups")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resourcegroupstagging(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#resourcegroupstagging AwsProvider#resourcegroupstagging}
        '''
        result = self._values.get("resourcegroupstagging")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resourcegroupstaggingapi(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#resourcegroupstaggingapi AwsProvider#resourcegroupstaggingapi}
        '''
        result = self._values.get("resourcegroupstaggingapi")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def robomaker(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#robomaker AwsProvider#robomaker}
        '''
        result = self._values.get("robomaker")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route53(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53 AwsProvider#route53}
        '''
        result = self._values.get("route53")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route53_domains(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53domains AwsProvider#route53domains}
        '''
        result = self._values.get("route53_domains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route53_recoverycontrolconfig(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53recoverycontrolconfig AwsProvider#route53recoverycontrolconfig}
        '''
        result = self._values.get("route53_recoverycontrolconfig")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route53_recoveryreadiness(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53recoveryreadiness AwsProvider#route53recoveryreadiness}
        '''
        result = self._values.get("route53_recoveryreadiness")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route53_resolver(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#route53resolver AwsProvider#route53resolver}
        '''
        result = self._values.get("route53_resolver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#s3 AwsProvider#s3}
        '''
        result = self._values.get("s3")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_control(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#s3control AwsProvider#s3control}
        '''
        result = self._values.get("s3_control")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def s3_outposts(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#s3outposts AwsProvider#s3outposts}
        '''
        result = self._values.get("s3_outposts")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sagemaker(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sagemaker AwsProvider#sagemaker}
        '''
        result = self._values.get("sagemaker")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sagemakeredgemanager(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sagemakeredgemanager AwsProvider#sagemakeredgemanager}
        '''
        result = self._values.get("sagemakeredgemanager")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sagemakerfeaturestoreruntime(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sagemakerfeaturestoreruntime AwsProvider#sagemakerfeaturestoreruntime}
        '''
        result = self._values.get("sagemakerfeaturestoreruntime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sagemakerruntime(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sagemakerruntime AwsProvider#sagemakerruntime}
        '''
        result = self._values.get("sagemakerruntime")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def savingsplans(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#savingsplans AwsProvider#savingsplans}
        '''
        result = self._values.get("savingsplans")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schemas(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#schemas AwsProvider#schemas}
        '''
        result = self._values.get("schemas")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sdb(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sdb AwsProvider#sdb}
        '''
        result = self._values.get("sdb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secretsmanager(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#secretsmanager AwsProvider#secretsmanager}
        '''
        result = self._values.get("secretsmanager")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def securityhub(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#securityhub AwsProvider#securityhub}
        '''
        result = self._values.get("securityhub")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serverlessapplicationrepository(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#serverlessapplicationrepository AwsProvider#serverlessapplicationrepository}
        '''
        result = self._values.get("serverlessapplicationrepository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serverlessapprepo(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#serverlessapprepo AwsProvider#serverlessapprepo}
        '''
        result = self._values.get("serverlessapprepo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serverlessrepo(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#serverlessrepo AwsProvider#serverlessrepo}
        '''
        result = self._values.get("serverlessrepo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def servicecatalog(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#servicecatalog AwsProvider#servicecatalog}
        '''
        result = self._values.get("servicecatalog")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def servicediscovery(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#servicediscovery AwsProvider#servicediscovery}
        '''
        result = self._values.get("servicediscovery")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def servicequotas(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#servicequotas AwsProvider#servicequotas}
        '''
        result = self._values.get("servicequotas")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ses(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ses AwsProvider#ses}
        '''
        result = self._values.get("ses")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sesv2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sesv2 AwsProvider#sesv2}
        '''
        result = self._values.get("sesv2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sfn(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sfn AwsProvider#sfn}
        '''
        result = self._values.get("sfn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def shield(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#shield AwsProvider#shield}
        '''
        result = self._values.get("shield")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signer(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#signer AwsProvider#signer}
        '''
        result = self._values.get("signer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def simpledb(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#simpledb AwsProvider#simpledb}
        '''
        result = self._values.get("simpledb")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sms(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sms AwsProvider#sms}
        '''
        result = self._values.get("sms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snowball(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#snowball AwsProvider#snowball}
        '''
        result = self._values.get("snowball")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sns(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sns AwsProvider#sns}
        '''
        result = self._values.get("sns")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sqs(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sqs AwsProvider#sqs}
        '''
        result = self._values.get("sqs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssm(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssm AwsProvider#ssm}
        '''
        result = self._values.get("ssm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssmcontacts(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssmcontacts AwsProvider#ssmcontacts}
        '''
        result = self._values.get("ssmcontacts")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssmincidents(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssmincidents AwsProvider#ssmincidents}
        '''
        result = self._values.get("ssmincidents")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sso(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sso AwsProvider#sso}
        '''
        result = self._values.get("sso")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssoadmin(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssoadmin AwsProvider#ssoadmin}
        '''
        result = self._values.get("ssoadmin")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssooidc(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#ssooidc AwsProvider#ssooidc}
        '''
        result = self._values.get("ssooidc")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stepfunctions(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#stepfunctions AwsProvider#stepfunctions}
        '''
        result = self._values.get("stepfunctions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storagegateway(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#storagegateway AwsProvider#storagegateway}
        '''
        result = self._values.get("storagegateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sts(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#sts AwsProvider#sts}
        '''
        result = self._values.get("sts")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def support(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#support AwsProvider#support}
        '''
        result = self._values.get("support")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def swf(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#swf AwsProvider#swf}
        '''
        result = self._values.get("swf")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def synthetics(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#synthetics AwsProvider#synthetics}
        '''
        result = self._values.get("synthetics")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def textract(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#textract AwsProvider#textract}
        '''
        result = self._values.get("textract")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timestreamquery(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#timestreamquery AwsProvider#timestreamquery}
        '''
        result = self._values.get("timestreamquery")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timestreamwrite(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#timestreamwrite AwsProvider#timestreamwrite}
        '''
        result = self._values.get("timestreamwrite")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transcribe(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transcribe AwsProvider#transcribe}
        '''
        result = self._values.get("transcribe")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transcribeservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transcribeservice AwsProvider#transcribeservice}
        '''
        result = self._values.get("transcribeservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transcribestreaming(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transcribestreaming AwsProvider#transcribestreaming}
        '''
        result = self._values.get("transcribestreaming")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transcribestreamingservice(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transcribestreamingservice AwsProvider#transcribestreamingservice}
        '''
        result = self._values.get("transcribestreamingservice")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transfer(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#transfer AwsProvider#transfer}
        '''
        result = self._values.get("transfer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def translate(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#translate AwsProvider#translate}
        '''
        result = self._values.get("translate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def waf(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#waf AwsProvider#waf}
        '''
        result = self._values.get("waf")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wafregional(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#wafregional AwsProvider#wafregional}
        '''
        result = self._values.get("wafregional")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wafv2(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#wafv2 AwsProvider#wafv2}
        '''
        result = self._values.get("wafv2")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wellarchitected(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#wellarchitected AwsProvider#wellarchitected}
        '''
        result = self._values.get("wellarchitected")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workdocs(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#workdocs AwsProvider#workdocs}
        '''
        result = self._values.get("workdocs")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def worklink(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#worklink AwsProvider#worklink}
        '''
        result = self._values.get("worklink")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workmail(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#workmail AwsProvider#workmail}
        '''
        result = self._values.get("workmail")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workmailmessageflow(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#workmailmessageflow AwsProvider#workmailmessageflow}
        '''
        result = self._values.get("workmailmessageflow")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def workspaces(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#workspaces AwsProvider#workspaces}
        '''
        result = self._values.get("workspaces")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def xray(self) -> typing.Optional[builtins.str]:
        '''Use this to override the default service endpoint URL.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#xray AwsProvider#xray}
        '''
        result = self._values.get("xray")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsProviderEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.AwsProviderIgnoreTags",
    jsii_struct_bases=[],
    name_mapping={"key_prefixes": "keyPrefixes", "keys": "keys"},
)
class AwsProviderIgnoreTags:
    def __init__(
        self,
        *,
        key_prefixes: typing.Optional[typing.Sequence[builtins.str]] = None,
        keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param key_prefixes: Resource tag key prefixes to ignore across all resources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#key_prefixes AwsProvider#key_prefixes}
        :param keys: Resource tag keys to ignore across all resources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#keys AwsProvider#keys}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if key_prefixes is not None:
            self._values["key_prefixes"] = key_prefixes
        if keys is not None:
            self._values["keys"] = keys

    @builtins.property
    def key_prefixes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Resource tag key prefixes to ignore across all resources.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#key_prefixes AwsProvider#key_prefixes}
        '''
        result = self._values.get("key_prefixes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Resource tag keys to ignore across all resources.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws#keys AwsProvider#keys}
        '''
        result = self._values.get("keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AwsProviderIgnoreTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudcontrolapiResource(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.CloudcontrolapiResource",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource aws_cloudcontrolapi_resource}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        desired_state: builtins.str,
        type_name: builtins.str,
        role_arn: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["CloudcontrolapiResourceTimeouts"] = None,
        type_version_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource aws_cloudcontrolapi_resource} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param desired_state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#desired_state CloudcontrolapiResource#desired_state}.
        :param type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#type_name CloudcontrolapiResource#type_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#role_arn CloudcontrolapiResource#role_arn}.
        :param schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#schema CloudcontrolapiResource#schema}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#timeouts CloudcontrolapiResource#timeouts}
        :param type_version_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#type_version_id CloudcontrolapiResource#type_version_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CloudcontrolapiResourceConfig(
            desired_state=desired_state,
            type_name=type_name,
            role_arn=role_arn,
            schema=schema,
            timeouts=timeouts,
            type_version_id=type_version_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#create CloudcontrolapiResource#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#delete CloudcontrolapiResource#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#update CloudcontrolapiResource#update}.
        '''
        value = CloudcontrolapiResourceTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetRoleArn")
    def reset_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleArn", []))

    @jsii.member(jsii_name="resetSchema")
    def reset_schema(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchema", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTypeVersionId")
    def reset_type_version_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeVersionId", []))

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
    @jsii.member(jsii_name="properties")
    def properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "properties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "CloudcontrolapiResourceTimeoutsOutputReference":
        return typing.cast("CloudcontrolapiResourceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="desiredStateInput")
    def desired_state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "desiredStateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schemaInput")
    def schema_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "schemaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["CloudcontrolapiResourceTimeouts"]:
        return typing.cast(typing.Optional["CloudcontrolapiResourceTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeNameInput")
    def type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeVersionIdInput")
    def type_version_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeVersionIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="desiredState")
    def desired_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "desiredState"))

    @desired_state.setter
    def desired_state(self, value: builtins.str) -> None:
        jsii.set(self, "desiredState", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schema")
    def schema(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "schema"))

    @schema.setter
    def schema(self, value: builtins.str) -> None:
        jsii.set(self, "schema", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        jsii.set(self, "typeName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeVersionId")
    def type_version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeVersionId"))

    @type_version_id.setter
    def type_version_id(self, value: builtins.str) -> None:
        jsii.set(self, "typeVersionId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.CloudcontrolapiResourceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "desired_state": "desiredState",
        "type_name": "typeName",
        "role_arn": "roleArn",
        "schema": "schema",
        "timeouts": "timeouts",
        "type_version_id": "typeVersionId",
    },
)
class CloudcontrolapiResourceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        desired_state: builtins.str,
        type_name: builtins.str,
        role_arn: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional["CloudcontrolapiResourceTimeouts"] = None,
        type_version_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param desired_state: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#desired_state CloudcontrolapiResource#desired_state}.
        :param type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#type_name CloudcontrolapiResource#type_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#role_arn CloudcontrolapiResource#role_arn}.
        :param schema: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#schema CloudcontrolapiResource#schema}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#timeouts CloudcontrolapiResource#timeouts}
        :param type_version_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#type_version_id CloudcontrolapiResource#type_version_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = CloudcontrolapiResourceTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "desired_state": desired_state,
            "type_name": type_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if schema is not None:
            self._values["schema"] = schema
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if type_version_id is not None:
            self._values["type_version_id"] = type_version_id

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
    def desired_state(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#desired_state CloudcontrolapiResource#desired_state}.'''
        result = self._values.get("desired_state")
        assert result is not None, "Required property 'desired_state' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#type_name CloudcontrolapiResource#type_name}.'''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#role_arn CloudcontrolapiResource#role_arn}.'''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#schema CloudcontrolapiResource#schema}.'''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["CloudcontrolapiResourceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#timeouts CloudcontrolapiResource#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["CloudcontrolapiResourceTimeouts"], result)

    @builtins.property
    def type_version_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#type_version_id CloudcontrolapiResource#type_version_id}.'''
        result = self._values.get("type_version_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudcontrolapiResourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.CloudcontrolapiResourceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class CloudcontrolapiResourceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#create CloudcontrolapiResource#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#delete CloudcontrolapiResource#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#update CloudcontrolapiResource#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#create CloudcontrolapiResource#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#delete CloudcontrolapiResource#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/cloudcontrolapi_resource#update CloudcontrolapiResource#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudcontrolapiResourceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudcontrolapiResourceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.CloudcontrolapiResourceTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudcontrolapiResourceTimeouts]:
        return typing.cast(typing.Optional[CloudcontrolapiResourceTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudcontrolapiResourceTimeouts],
    ) -> None:
        jsii.set(self, "internalValue", value)


class DataAwsCloudcontrolapiResource(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.DataAwsCloudcontrolapiResource",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource aws_cloudcontrolapi_resource}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identifier: builtins.str,
        type_name: builtins.str,
        role_arn: typing.Optional[builtins.str] = None,
        type_version_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource aws_cloudcontrolapi_resource} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#identifier DataAwsCloudcontrolapiResource#identifier}.
        :param type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#type_name DataAwsCloudcontrolapiResource#type_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#role_arn DataAwsCloudcontrolapiResource#role_arn}.
        :param type_version_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#type_version_id DataAwsCloudcontrolapiResource#type_version_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsCloudcontrolapiResourceConfig(
            identifier=identifier,
            type_name=type_name,
            role_arn=role_arn,
            type_version_id=type_version_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetRoleArn")
    def reset_role_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleArn", []))

    @jsii.member(jsii_name="resetTypeVersionId")
    def reset_type_version_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTypeVersionId", []))

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
    @jsii.member(jsii_name="properties")
    def properties(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "properties"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifierInput")
    def identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identifierInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeNameInput")
    def type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeVersionIdInput")
    def type_version_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeVersionIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identifier"))

    @identifier.setter
    def identifier(self, value: builtins.str) -> None:
        jsii.set(self, "identifier", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        jsii.set(self, "typeName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeVersionId")
    def type_version_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeVersionId"))

    @type_version_id.setter
    def type_version_id(self, value: builtins.str) -> None:
        jsii.set(self, "typeVersionId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.DataAwsCloudcontrolapiResourceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "identifier": "identifier",
        "type_name": "typeName",
        "role_arn": "roleArn",
        "type_version_id": "typeVersionId",
    },
)
class DataAwsCloudcontrolapiResourceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        identifier: builtins.str,
        type_name: builtins.str,
        role_arn: typing.Optional[builtins.str] = None,
        type_version_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param identifier: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#identifier DataAwsCloudcontrolapiResource#identifier}.
        :param type_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#type_name DataAwsCloudcontrolapiResource#type_name}.
        :param role_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#role_arn DataAwsCloudcontrolapiResource#role_arn}.
        :param type_version_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#type_version_id DataAwsCloudcontrolapiResource#type_version_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "identifier": identifier,
            "type_name": type_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if type_version_id is not None:
            self._values["type_version_id"] = type_version_id

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
    def identifier(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#identifier DataAwsCloudcontrolapiResource#identifier}.'''
        result = self._values.get("identifier")
        assert result is not None, "Required property 'identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#type_name DataAwsCloudcontrolapiResource#type_name}.'''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#role_arn DataAwsCloudcontrolapiResource#role_arn}.'''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type_version_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/cloudcontrolapi_resource#type_version_id DataAwsCloudcontrolapiResource#type_version_id}.'''
        result = self._values.get("type_version_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsCloudcontrolapiResourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsDefaultTags(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.DataAwsDefaultTags",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/default_tags aws_default_tags}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/default_tags aws_default_tags} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/default_tags#tags DataAwsDefaultTags#tags}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsDefaultTagsConfig(
            tags=tags,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.DataAwsDefaultTagsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "tags": "tags",
    },
)
class DataAwsDefaultTagsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/default_tags#tags DataAwsDefaultTags#tags}.
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
        if tags is not None:
            self._values["tags"] = tags

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
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/default_tags#tags DataAwsDefaultTags#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsDefaultTagsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIdentitystoreGroup(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.DataAwsIdentitystoreGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group aws_identitystore_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        filter: typing.Sequence["DataAwsIdentitystoreGroupFilter"],
        identity_store_id: builtins.str,
        group_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group aws_identitystore_group} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#filter DataAwsIdentitystoreGroup#filter}
        :param identity_store_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#identity_store_id DataAwsIdentitystoreGroup#identity_store_id}.
        :param group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#group_id DataAwsIdentitystoreGroup#group_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIdentitystoreGroupConfig(
            filter=filter,
            identity_store_id=identity_store_id,
            group_id=group_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetGroupId")
    def reset_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.List["DataAwsIdentitystoreGroupFilter"]]:
        return typing.cast(typing.Optional[typing.List["DataAwsIdentitystoreGroupFilter"]], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupIdInput")
    def group_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityStoreIdInput")
    def identity_store_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityStoreIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> typing.List["DataAwsIdentitystoreGroupFilter"]:
        return typing.cast(typing.List["DataAwsIdentitystoreGroupFilter"], jsii.get(self, "filter"))

    @filter.setter
    def filter(self, value: typing.List["DataAwsIdentitystoreGroupFilter"]) -> None:
        jsii.set(self, "filter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @group_id.setter
    def group_id(self, value: builtins.str) -> None:
        jsii.set(self, "groupId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityStoreId")
    def identity_store_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityStoreId"))

    @identity_store_id.setter
    def identity_store_id(self, value: builtins.str) -> None:
        jsii.set(self, "identityStoreId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.DataAwsIdentitystoreGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter": "filter",
        "identity_store_id": "identityStoreId",
        "group_id": "groupId",
    },
)
class DataAwsIdentitystoreGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter: typing.Sequence["DataAwsIdentitystoreGroupFilter"],
        identity_store_id: builtins.str,
        group_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#filter DataAwsIdentitystoreGroup#filter}
        :param identity_store_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#identity_store_id DataAwsIdentitystoreGroup#identity_store_id}.
        :param group_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#group_id DataAwsIdentitystoreGroup#group_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "filter": filter,
            "identity_store_id": identity_store_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if group_id is not None:
            self._values["group_id"] = group_id

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
    def filter(self) -> typing.List["DataAwsIdentitystoreGroupFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#filter DataAwsIdentitystoreGroup#filter}
        '''
        result = self._values.get("filter")
        assert result is not None, "Required property 'filter' is missing"
        return typing.cast(typing.List["DataAwsIdentitystoreGroupFilter"], result)

    @builtins.property
    def identity_store_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#identity_store_id DataAwsIdentitystoreGroup#identity_store_id}.'''
        result = self._values.get("identity_store_id")
        assert result is not None, "Required property 'identity_store_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#group_id DataAwsIdentitystoreGroup#group_id}.'''
        result = self._values.get("group_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIdentitystoreGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.DataAwsIdentitystoreGroupFilter",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_path": "attributePath",
        "attribute_value": "attributeValue",
    },
)
class DataAwsIdentitystoreGroupFilter:
    def __init__(
        self,
        *,
        attribute_path: builtins.str,
        attribute_value: builtins.str,
    ) -> None:
        '''
        :param attribute_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#attribute_path DataAwsIdentitystoreGroup#attribute_path}.
        :param attribute_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#attribute_value DataAwsIdentitystoreGroup#attribute_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "attribute_path": attribute_path,
            "attribute_value": attribute_value,
        }

    @builtins.property
    def attribute_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#attribute_path DataAwsIdentitystoreGroup#attribute_path}.'''
        result = self._values.get("attribute_path")
        assert result is not None, "Required property 'attribute_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_group#attribute_value DataAwsIdentitystoreGroup#attribute_value}.'''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIdentitystoreGroupFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsIdentitystoreUser(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.DataAwsIdentitystoreUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user aws_identitystore_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        filter: typing.Sequence["DataAwsIdentitystoreUserFilter"],
        identity_store_id: builtins.str,
        user_id: typing.Optional[builtins.str] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user aws_identitystore_user} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#filter DataAwsIdentitystoreUser#filter}
        :param identity_store_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#identity_store_id DataAwsIdentitystoreUser#identity_store_id}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#user_id DataAwsIdentitystoreUser#user_id}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataAwsIdentitystoreUserConfig(
            filter=filter,
            identity_store_id=identity_store_id,
            user_id=user_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetUserId")
    def reset_user_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserId", []))

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
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.List["DataAwsIdentitystoreUserFilter"]]:
        return typing.cast(typing.Optional[typing.List["DataAwsIdentitystoreUserFilter"]], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityStoreIdInput")
    def identity_store_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityStoreIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filter")
    def filter(self) -> typing.List["DataAwsIdentitystoreUserFilter"]:
        return typing.cast(typing.List["DataAwsIdentitystoreUserFilter"], jsii.get(self, "filter"))

    @filter.setter
    def filter(self, value: typing.List["DataAwsIdentitystoreUserFilter"]) -> None:
        jsii.set(self, "filter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityStoreId")
    def identity_store_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityStoreId"))

    @identity_store_id.setter
    def identity_store_id(self, value: builtins.str) -> None:
        jsii.set(self, "identityStoreId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        jsii.set(self, "userId", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.DataAwsIdentitystoreUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "filter": "filter",
        "identity_store_id": "identityStoreId",
        "user_id": "userId",
    },
)
class DataAwsIdentitystoreUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        filter: typing.Sequence["DataAwsIdentitystoreUserFilter"],
        identity_store_id: builtins.str,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#filter DataAwsIdentitystoreUser#filter}
        :param identity_store_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#identity_store_id DataAwsIdentitystoreUser#identity_store_id}.
        :param user_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#user_id DataAwsIdentitystoreUser#user_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "filter": filter,
            "identity_store_id": identity_store_id,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if user_id is not None:
            self._values["user_id"] = user_id

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
    def filter(self) -> typing.List["DataAwsIdentitystoreUserFilter"]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#filter DataAwsIdentitystoreUser#filter}
        '''
        result = self._values.get("filter")
        assert result is not None, "Required property 'filter' is missing"
        return typing.cast(typing.List["DataAwsIdentitystoreUserFilter"], result)

    @builtins.property
    def identity_store_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#identity_store_id DataAwsIdentitystoreUser#identity_store_id}.'''
        result = self._values.get("identity_store_id")
        assert result is not None, "Required property 'identity_store_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#user_id DataAwsIdentitystoreUser#user_id}.'''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIdentitystoreUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.DataAwsIdentitystoreUserFilter",
    jsii_struct_bases=[],
    name_mapping={
        "attribute_path": "attributePath",
        "attribute_value": "attributeValue",
    },
)
class DataAwsIdentitystoreUserFilter:
    def __init__(
        self,
        *,
        attribute_path: builtins.str,
        attribute_value: builtins.str,
    ) -> None:
        '''
        :param attribute_path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#attribute_path DataAwsIdentitystoreUser#attribute_path}.
        :param attribute_value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#attribute_value DataAwsIdentitystoreUser#attribute_value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "attribute_path": attribute_path,
            "attribute_value": attribute_value,
        }

    @builtins.property
    def attribute_path(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#attribute_path DataAwsIdentitystoreUser#attribute_path}.'''
        result = self._values.get("attribute_path")
        assert result is not None, "Required property 'attribute_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attribute_value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/d/identitystore_user#attribute_value DataAwsIdentitystoreUser#attribute_value}.'''
        result = self._values.get("attribute_value")
        assert result is not None, "Required property 'attribute_value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsIdentitystoreUserFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DetectiveGraph(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.DetectiveGraph",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/detective_graph aws_detective_graph}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/detective_graph aws_detective_graph} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/detective_graph#tags DetectiveGraph#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/detective_graph#tags_all DetectiveGraph#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DetectiveGraphConfig(
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdTime")
    def created_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="graphArn")
    def graph_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "graphArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.DetectiveGraphConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class DetectiveGraphConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/detective_graph#tags DetectiveGraph#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/detective_graph#tags_all DetectiveGraph#tags_all}.
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
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

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
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/detective_graph#tags DetectiveGraph#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/detective_graph#tags_all DetectiveGraph#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DetectiveGraphConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MemorydbAcl(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbAcl",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl aws_memorydb_acl}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl aws_memorydb_acl} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#name MemorydbAcl#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#name_prefix MemorydbAcl#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#tags MemorydbAcl#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#tags_all MemorydbAcl#tags_all}.
        :param user_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#user_names MemorydbAcl#user_names}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MemorydbAclConfig(
            name=name,
            name_prefix=name_prefix,
            tags=tags,
            tags_all=tags_all,
            user_names=user_names,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUserNames")
    def reset_user_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserNames", []))

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
    @jsii.member(jsii_name="minimumEngineVersion")
    def minimum_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimumEngineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNamesInput")
    def user_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "userNamesInput"))

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
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNames")
    def user_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "userNames"))

    @user_names.setter
    def user_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "userNames", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbAclConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "name_prefix": "namePrefix",
        "tags": "tags",
        "tags_all": "tagsAll",
        "user_names": "userNames",
    },
)
class MemorydbAclConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        user_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#name MemorydbAcl#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#name_prefix MemorydbAcl#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#tags MemorydbAcl#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#tags_all MemorydbAcl#tags_all}.
        :param user_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#user_names MemorydbAcl#user_names}.
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
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if user_names is not None:
            self._values["user_names"] = user_names

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
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#name MemorydbAcl#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#name_prefix MemorydbAcl#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#tags MemorydbAcl#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#tags_all MemorydbAcl#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def user_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_acl#user_names MemorydbAcl#user_names}.'''
        result = self._values.get("user_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbAclConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MemorydbCluster(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbCluster",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster aws_memorydb_cluster}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        acl_name: builtins.str,
        node_type: builtins.str,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        num_replicas_per_shard: typing.Optional[jsii.Number] = None,
        num_shards: typing.Optional[jsii.Number] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_name: typing.Optional[builtins.str] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        snapshot_window: typing.Optional[builtins.str] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
        subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["MemorydbClusterTimeouts"] = None,
        tls_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster aws_memorydb_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param acl_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#acl_name MemorydbCluster#acl_name}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#node_type MemorydbCluster#node_type}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#auto_minor_version_upgrade MemorydbCluster#auto_minor_version_upgrade}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#description MemorydbCluster#description}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#engine_version MemorydbCluster#engine_version}.
        :param final_snapshot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#final_snapshot_name MemorydbCluster#final_snapshot_name}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#kms_key_arn MemorydbCluster#kms_key_arn}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#maintenance_window MemorydbCluster#maintenance_window}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#name MemorydbCluster#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#name_prefix MemorydbCluster#name_prefix}.
        :param num_replicas_per_shard: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#num_replicas_per_shard MemorydbCluster#num_replicas_per_shard}.
        :param num_shards: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#num_shards MemorydbCluster#num_shards}.
        :param parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#parameter_group_name MemorydbCluster#parameter_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#port MemorydbCluster#port}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#security_group_ids MemorydbCluster#security_group_ids}.
        :param snapshot_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_arns MemorydbCluster#snapshot_arns}.
        :param snapshot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_name MemorydbCluster#snapshot_name}.
        :param snapshot_retention_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_retention_limit MemorydbCluster#snapshot_retention_limit}.
        :param snapshot_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_window MemorydbCluster#snapshot_window}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#sns_topic_arn MemorydbCluster#sns_topic_arn}.
        :param subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#subnet_group_name MemorydbCluster#subnet_group_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#tags MemorydbCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#tags_all MemorydbCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#timeouts MemorydbCluster#timeouts}
        :param tls_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#tls_enabled MemorydbCluster#tls_enabled}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MemorydbClusterConfig(
            acl_name=acl_name,
            node_type=node_type,
            auto_minor_version_upgrade=auto_minor_version_upgrade,
            description=description,
            engine_version=engine_version,
            final_snapshot_name=final_snapshot_name,
            kms_key_arn=kms_key_arn,
            maintenance_window=maintenance_window,
            name=name,
            name_prefix=name_prefix,
            num_replicas_per_shard=num_replicas_per_shard,
            num_shards=num_shards,
            parameter_group_name=parameter_group_name,
            port=port,
            security_group_ids=security_group_ids,
            snapshot_arns=snapshot_arns,
            snapshot_name=snapshot_name,
            snapshot_retention_limit=snapshot_retention_limit,
            snapshot_window=snapshot_window,
            sns_topic_arn=sns_topic_arn,
            subnet_group_name=subnet_group_name,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            tls_enabled=tls_enabled,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="clusterEndpoint")
    def cluster_endpoint(self, index: builtins.str) -> "MemorydbClusterClusterEndpoint":
        '''
        :param index: -
        '''
        return typing.cast("MemorydbClusterClusterEndpoint", jsii.invoke(self, "clusterEndpoint", [index]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#create MemorydbCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#delete MemorydbCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#update MemorydbCluster#update}.
        '''
        value = MemorydbClusterTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAutoMinorVersionUpgrade")
    def reset_auto_minor_version_upgrade(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoMinorVersionUpgrade", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEngineVersion")
    def reset_engine_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEngineVersion", []))

    @jsii.member(jsii_name="resetFinalSnapshotName")
    def reset_final_snapshot_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFinalSnapshotName", []))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @jsii.member(jsii_name="resetMaintenanceWindow")
    def reset_maintenance_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaintenanceWindow", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetNumReplicasPerShard")
    def reset_num_replicas_per_shard(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumReplicasPerShard", []))

    @jsii.member(jsii_name="resetNumShards")
    def reset_num_shards(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumShards", []))

    @jsii.member(jsii_name="resetParameterGroupName")
    def reset_parameter_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameterGroupName", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetSecurityGroupIds")
    def reset_security_group_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityGroupIds", []))

    @jsii.member(jsii_name="resetSnapshotArns")
    def reset_snapshot_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotArns", []))

    @jsii.member(jsii_name="resetSnapshotName")
    def reset_snapshot_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotName", []))

    @jsii.member(jsii_name="resetSnapshotRetentionLimit")
    def reset_snapshot_retention_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotRetentionLimit", []))

    @jsii.member(jsii_name="resetSnapshotWindow")
    def reset_snapshot_window(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotWindow", []))

    @jsii.member(jsii_name="resetSnsTopicArn")
    def reset_sns_topic_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnsTopicArn", []))

    @jsii.member(jsii_name="resetSubnetGroupName")
    def reset_subnet_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubnetGroupName", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTlsEnabled")
    def reset_tls_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsEnabled", []))

    @jsii.member(jsii_name="shards")
    def shards(self, index: builtins.str) -> "MemorydbClusterShards":
        '''
        :param index: -
        '''
        return typing.cast("MemorydbClusterShards", jsii.invoke(self, "shards", [index]))

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
    @jsii.member(jsii_name="enginePatchVersion")
    def engine_patch_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enginePatchVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MemorydbClusterTimeoutsOutputReference":
        return typing.cast("MemorydbClusterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclNameInput")
    def acl_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aclNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgradeInput")
    def auto_minor_version_upgrade_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "autoMinorVersionUpgradeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersionInput")
    def engine_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "engineVersionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="finalSnapshotNameInput")
    def final_snapshot_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "finalSnapshotNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindowInput")
    def maintenance_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maintenanceWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeTypeInput")
    def node_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeTypeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numReplicasPerShardInput")
    def num_replicas_per_shard_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numReplicasPerShardInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numShardsInput")
    def num_shards_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numShardsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupNameInput")
    def parameter_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parameterGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIdsInput")
    def security_group_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityGroupIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotArnsInput")
    def snapshot_arns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "snapshotArnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotNameInput")
    def snapshot_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimitInput")
    def snapshot_retention_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "snapshotRetentionLimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindowInput")
    def snapshot_window_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotWindowInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArnInput")
    def sns_topic_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snsTopicArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupNameInput")
    def subnet_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subnetGroupNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["MemorydbClusterTimeouts"]:
        return typing.cast(typing.Optional["MemorydbClusterTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsEnabledInput")
    def tls_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "tlsEnabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aclName")
    def acl_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aclName"))

    @acl_name.setter
    def acl_name(self, value: builtins.str) -> None:
        jsii.set(self, "aclName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "autoMinorVersionUpgrade"))

    @auto_minor_version_upgrade.setter
    def auto_minor_version_upgrade(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "autoMinorVersionUpgrade", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersion"))

    @engine_version.setter
    def engine_version(self, value: builtins.str) -> None:
        jsii.set(self, "engineVersion", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="finalSnapshotName")
    def final_snapshot_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "finalSnapshotName"))

    @final_snapshot_name.setter
    def final_snapshot_name(self, value: builtins.str) -> None:
        jsii.set(self, "finalSnapshotName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindow"))

    @maintenance_window.setter
    def maintenance_window(self, value: builtins.str) -> None:
        jsii.set(self, "maintenanceWindow", value)

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
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @node_type.setter
    def node_type(self, value: builtins.str) -> None:
        jsii.set(self, "nodeType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numReplicasPerShard")
    def num_replicas_per_shard(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numReplicasPerShard"))

    @num_replicas_per_shard.setter
    def num_replicas_per_shard(self, value: jsii.Number) -> None:
        jsii.set(self, "numReplicasPerShard", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numShards")
    def num_shards(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numShards"))

    @num_shards.setter
    def num_shards(self, value: jsii.Number) -> None:
        jsii.set(self, "numShards", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupName"))

    @parameter_group_name.setter
    def parameter_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "parameterGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        jsii.set(self, "port", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroupIds")
    def security_group_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityGroupIds"))

    @security_group_ids.setter
    def security_group_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityGroupIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotArns")
    def snapshot_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "snapshotArns"))

    @snapshot_arns.setter
    def snapshot_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "snapshotArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotName")
    def snapshot_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotName"))

    @snapshot_name.setter
    def snapshot_name(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimit")
    def snapshot_retention_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "snapshotRetentionLimit"))

    @snapshot_retention_limit.setter
    def snapshot_retention_limit(self, value: jsii.Number) -> None:
        jsii.set(self, "snapshotRetentionLimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindow")
    def snapshot_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotWindow"))

    @snapshot_window.setter
    def snapshot_window(self, value: builtins.str) -> None:
        jsii.set(self, "snapshotWindow", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snsTopicArn"))

    @sns_topic_arn.setter
    def sns_topic_arn(self, value: builtins.str) -> None:
        jsii.set(self, "snsTopicArn", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetGroupName"))

    @subnet_group_name.setter
    def subnet_group_name(self, value: builtins.str) -> None:
        jsii.set(self, "subnetGroupName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tlsEnabled")
    def tls_enabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "tlsEnabled"))

    @tls_enabled.setter
    def tls_enabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "tlsEnabled", value)


class MemorydbClusterClusterEndpoint(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbClusterClusterEndpoint",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbClusterConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "acl_name": "aclName",
        "node_type": "nodeType",
        "auto_minor_version_upgrade": "autoMinorVersionUpgrade",
        "description": "description",
        "engine_version": "engineVersion",
        "final_snapshot_name": "finalSnapshotName",
        "kms_key_arn": "kmsKeyArn",
        "maintenance_window": "maintenanceWindow",
        "name": "name",
        "name_prefix": "namePrefix",
        "num_replicas_per_shard": "numReplicasPerShard",
        "num_shards": "numShards",
        "parameter_group_name": "parameterGroupName",
        "port": "port",
        "security_group_ids": "securityGroupIds",
        "snapshot_arns": "snapshotArns",
        "snapshot_name": "snapshotName",
        "snapshot_retention_limit": "snapshotRetentionLimit",
        "snapshot_window": "snapshotWindow",
        "sns_topic_arn": "snsTopicArn",
        "subnet_group_name": "subnetGroupName",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
        "tls_enabled": "tlsEnabled",
    },
)
class MemorydbClusterConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        acl_name: builtins.str,
        node_type: builtins.str,
        auto_minor_version_upgrade: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        engine_version: typing.Optional[builtins.str] = None,
        final_snapshot_name: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        maintenance_window: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        num_replicas_per_shard: typing.Optional[jsii.Number] = None,
        num_shards: typing.Optional[jsii.Number] = None,
        parameter_group_name: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        security_group_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        snapshot_name: typing.Optional[builtins.str] = None,
        snapshot_retention_limit: typing.Optional[jsii.Number] = None,
        snapshot_window: typing.Optional[builtins.str] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
        subnet_group_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["MemorydbClusterTimeouts"] = None,
        tls_enabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param acl_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#acl_name MemorydbCluster#acl_name}.
        :param node_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#node_type MemorydbCluster#node_type}.
        :param auto_minor_version_upgrade: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#auto_minor_version_upgrade MemorydbCluster#auto_minor_version_upgrade}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#description MemorydbCluster#description}.
        :param engine_version: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#engine_version MemorydbCluster#engine_version}.
        :param final_snapshot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#final_snapshot_name MemorydbCluster#final_snapshot_name}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#kms_key_arn MemorydbCluster#kms_key_arn}.
        :param maintenance_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#maintenance_window MemorydbCluster#maintenance_window}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#name MemorydbCluster#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#name_prefix MemorydbCluster#name_prefix}.
        :param num_replicas_per_shard: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#num_replicas_per_shard MemorydbCluster#num_replicas_per_shard}.
        :param num_shards: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#num_shards MemorydbCluster#num_shards}.
        :param parameter_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#parameter_group_name MemorydbCluster#parameter_group_name}.
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#port MemorydbCluster#port}.
        :param security_group_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#security_group_ids MemorydbCluster#security_group_ids}.
        :param snapshot_arns: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_arns MemorydbCluster#snapshot_arns}.
        :param snapshot_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_name MemorydbCluster#snapshot_name}.
        :param snapshot_retention_limit: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_retention_limit MemorydbCluster#snapshot_retention_limit}.
        :param snapshot_window: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_window MemorydbCluster#snapshot_window}.
        :param sns_topic_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#sns_topic_arn MemorydbCluster#sns_topic_arn}.
        :param subnet_group_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#subnet_group_name MemorydbCluster#subnet_group_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#tags MemorydbCluster#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#tags_all MemorydbCluster#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#timeouts MemorydbCluster#timeouts}
        :param tls_enabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#tls_enabled MemorydbCluster#tls_enabled}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = MemorydbClusterTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "acl_name": acl_name,
            "node_type": node_type,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auto_minor_version_upgrade is not None:
            self._values["auto_minor_version_upgrade"] = auto_minor_version_upgrade
        if description is not None:
            self._values["description"] = description
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if final_snapshot_name is not None:
            self._values["final_snapshot_name"] = final_snapshot_name
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if maintenance_window is not None:
            self._values["maintenance_window"] = maintenance_window
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if num_replicas_per_shard is not None:
            self._values["num_replicas_per_shard"] = num_replicas_per_shard
        if num_shards is not None:
            self._values["num_shards"] = num_shards
        if parameter_group_name is not None:
            self._values["parameter_group_name"] = parameter_group_name
        if port is not None:
            self._values["port"] = port
        if security_group_ids is not None:
            self._values["security_group_ids"] = security_group_ids
        if snapshot_arns is not None:
            self._values["snapshot_arns"] = snapshot_arns
        if snapshot_name is not None:
            self._values["snapshot_name"] = snapshot_name
        if snapshot_retention_limit is not None:
            self._values["snapshot_retention_limit"] = snapshot_retention_limit
        if snapshot_window is not None:
            self._values["snapshot_window"] = snapshot_window
        if sns_topic_arn is not None:
            self._values["sns_topic_arn"] = sns_topic_arn
        if subnet_group_name is not None:
            self._values["subnet_group_name"] = subnet_group_name
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if tls_enabled is not None:
            self._values["tls_enabled"] = tls_enabled

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
    def acl_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#acl_name MemorydbCluster#acl_name}.'''
        result = self._values.get("acl_name")
        assert result is not None, "Required property 'acl_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def node_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#node_type MemorydbCluster#node_type}.'''
        result = self._values.get("node_type")
        assert result is not None, "Required property 'node_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_minor_version_upgrade(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#auto_minor_version_upgrade MemorydbCluster#auto_minor_version_upgrade}.'''
        result = self._values.get("auto_minor_version_upgrade")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#description MemorydbCluster#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def engine_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#engine_version MemorydbCluster#engine_version}.'''
        result = self._values.get("engine_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def final_snapshot_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#final_snapshot_name MemorydbCluster#final_snapshot_name}.'''
        result = self._values.get("final_snapshot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#kms_key_arn MemorydbCluster#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def maintenance_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#maintenance_window MemorydbCluster#maintenance_window}.'''
        result = self._values.get("maintenance_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#name MemorydbCluster#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#name_prefix MemorydbCluster#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_replicas_per_shard(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#num_replicas_per_shard MemorydbCluster#num_replicas_per_shard}.'''
        result = self._values.get("num_replicas_per_shard")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def num_shards(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#num_shards MemorydbCluster#num_shards}.'''
        result = self._values.get("num_shards")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def parameter_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#parameter_group_name MemorydbCluster#parameter_group_name}.'''
        result = self._values.get("parameter_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#port MemorydbCluster#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def security_group_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#security_group_ids MemorydbCluster#security_group_ids}.'''
        result = self._values.get("security_group_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_arns MemorydbCluster#snapshot_arns}.'''
        result = self._values.get("snapshot_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def snapshot_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_name MemorydbCluster#snapshot_name}.'''
        result = self._values.get("snapshot_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_retention_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_retention_limit MemorydbCluster#snapshot_retention_limit}.'''
        result = self._values.get("snapshot_retention_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def snapshot_window(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#snapshot_window MemorydbCluster#snapshot_window}.'''
        result = self._values.get("snapshot_window")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sns_topic_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#sns_topic_arn MemorydbCluster#sns_topic_arn}.'''
        result = self._values.get("sns_topic_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#subnet_group_name MemorydbCluster#subnet_group_name}.'''
        result = self._values.get("subnet_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#tags MemorydbCluster#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#tags_all MemorydbCluster#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MemorydbClusterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#timeouts MemorydbCluster#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MemorydbClusterTimeouts"], result)

    @builtins.property
    def tls_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#tls_enabled MemorydbCluster#tls_enabled}.'''
        result = self._values.get("tls_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MemorydbClusterShards(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbClusterShards",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodes")
    def nodes(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "nodes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numNodes")
    def num_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numNodes"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="slots")
    def slots(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "slots"))


class MemorydbClusterShardsNodes(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbClusterShardsNodes",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createTime")
    def create_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "endpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))


class MemorydbClusterShardsNodesEndpoint(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbClusterShardsNodesEndpoint",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbClusterTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class MemorydbClusterTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#create MemorydbCluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#delete MemorydbCluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#update MemorydbCluster#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#create MemorydbCluster#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#delete MemorydbCluster#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_cluster#update MemorydbCluster#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbClusterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MemorydbClusterTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbClusterTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MemorydbClusterTimeouts]:
        return typing.cast(typing.Optional[MemorydbClusterTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MemorydbClusterTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class MemorydbParameterGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbParameterGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group aws_memorydb_parameter_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        family: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["MemorydbParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group aws_memorydb_parameter_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#family MemorydbParameterGroup#family}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#description MemorydbParameterGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#name MemorydbParameterGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#name_prefix MemorydbParameterGroup#name_prefix}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#parameter MemorydbParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#tags MemorydbParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#tags_all MemorydbParameterGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MemorydbParameterGroupConfig(
            family=family,
            description=description,
            name=name,
            name_prefix=name_prefix,
            parameter=parameter,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetParameter")
    def reset_parameter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameter", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="familyInput")
    def family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "familyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterInput")
    def parameter_input(
        self,
    ) -> typing.Optional[typing.List["MemorydbParameterGroupParameter"]]:
        return typing.cast(typing.Optional[typing.List["MemorydbParameterGroupParameter"]], jsii.get(self, "parameterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="family")
    def family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "family"))

    @family.setter
    def family(self, value: builtins.str) -> None:
        jsii.set(self, "family", value)

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
    @jsii.member(jsii_name="parameter")
    def parameter(self) -> typing.List["MemorydbParameterGroupParameter"]:
        return typing.cast(typing.List["MemorydbParameterGroupParameter"], jsii.get(self, "parameter"))

    @parameter.setter
    def parameter(self, value: typing.List["MemorydbParameterGroupParameter"]) -> None:
        jsii.set(self, "parameter", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbParameterGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "family": "family",
        "description": "description",
        "name": "name",
        "name_prefix": "namePrefix",
        "parameter": "parameter",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class MemorydbParameterGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        family: builtins.str,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        parameter: typing.Optional[typing.Sequence["MemorydbParameterGroupParameter"]] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param family: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#family MemorydbParameterGroup#family}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#description MemorydbParameterGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#name MemorydbParameterGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#name_prefix MemorydbParameterGroup#name_prefix}.
        :param parameter: parameter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#parameter MemorydbParameterGroup#parameter}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#tags MemorydbParameterGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#tags_all MemorydbParameterGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "family": family,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if parameter is not None:
            self._values["parameter"] = parameter
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

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
    def family(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#family MemorydbParameterGroup#family}.'''
        result = self._values.get("family")
        assert result is not None, "Required property 'family' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#description MemorydbParameterGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#name MemorydbParameterGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#name_prefix MemorydbParameterGroup#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameter(
        self,
    ) -> typing.Optional[typing.List["MemorydbParameterGroupParameter"]]:
        '''parameter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#parameter MemorydbParameterGroup#parameter}
        '''
        result = self._values.get("parameter")
        return typing.cast(typing.Optional[typing.List["MemorydbParameterGroupParameter"]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#tags MemorydbParameterGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#tags_all MemorydbParameterGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbParameterGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbParameterGroupParameter",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class MemorydbParameterGroupParameter:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#name MemorydbParameterGroup#name}.
        :param value: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#value MemorydbParameterGroup#value}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#name MemorydbParameterGroup#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_parameter_group#value MemorydbParameterGroup#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbParameterGroupParameter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MemorydbSnapshot(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbSnapshot",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot aws_memorydb_snapshot}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        kms_key_arn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["MemorydbSnapshotTimeouts"] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot aws_memorydb_snapshot} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#cluster_name MemorydbSnapshot#cluster_name}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#kms_key_arn MemorydbSnapshot#kms_key_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#name MemorydbSnapshot#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#name_prefix MemorydbSnapshot#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#tags MemorydbSnapshot#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#tags_all MemorydbSnapshot#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#timeouts MemorydbSnapshot#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MemorydbSnapshotConfig(
            cluster_name=cluster_name,
            kms_key_arn=kms_key_arn,
            name=name,
            name_prefix=name_prefix,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="clusterConfiguration")
    def cluster_configuration(
        self,
        index: builtins.str,
    ) -> "MemorydbSnapshotClusterConfiguration":
        '''
        :param index: -
        '''
        return typing.cast("MemorydbSnapshotClusterConfiguration", jsii.invoke(self, "clusterConfiguration", [index]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#create MemorydbSnapshot#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#delete MemorydbSnapshot#delete}.
        '''
        value = MemorydbSnapshotTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetKmsKeyArn")
    def reset_kms_key_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKmsKeyArn", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

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
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "MemorydbSnapshotTimeoutsOutputReference":
        return typing.cast("MemorydbSnapshotTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArnInput")
    def kms_key_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kmsKeyArnInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(self) -> typing.Optional["MemorydbSnapshotTimeouts"]:
        return typing.cast(typing.Optional["MemorydbSnapshotTimeouts"], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        jsii.set(self, "clusterName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="kmsKeyArn")
    def kms_key_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kmsKeyArn"))

    @kms_key_arn.setter
    def kms_key_arn(self, value: builtins.str) -> None:
        jsii.set(self, "kmsKeyArn", value)

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
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


class MemorydbSnapshotClusterConfiguration(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbSnapshotClusterConfiguration",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "engineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maintenanceWindow")
    def maintenance_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maintenanceWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeType")
    def node_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="numShards")
    def num_shards(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numShards"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parameterGroupName")
    def parameter_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parameterGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotRetentionLimit")
    def snapshot_retention_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "snapshotRetentionLimit"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snapshotWindow")
    def snapshot_window(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotWindow"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetGroupName")
    def subnet_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnetGroupName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="topicArn")
    def topic_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "topicArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbSnapshotConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "cluster_name": "clusterName",
        "kms_key_arn": "kmsKeyArn",
        "name": "name",
        "name_prefix": "namePrefix",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class MemorydbSnapshotConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        cluster_name: builtins.str,
        kms_key_arn: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        timeouts: typing.Optional["MemorydbSnapshotTimeouts"] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param cluster_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#cluster_name MemorydbSnapshot#cluster_name}.
        :param kms_key_arn: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#kms_key_arn MemorydbSnapshot#kms_key_arn}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#name MemorydbSnapshot#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#name_prefix MemorydbSnapshot#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#tags MemorydbSnapshot#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#tags_all MemorydbSnapshot#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#timeouts MemorydbSnapshot#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timeouts, dict):
            timeouts = MemorydbSnapshotTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
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
    def cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#cluster_name MemorydbSnapshot#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#kms_key_arn MemorydbSnapshot#kms_key_arn}.'''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#name MemorydbSnapshot#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#name_prefix MemorydbSnapshot#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#tags MemorydbSnapshot#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#tags_all MemorydbSnapshot#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["MemorydbSnapshotTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#timeouts MemorydbSnapshot#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["MemorydbSnapshotTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbSnapshotConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbSnapshotTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class MemorydbSnapshotTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#create MemorydbSnapshot#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#delete MemorydbSnapshot#delete}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#create MemorydbSnapshot#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_snapshot#delete MemorydbSnapshot#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbSnapshotTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MemorydbSnapshotTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbSnapshotTimeoutsOutputReference",
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

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MemorydbSnapshotTimeouts]:
        return typing.cast(typing.Optional[MemorydbSnapshotTimeouts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[MemorydbSnapshotTimeouts]) -> None:
        jsii.set(self, "internalValue", value)


class MemorydbSubnetGroup(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbSubnetGroup",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group aws_memorydb_subnet_group}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        subnet_ids: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group aws_memorydb_subnet_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#subnet_ids MemorydbSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#description MemorydbSubnetGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#name MemorydbSubnetGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#name_prefix MemorydbSubnetGroup#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#tags MemorydbSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#tags_all MemorydbSubnetGroup#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MemorydbSubnetGroupConfig(
            subnet_ids=subnet_ids,
            description=description,
            name=name,
            name_prefix=name_prefix,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

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
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnetIdsInput")
    def subnet_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subnetIdsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        jsii.set(self, "description", value)

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
    @jsii.member(jsii_name="subnetIds")
    def subnet_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subnetIds"))

    @subnet_ids.setter
    def subnet_ids(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "subnetIds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbSubnetGroupConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "subnet_ids": "subnetIds",
        "description": "description",
        "name": "name",
        "name_prefix": "namePrefix",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class MemorydbSubnetGroupConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        subnet_ids: typing.Sequence[builtins.str],
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param subnet_ids: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#subnet_ids MemorydbSubnetGroup#subnet_ids}.
        :param description: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#description MemorydbSubnetGroup#description}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#name MemorydbSubnetGroup#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#name_prefix MemorydbSubnetGroup#name_prefix}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#tags MemorydbSubnetGroup#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#tags_all MemorydbSubnetGroup#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "subnet_ids": subnet_ids,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

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
    def subnet_ids(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#subnet_ids MemorydbSubnetGroup#subnet_ids}.'''
        result = self._values.get("subnet_ids")
        assert result is not None, "Required property 'subnet_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#description MemorydbSubnetGroup#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#name MemorydbSubnetGroup#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#name_prefix MemorydbSubnetGroup#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#tags MemorydbSubnetGroup#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_subnet_group#tags_all MemorydbSubnetGroup#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbSubnetGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MemorydbUser(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbUser",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user aws_memorydb_user}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        access_string: builtins.str,
        authentication_mode: "MemorydbUserAuthenticationMode",
        user_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user aws_memorydb_user} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#access_string MemorydbUser#access_string}.
        :param authentication_mode: authentication_mode block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#authentication_mode MemorydbUser#authentication_mode}
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#user_name MemorydbUser#user_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#tags MemorydbUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#tags_all MemorydbUser#tags_all}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = MemorydbUserConfig(
            access_string=access_string,
            authentication_mode=authentication_mode,
            user_name=user_name,
            tags=tags,
            tags_all=tags_all,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putAuthenticationMode")
    def put_authentication_mode(
        self,
        *,
        passwords: typing.Sequence[builtins.str],
        type: builtins.str,
    ) -> None:
        '''
        :param passwords: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#passwords MemorydbUser#passwords}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#type MemorydbUser#type}.
        '''
        value = MemorydbUserAuthenticationMode(passwords=passwords, type=type)

        return typing.cast(None, jsii.invoke(self, "putAuthenticationMode", [value]))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

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
    @jsii.member(jsii_name="authenticationMode")
    def authentication_mode(self) -> "MemorydbUserAuthenticationModeOutputReference":
        return typing.cast("MemorydbUserAuthenticationModeOutputReference", jsii.get(self, "authenticationMode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="minimumEngineVersion")
    def minimum_engine_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimumEngineVersion"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessStringInput")
    def access_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessStringInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticationModeInput")
    def authentication_mode_input(
        self,
    ) -> typing.Optional["MemorydbUserAuthenticationMode"]:
        return typing.cast(typing.Optional["MemorydbUserAuthenticationMode"], jsii.get(self, "authenticationModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userNameInput")
    def user_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessString")
    def access_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessString"))

    @access_string.setter
    def access_string(self, value: builtins.str) -> None:
        jsii.set(self, "accessString", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @tags.setter
    def tags(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userName")
    def user_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userName"))

    @user_name.setter
    def user_name(self, value: builtins.str) -> None:
        jsii.set(self, "userName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbUserAuthenticationMode",
    jsii_struct_bases=[],
    name_mapping={"passwords": "passwords", "type": "type"},
)
class MemorydbUserAuthenticationMode:
    def __init__(
        self,
        *,
        passwords: typing.Sequence[builtins.str],
        type: builtins.str,
    ) -> None:
        '''
        :param passwords: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#passwords MemorydbUser#passwords}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#type MemorydbUser#type}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "passwords": passwords,
            "type": type,
        }

    @builtins.property
    def passwords(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#passwords MemorydbUser#passwords}.'''
        result = self._values.get("passwords")
        assert result is not None, "Required property 'passwords' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#type MemorydbUser#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbUserAuthenticationMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MemorydbUserAuthenticationModeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.MemorydbUserAuthenticationModeOutputReference",
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
    @jsii.member(jsii_name="passwordsInput")
    def passwords_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "passwordsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwords")
    def passwords(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "passwords"))

    @passwords.setter
    def passwords(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "passwords", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MemorydbUserAuthenticationMode]:
        return typing.cast(typing.Optional[MemorydbUserAuthenticationMode], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MemorydbUserAuthenticationMode],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.MemorydbUserConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "access_string": "accessString",
        "authentication_mode": "authenticationMode",
        "user_name": "userName",
        "tags": "tags",
        "tags_all": "tagsAll",
    },
)
class MemorydbUserConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[typing.Union[jsii.Number, cdktf.IResolvable]] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        access_string: builtins.str,
        authentication_mode: MemorydbUserAuthenticationMode,
        user_name: builtins.str,
        tags: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
        tags_all: typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param access_string: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#access_string MemorydbUser#access_string}.
        :param authentication_mode: authentication_mode block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#authentication_mode MemorydbUser#authentication_mode}
        :param user_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#user_name MemorydbUser#user_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#tags MemorydbUser#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#tags_all MemorydbUser#tags_all}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(authentication_mode, dict):
            authentication_mode = MemorydbUserAuthenticationMode(**authentication_mode)
        self._values: typing.Dict[str, typing.Any] = {
            "access_string": access_string,
            "authentication_mode": authentication_mode,
            "user_name": user_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all

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
    def access_string(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#access_string MemorydbUser#access_string}.'''
        result = self._values.get("access_string")
        assert result is not None, "Required property 'access_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authentication_mode(self) -> MemorydbUserAuthenticationMode:
        '''authentication_mode block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#authentication_mode MemorydbUser#authentication_mode}
        '''
        result = self._values.get("authentication_mode")
        assert result is not None, "Required property 'authentication_mode' is missing"
        return typing.cast(MemorydbUserAuthenticationMode, result)

    @builtins.property
    def user_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#user_name MemorydbUser#user_name}.'''
        result = self._values.get("user_name")
        assert result is not None, "Required property 'user_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#tags MemorydbUser#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    @builtins.property
    def tags_all(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/memorydb_user#tags_all MemorydbUser#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.Mapping[builtins.str, builtins.str]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemorydbUserConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccountAlternateContact",
    "AccountAlternateContactConfig",
    "AwsProvider",
    "AwsProviderAssumeRole",
    "AwsProviderConfig",
    "AwsProviderDefaultTags",
    "AwsProviderEndpoints",
    "AwsProviderIgnoreTags",
    "CloudcontrolapiResource",
    "CloudcontrolapiResourceConfig",
    "CloudcontrolapiResourceTimeouts",
    "CloudcontrolapiResourceTimeoutsOutputReference",
    "DataAwsCloudcontrolapiResource",
    "DataAwsCloudcontrolapiResourceConfig",
    "DataAwsDefaultTags",
    "DataAwsDefaultTagsConfig",
    "DataAwsIdentitystoreGroup",
    "DataAwsIdentitystoreGroupConfig",
    "DataAwsIdentitystoreGroupFilter",
    "DataAwsIdentitystoreUser",
    "DataAwsIdentitystoreUserConfig",
    "DataAwsIdentitystoreUserFilter",
    "DetectiveGraph",
    "DetectiveGraphConfig",
    "MemorydbAcl",
    "MemorydbAclConfig",
    "MemorydbCluster",
    "MemorydbClusterClusterEndpoint",
    "MemorydbClusterConfig",
    "MemorydbClusterShards",
    "MemorydbClusterShardsNodes",
    "MemorydbClusterShardsNodesEndpoint",
    "MemorydbClusterTimeouts",
    "MemorydbClusterTimeoutsOutputReference",
    "MemorydbParameterGroup",
    "MemorydbParameterGroupConfig",
    "MemorydbParameterGroupParameter",
    "MemorydbSnapshot",
    "MemorydbSnapshotClusterConfiguration",
    "MemorydbSnapshotConfig",
    "MemorydbSnapshotTimeouts",
    "MemorydbSnapshotTimeoutsOutputReference",
    "MemorydbSubnetGroup",
    "MemorydbSubnetGroupConfig",
    "MemorydbUser",
    "MemorydbUserAuthenticationMode",
    "MemorydbUserAuthenticationModeOutputReference",
    "MemorydbUserConfig",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import accessanalyzer
from . import acm
from . import amplify
from . import apigateway
from . import apigatewayv2
from . import appautoscaling
from . import appconfig
from . import appmesh
from . import apprunner
from . import appstream
from . import appsync
from . import athena
from . import autoscaling
from . import autoscalingplans
from . import backup
from . import batch
from . import budgets
from . import chime
from . import cloud9
from . import cloudformation
from . import cloudfront
from . import cloudhsm
from . import cloudtrail
from . import cloudwatch
from . import codeartifact
from . import codebuild
from . import codecommit
from . import codedeploy
from . import codepipeline
from . import codestar
from . import cognito
from . import config
from . import connect
from . import cur
from . import datapipeline
from . import datasources
from . import datasync
from . import dax
from . import devicefarm
from . import directconnect
from . import directoryservice
from . import dlm
from . import dms
from . import documentdb
from . import dynamodb
from . import ec2
from . import ecr
from . import ecs
from . import efs
from . import eks
from . import elasticache
from . import elasticbeanstalk
from . import elasticsearch
from . import elastictranscoder
from . import elb
from . import emr
from . import eventbridge
from . import eventbridgeschemas
from . import fms
from . import fsx
from . import gamelift
from . import glacier
from . import globalaccelerator
from . import glue
from . import guardduty
from . import iam
from . import imagebuilder
from . import inspector
from . import iot
from . import kinesis
from . import kms
from . import lakeformation
from . import lambdafunction
from . import lex
from . import licensemanager
from . import lightsail
from . import macie
from . import macie2
from . import mediaconvert
from . import mediapackage
from . import mediastore
from . import mq
from . import msk
from . import mwaa
from . import neptune
from . import networkfirewall
from . import opsworks
from . import organizations
from . import outposts
from . import pinpoint
from . import pricing
from . import prometheus
from . import qldb
from . import quicksight
from . import ram
from . import rds
from . import redshift
from . import resourcegroups
from . import route53
from . import s3
from . import sagemaker
from . import secretsmanager
from . import securityhub
from . import serverlessapplicationrepository
from . import servicecatalog
from . import servicediscovery
from . import servicequotas
from . import ses
from . import sfn
from . import shield
from . import signer
from . import simpledb
from . import sns
from . import sqs
from . import ssm
from . import ssoadmin
from . import storagegateway
from . import swf
from . import synthetics
from . import timestreamwrite
from . import transfer
from . import vpc
from . import waf
from . import wafregional
from . import wafv2
from . import worklink
from . import workspaces
from . import xray
