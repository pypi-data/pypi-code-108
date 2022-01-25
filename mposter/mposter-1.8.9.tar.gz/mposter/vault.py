from hvac import Client
from hvac.api.auth_methods import AppRole, Userpass
from pydantic import BaseSettings, Field


class VaultAPI(BaseSettings):
    vault_api_url: str = Field(...)
    vault_userpass_user: str = Field(...)
    vault_userpass_password: str = Field(...)

    def fetch_secret(self, secret_path: str) -> dict:
        client = Client(url=self.vault_api_url)
        user = Userpass(client.adapter)
        user.login(
            username=self.vault_userpass_user,
            password=self.vault_userpass_password,
        )
        approle = AppRole(client.adapter)

        role_id = approle.read_role_id(self.vault_userpass_user)['data']['role_id']
        secret_id = approle.generate_secret_id(self.vault_userpass_user)['data']['secret_id']
        auth_response = approle.login(role_id, secret_id)

        if client.is_authenticated():
            client.token = auth_response['auth']['client_token']

        secrets = client.secrets.kv.v2.read_secret_version(
            mount_point='dwh_crawlers',
            path=secret_path
        )
        return secrets['data']['data']
