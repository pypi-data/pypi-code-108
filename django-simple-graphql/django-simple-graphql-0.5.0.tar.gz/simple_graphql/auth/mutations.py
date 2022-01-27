from typing import Any

import graphene
from django.contrib.auth import authenticate
from graphene import relay
from graphql import GraphQLError

from simple_graphql.auth.models import AuthenticationSession


class LoginMutation(relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    auth_token = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root: Any, info: Any, username: str, password: str):
        user = authenticate(
            request=info.context,
            username=username,
            password=password,
        )
        if not user or not user.is_active:
            raise GraphQLError("Invalid username or password")
        auth_session = AuthenticationSession.create_for_user(user=user)
        return LoginMutation(auth_token=auth_session.key)
