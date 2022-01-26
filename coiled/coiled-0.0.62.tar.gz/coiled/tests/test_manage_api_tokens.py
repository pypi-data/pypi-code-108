import coiled
import pytest
from distributed.utils_test import loop  # noqa: F401
from django.test import override_settings

from api_tokens.models import ApiToken

pytestmark = pytest.mark.test_group("test_api_tokens")


@pytest.fixture(
    params=[
        {},
        {"days_to_expire": 2},
        {"label": "my token"},
    ]  # testing out a few different token creation kwargs
)
def created_api_token(sample_user, request):
    with override_settings(LONG_LIVED_TOKENS_ENABLED=True):
        api_token = coiled.create_api_token(**request.param)
    return api_token


@override_settings(LONG_LIVED_TOKENS_ENABLED=True)
def test_can_create_api_token(sample_user, created_api_token):
    assert created_api_token["token"] is not None


@override_settings(LONG_LIVED_TOKENS_ENABLED=True)
def test_default_list_excludes_revoked(sample_user):
    created_api_token = coiled.create_api_token()
    identifier = created_api_token["identifier"]
    coiled.revoke_api_token(identifier=identifier)
    listed_api_tokens = coiled.list_api_tokens()
    assert identifier not in listed_api_tokens


@override_settings(LONG_LIVED_TOKENS_ENABLED=True)
def test_list_create_api_tokens(created_api_token, sample_user):
    """Check that the listed details of an API token match what we created it with.

    Here we'll just check that the tokens *include* the token we expect. It's okay if there are extras.
    We have stricter tests elsewhere (api_tokens/tests.py::test_list_tokens) that confirm the list is
    exactly what we expect, and that users don't see other users' tokens in the list.
    """
    identifier = created_api_token["identifier"]
    listed_api_tokens = coiled.list_api_tokens()
    listed_api_token = listed_api_tokens[identifier]

    assert "token" not in listed_api_token  # the token value shouldn't be here

    # check that the created token and listed token match (except for 'token')
    created_token_without_secret_token = {
        k: v for k, v in created_api_token.items() if k != "token"
    }

    assert listed_api_tokens[identifier] == created_token_without_secret_token


@override_settings(LONG_LIVED_TOKENS_ENABLED=True)
def test_revoke_api_token_by_identifier(sample_user):
    created_api_token = coiled.create_api_token()
    identifier = created_api_token["identifier"]
    coiled.revoke_api_token(identifier=identifier)
    listed_api_tokens = coiled.list_api_tokens(include_inactive=True)
    assert listed_api_tokens[identifier]["revoked"]


@override_settings(LONG_LIVED_TOKENS_ENABLED=True)
def test_revoke_api_token_by_label(sample_user):
    token_to_revoke = coiled.create_api_token(label="my token to revoke")
    token_to_keep = coiled.create_api_token(label="my token not to revoke")
    coiled.revoke_api_token(label="my token to revoke")
    listed_api_tokens = coiled.list_api_tokens(include_inactive=True)

    assert listed_api_tokens[token_to_revoke["identifier"]]["revoked"]
    assert not listed_api_tokens[token_to_keep["identifier"]]["revoked"]


@override_settings(LONG_LIVED_TOKENS_ENABLED=True)
def test_revoke_all_api_tokens(sample_user):
    coiled.create_api_token()
    coiled.create_api_token()
    coiled.revoke_all_api_tokens()

    tokens = ApiToken.objects.filter(user_id=sample_user.user.id)
    for token in tokens:
        assert token.revoked
