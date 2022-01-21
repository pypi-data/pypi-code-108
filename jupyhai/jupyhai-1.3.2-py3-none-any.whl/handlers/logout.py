from jupyhai.handlers.base import JupyhaiHandler
from jupyhai.utils.auth import login_status, logout


class LogoutHandler(JupyhaiHandler):
    def get(self) -> None:
        self.finish({'result': login_status()})

    def post(self) -> None:
        self.log.info("Logging out...")
        logout()
        success = not login_status()
        if success:
            self.log.info("Logged out.")
        self.finish({'success': success})
