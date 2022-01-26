"""
REST Wrapper for signal-cli running on system dbus
"""


from sanic import Sanic

from signal_cli_dbus_rest_api.api import entrypoint
from signal_cli_dbus_rest_api.version import __version__

app = Sanic("signal-cli-dbus-rest-api", env_prefix="SIGNAL_CLI_DBUS_REST_API_")
app.config.FALLBACK_ERROR_FORMAT = "json"
app.config.API_HOST = (
    f'{app.config.get("API_HOST", "127.0.0.1")}:{app.config.get("API_PORT", 8080)}'
)
app.config.API_BASEPATH = app.config.get("API_BASEPATH")
app.config.API_SCHEMES = app.config.get("API_SCHEMES", "http,https").split(",")
app.config.API_LICENSE_NAME = "MIT"
app.config.API_LICENSE_URL = "https://mit-license.org/"
app.config.API_TITLE = "Signal Cli REST API"
app.config.API_DESCRIPTION = "This is the Signal Cli REST API documentation."
app.config.API_VERSION = __version__
app.blueprint(entrypoint)


def run():
    """
    run app
    """
    app.run(
        host=app.config.get("HOST", "127.0.0.1"),
        port=app.config.get("PORT", 8080),
        debug=app.config.get("DEBUG", False),
        workers=app.config.get("WORKERS", 1),
        access_log=app.config.get("ACCESS_LOG", False),
        auto_reload=app.config.get("AUTO_RELOAD", False),
    )
