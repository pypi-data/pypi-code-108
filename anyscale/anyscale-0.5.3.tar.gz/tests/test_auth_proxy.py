from http.cookies import SimpleCookie
from typing import Optional
from unittest.mock import Mock

import pytest

from anyscale.auth_proxy import index, make_auth_proxy_app


async def test_auth_token_redirect_serve():
    make_auth_proxy_app("mock_auth_token")
    mock_request = Mock(
        query={"token": "mock_auth_token", "redirect_to": None, "auth_only": None},
        headers={"Host": "serve-session-id.i.anyscaleuserdata-staging.com"},
    )

    resp = await index(mock_request)
    assert resp.status == 302
    assert resp.location == "https://serve-session-id.i.anyscaleuserdata-staging.com"

    expected_cookies = SimpleCookie()
    expected_cookies["anyscale-token"] = "mock_auth_token"
    expected_cookies["anyscale-token"]["path"] = "/"
    assert str(resp.cookies) == str(expected_cookies)


@pytest.mark.parametrize(
    "service",
    [
        "tensorboard",
        "dashboard",
        "grafana",
        "webterminal",
        "serve",
        "hosted_dashboard",
        "anyscaled",
        "metrics",
    ],
)
@pytest.mark.parametrize("auth_only", [True, None])
async def test_auth_token_redirect_services(service: str, auth_only: Optional[bool]):
    make_auth_proxy_app("mock_auth_token")
    mock_request = Mock(
        query={
            "token": "mock_auth_token",
            "redirect_to": service,
            "auth_only": auth_only,
        },
        headers={"Host": "session-id.i.anyscaleuserdata-staging.com"},
    )

    resp = await index(mock_request)
    if auth_only:
        assert resp.status == 200
    else:
        assert resp.status == 302

        redirect_path = {
            "tensorboard": "/tensorboard/",
            "grafana": "/grafana/",
            "dashboard": "/",
            "hosted_dashboard": "/metrics/redirect",
            "webterminal": "/webterminal/",
            "anyscaled": "/anyscaled/",
            "metrics": "/metrics",
            "autoscalermetrics": "/autoscalermetrics",
            "serve": "/serve",
        }
        assert resp.location == redirect_path[service]

    expected_cookies: SimpleCookie = SimpleCookie()
    expected_cookies["anyscale-token"] = "mock_auth_token"
    expected_cookies["anyscale-token"]["path"] = "/"
    if service == "webterminal":
        expected_cookies["anyscale-token"]["samesite"] = None
        expected_cookies["anyscale-token"]["secure"] = True
    assert str(resp.cookies) == str(expected_cookies)
