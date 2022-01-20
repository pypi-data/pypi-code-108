import os


class MSGraphyConfig:

    def __init__(self,
                 client_id=None,
                 client_secret=None,
                 tenant_id=None,
                 authority=None,
                 env_prefix="MSGRAPHY"
                 ):

        if not client_id:
            client_id = os.environ[f'{env_prefix}_CLIENT_ID']
        self.client_id = client_id

        if not client_secret:
            client_secret = os.getenv(f'{env_prefix}_CLIENT_SECRET')
        self.client_secret = client_secret

        if not tenant_id:
            tenant_id = os.getenv(f'{env_prefix}_TENANT_ID')
        self.tenant_id = tenant_id

        if not authority:
            authority = os.getenv(f'{env_prefix}_AUTHORITY')

        if not authority:
            if tenant_id:
                authority = f"https://login.microsoftonline.com/{tenant_id}"
            else:
                raise Exception("Either 'authority' or 'tenant_id' must be set")

        self.authority = authority
        self.token_cache_file = os.getenv(f'{env_prefix}_TOKEN_CACHE_FILE')
