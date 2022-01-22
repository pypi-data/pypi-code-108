from typing import Any, Dict

import requests
from jwt import decode

from fastel.social import SocialModel


class LineLogin:
    def __init__(self, data: SocialModel) -> None:
        self.project_client_id = data.project_client_id
        self.project_api_host = data.project_api_host
        self.client_id = data.client_id
        self.client_secret = data.client_secret

        self.CALLBACK_URL = f"{self.project_api_host}/line/callback"
        self.LINE_URL = "https://access.line.me/oauth2/v2.1/authorize"

    def redirect(self, state: str) -> str:
        url = f"{self.LINE_URL}?response_type=code&client_id={self.client_id}&redirect_uri={self.CALLBACK_URL}&state={state}&scope=profile%20openid%20email"
        return url

    def callback(self, state: Dict[str, Any], code: str) -> Dict[str, Any]:
        print(state)
        resp = requests.post(
            "https://api.line.me/oauth2/v2.1/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.CALLBACK_URL,
            },
        )

        resp_json = resp.json()
        line_token = decode(resp_json["id_token"], options={"verify_signature": False})
        result = {}
        result["social_id"] = line_token.get("sub", "")
        result["provider"] = "line"

        try:
            result["email"] = line_token["email"]
            result["name"] = line_token["name"]
        except Exception:
            print(
                f"[WARNING] fb social user {result['social_id']} doesn't have email or name"
            )

        return result
