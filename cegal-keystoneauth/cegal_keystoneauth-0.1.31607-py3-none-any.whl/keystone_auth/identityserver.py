import requests

from cegal.keystone_auth import logger


class IdentityServer:
    def openid_configuration(self, provider_uri, verify_tls):
        response = requests.get(
            provider_uri + "/.well-known/openid-configuration", verify=verify_tls
        )
        logger.debug(f"<-- openid_configuration {response.content}")
        return response

    def request_token_from_endpoint(
        self,
        token_endpoint,
        client_id,
        auth_code,
        code_verifier,
        listener_address,
        verify_tls,
    ):
        request_body = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code_verifier": code_verifier,
            "code": auth_code,
            "redirect_uri": listener_address,
        }

        logger.debug(f"--> request_token_from_endpoint {request_body}")

        response = requests.post(token_endpoint, data=request_body, verify=verify_tls)
        logger.debug(f"<-- request_token_from_endpoint {response.content}")
        return response

    def signing_keys(self, jwks_uri, verify_tls):
        response = requests.get(jwks_uri, verify=verify_tls)
        logger.debug(f"<-- signing_keys {response.content}")
        return response

    def device_activation(
        self, token_endpoint, device_code, client_id, code_expired, interval
    ):
        import time
        from urllib.parse import urlencode
        from datetime import datetime

        params = urlencode(
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": device_code,
                "client_id": client_id,
            }
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        while code_expired > datetime.now():
            r = requests.post(token_endpoint, params, headers=headers)
            resp = r.json()
            if "authorization_pending" in resp.values() or "slow_down" in resp.values():
                logger.info(f"waiting for device...")
                time.sleep(interval)
            elif r.status_code == 200:
                return resp
            else:
                raise Exception("Error authorizing device: " + r.reason)
        raise Exception("Timed out waiting for device auth.")

    def request_device_code(
        self, device_authorization_endpoint, client_id, request_scopes, audience
    ):
        from urllib.parse import urlencode

        params = urlencode(
            {
                "client_id": client_id,
                "scope": request_scopes,
                "audience": None if audience is None else " ".join(audience),
            }
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post(device_authorization_endpoint, params, headers=headers)
        if r.status_code != 200:
            raise Exception("Error requesting device code: " + r.reason)
        return r

    def is_uri_allowed(self, provider_uri, verify_tls):
        return not (provider_uri.split(":")[0] != "https" and verify_tls == True)
