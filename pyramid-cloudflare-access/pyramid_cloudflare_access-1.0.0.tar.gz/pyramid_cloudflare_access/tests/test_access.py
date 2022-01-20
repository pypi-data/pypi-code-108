"""Tests for HerokuappAccess tween."""

from pyramid import testing
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid_cloudflare_access import CloudflareAccess

import pytest

# Taken from example at https://pyjwt.readthedocs.io/en/latest/usage.html#retrieve-rsa-signing-keys-from-a-jwks-endpoint
sample_jwk = {
    "keys": [
        {
            "alg": "RS256",
            "kty": "RSA",
            "use": "sig",
            "n": "0wtlJRY9-ru61LmOgieeI7_rD1oIna9QpBMAOWw8wTuoIhFQFwcIi7MFB7IEfelCPj08vkfLsuFtR8cG07EE4uvJ78bAqRjMsCvprWp4e2p7hqPnWcpRpDEyHjzirEJle1LPpjLLVaSWgkbrVaOD0lkWkP1T1TkrOset_Obh8BwtO-Ww-UfrEwxTyz1646AGkbT2nL8PX0trXrmira8GnrCkFUgTUS61GoTdb9bCJ19PLX9Gnxw7J0BtR0GubopXq8KlI0ThVql6ZtVGN2dvmrCPAVAZleM5TVB61m0VSXvGWaF6_GeOhbFoyWcyUmFvzWhBm8Q38vWgsSI7oHTkEw",
            "e": "AQAB",
            "kid": "NEE1QURBOTM4MzI5RkFDNTYxOTU1MDg2ODgwQ0UzMTk1QjYyRkRFQw",
            "x5t": "NEE1QURBOTM4MzI5RkFDNTYxOTU1MDg2ODgwQ0UzMTk1QjYyRkRFQw",
            "x5c": [
                "MIIDBzCCAe+gAwIBAgIJNtD9Ozi6j2jJMA0GCSqGSIb3DQEBCwUAMCExHzAdBgNVBAMTFmRldi04N2V2eDlydS5hdXRoMC5jb20wHhcNMTkwNjIwMTU0NDU4WhcNMzMwMjI2MTU0NDU4WjAhMR8wHQYDVQQDExZkZXYtODdldng5cnUuYXV0aDAuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0wtlJRY9+ru61LmOgieeI7/rD1oIna9QpBMAOWw8wTuoIhFQFwcIi7MFB7IEfelCPj08vkfLsuFtR8cG07EE4uvJ78bAqRjMsCvprWp4e2p7hqPnWcpRpDEyHjzirEJle1LPpjLLVaSWgkbrVaOD0lkWkP1T1TkrOset/Obh8BwtO+Ww+UfrEwxTyz1646AGkbT2nL8PX0trXrmira8GnrCkFUgTUS61GoTdb9bCJ19PLX9Gnxw7J0BtR0GubopXq8KlI0ThVql6ZtVGN2dvmrCPAVAZleM5TVB61m0VSXvGWaF6/GeOhbFoyWcyUmFvzWhBm8Q38vWgsSI7oHTkEwIDAQABo0IwQDAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBQlGXpmYaXFB7Q3eG69Uhjd4cFp/jAOBgNVHQ8BAf8EBAMCAoQwDQYJKoZIhvcNAQELBQADggEBAIzQOF/h4T5WWAdjhcIwdNS7hS2Deq+UxxkRv+uavj6O9mHLuRG1q5onvSFShjECXaYT6OGibn7Ufw/JSm3+86ZouMYjBEqGh4OvWRkwARy1YTWUVDGpT2HAwtIq3lfYvhe8P4VfZByp1N4lfn6X2NcJflG+Q+mfXNmRFyyft3Oq51PCZyyAkU7bTun9FmMOyBtmJvQjZ8RXgBLvu9nUcZB8yTVoeUEg4cLczQlli/OkiFXhWgrhVr8uF0/9klslMFXtm78iYSgR8/oC+k1pSNd1+ESSt7n6+JiAQ2Co+ZNKta7LTDGAjGjNDymyoCrZpeuYQwwnHYEHu/0khjAxhXo="
            ],
        },
        {
            "alg": "RS256",
            "kty": "RSA",
            "use": "sig",
            "n": "qMDEywqsPbiQbnSPVoKOb1HrQ_2KxI4JDe-AK-kbpb2Q3QXFl6IM3pJCvfYOm-f3DuEtBpll_Rg28WWeXl8pXAhmHk3V2Ig57f81uzGXg5xFtZDrqAG0chgwCQPD15FG00xrLDTvSDkIEPJZq-Y4IlJ3NbzQ8gn_JiappjMc8FjqQMz_4uUF-iIPU_aUgbLLtN98moKeNLAVV2lV3H5kVhNP8Fqd6piiH-mdma_KdY--GahAFC7Lt72_QtxnxowalbdkdMDim7paTeqxoZUKKHJsRVPXbiGx1zB3cfgBH7meU8ILv7JX3odu0juy0y2gagSaMkEd9-mcTLr8Bg0-5Q",
            "e": "AQAB",
            "kid": "Dt0jkFkY7KkmYdDb2BaI1",
            "x5t": "lhmczC7hbLpBZh6MBSygH1D9qeE",
            "x5c": [
                "MIIDBzCCAe+gAwIBAgIJHjJKyTNJE/wIMA0GCSqGSIb3DQEBCwUAMCExHzAdBgNVBAMTFmRldi04N2V2eDlydS5hdXRoMC5jb20wHhcNMjAwMzExMjA1OTM5WhcNMzMxMTE4MjA1OTM5WjAhMR8wHQYDVQQDExZkZXYtODdldng5cnUuYXV0aDAuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqMDEywqsPbiQbnSPVoKOb1HrQ/2KxI4JDe+AK+kbpb2Q3QXFl6IM3pJCvfYOm+f3DuEtBpll/Rg28WWeXl8pXAhmHk3V2Ig57f81uzGXg5xFtZDrqAG0chgwCQPD15FG00xrLDTvSDkIEPJZq+Y4IlJ3NbzQ8gn/JiappjMc8FjqQMz/4uUF+iIPU/aUgbLLtN98moKeNLAVV2lV3H5kVhNP8Fqd6piiH+mdma/KdY++GahAFC7Lt72/QtxnxowalbdkdMDim7paTeqxoZUKKHJsRVPXbiGx1zB3cfgBH7meU8ILv7JX3odu0juy0y2gagSaMkEd9+mcTLr8Bg0+5QIDAQABo0IwQDAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBQxVQqyrrAtXsBznZj2GN4nfJf+sTAOBgNVHQ8BAf8EBAMCAoQwDQYJKoZIhvcNAQELBQADggEBAGsIl6yxIG8GOkHlfcSEa4//4WDxwfw8lg6zNPri6nhYtF1kbHTO5PqUbE+kasMnvqEV5Y0QXvyxwIjLLbbYiySK6aWp5XS2Wy5hYlMjXOimAw6mwbkNVhujRsPjTY3P+bv/9eiv2zO9yEfzfmfr6jhYcmnOdTFgAujsL4AyDpUh4/jKDtDNFl6lMdn8J7DcdRNZM/8OsAk6GgZYlzStfh4aI/uE3ekJ84XAxxdHUzwDUu5B8CetmHvfxQvV9MjmozLR8SbkTEhUv4//tr8SfGc8jS78E5w8NJN6DtYVcUNweHrAlvQXRevCmBRu3D9hKARjXfTBqilBBF9nNt93mYM="
            ],
        },
    ]
}
sample_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik5FRTFRVVJCT1RNNE16STVSa0ZETlRZeE9UVTFNRGcyT0Rnd1EwVXpNVGsxUWpZeVJrUkZRdyJ9.eyJpc3MiOiJodHRwczovL2Rldi04N2V2eDlydS5hdXRoMC5jb20vIiwic3ViIjoiYVc0Q2NhNzl4UmVMV1V6MGFFMkg2a0QwTzNjWEJWdENAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vZXhwZW5zZXMtYXBpIiwiaWF0IjoxNTcyMDA2OTU0LCJleHAiOjE1NzIwMDY5NjQsImF6cCI6ImFXNENjYTc5eFJlTFdVejBhRTJINmtEME8zY1hCVnRDIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIn0.PUxE7xn52aTCohGiWoSdMBZGiYAHwE5FYie0Y1qUT68IHSTXwXVd6hn02HTah6epvHHVKA2FqcFZ4GGv5VTHEvYpeggiiZMgbxFrmTEY0csL6VNkX1eaJGcuehwQCRBKRLL3zKmA5IKGy5GeUnIbpPHLHDxr-GXvgFzsdsyWlVQvPX2xjeaQ217r2PtxDeqjlf66UYl6oY6AqNS8DH3iryCvIfCcybRZkc_hdy-6ZMoKT6Piijvk_aXdm7-QQqKJFHLuEqrVSOuBqqiNfVrG27QzAPuPOxvfXTVLXL2jek5meH6n-VWgrBdoMFH93QEszEDowDAEhQPHVs0xj7SIzA"
sample_audience = "https://expenses-api"


@pytest.mark.freeze_time("2017-05-21")
def test_happy_path(mocker) -> None:
    """Test that JWT token is parsed and authorized."""

    mocker.patch(
        "pyramid_cloudflare_access.PyJWKClient.fetch_data", return_value=sample_jwk
    )
    tween_handler = mocker.Mock()

    request = testing.DummyRequest()
    request.cookies = {"CF_Authorization": sample_token}
    request.registry.settings = {
        "pyramid_cloudflare_access.policy_audience": sample_audience,
        "pyramid_cloudflare_access.team": "auth0",
    }

    CloudflareAccess(tween_handler, request.registry)(request)
    tween_handler.assert_called_with(request)


def test_missing_cookie(mocker) -> None:
    """Test that access is denied on wrong request."""

    mocker.patch(
        "pyramid_cloudflare_access.PyJWKClient.fetch_data", return_value=sample_jwk
    )
    tween_handler = mocker.Mock()

    request = testing.DummyRequest()
    request.registry.settings = {
        "pyramid_cloudflare_access.policy_audience": sample_audience,
        "pyramid_cloudflare_access.team": "auth0",
    }
    with pytest.raises(HTTPBadRequest):
        CloudflareAccess(tween_handler, request.registry)(request)


def test_auth_failed(mocker) -> None:
    """Test that access is denied on expired auth."""

    mocker.patch(
        "pyramid_cloudflare_access.PyJWKClient.fetch_data", return_value=sample_jwk
    )
    tween_handler = mocker.Mock()

    request = testing.DummyRequest()
    request.cookies = {"CF_Authorization": sample_token}
    request.registry.settings = {
        "pyramid_cloudflare_access.policy_audience": sample_audience,
        "pyramid_cloudflare_access.team": "auth0",
    }
    with pytest.raises(HTTPForbidden):
        CloudflareAccess(tween_handler, request.registry)(request)
