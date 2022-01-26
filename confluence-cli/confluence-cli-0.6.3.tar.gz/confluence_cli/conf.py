from logging import config as loggingconfig
from logging import getLogger

from decouple import config as deconf
from confluence_cli import yamlparser
from confluence_cli.cli import ConfluenceWrapper
from confluence_cli.cli.types import NavigableDict

def __check_vars():
    if deconf("CONFLUENCE_ADMIN_PASS"):
        print(".env vars set.")
    else:
        raise ValueError("Config error, some env vars not set")


## Call env.py for imput env vars
with open("./env.py") as f:
    exec(f.read())
## Check env vars by decouple lib
__check_vars()

## Application context and keys
__application_context: dict = {}

## load logging conf
__logconfig = yamlparser.parse_config("logs/logging.yml")
loggingconfig.dictConfig(__logconfig)
logger = getLogger("confluence_log")

## load components conf
__confluence_conf: NavigableDict = NavigableDict(yamlparser.parse_config("confluence.yml"))

__confluence_api: ConfluenceWrapper


def get_confluence_conf() -> NavigableDict:
    return __confluence_conf

def get_confluence_api() -> ConfluenceWrapper:
    global __confluence_api
    try:
        return __confluence_api
    except NameError:  # Still not defined
        raise ValueError("No Confluence server configured via conf.set_confluence_server()") from NameError


def set_confluence_server(server: str):
    global __confluence_api
    __confluence_api = ConfluenceWrapper(get_confluence_conf().get("api_service").get(server))


