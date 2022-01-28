import os


class ManageClientConfig(object):
    def __init__(
        self,
        manage_system_id: str,
        manage_system_url: str,
        manage_system_token: str,
        manage_system_debug: bool = False,
    ):
        self.manage_system_id = manage_system_id
        self.manage_system_url = manage_system_url
        self.manage_system_token = manage_system_token
        self.manage_system_debug = '1' if manage_system_debug else '0'
        self.init_environ_settings()

    def init_environ_settings(self) -> None:
        os.environ["MANAGE_SYSTEM_ID"] = self.manage_system_id
        os.environ["MANAGE_SYSTEM_URL"] = self.manage_system_url
        os.environ["MANAGE_SYSTEM_TOKEN"] = self.manage_system_token
        os.environ["MANAGE_SYSTEM_DEBUG"] = self.manage_system_debug
