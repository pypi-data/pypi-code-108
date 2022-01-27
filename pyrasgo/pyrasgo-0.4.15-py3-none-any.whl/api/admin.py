
class Admin():

    def __init__(self):
        from .connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)

    def fix_permission_errors(self, user_id: int):
        response = self.api._patch(f"/admin/users/{user_id}/fix-permission-errors", api_version=1).json()
        return response