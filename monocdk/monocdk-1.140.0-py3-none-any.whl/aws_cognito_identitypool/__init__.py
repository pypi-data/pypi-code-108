'''
# Amazon Cognito Identity Pool Construct Library

> **Identity Pools are in a separate module while the API is being stabilized. Once we stabilize the module, they will**
> **be included into the stable [aws-cognito](../aws-cognito) library. Please provide feedback on this experience by**
> **creating an [issue here](https://github.com/aws/aws-cdk/issues/new/choose)**

[Amazon Cognito Identity Pools](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-identity.html) enable you to grant your users access to other AWS services.

Identity Pools are one of the two main components of [Amazon Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html), which provides authentication, authorization, and
user management for your web and mobile apps. Your users can sign in directly with a user name and password, or through
a third party such as Facebook, Amazon, Google or Apple.

The other main component in Amazon Cognito is [user pools](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html). User Pools are user directories that provide sign-up and
sign-in options for your app users.

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

## Table of Contents

* [Identity Pools](#identity-pools)

  * [Authenticated and Unauthenticated Identities](#authenticated-and-unauthenticated-identities)
  * [Authentication Providers](#authentication-providers)

    * [User Pool Authentication Provider](#user-pool-authentication-provider)
    * [Server Side Token Check](#server-side-token-check)
    * [Associating an External Provider Directly](#associating-an-external-provider-directly)
    * [OpenIdConnect and Saml](#openid-connect-and-saml)
    * [Custom Providers](#custom-providers)
  * [Role Mapping](#role-mapping)

    * [Provider Urls](#provider-urls)
  * [Authentication Flow](#authentication-flow)
  * [Cognito Sync](#cognito-sync)
  * [Importing Identity Pools](#importing-identity-pools)

## Identity Pools

Identity pools provide temporary AWS credentials for users who are guests (unauthenticated) and for users who have been\
authenticated and received a token. An identity pool is a store of user identity data specific to an account.

Identity pools can be used in conjunction with Cognito User Pools or by accessing external federated identity providers\
directly. Learn more at [Amazon Cognito Identity Pools](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-identity.html).

### Authenticated and Unauthenticated Identities

Identity pools define two types of identities: authenticated(`user`) and unauthenticated (`guest`). Every identity in\
an identity pool is either authenticated or unauthenticated. Each identity pool has a default role for authenticated\
identities, and a default role for unauthenticated identities. Absent other overriding rules (see below), these are the\
roles that will be assumed by the corresponding users in the authentication process.

A basic Identity Pool with minimal configuration has no required props, with default authenticated (user) and\
unauthenticated (guest) roles applied to the identity pool:

```python
# Example automatically generated from non-compiling source. May contain errors.
cognito.IdentityPool(self, "myIdentityPool")
```

By default, both the authenticated and unauthenticated roles will have no permissions attached. Grant permissions
to roles using the public `authenticatedRole` and `unauthenticatedRole` properties:

```python
# Example automatically generated from non-compiling source. May contain errors.
identity_pool = cognito.IdentityPool(self, "myIdentityPool")
table = dynamodb.Table(self, "MyTable")

# Grant permissions to authenticated users
table.grant_read_write_data(identity_pool.authenticated_role)
# Grant permissions to unauthenticated guest users
table.grant_read(identity_pool.unauthenticated_role)

# Or add policy statements straight to the role
identity_pool.authenticated_role.add_to_principal_policy(PolicyStatement(
    effect=Effect.ALLOW,
    actions=["dynamodb:*"],
    resources=["*"]
))
```

The default roles can also be supplied in `IdentityPoolProps`:

```python
# Example automatically generated from non-compiling source. May contain errors.
stack = Stack()
authenticated_role = Role(stack, "authRole",
    assumed_by=ServicePrincipal("service.amazonaws.com")
)
unauthenticated_role = Role(stack, "unauthRole",
    assumed_by=ServicePrincipal("service.amazonaws.com")
)
identity_pool = IdentityPool(stack, "TestIdentityPoolActions",
    authenticated_role=authenticated_role, unauthenticated_role=unauthenticated_role
)
```

### Authentication Providers

Authenticated identities belong to users who are authenticated by a public login provider (Amazon Cognito user pools,\
Login with Amazon, Sign in with Apple, Facebook, Google, SAML, or any OpenID Connect Providers) or a developer provider\
(your own backend authentication process).

[Authentication providers](https://docs.aws.amazon.com/cognito/latest/developerguide/external-identity-providers.html) can be associated with an Identity Pool by first associating them with a Cognito User Pool or by\
associating the provider directly with the identity pool.

#### User Pool Authentication Provider

In order to attach a user pool to an identity pool as an authentication provider, the identity pool needs properties
from both the user pool and the user pool client. For this reason identity pools use a `UserPoolAuthenticationProvider`
to gather the necessary properties from the user pool constructs.

```python
# Example automatically generated from non-compiling source. May contain errors.
user_pool = cognito.UserPool(self, "Pool")

cognito.IdentityPool(self, "myidentitypool",
    identity_pool_name="myidentitypool",
    authentication_providers={
        "user_pools": [UserPoolAuthenticationProvider(user_pool=user_pool)]
    }
)
```

User pools can also be associated with an identity pool after instantiation. The Identity Pool's `addUserPoolAuthentication` method\
returns the User Pool Client that has been created:

```python
# Example automatically generated from non-compiling source. May contain errors.
user_pool = cognito.UserPool(self, "Pool")
user_pool_client = identity_pool.add_user_pool_authentication(
    user_pools=[UserPoolAuthenticationProvider(user_pool=user_pool)]
)
```

#### Server Side Token Check

With the `IdentityPool` CDK Construct, by default the pool is configured to check with the integrated user pools to\
make sure that the user has not been globally signed out or deleted before the identity pool provides an OIDC token or\
AWS credentials for the user.

If the user is signed out or deleted, the identity pool will return a 400 Not Authorized error. This setting can be\
disabled, however, in several ways.

Setting `disableServerSideTokenCheck` to true will change the default behavior to no server side token check. Learn\
more [here](https://docs.aws.amazon.com/cognitoidentity/latest/APIReference/API_CognitoIdentityProvider.html#CognitoIdentity-Type-CognitoIdentityProvider-ServerSideTokenCheck):

```python
# Example automatically generated from non-compiling source. May contain errors.
user_pool = cognito.UserPool(self, "Pool")
identity_pool.add_user_pool_authentication(
    user_pool=UserPoolAuthenticationProvider(
        user_pool=user_pool,
        disable_server_side_token_check=True
    )
)
```

#### Associating an External Provider Directly

One or more [external identity providers](https://docs.aws.amazon.com/cognito/latest/developerguide/external-identity-providers.html) can be associated with an identity pool directly using\
`authenticationProviders`:

```python
# Example automatically generated from non-compiling source. May contain errors.
cognito.IdentityPool(self, "myidentitypool",
    identity_pool_name="myidentitypool",
    authentication_providers={
        "amazon": {
            "app_id": "amzn1.application.12312k3j234j13rjiwuenf"
        },
        "facebook": {
            "app_id": "1234567890123"
        },
        "google": {
            "client_id": "12345678012.apps.googleusercontent.com"
        },
        "apple": {
            "services_id": "com.myappleapp.auth"
        },
        "twitter": {
            "consumer_key": "my-twitter-id",
            "consumer_secret": "my-twitter-secret"
        }
    }
)
```

To associate more than one provider of the same type with the identity pool, use User\
Pools, OpenIdConnect, or SAML. Only one provider per external service can be attached directly to the identity pool.

#### OpenId Connect and Saml

[OpenID Connect](https://docs.aws.amazon.com/cognito/latest/developerguide/open-id.html) is an open standard for\
authentication that is supported by a number of login providers. Amazon Cognito supports linking of identities with\
OpenID Connect providers that are configured through [AWS Identity and Access Management](http://aws.amazon.com/iam/).

An identity provider that supports [Security Assertion Markup Language 2.0 (SAML 2.0)](https://docs.aws.amazon.com/cognito/latest/developerguide/saml-identity-provider.html) can be used to provide a simple\
onboarding flow for users. The SAML-supporting identity provider specifies the IAM roles that can be assumed by users\
so that different users can be granted different sets of permissions. Associating an OpenId Connect or Saml provider\
with an identity pool:

```python
# Example automatically generated from non-compiling source. May contain errors.
open_id_connect_provider = iam.OpenIdConnectProvider(self, "my-openid-connect-provider", ...)
saml_provider = iam.SamlProvider(self, "my-saml-provider", ...)

cognito.IdentityPool(self, "myidentitypool",
    identity_pool_name="myidentitypool",
    authentication_providers={
        "open_id_connect_provider": open_id_connect_provider,
        "saml_provider": saml_provider
    }
)
```

#### Custom Providers

The identity pool's behavior can be customized further using custom [developer authenticated identities](https://docs.aws.amazon.com/cognito/latest/developerguide/developer-authenticated-identities.html).\
With developer authenticated identities, users can be registered and authenticated via an existing authentication\
process while still using Amazon Cognito to synchronize user data and access AWS resources.

Like the supported external providers, though, only one custom provider can be directly associated with the identity\
pool.

```python
# Example automatically generated from non-compiling source. May contain errors.
cognito.IdentityPool(self, "myidentitypool",
    identity_pool_name="myidentitypool",
    authentication_providers={
        "google": "12345678012.apps.googleusercontent.com",
        "open_id_connect_provider": open_id_connect_provider,
        "custom_provider": "my-custom-provider.example.com"
    }
)
```

### Role Mapping

In addition to setting default roles for authenticated and unauthenticated users, identity pools can also be used to\
define rules to choose the role for each user based on claims in the user's ID token by using Role Mapping. When using\
role mapping, it's important to be aware of some of the permissions the role will need. An in depth\
review of roles and role mapping can be found [here](https://docs.aws.amazon.com/cognito/latest/developerguide/role-based-access-control.html).

Using a [token-based approach](https://docs.aws.amazon.com/cognito/latest/developerguide/role-based-access-control.html#using-tokens-to-assign-roles-to-users) to role mapping will allow mapped roles to be passed through the `cognito:roles` or\
`cognito:preferred_role` claims from the identity provider:

```python
# Example automatically generated from non-compiling source. May contain errors.
cognito.IdentityPool(self, "myidentitypool",
    identity_pool_name="myidentitypool",
    role_mappings=[{
        "provider_url": IdentityPoolProviderUrl.AMAZON,
        "use_token": True
    }]
)
```

Using a rule-based approach to role mapping allows roles to be assigned based on custom claims passed from the identity  provider:

```python
# Example automatically generated from non-compiling source. May contain errors.
cognito.IdentityPool(self, "myidentitypool",
    identity_pool_name="myidentitypool",
    # Assign specific roles to users based on whether or not the custom admin claim is passed from the identity provider
    role_mappings=[{
        "provider_url": IdentityPoolProviderUrl.AMAZON,
        "rules": [{
            "claim": "custom:admin",
            "claim_value": "admin",
            "mapped_role": admin_role
        }, {
            "claim": "custom:admin",
            "claim_value": "admin",
            "match_type": RoleMappingMatchType.NOTEQUAL,
            "mapped_role": non_admin_role
        }
        ]
    }]
)
```

Role mappings can also be added after instantiation with the Identity Pool's `addRoleMappings` method:

```python
# Example automatically generated from non-compiling source. May contain errors.
identity_pool.add_role_mappings(my_added_role_mapping1, my_added_role_mapping2, my_added_role_mapping3)
```

#### Provider Urls

Role mappings must be associated with the url of an Identity Provider which can be supplied
`IdentityPoolProviderUrl`. Supported Providers have static Urls that can be used:

```python
# Example automatically generated from non-compiling source. May contain errors.
cognito.IdentityPool(self, "myidentitypool",
    identity_pool_name="myidentitypool",
    role_mappings=[{
        "provider_url": IdentityPoolProviderUrl.FACEBOOK,
        "use_token": True
    }]
)
```

For identity providers that don't have static Urls, a custom Url or User Pool Client Url can be supplied:

```python
# Example automatically generated from non-compiling source. May contain errors.
cognito.IdentityPool(self, "myidentitypool",
    identity_pool_name="myidentitypool",
    role_mappings=[{
        "provider_url": IdentityPoolProviderUrl.user_pool("cognito-idp.my-idp-region.amazonaws.com/my-idp-region_abcdefghi:app_client_id"),
        "use_token": True
    }, {
        "provider_url": IdentityPoolProviderUrl.custom("my-custom-provider.com"),
        "use_token": True
    }
    ]
)
```

See [here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypoolroleattachment-rolemapping.html#cfn-cognito-identitypoolroleattachment-rolemapping-identityprovider) for more information.

### Authentication Flow

Identity Pool [Authentication Flow](https://docs.aws.amazon.com/cognito/latest/developerguide/authentication-flow.html) defaults to the enhanced, simplified flow. The Classic (basic) Authentication Flow\
can also be implemented using `allowClassicFlow`:

```python
# Example automatically generated from non-compiling source. May contain errors.
cognito.IdentityPool(self, "myidentitypool",
    identity_pool_name="myidentitypool",
    allow_classic_flow=True
)
```

### Cognito Sync

It's now recommended to integrate [AWS AppSync](https://aws.amazon.com/appsync/) for synchronizing app data across devices, so\
Cognito Sync features like `PushSync`, `CognitoEvents`, and `CognitoStreams` are not a part of `IdentityPool`. More\
information can be found [here](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-sync.html).

### Importing Identity Pools

You can import existing identity pools into your stack using Identity Pool static methods with the Identity Pool Id or\
Arn:

```python
# Example automatically generated from non-compiling source. May contain errors.
IdentityPool.from_identity_pool_id(self, "my-imported-identity-pool", "us-east-1:dj2823ryiwuhef937")
IdentityPool.from_identity_pool_arn(self, "my-imported-identity-pool", "arn:aws:cognito-identity:us-east-1:123456789012:identitypool/us-east-1:dj2823ryiwuhef937")
```
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs
from .. import IResource as _IResource_8c1dbbbd, Resource as _Resource_abff4495
from ..aws_cognito import (
    IUserPool as _IUserPool_5e500460, IUserPoolClient as _IUserPoolClient_4cdf19bd
)
from ..aws_iam import (
    IOpenIdConnectProvider as _IOpenIdConnectProvider_bb431740,
    IRole as _IRole_59af6f50,
    ISamlProvider as _ISamlProvider_b494dc4e,
)


@jsii.interface(jsii_type="monocdk.aws_cognito_identitypool.IIdentityPool")
class IIdentityPool(_IResource_8c1dbbbd, typing_extensions.Protocol):
    '''(experimental) Represents a Cognito IdentityPool.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolArn")
    def identity_pool_arn(self) -> builtins.str:
        '''(experimental) The ARN of the Identity Pool.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        '''(experimental) The id of the Identity Pool in the format REGION:GUID.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolName")
    def identity_pool_name(self) -> builtins.str:
        '''(experimental) Name of the Identity Pool.

        :stability: experimental
        :attribute: true
        '''
        ...


class _IIdentityPoolProxy(
    jsii.proxy_for(_IResource_8c1dbbbd) # type: ignore[misc]
):
    '''(experimental) Represents a Cognito IdentityPool.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_cognito_identitypool.IIdentityPool"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolArn")
    def identity_pool_arn(self) -> builtins.str:
        '''(experimental) The ARN of the Identity Pool.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "identityPoolArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        '''(experimental) The id of the Identity Pool in the format REGION:GUID.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "identityPoolId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolName")
    def identity_pool_name(self) -> builtins.str:
        '''(experimental) Name of the Identity Pool.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "identityPoolName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIdentityPool).__jsii_proxy_class__ = lambda : _IIdentityPoolProxy


@jsii.interface(
    jsii_type="monocdk.aws_cognito_identitypool.IIdentityPoolRoleAttachment"
)
class IIdentityPoolRoleAttachment(_IResource_8c1dbbbd, typing_extensions.Protocol):
    '''(experimental) Represents an Identity Pool Role Attachment.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        '''(experimental) Id of the Attachments Underlying Identity Pool.

        :stability: experimental
        '''
        ...


class _IIdentityPoolRoleAttachmentProxy(
    jsii.proxy_for(_IResource_8c1dbbbd) # type: ignore[misc]
):
    '''(experimental) Represents an Identity Pool Role Attachment.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_cognito_identitypool.IIdentityPoolRoleAttachment"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        '''(experimental) Id of the Attachments Underlying Identity Pool.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "identityPoolId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIdentityPoolRoleAttachment).__jsii_proxy_class__ = lambda : _IIdentityPoolRoleAttachmentProxy


@jsii.interface(
    jsii_type="monocdk.aws_cognito_identitypool.IUserPoolAuthenticationProvider"
)
class IUserPoolAuthenticationProvider(typing_extensions.Protocol):
    '''(experimental) Represents the concept of a User Pool Authentication Provider.

    You use user pool authentication providers to configure User Pools
    and User Pool Clients for use with Identity Pools

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        identity_pool: IIdentityPool,
    ) -> "UserPoolAuthenticationProviderBindConfig":
        '''(experimental) The method called when a given User Pool Authentication Provider is added (for the first time) to an Identity Pool.

        :param scope: -
        :param identity_pool: -

        :stability: experimental
        '''
        ...


class _IUserPoolAuthenticationProviderProxy:
    '''(experimental) Represents the concept of a User Pool Authentication Provider.

    You use user pool authentication providers to configure User Pools
    and User Pool Clients for use with Identity Pools

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "monocdk.aws_cognito_identitypool.IUserPoolAuthenticationProvider"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        identity_pool: IIdentityPool,
    ) -> "UserPoolAuthenticationProviderBindConfig":
        '''(experimental) The method called when a given User Pool Authentication Provider is added (for the first time) to an Identity Pool.

        :param scope: -
        :param identity_pool: -

        :stability: experimental
        '''
        options = UserPoolAuthenticationProviderBindOptions()

        return typing.cast("UserPoolAuthenticationProviderBindConfig", jsii.invoke(self, "bind", [scope, identity_pool, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IUserPoolAuthenticationProvider).__jsii_proxy_class__ = lambda : _IUserPoolAuthenticationProviderProxy


@jsii.implements(IIdentityPool)
class IdentityPool(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPool",
):
    '''(experimental) Define a Cognito Identity Pool.

    :stability: experimental
    :resource: AWS::Cognito::IdentityPool
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_cognito_identitypool as cognito_identitypool
        from monocdk import aws_iam as iam
        
        # identity_pool_provider_url: cognito_identitypool.IdentityPoolProviderUrl
        # open_id_connect_provider: iam.OpenIdConnectProvider
        # role: iam.Role
        # saml_provider: iam.SamlProvider
        # user_pool_authentication_provider: cognito_identitypool.UserPoolAuthenticationProvider
        
        identity_pool = cognito_identitypool.IdentityPool(self, "MyIdentityPool",
            allow_classic_flow=False,
            allow_unauthenticated_identities=False,
            authenticated_role=role,
            authentication_providers=cognito_identitypool.IdentityPoolAuthenticationProviders(
                amazon=cognito_identitypool.IdentityPoolAmazonLoginProvider(
                    app_id="appId"
                ),
                apple=cognito_identitypool.IdentityPoolAppleLoginProvider(
                    services_id="servicesId"
                ),
                custom_provider="customProvider",
                digits=cognito_identitypool.IdentityPoolDigitsLoginProvider(
                    consumer_key="consumerKey",
                    consumer_secret="consumerSecret"
                ),
                facebook=cognito_identitypool.IdentityPoolFacebookLoginProvider(
                    app_id="appId"
                ),
                google=cognito_identitypool.IdentityPoolGoogleLoginProvider(
                    client_id="clientId"
                ),
                open_id_connect_providers=[open_id_connect_provider],
                saml_providers=[saml_provider],
                twitter=cognito_identitypool.IdentityPoolTwitterLoginProvider(
                    consumer_key="consumerKey",
                    consumer_secret="consumerSecret"
                ),
                user_pools=[user_pool_authentication_provider]
            ),
            identity_pool_name="identityPoolName",
            role_mappings=[cognito_identitypool.IdentityPoolRoleMapping(
                provider_url=identity_pool_provider_url,
        
                # the properties below are optional
                resolve_ambiguous_roles=False,
                rules=[cognito_identitypool.RoleMappingRule(
                    claim="claim",
                    claim_value="claimValue",
                    mapped_role=role,
        
                    # the properties below are optional
                    match_type=cognito_identitypool.RoleMappingMatchType.EQUALS
                )],
                use_token=False
            )],
            unauthenticated_role=role
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allow_classic_flow: typing.Optional[builtins.bool] = None,
        allow_unauthenticated_identities: typing.Optional[builtins.bool] = None,
        authenticated_role: typing.Optional[_IRole_59af6f50] = None,
        authentication_providers: typing.Optional["IdentityPoolAuthenticationProviders"] = None,
        identity_pool_name: typing.Optional[builtins.str] = None,
        role_mappings: typing.Optional[typing.Sequence["IdentityPoolRoleMapping"]] = None,
        unauthenticated_role: typing.Optional[_IRole_59af6f50] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param allow_classic_flow: (experimental) Enables the Basic (Classic) authentication flow. Default: - Classic Flow not allowed
        :param allow_unauthenticated_identities: (experimental) Wwhether the identity pool supports unauthenticated logins. Default: - false
        :param authenticated_role: (experimental) The Default Role to be assumed by Authenticated Users. Default: - A Default Authenticated Role will be added
        :param authentication_providers: (experimental) Authentication providers for using in identity pool. Default: - No Authentication Providers passed directly to Identity Pool
        :param identity_pool_name: (experimental) The name of the Identity Pool. Default: - automatically generated name by CloudFormation at deploy time
        :param role_mappings: (experimental) Rules for mapping roles to users. Default: - no Role Mappings
        :param unauthenticated_role: (experimental) The Default Role to be assumed by Unauthenticated Users. Default: - A Default Unauthenticated Role will be added

        :stability: experimental
        '''
        props = IdentityPoolProps(
            allow_classic_flow=allow_classic_flow,
            allow_unauthenticated_identities=allow_unauthenticated_identities,
            authenticated_role=authenticated_role,
            authentication_providers=authentication_providers,
            identity_pool_name=identity_pool_name,
            role_mappings=role_mappings,
            unauthenticated_role=unauthenticated_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromIdentityPoolArn") # type: ignore[misc]
    @builtins.classmethod
    def from_identity_pool_arn(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        identity_pool_arn: builtins.str,
    ) -> IIdentityPool:
        '''(experimental) Import an existing Identity Pool from its Arn.

        :param scope: -
        :param id: -
        :param identity_pool_arn: -

        :stability: experimental
        '''
        return typing.cast(IIdentityPool, jsii.sinvoke(cls, "fromIdentityPoolArn", [scope, id, identity_pool_arn]))

    @jsii.member(jsii_name="fromIdentityPoolId") # type: ignore[misc]
    @builtins.classmethod
    def from_identity_pool_id(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        identity_pool_id: builtins.str,
    ) -> IIdentityPool:
        '''(experimental) Import an existing Identity Pool from its id.

        :param scope: -
        :param id: -
        :param identity_pool_id: -

        :stability: experimental
        '''
        return typing.cast(IIdentityPool, jsii.sinvoke(cls, "fromIdentityPoolId", [scope, id, identity_pool_id]))

    @jsii.member(jsii_name="addRoleMappings")
    def add_role_mappings(self, *role_mappings: "IdentityPoolRoleMapping") -> None:
        '''(experimental) Adds Role Mappings to Identity Pool.

        :param role_mappings: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addRoleMappings", [*role_mappings]))

    @jsii.member(jsii_name="addUserPoolAuthentication")
    def add_user_pool_authentication(
        self,
        user_pool: IUserPoolAuthenticationProvider,
    ) -> None:
        '''(experimental) Add a User Pool to the IdentityPool and configure User Pool Client to handle identities.

        :param user_pool: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addUserPoolAuthentication", [user_pool]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authenticatedRole")
    def authenticated_role(self) -> _IRole_59af6f50:
        '''(experimental) Default role for authenticated users.

        :stability: experimental
        '''
        return typing.cast(_IRole_59af6f50, jsii.get(self, "authenticatedRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolArn")
    def identity_pool_arn(self) -> builtins.str:
        '''(experimental) The ARN of the Identity Pool.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "identityPoolArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        '''(experimental) The id of the Identity Pool in the format REGION:GUID.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "identityPoolId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolName")
    def identity_pool_name(self) -> builtins.str:
        '''(experimental) The name of the Identity Pool.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "identityPoolName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unauthenticatedRole")
    def unauthenticated_role(self) -> _IRole_59af6f50:
        '''(experimental) Default role for unauthenticated users.

        :stability: experimental
        '''
        return typing.cast(_IRole_59af6f50, jsii.get(self, "unauthenticatedRole"))


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolAmazonLoginProvider",
    jsii_struct_bases=[],
    name_mapping={"app_id": "appId"},
)
class IdentityPoolAmazonLoginProvider:
    def __init__(self, *, app_id: builtins.str) -> None:
        '''(experimental) Login Provider for Identity Federation using Amazon Credentials.

        :param app_id: (experimental) App Id for Amazon Identity Federation.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            identity_pool_amazon_login_provider = cognito_identitypool.IdentityPoolAmazonLoginProvider(
                app_id="appId"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_id": app_id,
        }

    @builtins.property
    def app_id(self) -> builtins.str:
        '''(experimental) App Id for Amazon Identity Federation.

        :stability: experimental
        '''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolAmazonLoginProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolAppleLoginProvider",
    jsii_struct_bases=[],
    name_mapping={"services_id": "servicesId"},
)
class IdentityPoolAppleLoginProvider:
    def __init__(self, *, services_id: builtins.str) -> None:
        '''(experimental) Login Provider for Identity Federation using Apple Credentials.

        :param services_id: (experimental) App Id for Apple Identity Federation.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            identity_pool_apple_login_provider = cognito_identitypool.IdentityPoolAppleLoginProvider(
                services_id="servicesId"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "services_id": services_id,
        }

    @builtins.property
    def services_id(self) -> builtins.str:
        '''(experimental) App Id for Apple Identity Federation.

        :stability: experimental
        '''
        result = self._values.get("services_id")
        assert result is not None, "Required property 'services_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolAppleLoginProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolFacebookLoginProvider",
    jsii_struct_bases=[],
    name_mapping={"app_id": "appId"},
)
class IdentityPoolFacebookLoginProvider:
    def __init__(self, *, app_id: builtins.str) -> None:
        '''(experimental) Login Provider for Identity Federation using Facebook Credentials.

        :param app_id: (experimental) App Id for Facebook Identity Federation.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            identity_pool_facebook_login_provider = cognito_identitypool.IdentityPoolFacebookLoginProvider(
                app_id="appId"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_id": app_id,
        }

    @builtins.property
    def app_id(self) -> builtins.str:
        '''(experimental) App Id for Facebook Identity Federation.

        :stability: experimental
        '''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolFacebookLoginProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolGoogleLoginProvider",
    jsii_struct_bases=[],
    name_mapping={"client_id": "clientId"},
)
class IdentityPoolGoogleLoginProvider:
    def __init__(self, *, client_id: builtins.str) -> None:
        '''(experimental) Login Provider for Identity Federation using Google Credentials.

        :param client_id: (experimental) App Id for Google Identity Federation.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            identity_pool_google_login_provider = cognito_identitypool.IdentityPoolGoogleLoginProvider(
                client_id="clientId"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "client_id": client_id,
        }

    @builtins.property
    def client_id(self) -> builtins.str:
        '''(experimental) App Id for Google Identity Federation.

        :stability: experimental
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolGoogleLoginProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolProps",
    jsii_struct_bases=[],
    name_mapping={
        "allow_classic_flow": "allowClassicFlow",
        "allow_unauthenticated_identities": "allowUnauthenticatedIdentities",
        "authenticated_role": "authenticatedRole",
        "authentication_providers": "authenticationProviders",
        "identity_pool_name": "identityPoolName",
        "role_mappings": "roleMappings",
        "unauthenticated_role": "unauthenticatedRole",
    },
)
class IdentityPoolProps:
    def __init__(
        self,
        *,
        allow_classic_flow: typing.Optional[builtins.bool] = None,
        allow_unauthenticated_identities: typing.Optional[builtins.bool] = None,
        authenticated_role: typing.Optional[_IRole_59af6f50] = None,
        authentication_providers: typing.Optional["IdentityPoolAuthenticationProviders"] = None,
        identity_pool_name: typing.Optional[builtins.str] = None,
        role_mappings: typing.Optional[typing.Sequence["IdentityPoolRoleMapping"]] = None,
        unauthenticated_role: typing.Optional[_IRole_59af6f50] = None,
    ) -> None:
        '''(experimental) Props for the IdentityPool construct.

        :param allow_classic_flow: (experimental) Enables the Basic (Classic) authentication flow. Default: - Classic Flow not allowed
        :param allow_unauthenticated_identities: (experimental) Wwhether the identity pool supports unauthenticated logins. Default: - false
        :param authenticated_role: (experimental) The Default Role to be assumed by Authenticated Users. Default: - A Default Authenticated Role will be added
        :param authentication_providers: (experimental) Authentication providers for using in identity pool. Default: - No Authentication Providers passed directly to Identity Pool
        :param identity_pool_name: (experimental) The name of the Identity Pool. Default: - automatically generated name by CloudFormation at deploy time
        :param role_mappings: (experimental) Rules for mapping roles to users. Default: - no Role Mappings
        :param unauthenticated_role: (experimental) The Default Role to be assumed by Unauthenticated Users. Default: - A Default Unauthenticated Role will be added

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            from monocdk import aws_iam as iam
            
            # identity_pool_provider_url: cognito_identitypool.IdentityPoolProviderUrl
            # open_id_connect_provider: iam.OpenIdConnectProvider
            # role: iam.Role
            # saml_provider: iam.SamlProvider
            # user_pool_authentication_provider: cognito_identitypool.UserPoolAuthenticationProvider
            
            identity_pool_props = cognito_identitypool.IdentityPoolProps(
                allow_classic_flow=False,
                allow_unauthenticated_identities=False,
                authenticated_role=role,
                authentication_providers=cognito_identitypool.IdentityPoolAuthenticationProviders(
                    amazon=cognito_identitypool.IdentityPoolAmazonLoginProvider(
                        app_id="appId"
                    ),
                    apple=cognito_identitypool.IdentityPoolAppleLoginProvider(
                        services_id="servicesId"
                    ),
                    custom_provider="customProvider",
                    digits=cognito_identitypool.IdentityPoolDigitsLoginProvider(
                        consumer_key="consumerKey",
                        consumer_secret="consumerSecret"
                    ),
                    facebook=cognito_identitypool.IdentityPoolFacebookLoginProvider(
                        app_id="appId"
                    ),
                    google=cognito_identitypool.IdentityPoolGoogleLoginProvider(
                        client_id="clientId"
                    ),
                    open_id_connect_providers=[open_id_connect_provider],
                    saml_providers=[saml_provider],
                    twitter=cognito_identitypool.IdentityPoolTwitterLoginProvider(
                        consumer_key="consumerKey",
                        consumer_secret="consumerSecret"
                    ),
                    user_pools=[user_pool_authentication_provider]
                ),
                identity_pool_name="identityPoolName",
                role_mappings=[cognito_identitypool.IdentityPoolRoleMapping(
                    provider_url=identity_pool_provider_url,
            
                    # the properties below are optional
                    resolve_ambiguous_roles=False,
                    rules=[cognito_identitypool.RoleMappingRule(
                        claim="claim",
                        claim_value="claimValue",
                        mapped_role=role,
            
                        # the properties below are optional
                        match_type=cognito_identitypool.RoleMappingMatchType.EQUALS
                    )],
                    use_token=False
                )],
                unauthenticated_role=role
            )
        '''
        if isinstance(authentication_providers, dict):
            authentication_providers = IdentityPoolAuthenticationProviders(**authentication_providers)
        self._values: typing.Dict[str, typing.Any] = {}
        if allow_classic_flow is not None:
            self._values["allow_classic_flow"] = allow_classic_flow
        if allow_unauthenticated_identities is not None:
            self._values["allow_unauthenticated_identities"] = allow_unauthenticated_identities
        if authenticated_role is not None:
            self._values["authenticated_role"] = authenticated_role
        if authentication_providers is not None:
            self._values["authentication_providers"] = authentication_providers
        if identity_pool_name is not None:
            self._values["identity_pool_name"] = identity_pool_name
        if role_mappings is not None:
            self._values["role_mappings"] = role_mappings
        if unauthenticated_role is not None:
            self._values["unauthenticated_role"] = unauthenticated_role

    @builtins.property
    def allow_classic_flow(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enables the Basic (Classic) authentication flow.

        :default: - Classic Flow not allowed

        :stability: experimental
        '''
        result = self._values.get("allow_classic_flow")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_unauthenticated_identities(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Wwhether the identity pool supports unauthenticated logins.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("allow_unauthenticated_identities")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def authenticated_role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Default Role to be assumed by Authenticated Users.

        :default: - A Default Authenticated Role will be added

        :stability: experimental
        '''
        result = self._values.get("authenticated_role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def authentication_providers(
        self,
    ) -> typing.Optional["IdentityPoolAuthenticationProviders"]:
        '''(experimental) Authentication providers for using in identity pool.

        :default: - No Authentication Providers passed directly to Identity Pool

        :stability: experimental
        '''
        result = self._values.get("authentication_providers")
        return typing.cast(typing.Optional["IdentityPoolAuthenticationProviders"], result)

    @builtins.property
    def identity_pool_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Identity Pool.

        :default: - automatically generated name by CloudFormation at deploy time

        :stability: experimental
        '''
        result = self._values.get("identity_pool_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_mappings(self) -> typing.Optional[typing.List["IdentityPoolRoleMapping"]]:
        '''(experimental) Rules for mapping roles to users.

        :default: - no Role Mappings

        :stability: experimental
        '''
        result = self._values.get("role_mappings")
        return typing.cast(typing.Optional[typing.List["IdentityPoolRoleMapping"]], result)

    @builtins.property
    def unauthenticated_role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) The Default Role to be assumed by Unauthenticated Users.

        :default: - A Default Unauthenticated Role will be added

        :stability: experimental
        '''
        result = self._values.get("unauthenticated_role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolProviderType")
class IdentityPoolProviderType(enum.Enum):
    '''(experimental) Types of Identity Pool Login Providers.

    :stability: experimental
    '''

    FACEBOOK = "FACEBOOK"
    '''(experimental) Facebook Provider type.

    :stability: experimental
    '''
    GOOGLE = "GOOGLE"
    '''(experimental) Google Provider Type.

    :stability: experimental
    '''
    AMAZON = "AMAZON"
    '''(experimental) Amazon Provider Type.

    :stability: experimental
    '''
    APPLE = "APPLE"
    '''(experimental) Apple Provider Type.

    :stability: experimental
    '''
    TWITTER = "TWITTER"
    '''(experimental) Twitter Provider Type.

    :stability: experimental
    '''
    DIGITS = "DIGITS"
    '''(experimental) Digits Provider Type.

    :stability: experimental
    '''
    OPEN_ID = "OPEN_ID"
    '''(experimental) Open Id Provider Type.

    :stability: experimental
    '''
    SAML = "SAML"
    '''(experimental) Saml Provider Type.

    :stability: experimental
    '''
    USER_POOL = "USER_POOL"
    '''(experimental) User Pool Provider Type.

    :stability: experimental
    '''
    CUSTOM = "CUSTOM"
    '''(experimental) Custom Provider Type.

    :stability: experimental
    '''


class IdentityPoolProviderUrl(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolProviderUrl",
):
    '''(experimental) Keys for Login Providers - correspond to client id's of respective federation identity providers.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_cognito_identitypool as cognito_identitypool
        
        identity_pool_provider_url = cognito_identitypool.IdentityPoolProviderUrl.custom("url")
    '''

    def __init__(self, type: IdentityPoolProviderType, value: builtins.str) -> None:
        '''
        :param type: type of Provider Url.
        :param value: value of Provider Url.

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [type, value])

    @jsii.member(jsii_name="custom") # type: ignore[misc]
    @builtins.classmethod
    def custom(cls, url: builtins.str) -> "IdentityPoolProviderUrl":
        '''(experimental) Custom Provider Url.

        :param url: -

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sinvoke(cls, "custom", [url]))

    @jsii.member(jsii_name="openId") # type: ignore[misc]
    @builtins.classmethod
    def open_id(cls, url: builtins.str) -> "IdentityPoolProviderUrl":
        '''(experimental) OpenId Provider Url.

        :param url: -

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sinvoke(cls, "openId", [url]))

    @jsii.member(jsii_name="saml") # type: ignore[misc]
    @builtins.classmethod
    def saml(cls, url: builtins.str) -> "IdentityPoolProviderUrl":
        '''(experimental) Saml Provider Url.

        :param url: -

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sinvoke(cls, "saml", [url]))

    @jsii.member(jsii_name="userPool") # type: ignore[misc]
    @builtins.classmethod
    def user_pool(cls, url: builtins.str) -> "IdentityPoolProviderUrl":
        '''(experimental) User Pool Provider Url.

        :param url: -

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sinvoke(cls, "userPool", [url]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="AMAZON")
    def AMAZON(cls) -> "IdentityPoolProviderUrl":
        '''(experimental) Amazon Provider Url.

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sget(cls, "AMAZON"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="APPLE")
    def APPLE(cls) -> "IdentityPoolProviderUrl":
        '''(experimental) Apple Provider Url.

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sget(cls, "APPLE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DIGITS")
    def DIGITS(cls) -> "IdentityPoolProviderUrl":
        '''(experimental) Digits Provider Url.

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sget(cls, "DIGITS"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="FACEBOOK")
    def FACEBOOK(cls) -> "IdentityPoolProviderUrl":
        '''(experimental) Facebook Provider Url.

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sget(cls, "FACEBOOK"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="GOOGLE")
    def GOOGLE(cls) -> "IdentityPoolProviderUrl":
        '''(experimental) Google Provider Url.

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sget(cls, "GOOGLE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="TWITTER")
    def TWITTER(cls) -> "IdentityPoolProviderUrl":
        '''(experimental) Twitter Provider Url.

        :stability: experimental
        '''
        return typing.cast("IdentityPoolProviderUrl", jsii.sget(cls, "TWITTER"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> IdentityPoolProviderType:
        '''(experimental) type of Provider Url.

        :stability: experimental
        '''
        return typing.cast(IdentityPoolProviderType, jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        '''(experimental) value of Provider Url.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "value"))


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolProviders",
    jsii_struct_bases=[],
    name_mapping={
        "amazon": "amazon",
        "apple": "apple",
        "digits": "digits",
        "facebook": "facebook",
        "google": "google",
        "twitter": "twitter",
    },
)
class IdentityPoolProviders:
    def __init__(
        self,
        *,
        amazon: typing.Optional[IdentityPoolAmazonLoginProvider] = None,
        apple: typing.Optional[IdentityPoolAppleLoginProvider] = None,
        digits: typing.Optional["IdentityPoolDigitsLoginProvider"] = None,
        facebook: typing.Optional[IdentityPoolFacebookLoginProvider] = None,
        google: typing.Optional[IdentityPoolGoogleLoginProvider] = None,
        twitter: typing.Optional["IdentityPoolTwitterLoginProvider"] = None,
    ) -> None:
        '''(experimental) External Identity Providers To Connect to User Pools and Identity Pools.

        :param amazon: (experimental) App Id for Amazon Identity Federation. Default: - No Amazon Authentication Provider used without OpenIdConnect or a User Pool
        :param apple: (experimental) Services Id for Apple Identity Federation. Default: - No Apple Authentication Provider used without OpenIdConnect or a User Pool
        :param digits: (experimental) Consumer Key and Secret for Digits Identity Federation. Default: - No Digits Authentication Provider used without OpenIdConnect or a User Pool
        :param facebook: (experimental) App Id for Facebook Identity Federation. Default: - No Facebook Authentication Provider used without OpenIdConnect or a User Pool
        :param google: (experimental) Client Id for Google Identity Federation. Default: - No Google Authentication Provider used without OpenIdConnect or a User Pool
        :param twitter: (experimental) Consumer Key and Secret for Twitter Identity Federation. Default: - No Twitter Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            identity_pool_providers = cognito_identitypool.IdentityPoolProviders(
                amazon=cognito_identitypool.IdentityPoolAmazonLoginProvider(
                    app_id="appId"
                ),
                apple=cognito_identitypool.IdentityPoolAppleLoginProvider(
                    services_id="servicesId"
                ),
                digits=cognito_identitypool.IdentityPoolDigitsLoginProvider(
                    consumer_key="consumerKey",
                    consumer_secret="consumerSecret"
                ),
                facebook=cognito_identitypool.IdentityPoolFacebookLoginProvider(
                    app_id="appId"
                ),
                google=cognito_identitypool.IdentityPoolGoogleLoginProvider(
                    client_id="clientId"
                ),
                twitter=cognito_identitypool.IdentityPoolTwitterLoginProvider(
                    consumer_key="consumerKey",
                    consumer_secret="consumerSecret"
                )
            )
        '''
        if isinstance(amazon, dict):
            amazon = IdentityPoolAmazonLoginProvider(**amazon)
        if isinstance(apple, dict):
            apple = IdentityPoolAppleLoginProvider(**apple)
        if isinstance(digits, dict):
            digits = IdentityPoolDigitsLoginProvider(**digits)
        if isinstance(facebook, dict):
            facebook = IdentityPoolFacebookLoginProvider(**facebook)
        if isinstance(google, dict):
            google = IdentityPoolGoogleLoginProvider(**google)
        if isinstance(twitter, dict):
            twitter = IdentityPoolTwitterLoginProvider(**twitter)
        self._values: typing.Dict[str, typing.Any] = {}
        if amazon is not None:
            self._values["amazon"] = amazon
        if apple is not None:
            self._values["apple"] = apple
        if digits is not None:
            self._values["digits"] = digits
        if facebook is not None:
            self._values["facebook"] = facebook
        if google is not None:
            self._values["google"] = google
        if twitter is not None:
            self._values["twitter"] = twitter

    @builtins.property
    def amazon(self) -> typing.Optional[IdentityPoolAmazonLoginProvider]:
        '''(experimental) App Id for Amazon Identity Federation.

        :default: - No Amazon Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("amazon")
        return typing.cast(typing.Optional[IdentityPoolAmazonLoginProvider], result)

    @builtins.property
    def apple(self) -> typing.Optional[IdentityPoolAppleLoginProvider]:
        '''(experimental) Services Id for Apple Identity Federation.

        :default: - No Apple Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("apple")
        return typing.cast(typing.Optional[IdentityPoolAppleLoginProvider], result)

    @builtins.property
    def digits(self) -> typing.Optional["IdentityPoolDigitsLoginProvider"]:
        '''(experimental) Consumer Key and Secret for Digits Identity Federation.

        :default: - No Digits Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("digits")
        return typing.cast(typing.Optional["IdentityPoolDigitsLoginProvider"], result)

    @builtins.property
    def facebook(self) -> typing.Optional[IdentityPoolFacebookLoginProvider]:
        '''(experimental) App Id for Facebook Identity Federation.

        :default: - No Facebook Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("facebook")
        return typing.cast(typing.Optional[IdentityPoolFacebookLoginProvider], result)

    @builtins.property
    def google(self) -> typing.Optional[IdentityPoolGoogleLoginProvider]:
        '''(experimental) Client Id for Google Identity Federation.

        :default: - No Google Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("google")
        return typing.cast(typing.Optional[IdentityPoolGoogleLoginProvider], result)

    @builtins.property
    def twitter(self) -> typing.Optional["IdentityPoolTwitterLoginProvider"]:
        '''(experimental) Consumer Key and Secret for Twitter Identity Federation.

        :default: - No Twitter Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("twitter")
        return typing.cast(typing.Optional["IdentityPoolTwitterLoginProvider"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolProviders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IIdentityPoolRoleAttachment)
class IdentityPoolRoleAttachment(
    _Resource_abff4495,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolRoleAttachment",
):
    '''(experimental) Defines an Identity Pool Role Attachment.

    :stability: experimental
    :resource: AWS::Cognito::IdentityPoolRoleAttachment
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_cognito_identitypool as cognito_identitypool
        from monocdk import aws_iam as iam
        
        # identity_pool: cognito_identitypool.IdentityPool
        # identity_pool_provider_url: cognito_identitypool.IdentityPoolProviderUrl
        # role: iam.Role
        
        identity_pool_role_attachment = cognito_identitypool.IdentityPoolRoleAttachment(self, "MyIdentityPoolRoleAttachment",
            identity_pool=identity_pool,
        
            # the properties below are optional
            authenticated_role=role,
            role_mappings=[cognito_identitypool.IdentityPoolRoleMapping(
                provider_url=identity_pool_provider_url,
        
                # the properties below are optional
                resolve_ambiguous_roles=False,
                rules=[cognito_identitypool.RoleMappingRule(
                    claim="claim",
                    claim_value="claimValue",
                    mapped_role=role,
        
                    # the properties below are optional
                    match_type=cognito_identitypool.RoleMappingMatchType.EQUALS
                )],
                use_token=False
            )],
            unauthenticated_role=role
        )
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identity_pool: IIdentityPool,
        authenticated_role: typing.Optional[_IRole_59af6f50] = None,
        role_mappings: typing.Optional[typing.Sequence["IdentityPoolRoleMapping"]] = None,
        unauthenticated_role: typing.Optional[_IRole_59af6f50] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param identity_pool: (experimental) Id of the Attachments Underlying Identity Pool.
        :param authenticated_role: (experimental) Default Authenticated (User) Role. Default: - No default authenticated role will be added
        :param role_mappings: (experimental) Rules for mapping roles to users. Default: - no Role Mappings
        :param unauthenticated_role: (experimental) Default Unauthenticated (Guest) Role. Default: - No default unauthenticated role will be added

        :stability: experimental
        '''
        props = IdentityPoolRoleAttachmentProps(
            identity_pool=identity_pool,
            authenticated_role=authenticated_role,
            role_mappings=role_mappings,
            unauthenticated_role=unauthenticated_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="identityPoolId")
    def identity_pool_id(self) -> builtins.str:
        '''(experimental) Id of the underlying identity pool.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "identityPoolId"))


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolRoleAttachmentProps",
    jsii_struct_bases=[],
    name_mapping={
        "identity_pool": "identityPool",
        "authenticated_role": "authenticatedRole",
        "role_mappings": "roleMappings",
        "unauthenticated_role": "unauthenticatedRole",
    },
)
class IdentityPoolRoleAttachmentProps:
    def __init__(
        self,
        *,
        identity_pool: IIdentityPool,
        authenticated_role: typing.Optional[_IRole_59af6f50] = None,
        role_mappings: typing.Optional[typing.Sequence["IdentityPoolRoleMapping"]] = None,
        unauthenticated_role: typing.Optional[_IRole_59af6f50] = None,
    ) -> None:
        '''(experimental) Props for an Identity Pool Role Attachment.

        :param identity_pool: (experimental) Id of the Attachments Underlying Identity Pool.
        :param authenticated_role: (experimental) Default Authenticated (User) Role. Default: - No default authenticated role will be added
        :param role_mappings: (experimental) Rules for mapping roles to users. Default: - no Role Mappings
        :param unauthenticated_role: (experimental) Default Unauthenticated (Guest) Role. Default: - No default unauthenticated role will be added

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            from monocdk import aws_iam as iam
            
            # identity_pool: cognito_identitypool.IdentityPool
            # identity_pool_provider_url: cognito_identitypool.IdentityPoolProviderUrl
            # role: iam.Role
            
            identity_pool_role_attachment_props = cognito_identitypool.IdentityPoolRoleAttachmentProps(
                identity_pool=identity_pool,
            
                # the properties below are optional
                authenticated_role=role,
                role_mappings=[cognito_identitypool.IdentityPoolRoleMapping(
                    provider_url=identity_pool_provider_url,
            
                    # the properties below are optional
                    resolve_ambiguous_roles=False,
                    rules=[cognito_identitypool.RoleMappingRule(
                        claim="claim",
                        claim_value="claimValue",
                        mapped_role=role,
            
                        # the properties below are optional
                        match_type=cognito_identitypool.RoleMappingMatchType.EQUALS
                    )],
                    use_token=False
                )],
                unauthenticated_role=role
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "identity_pool": identity_pool,
        }
        if authenticated_role is not None:
            self._values["authenticated_role"] = authenticated_role
        if role_mappings is not None:
            self._values["role_mappings"] = role_mappings
        if unauthenticated_role is not None:
            self._values["unauthenticated_role"] = unauthenticated_role

    @builtins.property
    def identity_pool(self) -> IIdentityPool:
        '''(experimental) Id of the Attachments Underlying Identity Pool.

        :stability: experimental
        '''
        result = self._values.get("identity_pool")
        assert result is not None, "Required property 'identity_pool' is missing"
        return typing.cast(IIdentityPool, result)

    @builtins.property
    def authenticated_role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) Default Authenticated (User) Role.

        :default: - No default authenticated role will be added

        :stability: experimental
        '''
        result = self._values.get("authenticated_role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    @builtins.property
    def role_mappings(self) -> typing.Optional[typing.List["IdentityPoolRoleMapping"]]:
        '''(experimental) Rules for mapping roles to users.

        :default: - no Role Mappings

        :stability: experimental
        '''
        result = self._values.get("role_mappings")
        return typing.cast(typing.Optional[typing.List["IdentityPoolRoleMapping"]], result)

    @builtins.property
    def unauthenticated_role(self) -> typing.Optional[_IRole_59af6f50]:
        '''(experimental) Default Unauthenticated (Guest) Role.

        :default: - No default unauthenticated role will be added

        :stability: experimental
        '''
        result = self._values.get("unauthenticated_role")
        return typing.cast(typing.Optional[_IRole_59af6f50], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolRoleAttachmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolRoleMapping",
    jsii_struct_bases=[],
    name_mapping={
        "provider_url": "providerUrl",
        "resolve_ambiguous_roles": "resolveAmbiguousRoles",
        "rules": "rules",
        "use_token": "useToken",
    },
)
class IdentityPoolRoleMapping:
    def __init__(
        self,
        *,
        provider_url: IdentityPoolProviderUrl,
        resolve_ambiguous_roles: typing.Optional[builtins.bool] = None,
        rules: typing.Optional[typing.Sequence["RoleMappingRule"]] = None,
        use_token: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''(experimental) Map roles to users in the identity pool based on claims from the Identity Provider.

        :param provider_url: (experimental) The url of the provider of for which the role is mapped.
        :param resolve_ambiguous_roles: (experimental) Allow for role assumption when results of role mapping are ambiguous. Default: false - Ambiguous role resolutions will lead to requester being denied
        :param rules: (experimental) The claim and value that must be matched in order to assume the role. Required if useToken is false Default: - No Rule Mapping Rule
        :param use_token: (experimental) If true then mapped roles must be passed through the cognito:roles or cognito:preferred_role claims from identity provider. Default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-identitypoolroleattachment.html
        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            from monocdk import aws_iam as iam
            
            # identity_pool_provider_url: cognito_identitypool.IdentityPoolProviderUrl
            # role: iam.Role
            
            identity_pool_role_mapping = cognito_identitypool.IdentityPoolRoleMapping(
                provider_url=identity_pool_provider_url,
            
                # the properties below are optional
                resolve_ambiguous_roles=False,
                rules=[cognito_identitypool.RoleMappingRule(
                    claim="claim",
                    claim_value="claimValue",
                    mapped_role=role,
            
                    # the properties below are optional
                    match_type=cognito_identitypool.RoleMappingMatchType.EQUALS
                )],
                use_token=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "provider_url": provider_url,
        }
        if resolve_ambiguous_roles is not None:
            self._values["resolve_ambiguous_roles"] = resolve_ambiguous_roles
        if rules is not None:
            self._values["rules"] = rules
        if use_token is not None:
            self._values["use_token"] = use_token

    @builtins.property
    def provider_url(self) -> IdentityPoolProviderUrl:
        '''(experimental) The url of the provider of for which the role is mapped.

        :stability: experimental
        '''
        result = self._values.get("provider_url")
        assert result is not None, "Required property 'provider_url' is missing"
        return typing.cast(IdentityPoolProviderUrl, result)

    @builtins.property
    def resolve_ambiguous_roles(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Allow for role assumption when results of role mapping are ambiguous.

        :default: false - Ambiguous role resolutions will lead to requester being denied

        :stability: experimental
        '''
        result = self._values.get("resolve_ambiguous_roles")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def rules(self) -> typing.Optional[typing.List["RoleMappingRule"]]:
        '''(experimental) The claim and value that must be matched in order to assume the role.

        Required if useToken is false

        :default: - No Rule Mapping Rule

        :stability: experimental
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.List["RoleMappingRule"]], result)

    @builtins.property
    def use_token(self) -> typing.Optional[builtins.bool]:
        '''(experimental) If true then mapped roles must be passed through the cognito:roles or cognito:preferred_role claims from identity provider.

        :default: false

        :see: https://docs.aws.amazon.com/cognito/latest/developerguide/role-based-access-control.html#using-tokens-to-assign-roles-to-users
        :stability: experimental
        '''
        result = self._values.get("use_token")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolRoleMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolTwitterLoginProvider",
    jsii_struct_bases=[],
    name_mapping={"consumer_key": "consumerKey", "consumer_secret": "consumerSecret"},
)
class IdentityPoolTwitterLoginProvider:
    def __init__(
        self,
        *,
        consumer_key: builtins.str,
        consumer_secret: builtins.str,
    ) -> None:
        '''(experimental) Login Provider for Identity Federation using Twitter Credentials.

        :param consumer_key: (experimental) App Id for Twitter Identity Federation.
        :param consumer_secret: (experimental) App Secret for Twitter Identity Federation.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            identity_pool_twitter_login_provider = cognito_identitypool.IdentityPoolTwitterLoginProvider(
                consumer_key="consumerKey",
                consumer_secret="consumerSecret"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
        }

    @builtins.property
    def consumer_key(self) -> builtins.str:
        '''(experimental) App Id for Twitter Identity Federation.

        :stability: experimental
        '''
        result = self._values.get("consumer_key")
        assert result is not None, "Required property 'consumer_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def consumer_secret(self) -> builtins.str:
        '''(experimental) App Secret for Twitter Identity Federation.

        :stability: experimental
        '''
        result = self._values.get("consumer_secret")
        assert result is not None, "Required property 'consumer_secret' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolTwitterLoginProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="monocdk.aws_cognito_identitypool.RoleMappingMatchType")
class RoleMappingMatchType(enum.Enum):
    '''(experimental) Types of matches allowed for Role Mapping.

    :stability: experimental
    '''

    EQUALS = "EQUALS"
    '''(experimental) The Claim from the token must equal the given value in order for a match.

    :stability: experimental
    '''
    CONTAINS = "CONTAINS"
    '''(experimental) The Claim from the token must contain the given value in order for a match.

    :stability: experimental
    '''
    STARTS_WITH = "STARTS_WITH"
    '''(experimental) The Claim from the token must start with the given value in order for a match.

    :stability: experimental
    '''
    NOTEQUAL = "NOTEQUAL"
    '''(experimental) The Claim from the token must not equal the given value in order for a match.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.RoleMappingRule",
    jsii_struct_bases=[],
    name_mapping={
        "claim": "claim",
        "claim_value": "claimValue",
        "mapped_role": "mappedRole",
        "match_type": "matchType",
    },
)
class RoleMappingRule:
    def __init__(
        self,
        *,
        claim: builtins.str,
        claim_value: builtins.str,
        mapped_role: _IRole_59af6f50,
        match_type: typing.Optional[RoleMappingMatchType] = None,
    ) -> None:
        '''(experimental) Represents an Identity Pool Role Attachment Role Mapping Rule.

        :param claim: (experimental) The key sent in the token by the federated identity provider.
        :param claim_value: (experimental) The value of the claim that must be matched.
        :param mapped_role: (experimental) The Role to be assumed when Claim Value is matched.
        :param match_type: (experimental) How to match with the Claim value. Default: RoleMappingMatchType.EQUALS

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            from monocdk import aws_iam as iam
            
            # role: iam.Role
            
            role_mapping_rule = cognito_identitypool.RoleMappingRule(
                claim="claim",
                claim_value="claimValue",
                mapped_role=role,
            
                # the properties below are optional
                match_type=cognito_identitypool.RoleMappingMatchType.EQUALS
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "claim": claim,
            "claim_value": claim_value,
            "mapped_role": mapped_role,
        }
        if match_type is not None:
            self._values["match_type"] = match_type

    @builtins.property
    def claim(self) -> builtins.str:
        '''(experimental) The key sent in the token by the federated identity provider.

        :stability: experimental
        '''
        result = self._values.get("claim")
        assert result is not None, "Required property 'claim' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def claim_value(self) -> builtins.str:
        '''(experimental) The value of the claim that must be matched.

        :stability: experimental
        '''
        result = self._values.get("claim_value")
        assert result is not None, "Required property 'claim_value' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mapped_role(self) -> _IRole_59af6f50:
        '''(experimental) The Role to be assumed when Claim Value is matched.

        :stability: experimental
        '''
        result = self._values.get("mapped_role")
        assert result is not None, "Required property 'mapped_role' is missing"
        return typing.cast(_IRole_59af6f50, result)

    @builtins.property
    def match_type(self) -> typing.Optional[RoleMappingMatchType]:
        '''(experimental) How to match with the Claim value.

        :default: RoleMappingMatchType.EQUALS

        :stability: experimental
        '''
        result = self._values.get("match_type")
        return typing.cast(typing.Optional[RoleMappingMatchType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RoleMappingRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IUserPoolAuthenticationProvider)
class UserPoolAuthenticationProvider(
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_cognito_identitypool.UserPoolAuthenticationProvider",
):
    '''(experimental) Defines a User Pool Authentication Provider.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        from monocdk import aws_cognito as cognito
        from monocdk import aws_cognito_identitypool as cognito_identitypool
        
        # user_pool: cognito.UserPool
        # user_pool_client: cognito.UserPoolClient
        
        user_pool_authentication_provider = cognito_identitypool.UserPoolAuthenticationProvider(
            user_pool=user_pool,
        
            # the properties below are optional
            disable_server_side_token_check=False,
            user_pool_client=user_pool_client
        )
    '''

    def __init__(
        self,
        *,
        user_pool: _IUserPool_5e500460,
        disable_server_side_token_check: typing.Optional[builtins.bool] = None,
        user_pool_client: typing.Optional[_IUserPoolClient_4cdf19bd] = None,
    ) -> None:
        '''
        :param user_pool: (experimental) The User Pool of the Associated Identity Providers.
        :param disable_server_side_token_check: (experimental) Setting this to true turns off identity pool checks for this user pool to make sure the user has not been globally signed out or deleted before the identity pool provides an OIDC token or AWS credentials for the user. Default: false
        :param user_pool_client: (experimental) The User Pool Client for the provided User Pool. Default: - A default user pool client will be added to User Pool

        :stability: experimental
        '''
        props = UserPoolAuthenticationProviderProps(
            user_pool=user_pool,
            disable_server_side_token_check=disable_server_side_token_check,
            user_pool_client=user_pool_client,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: constructs.Construct,
        identity_pool: IIdentityPool,
    ) -> "UserPoolAuthenticationProviderBindConfig":
        '''(experimental) The method called when a given User Pool Authentication Provider is added (for the first time) to an Identity Pool.

        :param scope: -
        :param identity_pool: -

        :stability: experimental
        '''
        _options = UserPoolAuthenticationProviderBindOptions()

        return typing.cast("UserPoolAuthenticationProviderBindConfig", jsii.invoke(self, "bind", [scope, identity_pool, _options]))


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.UserPoolAuthenticationProviderBindConfig",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "provider_name": "providerName",
        "server_side_token_check": "serverSideTokenCheck",
    },
)
class UserPoolAuthenticationProviderBindConfig:
    def __init__(
        self,
        *,
        client_id: builtins.str,
        provider_name: builtins.str,
        server_side_token_check: builtins.bool,
    ) -> None:
        '''(experimental) Represents a UserPoolAuthenticationProvider Bind Configuration.

        :param client_id: (experimental) Client Id of the Associated User Pool Client.
        :param provider_name: (experimental) The identity providers associated with the UserPool.
        :param server_side_token_check: (experimental) Whether to enable the identity pool's server side token check.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            user_pool_authentication_provider_bind_config = cognito_identitypool.UserPoolAuthenticationProviderBindConfig(
                client_id="clientId",
                provider_name="providerName",
                server_side_token_check=False
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "client_id": client_id,
            "provider_name": provider_name,
            "server_side_token_check": server_side_token_check,
        }

    @builtins.property
    def client_id(self) -> builtins.str:
        '''(experimental) Client Id of the Associated User Pool Client.

        :stability: experimental
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_name(self) -> builtins.str:
        '''(experimental) The identity providers associated with the UserPool.

        :stability: experimental
        '''
        result = self._values.get("provider_name")
        assert result is not None, "Required property 'provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def server_side_token_check(self) -> builtins.bool:
        '''(experimental) Whether to enable the identity pool's server side token check.

        :stability: experimental
        '''
        result = self._values.get("server_side_token_check")
        assert result is not None, "Required property 'server_side_token_check' is missing"
        return typing.cast(builtins.bool, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPoolAuthenticationProviderBindConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.UserPoolAuthenticationProviderBindOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class UserPoolAuthenticationProviderBindOptions:
    def __init__(self) -> None:
        '''(experimental) Represents UserPoolAuthenticationProvider Bind Options.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            user_pool_authentication_provider_bind_options = cognito_identitypool.UserPoolAuthenticationProviderBindOptions()
        '''
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPoolAuthenticationProviderBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.UserPoolAuthenticationProviderProps",
    jsii_struct_bases=[],
    name_mapping={
        "user_pool": "userPool",
        "disable_server_side_token_check": "disableServerSideTokenCheck",
        "user_pool_client": "userPoolClient",
    },
)
class UserPoolAuthenticationProviderProps:
    def __init__(
        self,
        *,
        user_pool: _IUserPool_5e500460,
        disable_server_side_token_check: typing.Optional[builtins.bool] = None,
        user_pool_client: typing.Optional[_IUserPoolClient_4cdf19bd] = None,
    ) -> None:
        '''(experimental) Props for the User Pool Authentication Provider.

        :param user_pool: (experimental) The User Pool of the Associated Identity Providers.
        :param disable_server_side_token_check: (experimental) Setting this to true turns off identity pool checks for this user pool to make sure the user has not been globally signed out or deleted before the identity pool provides an OIDC token or AWS credentials for the user. Default: false
        :param user_pool_client: (experimental) The User Pool Client for the provided User Pool. Default: - A default user pool client will be added to User Pool

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito as cognito
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            # user_pool: cognito.UserPool
            # user_pool_client: cognito.UserPoolClient
            
            user_pool_authentication_provider_props = cognito_identitypool.UserPoolAuthenticationProviderProps(
                user_pool=user_pool,
            
                # the properties below are optional
                disable_server_side_token_check=False,
                user_pool_client=user_pool_client
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "user_pool": user_pool,
        }
        if disable_server_side_token_check is not None:
            self._values["disable_server_side_token_check"] = disable_server_side_token_check
        if user_pool_client is not None:
            self._values["user_pool_client"] = user_pool_client

    @builtins.property
    def user_pool(self) -> _IUserPool_5e500460:
        '''(experimental) The User Pool of the Associated Identity Providers.

        :stability: experimental
        '''
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(_IUserPool_5e500460, result)

    @builtins.property
    def disable_server_side_token_check(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Setting this to true turns off identity pool checks for this user pool to make sure the user has not been globally signed out or deleted before the identity pool provides an OIDC token or AWS credentials for the user.

        :default: false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cognito-identitypool-cognitoidentityprovider.html
        :stability: experimental
        '''
        result = self._values.get("disable_server_side_token_check")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def user_pool_client(self) -> typing.Optional[_IUserPoolClient_4cdf19bd]:
        '''(experimental) The User Pool Client for the provided User Pool.

        :default: - A default user pool client will be added to User Pool

        :stability: experimental
        '''
        result = self._values.get("user_pool_client")
        return typing.cast(typing.Optional[_IUserPoolClient_4cdf19bd], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UserPoolAuthenticationProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolAuthenticationProviders",
    jsii_struct_bases=[IdentityPoolProviders],
    name_mapping={
        "amazon": "amazon",
        "apple": "apple",
        "digits": "digits",
        "facebook": "facebook",
        "google": "google",
        "twitter": "twitter",
        "custom_provider": "customProvider",
        "open_id_connect_providers": "openIdConnectProviders",
        "saml_providers": "samlProviders",
        "user_pools": "userPools",
    },
)
class IdentityPoolAuthenticationProviders(IdentityPoolProviders):
    def __init__(
        self,
        *,
        amazon: typing.Optional[IdentityPoolAmazonLoginProvider] = None,
        apple: typing.Optional[IdentityPoolAppleLoginProvider] = None,
        digits: typing.Optional["IdentityPoolDigitsLoginProvider"] = None,
        facebook: typing.Optional[IdentityPoolFacebookLoginProvider] = None,
        google: typing.Optional[IdentityPoolGoogleLoginProvider] = None,
        twitter: typing.Optional[IdentityPoolTwitterLoginProvider] = None,
        custom_provider: typing.Optional[builtins.str] = None,
        open_id_connect_providers: typing.Optional[typing.Sequence[_IOpenIdConnectProvider_bb431740]] = None,
        saml_providers: typing.Optional[typing.Sequence[_ISamlProvider_b494dc4e]] = None,
        user_pools: typing.Optional[typing.Sequence[IUserPoolAuthenticationProvider]] = None,
    ) -> None:
        '''(experimental) Authentication providers for using in identity pool.

        :param amazon: (experimental) App Id for Amazon Identity Federation. Default: - No Amazon Authentication Provider used without OpenIdConnect or a User Pool
        :param apple: (experimental) Services Id for Apple Identity Federation. Default: - No Apple Authentication Provider used without OpenIdConnect or a User Pool
        :param digits: (experimental) Consumer Key and Secret for Digits Identity Federation. Default: - No Digits Authentication Provider used without OpenIdConnect or a User Pool
        :param facebook: (experimental) App Id for Facebook Identity Federation. Default: - No Facebook Authentication Provider used without OpenIdConnect or a User Pool
        :param google: (experimental) Client Id for Google Identity Federation. Default: - No Google Authentication Provider used without OpenIdConnect or a User Pool
        :param twitter: (experimental) Consumer Key and Secret for Twitter Identity Federation. Default: - No Twitter Authentication Provider used without OpenIdConnect or a User Pool
        :param custom_provider: (experimental) The Developer Provider Name to associate with this Identity Pool. Default: - no Custom Provider
        :param open_id_connect_providers: (experimental) The OpenIdConnect Provider associated with this Identity Pool. Default: - no OpenIdConnectProvider
        :param saml_providers: (experimental) The Security Assertion Markup Language Provider associated with this Identity Pool. Default: - no SamlProvider
        :param user_pools: (experimental) The User Pool Authentication Providers associated with this Identity Pool. Default: - no User Pools Associated

        :see: https://docs.aws.amazon.com/cognito/latest/developerguide/external-identity-providers.html
        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            from monocdk import aws_iam as iam
            
            # open_id_connect_provider: iam.OpenIdConnectProvider
            # saml_provider: iam.SamlProvider
            # user_pool_authentication_provider: cognito_identitypool.UserPoolAuthenticationProvider
            
            identity_pool_authentication_providers = cognito_identitypool.IdentityPoolAuthenticationProviders(
                amazon=cognito_identitypool.IdentityPoolAmazonLoginProvider(
                    app_id="appId"
                ),
                apple=cognito_identitypool.IdentityPoolAppleLoginProvider(
                    services_id="servicesId"
                ),
                custom_provider="customProvider",
                digits=cognito_identitypool.IdentityPoolDigitsLoginProvider(
                    consumer_key="consumerKey",
                    consumer_secret="consumerSecret"
                ),
                facebook=cognito_identitypool.IdentityPoolFacebookLoginProvider(
                    app_id="appId"
                ),
                google=cognito_identitypool.IdentityPoolGoogleLoginProvider(
                    client_id="clientId"
                ),
                open_id_connect_providers=[open_id_connect_provider],
                saml_providers=[saml_provider],
                twitter=cognito_identitypool.IdentityPoolTwitterLoginProvider(
                    consumer_key="consumerKey",
                    consumer_secret="consumerSecret"
                ),
                user_pools=[user_pool_authentication_provider]
            )
        '''
        if isinstance(amazon, dict):
            amazon = IdentityPoolAmazonLoginProvider(**amazon)
        if isinstance(apple, dict):
            apple = IdentityPoolAppleLoginProvider(**apple)
        if isinstance(digits, dict):
            digits = IdentityPoolDigitsLoginProvider(**digits)
        if isinstance(facebook, dict):
            facebook = IdentityPoolFacebookLoginProvider(**facebook)
        if isinstance(google, dict):
            google = IdentityPoolGoogleLoginProvider(**google)
        if isinstance(twitter, dict):
            twitter = IdentityPoolTwitterLoginProvider(**twitter)
        self._values: typing.Dict[str, typing.Any] = {}
        if amazon is not None:
            self._values["amazon"] = amazon
        if apple is not None:
            self._values["apple"] = apple
        if digits is not None:
            self._values["digits"] = digits
        if facebook is not None:
            self._values["facebook"] = facebook
        if google is not None:
            self._values["google"] = google
        if twitter is not None:
            self._values["twitter"] = twitter
        if custom_provider is not None:
            self._values["custom_provider"] = custom_provider
        if open_id_connect_providers is not None:
            self._values["open_id_connect_providers"] = open_id_connect_providers
        if saml_providers is not None:
            self._values["saml_providers"] = saml_providers
        if user_pools is not None:
            self._values["user_pools"] = user_pools

    @builtins.property
    def amazon(self) -> typing.Optional[IdentityPoolAmazonLoginProvider]:
        '''(experimental) App Id for Amazon Identity Federation.

        :default: - No Amazon Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("amazon")
        return typing.cast(typing.Optional[IdentityPoolAmazonLoginProvider], result)

    @builtins.property
    def apple(self) -> typing.Optional[IdentityPoolAppleLoginProvider]:
        '''(experimental) Services Id for Apple Identity Federation.

        :default: - No Apple Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("apple")
        return typing.cast(typing.Optional[IdentityPoolAppleLoginProvider], result)

    @builtins.property
    def digits(self) -> typing.Optional["IdentityPoolDigitsLoginProvider"]:
        '''(experimental) Consumer Key and Secret for Digits Identity Federation.

        :default: - No Digits Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("digits")
        return typing.cast(typing.Optional["IdentityPoolDigitsLoginProvider"], result)

    @builtins.property
    def facebook(self) -> typing.Optional[IdentityPoolFacebookLoginProvider]:
        '''(experimental) App Id for Facebook Identity Federation.

        :default: - No Facebook Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("facebook")
        return typing.cast(typing.Optional[IdentityPoolFacebookLoginProvider], result)

    @builtins.property
    def google(self) -> typing.Optional[IdentityPoolGoogleLoginProvider]:
        '''(experimental) Client Id for Google Identity Federation.

        :default: - No Google Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("google")
        return typing.cast(typing.Optional[IdentityPoolGoogleLoginProvider], result)

    @builtins.property
    def twitter(self) -> typing.Optional[IdentityPoolTwitterLoginProvider]:
        '''(experimental) Consumer Key and Secret for Twitter Identity Federation.

        :default: - No Twitter Authentication Provider used without OpenIdConnect or a User Pool

        :stability: experimental
        '''
        result = self._values.get("twitter")
        return typing.cast(typing.Optional[IdentityPoolTwitterLoginProvider], result)

    @builtins.property
    def custom_provider(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Developer Provider Name to associate with this Identity Pool.

        :default: - no Custom Provider

        :stability: experimental
        '''
        result = self._values.get("custom_provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def open_id_connect_providers(
        self,
    ) -> typing.Optional[typing.List[_IOpenIdConnectProvider_bb431740]]:
        '''(experimental) The OpenIdConnect Provider associated with this Identity Pool.

        :default: - no OpenIdConnectProvider

        :stability: experimental
        '''
        result = self._values.get("open_id_connect_providers")
        return typing.cast(typing.Optional[typing.List[_IOpenIdConnectProvider_bb431740]], result)

    @builtins.property
    def saml_providers(self) -> typing.Optional[typing.List[_ISamlProvider_b494dc4e]]:
        '''(experimental) The Security Assertion Markup Language Provider associated with this Identity Pool.

        :default: - no SamlProvider

        :stability: experimental
        '''
        result = self._values.get("saml_providers")
        return typing.cast(typing.Optional[typing.List[_ISamlProvider_b494dc4e]], result)

    @builtins.property
    def user_pools(
        self,
    ) -> typing.Optional[typing.List[IUserPoolAuthenticationProvider]]:
        '''(experimental) The User Pool Authentication Providers associated with this Identity Pool.

        :default: - no User Pools Associated

        :stability: experimental
        '''
        result = self._values.get("user_pools")
        return typing.cast(typing.Optional[typing.List[IUserPoolAuthenticationProvider]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolAuthenticationProviders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="monocdk.aws_cognito_identitypool.IdentityPoolDigitsLoginProvider",
    jsii_struct_bases=[IdentityPoolTwitterLoginProvider],
    name_mapping={"consumer_key": "consumerKey", "consumer_secret": "consumerSecret"},
)
class IdentityPoolDigitsLoginProvider(IdentityPoolTwitterLoginProvider):
    def __init__(
        self,
        *,
        consumer_key: builtins.str,
        consumer_secret: builtins.str,
    ) -> None:
        '''(experimental) Login Provider for Identity Federation using Digits Credentials.

        :param consumer_key: (experimental) App Id for Twitter Identity Federation.
        :param consumer_secret: (experimental) App Secret for Twitter Identity Federation.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from monocdk import aws_cognito_identitypool as cognito_identitypool
            
            identity_pool_digits_login_provider = cognito_identitypool.IdentityPoolDigitsLoginProvider(
                consumer_key="consumerKey",
                consumer_secret="consumerSecret"
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
        }

    @builtins.property
    def consumer_key(self) -> builtins.str:
        '''(experimental) App Id for Twitter Identity Federation.

        :stability: experimental
        '''
        result = self._values.get("consumer_key")
        assert result is not None, "Required property 'consumer_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def consumer_secret(self) -> builtins.str:
        '''(experimental) App Secret for Twitter Identity Federation.

        :stability: experimental
        '''
        result = self._values.get("consumer_secret")
        assert result is not None, "Required property 'consumer_secret' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "IdentityPoolDigitsLoginProvider(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IIdentityPool",
    "IIdentityPoolRoleAttachment",
    "IUserPoolAuthenticationProvider",
    "IdentityPool",
    "IdentityPoolAmazonLoginProvider",
    "IdentityPoolAppleLoginProvider",
    "IdentityPoolAuthenticationProviders",
    "IdentityPoolDigitsLoginProvider",
    "IdentityPoolFacebookLoginProvider",
    "IdentityPoolGoogleLoginProvider",
    "IdentityPoolProps",
    "IdentityPoolProviderType",
    "IdentityPoolProviderUrl",
    "IdentityPoolProviders",
    "IdentityPoolRoleAttachment",
    "IdentityPoolRoleAttachmentProps",
    "IdentityPoolRoleMapping",
    "IdentityPoolTwitterLoginProvider",
    "RoleMappingMatchType",
    "RoleMappingRule",
    "UserPoolAuthenticationProvider",
    "UserPoolAuthenticationProviderBindConfig",
    "UserPoolAuthenticationProviderBindOptions",
    "UserPoolAuthenticationProviderProps",
]

publication.publish()
