'''
# Actions for AWS Elastic Load Balancing V2

This package contains integration actions for ELBv2. See the README of the `@aws-cdk/aws-elasticloadbalancingv2` library.

## Cognito

ELB allows for requests to be authenticated against a Cognito user pool using
the `AuthenticateCognitoAction`. For details on the setup's requirements,
read [Prepare to use Amazon
Cognito](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html#cognito-requirements).
Here's an example:

[Example of using AuthenticateCognitoAction](test/integ.cognito.lit.ts)

> NOTE: this example seems incomplete, I was not able to get the redirect back to the
> Load Balancer after authentication working. Would love some pointers on what a full working
> setup actually looks like!
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

from .. import Duration as _Duration_070aa057
from ..aws_cognito import (
    IUserPool as _IUserPool_5e500460,
    IUserPoolClient as _IUserPoolClient_4cdf19bd,
    IUserPoolDomain as _IUserPoolDomain_1ae2cfab,
)
from ..aws_elasticloadbalancingv2 import (
    ListenerAction as _ListenerAction_5de1dcc2,
    UnauthenticatedAction as _UnauthenticatedAction_dce2040c,
)


class AuthenticateCognitoAction(
    _ListenerAction_5de1dcc2,
    metaclass=jsii.JSIIMeta,
    jsii_type="monocdk.aws_elasticloadbalancingv2_actions.AuthenticateCognitoAction",
):
    '''(experimental) A Listener Action to authenticate with Cognito.

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import monocdk as monocdk
        from monocdk import aws_elasticloadbalancingv2 as elasticloadbalancingv2
        from monocdk import aws_elasticloadbalancingv2_actions as elasticloadbalancingv2_actions
        
        # duration: monocdk.Duration
        # listener_action: elasticloadbalancingv2.ListenerAction
        # secret_value: monocdk.SecretValue
        
        authenticate_cognito_action = elasticloadbalancingv2_actions.AuthenticateCognitoAction.authenticate_oidc(
            authorization_endpoint="authorizationEndpoint",
            client_id="clientId",
            client_secret=secret_value,
            issuer="issuer",
            next=listener_action,
            token_endpoint="tokenEndpoint",
            user_info_endpoint="userInfoEndpoint",
        
            # the properties below are optional
            authentication_request_extra_params={
                "authentication_request_extra_params_key": "authenticationRequestExtraParams"
            },
            on_unauthenticated_request=elasticloadbalancingv2.UnauthenticatedAction.DENY,
            scope="scope",
            session_cookie_name="sessionCookieName",
            session_timeout=duration
        )
    '''

    def __init__(
        self,
        *,
        next: _ListenerAction_5de1dcc2,
        user_pool: _IUserPool_5e500460,
        user_pool_client: _IUserPoolClient_4cdf19bd,
        user_pool_domain: _IUserPoolDomain_1ae2cfab,
        authentication_request_extra_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        on_unauthenticated_request: typing.Optional[_UnauthenticatedAction_dce2040c] = None,
        scope: typing.Optional[builtins.str] = None,
        session_cookie_name: typing.Optional[builtins.str] = None,
        session_timeout: typing.Optional[_Duration_070aa057] = None,
    ) -> None:
        '''(experimental) Authenticate using an identity provide (IdP) that is compliant with OpenID Connect (OIDC).

        :param next: (experimental) What action to execute next. Multiple actions form a linked chain; the chain must always terminate in a (weighted)forward, fixedResponse or redirect action.
        :param user_pool: (experimental) The Amazon Cognito user pool.
        :param user_pool_client: (experimental) The Amazon Cognito user pool client.
        :param user_pool_domain: (experimental) The domain prefix or fully-qualified domain name of the Amazon Cognito user pool.
        :param authentication_request_extra_params: (experimental) The query parameters (up to 10) to include in the redirect request to the authorization endpoint. Default: - No extra parameters
        :param on_unauthenticated_request: (experimental) The behavior if the user is not authenticated. Default: UnauthenticatedAction.AUTHENTICATE
        :param scope: (experimental) The set of user claims to be requested from the IdP. To verify which scope values your IdP supports and how to separate multiple values, see the documentation for your IdP. Default: "openid"
        :param session_cookie_name: (experimental) The name of the cookie used to maintain session information. Default: "AWSELBAuthSessionCookie"
        :param session_timeout: (experimental) The maximum duration of the authentication session. Default: Duration.days(7)

        :stability: experimental
        '''
        options = AuthenticateCognitoActionProps(
            next=next,
            user_pool=user_pool,
            user_pool_client=user_pool_client,
            user_pool_domain=user_pool_domain,
            authentication_request_extra_params=authentication_request_extra_params,
            on_unauthenticated_request=on_unauthenticated_request,
            scope=scope,
            session_cookie_name=session_cookie_name,
            session_timeout=session_timeout,
        )

        jsii.create(self.__class__, self, [options])


@jsii.data_type(
    jsii_type="monocdk.aws_elasticloadbalancingv2_actions.AuthenticateCognitoActionProps",
    jsii_struct_bases=[],
    name_mapping={
        "next": "next",
        "user_pool": "userPool",
        "user_pool_client": "userPoolClient",
        "user_pool_domain": "userPoolDomain",
        "authentication_request_extra_params": "authenticationRequestExtraParams",
        "on_unauthenticated_request": "onUnauthenticatedRequest",
        "scope": "scope",
        "session_cookie_name": "sessionCookieName",
        "session_timeout": "sessionTimeout",
    },
)
class AuthenticateCognitoActionProps:
    def __init__(
        self,
        *,
        next: _ListenerAction_5de1dcc2,
        user_pool: _IUserPool_5e500460,
        user_pool_client: _IUserPoolClient_4cdf19bd,
        user_pool_domain: _IUserPoolDomain_1ae2cfab,
        authentication_request_extra_params: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        on_unauthenticated_request: typing.Optional[_UnauthenticatedAction_dce2040c] = None,
        scope: typing.Optional[builtins.str] = None,
        session_cookie_name: typing.Optional[builtins.str] = None,
        session_timeout: typing.Optional[_Duration_070aa057] = None,
    ) -> None:
        '''(experimental) Properties for AuthenticateCognitoAction.

        :param next: (experimental) What action to execute next. Multiple actions form a linked chain; the chain must always terminate in a (weighted)forward, fixedResponse or redirect action.
        :param user_pool: (experimental) The Amazon Cognito user pool.
        :param user_pool_client: (experimental) The Amazon Cognito user pool client.
        :param user_pool_domain: (experimental) The domain prefix or fully-qualified domain name of the Amazon Cognito user pool.
        :param authentication_request_extra_params: (experimental) The query parameters (up to 10) to include in the redirect request to the authorization endpoint. Default: - No extra parameters
        :param on_unauthenticated_request: (experimental) The behavior if the user is not authenticated. Default: UnauthenticatedAction.AUTHENTICATE
        :param scope: (experimental) The set of user claims to be requested from the IdP. To verify which scope values your IdP supports and how to separate multiple values, see the documentation for your IdP. Default: "openid"
        :param session_cookie_name: (experimental) The name of the cookie used to maintain session information. Default: "AWSELBAuthSessionCookie"
        :param session_timeout: (experimental) The maximum duration of the authentication session. Default: Duration.days(7)

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import monocdk as monocdk
            from monocdk import aws_cognito as cognito
            from monocdk import aws_elasticloadbalancingv2 as elasticloadbalancingv2
            from monocdk import aws_elasticloadbalancingv2_actions as elasticloadbalancingv2_actions
            
            # duration: monocdk.Duration
            # listener_action: elasticloadbalancingv2.ListenerAction
            # user_pool: cognito.UserPool
            # user_pool_client: cognito.UserPoolClient
            # user_pool_domain: cognito.UserPoolDomain
            
            authenticate_cognito_action_props = elasticloadbalancingv2_actions.AuthenticateCognitoActionProps(
                next=listener_action,
                user_pool=user_pool,
                user_pool_client=user_pool_client,
                user_pool_domain=user_pool_domain,
            
                # the properties below are optional
                authentication_request_extra_params={
                    "authentication_request_extra_params_key": "authenticationRequestExtraParams"
                },
                on_unauthenticated_request=elasticloadbalancingv2.UnauthenticatedAction.DENY,
                scope="scope",
                session_cookie_name="sessionCookieName",
                session_timeout=duration
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "next": next,
            "user_pool": user_pool,
            "user_pool_client": user_pool_client,
            "user_pool_domain": user_pool_domain,
        }
        if authentication_request_extra_params is not None:
            self._values["authentication_request_extra_params"] = authentication_request_extra_params
        if on_unauthenticated_request is not None:
            self._values["on_unauthenticated_request"] = on_unauthenticated_request
        if scope is not None:
            self._values["scope"] = scope
        if session_cookie_name is not None:
            self._values["session_cookie_name"] = session_cookie_name
        if session_timeout is not None:
            self._values["session_timeout"] = session_timeout

    @builtins.property
    def next(self) -> _ListenerAction_5de1dcc2:
        '''(experimental) What action to execute next.

        Multiple actions form a linked chain; the chain must always terminate in a
        (weighted)forward, fixedResponse or redirect action.

        :stability: experimental
        '''
        result = self._values.get("next")
        assert result is not None, "Required property 'next' is missing"
        return typing.cast(_ListenerAction_5de1dcc2, result)

    @builtins.property
    def user_pool(self) -> _IUserPool_5e500460:
        '''(experimental) The Amazon Cognito user pool.

        :stability: experimental
        '''
        result = self._values.get("user_pool")
        assert result is not None, "Required property 'user_pool' is missing"
        return typing.cast(_IUserPool_5e500460, result)

    @builtins.property
    def user_pool_client(self) -> _IUserPoolClient_4cdf19bd:
        '''(experimental) The Amazon Cognito user pool client.

        :stability: experimental
        '''
        result = self._values.get("user_pool_client")
        assert result is not None, "Required property 'user_pool_client' is missing"
        return typing.cast(_IUserPoolClient_4cdf19bd, result)

    @builtins.property
    def user_pool_domain(self) -> _IUserPoolDomain_1ae2cfab:
        '''(experimental) The domain prefix or fully-qualified domain name of the Amazon Cognito user pool.

        :stability: experimental
        '''
        result = self._values.get("user_pool_domain")
        assert result is not None, "Required property 'user_pool_domain' is missing"
        return typing.cast(_IUserPoolDomain_1ae2cfab, result)

    @builtins.property
    def authentication_request_extra_params(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The query parameters (up to 10) to include in the redirect request to the authorization endpoint.

        :default: - No extra parameters

        :stability: experimental
        '''
        result = self._values.get("authentication_request_extra_params")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def on_unauthenticated_request(
        self,
    ) -> typing.Optional[_UnauthenticatedAction_dce2040c]:
        '''(experimental) The behavior if the user is not authenticated.

        :default: UnauthenticatedAction.AUTHENTICATE

        :stability: experimental
        '''
        result = self._values.get("on_unauthenticated_request")
        return typing.cast(typing.Optional[_UnauthenticatedAction_dce2040c], result)

    @builtins.property
    def scope(self) -> typing.Optional[builtins.str]:
        '''(experimental) The set of user claims to be requested from the IdP.

        To verify which scope values your IdP supports and how to separate multiple values, see the documentation for your IdP.

        :default: "openid"

        :stability: experimental
        '''
        result = self._values.get("scope")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_cookie_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the cookie used to maintain session information.

        :default: "AWSELBAuthSessionCookie"

        :stability: experimental
        '''
        result = self._values.get("session_cookie_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_timeout(self) -> typing.Optional[_Duration_070aa057]:
        '''(experimental) The maximum duration of the authentication session.

        :default: Duration.days(7)

        :stability: experimental
        '''
        result = self._values.get("session_timeout")
        return typing.cast(typing.Optional[_Duration_070aa057], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthenticateCognitoActionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthenticateCognitoAction",
    "AuthenticateCognitoActionProps",
]

publication.publish()
