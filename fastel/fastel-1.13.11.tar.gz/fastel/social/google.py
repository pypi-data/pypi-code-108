from typing import Any, Dict, Tuple

import google_auth_oauthlib.flow
import requests

from fastel.exceptions import APIException
from fastel.social import SocialModel


class GoogleLogin:
    def __init__(self, data: SocialModel) -> None:
        self.project_api_host = data.project_api_host
        self.redirect_uri = f"{data.project_api_host}/google/callback"
        self.flow = google_auth_oauthlib.flow.Flow.from_client_config(
            {
                "web": {
                    "client_id": data.client_id,
                    "project_id": data.client_id,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": data.client_secret,
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
        )
        self.flow.redirect_uri = self.redirect_uri

    def redirect(self) -> Tuple[str, str]:
        authorization_url, state = self.flow.authorization_url(
            include_granted_scopes="true"
        )
        return authorization_url, state

    def callback(
        self, state: Dict[str, Any], full_query_param_str: str
    ) -> Dict[str, Any]:
        self.flow.state = state["state"]
        self.flow.fetch_token(
            authorization_response=f"{self.redirect_uri}?{full_query_param_str}"
        )
        access_token = self.flow.credentials.token
        return self.get_profile(access_token)

    def get_profile(self, access_token: str) -> Dict[str, Any]:
        resp = requests.get(
            f"https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses&access_token={access_token}"
        )
        profile = resp.json()

        try:
            resp.raise_for_status()
        except Exception:
            raise APIException(
                status_code=401,
                error="http_error_occur",
                detail=profile["detail"],
            )

        result = {}
        result["social_id"] = profile["names"][0]["metadata"]["source"]["id"]
        result["provider"] = "google"

        try:
            result["email"] = profile["emailAddresses"][0]["value"]
            result["name"] = profile["names"][0]["unstructuredName"]
        except Exception:
            print(
                f"[WARNING] google social user {result['social_id']} doesn't have email or name"
            )

        return result
