# Imports
from typing import Optional


# Base class for credentials
class OIAnalyticsAPICredentials:
    def __init__(
            self,
            base_url: str,
            login: Optional[str] = None,
            pwd: Optional[str] = None,
            token: Optional[str] = None,
    ):
        if login is not None and pwd is not None:
            self.auth_type = "Basic"
        elif token is not None:
            self.auth_type = "Token"
        else:
            raise ValueError("Either login/password or token should be provided")
        self.base_url = base_url.strip("/")
        self.login = login
        self.pwd = pwd
        self.token = token

    def __repr__(self):
        if self.auth_type == "Basic":
            auth_summary = f"Login: {self.login}\nPassword: {self.pwd}"
        elif self.auth_type == "Token":
            auth_summary = f"Token: {self.token}"
        else:
            raise ValueError(
                "The only supported authentication types are Basic or Token"
            )
        return f"{self.auth_type} authentication on {self.base_url}\n{auth_summary}"

    def auth_kwargs(self):
        if self.auth_type == "Basic":
            return {"auth": (self.login, self.pwd)}
        elif self.auth_type == "Token":
            return {"headers": {"Authorization": f"Bearer {self.token}"}}
